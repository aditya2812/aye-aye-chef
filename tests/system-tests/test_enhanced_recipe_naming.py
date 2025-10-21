#!/usr/bin/env python3
"""
Test script to demonstrate the enhanced recipe naming system.
This shows how recipe names are now intelligently generated based on cuisine and ingredients.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../lambda/create-recipe'))

# Import the enhanced function
from create_recipe import generate_intelligent_recipe_names

def test_recipe_naming():
    """Test the enhanced recipe naming with different cuisine and ingredient combinations"""
    
    print("🍽️  Enhanced Recipe Naming System Test")
    print("=" * 50)
    
    # Test cases with different cuisine and ingredient combinations
    test_cases = [
        {
            'ingredients': ['paneer', 'spinach', 'onion', 'garlic'],
            'cuisine': 'indian',
            'description': 'Classic Indian ingredients'
        },
        {
            'ingredients': ['chicken', 'tomato', 'bell pepper'],
            'cuisine': 'indian', 
            'description': 'Indian chicken dish'
        },
        {
            'ingredients': ['chicken', 'olive oil', 'lemon', 'herbs'],
            'cuisine': 'mediterranean',
            'description': 'Mediterranean chicken'
        },
        {
            'ingredients': ['salmon', 'garlic', 'tomato', 'basil'],
            'cuisine': 'mediterranean',
            'description': 'Mediterranean fish'
        },
        {
            'ingredients': ['tofu', 'soy sauce', 'ginger', 'broccoli'],
            'cuisine': 'asian',
            'description': 'Asian tofu stir-fry'
        },
        {
            'ingredients': ['chicken', 'ginger', 'scallions'],
            'cuisine': 'asian',
            'description': 'Asian chicken'
        },
        {
            'ingredients': ['black beans', 'chicken', 'peppers', 'lime'],
            'cuisine': 'mexican',
            'description': 'Mexican chicken and beans'
        },
        {
            'ingredients': ['potato', 'cauliflower', 'cumin'],
            'cuisine': 'indian',
            'description': 'Indian vegetables (Aloo Gobi)'
        },
        {
            'ingredients': ['tomato', 'basil', 'mozzarella'],
            'cuisine': 'italian',
            'description': 'Classic Italian ingredients'
        },
        {
            'ingredients': ['pasta', 'parmesan', 'garlic'],
            'cuisine': 'italian',
            'description': 'Italian pasta dish'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['description']}")
        print(f"   Ingredients: {', '.join(test_case['ingredients'])}")
        print(f"   Cuisine: {test_case['cuisine'].title()}")
        print("   Generated Recipe Names:")
        
        try:
            recipes = generate_intelligent_recipe_names(
                test_case['ingredients'], 
                test_case['cuisine']
            )
            
            for j, recipe in enumerate(recipes, 1):
                print(f"      {j}. {recipe['title']}")
                print(f"         Method: {recipe['method']} | Time: {recipe['time']}")
                
        except Exception as e:
            print(f"      Error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Enhanced Recipe Naming Features:")
    print("• Cuisine-specific naming patterns")
    print("• Intelligent ingredient combination detection")
    print("• Traditional dish name recognition (e.g., Palak Paneer, Aloo Gobi)")
    print("• Regional style inclusion (e.g., Punjabi, Mediterranean, Szechuan)")
    print("• Cooking method integration in titles")
    print("• Appetizing, restaurant-quality naming")

if __name__ == "__main__":
    test_recipe_naming()