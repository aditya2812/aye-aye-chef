import json
import boto3
import logging
import os
from typing import List, Dict, Any

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
rekognition = boto3.client('rekognition')
s3 = boto3.client('s3')
bedrock_client = boto3.client('bedrock-runtime')

# Food-related labels that Rekognition can detect
FOOD_LABELS = {
    # Fruits
    'apple', 'banana', 'orange', 'grape', 'strawberry', 'blueberry', 'raspberry',
    'lemon', 'lime', 'pineapple', 'mango', 'avocado', 'peach', 'pear', 'cherry',
    'watermelon', 'cantaloupe', 'kiwi', 'papaya', 'coconut',
    
    # Vegetables
    'tomato', 'onion', 'garlic', 'carrot', 'potato', 'broccoli', 'spinach',
    'lettuce', 'cucumber', 'bell pepper', 'mushroom', 'corn', 'peas',
    'celery', 'cabbage', 'cauliflower', 'zucchini', 'eggplant',
    
    # Proteins
    'chicken', 'beef', 'pork', 'fish', 'salmon', 'tuna', 'shrimp', 'egg',
    'turkey', 'lamb', 'bacon', 'sausage', 'tofu', 'tempeh', 'seitan',
    
    # Dairy
    'milk', 'cheese', 'butter', 'yogurt', 'cream', 'paneer', 'cottage cheese',
    
    # Grains & Legumes
    'rice', 'bread', 'pasta', 'beans', 'lentils', 'quinoa', 'oats', 'dal', 'chickpeas',
    
    # Herbs & Spices
    'basil', 'cilantro', 'parsley', 'mint', 'rosemary', 'thyme',
    
    # Nuts & Seeds
    'almond', 'walnut', 'peanut', 'cashew', 'pistachio'
}

def extract_s3_info(s3_uri: str) -> tuple:
    """Extract bucket and key from S3 URI"""
    if s3_uri.startswith('s3://'):
        parts = s3_uri[5:].split('/', 1)
        return parts[0], parts[1] if len(parts) > 1 else ''
    else:
        raise ValueError(f"Invalid S3 URI format: {s3_uri}")

def is_food_related(label_name: str) -> bool:
    """Check if a label is food-related"""
    label_lower = label_name.lower()
    
    # Exclude generic food categories that are too broad
    generic_categories = {
        'food', 'produce', 'vegetable', 'fruit', 'meat', 'seafood', 
        'plant', 'organic', 'fresh', 'natural', 'ingredient', 'nutrition',
        'diet', 'healthy', 'eating', 'cooking', 'kitchen', 'meal'
    }
    
    # Don't include generic categories
    if label_lower in generic_categories:
        return False
    
    return any(food_item in label_lower for food_item in FOOD_LABELS)

def normalize_food_label_ai(label_name: str, detected_text: List[str] = None) -> str:
    """Use AI to intelligently normalize food labels"""
    try:
        # Quick check for direct text matches first
        if detected_text:
            for text in detected_text:
                text_lower = text.lower()
                if 'paneer' in text_lower:
                    logger.info(f"Direct text match: '{text}' → paneer")
                    return 'paneer'
                elif 'spinach' in text_lower or 'palak' in text_lower:
                    logger.info(f"Direct text match: '{text}' → spinach")
                    return 'spinach'
                elif 'tofu' in text_lower:
                    logger.info(f"Direct text match: '{text}' → tofu")
                    return 'tofu'
        
        # Get Bedrock Agent ID from environment
        agent_id = os.environ.get('BEDROCK_AGENT_ID')
        if not agent_id:
            return normalize_food_label_fallback(label_name)
        
        # Prepare context for AI
        context = {
            'detected_label': label_name,
            'detected_text': detected_text or [],
            'task': 'identify_specific_ingredient'
        }
        
        # Create AI prompt with enhanced paneer/spinach detection
        prompt = f"""
        Identify the specific ingredient from this detection:
        
        Visual Label: "{label_name}"
        Text from Package: {detected_text or 'None'}
        
        Rules:
        1. PRIORITIZE package text over visual labels
        2. Consider cultural context (paneer vs cottage cheese, dal vs lentils)
        3. Prefer specific over generic (apple vs fruit, spinach vs vegetable)
        4. Use common cooking names (not scientific names)
        5. Return only the ingredient name, nothing else
        
        Special mappings:
        - "cheese" + Indian context → paneer
        - "leafy greens" or "vegetable" → spinach (if green leafy)
        - "white food" + cubed → paneer or tofu
        
        Examples:
        - "cheese" + text "PANEER" → paneer
        - "cheese" + no text but cubed white → paneer
        - "leafy greens" + text "SPINACH" → spinach
        - "vegetable" + green leafy → spinach
        - "white food" + text "TOFU" → tofu
        
        Ingredient:"""
        
        # Call Bedrock for intelligent identification using Titan
        bedrock_client = boto3.client('bedrock-runtime', region_name='us-west-2')
        
        try:
            # Use Titan model directly (no Claude dependency)
            titan_prompt = f"Identify this food ingredient and provide just the name: {prompt}"
            response = bedrock_client.invoke_model(
                modelId='amazon.titan-text-express-v1',
                body=json.dumps({
                    'inputText': titan_prompt,
                    'textGenerationConfig': {
                        'maxTokenCount': 50,
                        'temperature': 0.1,
                        'topP': 0.9
                    }
                })
            )
            result = json.loads(response['body'].read())
            ai_ingredient = result['results'][0]['outputText'].strip().lower()
            logger.info("Successfully using Titan for normalization")
        except Exception as titan_error:
            logger.error(f"Titan model failed: {titan_error}")
            return normalize_food_label_fallback(label_name)
        
        # Validate AI response (should be a single ingredient)
        if len(ai_ingredient.split()) <= 2 and ai_ingredient.replace(' ', '').isalpha():
            logger.info(f"AI normalized '{label_name}' to '{ai_ingredient}'")
            return ai_ingredient
        else:
            logger.warning(f"AI returned invalid ingredient: '{ai_ingredient}', using fallback")
            return normalize_food_label_fallback(label_name)
            
    except Exception as e:
        logger.warning(f"AI normalization failed: {e}, using fallback")
        return normalize_food_label_fallback(label_name)

