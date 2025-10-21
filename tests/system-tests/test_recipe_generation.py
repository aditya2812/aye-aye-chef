#!/usr/bin/env python3
"""
Test script to verify recipe generation is working after permission fix
"""
import boto3
import json
import uuid

def test_recipe_generation():
    """Test the create-recipe Lambda function"""
    try:
        lambda_client = boto3.client('lambda')
        
        # Create test payload similar to what the mobile app would send
        test_payload = {
            "body": json.dumps({
                "scan_id": "test-scan-123",
                "user_id": "test-user",
                "servings": 2
            }),
            "headers": {
                "Authorization": "Bearer test-token"
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
        
        print("🧪 Testing recipe generation Lambda function...")
        print(f"Payload: {json.dumps(test_payload, indent=2)}")
        
        # Invoke the create-recipe Lambda function
        response = lambda_client.invoke(
            FunctionName='AyeAyeStack-CreateRecipeLambda2BD8AFF3-iuqdJg0lCo0I',
            InvocationType='RequestResponse',
            Payload=json.dumps(test_payload)
        )
        
        # Parse response
        response_payload = json.loads(response['Payload'].read())
        
        print(f"✅ Lambda invocation successful!")
        print(f"Status Code: {response_payload.get('statusCode', 'Unknown')}")
        
        if response_payload.get('statusCode') == 200:
            body = json.loads(response_payload.get('body', '{}'))
            print(f"✅ Recipe generation successful!")
            print(f"Generated {len(body.get('recipes', []))} recipes")
            
            for i, recipe in enumerate(body.get('recipes', [])[:2]):  # Show first 2 recipes
                print(f"\n📝 Recipe {i+1}: {recipe.get('title', 'Untitled')}")
                print(f"   Time: {recipe.get('estimated_time', 'Unknown')}")
                print(f"   Steps: {len(recipe.get('steps', []))} steps")
        else:
            print(f"❌ Recipe generation failed:")
            print(f"Response: {json.dumps(response_payload, indent=2)}")
            
        return response_payload.get('statusCode') == 200
        
    except Exception as e:
        print(f"❌ FAILED: Recipe generation test failed: {e}")
        return False

def test_bedrock_direct():
    """Test direct Bedrock access to verify permissions"""
    try:
        bedrock = boto3.client('bedrock-runtime')
        
        print("\n🧪 Testing direct Bedrock Titan access...")
        
        response = bedrock.invoke_model(
            modelId='amazon.titan-text-express-v1',
            body=json.dumps({
                'inputText': 'Create a simple recipe title for paneer and spinach. Just respond with the title only.',
                'textGenerationConfig': {
                    'maxTokenCount': 100,
                    'temperature': 0.7
                }
            })
        )
        
        result = json.loads(response['body'].read())
        ai_response = result['results'][0]['outputText']
        
        print("✅ SUCCESS: Direct Bedrock Titan access is working!")
        print(f"Sample recipe title: {ai_response}")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: Direct Bedrock access failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Recipe Generation System")
    print("=" * 50)
    
    # Test direct Bedrock access first
    bedrock_ok = test_bedrock_direct()
    
    # Test Lambda function
    lambda_ok = test_recipe_generation()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"Direct Bedrock Access: {'✅ PASS' if bedrock_ok else '❌ FAIL'}")
    print(f"Lambda Recipe Generation: {'✅ PASS' if lambda_ok else '❌ FAIL'}")
    
    if bedrock_ok and lambda_ok:
        print("\n🎉 All tests passed! Recipe generation should be working now.")
    else:
        print("\n⚠️  Some tests failed. Check the error messages above.")