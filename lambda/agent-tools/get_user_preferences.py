import json
import boto3
import os
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

rds_client = boto3.client('rds-data')

def handler(event, context):
    """
    Agent tool: Get user preferences for personalized recipe generation
    """
    try:
        # Parse input from Bedrock Agent
        input_data = json.loads(event.get('inputText', '{}'))
        user_id = input_data.get('user_id')
        
        if not user_id:
            # Return default preferences if no user_id
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'diets': [],
                    'cuisines': [],
                    'allergens': [],
                    'cooking_skill': 'intermediate',
                    'time_preference': 'moderate',
                    'default_servings': 2
                })
            }
        
        logger.info(f"Getting preferences for user: {user_id}")
        
        # Database connection info
        db_secret_arn = os.environ['DB_SECRET_ARN']
        db_cluster_arn = os.environ['DB_CLUSTER_ARN']
        
        # Get user preferences from database
        try:
            user_response = rds_client.execute_statement(
                resourceArn=db_cluster_arn,
                secretArn=db_secret_arn,
                database='ayeaye',
                sql="""
                    SELECT diets, cuisines, allergens
                    FROM users 
                    WHERE id = :user_id::uuid
                """,
                parameters=[
                    {'name': 'user_id', 'value': {'stringValue': user_id}}
                ]
            )
            
            if user_response['records']:
                record = user_response['records'][0]
                
                # Parse arrays from database
                diets = []
                cuisines = []
                allergens = []
                
                if record[0] and 'stringValue' in record[0]:
                    diets_str = record[0]['stringValue']
                    if diets_str and diets_str != '{}':
                        diets = diets_str.strip('{}').split(',') if diets_str.strip('{}') else []
                
                if record[1] and 'stringValue' in record[1]:
                    cuisines_str = record[1]['stringValue']
                    if cuisines_str and cuisines_str != '{}':
                        cuisines = cuisines_str.strip('{}').split(',') if cuisines_str.strip('{}') else []
                
                if record[2] and 'stringValue' in record[2]:
                    allergens_str = record[2]['stringValue']
                    if allergens_str and allergens_str != '{}':
                        allergens = allergens_str.strip('{}').split(',') if allergens_str.strip('{}') else []
                
                preferences = {
                    'diets': [d.strip().strip('"') for d in diets if d.strip()],
                    'cuisines': [c.strip().strip('"') for c in cuisines if c.strip()],
                    'allergens': [a.strip().strip('"') for a in allergens if a.strip()],
                    'cooking_skill': 'intermediate',  # Could be stored in DB later
                    'time_preference': 'moderate',    # Could be stored in DB later
                    'default_servings': 2
                }
                
                logger.info(f"Found preferences: diets={preferences['diets']}, cuisines={preferences['cuisines']}")
                
            else:
                # User not found, return defaults
                preferences = {
                    'diets': [],
                    'cuisines': [],
                    'allergens': [],
                    'cooking_skill': 'intermediate',
                    'time_preference': 'moderate',
                    'default_servings': 2
                }
                logger.info("User not found, using default preferences")
                
        except Exception as db_error:
            logger.error(f"Database error: {str(db_error)}")
            # Return defaults on database error
            preferences = {
                'diets': [],
                'cuisines': [],
                'allergens': [],
                'cooking_skill': 'intermediate',
                'time_preference': 'moderate',
                'default_servings': 2
            }
        
        # Add contextual preferences based on common patterns
        contextual_info = {
            'seasonal_preference': get_seasonal_preference(),
            'popular_cooking_methods': ['sautéed', 'fresh', 'baked', 'blended'],
            'dietary_considerations': get_dietary_considerations(preferences['diets']),
            'allergen_warnings': preferences['allergens']
        }
        
        preferences.update(contextual_info)
        
        return {
            'statusCode': 200,
            'body': json.dumps(preferences)
        }
        
    except Exception as e:
        logger.error(f"Error getting user preferences: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Failed to get user preferences',
                'details': str(e)
            })
        }

def get_seasonal_preference():
    """Get seasonal cooking preferences"""
    import datetime
    month = datetime.datetime.now().month
    
    if month in [12, 1, 2]:  # Winter
        return {'season': 'winter', 'preference': 'warm_cooked_foods'}
    elif month in [3, 4, 5]:  # Spring
        return {'season': 'spring', 'preference': 'fresh_light_foods'}
    elif month in [6, 7, 8]:  # Summer
        return {'season': 'summer', 'preference': 'cold_fresh_foods'}
    else:  # Fall
        return {'season': 'fall', 'preference': 'hearty_comfort_foods'}

def get_dietary_considerations(diets):
    """Get cooking considerations based on dietary restrictions"""
    considerations = []
    
    for diet in diets:
        diet_lower = diet.lower()
        if 'vegan' in diet_lower:
            considerations.extend(['no_animal_products', 'plant_based_proteins'])
        elif 'vegetarian' in diet_lower:
            considerations.extend(['no_meat', 'dairy_ok', 'eggs_ok'])
        elif 'gluten' in diet_lower:
            considerations.append('gluten_free_ingredients')
        elif 'keto' in diet_lower:
            considerations.extend(['low_carb', 'high_fat'])
        elif 'paleo' in diet_lower:
            considerations.extend(['no_grains', 'no_dairy', 'whole_foods'])
    
    return considerations