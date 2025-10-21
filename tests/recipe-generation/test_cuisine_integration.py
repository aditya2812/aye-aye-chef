#!/usr/bin/env python3
"""
Test script for cuisine and preference integration system
"""

import json
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import the cuisine integration functions
from create_recipe import (
    get_cuisine_specific_techniques,
    get_skill_level_adaptations,
    get_dietary_restriction_adaptations,
    get_meal_type_optimizations,
    build_comprehensive_ai_prompt
)

def test_get_cuisine_specific_techniques():
    """Test cuisine-specific technique retrieval"""
    print("🧪 Testing get_cuisine_specific_techniques...")
    
    try:
        # Test known cuisines
        italian = get_cuisine_specific_techniques('italian', ['chicken', 'spinach'])
        print(f"Italian result: {italian}")
        assert italian is not None
        assert 'core_techniques' in italian
        assert len(italian['core_techniques']) > 0
        assert any('sauté' in technique for technique in italian['core_techniques'])
        assert 'garlic' in italian['key_seasonings']
        assert 'olive oil' in italian['cooking_fats']
    except Exception as e:
        print(f"Error in Italian test: {e}")
        raise
    
    indian = get_cuisine_specific_techniques('indian', ['chicken', 'spinach'])
    assert any('tempering' in technique for technique in indian['core_techniques'])
    assert 'cumin' in indian['key_seasonings']
    assert 'ghee' in indian['cooking_fats']
    
    chinese = get_cuisine_specific_techniques('chinese', ['chicken', 'vegetables'])
    assert any('stir-fry' in technique for technique in chinese['core_techniques'])
    assert 'soy sauce' in chinese['key_seasonings']
    
    # Test unknown cuisine (should return default)
    unknown = get_cuisine_specific_techniques('martian', ['ingredient'])
    assert 'sauté' in unknown['core_techniques']
    
    print("✅ get_cuisine_specific_techniques test passed")
    return True

def test_get_skill_level_adaptations():
    """Test skill level adaptation system"""
    print("🧪 Testing get_skill_level_adaptations...")
    
    beginner = get_skill_level_adaptations('beginner', 'italian')
    assert 'detailed step-by-step' in beginner['instruction_style']
    assert 'basic techniques' in beginner['technique_complexity']
    assert '8-10' in beginner['step_count']
    
    intermediate = get_skill_level_adaptations('intermediate', 'italian')
    assert 'clear instructions' in intermediate['instruction_style']
    assert 'standard techniques' in intermediate['technique_complexity']
    assert '10-12' in intermediate['step_count']
    
    advanced = get_skill_level_adaptations('advanced', 'italian')
    assert 'concise professional' in advanced['instruction_style']
    assert 'advanced techniques' in advanced['technique_complexity']
    assert '12-15' in advanced['step_count']
    
    print("✅ get_skill_level_adaptations test passed")
    return True

def test_get_dietary_restriction_adaptations():
    """Test dietary restriction adaptation system"""
    print("🧪 Testing get_dietary_restriction_adaptations...")
    
    # Test vegan restrictions
    vegan = get_dietary_restriction_adaptations(['vegan'], 'italian')
    assert len(vegan['substitutions']) > 0
    assert 'butter' in vegan['ingredient_alternatives']
    assert 'olive oil' in vegan['ingredient_alternatives']['butter']
    
    # Test gluten-free restrictions
    gluten_free = get_dietary_restriction_adaptations(['gluten-free'], 'italian')
    assert 'flour' in gluten_free['ingredient_alternatives']
    assert 'tamari' in gluten_free['ingredient_alternatives'].get('soy sauce', '')
    
    # Test multiple restrictions
    multiple = get_dietary_restriction_adaptations(['vegan', 'gluten-free'], 'italian')
    assert len(multiple['substitutions']) > len(vegan['substitutions'])
    assert 'butter' in multiple['ingredient_alternatives']
    assert 'flour' in multiple['ingredient_alternatives']
    
    # Test no restrictions
    none_restrictions = get_dietary_restriction_adaptations([], 'italian')
    assert len(none_restrictions['substitutions']) == 0
    
    print("✅ get_dietary_restriction_adaptations test passed")
    return True

