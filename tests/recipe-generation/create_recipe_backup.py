import json
import boto3
import os
import uuid
import logging
import requests
from typing import List, Dict, Any

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

rds_client = boto3.client('rds-data')
secrets_client = boto3.client('secretsmanager')
bedrock_agent_client = boto3.client('bedrock-agent-runtime')
bedrock_agent_mgmt_client = boto3.client('bedrock-agent')

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
        query_params = {
            'api_key': api_key
        }
        
        json_data = {
            'fdcIds': fdc_ids_int
        }
        
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
        'kcal': 0,
        'protein_g': 0,
        'fat_g': 0,
        'carb_g': 0,
        'fiber_g': 0,
        'sugar_g': 0,
        'sodium_mg': 0,
        'calcium_mg': 0,
        'iron_mg': 0,
        'vit_c_mg': 0
    }
    
    # If no nutrition facts available, provide estimated values based on ingredients
    if not nutrition_facts:
        logger.info("No nutrition data available, using estimated values")
        # Provide basic estimated nutrition for common ingredients
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
    
    # Round values
    for key in totals:
        totals[key] = round(totals[key], 1)
    
    # Calculate per serving
    per_serving = {}
    for key, value in totals.items():
        per_serving[key] = round(value / servings, 1)
    
    return {
        'totals_per_recipe': totals,
        'per_serving': per_serving
    }

# Removed static recipe generation - now only using AI-generated recipes

def generate_ai_recipes(items: List[Dict], nutrition: Dict, servings: int = 2, user_id: str = None) -> List[Dict[str, Any]]:
    """Generate AI-powered recipe options using Bedrock Agent"""
    
    try:
        # Get Bedrock Agent ID from environment
        agent_id = os.environ.get('BEDROCK_AGENT_ID')
        if not agent_id:
            logger.warning("No Bedrock Agent ID configured, falling back to static recipes")
            return generate_basic_fallback_recipes(items, nutrition, servings)
        
        # Prepare ingredients data for AI
        ingredients_data = []
        for item in items:
            ingredients_data.append({
                'name': item.get('label', 'Unknown ingredient'),
                'grams': float(item.get('grams', 100)),
                'fdc_id': item.get('fdc_id', '')
            })
        
        # Create AI prompt with structured data
        ingredient_names = [item['name'] for item in ingredients_data]
        
        # Create a detailed, professional prompt for the Bedrock Agent
        primary_ingredient = ingredient_names[0] if ingredient_names else "ingredient"
        
        prompt = f"""Create exactly 3 professional, restaurant-quality recipes using ALL these ingredients: {", ".join(ingredient_names)}.

TITLE REQUIREMENTS:
- Create specific, appealing titles that combine CUISINE STYLE + MAIN INGREDIENTS + COOKING METHOD
- Examples: "Traditional Indian Palak Paneer with Fresh Spinach", "Mediterranean Herb-Crusted Chicken with Lemon", "Asian Ginger Soy Tofu Stir-Fry"
- NOT generic titles like "{primary_ingredient.title()} Recipe" or "Simple {primary_ingredient.title()}"
- Include the cuisine style, main ingredients, and cooking method in the title
- Make titles descriptive and appetizing like a restaurant menu

STEP REQUIREMENTS:
- Provide 10-12 highly detailed steps with professional techniques
- Include specific temperatures, timing, and techniques
- Example: "Heat 2 tablespoons olive oil in a large skillet over medium-high heat until shimmering, about 2 minutes"

RECIPE 1 - SAUTÉED/PAN-FRIED:
Recipe Name: Professional Sautéed {primary_ingredient.title()} with [Flavor Profile]
Cooking Method: sautéed
Estimated Time: 25 minutes
Difficulty: medium
Cuisine: Mediterranean/International
Tags: restaurant-style, quick, flavorful
Steps:
1. Preheat a large heavy-bottomed skillet over medium-high heat for 2-3 minutes until hot
2. Pat the {primary_ingredient} completely dry with paper towels and season generously with salt and freshly ground black pepper
3. Add 2 tablespoons high-heat oil to the hot pan and swirl to coat evenly
4. Carefully place the {primary_ingredient} in the pan, ensuring pieces don't overlap, and cook undisturbed for 3-4 minutes
5. Flip using tongs and cook for another 2-3 minutes until golden brown crust forms
6. Add 3 cloves minced garlic and 2 tablespoons butter, tilting pan to baste for 1 minute
7. Squeeze fresh lemon juice and add chopped herbs like parsley or thyme
8. Remove from heat and let rest for 2 minutes to allow juices to redistribute
9. Taste and adjust seasoning with additional salt, pepper, or lemon juice
10. Serve immediately while hot, garnished with fresh herbs and lemon wedges

RECIPE 2 - BAKED/ROASTED:
Recipe Name: Herb-Crusted Baked {primary_ingredient.title()} with [Seasonings]
Cooking Method: baked
Estimated Time: 35 minutes
Difficulty: medium
Cuisine: American/European
Tags: baked, herb-crusted, comfort-food
Steps:
1. Preheat oven to 400°F (200°C) and line a baking sheet with parchment paper
2. In a bowl, combine 1/2 cup breadcrumbs, 2 tbsp olive oil, 2 cloves minced garlic, and mixed herbs
3. Pat {primary_ingredient} dry and season with salt and pepper on both sides
4. Brush {primary_ingredient} with Dijon mustard or olive oil for coating to stick
5. Press the herb mixture firmly onto the {primary_ingredient} to create an even crust
6. Place on prepared baking sheet and drizzle with additional olive oil
7. Bake for 15-20 minutes until crust is golden brown and {primary_ingredient} is cooked through
8. Check internal temperature reaches safe cooking levels with a thermometer
9. Let rest for 5 minutes before slicing to retain juices
10. Serve with roasted vegetables or a fresh salad

RECIPE 3 - GRILLED/BROILED:
Recipe Name: Mediterranean Grilled {primary_ingredient.title()} with [Marinade/Sauce]
Cooking Method: grilled
Estimated Time: 30 minutes (including marinating)
Difficulty: medium
Cuisine: Mediterranean
Tags: grilled, smoky, mediterranean
Steps:
1. Preheat grill to medium-high heat and clean grates thoroughly
2. Create marinade with olive oil, lemon juice, minced garlic, oregano, and black pepper
3. Marinate {primary_ingredient} for 15-20 minutes, turning once halfway through
4. Remove from marinade and pat lightly dry, reserving marinade for basting
5. Oil the grill grates to prevent sticking
6. Place {primary_ingredient} on grill and cook for 4-5 minutes without moving
7. Flip once and cook for another 3-4 minutes, basting with reserved marinade
8. Check for proper doneness and grill marks, adjusting time as needed
9. Remove from grill and tent with foil, let rest for 3-4 minutes
10. Slice against the grain if applicable and serve with grilled vegetables

INGREDIENTS TO USE: {", ".join(ingredient_names)}
SERVINGS: {servings}

SPECIAL RULES:
- If ingredients include paneer and spinach, Recipe 1 MUST be "Palak Paneer (Traditional Indian Spinach Cottage Cheese Curry)"
- If ingredients include shrimp, create "Garlic Butter Shrimp Scampi" or similar
- Always use professional cooking techniques and specific details"""
        
        ai_input = prompt
        
        logger.info(f"Calling Bedrock Agent with {len(ingredients_data)} ingredients")
        
        # First, check if the agent exists
        try:
            logger.info(f"Checking if Bedrock Agent {agent_id} exists")
            bedrock_agent_mgmt = bedrock_agent_mgmt_client
            agent_info = bedrock_agent_mgmt.get_agent(agentId=agent_id)
            logger.info(f"Agent found: {agent_info['agent']['agentName']} - Status: {agent_info['agent']['agentStatus']}")
            
            # Check if agent is prepared
            if agent_info['agent']['agentStatus'] not in ['PREPARED', 'CREATING']:
                logger.warning(f"Agent status is {agent_info['agent']['agentStatus']}, may not be ready for invocation")
                
        except Exception as agent_check_error:
            logger.error(f"Agent {agent_id} not found or not accessible: {agent_check_error}")
            raise Exception(f"Bedrock Agent not available: {agent_check_error}")
        
        # Try to get agent aliases
        try:
            aliases_response = bedrock_agent_mgmt.list_agent_aliases(agentId=agent_id)
            available_aliases = [alias['agentAliasId'] for alias in aliases_response.get('agentAliasSummaries', [])]
            logger.info(f"Available aliases: {available_aliases}")
            
            if not available_aliases:
                raise Exception("No agent aliases available")
                
        except Exception as alias_error:
            logger.error(f"Could not list agent aliases: {alias_error}")
            raise Exception(f"Agent aliases not available: {alias_error}")
        
        # Call Bedrock Agent with the live alias (prefer 3TWYTIVDSI over TSTALIASID)
        session_id = f"recipe_session_{user_id}_{uuid.uuid4().hex[:8]}"
        
        # Use TSTALIASID (DRAFT) which has the Titan model, not 3TWYTIVDSI (version 1) which has Claude
        if 'TSTALIASID' in available_aliases:
            alias_to_use = 'TSTALIASID'
            logger.info("Using test alias (TSTALIASID) pointing to DRAFT version with Titan model")
        elif '3TWYTIVDSI' in available_aliases:
            alias_to_use = '3TWYTIVDSI'
            logger.info("Using live alias (3TWYTIVDSI) pointing to version 1 with Claude model")
        else:
            alias_to_use = available_aliases[0]
            logger.info(f"Using first available alias: {alias_to_use}")
        
        # Construct the full agent alias ARN
        region = 'us-west-2'
        account_id = '709716141648'
        agent_alias_arn = f"arn:aws:bedrock:{region}:{account_id}:agent-alias/{agent_id}/{alias_to_use}"
        
        logger.info(f"Calling Bedrock Agent with alias ARN: {agent_alias_arn} and session {session_id}")
        
        # Log the exact parameters being used
        logger.info(f"invoke_agent parameters:")
        logger.info(f"  agentId: {agent_id}")
        logger.info(f"  agentAliasId: {alias_to_use}")
        logger.info(f"  sessionId: {session_id}")
        logger.info(f"  region: {region}")
        
        logger.info(f"Sending input to Bedrock Agent: {ai_input[:200]}...")
        
        response = bedrock_agent_client.invoke_agent(
            agentId=agent_id,
            agentAliasId=alias_to_use,
            sessionId=session_id,
            inputText=ai_input
        )
        
        logger.info(f"Successfully invoked Bedrock Agent with alias {alias_to_use}")
        logger.info(f"Response structure: {list(response.keys())}")
        
        if not response:
            raise Exception("Bedrock Agent response is empty")
        
        # Parse agent response
        ai_recipes = []
        response_text = ""
        
        # Stream the response
        if 'completion' in response:
            logger.info(f"Found completion in response")
            for event in response['completion']:
                logger.info(f"Processing event: {list(event.keys())}")
                if 'chunk' in event:
                    chunk = event['chunk']
                    logger.info(f"Chunk structure: {list(chunk.keys())}")
                    if 'bytes' in chunk:
                        chunk_text = chunk['bytes'].decode('utf-8')
                        response_text += chunk_text
                        logger.info(f"Added chunk: {chunk_text[:100]}...")
        else:
            logger.error("No 'completion' key in response")
            logger.error(f"Available keys: {list(response.keys())}")
        
        logger.info(f"Total response length: {len(response_text)}")
        logger.info(f"AI Response: {response_text[:200]}...")
        
        # Try to parse JSON response from AI
        try:
            # Clean up the response text - sometimes AI adds extra text before/after JSON
            response_text = response_text.strip()
            
            # Try to find JSON in the response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_text = response_text[json_start:json_end]
                logger.info(f"Extracted JSON: {json_text[:300]}...")
                
                ai_response = json.loads(json_text)
                if 'recipes' in ai_response:
                    ai_recipes = ai_response['recipes']
                else:
                    # If response is just an array
                    ai_recipes = ai_response if isinstance(ai_response, list) else []
            else:
                logger.warning("No JSON found in response, trying text parsing")
                ai_recipes = extract_recipes_from_text(response_text, ingredients_data)
                
        except json.JSONDecodeError as json_error:
            logger.warning(f"Could not parse AI response as JSON: {json_error}")
            logger.warning(f"Raw response: {response_text[:500]}...")
            logger.info("Extracting recipes manually from text")
            ai_recipes = extract_recipes_from_text(response_text, ingredients_data)
        
        # If we still don't have recipes, try a different approach
        if not ai_recipes or len(ai_recipes) == 0:
            logger.warning("No recipes extracted from agent response, trying text-based extraction")
            ai_recipes = extract_recipes_from_text(response_text, ingredients_data)
        
        # Convert AI recipes to our format
        formatted_recipes = []
        for i, ai_recipe in enumerate(ai_recipes[:4]):  # Limit to 4 recipes
            formatted_recipe = format_ai_recipe(ai_recipe, ingredients_data, nutrition, servings)
            formatted_recipes.append(formatted_recipe)
        
        if formatted_recipes:
            logger.info(f"Successfully generated {len(formatted_recipes)} AI recipes")
            return formatted_recipes
        else:
            logger.error("No valid AI recipes generated - AI returned empty response")
            raise Exception("AI recipe generation failed - no recipes returned")
            
    except Exception as e:
        logger.error(f"Error generating AI recipes with Bedrock Agent: {str(e)}")
        logger.info("Trying direct Bedrock model call as fallback")
        
        # Try direct Bedrock model call as fallback
        try:
            return generate_recipes_direct_bedrock(ingredients_data, nutrition, servings)
        except Exception as direct_error:
            logger.error(f"Direct Bedrock model call also failed: {str(direct_error)}")
            raise Exception(f"Both Bedrock Agent and direct model calls failed: Agent={str(e)}, Direct={str(direct_error)}")

def generate_recipes_direct_bedrock(ingredients_data: List[Dict], nutrition: Dict, servings: int) -> List[Dict[str, Any]]:
    """Generate recipes using direct Bedrock model call as fallback"""
    
    bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-west-2')
    
    # Create ingredient list
    ingredient_names = [item['name'] for item in ingredients_data]
    logger.info(f"Generating recipes with direct Titan call for: {ingredient_names}")
    
    # Create a simpler prompt that works better with Titan
    primary_ingredient = ingredient_names[0] if ingredient_names else "ingredient"
    
    # Titan works better with simpler, more direct prompts
    prompt = f"""Create 3 simple recipes using: {', '.join(ingredient_names)}

Recipe 1: Quick {primary_ingredient.title()}
- Heat oil in pan
- Add {primary_ingredient} and cook 5 minutes
- Add other ingredients
- Cook 10 more minutes
- Season and serve

Recipe 2: Baked {primary_ingredient.title()}
- Preheat oven to 375°F
- Mix ingredients in baking dish
- Bake 25 minutes
- Serve hot

Recipe 3: Fresh {primary_ingredient.title()}
- Combine all ingredients
- Mix well
- Let sit 10 minutes
- Serve fresh

Ingredients: {', '.join(ingredient_names)}
Servings: {servings}"""

    try:
        # Try Titan model as fallback
        response = bedrock_runtime.invoke_model(
            modelId='amazon.titan-text-express-v1',
            body=json.dumps({
                'inputText': prompt,
                'textGenerationConfig': {
                    'maxTokenCount': 2000,
                    'temperature': 0.7,
                    'topP': 0.9
                }
            })
        )
        
        response_body = json.loads(response['body'].read())
        response_text = response_body['results'][0]['outputText']
        
        logger.info(f"Direct Titan response: {response_text[:200]}...")
        
        # Parse text response from Titan (not JSON)
        try:
            # Extract recipes from Titan's text response
            recipes = parse_titan_text_response(response_text, ingredients_data, nutrition, servings)
            
            if recipes and len(recipes) > 0:
                logger.info(f"Successfully generated {len(recipes)} recipes with direct Titan call")
                return recipes
            else:
                logger.warning("No recipes could be parsed from Titan response")
                # Fall back to static recipes
                return generate_basic_fallback_recipes(ingredients_data, nutrition, servings)
        
        except Exception as parse_error:
            logger.warning(f"Could not parse Titan response: {parse_error}")
            # Fall back to static recipes
            return generate_basic_fallback_recipes(ingredients_data, nutrition, servings)
        
    except Exception as e:
        logger.error(f"Direct Titan model call failed: {str(e)}")
        # Final fallback to static recipes
        logger.info("Using static fallback recipes")
        return generate_basic_fallback_recipes(ingredients_data, nutrition, servings)

