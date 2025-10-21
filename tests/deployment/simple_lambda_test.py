#!/usr/bin/env python3
"""
Simple test to check Lambda function response
"""

import json
import boto3

def test_lambda_simple():
    """Simple test of the Lambda function"""
    
    lambda_client = boto3.client('lambda', region_name='us-west-2')
    function_name = 'AyeAyeStack-CreateRecipeLambda2BD8AFF3-iuqdJg0lCo0I'
    
    # Simple test payload
    payload = {
        'httpMethod': 'POST',
        'body': json.dumps({
            'test_mode': True,
            'servings': 2,
            'user_id': 'test_user'
        })
    }
    
    print("🧪 Testing Lambda function with simple payload...")
    
    try:
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )
        
        # Get the response
        response_payload = json.loads(response['Payload'].read())
        
        print(f"📊 Status Code: {response_payload.get('statusCode')}")
        print(f"📋 Response Keys: {list(response_payload.keys())}")
        
        if response_payload.get('statusCode') == 200:
            body = json.loads(response_payload['body'])
            print(f"✅ Success! Body keys: {list(body.keys())}")
            
            if 'recipes' in body:
                recipes = body['recipes']
                print(f"🍽️ Got {len(recipes)} recipes:")
                for i, recipe in enumerate(recipes, 1):
                    title = recipe.get('title', 'No Title')
                    print(f"  {i}. {title}")
            else:
                print("❌ No recipes in response")
                print(f"Body: {body}")
        else:
            print(f"❌ Error response: {response_payload}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_lambda_simple()