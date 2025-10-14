import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Pressable,
  Animated,
  Dimensions,
} from 'react-native';

interface GestureSection {
  id: string;
  label: string;
  gestures: {
    name: string;
    description: string;
    icon: string;
  }[];
}

interface FloatingGestureMenuProps {
  visible: boolean;
  onHide: () => void;
  autoHideDelay?: number;
}

export default function FloatingGestureMenu({ 
  visible, 
  onHide, 
  autoHideDelay = 10000 
}: FloatingGestureMenuProps) {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set());
  const fadeAnim = new Animated.Value(0);
  const scaleAnim = new Animated.Value(0);

  const gestureSections: GestureSection[] = [
    {
      id: 'navigation',
      label: 'Navigation Gestures',
      gestures: [
        { name: 'Circle Gesture', description: 'Draw circle → Home', icon: '⭕' },
        { name: 'Swipe Left/Right', description: 'Navigate between tabs', icon: '↔️' },
        { name: 'Two-Finger Swipe', description: 'Desktop/laptop touchpad navigation', icon: '👆👆↔️' },
        { name: 'Arrow Navigation', description: 'Tap arrows on sides', icon: '◀️▶️' },
      ],
    },
    {
      id: 'quick_actions',
      label: 'Quick Actions',
      gestures: [
        { name: 'Double Tap', description: 'Go to Transactions', icon: '👆👆' },
        { name: 'Triple Tap', description: 'Jump 3 tabs / Account', icon: '👆👆👆' },
        { name: 'Scroll Down 360px', description: 'Return to previous tab', icon: '📜⬇️' },
      ],
    },
    {
      id: 'menu_controls',
      label: 'Menu Controls',
      gestures: [
        { name: 'Two Finger Press', description: '2.2s → Show this menu', icon: '👆👆⏱️' },
        { name: 'Tab Menu', description: 'Home page quick nav', icon: '🏠📋' },
        { name: 'Auto Hide', description: 'Menu hides in 10s', icon: '⏰' },
      ],
    },
  ];

  useEffect(() => {
    if (visible) {
      Animated.parallel([
        Animated.timing(fadeAnim, {
          toValue: 1,
          duration: 300,
          useNativeDriver: true,
        }),
        Animated.spring(scaleAnim, {
          toValue: 1,
          tension: 100,
          friction: 8,
          useNativeDriver: true,
        }),
      ]).start();

      // Auto-hide timer
      const timer = setTimeout(() => {
        hideMenu();
      }, autoHideDelay);

      return () => clearTimeout(timer);
    } else {
      Animated.parallel([
        Animated.timing(fadeAnim, {
          toValue: 0,
          duration: 200,
          useNativeDriver: true,
        }),
        Animated.timing(scaleAnim, {
          toValue: 0,
          duration: 200,
          useNativeDriver: true,
        }),
      ]).start();
    }
  }, [visible]);

  const hideMenu = () => {
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 0,
        duration: 200,
        useNativeDriver: true,
      }),
      Animated.timing(scaleAnim, {
        toValue: 0,
        duration: 200,
        useNativeDriver: true,
      }),
    ]).start(() => {
      onHide();
      setExpandedSections(new Set());
    });
  };

  const toggleSection = (sectionId: string) => {
    setExpandedSections(prev => {
      const newSet = new Set(prev);
      if (newSet.has(sectionId)) {
        newSet.delete(sectionId);
      } else {
        newSet.add(sectionId);
      }
      return newSet;
    });
  };

  if (!visible) return null;

  const screenHeight = Dimensions.get('window').height;
  const screenWidth = Dimensions.get('window').width;

  return (
    <View style={styles.overlay}>
      <Pressable style={styles.backdrop} onPress={hideMenu} />
      <Animated.View 
        style={[
          styles.menuContainer,
          {
            opacity: fadeAnim,
            transform: [{ scale: scaleAnim }],
            maxHeight: screenHeight * 0.7,
            maxWidth: screenWidth * 0.9,
          }
        ]}
      >
        <View style={styles.header}>
          <Text style={styles.title}>🎯 Gesture Guide</Text>
          <Pressable onPress={hideMenu} style={styles.closeButton}>
            <Text style={styles.closeButtonText}>✕</Text>
          </Pressable>
        </View>

        <View style={styles.content}>
          {gestureSections.map((section) => (
            <View key={section.id} style={styles.section}>
              <Pressable 
                onPress={() => toggleSection(section.id)}
                style={styles.sectionHeader}
              >
                <Text style={styles.sectionLabel}>{section.label}</Text>
                <Text style={[
                  styles.arrow,
                  expandedSections.has(section.id) && styles.arrowExpanded
                ]}>
                  ▶
                </Text>
              </Pressable>

              {expandedSections.has(section.id) && (
                <View style={styles.sectionContent}>
                  {section.gestures.map((gesture, index) => (
                    <View key={index} style={styles.gestureItem}>
                      <Text style={styles.gestureIcon}>{gesture.icon}</Text>
                      <View style={styles.gestureInfo}>
                        <Text style={styles.gestureName}>{gesture.name}</Text>
                        <Text style={styles.gestureDescription}>{gesture.description}</Text>
                      </View>
                    </View>
                  ))}
                </View>
              )}
            </View>
          ))}
        </View>

        <View style={styles.footer}>
          <Text style={styles.footerText}>Menu auto-hides in 10 seconds</Text>
        </View>
      </Animated.View>
    </View>
  );
}

const styles = StyleSheet.create({
  overlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    zIndex: 9999,
    justifyContent: 'flex-end', // Position at bottom instead of center
    alignItems: 'stretch', // Stretch to full width
  },
  backdrop: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
  },
  menuContainer: {
    backgroundColor: '#1a2238',
    borderTopLeftRadius: 16, // Only round top corners
    borderTopRightRadius: 16,
    borderWidth: 2,
    borderColor: '#3b82f6',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: -4 }, // Shadow above instead of below
    shadowOpacity: 0.3,
    shadowRadius: 16,
    elevation: 20,
    margin: 0, // Remove margins for full screen width
    marginBottom: 0, // Ensure it touches bottom
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#2d3748',
  },
  title: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: '700',
  },
  closeButton: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#ef4444',
    justifyContent: 'center',
    alignItems: 'center',
  },
  closeButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  content: {
    maxHeight: 400,
  },
  section: {
    borderBottomWidth: 1,
    borderBottomColor: '#2d3748',
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#233044',
  },
  sectionLabel: {
    color: '#9fb3c8',
    fontSize: 16,
    fontWeight: '600',
  },
  arrow: {
    color: '#9fb3c8',
    fontSize: 14,
    fontWeight: 'bold',
    transform: [{ rotate: '0deg' }],
  },
  arrowExpanded: {
    transform: [{ rotate: '90deg' }],
  },
  sectionContent: {
    backgroundColor: '#0f1930',
    paddingVertical: 8,
  },
  gestureItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#1a2238',
  },
  gestureIcon: {
    fontSize: 24,
    marginRight: 16,
    width: 40,
    textAlign: 'center',
  },
  gestureInfo: {
    flex: 1,
  },
  gestureName: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 2,
  },
  gestureDescription: {
    color: '#9bb4da',
    fontSize: 12,
    lineHeight: 16,
  },
  footer: {
    padding: 12,
    backgroundColor: '#233044',
    borderBottomLeftRadius: 14,
    borderBottomRightRadius: 14,
    alignItems: 'center',
  },
  footerText: {
    color: '#7a8fa5',
    fontSize: 11,
    fontStyle: 'italic',
  },
});