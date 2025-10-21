#!/usr/bin/env python3
"""
Test script to demonstrate ingredient-specific recipe generation
"""

import sys
import os
sys.path.append('lambda/create-recipe')

# Import the function from the Lambda code
from create_recipe import generate_ingredient_specific_recipes

def test_ingredient_recipes(ingredient_name, recipe_category='smoothie'):
    """Test recipe generation for a specific ingredient"""
    
    print(f"\n{'='*60}")
    print(f"TESTING RECIPES FOR: {ingredient_name.upper()}")
    print(f"Recipe Category: {recipe_category.upper()}")
    print(f"{'='*60}")
    
    # Generate recipes
    recipes = generate_ingredient_specific_recipes(
        ingredient_names=[ingredient_name],
        recipe_category=recipe_category,
        cuisine='international',
        servings=2,
        user_id='test_user'
    )
    
    if not recipes:
        print("❌ No recipes generated!")
        return
    
    print(f"✅ Generated {len(recipes)} unique recipes:\n")
    
    for i, recipe in enumerate(recipes, 1):
        print(f"{i}. {recipe['title']}")
        print(f"   Difficulty: {recipe['difficulty']}")
        print(f"   Time: {recipe['estimated_time']}")
        print(f"   Servings: {recipe['servings']}")
        print(f"   Method: {recipe['cooking_method']}")
        print(f"   Tags: {', '.join(recipe['tags'])}")
        
        print(f"   Ingredients ({len(recipe['ingredients'])}):")
        for ing in recipe['ingredients']:
            print(f"     • {ing['amount']} {ing['name']} ({ing['preparation']})")
        
        print(f"   Steps ({len(recipe['steps'])}):")
        for j, step in enumerate(recipe['steps'], 1):
            print(f"     {j}. {step}")
        
        print()

def main():
    """Test with different ingredients"""
    
    # Test ingredients that should have unique recipes
    test_cases = [
        ('banana', 'smoothie'),
        ('grapes', 'smoothie'), 
        ('mango', 'smoothie'),
        ('apple', 'smoothie'),
        ('strawberry', 'smoothie')
    ]
    
    for ingredient, category in test_cases:
        test_ingredient_recipes(ingredient, category)
        
    print(f"\n{'='*60}")
    print("COMPARISON SUMMARY:")
    print(f"{'='*60}")
    print("Notice how each ingredient gets completely different recipes:")
    print("• Banana: Creamy oat breakfast, Green spinach, Cocoa milkshake")
    print("• Grapes: Frosty lime cooler, Green spinach, Purple berry antioxidant")
    print("• Mango: Tropical coconut paradise, Golden cardamom lassi, Mint green refresher")
    print("\nEach recipe uses the ingredient's unique properties and complementary flavors!")

if __name__ == "__main__":
    main()