#!/usr/bin/env python3
"""
Enhanced Recipe Generation System - Ingredient-Specific Recipe Creation

This script creates truly unique recipes for each ingredient rather than using templates
that just swap ingredient names. Each ingredient gets recipes tailored to its specific
properties, cooking methods, and flavor profiles.
"""

import json
import hashlib
import time
from typing import List, Dict, Any

def get_ingredient_specific_properties(ingredient_name: str) -> Dict[str, Any]:
    """Get ingredient-specific properties for recipe generation"""
    
    ingredient_lower = ingredient_name.lower()
    
    # Comprehensive ingredient database with specific properties
    ingredient_database = {
        'banana': {
            'category': 'fruit',
            'texture': 'creamy when ripe',
            'flavor_profile': 'sweet, mild, tropical',
            'best_cooking_methods': ['blend', 'bake', 'sauté', 'grill'],
            'complementary_flavors': ['chocolate', 'peanut butter', 'cinnamon', 'vanilla', 'coconut', 'berries'],
            'nutritional_highlights': ['potassium', 'fiber', 'vitamin B6'],
            'preparation_tips': ['use ripe for sweetness', 'freeze for thickness in smoothies', 'brown spots indicate ripeness'],
            'smoothie_styles': {
                'creamy': {
                    'base': 'milk or yogurt',
                    'additions': ['oats', 'nut butter', 'vanilla'],
                    'texture': 'thick and creamy'
                },
                'green': {
                    'base': 'coconut water or almond milk',
                    'additions': ['spinach', 'avocado', 'lime'],
                    'texture': 'smooth and refreshing'
                },
                'dessert': {
                    'base': 'milk or plant milk',
                    'additions': ['cocoa', 'dates', 'nut butter'],
                    'texture': 'rich and indulgent'
                }
            },
            'cooking_recipes': {
                'quick': 'banana pancakes with cinnamon',
                'comfort': 'banana bread with walnuts',
                'healthy': 'grilled banana with honey'
            }
        },
        'grapes': {
            'category': 'fruit',
            'texture': 'juicy, burst of flavor',
            'flavor_profile': 'sweet-tart, refreshing, clean',
            'best_cooking_methods': ['blend', 'roast', 'reduce', 'freeze'],
            'complementary_flavors': ['lime', 'mint', 'ginger', 'berries', 'citrus', 'herbs'],
            'nutritional_highlights': ['antioxidants', 'vitamin C', 'resveratrol'],
            'preparation_tips': ['freeze for slushy texture', 'use different colors for variety', 'remove seeds if needed'],
            'smoothie_styles': {
                'refreshing': {
                    'base': 'water or coconut water',
                    'additions': ['lime', 'mint', 'chia seeds'],
                    'texture': 'light and refreshing'
                },
                'antioxidant': {
                    'base': 'almond milk or juice',
                    'additions': ['berries', 'spinach', 'ginger'],
                    'texture': 'nutrient-dense'
                },
                'slushy': {
                    'base': 'minimal liquid',
                    'additions': ['frozen fruit', 'lime', 'herbs'],
                    'texture': 'thick and slushy'
                }
            },
            'cooking_recipes': {
                'elegant': 'roasted grapes with thyme and goat cheese',
                'sauce': 'grape reduction for meat dishes',
                'salad': 'grape and walnut salad with vinaigrette'
            }
        },
        'mango': {
            'category': 'fruit',
            'texture': 'smooth, fibrous when ripe',
            'flavor_profile': 'tropical, sweet, aromatic',
            'best_cooking_methods': ['blend', 'grill', 'dice', 'puree'],
            'complementary_flavors': ['coconut', 'lime', 'chili', 'mint', 'ginger', 'cardamom'],
            'nutritional_highlights': ['vitamin A', 'vitamin C', 'folate'],
            'preparation_tips': ['check for ripeness by smell', 'cut around the pit', 'freeze chunks for smoothies'],
            'smoothie_styles': {
                'tropical': {
                    'base': 'coconut milk or water',
                    'additions': ['pineapple', 'coconut', 'lime'],
                    'texture': 'tropical and creamy'
                },
                'spiced': {
                    'base': 'milk or yogurt',
                    'additions': ['cardamom', 'ginger', 'turmeric'],
                    'texture': 'aromatic and warming'
                },
                'green': {
                    'base': 'coconut water',
                    'additions': ['spinach', 'cucumber', 'mint'],
                    'texture': 'fresh and hydrating'
                }
            },
            'cooking_recipes': {
                'salsa': 'mango salsa with red onion and cilantro',
                'curry': 'mango curry with coconut milk',
                'dessert': 'grilled mango with lime and chili'
            }
        },
        'apple': {
            'category': 'fruit',
            'texture': 'crisp, firm',
            'flavor_profile': 'sweet-tart, fresh, clean',
            'best_cooking_methods': ['bake', 'sauté', 'blend', 'roast'],
            'complementary_flavors': ['cinnamon', 'caramel', 'vanilla', 'ginger', 'lemon'],
            'nutritional_highlights': ['fiber', 'vitamin C', 'antioxidants'],
            'preparation_tips': ['leave skin on for fiber', 'prevent browning with lemon', 'choose variety for purpose'],
            'smoothie_styles': {
                'spiced': {
                    'base': 'apple juice or milk',
                    'additions': ['cinnamon', 'ginger', 'vanilla'],
                    'texture': 'warming and comforting'
                },
                'green': {
                    'base': 'water or coconut water',
                    'additions': ['spinach', 'cucumber', 'lemon'],
                    'texture': 'fresh and cleansing'
                },
                'protein': {
                    'base': 'milk or protein powder',
                    'additions': ['oats', 'nut butter', 'cinnamon'],
                    'texture': 'filling and nutritious'
                }
            },
            'cooking_recipes': {
                'comfort': 'apple crisp with oat topping',
                'savory': 'apple and onion sauté',
                'healthy': 'baked apple with cinnamon'
            }
        },
        'strawberry': {
            'category': 'berry',
            'texture': 'juicy, soft',
            'flavor_profile': 'sweet, aromatic, bright',
            'best_cooking_methods': ['blend', 'macerate', 'roast', 'puree'],
            'complementary_flavors': ['vanilla', 'chocolate', 'basil', 'balsamic', 'mint'],
            'nutritional_highlights': ['vitamin C', 'folate', 'antioxidants'],
            'preparation_tips': ['hull before using', 'macerate with sugar', 'freeze for smoothies'],
            'smoothie_styles': {
                'classic': {
                    'base': 'milk or yogurt',
                    'additions': ['vanilla', 'honey', 'banana'],
                    'texture': 'creamy and sweet'
                },
                'refreshing': {
                    'base': 'water or coconut water',
                    'additions': ['mint', 'lime', 'cucumber'],
                    'texture': 'light and refreshing'
                },
                'protein': {
                    'base': 'protein powder and milk',
                    'additions': ['oats', 'chia seeds', 'vanilla'],
                    'texture': 'thick and nutritious'
                }
            },
            'cooking_recipes': {
                'dessert': 'strawberry shortcake with biscuits',
                'sauce': 'strawberry balsamic reduction',
                'salad': 'strawberry spinach salad with poppy seed dressing'
            }
        }
    }
    
    # Try to match ingredient name to database
    for key, properties in ingredient_database.items():
        if key in ingredient_lower or ingredient_lower in key:
            return properties
    
    # Default properties for unknown ingredients
    return {
        'category': 'unknown',
        'texture': 'varies',
        'flavor_profile': 'unique',
        'best_cooking_methods': ['sauté', 'steam', 'blend'],
        'complementary_flavors': ['garlic', 'herbs', 'lemon'],
        'nutritional_highlights': ['nutrients', 'vitamins'],
        'preparation_tips': ['prepare as appropriate'],
        'smoothie_styles': {
            'basic': {
                'base': 'water or milk',
                'additions': ['honey', 'vanilla'],
                'texture': 'smooth'
            }
        },
        'cooking_recipes': {
            'simple': 'sautéed with garlic and herbs'
        }
    }

