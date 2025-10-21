import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  Alert,
  ActivityIndicator,
  Image,
  TextInput,
} from 'react-native';
import { apiService } from '../services/api';
import { authService } from '../services/auth';
import { DIETARY_PREFERENCES, CUISINE_TYPES, COMMON_ALLERGENS } from '../utils/constants';
import { detectFruits } from '../utils/ingredientDetection';

export default function ConfirmScreen({ route, navigation }) {
  const { scanId, imageUri, detectedItems } = route.params;
  const [loading, setLoading] = useState(true);
  const [items, setItems] = useState([]);
  const [servings, setServings] = useState(2);
  const [selectedDiets, setSelectedDiets] = useState([]);
  const [selectedAllergens, setSelectedAllergens] = useState([]);
  const [customDiet, setCustomDiet] = useState('');
  const [newIngredientName, setNewIngredientName] = useState('');
  const [newIngredientGrams, setNewIngredientGrams] = useState('100');
  const [userName, setUserName] = useState('');
  
  // New preference states
  const [selectedMealType, setSelectedMealType] = useState('lunch');
  const [selectedRecipeType, setSelectedRecipeType] = useState('international'); // Default to neutral value
  const [selectedCookingLevel, setSelectedCookingLevel] = useState('intermediate');
  const [isFruitDetected, setIsFruitDetected] = useState(false);

  useEffect(() => {
    loadUserInfo();
    loadScanResults();
  }, []);

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

  const loadScanResults = async () => {
    try {
      // Removed intelligent fallback - use real API results only
      
      // Only use fallback for truly mock scan IDs
      if (scanId.startsWith('mock_') || scanId.startsWith('manual_') || scanId.startsWith('test_')) {
        const mockItems = [
          { label: 'unknown food', fdc_id: '', confidence: 0.5, grams_est: 100, confirmed: true },
        ];
        setItems(mockItems);
        setLoading(false);
        return;
      }
      
      // Try to get real scan results from API
      const result = await apiService.getScan(scanId);
      
      if (result.success && result.data) {
        if (result.data.items && result.data.items.length > 0) {
          // Auto-confirm the first ingredient for better UX and normalize field names
          const itemsWithFirstConfirmed = result.data.items.map((item, index) => ({
            ...item,
            grams: item.grams || item.grams_est || 100, // Normalize grams field
            grams_est: item.grams_est || item.grams || 100, // Keep both for compatibility
            manually_added: false, // Detected items are not manually added
            confirmed: index === 0 // Auto-confirm first ingredient
          }));
          setItems(itemsWithFirstConfirmed);
          
          // Detect fruits and set appropriate recipe type
          const fruitsDetected = detectFruits(itemsWithFirstConfirmed);
          setIsFruitDetected(fruitsDetected);
          if (fruitsDetected) {
            setSelectedRecipeType('smoothie');
          }
        } else if (result.data.status === 'processing') {
          // Wait a bit and try again
          setTimeout(() => {
            loadScanResults();
          }, 2000);
          return;
        } else {
          // Use generic fallback
          const mockItems = [
            { label: 'unknown food item', fdc_id: '', confidence: 0.5, grams_est: 100, confirmed: true },
          ];
          setItems(mockItems);
        }
      } else {
        // Check if we have detected items from the scan response
        if (detectedItems && detectedItems.length > 0) {
          // Auto-confirm the first ingredient for better UX and normalize field names
          const itemsWithFirstConfirmed = detectedItems.map((item, index) => ({
            ...item,
            grams: item.grams || item.grams_est || 100, // Normalize grams field
            grams_est: item.grams_est || item.grams || 100, // Keep both for compatibility
            manually_added: false, // Detected items are not manually added
            confirmed: index === 0 // Auto-confirm first ingredient
          }));
          setItems(itemsWithFirstConfirmed);
        } else {
          // Show detailed error to user
          const errorMsg = result.error || 'Unknown error';
          Alert.alert('Detection Failed', `Real AI detection failed: ${errorMsg}\n\nUsing fallback detection for now.`);
          
          // Use generic fallback
          const mockItems = [
            { label: 'unknown food item', fdc_id: '', confidence: 0.5, grams_est: 100, confirmed: true },
          ];
          setItems(mockItems);
        }
      }
      
      setLoading(false);
    } catch (error) {
      // Show error instead of fallback
      Alert.alert('Error', 'Failed to load scan results: ' + error.message);
      setItems([]);
      setLoading(false);
    }
  };

  const updateItemGrams = (index, grams) => {
    const updatedItems = [...items];
    // Update both fields for compatibility
    const gramsValue = parseFloat(grams) || 0;
    updatedItems[index].grams = gramsValue;
    updatedItems[index].grams_est = gramsValue;
    setItems(updatedItems);
  };

  const toggleItemConfirmed = (index) => {
    const updatedItems = [...items];
    updatedItems[index].confirmed = !updatedItems[index].confirmed;
    setItems(updatedItems);
  };

  const togglePreference = (item, list, setList) => {
    if (list.includes(item)) {
      setList(list.filter(i => i !== item));
    } else {
      setList([...list, item]);
    }
  };

  const addCustomDiet = () => {
    if (customDiet.trim() && !selectedDiets.includes(customDiet.trim())) {
      setSelectedDiets([...selectedDiets, customDiet.trim()]);
      setCustomDiet('');
    }
  };



  const addNewIngredient = () => {
    if (newIngredientName.trim()) {
      const newItem = {
        label: newIngredientName.trim(),
        fdc_id: `manual_${Date.now()}`, // Generate a unique ID for manual ingredients
        confidence: 1.0, // Manual ingredients have 100% confidence
        grams: parseFloat(newIngredientGrams) || 100,
        confirmed: true, // Auto-confirm manual ingredients
        manually_added: true // Flag to identify manual ingredients
      };
      setItems([...items, newItem]);
      setNewIngredientName('');
      setNewIngredientGrams('100');
    }
  };

  const handleConfirm = async () => {
    const confirmedItems = items.filter(item => item.confirmed);
    
    if (confirmedItems.length === 0) {
      Alert.alert('Error', 'Please confirm at least one ingredient');
      return;
    }

    setLoading(true);

    try {
      // Prepare confirmation data
      const confirmationData = {
        items: confirmedItems.map(item => ({
          fdc_id: item.fdc_id,
          label: item.label,
          grams: item.grams || item.grams_est,
          confirmed: true,
          manually_added: item.manually_added || false,
        })),
        diets: selectedDiets,
        cuisines: isFruitDetected ? [] : [selectedRecipeType], // Use recipe type as cuisine for regular food
        allergens: selectedAllergens,
        servings: servings,
      };

      // Call the actual API to confirm the scan
      const confirmResponse = await apiService.confirmScan(scanId, confirmationData.items, {
        diets: confirmationData.diets,
        cuisines: confirmationData.cuisines,
        allergens: confirmationData.allergens,
        servings: confirmationData.servings
      });
      
      // Even if confirmation fails (e.g., already confirmed), still navigate to recipe
      if (!confirmResponse.success) {
        // Don't throw error, just log it and continue
      }
      
      // Navigate to recipe screen
      const navigationPreferences = {
        diets: selectedDiets,
        cuisines: isFruitDetected ? [] : [selectedRecipeType], // Use recipe type as cuisine for regular food
        allergens: selectedAllergens,
        mealType: selectedMealType,
        recipeType: selectedRecipeType,
        cookingLevel: selectedCookingLevel,
        isFruitDetected: isFruitDetected,
      };
      
      console.log('🚀 Navigating to RecipeScreen with preferences:', navigationPreferences);
      
      navigation.navigate('Recipe', { 
        scanId, 
        confirmedItems,
        servings,
        preferences: navigationPreferences
      });

    } catch (error) {
      // Still try to navigate to recipe screen with current data
      const errorNavigationPreferences = {
        diets: selectedDiets,
        cuisines: isFruitDetected ? [] : [selectedRecipeType], // Use recipe type as cuisine for regular food
        allergens: selectedAllergens,
        mealType: selectedMealType,
        recipeType: selectedRecipeType,
        cookingLevel: selectedCookingLevel,
        isFruitDetected: isFruitDetected,
      };
      
      console.log('🚨 Error case - Navigating to RecipeScreen with preferences:', errorNavigationPreferences);
      
      navigation.navigate('Recipe', { 
        scanId, 
        confirmedItems: items.filter(item => item.confirmed),
        servings,
        preferences: errorNavigationPreferences
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading && items.length === 0) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#007AFF" />
        <Text style={styles.loadingText}>Processing your scan...</Text>
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
        <Text style={styles.headerTitle}>Confirm Ingredients</Text>
        {userName && (
          <View style={styles.userSection}>
            <Text style={styles.userName}>Hi, {userName}!</Text>
          </View>
        )}
      </View>
      
      <View style={styles.imageContainer}>
        <Image source={{ uri: imageUri }} style={styles.image} />
        <Text style={styles.imageLabel}>Scanned Image</Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Detected Ingredients</Text>
        <Text style={styles.sectionSubtitle}>✓ Check ingredients to include • Adjust quantities as needed</Text>
        
        {/* Debug info */}
        <Text style={styles.debugText}>Scan ID: {scanId}</Text>
        <Text style={styles.debugText}>Items count: {items.length}</Text>
        
        {items.length === 0 ? (
          <Text style={styles.noItemsText}>No ingredients detected yet...</Text>
        ) : (
          items.map((item, index) => (
          <View key={index} style={styles.ingredientItem}>
            <View style={styles.ingredientHeader}>
              <TouchableOpacity
                style={styles.checkbox}
                onPress={() => toggleItemConfirmed(index)}
              >
                <Text style={styles.checkboxText}>
                  {item.confirmed ? '✓' : '○'}
                </Text>
              </TouchableOpacity>
              <View style={styles.ingredientInfo}>
                <Text style={styles.ingredientName}>
                  {item.label} {item.manual && <Text style={styles.manualTag}>(Added)</Text>}
                </Text>
                <Text style={styles.ingredientConfidence}>
                  {item.manual ? 'Manually added' : `Confidence: ${Math.round(item.confidence * 100)}%`}
                </Text>
              </View>
            </View>
            <View style={styles.gramsContainer}>
              <Text style={styles.gramsLabel}>Grams:</Text>
              <TextInput
                style={styles.gramsInput}
                value={(item.grams || item.grams_est || 0).toString()}
                onChangeText={(text) => updateItemGrams(index, text)}
                keyboardType="numeric"
                placeholder="0"
              />
            </View>
          </View>
          ))
        )}
        
        {/* Add New Ingredient Section */}
        <View style={styles.addIngredientSection}>
          <Text style={styles.addIngredientTitle}>Add Missing Ingredient</Text>
          <View style={styles.addIngredientForm}>
            <TextInput
              style={styles.addIngredientInput}
              placeholder="Ingredient name (e.g., onion, garlic)"
              value={newIngredientName}
              onChangeText={setNewIngredientName}
            />
            <View style={styles.addIngredientGramsContainer}>
              <TextInput
                style={styles.addIngredientGramsInput}
                placeholder="Grams"
                value={newIngredientGrams}
                onChangeText={setNewIngredientGrams}
                keyboardType="numeric"
              />
              <TouchableOpacity
                style={styles.addIngredientButton}
                onPress={addNewIngredient}
              >
                <Text style={styles.addIngredientButtonText}>+ Add</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </View>

      {/* Quick action buttons - placed here for visibility */}

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Recipe Preferences</Text>
        
        <View style={styles.servingsContainer}>
          <Text style={styles.servingsLabel}>Servings:</Text>
          <View style={styles.servingsControls}>
            <TouchableOpacity
              style={styles.servingsButton}
              onPress={() => setServings(Math.max(1, servings - 1))}
            >
              <Text style={styles.servingsButtonText}>-</Text>
            </TouchableOpacity>
            <Text style={styles.servingsValue}>{servings}</Text>
            <TouchableOpacity
              style={styles.servingsButton}
              onPress={() => setServings(servings + 1)}
            >
              <Text style={styles.servingsButtonText}>+</Text>
            </TouchableOpacity>
          </View>
        </View>

        <Text style={styles.preferenceTitle}>Meal Type:</Text>
        <View style={styles.preferencesGrid}>
          {['Breakfast', 'Lunch', 'Dinner', 'Snack'].map((mealType) => (
            <TouchableOpacity
              key={mealType}
              style={[
                styles.preferenceChip,
                selectedMealType === mealType.toLowerCase() && styles.preferenceChipSelected
              ]}
              onPress={() => setSelectedMealType(mealType.toLowerCase())}
            >
              <Text style={[
                styles.preferenceChipText,
                selectedMealType === mealType.toLowerCase() && styles.preferenceChipTextSelected
              ]}>
                {mealType === 'Breakfast' && '🌅'} {mealType === 'Lunch' && '☀️'} {mealType === 'Dinner' && '🌙'} {mealType === 'Snack' && '🍿'} {mealType}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        <Text style={styles.preferenceTitle}>
          {isFruitDetected ? 'Recipe Type:' : 'Cuisine Type:'}
        </Text>
        <View style={styles.preferencesGrid}>
          {(isFruitDetected ? ['Smoothie', 'Dessert'] : ['Italian', 'Mexican', 'Asian', 'Indian', 'Mediterranean', 'American']).map((recipeType) => (
            <TouchableOpacity
              key={recipeType}
              style={[
                styles.preferenceChip,
                selectedRecipeType === recipeType.toLowerCase() && styles.preferenceChipSelected
              ]}
              onPress={() => {
                console.log('🔍 User selected recipe type:', recipeType.toLowerCase());
                setSelectedRecipeType(recipeType.toLowerCase());
              }}
            >
              <Text style={[
                styles.preferenceChipText,
                selectedRecipeType === recipeType.toLowerCase() && styles.preferenceChipTextSelected
              ]}>
                {recipeType === 'Smoothie' && '🥤'} {recipeType === 'Dessert' && '🍰'} 
                {recipeType === 'Italian' && '🇮🇹'} {recipeType === 'Mexican' && '🇲🇽'} 
                {recipeType === 'Asian' && '🥢'} {recipeType === 'Indian' && '🇮🇳'} 
                {recipeType === 'Mediterranean' && '🇬🇷'} {recipeType === 'American' && '🇺🇸'} {recipeType}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
        {isFruitDetected && (
          <Text style={styles.fruitDetectedText}>🍎 Fruits detected - showing fruit recipes</Text>
        )}

        <Text style={styles.preferenceTitle}>Cooking Level:</Text>
        <View style={styles.preferencesGrid}>
          {['Beginner', 'Intermediate', 'Advanced'].map((level) => (
            <TouchableOpacity
              key={level}
              style={[
                styles.preferenceChip,
                selectedCookingLevel === level.toLowerCase() && styles.preferenceChipSelected
              ]}
              onPress={() => setSelectedCookingLevel(level.toLowerCase())}
            >
              <Text style={[
                styles.preferenceChipText,
                selectedCookingLevel === level.toLowerCase() && styles.preferenceChipTextSelected
              ]}>
                {level === 'Beginner' && '👶'} {level === 'Intermediate' && '👨‍🍳'} {level === 'Advanced' && '🔥'} {level}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        <Text style={styles.preferenceTitle}>Dietary Preferences:</Text>
        <View style={styles.preferencesGrid}>
          {DIETARY_PREFERENCES.map((diet) => (
            <TouchableOpacity
              key={diet}
              style={[
                styles.preferenceChip,
                selectedDiets.includes(diet) && styles.preferenceChipSelected
              ]}
              onPress={() => togglePreference(diet, selectedDiets, setSelectedDiets)}
            >
              <Text style={[
                styles.preferenceChipText,
                selectedDiets.includes(diet) && styles.preferenceChipTextSelected
              ]}>
                {diet}
              </Text>
            </TouchableOpacity>
          ))}
          {/* Show selected custom diets */}
          {selectedDiets.filter(diet => !DIETARY_PREFERENCES.includes(diet)).map((diet) => (
            <TouchableOpacity
              key={diet}
              style={[styles.preferenceChip, styles.preferenceChipSelected, styles.customChip]}
              onPress={() => togglePreference(diet, selectedDiets, setSelectedDiets)}
            >
              <Text style={[styles.preferenceChipText, styles.preferenceChipTextSelected]}>
                {diet} ×
              </Text>
            </TouchableOpacity>
          ))}
        </View>
        
        {/* Add Custom Diet */}
        <View style={styles.customInputContainer}>
          <TextInput
            style={styles.customInput}
            placeholder="Add custom dietary preference"
            value={customDiet}
            onChangeText={setCustomDiet}
          />
          <TouchableOpacity
            style={styles.customAddButton}
            onPress={addCustomDiet}
          >
            <Text style={styles.customAddButtonText}>+ Add</Text>
          </TouchableOpacity>
        </View>


      </View>

      <TouchableOpacity
        style={[styles.confirmButton, loading && styles.confirmButtonDisabled]}
        onPress={handleConfirm}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator color="white" />
        ) : (
          <Text style={styles.confirmButtonText}>Generate Recipe</Text>
        )}
      </TouchableOpacity>
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
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    backgroundColor: 'white',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  userSection: {
    alignItems: 'flex-end',
  },
  userName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  scrollView: {
    flex: 1,
    width: '100%',
    height: '100%', // Ensure full height
    // Web-specific scrolling fixes
    WebkitOverflowScrolling: 'touch', // Smooth scrolling on iOS Safari
    overflowY: 'auto', // Enable vertical scrolling on web
    maxHeight: '80vh', // Limit height to viewport
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
    fontSize: 16,
    color: '#666',
  },
  imageContainer: {
    alignItems: 'center',
    padding: 20,
    backgroundColor: 'white',
    marginBottom: 10,
  },
  image: {
    width: 200,
    height: 150,
    borderRadius: 10,
  },
  imageLabel: {
    marginTop: 10,
    fontSize: 14,
    color: '#666',
  },
  section: {
    backgroundColor: 'white',
    padding: 20,
    marginBottom: 10,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 5,
    color: '#333',
  },
  sectionSubtitle: {
    fontSize: 14,
    color: '#666',
    marginBottom: 15,
  },
  debugText: {
    fontSize: 12,
    color: '#999',
    marginBottom: 10,
    fontStyle: 'italic',
  },
  noItemsText: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    padding: 20,
    backgroundColor: '#f9f9f9',
    borderRadius: 8,
  },
  ingredientItem: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 15,
    marginBottom: 10,
  },
  ingredientHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  checkbox: {
    width: 30,
    height: 30,
    borderRadius: 15,
    borderWidth: 2,
    borderColor: '#007AFF',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15,
  },
  checkboxText: {
    fontSize: 16,
    color: '#007AFF',
    fontWeight: 'bold',
  },
  ingredientInfo: {
    flex: 1,
  },
  ingredientName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    textTransform: 'capitalize',
  },
  ingredientConfidence: {
    fontSize: 12,
    color: '#666',
  },
  gramsContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  gramsLabel: {
    fontSize: 14,
    color: '#666',
    marginRight: 10,
  },
  gramsInput: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 5,
    padding: 8,
    width: 80,
    textAlign: 'center',
  },
  servingsContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
  },
  servingsLabel: {
    fontSize: 16,
    color: '#333',
    marginRight: 15,
  },
  servingsControls: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  servingsButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#007AFF',
    justifyContent: 'center',
    alignItems: 'center',
  },
  servingsButtonText: {
    color: 'white',
    fontSize: 20,
    fontWeight: 'bold',
  },
  servingsValue: {
    fontSize: 18,
    fontWeight: 'bold',
    marginHorizontal: 20,
    color: '#333',
  },
  preferenceTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 10,
    marginTop: 10,
    color: '#333',
  },
  preferencesGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
  },
  preferenceChip: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#007AFF',
    backgroundColor: 'white',
  },
  preferenceChipSelected: {
    backgroundColor: '#007AFF',
  },
  preferenceChipText: {
    fontSize: 12,
    color: '#007AFF',
  },
  preferenceChipTextSelected: {
    color: 'white',
  },
  confirmButton: {
    backgroundColor: '#007AFF',
    padding: 18,
    borderRadius: 10,
    alignItems: 'center',
    margin: 20,
  },
  confirmButtonDisabled: {
    backgroundColor: '#ccc',
  },
  confirmButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
  manualTag: {
    fontSize: 12,
    color: '#28a745',
    fontWeight: 'bold',
  },
  addIngredientSection: {
    marginTop: 20,
    padding: 15,
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#e9ecef',
  },
  addIngredientTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
  },
  addIngredientForm: {
    gap: 10,
  },
  addIngredientInput: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 5,
    padding: 12,
    fontSize: 16,
    backgroundColor: 'white',
  },
  addIngredientGramsContainer: {
    flexDirection: 'row',
    gap: 10,
  },
  addIngredientGramsInput: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 5,
    padding: 12,
    fontSize: 16,
    backgroundColor: 'white',
  },
  addIngredientButton: {
    backgroundColor: '#28a745',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 5,
    justifyContent: 'center',
  },
  addIngredientButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  customInputContainer: {
    flexDirection: 'row',
    marginTop: 10,
    gap: 10,
  },
  customInput: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 5,
    padding: 10,
    fontSize: 14,
    backgroundColor: 'white',
  },
  customAddButton: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 15,
    paddingVertical: 10,
    borderRadius: 5,
    justifyContent: 'center',
  },
  customAddButtonText: {
    color: 'white',
    fontSize: 14,
    fontWeight: 'bold',
  },
  customChip: {
    borderColor: '#28a745',
  },
  fruitDetectedText: {
    fontSize: 12,
    color: '#2d5a2d',
    fontWeight: '600',
    marginTop: 8,
    backgroundColor: '#e8f5e8',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
    alignSelf: 'flex-start',
  },
});