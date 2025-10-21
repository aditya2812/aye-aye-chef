#!/usr/bin/env python3
"""
Enhanced Recipe System - Dynamic Step Generation
"""

def generate_cuisine_specific_steps(ingredients, cuisine_type, cooking_method="sautéed"):
    """Generate detailed, cuisine-specific cooking steps"""
    
    # Cuisine-specific cooking techniques and flavor profiles
    cuisine_profiles = {
        "indian": {
            "base_spices": ["cumin seeds", "mustard seeds", "turmeric", "coriander powder", "garam masala"],
            "aromatics": ["ginger-garlic paste", "onions", "green chilies"],
            "cooking_fat": "ghee or oil",
            "finishing": ["fresh coriander", "cream", "lemon juice"],
            "techniques": ["tempering (tadka)", "slow cooking", "layering flavors"],
            "temperatures": {"low": "simmer", "medium": "sauté", "high": "tempering"}
        },
        "mediterranean": {
            "base_spices": ["oregano", "basil", "thyme", "rosemary"],
            "aromatics": ["garlic", "onions", "shallots"],
            "cooking_fat": "extra virgin olive oil",
            "finishing": ["fresh herbs", "lemon zest", "parmesan"],
            "techniques": ["sautéing", "grilling", "roasting"],
            "temperatures": {"low": "gentle simmer", "medium": "golden sauté", "high": "sear"}
        },
        "asian": {
            "base_spices": ["ginger", "garlic", "soy sauce", "sesame oil"],
            "aromatics": ["scallions", "ginger", "garlic"],
            "cooking_fat": "vegetable oil or sesame oil",
            "finishing": ["sesame seeds", "scallions", "cilantro"],
            "techniques": ["stir-frying", "steaming", "quick cooking"],
            "temperatures": {"low": "gentle steam", "medium": "stir-fry", "high": "wok hei"}
        }
    }
    
    profile = cuisine_profiles.get(cuisine_type.lower(), cuisine_profiles["mediterranean"])
    
    # Generate dynamic steps based on ingredients and cuisine
    steps = []
    
    # Step 1: Preparation
    prep_ingredients = [ing["name"] for ing in ingredients]
    steps.append(f"Prepare ingredients: Wash and chop {', '.join(prep_ingredients[:3])}. Pat dry and cut into uniform pieces for even cooking.")
    
    # Step 2: Heat and aromatics (cuisine-specific)
    if cuisine_type.lower() == "indian":
        steps.append(f"Heat 2-3 tablespoons {profile['cooking_fat']} in a heavy-bottomed pan over medium heat. Add 1 tsp cumin seeds and let them splutter for 30 seconds until fragrant.")
        steps.append(f"Add finely chopped onions and sauté for 5-6 minutes until golden brown. Add 1 tbsp ginger-garlic paste and cook for 1 minute until the raw smell disappears.")
    elif cuisine_type.lower() == "mediterranean":
        steps.append(f"Heat 3 tablespoons {profile['cooking_fat']} in a large skillet over medium heat. Add minced garlic and cook for 30 seconds until fragrant but not browned.")
        steps.append(f"Add sliced onions and cook for 3-4 minutes until translucent. Season with salt and freshly ground black pepper.")
    
    # Step 3: Main ingredient cooking (ingredient-specific)
    main_ingredient = ingredients[0]["name"] if ingredients else "main ingredient"
    if "paneer" in main_ingredient.lower():
        steps.append(f"Gently add paneer cubes to the pan. Cook for 2-3 minutes on each side until lightly golden. Remove and set aside to prevent overcooking.")
    elif "chicken" in main_ingredient.lower():
        steps.append(f"Add chicken pieces to the pan. Cook for 6-8 minutes, turning once, until golden brown on both sides and cooked through (internal temp 165°F/74°C).")
    else:
        steps.append(f"Add {main_ingredient} to the pan and cook for 4-5 minutes until lightly browned and heated through.")
    
    # Step 4: Spice building (cuisine-specific)
    if cuisine_type.lower() == "indian":
        steps.append(f"Add 1/2 tsp turmeric, 1 tsp coriander powder, and 1/2 tsp red chili powder. Cook for 30 seconds until spices are fragrant and well combined.")
        if len(ingredients) > 1:
            steps.append(f"Add remaining vegetables and cook for 5-7 minutes until tender. If using leafy greens, add them last and cook until just wilted.")
    elif cuisine_type.lower() == "mediterranean":
        steps.append(f"Add 1 tsp dried oregano, 1/2 tsp dried basil, and a pinch of red pepper flakes. Stir to combine and cook for 30 seconds.")
        steps.append(f"Add remaining vegetables and cook for 8-10 minutes until tender and lightly caramelized.")
    
    # Step 5: Liquid and simmering
    if cuisine_type.lower() == "indian":
        steps.append(f"Add 1/2 cup water or broth if needed. Bring to a gentle simmer, cover, and cook for 10-12 minutes until flavors meld together.")
        steps.append(f"Return paneer to the pan and simmer for 2-3 minutes. Add 1/2 tsp garam masala and mix gently.")
    else:
        steps.append(f"Add a splash of white wine or broth if desired. Let it reduce for 1-2 minutes, then simmer for 5-7 minutes until sauce thickens slightly.")
    
    # Step 6: Finishing touches (cuisine-specific)
    if cuisine_type.lower() == "indian":
        steps.append(f"Finish with 2 tablespoons fresh cream and chopped coriander. Taste and adjust salt. Let rest for 2 minutes before serving.")
        steps.append(f"Serve hot with basmati rice, naan, or roti. Garnish with additional coriander and a wedge of lemon.")
    elif cuisine_type.lower() == "mediterranean":
        steps.append(f"Remove from heat and stir in fresh lemon juice and chopped herbs. Drizzle with extra virgin olive oil.")
        steps.append(f"Serve immediately with crusty bread, pasta, or over rice. Top with grated Parmesan if desired.")
    
    return steps

