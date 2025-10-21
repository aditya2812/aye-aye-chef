#!/usr/bin/env python3
"""
Test script for comprehensive monitoring and logging implementation
"""

import json
import sys
import os
from datetime import datetime, timezone
from unittest.mock import Mock, patch

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import the monitoring functions
from create_recipe import (
    log_performance_metrics,
    send_cloudwatch_metrics,
    log_ai_request_response,
    create_monitoring_alert,
    send_request_level_metrics
)

def test_log_performance_metrics():
    """Test the log_performance_metrics function"""
    print("🧪 Testing log_performance_metrics...")
    
    test_metrics = {
        'request_id': 'test_req_123',
        'user_id': 'test_user',
        'ingredient_count': 3,
        'cuisine': 'italian',
        'skill_level': 'intermediate',
        'meal_type': 'dinner',
        'recipe_category': 'cuisine',
        'total_time': 15.5,
        'prompt_build_time': 0.2,
        'bedrock_call_time': 12.3,
        'bedrock_attempts': 1,
        'success': True,
        'fallback_used': False,
        'recipes_generated': 3,
        'prompt_length': 2500
    }
    
    # Mock CloudWatch client to avoid actual API calls
    with patch('create_recipe.cloudwatch') as mock_cloudwatch:
        mock_cloudwatch.put_metric_data.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
        
        try:
            log_performance_metrics(test_metrics)
            print("✅ log_performance_metrics test passed")
            return True
        except Exception as e:
            print(f"❌ log_performance_metrics test failed: {e}")
            return False

def test_log_ai_request_response():
    """Test the log_ai_request_response function"""
    print("🧪 Testing log_ai_request_response...")
    
    request_data = {
        'user_id': 'test_user',
        'ingredients': ['chicken', 'spinach', 'garlic'],
        'cuisine': 'italian',
        'skill_level': 'intermediate',
        'meal_type': 'dinner',
        'prompt': 'Create 3 Italian recipes using chicken, spinach, and garlic...',
        'agent_id': 'GDKC6RTZHD',
        'session_id': 'test_session_123',
        'alias': 'TSTALIASID'
    }
    
    response_data = {
        'response_text': '{"recipes": [{"title": "Italian Chicken with Spinach", "steps": [...]}]}',
        'response_time': 8.5,
        'attempts': 1,
        'success': True,
        'recipes_parsed': 3,
        'validation_errors': [],
        'error': None
    }
    
    metrics = {
        'request_id': 'test_req_123',
        'user_id': 'test_user'
    }
    
    try:
        log_ai_request_response(request_data, response_data, metrics)
        print("✅ log_ai_request_response test passed")
        return True
    except Exception as e:
        print(f"❌ log_ai_request_response test failed: {e}")
        return False

def test_create_monitoring_alert():
    """Test the create_monitoring_alert function"""
    print("🧪 Testing create_monitoring_alert...")
    
    metrics = {
        'request_id': 'test_req_123',
        'user_id': 'test_user',
        'total_time': 45.2,
        'bedrock_attempts': 3,
        'success': False,
        'fallback_used': True
    }
    
    # Mock CloudWatch client
    with patch('create_recipe.cloudwatch') as mock_cloudwatch:
        mock_cloudwatch.put_metric_data.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
        
        try:
            create_monitoring_alert('test_alert', 'This is a test alert', 'WARNING', metrics)
            print("✅ create_monitoring_alert test passed")
            return True
        except Exception as e:
            print(f"❌ create_monitoring_alert test failed: {e}")
            return False

def test_send_request_level_metrics():
    """Test the send_request_level_metrics function"""
    print("🧪 Testing send_request_level_metrics...")
    
    request_metrics = {
        'request_id': 'test_req_123',
        'lambda_start_time': 1234567890.0,
        'user_id': 'test_user',
        'scan_id': 'scan_123',
        'cuisine': 'italian',
        'skill_level': 'intermediate',
        'meal_type': 'dinner',
        'recipe_category': 'cuisine',
        'servings': 2,
        'has_mock_ingredients': False,
        'total_request_time': 18.7,
        'recipes_generated': 3,
        'success': True
    }
    
    # Mock CloudWatch client
    with patch('create_recipe.cloudwatch') as mock_cloudwatch:
        mock_cloudwatch.put_metric_data.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
        
        try:
            send_request_level_metrics(request_metrics)
            print("✅ send_request_level_metrics test passed")
            return True
        except Exception as e:
            print(f"❌ send_request_level_metrics test failed: {e}")
            return False

def main():
    """Run all monitoring tests"""
    print("🚀 Starting comprehensive monitoring tests...")
    print("=" * 60)
    
    tests = [
        test_log_performance_metrics,
        test_log_ai_request_response,
        test_create_monitoring_alert,
        test_send_request_level_metrics
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
        print("🎉 All monitoring tests passed!")
        return True
    else:
        print("⚠️ Some monitoring tests failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)