#!/usr/bin/env python3
"""
Simple test runner for the organized test suite.
Usage: python run_tests.py [test_name]
"""

import sys
import os
import subprocess

def run_test(test_path, test_name):
    """Run a test with proper PYTHONPATH"""
    print(f"🧪 Running {test_name}")
    print("=" * 60)
    
    try:
        env = os.environ.copy()
        env['PYTHONPATH'] = 'lambda/create-recipe'
        
        result = subprocess.run(['python', test_path], env=env, capture_output=False)
        
        if result.returncode == 0:
            print(f"\n✅ {test_name} PASSED")
            return True
        else:
            print(f"\n❌ {test_name} FAILED")
            return False
            
    except Exception as e:
        print(f"\n❌ {test_name} ERROR: {e}")
        return False

def main():
    """Main test runner"""
    
    # Available tests
    tests = {
        'final': ('tests/cuisine-tests/test_final_5_cuisines.py', 'Final 5 Cuisines Test'),
        'mediterranean': ('tests/cuisine-tests/test_mediterranean_fix.py', 'Mediterranean Fix Test'),
        'all': ('tests/cuisine-tests/test_all_supported_cuisines.py', 'All Supported Cuisines Test'),
        'mexican': ('tests/cuisine-tests/test_mexican_cuisine_fix.py', 'Mexican Cuisine Fix Test'),
        'distinct': ('tests/cuisine-tests/test_distinct_recipes_by_cuisine.py', 'Recipe Distinctiveness Test')
    }
    
    print("🧪 Aye Aye Chef Test Runner")
    print("=" * 60)
    
    # Check if specific test requested
    if len(sys.argv) > 1:
        test_key = sys.argv[1].lower()
        if test_key in tests:
            test_path, test_name = tests[test_key]
            success = run_test(test_path, test_name)
            sys.exit(0 if success else 1)
        else:
            print(f"❌ Unknown test: {test_key}")
            print(f"Available tests: {', '.join(tests.keys())}")
            sys.exit(1)
    
    # Run key tests
    print("🎯 Running key tests...")
    
    key_tests = ['final', 'mediterranean', 'all']
    passed = 0
    total = len(key_tests)
    
    for test_key in key_tests:
        test_path, test_name = tests[test_key]
        if run_test(test_path, test_name):
            passed += 1
        print()  # Add spacing between tests
    
    print("=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The organized test suite is working correctly.")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()