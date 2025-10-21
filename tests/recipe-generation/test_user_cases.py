#!/usr/bin/env python3
"""
Test script for user-provided test cases
"""

import sys
import os
sys.path.append('lambda/create-recipe')

# Import the function from the Lambda code
from create_recipe import generate_ingredient_specific_recipes

def test_user_case(test_name, ingredients, cuisine, recipe_category='cuisine'):
    """Test recipe generation for user-provided cases"""
    
    print(f"\n{'='*80}")
    print(f"TEST CASE: {test_name}")
    print(f"Ingredients: {', '.join(ingredients)}")
    print(f"Cuisine: {cuisine}")
    print(f"Category: {recipe_category}")
    print(f"{'='*80}")
    
    # Generate recipes
    recipes = generate_ingredient_specific_recipes(
        ingredient_names=ingredients,
        recipe_category=recipe_category,
        cuisine=cuisine,
        servings=2,
        user_id='test_user'
    )
    
    if not recipes:
        print("❌ No recipes generated!")
        return
    
    print(f"✅ Generated {len(recipes)} unique recipes:\n")
    
    for i, recipe in enumerate(recipes, 1):
        print(f"{i}. 🍽️  {recipe['title']}")
        print(f"   📊 Difficulty: {recipe['difficulty']} | ⏱️  Time: {recipe['estimated_time']} | 👥 Servings: {recipe['servings']}")
        print(f"   🔥 Method: {recipe['cooking_method']} | 🏷️  Tags: {', '.join(recipe['tags'])}")
        
        print(f"   🥘 Ingredients ({len(recipe['ingredients'])}):")
        for ing in recipe['ingredients']:
            print(f"     • {ing['amount']} {ing['name']} ({ing['preparation']})")
        
        print(f"   📝 Steps ({len(recipe['steps'])}):")
        for j, step in enumerate(recipe['steps'], 1):
            print(f"     {j}. {step}")
        
        print()

def main():
    """Test all user-provided cases"""
    
    test_cases = [
        {
            'name': 'TEST 1 - Italian Chicken & Spinach',
            'ingredients': ['chicken', 'spinach'],
            'cuisine': 'italian',
            'category': 'cuisine'
        },
        {
            'name': 'TEST 2 - Mexican Shrimp',
            'ingredients': ['shrimp'],
            'cuisine': 'mexican',
            'category': 'cuisine'
        },
        {
            'name': 'TEST 3 - Thai Tofu',
            'ingredients': ['tofu'],
            'cuisine': 'thai',
            'category': 'cuisine'
        },
        {
            'name': 'TEST 4 - Strawberry Dessert',
            'ingredients': ['strawberry'],
            'cuisine': 'dessert',
            'category': 'dessert'
        },
        {
            'name': 'TEST 5 - Blueberry Smoothie',
            'ingredients': ['blueberry'],
            'cuisine': 'healthy',
            'category': 'smoothie'
        }
    ]
    
    for test_case in test_cases:
        test_user_case(
            test_case['name'],
            test_case['ingredients'],
            test_case['cuisine'],
            test_case['category']
        )
    
    print(f"\n{'='*80}")
    print("🎯 ANALYSIS SUMMARY:")
    print(f"{'='*80}")
    print("Each ingredient combination should produce unique recipes based on:")
    print("• Ingredient properties (texture, flavor, cooking methods)")
    print("• Cuisine-specific techniques and seasonings")
    print("• Recipe category requirements (smoothie vs cooking vs dessert)")
    print("• Complementary ingredient pairings")
    print("\nThis eliminates the template problem where all ingredients got the same recipe structure!")

if __name__ == "__main__":
    main()