def test_get_meal_type_optimizations():
    """Test meal type optimization system"""
    print("🧪 Testing get_meal_type_optimizations...")
    
    breakfast = get_meal_type_optimizations('breakfast', 'italian')
    assert 'quick' in breakfast['cooking_style']
    assert 'energizing' in breakfast['flavor_preferences']
    assert 'protein' in breakfast['ingredient_emphasis']
    
    lunch = get_meal_type_optimizations('lunch', 'italian')
    assert 'balanced' in lunch['cooking_style']
    assert 'satisfying' in lunch['flavor_preferences']
    
    dinner = get_meal_type_optimizations('dinner', 'italian')
    assert 'hearty' in dinner['cooking_style']
    assert 'rich' in dinner['flavor_preferences']
    
    snack = get_meal_type_optimizations('snack', 'italian')
    assert 'light' in snack['cooking_style']
    assert 'quick' in snack['timing_considerations']
    
    print("✅ get_meal_type_optimizations test passed")
    return True

def test_build_comprehensive_ai_prompt_with_cuisine():
    """Test comprehensive AI prompt building with cuisine integration"""
    print("🧪 Testing build_comprehensive_ai_prompt with cuisine integration...")
    
    ingredient_names = ['chicken', 'spinach', 'garlic', 'onion']
    ingredients_data = [
        {'name': 'chicken', 'grams': 200},
        {'name': 'spinach', 'grams': 150},
        {'name': 'garlic', 'grams': 20},
        {'name': 'onion', 'grams': 100}
    ]
    
    # Test Italian cuisine with intermediate skill
    italian_prompt = build_comprehensive_ai_prompt(
        ingredient_names=ingredient_names,
        cuisine='italian',
        skill_level='intermediate',
        dietary_restrictions=[],
        meal_type='dinner',
        recipe_category='cuisine',
        servings=2,
        ingredients_data=ingredients_data
    )
    
    # Check for Italian-specific content
    assert 'AUTHENTIC ITALIAN CUISINE REQUIREMENTS' in italian_prompt
    assert 'olive oil' in italian_prompt.lower()
    assert 'garlic' in italian_prompt.lower()
    assert 'sauté' in italian_prompt.lower()
    assert 'intermediate' in italian_prompt.lower()
    
    # Test Indian cuisine with beginner skill and dietary restrictions
    indian_prompt = build_comprehensive_ai_prompt(
        ingredient_names=ingredient_names,
        cuisine='indian',
        skill_level='beginner',
        dietary_restrictions=['vegetarian', 'gluten-free'],
        meal_type='lunch',
        recipe_category='cuisine',
        servings=4,
        ingredients_data=ingredients_data
    )
    
    # Check for Indian-specific content
    assert 'AUTHENTIC INDIAN CUISINE REQUIREMENTS' in indian_prompt
    assert 'tempering' in indian_prompt.lower()
    assert 'cumin' in indian_prompt.lower()
    assert 'ghee' in indian_prompt.lower()
    assert 'beginner' in indian_prompt.lower()
    assert 'vegetarian' in indian_prompt.lower()
    assert 'gluten-free' in indian_prompt.lower()
    
    # Test Chinese cuisine with advanced skill
    chinese_prompt = build_comprehensive_ai_prompt(
        ingredient_names=ingredient_names,
        cuisine='chinese',
        skill_level='advanced',
        dietary_restrictions=['dairy-free'],
        meal_type='dinner',
        recipe_category='cuisine',
        servings=3,
        ingredients_data=ingredients_data
    )
    
    # Check for Chinese-specific content
    assert 'AUTHENTIC CHINESE CUISINE REQUIREMENTS' in chinese_prompt
    assert 'stir-fry' in chinese_prompt.lower()
    assert 'soy sauce' in chinese_prompt.lower()
    assert 'advanced' in chinese_prompt.lower()
    assert 'dairy-free' in chinese_prompt.lower()
    
    print("✅ build_comprehensive_ai_prompt with cuisine integration test passed")
    return True

