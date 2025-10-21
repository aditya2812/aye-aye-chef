import json
import logging
from typing import List, Dict, Any

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    """
    Agent tool: Analyze ingredients for recipe generation
    """
    try:
        # Parse input from Bedrock Agent
        input_data = json.loads(event.get('inputText', '{}'))
        
        ingredients = input_data.get('ingredients', [])
        nutrition_data = input_data.get('nutrition', {})
        
        logger.info(f"Analyzing {len(ingredients)} ingredients")
        
        # Analyze ingredient categories
        categories = {
            'proteins': [],
            'vegetables': [],
            'fruits': [],
            'grains': [],
            'dairy': [],
            'herbs_spices': []
        }
        
        # Ingredient categorization
        ingredient_categories = {
            # Proteins
            'chicken': 'proteins', 'beef': 'proteins', 'pork': 'proteins', 
            'fish': 'proteins', 'salmon': 'proteins', 'tuna': 'proteins',
            'egg': 'proteins', 'tofu': 'proteins', 'beans': 'proteins',
            
            # Vegetables
            'onion': 'vegetables', 'garlic': 'vegetables', 'tomato': 'vegetables',
            'carrot': 'vegetables', 'potato': 'vegetables', 'broccoli': 'vegetables',
            'spinach': 'vegetables', 'lettuce': 'vegetables', 'cucumber': 'vegetables',
            'bell pepper': 'vegetables', 'mushroom': 'vegetables',
            
            # Fruits
            'apple': 'fruits', 'banana': 'fruits', 'orange': 'fruits',
            'strawberry': 'fruits', 'blueberry': 'fruits', 'lemon': 'fruits',
            'avocado': 'fruits', 'mango': 'fruits',
            
            # Grains
            'rice': 'grains', 'bread': 'grains', 'pasta': 'grains',
            'quinoa': 'grains', 'oats': 'grains',
            
            # Dairy
            'milk': 'dairy', 'cheese': 'dairy', 'butter': 'dairy',
            'yogurt': 'dairy', 'cream': 'dairy',
            
            # Herbs & Spices
            'basil': 'herbs_spices', 'cilantro': 'herbs_spices', 'parsley': 'herbs_spices'
        }
        
        # Categorize ingredients
        for ingredient in ingredients:
            name = ingredient.get('name', '').lower()
            category = ingredient_categories.get(name, 'vegetables')  # Default to vegetables
            categories[category].append(ingredient)
        
        # Determine cooking compatibility
        cooking_methods = []
        
        # Fresh/Raw suitable for fruits and some vegetables
        if categories['fruits'] or any(veg['name'].lower() in ['lettuce', 'cucumber', 'tomato'] 
                                      for veg in categories['vegetables']):
            cooking_methods.append({
                'method': 'fresh',
                'reason': 'Fresh fruits and vegetables are excellent raw',
                'time': '5-10 minutes'
            })
        
        # Sautéing good for most vegetables and proteins
        if categories['vegetables'] or categories['proteins']:
            cooking_methods.append({
                'method': 'sautéed',
                'reason': 'Vegetables and proteins cook well with quick sautéing',
                'time': '10-15 minutes'
            })
        
        # Blending perfect for fruits
        if categories['fruits']:
            cooking_methods.append({
                'method': 'blended',
                'reason': 'Fruits blend beautifully for smoothies and drinks',
                'time': '5 minutes'
            })
        
        # Baking suitable for most ingredients
        if len(ingredients) > 1:
            cooking_methods.append({
                'method': 'baked',
                'reason': 'Multiple ingredients can be roasted together',
                'time': '25-35 minutes'
            })
        
        # Determine flavor profiles
        flavor_profiles = []
        if categories['fruits']:
            flavor_profiles.extend(['sweet', 'fresh', 'light'])
        if categories['herbs_spices']:
            flavor_profiles.extend(['aromatic', 'flavorful'])
        if categories['proteins']:
            flavor_profiles.extend(['savory', 'hearty'])
        
        # Cuisine suggestions based on ingredients
        cuisine_suggestions = []
        if any(ing['name'].lower() in ['tomato', 'basil', 'garlic'] for ing in ingredients):
            cuisine_suggestions.append('Italian')
        if any(ing['name'].lower() in ['cilantro', 'lime', 'avocado'] for ing in ingredients):
            cuisine_suggestions.append('Mexican')
        if any(ing['name'].lower() in ['ginger', 'soy', 'rice'] for ing in ingredients):
            cuisine_suggestions.append('Asian')
        
        # Nutritional insights
        per_serving = nutrition_data.get('per_serving', {})
        nutritional_highlights = []
        
        if per_serving.get('protein_g', 0) > 15:
            nutritional_highlights.append('High protein content')
        if per_serving.get('fiber_g', 0) > 5:
            nutritional_highlights.append('High fiber content')
        if per_serving.get('vit_c_mg', 0) > 20:
            nutritional_highlights.append('Rich in Vitamin C')
        if per_serving.get('kcal', 0) < 200:
            nutritional_highlights.append('Low calorie option')
        
        analysis = {
            'ingredient_categories': categories,
            'recommended_cooking_methods': cooking_methods,
            'flavor_profiles': flavor_profiles,
            'cuisine_suggestions': cuisine_suggestions,
            'nutritional_highlights': nutritional_highlights,
            'total_ingredients': len(ingredients),
            'primary_category': max(categories.keys(), key=lambda k: len(categories[k])) if ingredients else 'mixed'
        }
        
        logger.info(f"Analysis complete: {analysis['primary_category']} dish with {len(cooking_methods)} cooking methods")
        
        return {
            'statusCode': 200,
            'body': json.dumps(analysis)
        }
        
    except Exception as e:
        logger.error(f"Error analyzing ingredients: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Failed to analyze ingredients',
                'details': str(e)
            })
        }