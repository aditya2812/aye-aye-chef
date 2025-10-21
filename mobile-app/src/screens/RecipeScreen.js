import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  Alert,
  ActivityIndicator,
  Share,
} from 'react-native';
import { apiService } from '../services/api';
import { authService } from '../services/auth';
import CuisineSelector from '../components/CuisineSelector';
import SkillLevelSelector from '../components/SkillLevelSelector';
import DietaryRestrictionsSelector from '../components/DietaryRestrictionsSelector';
import MealTypeSelector from '../components/MealTypeSelector';
import RecipeCategorySelector from '../components/RecipeCategorySelector';
import EnhancedRecipeSteps from '../components/EnhancedRecipeSteps';
import { detectFruits, getRecipeCategories, suggestMealType } from '../utils/ingredientDetection';

export default function RecipeScreen({ route, navigation }) {
  const { scanId, confirmedItems, servings, preferences } = route.params;
  const [loading, setLoading] = useState(true);
  const [recipe, setRecipe] = useState(null);
  const [nutrition, setNutrition] = useState(null);
  const [recipeOptions, setRecipeOptions] = useState([]);
  const [showRecipeSelection, setShowRecipeSelection] = useState(false);
  const [selectedRecipeIndex, setSelectedRecipeIndex] = useState(0);
  const [userName, setUserName] = useState('');
  
  // Enhanced recipe preferences - initialize from passed preferences
  const [selectedCuisine, setSelectedCuisine] = useState(
    preferences?.cuisines?.[0]?.toLowerCase() || preferences?.recipeType || 'international'
  );
  const [selectedSkillLevel, setSelectedSkillLevel] = useState(
    preferences?.cookingLevel || 'intermediate'
  );
  const [dietaryRestrictions, setDietaryRestrictions] = useState(
    preferences?.diets || []
  );
  
  // New meal type and recipe category states - initialize from passed preferences
  const [selectedMealType, setSelectedMealType] = useState(
    preferences?.mealType || 'lunch'
  );
  const [selectedRecipeCategory, setSelectedRecipeCategory] = useState(
    preferences?.recipeType || 'smoothie'
  );
  const [isFruitDetected, setIsFruitDetected] = useState(
    preferences?.isFruitDetected || false
  );
  
  // Modal visibility states
  const [showCuisineSelector, setShowCuisineSelector] = useState(false);
  const [showSkillLevelSelector, setShowSkillLevelSelector] = useState(false);
  const [showDietarySelector, setShowDietarySelector] = useState(false);
  const [showMealTypeSelector, setShowMealTypeSelector] = useState(false);
  const [showRecipeCategorySelector, setShowRecipeCategorySelector] = useState(false);
  const [showPreferences, setShowPreferences] = useState(
    // Only show preferences if they weren't set in ConfirmScreen
    !preferences?.mealType && !preferences?.recipeType && !preferences?.cookingLevel
  );

  // Debug function - accessible from browser console
  React.useEffect(() => {
    if (typeof window !== 'undefined') {
      window.debugRecipeScreen = {
        stopLoading: () => setLoading(false),
        generateMock: () => generateMockRecipe(),
        getState: () => ({
          loading,
          selectedCuisine,
          selectedRecipeCategory,
          selectedMealType,
          isFruitDetected
        })
      };
    }
  }, [loading, selectedCuisine, selectedRecipeCategory, selectedMealType, isFruitDetected]);

  useEffect(() => {
    // Debug: Log the preferences being passed
    console.log('🔍 RecipeScreen preferences received:', {
      preferences,
      selectedCuisine,
      selectedRecipeCategory,
      isFruitDetected,
      selectedMealType
    });
    
    // Initialize meal type and recipe category based on ingredients (only if no preferences passed)
    initializePreferences();
    loadUserInfo();
    
    // Auto-generate recipe for testing
    if (!showPreferences) {
      generateRecipe();
    }
  }, []);

  const initializePreferences = () => {
    // Only initialize if preferences weren't passed from ConfirmScreen
    if (!preferences || Object.keys(preferences).length === 0) {
      console.log('🔧 No preferences passed, initializing defaults...');
      
      // Detect if ingredients are primarily fruits
      const fruitDetected = detectFruits(confirmedItems || []);
      setIsFruitDetected(fruitDetected);
      
      // Set suggested meal type based on time of day
      const suggestedMeal = suggestMealType(confirmedItems || []);
      setSelectedMealType(suggestedMeal);
      
      // Set appropriate recipe category
      const { defaultCategory } = getRecipeCategories(confirmedItems || []);
      setSelectedRecipeCategory(defaultCategory);
      
      // Update cuisine for backward compatibility
      if (!fruitDetected) {
        setSelectedCuisine(defaultCategory);
      }
    } else {
      console.log('✅ Using preferences from ConfirmScreen:', preferences);
      // Preferences were passed, don't override them
    }
  };

  const loadUserInfo = async () => {
    try {
      const userResult = await authService.getCurrentUser();
      if (userResult.success && userResult.user) {
        const email = userResult.user.signInDetails?.loginId || userResult.user.username || '';
        const name = email.split('@')[0];
        setUserName(name);
      }
    } catch (error) {
      }
  };

  const generateRecipe = async () => {
    try {
      console.log('🚀 Starting recipe generation with params:', {
        scanId,
        servings,
        cuisine: isFruitDetected ? selectedRecipeCategory : selectedCuisine,
        skillLevel: selectedSkillLevel,
        dietaryRestrictions,
        mealType: selectedMealType,
        recipeCategory: selectedRecipeCategory
      });
      
      // Add timeout to prevent infinite loading
      const timeoutPromise = new Promise((_, reject) => 
        setTimeout(() => reject(new Error('Request timeout after 15 seconds')), 15000)
      );
      
      // Call the enhanced API to create recipe with preferences
      const createResponse = await Promise.race([
        apiService.createRecipe(
          scanId, 
          servings, 
          isFruitDetected ? 'healthy' : selectedCuisine, // Use 'healthy' as cuisine for fruits
          selectedSkillLevel, 
          dietaryRestrictions,
          selectedMealType,
          selectedRecipeCategory,
          false // Disable test mode to use real recipe generation
        ),
        timeoutPromise
      ]);
      console.log('🔍 API Response:', createResponse);
      console.log('🔍 API Response JSON:', JSON.stringify(createResponse, null, 2));
      console.log('🔍 Response structure check:', {
        hasSuccess: !!createResponse.success,
        hasData: !!createResponse.data,
        hasRecipeIds: !!(createResponse.data && createResponse.data.recipe_ids),
        hasRecipeId: !!(createResponse.data && createResponse.data.recipe_id),
        dataKeys: createResponse.data ? Object.keys(createResponse.data) : 'no data',
        fullDataStructure: createResponse.data
      });
      
      if (createResponse.success && createResponse.data.recipe_ids) {
        // Multiple recipes created - show selection
        const recipeOptions = createResponse.data.recipes;
        // Always store recipe options for navigation
        setRecipeOptions(recipeOptions);
        
        if (recipeOptions.length === 1) {
          // Only one recipe - check if it's a test recipe or generated recipe with complete data
          if ((createResponse.data.test_mode || recipeOptions[0].ai_generated !== undefined) && recipeOptions[0]) {
            // Generated recipe or test mode - use the recipe data directly without API call
            setRecipe(recipeOptions[0]);
            setNutrition({ 
              per_serving: { kcal: 150, protein_g: 3, carb_g: 15, fat_g: 8 },
              totals_per_recipe: { kcal: 300, protein_g: 6, carb_g: 30, fat_g: 16 }
            });
            setSelectedRecipeIndex(0);
          } else {
            // Database recipe - load recipe details from API
            const recipeResponse = await apiService.getRecipe(recipeOptions[0].id);
            if (recipeResponse.success) {
              const recipeData = recipeResponse.data;
              setRecipe(recipeData.recipe);
              setNutrition(recipeData.nutrition);
              setSelectedRecipeIndex(0);
            } else {
              throw new Error('Failed to fetch recipe details');
            }
          }
        } else {
          // Multiple recipes - show selection screen
          setShowRecipeSelection(true);
        }
        
        // Always set loading to false after processing recipes
        setLoading(false);
      } else if (createResponse.success && createResponse.data.recipe_id) {
        // Backward compatibility - single recipe
        const recipeResponse = await apiService.getRecipe(createResponse.data.recipe_id);
        if (recipeResponse.success) {
          const recipeData = recipeResponse.data;
          setRecipe(recipeData.recipe);
          setNutrition(recipeData.nutrition);
          setLoading(false); // Fix: Add missing setLoading(false)
        } else {
          throw new Error('Failed to fetch recipe details');
        }
      } else {
        throw new Error(createResponse.error || 'Unexpected API response format');
      }

    } catch (error) {
      // Always stop loading first
      setLoading(false);
      
      console.error('🚨 Recipe generation error:', error);
      console.error('🚨 Error details:', {
        message: error.message,
        stack: error.stack,
        scanId,
        servings,
        selectedCuisine,
        selectedRecipeCategory
      });
      
      // Check if this is a "no recipe found" error
      const isNoRecipeError = error.message.includes('Recipe generation failed') || 
                             error.message.includes('AI could not generate recipes');
      
      // Check if this is a timeout or network error
      const isNetworkError = error.message.includes('timeout') || 
                             error.message.includes('Network') ||
                             error.message.includes('fetch');
      
      if (isNetworkError) {
        Alert.alert(
          'Connection Issue', 
          `Unable to connect to the recipe service. Please check your internet connection and try again.\n\nError: ${error.message}`,
          [
            { text: 'Retry', onPress: generateRecipe },
            { text: 'Use Mock Recipe', onPress: () => generateMockRecipe() },
            { text: 'Go Back', onPress: () => navigation.goBack() }
          ]
        );
      } else if (isNoRecipeError) {
        Alert.alert(
          'No Recipes Found', 
          `Our AI couldn't generate recipes for your ingredients. This might be because:\n\n• The ingredients are unusual or not commonly cooked together\n• The AI service is temporarily unavailable\n• The ingredient detection wasn't accurate\n\nPlease try scanning different ingredients or try again later.`,
          [
            { text: 'Try Again', onPress: generateRecipe },
            { text: 'Use Mock Recipe', onPress: () => generateMockRecipe() },
            { text: 'Go Back', onPress: () => navigation.goBack() }
          ]
        );
      } else {
        Alert.alert(
          'Recipe Generation Failed', 
          `Unable to generate recipes: ${error.message}\n\nPlease try again or check your connection.`,
          [
            { text: 'Retry', onPress: generateRecipe },
            { text: 'Use Mock Recipe', onPress: () => generateMockRecipe() },
            { text: 'Go Back', onPress: () => navigation.goBack() }
          ]
        );
      }
    }
  };

  const generateMultipleMockRecipes = (ingredients, servings, preferences) => {
    console.log('🍳 Generating multiple mock recipes for ingredients:', ingredients.map(i => i.label));
    
    const mainIngredients = ingredients.filter(item => item.label !== 'food' && item.label !== 'produce');
    const primaryIngredient = mainIngredients[0]?.label || 'food';
    
    const recipes = [];
    
    // Check for special combinations
    const ingredientNames = mainIngredients.map(i => i.label.toLowerCase());
    
    if (ingredientNames.includes('paneer') && ingredientNames.includes('spinach')) {
      // Special paneer + spinach recipes
      recipes.push(generatePalakPaneerRecipe(ingredients, servings));
      recipes.push(generatePaneerSpinachSaladRecipe(ingredients, servings));
      recipes.push(generateSpinachPaneerCurryRecipe(ingredients, servings));
    } else {
      // Generate 3 different cooking methods
      recipes.push(generateFreshRecipe(ingredients, servings, 'fresh'));
      recipes.push(generateCookedRecipe(ingredients, servings, 'cooked'));
      recipes.push(generateBakedRecipe(ingredients, servings, 'baked'));
    }
    
    return recipes;
  };

  const generateRecipeFromIngredients = (ingredients, servings, preferences) => {
    console.log('🍳 Generating recipe for ingredients:', ingredients.map(i => i.label));
    
    const mainIngredients = ingredients.filter(item => item.label !== 'food' && item.label !== 'produce');
    const primaryIngredient = mainIngredients[0]?.label || 'food';
    
    console.log('🥘 Mock recipe generation for ingredients:', mainIngredients.map(i => i.label));
    // Recipe templates based on primary ingredient
    const recipeTemplates = {
      'apple': {
        title: 'Baked Cinnamon Apples',
        tags: ['healthy', 'dessert', 'gluten-free', '30-min'],
        steps: [
          'Preheat oven to 375°F (190°C).',
          'Core and slice the apples into wedges.',
          'Toss apple slices with cinnamon and a touch of honey.',
          'Arrange on a baking sheet lined with parchment paper.',
          'Bake for 20-25 minutes until tender and lightly caramelized.',
          'Serve warm, optionally with yogurt or nuts.',
        ],
        nutrition: { kcal: 95, protein_g: 0.5, carb_g: 25, fat_g: 0.3 }
      },
      'banana': {
        title: 'Healthy Banana Smoothie Bowl',
        tags: ['vegan', 'healthy', 'breakfast', '5-min'],
        steps: [
          'Peel the banana and slice into chunks.',
          'Add banana chunks to a blender with 1/2 cup of your favorite milk.',
          'Blend until smooth and creamy, about 30-60 seconds.',
          'Pour into a bowl and add your favorite toppings.',
          'Serve immediately for best texture.',
          'Optional: Add honey or maple syrup for extra sweetness.',
        ],
        nutrition: { kcal: 105, protein_g: 1.3, carb_g: 27, fat_g: 0.4 }
      },
      'egg': {
        title: 'Perfect Scrambled Eggs',
        tags: ['protein', 'breakfast', 'quick', '10-min'],
        steps: [
          'Crack eggs into a bowl and whisk until well combined.',
          'Heat a non-stick pan over medium-low heat.',
          'Add a small amount of butter or oil to the pan.',
          'Pour in the eggs and let them sit for 20 seconds.',
          'Gently stir with a spatula, pushing eggs from edges to center.',
          'Continue stirring gently until eggs are just set but still creamy.',
          'Remove from heat and season with salt and pepper.',
          'Serve immediately while hot.',
        ],
        nutrition: { kcal: 155, protein_g: 13, carb_g: 1, fat_g: 11 }
      },
      'potato': {
        title: 'Crispy Roasted Potatoes',
        tags: ['side-dish', 'crispy', 'comfort-food', '45-min'],
        steps: [
          'Preheat oven to 425°F (220°C).',
          'Wash and dice potatoes into 1-inch cubes.',
          'Toss with olive oil, salt, and your favorite herbs.',
          'Spread in a single layer on a baking sheet.',
          'Roast for 25-30 minutes, flipping halfway through.',
          'Cook until golden brown and crispy on the outside.',
          'Serve hot as a side dish.',
        ],
        nutrition: { kcal: 130, protein_g: 3, carb_g: 30, fat_g: 0.1 }
      },
      'tomato': {
        title: 'Fresh Tomato Salad',
        tags: ['fresh', 'healthy', 'summer', '10-min'],
        steps: [
          'Wash and slice tomatoes into wedges.',
          'Arrange on a serving plate.',
          'Drizzle with olive oil and balsamic vinegar.',
          'Season with salt, pepper, and fresh basil.',
          'Let sit for 5 minutes to allow flavors to meld.',
          'Serve at room temperature for best flavor.',
        ],
        nutrition: { kcal: 32, protein_g: 1.6, carb_g: 7, fat_g: 0.4 }
      }
    };
    
    // Get recipe template or create a generic one
    let template = recipeTemplates[primaryIngredient];
    
    // If multiple ingredients, create a combined recipe
    if (mainIngredients.length > 1) {
      const ingredientNames = mainIngredients.map(i => i.label).slice(0, 3);
      const title = ingredientNames.length === 2 
        ? `${ingredientNames[0]} and ${ingredientNames[1]} Mix`
        : `${ingredientNames[0]}, ${ingredientNames[1]} and More Recipe`;
      
      template = {
        title: title,
        tags: ['healthy', 'mixed', 'fresh', '15-min'],
        steps: [
          `Prepare all ingredients: ${ingredientNames.join(', ')}.`,
          'Wash and chop ingredients as needed.',
          'Combine ingredients in a bowl or pan.',
          'Mix or cook together until well combined.',
          'Season to taste with your favorite spices.',
          'Serve fresh or cook until heated through.',
        ],
        nutrition: { kcal: 120, protein_g: 3, carb_g: 25, fat_g: 2 }
      };
    } else if (!template) {
      template = {
        title: `Simple ${primaryIngredient.charAt(0).toUpperCase() + primaryIngredient.slice(1)} Recipe`,
        tags: ['healthy', 'simple', '20-min'],
        steps: [
          `Prepare your ${primaryIngredient} by washing and cutting as needed.`,
          'Heat a pan over medium heat with a little oil.',
          `Add the ${primaryIngredient} and cook until tender.`,
          'Season with salt, pepper, and your favorite herbs.',
          'Cook for 5-10 minutes until done to your liking.',
          'Serve hot and enjoy!',
        ],
        nutrition: { kcal: 100, protein_g: 2, carb_g: 20, fat_g: 1 }
      };
    }
    
    return {
      title: template.title,
      servings: servings,
      tags: template.tags,
      ingredients: ingredients.map(item => ({
        name: item.label,
        grams: item.grams_est || 100,
        notes: getIngredientNotes(item.label),
      })),
      steps: template.steps,
      substitutions: getSubstitutions(primaryIngredient),
      warnings: getWarnings(primaryIngredient),
    };
  };

  const getIngredientNotes = (ingredient) => {
    const notes = {
      'apple': 'washed and cored',
      'banana': 'ripe, peeled and sliced',
      'egg': 'room temperature works best',
      'potato': 'washed and peeled if desired',
      'tomato': 'ripe and fresh',
      'chicken': 'boneless, skinless',
      'onion': 'peeled and diced',
    };
    return notes[ingredient] || 'prepared as needed';
  };
  
  const getSubstitutions = (ingredient) => {
    const substitutions = {
      'apple': ['Can use pears instead of apples', 'Maple syrup can replace honey'],
      'banana': ['Can use frozen banana for thicker texture', 'Almond milk works great for dairy-free'],
      'egg': ['Can use egg whites only for lower fat', '2 eggs can be replaced with 1/4 cup egg substitute'],
      'potato': ['Sweet potatoes work as a substitute', 'Can use different potato varieties'],
      'tomato': ['Cherry tomatoes work well', 'Can add mozzarella for caprese style'],
    };
    return substitutions[ingredient] || ['Adjust seasonings to taste', 'Can add herbs for extra flavor'];
  };
  
  const getWarnings = (ingredient) => {
    const warnings = {
      'egg': ['Cook eggs to internal temperature of 160°F (71°C)', 'Use fresh eggs for best results'],
      'chicken': ['Cook to internal temperature of 165°F (74°C)', 'Wash hands after handling raw chicken'],
      'potato': ['Green potatoes should be avoided', 'Store potatoes in cool, dark place'],
    };
    return warnings[ingredient] || [];
  };

  const generatePalakPaneerRecipe = (ingredients, servings) => ({
    title: 'Palak Paneer (Indian Spinach Cottage Cheese Curry)',
    servings: servings,
    estimated_time: '30 minutes',
    tags: ['indian', 'vegetarian', 'curry', '30-min'],
    ingredients: ingredients.map(item => ({
      name: item.label,
      grams: item.grams_est || 100,
      notes: getIngredientNotes(item.label),
    })),
    steps: [
      'Heat 2 tablespoons oil in a heavy-bottomed pan over medium heat',
      'Add 1 teaspoon cumin seeds and let them splutter for 30 seconds',
      'Add 1 finely chopped onion and sauté until golden brown (5-6 minutes)',
      'Add 1 tablespoon ginger-garlic paste and cook for 1 minute until fragrant',
      'Add 1 chopped tomato and cook until soft and mushy (3-4 minutes)',
      'Add the washed spinach leaves and cook until wilted (2-3 minutes)',
      'Let the mixture cool, then blend to a smooth puree with little water',
      'Return puree to the pan, add 1/2 tsp turmeric, 1 tsp coriander powder, 1/2 tsp garam masala',
      'Simmer for 5 minutes, then gently add paneer cubes',
      'Cook for 3-4 minutes without stirring too much to prevent paneer from breaking',
      'Add salt to taste and 2 tablespoons fresh cream',
      'Garnish with fresh coriander and serve hot with basmati rice or naan bread'
    ],
    substitutions: [
      'Vegan: Substitute paneer with firm tofu',
      'Add cashews while blending for extra creaminess',
      'Use coconut milk instead of cream for dairy-free option'
    ],
    warnings: [
      'Potential allergens: Dairy (paneer, cream). Use tofu for dairy-free',
      'Don\'t overcook paneer as it becomes rubbery'
    ]
  });

  const generatePaneerSpinachSaladRecipe = (ingredients, servings) => ({
    title: 'Fresh Paneer Spinach Salad with Indian Spices',
    servings: servings,
    estimated_time: '15 minutes',
    tags: ['indian', 'vegetarian', 'fresh', '15-min', 'healthy'],
    ingredients: ingredients.map(item => ({
      name: item.label,
      grams: item.grams_est || 100,
      notes: getIngredientNotes(item.label),
    })),
    steps: [
      'Wash and thoroughly dry fresh spinach leaves',
      'Cut paneer into small cubes and lightly pan-fry until golden',
      'In a large bowl, combine spinach leaves with the warm paneer',
      'Prepare dressing: mix 2 tbsp olive oil, 1 tbsp lemon juice, 1/2 tsp chaat masala',
      'Add 1/4 tsp black pepper, 1/2 tsp roasted cumin powder, and salt to taste',
      'Toss the salad with dressing just before serving',
      'Garnish with pomegranate seeds and chopped mint if available',
      'Serve immediately as a light meal or side dish'
    ],
    substitutions: [
      'Add cherry tomatoes and cucumber for extra freshness',
      'Use hung curd instead of oil for lighter dressing',
      'Add roasted peanuts for crunch'
    ],
    warnings: [
      'Potential allergens: Dairy (paneer)',
      'Dress the salad just before serving to prevent wilting'
    ]
  });

  const generateSpinachPaneerCurryRecipe = (ingredients, servings) => ({
    title: 'Spinach Paneer Curry (Restaurant Style)',
    servings: servings,
    estimated_time: '25 minutes',
    tags: ['indian', 'vegetarian', 'curry', '25-min', 'restaurant-style'],
    ingredients: ingredients.map(item => ({
      name: item.label,
      grams: item.grams_est || 100,
      notes: getIngredientNotes(item.label),
    })),
    steps: [
      'Blanch spinach in boiling water for 2 minutes, then plunge in ice water',
      'Drain and blend spinach with 2 green chilies to smooth paste',
      'Heat 3 tablespoons ghee or oil in a pan over medium heat',
      'Add 1 bay leaf, 2 green cardamom, 1-inch cinnamon stick',
      'Add 1 sliced onion and cook until golden brown',
      'Add 1 tbsp ginger-garlic paste, cook for 1 minute',
      'Add 1/2 tsp turmeric, 1 tsp coriander powder, 1/2 tsp red chili powder',
      'Add the spinach puree and cook for 8-10 minutes on medium heat',
      'Add 1/4 cup water if needed, then add paneer cubes gently',
      'Simmer for 5 minutes, add 1/2 tsp garam masala',
      'Finish with 2 tbsp cream and fresh coriander',
      'Serve hot with rotis or steamed rice'
    ],
    substitutions: [
      'Use mustard greens mixed with spinach for variation',
      'Add a pinch of sugar to balance the flavors',
      'Use butter instead of ghee for richer taste'
    ],
    warnings: [
      'Potential allergens: Dairy (paneer, cream, ghee)',
      'Don\'t boil the curry after adding cream'
    ]
  });

  const generateFreshRecipe = (ingredients, servings, type) => ({
    title: `Fresh ${ingredients[0]?.label || 'Ingredient'} Bowl`,
    servings: servings,
    estimated_time: '10 minutes',
    tags: ['fresh', 'raw', 'healthy', '10-min'],
    ingredients: ingredients.map(item => ({
      name: item.label,
      grams: item.grams_est || 100,
      notes: getIngredientNotes(item.label),
    })),
    steps: [
      'Wash all ingredients thoroughly under cold running water',
      'Pat dry with clean paper towels or kitchen cloth',
      'Cut ingredients into bite-sized pieces using a sharp knife',
      'Arrange attractively in a serving bowl or individual plates',
      'Drizzle with fresh lemon juice or your favorite dressing',
      'Season with salt and freshly ground black pepper to taste',
      'Serve immediately while fresh and crisp'
    ],
    substitutions: [
      'Add toasted nuts or seeds for extra crunch and protein',
      'Use balsamic vinegar instead of lemon juice',
      'Drizzle with extra virgin olive oil for healthy fats'
    ],
    warnings: [
      'Wash all fresh ingredients thoroughly to remove dirt and bacteria',
      'Consume immediately for best texture and nutrition'
    ]
  });

  const generateCookedRecipe = (ingredients, servings, type) => ({
    title: `Sautéed ${ingredients[0]?.label || 'Ingredient'} Stir-Fry`,
    servings: servings,
    estimated_time: '20 minutes',
    tags: ['cooked', 'sautéed', 'warm', '20-min'],
    ingredients: ingredients.map(item => ({
      name: item.label,
      grams: item.grams_est || 100,
      notes: getIngredientNotes(item.label),
    })),
    steps: [
      'Heat 2 tablespoons oil in a large pan or wok over medium-high heat',
      'Add harder ingredients first (like potatoes, carrots) if present',
      'Cook for 3-5 minutes until starting to soften',
      'Add softer ingredients (like leafy greens, tomatoes)',
      'Stir-fry for 2-3 minutes until heated through but still crisp',
      'Season with salt, pepper, and your favorite spices',
      'Add a splash of soy sauce or lemon juice for extra flavor',
      'Serve hot as a side dish or main course'
    ],
    substitutions: [
      'Use butter instead of oil for richer flavor',
      'Add garlic and ginger for extra aroma',
      'Include your favorite herbs and spices'
    ],
    warnings: [
      'Don\'t overcook vegetables to maintain nutrients and texture',
      'Cook to safe internal temperatures for any meat or eggs'
    ]
  });

  const generateBakedRecipe = (ingredients, servings, type) => ({
    title: `Roasted ${ingredients[0]?.label || 'Ingredient'} Medley`,
    servings: servings,
    estimated_time: '35 minutes',
    tags: ['baked', 'roasted', 'warm', '35-min'],
    ingredients: ingredients.map(item => ({
      name: item.label,
      grams: item.grams_est || 100,
      notes: getIngredientNotes(item.label),
    })),
    steps: [
      'Preheat oven to 400°F (200°C)',
      'Wash and cut ingredients into uniform pieces',
      'Toss with 2-3 tablespoons olive oil in a large bowl',
      'Season generously with salt, pepper, and herbs',
      'Arrange in a single layer on a large baking sheet',
      'Roast for 20-25 minutes, flipping halfway through',
      'Cook until tender and lightly golden brown',
      'Serve hot as a side dish or light meal'
    ],
    substitutions: [
      'Add herbs like rosemary, thyme, or oregano',
      'Drizzle with balsamic vinegar before serving',
      'Top with grated cheese in the last 5 minutes'
    ],
    warnings: [
      'Don\'t overcrowd the baking sheet for even cooking',
      'Check for doneness with a fork - should be tender'
    ]
  });
  
  const calculateNutrition = (ingredients, servings) => {
    // Nutrition data per 100g for common ingredients
    const nutritionData = {
      'apple': { kcal: 52, protein_g: 0.3, carb_g: 14, fat_g: 0.2, fiber_g: 2.4 },
      'banana': { kcal: 89, protein_g: 1.1, carb_g: 23, fat_g: 0.3, fiber_g: 2.6 },
      'egg': { kcal: 155, protein_g: 13, carb_g: 1.1, fat_g: 11, fiber_g: 0 },
      'potato': { kcal: 77, protein_g: 2, carb_g: 17, fat_g: 0.1, fiber_g: 2.2 },
      'tomato': { kcal: 18, protein_g: 0.9, carb_g: 3.9, fat_g: 0.2, fiber_g: 1.2 },
      'chicken': { kcal: 165, protein_g: 31, carb_g: 0, fat_g: 3.6, fiber_g: 0 },
      'onion': { kcal: 40, protein_g: 1.1, carb_g: 9.3, fat_g: 0.1, fiber_g: 1.7 },
    };
    
    let totalKcal = 0;
    let totalProtein = 0;
    let totalCarbs = 0;
    let totalFat = 0;
    let totalFiber = 0;
    
    ingredients.forEach(ingredient => {
      const nutrition = nutritionData[ingredient.label] || nutritionData['apple']; // fallback
      const grams = ingredient.grams_est || 100;
      const factor = grams / 100; // Convert per 100g to actual grams
      
      totalKcal += nutrition.kcal * factor;
      totalProtein += nutrition.protein_g * factor;
      totalCarbs += nutrition.carb_g * factor;
      totalFat += nutrition.fat_g * factor;
      totalFiber += nutrition.fiber_g * factor;
    });
    
    return {
      totals_per_recipe: {
        kcal: Math.round(totalKcal),
        protein_g: Math.round(totalProtein * 10) / 10,
        carb_g: Math.round(totalCarbs * 10) / 10,
        fat_g: Math.round(totalFat * 10) / 10,
        fiber_g: Math.round(totalFiber * 10) / 10,
      },
      per_serving: {
        kcal: Math.round(totalKcal / servings),
        protein_g: Math.round((totalProtein / servings) * 10) / 10,
        carb_g: Math.round((totalCarbs / servings) * 10) / 10,
        fat_g: Math.round((totalFat / servings) * 10) / 10,
        fiber_g: Math.round((totalFiber / servings) * 10) / 10,
      },
    };
  };

  const handleShare = async () => {
    if (!recipe) return;

    const recipeText = `
${recipe.title}
Serves: ${recipe.servings}

Ingredients:
${recipe.ingredients.map(ing => `• ${ing.grams}g ${ing.name} ${ing.notes ? `(${ing.notes})` : ''}`).join('\n')}

Instructions:
${recipe.steps.map((step, index) => `${index + 1}. ${step}`).join('\n')}

Nutrition per serving:
• Calories: ${nutrition?.per_serving.kcal}
• Protein: ${nutrition?.per_serving.protein_g}g
• Carbs: ${nutrition?.per_serving.carb_g}g
• Fat: ${nutrition?.per_serving.fat_g}g

Generated by Aye Aye App
    `.trim();

    try {
      await Share.share({
        message: recipeText,
        title: recipe.title,
      });
    } catch (error) {
      }
  };

  const handleLogMeal = async () => {
    try {
      // In production: await apiService.logMeal(recipeId, servings);
      Alert.alert('Success', 'Meal logged successfully!');
    } catch (error) {
      Alert.alert('Error', 'Failed to log meal');
    }
  };

  const handleNewScan = () => {
    navigation.navigate('Camera');
  };

  const handleRecipeSelection = async (selectedRecipe, index) => {
    try {
      setLoading(true);
      
      // Check if this is a generated recipe (has ai_generated field) or needs API call
      if (selectedRecipe.ai_generated !== undefined || selectedRecipe.steps) {
        // Generated recipe - use directly without API call
        setRecipe(selectedRecipe);
        setNutrition({ 
          per_serving: { kcal: 150, protein_g: 3, carb_g: 15, fat_g: 8 },
          totals_per_recipe: { kcal: 300, protein_g: 6, carb_g: 30, fat_g: 16 }
        });
        setSelectedRecipeIndex(index);
        setShowRecipeSelection(false);
      } else {
        // Database recipe - use API to get recipe details
        const recipeResponse = await apiService.getRecipe(selectedRecipe.id);
        if (recipeResponse.success) {
          const recipeData = recipeResponse.data;
          setRecipe(recipeData.recipe);
          setNutrition(recipeData.nutrition);
          setSelectedRecipeIndex(index);
          setShowRecipeSelection(false);
        } else {
          throw new Error('Failed to fetch recipe details');
        }
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to load selected recipe');
    } finally {
      setLoading(false);
    }
  };

  const generateMockRecipe = () => {
    console.log('🎭 Generating mock recipe as fallback');
    
    // Create a mock recipe based on selected preferences
    const cuisineType = isFruitDetected ? selectedRecipeCategory : selectedCuisine;
    const mockRecipe = {
      title: `Mock ${cuisineType.charAt(0).toUpperCase() + cuisineType.slice(1)} Recipe`,
      servings: servings,
      estimated_time: '25 minutes',
      difficulty: selectedSkillLevel,
      cuisine: cuisineType,
      meal_type: selectedMealType,
      recipe_category: selectedRecipeCategory,
      tags: [cuisineType, selectedSkillLevel, selectedMealType, '25-min'],
      ingredients: confirmedItems?.map(item => ({
        name: item.label,
        grams: item.grams_est || 100,
        notes: 'prepared as needed',
        fdc_id: item.fdc_id || ''
      })) || [
        { name: 'Main ingredient', grams: 200, notes: 'prepared as needed', fdc_id: '' }
      ],
      steps: [
        'Prepare all ingredients by washing and cutting as needed.',
        'Heat 2 tablespoons oil in a large pan over medium heat.',
        'Add the main ingredients and cook for 5-7 minutes.',
        'Season with salt, pepper, and your favorite spices.',
        'Continue cooking until ingredients are tender and well combined.',
        'Taste and adjust seasoning as needed.',
        'Serve hot and enjoy your meal!'
      ],
      substitutions: [
        'You can substitute ingredients based on what you have available',
        'Adjust cooking time based on ingredient size and preference',
        'Add herbs and spices to enhance flavor'
      ],
      warnings: [
        'This is a mock recipe for testing purposes',
        'Adjust cooking times and temperatures as needed'
      ]
    };

    const mockNutrition = {
      totals_per_recipe: {
        kcal: 300,
        protein_g: 15,
        carb_g: 35,
        fat_g: 12,
        fiber_g: 8
      },
      per_serving: {
        kcal: Math.round(300 / servings),
        protein_g: Math.round(15 / servings),
        carb_g: Math.round(35 / servings),
        fat_g: Math.round(12 / servings),
        fiber_g: Math.round(8 / servings)
      }
    };

    setRecipe(mockRecipe);
    setNutrition(mockNutrition);
    setLoading(false);
  };

  const handleBackToRecipeList = () => {
    if (recipeOptions.length > 1) {
      setShowRecipeSelection(true);
    } else {
      navigation.navigate('Camera');
    }
  };

  if (loading) {
    // Create dynamic loading message based on user selection
    const getLoadingMessage = () => {
      console.log('🔍 Creating loading message with:', {
        isFruitDetected,
        selectedRecipeCategory,
        selectedCuisine,
        preferences
      });
      
      if (isFruitDetected) {
        // For fruits, show the selected recipe category (smoothie/dessert)
        const recipeType = selectedRecipeCategory || 'smoothie';
        return `Generating your ${recipeType} recipes...`;
      } else {
        // For food, show the selected cuisine
        const cuisine = selectedCuisine || selectedRecipeCategory || 'delicious';
        return `Generating your ${cuisine} recipes...`;
      }
    };

    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#007AFF" />
        <Text style={styles.loadingText}>{getLoadingMessage()}</Text>
        <Text style={styles.loadingSubtext}>Creating detailed, {selectedSkillLevel}-level instructions</Text>
        
        <TouchableOpacity 
          style={styles.cancelButton}
          onPress={() => {
            setLoading(false);
            Alert.alert(
              'Recipe Generation Cancelled',
              'Would you like to try a mock recipe instead?',
              [
                { text: 'Try Mock Recipe', onPress: () => generateMockRecipe() },
                { text: 'Go Back', onPress: () => navigation.goBack() },
                { text: 'Retry', onPress: () => { setLoading(true); generateRecipe(); } }
              ]
            );
          }}
        >
          <Text style={styles.cancelButtonText}>Cancel</Text>
        </TouchableOpacity>
      </View>
    );
  }

  // Show preferences selection screen
  if (showPreferences) {
    return (
      <View style={styles.container}>
        <CuisineSelector
          selectedCuisine={selectedCuisine}
          onCuisineSelect={setSelectedCuisine}
          visible={showCuisineSelector}
          onClose={() => setShowCuisineSelector(false)}
        />
        
        <SkillLevelSelector
          selectedSkillLevel={selectedSkillLevel}
          onSkillLevelSelect={setSelectedSkillLevel}
          visible={showSkillLevelSelector}
          onClose={() => setShowSkillLevelSelector(false)}
        />
        
        <DietaryRestrictionsSelector
          selectedRestrictions={dietaryRestrictions}
          onRestrictionsChange={setDietaryRestrictions}
          visible={showDietarySelector}
          onClose={() => setShowDietarySelector(false)}
        />

        <MealTypeSelector
          selectedMealType={selectedMealType}
          onMealTypeSelect={setSelectedMealType}
          visible={showMealTypeSelector}
          onClose={() => setShowMealTypeSelector(false)}
        />

        <RecipeCategorySelector
          selectedCategory={selectedRecipeCategory}
          onCategorySelect={setSelectedRecipeCategory}
          visible={showRecipeCategorySelector}
          onClose={() => setShowRecipeCategorySelector(false)}
          isFruitDetected={isFruitDetected}
        />

        <View style={styles.preferencesContainer}>
          <View style={styles.header}>
            <Text style={styles.title}>Recipe Preferences</Text>
            <Text style={styles.subtitle}>Customize your cooking experience</Text>
          </View>

          <ScrollView style={styles.preferencesScroll}>
            {/* Meal Type Selection - Always shown */}
            <View style={styles.preferenceSection}>
              <Text style={styles.sectionTitle}>Meal Type</Text>
              <TouchableOpacity
                style={styles.preferenceButton}
                onPress={() => setShowMealTypeSelector(true)}
              >
                <Text style={styles.preferenceButtonText}>
                  {selectedMealType === 'breakfast' && '🌅 Breakfast'}
                  {selectedMealType === 'lunch' && '☀️ Lunch'}
                  {selectedMealType === 'dinner' && '🌙 Dinner'}
                  {selectedMealType === 'snack' && '🍿 Snack'}
                </Text>
                <Text style={styles.preferenceArrow}>→</Text>
              </TouchableOpacity>
            </View>

            {/* Recipe Category Selection - Context-aware */}
            <View style={styles.preferenceSection}>
              <Text style={styles.sectionTitle}>
                {isFruitDetected ? 'Recipe Type' : 'Cuisine Style'}
              </Text>
              <TouchableOpacity
                style={styles.preferenceButton}
                onPress={() => setShowRecipeCategorySelector(true)}
              >
                <Text style={styles.preferenceButtonText}>
                  {isFruitDetected ? (
                    <>
                      {selectedRecipeCategory === 'smoothie' && '🥤 Smoothie'}
                      {selectedRecipeCategory === 'dessert' && '🍰 Dessert'}
                    </>
                  ) : (
                    <>
                      {selectedRecipeCategory === 'indian' && '🇮🇳 Indian'}
                      {selectedRecipeCategory === 'italian' && '🇮🇹 Italian'}
                      {selectedRecipeCategory === 'thai' && '🇹🇭 Thai'}
                      {selectedRecipeCategory === 'mediterranean' && '🇬🇷 Mediterranean'}
                      {selectedRecipeCategory === 'mexican' && '🇲🇽 Mexican'}
                    </>
                  )}
                </Text>
                <Text style={styles.preferenceArrow}>→</Text>
              </TouchableOpacity>
              {isFruitDetected && (
                <View style={styles.fruitDetectedBadge}>
                  <Text style={styles.fruitDetectedText}>🍎 Fruits detected - showing fruit recipes</Text>
                </View>
              )}
            </View>

            {/* Legacy Cuisine Selection - Hidden when fruits detected */}
            {!isFruitDetected && (
              <View style={styles.preferenceSection}>
                <Text style={styles.sectionTitle}>Cuisine Style (Legacy)</Text>
                <TouchableOpacity
                style={styles.preferenceButton}
                onPress={() => setShowCuisineSelector(true)}
              >
                <Text style={styles.preferenceButtonText}>
                  {selectedCuisine === 'indian' && '🇮🇳 Indian'}
                  {selectedCuisine === 'italian' && '🇮🇹 Italian'}
                  {selectedCuisine === 'thai' && '🇹🇭 Thai'}
                  {selectedCuisine === 'mediterranean' && '🇬🇷 Mediterranean'}
                  {selectedCuisine === 'mexican' && '🇲🇽 Mexican'}
                  {selectedCuisine === 'asian' && '🥢 Asian'}
                </Text>
                <Text style={styles.preferenceArrow}>→</Text>
              </TouchableOpacity>
              </View>
            )}

            {/* Skill Level Selection */}
            <View style={styles.preferenceSection}>
              <Text style={styles.sectionTitle}>Cooking Level</Text>
              <TouchableOpacity
                style={styles.preferenceButton}
                onPress={() => setShowSkillLevelSelector(true)}
              >
                <Text style={styles.preferenceButtonText}>
                  {selectedSkillLevel === 'beginner' && '👶 Beginner'}
                  {selectedSkillLevel === 'intermediate' && '👨‍🍳 Intermediate'}
                  {selectedSkillLevel === 'advanced' && '🔥 Advanced'}
                </Text>
                <Text style={styles.preferenceArrow}>→</Text>
              </TouchableOpacity>
            </View>

            {/* Dietary Restrictions */}
            <View style={styles.preferenceSection}>
              <Text style={styles.sectionTitle}>Dietary Preferences</Text>
              <TouchableOpacity
                style={styles.preferenceButton}
                onPress={() => setShowDietarySelector(true)}
              >
                <Text style={styles.preferenceButtonText}>
                  {dietaryRestrictions.length === 0 
                    ? 'None selected' 
                    : `${dietaryRestrictions.length} restriction${dietaryRestrictions.length > 1 ? 's' : ''} selected`
                  }
                </Text>
                <Text style={styles.preferenceArrow}>→</Text>
              </TouchableOpacity>
              {dietaryRestrictions.length > 0 && (
                <View style={styles.restrictionsPreview}>
                  {dietaryRestrictions.slice(0, 3).map((restriction, index) => (
                    <View key={restriction} style={styles.restrictionTag}>
                      <Text style={styles.restrictionTagText}>
                        {restriction === 'vegan' && '🌱 Vegan'}
                        {restriction === 'vegetarian' && '🥬 Vegetarian'}
                        {restriction === 'gluten-free' && '🌾 Gluten-Free'}
                        {restriction === 'dairy-free' && '🥛 Dairy-Free'}
                        {restriction === 'low-sodium' && '🧂 Low Sodium'}
                        {restriction === 'keto' && '🥑 Keto'}
                      </Text>
                    </View>
                  ))}
                  {dietaryRestrictions.length > 3 && (
                    <Text style={styles.moreRestrictionsText}>
                      +{dietaryRestrictions.length - 3} more
                    </Text>
                  )}
                </View>
              )}
            </View>

            {/* Servings */}
            <View style={styles.preferenceSection}>
              <Text style={styles.sectionTitle}>Servings: {servings}</Text>
              <View style={styles.servingsContainer}>
                <TouchableOpacity
                  style={styles.servingsButton}
                  onPress={() => servings > 1 && setServings && setServings(servings - 1)}
                >
                  <Text style={styles.servingsButtonText}>-</Text>
                </TouchableOpacity>
                <Text style={styles.servingsText}>{servings}</Text>
                <TouchableOpacity
                  style={styles.servingsButton}
                  onPress={() => servings < 8 && setServings && setServings(servings + 1)}
                >
                  <Text style={styles.servingsButtonText}>+</Text>
                </TouchableOpacity>
              </View>
            </View>
          </ScrollView>

          <TouchableOpacity
            style={styles.generateButton}
            onPress={() => {
              setShowPreferences(false);
              setLoading(true);
              generateRecipe();
            }}
          >
            <Text style={styles.generateButtonText}>
              Generate {(isFruitDetected ? selectedRecipeCategory : selectedCuisine).charAt(0).toUpperCase() + (isFruitDetected ? selectedRecipeCategory : selectedCuisine).slice(1)} Recipes
            </Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  }

  if (showRecipeSelection && recipeOptions.length > 0) {
    return (
      <View style={styles.container}>
        <View style={styles.header}>
          <View style={styles.headerTop}>
            <TouchableOpacity 
              style={styles.backButton}
              onPress={() => navigation.navigate('Camera')}
            >
              <Text style={styles.backButtonText}>📷 New Scan</Text>
            </TouchableOpacity>
            
            {userName && (
              <View style={styles.userSection}>
                <Text style={styles.userName}>Hi, {userName}!</Text>
              </View>
            )}
          </View>
          
          <Text style={styles.title}>Choose Your Recipe</Text>
          <Text style={styles.subtitle}>We created {recipeOptions.length} options for your ingredients</Text>
        </View>

        <ScrollView style={styles.scrollView} contentContainerStyle={styles.scrollContent}>
          {recipeOptions.map((option, index) => (
            <TouchableOpacity
              key={option.id}
              style={styles.recipeOption}
              onPress={() => handleRecipeSelection(option, index)}
            >
              <Text style={styles.recipeOptionTitle}>{option.title}</Text>
              <View style={styles.tagsContainer}>
                {option.tags.map((tag, tagIndex) => (
                  <View key={tagIndex} style={styles.tag}>
                    <Text style={styles.tagText}>{tag}</Text>
                  </View>
                ))}
              </View>
              <Text style={styles.recipeOptionArrow}>→</Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>
    );
  }

  if (!recipe) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>Failed to generate recipe</Text>
        <TouchableOpacity style={styles.retryButton} onPress={generateRecipe}>
          <Text style={styles.retryButtonText}>Try Again</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <ScrollView 
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={true}
        bounces={true}
        scrollEnabled={true}
        nestedScrollEnabled={true}
      >
      <View style={styles.header}>
        <View style={styles.headerTop}>
          <View style={styles.headerButtons}>
            <TouchableOpacity 
              style={styles.backButton}
              onPress={handleBackToRecipeList}
            >
              <Text style={styles.backButtonText}>
                {recipeOptions.length > 1 ? '← Back to Recipes' : '📷 New Scan'}
              </Text>
            </TouchableOpacity>
            
            <TouchableOpacity 
              style={[styles.backButton, styles.newScanButton]}
              onPress={() => navigation.navigate('Camera')}
            >
              <Text style={styles.backButtonText}>📷 New Scan</Text>
            </TouchableOpacity>
          </View>
          
          {userName && (
            <View style={styles.userSection}>
              <Text style={styles.userName}>Hi, {userName}!</Text>
            </View>
          )}
        </View>
        
        <Text style={styles.title}>{recipe.title}</Text>
        
        {/* Time & Yield Section */}
        <View style={styles.timeYieldSection}>
          <Text style={styles.timeYieldTitle}>Time & Yield</Text>
          <Text style={styles.timeYieldText}>
            Total time: {recipe.estimated_time || '25 min'} (Prep 5, Cook 20)
          </Text>
          <Text style={styles.timeYieldText}>Servings: {recipe.servings}</Text>
        </View>
        
        <View style={styles.tagsContainer}>
          {recipe.tags.map((tag, index) => (
            <View key={index} style={styles.tag}>
              <Text style={styles.tagText}>{tag}</Text>
            </View>
          ))}
        </View>
      </View>

      {nutrition && (
        <View style={styles.nutritionCard}>
          <Text style={styles.sectionTitle}>Nutrition (per serving, approx)</Text>
          <View style={styles.nutritionList}>
            <Text style={styles.nutritionText}>
              <Text style={styles.nutritionLabel}>Calories: </Text>
              <Text style={styles.nutritionValue}>{nutrition.per_serving.kcal} kcal</Text>
            </Text>
            <Text style={styles.nutritionText}>
              <Text style={styles.nutritionLabel}>Protein: </Text>
              <Text style={styles.nutritionValue}>{nutrition.per_serving.protein_g} g</Text>
            </Text>
            <Text style={styles.nutritionText}>
              <Text style={styles.nutritionLabel}>Carbs: </Text>
              <Text style={styles.nutritionValue}>{nutrition.per_serving.carb_g} g</Text>
              {nutrition.per_serving.fiber_g && (
                <Text style={styles.nutritionSubtext}> (Fiber {nutrition.per_serving.fiber_g} g, Sugar {nutrition.per_serving.sugar_g || 'N/A'} g)</Text>
              )}
            </Text>
            <Text style={styles.nutritionText}>
              <Text style={styles.nutritionLabel}>Fat: </Text>
              <Text style={styles.nutritionValue}>{nutrition.per_serving.fat_g} g</Text>
              {nutrition.per_serving.saturated_fat_g && (
                <Text style={styles.nutritionSubtext}> (Sat {nutrition.per_serving.saturated_fat_g} g)</Text>
              )}
            </Text>
            {nutrition.per_serving.sodium_mg && (
              <Text style={styles.nutritionText}>
                <Text style={styles.nutritionLabel}>Sodium: </Text>
                <Text style={styles.nutritionValue}>{nutrition.per_serving.sodium_mg} mg</Text>
              </Text>
            )}
            {nutrition.per_serving.iron_mg && (
              <Text style={styles.nutritionText}>
                <Text style={styles.nutritionLabel}>Notable micros: </Text>
                <Text style={styles.nutritionValue}>Iron {nutrition.per_serving.iron_mg} mg, Vit A {nutrition.per_serving.vit_a_iu || 'N/A'} IU</Text>
              </Text>
            )}
          </View>
        </View>
      )}

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Ingredients</Text>
        {recipe.ingredients.map((ingredient, index) => (
          <View key={index} style={styles.ingredientItem}>
            <Text style={styles.ingredientName}>{ingredient.name}</Text>
            <Text style={styles.ingredientAmount}>
              {ingredient.grams}g ({Math.round(ingredient.grams * 0.035274)} oz)
              {ingredient.notes && <Text style={styles.ingredientNotes}> — {ingredient.notes}</Text>}
            </Text>
          </View>
        ))}
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Cooking Instructions</Text>
        <EnhancedRecipeSteps
          steps={recipe.steps}
          skillLevel={selectedSkillLevel}
          cuisine={selectedCuisine}
          onStepComplete={(stepIndex, isComplete) => {
            }}
        />
      </View>

      {recipe.substitutions && recipe.substitutions.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Substitutions</Text>
          {recipe.substitutions.map((sub, index) => (
            <Text key={index} style={styles.substitutionText}>• {sub}</Text>
          ))}
        </View>
      )}

      {recipe.warnings && recipe.warnings.length > 0 && (
        <View style={styles.warningSection}>
          <Text style={styles.sectionTitle}>Allergens & Notes</Text>
          {recipe.warnings.map((warning, index) => (
            <Text key={index} style={styles.warningText}>• {warning}</Text>
          ))}
          <Text style={styles.warningText}>• Storage: Keep in an airtight container in the fridge for up to 2 days. Reheat in a pan or microwave.</Text>
        </View>
      )}

      {/* Shopping List Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Shopping List (if needed)</Text>
        {recipe.ingredients
          .filter(ing => !['salt', 'pepper', 'oil', 'water'].includes(ing.name.toLowerCase()))
          .map((ingredient, index) => (
            <Text key={index} style={styles.shoppingItem}>• {ingredient.name}</Text>
          ))}
        <Text style={styles.shoppingItem}>• Basic seasonings (salt, pepper, oil)</Text>
      </View>

      <View style={styles.actionButtons}>
        <TouchableOpacity style={styles.actionButton} onPress={handleShare}>
          <Text style={styles.actionButtonText}>📤 Share Recipe</Text>
        </TouchableOpacity>
        
        <TouchableOpacity style={styles.actionButton} onPress={handleLogMeal}>
          <Text style={styles.actionButtonText}>📝 Log Meal</Text>
        </TouchableOpacity>
        
        <TouchableOpacity style={[styles.actionButton, styles.primaryButton]} onPress={handleNewScan}>
          <Text style={[styles.actionButtonText, styles.primaryButtonText]}>📷 New Scan</Text>
        </TouchableOpacity>
      </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    height: '100vh', // Full viewport height for web
    overflow: 'hidden', // Prevent body scroll on web
  },
  scrollView: {
    flex: 1,
    width: '100%',
    // Web-specific scrolling fixes
    WebkitOverflowScrolling: 'touch', // Smooth scrolling on iOS Safari
    overflowY: 'scroll', // Enable vertical scrolling on web
  },
  scrollContent: {
    paddingBottom: 150, // Extra padding at bottom for scrolling
    flexGrow: 1, // Allow content to grow
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
  },
  loadingText: {
    marginTop: 10,
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  loadingSubtext: {
    marginTop: 5,
    fontSize: 14,
    color: '#666',
  },
  cancelButton: {
    marginTop: 30,
    backgroundColor: '#ff4444',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 8,
  },
  cancelButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
    padding: 20,
  },
  errorText: {
    fontSize: 18,
    color: '#666',
    marginBottom: 20,
  },
  retryButton: {
    backgroundColor: '#007AFF',
    padding: 15,
    borderRadius: 8,
  },
  retryButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  header: {
    backgroundColor: 'white',
    padding: 20,
    marginBottom: 10,
  },
  headerTop: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  headerButtons: {
    flexDirection: 'row',
    gap: 10,
  },
  userSection: {
    alignItems: 'flex-end',
  },
  userName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  backButton: {
    backgroundColor: '#007AFF',
    padding: 10,
    borderRadius: 8,
    flex: 1,
    marginRight: 10,
  },
  newScanButton: {
    backgroundColor: '#28a745',
    marginRight: 0,
    marginLeft: 10,
  },
  backButtonText: {
    color: 'white',
    fontSize: 14,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  timeYieldSection: {
    backgroundColor: '#f8f9fa',
    padding: 15,
    borderRadius: 8,
    marginBottom: 15,
  },
  timeYieldTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  timeYieldText: {
    fontSize: 14,
    color: '#666',
    marginBottom: 2,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
  },
  tagsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 10,
  },
  tag: {
    backgroundColor: '#e3f2fd',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    marginRight: 8,
    marginBottom: 4,
  },
  tagText: {
    fontSize: 12,
    color: '#1976d2',
    fontWeight: '500',
  },
  servings: {
    fontSize: 16,
    color: '#666',
  },
  nutritionCard: {
    backgroundColor: 'white',
    padding: 20,
    marginBottom: 10,
  },
  nutritionList: {
    gap: 8,
  },
  nutritionText: {
    fontSize: 16,
    color: '#333',
    lineHeight: 22,
  },
  nutritionLabel: {
    fontWeight: 'bold',
    color: '#333',
  },
  nutritionValue: {
    color: '#007AFF',
    fontWeight: '600',
  },
  nutritionSubtext: {
    fontSize: 14,
    color: '#666',
    fontWeight: 'normal',
  },
  section: {
    backgroundColor: 'white',
    padding: 20,
    marginBottom: 10,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  ingredientItem: {
    marginBottom: 12,
    paddingBottom: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  ingredientName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    textTransform: 'capitalize',
  },
  ingredientAmount: {
    fontSize: 14,
    color: '#666',
    marginTop: 2,
  },
  ingredientNotes: {
    fontStyle: 'italic',
    color: '#888',
  },
  stepItem: {
    marginBottom: 15,
  },
  stepNumber: {
    fontWeight: 'bold',
    color: '#007AFF',
  },
  stepText: {
    fontSize: 16,
    color: '#333',
    lineHeight: 24,
  },
  substitutionText: {
    fontSize: 14,
    color: '#666',
    marginBottom: 5,
    lineHeight: 20,
  },
  warningSection: {
    backgroundColor: '#fff3cd',
    padding: 20,
    marginBottom: 10,
    borderLeftWidth: 4,
    borderLeftColor: '#ffc107',
  },
  warningText: {
    fontSize: 14,
    color: '#856404',
    marginBottom: 5,
    lineHeight: 20,
  },
  actionButtons: {
    padding: 20,
    gap: 10,
  },
  actionButton: {
    backgroundColor: 'white',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#007AFF',
  },
  actionButtonText: {
    fontSize: 16,
    color: '#007AFF',
    fontWeight: '500',
  },
  primaryButton: {
    backgroundColor: '#007AFF',
  },
  primaryButtonText: {
    color: 'white',
  },
  shoppingItem: {
    fontSize: 14,
    color: '#333',
    marginBottom: 4,
    lineHeight: 20,
  },
  subtitle: {
    fontSize: 14,
    color: '#666',
    marginBottom: 10,
  },
  recipeOption: {
    backgroundColor: 'white',
    padding: 20,
    marginBottom: 10,
    borderRadius: 8,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  recipeOptionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    flex: 1,
  },
  recipeOptionArrow: {
    fontSize: 20,
    color: '#007AFF',
    marginLeft: 10,
  },
  
  // Preferences Screen Styles
  preferencesContainer: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  preferencesScroll: {
    flex: 1,
    padding: 16,
  },
  preferenceSection: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#212529',
    marginBottom: 12,
  },
  preferenceButton: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#f8f9fa',
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#e9ecef',
  },
  preferenceButtonText: {
    fontSize: 16,
    color: '#495057',
    fontWeight: '500',
  },
  preferenceArrow: {
    fontSize: 16,
    color: '#6c757d',
  },
  servingsContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  servingsButton: {
    backgroundColor: '#007AFF',
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  servingsButtonText: {
    color: '#fff',
    fontSize: 20,
    fontWeight: 'bold',
  },
  servingsText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#212529',
    marginHorizontal: 20,
  },
  generateButton: {
    backgroundColor: '#28a745',
    margin: 16,
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 5,
  },
  generateButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  restrictionsPreview: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginTop: 8,
  },
  restrictionTag: {
    backgroundColor: '#17a2b8',
    borderRadius: 12,
    paddingHorizontal: 8,
    paddingVertical: 4,
    marginRight: 6,
    marginBottom: 4,
  },
  restrictionTagText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  moreRestrictionsText: {
    fontSize: 12,
    color: '#6c757d',
    alignSelf: 'center',
    marginLeft: 4,
  },
  
  // New styles for meal type and fruit detection
  fruitDetectedBadge: {
    backgroundColor: '#e8f5e8',
    borderRadius: 20,
    paddingHorizontal: 12,
    paddingVertical: 6,
    marginTop: 8,
    alignSelf: 'flex-start',
  },
  fruitDetectedText: {
    fontSize: 12,
    color: '#2d5a2d',
    fontWeight: '600',
  },
});