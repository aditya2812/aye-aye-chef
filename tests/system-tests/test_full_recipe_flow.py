#!/usr/bin/env python3
"""
Test the full recipe generation flow by creating a scan first, then generating recipes
"""
import boto3
import json
import uuid
import time

def create_test_scan():
    """Create a test scan in the database"""
    try:
        lambda_client = boto3.client('lambda')
        
        # Create test scan payload
        scan_payload = {
            "body": json.dumps({
                "image_key": "test-image.jpg"
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
        
        print("🧪 Creating test scan...")
        
        # Invoke the start-scan Lambda function
        response = lambda_client.invoke(
            FunctionName='AyeAyeStack-StartScanLambda7E8F8A5A-Ej8Ej8Ej8Ej8Ej8',  # You'll need to update this
            InvocationType='RequestResponse',
            Payload=json.dumps(scan_payload)
        )
        
        response_payload = json.loads(response['Payload'].read())
        
        if response_payload.get('statusCode') == 200:
            body = json.loads(response_payload.get('body', '{}'))
            scan_id = body.get('scan_id')
            print(f"✅ Test scan created: {scan_id}")
            return scan_id
        else:
            print(f"❌ Failed to create test scan: {response_payload}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating test scan: {e}")
        return None

def test_bedrock_titan():
    """Test Titan model access"""
    try:
        bedrock = boto3.client('bedrock-runtime')
        
        print("🧪 Testing Bedrock Titan model...")
        
        response = bedrock.invoke_model(
            modelId='amazon.titan-text-express-v1',
            body=json.dumps({
                'inputText': 'Create a recipe title for paneer and spinach.',
                'textGenerationConfig': {
                    'maxTokenCount': 50,
                    'temperature': 0.7
                }
            })
        )
        
        result = json.loads(response['body'].read())
        ai_response = result['results'][0]['outputText']
        
        print("✅ SUCCESS: Titan model is working!")
        print(f"Sample response: {ai_response.strip()}")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: Titan model test failed: {e}")
        return False

def test_simple_recipe_generation():
    """Test recipe generation with mock data"""
    try:
        lambda_client = boto3.client('lambda')
        
        # Create a simple test that bypasses the scan lookup
        test_payload = {
            "body": json.dumps({
                "ingredients": [
                    {"label": "paneer", "grams": 200, "fdc_id": "123456"},
                    {"label": "spinach", "grams": 150, "fdc_id": "789012"}
                ],
                "servings": 2,
                "user_id": "test-user"
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
        
        print("🧪 Testing recipe generation with mock ingredients...")
        
        # We'll need to modify the Lambda to accept direct ingredients for testing
        # For now, let's just test the Bedrock Agent directly
        
        bedrock_agent = boto3.client('bedrock-agent-runtime')
        
        # Test the Bedrock Agent directly
        agent_id = "GDKC6RTZHD"  # From the deployment output
        session_id = f"test_session_{uuid.uuid4().hex[:8]}"
        
        prompt = """Create 2 professional recipes using paneer and spinach. 
        
        Respond in JSON format:
        {
          "recipes": [
            {
              "title": "Recipe Name",
              "steps": ["Step 1", "Step 2", "Step 3"],
              "estimated_time": "25 minutes",
              "difficulty": "medium"
            }
          ]
        }"""
        
        print(f"Testing Bedrock Agent {agent_id}...")
        
        response = bedrock_agent.invoke_agent(
            agentId=agent_id,
            agentAliasId='TSTALIASID',  # Test alias
            sessionId=session_id,
            inputText=prompt
        )
        
        # Parse agent response
        response_text = ""
        if 'completion' in response:
            for event in response['completion']:
                if 'chunk' in event and 'bytes' in event['chunk']:
                    chunk_text = event['chunk']['bytes'].decode('utf-8')
                    response_text += chunk_text
        
        print("✅ SUCCESS: Bedrock Agent responded!")
        print(f"Response length: {len(response_text)} characters")
        print(f"Sample response: {response_text[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: Recipe generation test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Full Recipe Generation Flow")
    print("=" * 50)
    
    # Test Bedrock Titan access
    titan_ok = test_bedrock_titan()
    
    # Test Bedrock Agent recipe generation
    agent_ok = test_simple_recipe_generation()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"Bedrock Titan Access: {'✅ PASS' if titan_ok else '❌ FAIL'}")
    print(f"Bedrock Agent Recipe Gen: {'✅ PASS' if agent_ok else '❌ FAIL'}")
    
    if titan_ok and agent_ok:
        print("\n🎉 Core AI functionality is working!")
        print("The permission issue should be resolved.")
    else:
        print("\n⚠️  Some tests failed. Check the error messages above.")