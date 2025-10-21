#!/usr/bin/env python3
"""
Advanced Recipe Features - Interactive and Personalized
"""

class AdvancedRecipeSystem:
    
    def __init__(self):
        self.skill_levels = {
            "beginner": {
                "step_detail": "very_detailed",
                "techniques": "basic",
                "timing": "generous",
                "explanations": True
            },
            "intermediate": {
                "step_detail": "detailed",
                "techniques": "standard",
                "timing": "accurate",
                "explanations": False
            },
            "advanced": {
                "step_detail": "concise",
                "techniques": "advanced",
                "timing": "precise",
                "explanations": False
            }
        }
    
    def generate_adaptive_steps(self, ingredients, cuisine, user_skill="intermediate", dietary_restrictions=None):
        """Generate steps that adapt to user skill level and dietary needs"""
        
        skill_config = self.skill_levels.get(user_skill, self.skill_levels["intermediate"])
        steps = []
        
        # Skill-based step generation
        if skill_config["step_detail"] == "very_detailed":
            # Beginner steps with explanations
            steps.append("🔥 Heat Setup: Heat 2-3 tablespoons oil in a heavy-bottomed pan over medium heat. You'll know it's ready when the oil shimmers but doesn't smoke (about 2 minutes).")
            steps.append("🧅 Aromatics Foundation: Add finely chopped onions. Cook for 5-6 minutes, stirring occasionally, until they turn golden brown. This creates the flavor base for your dish.")
        else:
            # Standard/Advanced steps
            steps.append("Heat oil in pan over medium heat until shimmering.")
            steps.append("Sauté onions until golden brown, about 5-6 minutes.")
        
        # Add dietary adaptations
        if dietary_restrictions:
            steps = self.adapt_for_dietary_restrictions(steps, dietary_restrictions)
        
        return steps
    
    def adapt_for_dietary_restrictions(self, steps, restrictions):
        """Modify steps based on dietary restrictions"""
        adapted_steps = []
        
        for step in steps:
            adapted_step = step
            
            if "vegan" in restrictions:
                adapted_step = adapted_step.replace("ghee", "coconut oil")
                adapted_step = adapted_step.replace("cream", "coconut cream")
                adapted_step = adapted_step.replace("paneer", "firm tofu")
            
            if "gluten-free" in restrictions:
                adapted_step = adapted_step.replace("naan", "rice")
                adapted_step = adapted_step.replace("bread", "gluten-free bread")
            
            if "low-sodium" in restrictions:
                adapted_step = adapted_step.replace("soy sauce", "low-sodium soy sauce")
                adapted_step += " (Use minimal salt - taste as you go)"
            
            adapted_steps.append(adapted_step)
        
        return adapted_steps
    
    def generate_interactive_steps(self, ingredients, cuisine):
        """Generate steps with interactive elements and timing"""
        
        interactive_steps = [
            {
                "step_number": 1,
                "instruction": "Heat 2-3 tablespoons oil in a heavy-bottomed pan over medium heat",
                "timing": "2 minutes",
                "visual_cue": "Oil should shimmer but not smoke",
                "audio_cue": "No sizzling sound yet",
                "tips": ["Use a heavy pan for even heat distribution"],
                "common_mistakes": ["Don't let oil smoke - it will taste bitter"],
                "next_step_trigger": "Oil is shimmering"
            },
            {
                "step_number": 2,
                "instruction": "Add 1 tsp cumin seeds and let them splutter",
                "timing": "30 seconds",
                "visual_cue": "Seeds will dance and change color slightly",
                "audio_cue": "Gentle popping/crackling sound",
                "tips": ["This releases the essential oils in the spices"],
                "common_mistakes": ["Don't let them burn - they'll taste bitter"],
                "next_step_trigger": "Seeds are fragrant and lightly colored"
            },
            {
                "step_number": 3,
                "instruction": "Add finely chopped onions and cook until golden brown",
                "timing": "5-6 minutes",
                "visual_cue": "Onions turn from white to golden brown",
                "audio_cue": "Steady sizzling sound",
                "tips": ["Stir occasionally to prevent sticking", "Golden brown onions = sweet flavor"],
                "common_mistakes": ["Don't rush - properly cooked onions are key to flavor"],
                "next_step_trigger": "Onions are golden brown and smell sweet"
            }
        ]
        
        return interactive_steps
    
    def generate_video_timestamps(self, steps):
        """Generate timestamps for video recipe integration"""
        timestamps = []
        current_time = 0
        
        for i, step in enumerate(steps):
            # Estimate time based on step complexity
            if "prep" in step.lower():
                duration = 60  # 1 minute for prep
            elif "heat" in step.lower():
                duration = 120  # 2 minutes for heating
            elif "cook" in step.lower() and "minute" in step.lower():
                # Extract cooking time from step
                import re
                time_match = re.search(r'(\d+)-?(\d+)?\s*minute', step)
                if time_match:
                    duration = int(time_match.group(1)) * 60
                else:
                    duration = 300  # Default 5 minutes
            else:
                duration = 180  # Default 3 minutes
            
            timestamps.append({
                "step": i + 1,
                "start_time": current_time,
                "end_time": current_time + duration,
                "instruction": step,
                "duration_seconds": duration
            })
            
            current_time += duration
        
        return timestamps
    
    def generate_shopping_list(self, ingredients, cuisine, servings):
        """Generate detailed shopping list with quantities and alternatives"""
        
        shopping_list = {
            "fresh_produce": [],
            "pantry_staples": [],
            "spices_herbs": [],
            "dairy_proteins": [],
            "alternatives": {}
        }
        
        # Categorize ingredients
        for ingredient in ingredients:
            name = ingredient["name"].lower()
            quantity = f"{ingredient['grams']}g"
            
            if name in ["onion", "garlic", "ginger", "tomato", "spinach", "cilantro"]:
                shopping_list["fresh_produce"].append(f"{quantity} {ingredient['name']}")
            elif name in ["paneer", "chicken", "fish", "eggs"]:
                shopping_list["dairy_proteins"].append(f"{quantity} {ingredient['name']}")
            elif name in ["oil", "ghee", "rice", "flour"]:
                shopping_list["pantry_staples"].append(f"{quantity} {ingredient['name']}")
        
        # Add cuisine-specific spices
        if cuisine.lower() == "indian":
            shopping_list["spices_herbs"].extend([
                "Cumin seeds", "Turmeric powder", "Coriander powder", 
                "Garam masala", "Red chili powder", "Fresh ginger", "Fresh garlic"
            ])
            shopping_list["alternatives"]["paneer"] = "Firm tofu (for vegan option)"
            shopping_list["alternatives"]["ghee"] = "Coconut oil (for vegan option)"
        
        elif cuisine.lower() == "mediterranean":
            shopping_list["spices_herbs"].extend([
                "Oregano", "Basil", "Thyme", "Extra virgin olive oil",
                "Lemon", "Garlic", "Fresh herbs"
            ])
            shopping_list["alternatives"]["olive oil"] = "Avocado oil (for high heat)"
        
        return shopping_list
    
    def generate_meal_prep_instructions(self, recipe_steps, servings):
        """Generate meal prep and storage instructions"""
        
        meal_prep = {
            "advance_prep": [
                "Chop all vegetables and store in airtight containers (up to 2 days ahead)",
                "Measure out all spices into small bowls",
                "Marinate proteins if required (up to 24 hours ahead)"
            ],
            "cooking_day": [
                "Remove ingredients from refrigerator 30 minutes before cooking",
                "Have all ingredients prepped and ready before starting",
                "Cook according to recipe steps"
            ],
            "storage": {
                "refrigerator": "Store in airtight containers for up to 3-4 days",
                "freezer": "Can be frozen for up to 2 months (texture may change slightly)",
                "reheating": "Reheat gently on stovetop or microwave, adding a splash of water if needed"
            },
            "scaling": {
                "double_batch": "Double all ingredients and cooking times. May need larger cookware.",
                "half_batch": "Halve all ingredients. Cooking times remain mostly the same."
            }
        }
        
        return meal_prep

# Example usage
if __name__ == "__main__":
    system = AdvancedRecipeSystem()
    
    ingredients = [
        {"name": "paneer", "grams": 200},
        {"name": "spinach", "grams": 150}
    ]
    
    # Generate adaptive steps
    beginner_steps = system.generate_adaptive_steps(ingredients, "indian", "beginner")
    print("👶 BEGINNER STEPS:")
    for step in beginner_steps:
        print(f"• {step}")
    
    # Generate interactive steps
    interactive = system.generate_interactive_steps(ingredients, "indian")
    print("\n🎮 INTERACTIVE STEPS:")
    for step in interactive[:2]:  # Show first 2 steps
        print(f"Step {step['step_number']}: {step['instruction']}")
        print(f"  ⏱️  Timing: {step['timing']}")
        print(f"  👀 Visual: {step['visual_cue']}")
        print(f"  💡 Tip: {step['tips'][0]}")
    
    # Generate shopping list
    shopping = system.generate_shopping_list(ingredients, "indian", 2)
    print(f"\n🛒 SHOPPING LIST:")
    print(f"Fresh Produce: {shopping['fresh_produce']}")
    print(f"Spices: {shopping['spices_herbs'][:3]}...")  # Show first 3