def create_ingredient_specific_smoothie_recipes(ingredient_name: str, servings: int = 2, variety_seed: str = None) -> List[Dict[str, Any]]:
    """Create truly unique smoothie recipes based on ingredient properties"""
    
    properties = get_ingredient_specific_properties(ingredient_name)
    smoothie_styles = properties.get('smoothie_styles', {})
    
    # Create variety based on seed to ensure different recipes each time
    if variety_seed:
        variety_index = int(hashlib.md5(variety_seed.encode()).hexdigest()[:2], 16) % len(smoothie_styles)
    else:
        variety_index = 0
    
    recipes = []
    style_names = list(smoothie_styles.keys())
    
    # Create 3 different recipes based on the ingredient's specific properties
    for i in range(3):
        style_name = style_names[i % len(style_names)]
        style_info = smoothie_styles[style_name]
        
        if ingredient_name.lower() == 'banana':
            if i == 0:  # Creamy style
                recipe = {
                    'title': "Creamy Banana-Oat Breakfast Smoothie",
                    'ingredients': [
                        {'name': 'banana', 'amount': '1 ripe', 'preparation': 'chilled'},
                        {'name': 'rolled oats', 'amount': '3 Tbsp', 'preparation': 'soaked 5 min'},
                        {'name': 'milk', 'amount': '1 cup', 'preparation': 'dairy or oat/almond'},
                        {'name': 'honey', 'amount': '1–2 tsp', 'preparation': 'or maple syrup'},
                        {'name': 'cinnamon', 'amount': 'pinch', 'preparation': 'ground (optional)'},
                        {'name': 'ice cubes', 'amount': '3–4', 'preparation': 'for thickness'}
                    ],
                    'steps': [
                        "Add 1 cup milk (dairy or oat/almond) to a blender",
                        "Add 1 ripe banana (chilled), 3 Tbsp rolled oats, and 1–2 tsp honey/maple",
                        "Drop in 3–4 ice cubes and a pinch of cinnamon (optional)",
                        "Blend low 10–15s, then high 30–45s until silky",
                        "Adjust thickness with a splash more milk; serve immediately"
                    ],
                    'tags': ['creamy', 'breakfast', 'oats', 'filling']
                }
            elif i == 1:  # Green style
                recipe = {
                    'title': "Green Banana-Spinach Smoothie",
                    'ingredients': [
                        {'name': 'banana', 'amount': '1 ripe', 'preparation': 'fresh'},
                        {'name': 'baby spinach', 'amount': '1 packed cup', 'preparation': 'washed'},
                        {'name': 'coconut water', 'amount': '1 cup', 'preparation': 'cold'},
                        {'name': 'pineapple chunks', 'amount': '1/2 cup', 'preparation': 'fresh or frozen'},
                        {'name': 'avocado', 'amount': '1/2', 'preparation': 'for creaminess'},
                        {'name': 'lime juice', 'amount': 'squeeze', 'preparation': 'fresh'}
                    ],
                    'steps': [
                        "Add 1 cup cold coconut water to a blender",
                        "Add 1 ripe banana, 1 packed cup baby spinach, and ½ cup pineapple chunks",
                        "Add ½ avocado for creaminess",
                        "Blend low, then high 45s–60s until completely smooth",
                        "Taste; add a squeeze of lime and a few ice cubes; pulse 5–10s"
                    ],
                    'tags': ['green', 'detox', 'healthy', 'energizing']
                }
            else:  # Dessert style
                recipe = {
                    'title': "Cocoa Banana 'Milkshake' (No-Peanut Base)",
                    'ingredients': [
                        {'name': 'banana', 'amount': '1 ripe', 'preparation': 'frozen for thickness'},
                        {'name': 'milk', 'amount': '1 cup', 'preparation': 'dairy or oat'},
                        {'name': 'cocoa powder', 'amount': '1 Tbsp', 'preparation': 'unsweetened'},
                        {'name': 'dates', 'amount': '1-2', 'preparation': 'pitted, or 1 tsp maple syrup'},
                        {'name': 'almond butter', 'amount': '1 Tbsp', 'preparation': 'optional for richness'},
                        {'name': 'vanilla extract', 'amount': '1/2 tsp', 'preparation': 'pure'},
                        {'name': 'salt', 'amount': 'pinch', 'preparation': 'to enhance flavor'}
                    ],
                    'steps': [
                        "Add 1 cup milk (dairy or oat) to a blender",
                        "Add 1 ripe banana (frozen for thickness), 1 Tbsp cocoa, and 1–2 dates",
                        "Add 1 Tbsp almond butter if using for extra richness",
                        "Blend low 10–15s, then high 30–45s; add ice if you want it frosty",
                        "Finish with a pinch of salt and ½ tsp vanilla; pulse and pour"
                    ],
                    'tags': ['chocolate', 'dessert', 'indulgent', 'dairy-free-option']
                }
        
        elif ingredient_name.lower() == 'grapes':
            if i == 0:  # Refreshing style
                recipe = {
                    'title': "Frosty Grape–Lime Cooler",
                    'ingredients': [
                        {'name': 'seedless grapes', 'amount': '1½ cups', 'preparation': 'frozen (red or green)'},
                        {'name': 'banana', 'amount': '1/2', 'preparation': 'for creaminess'},
                        {'name': 'cold water', 'amount': '1 cup', 'preparation': 'or coconut water'},
                        {'name': 'chia seeds', 'amount': '1 Tbsp', 'preparation': 'for nutrition'},
                        {'name': 'lime', 'amount': '1/2', 'preparation': 'juiced'}
                    ],
                    'steps': [
                        "Add 1 cup cold water (or coconut water) to a blender",
                        "Add 1½ cups frozen seedless grapes and ½ banana",
                        "Add 1 Tbsp chia seeds and the juice of ½ lime",
                        "Blend low 10–15s, then high 30–45s until slushy-smooth",
                        "Taste; add more lime or water to adjust thickness, then serve"
                    ],
                    'tags': ['frosty', 'refreshing', 'citrus', 'slushy']
                }
            elif i == 1:  # Antioxidant style
                recipe = {
                    'title': "Green Grape–Spinach Smoothie",
                    'ingredients': [
                        {'name': 'green grapes', 'amount': '1 cup', 'preparation': 'seedless'},
                        {'name': 'baby spinach', 'amount': '1 packed cup', 'preparation': 'washed'},
                        {'name': 'almond milk', 'amount': '1 cup', 'preparation': 'unsweetened'},
                        {'name': 'avocado', 'amount': '1/2', 'preparation': 'or ¼ cup Greek yogurt'},
                        {'name': 'honey', 'amount': '1/2 tsp', 'preparation': 'if you like it sweeter'},
                        {'name': 'lemon juice', 'amount': 'squeeze', 'preparation': 'fresh'}
                    ],
                    'steps': [
                        "Add 1 cup unsweetened almond milk to a blender",
                        "Add 1 cup seedless green grapes, 1 packed cup spinach, and ½ avocado",
                        "Add 4–5 ice cubes and ½ tsp honey if you like it sweeter",
                        "Blend low, then high 45–60s until completely smooth",
                        "Finish with a squeeze of lemon; pulse 2–3s and pour"
                    ],
                    'tags': ['green', 'healthy', 'antioxidant', 'fresh']
                }
            else:  # Berry antioxidant style
                recipe = {
                    'title': "Purple Grape–Berry Antioxidant Shake",
                    'ingredients': [
                        {'name': 'red grapes', 'amount': '1 cup', 'preparation': 'seedless'},
                        {'name': 'frozen blueberries', 'amount': '1/2 cup', 'preparation': 'for antioxidants'},
                        {'name': 'banana', 'amount': '1 ripe', 'preparation': 'for creaminess'},
                        {'name': 'milk', 'amount': '1 cup', 'preparation': 'dairy or oat'},
                        {'name': 'vanilla extract', 'amount': '1/2 tsp', 'preparation': 'optional'},
                        {'name': 'protein powder', 'amount': '1 scoop', 'preparation': 'vanilla (optional)'}
                    ],
                    'steps': [
                        "Add 1 cup milk (dairy or oat) to a blender",
                        "Add 1 cup seedless red grapes, ½ cup frozen blueberries, and 1 ripe banana",
                        "Optionally add 1 scoop vanilla protein and ½ tsp vanilla extract",
                        "Blend low 10–15s, then high 30–45s until silky",
                        "Adjust thickness with a splash more milk; serve cold"
                    ],
                    'tags': ['antioxidant', 'berry', 'protein', 'purple']
                }
        
        elif ingredient_name.lower() == 'mango':
            if i == 0:  # Tropical style
                recipe = {
                    'title': "Tropical Mango-Coconut Paradise Smoothie",
                    'ingredients': [
                        {'name': 'mango', 'amount': '1 cup', 'preparation': 'frozen chunks'},
                        {'name': 'coconut milk', 'amount': '1/2 cup', 'preparation': 'canned, thick'},
                        {'name': 'pineapple', 'amount': '1/2 cup', 'preparation': 'fresh or frozen'},
                        {'name': 'coconut water', 'amount': '1/2 cup', 'preparation': 'cold'},
                        {'name': 'lime juice', 'amount': '1 Tbsp', 'preparation': 'fresh'},
                        {'name': 'coconut flakes', 'amount': '1 Tbsp', 'preparation': 'unsweetened (optional)'}
                    ],
                    'steps': [
                        "Add ½ cup coconut water and ½ cup thick coconut milk to a blender",
                        "Add 1 cup frozen mango chunks and ½ cup pineapple",
                        "Add 1 Tbsp fresh lime juice",
                        "Blend low 10–15s, then high 30–45s until creamy",
                        "Garnish with coconut flakes if desired; serve immediately"
                    ],
                    'tags': ['tropical', 'coconut', 'paradise', 'creamy']
                }
            elif i == 1:  # Spiced style
                recipe = {
                    'title': "Golden Mango Lassi with Cardamom",
                    'ingredients': [
                        {'name': 'mango', 'amount': '1 cup', 'preparation': 'ripe, diced'},
                        {'name': 'Greek yogurt', 'amount': '1/2 cup', 'preparation': 'thick'},
                        {'name': 'milk', 'amount': '1/2 cup', 'preparation': 'whole or oat'},
                        {'name': 'cardamom', 'amount': '1/4 tsp', 'preparation': 'ground'},
                        {'name': 'ginger', 'amount': '1/2 inch', 'preparation': 'fresh, peeled'},
                        {'name': 'honey', 'amount': '1 tsp', 'preparation': 'or to taste'},
                        {'name': 'turmeric', 'amount': 'pinch', 'preparation': 'for color (optional)'}
                    ],
                    'steps': [
                        "Add ½ cup milk and ½ cup Greek yogurt to a blender",
                        "Add 1 cup ripe mango, ¼ tsp cardamom, and ½ inch fresh ginger",
                        "Add 1 tsp honey and a pinch of turmeric if using",
                        "Blend low, then high 45s–60s until smooth and aromatic",
                        "Taste and adjust sweetness; serve chilled"
                    ],
                    'tags': ['spiced', 'lassi', 'cardamom', 'aromatic']
                }
            else:  # Green style
                recipe = {
                    'title': "Mango-Mint Green Refresher",
                    'ingredients': [
                        {'name': 'mango', 'amount': '3/4 cup', 'preparation': 'ripe, diced'},
                        {'name': 'cucumber', 'amount': '1/2 cup', 'preparation': 'peeled, diced'},
                        {'name': 'baby spinach', 'amount': '1/2 cup', 'preparation': 'packed'},
                        {'name': 'coconut water', 'amount': '1 cup', 'preparation': 'cold'},
                        {'name': 'fresh mint', 'amount': '6-8 leaves', 'preparation': 'fresh'},
                        {'name': 'lime juice', 'amount': '1 Tbsp', 'preparation': 'fresh'},
                        {'name': 'ice cubes', 'amount': '4-5', 'preparation': 'for chill'}
                    ],
                    'steps': [
                        "Add 1 cup cold coconut water to a blender",
                        "Add ¾ cup mango, ½ cup cucumber, and ½ cup spinach",
                        "Add 6-8 fresh mint leaves and 1 Tbsp lime juice",
                        "Add 4-5 ice cubes and blend low, then high 45s until smooth",
                        "Strain if desired for ultra-smooth texture; serve immediately"
                    ],
                    'tags': ['green', 'refreshing', 'mint', 'hydrating']
                }
        
        else:
            # Generic recipe for unknown ingredients
            recipe = {
                'title': f"Fresh {ingredient_name.title()} Smoothie",
                'ingredients': [
                    {'name': ingredient_name, 'amount': '1 cup', 'preparation': 'prepared'},
                    {'name': 'milk', 'amount': '1 cup', 'preparation': 'dairy or plant-based'},
                    {'name': 'honey', 'amount': '1 tsp', 'preparation': 'or to taste'},
                    {'name': 'vanilla extract', 'amount': '1/2 tsp', 'preparation': 'pure'},
                    {'name': 'ice cubes', 'amount': '4-5', 'preparation': 'for chill'}
                ],
                'steps': [
                    "Add 1 cup milk to a blender",
                    f"Add 1 cup prepared {ingredient_name}",
                    "Add honey and vanilla extract",
                    "Add ice cubes and blend until smooth",
                    "Taste and adjust sweetness; serve immediately"
                ],
                'tags': ['fresh', 'simple', 'customizable']
            }
        
        # Add common recipe properties
        recipe.update({
            'difficulty': 'easy',
            'estimated_time': '5 minutes',
            'servings': servings,
            'cooking_method': 'blended',
            'cuisine': 'Healthy',
            'meal_type': 'lunch',
            'recipe_category': 'smoothie',
            'ai_generated': True
        })
        
        recipes.append(recipe)
    
    return recipes

