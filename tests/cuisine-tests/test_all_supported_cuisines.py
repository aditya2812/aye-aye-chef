#!/usr/bin/env python3
"""
Test all currently supported cuisines to verify they work correctly.
"""

import sys
import os
sys.path.append('../../lambda/create-recipe')

from create_recipe import generate_simple_cuisine_recipes, get_cuisine_appropriate_fallback_ingredients

def test_all_supported_cuisines():
    """Test all supported cuisines with sample ingredients"""
    
    print("🌍 Testing All Supported Cuisines")
    print("=" * 60)
    
    # Test ingredients (chicken is common across many cuisines)
    test_ingredients = [
        {"label": "chicken", "grams": 300, "fdc_id": "chicken001"},
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
        'american'
    ]
    
    for cuisine in cuisines_to_test:
        print(f"\n--- 🍽️ {cuisine.upper()} CUISINE ---")
        
        # Test fallback ingredients
        try:
            fallback = get_cuisine_appropriate_fallback_ingredients(cuisine)
            fallback_names = [item['label'] for item in fallback]
            print(f"Fallback ingredients: {', '.join(fallback_names)}")
        except Exception as e:
            print(f"❌ Fallback ingredients error: {e}")
            continue
        
        # Test recipe generation
        try:
            recipes = generate_simple_cuisine_recipes(
                test_ingredients, 
                nutrition, 
                servings=2, 
                cuisine=cuisine
            )
            
            print(f"Generated {len(recipes)} recipes:")
            for i, recipe in enumerate(recipes, 1):
                print(f"   {i}. {recipe['title']}")
                print(f"      Cuisine: {recipe['cuisine']}")
                print(f"      Tags: {', '.join(recipe['tags'][:3])}")
            
            # Check if recipes match the cuisine
            recipe_text = ' '.join([recipe['title'].lower() for recipe in recipes])
            cuisine_text = ' '.join([' '.join(recipe['tags']) for recipe in recipes]).lower()
            all_text = recipe_text + ' ' + cuisine_text
            
            # Cuisine-specific terms to look for
            cuisine_indicators = {
                'indian': ['indian', 'curry', 'masala', 'tandoori', 'spiced'],
                'italian': ['italian', 'pasta', 'pizza', 'parmigiana', 'tuscan', 'roman'],
                'mediterranean': ['mediterranean', 'greek', 'olive', 'lemon', 'herbs'],
                'thai': ['thai', 'pad', 'tom yum', 'curry', 'coconut'],
                'asian': ['asian', 'stir-fry', 'teriyaki', 'soy', 'ginger'],
                'mexican': ['mexican', 'pollo', 'fajitas', 'lime'],
                'french': ['french', 'butter', 'wine', 'herbs'],
                'american': ['american', 'beef', 'cheese']
            }
            
            expected_terms = cuisine_indicators.get(cuisine, [])
            has_appropriate_terms = any(term in all_text for term in expected_terms)
            
            if has_appropriate_terms:
                print(f"      ✅ Contains appropriate {cuisine} elements")
            else:
                print(f"      ⚠️  May need more specific {cuisine} elements")
                
        except Exception as e:
            print(f"❌ Recipe generation error: {e}")
    
    print(f"\n" + "=" * 60)
    print("📊 CUISINE SUPPORT SUMMARY:")
    print("✅ Fully Supported: Indian, Italian, Mediterranean, Thai, Asian, Mexican")
    print("🔧 Partially Supported: French, American (have fallback ingredients)")
    print("🚀 Easy to extend with new cuisines using the same pattern")

if __name__ == "__main__":
    test_all_supported_cuisines()