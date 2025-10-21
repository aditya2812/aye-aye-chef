import json
import boto3
import os
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

rds_client = boto3.client('rds-data')

def handler(event, context):
    """Lambda handler for getting recipe details"""
    try:
        # Get recipe ID from path parameters
        recipe_id = event['pathParameters']['id']
        
        # Get user ID from JWT
        user_id = event['requestContext']['authorizer']['claims']['sub']
        
        logger.info(f"Getting recipe {recipe_id} for user {user_id}")
        
        # Database connection info
        db_secret_arn = os.environ['DB_SECRET_ARN']
        db_cluster_arn = os.environ['DB_CLUSTER_ARN']
        
        # Get recipe data
        try:
            recipe_response = rds_client.execute_statement(
                resourceArn=db_cluster_arn,
                secretArn=db_secret_arn,
                database='ayeaye',
                sql="""
                    SELECT 
                        r.id::text,
                        r.title,
                        r.json_payload,
                        r.nutrition,
                        r.facts_snapshot,
                        r.created_at,
                        s.id::text as scan_id
                    FROM recipes r
                    LEFT JOIN scans s ON s.id = r.scan_id
                    WHERE r.id = :recipe_id::uuid AND r.user_id = :user_id::uuid
                """,
                parameters=[
                    {'name': 'recipe_id', 'value': {'stringValue': recipe_id}},
                    {'name': 'user_id', 'value': {'stringValue': user_id}}
                ]
            )
            
            if not recipe_response['records']:
                return {
                    'statusCode': 404,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'error': 'Recipe not found'
                    })
                }
            
            record = recipe_response['records'][0]
            
            # Parse JSON fields
            json_payload = json.loads(record[2]['stringValue']) if record[2] and record[2].get('stringValue') else {}
            nutrition = json.loads(record[3]['stringValue']) if record[3] and record[3].get('stringValue') else {}
            facts_snapshot = json.loads(record[4]['stringValue']) if record[4] and record[4].get('stringValue') else {}
            
            recipe_data = {
                'recipe_id': record[0]['stringValue'],
                'title': record[1]['stringValue'],
                'scan_id': record[6]['stringValue'] if record[6] and record[6].get('stringValue') else None,
                'created_at': record[5]['stringValue'],
                'recipe': json_payload,
                'nutrition': nutrition,
                'facts_snapshot': facts_snapshot
            }
            
            logger.info(f"Successfully retrieved recipe: {recipe_data['title']}")
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps(recipe_data)
            }
            
        except Exception as db_error:
            logger.error(f"Database error: {str(db_error)}")
            raise
        
    except Exception as e:
        logger.error(f"Error getting recipe: {str(e)}")
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