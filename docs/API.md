# 📡 API Documentation

## Base URL
```
https://your-api-gateway-url.amazonaws.com/prod/
```

## Authentication
All API endpoints require JWT authentication via AWS Cognito.

```javascript
// Include in request headers
Authorization: Bearer <jwt-token>
```

## Endpoints

### 1. Image Upload
**POST** `/presign`

Get presigned URL for image upload to S3.

**Response:**
```json
{
  "success": true,
  "data": {
    "uploadUrl": "https://s3-presigned-url...",
    "s3Key": "images/uuid-filename.jpg"
  }
}
```

### 2. Start Scan
**POST** `/start-scan`

Initiate ingredient detection from uploaded image.

**Request:**
```json
{
  "s3Key": "images/uuid-filename.jpg"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "scan_id": "scan_uuid",
    "status": "processing"
  }
}
```

### 3. Get Scan Results
**GET** `/scan/{scan_id}`

Retrieve ingredient detection results.

**Response:**
```json
{
  "success": true,
  "data": {
    "scan_id": "scan_uuid",
    "status": "completed",
    "items": [
      {
        "label": "banana",
        "confidence": 0.95,
        "grams_est": 120
      }
    ]
  }
}
```

### 4. Confirm Scan
**POST** `/confirm-scan`

Confirm detected ingredients and user preferences.

**Request:**
```json
{
  "scan_id": "scan_uuid",
  "items": [
    {
      "label": "banana",
      "confirmed": true,
      "grams": 120
    }
  ],
  "preferences": {
    "diets": ["vegetarian"],
    "cuisines": ["italian"],
    "allergens": [],
    "servings": 2
  }
}
```

### 5. Create Recipe
**POST** `/create-recipe`

Generate AI-powered recipes from confirmed ingredients.

**Request:**
```json
{
  "scan_id": "scan_uuid",
  "servings": 2,
  "cuisine": "italian",
  "skill_level": "intermediate",
  "dietary_restrictions": ["vegetarian"],
  "meal_type": "lunch",
  "recipe_category": "cuisine"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "recipe_ids": ["recipe_1", "recipe_2", "recipe_3"],
    "recipes": [
      {
        "id": "recipe_1",
        "title": "Italian Banana Smoothie Bowl",
        "servings": 2,
        "estimated_time": "15 minutes",
        "difficulty": "beginner",
        "cuisine": "italian",
        "tags": ["vegetarian", "healthy", "breakfast"],
        "ingredients": [
          {
            "name": "banana",
            "grams": 120,
            "notes": "ripe, peeled and sliced"
          }
        ],
        "steps": [
          "Peel and slice the banana...",
          "Add to blender with milk...",
          "Blend until smooth..."
        ],
        "nutrition": {
          "per_serving": {
            "kcal": 150,
            "protein_g": 3,
            "carb_g": 35,
            "fat_g": 1
          }
        }
      }
    ]
  }
}
```

### 6. Get Recipe
**GET** `/recipe/{recipe_id}`

Retrieve specific recipe details.

**Response:**
```json
{
  "success": true,
  "data": {
    "recipe": { /* recipe object */ },
    "nutrition": { /* nutrition data */ }
  }
}
```

## Error Responses

All endpoints return errors in this format:

```json
{
  "success": false,
  "error": "Error message description",
  "code": "ERROR_CODE"
}
```

### Common Error Codes
- `INVALID_TOKEN` - Authentication failed
- `SCAN_NOT_FOUND` - Scan ID doesn't exist
- `PROCESSING_ERROR` - AI processing failed
- `VALIDATION_ERROR` - Invalid request data

## Rate Limits
- 100 requests per minute per user
- 1000 requests per hour per user
- Burst limit: 20 requests per second

## SDKs and Examples

### JavaScript/React Native
```javascript
import { apiService } from './services/api';

// Start scan
const result = await apiService.startScan(s3Key);

// Create recipe
const recipes = await apiService.createRecipe(
  scanId, 
  servings, 
  cuisine, 
  skillLevel, 
  dietaryRestrictions
);
```

### Python
```python
import requests

headers = {'Authorization': f'Bearer {jwt_token}'}
response = requests.post(
    f'{API_BASE_URL}/start-scan',
    json={'s3Key': s3_key},
    headers=headers
)
```

## Webhooks (Future)
Webhook support for real-time updates on scan processing and recipe generation.