import React, { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Alert,
  Image,
  ScrollView,
  TextInput,
} from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import * as ImagePicker from 'expo-image-picker';

const Stack = createStackNavigator();

// Simple Sign In Screen
function SignInScreen({ navigation }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSignIn = () => {
    if (email && password) {
      navigation.navigate('Camera');
    } else {
      Alert.alert('Error', 'Please enter email and password');
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Aye Aye</Text>
      <Text style={styles.subtitle}>Scan ingredients, get recipes</Text>
      
      <TextInput
        style={styles.input}
        placeholder="Email"
        value={email}
        onChangeText={setEmail}
        keyboardType="email-address"
        autoCapitalize="none"
      />

      <TextInput
        style={styles.input}
        placeholder="Password"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
      />

      <TouchableOpacity style={styles.button} onPress={handleSignIn}>
        <Text style={styles.buttonText}>Sign In</Text>
      </TouchableOpacity>
    </View>
  );
}

// Camera Screen
function CameraScreen({ navigation }) {
  const [image, setImage] = useState(null);

  const takePhoto = async () => {
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permission needed', 'Camera permission is required');
      return;
    }

    const result = await ImagePicker.launchCameraAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [4, 3],
      quality: 0.8,
    });

    if (!result.canceled) {
      setImage(result.assets[0].uri);
      // Simulate processing delay
      setTimeout(() => {
        navigation.navigate('Confirm', { imageUri: result.assets[0].uri });
      }, 1000);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Scan Your Ingredients</Text>
      
      {image ? (
        <View style={styles.imageContainer}>
          <Image source={{ uri: image }} style={styles.image} />
          <Text style={styles.imageText}>Processing...</Text>
        </View>
      ) : (
        <View style={styles.placeholder}>
          <Text style={styles.placeholderText}>
            Take a photo of your ingredients
          </Text>
        </View>
      )}

      <TouchableOpacity style={styles.button} onPress={takePhoto}>
        <Text style={styles.buttonText}>📷 Take Photo</Text>
      </TouchableOpacity>
    </View>
  );
}

