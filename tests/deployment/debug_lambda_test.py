#!/usr/bin/env python3
"""
Debug test to see Lambda logs
"""

import json
import boto3
import time

def test_with_logs():
    """Test Lambda and check logs"""
    
    lambda_client = boto3.client('lambda', region_name='us-west-2')
    logs_client = boto3.client('logs', region_name='us-west-2')
    function_name = 'AyeAyeStack-CreateRecipeLambda2BD8AFF3-iuqdJg0lCo0I'
    log_group = f'/aws/lambda/{function_name}'
    
    # Test with banana smoothie
    payload = {
        'httpMethod': 'POST',
        'body': json.dumps({
            'mock_ingredients': [
                {'name': 'banana', 'grams': 150, 'fdc_id': '173944'}
            ],
            'recipe_category': 'smoothie',
            'cuisine': 'healthy',
            'servings': 2,
            'user_id': 'test_user_banana_debug'
        })
    }
    
    print("🍌 Testing Banana Smoothie with Debug Logging...")
    
    # Get current time for log filtering
    start_time = int(time.time() * 1000)
    
    try:
        # Invoke Lambda
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )
        
        response_payload = json.loads(response['Payload'].read())
        print(f"📊 Lambda Response Status: {response_payload.get('statusCode')}")
        
        if response_payload.get('statusCode') == 200:
            body = json.loads(response_payload['body'])
            recipes = body.get('recipes', [])
            print(f"🍽️ Got {len(recipes)} recipes:")
            for i, recipe in enumerate(recipes, 1):
                print(f"  {i}. {recipe.get('title', 'No Title')}")
        
        # Wait a moment for logs to be available
        time.sleep(3)
        
        # Get recent log streams
        log_streams = logs_client.describe_log_streams(
            logGroupName=log_group,
            orderBy='LastEventTime',
            descending=True,
            limit=1
        )
        
        if log_streams['logStreams']:
            stream_name = log_streams['logStreams'][0]['logStreamName']
            
            # Get recent log events
            log_events = logs_client.get_log_events(
                logGroupName=log_group,
                logStreamName=stream_name,
                startTime=start_time
            )
            
            print("\n📋 Recent Lambda Logs:")
            print("-" * 50)
            for event in log_events['events']:
                message = event['message'].strip()
                if any(keyword in message for keyword in ['🎯', '✅', '❌', '🔄', '🍌', 'ingredient', 'recipe', 'ERROR']):
                    print(message)
        
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

if __name__ == "__main__":
    test_with_logs()