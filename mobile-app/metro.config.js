const { getDefaultConfig } = require('expo/metro-config');

const config = getDefaultConfig(__dirname);

// Add polyfill resolver
config.resolver.alias = {
  ...config.resolver.alias,
  crypto: 'react-native-get-random-values',
};

module.exports = config;