def test_cuisine_skill_meal_integration():
    """Test integration between cuisine, skill level, and meal type"""
    print("🧪 Testing cuisine-skill-meal integration...")
    
    ingredients_data = [
        {'name': 'fish', 'grams': 180},
        {'name': 'tomato', 'grams': 200},
        {'name': 'basil', 'grams': 30}
    ]
    
    # Test Mediterranean breakfast for beginner
    prompt = build_comprehensive_ai_prompt(
        ingredient_names=['fish', 'tomato', 'basil'],
        cuisine='mediterranean',
        skill_level='beginner',
        dietary_restrictions=[],
        meal_type='breakfast',
        recipe_category='cuisine',
        servings=1,
        ingredients_data=ingredients_data
    )
    
    # Should combine Mediterranean techniques with beginner guidance for breakfast
    assert 'mediterranean' in prompt.lower()
    assert 'beginner' in prompt.lower()
    assert 'breakfast' in prompt.lower()
    assert 'olive oil' in prompt.lower()
    assert 'detailed step-by-step' in prompt.lower()
    assert 'quick' in prompt.lower()  # breakfast optimization
    
    # Test French dinner for advanced
    prompt = build_comprehensive_ai_prompt(
        ingredient_names=['fish', 'tomato', 'basil'],
        cuisine='french',
        skill_level='advanced',
        dietary_restrictions=['keto'],
        meal_type='dinner',
        recipe_category='cuisine',
        servings=2,
        ingredients_data=ingredients_data
    )
    
    # Should combine French techniques with advanced guidance for dinner
    assert 'french' in prompt.lower()
    assert 'advanced' in prompt.lower()
    assert 'dinner' in prompt.lower()
    assert 'butter' in prompt.lower()
    assert 'professional' in prompt.lower()
    assert 'hearty' in prompt.lower()  # dinner optimization
    assert 'keto' in prompt.lower()
    
    print("✅ cuisine-skill-meal integration test passed")
    return True

def test_dietary_restriction_integration():
    """Test dietary restriction integration with cuisines"""
    print("🧪 Testing dietary restriction integration...")
    
    ingredients_data = [
        {'name': 'chicken', 'grams': 200},
        {'name': 'rice', 'grams': 150}
    ]
    
    # Test vegan + gluten-free with Italian cuisine
    prompt = build_comprehensive_ai_prompt(
        ingredient_names=['chicken', 'rice'],
        cuisine='italian',
        skill_level='intermediate',
        dietary_restrictions=['vegan', 'gluten-free'],
        meal_type='lunch',
        recipe_category='cuisine',
        servings=2,
        ingredients_data=ingredients_data
    )
    
    # Should include both dietary adaptations
    assert 'vegan' in prompt.lower()
    assert 'gluten-free' in prompt.lower()
    assert 'substitutions' in prompt.lower()
    assert 'alternatives' in prompt.lower()
    
    # Should still maintain Italian authenticity
    assert 'italian' in prompt.lower()
    assert 'olive oil' in prompt.lower()
    
    print("✅ dietary restriction integration test passed")
    return True

def main():
    """Run all cuisine and preference integration tests"""
    print("🚀 Starting cuisine and preference integration tests...")
    print("=" * 60)
    
    tests = [
        test_get_cuisine_specific_techniques,
        test_get_skill_level_adaptations,
        test_get_dietary_restriction_adaptations,
        test_get_meal_type_optimizations,
        test_build_comprehensive_ai_prompt_with_cuisine,
        test_cuisine_skill_meal_integration,
        test_dietary_restriction_integration
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
        print("🎉 All cuisine and preference integration tests passed!")
        return True
    else:
        print("⚠️ Some cuisine and preference integration tests failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)