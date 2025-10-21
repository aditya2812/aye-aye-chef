#!/usr/bin/env python3
"""
Test script for dynamic ingredient integration system
"""

import json
import sys
import os
from unittest.mock import Mock, patch

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import the ingredient integration functions
from create_recipe import (
    analyze_ingredient_properties,
    create_ingredient_cooking_sequence,
    build_ingredient_specific_instructions,
    validate_ingredient_integration,
    build_comprehensive_ai_prompt
)

def test_analyze_ingredient_properties():
    """Test ingredient property analysis"""
    print("🧪 Testing analyze_ingredient_properties...")
    
    # Test known ingredients
    chicken_props = analyze_ingredient_properties('chicken')
    assert chicken_props['category'] == 'protein'
    assert 'sauté' in chicken_props['cooking_methods']
    assert chicken_props['cooking_sequence'] == 'early'
    
    spinach_props = analyze_ingredient_properties('spinach')
    assert spinach_props['category'] == 'leafy_green'
    assert spinach_props['cooking_sequence'] == 'late'
    
    onion_props = analyze_ingredient_properties('onion')
    assert onion_props['category'] == 'aromatic'
    assert onion_props['cooking_sequence'] == 'first'
    
    # Test unknown ingredient
    unknown_props = analyze_ingredient_properties('exotic_fruit')
    assert unknown_props['category'] == 'unknown'
    
    print("✅ analyze_ingredient_properties test passed")
    return True

def test_create_ingredient_cooking_sequence():
    """Test cooking sequence creation"""
    print("🧪 Testing create_ingredient_cooking_sequence...")
    
    ingredients_data = [
        {'name': 'onion', 'grams': 100},
        {'name': 'chicken', 'grams': 200},
        {'name': 'spinach', 'grams': 150},
        {'name': 'garlic', 'grams': 20}
    ]
    
    sequence = create_ingredient_cooking_sequence(ingredients_data)
    
    # Check that ingredients are in correct sequence
    assert 'onion' in sequence['first']
    assert 'chicken' in sequence['early']
    assert 'spinach' in sequence['late']
    assert 'garlic' in sequence['late']
    
    print("✅ create_ingredient_cooking_sequence test passed")
    return True

def test_build_ingredient_specific_instructions():
    """Test ingredient-specific instruction building"""
    print("🧪 Testing build_ingredient_specific_instructions...")
    
    ingredients_data = [
        {'name': 'chicken', 'grams': 200},
        {'name': 'spinach', 'grams': 150}
    ]
    
    instructions = build_ingredient_specific_instructions(ingredients_data)
    
    # Check that instructions contain key information
    assert 'CHICKEN' in instructions
    assert 'SPINACH' in instructions
    assert '200g' in instructions
    assert '150g' in instructions
    assert 'Preparation:' in instructions
    assert 'Cooking Methods:' in instructions
    
    print("✅ build_ingredient_specific_instructions test passed")
    return True

def test_validate_ingredient_integration():
    """Test ingredient integration validation"""
    print("🧪 Testing validate_ingredient_integration...")
    
    # Test good recipe
    good_recipe = {
        'title': 'Chicken and Spinach Sauté',
        'steps': [
            'Heat oil and sauté onion until translucent',
            'Add chicken and cook until browned and cooked through',
            'Add spinach and cook until wilted',
            'Season and serve'
        ],
        'ingredients': [
            {'name': 'chicken', 'preparation': 'cut into pieces'},
            {'name': 'spinach', 'preparation': 'washed and chopped'}
        ]
    }
    
    ingredients_data = [
        {'name': 'chicken', 'grams': 200},
        {'name': 'spinach', 'grams': 150},
        {'name': 'onion', 'grams': 100}
    ]
    
    result = validate_ingredient_integration(good_recipe, ingredients_data)
    assert result['valid'] == True
    
    # Test recipe missing ingredients
    bad_recipe = {
        'title': 'Incomplete Recipe',
        'steps': ['Cook something'],
        'ingredients': []
    }
    
    result = validate_ingredient_integration(bad_recipe, ingredients_data)
    assert result['valid'] == False
    assert len(result['errors']) > 0
    
    print("✅ validate_ingredient_integration test passed")
    return True