def format_ai_recipe(ai_recipe: Dict, ingredients: List[Dict], nutrition: Dict, servings: int) -> Dict[str, Any]:
    """Format AI-generated recipe to our standard format"""
    
    # Create ingredient list with our format
    formatted_ingredients = []
    for ingredient in ingredients:
        formatted_ingredients.append({
            'name': ingredient['name'],
            'grams': ingredient['grams'],
            'notes': get_ingredient_notes(ingredient['name']),
            'fdc_id': ingredient.get('fdc_id', '')
        })
    
    # Extract recipe data from AI response
    title = ai_recipe.get('title', 'AI-Generated Recipe')
    steps = ai_recipe.get('steps', ['Prepare ingredients as directed'])
    tags = ai_recipe.get('tags', ['ai-generated'])
    substitutions = ai_recipe.get('substitutions', ['Adjust seasonings to taste'])
    warnings = ai_recipe.get('warnings', [])
    
    # Extract additional fields
    estimated_time = ai_recipe.get('estimated_time', '25 minutes')
    difficulty = ai_recipe.get('difficulty', 'medium')
    cuisine = ai_recipe.get('cuisine', 'International')
    cooking_method = ai_recipe.get('cooking_method', 'mixed')
    
    # Add cooking method and time tags if not already in tags
    if cooking_method and cooking_method not in tags:
        tags.append(cooking_method)
    if estimated_time and estimated_time not in tags:
        tags.append(estimated_time.replace(' minutes', '-min'))
    if difficulty and difficulty not in tags:
        tags.append(difficulty)
    if cuisine and cuisine.lower() not in [tag.lower() for tag in tags]:
        tags.append(cuisine.lower())
    
    return {
        'title': title,
        'servings': servings,
        'estimated_time': estimated_time,
        'difficulty': difficulty,
        'cuisine': cuisine,
        'tags': tags,
        'ingredients': formatted_ingredients,
        'steps': steps,
        'substitutions': substitutions,
        'warnings': warnings
    }

def extract_recipes_from_text(text: str, ingredients_data: List[Dict] = None) -> List[Dict]:
    """Extract recipe information from AI text response if JSON parsing fails"""
    recipes = []
    
    logger.info(f"Parsing AI text response: {text[:300]}...")
    
    # Try multiple parsing strategies
    
    # Strategy 1: Look for numbered recipes
    recipe_patterns = [
        r'Recipe \d+[:\-\s]*(.+?)(?=Recipe \d+|$)',
        r'\d+\.\s*(.+?)(?=\d+\.|$)',
        r'Title:\s*(.+?)(?=Title:|$)',
    ]
    
    for pattern in recipe_patterns:
        import re
        matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
        if matches:
            logger.info(f"Found {len(matches)} recipe matches with pattern")
            for i, match in enumerate(matches[:3]):
                recipe = parse_recipe_text_block(match.strip(), i+1)
                if recipe:
                    recipes.append(recipe)
            break
    
    # Strategy 2: If no structured recipes found, create basic recipes from text
    if len(recipes) == 0:
        logger.info("No structured recipes found, creating basic recipes from text")
        recipes = create_basic_recipes_from_text(text, ingredients_data)
    
    # Strategy 3: If still no recipes, use static fallback
    if len(recipes) == 0:
        logger.warning("No recipes could be extracted from AI response, using static fallback")
        recipes = generate_basic_fallback_recipes(ingredients_data or [], {}, 2)
    
    logger.info(f"Generated {len(recipes)} total recipes")
    return recipes[:3]  # Return exactly 3 recipes

def parse_recipe_text_block(text_block: str, recipe_num: int) -> Dict:
    """Parse a single recipe text block"""
    lines = text_block.split('\n')
    
    # Extract title (first meaningful line)
    title = f"AI Recipe {recipe_num}"
    for line in lines:
        line = line.strip()
        if line and not line.startswith(('Recipe', 'Ingredients:', 'Steps:', 'Instructions:')):
            title = line
            break
    
    # Extract steps
    steps = []
    in_steps = False
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if any(keyword in line.lower() for keyword in ['steps:', 'instructions:', 'method:']):
            in_steps = True
            continue
            
        if in_steps and (line[0].isdigit() or line.startswith(('•', '-', '*'))):
            step_text = line
            if line[0].isdigit() and '.' in line:
                step_text = line.split('.', 1)[1].strip()
            elif line.startswith(('•', '-', '*')):
                step_text = line[1:].strip()
            steps.append(step_text)
    
    # If no steps found, create basic ones
    if not steps:
        steps = [
            "Prepare all ingredients",
            "Heat oil in a pan over medium heat",
            "Add ingredients and cook until tender",
            "Season with salt and pepper to taste",
            "Serve hot"
        ]
    
    return {
        'title': title,
        'cooking_method': 'mixed',
        'estimated_time': '25 minutes',
        'difficulty': 'medium',
        'cuisine': 'International',
        'tags': ['ai-generated'],
        'steps': steps,
        'substitutions': ['Adjust seasonings to taste'],
        'warnings': ['Cook to safe temperatures']
    }

def create_basic_recipes_from_text(text: str, ingredients_data: List[Dict]) -> List[Dict]:
    """Create basic recipes when structured parsing fails"""
    if not ingredients_data:
        return []
    
    primary_ingredient = ingredients_data[0]['name'] if ingredients_data else "ingredient"
    
    recipes = [
        {
            'title': f'Simple {primary_ingredient.title()} Dish',
            'cooking_method': 'sautéed',
            'estimated_time': '25 minutes',
            'difficulty': 'easy',
            'cuisine': 'International',
            'tags': ['quick', 'simple'],
            'steps': [
                'Heat 2 tablespoons oil in a large pan',
                f'Add {primary_ingredient} and cook for 5 minutes',
                'Add remaining ingredients',
                'Cook until tender, about 10-15 minutes',
                'Season with salt and pepper',
                'Serve hot'
            ],
            'substitutions': ['Use any cooking oil', 'Add herbs for extra flavor'],
            'warnings': ['Cook to safe temperatures']
        }
    ]
    
    return recipes

def parse_recipe_section(section: str) -> Dict:
    """Parse a single recipe section"""
    recipe = {
        'title': 'AI-Generated Recipe',
        'estimated_time': '25 minutes',
        'difficulty': 'medium',
        'cuisine': 'International',
        'tags': ['ai-generated'],
        'steps': [],
        'substitutions': ['Adjust seasonings to taste'],
        'warnings': ['Cook to safe temperatures']
    }
    
    lines = section.split('\n')
    current_section = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('Recipe Name:'):
            recipe['title'] = line.replace('Recipe Name:', '').strip()
        elif line.startswith('Cooking Method:'):
            method = line.replace('Cooking Method:', '').strip()
            if method not in recipe['tags']:
                recipe['tags'].append(method)
        elif line.startswith('Estimated Time:'):
            recipe['estimated_time'] = line.replace('Estimated Time:', '').strip()
        elif line.startswith('Difficulty:'):
            recipe['difficulty'] = line.replace('Difficulty:', '').strip()
        elif line.startswith('Cuisine:'):
            recipe['cuisine'] = line.replace('Cuisine:', '').strip()
        elif line.startswith('Tags:'):
            tags_text = line.replace('Tags:', '').strip()
            recipe['tags'] = [tag.strip() for tag in tags_text.split(',')]
        elif line.startswith('Steps:'):
            current_section = 'steps'
        elif line.startswith('Substitutions:'):
            current_section = 'substitutions'
        elif line.startswith('Warnings:'):
            current_section = 'warnings'
        elif current_section == 'steps' and line and (line[0].isdigit() or line.startswith(('•', '-', '*'))):
            step_text = line
            if line[0].isdigit() and '.' in line:
                step_text = line.split('.', 1)[1].strip()
            elif line.startswith(('•', '-', '*')):
                step_text = line[1:].strip()
            recipe['steps'].append(step_text)
        elif current_section == 'substitutions' and line:
            recipe['substitutions'].append(line)
        elif current_section == 'warnings' and line:
            recipe['warnings'].append(line)
    
    return recipe if recipe['steps'] else None

def parse_single_recipe_from_text(text: str) -> Dict:
    """Parse a single recipe from unstructured text"""
    recipe = {
        'title': 'AI-Generated Recipe',
        'estimated_time': '25 minutes',
        'difficulty': 'medium',
        'cuisine': 'International',
        'tags': ['ai-generated'],
        'steps': [],
        'substitutions': ['Adjust seasonings to taste'],
        'warnings': ['Cook to safe temperatures']
    }
    
    lines = text.split('\n')
    current_section = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Extract key information
        if line.startswith('Recipe Name:'):
            recipe['title'] = line.replace('Recipe Name:', '').strip()
        elif line.startswith('Cooking Method:'):
            method = line.replace('Cooking Method:', '').strip()
            recipe['tags'].append(method)
        elif line.startswith('Estimated Time:'):
            recipe['estimated_time'] = line.replace('Estimated Time:', '').strip()
        elif line.startswith('Difficulty:'):
            recipe['difficulty'] = line.replace('Difficulty:', '').strip()
        elif line.startswith('Cuisine:'):
            recipe['cuisine'] = line.replace('Cuisine:', '').strip()
        elif line.startswith('Tags:'):
            tags_text = line.replace('Tags:', '').strip()
            recipe['tags'] = [tag.strip() for tag in tags_text.split(',')]
        elif line.startswith('Steps:'):
            current_section = 'steps'
        elif current_section == 'steps' and line and (line[0].isdigit() or line.startswith(('•', '-', '*'))):
            step_text = line
            if line[0].isdigit() and '.' in line:
                step_text = line.split('.', 1)[1].strip()
            elif line.startswith(('•', '-', '*')):
                step_text = line[1:].strip()
            recipe['steps'].append(step_text)
    
    return recipe if recipe['steps'] else None

def get_ingredient_notes(ingredient_name: str) -> str:
    """Get preparation notes for ingredients"""
    notes_map = {
        'apple': 'washed and cored',
        'banana': 'ripe, peeled and sliced',
        'egg': 'room temperature works best',
        'potato': 'washed and peeled if desired',
        'tomato': 'ripe and fresh',
        'chicken': 'boneless, skinless',
        'onion': 'peeled and diced',
        'spinach': 'washed and trimmed',
        'paneer': 'cut into cubes',
        'avocado': 'ripe and pitted'
    }
    return notes_map.get(ingredient_name.lower(), 'prepared as needed')

def generate_palak_paneer_recipe(ingredients, nutrition, servings):
    """Generate authentic Palak Paneer recipe"""
    return {
        'title': 'Palak Paneer (Indian Spinach Cottage Cheese Curry)',
        'servings': servings,
        'estimated_time': '30 minutes',
        'difficulty': 'medium',
        'cuisine': 'Indian',
        'tags': ['indian', 'vegetarian', 'curry', '30-min', 'authentic'],
        'ingredients': ingredients,
        'steps': [
            "Heat 2 tablespoons oil in a heavy-bottomed pan over medium heat",
            "Add 1 teaspoon cumin seeds and let them splutter for 30 seconds",
            "Add 1 finely chopped onion and sauté until golden brown (5-6 minutes)",
            "Add 1 tablespoon ginger-garlic paste and cook for 1 minute until fragrant",
            "Add 1 chopped tomato and cook until soft and mushy (3-4 minutes)",
            "Add the washed spinach leaves and cook until wilted (2-3 minutes)",
            "Let the mixture cool, then blend to a smooth puree with little water",
            "Return puree to the pan, add 1/2 tsp turmeric, 1 tsp coriander powder, 1/2 tsp garam masala",
            "Simmer for 5 minutes, then gently add paneer cubes",
            "Cook for 3-4 minutes without stirring too much to prevent paneer from breaking",
            "Add salt to taste and 2 tablespoons fresh cream",
            "Garnish with fresh coriander and serve hot with basmati rice or naan bread"
        ],
        'substitutions': [
            "Vegan: Substitute paneer with firm tofu",
            "Spice it up by adding green chilies or red chili powder",
            "Add cashews while blending for extra creaminess",
            "Use coconut milk instead of cream for dairy-free option"
        ],
        'warnings': [
            "Potential allergens: Dairy (paneer, cream). Use tofu and coconut milk for dairy-free",
            "Don't overcook paneer as it becomes rubbery",
            "Blanch spinach in boiling water for better color retention"
        ]
    }

def generate_paneer_spinach_salad_recipe(ingredients, nutrition, servings):
    """Generate fresh Paneer Spinach Salad recipe"""
    return {
        'title': 'Fresh Paneer Spinach Salad with Indian Spices',
        'servings': servings,
        'tags': ['indian', 'vegetarian', 'fresh', '15-min', 'healthy'],
        'ingredients': ingredients,
        'steps': [
            "Wash and thoroughly dry fresh spinach leaves",
            "Cut paneer into small cubes and lightly pan-fry until golden",
            "In a large bowl, combine spinach leaves with the warm paneer",
            "Prepare dressing: mix 2 tbsp olive oil, 1 tbsp lemon juice, 1/2 tsp chaat masala",
            "Add 1/4 tsp black pepper, 1/2 tsp roasted cumin powder, and salt to taste",
            "Toss the salad with dressing just before serving",
            "Garnish with pomegranate seeds and chopped mint if available",
            "Serve immediately as a light meal or side dish"
        ],
        'substitutions': [
            "Add cherry tomatoes and cucumber for extra freshness",
            "Use hung curd instead of oil for lighter dressing",
            "Add roasted peanuts for crunch"
        ],
        'warnings': [
            "Dress the salad just before serving to prevent wilting"
        ]
    }

def generate_spinach_paneer_curry_recipe(ingredients, nutrition, servings):
    """Generate Spinach Paneer Curry recipe"""
    return {
        'title': 'Spinach Paneer Curry (Restaurant Style)',
        'servings': servings,
        'tags': ['indian', 'vegetarian', 'curry', '25-min', 'restaurant-style'],
        'ingredients': ingredients,
        'steps': [
            "Blanch spinach in boiling water for 2 minutes, then plunge in ice water",
            "Drain and blend spinach with 2 green chilies to smooth paste",
            "Heat 3 tablespoons ghee or oil in a pan over medium heat",
            "Add 1 bay leaf, 2 green cardamom, 1-inch cinnamon stick",
            "Add 1 sliced onion and cook until golden brown",
            "Add 1 tbsp ginger-garlic paste, cook for 1 minute",
            "Add 1/2 tsp turmeric, 1 tsp coriander powder, 1/2 tsp red chili powder",
            "Add the spinach puree and cook for 8-10 minutes on medium heat",
            "Add 1/4 cup water if needed, then add paneer cubes gently",
            "Simmer for 5 minutes, add 1/2 tsp garam masala",
            "Finish with 2 tbsp cream and fresh coriander",
            "Serve hot with rotis or steamed rice"
        ],
        'substitutions': [
            "Use mustard greens (sarson) mixed with spinach for variation",
            "Add a pinch of sugar to balance the flavors",
            "Use butter instead of ghee for richer taste"
        ],
        'warnings': [
            "Don't boil the curry after adding cream",
            "Add paneer at the end to prevent it from becoming hard"
        ]
    }

