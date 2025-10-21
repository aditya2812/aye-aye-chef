#!/usr/bin/env python3
"""
Test script to demonstrate dynamic recipe variety
"""

import hashlib
import time

def simulate_variety_generation(user_id, ingredient, num_tests=10):
    """Simulate how the dynamic variety system works"""
    print(f"🧪 Testing dynamic variety for {ingredient} with user {user_id}")
    print("=" * 60)
    
    results = []
    
    for test_num in range(num_tests):
        # Simulate different time periods (every 5 minutes)
        simulated_time = int(time.time()) + (test_num * 300)  # Add 5 minutes each test
        time_seed = simulated_time // 300  # Changes every 5 minutes
        
        # Create variety seed (same logic as in the code)
        variety_seed = hashlib.md5(f"{user_id}_{time_seed}_{ingredient}".encode()).hexdigest()
        variety_index = int(variety_seed[:2], 16) % 6  # 6 different variety sets
        
        # Define the same style combinations as in the code
        smoothie_style_combinations = [
            ["CREAMY & PROTEIN-RICH", "GREEN & DETOX", "TROPICAL & EXOTIC"],
            ["DESSERT & INDULGENT", "ENERGIZING & FRESH", "SPICED & WARMING"],
            ["BREAKFAST & FILLING", "ANTIOXIDANT & BERRY", "CHOCOLATE & RICH"],
            ["SMOOTH & SILKY", "CHUNKY & TEXTURED", "FROZEN & THICK"],
            ["CITRUS & BRIGHT", "NUTTY & CREAMY", "SUPERFOOD & HEALTHY"],
            ["COFFEE & ENERGIZING", "VANILLA & SWEET", "MINT & REFRESHING"]
        ]
        
        cooking_style_combinations = [
            ["QUICK & FRESH", "COMFORT & HEARTY", "BOLD & SPICY"],
            ["ELEGANT & REFINED", "RUSTIC & HOMESTYLE", "FUSION & CREATIVE"],
            ["LIGHT & HEALTHY", "RICH & INDULGENT", "SMOKY & GRILLED"],
            ["AROMATIC & FRAGRANT", "CRISPY & TEXTURED", "SAUCY & FLAVORFUL"],
            ["TRADITIONAL & AUTHENTIC", "MODERN & INNOVATIVE", "STREET-STYLE & CASUAL"],
            ["HERB-FORWARD", "SPICE-HEAVY", "CITRUS-BRIGHT"]
        ]
        
        selected_smoothie_styles = smoothie_style_combinations[variety_index]
        selected_cooking_styles = cooking_style_combinations[variety_index]
        
        results.append({
            'test': test_num + 1,
            'time_seed': time_seed,
            'variety_index': variety_index,
            'smoothie_styles': selected_smoothie_styles,
            'cooking_styles': selected_cooking_styles
        })
        
        print(f"Test {test_num + 1:2d} | Variety Set {variety_index} | Smoothie: {selected_smoothie_styles[0][:15]}... | Cooking: {selected_cooking_styles[0][:15]}...")
    
    # Analyze variety
    unique_indices = len(set(r['variety_index'] for r in results))
    print(f"\n📊 Variety Analysis:")
    print(f"  Total tests: {num_tests}")
    print(f"  Unique variety sets used: {unique_indices}/6")
    print(f"  Variety percentage: {(unique_indices/6)*100:.1f}%")
    
    return results

def demonstrate_recipe_examples():
    """Show examples of different recipe types users would see"""
    print("\n🥤 SMOOTHIE RECIPE EXAMPLES")
    print("=" * 60)
    
    examples = [
        {
            'set': 0,
            'styles': ["CREAMY & PROTEIN-RICH", "GREEN & DETOX", "TROPICAL & EXOTIC"],
            'recipes': [
                "Protein-Packed Banana Peanut Butter Smoothie",
                "Green Banana Detox Cleanse Smoothie", 
                "Tropical Banana Coconut Paradise Smoothie"
            ]
        },
        {
            'set': 1,
            'styles': ["DESSERT & INDULGENT", "ENERGIZING & FRESH", "SPICED & WARMING"],
            'recipes': [
                "Banana Split Dessert Smoothie",
                "Fresh Banana Mint Energy Boost",
                "Spiced Banana Chai Latte Smoothie"
            ]
        },
        {
            'set': 2,
            'styles': ["BREAKFAST & FILLING", "ANTIOXIDANT & BERRY", "CHOCOLATE & RICH"],
            'recipes': [
                "Hearty Banana Oatmeal Breakfast Smoothie",
                "Banana Berry Antioxidant Power Smoothie",
                "Rich Chocolate Banana Fudge Smoothie"
            ]
        }
    ]
    
    for example in examples:
        print(f"\nVariety Set {example['set']}:")
        for i, (style, recipe) in enumerate(zip(example['styles'], example['recipes']), 1):
            print(f"  {i}. {style}: {recipe}")
    
    print("\n🍳 COOKING RECIPE EXAMPLES")
    print("=" * 60)
    
    cooking_examples = [
        {
            'set': 0,
            'styles': ["QUICK & FRESH", "COMFORT & HEARTY", "BOLD & SPICY"],
            'recipes': [
                "Quick Pan-Seared Paneer with Fresh Herbs",
                "Hearty Baked Paneer Casserole",
                "Spicy Paneer Tikka Masala"
            ]
        },
        {
            'set': 1,
            'styles': ["ELEGANT & REFINED", "RUSTIC & HOMESTYLE", "FUSION & CREATIVE"],
            'recipes': [
                "Elegant Paneer Wellington",
                "Rustic Paneer Curry",
                "Asian-Fusion Paneer Stir-Fry"
            ]
        }
    ]
    
    for example in cooking_examples:
        print(f"\nVariety Set {example['set']}:")
        for i, (style, recipe) in enumerate(zip(example['styles'], example['recipes']), 1):
            print(f"  {i}. {style}: {recipe}")

def main():
    """Demonstrate the dynamic variety system"""
    print("🚀 DYNAMIC RECIPE VARIETY DEMONSTRATION")
    print("=" * 60)
    
    # Test with different users and ingredients
    test_cases = [
        ("user123", "banana"),
        ("user456", "paneer"),
        ("user789", "spinach")
    ]
    
    for user_id, ingredient in test_cases:
        print(f"\n👤 User: {user_id} | 🥘 Ingredient: {ingredient}")
        simulate_variety_generation(user_id, ingredient, 6)
    
    demonstrate_recipe_examples()
    
    print("\n" + "=" * 60)
    print("🎯 HOW IT WORKS:")
    print("1. System creates a seed based on user_id + time (changes every 5 minutes)")
    print("2. Seed determines which of 6 variety sets to use")
    print("3. Each variety set has completely different recipe styles")
    print("4. Same user gets same recipes for 5 minutes, then variety changes")
    print("5. Different users get different recipes even at same time")
    
    print("\n✅ BENEFITS:")
    print("• Users see different recipes each time they use the app")
    print("• Recipes are still consistent within a short time window")
    print("• True variety showcases ingredient versatility")
    print("• System works for any ingredient, cuisine, or meal type")

if __name__ == "__main__":
    main()