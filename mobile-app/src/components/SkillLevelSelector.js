import React from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Modal,
} from 'react-native';

const SkillLevelSelector = ({ selectedSkillLevel, onSkillLevelSelect, visible, onClose }) => {
  const skillLevels = [
    {
      id: 'beginner',
      name: '👶 Beginner',
      description: 'Detailed explanations and visual cues',
      features: ['Step-by-step guidance', 'Visual indicators', 'Timing help', 'Basic techniques']
    },
    {
      id: 'intermediate',
      name: '👨‍🍳 Intermediate',
      description: 'Standard instructions with helpful tips',
      features: ['Clear instructions', 'Cooking tips', 'Technique notes', 'Time estimates']
    },
    {
      id: 'advanced',
      name: '🔥 Advanced',
      description: 'Concise steps for experienced cooks',
      features: ['Efficient steps', 'Professional techniques', 'Precise timing', 'Advanced methods']
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
          <Text style={styles.title}>Your Cooking Level</Text>
          <Text style={styles.subtitle}>We'll adapt the recipe instructions for you</Text>
        </View>

        <View style={styles.content}>
          {skillLevels.map((level) => (
            <TouchableOpacity
              key={level.id}
              style={[
                styles.levelOption,
                selectedSkillLevel === level.id && styles.selectedOption
              ]}
              onPress={() => {
                onSkillLevelSelect(level.id);
                onClose();
              }}
            >
              <View style={styles.levelHeader}>
                <Text style={styles.levelName}>{level.name}</Text>
                {selectedSkillLevel === level.id && (
                  <Text style={styles.selectedIndicator}>✓</Text>
                )}
              </View>
              <Text style={styles.levelDescription}>{level.description}</Text>
              <View style={styles.featuresContainer}>
                {level.features.map((feature, index) => (
                  <View key={index} style={styles.featureItem}>
                    <Text style={styles.featureBullet}>•</Text>
                    <Text style={styles.featureText}>{feature}</Text>
                  </View>
                ))}
              </View>
            </TouchableOpacity>
          ))}
        </View>

        <TouchableOpacity style={styles.closeButton} onPress={onClose}>
          <Text style={styles.closeButtonText}>Done</Text>
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
  content: {
    flex: 1,
    padding: 16,
  },
  levelOption: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    borderWidth: 2,
    borderColor: '#e9ecef',
  },
  selectedOption: {
    borderColor: '#28a745',
    backgroundColor: '#f8fff9',
  },
  levelHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  levelName: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#212529',
  },
  selectedIndicator: {
    fontSize: 18,
    color: '#28a745',
    fontWeight: 'bold',
  },
  levelDescription: {
    fontSize: 14,
    color: '#6c757d',
    marginBottom: 12,
  },
  featuresContainer: {
    marginTop: 8,
  },
  featureItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  featureBullet: {
    fontSize: 16,
    color: '#28a745',
    marginRight: 8,
    fontWeight: 'bold',
  },
  featureText: {
    fontSize: 14,
    color: '#495057',
    flex: 1,
  },
  closeButton: {
    backgroundColor: '#28a745',
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

export default SkillLevelSelector;