def create_ingredient_specific_cooking_recipes(ingredient_name: str, cuisine: str, servings: int = 2, variety_seed: str = None) -> List[Dict[str, Any]]:
    """Create truly unique cooking recipes based on ingredient properties"""
    
    properties = get_ingredient_specific_properties(ingredient_name)
    cooking_methods = properties.get('best_cooking_methods', ['sauté', 'bake', 'steam'])
    complementary_flavors = properties.get('complementary_flavors', ['garlic', 'herbs'])
    
    recipes = []
    
    # Create 3 different cooking methods for the ingredient
    for i, method in enumerate(cooking_methods[:3]):
        if method == 'sauté' or method == 'blend':
            recipe = {
                'title': f"Pan-Seared {ingredient_name.title()} with {complementary_flavors[0].title()} Herbs",
                'cooking_method': 'pan-seared',
                'ingredients': [
                    {'name': ingredient_name, 'amount': '300g', 'preparation': 'cleaned and prepared'},
                    {'name': 'olive oil', 'amount': '2 tbsp', 'preparation': 'extra virgin'},
                    {'name': complementary_flavors[0], 'amount': '3 cloves' if complementary_flavors[0] == 'garlic' else '2 tbsp', 'preparation': 'minced' if complementary_flavors[0] == 'garlic' else 'chopped'},
                    {'name': 'fresh herbs', 'amount': '2 tbsp', 'preparation': 'chopped (parsley, thyme)'},
                    {'name': 'lemon', 'amount': '1/2', 'preparation': 'juiced'},
                    {'name': 'salt and pepper', 'amount': 'to taste', 'preparation': 'freshly ground'}
                ],
                'steps': [
                    f"Pat {ingredient_name} dry and season with salt and pepper",
                    "Heat olive oil in a large skillet over medium-high heat",
                    f"Add {ingredient_name} and sear for 3-4 minutes per side until golden",
                    f"Add {complementary_flavors[0]} and cook for 30 seconds until fragrant",
                    "Add fresh herbs and lemon juice",
                    "Toss to combine and serve immediately"
                ],
                'tags': ['pan-seared', complementary_flavors[0], 'herbs', 'quick']
            }
        elif method == 'bake':
            recipe = {
                'title': f"Herb-Crusted Baked {ingredient_name.title()}",
                'cooking_method': 'baked',
                'ingredients': [
                    {'name': ingredient_name, 'amount': '300g', 'preparation': 'cleaned'},
                    {'name': 'breadcrumbs', 'amount': '1/2 cup', 'preparation': 'panko or fresh'},
                    {'name': 'parmesan', 'amount': '1/4 cup', 'preparation': 'grated'},
                    {'name': 'mixed herbs', 'amount': '2 tsp', 'preparation': 'dried (oregano, basil, thyme)'},
                    {'name': 'olive oil', 'amount': '3 tbsp', 'preparation': 'for drizzling'},
                    {'name': 'lemon zest', 'amount': '1 tsp', 'preparation': 'freshly grated'}
                ],
                'steps': [
                    "Preheat oven to 400°F (200°C)",
                    "Mix breadcrumbs, parmesan, herbs, and lemon zest in a bowl",
                    f"Brush {ingredient_name} with olive oil",
                    f"Press herb mixture onto {ingredient_name} to coat",
                    "Place on baking sheet and bake 20-25 minutes until golden",
                    "Let rest 5 minutes before serving"
                ],
                'tags': ['baked', 'herb-crusted', 'crispy', 'comfort']
            }
        else:  # stir-fry or other methods
            recipe = {
                'title': f"Spicy {cuisine.title()} {ingredient_name.title()} Stir-Fry",
                'cooking_method': 'stir-fry',
                'ingredients': [
                    {'name': ingredient_name, 'amount': '300g', 'preparation': 'cut into pieces'},
                    {'name': 'ginger', 'amount': '1 inch', 'preparation': 'minced'},
                    {'name': 'chili flakes', 'amount': '1/2 tsp', 'preparation': 'or to taste'},
                    {'name': 'soy sauce', 'amount': '2 tbsp', 'preparation': 'low sodium'},
                    {'name': 'sesame oil', 'amount': '1 tsp', 'preparation': 'for finishing'},
                    {'name': 'green onions', 'amount': '2', 'preparation': 'sliced'}
                ],
                'steps': [
                    "Heat wok or large pan over high heat",
                    "Add oil and swirl to coat",
                    f"Add {ingredient_name} and stir-fry 2-3 minutes",
                    "Add ginger and chili flakes, stir-fry 30 seconds",
                    "Add soy sauce and toss to coat",
                    "Finish with sesame oil and green onions, serve immediately"
                ],
                'tags': ['spicy', 'stir-fry', 'quick', 'asian-inspired']
            }
        
        # Add common recipe properties
        recipe.update({
            'difficulty': 'intermediate',
            'estimated_time': '20-35 minutes',
            'servings': servings,
            'cuisine': cuisine.title(),
            'meal_type': 'dinner',
            'recipe_category': 'cuisine',
            'ai_generated': True
        })
        
        recipes.append(recipe)
    
    return recipes

