import json
import boto3
import os
import uuid
import logging
import requests
import time
from datetime import datetime, timezone
from typing import List, Dict, Any

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize clients
cloudwatch = boto3.client('cloudwatch')
rds_client = boto3.client('rds-data')
secrets_client = boto3.client('secretsmanager')
bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-west-2')

def get_usda_api_key():
    """Get USDA API key from Secrets Manager"""
    try:
        secret_name = os.environ.get('USDA_SECRET_NAME', 'aye-aye/usda-api-key')
        response = secrets_client.get_secret_value(SecretId=secret_name)
        secret_data = json.loads(response['SecretString'])
        return secret_data.get('api_key')
    except Exception as e:
        logger.warning(f"Could not get USDA API key: {e}")
        return None

def fetch_usda_nutrients(fdc_ids: List[str], api_key: str) -> Dict[str, Any]:
    """Fetch nutrition facts from USDA FDC API"""
    if not api_key:
        logger.warning("No USDA API key available")
        return {}
    
    url = "https://api.nal.usda.gov/fdc/v1/foods"
    
    try:
        # Convert fdc_ids to integers for the API
        fdc_ids_int = []
        for fdc_id in fdc_ids:
            try:
                fdc_ids_int.append(int(fdc_id))
            except ValueError:
                logger.warning(f"Invalid FDC ID: {fdc_id}")
                continue
        
        if not fdc_ids_int:
            return {}   
     
        # API key goes in query parameters, data goes in JSON body
        query_params = {'api_key': api_key}
        json_data = {'fdcIds': fdc_ids_int}
        
        logger.info(f"Fetching nutrition data for FDC IDs: {fdc_ids_int}")
        response = requests.post(url, params=query_params, json=json_data, timeout=10)
        response.raise_for_status()
        
        foods = response.json()
        
        # Normalize nutrition data to per-100g format
        nutrition_facts = {}
        
        for food in foods:
            fdc_id = str(food.get('fdcId', ''))
            nutrients = food.get('foodNutrients', [])
            
            per_100g = {}
            
            # Map common nutrients
            nutrient_mapping = {
                1008: 'kcal',           # Energy
                1003: 'protein_g',      # Protein
                1004: 'fat_g',          # Total lipid (fat)
                1005: 'carb_g',         # Carbohydrate, by difference
                1079: 'fiber_g',        # Fiber, total dietary
                1063: 'sugar_g',        # Sugars, total
                1093: 'sodium_mg',      # Sodium
                1087: 'calcium_mg',     # Calcium
                1089: 'iron_mg',        # Iron
                1162: 'vit_c_mg',       # Vitamin C
            }
            
            for nutrient in nutrients:
                nutrient_id = nutrient.get('nutrient', {}).get('id')
                amount = nutrient.get('amount', 0)
                
                if nutrient_id in nutrient_mapping:
                    per_100g[nutrient_mapping[nutrient_id]] = float(amount)
            
            nutrition_facts[fdc_id] = {'per_100g': per_100g}
        
        logger.info(f"Successfully fetched nutrition data for {len(nutrition_facts)} foods")
        return nutrition_facts
        
    except Exception as e:
        logger.error(f"Error fetching USDA nutrition data: {e}")
        return {}

