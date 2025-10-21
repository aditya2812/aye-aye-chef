import * as ImagePicker from 'expo-image-picker';
import { Camera } from 'expo-camera';

export const cameraService = {
  // Request camera permissions
  requestCameraPermissions: async () => {
    try {
      const { status } = await Camera.requestCameraPermissionsAsync();
      return { success: status === 'granted', status };
    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  // Request media library permissions
  requestMediaLibraryPermissions: async () => {
    try {
      const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
      return { success: status === 'granted', status };
    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  // Take photo with camera
  takePhoto: async () => {
    try {
      // Check permissions first
      const cameraPermission = await cameraService.requestCameraPermissions();
      if (!cameraPermission.success) {
        return { success: false, error: 'Camera permission denied' };
      }

      const result = await ImagePicker.launchCameraAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.8,
        base64: false,
      });

      if (result.canceled) {
        return { success: false, error: 'User canceled' };
      }

      return { 
        success: true, 
        image: {
          uri: result.assets[0].uri,
          width: result.assets[0].width,
          height: result.assets[0].height,
        }
      };
    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  // Pick image from gallery
  pickImage: async () => {
    try {
      // Check permissions first
      const libraryPermission = await cameraService.requestMediaLibraryPermissions();
      if (!libraryPermission.success) {
        return { success: false, error: 'Media library permission denied' };
      }

      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.8,
        base64: false,
      });

      if (result.canceled) {
        return { success: false, error: 'User canceled' };
      }

      return { 
        success: true, 
        image: {
          uri: result.assets[0].uri,
          width: result.assets[0].width,
          height: result.assets[0].height,
        }
      };
    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  // Show image picker options
  showImagePicker: () => {
    return new Promise((resolve) => {
      // This would typically show an action sheet
      // For now, we'll just default to camera
      cameraService.takePhoto().then(resolve);
    });
  },
};