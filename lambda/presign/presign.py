import json
import boto3
import uuid
import os
from datetime import datetime, timedelta

s3_client = boto3.client('s3')

def handler(event, context):
    try:
        # Parse request
        body = json.loads(event['body'])
        content_type = body.get('contentType', 'image/jpeg')
        
        # Get user ID from JWT
        user_id = event['requestContext']['authorizer']['claims']['sub']
        
        # Generate S3 key
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_id = str(uuid.uuid4())[:8]
        s3_key = f"uploads/{user_id}/scan_{timestamp}_{file_id}.jpg"
        
        # Generate presigned URL
        bucket_name = os.environ['IMAGES_BUCKET']
        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': bucket_name,
                'Key': s3_key,
                'ContentType': content_type
            },
            ExpiresIn=300  # 5 minutes
        )
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'uploadUrl': presigned_url,
                's3Key': s3_key
            })
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
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