def normalize_food_label_fallback(label_name: str) -> str:
    """Fallback normalization with enhanced Indian food mapping"""
    label_lower = label_name.lower()
    
    # Enhanced mappings including Indian foods
    essential_mappings = {
        'bell pepper': 'bell pepper',
        'green pepper': 'bell pepper', 
        'chicken breast': 'chicken',
        'ground beef': 'beef',
        'cherry tomato': 'tomato',
        'cottage cheese': 'paneer',  # Default cottage cheese to paneer in Indian context
        'white cheese': 'paneer',
        'fresh cheese': 'paneer',
        'leafy greens': 'spinach',
        'leafy vegetables': 'spinach',
        'green leafy': 'spinach',
        'palak': 'spinach',
    }
    
    # Check essential mappings
    for key, value in essential_mappings.items():
        if key in label_lower:
            return value
    
    # Special case: if we see "cheese" without other context, assume paneer in Indian food context
    if label_lower == 'cheese':
        return 'paneer'
    
    return label_name.lower()

def normalize_food_label(label_name: str) -> str:
    """Main normalization function - tries AI first, falls back to manual"""
    return normalize_food_label_ai(label_name)

def validate_fruit_detection(labels: List[Dict]) -> List[Dict]:
    """Apply additional validation for fruit detection accuracy"""
    validated_labels = []
    
    # Group labels by type
    fruit_labels = []
    other_labels = []
    
    for label in labels:
        label_name = label['label'].lower()
        if any(fruit in label_name for fruit in ['apple', 'banana', 'orange', 'pear', 'peach']):
            fruit_labels.append(label)
        else:
            other_labels.append(label)
    
    # If we have multiple fruit detections, prefer the one with highest confidence
    # but add a penalty for common misidentifications
    if len(fruit_labels) > 1:
        # Apply confidence penalties for common misidentifications
        for fruit_label in fruit_labels:
            if fruit_label['label'] == 'banana' and fruit_label['confidence'] < 0.95:
                # Banana is often misidentified, require higher confidence
                fruit_label['confidence'] *= 0.8
    
    # Combine and sort
    all_labels = fruit_labels + other_labels
    all_labels.sort(key=lambda x: x['confidence'], reverse=True)
    
    return all_labels

def detect_ingredients_ai_enhanced(bucket: str, key: str) -> List[Dict[str, Any]]:
    """Use AI-enhanced detection for better accuracy"""
    try:
        # Try AI-powered detection first
        from ai_food_detector import AIFoodDetector
        
        logger.info(f"Starting AI-enhanced detection for {bucket}/{key}")
        ai_detector = AIFoodDetector()
        ai_results = ai_detector.detect_food_multimodal(bucket, key)
        
        if ai_results:
            logger.info(f"AI detection successful: {len(ai_results)} ingredients found")
            for result in ai_results:
                logger.info(f"  - {result['label']}: {result['confidence']:.3f} (source: {result.get('original_label', 'unknown')})")
            return ai_results
        else:
            logger.info("AI detection returned no results, falling back to traditional Rekognition")
            return detect_ingredients_rekognition_fallback(bucket, key)
            
    except Exception as e:
        logger.error(f"AI detection error: {e}, falling back to traditional method")
        return detect_ingredients_rekognition_fallback(bucket, key)