def generate_fresh_recipe(ingredients, main_ingredients, nutrition, servings):
    """Generate a fresh/raw recipe option"""
    if len(main_ingredients) == 1:
        title = f"Fresh {main_ingredients[0].title()} Bowl"
    elif len(main_ingredients) == 2:
        title = f"{main_ingredients[0].title()} and {main_ingredients[1].title()} Salad"
    else:
        title = f"Fresh {main_ingredients[0].title()} Mix"
    
    return {
        'title': title,
        'servings': servings,
        'estimated_time': '10 minutes',
        'difficulty': 'easy',
        'cuisine': 'Fresh',
        'tags': ['fresh', 'raw', 'healthy', '10-min'],
        'ingredients': ingredients,
        'steps': [
            "Wash all ingredients thoroughly under cold running water",
            "Pat dry with clean paper towels or kitchen cloth",
            "Cut ingredients into bite-sized pieces using a sharp knife",
            "Arrange attractively in a serving bowl or individual plates",
            "Drizzle with fresh lemon juice or your favorite dressing",
            "Season with salt and freshly ground black pepper to taste",
            "Serve immediately while fresh and crisp"
        ],
        'substitutions': [
            "Add toasted nuts or seeds for extra crunch and protein",
            "Use balsamic vinegar instead of lemon juice",
            "Drizzle with extra virgin olive oil for healthy fats"
        ],
        'warnings': [
            "Potential allergens: None (unless nuts added)",
            "Wash all fresh ingredients thoroughly to remove dirt and bacteria",
            "Consume immediately for best texture and nutrition"
        ]
    }

def generate_cooked_recipe(ingredients, main_ingredients, nutrition, servings):
    """Generate a cooked/sautéed recipe option"""
    if len(main_ingredients) == 1:
        title = f"Sautéed {main_ingredients[0].title()}"
    elif len(main_ingredients) == 2:
        title = f"{main_ingredients[0].title()} and {main_ingredients[1].title()} Stir-Fry"
    else:
        title = f"Mixed {main_ingredients[0].title()} Sauté"
    
    return {
        'title': title,
        'servings': servings,
        'tags': ['cooked', 'sautéed', 'warm', '15-min'],
        'ingredients': ingredients,
        'steps': [
            "Heat 1-2 tablespoons of oil in a large pan over medium heat.",
            "Add harder ingredients first (like apples, potatoes).",
            "Cook for 3-5 minutes until starting to soften.",
            "Add softer ingredients (like bananas, leafy greens).",
            "Stir gently and cook for another 2-3 minutes.",
            "Season with salt, pepper, and your favorite spices.",
            "Serve hot as a side dish or main course."
        ],
        'substitutions': [
            "Use butter instead of oil for richer flavor",
            "Add garlic and onions for extra flavor"
        ],
        'warnings': [
            "Don't overcook soft ingredients",
            "Cook to safe internal temperatures"
        ]
    }

def generate_blended_recipe(ingredients, main_ingredients, nutrition, servings):
    """Generate a smoothie/blended recipe option"""
    if len(main_ingredients) == 1:
        title = f"{main_ingredients[0].title()} Smoothie"
    elif len(main_ingredients) == 2:
        title = f"{main_ingredients[0].title()} {main_ingredients[1].title()} Smoothie Bowl"
    else:
        title = f"Mixed Fruit Smoothie"
    
    return {
        'title': title,
        'servings': servings,
        'tags': ['smoothie', 'blended', 'healthy', '5-min'],
        'ingredients': ingredients,
        'steps': [
            "Add all ingredients to a high-speed blender.",
            "Add 1/2 to 1 cup of liquid (milk, water, or juice).",
            "Blend on high speed for 30-60 seconds until smooth.",
            "Check consistency and add more liquid if needed.",
            "Pour into glasses or bowls.",
            "Top with your favorite garnishes and serve immediately."
        ],
        'substitutions': [
            "Use frozen ingredients for thicker texture",
            "Add protein powder for extra nutrition",
            "Use coconut milk for dairy-free option"
        ],
        'warnings': [
            "Start blender on low speed to avoid splashing"
        ]
    }

def generate_baked_recipe(ingredients, main_ingredients, nutrition, servings):
    """Generate a baked recipe option"""
    if len(main_ingredients) == 1:
        title = f"Baked {main_ingredients[0].title()}"
    elif len(main_ingredients) == 2:
        title = f"Roasted {main_ingredients[0].title()} and {main_ingredients[1].title()}"
    else:
        title = f"Baked {main_ingredients[0].title()} Medley"
    
    return {
        'title': title,
        'servings': servings,
        'tags': ['baked', 'roasted', 'warm', '30-min'],
        'ingredients': ingredients,
        'steps': [
            "Preheat oven to 375°F (190°C).",
            "Cut ingredients into uniform pieces.",
            "Toss with olive oil, salt, and pepper.",
            "Arrange in a single layer on a baking sheet.",
            "Bake for 20-25 minutes, flipping halfway through.",
            "Cook until tender and lightly golden.",
            "Serve hot as a side dish or snack."
        ],
        'substitutions': [
            "Add herbs like rosemary or thyme",
            "Drizzle with honey for sweetness"
        ],
        'warnings': [
            "Don't overcrowd the baking sheet",
            "Check for doneness with a fork"
        ]
    }
    
    # Generate cooking steps based on ingredients
    primary_ingredient = items[0]['label'] if items else 'ingredients'
    
    # Customize steps based on primary ingredient
    if 'banana' in primary_ingredient.lower():
        steps = [
            f"Peel and slice the {primary_ingredient}.",
            "Add to a blender with your choice of liquid (milk, yogurt, etc.).",
            "Blend until smooth and creamy.",
            "Add other ingredients and blend briefly to combine.",
            "Pour into a bowl or glass.",
            "Top with your favorite garnishes and serve immediately."
        ]
    elif 'apple' in primary_ingredient.lower():
        steps = [
            f"Wash and core the {primary_ingredient}.",
            "Cut into slices or chunks as desired.",
            "If cooking, heat a pan over medium heat.",
            "Add the apple pieces and cook until tender.",
            "Season with cinnamon or other spices to taste.",
            "Serve warm or at room temperature."
        ]
    elif 'egg' in primary_ingredient.lower():
        steps = [
            f"Crack the {primary_ingredient}s into a bowl.",
            "Whisk until well combined.",
            "Heat a non-stick pan over medium-low heat.",
            "Add a little butter or oil to the pan.",
            "Pour in the eggs and cook, stirring gently.",
            "Remove from heat when just set and serve immediately."
        ]
    else:
        steps = [
            f"Prepare the {primary_ingredient} by washing and chopping as needed.",
            "Heat a large pan or skillet over medium heat.",
            "Add ingredients starting with those that take longest to cook.",
            "Cook until all ingredients are tender and heated through.",
            "Season to taste with salt and pepper.",
            "Serve hot and enjoy!"
        ]
    
    # Basic tags
    tags = ["homemade", "fresh"]
    
    # Add protein tag if protein content is high
    if nutrition.get('per_serving', {}).get('protein_g', 0) > 15:
        tags.append("high-protein")
    
    # Add low-carb tag if carb content is low
    if nutrition.get('per_serving', {}).get('carb_g', 0) < 10:
        tags.append("low-carb")
    
    return {
        'title': title,
        'servings': servings,
        'tags': tags,
        'ingredients': ingredients,
        'steps': steps,
        'substitutions': [
            "Season with your favorite herbs and spices",
            "Add vegetables of your choice for extra nutrition"
        ],
        'warnings': [
            "Cook all ingredients to safe internal temperatures",
            "Wash hands and surfaces frequently when handling food"
        ]
    }

