import React, { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  Modal,
} from 'react-native';

const CuisineSelector = ({ selectedCuisine, onCuisineSelect, visible, onClose }) => {
  const cuisineOptions = [
    { 
      id: 'italian', 
      name: '🇮🇹 Italian', 
      description: 'Fresh pasta, authentic flavors',
      specialties: ['Parmigiana', 'Cacciatora', 'Herb Roasted']
    },
    { 
      id: 'thai', 
      name: '🇹🇭 Thai', 
      description: 'Sweet, sour, salty, spicy balance',
      specialties: ['Green Curry', 'Pad Kra Pao', 'Satay']
    },
    { 
      id: 'mexican', 
      name: '🇲🇽 Mexican', 
      description: 'Bold flavors, fresh ingredients',
      specialties: ['Fajitas', 'Grilled', 'Sautéed']
    },
    { 
      id: 'indian', 
      name: '🇮🇳 Indian', 
      description: 'Rich spices, traditional techniques',
      specialties: ['Curry', 'Tandoori', 'Biryani']
    },
    { 
      id: 'mediterranean', 
      name: '🇬🇷 Mediterranean', 
      description: 'Fresh herbs, olive oil, healthy cooking',
      specialties: ['Grilled', 'Baked', 'Fresh Salads']
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
          <Text style={styles.title}>Choose Your Cuisine</Text>
          <Text style={styles.subtitle}>Get detailed, authentic recipes</Text>
        </View>

        <ScrollView style={styles.scrollView}>
          {cuisineOptions.map((cuisine) => (
            <TouchableOpacity
              key={cuisine.id}
              style={[
                styles.cuisineOption,
                selectedCuisine === cuisine.id && styles.selectedOption
              ]}
              onPress={() => {
                onCuisineSelect(cuisine.id);
                onClose();
              }}
            >
              <View style={styles.cuisineHeader}>
                <Text style={styles.cuisineName}>{cuisine.name}</Text>
                {selectedCuisine === cuisine.id && (
                  <Text style={styles.selectedIndicator}>✓</Text>
                )}
              </View>
              <Text style={styles.cuisineDescription}>{cuisine.description}</Text>
              <View style={styles.specialtiesContainer}>
                {cuisine.specialties.map((specialty, index) => (
                  <View key={index} style={styles.specialtyTag}>
                    <Text style={styles.specialtyText}>{specialty}</Text>
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
  cuisineOption: {
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
  cuisineHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  cuisineName: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#212529',
  },
  selectedIndicator: {
    fontSize: 18,
    color: '#007AFF',
    fontWeight: 'bold',
  },
  cuisineDescription: {
    fontSize: 14,
    color: '#6c757d',
    marginBottom: 12,
  },
  specialtiesContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  specialtyTag: {
    backgroundColor: '#e9ecef',
    borderRadius: 16,
    paddingHorizontal: 12,
    paddingVertical: 4,
    marginRight: 8,
    marginBottom: 4,
  },
  specialtyText: {
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

export default CuisineSelector;