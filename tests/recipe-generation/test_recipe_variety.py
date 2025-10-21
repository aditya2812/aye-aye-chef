#!/usr/bin/env python3
"""
Test script for recipe variety and creativity system
"""

import json
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import the recipe variety functions
from create_recipe import (
    get_cooking_method_variations,
    get_flavor_profile_variations,
    get_creative_ingredient_combinations,
    get_session_variation_strategies,
    build_comprehensive_ai_prompt
)

def test_get_cooking_method_variations():
    """Test cooking method variations generation"""
    print("🧪 Testing get_cooking_method_variations...")
    
    ingredients_data = [
        {'name': 'chicken', 'grams': 200},
        {'name': 'vegetables', 'grams': 150},
        {'name': 'rice', 'grams': 100}
    ]
    
    # Test with Italian cuisine
    italian_variations = get_cooking_method_variations(ingredients_data, 'italian')
    assert len(italian_variations) == 3
    assert all('method' in variation for variation in italian_variations)
    assert all('characteristics' in variation for variation in italian_variations)
    assert all('techniques' in variation for variation in italian_variations)
    assert all('flavor_development' in variation for variation in italian_variations)
    
    # Test with Chinese cuisine
    chinese_variations = get_cooking_method_variations(ingredients_data, 'chinese')
    assert len(chinese_variations) == 3
    
    # Variations should be different objects
    assert italian_variations != chinese_variations
    
    print("✅ get_cooking_method_variations test passed")
    return True

def test_get_flavor_profile_variations():
    """Test flavor profile variations generation"""
    print("🧪 Testing get_flavor_profile_variations...")
    
    ingredients_data = [
        {'name': 'beef', 'grams': 250},
        {'name': 'mushrooms', 'grams': 200}
    ]
    
    # Test with different cuisines
    italian_flavors = get_flavor_profile_variations('italian', ingredients_data, 'dinner')
    assert len(italian_flavors) == 3
    assert all('profile' in flavor for flavor in italian_flavors)
    assert all('characteristics' in flavor for flavor in italian_flavors)
    assert all('seasoning_approach' in flavor for flavor in italian_flavors)
    
    indian_flavors = get_flavor_profile_variations('indian', ingredients_data, 'dinner')
    assert len(indian_flavors) == 3
    
    # Different cuisines should have different flavor profiles
    italian_profiles = [f['profile'] for f in italian_flavors]
    indian_profiles = [f['profile'] for f in indian_flavors]
    assert italian_profiles != indian_profiles
    
    print("✅ get_flavor_profile_variations test passed")
    return True

def test_get_creative_ingredient_combinations():
    """Test creative ingredient combinations generation"""
    print("🧪 Testing get_creative_ingredient_combinations...")
    
    ingredients_data = [
        {'name': 'salmon', 'grams': 180},
        {'name': 'asparagus', 'grams': 200},
        {'name': 'lemon', 'grams': 50}
    ]
    
    combinations = get_creative_ingredient_combinations(ingredients_data, 'french')
    assert len(combinations) >= 3
    assert all('strategy' in combo for combo in combinations)
    assert all('description' in combo for combo in combinations)
    assert all('approach' in combo for combo in combinations)
    assert all('technique_focus' in combo for combo in combinations)
    
    # Check for expected strategies
    strategies = [combo['strategy'] for combo in combinations]
    expected_strategies = ['texture_contrast', 'temperature_play', 'flavor_layering', 'cultural_fusion', 'seasonal_adaptation']
    assert any(strategy in expected_strategies for strategy in strategies)
    
    print("✅ get_creative_ingredient_combinations test passed")
    return True