// Confirm Screen
function ConfirmScreen({ route, navigation }) {
  const { imageUri } = route.params;
  const [servings, setServings] = useState(2);

  // Mock detected ingredients
  const mockIngredients = [
    { name: 'Chicken Breast', grams: 450, confirmed: true },
    { name: 'Onion', grams: 150, confirmed: true },
    { name: 'Cilantro', grams: 20, confirmed: true },
  ];

  const generateRecipe = () => {
    navigation.navigate('Recipe', { 
      ingredients: mockIngredients,
      servings,
      imageUri 
    });
  };

  return (
    <ScrollView style={styles.container}>
      <Image source={{ uri: imageUri }} style={styles.image} />
      
      <Text style={styles.sectionTitle}>Detected Ingredients</Text>
      
      {mockIngredients.map((item, index) => (
        <View key={index} style={styles.ingredientItem}>
          <Text style={styles.ingredientName}>{item.name}</Text>
          <Text style={styles.ingredientGrams}>{item.grams}g</Text>
        </View>
      ))}

      <View style={styles.servingsContainer}>
        <Text style={styles.servingsLabel}>Servings: {servings}</Text>
        <View style={styles.servingsControls}>
          <TouchableOpacity
            style={styles.servingsButton}
            onPress={() => setServings(Math.max(1, servings - 1))}
          >
            <Text style={styles.servingsButtonText}>-</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.servingsButton}
            onPress={() => setServings(servings + 1)}
          >
            <Text style={styles.servingsButtonText}>+</Text>
          </TouchableOpacity>
        </View>
      </View>

      <TouchableOpacity style={styles.button} onPress={generateRecipe}>
        <Text style={styles.buttonText}>Generate Recipe</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

// Recipe Screen
function RecipeScreen({ route }) {
  const { ingredients, servings, imageUri } = route.params;

  const mockRecipe = {
    title: "Cilantro-Lime Chicken Skillet",
    steps: [
      "Season chicken with salt and pepper",
      "Heat oil in a large skillet",
      "Cook chicken 6-7 minutes per side",
      "Add diced onion, cook until soft",
      "Garnish with fresh cilantro",
      "Serve with lime wedges"
    ],
    nutrition: {
      calories: Math.round(685 / servings),
      protein: Math.round(75.2 / servings),
      carbs: Math.round(18.4 / servings),
      fat: Math.round(32.1 / servings),
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>{mockRecipe.title}</Text>
      <Text style={styles.subtitle}>Serves {servings}</Text>
      
      <Image source={{ uri: imageUri }} style={styles.image} />

      <View style={styles.nutritionCard}>
        <Text style={styles.sectionTitle}>Nutrition per serving</Text>
        <View style={styles.nutritionGrid}>
          <View style={styles.nutritionItem}>
            <Text style={styles.nutritionValue}>{mockRecipe.nutrition.calories}</Text>
            <Text style={styles.nutritionLabel}>Calories</Text>
          </View>
          <View style={styles.nutritionItem}>
            <Text style={styles.nutritionValue}>{mockRecipe.nutrition.protein}g</Text>
            <Text style={styles.nutritionLabel}>Protein</Text>
          </View>
          <View style={styles.nutritionItem}>
            <Text style={styles.nutritionValue}>{mockRecipe.nutrition.carbs}g</Text>
            <Text style={styles.nutritionLabel}>Carbs</Text>
          </View>
          <View style={styles.nutritionItem}>
            <Text style={styles.nutritionValue}>{mockRecipe.nutrition.fat}g</Text>
            <Text style={styles.nutritionLabel}>Fat</Text>
          </View>
        </View>
      </View>

      <Text style={styles.sectionTitle}>Ingredients</Text>
      {ingredients.map((item, index) => (
        <Text key={index} style={styles.ingredientText}>
          • {item.grams}g {item.name}
        </Text>
      ))}

      <Text style={styles.sectionTitle}>Instructions</Text>
      {mockRecipe.steps.map((step, index) => (
        <View key={index} style={styles.stepItem}>
          <Text style={styles.stepNumber}>{index + 1}</Text>
          <Text style={styles.stepText}>{step}</Text>
        </View>
      ))}
    </ScrollView>
  );
}

// Main App
export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="SignIn">
        <Stack.Screen 
          name="SignIn" 
          component={SignInScreen}
          options={{ headerShown: false }}
        />
        <Stack.Screen 
          name="Camera" 
          component={CameraScreen}
          options={{ title: 'Scan Ingredients' }}
        />
        <Stack.Screen 
          name="Confirm" 
          component={ConfirmScreen}
          options={{ title: 'Confirm Ingredients' }}
        />
        <Stack.Screen 
          name="Recipe" 
          component={RecipeScreen}
          options={{ title: 'Your Recipe' }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#f5f5f5',
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 10,
    color: '#333',
  },
  subtitle: {
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 30,
    color: '#666',
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    padding: 15,
    borderRadius: 8,
    marginBottom: 15,
    fontSize: 16,
    backgroundColor: 'white',
  },
  button: {
    backgroundColor: '#007AFF',
    padding: 18,
    borderRadius: 10,
    alignItems: 'center',
    marginVertical: 10,
  },
  buttonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
  placeholder: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'white',
    borderRadius: 10,
    borderWidth: 2,
    borderColor: '#ddd',
    borderStyle: 'dashed',
    margin: 20,
  },
  placeholderText: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
  },
  imageContainer: {
    alignItems: 'center',
    marginVertical: 20,
  },
  image: {
    width: 300,
    height: 200,
    borderRadius: 10,
    marginBottom: 10,
  },
  imageText: {
    fontSize: 16,
    color: '#666',
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginVertical: 15,
    color: '#333',
  },
  ingredientItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    padding: 15,
    backgroundColor: 'white',
    borderRadius: 8,
    marginBottom: 10,
  },
  ingredientName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  ingredientGrams: {
    fontSize: 16,
    color: '#666',
  },
  ingredientText: {
    fontSize: 16,
    marginBottom: 5,
    color: '#333',
  },
  servingsContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 15,
    backgroundColor: 'white',
    borderRadius: 8,
    marginVertical: 15,
  },
  servingsLabel: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
  },
  servingsControls: {
    flexDirection: 'row',
    gap: 15,
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
  nutritionCard: {
    backgroundColor: 'white',
    padding: 20,
    borderRadius: 10,
    marginVertical: 15,
  },
  nutritionGrid: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  nutritionItem: {
    alignItems: 'center',
  },
  nutritionValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#007AFF',
  },
  nutritionLabel: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
  },
  stepItem: {
    flexDirection: 'row',
    marginBottom: 15,
    alignItems: 'flex-start',
  },
  stepNumber: {
    width: 30,
    height: 30,
    borderRadius: 15,
    backgroundColor: '#007AFF',
    color: 'white',
    textAlign: 'center',
    lineHeight: 30,
    fontWeight: 'bold',
    marginRight: 15,
  },
  stepText: {
    flex: 1,
    fontSize: 16,
    color: '#333',
    lineHeight: 24,
  },
});