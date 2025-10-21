import json
import boto3
import os
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

rds_client = boto3.client('rds-data')

def handler(event, context):
    """Lambda handler for getting scan results"""
    try:
        # Get scan ID from path parameters
        scan_id = event['pathParameters']['id']
        
        # Get user ID from JWT
        user_id = event['requestContext']['authorizer']['claims']['sub']
        
        logger.info(f"Getting scan results for scan_id: {scan_id} (type: {type(scan_id)}), user_id: {user_id} (type: {type(user_id)})")
        logger.info(f"Raw event pathParameters: {event.get('pathParameters', {})}")
        logger.info(f"Raw event requestContext: {event.get('requestContext', {}).get('authorizer', {}).get('claims', {})}")
        
        # Database connection info
        db_secret_arn = os.environ['DB_SECRET_ARN']
        db_cluster_arn = os.environ['DB_CLUSTER_ARN']
        
        # Get scan info
        try:
            logger.info(f"Executing scan query with scan_id: {scan_id}, user_id: {user_id}")
            
            # Validate UUIDs
            import uuid
            try:
                uuid.UUID(scan_id)
                uuid.UUID(user_id)
                logger.info(f"Both UUIDs validated successfully")
            except ValueError as uuid_error:
                logger.error(f"Invalid UUID format - scan_id: {scan_id}, user_id: {user_id}, error: {uuid_error}")
                raise ValueError(f"Invalid UUID format: {uuid_error}")
            
            # Use direct string substitution with validated UUIDs
            scan_response = rds_client.execute_statement(
                resourceArn=db_cluster_arn,
                secretArn=db_secret_arn,
                database='ayeaye',
                sql="""
                    SELECT id::text, status, s3_key, created_at 
                    FROM scans 
                    WHERE id = :scan_id::uuid AND user_id = :user_id::uuid
                """,
                parameters=[
                    {'name': 'scan_id', 'value': {'stringValue': scan_id}},
                    {'name': 'user_id', 'value': {'stringValue': user_id}}
                ]
            )
            logger.info(f"Scan query executed successfully")
        except Exception as scan_query_error:
            logger.error(f"Error executing scan query: {str(scan_query_error)}")
            logger.error(f"Query parameters: scan_id={scan_id}, user_id={user_id}")
            raise
        
        logger.info(f"Scan query returned {len(scan_response['records'])} records")
        
        if not scan_response['records']:
            logger.warning(f"No scan found for scan_id: {scan_id}, user_id: {user_id}")
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Scan not found'
                })
            }
        
        scan_record = scan_response['records'][0]
        scan_status = scan_record[1]['stringValue']
        
        # Get detected ingredients - let's try a diagnostic approach first
        try:
            logger.info(f"Executing items query with scan_id: {scan_id}")
            
            # First, let's check what's actually in the scan_items table
            logger.info("Checking scan_items table structure and data...")
            diagnostic_response = rds_client.execute_statement(
                resourceArn=db_cluster_arn,
                secretArn=db_secret_arn,
                database='ayeaye',
                sql="""
                    SELECT 
                        scan_id::text as scan_id_text,
                        label,
                        fdc_id,
                        confidence,
                        grams_est,
                        confirmed
                    FROM scan_items 
                    LIMIT 5
                """
            )
            
            logger.info(f"Diagnostic query returned {len(diagnostic_response['records'])} records")
            for i, record in enumerate(diagnostic_response['records']):
                logger.info(f"Record {i}: scan_id={record[0].get('stringValue', 'NULL')}, label={record[1].get('stringValue', 'NULL')}")
            
            # Now try the actual query with a simpler approach
            items_response = rds_client.execute_statement(
                resourceArn=db_cluster_arn,
                secretArn=db_secret_arn,
                database='ayeaye',
                sql=f"""
                    SELECT label, fdc_id, confidence, grams_est, confirmed
                    FROM scan_items 
                    WHERE scan_id::text = '{scan_id}'
                    ORDER BY confidence DESC
                """
            )
            logger.info(f"Items query executed successfully")
        except Exception as items_query_error:
            logger.error(f"Error executing items query: {str(items_query_error)}")
            logger.error(f"Query parameters: scan_id={scan_id}")
            
            # If the main query fails, try to return empty results instead of failing
            logger.warning("Returning empty items list due to database error")
            items_response = {'records': []}
            # Don't raise the exception, just continue with empty results
        
        logger.info(f"Items query returned {len(items_response['records'])} records")
        
        items = []
        for record in items_response['records']:
            # Handle potential null values in the response
            fdc_id_value = record[1].get('stringValue') if record[1] and 'stringValue' in record[1] else None
            confidence_value = record[2].get('doubleValue', 0.0) if record[2] else 0.0
            grams_est_value = record[3].get('doubleValue', 100.0) if record[3] else 100.0
            confirmed_value = record[4].get('booleanValue', False) if record[4] else False
            
            item = {
                'label': record[0]['stringValue'],
                'fdc_id': fdc_id_value,
                'confidence': confidence_value,
                'grams_est': grams_est_value,
                'confirmed': confirmed_value
            }
            items.append(item)
            logger.info(f"Found item: {item['label']} with confidence {item['confidence']}")
        
        logger.info(f"Returning {len(items)} items for scan {scan_id}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'scan_id': scan_id,
                'status': scan_status,
                'requires_confirmation': scan_status == 'ready',
                'items': items
            })
        }
        
    except Exception as e:
        logger.error(f"Error getting scan results: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error'
            })
        }