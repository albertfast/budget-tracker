import React, { useState, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Pressable,
  Animated,
  TouchableOpacity,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';

interface HamburgerMenuProps {
  currentTab: string;
}

export default function HamburgerMenu({ currentTab }: HamburgerMenuProps) {
  const [isOpen, setIsOpen] = useState(false);
  const navigation = useNavigation();
  const slideAnim = useRef(new Animated.Value(0)).current;
  const fadeAnim = useRef(new Animated.Value(0)).current;

  const tabs = [
    { name: 'Add', icon: '➕', description: 'Quick Entry Form' },
    { name: 'Connect Account', icon: '🏦', description: 'Link Bank Account' },
    { name: 'Account', icon: '👤', description: 'Profile & Settings' },
  ];

  const toggleMenu = () => {
    const toValue = isOpen ? 0 : 1;
    
    Animated.parallel([
      Animated.timing(slideAnim, {
        toValue,
        duration: 250,
        useNativeDriver: true,
      }),
      Animated.timing(fadeAnim, {
        toValue,
        duration: 200,
        useNativeDriver: true,
      }),
    ]).start();
    
    setIsOpen(!isOpen);
  };

  const navigateToTab = (tabName: string) => {
    if (tabName !== currentTab) {
      navigation.navigate(tabName as never);
    }
    toggleMenu(); // Close menu after navigation
  };

  const slideTransform = slideAnim.interpolate({
    inputRange: [0, 1],
    outputRange: [200, 0], // Slide in from right
  });

  return (
    <View style={styles.container}>
      {/* Hamburger Button */}
      <TouchableOpacity
        onPress={toggleMenu}
        style={styles.hamburgerButton}
        activeOpacity={0.7}
      >
        <Text style={styles.hamburgerIcon}>☰</Text>
      </TouchableOpacity>

      {/* Backdrop */}
      {isOpen && (
        <Pressable
          style={styles.backdrop}
          onPress={toggleMenu}
        />
      )}

      {/* Dropdown Menu */}
      <Animated.View
        style={[
          styles.dropdown,
          {
            opacity: fadeAnim,
            transform: [{ translateX: slideTransform }],
          },
        ]}
        pointerEvents={isOpen ? 'auto' : 'none'}
      >
        <View style={styles.menuHeader}>
          <Text style={styles.menuTitle}>Quick Navigation</Text>
          <TouchableOpacity onPress={toggleMenu} style={styles.closeButton}>
            <Text style={styles.closeButtonText}>✕</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.menuContent}>
          {tabs.map((tab) => (
            <TouchableOpacity
              key={tab.name}
              onPress={() => navigateToTab(tab.name)}
              style={[
                styles.menuItem,
                tab.name === currentTab && styles.menuItemActive
              ]}
              disabled={tab.name === currentTab}
            >
              <Text style={styles.menuItemIcon}>{tab.icon}</Text>
              <View style={styles.menuItemContent}>
                <Text style={[
                  styles.menuItemName,
                  tab.name === currentTab && styles.menuItemNameActive
                ]}>
                  {tab.name}
                </Text>
                <Text style={styles.menuItemDescription}>
                  {tab.description}
                </Text>
              </View>
              {tab.name === currentTab && (
                <Text style={styles.currentIndicator}>●</Text>
              )}
            </TouchableOpacity>
          ))}
        </View>

        <View style={styles.menuFooter}>
          <Text style={styles.footerText}>Tap outside to close</Text>
        </View>
      </Animated.View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    position: 'relative',
    zIndex: 1000,
  },
  hamburgerButton: {
    position: 'absolute',
    top: 16,
    right: 16,
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#3b82f6',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    elevation: 5,
    zIndex: 1001,
  },
  hamburgerIcon: {
    color: '#ffffff',
    fontSize: 20,
    fontWeight: 'bold',
  },
  backdrop: {
    position: 'absolute',
    top: 0,
    left: -1000, // Cover entire screen
    right: 0,
    bottom: -1000,
    backgroundColor: 'rgba(0, 0, 0, 0.3)',
    zIndex: 999,
  },
  dropdown: {
    position: 'absolute',
    top: 70, // Below hamburger button
    right: 16,
    width: 280,
    backgroundColor: '#1a2238',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#3b82f6',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 10,
    zIndex: 1000,
  },
  menuHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#2d3748',
  },
  menuTitle: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
  closeButton: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: '#ef4444',
    justifyContent: 'center',
    alignItems: 'center',
  },
  closeButtonText: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  menuContent: {
    paddingVertical: 8,
  },
  menuItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#2d3748',
  },
  menuItemActive: {
    backgroundColor: '#233044',
  },
  menuItemIcon: {
    fontSize: 20,
    marginRight: 12,
    width: 24,
    textAlign: 'center',
  },
  menuItemContent: {
    flex: 1,
  },
  menuItemName: {
    color: '#9fb3c8',
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 2,
  },
  menuItemNameActive: {
    color: '#ffffff',
  },
  menuItemDescription: {
    color: '#7a8fa5',
    fontSize: 11,
    lineHeight: 14,
  },
  currentIndicator: {
    color: '#3b82f6',
    fontSize: 16,
    fontWeight: 'bold',
  },
  menuFooter: {
    padding: 12,
    backgroundColor: '#233044',
    borderBottomLeftRadius: 11,
    borderBottomRightRadius: 11,
    alignItems: 'center',
  },
  footerText: {
    color: '#7a8fa5',
    fontSize: 10,
    fontStyle: 'italic',
  },
});