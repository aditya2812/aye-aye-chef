#!/usr/bin/env python3
"""
Test the final 5 cuisines selected for the UI to ensure they all provide distinct recipes.
"""

import sys
import os
sys.path.append('../../lambda/create-recipe')

from create_recipe import generate_simple_cuisine_recipes

def test_final_5_cuisines():
    """Test the 5 cuisines selected for the UI"""
    
    print("🍽️ Testing Final 5 Cuisines for UI")
    print("=" * 60)
    
    # Test ingredients
    test_ingredients = [
        {"label": "chicken", "grams": 300, "fdc_id": "chicken001"},
        {"label": "bell pepper", "grams": 150, "fdc_id": "pepper001"},
        {"label": "onion", "grams": 100, "fdc_id": "onion001"}
    ]
    
    nutrition = {'per_serving': {'kcal': 400, 'protein_g': 25, 'fat_g': 15, 'carb_g': 30}}
    
    # The 5 cuisines selected for the UI (in order of appearance)
    final_cuisines = [
        'italian',
        'thai', 
        'mexican',
        'indian',
        'mediterranean'
    ]
    
    results = {}
    
    for cuisine in final_cuisines:
        print(f"\n--- 🍽️ {cuisine.upper()} CUISINE ---")
        
        recipes = generate_simple_cuisine_recipes(
            test_ingredients, 
            nutrition, 
            servings=2, 
            cuisine=cuisine
        )
        
        print(f"Generated {len(recipes)} recipes:")
        
        # Collect step signatures for distinctiveness check
        all_steps = []
        
        for i, recipe in enumerate(recipes, 1):
            print(f"   {i}. {recipe['title']}")
            print(f"      Method: {[tag for tag in recipe['tags'] if tag in ['curry', 'baked', 'grilled', 'fajitas', 'fresh', 'sautéed', 'stir-fry', 'braised', 'roasted']]}")
            print(f"      Steps: {len(recipe['steps'])} total")
            
            # Show first step as preview
            if recipe['steps']:
                print(f"      Preview: {recipe['steps'][0][:60]}...")
            
            # Create step signature for comparison
            steps_signature = ' '.join(recipe['steps']).lower()
            all_steps.append(steps_signature)
        
        # Check distinctiveness
        unique_steps = set(all_steps)
        distinct_count = len(unique_steps)
        total_count = len(all_steps)
        
        if distinct_count == total_count:
            distinctiveness = "✅ FULLY DISTINCT"
            quality = "excellent"
        elif distinct_count > 1:
            distinctiveness = f"🔶 PARTIALLY DISTINCT ({distinct_count}/{total_count})"
            quality = "good"
        else:
            distinctiveness = "❌ IDENTICAL STEPS"
            quality = "poor"
        
        print(f"   Result: {distinctiveness}")
        
        results[cuisine] = {
            'distinct_recipes': distinct_count,
            'total_recipes': total_count,
            'quality': quality
        }
    
    # Final Summary
    print(f"\n" + "=" * 60)
    print("📊 FINAL UI CUISINE SUMMARY")
    print("=" * 60)
    
    excellent_count = 0
    good_count = 0
    poor_count = 0
    
    for cuisine, result in results.items():
        status_icon = "✅" if result['quality'] == 'excellent' else "🔶" if result['quality'] == 'good' else "❌"
        print(f"{status_icon} {cuisine.title()}: {result['distinct_recipes']}/{result['total_recipes']} distinct recipes ({result['quality']})")
        
        if result['quality'] == 'excellent':
            excellent_count += 1
        elif result['quality'] == 'good':
            good_count += 1
        else:
            poor_count += 1
    
    print(f"\n📈 STATISTICS:")
    print(f"   Excellent cuisines: {excellent_count}/5")
    print(f"   Good cuisines: {good_count}/5")
    print(f"   Poor cuisines: {poor_count}/5")
    
    success_rate = (excellent_count + good_count) / 5 * 100
    print(f"   Overall success rate: {success_rate:.0f}%")
    
    print(f"\n🎯 UI RECOMMENDATION:")
    if excellent_count >= 4:
        print("   🎉 EXCELLENT! All cuisines provide great recipe variety.")
        print("   ✅ Users will get distinct, authentic cooking experiences.")
        print("   ✅ Ready for production deployment!")
    elif excellent_count + good_count >= 4:
        print("   👍 GOOD! Most cuisines provide good recipe variety.")
        print("   ✅ Users will generally get distinct cooking experiences.")
        print("   🔧 Consider minor improvements for remaining cuisines.")
    else:
        print("   ⚠️ NEEDS IMPROVEMENT. Some cuisines still have identical steps.")
        print("   🔧 Enhance step generation for better user experience.")
    
    print(f"\n🚀 DEPLOYMENT STATUS:")
    if success_rate >= 80:
        print("   ✅ READY FOR DEPLOYMENT")
        print("   The 5 selected cuisines provide excellent recipe diversity!")
    else:
        print("   🔧 NEEDS MORE WORK")
        print("   Enhance remaining cuisines before deployment.")

if __name__ == "__main__":
    test_final_5_cuisines()