def detect_ingredients_rekognition_fallback(bucket: str, key: str) -> List[Dict[str, Any]]:
    """Fallback to traditional Rekognition detection"""
    try:
        # Call Rekognition detect_labels for visual detection
        response = rekognition.detect_labels(
            Image={
                'S3Object': {
                    'Bucket': bucket,
                    'Name': key
                }
            },
            MaxLabels=50,
            MinConfidence=60.0,  # Lowered for packaged foods
            Features=['GENERAL_LABELS']
        )
        
        ingredients = []
        seen_labels = set()
        
        # Log all detected labels for debugging
        logger.info(f"Rekognition detected {len(response['Labels'])} labels:")
        for label in response['Labels']:
            logger.info(f"  - {label['Name']}: {label['Confidence']:.1f}%")
        
        for label in response['Labels']:
            label_name = label['Name']
            confidence = label['Confidence'] / 100.0  # Convert to 0-1 scale
            
            # Check if this is a food-related label
            if is_food_related(label_name):
                normalized_label = normalize_food_label(label_name)
                
                # Additional filter to exclude generic terms that might slip through
                generic_terms = {'food', 'produce', 'vegetable', 'fruit', 'plant', 'organic', 'fresh'}
                if normalized_label.lower() in generic_terms:
                    logger.info(f"Skipping generic term: {normalized_label} (from {label_name})")
                    continue
                
                # Avoid duplicates
                if normalized_label not in seen_labels:
                    seen_labels.add(normalized_label)
                    ingredients.append({
                        'label': normalized_label,
                        'confidence': round(confidence, 3),
                        'original_label': label_name
                    })
                    logger.info(f"Added ingredient: {normalized_label} (from {label_name}) - {confidence:.3f}")
        
        # Apply fruit validation logic
        ingredients = validate_fruit_detection(ingredients)
        
        # Try text detection for packaged foods
        try:
            text_response = rekognition.detect_text(
                Image={
                    'S3Object': {
                        'Bucket': bucket,
                        'Name': key
                    }
                }
            )
            
            # Extract food-related text
            for text_detection in text_response.get('TextDetections', []):
                if text_detection.get('Type') == 'WORD':
                    detected_text = text_detection.get('DetectedText', '').lower()
                    confidence = text_detection.get('Confidence', 0) / 100.0
                    
                    # Check if detected text matches food items or common package terms
                    logger.info(f"Text detected: '{detected_text}' with confidence {confidence}")
                    
                    # Check for direct food matches or common package terms
                    is_food_text = (is_food_related(detected_text) or 
                                  detected_text in ['paneer', 'spinach', 'tofu', 'cheese', 'dal'])
                    
                    if is_food_text and confidence > 0.5:  # Lower threshold for text
                        normalized_label = normalize_food_label(detected_text)
                        if normalized_label not in seen_labels:
                            seen_labels.add(normalized_label)
                            ingredients.append({
                                'label': normalized_label,
                                'confidence': round(confidence * 0.9, 3),  # Slightly lower confidence for text
                                'original_label': f"Text: {detected_text}"
                            })
                            logger.info(f"Added from text: {normalized_label} (from text: {detected_text})")
        
        except Exception as text_error:
            logger.warning(f"Text detection failed: {str(text_error)}")
        
        # Sort by confidence (highest first)
        ingredients.sort(key=lambda x: x['confidence'], reverse=True)
        
        # Limit to top 10 ingredients
        return ingredients[:10]
        
    except Exception as e:
        logger.error(f"Rekognition detection failed: {str(e)}")
        raise

def handler(event, context):
    """Lambda handler for ingredient detection"""
    try:
        # Parse the input
        if isinstance(event, str):
            event = json.loads(event)
        
        image_s3_uri = event.get('image_s3_uri')
        if not image_s3_uri:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Missing required parameter: image_s3_uri'
                })
            }
        
        logger.info(f"Processing image: {image_s3_uri}")
        
        # Extract S3 bucket and key
        bucket, key = extract_s3_info(image_s3_uri)
        
        # Verify the image exists
        try:
            s3.head_object(Bucket=bucket, Key=key)
        except s3.exceptions.NoSuchKey:
            return {
                'statusCode': 404,
                'body': json.dumps({
                    'error': f'Image not found: {image_s3_uri}'
                })
            }
        
        # Detect ingredients using AI-enhanced detection
        ingredients = detect_ingredients_ai_enhanced(bucket, key)
        
        # Format response according to the schema
        candidates = []
        for ingredient in ingredients:
            candidates.append({
                'label': ingredient['label'],
                'confidence': ingredient['confidence']
            })
        
        # Ensure we have at least one candidate
        if not candidates:
            candidates = [{
                'label': 'unknown food item',
                'confidence': 0.5
            }]
        
        response = {
            'candidates': candidates
        }
        
        logger.info(f"Detected {len(candidates)} ingredients")
        logger.info(f"Final response candidates: {[c['label'] for c in candidates]}")
        
        return {
            'statusCode': 200,
            'body': json.dumps(response)
        }
        
    except Exception as e:
        logger.error(f"Error in ingredient detection: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Internal server error',
                'details': str(e)
            })
        }