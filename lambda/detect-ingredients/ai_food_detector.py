import json
import boto3
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger()

class AIFoodDetector:
    """AI-powered food detection using multiple approaches"""
    
    def __init__(self):
        self.bedrock_client = boto3.client('bedrock-runtime', region_name='us-west-2')
        self.rekognition = boto3.client('rekognition', region_name='us-west-2')
    
    def detect_food_multimodal(self, bucket: str, key: str) -> List[Dict[str, Any]]:
        """Use multiple AI approaches with smart cost optimization"""
        
        # Start with cheaper methods first
        logger.info("Starting multi-modal food detection")
        
        # Approach 1: Traditional Rekognition + AI enhancement (cheaper)
        rekognition_results = self._enhance_rekognition_with_ai(bucket, key)
        logger.info(f"Rekognition results: {len(rekognition_results)} ingredients - {[r['label'] for r in rekognition_results]}")
        
        # Approach 2: Text extraction + AI interpretation (cheap)
        text_results = self._extract_and_interpret_text(bucket, key)
        logger.info(f"Text results: {len(text_results)} ingredients - {[r['label'] for r in text_results]}")
        
        # Combine initial results
        initial_results = self._combine_detection_results(rekognition_results, text_results)
        logger.info(f"Initial combined results: {len(initial_results)} ingredients - {[r['label'] for r in initial_results]}")
        
        # Smart routing: Use Claude Vision if we have less than 2 ingredients or low confidence
        visual_results = []
        max_confidence = max(r['confidence'] for r in initial_results) if initial_results else 0
        ingredient_count = len(initial_results)
        
        # Check if we need Claude Vision (only if initial results are insufficient)
        if ingredient_count < 2 or max_confidence < 0.7:
            try:
                visual_results = self._analyze_image_with_claude(bucket, key)
                logger.info(f"Claude Vision analysis: {len(visual_results)} ingredients - {[r['label'] for r in visual_results]}")
            except Exception as e:
                logger.warning(f"Claude Vision unavailable (likely needs use case approval): {e}")
                visual_results = []
                logger.info(f"Falling back to enhanced text/Rekognition only. Current: {ingredient_count} ingredients, max confidence: {max_confidence}")
        else:
            visual_results = []
            logger.info(f"Skipping Claude Vision - sufficient results from other methods: {ingredient_count} ingredients, max confidence: {max_confidence}")
        
        # Final combination
        all_results = self._combine_detection_results(
            visual_results, rekognition_results, text_results
        )
        logger.info(f"Final combined results: {len(all_results)} ingredients - {[r['label'] for r in all_results]}")
        
        logger.info(f"Multi-modal detection complete: {len(all_results)} ingredients found")
        return all_results
    
    def _analyze_image_with_claude(self, bucket: str, key: str) -> List[Dict[str, Any]]:
        """Use Claude Vision with smart cost optimization"""
        try:
            logger.info(f"Starting Claude Vision analysis for {bucket}/{key}")
            # Get image from S3
            s3_client = boto3.client('s3')
            image_obj = s3_client.get_object(Bucket=bucket, Key=key)
            image_bytes = image_obj['Body'].read()
            
            # Check image size for cost optimization
            image_size_mb = len(image_bytes) / (1024 * 1024)
            logger.info(f"Image size: {image_size_mb:.1f}MB")
            if image_size_mb > 5:  # Skip very large images to control costs
                logger.info(f"Skipping Claude Vision for large image ({image_size_mb:.1f}MB)")
                return []
            
            # Encode image for Claude
            import base64
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            
            prompt = """
            Analyze this food image and identify ALL visible ingredients. Look carefully for multiple items.
            
            Instructions:
            1. Look for ALL individual food items in the image, even if packaged together
            2. Consider cultural context (paneer vs cottage cheese, dal vs lentils)
            3. If items are packaged, try to read package labels carefully
            4. Return specific ingredient names, not generic terms
            5. Include confidence level (0.0-1.0) for each ingredient
            6. Look for combinations like "paneer and spinach" or mixed vegetables
            7. Even if confidence is moderate (0.6+), include the ingredient
            
            Common combinations to look for:
            - Paneer + Spinach (palak paneer ingredients)
            - Multiple vegetables in one package
            - Mixed ingredients for specific dishes
            
            Return JSON format:
            {
                "ingredients": [
                    {"name": "paneer", "confidence": 0.85, "reasoning": "white cubed cheese, likely paneer"},
                    {"name": "spinach", "confidence": 0.75, "reasoning": "green leafy vegetable visible in package"}
                ]
            }
            """
            
            # Since Titan doesn't support vision, we'll rely on Rekognition labels
            # and use Titan for text-based ingredient identification only
            logger.info("Using Rekognition-based detection (Titan doesn't support vision)")
            
            # Return empty result to fall back to Rekognition
            return {
                'ingredients': [],
                'confidence': 0.0,
                'method': 'rekognition_only'
            }
            
            # Note: The following Claude code is commented out due to access restrictions
            # If Claude access is restored, uncomment and use:
            """
            response = None
            try:
                response = self.bedrock_client.invoke_model(
                    modelId='anthropic.claude-3-5-sonnet-20241022-v2:0',
                    body=json.dumps({
                        'anthropic_version': 'bedrock-2023-05-31',
                        'max_tokens': 500,
                        'messages': [{
                            'role': 'user',
                            'content': [
                                {'type': 'text', 'text': prompt},
                                {
                                    'type': 'image',
                                        'source': {
                                            'type': 'base64',
                                            'media_type': 'image/jpeg',
                                            'data': image_base64
                                        }
                                    }
                                ]
                            }]
                        })
                    )
                    logger.info(f"Successfully using Claude model: {model_id}")
                    break
                except Exception as model_error:
                    logger.warning(f"Failed to use model {model_id}: {model_error}")
                    continue
            
            if not response:
                raise Exception("All Claude models failed - use case approval may be required")
            
            result = json.loads(response['body'].read())
            ai_response = result['results'][0]['outputText']
            
            # Parse AI response
            try:
                logger.info(f"Claude Vision raw response: {ai_response}")
                parsed_response = json.loads(ai_response)
                ingredients = parsed_response.get('ingredients', [])
                
                # Convert to our format
                formatted_results = []
                for ingredient in ingredients:
                    formatted_results.append({
                        'label': ingredient['name'].lower(),
                        'confidence': float(ingredient['confidence']),
                        'source': 'claude_vision',
                        'reasoning': ingredient.get('reasoning', '')
                    })
                
                logger.info(f"Claude Vision detected {len(formatted_results)} ingredients: {[r['label'] for r in formatted_results]}")
                return formatted_results
                
            except json.JSONDecodeError as e:
                logger.warning(f"Could not parse Claude Vision response as JSON: {e}")
                logger.warning(f"Raw response was: {ai_response}")
                return []
                
        except Exception as e:
            logger.error(f"Claude Vision analysis failed: {e}")
            return []
    
    def _enhance_rekognition_with_ai(self, bucket: str, key: str) -> List[Dict[str, Any]]:
        """Use Rekognition + AI enhancement"""
        try:
            # Get Rekognition results
            response = self.rekognition.detect_labels(
                Image={'S3Object': {'Bucket': bucket, 'Name': key}},
                MaxLabels=20,
                MinConfidence=50.0
            )
            
            # Also get text detection for context
            text_response = self.rekognition.detect_text(
                Image={'S3Object': {'Bucket': bucket, 'Name': key}}
            )
            
            detected_text = []
            for text_detection in text_response.get('TextDetections', []):
                if text_detection.get('Type') == 'WORD' and text_detection.get('Confidence', 0) > 60:
                    detected_text.append(text_detection.get('DetectedText', ''))
            
            # Extract food-related labels
            food_labels = []
            for label in response['Labels']:
                label_name = label['Name'].lower()
                if self._is_potentially_food_related(label_name):
                    food_labels.append({
                        'name': label_name,
                        'confidence': label['Confidence'] / 100.0
                    })
            
            if not food_labels:
                return []
            
            # Use AI to interpret and enhance Rekognition results
            prompt = f"""
            These are labels detected by computer vision in a food image:
            {json.dumps(food_labels, indent=2)}
            
            Text detected on packaging: {', '.join(detected_text) if detected_text else 'None'}
            
            Task: Convert these generic labels into specific food ingredients. BE CONSERVATIVE - only return ingredients you're confident about.
            
            Rules:
            1. PRIORITIZE text from packaging over visual labels
            2. Only map generic terms if there's strong evidence:
               - "cheese" + clear Indian context → "paneer"
               - "leafy greens" + clearly green vegetables → "spinach"
               - "white food" + cubed shape → "paneer" or "tofu"
            3. Remove non-food items completely
            4. DO NOT add ingredients unless there's clear evidence
            5. If text clearly says "PANEER" or "SPINACH", use that
            6. AVOID false positives - better to miss an ingredient than add a wrong one
            
            Return JSON:
            {{
                "ingredients": [
                    {{"name": "specific_ingredient", "confidence": 0.85, "source_labels": ["original", "labels"]}}
                ]
            }}
            """
            
            # Use Titan for text processing
            try:
                response = self.bedrock_client.invoke_model(
                    modelId='amazon.titan-text-express-v1',
                    body=json.dumps({
                        'inputText': prompt,
                        'textGenerationConfig': {
                            'maxTokenCount': 500,
                            'temperature': 0.3,
                            'topP': 0.9
                        }
                    })
                )
                logger.info("Successfully using Titan model for Rekognition enhancement")
            except Exception as model_error:
                logger.warning(f"Failed to use Titan model: {model_error}")
                return []
                    continue
            
            if not response:
                logger.warning("All Claude models failed, trying Titan as fallback")
                try:
                    titan_prompt = f"Human: {prompt}\n\nAssistant:"
                    response = self.bedrock_client.invoke_model(
                        modelId='amazon.titan-text-express-v1',
                        body=json.dumps({
                            'inputText': titan_prompt,
                            'textGenerationConfig': {
                                'maxTokenCount': 500,
                                'temperature': 0.1,
                                'topP': 0.9
                            }
                        })
                    )
                    result = json.loads(response['body'].read())
                    ai_response = result['results'][0]['outputText']
                    logger.info("Successfully using Titan as fallback for Rekognition enhancement")
                except Exception as titan_error:
                    logger.error(f"Titan fallback also failed: {titan_error}")
                    return []
            
            result = json.loads(response['body'].read())
            ai_response = result['results'][0]['outputText']
            
            try:
                parsed_response = json.loads(ai_response)
                ingredients = parsed_response.get('ingredients', [])
                
                formatted_results = []
                for ingredient in ingredients:
                    formatted_results.append({
                        'label': ingredient['name'].lower(),
                        'confidence': float(ingredient['confidence']),
                        'source': 'rekognition_ai_enhanced',
                        'source_labels': ingredient.get('source_labels', [])
                    })
                
                logger.info(f"Enhanced Rekognition detected {len(formatted_results)} ingredients")
                return formatted_results
                
            except json.JSONDecodeError:
                logger.warning("Could not parse enhanced Rekognition response")
                return []
                
        except Exception as e:
            logger.error(f"Enhanced Rekognition failed: {e}")
            return []
    
    def _extract_and_interpret_text(self, bucket: str, key: str) -> List[Dict[str, Any]]:
        """Extract text and use AI to interpret food names"""
        try:
            # Extract text using Rekognition
            response = self.rekognition.detect_text(
                Image={'S3Object': {'Bucket': bucket, 'Name': key}}
            )
            
            # Collect all detected text
            detected_texts = []
            high_confidence_texts = []
            
            for text_detection in response.get('TextDetections', []):
                if text_detection.get('Type') == 'WORD':
                    text = text_detection.get('DetectedText', '')
                    confidence = text_detection.get('Confidence', 0)
                    
                    detected_texts.append(text)
                    
                    # Check for direct ingredient matches with higher confidence threshold for accuracy
                    text_lower = text.lower()
                    
                    # High confidence ingredients (exact matches)
                    exact_ingredients = ['paneer', 'spinach', 'tofu', 'dal', 'palak']
                    # Medium confidence ingredients (partial matches)
                    partial_ingredients = ['cheese', 'green', 'leafy']
                    
                    is_exact_match = any(ingredient in text_lower for ingredient in exact_ingredients)
                    is_partial_match = any(ingredient in text_lower for ingredient in partial_ingredients)
                    
                    # Require higher confidence for partial matches, lower for exact matches
                    confidence_threshold = 50 if is_exact_match else 70
                    
                    if (is_exact_match or is_partial_match) and confidence > confidence_threshold:
                        high_confidence_texts.append({
                            'text': text,
                            'confidence': confidence / 100.0,
                            'is_direct_match': True
                        })
            
            # If we found direct ingredient matches, prioritize them
            if high_confidence_texts:
                results = []
                for item in high_confidence_texts:
                    text_lower = item['text'].lower()
                    
                    # Map common variations more conservatively
                    ingredients_to_add = []
                    
                    # Exact matches (high confidence)
                    if 'paneer' in text_lower:
                        ingredients_to_add.append('paneer')
                    if 'spinach' in text_lower or 'palak' in text_lower:
                        ingredients_to_add.append('spinach')
                    if 'tofu' in text_lower:
                        ingredients_to_add.append('tofu')
                    if 'dal' in text_lower and len(text_lower) <= 5:  # Only if "dal" is standalone, not part of another word
                        ingredients_to_add.append('dal')
                    
                    # Partial matches (only if no exact matches found)
                    if not ingredients_to_add:
                        if 'cheese' in text_lower and confidence > 75:  # Higher threshold for generic terms
                            ingredients_to_add.append('paneer')
                        elif ('green' in text_lower or 'leafy' in text_lower) and confidence > 75:
                            ingredients_to_add.append('spinach')
                    
                    # Only add ingredients if we found specific matches
                    for ingredient_name in ingredients_to_add:
                    
                        results.append({
                            'label': ingredient_name,
                            'confidence': min(item['confidence'] * 1.1, 1.0),  # Boost confidence for direct matches
                            'source': 'text_direct_match',
                            'source_text': item['text']
                        })
                
                logger.info(f"Direct text matches found: {[r['label'] for r in results]}")
                return results
            
            if not detected_texts:
                return []
            
            # Use AI to interpret text for food ingredients
            prompt = f"""
            These words were detected on a food package or label:
            {', '.join(detected_texts)}
            
            Task: Identify which words are food ingredients and normalize them.
            
            Rules:
            1. Look for ingredient names in any language (English, Hindi, etc.)
            2. Normalize to common English cooking terms
            3. Consider brand names and product descriptions
            4. Ignore non-food text (prices, dates, barcodes, etc.)
            5. IMPORTANT: If you see "PANEER", "SPINACH", "PALAK", "TOFU" - include them with high confidence
            6. Map variations: "PALAK" → "spinach", "PANEER" → "paneer"
            
            Return JSON:
            {{
                "ingredients": [
                    {{"name": "ingredient_name", "confidence": 0.9, "source_text": "original_text"}}
                ]
            }}
            """
            
            # Use Titan for text interpretation
            try:
                response = self.bedrock_client.invoke_model(
                    modelId='amazon.titan-text-express-v1',
                    body=json.dumps({
                        'inputText': prompt,
                        'textGenerationConfig': {
                            'maxTokenCount': 300,
                            'temperature': 0.3,
                            'topP': 0.9
                        }
                    })
                )
                logger.info("Successfully using Titan model for text interpretation")
            except Exception as model_error:
                logger.warning(f"Failed to use Titan model: {model_error}")
                response = None
            
            if not response:
                logger.warning("All Claude models failed, trying Titan as fallback")
                try:
                    titan_prompt = f"Human: {prompt}\n\nAssistant:"
                    response = self.bedrock_client.invoke_model(
                        modelId='amazon.titan-text-express-v1',
                        body=json.dumps({
                            'inputText': titan_prompt,
                            'textGenerationConfig': {
                                'maxTokenCount': 300,
                                'temperature': 0.1,
                                'topP': 0.9
                            }
                        })
                    )
                    result = json.loads(response['body'].read())
                    ai_response = result['results'][0]['outputText']
                    logger.info("Successfully using Titan as fallback for text interpretation")
                except Exception as titan_error:
                    logger.error(f"Titan fallback also failed: {titan_error}")
                    return []
            
            result = json.loads(response['body'].read())
            ai_response = result['results'][0]['outputText']
            
            try:
                parsed_response = json.loads(ai_response)
                ingredients = parsed_response.get('ingredients', [])
                
                formatted_results = []
                for ingredient in ingredients:
                    formatted_results.append({
                        'label': ingredient['name'].lower(),
                        'confidence': float(ingredient['confidence']),
                        'source': 'text_ai_interpreted',
                        'source_text': ingredient.get('source_text', '')
                    })
                
                logger.info(f"Text interpretation found {len(formatted_results)} ingredients")
                return formatted_results
                
            except json.JSONDecodeError:
                logger.warning("Could not parse text interpretation response")
                return []
                
        except Exception as e:
            logger.error(f"Text interpretation failed: {e}")
            return []
    
    def _combine_detection_results(self, *result_lists) -> List[Dict[str, Any]]:
        """Combine results from multiple detection methods"""
        
        # Flatten all results
        all_results = []
        for result_list in result_lists:
            all_results.extend(result_list)
        
        if not all_results:
            return []
        
        # Group by ingredient name
        ingredient_groups = {}
        for result in all_results:
            name = result['label']
            if name not in ingredient_groups:
                ingredient_groups[name] = []
            ingredient_groups[name].append(result)
        
        # Combine confidence scores and select best result for each ingredient
        final_results = []
        for name, results in ingredient_groups.items():
            # Calculate weighted average confidence
            total_confidence = sum(r['confidence'] for r in results)
            avg_confidence = total_confidence / len(results)
            
            # Boost confidence if detected by multiple methods
            if len(results) > 1:
                avg_confidence = min(avg_confidence * 1.2, 1.0)
            
            # Select the result with best source priority
            source_priority = {'claude_vision': 3, 'text_ai_interpreted': 2, 'rekognition_ai_enhanced': 1}
            best_result = max(results, key=lambda r: source_priority.get(r['source'], 0))
            
            final_results.append({
                'label': name,
                'confidence': round(avg_confidence, 3),
                'original_label': f"AI-Enhanced: {name}",
                'detection_methods': [r['source'] for r in results],
                'method_count': len(results)
            })
        
        # Filter out low confidence results and sort by confidence
        filtered_results = [r for r in final_results if r['confidence'] >= 0.6]  # Minimum 60% confidence
        filtered_results.sort(key=lambda x: x['confidence'], reverse=True)
        
        logger.info(f"Combined detection found {len(filtered_results)} high-confidence ingredients (filtered from {len(final_results)} total)")
        return filtered_results[:5]  # Limit to top 5 high-confidence ingredients
    
    def _is_potentially_food_related(self, label: str) -> bool:
        """Check if a label could be food-related"""
        food_keywords = [
            'food', 'ingredient', 'vegetable', 'fruit', 'meat', 'dairy', 'cheese', 
            'leaf', 'green', 'white', 'fresh', 'organic', 'produce', 'plant',
            'bean', 'grain', 'seed', 'nut', 'herb', 'spice', 'leafy', 'spinach',
            'paneer', 'tofu', 'dal', 'palak', 'greens'
        ]
        
        return any(keyword in label.lower() for keyword in food_keywords)