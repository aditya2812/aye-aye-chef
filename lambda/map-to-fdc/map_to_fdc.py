import json
import boto3
import logging
import os
import requests
import time
from typing import List, Dict, Any

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
secrets_client = boto3.client('secretsmanager')
dynamodb = boto3.resource('dynamodb')

# Cache table (will be created by CDK)
CACHE_TABLE_NAME = os.environ.get('FDC_CACHE_TABLE', 'fdc-label-cache')

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

def normalize_label(label: str) -> str:
    """Normalize ingredient labels for better matching"""
    # Convert to lowercase and strip
    normalized = label.lower().strip()
    
    # Common synonyms mapping
    synonyms = {
        'coriander leaves': 'cilantro',
        'coriander': 'cilantro',
        'scallion': 'green onion',
        'spring onion': 'green onion',
        'bell pepper': 'sweet pepper',
        'capsicum': 'sweet pepper',
        'chicken breast': 'chicken',
        'chicken thigh': 'chicken',
        'ground beef': 'beef',
        'beef steak': 'beef',
        'roma tomato': 'tomato',
        'cherry tomato': 'tomato',
        'yellow onion': 'onion',
        'red onion': 'onion',
        'white onion': 'onion',
    }
    
    return synonyms.get(normalized, normalized)

def check_cache(label: str) -> Dict[str, Any]:
    """Check DynamoDB cache for existing mapping"""
    try:
        table = dynamodb.Table(CACHE_TABLE_NAME)
        response = table.get_item(Key={'label': label})
        
        if 'Item' in response:
            item = response['Item']
            logger.info(f"Cache hit for label: {label}")
            return {
                'fdc_id': item['fdc_id'],
                'score': item['score'],
                'options': item.get('options', []),
                'cached': True
            }
    except Exception as e:
        logger.warning(f"Cache check failed for {label}: {e}")
    
    return None

def write_cache(label: str, fdc_id: str, score: float, options: List[str]):
    """Write mapping to DynamoDB cache with TTL"""
    try:
        table = dynamodb.Table(CACHE_TABLE_NAME)
        
        # TTL: 30 days from now
        ttl = int(time.time()) + (30 * 24 * 60 * 60)
        
        table.put_item(
            Item={
                'label': label,
                'fdc_id': fdc_id,
                'score': score,
                'options': options,
                'cached_at': int(time.time()),
                'ttl': ttl
            }
        )
        logger.info(f"Cached mapping for {label} -> {fdc_id}")
    except Exception as e:
        logger.warning(f"Cache write failed for {label}: {e}")

def search_usda_fdc(query: str, api_key: str) -> List[Dict[str, Any]]:
    """Search USDA FDC API for ingredient"""
    if not api_key:
        logger.warning("No USDA API key available")
        return []
    
    url = "https://api.nal.usda.gov/fdc/v1/foods/search"
    
    params = {
        'query': query,
        'dataType': ['Foundation', 'SR Legacy', 'Survey (FNDDS)'],
        'pageSize': 5,
        'requireAllWords': True,
        'api_key': api_key
    }
    
    try:
        logger.info(f"Searching USDA FDC for: {query}")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        foods = data.get('foods', [])
        
        logger.info(f"USDA API returned {len(foods)} results for {query}")
        return foods
        
    except Exception as e:
        logger.error(f"USDA API search failed for {query}: {e}")
        return []

def rank_and_filter_results(foods: List[Dict], query: str) -> Dict[str, Any]:
    """Rank and filter USDA search results"""
    if not foods:
        return None
    
    scored_foods = []
    
    for food in foods:
        score = 0.0
        fdc_id = str(food.get('fdcId', ''))
        description = food.get('description', '').lower()
        data_type = food.get('dataType', '')
        
        # Score based on data type preference
        if data_type == 'Foundation':
            score += 0.4
        elif data_type == 'SR Legacy':
            score += 0.3
        elif data_type == 'Survey (FNDDS)':
            score += 0.2
        
        # Score based on description match
        query_words = query.lower().split()
        for word in query_words:
            if word in description:
                score += 0.3
        
        # Exact match bonus
        if query.lower() in description:
            score += 0.3
        
        # Prefer shorter, more specific descriptions
        if len(description.split()) <= 3:
            score += 0.1
        
        scored_foods.append({
            'fdc_id': fdc_id,
            'description': description,
            'data_type': data_type,
            'score': min(score, 1.0)  # Cap at 1.0
        })
    
    # Sort by score (highest first)
    scored_foods.sort(key=lambda x: x['score'], reverse=True)
    
    if scored_foods:
        best = scored_foods[0]
        options = [food['fdc_id'] for food in scored_foods[:3]]  # Top 3 options
        
        return {
            'fdc_id': best['fdc_id'],
            'score': best['score'],
            'options': options,
            'description': best['description']
        }
    
    return None

def map_single_label(label: str, api_key: str) -> Dict[str, Any]:
    """Map a single label to FDC ID"""
    normalized_label = normalize_label(label)
    
    # Check cache first
    cached_result = check_cache(normalized_label)
    if cached_result:
        return {
            'label': label,
            'fdc_id': cached_result['fdc_id'],
            'score': cached_result['score'],
            'options': cached_result['options']
        }
    
    # Search USDA API
    foods = search_usda_fdc(normalized_label, api_key)
    result = rank_and_filter_results(foods, normalized_label)
    
    if result:
        # Write to cache
        write_cache(normalized_label, result['fdc_id'], result['score'], result['options'])
        
        return {
            'label': label,
            'fdc_id': result['fdc_id'],
            'score': result['score'],
            'options': result['options']
        }
    else:
        # Fallback mapping for common ingredients
        fallback_mappings = {
            'apple': '09003',
            'banana': '09040', 
            'egg': '01123',
            'chicken': '05064',
            'onion': '11282',
            'tomato': '11529',
            'potato': '11352',
            'carrot': '11124'
        }
        
        fallback_fdc = fallback_mappings.get(normalized_label)
        if fallback_fdc:
            logger.info(f"Using fallback mapping for {label}: {fallback_fdc}")
            return {
                'label': label,
                'fdc_id': fallback_fdc,
                'score': 0.8,  # Good confidence for fallback
                'options': [fallback_fdc]
            }
        
        # No mapping found
        logger.warning(f"No mapping found for label: {label}")
        return {
            'label': label,
            'fdc_id': '99999',  # Generic food placeholder
            'score': 0.1,
            'options': ['99999']
        }

def handler(event, context):
    """Lambda handler for mapping ingredient labels to FDC IDs"""
    try:
        # Parse input
        if isinstance(event, str):
            event = json.loads(event)
        
        labels = event.get('labels', [])
        if not labels:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Missing required parameter: labels'
                })
            }
        
        logger.info(f"Mapping {len(labels)} labels to FDC IDs")
        
        # Get USDA API key
        api_key = get_usda_api_key()
        
        # Map each label
        mapped_results = []
        for label in labels:
            result = map_single_label(label, api_key)
            mapped_results.append(result)
            logger.info(f"Mapped {label} -> {result['fdc_id']} (score: {result['score']:.2f})")
        
        response = {
            'mapped': mapped_results
        }
        
        logger.info(f"Successfully mapped {len(mapped_results)} labels")
        
        return {
            'statusCode': 200,
            'body': json.dumps(response)
        }
        
    except Exception as e:
        logger.error(f"Error in map_to_fdc: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Internal server error',
                'details': str(e)
            })
        }