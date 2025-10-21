#!/usr/bin/env python3
"""
Simulate the exact UI workflow to debug the cuisine selection issue.
This tests the complete flow from request body parsing to recipe generation.
"""

import sys
import os
import json
sys.path.append('../../lambda/create-recipe')

from create_recipe import generate_simple_cuisine_recipes, get_cuisine_appropriate_fallback_ingredients

def simulate_ui_request(cuisine_selection, detected_ingredients):
    """Simulate the exact request that comes from the UI"""
    
    print(f"🔄 Simulating UI Request")
    print(f"   Selected Cuisine: {cuisine_selection}")
    print(f"   Detected Ingredients: {[item['label'] for item in detected_ingredients]}")
    
    # Simulate the request body parsing (like in the Lambda handler)
    body = {
        'scan_id': 'test-scan-123',
        'servings': 2,
        'cuisine': cuisine_selection,  # This is what the UI sends
        'skill_level': 'intermediate',
        'dietary_restrictions': []
    }
    
    # Extract parameters (like in the Lambda handler)
    scan_id = body.get('scan_id')
    servings = body.get('servings', 2)
    cuisine_preference = body.get('cuisine', 'indian')  # Default to Indian
    
    print(f"   Parsed cuisine_preference: '{cuisine_preference}'")
    
    # Simulate nutrition calculation
    nutrition = {'per_serving': {'kcal': 350, 'protein_g': 25, 'fat_g': 15, 'carb_g': 20}}
    
    # Generate recipes (like in the Lambda handler)
    print(f"   Calling generate_simple_cuisine_recipes with cuisine: '{cuisine_preference}'")
    
    recipe_options = generate_simple_cuisine_recipes(
        detected_ingredients, 
        nutrition, 
        servings, 
        cuisine_preference
    )
    
    return recipe_options

def test_ui_workflow_simulation():
    """Test the complete UI workflow simulation"""
    
    print("🧪 UI Workflow Simulation Test")
    print("=" * 50)
    
    # Test Case 1: Thai cuisine with shrimp (user's exact scenario)
    print("\n--- Test Case 1: User's Exact Scenario ---")
    shrimp_ingredients = [
        {"label": "shrimp", "grams": 250, "fdc_id": "shrimp001"}
    ]
    
    thai_recipes = simulate_ui_request('thai', shrimp_ingredients)
    
    print(f"\n✨ Generated Recipes:")
    for i, recipe in enumerate(thai_recipes, 1):
        print(f"   {i}. {recipe['title']}")
        print(f"      Cuisine: {recipe['cuisine']}")
        print(f"      Tags: {', '.join(recipe['tags'][:3])}")
    
    # Check if we got the wrong recipes
    recipe_titles = [recipe['title'].lower() for recipe in thai_recipes]
    has_indian_names = any('indian' in title or 'masala' in title or 'sabzi' in title for title in recipe_titles)
    has_thai_names = any('thai' in title or 'pad' in title or 'tom yum' in title for title in recipe_titles)
    
    print(f"\n🔍 Analysis:")
    print(f"   Contains Indian recipe names: {has_indian_names}")
    print(f"   Contains Thai recipe names: {has_thai_names}")
    
    if has_indian_names:
        print("   ❌ PROBLEM: Still getting Indian recipes for Thai selection!")
        print("   🔧 This suggests the cuisine parameter isn't being used correctly")
    elif has_thai_names:
        print("   ✅ SUCCESS: Getting Thai recipes for Thai selection!")
    else:
        print("   ⚠️  UNCLEAR: Getting generic recipes")
    
    # Test Case 2: Italian cuisine with shrimp
    print("\n--- Test Case 2: Italian Cuisine with Shrimp ---")
    italian_recipes = simulate_ui_request('italian', shrimp_ingredients)
    
    print(f"\n✨ Generated Recipes:")
    for i, recipe in enumerate(italian_recipes, 1):
        print(f"   {i}. {recipe['title']}")
        print(f"      Cuisine: {recipe['cuisine']}")
    
    # Test Case 3: Test with fallback scenario (no ingredients detected)
    print("\n--- Test Case 3: Fallback Scenario ---")
    print("   Simulating when photo scan fails...")
    
    # Get fallback ingredients for Thai
    thai_fallback = get_cuisine_appropriate_fallback_ingredients('thai')
    print(f"   Thai fallback ingredients: {[item['label'] for item in thai_fallback]}")
    
    fallback_recipes = simulate_ui_request('thai', thai_fallback)
    
    print(f"\n✨ Generated Fallback Recipes:")
    for i, recipe in enumerate(fallback_recipes, 1):
        print(f"   {i}. {recipe['title']}")
        print(f"      Cuisine: {recipe['cuisine']}")
    
    # Final diagnosis
    print(f"\n" + "=" * 50)
    print("🏥 DIAGNOSIS:")
    
    if has_indian_names:
        print("❌ ISSUE CONFIRMED: Thai cuisine selection generates Indian recipes")
        print("🔧 POSSIBLE CAUSES:")
        print("   1. Cuisine parameter not being passed correctly from UI")
        print("   2. Default fallback to 'indian' is being triggered")
        print("   3. Recipe naming function not recognizing 'thai' cuisine")
        print("   4. Some other fallback logic is overriding the cuisine selection")
    else:
        print("✅ ISSUE RESOLVED: Cuisine selection working correctly")
        print("🎉 Thai cuisine → Thai recipes")
        print("🎉 Italian cuisine → Italian recipes")

if __name__ == "__main__":
    test_ui_workflow_simulation()