def generate_cooking_tips(cuisine_type, ingredients):
    """Generate cuisine-specific cooking tips"""
    tips = []
    
    if cuisine_type.lower() == "indian":
        tips.extend([
            "Toast whole spices for 30 seconds before grinding for maximum flavor",
            "Cook onions until golden brown - this is the flavor base for most Indian dishes",
            "Add salt in layers throughout cooking, not just at the end",
            "Let the dish rest for 5 minutes after cooking to allow flavors to meld"
        ])
    elif cuisine_type.lower() == "mediterranean":
        tips.extend([
            "Use high-quality extra virgin olive oil for the best flavor",
            "Don't overcook garlic - it should be fragrant, not browned",
            "Fresh herbs added at the end provide the brightest flavor",
            "A splash of good wine can elevate the entire dish"
        ])
    
    return tips

def generate_substitutions(cuisine_type, ingredients):
    """Generate cuisine-appropriate substitutions"""
    substitutions = []
    
    if cuisine_type.lower() == "indian":
        substitutions.extend([
            "Ghee can be substituted with vegetable oil or butter",
            "Fresh ginger-garlic paste can be replaced with 1 tsp each of ginger and garlic powder",
            "Garam masala can be made with cinnamon, cardamom, and cloves",
            "Heavy cream can be replaced with coconut milk for dairy-free option"
        ])
    elif cuisine_type.lower() == "mediterranean":
        substitutions.extend([
            "Olive oil can be substituted with avocado oil for high-heat cooking",
            "Fresh herbs can be replaced with 1/3 the amount of dried herbs",
            "White wine can be substituted with chicken or vegetable broth",
            "Parmesan can be replaced with Pecorino Romano or nutritional yeast"
        ])
    
    return substitutions

# Example usage
if __name__ == "__main__":
    ingredients = [
        {"name": "paneer", "grams": 200},
        {"name": "spinach", "grams": 150},
        {"name": "onion", "grams": 100}
    ]
    
    indian_steps = generate_cuisine_specific_steps(ingredients, "indian")
    mediterranean_steps = generate_cuisine_specific_steps(ingredients, "mediterranean")
    
    print("🇮🇳 INDIAN RECIPE STEPS:")
    for i, step in enumerate(indian_steps, 1):
        print(f"{i}. {step}")
    
    print("\n🇬🇷 MEDITERRANEAN RECIPE STEPS:")
    for i, step in enumerate(mediterranean_steps, 1):
        print(f"{i}. {step}")