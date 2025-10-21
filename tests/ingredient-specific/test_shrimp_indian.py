#!/usr/bin/env python3
"""
Test shrimp + indian cuisine to verify the fix
"""

import json
import boto3

def test_shrimp_indian():
    """Test shrimp with Indian cuisine"""
    
    lambda_client = boto3.client('lambda', region_name='us-west-2')
    function_name = 'AyeAyeStack-CreateRecipeLambda2BD8AFF3-iuqdJg0lCo0I'
    
    # Test with shrimp + indian
    payload = {
        'httpMethod': 'POST',
        'body': json.dumps({
            'mock_ingredients': [
                {'name': 'shrimp', 'grams': 300, 'fdc_id': '175180'}
            ],
            'recipe_category': 'cuisine',
            'cuisine': 'indian',
            'servings': 2,
            'user_id': 'test_user_shrimp_indian'
        })
    }
    
    print("🍤 Testing Shrimp + Indian Cuisine...")
    
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
                    ingredients = recipe.get('ingredients', [])
                    
                    print(f"\n{i}. 🍽️ {title}")
                    print(f"   🏷️ Tags: {', '.join(tags)}")
                    print(f"   🥘 Key Ingredients:")
                    
                    # Show first few ingredients to verify Indian-ness
                    for ing in ingredients[:4]:
                        name = ing.get('name', '')
                        amount = ing.get('amount', '')
                        print(f"     • {amount} {name}")
                
                # Check if we got authentic Indian recipes
                titles = [recipe.get('title', '') for recipe in recipes]
                
                expected_indian_elements = [
                    'Goan', 'Tandoori', 'Kerala', 'Curry', 'Masala', 'Coconut'
                ]
                
                found_indian = any(element in title for title in titles for element in expected_indian_elements)
                
                if found_indian:
                    print("\n🎉 SUCCESS! Got authentic Indian shrimp recipes!")
                    
                    # Check for Indian ingredients
                    all_ingredients = []
                    for recipe in recipes:
                        for ing in recipe.get('ingredients', []):
                            all_ingredients.append(ing.get('name', '').lower())
                    
                    indian_ingredients = [
                        'garam masala', 'turmeric', 'curry leaves', 'coconut milk', 
                        'ginger-garlic paste', 'tandoori masala', 'ghee', 'cumin'
                    ]
                    
                    found_indian_ingredients = [ing for ing in indian_ingredients if any(ing in all_ing for all_ing in all_ingredients)]
                    
                    if found_indian_ingredients:
                        print(f"✅ Found Indian ingredients: {', '.join(found_indian_ingredients)}")
                    else:
                        print("⚠️ No traditional Indian ingredients found")
                        
                else:
                    print("❌ Still getting non-Indian recipes")
                    print(f"Got titles: {titles}")
                    
            else:
                print("❌ No recipes in response")
        else:
            print(f"❌ Error: {response_payload}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

if __name__ == "__main__":
    test_shrimp_indian()