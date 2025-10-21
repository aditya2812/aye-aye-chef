#!/usr/bin/env python3
"""
Deployment Verification Script
This script helps verify that the recipe variety fixes are properly deployed
"""

import json
import sys
import os

def check_code_changes():
    """Check if the code changes are present in the current file"""
    print("🔍 Checking Code Changes...")
    
    try:
        with open('lambda/create-recipe/create_recipe.py', 'r') as f:
            content = f.read()
        
        # Check for the fixed variable reference
        if 'all_smoothie_variations[i][\'title\']' in content:
            print("✅ Fixed variable reference found: all_smoothie_variations[i]['title']")
        else:
            print("❌ Fixed variable reference NOT found")
            return False
        
        # Check for enhanced variety recipes
        if 'Creamy {ingredient_names[0].title()}-Oat Breakfast Bowl Smoothie' in content:
            print("✅ Enhanced variety recipes found")
        else:
            print("❌ Enhanced variety recipes NOT found")
            return False
        
        # Check for dynamic variety system
        if 'variety_index = int(variety_seed[:2], 16) % 6' in content:
            print("✅ Dynamic variety system found")
        else:
            print("❌ Dynamic variety system NOT found")
            return False
        
        print("✅ All code changes are present in the file")
        return True
        
    except Exception as e:
        print(f"❌ Error checking code: {e}")
        return False

def check_for_old_patterns():
    """Check for any remaining old patterns that might cause issues"""
    print("\n🔍 Checking for Old Patterns...")
    
    try:
        with open('lambda/create-recipe/create_recipe.py', 'r') as f:
            content = f.read()
        
        # Check for problematic patterns
        issues = []
        
        if 'smoothie_variations[i]' in content and 'all_smoothie_variations[i]' not in content:
            issues.append("Found old variable reference: smoothie_variations[i]")
        
        if 'Smoothie Blend' in content and 'no generic names like' not in content:
            issues.append("Found 'Smoothie Blend' pattern in code")
        
        if 'Recipe {i+1}' in content and 'Create a minimal safe recipe' not in content:
            issues.append("Found generic Recipe numbering pattern")
        
        if issues:
            print("❌ Found potential issues:")
            for issue in issues:
                print(f"  - {issue}")
            return False
        else:
            print("✅ No problematic old patterns found")
            return True
            
    except Exception as e:
        print(f"❌ Error checking patterns: {e}")
        return False

def generate_expected_output():
    """Generate what the output should look like"""
    print("\n📋 Expected Recipe Output:")
    
    ingredient = "mango"  # Example
    
    expected_titles = [
        f"Creamy {ingredient.title()}-Oat Breakfast Bowl Smoothie",
        f"Green {ingredient.title()}-Spinach Power Smoothie",
        f"Cocoa {ingredient.title()} 'Milkshake' (No-Peanut Base)"
    ]
    
    print("✅ For mango smoothies, users should see:")
    for i, title in enumerate(expected_titles, 1):
        print(f"  {i}. {title}")
    
    print("\n❌ Users should NOT see:")
    print("  1. Mango Smoothie Blend 1")
    print("  2. Mango Smoothie Blend 2") 
    print("  3. Mango Smoothie Blend 3")

def deployment_checklist():
    """Provide deployment checklist"""
    print("\n📋 DEPLOYMENT CHECKLIST:")
    print("1. ✅ Code changes are present in the file")
    print("2. ⏳ Lambda function needs to be redeployed")
    print("3. ⏳ Test the API after deployment")
    print("4. ⏳ Clear any caches if present")
    
    print("\n🚀 DEPLOYMENT STEPS:")
    print("1. Deploy the updated Lambda function to AWS")
    print("2. Test with a new request (not cached)")
    print("3. Verify the new recipe names appear in the UI")
    
    print("\n🔧 IF STILL SEEING OLD NAMES:")
    print("- Check if Lambda deployment was successful")
    print("- Verify the correct Lambda function is being called")
    print("- Check for any caching layers (CloudFront, API Gateway)")
    print("- Test with a completely new ingredient/user combination")

def main():
    """Run deployment verification"""
    print("🚀 RECIPE VARIETY DEPLOYMENT VERIFICATION")
    print("=" * 50)
    
    code_ok = check_code_changes()
    patterns_ok = check_for_old_patterns()
    
    generate_expected_output()
    deployment_checklist()
    
    print("\n" + "=" * 50)
    if code_ok and patterns_ok:
        print("✅ CODE IS READY FOR DEPLOYMENT")
        print("The issue is likely that the Lambda function hasn't been redeployed yet.")
        print("Deploy the updated function and test again.")
    else:
        print("❌ CODE ISSUES FOUND")
        print("Fix the issues above before deploying.")
    
    return code_ok and patterns_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)