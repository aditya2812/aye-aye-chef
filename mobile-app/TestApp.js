import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

// Disable React DevTools to avoid compatibility issues
if (typeof window !== 'undefined') {
  window.__REACT_DEVTOOLS_GLOBAL_HOOK__ = { isDisabled: true };
}

export default function TestApp() {
  console.log('TestApp rendering...');
  
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Aye Aye Test</Text>
      <Text style={styles.subtitle}>Basic app is working</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    marginBottom: 10,
    color: '#333',
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
  },
});