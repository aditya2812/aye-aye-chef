import json
import boto3
import os
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

rds_client = boto3.client('rds-data')

def handler(event, context):
    """Lambda handler for confirming scan results"""
    try:
        # Parse request body
        body = json.loads(event['body'])
        
        # Get scan ID from path parameters
        scan_id = event['pathParameters']['id']
        
        # Get user ID from JWT
        user_id = event['requestContext']['authorizer']['claims']['sub']
        
        logger.info(f"Confirming scan {scan_id} for user {user_id}")
        
        # Extract confirmation data
        items = body.get('items', [])
        diets = body.get('diets', [])
        cuisines = body.get('cuisines', [])
        allergens = body.get('allergens', [])
        servings = body.get('servings', 2)
        
        # Debug: Log the received items data
        logger.info(f"DEBUG: Received {len(items)} items for confirmation")
        for i, item in enumerate(items):
            logger.info(f"DEBUG: Item {i}: {item}")
        
        if not items:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'No items provided for confirmation'
                })
            }
        
        # Database connection info
        db_secret_arn = os.environ['DB_SECRET_ARN']
        db_cluster_arn = os.environ['DB_CLUSTER_ARN']
        
        # Validate scan ownership and status
        try:
            scan_response = rds_client.execute_statement(
                resourceArn=db_cluster_arn,
                secretArn=db_secret_arn,
                database='ayeaye',
                sql="""
                    SELECT status FROM scans 
                    WHERE id::text = :scan_id AND user_id::text = :user_id
                """,
                parameters=[
                    {'name': 'scan_id', 'value': {'stringValue': scan_id}},
                    {'name': 'user_id', 'value': {'stringValue': user_id}}
                ]
            )
            
            if not scan_response['records']:
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
            
            current_status = scan_response['records'][0][0]['stringValue']
            if current_status not in ['ready', 'confirmed']:
                return {
                    'statusCode': 409,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'error': f'Scan status is {current_status}, cannot confirm'
                    })
                }
                
        except Exception as validation_error:
            logger.error(f"Error validating scan: {str(validation_error)}")
            raise
        
        # Update confirmed items
        confirmed_count = 0
        for item in items:
            if not item.get('confirmed', False):
                continue
                
            fdc_id = item.get('fdc_id')
            label = item.get('label', 'unknown')
            grams = item.get('grams', 100.0)
            manually_added = item.get('manually_added', False)
            
            logger.info(f"Processing item: {label} (fdc_id: {fdc_id}, manually_added: {manually_added})")
            
            if not fdc_id:
                logger.warning(f"Skipping item without fdc_id: {item}")
                continue
            
            try:
                if manually_added:
                    # For manually added items, just insert (they have unique fdc_ids)
                    logger.info(f"Handling manually added item: {label}")
                    rds_client.execute_statement(
                        resourceArn=db_cluster_arn,
                        secretArn=db_secret_arn,
                        database='ayeaye',
                        sql="""
                            INSERT INTO scan_items (scan_id, fdc_id, label, grams, confidence, confirmed)
                            VALUES (:scan_id::uuid, :fdc_id, :label, :grams, 100.0, true)
                        """,
                        parameters=[
                            {'name': 'scan_id', 'value': {'stringValue': scan_id}},
                            {'name': 'fdc_id', 'value': {'stringValue': fdc_id}},
                            {'name': 'label', 'value': {'stringValue': label}},
                            {'name': 'grams', 'value': {'doubleValue': grams}}
                        ]
                    )
                else:
                    # For detected items, just update
                    rds_client.execute_statement(
                        resourceArn=db_cluster_arn,
                        secretArn=db_secret_arn,
                        database='ayeaye',
                        sql="""
                            UPDATE scan_items 
                            SET grams = :grams, confirmed = true
                            WHERE scan_id::text = :scan_id AND fdc_id = :fdc_id
                        """,
                        parameters=[
                            {'name': 'grams', 'value': {'doubleValue': grams}},
                            {'name': 'scan_id', 'value': {'stringValue': scan_id}},
                            {'name': 'fdc_id', 'value': {'stringValue': fdc_id}}
                        ]
                    )
                
                confirmed_count += 1
                logger.info(f"Confirmed item: {label} - {grams}g")
                
            except Exception as item_error:
                logger.error(f"Error confirming item {fdc_id}: {str(item_error)}")
                # Continue with other items
        
        # Update user preferences (optional)
        if diets or cuisines or allergens:
            try:
                # Convert arrays to PostgreSQL array format
                diets_sql = "'{" + ",".join(diets) + "}'" if diets else "'{}'::text[]"
                cuisines_sql = "'{" + ",".join(cuisines) + "}'" if cuisines else "'{}'::text[]"
                allergens_sql = "'{" + ",".join(allergens) + "}'" if allergens else "'{}'::text[]"
                
                rds_client.execute_statement(
                    resourceArn=db_cluster_arn,
                    secretArn=db_secret_arn,
                    database='ayeaye',
                    sql="""
                        UPDATE users 
                        SET diets = :diets::text[], 
                            cuisines = :cuisines::text[], 
                            allergens = :allergens::text[]
                        WHERE id = :user_id::uuid
                    """,
                    parameters=[
                        {'name': 'diets', 'value': {'stringValue': diets_sql}},
                        {'name': 'cuisines', 'value': {'stringValue': cuisines_sql}},
                        {'name': 'allergens', 'value': {'stringValue': allergens_sql}},
                        {'name': 'user_id', 'value': {'stringValue': user_id}}
                    ]
                )
                logger.info(f"Updated user preferences: diets={diets}, cuisines={cuisines}, allergens={allergens}")
                
            except Exception as prefs_error:
                logger.error(f"Error updating user preferences: {str(prefs_error)}")
                # Don't fail the whole request for preference updates
        
        # Update scan status to confirmed
        try:
            rds_client.execute_statement(
                resourceArn=db_cluster_arn,
                secretArn=db_secret_arn,
                database='ayeaye',
                sql="""
                    UPDATE scans 
                    SET status = 'confirmed'
                    WHERE id::text = :scan_id AND user_id::text = :user_id
                """,
                parameters=[
                    {'name': 'scan_id', 'value': {'stringValue': scan_id}},
                    {'name': 'user_id', 'value': {'stringValue': user_id}}
                ]
            )
            logger.info(f"Updated scan {scan_id} status to confirmed")
            
        except Exception as status_error:
            logger.error(f"Error updating scan status: {str(status_error)}")
            raise
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'scan_id': scan_id,
                'status': 'confirmed',
                'confirmed_items': confirmed_count,
                'message': 'Scan confirmed successfully'
            })
        }
        
    except Exception as e:
        logger.error(f"Error confirming scan: {str(e)}")
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