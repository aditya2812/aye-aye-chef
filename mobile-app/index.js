import 'react-native-get-random-values';
import 'react-native-url-polyfill/auto';
import { registerRootComponent } from 'expo';

// Platform constants fix for SDK 54
if (typeof global !== 'undefined') {
  global.HermesInternal = global.HermesInternal || null;
}

import App from './App';

// Register the main component
registerRootComponent(App);