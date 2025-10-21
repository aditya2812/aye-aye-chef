import json
import boto3
import uuid
import os
from datetime import datetime
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

rds_client = boto3.client('rds-data')
lambda_client = boto3.client('lambda')
bedrock_agent_client = boto3.client('bedrock-agent-runtime')

def handler(event, context):
    try:
        # Parse request - handle both JSON and raw base64 data
        raw_body = event['body']
        logger.info(f"Received body type: {type(raw_body)}")
        logger.info(f"Body preview: {str(raw_body)[:100]}...")
        
        # Try to parse as JSON first
        try:
            body = json.loads(raw_body)
            logger.info("Successfully parsed body as JSON")
        except (json.JSONDecodeError, TypeError):
            # If JSON parsing fails, treat as raw base64 image data
            logger.info("Body is not JSON, treating as raw base64 image data")
            body = raw_body
        
        # Handle both s3Key (old method) and base64 image data (new method)
        if isinstance(body, dict) and 's3Key' in body:
            s3_key = body['s3Key']
            s3_uri = f"s3://{os.environ.get('IMAGES_BUCKET')}/{s3_key}"
            logger.info(f"Using s3Key: {s3_key}")
        elif isinstance(body, str) and (body.startswith('data:') or len(body) > 1000):
            # Handle base64 image data
            import base64
            from datetime import datetime
            
            logger.info("Processing base64 image data")
            
            # Decode base64 image
            if body.startswith('data:'):
                image_data = body.split(',')[1] if ',' in body else body
            else:
                image_data = body
                
            try:
                image_bytes = base64.b64decode(image_data)
                logger.info(f"Decoded image size: {len(image_bytes)} bytes")
            except Exception as decode_error:
                logger.error(f"Base64 decode error: {decode_error}")
                raise ValueError(f"Invalid base64 image data: {decode_error}")
            
            # Generate S3 key
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            file_id = str(uuid.uuid4())[:8]
            s3_key = f"uploads/direct/scan_{timestamp}_{file_id}.jpg"
            
            # Upload to S3
            s3_client = boto3.client('s3')
            bucket_name = os.environ.get('IMAGES_BUCKET')
            s3_client.put_object(
                Bucket=bucket_name,
                Key=s3_key,
                Body=image_bytes,
                ContentType='image/jpeg'
            )
            
            s3_uri = f"s3://{bucket_name}/{s3_key}"
            logger.info(f"Uploaded base64 image to S3: {s3_uri}")
        else:
            logger.error(f"Invalid request format. Body type: {type(body)}, Body: {str(body)[:200]}")
            raise ValueError("Missing s3Key or valid base64 image data in request")
        
        # Get user ID from JWT
        user_id = event['requestContext']['authorizer']['claims']['sub']
        
        # Generate scan ID
        scan_id = str(uuid.uuid4())
        
        # Database connection info
        db_secret_arn = os.environ['DB_SECRET_ARN']
        db_cluster_arn = os.environ['DB_CLUSTER_ARN']
        
        # Ensure user exists in database (upsert)
        try:
            logger.info(f"Upserting user: {user_id}")
            rds_client.execute_statement(
                resourceArn=db_cluster_arn,
                secretArn=db_secret_arn,
                database='ayeaye',
                sql="""
                    INSERT INTO users (id, email, created_at)
                    VALUES (:user_id::uuid, :email, NOW())
                    ON CONFLICT (id) DO UPDATE SET 
                        email = EXCLUDED.email
                """,
                parameters=[
                    {'name': 'user_id', 'value': {'stringValue': user_id}},
                    {'name': 'email', 'value': {'stringValue': event['requestContext']['authorizer']['claims'].get('email', 'unknown@example.com')}}
                ]
            )
            logger.info(f"User upsert successful for: {user_id}")
        except Exception as user_error:
            logger.error(f"User upsert failed: {str(user_error)}")
            # Don't fail the whole request for user upsert issues
        
        # Insert scan record
        try:
            logger.info(f"Creating scan record: {scan_id}")
            rds_client.execute_statement(
                resourceArn=db_cluster_arn,
                secretArn=db_secret_arn,
                database='ayeaye',
                sql="""
                    INSERT INTO scans (id, user_id, s3_key, status, created_at)
                    VALUES (:scan_id::uuid, :user_id::uuid, :s3_key, 'processing', NOW())
                """,
                parameters=[
                    {'name': 'scan_id', 'value': {'stringValue': scan_id}},
                    {'name': 'user_id', 'value': {'stringValue': user_id}},
                    {'name': 's3_key', 'value': {'stringValue': s3_key}}
                ]
            )
            logger.info(f"Scan record created successfully: {scan_id}")
        except Exception as scan_error:
            logger.error(f"Failed to create scan record: {str(scan_error)}")
            raise Exception(f"Database error creating scan: {scan_error}")
        
        # Invoke ingredient detection Lambda
        detect_function_name = os.environ.get('DETECT_INGREDIENTS_FUNCTION')
        
        try:
            # S3 URI is already prepared above
            
            # Invoke detect ingredients function
            detect_response = lambda_client.invoke(
                FunctionName=detect_function_name,
                InvocationType='RequestResponse',
                Payload=json.dumps({
                    'image_s3_uri': s3_uri
                })
            )
            
            # Parse the response
            detect_result = json.loads(detect_response['Payload'].read())
            
            if detect_result.get('statusCode') == 200:
                detection_data = json.loads(detect_result['body'])
                candidates = detection_data.get('candidates', [])
                
                logger.info(f"Successfully detected {len(candidates)} ingredients for scan {scan_id}")
                
                # Map ingredients to FDC IDs FIRST
                fdc_mapping = {}  # Initialize outside try block
                try:
                    logger.info("Mapping ingredients to FDC IDs...")
                    map_to_fdc_function = os.environ.get('MAP_TO_FDC_FUNCTION')
                    
                    if map_to_fdc_function:
                        # Extract labels for mapping
                        labels = [candidate['label'] for candidate in candidates]
                        
                        # Call map-to-fdc Lambda
                        map_response = lambda_client.invoke(
                            FunctionName=map_to_fdc_function,
                            InvocationType='RequestResponse',
                            Payload=json.dumps({'labels': labels})
                        )
                        
                        map_result = json.loads(map_response['Payload'].read())
                        logger.info(f"Map-to-FDC response: {map_result}")
                        
                        if map_result.get('statusCode') == 200:
                            map_data = json.loads(map_result['body'])
                            mapped_ingredients = map_data.get('mapped', [])
                            
                            # Create a mapping dict for easy lookup
                            fdc_mapping = {item['label']: item for item in mapped_ingredients}
                            
                            logger.info(f"Successfully mapped {len(mapped_ingredients)} ingredients to FDC IDs")
                            logger.info(f"FDC mapping: {fdc_mapping}")
                        else:
                            logger.warning("Map-to-FDC failed, using empty FDC IDs")
                            fdc_mapping = {}
                    else:
                        logger.warning("MAP_TO_FDC_FUNCTION not configured")
                        fdc_mapping = {}
                        
                except Exception as map_error:
                    logger.error(f"Error mapping to FDC: {str(map_error)}")
                    fdc_mapping = {}
                
                # NOW store detected ingredients in database with FDC IDs
                logger.info(f"About to store {len(candidates)} ingredients in database")
                
                try:
                    logger.info(f"Starting database storage for scan_id: {scan_id}")
                    for i, candidate in enumerate(candidates):
                        # Get FDC ID from mapping or use placeholder
                        fdc_info = fdc_mapping.get(candidate['label'], {})
                        fdc_id = fdc_info.get('fdc_id', f"temp_{scan_id}_{i}")
                        
                        logger.info(f"Storing ingredient {i+1}/{len(candidates)}: {candidate['label']} -> FDC ID: {fdc_id}")
                        
                        try:
                            insert_result = rds_client.execute_statement(
                                resourceArn=db_cluster_arn,
                                secretArn=db_secret_arn,
                                database='ayeaye',
                                sql="""
                                    INSERT INTO scan_items (scan_id, label, fdc_id, confidence, grams_est, confirmed, created_at)
                                    VALUES (:scan_id::uuid, :label, :fdc_id, :confidence, :grams_est, :confirmed, NOW())
                                """,
                                parameters=[
                                    {'name': 'scan_id', 'value': {'stringValue': scan_id}},
                                    {'name': 'label', 'value': {'stringValue': candidate['label']}},
                                    {'name': 'fdc_id', 'value': {'stringValue': fdc_id}},
                                    {'name': 'confidence', 'value': {'doubleValue': candidate['confidence']}},
                                    {'name': 'grams_est', 'value': {'doubleValue': 100.0}},  # Default estimate
                                    {'name': 'confirmed', 'value': {'booleanValue': False}}
                                ]
                            )
                            logger.info(f"✅ Successfully inserted ingredient {candidate['label']}")
                        except Exception as insert_error:
                            logger.error(f"❌ Failed to insert ingredient {candidate['label']}: {str(insert_error)}")
                            raise insert_error
                            
                    logger.info(f"✅ Successfully stored ALL {len(candidates)} ingredients with FDC IDs in database")
                except Exception as db_error:
                    logger.error(f"❌ Database error storing ingredients: {str(db_error)}")
                    logger.error(f"Database error details: {type(db_error).__name__}: {str(db_error)}")
                    # Continue anyway - don't fail the whole request for DB issues
                    logger.warning("Continuing despite database error")
                
                # Update scan status to ready
                try:
                    logger.info(f"Updating scan {scan_id} status to ready")
                    rds_client.execute_statement(
                        resourceArn=db_cluster_arn,
                        secretArn=db_secret_arn,
                        database='ayeaye',
                        sql="UPDATE scans SET status = 'ready' WHERE id = :scan_id::uuid",
                        parameters=[
                            {'name': 'scan_id', 'value': {'stringValue': scan_id}}
                        ]
                    )
                    logger.info(f"Successfully updated scan {scan_id} status to ready")
                except Exception as update_error:
                    logger.error(f"Database error updating scan status: {str(update_error)}")
                    # Continue anyway - don't fail the whole request
                
                # Always return success response, even if database operations fail
                response_body = {
                    'scan_id': scan_id,
                    'status': 'ready',
                    'ingredients_detected': len(candidates),
                    'message': 'Ingredients detected successfully',
                    'items': [
                        {
                            'label': candidate['label'],
                            'confidence': candidate['confidence'],
                            'grams_est': 100.0,
                            'confirmed': False,
                            'fdc_id': fdc_mapping.get(candidate['label'], {}).get('fdc_id', '')
                        }
                        for candidate in candidates
                    ]
                }
                
                logger.info(f"Returning success response: {response_body}")
                
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                        'Access-Control-Allow-Methods': 'POST,OPTIONS',
                        'Access-Control-Allow-Credentials': 'false'
                    },
                    'body': json.dumps(response_body)
                }
            else:
                logger.error(f"Ingredient detection failed: {detect_result}")
                return {
                    'statusCode': 500,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'error': 'Ingredient detection failed'
                    })
                }
                
        except Exception as detection_error:
            logger.error(f"Error in ingredient detection: {str(detection_error)}")
            # Fall back to placeholder response
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'scan_id': scan_id,
                    'status': 'processing',
                    'message': 'Scan started (detection pending)'
                })
            }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': 'http://localhost:8081',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'POST,OPTIONS',
                'Access-Control-Allow-Credentials': 'false'
            },
            'body': json.dumps({
                'error': 'Internal server error'
            })
        }