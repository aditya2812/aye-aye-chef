import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { Amplify } from 'aws-amplify';
import { StatusBar } from 'expo-status-bar';

// Import screens
import SignInScreen from './src/screens/SignInScreen';
import CameraScreen from './src/screens/CameraScreen';
import ConfirmScreen from './src/screens/ConfirmScreen';
import RecipeScreen from './src/screens/RecipeScreen';

// Import services
import { configureAmplify } from './src/services/auth';
import ErrorBoundary from './src/components/ErrorBoundary';

const Stack = createStackNavigator();

// Configure Amplify
configureAmplify();

export default function App() {
  return (
    <ErrorBoundary>
      <NavigationContainer>
        <StatusBar style="auto" />
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
    </ErrorBoundary>
  );
}