import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
} from 'react-native';
import { authService } from '../services/auth';

export default function SignInScreen({ navigation }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSignUp, setIsSignUp] = useState(false);
  const [confirmationCode, setConfirmationCode] = useState('');
  const [needsConfirmation, setNeedsConfirmation] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    checkCurrentUser();
  }, []);

  const checkCurrentUser = async () => {
    const result = await authService.getCurrentUser();
    if (result.success) {
      navigation.replace('Camera');
    }
  };

  const handleSignIn = async () => {
    if (!email || !password) {
      Alert.alert('Error', 'Please enter email and password');
      return;
    }

    setLoading(true);
    const result = await authService.signIn(email, password);
    setLoading(false);

    if (result.success) {
      navigation.replace('Camera');
    } else {
      Alert.alert('Sign In Failed', result.error);
    }
  };

  const handleSignUp = async () => {
    if (!email || !password) {
      Alert.alert('Error', 'Please enter email and password');
      return;
    }

    setLoading(true);
    const result = await authService.signUp(email, password);
    setLoading(false);

    if (result.success) {
      setNeedsConfirmation(true);
      Alert.alert('Success', 'Please check your email for confirmation code');
    } else {
      Alert.alert('Sign Up Failed', result.error);
    }
  };

  const handleConfirmSignUp = async () => {
    if (!confirmationCode) {
      Alert.alert('Error', 'Please enter confirmation code');
      return;
    }

    setLoading(true);
    const result = await authService.confirmSignUp(email, confirmationCode);
    setLoading(false);

    if (result.success) {
      setNeedsConfirmation(false);
      Alert.alert('Success', 'Account confirmed! Please sign in.');
    } else {
      Alert.alert('Confirmation Failed', result.error);
    }
  };

  if (needsConfirmation) {
    return (
      <KeyboardAvoidingView 
        style={styles.container} 
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        <View style={styles.form}>
          <Text style={styles.title}>Confirm Your Account</Text>
          <Text style={styles.subtitle}>Enter the code sent to {email}</Text>
          
          <TextInput
            style={styles.input}
            placeholder="Confirmation Code"
            value={confirmationCode}
            onChangeText={setConfirmationCode}
            keyboardType="number-pad"
            autoCapitalize="none"
          />

          <TouchableOpacity 
            style={styles.button} 
            onPress={handleConfirmSignUp}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color="white" />
            ) : (
              <Text style={styles.buttonText}>Confirm</Text>
            )}
          </TouchableOpacity>

          <TouchableOpacity 
            style={styles.linkButton}
            onPress={() => setNeedsConfirmation(false)}
          >
            <Text style={styles.linkText}>Back to Sign In</Text>
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    );
  }

  return (
    <KeyboardAvoidingView 
      style={styles.container} 
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <View style={styles.form}>
        <Text style={styles.title}>Aye Aye Chef</Text>
        <Text style={styles.subtitle}>Scan ingredients, get recipes</Text>
        
        <TextInput
          style={styles.input}
          placeholder="Email"
          value={email}
          onChangeText={setEmail}
          keyboardType="email-address"
          autoCapitalize="none"
          autoCorrect={false}
        />

        <TextInput
          style={styles.input}
          placeholder="Password"
          value={password}
          onChangeText={setPassword}
          secureTextEntry
          autoCapitalize="none"
        />

        <TouchableOpacity 
          style={styles.button} 
          onPress={isSignUp ? handleSignUp : handleSignIn}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color="white" />
          ) : (
            <Text style={styles.buttonText}>
              {isSignUp ? 'Sign Up' : 'Sign In'}
            </Text>
          )}
        </TouchableOpacity>

        <TouchableOpacity 
          style={styles.linkButton}
          onPress={() => setIsSignUp(!isSignUp)}
        >
          <Text style={styles.linkText}>
            {isSignUp 
              ? 'Already have an account? Sign In' 
              : "Don't have an account? Sign Up"
            }
          </Text>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    justifyContent: 'center',
  },
  form: {
    padding: 20,
    margin: 20,
    backgroundColor: 'white',
    borderRadius: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
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
  },
  button: {
    backgroundColor: '#007AFF',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 15,
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  linkButton: {
    alignItems: 'center',
  },
  linkText: {
    color: '#007AFF',
    fontSize: 14,
  },
});