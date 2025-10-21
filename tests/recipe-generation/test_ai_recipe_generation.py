#!/usr/bin/env python3
"""
Comprehensive test suite for AI recipe generation system
"""

import json
import sys
import os
import time
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import all the functions we need to test
from create_recipe import (
    build_comprehensive_ai_prompt,
    generate_ai_recipes,
    validate_ai_recipe,
    validate_ingredient_integration,
    format_ai_recipe,
    analyze_ingredient_properties,
    get_cuisine_specific_techniques,
    get_professional_formatting_requirements,
    get_cooking_method_variations,
    get_flavor_profile_variations,
    log_performance_metrics,
    handler
)

class TestAIPromptGeneration:
    """Test suite for AI prompt generation functionality"""
    
    def test_prompt_structure_completeness(self):
        """Test that AI prompts contain all required sections"""
        print("🧪 Testing AI prompt structure completeness...")
        
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
        
        # Check for all required sections
        required_sections = [
            'USER PREFERENCES',
            'AUTHENTIC ITALIAN CUISINE REQUIREMENTS',
            'SKILL LEVEL ADAPTATIONS',
            'MEAL TYPE OPTIMIZATION',
            'PROFESSIONAL RECIPE FORMATTING REQUIREMENTS',
            'MEASUREMENT PRECISION GUIDELINES',
            'COOKING TECHNIQUE EXPLANATIONS',
            'PRESENTATION AND PLATING GUIDELINES',
            'RECIPE VARIETY AND CREATIVITY SYSTEM',
            'INGREDIENT ANALYSIS AND COOKING SEQUENCE',
            'OPTIMAL COOKING SEQUENCE',
            'PROFESSIONAL RECIPE FORMAT',
            'COMPREHENSIVE PROFESSIONAL REQUIREMENTS'
        ]
        
        for section in required_sections:
            assert section in prompt, f"Missing required section: {section}"
        
        # Check prompt length (should be comprehensive)
        assert len(prompt) > 10000, f"Prompt too short: {len(prompt)} characters"
        
        # Check for dietary restrictions integration
        assert 'gluten-free' in prompt.lower()
        
        # Check for ingredient integration
        assert 'chicken' in prompt.lower()
        assert 'spinach' in prompt.lower()
        assert 'garlic' in prompt.lower()
        
        print("✅ AI prompt structure completeness test passed")
        return True
    
    def test_prompt_cuisine_adaptation(self):
        """Test that prompts adapt correctly to different cuisines"""
        print("🧪 Testing AI prompt cuisine adaptation...")
        
        ingredients_data = [{'name': 'rice', 'grams': 150}, {'name': 'vegetables', 'grams': 200}]
        base_params = {
            'ingredient_names': ['rice', 'vegetables'],
            'skill_level': 'intermediate',
            'dietary_restrictions': [],
            'meal_type': 'lunch',
            'recipe_category': 'cuisine',
            'servings': 2,
            'ingredients_data': ingredients_data,
            'user_id': 'test_user'
        }
        
        # Test different cuisines
        cuisines = ['italian', 'chinese', 'indian', 'mexican', 'french']
        
        for cuisine in cuisines:
            prompt = build_comprehensive_ai_prompt(cuisine=cuisine, **base_params)
            
            # Should contain cuisine-specific content
            assert cuisine.upper() in prompt
            assert f'AUTHENTIC {cuisine.upper()} CUISINE REQUIREMENTS' in prompt
            
            # Should have cuisine-specific techniques
            if cuisine == 'italian':
                assert 'olive oil' in prompt.lower()
                assert 'soffritto' in prompt.lower() or 'sauté' in prompt.lower()
            elif cuisine == 'chinese':
                assert 'soy sauce' in prompt.lower()
                assert 'stir-fry' in prompt.lower() or 'wok' in prompt.lower()
            elif cuisine == 'indian':
                assert 'cumin' in prompt.lower() or 'spices' in prompt.lower()
                assert 'tempering' in prompt.lower() or 'tadka' in prompt.lower()
        
        print("✅ AI prompt cuisine adaptation test passed")
        return True
    
    def test_prompt_skill_level_adaptation(self):
        """Test that prompts adapt to different skill levels"""
        print("🧪 Testing AI prompt skill level adaptation...")
        
        ingredients_data = [{'name': 'fish', 'grams': 180}]
        base_params = {
            'ingredient_names': ['fish'],
            'cuisine': 'mediterranean',
            'dietary_restrictions': [],
            'meal_type': 'dinner',
            'recipe_category': 'cuisine',
            'servings': 2,
            'ingredients_data': ingredients_data,
            'user_id': 'test_user'
        }
        
        # Test beginner level
        beginner_prompt = build_comprehensive_ai_prompt(skill_level='beginner', **base_params)
        assert 'beginner' in beginner_prompt.lower()
        assert 'detailed step-by-step' in beginner_prompt.lower()
        assert 'exact temperatures' in beginner_prompt.lower()
        
        # Test advanced level
        advanced_prompt = build_comprehensive_ai_prompt(skill_level='advanced', **base_params)
        assert 'advanced' in advanced_prompt.lower()
        assert 'professional' in advanced_prompt.lower()
        assert 'chef-level' in advanced_prompt.lower()
        
        # Prompts should be different
        assert beginner_prompt != advanced_prompt
        
        print("✅ AI prompt skill level adaptation test passed")
        return True
    
    def test_prompt_dietary_restrictions_integration(self):
        """Test that dietary restrictions are properly integrated"""
        print("🧪 Testing AI prompt dietary restrictions integration...")
        
        ingredients_data = [{'name': 'chicken', 'grams': 200}]
        
        # Test multiple dietary restrictions
        prompt = build_comprehensive_ai_prompt(
            ingredient_names=['chicken'],
            cuisine='italian',
            skill_level='intermediate',
            dietary_restrictions=['vegan', 'gluten-free', 'dairy-free'],
            meal_type='dinner',
            recipe_category='cuisine',
            servings=2,
            ingredients_data=ingredients_data,
            user_id='test_user'
        )
        
        # Should contain all dietary restrictions
        assert 'vegan' in prompt.lower()
        assert 'gluten-free' in prompt.lower()
        assert 'dairy-free' in prompt.lower()
        
        # Should contain substitution guidance
        assert 'substitutions' in prompt.lower()
        assert 'alternatives' in prompt.lower()
        
        print("✅ AI prompt dietary restrictions integration test passed")
        return True