def handler(event, context):
    """Lambda handler for creating recipes"""
    try:
        # Parse request body
        body = json.loads(event['body'])
        
        # Extract parameters
        scan_id = body.get('scan_id')
        servings = body.get('servings', 2)
        cuisine_preference = body.get('cuisine', 'indian')  # Default to Indian
        skill_level = body.get('skill_level', 'intermediate')  # beginner, intermediate, advanced
        dietary_restrictions = body.get('dietary_restrictions', [])  # vegan, gluten-free, etc.
        mock_ingredients = body.get('mock_ingredients')  # For testing
        
        # Debug logging for request body
        logger.info(f"Request body keys: {list(body.keys())}")
        logger.info(f"Raw cuisine value: '{body.get('cuisine')}'")
        logger.info(f"Full request body: {body}")
        
        logger.info(f"Recipe generation request: scan_id={scan_id}, cuisine={cuisine_preference}, skill={skill_level}, dietary={dietary_restrictions}")
        
        # Additional debugging for cuisine parameter
        if body.get('cuisine') is None:
            logger.warning("CUISINE PARAMETER IS MISSING FROM REQUEST BODY!")
            logger.warning("This means the UI is not sending the cuisine selection correctly")
        elif body.get('cuisine') != cuisine_preference:
            logger.warning(f"Cuisine mismatch: received '{body.get('cuisine')}' but using '{cuisine_preference}'")
        
        # If mock ingredients provided, use them directly (for testing)
        if mock_ingredients:
            logger.info(f"Using mock ingredients for testing: {mock_ingredients}")
            items = mock_ingredients
            fdc_ids = [item.get('fdc_id', '') for item in items]
            
            # Skip database lookup and use mock data
            try:
                api_key = get_usda_api_key()
                nutrition_facts = fetch_usda_nutrients(fdc_ids, api_key)
            except:
                nutrition_facts = {}
            
            nutrition = compute_nutrition(items, nutrition_facts, servings)
            
            # Generate recipes with mock data - use simple fallback for now
            try:
                logger.info(f"Generating {cuisine_preference} recipes for mock ingredients")
                recipe_options = generate_simple_cuisine_recipes(items, nutrition, servings, cuisine_preference)
                logger.info(f"Generated {len(recipe_options)} recipes with mock data for {cuisine_preference} cuisine")
            except Exception as recipe_error:
                logger.error(f"Failed to generate recipes with mock data: {recipe_error}")
                # Use basic fallback
                recipe_options = generate_basic_fallback_recipes(items, nutrition, servings)
            
            # Store recipes in database and return response
            recipe_ids = []
            for recipe in recipe_options:
                recipe_id = str(uuid.uuid4())
                recipe_ids.append(recipe_id)
                
                # Store in database
                rds_client.execute_statement(
                    resourceArn=os.environ['DB_CLUSTER_ARN'],
                    secretArn=os.environ['DB_SECRET_ARN'],
                    database='ayeaye',
                    sql="""
                        INSERT INTO recipes (id, user_id, title, servings, ingredients, steps, tags, substitutions, warnings, nutrition, created_at)
                        VALUES (:id, :user_id, :title, :servings, :ingredients, :steps, :tags, :substitutions, :warnings, :nutrition, NOW())
                    """,
                    parameters=[
                        {'name': 'id', 'value': {'stringValue': recipe_id}},
                        {'name': 'user_id', 'value': {'stringValue': user_id}},
                        {'name': 'title', 'value': {'stringValue': recipe['title']}},
                        {'name': 'servings', 'value': {'longValue': recipe['servings']}},
                        {'name': 'ingredients', 'value': {'stringValue': json.dumps(recipe['ingredients'])}},
                        {'name': 'steps', 'value': {'stringValue': json.dumps(recipe['steps'])}},
                        {'name': 'tags', 'value': {'stringValue': json.dumps(recipe['tags'])}},
                        {'name': 'substitutions', 'value': {'stringValue': json.dumps(recipe.get('substitutions', []))}},
                        {'name': 'warnings', 'value': {'stringValue': json.dumps(recipe.get('warnings', []))}},
                        {'name': 'nutrition', 'value': {'stringValue': json.dumps(nutrition)}}
                    ]
                )
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'recipe_ids': recipe_ids,
                    'recipes': [{'id': recipe_ids[i], 'title': recipe['title'], 'tags': recipe['tags']} 
                               for i, recipe in enumerate(recipe_options)],
                    'servings': servings,
                    'message': f'{len(recipe_options)} recipe options created successfully'
                })
            }
        
        if not scan_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Missing required parameter: scan_id'
                })
            }
        
        # Get user ID from JWT
        user_id = event['requestContext']['authorizer']['claims']['sub']
        
        logger.info(f"Creating recipe for scan {scan_id}, user {user_id}, servings {servings}, cuisine: {cuisine_preference}")
        
        # Database connection info
        db_secret_arn = os.environ['DB_SECRET_ARN']
        db_cluster_arn = os.environ['DB_CLUSTER_ARN']
        
        # Validate scan ownership and status
        try:
            scan_response = rds_client.execute_statement(
                resourceArn=db_cluster_arn,
                secretArn=db_secret_arn,
                database='ayeaye',
                sql="""
                    SELECT status FROM scans 
                    WHERE id::text = :scan_id AND user_id::text = :user_id
                """,
                parameters=[
                    {'name': 'scan_id', 'value': {'stringValue': scan_id}},
                    {'name': 'user_id', 'value': {'stringValue': user_id}}
                ]
            )
            
            if not scan_response['records']:
                logger.warning(f"Scan {scan_id} not found for user {user_id}, using fallback ingredients")
                
                # Instead of failing, use cuisine-appropriate fallback ingredients
                fallback_items = get_cuisine_appropriate_fallback_ingredients(cuisine_preference)
                
                logger.info("Using fallback ingredients for recipe generation")
                
                # Generate recipes with fallback ingredients
                try:
                    api_key = get_usda_api_key()
                    nutrition_facts = fetch_usda_nutrients([item['fdc_id'] for item in fallback_items], api_key)
                except:
                    nutrition_facts = {}
                
                nutrition = compute_nutrition(fallback_items, nutrition_facts, servings)
                recipe_options = generate_simple_cuisine_recipes(fallback_items, nutrition, servings, cuisine_preference)
                
                # Store recipes and return success
                recipe_ids = []
                for recipe in recipe_options:
                    recipe_id = str(uuid.uuid4())
                    recipe_ids.append(recipe_id)
                    
                    try:
                        rds_client.execute_statement(
                            resourceArn=os.environ['DB_CLUSTER_ARN'],
                            secretArn=os.environ['DB_SECRET_ARN'],
                            database='ayeaye',
                            sql="""
                                INSERT INTO recipes (id, user_id, title, servings, ingredients, steps, tags, substitutions, warnings, nutrition, created_at)
                                VALUES (:id, :user_id, :title, :servings, :ingredients, :steps, :tags, :substitutions, :warnings, :nutrition, NOW())
                            """,
                            parameters=[
                                {'name': 'id', 'value': {'stringValue': recipe_id}},
                                {'name': 'user_id', 'value': {'stringValue': user_id}},
                                {'name': 'title', 'value': {'stringValue': recipe['title']}},
                                {'name': 'servings', 'value': {'longValue': recipe['servings']}},
                                {'name': 'ingredients', 'value': {'stringValue': json.dumps(recipe['ingredients'])}},
                                {'name': 'steps', 'value': {'stringValue': json.dumps(recipe['steps'])}},
                                {'name': 'tags', 'value': {'stringValue': json.dumps(recipe['tags'])}},
                                {'name': 'substitutions', 'value': {'stringValue': json.dumps(recipe.get('substitutions', []))}},
                                {'name': 'warnings', 'value': {'stringValue': json.dumps(recipe.get('warnings', []))}},
                                {'name': 'nutrition', 'value': {'stringValue': json.dumps(nutrition)}}
                            ]
                        )
                    except Exception as db_error:
                        logger.warning(f"Failed to store recipe {recipe_id}: {db_error}")
                
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'recipe_ids': recipe_ids,
                        'recipes': [{'id': recipe_ids[i], 'title': recipe['title'], 'tags': recipe['tags']} 
                                   for i, recipe in enumerate(recipe_options)],
                        'servings': servings,
                        'message': f'{len(recipe_options)} fallback recipe options created successfully',
                        'note': 'Generated with common ingredients due to scan processing issues'
                    })
                }
            
            current_status = scan_response['records'][0][0]['stringValue']
            if current_status != 'confirmed':
                return {
                    'statusCode': 409,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'error': f'Scan status is {current_status}, must be confirmed to create recipe'
                    })
                }
                
        except Exception as validation_error:
            logger.error(f"Error validating scan: {str(validation_error)}")
            raise
        
        # Get confirmed items
        try:
            # First, let's see ALL items for this scan (for debugging)
            all_items_response = rds_client.execute_statement(
                resourceArn=db_cluster_arn,
                secretArn=db_secret_arn,
                database='ayeaye',
                sql="""
                    SELECT label, fdc_id, grams, confirmed
                    FROM scan_items 
                    WHERE scan_id::text = :scan_id
                    ORDER BY grams DESC
                """,
                parameters=[
                    {'name': 'scan_id', 'value': {'stringValue': scan_id}}
                ]
            )
            
            logger.info(f"DEBUG: All items in scan {scan_id}:")
            for record in all_items_response.get('records', []):
                try:
                    label = record[0]['stringValue']
                    confirmed = record[3]['booleanValue'] if len(record) > 3 and record[3] else 'unknown'
                    logger.info(f"  - {label}: confirmed={confirmed}")
                except Exception as debug_error:
                    logger.warning(f"Error parsing record: {record}, error: {debug_error}")
                    logger.info(f"  - Raw record: {record}")
            
            # Now get only confirmed items
            items_response = rds_client.execute_statement(
                resourceArn=db_cluster_arn,
                secretArn=db_secret_arn,
                database='ayeaye',
                sql="""
                    SELECT label, fdc_id, grams
                    FROM scan_items 
                    WHERE scan_id::text = :scan_id AND confirmed = true
                    ORDER BY grams DESC
                """,
                parameters=[
                    {'name': 'scan_id', 'value': {'stringValue': scan_id}}
                ]
            )
            
            if not items_response['records']:
                logger.warning(f"No confirmed items found for scan {scan_id}, using fallback ingredients")
                
                # Use fallback ingredients instead of failing
                items = [
                    {"label": "paneer", "grams": 200, "fdc_id": "123456"},
                    {"label": "spinach", "grams": 150, "fdc_id": "789012"},
                    {"label": "tomato", "grams": 100, "fdc_id": "345678"}
                ]
                fdc_ids = [item['fdc_id'] for item in items]
                
                logger.info("Using fallback ingredients due to no confirmed items")
            else:
            
                items = []
                fdc_ids = []
                
                for record in items_response['records']:
                    item = {
                        'label': record[0]['stringValue'],
                        'fdc_id': record[1]['stringValue'],
                        'grams': record[2]['doubleValue']
                    }
                    items.append(item)
                    fdc_ids.append(item['fdc_id'])
            
            logger.info(f"Found {len(items)} confirmed items")
            for item in items:
                logger.info(f"  - {item['label']}: {item['grams']}g (FDC: {item['fdc_id']})")
            
        except Exception as items_error:
            logger.error(f"Error getting confirmed items: {str(items_error)}")
            raise
        
        # Fetch nutrition data from USDA (optional)
        try:
            api_key = get_usda_api_key()
            nutrition_facts = fetch_usda_nutrients(fdc_ids, api_key)
            logger.info(f"Successfully fetched nutrition data for {len(nutrition_facts)} items")
        except Exception as nutrition_error:
            logger.warning(f"Could not fetch USDA nutrition data: {nutrition_error}")
            nutrition_facts = {}
        
        # Compute nutrition totals (with fallback for missing data)
        nutrition = compute_nutrition(items, nutrition_facts, servings)
        
        # Log the actual ingredients we're working with
        ingredient_names = [item['label'] for item in items]
        logger.info(f"Creating recipes for ingredients: {ingredient_names}")
        
        # Generate cuisine-specific recipe options
        try:
            logger.info(f"Generating {cuisine_preference} recipes for confirmed ingredients")
            recipe_options = generate_simple_cuisine_recipes(items, nutrition, servings, cuisine_preference)
            logger.info(f"Generated {len(recipe_options)} recipe options for {cuisine_preference} cuisine:")
            for i, recipe in enumerate(recipe_options):
                logger.info(f"  {i+1}. {recipe['title']} ({recipe.get('difficulty', 'medium')} difficulty)")
                
            if not recipe_options:
                return {
                    'statusCode': 503,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'error': 'Recipe generation failed',
                        'message': 'AI could not generate recipes for the provided ingredients. Please try again or contact support.',
                        'ingredients': ingredient_names
                    })
                }
        except Exception as recipe_error:
            logger.error(f"Recipe generation failed: {str(recipe_error)}")
            return {
                'statusCode': 503,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Recipe generation failed',
                    'message': f'AI recipe generation error: {str(recipe_error)}',
                    'ingredients': ingredient_names
                })
            }
        
        # Store all recipes in database
        recipe_ids = []
        try:
            # Begin transaction
            rds_client.execute_statement(
                resourceArn=db_cluster_arn,
                secretArn=db_secret_arn,
                database='ayeaye',
                sql="BEGIN"
            )
            
            # Insert each recipe option
            for i, recipe_json in enumerate(recipe_options):
                recipe_id = str(uuid.uuid4())
                recipe_ids.append(recipe_id)
                
                rds_client.execute_statement(
                    resourceArn=db_cluster_arn,
                    secretArn=db_secret_arn,
                    database='ayeaye',
                    sql=f"""
                        INSERT INTO recipes (id, user_id, scan_id, title, json_payload, nutrition, facts_snapshot, created_at)
                        VALUES (
                            '{recipe_id}'::uuid,
                            '{user_id}'::uuid,
                            '{scan_id}'::uuid,
                            '{recipe_json['title'].replace("'", "''")}',
                            '{json.dumps(recipe_json).replace("'", "''")}'::jsonb,
                            '{json.dumps(nutrition).replace("'", "''")}'::jsonb,
                            '{json.dumps(nutrition_facts).replace("'", "''")}'::jsonb,
                            NOW()
                        )
                    """
                )
            
            # Update scan status to completed
            rds_client.execute_statement(
                resourceArn=db_cluster_arn,
                secretArn=db_secret_arn,
                database='ayeaye',
                sql="""
                    UPDATE scans 
                    SET status = 'completed'
                    WHERE id::text = :scan_id AND user_id::text = :user_id
                """,
                parameters=[
                    {'name': 'scan_id', 'value': {'stringValue': scan_id}},
                    {'name': 'user_id', 'value': {'stringValue': user_id}}
                ]
            )
            
            # Commit transaction
            rds_client.execute_statement(
                resourceArn=db_cluster_arn,
                secretArn=db_secret_arn,
                database='ayeaye',
                sql="COMMIT"
            )
            
            logger.info(f"Successfully created recipe {recipe_id}")
            
        except Exception as db_error:
            # Rollback transaction
            try:
                rds_client.execute_statement(
                    resourceArn=db_cluster_arn,
                    secretArn=db_secret_arn,
                    database='ayeaye',
                    sql="ROLLBACK"
                )
            except:
                pass
            
            logger.error(f"Database error creating recipe: {str(db_error)}")
            raise
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'recipe_ids': recipe_ids,
                'recipes': [{'id': recipe_ids[i], 'title': recipe['title'], 'tags': recipe['tags']} 
                           for i, recipe in enumerate(recipe_options)],
                'servings': servings,
                'message': f'{len(recipe_options)} recipe options created successfully'
            })
        }
        
    except Exception as e:
        logger.error(f"Error creating recipe: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error'
            })
        }

def parse_titan_text_response(response_text: str, ingredients_data: List[Dict], nutrition: Dict, servings: int) -> List[Dict[str, Any]]:
    """Parse Titan's text response to extract recipe information"""
    recipes = []
    
    try:
        # Split response into recipe sections
        lines = response_text.split('\n')
        current_recipe = None
        current_steps = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for recipe titles
            if line.startswith('Title:'):
                if current_recipe:
                    # Save previous recipe
                    current_recipe['steps'] = current_steps
                    recipes.append(current_recipe)
                
                # Start new recipe
                title = line.replace('Title:', '').strip()
                current_recipe = {
                    'title': title,
                    'cooking_method': 'mixed',
                    'estimated_time': '30 minutes',
                    'difficulty': 'medium',
                    'cuisine': 'International',
                    'tags': ['ai-generated'],
                    'substitutions': ['Adjust seasonings to taste'],
                    'warnings': ['Cook to safe temperatures']
                }
                current_steps = []
                
            elif line.startswith('Method:'):
                if current_recipe:
                    method = line.replace('Method:', '').strip()
                    current_recipe['cooking_method'] = method
                    if method not in current_recipe['tags']:
                        current_recipe['tags'].append(method)
                        
            elif line.startswith('Time:'):
                if current_recipe:
                    current_recipe['estimated_time'] = line.replace('Time:', '').strip()
                    
            elif line.startswith(('Steps:', 'Recipe')):
                continue  # Skip section headers
                
            elif line and (line[0].isdigit() or line.startswith(('•', '-', '*'))):
                # This is a step
                step_text = line
                if line[0].isdigit() and '.' in line:
                    step_text = line.split('.', 1)[1].strip()
                current_steps.append(step_text)
        
        # Don't forget the last recipe
        if current_recipe:
            current_recipe['steps'] = current_steps
            recipes.append(current_recipe)
        
        # Format recipes with ingredients
        formatted_recipes = []
        for recipe in recipes[:3]:  # Limit to 3 recipes
            formatted_recipe = format_ai_recipe(recipe, ingredients_data, nutrition, servings)
            formatted_recipes.append(formatted_recipe)
        
        return formatted_recipes
        
    except Exception as e:
        logger.error(f"Error parsing Titan response: {e}")
        return []

def generate_cuisine_specific_steps(ingredients, cuisine_type, cooking_method="sautéed"):
    """Generate detailed, cuisine-specific cooking steps dynamically"""
    
    # Cuisine-specific profiles
    cuisine_profiles = {
        "indian": {
            "cooking_fat": "2-3 tablespoons ghee or oil",
            "base_spices": ["cumin seeds", "turmeric", "coriander powder", "garam masala"],
            "aromatics": "1 finely chopped onion and 1 tbsp ginger-garlic paste",
            "finishing": "2 tbsp cream and fresh coriander",
            "accompaniments": "basmati rice, naan, or roti"
        },
        "mediterranean": {
            "cooking_fat": "3 tablespoons extra virgin olive oil",
            "base_spices": ["oregano", "basil", "thyme"],
            "aromatics": "3 cloves minced garlic and 1 sliced onion",
            "finishing": "fresh lemon juice and chopped herbs",
            "accompaniments": "crusty bread, pasta, or rice"
        },
        "asian": {
            "cooking_fat": "2 tablespoons vegetable oil",
            "base_spices": ["ginger", "garlic", "soy sauce"],
            "aromatics": "2 tbsp minced ginger and garlic",
            "finishing": "sesame oil and scallions",
            "accompaniments": "steamed rice or noodles"
        }
    }
    
    profile = cuisine_profiles.get(cuisine_type.lower(), cuisine_profiles["mediterranean"])
    main_ingredient = ingredients[0]["name"] if ingredients else "main ingredient"
    
    steps = []
    
    # Dynamic step generation based on cuisine
    if cuisine_type.lower() == "indian":
        steps = [
            f"Prepare ingredients: Wash and cut {main_ingredient} into appropriate pieces. Pat dry if needed.",
            f"Heat {profile['cooking_fat']} in a heavy-bottomed pan over medium heat. Add 1 tsp cumin seeds and let splutter for 30 seconds until fragrant.",
            f"Add {profile['aromatics']} and cook for 5-6 minutes until onions are golden brown and ginger-garlic paste is fragrant.",
            f"Add 1/2 tsp turmeric, 1 tsp coriander powder, and 1/2 tsp red chili powder. Cook for 30 seconds until spices are aromatic.",
            f"Add {main_ingredient} and cook gently for 3-4 minutes until lightly golden. Handle carefully to prevent breaking.",
            "Add remaining vegetables and cook for 5-7 minutes until tender. If using leafy greens, add them last.",
            "Add 1/2 cup water if needed and bring to a gentle simmer. Cover and cook for 10-12 minutes until flavors meld.",
            "Add 1/2 tsp garam masala and mix gently. Taste and adjust salt and spices as needed.",
            f"Finish with {profile['finishing']}. Let rest for 2 minutes to allow flavors to develop.",
            f"Serve hot with {profile['accompaniments']}. Garnish with fresh coriander and lemon wedges."
        ]
    
    elif cuisine_type.lower() == "mediterranean":
        steps = [
            f"Prepare all ingredients: Wash and cut {main_ingredient} and vegetables into uniform pieces for even cooking.",
            f"Heat {profile['cooking_fat']} in a large skillet over medium heat until shimmering but not smoking.",
            f"Add {profile['aromatics']} and sauté for 2-3 minutes until garlic is fragrant and onions are translucent.",
            f"Season with salt, freshly ground black pepper, 1 tsp oregano, and 1/2 tsp dried basil.",
            f"Add {main_ingredient} and cook for 4-6 minutes until golden brown and cooked through.",
            "Add remaining vegetables and cook for 8-10 minutes until tender and lightly caramelized.",
            "Deglaze with 1/4 cup white wine or broth if desired. Let reduce for 1-2 minutes.",
            "Simmer for 5-7 minutes until sauce thickens slightly and flavors concentrate.",
            f"Remove from heat and stir in {profile['finishing']}. Taste and adjust seasoning.",
            f"Serve immediately with {profile['accompaniments']}. Drizzle with extra virgin olive oil before serving."
        ]
    
    elif cuisine_type.lower() == "asian":
        steps = [
            f"Prepare ingredients: Cut {main_ingredient} into bite-sized pieces. Have all ingredients ready for quick cooking.",
            f"Heat {profile['cooking_fat']} in a wok or large skillet over high heat until smoking.",
            f"Add {profile['aromatics']} and stir-fry for 30 seconds until very fragrant.",
            f"Add {main_ingredient} and stir-fry for 2-3 minutes until seared and nearly cooked through.",
            "Add harder vegetables first, then softer ones. Stir-fry constantly for 3-4 minutes.",
            "Add 2 tbsp soy sauce, 1 tsp sesame oil, and a pinch of sugar. Toss to combine.",
            "Continue stir-frying for 2-3 minutes until vegetables are crisp-tender and well-coated.",
            "Taste and adjust seasoning with more soy sauce or a splash of rice vinegar if needed.",
            f"Remove from heat and garnish with {profile['finishing']}.",
            f"Serve immediately over {profile['accompaniments']} while hot and crispy."
        ]
    
    return steps