def compute_nutrition(items: List[Dict], nutrition_facts: Dict, servings: int = 2) -> Dict[str, Any]:
    """Compute total nutrition from ingredients"""
    totals = {
        'kcal': 0, 'protein_g': 0, 'fat_g': 0, 'carb_g': 0,
        'fiber_g': 0, 'sugar_g': 0, 'sodium_mg': 0, 'calcium_mg': 0,
        'iron_mg': 0, 'vit_c_mg': 0
    }
    
    # If no nutrition facts available, provide estimated values
    if not nutrition_facts:
        logger.info("No nutrition data available, using estimated values")
        for item in items:
            label = item.get('label', '').lower()
            grams = float(item.get('grams', 100))
            
            # Basic nutrition estimates per 100g
            if 'paneer' in label:
                totals['kcal'] += (265 * grams) / 100
                totals['protein_g'] += (18 * grams) / 100
                totals['fat_g'] += (20 * grams) / 100
                totals['carb_g'] += (1.2 * grams) / 100
            elif 'spinach' in label:
                totals['kcal'] += (23 * grams) / 100
                totals['protein_g'] += (2.9 * grams) / 100
                totals['fat_g'] += (0.4 * grams) / 100
                totals['carb_g'] += (3.6 * grams) / 100
            else:
                # Generic vegetable estimate
                totals['kcal'] += (25 * grams) / 100
                totals['protein_g'] += (2 * grams) / 100
                totals['fat_g'] += (0.3 * grams) / 100
                totals['carb_g'] += (5 * grams) / 100
    
    for item in items:
        fdc_id = item.get('fdc_id', '')
        grams = float(item.get('grams', 0))
        
        if fdc_id in nutrition_facts:
            per_100g = nutrition_facts[fdc_id].get('per_100g', {})
            
            # Calculate actual amounts based on grams
            for nutrient, per_100g_value in per_100g.items():
                if nutrient in totals:
                    totals[nutrient] += (per_100g_value * grams) / 100.0
    
    # Round values and calculate per serving
    for key in totals:
        totals[key] = round(totals[key], 1)
    
    per_serving = {}
    for key, value in totals.items():
        per_serving[key] = round(value / servings, 1)
    
    return {
        'totals_per_recipe': totals,
        'per_serving': per_serving
    }

def generate_ai_recipes_with_claude(items: List[Dict], nutrition: Dict, servings: int, 
                                  cuisine: str, skill_level: str, dietary_restrictions: List[str],
                                  meal_type: str, recipe_category: str, user_id: str) -> List[Dict]:
    """Generate AI recipes using Claude - based on your working test"""
    
    logger.info(f"🤖 AI RECIPE GENERATION WITH CLAUDE STARTED")
    logger.info(f"  User ID: {user_id}")
    logger.info(f"  Ingredients: {len(items)} - {[item.get('name', 'unknown') for item in items]}")
    logger.info(f"  Cuisine: {cuisine}")
    logger.info(f"  Skill Level: {skill_level}")
    logger.info(f"  Meal Type: {meal_type}")
    logger.info(f"  Recipe Category: {recipe_category}")
    logger.info(f"  Servings: {servings}")
    
    try:
        # Prepare ingredients data
        ingredient_names = [item.get('name', item.get('label', 'Unknown ingredient')) for item in items]
        
        # Handle different recipe categories
        if recipe_category == 'smoothie':
            return generate_smoothie_with_claude(ingredient_names, servings, dietary_restrictions)
        elif recipe_category == 'dessert':
            return generate_dessert_with_claude(ingredient_names, servings, dietary_restrictions)
        else:
            return generate_cooking_recipes_with_claude(ingredient_names, servings, cuisine, skill_level, dietary_restrictions, meal_type, nutrition)
            
    except Exception as e:
        logger.error(f"❌ AI RECIPE GENERATION FAILED!")
        logger.error(f"  Error Type: {type(e).__name__}")
        logger.error(f"  Error Message: {str(e)}")
        
        # Return fallback recipe
        return create_fallback_recipes(ingredient_names if 'ingredient_names' in locals() else ['ingredient'], servings)

