#!/usr/bin/env python3
"""
Test specific ingredient to verify new recipe generation
"""

import json
import boto3

def test_banana_smoothie():
    """Test banana smoothie generation"""
    
    lambda_client = boto3.client('lambda', region_name='us-west-2')
    function_name = 'AyeAyeStack-CreateRecipeLambda2BD8AFF3-iuqdJg0lCo0I'
    
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
            'user_id': 'test_user_banana'
        })
    }
    
    print("🍌 Testing Banana Smoothie Generation...")
    
    try:
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )
        
        response_payload = json.loads(response['Payload'].read())
        
        if response_payload.get('statusCode') == 200:
            body = json.loads(response_payload['body'])
            
            if 'recipes' in body:
                recipes = body['recipes']
                print(f"✅ Got {len(recipes)} recipes:")
                
                for i, recipe in enumerate(recipes, 1):
                    title = recipe.get('title', 'No Title')
                    tags = recipe.get('tags', [])
                    print(f"  {i}. {title}")
                    print(f"     Tags: {', '.join(tags)}")
                    print(f"     Ingredients: {len(recipe.get('ingredients', []))}")
                    print()
                
                # Check if we got the new banana-specific recipes
                titles = [recipe.get('title', '') for recipe in recipes]
                
                expected_banana_titles = [
                    'Creamy Banana-Oat Breakfast Smoothie',
                    'Green Banana-Spinach Smoothie',
                    'Cocoa Banana \'Milkshake\' (No-Peanut Base)'
                ]
                
                found_specific = any(expected in title for title in titles for expected in expected_banana_titles)
                
                if found_specific:
                    print("🎉 SUCCESS! Got ingredient-specific banana recipes!")
                else:
                    print("❌ Still getting generic recipes")
                    print(f"Expected one of: {expected_banana_titles}")
                    print(f"Got: {titles}")
                    
            else:
                print("❌ No recipes in response")
        else:
            print(f"❌ Error: {response_payload}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

if __name__ == "__main__":
    test_banana_smoothie()