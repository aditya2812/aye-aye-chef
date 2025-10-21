#!/usr/bin/env python3
"""
Recipe Template System - Modular Step Generation
"""

class RecipeTemplateEngine:
    def __init__(self):
        self.templates = {
            "indian": {
                "prep_template": "Wash and prepare {ingredients}. Cut {main_ingredient} into {cut_style}.",
                "base_template": "Heat {cooking_fat} in a {cookware} over {heat_level}. Add {tempering_spices} and let splutter for 30 seconds.",
                "aromatics_template": "Add {aromatics} and cook until {doneness_indicator}. This forms the flavor base.",
                "main_cooking_template": "Add {main_ingredient} and cook for {time} until {doneness}. {technique_note}.",
                "spice_template": "Add {spice_blend} and cook for 30 seconds until fragrant. {spice_note}.",
                "liquid_template": "Add {liquid} and bring to a {cooking_style}. Cover and cook for {time}.",
                "finishing_template": "Finish with {finishing_ingredients}. {resting_instruction}.",
                "serving_template": "Serve hot with {accompaniments}. Garnish with {garnish}."
            },
            "mediterranean": {
                "prep_template": "Prepare {ingredients} by washing and cutting into {cut_style}. Pat dry if needed.",
                "base_template": "Heat {cooking_fat} in a {cookware} over {heat_level} until shimmering.",
                "aromatics_template": "Add {aromatics} and sauté until {doneness_indicator}. Season with salt and pepper.",
                "main_cooking_template": "Add {main_ingredient} and cook for {time} until {doneness}. {technique_note}.",
                "herb_template": "Add {herbs} and cook briefly until fragrant. {herb_note}.",
                "liquid_template": "Deglaze with {liquid} and let reduce. Simmer for {time}.",
                "finishing_template": "Remove from heat and add {finishing_ingredients}. {final_note}.",
                "serving_template": "Serve immediately with {accompaniments}. Drizzle with {final_drizzle}."
            }
        }
        
        self.ingredient_data = {
            "paneer": {
                "cut_style": "1-inch cubes",
                "cooking_time": "2-3 minutes per side",
                "doneness": "lightly golden",
                "technique_note": "Handle gently to prevent breaking"
            },
            "chicken": {
                "cut_style": "bite-sized pieces",
                "cooking_time": "6-8 minutes",
                "doneness": "golden brown and cooked through",
                "technique_note": "Ensure internal temperature reaches 165°F (74°C)"
            },
            "spinach": {
                "cut_style": "roughly chopped",
                "cooking_time": "2-3 minutes",
                "doneness": "wilted but still bright green",
                "technique_note": "Add last to prevent overcooking"
            }
        }
        
        self.cuisine_data = {
            "indian": {
                "cooking_fat": "2-3 tablespoons ghee or oil",
                "cookware": "heavy-bottomed pan",
                "tempering_spices": "1 tsp cumin seeds",
                "aromatics": "1 finely chopped onion and 1 tbsp ginger-garlic paste",
                "spice_blend": "1/2 tsp turmeric, 1 tsp coriander powder, 1/2 tsp red chili powder",
                "liquid": "1/2 cup water or broth",
                "finishing_ingredients": "2 tbsp cream and fresh coriander",
                "accompaniments": "basmati rice, naan, or roti",
                "garnish": "fresh coriander and lemon wedges"
            },
            "mediterranean": {
                "cooking_fat": "3 tablespoons extra virgin olive oil",
                "cookware": "large skillet",
                "aromatics": "3 cloves minced garlic and 1 sliced onion",
                "herbs": "1 tsp oregano and 1/2 tsp basil",
                "liquid": "1/4 cup white wine or broth",
                "finishing_ingredients": "fresh lemon juice and chopped herbs",
                "accompaniments": "crusty bread, pasta, or rice",
                "final_drizzle": "extra virgin olive oil"
            }
        }
    
    def generate_recipe_steps(self, ingredients, cuisine, cooking_method="sautéed"):
        """Generate detailed recipe steps using templates"""
        steps = []
        template = self.templates.get(cuisine, self.templates["mediterranean"])
        cuisine_info = self.cuisine_data.get(cuisine, self.cuisine_data["mediterranean"])
        
        main_ingredient = ingredients[0]["name"] if ingredients else "main ingredient"
        ingredient_info = self.ingredient_data.get(main_ingredient, {
            "cut_style": "appropriate pieces",
            "cooking_time": "5-7 minutes",
            "doneness": "cooked through",
            "technique_note": "Cook until tender"
        })
        
        # Generate each step using templates
        ingredient_names = [ing["name"] for ing in ingredients]
        
        # Prep step
        steps.append(template["prep_template"].format(
            ingredients=", ".join(ingredient_names),
            main_ingredient=main_ingredient,
            cut_style=ingredient_info["cut_style"]
        ))
        
        # Base cooking step
        steps.append(template["base_template"].format(
            cooking_fat=cuisine_info["cooking_fat"],
            cookware=cuisine_info["cookware"],
            heat_level="medium heat",
            tempering_spices=cuisine_info.get("tempering_spices", "aromatics")
        ))
        
        # Aromatics step
        steps.append(template["aromatics_template"].format(
            aromatics=cuisine_info["aromatics"],
            doneness_indicator="golden brown" if cuisine == "indian" else "translucent"
        ))
        
        # Main cooking step
        steps.append(template["main_cooking_template"].format(
            main_ingredient=main_ingredient,
            time=ingredient_info["cooking_time"],
            doneness=ingredient_info["doneness"],
            technique_note=ingredient_info["technique_note"]
        ))
        
        # Cuisine-specific steps
        if cuisine == "indian":
            steps.append(template["spice_template"].format(
                spice_blend=cuisine_info["spice_blend"],
                spice_note="This creates the flavor foundation"
            ))
            
            steps.append(template["liquid_template"].format(
                liquid=cuisine_info["liquid"],
                cooking_style="gentle simmer",
                time="10-12 minutes"
            ))
        
        elif cuisine == "mediterranean":
            steps.append(template["herb_template"].format(
                herbs=cuisine_info["herbs"],
                herb_note="Fresh herbs provide the best flavor"
            ))
            
            steps.append(template["liquid_template"].format(
                liquid=cuisine_info["liquid"],
                time="3-5 minutes"
            ))
        
        # Finishing step
        steps.append(template["finishing_template"].format(
            finishing_ingredients=cuisine_info["finishing_ingredients"],
            resting_instruction="Let rest for 2 minutes" if cuisine == "indian" else "Taste and adjust seasoning",
            final_note="The dish is now ready"
        ))
        
        # Serving step
        steps.append(template["serving_template"].format(
            accompaniments=cuisine_info["accompaniments"],
            garnish=cuisine_info.get("garnish", "fresh herbs"),
            final_drizzle=cuisine_info.get("final_drizzle", "olive oil")
        ))
        
        return steps
    
    def generate_technique_explanations(self, cuisine):
        """Generate cooking technique explanations"""
        techniques = {
            "indian": {
                "tempering": "Tempering (tadka) involves heating whole spices in oil to release their essential oils and create a flavor base.",
                "layering": "Indian cooking builds flavors in layers - each spice and ingredient is added at the right time for maximum impact.",
                "slow_cooking": "Many Indian dishes benefit from slow, gentle cooking to allow spices to meld and develop complex flavors."
            },
            "mediterranean": {
                "sautéing": "Sautéing means 'to jump' in French - ingredients should move freely in the pan with proper heat and oil.",
                "herb_timing": "Add hardy herbs (rosemary, thyme) early in cooking, but delicate herbs (basil, parsley) at the end.",
                "olive_oil": "Use regular olive oil for cooking and finish with extra virgin olive oil for the best flavor."
            }
        }
        
        return techniques.get(cuisine, {})

# Example usage
if __name__ == "__main__":
    engine = RecipeTemplateEngine()
    
    ingredients = [
        {"name": "paneer", "grams": 200},
        {"name": "spinach", "grams": 150}
    ]
    
    print("🇮🇳 INDIAN RECIPE (Template-Generated):")
    indian_steps = engine.generate_recipe_steps(ingredients, "indian")
    for i, step in enumerate(indian_steps, 1):
        print(f"{i}. {step}")
    
    print("\n🇬🇷 MEDITERRANEAN RECIPE (Template-Generated):")
    med_steps = engine.generate_recipe_steps(ingredients, "mediterranean")
    for i, step in enumerate(med_steps, 1):
        print(f"{i}. {step}")
    
    print("\n🔧 INDIAN COOKING TECHNIQUES:")
    techniques = engine.generate_technique_explanations("indian")
    for technique, explanation in techniques.items():
        print(f"• {technique.title()}: {explanation}")