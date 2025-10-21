#!/usr/bin/env python3
"""
Test the intelligent recipe naming system
"""
import boto3
import json

def test_intelligent_naming():
    """Test recipe generation with intelligent naming"""
    try:
        lambda_client = boto3.client('lambda')
        
        print("🧪 Testing intelligent recipe naming...")
        
        # Test with different ingredient combinations
        test_cases = [
            {
                "ingredients": ["paneer", "spinach"],
                "cuisine": "indian",
                "expected": "Palak Paneer"
            },
            {
                "ingredients": ["chicken", "tomato", "onion"],
                "cuisine": "indian", 
                "expected": "Chicken Curry with Tomato"
            },
            {
                "ingredients": ["salmon", "lemon", "herbs"],
                "cuisine": "mediterranean",
                "expected": "Mediterranean Salmon"
            }
        ]
        
        for test_case in test_cases:
            print(f"\n🔍 Testing: {test_case['ingredients']} + {test_case['cuisine']} cuisine")
            
            payload = {
                "body": json.dumps({
                    "mock_ingredients": [
                        {"label": ing, "grams": 150, "fdc_id": f"{i}123456"} 
                        for i, ing in enumerate(test_case['ingredients'])
                    ],
                    "servings": 2,
                    "cuisine": test_case['cuisine'],
                    "skill_level": "intermediate"
                }),
                "headers": {"Authorization": "Bearer test-token"},
                "requestContext": {
                    "authorizer": {"claims": {"sub": "test-user", "email": "test@example.com"}}
                }
            }
            
            response = lambda_client.invoke(
                FunctionName='AyeAyeStack-CreateRecipeLambda2BD8AFF3-iuqdJg0lCo0I',
                InvocationType='RequestResponse',
                Payload=json.dumps(payload)
            )
            
            result = json.loads(response['Payload'].read())
            
            if result.get('statusCode') == 200:
                body = json.loads(result.get('body', '{}'))
                recipes = body.get('recipes', [])
                
                print(f"✅ Generated {len(recipes)} recipes:")
                for recipe in recipes:
                    print(f"   📝 {recipe.get('title', 'Untitled')}")
                    
                # Check if naming is intelligent
                first_title = recipes[0].get('title', '') if recipes else ''
                if any(ing in first_title.lower() for ing in test_case['ingredients']):
                    print(f"   ✅ Intelligent naming: Uses actual ingredients")
                else:
                    print(f"   ⚠️  Generic naming: Doesn't use specific ingredients")
            else:
                print(f"   ❌ Failed: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Intelligent Recipe Naming")
    print("=" * 50)
    
    success = test_intelligent_naming()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Intelligent naming system tested!")
    else:
        print("⚠️  Testing failed - check errors above")