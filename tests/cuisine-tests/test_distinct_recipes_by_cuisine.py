#!/usr/bin/env python3
"""
Test which cuisines can generate distinct recipes with different steps.
"""

import sys
import os
sys.path.append('../../lambda/create-recipe')

from create_recipe import generate_simple_cuisine_recipes

def test_distinct_recipes_by_cuisine():
    """Test all cuisines to see which ones generate distinct recipes"""
    
    print("🔍 Testing Recipe Distinctiveness by Cuisine")
    print("=" * 70)
    
    # Test ingredients (common across all cuisines for fair comparison)
    test_ingredients = [
        {"label": "chicken", "grams": 300, "fdc_id": "chicken001"},
        {"label": "bell pepper", "grams": 150, "fdc_id": "pepper001"},
        {"label": "onion", "grams": 100, "fdc_id": "onion001"}
    ]
    
    nutrition = {'per_serving': {'kcal': 400, 'protein_g': 25, 'fat_g': 15, 'carb_g': 30}}
    
    # All cuisines to test
    cuisines_to_test = [
        'indian',
        'italian', 
        'mediterranean',
        'thai',
        'asian',
        'mexican',
        'french',
        'american',
        'chinese',  # Test unsupported cuisine
        'japanese'  # Test unsupported cuisine
    ]
    
    results = {}
    
    for cuisine in cuisines_to_test:
        print(f"\n--- 🍽️ {cuisine.upper()} CUISINE ---")
        
        try:
            recipes = generate_simple_cuisine_recipes(
                test_ingredients, 
                nutrition, 
                servings=2, 
                cuisine=cuisine
            )
            
            print(f"Generated {len(recipes)} recipes:")
            
            # Collect all step sets for comparison
            all_steps = []
            recipe_info = []
            
            for i, recipe in enumerate(recipes, 1):
                print(f"   {i}. {recipe['title']}")
                print(f"      Tags: {', '.join(recipe['tags'][:3])}")
                
                # Create a signature of the steps for comparison
                steps_text = ' '.join(recipe['steps']).lower()
                all_steps.append(steps_text)
                
                recipe_info.append({
                    'title': recipe['title'],
                    'tags': recipe['tags'],
                    'step_count': len(recipe['steps']),
                    'steps_signature': steps_text[:100] + '...'  # First 100 chars for preview
                })
            
            # Check distinctiveness
            unique_steps = set(all_steps)
            distinct_count = len(unique_steps)
            total_count = len(all_steps)
            
            if distinct_count == total_count:
                distinctiveness = "✅ FULLY DISTINCT"
                quality = "excellent"
            elif distinct_count > 1:
                distinctiveness = f"🔶 PARTIALLY DISTINCT ({distinct_count}/{total_count})"
                quality = "good"
            else:
                distinctiveness = "❌ IDENTICAL STEPS"
                quality = "poor"
            
            print(f"   Distinctiveness: {distinctiveness}")
            
            # Check for cuisine-specific elements
            cuisine_terms = {
                'indian': ['curry', 'cumin', 'garam masala', 'turmeric', 'coriander', 'ghee'],
                'italian': ['olive oil', 'garlic', 'parmesan', 'basil', 'pasta', 'pizza'],
                'mediterranean': ['olive oil', 'lemon', 'herbs', 'oregano', 'feta'],
                'thai': ['coconut', 'fish sauce', 'lime', 'basil', 'curry paste', 'lemongrass'],
                'asian': ['soy sauce', 'ginger', 'sesame', 'stir-fry', 'wok'],
                'mexican': ['cumin', 'chili powder', 'lime', 'cilantro', 'tortilla', 'jalapeño']
            }
            
            expected_terms = cuisine_terms.get(cuisine.lower(), [])
            if expected_terms:
                all_recipe_text = ' '.join(all_steps).lower()
                has_cuisine_terms = any(term in all_recipe_text for term in expected_terms)
                authenticity = "✅ AUTHENTIC" if has_cuisine_terms else "⚠️ GENERIC"
                print(f"   Authenticity: {authenticity}")
            
            results[cuisine] = {
                'distinct_recipes': distinct_count,
                'total_recipes': total_count,
                'quality': quality,
                'authenticity': authenticity if expected_terms else 'N/A',
                'recipes': recipe_info
            }
            
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            results[cuisine] = {
                'distinct_recipes': 0,
                'total_recipes': 0,
                'quality': 'error',
                'authenticity': 'N/A',
                'error': str(e)
            }
    
    # Summary Report
    print(f"\n" + "=" * 70)
    print("📊 CUISINE DISTINCTIVENESS SUMMARY")
    print("=" * 70)
    
    excellent_cuisines = []
    good_cuisines = []
    poor_cuisines = []
    error_cuisines = []
    
    for cuisine, result in results.items():
        if result['quality'] == 'excellent':
            excellent_cuisines.append(cuisine)
        elif result['quality'] == 'good':
            good_cuisines.append(cuisine)
        elif result['quality'] == 'poor':
            poor_cuisines.append(cuisine)
        else:
            error_cuisines.append(cuisine)
    
    print(f"\n🏆 EXCELLENT (Fully Distinct Recipes):")
    for cuisine in excellent_cuisines:
        result = results[cuisine]
        print(f"   ✅ {cuisine.title()}: {result['distinct_recipes']}/{result['total_recipes']} distinct, {result['authenticity']}")
    
    if good_cuisines:
        print(f"\n🔶 GOOD (Partially Distinct Recipes):")
        for cuisine in good_cuisines:
            result = results[cuisine]
            print(f"   🔶 {cuisine.title()}: {result['distinct_recipes']}/{result['total_recipes']} distinct, {result['authenticity']}")
    
    if poor_cuisines:
        print(f"\n❌ POOR (Identical Recipes):")
        for cuisine in poor_cuisines:
            result = results[cuisine]
            print(f"   ❌ {cuisine.title()}: {result['distinct_recipes']}/{result['total_recipes']} distinct, {result['authenticity']}")
    
    if error_cuisines:
        print(f"\n⚠️ ERRORS:")
        for cuisine in error_cuisines:
            print(f"   ⚠️ {cuisine.title()}: {results[cuisine].get('error', 'Unknown error')}")
    
    print(f"\n📈 OVERALL STATISTICS:")
    print(f"   Total cuisines tested: {len(cuisines_to_test)}")
    print(f"   Excellent (fully distinct): {len(excellent_cuisines)}")
    print(f"   Good (partially distinct): {len(good_cuisines)}")
    print(f"   Poor (identical steps): {len(poor_cuisines)}")
    print(f"   Errors: {len(error_cuisines)}")
    
    success_rate = (len(excellent_cuisines) + len(good_cuisines)) / len(cuisines_to_test) * 100
    print(f"   Success rate: {success_rate:.1f}%")
    
    print(f"\n🎯 RECOMMENDATION:")
    if len(excellent_cuisines) >= 5:
        print("   ✅ The system provides excellent recipe variety for most cuisines!")
        print("   ✅ Users will get distinct, authentic cooking experiences.")
    elif len(excellent_cuisines) >= 3:
        print("   🔶 The system provides good recipe variety for several cuisines.")
        print("   🔧 Consider enhancing the cuisines with identical steps.")
    else:
        print("   ❌ The system needs improvement for recipe distinctiveness.")
        print("   🔧 Most cuisines are generating identical or generic steps.")

if __name__ == "__main__":
    test_distinct_recipes_by_cuisine()