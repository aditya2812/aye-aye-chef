#!/usr/bin/env python3
"""
Test script for professional recipe formatting system
"""

import json
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import the professional formatting functions
from create_recipe import (
    get_professional_formatting_requirements,
    get_measurement_precision_guidelines,
    get_cooking_technique_explanations,
    get_presentation_and_plating_guidelines,
    build_comprehensive_ai_prompt
)

def test_get_professional_formatting_requirements():
    """Test professional formatting requirements retrieval"""
    print("🧪 Testing get_professional_formatting_requirements...")
    
    # Test different skill levels
    beginner = get_professional_formatting_requirements('beginner', 'italian')
    assert 'clear, approachable titles' in beginner['title_style']
    assert 'exact measurements' in beginner['ingredient_precision']
    assert 'very detailed steps' in beginner['step_detail']
    
    intermediate = get_professional_formatting_requirements('intermediate', 'italian')
    assert 'sophisticated titles' in intermediate['title_style']
    assert 'precise measurements' in intermediate['ingredient_precision']
    
    advanced = get_professional_formatting_requirements('advanced', 'italian')
    assert 'chef-level titles' in advanced['title_style']
    assert 'professional measurements' in advanced['ingredient_precision']
    assert 'concise professional' in advanced['step_detail']
    
    print("✅ get_professional_formatting_requirements test passed")
    return True

def test_get_measurement_precision_guidelines():
    """Test measurement precision guidelines"""
    print("🧪 Testing get_measurement_precision_guidelines...")
    
    beginner = get_measurement_precision_guidelines('beginner')
    assert 'Round to nearest 5g' in beginner['weight_precision']
    assert 'common measurements' in beginner['volume_precision']
    assert 'Start with less' in beginner['seasoning_guidance']
    
    intermediate = get_measurement_precision_guidelines('intermediate')
    assert 'nearest gram' in intermediate['weight_precision']
    assert 'Season progressively' in intermediate['seasoning_guidance']
    
    advanced = get_measurement_precision_guidelines('advanced')
    assert 'Professional precision' in advanced['weight_precision']
    assert 'Weight-based measurements' in advanced['volume_precision']
    assert 'Season by taste' in advanced['seasoning_guidance']
    
    print("✅ get_measurement_precision_guidelines test passed")
    return True

def test_get_cooking_technique_explanations():
    """Test cooking technique explanations"""
    print("🧪 Testing get_cooking_technique_explanations...")
    
    # Test base techniques
    italian_beginner = get_cooking_technique_explanations('italian', 'beginner')
    assert 'sauté' in italian_beginner
    assert 'soffritto' in italian_beginner
    assert 'step-by-step guidance' in italian_beginner['sauté']
    
    chinese_advanced = get_cooking_technique_explanations('chinese', 'advanced')
    assert 'velveting' in chinese_advanced
    assert 'wok hei' in chinese_advanced
    assert 'professional nuances' in chinese_advanced['sauté']
    
    # Test unknown cuisine (should have base techniques)
    unknown = get_cooking_technique_explanations('unknown', 'intermediate')
    assert 'sauté' in unknown
    assert 'braise' in unknown
    
    print("✅ get_cooking_technique_explanations test passed")
    return True