def generate_cuisine_specific_tips(cuisine_type):
    """Generate cooking tips specific to the cuisine"""
    tips = {
        "indian": [
            "Toast whole spices for 30 seconds before grinding for maximum flavor",
            "Cook onions until golden brown - this is the flavor base",
            "Add salt in layers throughout cooking for better flavor distribution",
            "Let the dish rest for 5 minutes after cooking to allow flavors to meld"
        ],
        "mediterranean": [
            "Use high-quality extra virgin olive oil for the best flavor",
            "Don't overcook garlic - it should be fragrant, not browned",
            "Fresh herbs added at the end provide the brightest flavor",
            "A splash of good wine can elevate the entire dish"
        ],
        "asian": [
            "Have all ingredients prepped before you start cooking",
            "Keep the heat high for proper wok hei (breath of the wok)",
            "Don't overcrowd the pan - cook in batches if needed",
            "Serve immediately while vegetables are still crisp"
        ]
    }
    return tips.get(cuisine_type.lower(), tips["mediterranean"])

def get_cuisine_appropriate_fallback_ingredients(cuisine: str) -> List[Dict[str, Any]]:
    """Generate cuisine-appropriate fallback ingredients when scan data is unavailable"""
    
    cuisine_fallbacks = {
        'italian': [
            {"label": "tomato", "grams": 200, "fdc_id": "321456"},
            {"label": "basil", "grams": 50, "fdc_id": "654321"},
            {"label": "mozzarella", "grams": 150, "fdc_id": "987654"}
        ],
        'mediterranean': [
            {"label": "olive oil", "grams": 50, "fdc_id": "111222"},
            {"label": "lemon", "grams": 100, "fdc_id": "333444"},
            {"label": "chicken", "grams": 300, "fdc_id": "555666"}
        ],
        'mexican': [
            {"label": "black beans", "grams": 200, "fdc_id": "777888"},
            {"label": "bell pepper", "grams": 150, "fdc_id": "999000"},
            {"label": "lime", "grams": 50, "fdc_id": "111333"}
        ],
        'asian': [
            {"label": "tofu", "grams": 200, "fdc_id": "222444"},
            {"label": "soy sauce", "grams": 30, "fdc_id": "555777"},
            {"label": "ginger", "grams": 50, "fdc_id": "888999"}
        ],
        'french': [
            {"label": "butter", "grams": 100, "fdc_id": "123789"},
            {"label": "herbs", "grams": 30, "fdc_id": "456012"},
            {"label": "wine", "grams": 100, "fdc_id": "789345"}
        ],
        'american': [
            {"label": "ground beef", "grams": 250, "fdc_id": "147258"},
            {"label": "cheese", "grams": 100, "fdc_id": "369147"},
            {"label": "potato", "grams": 200, "fdc_id": "258369"}
        ],
        'indian': [
            {"label": "paneer", "grams": 200, "fdc_id": "123456"},
            {"label": "spinach", "grams": 150, "fdc_id": "789012"},
            {"label": "onion", "grams": 100, "fdc_id": "345678"}
        ],
        'thai': [
            {"label": "shrimp", "grams": 250, "fdc_id": "thai001"},
            {"label": "coconut milk", "grams": 200, "fdc_id": "thai002"},
            {"label": "lime", "grams": 50, "fdc_id": "thai003"}
        ]
    }
    
    # Get cuisine-specific fallback or default to Italian
    fallback = cuisine_fallbacks.get(cuisine.lower(), cuisine_fallbacks['italian'])
    
    logger.info(f"Using {cuisine} fallback ingredients: {[item['label'] for item in fallback]}")
    return fallback

def generate_intelligent_recipe_names(ingredients: List[str], cuisine: str) -> List[Dict[str, str]]:
    """Generate intelligent recipe names based on actual ingredients and cuisine"""
    
    # Analyze ingredients to create smart combinations
    ingredient_set = set([ing.lower() for ing in ingredients])
    
    # Filter out common base ingredients for cleaner naming
    main_ingredients = [ing for ing in ingredients if ing.lower() not in ['onion', 'garlic', 'ginger', 'oil', 'salt', 'pepper']]
    primary_ingredient = main_ingredients[0] if main_ingredients else ingredients[0] if ingredients else "ingredient"
    secondary_ingredients = main_ingredients[1:3] if len(main_ingredients) > 1 else []
    
    # Special ingredient combinations for different cuisines
    recipe_templates = []
    
    if cuisine.lower() == 'indian':
        # Indian cuisine-specific combinations with enhanced naming
        if 'paneer' in ingredient_set and 'spinach' in ingredient_set:
            recipe_templates = [
                {'title': 'Palak Paneer (Traditional Spinach Cottage Cheese Curry)', 'method': 'curry', 'time': '30 minutes'},
                {'title': 'Restaurant-Style Creamy Spinach Paneer', 'method': 'grilled', 'time': '25 minutes'},
                {'title': 'Punjabi Palak Paneer with Fresh Cream', 'method': 'scrambled', 'time': '20 minutes'}
            ]
        elif 'paneer' in ingredient_set and 'tomato' in ingredient_set:
            recipe_templates = [
                {'title': 'Paneer Makhani (Rich Butter Paneer Curry)', 'method': 'curry', 'time': '35 minutes'},
                {'title': 'Paneer Tikka Masala with Tomato Gravy', 'method': 'grilled', 'time': '30 minutes'},
                {'title': 'Spiced Tomato Paneer Bhurji', 'method': 'scrambled', 'time': '20 minutes'}
            ]
        elif 'chicken' in ingredient_set:
            other_ingredients = [ing.title() for ing in ingredients if ing.lower() not in ['chicken', 'onion', 'garlic', 'ginger']][:2]
            recipe_templates = [
                {'title': f'Chicken Curry with {" & ".join(other_ingredients) if other_ingredients else "Aromatic Spices"}', 'method': 'curry', 'time': '40 minutes'},
                {'title': f'Tandoori Chicken with {other_ingredients[0] if other_ingredients else "Traditional Spices"}', 'method': 'grilled', 'time': '35 minutes'},
                {'title': f'Chicken Biryani with {other_ingredients[0] if other_ingredients else "Basmati Rice"}', 'method': 'rice', 'time': '50 minutes'}
            ]
        elif any(dal in ingredient_set for dal in ['dal', 'lentil', 'lentils']):
            other_ingredients = [ing.title() for ing in ingredients if not any(dal_word in ing.lower() for dal_word in ['dal', 'lentil'])][:2]
            recipe_templates = [
                {'title': f'Dal Tadka with {" & ".join(other_ingredients) if other_ingredients else "Tempered Spices"}', 'method': 'curry', 'time': '35 minutes'},
                {'title': f'South Indian Sambar with {other_ingredients[0] if other_ingredients else "Vegetables"}', 'method': 'soup', 'time': '40 minutes'},
                {'title': f'Punjabi Dal Fry with {other_ingredients[0] if other_ingredients else "Caramelized Onions"}', 'method': 'fried', 'time': '30 minutes'}
            ]
        elif 'potato' in ingredient_set or 'aloo' in ingredient_set:
            other_ingredients = [ing.title() for ing in ingredients if ing.lower() not in ['potato', 'aloo', 'onion', 'garlic']][:2]
            recipe_templates = [
                {'title': f'Aloo {other_ingredients[0] if other_ingredients else "Masala"} (Spiced Potato Curry)', 'method': 'curry', 'time': '25 minutes'},
                {'title': f'Bombay Aloo with {other_ingredients[0] if other_ingredients else "Cumin & Turmeric"}', 'method': 'stir-fry', 'time': '20 minutes'},
                {'title': f'Jeera Aloo with {" & ".join(other_ingredients) if other_ingredients else "Fresh Coriander"}', 'method': 'roasted', 'time': '30 minutes'}
            ]
        elif 'cauliflower' in ingredient_set or 'gobi' in ingredient_set:
            other_ingredients = [ing.title() for ing in ingredients if ing.lower() not in ['cauliflower', 'gobi', 'onion']][:2]
            recipe_templates = [
                {'title': f'Gobi {other_ingredients[0] if other_ingredients else "Masala"} (Spiced Cauliflower)', 'method': 'curry', 'time': '25 minutes'},
                {'title': f'Aloo Gobi with {other_ingredients[0] if other_ingredients else "Turmeric & Garam Masala"}', 'method': 'stir-fry', 'time': '30 minutes'},
                {'title': f'Tandoori Gobi with {other_ingredients[0] if other_ingredients else "Yogurt Marinade"}', 'method': 'grilled', 'time': '35 minutes'}
            ]
        else:
            # Generic Indian recipes with enhanced naming based on primary ingredients
            recipe_templates = [
                {'title': f'{primary_ingredient.title()} Curry with {secondary_ingredients[0].title() if secondary_ingredients else "Traditional Spices"}', 'method': 'curry', 'time': '30 minutes'},
                {'title': f'Spiced {primary_ingredient.title()} Sabzi with {secondary_ingredients[0].title() if secondary_ingredients else "Cumin & Coriander"}', 'method': 'stir-fry', 'time': '20 minutes'},
                {'title': f'Masala {primary_ingredient.title()} with {" & ".join([ing.title() for ing in secondary_ingredients[:2]]) if secondary_ingredients else "Garam Masala"}', 'method': 'spiced', 'time': '25 minutes'}
            ]
    
    elif cuisine.lower() == 'italian':
        if 'tomato' in ingredient_set and 'basil' in ingredient_set:
            other_ingredients = [ing.title() for ing in ingredients if ing.lower() not in ['tomato', 'basil', 'olive oil', 'garlic']][:2]
            recipe_templates = [
                {'title': f'Classic Margherita with {other_ingredients[0] if other_ingredients else "Fresh Mozzarella"}', 'method': 'pizza', 'time': '25 minutes'},
                {'title': f'Caprese Salad with {" & ".join(other_ingredients) if other_ingredients else "Balsamic Glaze"}', 'method': 'fresh', 'time': '10 minutes'},
                {'title': f'Pomodoro Pasta with {other_ingredients[0] if other_ingredients else "Fresh Basil"}', 'method': 'pasta', 'time': '20 minutes'}
            ]
        elif 'pasta' in ingredient_set or 'spaghetti' in ingredient_set:
            pasta_type = next((pasta.title() for pasta in ['spaghetti', 'penne', 'fettuccine', 'pasta'] if pasta in ingredient_set), 'Pasta')
            other_ingredients = [ing.title() for ing in ingredients if not any(p in ing.lower() for p in ['pasta', 'spaghetti', 'penne', 'fettuccine'])][:2]
            recipe_templates = [
                {'title': f'{pasta_type} Carbonara with {other_ingredients[0] if other_ingredients else "Pancetta & Parmesan"}', 'method': 'pasta', 'time': '20 minutes'},
                {'title': f'{pasta_type} Arrabbiata with {other_ingredients[0] if other_ingredients else "Spicy Tomato Sauce"}', 'method': 'pasta', 'time': '25 minutes'},
                {'title': f'{pasta_type} Puttanesca with {" & ".join(other_ingredients[:2]) if other_ingredients else "Olives & Capers"}', 'method': 'pasta', 'time': '30 minutes'}
            ]
        elif 'chicken' in ingredient_set:
            other_ingredients = [ing.title() for ing in ingredients if ing.lower() not in ['chicken', 'olive oil', 'garlic']][:2]
            recipe_templates = [
                {'title': f'Chicken Parmigiana with {other_ingredients[0] if other_ingredients else "Marinara & Mozzarella"}', 'method': 'baked', 'time': '35 minutes'},
                {'title': f'Pollo alla Cacciatora with {other_ingredients[0] if other_ingredients else "Tomatoes & Herbs"}', 'method': 'braised', 'time': '40 minutes'},
                {'title': f'Italian Herb Chicken with {" & ".join(other_ingredients) if other_ingredients else "Rosemary & Lemon"}', 'method': 'roasted', 'time': '45 minutes'}
            ]
        elif any(cheese in ingredient_set for cheese in ['mozzarella', 'parmesan', 'ricotta']):
            cheese_type = next((cheese.title() for cheese in ['mozzarella', 'parmesan', 'ricotta'] if cheese in ingredient_set), 'Cheese')
            other_ingredients = [ing.title() for ing in ingredients if not any(c in ing.lower() for c in ['mozzarella', 'parmesan', 'ricotta'])][:2]
            recipe_templates = [
                {'title': f'Italian {cheese_type} & {other_ingredients[0] if other_ingredients else "Tomato"} Bake', 'method': 'baked', 'time': '30 minutes'},
                {'title': f'{cheese_type} Stuffed {other_ingredients[0] if other_ingredients else "Zucchini"} Italian Style', 'method': 'stuffed', 'time': '35 minutes'},
                {'title': f'Creamy {cheese_type} Risotto with {other_ingredients[0] if other_ingredients else "Mushrooms"}', 'method': 'risotto', 'time': '40 minutes'}
            ]
        else:
            recipe_templates = [
                {'title': f'Italian {primary_ingredient.title()} with {secondary_ingredients[0].title() if secondary_ingredients else "Herbs & Olive Oil"}', 'method': 'sautéed', 'time': '25 minutes'},
                {'title': f'Tuscan {primary_ingredient.title()} & {secondary_ingredients[0].title() if secondary_ingredients else "White Beans"}', 'method': 'braised', 'time': '35 minutes'},
                {'title': f'Roman-Style {primary_ingredient.title()} with {" & ".join([ing.title() for ing in secondary_ingredients[:2]]) if secondary_ingredients else "Garlic & Parsley"}', 'method': 'roasted', 'time': '30 minutes'}
            ]
    
    elif cuisine.lower() == 'mediterranean':
        if 'chicken' in ingredient_set:
            other_ingredients = [ing.title() for ing in ingredients if ing.lower() not in ['chicken', 'olive oil', 'garlic', 'onion']][:2]
            recipe_templates = [
                {'title': f'Mediterranean Chicken with {" & ".join(other_ingredients) if other_ingredients else "Lemon & Herbs"}', 'method': 'grilled', 'time': '30 minutes'},
                {'title': f'Greek-Style Chicken with {other_ingredients[0] if other_ingredients else "Oregano & Feta"}', 'method': 'baked', 'time': '35 minutes'},
                {'title': f'Tuscan Herb Chicken with {other_ingredients[0] if other_ingredients else "Sun-Dried Tomatoes"}', 'method': 'roasted', 'time': '40 minutes'}
            ]
        elif any(fish in ingredient_set for fish in ['fish', 'salmon', 'tuna', 'cod']):
            fish_type = next((fish.title() for fish in ['salmon', 'tuna', 'cod', 'fish'] if fish in ingredient_set), 'Fish')
            other_ingredients = [ing.title() for ing in ingredients if ing.lower() not in ['fish', 'salmon', 'tuna', 'cod', 'olive oil']][:2]
            recipe_templates = [
                {'title': f'Mediterranean {fish_type} with {" & ".join(other_ingredients) if other_ingredients else "Lemon & Capers"}', 'method': 'grilled', 'time': '25 minutes'},
                {'title': f'Herb-Crusted {fish_type} with {other_ingredients[0] if other_ingredients else "Roasted Vegetables"}', 'method': 'baked', 'time': '30 minutes'},
                {'title': f'Pan-Seared {fish_type} with {other_ingredients[0] if other_ingredients else "Olive Tapenade"}', 'method': 'pan-seared', 'time': '20 minutes'}
            ]
        elif 'tomato' in ingredient_set:
            other_ingredients = [ing.title() for ing in ingredients if ing.lower() not in ['tomato', 'olive oil', 'garlic']][:2]
            recipe_templates = [
                {'title': f'Mediterranean Tomato & {other_ingredients[0] if other_ingredients else "Basil"} Salad', 'method': 'fresh', 'time': '15 minutes'},
                {'title': f'Roasted Tomato with {" & ".join(other_ingredients) if other_ingredients else "Fresh Mozzarella"}', 'method': 'roasted', 'time': '25 minutes'},
                {'title': f'Tuscan Tomato & {other_ingredients[0] if other_ingredients else "White Bean"} Stew', 'method': 'braised', 'time': '35 minutes'}
            ]
        else:
            recipe_templates = [
                {'title': f'Mediterranean {primary_ingredient.title()} with {secondary_ingredients[0].title() if secondary_ingredients else "Herbs & Olive Oil"}', 'method': 'grilled', 'time': '25 minutes'},
                {'title': f'Greek-Style {primary_ingredient.title()} & {secondary_ingredients[0].title() if secondary_ingredients else "Feta"} Bowl', 'method': 'fresh', 'time': '15 minutes'},
                {'title': f'Roasted {primary_ingredient.title()} with {" & ".join([ing.title() for ing in secondary_ingredients[:2]]) if secondary_ingredients else "Balsamic Glaze"}', 'method': 'roasted', 'time': '35 minutes'}
            ]
    
    elif cuisine.lower() == 'asian':
        if 'chicken' in ingredient_set:
            other_ingredients = [ing.title() for ing in ingredients if ing.lower() not in ['chicken', 'soy sauce', 'ginger', 'garlic']][:2]
            recipe_templates = [
                {'title': f'Asian {other_ingredients[0] if other_ingredients else "Vegetable"} Chicken Stir-Fry', 'method': 'stir-fry', 'time': '20 minutes'},
                {'title': f'Teriyaki Chicken with {other_ingredients[0] if other_ingredients else "Steamed Broccoli"}', 'method': 'glazed', 'time': '25 minutes'},
                {'title': f'Ginger Soy Chicken & {other_ingredients[0] if other_ingredients else "Snow Peas"}', 'method': 'wok', 'time': '18 minutes'}
            ]
        elif 'tofu' in ingredient_set:
            other_ingredients = [ing.title() for ing in ingredients if ing.lower() not in ['tofu', 'soy sauce', 'ginger']][:2]
            recipe_templates = [
                {'title': f'Crispy Tofu with {" & ".join(other_ingredients) if other_ingredients else "Asian Vegetables"}', 'method': 'stir-fry', 'time': '22 minutes'},
                {'title': f'Mapo Tofu with {other_ingredients[0] if other_ingredients else "Sichuan Peppercorns"}', 'method': 'braised', 'time': '25 minutes'},
                {'title': f'Sweet & Sour Tofu with {other_ingredients[0] if other_ingredients else "Bell Peppers"}', 'method': 'wok', 'time': '20 minutes'}
            ]
        elif any(noodle in ingredient_set for noodle in ['noodles', 'ramen', 'udon']):
            noodle_type = next((noodle.title() for noodle in ['ramen', 'udon', 'noodles'] if noodle in ingredient_set), 'Noodles')
            other_ingredients = [ing.title() for ing in ingredients if not any(n in ing.lower() for n in ['noodles', 'ramen', 'udon'])][:2]
            recipe_templates = [
                {'title': f'{noodle_type} Stir-Fry with {" & ".join(other_ingredients) if other_ingredients else "Mixed Vegetables"}', 'method': 'stir-fry', 'time': '15 minutes'},
                {'title': f'Asian {noodle_type} Soup with {other_ingredients[0] if other_ingredients else "Bok Choy"}', 'method': 'soup', 'time': '25 minutes'},
                {'title': f'Spicy {noodle_type} with {other_ingredients[0] if other_ingredients else "Chili Oil"}', 'method': 'tossed', 'time': '12 minutes'}
            ]
        else:
            recipe_templates = [
                {'title': f'Asian {primary_ingredient.title()} Stir-Fry with {secondary_ingredients[0].title() if secondary_ingredients else "Ginger & Soy"}', 'method': 'stir-fry', 'time': '18 minutes'},
                {'title': f'Sweet & Sour {primary_ingredient.title()} with {secondary_ingredients[0].title() if secondary_ingredients else "Pineapple"}', 'method': 'wok', 'time': '22 minutes'},
                {'title': f'Szechuan {primary_ingredient.title()} with {" & ".join([ing.title() for ing in secondary_ingredients[:2]]) if secondary_ingredients else "Chili Garlic Sauce"}', 'method': 'spicy', 'time': '20 minutes'}
            ]
    
    elif cuisine.lower() == 'mexican':
        if 'chicken' in ingredient_set:
            other_ingredients = [ing.title() for ing in ingredients if ing.lower() not in ['chicken', 'onion', 'garlic']][:2]
            recipe_templates = [
                {'title': f'Mexican Chicken with {" & ".join(other_ingredients) if other_ingredients else "Peppers & Lime"}', 'method': 'grilled', 'time': '25 minutes'},
                {'title': f'Pollo a la Mexicana with {other_ingredients[0] if other_ingredients else "Jalapeños"}', 'method': 'sautéed', 'time': '30 minutes'},
                {'title': f'Chicken Fajitas with {other_ingredients[0] if other_ingredients else "Bell Peppers"}', 'method': 'grilled', 'time': '20 minutes'}
            ]
        elif any(bean in ingredient_set for bean in ['beans', 'black beans', 'pinto beans']):
            bean_type = next((bean.replace(' beans', '').title() + ' Beans' for bean in ['black beans', 'pinto beans', 'beans'] if bean in ingredient_set), 'Beans')
            other_ingredients = [ing.title() for ing in ingredients if 'bean' not in ing.lower()][:2]
            recipe_templates = [
                {'title': f'Mexican {bean_type} with {" & ".join(other_ingredients) if other_ingredients else "Cumin & Cilantro"}', 'method': 'stewed', 'time': '35 minutes'},
                {'title': f'Refried {bean_type} with {other_ingredients[0] if other_ingredients else "Chipotle"}', 'method': 'mashed', 'time': '25 minutes'},
                {'title': f'{bean_type} & {other_ingredients[0] if other_ingredients else "Rice"} Bowl', 'method': 'bowl', 'time': '20 minutes'}
            ]
        else:
            recipe_templates = [
                {'title': f'Mexican {primary_ingredient.title()} with {secondary_ingredients[0].title() if secondary_ingredients else "Lime & Cilantro"}', 'method': 'grilled', 'time': '25 minutes'},
                {'title': f'Spicy {primary_ingredient.title()} Tacos with {secondary_ingredients[0].title() if secondary_ingredients else "Avocado"}', 'method': 'tacos', 'time': '20 minutes'},
                {'title': f'{primary_ingredient.title()} Burrito Bowl with {" & ".join([ing.title() for ing in secondary_ingredients[:2]]) if secondary_ingredients else "Black Beans & Rice"}', 'method': 'bowl', 'time': '15 minutes'}
            ]
    
    elif cuisine.lower() == 'thai':
        if 'shrimp' in ingredient_set or 'prawns' in ingredient_set:
            seafood_type = 'Shrimp' if 'shrimp' in ingredient_set else 'Prawns'
            other_ingredients = [ing.title() for ing in ingredients if ing.lower() not in ['shrimp', 'prawns', 'coconut milk']][:2]
            recipe_templates = [
                {'title': f'Thai {seafood_type} Curry with {other_ingredients[0] if other_ingredients else "Coconut Milk"}', 'method': 'curry', 'time': '25 minutes'},
                {'title': f'Pad Thai with {seafood_type} & {other_ingredients[0] if other_ingredients else "Bean Sprouts"}', 'method': 'stir-fry', 'time': '20 minutes'},
                {'title': f'Tom Yum {seafood_type} Soup with {other_ingredients[0] if other_ingredients else "Lemongrass"}', 'method': 'soup', 'time': '30 minutes'}
            ]
        elif 'chicken' in ingredient_set:
            other_ingredients = [ing.title() for ing in ingredients if ing.lower() not in ['chicken', 'coconut milk']][:2]
            recipe_templates = [
                {'title': f'Thai Green Curry Chicken with {other_ingredients[0] if other_ingredients else "Thai Basil"}', 'method': 'curry', 'time': '30 minutes'},
                {'title': f'Pad Kra Pao Chicken with {other_ingredients[0] if other_ingredients else "Holy Basil"}', 'method': 'stir-fry', 'time': '15 minutes'},
                {'title': f'Thai Chicken Satay with {other_ingredients[0] if other_ingredients else "Peanut Sauce"}', 'method': 'grilled', 'time': '25 minutes'}
            ]
        elif any(noodle in ingredient_set for noodle in ['noodles', 'rice noodles']):
            noodle_type = 'Rice Noodles' if 'rice noodles' in ingredient_set else 'Noodles'
            other_ingredients = [ing.title() for ing in ingredients if 'noodle' not in ing.lower()][:2]
            recipe_templates = [
                {'title': f'Pad Thai {noodle_type} with {" & ".join(other_ingredients) if other_ingredients else "Tamarind & Fish Sauce"}', 'method': 'stir-fry', 'time': '20 minutes'},
                {'title': f'Thai Drunken {noodle_type} with {other_ingredients[0] if other_ingredients else "Thai Chilies"}', 'method': 'wok', 'time': '18 minutes'},
                {'title': f'Thai {noodle_type} Soup with {other_ingredients[0] if other_ingredients else "Coconut Broth"}', 'method': 'soup', 'time': '25 minutes'}
            ]
        else:
            recipe_templates = [
                {'title': f'Thai {primary_ingredient.title()} Curry with {secondary_ingredients[0].title() if secondary_ingredients else "Coconut Milk"}', 'method': 'curry', 'time': '25 minutes'},
                {'title': f'Thai Basil {primary_ingredient.title()} Stir-Fry', 'method': 'stir-fry', 'time': '15 minutes'},
                {'title': f'Thai {primary_ingredient.title()} Salad with {secondary_ingredients[0].title() if secondary_ingredients else "Lime Dressing"}', 'method': 'salad', 'time': '10 minutes'}
            ]
    
    else:
        # International/fusion recipes with enhanced naming
        recipe_templates = [
            {'title': f'Pan-Seared {primary_ingredient.title()} with {secondary_ingredients[0].title() if secondary_ingredients else "Herb Butter"}', 'method': 'seared', 'time': '20 minutes'},
            {'title': f'Roasted {primary_ingredient.title()} & {secondary_ingredients[0].title() if secondary_ingredients else "Seasonal Vegetables"}', 'method': 'roasted', 'time': '35 minutes'},
            {'title': f'Fresh {primary_ingredient.title()} Salad with {" & ".join([ing.title() for ing in secondary_ingredients[:2]]) if secondary_ingredients else "Lemon Vinaigrette"}', 'method': 'fresh', 'time': '15 minutes'}
        ]
    
    # Ensure we always have at least 3 recipe options
    while len(recipe_templates) < 3:
        recipe_templates.append({
            'title': f'Simple {primary_ingredient.title()} with {secondary_ingredients[0].title() if secondary_ingredients else "Herbs"}',
            'method': 'simple',
            'time': '25 minutes'
        })
    
    return recipe_templates[:3]  # Return exactly 3 recipe options

