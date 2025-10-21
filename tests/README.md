# 🧪 Test Suite

This directory contains all test files, debug scripts, and related utilities for the Aye Aye Chef application.

## 📁 Directory Structure

### `/cuisine-tests/` - Cuisine-Specific Tests
Tests for individual cuisines and recipe generation functionality:
- `test_all_supported_cuisines.py` - Tests all supported cuisines
- `test_final_5_cuisines.py` - Tests the 5 selected UI cuisines
- `test_mediterranean_fix.py` - Tests Mediterranean cuisine enhancement
- `test_mexican_cuisine_fix.py` - Tests Mexican cuisine fix
- `test_italian_cuisine_fix.py` - Tests Italian cuisine functionality
- `test_thai_cuisine_fix.py` - Tests Thai cuisine functionality
- `test_distinct_recipes_by_cuisine.py` - Tests recipe distinctiveness
- `test_cuisine_fix_verification.py` - Verifies cuisine fixes
- `test_ideal_workflow.py` - Tests complete workflow
- `test_multi_cuisine_workflow.py` - Tests multiple cuisine scenarios
- `test_ui_workflow_simulation.py` - Simulates UI interactions

### `/system-tests/` - System Integration Tests
End-to-end and system-level tests:
- `test_complete_system.py` - Full system integration test
- `test_complete_mobile_flow.py` - Mobile app flow testing
- `test_full_recipe_flow.py` - Complete recipe generation flow
- `test_mobile_app_flow.py` - Mobile app specific tests
- `test_recipe_generation.py` - Core recipe generation tests
- `test_enhanced_recipe_naming.py` - Recipe naming system tests
- `test_intelligent_naming.py` - Intelligent naming tests
- `test_mock_recipe.py` - Mock recipe testing
- `test_claude_access.py` - AI service access tests
- `advanced_recipe_features.py` - Advanced feature tests
- `enhanced_recipe_system.py` - Enhanced system tests
- `recipe_template_system.py` - Template system tests

### `/debug-scripts/` - Debug and Utility Scripts
Scripts for debugging and development:
- `debug_cuisine_issue.py` - Debug cuisine-related issues
- `debug_mexican_methods.py` - Debug Mexican recipe methods
- `cleanup_unused_code.py` - Code cleanup utility
- `precise_cleanup.py` - Precise code cleanup
- `unused_legacy_functions_backup.py` - Legacy function backup

## 🚀 Running Tests

### Run All Cuisine Tests
```bash
cd tests/cuisine-tests
python test_all_supported_cuisines.py
python test_final_5_cuisines.py
```

### Run System Tests
```bash
cd tests/system-tests
python test_complete_system.py
```

### Run Debug Scripts
```bash
cd tests/debug-scripts
python debug_cuisine_issue.py
```

## 📋 Test Categories

### ✅ **Production Ready Tests**
- `test_final_5_cuisines.py` - Main test for production cuisines
- `test_all_supported_cuisines.py` - Comprehensive cuisine testing
- `test_complete_system.py` - Full system validation

### 🔧 **Development Tests**
- `test_mediterranean_fix.py` - Specific fix validation
- `test_mexican_cuisine_fix.py` - Mexican cuisine validation
- Debug scripts for troubleshooting

### 📱 **Mobile App Tests**
- `test_complete_mobile_flow.py` - Mobile app integration
- `test_ui_workflow_simulation.py` - UI interaction simulation

## 🎯 **Key Test Results**

- **5 UI Cuisines**: Italian, Thai, Mexican, Indian, Mediterranean
- **Recipe Distinctiveness**: 4/5 cuisines provide fully distinct recipes
- **Success Rate**: 100% for recipe generation
- **Mediterranean Enhancement**: ✅ Fixed with 3 distinct methods

## 📝 **Notes**

All tests use the same import pattern:
```python
import sys
import os
sys.path.append('../lambda/create-recipe')
from create_recipe import generate_simple_cuisine_recipes
```

Tests are designed to be run from their respective directories or from the project root.