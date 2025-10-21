import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function NutritionCard({ nutrition, servings = 1 }) {
  if (!nutrition) return null;

  const perServing = nutrition.per_serving || {};

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Nutrition Facts</Text>
      <Text style={styles.subtitle}>Per serving ({servings} servings total)</Text>
      
      <View style={styles.nutritionGrid}>
        <View style={styles.nutritionItem}>
          <Text style={styles.value}>{perServing.kcal || 0}</Text>
          <Text style={styles.label}>Calories</Text>
        </View>
        
        <View style={styles.nutritionItem}>
          <Text style={styles.value}>{perServing.protein_g || 0}g</Text>
          <Text style={styles.label}>Protein</Text>
        </View>
        
        <View style={styles.nutritionItem}>
          <Text style={styles.value}>{perServing.carb_g || 0}g</Text>
          <Text style={styles.label}>Carbs</Text>
        </View>
        
        <View style={styles.nutritionItem}>
          <Text style={styles.value}>{perServing.fat_g || 0}g</Text>
          <Text style={styles.label}>Fat</Text>
        </View>
      </View>
      
      {perServing.fiber_g && (
        <View style={styles.additionalNutrition}>
          <Text style={styles.additionalItem}>Fiber: {perServing.fiber_g}g</Text>
          {perServing.sodium_mg && (
            <Text style={styles.additionalItem}>Sodium: {perServing.sodium_mg}mg</Text>
          )}
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: 'white',
    padding: 20,
    borderRadius: 12,
    marginVertical: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  subtitle: {
    fontSize: 12,
    color: '#666',
    marginBottom: 15,
  },
  nutritionGrid: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 15,
  },
  nutritionItem: {
    alignItems: 'center',
    flex: 1,
  },
  value: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#007AFF',
  },
  label: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
    textAlign: 'center',
  },
  additionalNutrition: {
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0',
    paddingTop: 15,
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  additionalItem: {
    fontSize: 14,
    color: '#666',
  },
});