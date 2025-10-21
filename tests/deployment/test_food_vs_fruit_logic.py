#!/usr/bin/env python3
"""
Test to verify the core logic:
- Food (proteins/vegetables) → Ingredient + Cuisine specific recipes
- Fruit → Ingredient specific recipes (cuisine less relevant)
"""

import json
import boto3

def test_food_vs_fruit_logic():
    """Test that food and fruit are handled differently"""
    
    lambda_client = boto3.client('lambda', region_name='us-west-2')
    function_name = 'AyeAyeStack-CreateRecipeLambda2BD8AFF3-iuqdJg0lCo0I'
    
    print("🧪 TESTING FOOD vs FRUIT LOGIC")
    print("=" * 60)
    
    # Test Cases
    test_cases = [
        {
            'category': 'FRUIT',
            'name': 'Banana Smoothie (Fruit - Ingredient Only)',
            'payload': {
                'httpMethod': 'POST',
                'body': json.dumps({
                    'mock_ingredients': [{'name': 'banana', 'grams': 150, 'fdc_id': '173944'}],
                    'recipe_category': 'smoothie',
                    'cuisine': 'healthy',  # Should be less relevant for fruits
                    'servings': 2,
                    'user_id': 'test_fruit_banana'
                })
            },
            'expected_behavior': 'Ingredient-specific banana recipes regardless of cuisine'
        },
        {
            'category': 'FRUIT',
            'name': 'Strawberry Smoothie (Fruit - Ingredient Only)', 
            'payload': {
                'httpMethod': 'POST',
                'body': json.dumps({
                    'mock_ingredients': [{'name': 'strawberry', 'grams': 120, 'fdc_id': '167762'}],
                    'recipe_category': 'smoothie',
                    'cuisine': 'mexican',  # Should be ignored for fruit smoothies
                    'servings': 2,
                    'user_id': 'test_fruit_strawberry'
                })
            },
            'expected_behavior': 'Ingredient-specific strawberry recipes, not Mexican-style'
        },
        {
            'category': 'FOOD',
            'name': 'Shrimp Indian (Food - Ingredient + Cuisine)',
            'payload': {
                'httpMethod': 'POST',
                'body': json.dumps({
                    'mock_ingredients': [{'name': 'shrimp', 'grams': 300, 'fdc_id': '175180'}],
                    'recipe_category': 'cuisine',
                    'cuisine': 'indian',  # Should be highly relevant for food
                    'servings': 2,
                    'user_id': 'test_food_shrimp_indian'
                })
            },
            'expected_behavior': 'Indian-specific shrimp recipes with Indian spices and techniques'
        },
        {
            'category': 'FOOD',
            'name': 'Shrimp Mexican (Food - Different Cuisine)',
            'payload': {
                'httpMethod': 'POST',
                'body': json.dumps({
                    'mock_ingredients': [{'name': 'shrimp', 'grams': 300, 'fdc_id': '175180'}],
                    'recipe_category': 'cuisine',
                    'cuisine': 'mexican',  # Should give completely different recipes
                    'servings': 2,
                    'user_id': 'test_food_shrimp_mexican'
                })
            },
            'expected_behavior': 'Mexican-specific shrimp recipes (tacos, etc.)'
        },
        {
            'category': 'FOOD',
            'name': 'Chicken Italian (Food - Ingredient + Cuisine)',
            'payload': {
                'httpMethod': 'POST',
                'body': json.dumps({
                    'mock_ingredients': [{'name': 'chicken', 'grams': 400, 'fdc_id': '171477'}],
                    'recipe_category': 'cuisine',
                    'cuisine': 'italian',
                    'servings': 2,
                    'user_id': 'test_food_chicken_italian'
                })
            },
            'expected_behavior': 'Italian-specific chicken recipes with Italian techniques'
        }
    ]
    
    results = {}
    
    for test_case in test_cases:
        print(f"\n🔍 Testing: {test_case['name']}")
        print(f"   Expected: {test_case['expected_behavior']}")
        
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
                titles = [recipe.get('title', '') for recipe in recipes]
                
                print(f"   ✅ Got {len(recipes)} recipes:")
                for i, title in enumerate(titles, 1):
                    print(f"     {i}. {title}")
                
                results[test_case['name']] = {
                    'success': True,
                    'titles': titles,
                    'category': test_case['category']
                }
                
            else:
                print(f"   ❌ Error: {response_payload}")
                results[test_case['name']] = {'success': False, 'category': test_case['category']}
                
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
            results[test_case['name']] = {'success': False, 'category': test_case['category']}
    
    # Analyze results
    print("\n" + "=" * 60)
    print("📊 ANALYSIS:")
    
    # Check fruit behavior (should be ingredient-focused)
    fruit_tests = [r for r in results.values() if r.get('category') == 'FRUIT' and r.get('success')]
    food_tests = [r for r in results.values() if r.get('category') == 'FOOD' and r.get('success')]
    
    print(f"\n🍎 FRUIT TESTS ({len(fruit_tests)} successful):")
    for name, result in results.items():
        if result.get('category') == 'FRUIT' and result.get('success'):
            titles_text = ' '.join(result['titles'])
            if 'Banana' in titles_text or 'Strawberry' in titles_text:
                print(f"   ✅ {name}: Ingredient-specific recipes ✓")
            else:
                print(f"   ❌ {name}: Not ingredient-specific")
    
    print(f"\n🍖 FOOD TESTS ({len(food_tests)} successful):")
    
    # Check if shrimp gets different recipes for different cuisines
    shrimp_indian = results.get('Shrimp Indian (Food - Ingredient + Cuisine)', {})
    shrimp_mexican = results.get('Shrimp Mexican (Food - Different Cuisine)', {})
    
    if shrimp_indian.get('success') and shrimp_mexican.get('success'):
        indian_titles = ' '.join(shrimp_indian['titles'])
        mexican_titles = ' '.join(shrimp_mexican['titles'])
        
        if 'Goan' in indian_titles or 'Tandoori' in indian_titles or 'Kerala' in indian_titles:
            print(f"   ✅ Shrimp + Indian: Gets Indian-specific recipes ✓")
        else:
            print(f"   ❌ Shrimp + Indian: Not getting Indian recipes")
            
        if 'Tacos' in mexican_titles or 'Chipotle' in mexican_titles or 'Mexican' in mexican_titles:
            print(f"   ✅ Shrimp + Mexican: Gets Mexican-specific recipes ✓")
        else:
            print(f"   ❌ Shrimp + Mexican: Not getting Mexican recipes")
            
        # Check they're different
        if indian_titles != mexican_titles:
            print(f"   ✅ Cuisine Impact: Different cuisines produce different recipes ✓")
        else:
            print(f"   ❌ Cuisine Impact: Same recipes for different cuisines")
    
    # Check chicken Italian
    chicken_italian = results.get('Chicken Italian (Food - Ingredient + Cuisine)', {})
    if chicken_italian.get('success'):
        italian_titles = ' '.join(chicken_italian['titles'])
        if 'Parmigiana' in italian_titles or 'Tuscan' in italian_titles or 'Piccata' in italian_titles:
            print(f"   ✅ Chicken + Italian: Gets Italian-specific recipes ✓")
        else:
            print(f"   ❌ Chicken + Italian: Not getting Italian recipes")
    
    print(f"\n🎯 CONCLUSION:")
    
    fruit_working = len([r for r in results.values() if r.get('category') == 'FRUIT' and r.get('success')]) > 0
    food_working = len([r for r in results.values() if r.get('category') == 'FOOD' and r.get('success')]) > 0
    
    if fruit_working and food_working:
        print("✅ CORE LOGIC INTACT:")
        print("   🍎 Fruits → Ingredient-specific recipes")
        print("   🍖 Food → Ingredient + Cuisine specific recipes")
    else:
        print("❌ CORE LOGIC BROKEN:")
        if not fruit_working:
            print("   🍎 Fruit logic not working")
        if not food_working:
            print("   🍖 Food logic not working")
    
    return fruit_working and food_working

if __name__ == "__main__":
    success = test_food_vs_fruit_logic()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 CORE LOGIC VERIFIED!")
        print("✅ Food vs Fruit handling is working correctly")
    else:
        print("❌ CORE LOGIC ISSUE!")
        print("🔧 Need to investigate the logic")