class TestAIRecipeValidation:
    """Test suite for AI recipe validation functionality"""
    
    def test_recipe_structure_validation(self):
        """Test recipe structure validation"""
        print("🧪 Testing recipe structure validation...")
        
        ingredients_data = [
            {'name': 'chicken', 'grams': 200},
            {'name': 'rice', 'grams': 150}
        ]
        
        # Test valid recipe
        valid_recipe = {
            'title': 'Italian Chicken and Rice Risotto',
            'steps': [
                'Heat olive oil in a large pan',
                'Add chicken and cook until browned',
                'Add rice and stir for 2 minutes',
                'Add broth gradually while stirring',
                'Cook until rice is creamy and tender'
            ],
            'ingredients': [
                {'name': 'chicken', 'amount': '200g', 'preparation': 'diced'},
                {'name': 'rice', 'amount': '150g', 'preparation': 'arborio rice'}
            ],
            'estimated_time': '30 minutes'
        }
        
        result = validate_ai_recipe(valid_recipe, ingredients_data)
        assert result['valid'] == True
        assert len(result['errors']) == 0
        
        # Test invalid recipe (missing title)
        invalid_recipe = {
            'steps': ['Cook something'],
            'estimated_time': '10 minutes'
        }
        
        result = validate_ai_recipe(invalid_recipe, ingredients_data)
        assert result['valid'] == False
        assert len(result['errors']) > 0
        assert any('title' in error.lower() for error in result['errors'])
        
        print("✅ Recipe structure validation test passed")
        return True
    
    def test_ingredient_integration_validation(self):
        """Test ingredient integration validation"""
        print("🧪 Testing ingredient integration validation...")
        
        ingredients_data = [
            {'name': 'salmon', 'grams': 180},
            {'name': 'asparagus', 'grams': 200},
            {'name': 'lemon', 'grams': 50}
        ]
        
        # Test recipe with good ingredient integration
        good_recipe = {
            'title': 'Pan-Seared Salmon with Asparagus',
            'steps': [
                'Season salmon with salt and pepper',
                'Heat oil in pan and sear salmon until cooked through',
                'Steam asparagus until tender-crisp',
                'Finish with fresh lemon juice and serve'
            ],
            'ingredients': [
                {'name': 'salmon', 'preparation': 'seasoned and seared'},
                {'name': 'asparagus', 'preparation': 'steamed'},
                {'name': 'lemon', 'preparation': 'juiced'}
            ]
        }
        
        result = validate_ingredient_integration(good_recipe, ingredients_data)
        assert result['valid'] == True
        
        # Test recipe missing ingredients
        bad_recipe = {
            'title': 'Incomplete Recipe',
            'steps': ['Cook salmon'],
            'ingredients': []
        }
        
        result = validate_ingredient_integration(bad_recipe, ingredients_data)
        assert result['valid'] == False
        assert len(result['errors']) > 0
        
        print("✅ Ingredient integration validation test passed")
        return True
    
    def test_recipe_quality_validation(self):
        """Test recipe quality validation"""
        print("🧪 Testing recipe quality validation...")
        
        ingredients_data = [{'name': 'chicken', 'grams': 200}]
        
        # Test high-quality recipe
        quality_recipe = {
            'title': 'Professional Herb-Crusted Chicken Breast with Pan Sauce',
            'steps': [
                'Preheat oven to 375°F (190°C)',
                'Season chicken breast with salt and pepper',
                'Create herb crust with breadcrumbs, herbs, and olive oil',
                'Sear chicken in oven-safe pan for 3-4 minutes per side',
                'Transfer to oven and cook until internal temperature reaches 165°F',
                'Rest chicken for 5 minutes before slicing',
                'Deglaze pan with white wine to create sauce',
                'Finish sauce with butter and fresh herbs'
            ],
            'ingredients': [
                {'name': 'chicken', 'amount': '200g', 'preparation': 'breast, pounded to even thickness'}
            ],
            'estimated_time': '35 minutes',
            'cooking_tips': ['Use meat thermometer for accuracy'],
            'warnings': ['Cook to safe internal temperature']
        }
        
        result = validate_ai_recipe(quality_recipe, ingredients_data)
        assert result['valid'] == True
        
        # Test low-quality recipe
        poor_recipe = {
            'title': 'Food',
            'steps': ['Cook it'],
            'estimated_time': 'some time'
        }
        
        result = validate_ai_recipe(poor_recipe, ingredients_data)
        assert result['valid'] == False
        
        print("✅ Recipe quality validation test passed")
        return True

