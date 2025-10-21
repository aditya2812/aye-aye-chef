import React from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  Modal,
} from 'react-native';

const MealTypeSelector = ({ selectedMealType, onMealTypeSelect, visible, onClose }) => {
  const mealTypeOptions = [
    { 
      id: 'breakfast', 
      name: '🌅 Breakfast', 
      description: 'Start your day right',
      icon: '🌅',
      examples: ['Pancakes', 'Omelette', 'Smoothie Bowl']
    },
    { 
      id: 'lunch', 
      name: '☀️ Lunch', 
      description: 'Midday fuel',
      icon: '☀️',
      examples: ['Salad', 'Sandwich', 'Stir-fry']
    },
    { 
      id: 'dinner', 
      name: '🌙 Dinner', 
      description: 'Evening satisfaction',
      icon: '🌙',
      examples: ['Pasta', 'Curry', 'Grilled Dishes']
    },
    { 
      id: 'snack', 
      name: '🍿 Snack', 
      description: 'Quick bite',
      icon: '🍿',
      examples: ['Trail Mix', 'Fruit Bowl', 'Energy Bites']
    }
  ];

  return (
    <Modal
      visible={visible}
      animationType="slide"
      presentationStyle="pageSheet"
      onRequestClose={onClose}
    >
      <View style={styles.container}>
        <View style={styles.header}>
          <Text style={styles.title}>When will you eat this?</Text>
          <Text style={styles.subtitle}>Choose your meal type</Text>
        </View>

        <ScrollView style={styles.scrollView}>
          {mealTypeOptions.map((mealType) => (
            <TouchableOpacity
              key={mealType.id}
              style={[
                styles.mealTypeOption,
                selectedMealType === mealType.id && styles.selectedOption
              ]}
              onPress={() => {
                onMealTypeSelect(mealType.id);
                onClose();
              }}
            >
              <View style={styles.mealTypeHeader}>
                <Text style={styles.mealTypeName}>{mealType.name}</Text>
                {selectedMealType === mealType.id && (
                  <Text style={styles.selectedIndicator}>✓</Text>
                )}
              </View>
              <Text style={styles.mealTypeDescription}>{mealType.description}</Text>
              <View style={styles.examplesContainer}>
                {mealType.examples.map((example, index) => (
                  <View key={index} style={styles.exampleTag}>
                    <Text style={styles.exampleText}>{example}</Text>
                  </View>
                ))}
              </View>
            </TouchableOpacity>
          ))}
        </ScrollView>

        <TouchableOpacity style={styles.closeButton} onPress={onClose}>
          <Text style={styles.closeButtonText}>Close</Text>
        </TouchableOpacity>
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  header: {
    padding: 20,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e9ecef',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#212529',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 16,
    color: '#6c757d',
  },
  scrollView: {
    flex: 1,
    padding: 16,
  },
  mealTypeOption: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 2,
    borderColor: '#e9ecef',
  },
  selectedOption: {
    borderColor: '#007AFF',
    backgroundColor: '#f0f8ff',
  },
  mealTypeHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  mealTypeName: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#212529',
  },
  selectedIndicator: {
    fontSize: 18,
    color: '#007AFF',
    fontWeight: 'bold',
  },
  mealTypeDescription: {
    fontSize: 14,
    color: '#6c757d',
    marginBottom: 12,
  },
  examplesContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  exampleTag: {
    backgroundColor: '#e9ecef',
    borderRadius: 16,
    paddingHorizontal: 12,
    paddingVertical: 4,
    marginRight: 8,
    marginBottom: 4,
  },
  exampleText: {
    fontSize: 12,
    color: '#495057',
  },
  closeButton: {
    backgroundColor: '#007AFF',
    margin: 16,
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  closeButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});

export default MealTypeSelector;