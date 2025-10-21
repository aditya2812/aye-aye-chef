import { Amplify } from 'aws-amplify';
import { signIn, signUp, signOut, getCurrentUser, confirmSignUp, fetchAuthSession } from 'aws-amplify/auth';
import { AWS_CONFIG } from '../utils/constants';

// Configure Amplify
export const configureAmplify = () => {
  try {
    Amplify.configure({
      Auth: {
        Cognito: {
          userPoolId: AWS_CONFIG.USER_POOL_ID,
          userPoolClientId: AWS_CONFIG.USER_POOL_CLIENT_ID,
          region: AWS_CONFIG.REGION,
        }
      }
    });
    } catch (error) {
    }
};

// Authentication functions
export const authService = {
  // Sign in user
  signIn: async (email, password) => {
    try {
      const result = await signIn({
        username: email,
        password: password,
      });
      return { success: true, user: result };
    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  // Sign up user
  signUp: async (email, password) => {
    try {
      const result = await signUp({
        username: email,
        password: password,
        attributes: {
          email: email,
        },
      });
      return { success: true, user: result };
    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  // Confirm sign up
  confirmSignUp: async (email, confirmationCode) => {
    try {
      await confirmSignUp({
        username: email,
        confirmationCode: confirmationCode,
      });
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  // Sign out user
  signOut: async () => {
    try {
      await signOut();
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  // Get current user
  getCurrentUser: async () => {
    try {
      const user = await getCurrentUser();
      return { success: true, user };
    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  // Get user token
  getUserToken: async () => {
    try {
      const session = await fetchAuthSession();
      return session.tokens?.idToken?.toString();
    } catch (error) {
      return null;
    }
  },
};