import React, { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  Modal,
} from 'react-native';

const DietaryRestrictionsSelector = ({ selectedRestrictions, onRestrictionsChange, visible, onClose }) => {
  const [localRestrictions, setLocalRestrictions] = useState(selectedRestrictions);

  const dietaryOptions = [
    {
      id: 'vegan',
      name: '🌱 Vegan',
      description: 'No animal products',
      adaptations: ['Coconut oil instead of ghee', 'Tofu instead of paneer', 'Plant-based cream']
    },
    {
      id: 'vegetarian',
      name: '🥬 Vegetarian',
      description: 'No meat or fish',
      adaptations: ['Dairy products included', 'Eggs may be included', 'Plant-based proteins']
    },
    {
      id: 'gluten-free',
      name: '🌾 Gluten-Free',
      description: 'No wheat, barley, or rye',
      adaptations: ['Rice instead of naan', 'Gluten-free flour', 'Check spice blends']
    },
    {
      id: 'dairy-free',
      name: '🥛 Dairy-Free',
      description: 'No milk products',
      adaptations: ['Coconut milk instead of cream', 'Dairy-free butter', 'No cheese']
    },
    {
      id: 'low-sodium',
      name: '🧂 Low Sodium',
      description: 'Reduced salt content',
      adaptations: ['Herbs for flavor', 'Low-sodium soy sauce', 'Fresh ingredients']
    },
    {
      id: 'keto',
      name: '🥑 Keto',
      description: 'Low carb, high fat',
      adaptations: ['No rice or bread', 'Extra healthy fats', 'Low-carb vegetables']
    }
  ];

  const toggleRestriction = (restrictionId) => {
    const newRestrictions = localRestrictions.includes(restrictionId)
      ? localRestrictions.filter(id => id !== restrictionId)
      : [...localRestrictions, restrictionId];
    setLocalRestrictions(newRestrictions);
  };

  const handleSave = () => {
    onRestrictionsChange(localRestrictions);
    onClose();
  };

  return (
    <Modal
      visible={visible}
      animationType="slide"
      presentationStyle="pageSheet"
      onRequestClose={onClose}
    >
      <View style={styles.container}>
        <View style={styles.header}>
          <Text style={styles.title}>Dietary Preferences</Text>
          <Text style={styles.subtitle}>We'll adapt recipes to your needs</Text>
        </View>

        <ScrollView style={styles.scrollView}>
          {dietaryOptions.map((option) => {
            const isSelected = localRestrictions.includes(option.id);
            return (
              <TouchableOpacity
                key={option.id}
                style={[
                  styles.optionContainer,
                  isSelected && styles.selectedOption
                ]}
                onPress={() => toggleRestriction(option.id)}
              >
                <View style={styles.optionHeader}>
                  <Text style={styles.optionName}>{option.name}</Text>
                  <View style={[
                    styles.checkbox,
                    isSelected && styles.checkedBox
                  ]}>
                    {isSelected && <Text style={styles.checkmark}>✓</Text>}
                  </View>
                </View>
                <Text style={styles.optionDescription}>{option.description}</Text>
                <View style={styles.adaptationsContainer}>
                  <Text style={styles.adaptationsTitle}>Recipe adaptations:</Text>
                  {option.adaptations.map((adaptation, index) => (
                    <Text key={index} style={styles.adaptationText}>
                      • {adaptation}
                    </Text>
                  ))}
                </View>
              </TouchableOpacity>
            );
          })}
        </ScrollView>

        <View style={styles.footer}>
          <TouchableOpacity style={styles.clearButton} onPress={() => setLocalRestrictions([])}>
            <Text style={styles.clearButtonText}>Clear All</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.saveButton} onPress={handleSave}>
            <Text style={styles.saveButtonText}>
              Save ({localRestrictions.length} selected)
            </Text>
          </TouchableOpacity>
        </View>
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
  optionContainer: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 2,
    borderColor: '#e9ecef',
  },
  selectedOption: {
    borderColor: '#17a2b8',
    backgroundColor: '#f0fdff',
  },
  optionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  optionName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#212529',
  },
  checkbox: {
    width: 24,
    height: 24,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#dee2e6',
    justifyContent: 'center',
    alignItems: 'center',
  },
  checkedBox: {
    backgroundColor: '#17a2b8',
    borderColor: '#17a2b8',
  },
  checkmark: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
  },
  optionDescription: {
    fontSize: 14,
    color: '#6c757d',
    marginBottom: 12,
  },
  adaptationsContainer: {
    backgroundColor: '#f8f9fa',
    padding: 12,
    borderRadius: 8,
  },
  adaptationsTitle: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#495057',
    marginBottom: 4,
  },
  adaptationText: {
    fontSize: 12,
    color: '#6c757d',
    marginBottom: 2,
  },
  footer: {
    flexDirection: 'row',
    padding: 16,
    backgroundColor: '#fff',
    borderTopWidth: 1,
    borderTopColor: '#e9ecef',
  },
  clearButton: {
    flex: 1,
    backgroundColor: '#6c757d',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginRight: 8,
  },
  clearButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  saveButton: {
    flex: 2,
    backgroundColor: '#17a2b8',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginLeft: 8,
  },
  saveButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});

export default DietaryRestrictionsSelector;