def test_get_presentation_and_plating_guidelines():
    """Test presentation and plating guidelines"""
    print("🧪 Testing get_presentation_and_plating_guidelines...")
    
    # Test cuisine-specific plating
    italian_dinner = get_presentation_and_plating_guidelines('italian', 'dinner', 'intermediate')
    print(f"Italian dinner plating style: {italian_dinner.get('plating_style')}")
    # The function combines base + meal + skill guidelines, so check for dinner characteristics
    assert 'elegant' in italian_dinner['plating_style'] or 'sophisticated' in italian_dinner['plating_style']
    # Check if garnish suggestions exist
    assert 'garnish_suggestions' in italian_dinner
    
    french_dinner = get_presentation_and_plating_guidelines('french', 'dinner', 'advanced')
    print(f"French dinner plating style: {french_dinner.get('plating_style')}")
    # Check for sophisticated presentation characteristics
    assert 'elegant' in french_dinner['plating_style'] or 'sophisticated' in french_dinner['plating_style'] or 'restaurant' in french_dinner['plating_style']
    assert 'garnish_suggestions' in french_dinner
    
    # Test meal type adaptations
    breakfast = get_presentation_and_plating_guidelines('italian', 'breakfast', 'beginner')
    print(f"Breakfast plating style: {breakfast.get('plating_style')}")
    assert 'plating_style' in breakfast
    
    # Test skill level adaptations
    beginner_plating = get_presentation_and_plating_guidelines('italian', 'dinner', 'beginner')
    print(f"Beginner plating complexity: {beginner_plating.get('plating_complexity')}")
    assert 'simple' in beginner_plating.get('plating_complexity', '') or 'basic' in beginner_plating.get('plating_complexity', '')
    
    advanced_plating = get_presentation_and_plating_guidelines('italian', 'dinner', 'advanced')
    print(f"Advanced plating complexity: {advanced_plating.get('plating_complexity')}")
    assert 'restaurant' in advanced_plating.get('plating_complexity', '') or 'professional' in advanced_plating.get('plating_complexity', '')
    
    print("✅ get_presentation_and_plating_guidelines test passed")
    return True

def test_professional_prompt_generation():
    """Test professional AI prompt generation with formatting requirements"""
    print("🧪 Testing professional AI prompt generation...")
    
    try:
        ingredient_names = ['salmon', 'asparagus', 'lemon', 'butter']
        ingredients_data = [
            {'name': 'salmon', 'grams': 180},
            {'name': 'asparagus', 'grams': 200},
            {'name': 'lemon', 'grams': 50},
            {'name': 'butter', 'grams': 30}
        ]
        
        # Test French cuisine with advanced skill level
        french_prompt = build_comprehensive_ai_prompt(
            ingredient_names=ingredient_names,
            cuisine='french',
            skill_level='advanced',
            dietary_restrictions=[],
            meal_type='dinner',
            recipe_category='cuisine',
            servings=2,
            ingredients_data=ingredients_data
        )
    except Exception as e:
        print(f"Error generating prompt: {e}")
        raise
    
    # Check for professional formatting requirements
    assert 'PROFESSIONAL RECIPE FORMATTING REQUIREMENTS' in french_prompt
    assert 'MEASUREMENT PRECISION GUIDELINES' in french_prompt
    assert 'COOKING TECHNIQUE EXPLANATIONS' in french_prompt
    assert 'PRESENTATION AND PLATING GUIDELINES' in french_prompt
    assert 'PROFESSIONAL RECIPE FORMAT' in french_prompt
    
    # Check for advanced-level content
    assert 'chef-level titles' in french_prompt.lower()
    assert 'professional measurements' in french_prompt.lower()
    assert 'concise professional' in french_prompt.lower()
    assert 'restaurant-quality' in french_prompt.lower()
    
    # Check for French-specific content
    assert 'mirepoix' in french_prompt.lower()
    assert 'brunoise' in french_prompt.lower()
    assert 'monter au beurre' in french_prompt.lower()
    
    print("✅ Professional AI prompt generation test passed")
    return True

def test_skill_level_formatting_adaptation():
    """Test that formatting adapts properly to different skill levels"""
    print("🧪 Testing skill level formatting adaptation...")
    
    ingredients_data = [
        {'name': 'chicken', 'grams': 200},
        {'name': 'vegetables', 'grams': 150}
    ]
    
    # Test beginner formatting
    beginner_prompt = build_comprehensive_ai_prompt(
        ingredient_names=['chicken', 'vegetables'],
        cuisine='italian',
        skill_level='beginner',
        dietary_restrictions=[],
        meal_type='dinner',
        recipe_category='cuisine',
        servings=2,
        ingredients_data=ingredients_data
    )
    
    # Should include beginner-specific formatting
    assert 'clear, approachable titles' in beginner_prompt
    assert 'exact measurements with common substitutions' in beginner_prompt
    assert 'very detailed steps with explanations' in beginner_prompt
    assert 'step-by-step guidance' in beginner_prompt
    
    # Test advanced formatting
    advanced_prompt = build_comprehensive_ai_prompt(
        ingredient_names=['chicken', 'vegetables'],
        cuisine='italian',
        skill_level='advanced',
        dietary_restrictions=[],
        meal_type='dinner',
        recipe_category='cuisine',
        servings=2,
        ingredients_data=ingredients_data
    )
    
    # Should include advanced-specific formatting
    assert 'chef-level titles' in advanced_prompt
    assert 'professional measurements' in advanced_prompt
    assert 'concise professional steps' in advanced_prompt
    assert 'professional nuances' in advanced_prompt
    
    print("✅ Skill level formatting adaptation test passed")
    return True

