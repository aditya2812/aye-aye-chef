#!/usr/bin/env python3
"""
Test to verify that Italian cuisine selection generates Italian recipes, not Indian ones.
This addresses the bug where selecting Italian cuisine was generating Indian recipes.
"""

import sys
import os
sys.path.append('../../lambda/create-recipe')

from create_recipe import generate_simple_cuisine_recipes, get_cuisine_appropriate_fallback_ingredients

def test_italian_cuisine_fix():
    """Test that Italian cuisine selection generates Italian recipes"""
    
    print("🇮🇹 Italian Cuisine Fix Test")
    print("=" * 40)
    
    # Test 1: Italian fallback ingredients
    print("\n1. Testing Italian fallback ingredients:")
    italian_fallback = get_cuisine_appropriate_fallback_ingredients('italian')
    print(f"   Italian fallback ingredients: {[item['label'] for item in italian_fallback]}")
    
    # Test 2: Generate Italian recipes with fallback ingredients
    print("\n2. Testing Italian recipe generation:")
    nutrition = {'per_serving': {'kcal': 400, 'protein_g': 15, 'fat_g': 12, 'carb_g': 45}}
    
    italian_recipes = generate_simple_cuisine_recipes(
        italian_fallback, 
        nutrition, 
        servings=2, 
        cuisine='italian'
    )
    
    print(f"   Generated {len(italian_recipes)} Italian recipes:")
    for i, recipe in enumerate(italian_recipes, 1):
        print(f"      {i}. {recipe['title']}")
        print(f"         Cuisine: {recipe['cuisine']}")
        print(f"         Tags: {', '.join(recipe['tags'])}")
        print(f"         Method: {recipe.get('method', 'N/A')}")
    
    # Test 3: Compare with Indian cuisine
    print("\n3. Comparison - Indian cuisine with same test:")
    indian_fallback = get_cuisine_appropriate_fallback_ingredients('indian')
    print(f"   Indian fallback ingredients: {[item['label'] for item in indian_fallback]}")
    
    indian_recipes = generate_simple_cuisine_recipes(
        indian_fallback, 
        nutrition, 
        servings=2, 
        cuisine='indian'
    )
    
    print(f"   Generated {len(indian_recipes)} Indian recipes:")
    for i, recipe in enumerate(indian_recipes, 1):
        print(f"      {i}. {recipe['title']}")
        print(f"         Cuisine: {recipe['cuisine']}")
    
    # Test 4: Verify the fix
    print("\n4. Fix Verification:")
    italian_titles = [recipe['title'] for recipe in italian_recipes]
    indian_titles = [recipe['title'] for recipe in indian_recipes]
    
    has_italian_terms = any(
        term in ' '.join(italian_titles).lower() 
        for term in ['italian', 'pasta', 'pizza', 'margherita', 'carbonara', 'parmigiana']
    )
    
    has_indian_terms = any(
        term in ' '.join(italian_titles).lower() 
        for term in ['curry', 'masala', 'tandoori', 'palak', 'paneer', 'biryani']
    )
    
    print(f"   ✅ Italian recipes contain Italian terms: {has_italian_terms}")
    print(f"   ✅ Italian recipes don't contain Indian terms: {not has_indian_terms}")
    
    if has_italian_terms and not has_indian_terms:
        print("\n🎉 SUCCESS: Italian cuisine selection now generates Italian recipes!")
    else:
        print("\n❌ ISSUE: Italian cuisine selection still has problems")
    
    print("\n" + "=" * 40)
    print("Fix Summary:")
    print("• Added cuisine-appropriate fallback ingredients")
    print("• Added Italian cuisine support to recipe naming")
    print("• Added Italian cooking steps and methods")
    print("• Added Italian AI prompts for advanced generation")

if __name__ == "__main__":
    test_italian_cuisine_fix()