def generate_simple_cuisine_recipes(items: List[Dict], nutrition: Dict, servings: int, cuisine: str) -> List[Dict[str, Any]]:
    """Generate simple cuisine-specific recipes that work reliably"""
    
    ingredient_names = [item.get('label', item.get('name', 'ingredient')) for item in items]
    primary_ingredient = ingredient_names[0] if ingredient_names else "ingredient"
    
    logger.info(f"generate_simple_cuisine_recipes called with cuisine: '{cuisine}', ingredients: {ingredient_names}")
    
    # Ensure cuisine is lowercase for consistent comparison
    cuisine = cuisine.lower().strip()
    logger.info(f"Normalized cuisine to: '{cuisine}'")
    
    # Generate intelligent recipe names based on actual ingredients
    recipe_templates = generate_intelligent_recipe_names(ingredient_names, cuisine)
    
    # Create ingredient list with our format
    formatted_ingredients = []
    for ingredient in items:
        formatted_ingredients.append({
            'name': ingredient.get('label', ingredient.get('name', 'ingredient')),
            'grams': ingredient.get('grams', 100),
            'notes': 'prepared as needed',
            'fdc_id': ingredient.get('fdc_id', '')
        })
    
    recipes = []
    
    # Generate recipes using intelligent naming
    for i, template in enumerate(recipe_templates):
        if cuisine.lower() == 'indian':
            # Generate Indian-style cooking steps based on the recipe method
            if template['method'] == 'curry':
                steps = [
                    'Heat 2-3 tablespoons ghee or oil in a heavy-bottomed pan over medium heat',
                    'Add 1 teaspoon cumin seeds and let them splutter for 30 seconds until fragrant',
                    'Add 1 finely chopped onion and sauté for 5-6 minutes until golden brown',
                    'Add 1 tablespoon ginger-garlic paste and cook for 1 minute until aromatic',
                    'Add 1/2 teaspoon turmeric, 1 teaspoon coriander powder, and 1/2 teaspoon red chili powder',
                    'Cook the spices for 30 seconds until fragrant, being careful not to burn them',
                    f'Add the {", ".join(ingredient_names[:2])} and cook gently for 3-4 minutes',
                    'Add remaining ingredients and cook for 5-7 minutes until tender',
                    'Add 1/2 cup water if needed and bring to a gentle simmer',
                    'Cover and cook for 10-12 minutes until flavors meld together',
                    'Add 1/2 teaspoon garam masala and mix gently',
                    'Finish with 2 tablespoons fresh cream and chopped coriander, serve with basmati rice or naan'
                ]
                tags = ['indian', 'curry', 'authentic', 'comfort-food']
            elif template['method'] == 'stir-fry':
                steps = [
                    'Heat 2 tablespoons oil in a large wok or skillet over high heat',
                    'Add 1/2 teaspoon mustard seeds and let them pop for 15 seconds',
                    'Add curry leaves and dried red chilies, fry for 10 seconds',
                    f'Add {primary_ingredient} and stir-fry for 3-4 minutes until lightly browned',
                    'Add remaining vegetables and stir-fry for 5-6 minutes',
                    'Sprinkle 1/2 teaspoon turmeric and 1 teaspoon coriander powder',
                    'Add salt to taste and mix well',
                    'Cook for 2-3 more minutes until vegetables are tender but still crisp',
                    'Garnish with fresh coriander and serve hot with rice'
                ]
                tags = ['indian', 'quick', 'spiced', 'healthy']
            else:
                steps = [
                    'Heat oil in a pan over medium heat',
                    f'Add {", ".join(ingredient_names[:2])} and cook for 5 minutes',
                    'Add Indian spices (turmeric, coriander, cumin)',
                    'Cook until tender and well-spiced',
                    'Garnish with coriander and serve with rice'
                ]
                tags = ['indian', 'traditional', 'spiced']
        
        elif cuisine.lower() == 'italian':
            if template['method'] == 'pasta':
                steps = [
                    'Bring a large pot of salted water to a rolling boil',
                    'Add pasta and cook according to package directions until al dente',
                    'Meanwhile, heat 3 tablespoons extra virgin olive oil in a large pan',
                    'Add 3 cloves minced garlic and cook for 30 seconds until fragrant',
                    f'Add {", ".join(ingredient_names[:2])} and cook for 3-4 minutes',
                    'Add 1/2 cup pasta cooking water to create a silky sauce',
                    'Drain pasta and add to the pan with sauce',
                    'Toss vigorously for 1-2 minutes to combine',
                    'Remove from heat and add freshly grated Parmesan cheese',
                    'Finish with fresh herbs and a drizzle of olive oil',
                    'Serve immediately in warmed bowls'
                ]
                tags = ['italian', 'pasta', 'authentic', 'comfort-food']
            elif template['method'] == 'pizza':
                steps = [
                    'Preheat oven to 475°F (245°C) with pizza stone if available',
                    'Roll out pizza dough on a floured surface to desired thickness',
                    'Brush dough lightly with extra virgin olive oil',
                    'Spread a thin layer of tomato sauce, leaving 1-inch border',
                    f'Add {", ".join(ingredient_names[:2])} evenly over the sauce',
                    'Sprinkle with fresh mozzarella cheese',
                    'Season with salt, pepper, and dried oregano',
                    'Bake for 12-15 minutes until crust is golden and cheese bubbles',
                    'Remove from oven and let cool for 2-3 minutes',
                    'Garnish with fresh basil leaves and drizzle with olive oil',
                    'Slice and serve immediately while hot'
                ]
                tags = ['italian', 'pizza', 'baked', 'family-style']
            elif template['method'] == 'risotto':
                steps = [
                    'Heat 6 cups chicken or vegetable broth in a saucepan and keep warm',
                    'Heat 2 tablespoons olive oil and 1 tablespoon butter in a heavy pan',
                    'Add 1 finely chopped onion and cook until translucent',
                    'Add 1 1/2 cups Arborio rice and stir for 2 minutes until coated',
                    'Add 1/2 cup white wine and stir until absorbed',
                    f'Add {", ".join(ingredient_names[:2])} and mix gently',
                    'Add warm broth one ladle at a time, stirring constantly',
                    'Continue adding broth and stirring for 18-20 minutes',
                    'Rice should be creamy but still have a slight bite',
                    'Stir in butter and freshly grated Parmesan cheese',
                    'Season with salt and pepper, serve immediately'
                ]
                tags = ['italian', 'risotto', 'creamy', 'elegant']
            elif template['method'] == 'baked':
                steps = [
                    'Preheat oven to 375°F (190°C) and lightly grease a baking dish',
                    'Heat 2 tablespoons olive oil in a large oven-safe skillet',
                    'Season ingredients with salt, pepper, and Italian herbs',
                    f'Sear {primary_ingredient} for 2-3 minutes on each side until golden',
                    f'Add {", ".join(ingredient_names[1:3]) if len(ingredient_names) > 1 else "vegetables"} around the main ingredient',
                    'Drizzle with extra virgin olive oil and add minced garlic',
                    'Transfer skillet to preheated oven',
                    'Bake for 20-25 minutes until cooked through and golden',
                    'Remove from oven and let rest for 5 minutes',
                    'Garnish with fresh basil and grated Parmesan cheese',
                    'Serve hot with crusty Italian bread'
                ]
                tags = ['italian', 'baked', 'oven', 'golden']
            elif template['method'] == 'braised':
                steps = [
                    'Heat 3 tablespoons olive oil in a heavy Dutch oven over medium-high heat',
                    f'Season {primary_ingredient} with salt and pepper, then brown on all sides',
                    'Remove and set aside, leaving oil in the pot',
                    'Add diced onions, carrots, and celery, cook for 5 minutes until softened',
                    'Add 4 cloves minced garlic and cook for 1 minute until fragrant',
                    'Add 1 cup white wine and scrape up any browned bits',
                    f'Return {primary_ingredient} to pot and add remaining ingredients',
                    'Add enough broth to partially cover, bring to a simmer',
                    'Cover and braise in 325°F oven for 1.5-2 hours until tender',
                    'Check occasionally and add more liquid if needed',
                    'Finish with fresh herbs and serve with polenta or pasta'
                ]
                tags = ['italian', 'braised', 'slow-cooked', 'tender']
            elif template['method'] == 'roasted':
                steps = [
                    'Preheat oven to 425°F (220°C) and line a baking sheet with parchment',
                    f'Pat {primary_ingredient} dry and season generously with salt and pepper',
                    'Rub with 2 tablespoons olive oil and Italian seasoning',
                    'Add minced garlic, fresh rosemary, and lemon zest',
                    f'Arrange {", ".join(ingredient_names)} on the prepared baking sheet',
                    'Drizzle vegetables with olive oil and season with salt',
                    'Roast for 25-30 minutes until golden and cooked through',
                    'Turn once halfway through cooking for even browning',
                    'Check for doneness with a meat thermometer if needed',
                    'Let rest for 5 minutes, then squeeze fresh lemon juice over all',
                    'Serve with roasted vegetables and a drizzle of good olive oil'
                ]
                tags = ['italian', 'roasted', 'crispy', 'herbs']
            elif template['method'] == 'fresh':
                steps = [
                    'Wash and prepare all fresh ingredients carefully',
                    f'Slice {primary_ingredient} into attractive, even pieces',
                    'Arrange ingredients beautifully on a large serving platter',
                    'Drizzle with the finest extra virgin olive oil you have',
                    'Add a splash of aged balsamic vinegar for depth',
                    'Season lightly with sea salt and freshly cracked black pepper',
                    'Scatter fresh basil leaves or other herbs over the top',
                    'Let sit at room temperature for 10 minutes to develop flavors',
                    'Taste and adjust seasoning with more salt or acid as needed',
                    'Serve immediately with crusty bread and perhaps some fresh mozzarella',
                    'Enjoy this celebration of simple, quality ingredients'
                ]
                tags = ['italian', 'fresh', 'no-cook', 'simple']
            elif template['method'] == 'stuffed':
                steps = [
                    'Preheat oven to 350°F (175°C) and prepare a baking dish',
                    f'Carefully hollow out or prepare {primary_ingredient} for stuffing',
                    'Heat 2 tablespoons olive oil in a large skillet over medium heat',
                    'Sauté onions and garlic until fragrant and translucent',
                    'Add remaining filling ingredients and cook until just tender',
                    'Season the filling with Italian herbs, salt, and pepper',
                    'Mix in breadcrumbs and grated Parmesan cheese for binding',
                    f'Carefully stuff the prepared {primary_ingredient} with the mixture',
                    'Place in baking dish and drizzle with olive oil',
                    'Cover with foil and bake for 30-40 minutes until tender',
                    'Remove foil for last 10 minutes to brown the top',
                    'Serve hot with a simple tomato sauce or pesto'
                ]
                tags = ['italian', 'stuffed', 'baked', 'comfort']
            else:
                steps = [
                    'Heat 3 tablespoons extra virgin olive oil in a large pan',
                    'Add 2 cloves minced garlic and cook for 30 seconds',
                    f'Add {", ".join(ingredient_names[:2])} and cook for 5-6 minutes',
                    'Season with salt, pepper, and Italian herbs',
                    'Add remaining ingredients and cook until tender',
                    'Finish with fresh lemon juice and chopped parsley',
                    'Serve with crusty Italian bread or over pasta'
                ]
                tags = ['italian', 'simple', 'fresh', 'herbs']
        
        elif cuisine.lower() == 'mediterranean':
            steps = [
                'Heat 3 tablespoons extra virgin olive oil in a large skillet over medium heat',
                'Add 3 cloves minced garlic and cook for 30 seconds until fragrant',
                'Add 1 sliced onion and cook for 3-4 minutes until translucent',
                f'Add {", ".join(ingredient_names[:2])} and cook for 4-6 minutes until golden',
                'Season with salt, freshly ground black pepper, and dried oregano',
                'Add remaining ingredients and cook for 8-10 minutes until tender',
                'Add 1/4 cup white wine or broth and let it reduce for 2 minutes',
                'Stir in fresh lemon juice and chopped fresh herbs (basil, parsley)',
                'Remove from heat and drizzle with extra virgin olive oil',
                'Serve with crusty bread, pasta, or over rice'
            ]
            tags = ['mediterranean', 'healthy', 'fresh', 'herbs']
        
        elif cuisine.lower() == 'asian':
            steps = [
                'Heat 2 tablespoons oil in a wok over high heat until smoking',
                'Add minced ginger and garlic, stir-fry for 30 seconds',
                f'Add {primary_ingredient} and stir-fry for 2-3 minutes until seared',
                'Add remaining vegetables and stir-fry for 3-4 minutes',
                'Add 2 tablespoons soy sauce and 1 teaspoon sesame oil',
                'Toss everything together for 1-2 minutes',
                'Garnish with scallions and sesame seeds',
                'Serve immediately over steamed rice or noodles'
            ]
            tags = ['asian', 'stir-fry', 'quick', 'wok-hei']
        
        elif cuisine.lower() == 'thai':
            if template['method'] == 'curry':
                steps = [
                    'Heat 2 tablespoons coconut oil in a large pan over medium heat',
                    'Add 2-3 tablespoons Thai curry paste and fry for 1-2 minutes until fragrant',
                    'Add 1 can coconut milk gradually, stirring to combine with paste',
                    f'Add {", ".join(ingredient_names[:2])} and bring to a gentle simmer',
                    'Add Thai fish sauce, palm sugar, and lime leaves for authentic flavor',
                    'Simmer for 10-15 minutes until ingredients are cooked through',
                    'Taste and adjust seasoning with more fish sauce or lime juice',
                    'Garnish with fresh Thai basil and sliced chilies',
                    'Serve hot with jasmine rice',
                    'Finish with a squeeze of fresh lime juice'
                ]
                tags = ['thai', 'curry', 'coconut', 'spicy']
            elif template['method'] == 'stir-fry':
                steps = [
                    'Heat 2 tablespoons oil in a wok over high heat until smoking',
                    'Add 3-4 cloves minced garlic and 2 Thai chilies, stir-fry for 30 seconds',
                    f'Add {primary_ingredient} and stir-fry for 2-3 minutes until seared',
                    'Add remaining vegetables and stir-fry for 2-3 minutes',
                    'Add 2 tablespoons fish sauce, 1 tablespoon oyster sauce, and 1 tsp sugar',
                    'Toss everything together for 1-2 minutes until well coated',
                    'Add fresh Thai basil leaves and toss briefly until wilted',
                    'Remove from heat and squeeze fresh lime juice over the dish',
                    'Serve immediately over jasmine rice',
                    'Garnish with sliced chilies and lime wedges'
                ]
                tags = ['thai', 'stir-fry', 'spicy', 'basil']
            elif template['method'] == 'soup':
                steps = [
                    'Bring 4 cups chicken or vegetable broth to a boil in a large pot',
                    'Add 2 stalks lemongrass (bruised), 4 kaffir lime leaves, and 3 Thai chilies',
                    'Add 3 tablespoons fish sauce and 2 tablespoons lime juice',
                    f'Add {", ".join(ingredient_names[:2])} and simmer for 8-10 minutes',
                    'Add mushrooms and tomatoes, cook for 3-4 minutes',
                    'Taste and adjust with more fish sauce, lime juice, or chilies',
                    'Remove lemongrass stalks before serving',
                    'Garnish with fresh cilantro and Thai basil',
                    'Serve hot with steamed rice on the side',
                    'Provide extra lime wedges and chilies for individual seasoning'
                ]
                tags = ['thai', 'soup', 'sour', 'aromatic']
            else:
                steps = [
                    'Heat oil in a large pan over medium-high heat',
                    'Add garlic, chilies, and aromatics, cook for 1 minute',
                    f'Add {", ".join(ingredient_names[:2])} and cook for 5-6 minutes',
                    'Season with fish sauce, lime juice, and palm sugar',
                    'Add fresh herbs and toss to combine',
                    'Serve with jasmine rice and lime wedges'
                ]
                tags = ['thai', 'fresh', 'aromatic', 'spicy']
        
        else:
            steps = [
                'Heat oil in a large pan over medium heat',
                f'Add {primary_ingredient} and cook for 5 minutes',
                'Add remaining ingredients and season with salt and pepper',
                'Cook for 10-15 minutes until tender',
                'Taste and adjust seasoning',
                'Serve hot'
            ]
            tags = ['simple', 'quick', 'healthy']
        
        recipe = {
            'title': template['title'],
            'servings': servings,
            'estimated_time': template['time'],
            'difficulty': 'medium' if template['method'] in ['curry', 'braised'] else 'easy',
            'cuisine': cuisine.title(),
            'tags': tags,
            'ingredients': formatted_ingredients,
            'steps': steps,
            'substitutions': [f'Substitute {ingredient_names[0]} with similar ingredients', 'Adjust spices to taste'],
            'warnings': ['Cook to safe temperatures', 'Taste and adjust seasoning as needed']
        }
        recipes.append(recipe)

    
    logger.info(f"Generated {len(recipes)} {cuisine} recipes")
    return recipes