def test_cuisine_specific_formatting():
    """Test that formatting includes cuisine-specific elements"""
    print("🧪 Testing cuisine-specific formatting...")
    
    ingredients_data = [
        {'name': 'rice', 'grams': 150},
        {'name': 'vegetables', 'grams': 100}
    ]
    
    # Test Chinese cuisine formatting
    chinese_prompt = build_comprehensive_ai_prompt(
        ingredient_names=['rice', 'vegetables'],
        cuisine='chinese',
        skill_level='intermediate',
        dietary_restrictions=[],
        meal_type='lunch',
        recipe_category='cuisine',
        servings=2,
        ingredients_data=ingredients_data
    )
    
    # Should include Chinese-specific techniques
    assert 'velveting' in chinese_prompt.lower()
    assert 'wok hei' in chinese_prompt.lower()
    assert 'blanching' in chinese_prompt.lower()
    
    # Test Indian cuisine formatting
    indian_prompt = build_comprehensive_ai_prompt(
        ingredient_names=['rice', 'vegetables'],
        cuisine='indian',
        skill_level='intermediate',
        dietary_restrictions=[],
        meal_type='lunch',
        recipe_category='cuisine',
        servings=2,
        ingredients_data=ingredients_data
    )
    
    # Should include Indian-specific techniques
    assert 'tadka' in indian_prompt.lower()
    assert 'bhuna' in indian_prompt.lower()
    assert 'marination' in indian_prompt.lower()
    
    print("✅ Cuisine-specific formatting test passed")
    return True

def test_comprehensive_formatting_integration():
    """Test that all formatting elements work together"""
    print("🧪 Testing comprehensive formatting integration...")
    
    ingredients_data = [
        {'name': 'beef', 'grams': 250},
        {'name': 'mushrooms', 'grams': 200},
        {'name': 'wine', 'grams': 100}
    ]
    
    # Test comprehensive integration
    prompt = build_comprehensive_ai_prompt(
        ingredient_names=['beef', 'mushrooms', 'wine'],
        cuisine='french',
        skill_level='advanced',
        dietary_restrictions=['gluten-free'],
        meal_type='dinner',
        recipe_category='cuisine',
        servings=4,
        ingredients_data=ingredients_data
    )
    
    # Should include all major formatting sections
    sections_to_check = [
        'PROFESSIONAL RECIPE FORMATTING REQUIREMENTS',
        'MEASUREMENT PRECISION GUIDELINES',
        'COOKING TECHNIQUE EXPLANATIONS',
        'PRESENTATION AND PLATING GUIDELINES',
        'PROFESSIONAL RECIPE FORMAT',
        'COMPREHENSIVE PROFESSIONAL REQUIREMENTS'
    ]
    
    for section in sections_to_check:
        assert section in prompt, f"Missing section: {section}"
    
    # Should integrate skill level, cuisine, and dietary restrictions
    assert 'advanced' in prompt.lower()
    assert 'french' in prompt.lower()
    assert 'gluten-free' in prompt.lower()
    assert 'dinner' in prompt.lower()
    
    # Should include professional elements
    assert 'restaurant-quality' in prompt.lower()
    assert 'chef-level' in prompt.lower()
    assert 'professional' in prompt.lower()
    
    print("✅ Comprehensive formatting integration test passed")
    return True

def main():
    """Run all professional formatting tests"""
    print("🚀 Starting professional recipe formatting tests...")
    print("=" * 60)
    
    tests = [
        test_get_professional_formatting_requirements,
        test_get_measurement_precision_guidelines,
        test_get_cooking_technique_explanations,
        test_get_presentation_and_plating_guidelines,
        test_professional_prompt_generation,
        test_skill_level_formatting_adaptation,
        test_cuisine_specific_formatting,
        test_comprehensive_formatting_integration
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
        print("🎉 All professional formatting tests passed!")
        return True
    else:
        print("⚠️ Some professional formatting tests failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)