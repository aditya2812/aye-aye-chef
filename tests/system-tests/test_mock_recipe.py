#!/usr/bin/env python3
"""
Test recipe generation with mock ingredients to debug the 500 error
"""
import boto3
import json

def test_mock_recipe_generation():
    """Test recipe generation with mock ingredients"""
    try:
        lambda_client = boto3.client('lambda')
        
        print("🧪 Testing mock recipe generation...")
        
        # Simple mock payload
        payload = {
            "body": json.dumps({
                "mock_ingredients": [
                    {"label": "paneer", "grams": 200, "fdc_id": "123456"},
                    {"label": "spinach", "grams": 150, "fdc_id": "789012"}
                ],
                "servings": 2
            }),
            "headers": {
                "Authorization": "Bearer test-token",
                "Content-Type": "application/json"
            },
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "sub": "test-user-id",
                        "email": "test@example.com"
                    }
                }
            }
        }
        
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = lambda_client.invoke(
            FunctionName='AyeAyeStack-CreateRecipeLambda2BD8AFF3-iuqdJg0lCo0I',
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )
        
        response_payload = json.loads(response['Payload'].read())
        
        print(f"\nResponse Status: {response_payload.get('statusCode', 'Unknown')}")
        print(f"Full Response: {json.dumps(response_payload, indent=2)}")
        
        if response_payload.get('statusCode') == 200:
            body = json.loads(response_payload.get('body', '{}'))
            print(f"\n✅ SUCCESS!")
            print(f"Recipe IDs: {body.get('recipe_ids', [])}")
            print(f"Number of recipes: {len(body.get('recipes', []))}")
            return True
        else:
            print(f"\n❌ FAILED!")
            if 'errorMessage' in response_payload:
                print(f"Error: {response_payload['errorMessage']}")
            if 'stackTrace' in response_payload:
                print(f"Stack trace: {response_payload['stackTrace']}")
            return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_mock_recipe_generation()
    
    if success:
        print("\n🎉 Mock recipe generation works!")
    else:
        print("\n⚠️  Mock recipe generation failed - check error above")