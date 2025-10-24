import { API_CONFIG } from '../utils/constants';
import { authService } from './auth';

class ApiService {
  constructor() {
    this.baseURL = API_CONFIG.BASE_URL;
    this.timeout = API_CONFIG.TIMEOUT;
  }

  // Get authorization headers
  async getAuthHeaders() {
    const token = await authService.getUserToken();
    return {
      'Content-Type': 'application/json',
      'Authorization': token ? `Bearer ${token}` : '',
    };
  }

  // Generic API call method
  async apiCall(endpoint, options = {}) {
    try {
      const url = `${this.baseURL}${endpoint}`;
      const headers = await this.getAuthHeaders();
      
      // Create AbortController for proper timeout handling
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), this.timeout);
      
      const config = {
        method: 'GET',
        headers,
        signal: controller.signal,
        mode: 'cors',
        credentials: 'omit',
        ...options,
      };
      
      console.log('📤 API Call Details:', {
        method: config.method,
        url: url,
        baseURL: this.baseURL,
        endpoint: endpoint,
        hasAuth: !!headers.Authorization,
        hasBody: !!config.body,
        bodyPreview: config.body ? config.body.substring(0, 200) + '...' : 'none',
        headers: {
          'Content-Type': headers['Content-Type'],
          'Authorization': headers.Authorization ? 'Bearer [REDACTED]' : 'None'
        }
      });

      const response = await fetch(url, config);
      
      // Clear timeout on successful response
      clearTimeout(timeoutId);
      
      console.log('📥 API Response:', {
        status: response.status,
        statusText: response.statusText,
        ok: response.ok,
        url: response.url
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ API Error Response:', errorText);
        throw new Error(`HTTP error! status: ${response.status}, body: ${errorText}`);
      }

      const data = await response.json();
      console.log('✅ API Success:', {
        hasData: !!data,
        dataKeys: data ? Object.keys(data) : 'no data'
      });
      
      return { success: true, data };
    } catch (error) {
      // Handle AbortError specifically
      if (error.name === 'AbortError') {
        console.error('🚨 API Request Timeout:', {
          timeout: this.timeout,
          url: `${this.baseURL}${endpoint}`
        });
        return { success: false, error: `Request timed out after ${this.timeout/1000} seconds` };
      }
      console.error('🚨 API Call Failed:', {
        error: error.message,
        stack: error.stack,
        url: `${this.baseURL}${endpoint}`
      });
      return { success: false, error: error.message };
    }
  }

  // Get presigned URL for image upload
  async getPresignedUrl(contentType = 'image/jpeg') {
    return this.apiCall('/uploads/presign', {
      method: 'POST',
      body: JSON.stringify({ contentType }),
    });
  }

  // Upload image to S3
  async uploadImage(presignedUrl, imageUri) {
    try {
      const response = await fetch(imageUri);
      const blob = await response.blob();

      const uploadResponse = await fetch(presignedUrl, {
        method: 'PUT',
        body: blob,
        headers: {
          'Content-Type': 'image/jpeg',
        },
      });

      if (!uploadResponse.ok) {
        throw new Error(`Upload failed: ${uploadResponse.status}`);
      }

      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  // Start scan process
  async startScan(imageData) {
    // Handle both s3Key and base64 image data
    let requestBody;
    
    if (typeof imageData === 'string') {
      // If it's a string, treat it as base64 image data
      requestBody = imageData;
    } else if (imageData.s3Key) {
      // If it's an object with s3Key, use that format
      requestBody = JSON.stringify({ s3Key: imageData.s3Key });
    } else {
      // Otherwise, stringify the whole object
      requestBody = JSON.stringify(imageData);
    }
    
    console.log('📤 API startScan request preview:', requestBody.substring(0, 100) + '...');
    
    return this.apiCall('/scans', {
      method: 'POST',
      body: requestBody,
    });
  }

  // Get scan results
  async getScan(scanId) {
    return this.apiCall(`/scans/${scanId}`);
  }

  // Confirm scan ingredients
  async confirmScan(scanId, items, preferences = {}) {
    return this.apiCall(`/scans/${scanId}/confirm`, {
      method: 'POST',
      body: JSON.stringify({
        items,
        ...preferences,
      }),
    });
  }

  // Create recipe
  async createRecipe(scanId, servings = 2, cuisine = 'italian', skillLevel = 'intermediate', dietaryRestrictions = [], mealType = 'lunch', recipeCategory = 'italian', testMode = false) {
    return this.apiCall('/recipes', {
      method: 'POST',
      body: JSON.stringify({ 
        scan_id: scanId, 
        servings,
        cuisine,
        skill_level: skillLevel,
        dietary_restrictions: dietaryRestrictions,
        meal_type: mealType,
        recipe_category: recipeCategory,
        test_mode: testMode
      }),
    });
  }

  // Get recipe
  async getRecipe(recipeId) {
    return this.apiCall(`/recipes/${recipeId}`);
  }

  // Log meal
  async logMeal(recipeId, servings) {
    return this.apiCall('/meals', {
      method: 'POST',
      body: JSON.stringify({ recipe_id: recipeId, servings }),
    });
  }
}

export const apiService = new ApiService();