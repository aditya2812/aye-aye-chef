import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
  Image,
  ScrollView,
} from 'react-native';
import { cameraService } from '../services/camera';
import { apiService } from '../services/api';
import { authService } from '../services/auth';

export default function CameraScreen({ navigation }) {
  const [image, setImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [userName, setUserName] = useState('');

  useEffect(() => {
    loadUserInfo();
  }, []);

  const loadUserInfo = async () => {
    try {
      const userResult = await authService.getCurrentUser();
      if (userResult.success && userResult.user) {
        // Extract name from user attributes or use email
        const email = userResult.user.signInDetails?.loginId || userResult.user.username || '';
        const name = email.split('@')[0]; // Use part before @ as display name
        setUserName(name);
      }
    } catch (error) {
      }
  };

  const handleSignOut = async () => {
    const result = await authService.signOut();
    if (result.success) {
      navigation.replace('SignIn');
    }
  };

  const handleTakePhoto = async () => {
    setLoading(true);

    try {
      // For mobile web, create a file input that opens camera
      if (typeof window !== 'undefined' && window.document) {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'image/*';
        input.capture = 'environment'; // Use rear camera on mobile
        input.onchange = (e) => {
          const file = e.target.files[0];
          if (file) {
            const reader = new FileReader();
            reader.onload = (event) => {
              const imageUri = event.target.result;
              setImage({ uri: imageUri });
              setLoading(false);
              
              // Don't auto-navigate, let user click "Process Image" button
            };
            reader.readAsDataURL(file);
          } else {
            setLoading(false);
          }
        };
        input.click();
        return;
      }

      // Fallback to expo image picker for native
      const photoResult = await cameraService.takePhoto();
      if (!photoResult.success) {
        Alert.alert('Error', photoResult.error);
        setLoading(false);
        return;
      }

      setImage(photoResult.image);

      // Get presigned URL
      const presignResult = await apiService.getPresignedUrl();
      if (!presignResult.success) {
        Alert.alert('Error', 'Failed to get upload URL');
        setLoading(false);
        return;
      }

      const { uploadUrl, s3Key } = presignResult.data;

      // Upload image
      const uploadResult = await apiService.uploadImage(uploadUrl, photoResult.image.uri);
      if (!uploadResult.success) {
        Alert.alert('Error', 'Failed to upload image');
        setLoading(false);
        return;
      }

      // Start scan
      const scanResult = await apiService.startScan(s3Key);
      if (!scanResult.success) {
        Alert.alert('Error', 'Failed to start scan');
        setLoading(false);
        return;
      }

      setLoading(false);

      // Navigate to confirmation screen
      navigation.navigate('Confirm', {
        scanId: scanResult.data.scan_id,
        imageUri: photoResult.image.uri
      });

    } catch (error) {
      Alert.alert('Error', 'Something went wrong');
      setLoading(false);
    }
  };

  const handlePickImage = async () => {
    setLoading(true);

    try {
      // Pick image from gallery
      const imageResult = await cameraService.pickImage();
      if (!imageResult.success) {
        Alert.alert('Error', imageResult.error);
        setLoading(false);
        return;
      }

      setImage(imageResult.image);

      // Get presigned URL
      const presignResult = await apiService.getPresignedUrl();
      if (!presignResult.success) {
        Alert.alert('Error', 'Failed to get upload URL');
        setLoading(false);
        return;
      }

      const { uploadUrl, s3Key } = presignResult.data;

      // Upload image
      const uploadResult = await apiService.uploadImage(uploadUrl, imageResult.image.uri);
      if (!uploadResult.success) {
        Alert.alert('Error', 'Failed to upload image');
        setLoading(false);
        return;
      }

      // Start scan
      const scanResult = await apiService.startScan(s3Key);
      if (!scanResult.success) {
        Alert.alert('Error', 'Failed to start scan');
        setLoading(false);
        return;
      }

      setLoading(false);

      // Navigate to confirmation screen
      navigation.navigate('Confirm', {
        scanId: scanResult.data.scan_id,
        imageUri: imageResult.image.uri
      });

    } catch (error) {
      Alert.alert('Error', 'Something went wrong');
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Scan Your Ingredients</Text>
        <View style={styles.userSection}>
          {userName && <Text style={styles.userName}>Hi, {userName}!</Text>}
          <TouchableOpacity style={styles.signOutButton} onPress={handleSignOut}>
            <Text style={styles.signOutText}>Sign Out</Text>
          </TouchableOpacity>
        </View>
      </View>

      <ScrollView 
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={true}
      >
        <View style={styles.content}>
        {image ? (
          <View style={styles.imageContainer}>
            <Image source={{ uri: image.uri }} style={styles.image} />
            <Text style={styles.imageText}>Image captured!</Text>
            
            {/* Manual process button for debugging */}
            <TouchableOpacity 
              style={[styles.button, { backgroundColor: '#28a745', marginTop: 15 }]}
              onPress={async () => {
                setLoading(true);
                
                try {
                  // Convert image to base64 for direct API upload (bypass CORS issues)
                  const response = await fetch(image.uri);
                  const blob = await response.blob();
                  
                  // Convert blob to base64
                  const base64 = await new Promise((resolve) => {
                    const reader = new FileReader();
                    reader.onloadend = () => resolve(reader.result);
                    reader.readAsDataURL(blob);
                  });
                  
                  // Try real API call with CORS workaround
                  try {
                    // Call API with base64 image data directly
                    const scanResult = await apiService.startScan(base64);
                    
                    if (scanResult.success) {
                      // Check if we have a valid scan ID
                      if (scanResult.data && scanResult.data.scan_id) {
                        try {
                          // Navigate with REAL scan ID and detected items as backup
                          navigation.navigate('Confirm', { 
                            scanId: scanResult.data.scan_id,
                            imageUri: image.uri,
                            detectedItems: scanResult.data.items || []
                          });
                          return;
                        } catch (navError) {
                          // Try alternative navigation method
                          setTimeout(() => {
                            navigation.replace('Confirm', { 
                              scanId: scanResult.data.scan_id,
                              imageUri: image.uri,
                              detectedItems: scanResult.data.items || []
                            });
                          }, 100);
                          return;
                        }
                      } else {
                        throw new Error('No scan_id in response: ' + JSON.stringify(scanResult.data));
                      }
                    } else {
                      throw new Error('API call failed: ' + JSON.stringify(scanResult));
                    }
                  } catch (apiError) {
                    // Show the actual error to help debug
                    Alert.alert(
                      'API Error', 
                      `The scan API failed:\n\n${apiError.message}\n\nCheck console for full details.`
                    );
                    throw apiError;
                  }
                  if (!scanResult.success) {
                    throw new Error('AI scan failed');
                  }

                  // Navigate with REAL scan ID from AWS Rekognition
                  navigation.navigate('Confirm', { 
                    scanId: scanResult.data.scan_id,
                    imageUri: image.uri 
                  });
                } catch (error) {
                  // Show detailed error information
                  const errorDetails = {
                    message: error.message,
                    name: error.name,
                    stack: error.stack?.substring(0, 200)
                  };
                  
                  Alert.alert(
                    'AI Detection Failed', 
                    `Error: ${error.message}\n\nType: ${error.name}\n\nCheck browser console for full details.`
                  );
                  
                  // Don't navigate on failure - let user try again
                } finally {
                  setLoading(false);
                }
              }}
            >
              <Text style={styles.buttonText}>🔄 Process Image</Text>
            </TouchableOpacity>



          </View>
        ) : (
          <View style={styles.placeholder}>
            <Text style={styles.placeholderText}>
              Take a photo of your ingredients or select from gallery
            </Text>
          </View>
        )}

        {loading ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color="#007AFF" />
            <Text style={styles.loadingText}>Processing image...</Text>
          </View>
        ) : (
          <View style={styles.buttonContainer}>


            <TouchableOpacity style={styles.button} onPress={handleTakePhoto}>
              <Text style={styles.buttonText}>📷 Take Photo</Text>
            </TouchableOpacity>

            <TouchableOpacity style={[styles.button, styles.secondaryButton]} onPress={handlePickImage}>
              <Text style={[styles.buttonText, styles.secondaryButtonText]}>🖼️ Choose from Gallery</Text>
            </TouchableOpacity>
          </View>
        )}
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
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 15,
    backgroundColor: 'white',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
    zIndex: 1,
  },
  userSection: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  userName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  signOutButton: {
    padding: 8,
  },
  signOutText: {
    color: '#007AFF',
    fontSize: 14,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    paddingBottom: 50, // Extra space at bottom
  },
  content: {
    padding: 20,
    maxWidth: 500, // Reasonable width for web
    alignSelf: 'center',
    width: '100%',
    minHeight: 600, // Ensure minimum height
  },
  imageContainer: {
    alignItems: 'center',
    marginBottom: 20,
  },
  image: {
    width: 250,
    height: 188,
    borderRadius: 10,
    marginBottom: 10,
  },
  imageText: {
    fontSize: 16,
    color: '#666',
  },
  placeholder: {
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'white',
    borderRadius: 10,
    borderWidth: 2,
    borderColor: '#ddd',
    borderStyle: 'dashed',
    padding: 40,
    marginBottom: 20,
    minHeight: 200,
  },
  placeholderText: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    paddingHorizontal: 20,
  },
  loadingContainer: {
    alignItems: 'center',
    padding: 40,
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#666',
  },
  buttonContainer: {
    gap: 12,
    marginTop: 20,
  },
  button: {
    backgroundColor: '#007AFF',
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
    marginBottom: 10,
  },
  buttonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
  secondaryButton: {
    backgroundColor: 'white',
    borderWidth: 2,
    borderColor: '#007AFF',
  },
  secondaryButtonText: {
    color: '#007AFF',
  },
});