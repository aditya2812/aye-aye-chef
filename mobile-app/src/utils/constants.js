import Constants from 'expo-constants';

// API Configuration
export const API_CONFIG = {
  BASE_URL: Constants.expoConfig?.extra?.apiUrl || process.env.EXPO_PUBLIC_API_URL,
  TIMEOUT: 30000,
};

// AWS Configuration
export const AWS_CONFIG = {
  REGION: Constants.expoConfig?.extra?.awsRegion || process.env.EXPO_PUBLIC_AWS_REGION || 'us-east-1',
  USER_POOL_ID: Constants.expoConfig?.extra?.userPoolId || process.env.EXPO_PUBLIC_USER_POOL_ID,
  USER_POOL_CLIENT_ID: Constants.expoConfig?.extra?.userPoolClientId || process.env.EXPO_PUBLIC_USER_POOL_CLIENT_ID,
  IMAGES_BUCKET: Constants.expoConfig?.extra?.imagesBucket || process.env.EXPO_PUBLIC_IMAGES_BUCKET,
};

// App Constants
export const SCAN_STATUS = {
  PROCESSING: 'processing',
  READY: 'ready',
  CONFIRMED: 'confirmed',
  COMPLETED: 'completed',
};

export const DIETARY_PREFERENCES = [
  'Vegetarian',
  'Vegan',
  'Gluten-free',
  'Dairy-free',
  'Keto',
  'Paleo',
  'Low-carb',
  'Mediterranean',
];

export const CUISINE_TYPES = [
  'Italian',
  'Mexican',
  'Asian',
  'Indian',
  'Mediterranean',
  'American',
  'French',
  'Thai',
  'Japanese',
  'Chinese',
];

export const COMMON_ALLERGENS = [
  'Peanuts',
  'Tree nuts',
  'Milk',
  'Eggs',
  'Fish',
  'Shellfish',
  'Soy',
  'Wheat',
  'Sesame',
];