def generate_cooking_recipes_with_claude(ingredient_names: List[str], servings: int, cuisine: str, 
                                       skill_level: str, dietary_restrictions: List[str], 
                                       meal_type: str, nutrition: Dict) -> List[Dict]:
    """Generate cooking recipes using Claude AI"""
    
    logger.info(f"🍳 Generating cooking recipes with Claude for: {', '.join(ingredient_names)}")
    
    # System prompt for cooking recipes
    system_prompt = f"""You are an expert chef specializing in {cuisine} cuisine. Create authentic, delicious recipes using the provided ingredients as the main focus. 

Requirements:
- Generate exactly 3 distinct recipes using the same main ingredients
- Each recipe should be authentically {cuisine} with proper dish names (not generic "Style" names)
- Use traditional {cuisine} cooking techniques, spices, and flavor profiles
- Skill level: {skill_level}
- Meal type: {meal_type}
- Servings: {servings}
- Include only realistic ingredients that complement the main ones
- Each recipe should have a different cooking method or dish type

Return ONLY valid JSON in this exact format:
{{
  "recipes": [
    {{
      "recipe_name": "Authentic Dish Name (not generic)",
      "cuisine_type": "{cuisine}",
      "dish_type": "specific dish category",
      "preparation_time": "X minutes",
      "cooking_time": "X minutes", 
      "serving_size": "{servings} servings",
      "ingredients": [
        {{"name": "ingredient", "quantity": "amount", "notes": "preparation"}}
      ],
      "instructions": [
        "Step 1: Detailed instruction",
        "Step 2: Next step"
      ],
      "cooking_method": "sauté/grill/simmer/etc",
      "chefs_tip": "Professional tip",
      "difficulty": "{skill_level}"
    }}
  ]
}}"""

    # User prompt
    user_prompt = f"""Create 3 authentic {cuisine} recipes using these main ingredients: {', '.join(ingredient_names)}

Requirements:
- Each recipe must have a proper {cuisine} dish name (like "Butter Chicken" not "Indian Style Chicken")
- Use authentic {cuisine} spices, techniques, and cooking methods
- Make each recipe distinctly different (different dish types/cooking methods)
- Suitable for {meal_type}
- {skill_level} difficulty level"""

    # Add dietary restrictions if any
    if dietary_restrictions:
        user_prompt += f"\n- Accommodate these dietary restrictions: {', '.join(dietary_restrictions)}"

    try:
        logger.info("🤖 Calling Claude AI for cooking recipes...")
        
        # Call Claude API (based on your working test)
        response = bedrock_runtime.invoke_model(
            modelId='anthropic.claude-3-haiku-20240307-v1:0',
            body=json.dumps({
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 4000,
                'system': system_prompt,
                'messages': [
                    {
                        'role': 'user',
                        'content': user_prompt
                    }
                ]
            })
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        response_text = response_body['content'][0]['text']
        
        logger.info(f"✅ Claude AI response received: {len(response_text)} characters")
        
        # Parse JSON response
        try:
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_text = json_match.group()
                ai_response = json.loads(json_text)
                
                if 'recipes' in ai_response:
                    recipes = ai_response['recipes']
                    logger.info(f"✅ Successfully parsed {len(recipes)} recipes from Claude")
                    
                    # Convert to standard format
                    formatted_recipes = []
                    for i, recipe in enumerate(recipes):
                        recipe_id = f"ai_recipe_{uuid.uuid4().hex[:8]}"
                        
                        formatted_recipe = {
                            'id': recipe_id,
                            'title': recipe.get('recipe_name', f'AI Recipe {i+1}'),
                            'servings': servings,
                            'estimated_time': f"{recipe.get('preparation_time', '10 min')} + {recipe.get('cooking_time', '20 min')}",
                            'difficulty': recipe.get('difficulty', skill_level),
                            'cuisine': recipe.get('cuisine_type', cuisine),
                            'meal_type': meal_type,
                            'cooking_method': recipe.get('cooking_method', recipe.get('dish_type', 'mixed')),
                            'recipe_category': 'cuisine',
                            'ingredients': recipe.get('ingredients', []),
                            'steps': recipe.get('instructions', []),
                            'tags': [cuisine.lower(), recipe.get('dish_type', '').lower(), skill_level],
                            'description': recipe.get('chefs_tip', f"Authentic {cuisine} dish"),
                            'ai_generated': True
                        }
                        
                        # Add nutrition if available
                        if nutrition:
                            formatted_recipe['nutrition'] = nutrition
                        
                        formatted_recipes.append(formatted_recipe)
                        
                        # Log each recipe
                        logger.info(f"✅ AI Recipe {i+1}: {formatted_recipe['title']}")
                        logger.info(f"   Method: {formatted_recipe['cooking_method']}")
                        logger.info(f"   Ingredients: {len(formatted_recipe['ingredients'])}")
                        logger.info(f"   Steps: {len(formatted_recipe['steps'])}")
                    
                    logger.info(f"🎉 Claude AI generated {len(formatted_recipes)} authentic {cuisine} recipes!")
                    return formatted_recipes[:3]  # Ensure exactly 3 recipes
                    
        except Exception as parse_error:
            logger.error(f"❌ Failed to parse Claude response: {parse_error}")
            logger.error(f"Raw response: {response_text[:500]}...")
            
    except Exception as api_error:
        logger.error(f"❌ Claude API call failed: {api_error}")
    
    # Fallback if Claude fails
    logger.info("🔄 Claude failed, creating fallback recipes")
    return create_fallback_recipes(ingredient_names, servings)

def generate_smoothie_with_claude(ingredient_names: List[str], servings: int, dietary_restrictions: List[str]) -> List[Dict]:
    """Generate smoothie recipes using Claude AI"""
    
    logger.info(f"🥤 Generating smoothie recipes with Claude for: {', '.join(ingredient_names)}")
    
    # System prompt for smoothies
    system_prompt = """You are a nutrition expert and smoothie specialist. Create healthy, delicious smoothie recipes using the provided ingredients as the main focus.

Requirements:
- Generate exactly 3 distinct smoothie recipes
- Each smoothie should have different flavor profiles and nutritional benefits
- Use only blending - NO COOKING OR HEATING
- Include appropriate liquid bases, natural sweeteners, and nutritional boosters
- Focus on taste, nutrition, and texture variety

Return ONLY valid JSON in this exact format:
{
  "recipes": [
    {
      "recipe_name": "Creative Smoothie Name",
      "cuisine_type": "Healthy",
      "dish_type": "smoothie",
      "preparation_time": "5 minutes",
      "cooking_time": "0 minutes", 
      "serving_size": "X servings",
      "ingredients": [
        {"name": "ingredient", "quantity": "amount", "notes": "preparation"}
      ],
      "instructions": [
        "Step 1: Add liquid to blender first",
        "Step 2: Add fruits/ingredients"
      ],
      "cooking_method": "blended",
      "chefs_tip": "Smoothie tip",
      "difficulty": "easy"
    }
  ]
}"""

    # User prompt for smoothies
    user_prompt = f"""Create 3 unique smoothie recipes using these main ingredients: {', '.join(ingredient_names)}

Requirements:
- Each smoothie should have a different style (e.g., green smoothie, protein smoothie, dessert smoothie)
- Use appropriate liquid bases (milk, coconut water, juice, etc.)
- Include natural sweeteners if needed (honey, dates, banana)
- Add nutritional boosters (chia seeds, protein powder, spinach, etc.)
- NO COOKING - only blending
- Make each smoothie nutritionally balanced and delicious"""

    if dietary_restrictions:
        user_prompt += f"\n- Accommodate: {', '.join(dietary_restrictions)}"

    try:
        logger.info("🤖 Calling Claude AI for smoothie recipes...")
        
        response = bedrock_runtime.invoke_model(
            modelId='anthropic.claude-3-haiku-20240307-v1:0',
            body=json.dumps({
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 3000,
                'system': system_prompt,
                'messages': [{'role': 'user', 'content': user_prompt}]
            })
        )
        
        response_body = json.loads(response['body'].read())
        response_text = response_body['content'][0]['text']
        
        logger.info(f"✅ Claude smoothie response received: {len(response_text)} characters")
        
        # Parse and format smoothie recipes
        import re
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            ai_response = json.loads(json_match.group())
            
            if 'recipes' in ai_response:
                recipes = ai_response['recipes']
                formatted_recipes = []
                
                for i, recipe in enumerate(recipes):
                    recipe_id = f"smoothie_{uuid.uuid4().hex[:8]}"
                    
                    formatted_recipe = {
                        'id': recipe_id,
                        'title': recipe.get('recipe_name', f'Smoothie {i+1}'),
                        'servings': servings,
                        'estimated_time': '5 minutes',
                        'difficulty': 'easy',
                        'cuisine': 'Healthy',
                        'meal_type': 'breakfast',
                        'cooking_method': 'blended',
                        'recipe_category': 'smoothie',
                        'ingredients': recipe.get('ingredients', []),
                        'steps': recipe.get('instructions', []),
                        'tags': ['smoothie', 'healthy', 'quick', 'no-cook'],
                        'description': recipe.get('chefs_tip', 'Nutritious and delicious smoothie'),
                        'ai_generated': True
                    }
                    formatted_recipes.append(formatted_recipe)
                    
                    logger.info(f"✅ AI Smoothie {i+1}: {formatted_recipe['title']}")
                
                logger.info(f"🎉 Claude AI generated {len(formatted_recipes)} smoothie recipes!")
                return formatted_recipes[:3]
                
    except Exception as e:
        logger.error(f"❌ Claude smoothie generation failed: {e}")
    
    # Fallback smoothie
    return create_fallback_smoothies(ingredient_names, servings)

def generate_dessert_with_claude(ingredient_names: List[str], servings: int, dietary_restrictions: List[str]) -> List[Dict]:
    """Generate dessert recipes using Claude AI"""
    
    logger.info(f"🍰 Generating dessert recipes with Claude for: {', '.join(ingredient_names)}")
    
    # Simple dessert fallback for now
    return create_fallback_desserts(ingredient_names, servings)

def create_fallback_recipes(ingredient_names: List[str], servings: int) -> List[Dict]:
    """Create fallback recipes when AI fails"""
    
    primary_ingredient = ingredient_names[0] if ingredient_names else "ingredient"
    
    return [
        {
            'id': f"fallback_{uuid.uuid4().hex[:8]}",
            'title': f'Simple Sautéed {primary_ingredient.title()}',
            'servings': servings,
            'estimated_time': '20 minutes',
            'difficulty': 'easy',
            'cuisine': 'Home Cooking',
            'cooking_method': 'sauté',
            'recipe_category': 'cuisine',
            'tags': ['simple', 'quick', 'fallback'],
            'ingredients': [
                {'name': ing, 'quantity': '100g', 'notes': 'prepared as needed'} 
                for ing in ingredient_names[:3]
            ],
            'steps': [
                f'Prepare {", ".join(ingredient_names[:3])} by washing and cutting as needed',
                'Heat 2 tablespoons oil in a large pan over medium heat',
                f'Add {primary_ingredient} and cook for 5-7 minutes',
                'Season with salt and pepper to taste',
                'Serve hot and enjoy'
            ],
            'description': 'Simple and delicious preparation',
            'ai_generated': False
        }
    ]

def create_fallback_smoothies(ingredient_names: List[str], servings: int) -> List[Dict]:
    """Create fallback smoothie recipes"""
    
    primary_ingredient = ingredient_names[0] if ingredient_names else "fruit"
    
    return [
        {
            'id': f"smoothie_fallback_{uuid.uuid4().hex[:8]}",
            'title': f'Fresh {primary_ingredient.title()} Smoothie',
            'servings': servings,
            'estimated_time': '5 minutes',
            'difficulty': 'easy',
            'cuisine': 'Healthy',
            'meal_type': 'breakfast',
            'cooking_method': 'blended',
            'recipe_category': 'smoothie',
            'ingredients': [
                {'name': primary_ingredient, 'quantity': '1 cup', 'notes': 'fresh or frozen'},
                {'name': 'milk', 'quantity': '1 cup', 'notes': 'cold'},
                {'name': 'honey', 'quantity': '1 tsp', 'notes': 'optional'},
                {'name': 'ice cubes', 'quantity': '4-6', 'notes': 'for thickness'}
            ],
            'steps': [
                'Add cold milk to blender',
                f'Add {primary_ingredient} and honey',
                'Add ice cubes',
                'Blend until smooth',
                'Serve immediately'
            ],
            'tags': ['smoothie', 'simple', 'healthy'],
            'description': f'A refreshing {primary_ingredient} smoothie',
            'ai_generated': False
        }
    ]

def create_fallback_desserts(ingredient_names: List[str], servings: int) -> List[Dict]:
    """Create fallback dessert recipes"""
    
    primary_ingredient = ingredient_names[0] if ingredient_names else "fruit"
    
    return [
        {
            'id': f"dessert_fallback_{uuid.uuid4().hex[:8]}",
            'title': f'Simple {primary_ingredient.title()} Parfait',
            'servings': servings,
            'estimated_time': '15 minutes',
            'difficulty': 'easy',
            'cuisine': 'Dessert',
            'meal_type': 'dessert',
            'cooking_method': 'no-bake',
            'recipe_category': 'dessert',
            'ingredients': [
                {'name': primary_ingredient, 'quantity': '2 cups', 'notes': 'prepared'},
                {'name': 'Greek yogurt', 'quantity': '1 cup', 'notes': 'vanilla'},
                {'name': 'honey', 'quantity': '2 tbsp', 'notes': 'for sweetening'},
                {'name': 'granola', 'quantity': '1/2 cup', 'notes': 'for crunch'}
            ],
            'steps': [
                f'Prepare {primary_ingredient} as needed',
                'Mix Greek yogurt with honey',
                f'Layer {primary_ingredient}, yogurt mixture, and granola in glasses',
                'Repeat layers ending with granola on top',
                'Chill 15 minutes before serving'
            ],
            'tags': ['dessert', 'no-bake', 'healthy'],
            'description': f'A simple and delicious {primary_ingredient} parfait',
            'ai_generated': False
        }
    ]

def send_metrics(metric_name: str, value: float, unit: str = 'Count'):
    """Send metrics to CloudWatch"""
    try:
        cloudwatch.put_metric_data(
            Namespace='AyeAye/Lambda',
            MetricData=[{
                'MetricName': metric_name,
                'Value': value,
                'Unit': unit,
                'Timestamp': datetime.now(timezone.utc)
            }]
        )
    except Exception as e:
        logger.warning(f"Failed to send metric {metric_name}: {e}")

def handler(event, context):
    """AI-powered Lambda handler using Claude"""
    
    # Handle CORS preflight
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': ''
        }
    
    # Handle GET as health check
    if event.get('httpMethod') == 'GET':
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': True,
                'message': 'AI-powered Lambda function is healthy',
                'timestamp': time.time(),
                'ai_enabled': True
            })
        }
    
    start_time = time.time()
    request_id = f"ai_req_{uuid.uuid4().hex[:8]}"
    
    try:
        logger.info(f"🚀 Processing AI request {request_id}")
        
        # Parse request body
        try:
            body = json.loads(event.get('body', '{}'))
        except json.JSONDecodeError:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'success': False, 'error': 'Invalid JSON'})
            }
        
        # Extract parameters
        scan_id = body.get('scan_id')
        servings = body.get('servings', 2)
        cuisine = body.get('cuisine', 'international')
        skill_level = body.get('skill_level', 'intermediate')
        dietary_restrictions = body.get('dietary_restrictions', [])
        meal_type = body.get('meal_type', 'lunch')
        recipe_category = body.get('recipe_category', 'cuisine')
        mock_ingredients = body.get('mock_ingredients')
        user_id = body.get('user_id', 'anonymous')
        
        # Test mode - return simple recipe
        if body.get('test_mode') or (not scan_id and not mock_ingredients):
            logger.info("🧪 AI Test mode - returning simple recipe")
            
            test_recipe = {
                'id': 'ai_test_recipe_1',
                'title': 'AI Test Recipe',
                'servings': servings,
                'estimated_time': '20 minutes',
                'difficulty': 'easy',
                'cuisine': 'Test',
                'ingredients': [
                    {'name': 'olive oil', 'quantity': '2 tbsp', 'notes': ''},
                    {'name': 'garlic', 'quantity': '2 cloves', 'notes': 'minced'},
                    {'name': 'vegetables', 'quantity': '2 cups', 'notes': 'chopped'}
                ],
                'steps': [
                    'Heat oil in pan',
                    'Add garlic, cook 1 minute',
                    'Add vegetables, cook until tender',
                    'Season and serve'
                ],
                'tags': ['test', 'simple', 'ai'],
                'ai_generated': True
            }
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({
                    'recipe_ids': ['ai_test_recipe_1'],
                    'recipes': [test_recipe],
                    'request_id': request_id,
                    'test_mode': True,
                    'ai_enabled': True
                })
            }
        
        # Get ingredients
        items = []
        if mock_ingredients:
            logger.info("Using mock ingredients for AI generation")
            items = mock_ingredients
        elif scan_id:
            logger.info(f"Fetching ingredients for scan_id: {scan_id}")
            try:
                db_secret_arn = os.environ['DB_SECRET_ARN']
                db_cluster_arn = os.environ['DB_CLUSTER_ARN']
                
                response = rds_client.execute_statement(
                    resourceArn=db_cluster_arn,
                    secretArn=db_secret_arn,
                    database='ayeaye',
                    sql="""
                        SELECT fdc_id, label, grams 
                        FROM scan_items 
                        WHERE scan_id::text = :scan_id AND confirmed = true
                        ORDER BY grams DESC
                    """,
                    parameters=[{'name': 'scan_id', 'value': {'stringValue': scan_id}}]
                )
                
                if response.get('records'):
                    for record in response['records']:
                        items.append({
                            'name': record[1].get('stringValue', 'unknown'),
                            'grams': record[2].get('doubleValue', 100.0),
                            'fdc_id': record[0].get('stringValue', '')
                        })
                    logger.info(f"Found {len(items)} ingredients")
                else:
                    logger.warning("No ingredients found")
                    
            except Exception as db_error:
                logger.error(f"Database error: {db_error}")
                items = []
        
        # Get nutrition data
        nutrition = {}
        if items:
            fdc_ids = [item.get('fdc_id', '') for item in items if item.get('fdc_id')]
            if fdc_ids:
                try:
                    api_key = get_usda_api_key()
                    nutrition_facts = fetch_usda_nutrients(fdc_ids, api_key)
                    nutrition = compute_nutrition(items, nutrition_facts, servings)
                except Exception as nutrition_error:
                    logger.warning(f"Nutrition fetch failed: {nutrition_error}")
        
        # Generate recipes with Claude AI
        logger.info(f"🤖 Calling Claude AI for recipe generation...")
        recipes = generate_ai_recipes_with_claude(
            items, nutrition, servings, cuisine, skill_level,
            dietary_restrictions, meal_type, recipe_category, user_id
        )
        
        # Send metrics
        processing_time = time.time() - start_time
        send_metrics('AIRequestDuration', processing_time, 'Seconds')
        send_metrics('AIRecipesGenerated', len(recipes))
        
        logger.info(f"✅ AI Request {request_id} completed in {processing_time:.2f}s")
        logger.info(f"🎉 Generated {len(recipes)} AI recipes with Claude!")
        
        # Return response
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'recipe_ids': [recipe['id'] for recipe in recipes],
                'recipes': recipes,
                'request_id': request_id,
                'processing_time': processing_time,
                'ai_enabled': True,
                'ai_model': 'claude-3-haiku'
            })
        }
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"❌ AI Request {request_id} failed: {str(e)}")
        
        send_metrics('AIRequestFailure', 1)
        
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'success': False,
                'error': str(e),
                'request_id': request_id,
                'processing_time': processing_time,
                'ai_enabled': True
            })
        }