def test_get_session_variation_strategies():
    """Test session variation strategies generation"""
    print("🧪 Testing get_session_variation_strategies...")
    
    # Test with same ingredients but different user IDs
    ingredients = ['chicken', 'rice', 'vegetables']
    
    user1_variations = get_session_variation_strategies('user1', ingredients)
    user2_variations = get_session_variation_strategies('user2', ingredients)
    
    # Both should have the same structure
    expected_keys = ['cooking_method_preference', 'flavor_intensity', 'complexity_level', 'presentation_style', 'technique_focus']
    assert all(key in user1_variations for key in expected_keys)
    assert all(key in user2_variations for key in expected_keys)
    
    # Different users should potentially get different variations
    # (though they might be the same due to hashing)
    assert isinstance(user1_variations, dict)
    assert isinstance(user2_variations, dict)
    
    # Test with same user and same ingredients (should be consistent)
    user1_repeat = get_session_variation_strategies('user1', ingredients)
    assert user1_variations == user1_repeat
    
    # Test with same user but different ingredients (should be different)
    different_ingredients = ['beef', 'potatoes', 'carrots']
    user1_different = get_session_variation_strategies('user1', different_ingredients)
    # May or may not be different due to hashing, but structure should be same
    assert all(key in user1_different for key in expected_keys)
    
    print("✅ get_session_variation_strategies test passed")
    return True

def test_recipe_variety_prompt_generation():
    """Test recipe variety in AI prompt generation"""
    print("🧪 Testing recipe variety prompt generation...")
    
    ingredient_names = ['chicken', 'spinach', 'garlic', 'onion']
    ingredients_data = [
        {'name': 'chicken', 'grams': 200},
        {'name': 'spinach', 'grams': 150},
        {'name': 'garlic', 'grams': 20},
        {'name': 'onion', 'grams': 100}
    ]
    
    # Test with Italian cuisine and variety system
    prompt = build_comprehensive_ai_prompt(
        ingredient_names=ingredient_names,
        cuisine='italian',
        skill_level='intermediate',
        dietary_restrictions=[],
        meal_type='dinner',
        recipe_category='cuisine',
        servings=2,
        ingredients_data=ingredients_data,
        user_id='test_user'
    )
    
    # Check for variety and creativity sections
    assert 'RECIPE VARIETY AND CREATIVITY SYSTEM' in prompt
    assert 'COOKING METHOD VARIATIONS' in prompt
    assert 'FLAVOR PROFILE VARIATIONS' in prompt
    assert 'CREATIVE COMBINATION STRATEGIES' in prompt
    assert 'SESSION VARIATION PREFERENCES' in prompt
    
    # Check for recipe differentiation
    assert 'RECIPE 1 -' in prompt
    assert 'RECIPE 2 -' in prompt
    assert 'RECIPE 3 -' in prompt
    
    # Check for creativity requirements
    assert 'RECIPE VARIETY AND CREATIVITY REQUIREMENTS' in prompt
    assert 'CREATIVITY AND INNOVATION GUIDELINES' in prompt
    assert 'DISTINCTLY DIFFERENT recipes' in prompt
    
    print("✅ Recipe variety prompt generation test passed")
    return True

def test_variety_across_cuisines():
    """Test that variety system adapts to different cuisines"""
    print("🧪 Testing variety adaptation across cuisines...")
    
    ingredients_data = [
        {'name': 'rice', 'grams': 150},
        {'name': 'vegetables', 'grams': 200}
    ]
    
    # Test different cuisines
    cuisines = ['italian', 'chinese', 'indian', 'mexican']
    
    for cuisine in cuisines:
        # Test cooking method variations
        cooking_variations = get_cooking_method_variations(ingredients_data, cuisine)
        assert len(cooking_variations) == 3
        
        # Test flavor profile variations
        flavor_variations = get_flavor_profile_variations(cuisine, ingredients_data, 'dinner')
        assert len(flavor_variations) == 3
        
        # Generate prompt
        prompt = build_comprehensive_ai_prompt(
            ingredient_names=['rice', 'vegetables'],
            cuisine=cuisine,
            skill_level='intermediate',
            dietary_restrictions=[],
            meal_type='dinner',
            recipe_category='cuisine',
            servings=2,
            ingredients_data=ingredients_data,
            user_id='test_user'
        )
        
        # Should contain cuisine-specific content
        assert cuisine.upper() in prompt
        assert 'RECIPE VARIETY AND CREATIVITY SYSTEM' in prompt
    
    print("✅ Variety adaptation across cuisines test passed")
    return True

