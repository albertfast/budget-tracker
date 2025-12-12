import React from 'react';
import { View, StyleSheet } from 'react-native';
import HamburgerMenu from './HamburgerMenu';

interface LayoutProps {
  children: React.ReactNode;
  currentTab: string;
}

export default function Layout({ children, currentTab }: LayoutProps) {
  return (
    <View style={styles.container}>
      {/* Global Hamburger Menu */}
      <HamburgerMenu currentTab={currentTab} />

      {/* Screen Content */}
      <View style={styles.content}>
        {children}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  content: {
    flex: 1,
  },
});
