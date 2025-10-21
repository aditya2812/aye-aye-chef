#!/usr/bin/env python3
"""
Test current functionality before cleanup to ensure we don't break anything
"""

import json
import boto3

def test_current_functionality():
    """Test all current working functionality"""
    
    lambda_client = boto3.client('lambda', region_name='us-west-2')
    function_name = 'AyeAyeStack-CreateRecipeLambda2BD8AFF3-iuqdJg0lCo0I'
    
    test_cases = [
        {
            'name': 'Banana Smoothie',
            'payload': {
                'httpMethod': 'POST',
                'body': json.dumps({
                    'mock_ingredients': [{'name': 'banana', 'grams': 150, 'fdc_id': '173944'}],
                    'recipe_category': 'smoothie',
                    'cuisine': 'healthy',
                    'servings': 2,
                    'user_id': 'test_banana'
                })
            },
            'expected_count': 3,
            'expected_keywords': ['Banana', 'Smoothie']
        },
        {
            'name': 'Indian Shrimp',
            'payload': {
                'httpMethod': 'POST',
                'body': json.dumps({
                    'mock_ingredients': [{'name': 'shrimp', 'grams': 300, 'fdc_id': '175180'}],
                    'recipe_category': 'cuisine',
                    'cuisine': 'indian',
                    'servings': 2,
                    'user_id': 'test_shrimp'
                })
            },
            'expected_count': 3,
            'expected_keywords': ['Shrimp', 'Goan', 'Tandoori', 'Kerala']
        },
        {
            'name': 'Italian Chicken',
            'payload': {
                'httpMethod': 'POST',
                'body': json.dumps({
                    'mock_ingredients': [{'name': 'chicken', 'grams': 400, 'fdc_id': '171477'}],
                    'recipe_category': 'cuisine',
                    'cuisine': 'italian',
                    'servings': 2,
                    'user_id': 'test_chicken'
                })
            },
            'expected_count': 3,
            'expected_keywords': ['Chicken', 'Italian', 'Parmigiana', 'Tuscan']
        }
    ]
    
    print("🧪 TESTING CURRENT FUNCTIONALITY BEFORE CLEANUP")
    print("=" * 60)
    
    all_passed = True
    
    for test_case in test_cases:
        print(f"\n🔍 Testing: {test_case['name']}")
        
        try:
            response = lambda_client.invoke(
                FunctionName=function_name,
                InvocationType='RequestResponse',
                Payload=json.dumps(test_case['payload'])
            )
            
            response_payload = json.loads(response['Payload'].read())
            
            if response_payload.get('statusCode') == 200:
                body = json.loads(response_payload['body'])
                recipes = body.get('recipes', [])
                
                # Check recipe count
                if len(recipes) == test_case['expected_count']:
                    print(f"  ✅ Recipe count: {len(recipes)}")
                else:
                    print(f"  ❌ Recipe count: {len(recipes)} (expected {test_case['expected_count']})")
                    all_passed = False
                
                # Check recipe titles
                titles = [recipe.get('title', '') for recipe in recipes]
                print(f"  📋 Titles: {titles}")
                
                # Check for expected keywords
                all_titles_text = ' '.join(titles)
                found_keywords = [kw for kw in test_case['expected_keywords'] if kw in all_titles_text]
                
                if found_keywords:
                    print(f"  ✅ Found keywords: {found_keywords}")
                else:
                    print(f"  ❌ Missing expected keywords: {test_case['expected_keywords']}")
                    all_passed = False
                    
            else:
                print(f"  ❌ Error response: {response_payload.get('statusCode')}")
                all_passed = False
                
        except Exception as e:
            print(f"  ❌ Exception: {str(e)}")
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED - Safe to proceed with cleanup")
    else:
        print("❌ SOME TESTS FAILED - Do not proceed with cleanup")
    
    return all_passed

if __name__ == "__main__":
    test_current_functionality()