def test_session_consistency():
    """Test that session variations are consistent for same user/ingredients"""
    print("🧪 Testing session consistency...")
    
    ingredients_data = [
        {'name': 'chicken', 'grams': 200},
        {'name': 'rice', 'grams': 150}
    ]
    
    # Generate prompt twice for same user and ingredients
    prompt1 = build_comprehensive_ai_prompt(
        ingredient_names=['chicken', 'rice'],
        cuisine='italian',
        skill_level='intermediate',
        dietary_restrictions=[],
        meal_type='dinner',
        recipe_category='cuisine',
        servings=2,
        ingredients_data=ingredients_data,
        user_id='consistent_user'
    )
    
    prompt2 = build_comprehensive_ai_prompt(
        ingredient_names=['chicken', 'rice'],
        cuisine='italian',
        skill_level='intermediate',
        dietary_restrictions=[],
        meal_type='dinner',
        recipe_category='cuisine',
        servings=2,
        ingredients_data=ingredients_data,
        user_id='consistent_user'
    )
    
    # Prompts should be identical for same inputs
    assert prompt1 == prompt2
    
    # Different user should potentially get different prompt
    prompt3 = build_comprehensive_ai_prompt(
        ingredient_names=['chicken', 'rice'],
        cuisine='italian',
        skill_level='intermediate',
        dietary_restrictions=[],
        meal_type='dinner',
        recipe_category='cuisine',
        servings=2,
        ingredients_data=ingredients_data,
        user_id='different_user'
    )
    
    # Structure should be same but content may vary
    assert 'RECIPE VARIETY AND CREATIVITY SYSTEM' in prompt3
    assert len(prompt3) > 1000  # Should be substantial
    
    print("✅ Session consistency test passed")
    return True

def test_creativity_strategies_integration():
    """Test that creativity strategies are properly integrated"""
    print("🧪 Testing creativity strategies integration...")
    
    ingredients_data = [
        {'name': 'fish', 'grams': 180},
        {'name': 'vegetables', 'grams': 200},
        {'name': 'herbs', 'grams': 30}
    ]
    
    # Test creative combinations
    combinations = get_creative_ingredient_combinations(ingredients_data, 'mediterranean')
    
    # Should have multiple strategies
    assert len(combinations) >= 3
    
    # Each strategy should have required fields
    for combo in combinations:
        assert 'strategy' in combo
        assert 'description' in combo
        assert 'approach' in combo
        assert 'technique_focus' in combo
        assert 'example_combinations' in combo
    
    # Generate prompt and check integration
    prompt = build_comprehensive_ai_prompt(
        ingredient_names=['fish', 'vegetables', 'herbs'],
        cuisine='mediterranean',
        skill_level='advanced',
        dietary_restrictions=[],
        meal_type='dinner',
        recipe_category='cuisine',
        servings=2,
        ingredients_data=ingredients_data,
        user_id='creative_user'
    )
    
    # Should include creativity strategies in recipes
    assert 'Creative Strategy:' in prompt
    assert 'texture_contrast' in prompt.lower() or 'temperature_play' in prompt.lower() or 'flavor_layering' in prompt.lower()
    
    print("✅ Creativity strategies integration test passed")
    return True

def main():
    """Run all recipe variety and creativity tests"""
    print("🚀 Starting recipe variety and creativity system tests...")
    print("=" * 60)
    
    tests = [
        test_get_cooking_method_variations,
        test_get_flavor_profile_variations,
        test_get_creative_ingredient_combinations,
        test_get_session_variation_strategies,
        test_recipe_variety_prompt_generation,
        test_variety_across_cuisines,
        test_session_consistency,
        test_creativity_strategies_integration
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
        print("🎉 All recipe variety and creativity tests passed!")
        return True
    else:
        print("⚠️ Some recipe variety and creativity tests failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)