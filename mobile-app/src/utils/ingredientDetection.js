// Utility functions for ingredient detection and categorization

// Common fruits that should trigger smoothie/dessert options
const COMMON_FRUITS = [
  // Citrus fruits
  'orange', 'lemon', 'lime', 'grapefruit', 'tangerine', 'mandarin',
  
  // Berries
  'strawberry', 'blueberry', 'raspberry', 'blackberry', 'cranberry', 'cherry',
  
  // Tropical fruits
  'banana', 'pineapple', 'mango', 'papaya', 'coconut', 'kiwi', 'passion fruit',
  
  // Stone fruits
  'peach', 'plum', 'apricot', 'nectarine',
  
  // Pome fruits
  'apple', 'pear',
  
  // Melons
  'watermelon', 'cantaloupe', 'honeydew', 'melon',
  
  // Grapes and others
  'grape', 'fig', 'date', 'pomegranate', 'avocado',
  
  // Exotic fruits
  'dragon fruit', 'star fruit', 'lychee', 'rambutan', 'durian'
];

// Vegetables that are commonly used in smoothies
const SMOOTHIE_VEGETABLES = [
  'spinach', 'kale', 'carrot', 'beet', 'cucumber', 'celery'
];

/**
 * Detect if the scanned ingredients are primarily fruits
 * @param {Array} ingredients - Array of ingredient objects with label property
 * @returns {boolean} - True if fruits are detected
 */
export const detectFruits = (ingredients) => {
  if (!ingredients || ingredients.length === 0) {
    return false;
  }

  let fruitCount = 0;
  let totalCount = ingredients.length;

  ingredients.forEach(ingredient => {
    const label = ingredient.label?.toLowerCase() || '';
    
    // Check if ingredient is a fruit
    const isFruit = COMMON_FRUITS.some(fruit => 
      label.includes(fruit) || fruit.includes(label)
    );
    
    // Check if ingredient is a smoothie-friendly vegetable
    const isSmoothieVegetable = SMOOTHIE_VEGETABLES.some(veg => 
      label.includes(veg) || veg.includes(label)
    );
    
    if (isFruit || isSmoothieVegetable) {
      fruitCount++;
    }
  });

  // Consider it fruit-based if more than 60% of ingredients are fruits/smoothie vegetables
  const fruitPercentage = fruitCount / totalCount;
  return fruitPercentage > 0.6;
};

/**
 * Get appropriate recipe categories based on ingredients
 * @param {Array} ingredients - Array of ingredient objects
 * @returns {Object} - Object with isFruitBased and suggestedCategories
 */
export const getRecipeCategories = (ingredients) => {
  const isFruitBased = detectFruits(ingredients);
  
  if (isFruitBased) {
    return {
      isFruitBased: true,
      suggestedCategories: ['smoothie', 'dessert'],
      defaultCategory: 'smoothie'
    };
  } else {
    return {
      isFruitBased: false,
      suggestedCategories: ['italian', 'thai', 'mexican', 'indian', 'mediterranean'],
      defaultCategory: 'italian'
    };
  }
};

/**
 * Get meal type suggestions based on ingredients and time of day
 * @param {Array} ingredients - Array of ingredient objects
 * @param {Date} currentTime - Current time (optional)
 * @returns {string} - Suggested meal type
 */
export const suggestMealType = (ingredients, currentTime = new Date()) => {
  const hour = currentTime.getHours();
  const isFruitBased = detectFruits(ingredients);
  
  // Time-based suggestions
  if (hour >= 6 && hour < 11) {
    return 'breakfast';
  } else if (hour >= 11 && hour < 16) {
    return 'lunch';
  } else if (hour >= 16 && hour < 21) {
    return 'dinner';
  } else {
    return 'snack';
  }
};

/**
 * Validate meal type and recipe category combination
 * @param {string} mealType - Selected meal type
 * @param {string} recipeCategory - Selected recipe category
 * @param {Array} ingredients - Array of ingredient objects
 * @returns {Object} - Validation result with isValid and suggestions
 */
export const validateMealCombination = (mealType, recipeCategory, ingredients) => {
  const isFruitBased = detectFruits(ingredients);
  
  // Fruit-based recipes are valid for all meal types
  if (isFruitBased && ['smoothie', 'dessert'].includes(recipeCategory)) {
    return {
      isValid: true,
      message: `Perfect ${recipeCategory} for ${mealType}!`
    };
  }
  
  // Cuisine-based recipes are valid for main meals
  if (!isFruitBased && ['italian', 'thai', 'mexican', 'indian', 'mediterranean'].includes(recipeCategory)) {
    if (mealType === 'snack') {
      return {
        isValid: true,
        message: `Light ${recipeCategory} snack coming up!`,
        suggestion: 'Consider smaller portions for snack time'
      };
    }
    return {
      isValid: true,
      message: `Delicious ${recipeCategory} ${mealType}!`
    };
  }
  
  return {
    isValid: false,
    message: 'Unusual combination, but let\'s try it!',
    suggestion: 'This combination might work better with different ingredients'
  };
};

export default {
  detectFruits,
  getRecipeCategories,
  suggestMealType,
  validateMealCombination
};