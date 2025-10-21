#!/usr/bin/env python3
"""
Core test suite for AI recipe generation system
"""

import json
import sys
import os
import time
from unittest.mock import Mock, patch

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import core functions
from create_recipe import (
    build_comprehensive_ai_prompt,
    generate_ai_recipes,
    validate_ai_recipe,
    format_ai_recipe,
    handler
)

def test_ai_prompt_generation():
    """Test AI prompt generation with all features"""
    print("🧪 Testing AI prompt generation...")
    
    ingredients_data = [
        {'name': 'chicken', 'grams': 200},
        {'name': 'spinach', 'grams': 150},
        {'name': 'garlic', 'grams': 20}
    ]
    
    prompt = build_comprehensive_ai_prompt(
        ingredient_names=['chicken', 'spinach', 'garlic'],
        cuisine='italian',
        skill_level='intermediate',
        dietary_restrictions=['gluten-free'],
        meal_type='dinner',
        recipe_category='cuisine',
        servings=2,
        ingredients_data=ingredients_data,
        user_id='test_user'
    )
    
    # Check essential sections
    essential_sections = [
        'USER PREFERENCES',
        'AUTHENTIC ITALIAN CUISINE REQUIREMENTS',
        'RECIPE VARIETY AND CREATIVITY SYSTEM',
        'PROFESSIONAL RECIPE FORMAT'
    ]
    
    for section in essential_sections:
        assert section in prompt, f"Missing section: {section}"
    
    # Check content quality
    assert len(prompt) > 5000, "Prompt should be comprehensive"
    assert 'gluten-free' in prompt.lower(), "Should include dietary restrictions"
    assert 'chicken' in prompt.lower(), "Should include ingredients"
    assert 'italian' in prompt.lower(), "Should include cuisine"
    
    print("✅ AI prompt generation test passed")
    return True

def test_recipe_validation():
    """Test recipe validation functionality"""
    print("🧪 Testing recipe validation...")
    
    ingredients_data = [
        {'name': 'salmon', 'grams': 180},
        {'name': 'asparagus', 'grams': 200}
    ]
    
    # Test valid recipe
    valid_recipe = {
        'title': 'Pan-Seared Salmon with Asparagus',
        'steps': [
            'Season salmon with salt and pepper',
            'Heat oil in pan over medium-high heat',
            'Sear salmon for 4-5 minutes per side until cooked through',
            'Steam asparagus until tender-crisp',
            'Serve salmon with asparagus and lemon'
        ],
        'ingredients': [
            {'name': 'salmon', 'preparation': 'seasoned'},
            {'name': 'asparagus', 'preparation': 'steamed'}
        ],
        'estimated_time': '20 minutes'
    }
    
    result = validate_ai_recipe(valid_recipe, ingredients_data)
    assert result['valid'] == True, "Valid recipe should pass validation"
    
    # Test invalid recipe
    invalid_recipe = {
        'title': 'Bad Recipe',
        'steps': ['Do something'],
        'estimated_time': 'unknown'
    }
    
    result = validate_ai_recipe(invalid_recipe, ingredients_data)
    assert result['valid'] == False, "Invalid recipe should fail validation"
    assert len(result['errors']) > 0, "Should have validation errors"
    
    print("✅ Recipe validation test passed")
    return True

def test_recipe_generation_fallback():
    """Test recipe generation with fallback"""
    print("🧪 Testing recipe generation fallback...")
    
    ingredients_data = [
        {'name': 'chicken', 'grams': 200, 'label': 'chicken breast'},
        {'name': 'rice', 'grams': 150, 'label': 'basmati rice'}
    ]
    
    # Test without Bedrock (should use fallback)
    recipes = generate_ai_recipes(
        items=ingredients_data,
        nutrition={},
        servings=2,
        cuisine='italian',
        skill_level='intermediate',
        dietary_restrictions=[],
        meal_type='dinner',
        recipe_category='cuisine',
        user_id='test_user'
    )
    
    # Should get fallback recipes
    assert len(recipes) == 3, "Should generate 3 recipes"
    assert all('title' in recipe for recipe in recipes), "All recipes should have titles"
    assert all('steps' in recipe for recipe in recipes), "All recipes should have steps"
    assert all('ingredients' in recipe for recipe in recipes), "All recipes should have ingredients"
    
    # Check that ingredients are included
    recipe_text = json.dumps(recipes).lower()
    assert 'chicken' in recipe_text, "Should include chicken"
    assert 'rice' in recipe_text, "Should include rice"
    
    print("✅ Recipe generation fallback test passed")
    return True