def test_build_comprehensive_ai_prompt():
    """Test comprehensive AI prompt building with ingredient integration"""
    print("🧪 Testing build_comprehensive_ai_prompt...")
    
    ingredient_names = ['chicken', 'spinach', 'onion', 'garlic']
    ingredients_data = [
        {'name': 'chicken', 'grams': 200},
        {'name': 'spinach', 'grams': 150},
        {'name': 'onion', 'grams': 100},
        {'name': 'garlic', 'grams': 20}
    ]
    
    prompt = build_comprehensive_ai_prompt(
        ingredient_names=ingredient_names,
        cuisine='italian',
        skill_level='intermediate',
        dietary_restrictions=[],
        meal_type='dinner',
        recipe_category='cuisine',
        servings=2,
        ingredients_data=ingredients_data
    )
    
    # Check that prompt contains ingredient analysis
    assert 'INGREDIENT ANALYSIS' in prompt
    assert 'OPTIMAL COOKING SEQUENCE' in prompt
    assert 'CHICKEN' in prompt
    assert 'SPINACH' in prompt
    assert 'Start with:' in prompt
    assert 'Cook early:' in prompt
    assert 'Add late:' in prompt
    
    # Check that cooking methods are ingredient-appropriate
    assert 'sauté' in prompt.lower() or 'bake' in prompt.lower()
    
    print("✅ build_comprehensive_ai_prompt test passed")
    return True

def test_integration_workflow():
    """Test the complete ingredient integration workflow"""
    print("🧪 Testing complete ingredient integration workflow...")
    
    # Simulate a complete workflow
    ingredients_data = [
        {'name': 'chicken breast', 'grams': 250},
        {'name': 'fresh spinach', 'grams': 200},
        {'name': 'yellow onion', 'grams': 150},
        {'name': 'garlic cloves', 'grams': 15}
    ]
    
    # Step 1: Analyze ingredients
    for ingredient in ingredients_data:
        properties = analyze_ingredient_properties(ingredient['name'])
        assert properties is not None
        assert 'category' in properties
        assert 'cooking_methods' in properties
    
    # Step 2: Create cooking sequence
    sequence = create_ingredient_cooking_sequence(ingredients_data)
    assert len(sequence) == 5  # first, early, middle, late, finish
    
    # Step 3: Build instructions
    instructions = build_ingredient_specific_instructions(ingredients_data)
    assert len(instructions) > 100  # Should be detailed
    
    # Step 4: Build comprehensive prompt
    ingredient_names = [item['name'] for item in ingredients_data]
    prompt = build_comprehensive_ai_prompt(
        ingredient_names=ingredient_names,
        cuisine='mediterranean',
        skill_level='advanced',
        dietary_restrictions=['gluten-free'],
        meal_type='dinner',
        recipe_category='cuisine',
        servings=4,
        ingredients_data=ingredients_data
    )
    
    # Verify prompt quality
    assert len(prompt) > 1000  # Should be comprehensive
    assert 'mediterranean' in prompt.lower()
    assert 'gluten-free' in prompt.lower()
    assert 'advanced' in prompt.lower()
    
    print("✅ Complete ingredient integration workflow test passed")
    return True

def main():
    """Run all ingredient integration tests"""
    print("🚀 Starting ingredient integration system tests...")
    print("=" * 60)
    
    tests = [
        test_analyze_ingredient_properties,
        test_create_ingredient_cooking_sequence,
        test_build_ingredient_specific_instructions,
        test_validate_ingredient_integration,
        test_build_comprehensive_ai_prompt,
        test_integration_workflow
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1
        print("-" * 40)
    
    print("=" * 60)
    print(f"📊 Test Results:")
    print(f"  ✅ Passed: {passed}")
    print(f"  ❌ Failed: {failed}")
    print(f"  📈 Success Rate: {(passed / (passed + failed)) * 100:.1f}%")
    
    if failed == 0:
        print("🎉 All ingredient integration tests passed!")
        return True
    else:
        print("⚠️ Some ingredient integration tests failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)