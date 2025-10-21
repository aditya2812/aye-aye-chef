#!/usr/bin/env python3
"""
Test the exact mobile app flow to debug the "Failed to generate recipe" error
"""
import boto3
import json
import uuid

def test_mobile_app_recipe_generation():
    """Test the exact flow that the mobile app uses"""
    try:
        lambda_client = boto3.client('lambda')
        
        # First, let's create a test scan in the database
        print("🧪 Step 1: Creating a test scan...")
        
        # Create test scan payload (simulating what start-scan would create)
        scan_payload = {
            "body": json.dumps({
                "image_key": "test-paneer-spinach.jpg"
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
        
        # Invoke start-scan to create a scan
        start_scan_response = lambda_client.invoke(
            FunctionName='AyeAyeStack-StartScanLambda45E999A6-XzmkXMkHPCug',
            InvocationType='RequestResponse',
            Payload=json.dumps(scan_payload)
        )
        
        start_scan_result = json.loads(start_scan_response['Payload'].read())
        print(f"Start scan result: {start_scan_result}")
        
        if start_scan_result.get('statusCode') != 200:
            print("❌ Failed to create test scan, using mock scan_id")
            scan_id = "test-scan-123"
        else:
            scan_body = json.loads(start_scan_result.get('body', '{}'))
            scan_id = scan_body.get('scan_id', 'test-scan-123')
        
        print(f"✅ Using scan_id: {scan_id}")
        
        # Step 2: Now test the exact mobile app recipe generation call
        print("\n🧪 Step 2: Testing mobile app recipe generation...")
        
        # This is exactly what the mobile app sends
        mobile_app_payload = {
            "body": json.dumps({
                "scan_id": scan_id,
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
            },
            "httpMethod": "POST",
            "path": "/recipes"
        }
        
        print(f"Mobile app payload: {json.dumps(mobile_app_payload, indent=2)}")
        
        # Invoke create-recipe Lambda
        response = lambda_client.invoke(
            FunctionName='AyeAyeStack-CreateRecipeLambda2BD8AFF3-iuqdJg0lCo0I',
            InvocationType='RequestResponse',
            Payload=json.dumps(mobile_app_payload)
        )
        
        response_payload = json.loads(response['Payload'].read())
        
        print(f"\n📊 Lambda Response:")
        print(f"Status Code: {response_payload.get('statusCode', 'Unknown')}")
        print(f"Response: {json.dumps(response_payload, indent=2)}")
        
        if response_payload.get('statusCode') == 200:
            body = json.loads(response_payload.get('body', '{}'))
            print(f"✅ SUCCESS: Recipe generation worked!")
            print(f"Recipe IDs: {body.get('recipe_ids', [])}")
            print(f"Number of recipes: {len(body.get('recipes', []))}")
            
            for i, recipe in enumerate(body.get('recipes', [])[:2]):
                print(f"\n📝 Recipe {i+1}: {recipe.get('title', 'Untitled')}")
                print(f"   Tags: {recipe.get('tags', [])}")
        else:
            print(f"❌ FAILED: {response_payload}")
            
            # Let's check the error details
            error_body = response_payload.get('body', '{}')
            if isinstance(error_body, str):
                try:
                    error_data = json.loads(error_body)
                    print(f"Error details: {error_data}")
                except:
                    print(f"Raw error: {error_body}")
        
        return response_payload.get('statusCode') == 200
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_direct_recipe_creation():
    """Test recipe creation with mock ingredients"""
    try:
        lambda_client = boto3.client('lambda')
        
        print("\n🧪 Testing direct recipe creation with mock data...")
        
        # Create a payload that bypasses scan lookup
        direct_payload = {
            "body": json.dumps({
                "mock_ingredients": [
                    {"label": "paneer", "grams": 200, "fdc_id": "123456"},
                    {"label": "spinach", "grams": 150, "fdc_id": "789012"}
                ],
                "servings": 2,
                "user_id": "test-user"
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
        
        response = lambda_client.invoke(
            FunctionName='AyeAyeStack-CreateRecipeLambda2BD8AFF3-iuqdJg0lCo0I',
            InvocationType='RequestResponse',
            Payload=json.dumps(direct_payload)
        )
        
        response_payload = json.loads(response['Payload'].read())
        print(f"Direct test result: {response_payload.get('statusCode', 'Unknown')}")
        
        return response_payload.get('statusCode') == 200
        
    except Exception as e:
        print(f"❌ Direct test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Mobile App Recipe Generation Flow")
    print("=" * 60)
    
    # Test the exact mobile app flow
    mobile_app_ok = test_mobile_app_recipe_generation()
    
    # Test direct recipe creation
    direct_ok = test_direct_recipe_creation()
    
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    print(f"Mobile App Flow:     {'✅ PASS' if mobile_app_ok else '❌ FAIL'}")
    print(f"Direct Recipe Test:  {'✅ PASS' if direct_ok else '❌ FAIL'}")
    
    if mobile_app_ok:
        print("\n🎉 Mobile app recipe generation is working!")
    else:
        print("\n⚠️  Mobile app flow failed - check the error details above")
        print("This explains why users see 'Failed to generate recipe'")