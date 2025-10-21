import React, { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  Animated,
} from 'react-native';

const EnhancedRecipeSteps = ({ steps, skillLevel, cuisine, onStepComplete }) => {
  const [completedSteps, setCompletedSteps] = useState(new Set());
  const [expandedSteps, setExpandedSteps] = useState(new Set());

  const toggleStepComplete = (stepIndex) => {
    const newCompleted = new Set(completedSteps);
    if (newCompleted.has(stepIndex)) {
      newCompleted.delete(stepIndex);
    } else {
      newCompleted.add(stepIndex);
    }
    setCompletedSteps(newCompleted);
    onStepComplete && onStepComplete(stepIndex, newCompleted.has(stepIndex));
  };

  const toggleStepExpanded = (stepIndex) => {
    const newExpanded = new Set(expandedSteps);
    if (newExpanded.has(stepIndex)) {
      newExpanded.delete(stepIndex);
    } else {
      newExpanded.add(stepIndex);
    }
    setExpandedSteps(newExpanded);
  };

  const getStepIcon = (step, stepIndex) => {
    const stepText = step.toLowerCase();
    
    if (stepText.includes('heat') || stepText.includes('oil')) return '🔥';
    if (stepText.includes('chop') || stepText.includes('cut')) return '🔪';
    if (stepText.includes('mix') || stepText.includes('stir')) return '🥄';
    if (stepText.includes('cook') || stepText.includes('sauté')) return '🍳';
    if (stepText.includes('add') || stepText.includes('combine')) return '➕';
    if (stepText.includes('serve') || stepText.includes('garnish')) return '🍽️';
    if (stepText.includes('season') || stepText.includes('salt')) return '🧂';
    if (stepText.includes('water') || stepText.includes('liquid')) return '💧';
    
    return `${stepIndex + 1}`;
  };

  const getStepTiming = (step) => {
    const timingRegex = /(\d+)-?(\d+)?\s*(minute|min|second|sec)/gi;
    const match = step.match(timingRegex);
    return match ? match[0] : null;
  };

  const getStepTips = (step, cuisine, skillLevel) => {
    const tips = [];
    const stepText = step.toLowerCase();
    
    // Skill-level specific tips
    if (skillLevel === 'beginner') {
      if (stepText.includes('golden brown')) {
        tips.push('💡 Golden brown means the color of honey - usually takes 5-6 minutes');
      }
      if (stepText.includes('medium heat')) {
        tips.push('💡 Medium heat is about 4-5 on a scale of 1-10 on your stove');
      }
      if (stepText.includes('until fragrant')) {
        tips.push('💡 Fragrant means you can smell the spices - usually 30-60 seconds');
      }
    }
    
    // Cuisine-specific tips
    if (cuisine === 'indian') {
      if (stepText.includes('cumin seeds')) {
        tips.push('🇮🇳 Cumin seeds should splutter and change color slightly');
      }
      if (stepText.includes('garam masala')) {
        tips.push('🇮🇳 Add garam masala at the end to preserve its aroma');
      }
    } else if (cuisine === 'mediterranean') {
      if (stepText.includes('olive oil')) {
        tips.push('🇬🇷 Use extra virgin olive oil for the best Mediterranean flavor');
      }
      if (stepText.includes('garlic')) {
        tips.push('🇬🇷 Don\'t let garlic brown - it becomes bitter');
      }
    }
    
    return tips;
  };

  const renderStep = (step, index) => {
    const isCompleted = completedSteps.has(index);
    const isExpanded = expandedSteps.has(index);
    const stepIcon = getStepIcon(step, index);
    const timing = getStepTiming(step);
    const tips = getStepTips(step, cuisine, skillLevel);
    
    // Clean step text (remove emoji prefixes if they exist)
    const cleanStep = step.replace(/^[🔥👀📝]\s*/, '');

    return (
      <View key={index} style={[styles.stepContainer, isCompleted && styles.completedStep]}>
        <TouchableOpacity
          style={styles.stepHeader}
          onPress={() => toggleStepComplete(index)}
        >
          <View style={[styles.stepIcon, isCompleted && styles.completedIcon]}>
            <Text style={[styles.stepIconText, isCompleted && styles.completedIconText]}>
              {isCompleted ? '✓' : stepIcon}
            </Text>
          </View>
          
          <View style={styles.stepContent}>
            <Text style={[styles.stepText, isCompleted && styles.completedText]}>
              {cleanStep}
            </Text>
            
            {timing && (
              <View style={styles.timingContainer}>
                <Text style={styles.timingText}>⏱️ {timing}</Text>
              </View>
            )}
          </View>
          
          {tips.length > 0 && (
            <TouchableOpacity
              style={styles.expandButton}
              onPress={() => toggleStepExpanded(index)}
            >
              <Text style={styles.expandButtonText}>
                {isExpanded ? '▼' : '▶'}
              </Text>
            </TouchableOpacity>
          )}
        </TouchableOpacity>
        
        {isExpanded && tips.length > 0 && (
          <View style={styles.tipsContainer}>
            {tips.map((tip, tipIndex) => (
              <Text key={tipIndex} style={styles.tipText}>{tip}</Text>
            ))}
          </View>
        )}
      </View>
    );
  };

  const completionPercentage = (completedSteps.size / steps.length) * 100;

  return (
    <View style={styles.container}>
      {/* Progress Bar */}
      <View style={styles.progressContainer}>
        <Text style={styles.progressText}>
          Progress: {completedSteps.size}/{steps.length} steps
        </Text>
        <View style={styles.progressBar}>
          <View 
            style={[styles.progressFill, { width: `${completionPercentage}%` }]}
          />
        </View>
      </View>

      {/* Steps List */}
      <ScrollView style={styles.stepsContainer}>
        {steps.map((step, index) => renderStep(step, index))}
      </ScrollView>

      {/* Completion Message */}
      {completedSteps.size === steps.length && (
        <View style={styles.completionContainer}>
          <Text style={styles.completionText}>🎉 Recipe Complete!</Text>
          <Text style={styles.completionSubtext}>Enjoy your {cuisine} dish!</Text>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  progressContainer: {
    padding: 16,
    backgroundColor: '#f8f9fa',
    borderBottomWidth: 1,
    borderBottomColor: '#e9ecef',
  },
  progressText: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#495057',
    marginBottom: 8,
  },
  progressBar: {
    height: 8,
    backgroundColor: '#e9ecef',
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#28a745',
    borderRadius: 4,
  },
  stepsContainer: {
    flex: 1,
  },
  stepContainer: {
    backgroundColor: '#fff',
    marginHorizontal: 16,
    marginVertical: 4,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#e9ecef',
  },
  completedStep: {
    backgroundColor: '#f8fff9',
    borderColor: '#28a745',
  },
  stepHeader: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    padding: 16,
  },
  stepIcon: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: '#007AFF',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  completedIcon: {
    backgroundColor: '#28a745',
  },
  stepIconText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
  },
  completedIconText: {
    fontSize: 16,
  },
  stepContent: {
    flex: 1,
  },
  stepText: {
    fontSize: 16,
    color: '#212529',
    lineHeight: 24,
  },
  completedText: {
    textDecorationLine: 'line-through',
    color: '#6c757d',
  },
  timingContainer: {
    marginTop: 8,
    backgroundColor: '#fff3cd',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
    alignSelf: 'flex-start',
  },
  timingText: {
    fontSize: 12,
    color: '#856404',
    fontWeight: 'bold',
  },
  expandButton: {
    padding: 4,
    marginLeft: 8,
  },
  expandButtonText: {
    fontSize: 12,
    color: '#6c757d',
  },
  tipsContainer: {
    backgroundColor: '#f8f9fa',
    padding: 12,
    marginHorizontal: 16,
    marginBottom: 16,
    borderRadius: 8,
  },
  tipText: {
    fontSize: 14,
    color: '#495057',
    marginBottom: 4,
    lineHeight: 20,
  },
  completionContainer: {
    backgroundColor: '#d4edda',
    padding: 16,
    margin: 16,
    borderRadius: 12,
    alignItems: 'center',
  },
  completionText: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#155724',
    marginBottom: 4,
  },
  completionSubtext: {
    fontSize: 16,
    color: '#155724',
  },
});

export default EnhancedRecipeSteps;