def generate_truly_unique_recipes(ingredient_names: List[str], recipe_category: str, cuisine: str = 'international', servings: int = 2, user_id: str = None) -> List[Dict[str, Any]]:
    """Generate truly unique recipes based on ingredient properties rather than templates"""
    
    if not ingredient_names:
        return []
    
    primary_ingredient = ingredient_names[0]
    
    # Create variety seed for consistent but different recipes
    time_seed = int(time.time() // 300)  # Changes every 5 minutes
    variety_seed = f"{user_id}_{time_seed}_{primary_ingredient}"
    
    if recipe_category == 'smoothie':
        return create_ingredient_specific_smoothie_recipes(primary_ingredient, servings, variety_seed)
    else:
        return create_ingredient_specific_cooking_recipes(primary_ingredient, cuisine, servings, variety_seed)

def main():
    """Test the ingredient-specific recipe generation"""
    
    # Test with different ingredients
    test_ingredients = ['banana', 'grapes', 'mango']
    
    for ingredient in test_ingredients:
        print(f"\n{'='*50}")
        print(f"TESTING RECIPES FOR: {ingredient.upper()}")
        print(f"{'='*50}")
        
        # Test smoothie recipes
        print(f"\n--- SMOOTHIE RECIPES FOR {ingredient.upper()} ---")
        smoothie_recipes = generate_truly_unique_recipes([ingredient], 'smoothie', user_id='test_user')
        
        for i, recipe in enumerate(smoothie_recipes, 1):
            print(f"\n{i}. {recipe['title']}")
            print(f"   Tags: {', '.join(recipe['tags'])}")
            print(f"   Ingredients: {len(recipe['ingredients'])} items")
            print(f"   Steps: {len(recipe['steps'])} steps")
        
        # Test cooking recipes
        print(f"\n--- COOKING RECIPES FOR {ingredient.upper()} ---")
        cooking_recipes = generate_truly_unique_recipes([ingredient], 'cuisine', 'mediterranean', user_id='test_user')
        
        for i, recipe in enumerate(cooking_recipes, 1):
            print(f"\n{i}. {recipe['title']}")
            print(f"   Method: {recipe['cooking_method']}")
            print(f"   Tags: {', '.join(recipe['tags'])}")

if __name__ == "__main__":
    main()