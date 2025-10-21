import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';

export default function IngredientItem({ 
  ingredient, 
  onToggle, 
  onUpdateGrams, 
  isSelected = false 
}) {
  return (
    <TouchableOpacity 
      style={[styles.container, isSelected && styles.selectedContainer]}
      onPress={onToggle}
    >
      <View style={styles.header}>
        <View style={[styles.checkbox, isSelected && styles.checkboxSelected]}>
          {isSelected && <Text style={styles.checkmark}>✓</Text>}
        </View>
        <View style={styles.info}>
          <Text style={styles.name}>{ingredient.label}</Text>
          <Text style={styles.confidence}>
            Confidence: {Math.round(ingredient.confidence * 100)}%
          </Text>
        </View>
      </View>
      
      <View style={styles.gramsContainer}>
        <Text style={styles.gramsLabel}>Estimated: {ingredient.grams_est}g</Text>
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: 'white',
    padding: 15,
    marginVertical: 5,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#e0e0e0',
  },
  selectedContainer: {
    borderColor: '#007AFF',
    backgroundColor: '#f0f8ff',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  checkbox: {
    width: 24,
    height: 24,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#ccc',
    marginRight: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  checkboxSelected: {
    borderColor: '#007AFF',
    backgroundColor: '#007AFF',
  },
  checkmark: {
    color: 'white',
    fontSize: 14,
    fontWeight: 'bold',
  },
  info: {
    flex: 1,
  },
  name: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    textTransform: 'capitalize',
  },
  confidence: {
    fontSize: 12,
    color: '#666',
    marginTop: 2,
  },
  gramsContainer: {
    marginTop: 8,
    paddingTop: 8,
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0',
  },
  gramsLabel: {
    fontSize: 14,
    color: '#666',
  },
});