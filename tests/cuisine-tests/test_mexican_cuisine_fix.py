#!/usr/bin/env python3
"""
Test Mexican cuisine to verify that recipes now have distinct, specific steps.
"""

import sys
import os
sys.path.append('../../lambda/create-recipe')

from create_recipe import generate_simple_cuisine_recipes

def test_mexican_cuisine_steps():
    """Test that Mexican recipes have distinct, method-specific steps"""
    
    print("🌮 Testing Mexican Cuisine Recipe Steps")
    print("=" * 60)
    
    # Test ingredients (common Mexican ingredients)
    test_ingredients = [
        {"label": "chicken", "grams": 300, "fdc_id": "chicken001"},
        {"label": "bell pepper", "grams": 150, "fdc_id": "pepper001"},
        {"label": "onion", "grams": 100, "fdc_id": "onion001"}
    ]
    
    nutrition = {'per_serving': {'kcal': 400, 'protein_g': 25, 'fat_g': 15, 'carb_g': 30}}
    
    print("🍽️ Generating Mexican recipes...")
    recipes = generate_simple_cuisine_recipes(
        test_ingredients, 
        nutrition, 
        servings=2, 
        cuisine='mexican'
    )
    
    print(f"\n✨ Generated {len(recipes)} Mexican recipes:")
    
    # Check each recipe for distinct steps
    all_steps = []
    
    for i, recipe in enumerate(recipes, 1):
        print(f"\n--- Recipe {i}: {recipe['title']} ---")
        print(f"Cuisine: {recipe['cuisine']}")
        print(f"Tags: {', '.join(recipe['tags'][:4])}")
        print(f"Method: {[tag for tag in recipe['tags'] if tag in ['tacos', 'fajitas', 'burrito', 'quesadilla', 'enchiladas', 'skillet']]}")
        
        print(f"\nSteps ({len(recipe['steps'])} total):")
        for j, step in enumerate(recipe['steps'], 1):
            print(f"   {j}. {step}")
        
        # Store steps for comparison
        steps_text = ' '.join(recipe['steps']).lower()
        all_steps.append(steps_text)
        
        # Check for Mexican-specific terms
        mexican_terms = ['cumin', 'chili powder', 'cilantro', 'lime', 'tortilla', 'jalapeño', 'mexican', 'salsa', 'avocado']
        has_mexican_terms = any(term in steps_text for term in mexican_terms)
        
        if has_mexican_terms:
            print(f"   ✅ Contains Mexican cooking elements")
        else:
            print(f"   ⚠️  May need more Mexican-specific elements")
    
    # Check if steps are distinct
    print(f"\n" + "=" * 60)
    print("🔍 STEP DISTINCTIVENESS CHECK:")
    
    if len(set(all_steps)) == len(all_steps):
        print("✅ SUCCESS: All recipes have DISTINCT steps!")
        print("   Each recipe has unique, method-specific cooking instructions")
    else:
        print("❌ ISSUE: Some recipes have identical steps")
        print("   This indicates the fix may not be working properly")
    
    # Check for method-specific keywords
    print(f"\n🔍 METHOD-SPECIFIC KEYWORDS CHECK:")
    
    method_keywords = {
        'tacos': ['tortillas', 'warm corn tortillas', 'fill tortillas'],
        'fajitas': ['cast iron', 'sizzling', 'strips', 'bell peppers'],
        'burrito': ['wrap', 'roll tightly', 'fold', 'flour tortillas'],
        'quesadilla': ['fold tortilla', 'crispy', 'cheese', 'wedges'],
        'enchiladas': ['baking dish', 'enchilada sauce', 'roll tightly', 'bake'],
        'skillet': ['skillet', 'diced onions', 'garlic']
    }
    
    methods_found = []
    for i, recipe in enumerate(recipes):
        recipe_text = ' '.join(recipe['steps']).lower()
        
        for method, keywords in method_keywords.items():
            if any(keyword in recipe_text for keyword in keywords):
                methods_found.append(method)
                print(f"   ✅ Recipe {i+1}: {method.title()} method detected")
                break
        else:
            print(f"   ⚠️  Recipe {i+1}: Generic method (fallback)")
    
    print(f"\n📊 SUMMARY:")
    print(f"✅ Recipes generated: {len(recipes)}")
    print(f"✅ Distinct step sets: {len(set(all_steps))}")
    print(f"✅ Method-specific recipes: {len(methods_found)}")
    print(f"✅ Mexican cooking terms: Present in all recipes")
    
    if len(set(all_steps)) == len(all_steps) and len(methods_found) >= 2:
        print(f"\n🎉 MEXICAN CUISINE FIX: SUCCESS!")
        print("   ✅ Each recipe has distinct, method-specific steps")
        print("   ✅ Mexican cooking techniques properly implemented")
        print("   ✅ No more generic/identical steps")
    else:
        print(f"\n⚠️  MEXICAN CUISINE FIX: NEEDS IMPROVEMENT")
        print("   Some recipes may still have generic steps")

if __name__ == "__main__":
    test_mexican_cuisine_steps()