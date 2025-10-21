#!/usr/bin/env python3
"""
Test Thai cuisine support to fix the issue where Thai selection was generating Indian recipes.
"""

import sys
import os
sys.path.append('../../lambda/create-recipe')

from create_recipe import generate_simple_cuisine_recipes, get_cuisine_appropriate_fallback_ingredients

def test_thai_cuisine_fix():
    """Test that Thai cuisine selection generates Thai recipes"""
    
    print("🇹🇭 Thai Cuisine Fix Test")
    print("=" * 40)
    
    # Test with shrimp (the ingredient from the user's test)
    shrimp_ingredients = [
        {"label": "shrimp", "grams": 250, "fdc_id": "shrimp001"},
        {"label": "coconut milk", "grams": 200, "fdc_id": "coconut001"},
        {"label": "lime", "grams": 50, "fdc_id": "lime001"}
    ]
    
    nutrition = {'per_serving': {'kcal': 350, 'protein_g': 25, 'fat_g': 15, 'carb_g': 20}}
    
    print("🦐 Testing with shrimp ingredients:")
    print(f"   Ingredients: {[item['label'] for item in shrimp_ingredients]}")
    
    # Test Thai cuisine
    print("\n1. Thai Cuisine Selection:")
    thai_recipes = generate_simple_cuisine_recipes(
        shrimp_ingredients, 
        nutrition, 
        servings=2, 
        cuisine='thai'
    )
    
    print(f"   Generated {len(thai_recipes)} Thai recipes:")
    for i, recipe in enumerate(thai_recipes, 1):
        print(f"      {i}. {recipe['title']}")
        print(f"         Cuisine: {recipe['cuisine']}")
        print(f"         Tags: {', '.join(recipe['tags'])}")
    
    # Test Italian cuisine with same ingredients
    print("\n2. Italian Cuisine Selection (same ingredients):")
    italian_recipes = generate_simple_cuisine_recipes(
        shrimp_ingredients, 
        nutrition, 
        servings=2, 
        cuisine='italian'
    )
    
    print(f"   Generated {len(italian_recipes)} Italian recipes:")
    for i, recipe in enumerate(italian_recipes, 1):
        print(f"      {i}. {recipe['title']}")
        print(f"         Cuisine: {recipe['cuisine']}")
        print(f"         Tags: {', '.join(recipe['tags'])}")
    
    # Test fallback ingredients
    print("\n3. Thai Fallback Ingredients:")
    thai_fallback = get_cuisine_appropriate_fallback_ingredients('thai')
    print(f"   Thai fallback: {[item['label'] for item in thai_fallback]}")
    
    # Verify the fix
    print("\n4. Fix Verification:")
    
    # Check Thai recipes
    thai_titles = ' '.join([recipe['title'] for recipe in thai_recipes]).lower()
    thai_tags = ' '.join([' '.join(recipe['tags']) for recipe in thai_recipes]).lower()
    thai_text = thai_titles + ' ' + thai_tags
    
    has_thai_terms = any(term in thai_text for term in ['thai', 'pad', 'tom yum', 'curry', 'coconut'])
    has_indian_terms = any(term in thai_text for term in ['masala', 'curry', 'sabzi', 'tandoori', 'indian'])
    
    print(f"   ✅ Thai recipes contain Thai terms: {has_thai_terms}")
    print(f"   ✅ Thai recipes don't contain Indian terms: {not has_indian_terms}")
    
    # Check Italian recipes
    italian_titles = ' '.join([recipe['title'] for recipe in italian_recipes]).lower()
    italian_tags = ' '.join([' '.join(recipe['tags']) for recipe in italian_recipes]).lower()
    italian_text = italian_titles + ' ' + italian_tags
    
    has_italian_terms = any(term in italian_text for term in ['italian', 'pasta', 'parmigiana', 'tuscan'])
    has_indian_in_italian = any(term in italian_text for term in ['masala', 'sabzi', 'tandoori', 'indian'])
    
    print(f"   ✅ Italian recipes contain Italian terms: {has_italian_terms}")
    print(f"   ✅ Italian recipes don't contain Indian terms: {not has_indian_in_italian}")
    
    if has_thai_terms and not has_indian_terms and has_italian_terms and not has_indian_in_italian:
        print("\n🎉 SUCCESS: Cuisine selection now works correctly!")
        print("   Thai selection → Thai recipes")
        print("   Italian selection → Italian recipes")
    else:
        print("\n❌ ISSUE: Still problems with cuisine selection")
    
    print("\n" + "=" * 40)
    print("Expected Results:")
    print("🇹🇭 Thai + Shrimp → 'Thai Shrimp Curry', 'Pad Thai with Shrimp', 'Tom Yum Shrimp'")
    print("🇮🇹 Italian + Shrimp → 'Italian Shrimp Scampi', 'Shrimp Pasta', 'Mediterranean Shrimp'")
    print("❌ NOT: 'Indian Shrimp Curry', 'Spiced Shrimp Sabzi', 'Masala Shrimp'")

if __name__ == "__main__":
    test_thai_cuisine_fix()