def generate_basic_fallback_recipes(items: List[Dict], nutrition: Dict, servings: int) -> List[Dict[str, Any]]:
    """Generate basic fallback recipes when everything else fails"""
    
    ingredient_names = [item.get('label', item.get('name', 'ingredient')) for item in items]
    primary_ingredient = ingredient_names[0] if ingredient_names else "ingredient"
    
    formatted_ingredients = []
    for ingredient in items:
        formatted_ingredients.append({
            'name': ingredient.get('label', ingredient.get('name', 'ingredient')),
            'grams': ingredient.get('grams', 100),
            'notes': 'prepared as needed',
            'fdc_id': ingredient.get('fdc_id', '')
        })
    
    recipes = [
        {
            'title': f'Simple {primary_ingredient.title()} Dish',
            'servings': servings,
            'estimated_time': '20 minutes',
            'difficulty': 'easy',
            'cuisine': 'International',
            'tags': ['simple', 'quick'],
            'ingredients': formatted_ingredients,
            'steps': [
                'Heat 2 tablespoons oil in a large pan',
                f'Add {primary_ingredient} and cook for 5 minutes',
                'Add remaining ingredients',
                'Cook for 10-15 minutes until tender',
                'Season with salt and pepper',
                'Serve hot'
            ],
            'substitutions': ['Use any cooking oil', 'Add herbs for flavor'],
            'warnings': ['Cook to safe temperatures']
        }
    ]
    
    return recipes

def generate_enhanced_recipes(items: List[Dict], nutrition: Dict, servings: int, cuisine: str, skill_level: str, dietary_restrictions: List[str], user_id: str) -> List[Dict[str, Any]]:
    """Generate enhanced recipes with cuisine-specific details"""
    try:
        # Try AI generation first with cuisine context
        ai_recipes = generate_ai_recipes_with_cuisine(items, nutrition, servings, cuisine, user_id)
        if ai_recipes and len(ai_recipes) > 0:
            # Enhance AI recipes with skill level and dietary adaptations
            enhanced_recipes = []
            for recipe in ai_recipes:
                enhanced_recipe = enhance_recipe_with_preferences(recipe, cuisine, skill_level, dietary_restrictions)
                enhanced_recipes.append(enhanced_recipe)
            return enhanced_recipes
    except Exception as e:
        logger.warning(f"AI recipe generation failed: {e}")
    
    # Fallback to enhanced static recipes
    return generate_enhanced_fallback_recipes(items, nutrition, servings, cuisine, skill_level, dietary_restrictions)

