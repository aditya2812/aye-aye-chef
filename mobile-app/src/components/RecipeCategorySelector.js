import React from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  Modal,
} from 'react-native';

const RecipeCategorySelector = ({ 
  selectedCategory, 
  onCategorySelect, 
  visible, 
  onClose, 
  isFruitDetected = false 
}) => {
  
  // Different options based on whether fruits are detected
  const categoryOptions = isFruitDetected ? [
    { 
      id: 'smoothie', 
      name: '🥤 Smoothie', 
      description: 'Blended fruit drinks',
      examples: ['Green Smoothie', 'Berry Blast', 'Tropical Mix']
    },
    { 
      id: 'dessert', 
      name: '🍰 Dessert', 
      description: 'Sweet fruit treats',
      examples: ['Fruit Salad', 'Parfait', 'Fruit Tart']
    }
  ] : [
    { 
      id: 'italian', 
      name: '🇮🇹 Italian', 
      description: 'Fresh pasta, authentic flavors',
      examples: ['Parmigiana', 'Cacciatora', 'Herb Roasted']
    },
    { 
      id: 'thai', 
      name: '🇹🇭 Thai', 
      description: 'Sweet, sour, salty, spicy balance',
      examples: ['Green Curry', 'Pad Kra Pao', 'Satay']
    },
    { 
      id: 'mexican', 
      name: '🇲🇽 Mexican', 
      description: 'Bold flavors, fresh ingredients',
      examples: ['Fajitas', 'Grilled', 'Sautéed']
    },
    { 
      id: 'indian', 
      name: '🇮🇳 Indian', 
      description: 'Rich spices, traditional techniques',
      examples: ['Curry', 'Tandoori', 'Biryani']
    },
    { 
      id: 'mediterranean', 
      name: '🇬🇷 Mediterranean', 
      description: 'Fresh herbs, olive oil, healthy cooking',
      examples: ['Grilled', 'Baked', 'Fresh Salads']
    }
  ];

  const title = isFruitDetected ? 'What type of recipe?' : 'Choose Your Cuisine';
  const subtitle = isFruitDetected ? 'Perfect for your fruits' : 'Get detailed, authentic recipes';

  return (
    <Modal
      visible={visible}
      animationType="slide"
      presentationStyle="pageSheet"
      onRequestClose={onClose}
    >
      <View style={styles.container}>
        <View style={styles.header}>
          <Text style={styles.title}>{title}</Text>
          <Text style={styles.subtitle}>{subtitle}</Text>
          {isFruitDetected && (
            <View style={styles.fruitBadge}>
              <Text style={styles.fruitBadgeText}>🍎 Fruits Detected</Text>
            </View>
          )}
        </View>

        <ScrollView style={styles.scrollView}>
          {categoryOptions.map((category) => (
            <TouchableOpacity
              key={category.id}
              style={[
                styles.categoryOption,
                selectedCategory === category.id && styles.selectedOption
              ]}
              onPress={() => {
                onCategorySelect(category.id);
                onClose();
              }}
            >
              <View style={styles.categoryHeader}>
                <Text style={styles.categoryName}>{category.name}</Text>
                {selectedCategory === category.id && (
                  <Text style={styles.selectedIndicator}>✓</Text>
                )}
              </View>
              <Text style={styles.categoryDescription}>{category.description}</Text>
              <View style={styles.examplesContainer}>
                {category.examples.map((example, index) => (
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
    marginBottom: 8,
  },
  fruitBadge: {
    backgroundColor: '#e8f5e8',
    borderRadius: 20,
    paddingHorizontal: 12,
    paddingVertical: 6,
    alignSelf: 'flex-start',
  },
  fruitBadgeText: {
    fontSize: 14,
    color: '#2d5a2d',
    fontWeight: '600',
  },
  scrollView: {
    flex: 1,
    padding: 16,
  },
  categoryOption: {
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
  categoryHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  categoryName: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#212529',
  },
  selectedIndicator: {
    fontSize: 18,
    color: '#007AFF',
    fontWeight: 'bold',
  },
  categoryDescription: {
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

export default RecipeCategorySelector;