def test_recipe_formatting():
    """Test recipe formatting functionality"""
    print("🧪 Testing recipe formatting...")
    
    ai_recipe = {
        'title': 'Italian Chicken Risotto',
        'cuisine': 'Italian',
        'difficulty': 'intermediate',
        'estimated_time': '35 minutes',
        'servings': 2,
        'ingredients': [
            {'name': 'chicken', 'amount': '200g', 'preparation': 'diced'},
            {'name': 'rice', 'amount': '150g', 'preparation': 'arborio'}
        ],
        'steps': [
            'Heat olive oil in large pan',
            'Cook chicken until browned',
            'Add rice and toast for 2 minutes',
            'Add warm broth gradually',
            'Stir constantly until creamy'
        ],
        'cooking_tips': ['Use warm broth for best results'],
        'warnings': ['Cook chicken to 165°F internal temperature']
    }
    
    ingredients_data = [
        {'name': 'chicken', 'grams': 200},
        {'name': 'rice', 'grams': 150}
    ]
    
    formatted_recipe = format_ai_recipe(
        ai_recipe=ai_recipe,
        ingredients=ingredients_data,
        nutrition={},
        servings=2,
        cuisine='italian',
        skill_level='intermediate',
        meal_type='dinner',
        recipe_category='cuisine'
    )
    
    # Check required fields
    required_fields = ['title', 'servings', 'ingredients', 'steps', 'ai_generated']
    for field in required_fields:
        assert field in formatted_recipe, f"Missing field: {field}"
    
    # Check data integrity
    assert formatted_recipe['title'] == 'Italian Chicken Risotto'
    assert formatted_recipe['servings'] == 2
    assert formatted_recipe['ai_generated'] == True
    assert len(formatted_recipe['ingredients']) == 2
    assert len(formatted_recipe['steps']) == 5
    
    print("✅ Recipe formatting test passed")
    return True

def test_lambda_handler_basic():
    """Test basic Lambda handler functionality"""
    print("🧪 Testing Lambda handler basic functionality...")
    
    # Test with mock ingredients (no Bedrock needed)
    mock_event = {
        'body': json.dumps({
            'mock_ingredients': [
                {'name': 'chicken', 'grams': 200, 'label': 'chicken breast', 'fdc_id': '12345'},
                {'name': 'rice', 'grams': 150, 'label': 'basmati rice', 'fdc_id': '67890'}
            ],
            'servings': 2,
            'cuisine': 'italian',
            'skill_level': 'intermediate',
            'dietary_restrictions': [],
            'meal_type': 'dinner',
            'user_id': 'test_user'
        })
    }
    
    mock_context = Mock()
    mock_context.aws_request_id = 'test-request-id'
    
    with patch('create_recipe.get_usda_api_key') as mock_api_key:
        mock_api_key.return_value = None  # No API key, will skip nutrition lookup
        
        response = handler(mock_event, mock_context)
        
        # Should succeed with fallback recipes
        assert response['statusCode'] == 200
        
        body = json.loads(response['body'])
        assert body['success'] == True
        assert 'recipes' in body
        assert len(body['recipes']) > 0
        assert 'request_id' in body
        assert 'processing_time' in body
    
    print("✅ Lambda handler basic test passed")
    return True

def test_error_handling():
    """Test error handling"""
    print("🧪 Testing error handling...")
    
    # Test with invalid JSON
    invalid_event = {
        'body': 'invalid json'
    }
    
    mock_context = Mock()
    
    response = handler(invalid_event, mock_context)
    
    # Should return error response
    assert response['statusCode'] == 500
    body = json.loads(response['body'])
    assert body['success'] == False
    assert 'error' in body
    assert 'request_id' in body
    
    print("✅ Error handling test passed")
    return True

def test_performance():
    """Test basic performance"""
    print("🧪 Testing performance...")
    
    ingredients_data = [
        {'name': 'chicken', 'grams': 200},
        {'name': 'vegetables', 'grams': 150}
    ]
    
    # Test prompt generation speed
    start_time = time.time()
    
    for i in range(5):
        prompt = build_comprehensive_ai_prompt(
            ingredient_names=['chicken', 'vegetables'],
            cuisine='italian',
            skill_level='intermediate',
            dietary_restrictions=[],
            meal_type='dinner',
            recipe_category='cuisine',
            servings=2,
            ingredients_data=ingredients_data,
            user_id=f'test_user_{i}'
        )
        assert len(prompt) > 1000
    
    end_time = time.time()
    avg_time = (end_time - start_time) / 5
    
    # Should be reasonably fast
    assert avg_time < 0.5, f"Prompt generation too slow: {avg_time:.3f}s average"
    
    print(f"✅ Performance test passed (avg: {avg_time:.3f}s per prompt)")
    return True

def main():
    """Run core test suite"""
    print("🚀 Starting AI Recipe Generation Core Test Suite...")
    print("=" * 60)
    
    tests = [
        test_ai_prompt_generation,
        test_recipe_validation,
        test_recipe_generation_fallback,
        test_recipe_formatting,
        test_lambda_handler_basic,
        test_error_handling,
        test_performance
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
    print(f"📊 Core Test Results:")
    print(f"  ✅ Passed: {passed}")
    print(f"  ❌ Failed: {failed}")
    print(f"  📈 Success Rate: {(passed / (passed + failed)) * 100:.1f}%")
    
    if failed == 0:
        print("🎉 All core tests passed! AI Recipe Generation system is working correctly.")
        return True
    else:
        print("⚠️ Some core tests failed. Please review and fix issues.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)