def generate_ai_recipes_with_cuisine(items: List[Dict], nutrition: Dict, servings: int, cuisine: str, user_id: str) -> List[Dict[str, Any]]:
    """Generate AI recipes with specific cuisine context"""
    try:
        # Get Bedrock Agent ID from environment
        agent_id = os.environ.get('BEDROCK_AGENT_ID')
        if not agent_id:
            logger.warning("No Bedrock Agent ID configured")
            return []
        
        # Prepare ingredients data for AI with cuisine context
        ingredients_data = []
        for item in items:
            ingredients_data.append({
                'name': item.get('label', 'Unknown ingredient'),
                'grams': float(item.get('grams', 100)),
                'fdc_id': item.get('fdc_id', '')
            })
        
        ingredient_names = [item['name'] for item in ingredients_data]
        
        # Create cuisine-specific prompt
        cuisine_prompts = {
            "indian": f"""Create 3 authentic Indian recipes using: {", ".join(ingredient_names)}.

RECIPE NAMING REQUIREMENTS:
- Create descriptive titles that include cuisine + main ingredients + cooking style
- Examples: "Traditional Palak Paneer (Spinach Cottage Cheese Curry)", "Punjabi Aloo Gobi with Cumin & Turmeric", "Restaurant-Style Chicken Tikka Masala"
- Include regional styles (Punjabi, South Indian, Bengali) when appropriate
- Use authentic Indian dish names when possible (Palak Paneer, Aloo Gobi, Dal Tadka)

COOKING REQUIREMENTS:
- Use traditional Indian cooking techniques (tempering/tadka, slow cooking, layering spices)
- Include authentic spice combinations (cumin, coriander, turmeric, garam masala)
- Provide 10-12 detailed steps with specific temperatures and timing
- Include traditional accompaniments (basmati rice, naan, roti)

SPECIAL INGREDIENT COMBINATIONS:
- Paneer + Spinach = "Palak Paneer (Traditional Spinach Cottage Cheese Curry)"
- Paneer + Tomato = "Paneer Makhani (Rich Butter Paneer Curry)"
- Potato + Cauliflower = "Aloo Gobi (Spiced Potato & Cauliflower)"
- Use ghee or oil for cooking, ginger-garlic paste as base, finish with cream and coriander

Generate detailed, professional Indian recipes with authentic names and techniques.""",

            "mediterranean": f"""Create 3 authentic Mediterranean recipes using: {", ".join(ingredient_names)}.

RECIPE NAMING REQUIREMENTS:
- Create descriptive titles that include cuisine + main ingredients + cooking method
- Examples: "Mediterranean Herb-Crusted Chicken with Lemon", "Greek-Style Roasted Vegetables with Feta", "Tuscan Tomato & Basil Pasta"
- Include regional styles (Greek, Italian, Spanish) when appropriate
- Emphasize fresh herbs, olive oil, and cooking methods in titles

COOKING REQUIREMENTS:
- Use Mediterranean cooking techniques (sautéing, grilling, roasting, braising)
- Include classic ingredients (extra virgin olive oil, garlic, fresh herbs, lemon)
- Provide 10-12 detailed steps with specific temperatures and timing
- Include traditional accompaniments (crusty bread, pasta, rice pilaf)

SPECIAL FOCUS:
- Use extra virgin olive oil as primary cooking fat
- Include fresh herbs (basil, oregano, thyme, parsley)
- Finish with lemon juice, fresh herbs, and quality olive oil
- Emphasize simple, clean flavors that highlight ingredients

Generate detailed, professional Mediterranean recipes with regional authenticity.""",

            "asian": f"""Create 3 authentic Asian recipes using: {", ".join(ingredient_names)}.

RECIPE NAMING REQUIREMENTS:
- Create descriptive titles that include cuisine + main ingredients + cooking technique
- Examples: "Szechuan Mapo Tofu with Silken Texture", "Cantonese Ginger Soy Chicken Stir-Fry", "Korean-Style Spicy Vegetable Bibimbap"
- Include regional styles (Chinese, Japanese, Korean, Thai) when appropriate
- Emphasize cooking techniques (stir-fry, steamed, braised) in titles

COOKING REQUIREMENTS:
- Use Asian cooking techniques (stir-frying, steaming, quick high-heat cooking)
- Include classic seasonings (soy sauce, fresh ginger, garlic, sesame oil)
- Provide 10-12 detailed steps emphasizing high-heat, quick cooking methods
- Include traditional accompaniments (steamed rice, noodles, pickled vegetables)

SPECIAL FOCUS:
- High-heat wok cooking for maximum flavor (wok hei)
- Quick cooking times to preserve texture and nutrients
- Fresh ginger and garlic as aromatics
- Finish with sesame oil, scallions, and fresh herbs

Generate detailed, professional Asian recipes with authentic regional techniques.""",

            "mexican": f"""Create 3 authentic Mexican recipes using: {", ".join(ingredient_names)}.

RECIPE NAMING REQUIREMENTS:
- Create descriptive titles that include cuisine + main ingredients + preparation style
- Examples: "Pollo a la Mexicana with Jalapeños & Tomatoes", "Traditional Refried Black Beans with Chipotle", "Mexican Street Corn Salad with Lime & Cotija"
- Include regional styles (Oaxacan, Yucatecan, Northern Mexican) when appropriate
- Use Spanish names when authentic (Pollo a la Mexicana, Frijoles Refritos)

COOKING REQUIREMENTS:
- Use traditional Mexican cooking techniques (charring, slow braising, quick sautéing)
- Include classic seasonings (cumin, chili powder, lime, cilantro, garlic)
- Provide 10-12 detailed steps with proper heat management
- Include traditional accompaniments (rice, beans, tortillas, lime wedges)

SPECIAL FOCUS:
- Build layers of flavor with chiles, onions, and garlic
- Use fresh lime juice and cilantro as finishing touches
- Include traditional cooking methods (comal, molcajete techniques)
- Balance heat, acid, and fresh herbs

Generate detailed, professional Mexican recipes with authentic regional flavors.""",

            "italian": f"""Create 3 authentic Italian recipes using: {", ".join(ingredient_names)}.

RECIPE NAMING REQUIREMENTS:
- Create descriptive titles that include cuisine + main ingredients + preparation style
- Examples: "Classic Spaghetti Carbonara with Pancetta", "Margherita Pizza with Fresh Basil", "Osso Buco alla Milanese with Gremolata"
- Include regional styles (Tuscan, Roman, Sicilian, Milanese) when appropriate
- Use authentic Italian dish names (Carbonara, Puttanesca, Cacio e Pepe, Risotto)

COOKING REQUIREMENTS:
- Use traditional Italian cooking techniques (pasta al dente, risotto stirring, pizza stone baking)
- Include classic ingredients (extra virgin olive oil, San Marzano tomatoes, Parmigiano-Reggiano)
- Provide 10-12 detailed steps with proper Italian techniques
- Include traditional accompaniments (crusty bread, wine pairings, fresh herbs)

SPECIAL INGREDIENT COMBINATIONS:
- Tomato + Basil + Mozzarella = "Classic Margherita Pizza with Fresh Basil"
- Pasta + Eggs + Pancetta = "Traditional Spaghetti Carbonara"
- Arborio Rice + Broth = "Creamy Risotto Milanese"
- Use high-quality olive oil, finish with fresh herbs and Parmesan

SPECIAL FOCUS:
- Emphasize simplicity and quality of ingredients
- Use proper pasta cooking techniques (al dente, pasta water for sauce)
- Include traditional Italian cooking methods (soffritto, mantecatura)
- Balance flavors with herbs, cheese, and acidity

Generate detailed, professional Italian recipes with regional authenticity.""",

            "thai": f"""Create 3 authentic Thai recipes using: {", ".join(ingredient_names)}.

RECIPE NAMING REQUIREMENTS:
- Create descriptive titles that include Thai cuisine + main ingredients + cooking style
- Examples: "Thai Green Curry with Shrimp", "Pad Thai with Fresh Shrimp", "Tom Yum Shrimp Soup"
- Include authentic Thai dish names (Pad Thai, Tom Yum, Green Curry, Pad Kra Pao)
- Emphasize key Thai flavors (coconut, lime, fish sauce, chilies) in titles

COOKING REQUIREMENTS:
- Use traditional Thai cooking techniques (wok stir-frying, curry paste frying, balance of flavors)
- Include authentic Thai ingredients (fish sauce, coconut milk, lime leaves, Thai basil, palm sugar)
- Provide 10-12 detailed steps with proper Thai cooking methods
- Include traditional accompaniments (jasmine rice, lime wedges, fresh herbs)

SPECIAL INGREDIENT COMBINATIONS:
- Shrimp + Coconut Milk = "Thai Shrimp Curry with Coconut Milk"
- Shrimp + Noodles = "Pad Thai with Fresh Shrimp"
- Shrimp + Lemongrass = "Tom Yum Shrimp Soup"
- Use coconut oil for curries, high heat for stir-fries, balance sweet-sour-salty-spicy

SPECIAL FOCUS:
- Balance the four fundamental Thai flavors: sweet, sour, salty, spicy
- Use fresh aromatics (lemongrass, galangal, lime leaves, Thai chilies)
- Include proper curry paste preparation and coconut milk techniques
- Finish with fresh herbs (Thai basil, cilantro) and lime juice

Generate detailed, professional Thai recipes with authentic flavors and techniques."""
        }
        
        prompt = cuisine_prompts.get(cuisine.lower(), cuisine_prompts["indian"])
        
        # Call Bedrock Agent
        bedrock_agent_client = boto3.client('bedrock-agent-runtime')
        session_id = f"cuisine_recipe_{user_id}_{uuid.uuid4().hex[:8]}"
        
        response = bedrock_agent_client.invoke_agent(
            agentId=agent_id,
            agentAliasId='TSTALIASID',
            sessionId=session_id,
            inputText=prompt
        )
        
        # Parse response
        response_text = ""
        if 'completion' in response:
            for event in response['completion']:
                if 'chunk' in event and 'bytes' in event['chunk']:
                    chunk_text = event['chunk']['bytes'].decode('utf-8')
                    response_text += chunk_text
        
        # Extract recipes from response
        if response_text:
            return extract_recipes_from_text(response_text, ingredients_data)
        
        return []
        
    except Exception as e:
        logger.error(f"Error in AI recipe generation with cuisine: {e}")
        return []

def enhance_recipe_with_preferences(recipe: Dict, cuisine: str, skill_level: str, dietary_restrictions: List[str]) -> Dict[str, Any]:
    """Enhance recipe based on user preferences"""
    
    # Adapt steps based on skill level
    if skill_level == "beginner":
        # Add more detailed explanations
        enhanced_steps = []
        for step in recipe.get('steps', []):
            if "heat" in step.lower() and "oil" in step.lower():
                enhanced_steps.append(f"🔥 {step} (You'll know the oil is ready when it shimmers but doesn't smoke - about 2 minutes)")
            elif "cook" in step.lower() and "golden" in step.lower():
                enhanced_steps.append(f"👀 {step} (Look for a golden brown color and sweet aroma - this usually takes 5-6 minutes)")
            else:
                enhanced_steps.append(f"📝 {step}")
        recipe['steps'] = enhanced_steps
        recipe['skill_level'] = 'beginner'
        recipe['tags'].append('beginner-friendly')
    
    # Adapt for dietary restrictions
    if dietary_restrictions:
        adapted_steps = []
        adapted_substitutions = recipe.get('substitutions', [])
        
        for step in recipe.get('steps', []):
            adapted_step = step
            
            if "vegan" in dietary_restrictions:
                adapted_step = adapted_step.replace("ghee", "coconut oil")
                adapted_step = adapted_step.replace("cream", "coconut cream")
                adapted_step = adapted_step.replace("paneer", "firm tofu")
                if "coconut oil" in adapted_step and "coconut oil" not in step:
                    adapted_substitutions.append("Using coconut oil instead of ghee for vegan option")
            
            if "gluten-free" in dietary_restrictions:
                adapted_step = adapted_step.replace("naan", "rice")
                adapted_step = adapted_step.replace("bread", "gluten-free bread")
                if "rice" in adapted_step and "naan" in step:
                    adapted_substitutions.append("Serving with rice instead of naan for gluten-free option")
            
            adapted_steps.append(adapted_step)
        
        recipe['steps'] = adapted_steps
        recipe['substitutions'] = adapted_substitutions
        recipe['dietary_adaptations'] = dietary_restrictions
        recipe['tags'].extend([f"{restriction}-friendly" for restriction in dietary_restrictions])
    
    return recipe

def generate_enhanced_fallback_recipes(ingredients_data: List[Dict], nutrition: Dict, servings: int, cuisine: str, skill_level: str, dietary_restrictions: List[str]) -> List[Dict[str, Any]]:
    """Generate enhanced fallback recipes with user preferences"""
    
    ingredient_names = [item['name'] for item in ingredients_data]
    primary_ingredient = ingredient_names[0] if ingredient_names else "ingredient"
    
    # Create ingredient list with our format
    formatted_ingredients = []
    for ingredient in ingredients_data:
        formatted_ingredients.append({
            'name': ingredient['name'],
            'grams': ingredient['grams'],
            'notes': get_ingredient_notes(ingredient['name']),
            'fdc_id': ingredient.get('fdc_id', '')
        })
    
    # Generate recipes based on selected cuisine or multiple cuisines
    if cuisine and cuisine.lower() in ["indian", "mediterranean", "asian"]:
        cuisines_to_generate = [cuisine.lower()]
    else:
        cuisines_to_generate = ["indian", "mediterranean", "asian"]
    
    recipes = []
    
    for cuisine_type in cuisines_to_generate:
        # Generate detailed steps for this cuisine
        steps = generate_cuisine_specific_steps(ingredients_data, cuisine_type)
        tips = generate_cuisine_specific_tips(cuisine_type)
        
        # Create base recipe
        recipe = {
            'title': f'{cuisine_type.title()} Style {primary_ingredient.title()}',
            'servings': servings,
            'estimated_time': '25-30 minutes',
            'difficulty': 'medium',
            'cuisine': cuisine_type.title(),
            'tags': [cuisine_type, 'detailed-steps', 'authentic'],
            'ingredients': formatted_ingredients,
            'steps': steps,
            'substitutions': tips[:2],
            'warnings': tips[2:] if len(tips) > 2 else [],
            'cooking_tips': tips
        }
        
        # Enhance recipe with user preferences
        enhanced_recipe = enhance_recipe_with_preferences(recipe, cuisine_type, skill_level, dietary_restrictions)
        recipes.append(enhanced_recipe)
        
        # If user selected specific cuisine, generate 3 variations
        if len(cuisines_to_generate) == 1:
            # Generate 2 more variations with different cooking methods
            cooking_methods = ["grilled", "baked"]
            for method in cooking_methods:
                variation_steps = generate_cuisine_specific_steps(ingredients_data, cuisine_type, method)
                variation_recipe = {
                    'title': f'{method.title()} {cuisine_type.title()} {primary_ingredient.title()}',
                    'servings': servings,
                    'estimated_time': '30-35 minutes' if method == 'baked' else '20-25 minutes',
                    'difficulty': 'medium',
                    'cuisine': cuisine_type.title(),
                    'tags': [cuisine_type, method, 'detailed-steps'],
                    'ingredients': formatted_ingredients,
                    'steps': variation_steps,
                    'substitutions': tips[:2],
                    'warnings': tips[2:] if len(tips) > 2 else [],
                    'cooking_tips': tips,
                    'cooking_method': method
                }
                enhanced_variation = enhance_recipe_with_preferences(variation_recipe, cuisine_type, skill_level, dietary_restrictions)
                recipes.append(enhanced_variation)
            break  # Only generate variations for the selected cuisine
    
    logger.info(f"Generated {len(recipes)} enhanced fallback recipes for {cuisine} cuisine")
    return recipes