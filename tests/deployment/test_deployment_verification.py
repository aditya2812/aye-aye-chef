#!/usr/bin/env python3
"""
Test script to verify the deployed Lambda function is working with ingredient-specific recipes
"""

import json
import boto3
import time

def test_lambda_function():
    """Test the deployed Lambda function directly"""
    
    lambda_client = boto3.client('lambda', region_name='us-west-2')
    function_name = 'AyeAyeStack-CreateRecipeLambda2BD8AFF3-iuqdJg0lCo0I'
    
    # Test cases to verify ingredient-specific recipes
    test_cases = [
        {
            'name': 'Banana Smoothie Test',
            'payload': {
                'httpMethod': 'POST',
                'body': json.dumps({
                    'mock_ingredients': [
                        {'name': 'banana', 'grams': 150, 'fdc_id': '173944'}
                    ],
                    'recipe_category': 'smoothie',
                    'cuisine': 'healthy',
                    'servings': 2,
                    'user_id': 'test_user_banana'
                })
            },
            'expected_titles': [
                'Creamy Banana-Oat Breakfast Smoothie',
                'Green Banana-Spinach Smoothie',
                'Cocoa Banana \'Milkshake\' (No-Peanut Base)'
            ]
        },
        {
            'name': 'Blueberry Smoothie Test',
            'payload': {
                'httpMethod': 'POST',
                'body': json.dumps({
                    'mock_ingredients': [
                        {'name': 'blueberry', 'grams': 100, 'fdc_id': '171711'}
                    ],
                    'recipe_category': 'smoothie',
                    'cuisine': 'healthy',
                    'servings': 2,
                    'user_id': 'test_user_blueberry'
                })
            },
            'expected_titles': [
                'Antioxidant Blueberry-Spinach Power Smoothie',
                'Protein-Packed Blueberry Vanilla Smoothie',
                'Refreshing Blueberry-Lemon Mint Cooler'
            ]
        },
        {
            'name': 'Italian Chicken Test',
            'payload': {
                'httpMethod': 'POST',
                'body': json.dumps({
                    'mock_ingredients': [
                        {'name': 'chicken', 'grams': 300, 'fdc_id': '171477'}
                    ],
                    'recipe_category': 'cuisine',
                    'cuisine': 'italian',
                    'servings': 2,
                    'user_id': 'test_user_chicken'
                })
            },
            'expected_titles': [
                'Chicken Parmigiana with Fresh Basil',
                'Tuscan Chicken with Spinach and Sun-Dried Tomatoes',
                'Italian Herb-Crusted Chicken Piccata'
            ]
        }
    ]
    
    print("🧪 TESTING DEPLOYED LAMBDA FUNCTION")
    print("=" * 60)
    
    all_tests_passed = True
    
    for test_case in test_cases:
        print(f"\n🔍 Testing: {test_case['name']}")
        print("-" * 40)
        
        try:
            # Invoke the Lambda function
            response = lambda_client.invoke(
                FunctionName=function_name,
                InvocationType='RequestResponse',
                Payload=json.dumps(test_case['payload'])
            )
            
            # Parse the response
            response_payload = json.loads(response['Payload'].read())
            
            if response_payload.get('statusCode') == 200:
                body = json.loads(response_payload['body'])
                
                if 'recipes' in body:
                    recipes = body['recipes']
                    print(f"✅ Got {len(recipes)} recipes")
                    
                    # Check recipe titles
                    actual_titles = [recipe.get('title', 'No Title') for recipe in recipes]
                    
                    print("📋 Recipe Titles:")
                    for i, title in enumerate(actual_titles, 1):
                        print(f"  {i}. {title}")
                    
                    # Verify we got ingredient-specific recipes (not generic ones)
                    has_specific_recipes = False
                    for title in actual_titles:
                        if any(expected in title for expected in test_case['expected_titles']):
                            has_specific_recipes = True
                            break
                    
                    if has_specific_recipes:
                        print("✅ SUCCESS: Got ingredient-specific recipes!")
                    else:
                        print("❌ FAILURE: Still getting generic recipes")
                        print(f"Expected one of: {test_case['expected_titles']}")
                        all_tests_passed = False
                        
                    # Check for old template patterns
                    generic_patterns = ['Recipe 1', 'Recipe 2', 'Recipe 3', 'Simple Test Recipe']
                    has_generic = any(pattern in title for title in actual_titles for pattern in generic_patterns)
                    
                    if has_generic:
                        print("❌ WARNING: Still seeing generic recipe names")
                        all_tests_passed = False
                    else:
                        print("✅ No generic template names found")
                        
                else:
                    print("❌ No recipes in response")
                    print(f"Response body: {body}")
                    all_tests_passed = False
            else:
                print(f"❌ Lambda returned error: {response_payload.get('statusCode')}")
                print(f"Error: {response_payload.get('body')}")
                all_tests_passed = False
                
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
            all_tests_passed = False
    
    print("\n" + "=" * 60)
    if all_tests_passed:
        print("🎉 ALL TESTS PASSED! Deployment is successful!")
        print("✅ Ingredient-specific recipes are working correctly")
    else:
        print("❌ SOME TESTS FAILED! Check the issues above")
        print("🔧 You may need to:")
        print("   - Wait a few minutes for Lambda to update")
        print("   - Check if the correct function was deployed")
        print("   - Verify the code changes are in the deployed version")
    
    return all_tests_passed

if __name__ == "__main__":
    test_lambda_function()