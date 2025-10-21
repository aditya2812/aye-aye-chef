#!/usr/bin/env python3
"""
Test runner that properly sets up the Python path for all tests.
"""

import sys
import os

# Add the lambda/create-recipe directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
lambda_path = os.path.join(project_root, 'lambda', 'create-recipe')
sys.path.insert(0, lambda_path)

def run_test(test_file):
    """Run a specific test file"""
    print(f"🧪 Running {test_file}")
    print("=" * 50)
    
    try:
        # Import and run the test
        if test_file == 'test_final_5_cuisines':
            from cuisine_tests.test_final_5_cuisines import test_final_5_cuisines
            test_final_5_cuisines()
        elif test_file == 'test_mediterranean_fix':
            from cuisine_tests.test_mediterranean_fix import test_mediterranean_fix
            test_mediterranean_fix()
        elif test_file == 'test_all_supported_cuisines':
            from cuisine_tests.test_all_supported_cuisines import test_all_supported_cuisines
            test_all_supported_cuisines()
        else:
            print(f"❌ Unknown test: {test_file}")
            return False
            
        print(f"✅ {test_file} completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ {test_file} failed: {e}")
        return False

def test_imports():
    """Test that we can import the create_recipe module"""
    print("🔍 Testing module imports...")
    
    try:
        from create_recipe import generate_simple_cuisine_recipes
        print("✅ Successfully imported generate_simple_cuisine_recipes")
        
        # Test a simple call
        test_ingredients = [{"label": "chicken", "grams": 300, "fdc_id": "test"}]
        nutrition = {'per_serving': {'kcal': 400, 'protein_g': 25, 'fat_g': 15, 'carb_g': 30}}
        
        recipes = generate_simple_cuisine_recipes(test_ingredients, nutrition, 2, 'italian')
        print(f"✅ Successfully generated {len(recipes)} test recipes")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Test Runner for Organized Tests")
    print("=" * 60)
    
    # Test imports first
    if not test_imports():
        print("\n❌ Import test failed - cannot run other tests")
        sys.exit(1)
    
    print("\n🎯 Running key tests...")
    
    # Run key tests
    tests_to_run = [
        'test_final_5_cuisines',
        'test_mediterranean_fix', 
        'test_all_supported_cuisines'
    ]
    
    success_count = 0
    for test in tests_to_run:
        print(f"\n" + "=" * 60)
        if run_test(test):
            success_count += 1
    
    print(f"\n" + "=" * 60)
    print(f"📊 Test Results: {success_count}/{len(tests_to_run)} tests passed")
    
    if success_count == len(tests_to_run):
        print("🎉 All tests passed! Import paths are working correctly.")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")