class TestAIRecipeGeneration:
    """Test suite for complete AI recipe generation workflow"""
    
    def test_recipe_generation_with_mocked_bedrock(self):
        """Test recipe generation with mocked Bedrock responses"""
        print("🧪 Testing recipe generation with mocked Bedrock...")
        
        # Mock Bedrock response
        mock_response = {
            'completion': [
                {
                    'chunk': {
                        'bytes': json.dumps({
                            'recipes': [
                                {
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
                            ]
                        }).encode('utf-8')
                    }
                }
            ]
        }
        
        ingredients_data = [
            {'name': 'chicken', 'grams': 200, 'label': 'chicken breast'},
            {'name': 'rice', 'grams': 150, 'label': 'arborio rice'}
        ]
        
        with patch('create_recipe.bedrock_agent_client') as mock_client:
            with patch('create_recipe.bedrock_agent_mgmt_client') as mock_mgmt:
                with patch('create_recipe.os.environ.get') as mock_env:
                    # Setup mocks
                    mock_env.return_value = 'test-agent-id'
                    mock_client.invoke_agent.return_value = mock_response
                    mock_mgmt.get_agent.return_value = {
                        'agent': {'agentName': 'test-agent', 'agentStatus': 'PREPARED'}
                    }
                    mock_mgmt.list_agent_aliases.return_value = {
                        'agentAliasSummaries': [{'agentAliasId': 'TSTALIASID'}]
                    }
                    
                    # Test recipe generation
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
                    
                    # Validate results
                    assert len(recipes) > 0
                    assert recipes[0]['title'] == 'Italian Chicken Risotto'
                    assert recipes[0]['ai_generated'] == True
                    assert 'chicken' in str(recipes[0]['ingredients'])
                    assert 'rice' in str(recipes[0]['ingredients'])
        
        print("✅ Recipe generation with mocked Bedrock test passed")
        return True
    
    def test_recipe_generation_error_handling(self):
        """Test recipe generation error handling and fallbacks"""
        print("🧪 Testing recipe generation error handling...")
        
        ingredients_data = [
            {'name': 'chicken', 'grams': 200, 'label': 'chicken breast'}
        ]
        
        # Test with no Bedrock Agent ID (should use fallback)
        with patch('create_recipe.os.environ.get') as mock_env:
            mock_env.return_value = None  # No agent ID
            
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
            assert len(recipes) > 0
            assert recipes[0]['ai_generated'] == False
            assert 'fallback' in recipes[0]['tags']
        
        # Test with Bedrock error (should use fallback)
        with patch('create_recipe.bedrock_agent_client') as mock_client:
            with patch('create_recipe.os.environ.get') as mock_env:
                mock_env.return_value = 'test-agent-id'
                mock_client.invoke_agent.side_effect = Exception("Bedrock error")
                
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
                assert len(recipes) > 0
                assert recipes[0]['ai_generated'] == False
        
        print("✅ Recipe generation error handling test passed")
        return True
    
    def test_recipe_formatting_consistency(self):
        """Test that formatted recipes have consistent structure"""
        print("🧪 Testing recipe formatting consistency...")
        
        # Test AI recipe formatting
        ai_recipe = {
            'title': 'Test Recipe',
            'cuisine': 'Italian',
            'difficulty': 'intermediate',
            'estimated_time': '30 minutes',
            'servings': 2,
            'ingredients': [
                {'name': 'chicken', 'amount': '200g', 'preparation': 'diced'}
            ],
            'steps': [
                'Step 1: Prepare ingredients',
                'Step 2: Cook chicken',
                'Step 3: Serve hot'
            ],
            'cooking_tips': ['Use fresh ingredients'],
            'warnings': ['Cook to safe temperature']
        }
        
        ingredients_data = [{'name': 'chicken', 'grams': 200}]
        
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
        
        # Check data types
        assert isinstance(formatted_recipe['ingredients'], list)
        assert isinstance(formatted_recipe['steps'], list)
        assert isinstance(formatted_recipe['servings'], int)
        assert isinstance(formatted_recipe['ai_generated'], bool)
        
        print("✅ Recipe formatting consistency test passed")
        return True

class TestPerformanceAndReliability:
    """Test suite for performance and reliability"""
    
    def test_prompt_generation_performance(self):
        """Test AI prompt generation performance"""
        print("🧪 Testing AI prompt generation performance...")
        
        ingredients_data = [
            {'name': 'chicken', 'grams': 200},
            {'name': 'vegetables', 'grams': 150},
            {'name': 'rice', 'grams': 100}
        ]
        
        # Measure prompt generation time
        start_time = time.time()
        
        for i in range(10):  # Generate 10 prompts
            prompt = build_comprehensive_ai_prompt(
                ingredient_names=['chicken', 'vegetables', 'rice'],
                cuisine='italian',
                skill_level='intermediate',
                dietary_restrictions=[],
                meal_type='dinner',
                recipe_category='cuisine',
                servings=2,
                ingredients_data=ingredients_data,
                user_id=f'test_user_{i}'
            )
            assert len(prompt) > 1000  # Should be substantial
        
        end_time = time.time()
        avg_time = (end_time - start_time) / 10
        
        # Should be fast (less than 0.1 seconds per prompt)
        assert avg_time < 0.1, f"Prompt generation too slow: {avg_time:.3f}s average"
        
        print(f"✅ Prompt generation performance test passed (avg: {avg_time:.3f}s)")
        return True
    
    def test_validation_performance(self):
        """Test recipe validation performance"""
        print("🧪 Testing recipe validation performance...")
        
        ingredients_data = [
            {'name': 'chicken', 'grams': 200},
            {'name': 'rice', 'grams': 150}
        ]
        
        test_recipe = {
            'title': 'Test Recipe for Performance',
            'steps': [
                'Step 1: Prepare ingredients',
                'Step 2: Cook chicken until done',
                'Step 3: Add rice and cook',
                'Step 4: Season and serve'
            ],
            'ingredients': [
                {'name': 'chicken', 'preparation': 'diced'},
                {'name': 'rice', 'preparation': 'washed'}
            ],
            'estimated_time': '25 minutes'
        }
        
        # Measure validation time
        start_time = time.time()
        
        for i in range(100):  # Validate 100 times
            result = validate_ai_recipe(test_recipe, ingredients_data)
            assert result['valid'] == True
        
        end_time = time.time()
        avg_time = (end_time - start_time) / 100
        
        # Should be very fast (less than 0.01 seconds per validation)
        assert avg_time < 0.01, f"Validation too slow: {avg_time:.4f}s average"
        
        print(f"✅ Recipe validation performance test passed (avg: {avg_time:.4f}s)")
        return True
    
    def test_memory_usage(self):
        """Test memory usage during recipe generation"""
        print("🧪 Testing memory usage...")
        
        import psutil
        import gc
        
        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        ingredients_data = [
            {'name': 'chicken', 'grams': 200},
            {'name': 'vegetables', 'grams': 150}
        ]
        
        # Generate multiple prompts
        prompts = []
        for i in range(50):
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
            prompts.append(prompt)
        
        # Check memory usage
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = peak_memory - initial_memory
        
        # Clean up
        del prompts
        gc.collect()
        
        # Memory increase should be reasonable (less than 100MB for 50 prompts)
        assert memory_increase < 100, f"Memory usage too high: {memory_increase:.1f}MB increase"
        
        print(f"✅ Memory usage test passed (increase: {memory_increase:.1f}MB)")
        return True

class TestIntegrationTests:
    """Integration tests for complete workflows"""
    
    def test_lambda_handler_integration(self):
        """Test complete Lambda handler integration"""
        print("🧪 Testing Lambda handler integration...")
        
        # Mock event and context
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
        
        # Mock Bedrock response
        mock_bedrock_response = {
            'completion': [
                {
                    'chunk': {
                        'bytes': json.dumps({
                            'recipes': [
                                {
                                    'title': 'Italian Chicken and Rice',
                                    'steps': ['Cook chicken', 'Add rice', 'Serve'],
                                    'ingredients': [
                                        {'name': 'chicken', 'amount': '200g'},
                                        {'name': 'rice', 'amount': '150g'}
                                    ]
                                }
                            ]
                        }).encode('utf-8')
                    }
                }
            ]
        }
        
        with patch('create_recipe.bedrock_agent_client') as mock_client:
            with patch('create_recipe.bedrock_agent_mgmt_client') as mock_mgmt:
                with patch('create_recipe.os.environ.get') as mock_env:
                    with patch('create_recipe.get_usda_api_key') as mock_api_key:
                        # Setup mocks
                        mock_env.return_value = 'test-agent-id'
                        mock_client.invoke_agent.return_value = mock_bedrock_response
                        mock_mgmt.get_agent.return_value = {
                            'agent': {'agentName': 'test-agent', 'agentStatus': 'PREPARED'}
                        }
                        mock_mgmt.list_agent_aliases.return_value = {
                            'agentAliasSummaries': [{'agentAliasId': 'TSTALIASID'}]
                        }
                        mock_api_key.return_value = 'test-api-key'
                        
                        # Test handler
                        response = handler(mock_event, mock_context)
                        
                        # Validate response
                        assert response['statusCode'] == 200
                        
                        body = json.loads(response['body'])
                        assert body['success'] == True
                        assert 'recipes' in body
                        assert len(body['recipes']) > 0
                        assert 'request_id' in body
                        assert 'processing_time' in body
        
        print("✅ Lambda handler integration test passed")
        return True
    
    def test_error_handling_integration(self):
        """Test error handling integration"""
        print("🧪 Testing error handling integration...")
        
        # Test with invalid event
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
        
        print("✅ Error handling integration test passed")
        return True
    
    def test_monitoring_integration(self):
        """Test monitoring and logging integration"""
        print("🧪 Testing monitoring integration...")
        
        # Test performance metrics logging
        test_metrics = {
            'request_id': 'test_req_123',
            'user_id': 'test_user',
            'total_time': 15.5,
            'success': True,
            'recipes_generated': 3
        }
        
        # Mock CloudWatch client
        with patch('create_recipe.cloudwatch') as mock_cloudwatch:
            mock_cloudwatch.put_metric_data.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
            
            # Should not raise exception
            log_performance_metrics(test_metrics)
            
            # Should have called CloudWatch
            assert mock_cloudwatch.put_metric_data.called
        
        print("✅ Monitoring integration test passed")
        return True

def run_test_suite():
    """Run the complete test suite"""
    print("🚀 Starting comprehensive AI recipe generation test suite...")
    print("=" * 80)
    
    test_classes = [
        TestAIPromptGeneration(),
        TestAIRecipeValidation(),
        TestAIRecipeGeneration(),
        TestPerformanceAndReliability(),
        TestIntegrationTests()
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    for test_class in test_classes:
        class_name = test_class.__class__.__name__
        print(f"\n📋 Running {class_name} tests...")
        print("-" * 60)
        
        # Get all test methods
        test_methods = [method for method in dir(test_class) if method.startswith('test_')]
        
        for method_name in test_methods:
            total_tests += 1
            try:
                test_method = getattr(test_class, method_name)
                if test_method():
                    passed_tests += 1
                else:
                    failed_tests += 1
                    print(f"❌ {method_name} failed")
            except Exception as e:
                failed_tests += 1
                print(f"❌ {method_name} crashed: {e}")
            
            print("-" * 40)
    
    print("=" * 80)
    print(f"📊 TEST SUITE RESULTS:")
    print(f"  Total Tests: {total_tests}")
    print(f"  ✅ Passed: {passed_tests}")
    print(f"  ❌ Failed: {failed_tests}")
    print(f"  📈 Success Rate: {(passed_tests / total_tests) * 100:.1f}%")
    
    if failed_tests == 0:
        print("🎉 ALL TESTS PASSED! AI Recipe Generation system is ready for production.")
        return True
    else:
        print("⚠️ Some tests failed. Please review and fix issues before deployment.")
        return False

if __name__ == "__main__":
    success = run_test_suite()
    sys.exit(0 if success else 1)