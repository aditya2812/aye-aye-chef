#!/usr/bin/env python3
"""
Test the complete mobile app flow: scan → confirm → generate recipe
"""
import boto3
import json
import time

def test_complete_mobile_flow():
    """Test the complete flow that the mobile app uses"""
    try:
        lambda_client = boto3.client('lambda')
        
        print("🚀 Testing Complete Mobile App Flow")
        print("=" * 50)
        
        # Step 1: Create a scan (simulate image upload and processing)
        print("\n📱 Step 1: Creating scan...")
        
        scan_payload = {
            "body": json.dumps({
                "image_key": "test-paneer-spinach.jpg"
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
        
        start_scan_response = lambda_client.invoke(
            FunctionName='AyeAyeStack-StartScanLambda45E999A6-XzmkXMkHPCug',
            InvocationType='RequestResponse',
            Payload=json.dumps(scan_payload)
        )
        
        start_scan_result = json.loads(start_scan_response['Payload'].read())
        print(f"Start scan response: {start_scan_result.get('statusCode', 'Unknown')}")
        
        if start_scan_result.get('statusCode') != 200:
            print(f"❌ Scan creation failed: {start_scan_result}")
            return False
        
        scan_body = json.loads(start_scan_result.get('body', '{}'))
        scan_id = scan_body.get('scan_id')
        
        if not scan_id:
            print("❌ No scan_id returned from start-scan")
            return False
            
        print(f"✅ Scan created: {scan_id}")
        
        # Step 2: Wait for scan processing and check status
        print(f"\n🔍 Step 2: Checking scan status...")
        
        # Wait a bit for processing
        time.sleep(2)
        
        get_scan_payload = {
            "pathParameters": {"id": scan_id},
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
        
        get_scan_response = lambda_client.invoke(
            FunctionName='AyeAyeStack-GetScanLambda2E357DCC-plYPaZME1sVq',
            InvocationType='RequestResponse',
            Payload=json.dumps(get_scan_payload)
        )
        
        get_scan_result = json.loads(get_scan_response['Payload'].read())
        print(f"Get scan response: {get_scan_result.get('statusCode', 'Unknown')}")
        
        if get_scan_result.get('statusCode') != 200:
            print(f"❌ Get scan failed: {get_scan_result}")
            return False
        
        scan_data = json.loads(get_scan_result.get('body', '{}'))
        print(f"✅ Scan status: {scan_data.get('status', 'unknown')}")
        print(f"   Items found: {len(scan_data.get('items', []))}")
        
        # Step 3: Confirm the scan (simulate user confirming ingredients)
        print(f"\n✅ Step 3: Confirming scan...")
        
        # Get the detected items and confirm them
        detected_items = scan_data.get('items', [])
        if not detected_items:
            # Add mock items if none detected
            detected_items = [
                {"label": "paneer", "grams": 200, "fdc_id": "123456"},
                {"label": "spinach", "grams": 150, "fdc_id": "789012"}
            ]
            print("   Using mock items since none were detected")
        
        confirm_payload = {
            "pathParameters": {"id": scan_id},
            "body": json.dumps({
                "confirmed_items": detected_items
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
        
        confirm_response = lambda_client.invoke(
            FunctionName='AyeAyeStack-ConfirmScanLambda3F02AE3F-C9T59KJLFNVB',
            InvocationType='RequestResponse',
            Payload=json.dumps(confirm_payload)
        )
        
        confirm_result = json.loads(confirm_response['Payload'].read())
        print(f"Confirm scan response: {confirm_result.get('statusCode', 'Unknown')}")
        
        if confirm_result.get('statusCode') != 200:
            print(f"❌ Confirm scan failed: {confirm_result}")
            return False
        
        print(f"✅ Scan confirmed successfully")
        
        # Step 4: Generate recipe (this is where the mobile app fails)
        print(f"\n🍳 Step 4: Generating recipe...")
        
        recipe_payload = {
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
            }
        }
        
        recipe_response = lambda_client.invoke(
            FunctionName='AyeAyeStack-CreateRecipeLambda2BD8AFF3-iuqdJg0lCo0I',
            InvocationType='RequestResponse',
            Payload=json.dumps(recipe_payload)
        )
        
        recipe_result = json.loads(recipe_response['Payload'].read())
        print(f"Recipe generation response: {recipe_result.get('statusCode', 'Unknown')}")
        
        if recipe_result.get('statusCode') == 200:
            recipe_body = json.loads(recipe_result.get('body', '{}'))
            print(f"✅ SUCCESS: Recipe generation worked!")
            print(f"   Recipe IDs: {recipe_body.get('recipe_ids', [])}")
            print(f"   Number of recipes: {len(recipe_body.get('recipes', []))}")
            
            for i, recipe in enumerate(recipe_body.get('recipes', [])[:2]):
                print(f"   Recipe {i+1}: {recipe.get('title', 'Untitled')}")
            
            return True
        else:
            print(f"❌ Recipe generation failed: {recipe_result}")
            recipe_error = json.loads(recipe_result.get('body', '{}'))
            print(f"   Error: {recipe_error.get('error', 'Unknown error')}")
            return False
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_complete_mobile_flow()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 COMPLETE MOBILE FLOW: SUCCESS!")
        print("✅ The mobile app should work correctly")
    else:
        print("❌ COMPLETE MOBILE FLOW: FAILED!")
        print("⚠️  This explains why users see 'Failed to generate recipe'")
        print("🔧 Check the error details above to identify the issue")