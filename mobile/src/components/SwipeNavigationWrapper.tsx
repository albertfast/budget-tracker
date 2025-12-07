import React, { useState, useRef } from 'react';
import { View, Text, StyleSheet, Pressable, Platform, Dimensions } from 'react-native';
import { PanGestureHandler, State, TapGestureHandler, LongPressGestureHandler, ScrollView } from 'react-native-gesture-handler';
import { useNavigation } from '@react-navigation/native';
import HamburgerMenu from './HamburgerMenu';

interface SwipeNavigationWrapperProps {
  children: React.ReactNode;
  currentTab: string;
  showIndicator?: boolean;
  showArrows?: boolean;
  scrollable?: boolean;
}

export default function SwipeNavigationWrapper({ 
  children, 
  currentTab, 
  showIndicator = true,
  showArrows = false,
  scrollable = true
}: SwipeNavigationWrapperProps) {
  const navigation = useNavigation();

  // Tab order for swipe navigation
  const tabs = ['Home', 'Transactions', 'Add', 'Connect Account', 'Account'];
  const currentTabIndex = tabs.indexOf(currentTab);
  
  // State for advanced gesture tracking
  const [previousTab, setPreviousTab] = useState<string>('Home');
  const [gesturePoints, setGesturePoints] = useState<{x: number, y: number}[]>([]);
  const [tapCount, setTapCount] = useState(0);
  const [scrollAccumulator, setScrollAccumulator] = useState(0);
  const [desktopSwipeIndicator, setDesktopSwipeIndicator] = useState<'left' | 'right' | null>(null);
  const [longSwipeIndicator, setLongSwipeIndicator] = useState<'left' | 'right' | null>(null);
  const [swipeStartTime, setSwipeStartTime] = useState<number | null>(null);
  const tapTimeoutRef = useRef<any>(null);
  const doubleTapRef = useRef<any>(null);
  const tripleTapRef = useRef<any>(null);
  const indicatorTimeoutRef = useRef<any>(null);
  const longSwipeTimeoutRef = useRef<any>(null);

  // Platform detection for desktop-specific gestures
  const isDesktop = Platform.OS === 'web' || (Platform.OS === 'windows' || Platform.OS === 'macos');
  const screenWidth = Dimensions.get('window').width;
  const isLargeScreen = screenWidth > 768; // Tablet/Desktop size

  // Page-specific background colors for long swipe indicators
  const getPageBackgroundColor = (tabName: string) => {
    const pageColors: { [key: string]: string } = {
      'Home': '#0b1220',
      'Transactions': '#0b1220', 
      'Add': '#0b1220',
      'Connect Account': '#0b1220',
      'Account': '#0b1220'
    };
    return pageColors[tabName] || '#0b1220';
  };

  const navigateToPrevious = () => {
    if (currentTabIndex > 0) {
      setPreviousTab(currentTab);
      navigation.navigate(tabs[currentTabIndex - 1] as never);
    }
  };

  const navigateToNext = () => {
    if (currentTabIndex < tabs.length - 1) {
      setPreviousTab(currentTab);
      navigation.navigate(tabs[currentTabIndex + 1] as never);
    }
  };

  const navigateToTab = (tabName: string) => {
    if (tabName !== currentTab) {
      setPreviousTab(currentTab);
      navigation.navigate(tabName as never);
    }
  };

  // Circle gesture detection for Home navigation
  const detectCircleGesture = (points: {x: number, y: number}[]) => {
    if (points.length < 10) return false;
    
    const centerX = points.reduce((sum, p) => sum + p.x, 0) / points.length;
    const centerY = points.reduce((sum, p) => sum + p.y, 0) / points.length;
    
    let angleSum = 0;
    for (let i = 1; i < points.length; i++) {
      const prevAngle = Math.atan2(points[i-1].y - centerY, points[i-1].x - centerX);
      const currAngle = Math.atan2(points[i].y - centerY, points[i].x - centerX);
      let angleDiff = currAngle - prevAngle;
      
      // Normalize angle difference to [-π, π]
      while (angleDiff > Math.PI) angleDiff -= 2 * Math.PI;
      while (angleDiff < -Math.PI) angleDiff += 2 * Math.PI;
      
      angleSum += angleDiff;
    }
    
    // Check if we've made roughly a full circle (≥ 300 degrees)
    const totalRotation = Math.abs(angleSum);
    return totalRotation >= (5 * Math.PI / 3); // 300 degrees in radians
  };

  // Handle tap gestures
  const handleTap = () => {
    setTapCount(prev => prev + 1);
    
    if (tapTimeoutRef.current) {
      clearTimeout(tapTimeoutRef.current);
    }
    
    tapTimeoutRef.current = setTimeout(() => {
      if (tapCount === 1) {
        // Single tap - do nothing special
      } else if (tapCount === 2) {
        // Double tap - navigate to second tab (Transactions)
        navigateToTab('Transactions');
      } else if (tapCount >= 3) {
        // Triple tap - navigate three tabs over or to highest cardinality tab (Account)
        const targetIndex = Math.min(currentTabIndex + 3, tabs.length - 1);
        navigateToTab(tabs[targetIndex]);
      }
      setTapCount(0);
    }, 400); // 400ms window for multiple taps
  };

  // Handle scroll gesture for previous tab navigation
  const handleScroll = (event: any) => {
    const { contentOffset } = event.nativeEvent;
    const scrollY = contentOffset.y;
    
    setScrollAccumulator(prev => {
      const newAccumulator = prev + scrollY;
      
      // If we've scrolled down 360px, navigate to previous tab
      if (newAccumulator >= 360) {
        navigateToTab(previousTab);
        return 0; // Reset accumulator
      }
      
      // Reset if scrolling up
      if (scrollY < 0) {
        return 0;
      }
      
      return newAccumulator;
    });
  };

  // Handle two-finger long press for gesture menu
  // Handle tab navigation from bubble clicks
  const handleTabNavigation = (index: number) => {
    if (index >= 0 && index < tabs.length) {
      navigateToTab(tabs[index]);
    }
  };

  // Handle desktop two-finger swipe navigation
  const handleDesktopTwoFingerSwipe = (translationX: number, translationY: number, velocityX: number, velocityY: number) => {
    // Desktop-optimized thresholds for touchpad gestures
    const desktopSwipeThreshold = 80; // Lower threshold for touchpads
    const desktopVelocityThreshold = 400; // Lower velocity for precision touchpads
    const minHorizontalDistance = 40;
    
    // Prevent accidental navigation during vertical scrolling
    const verticalScrollThreshold = 60; // Lower for touchpads
    const isVerticalScroll = Math.abs(translationY) > verticalScrollThreshold && 
                            Math.abs(translationY) > Math.abs(translationX) * 1.2;
    
    if (!isVerticalScroll) {
      const shouldSwipeRight = (translationX > desktopSwipeThreshold) || 
                              (velocityX > desktopVelocityThreshold && translationX > minHorizontalDistance);
      const shouldSwipeLeft = (translationX < -desktopSwipeThreshold) || 
                             (velocityX < -desktopVelocityThreshold && translationX < -minHorizontalDistance);
      
      if (shouldSwipeRight) {
        navigateToPrevious();
        showDesktopSwipeIndicator('right');
      } else if (shouldSwipeLeft) {
        navigateToNext();
        showDesktopSwipeIndicator('left');
      }
    }
  };

  // Show desktop swipe visual feedback
  const showDesktopSwipeIndicator = (direction: 'left' | 'right') => {
    setDesktopSwipeIndicator(direction);
    
    // Clear existing timeout
    if (indicatorTimeoutRef.current) {
      clearTimeout(indicatorTimeoutRef.current);
    }
    
    // Auto-hide indicator after 1.5 seconds
    indicatorTimeoutRef.current = setTimeout(() => {
      setDesktopSwipeIndicator(null);
    }, 1500);
  };

  // Clear desktop swipe indicator
  const clearDesktopIndicator = () => {
    setDesktopSwipeIndicator(null);
    if (indicatorTimeoutRef.current) {
      clearTimeout(indicatorTimeoutRef.current);
      indicatorTimeoutRef.current = null;
    }
  };

  // Show long swipe visual feedback
  const showLongSwipeIndicator = (direction: 'left' | 'right') => {
    setLongSwipeIndicator(direction);
    
    // Clear existing timeout
    if (longSwipeTimeoutRef.current) {
      clearTimeout(longSwipeTimeoutRef.current);
    }
    
    // Auto-hide indicator after 2 seconds
    longSwipeTimeoutRef.current = setTimeout(() => {
      setLongSwipeIndicator(null);
    }, 2000);
  };

  // Clear long swipe indicator
  const clearLongSwipeIndicator = () => {
    setLongSwipeIndicator(null);
    if (longSwipeTimeoutRef.current) {
      clearTimeout(longSwipeTimeoutRef.current);
      longSwipeTimeoutRef.current = null;
    }
  };



  const handleSwipe = (event: any) => {
    const { translationX, translationY, state, velocityX, velocityY, x, y, numberOfPointers } = event.nativeEvent;
    
    // Track gesture points for circle detection
    if (state === State.ACTIVE) {
      setGesturePoints(prev => [...prev, { x, y }]);
    }
    
    if (state === State.BEGAN) {
      setGesturePoints([]);
      clearDesktopIndicator();
      clearLongSwipeIndicator();
      setSwipeStartTime(Date.now());
    }
    
    if (state === State.ACTIVE) {
      // Long swipe detection - requires both distance and time
      const currentTime = Date.now();
      const swipeDuration = swipeStartTime ? currentTime - swipeStartTime : 0;
      const isLongSwipe = Math.abs(translationX) > 200 && swipeDuration > 800; // 200px + 800ms
      
      if (isLongSwipe && !longSwipeIndicator) {
        const direction = translationX > 0 ? 'right' : 'left';
        showLongSwipeIndicator(direction);
      }
      
      // Show visual feedback during desktop two-finger swipe
      if ((isDesktop || isLargeScreen) && numberOfPointers === 2) {
        if (Math.abs(translationX) > 50) {
          const direction = translationX > 0 ? 'right' : 'left';
          setDesktopSwipeIndicator(direction);
        }
      }
    }
    
    if (state === State.END) {
      // Check for circle gesture first
      if (detectCircleGesture(gesturePoints)) {
        navigateToTab('Home');
        setGesturePoints([]);
        clearDesktopIndicator();
        clearLongSwipeIndicator();
        return;
      }
      
      setGesturePoints([]);
      
      // Desktop/Laptop specific two-finger swipe logic
      if ((isDesktop || isLargeScreen) && numberOfPointers === 2) {
        handleDesktopTwoFingerSwipe(translationX, translationY, velocityX, velocityY);
        return;
      }

      // Long swipe navigation (prioritized over regular swipe)
      const currentTime = Date.now();
      const swipeDuration = swipeStartTime ? currentTime - swipeStartTime : 0;
      const isLongSwipe = Math.abs(translationX) > 200 && swipeDuration > 800;
      
      if (isLongSwipe) {
        const verticalScrollThreshold = 120;
        const isVerticalScroll = Math.abs(translationY) > verticalScrollThreshold && 
                                Math.abs(translationY) > Math.abs(translationX) * 1.2;
        
        if (!isVerticalScroll) {
          if (translationX > 200) {
            navigateToPrevious();
            showLongSwipeIndicator('right');
          } else if (translationX < -200) {
            navigateToNext();
            showLongSwipeIndicator('left');
          }
        }
        clearLongSwipeIndicator();
        return;
      }
      
      // Regular mobile single-finger swipe logic
      const swipeThreshold = 150;
      const velocityThreshold = 800;
      const minHorizontalDistance = 80;
      
      const verticalScrollThreshold = 100;
      const isVerticalScroll = Math.abs(translationY) > verticalScrollThreshold && 
                              Math.abs(translationY) > Math.abs(translationX) * 1.5;
      
      if (!isVerticalScroll) {
        const shouldSwipeRight = (translationX > swipeThreshold) || 
                                (velocityX > velocityThreshold && translationX > minHorizontalDistance);
        const shouldSwipeLeft = (translationX < -swipeThreshold) || 
                               (velocityX < -velocityThreshold && translationX < -minHorizontalDistance);
        
        if (shouldSwipeRight) {
          navigateToPrevious();
          showDesktopSwipeIndicator('right');
        } else if (shouldSwipeLeft) {
          navigateToNext();
          showDesktopSwipeIndicator('left');
        }
      }
      
      clearLongSwipeIndicator();
      setSwipeStartTime(null);
    }
  };

  return (
    <>
      <TapGestureHandler
        ref={tripleTapRef}
        numberOfTaps={3}
        onActivated={handleTap}
        waitFor={doubleTapRef}
      >
        <TapGestureHandler
          ref={doubleTapRef}
          numberOfTaps={2}
          onActivated={handleTap}
        >
          <TapGestureHandler
            numberOfTaps={1}
            onActivated={handleTap}
          >
            <PanGestureHandler 
              onGestureEvent={handleSwipe} 
              onHandlerStateChange={handleSwipe}
              minPointers={isDesktop || isLargeScreen ? 1 : 1}
              maxPointers={isDesktop || isLargeScreen ? 2 : 1} // Allow 2 fingers on desktop
              activeOffsetX={[-40, 40]}
              failOffsetY={isDesktop || isLargeScreen ? [-30, 30] : [-50, 50]} // More sensitive on desktop
              shouldCancelWhenOutside={false}
              enabled={true}
            >
            <View style={styles.container}>
              {/* Navigation Arrows */}
              {showArrows && (
                <>
                  {/* Left Arrow */}
                  {currentTabIndex > 0 && (
                    <Pressable 
                      style={[styles.navArrow, styles.leftArrow]}
                      onPress={navigateToPrevious}
                      hitSlop={{ top: 25, bottom: 25, left: 15, right: 15 }} // Enhanced mobile touch targets
                    >
                      <Text style={styles.arrowText}>‹</Text>
                    </Pressable>
                  )}
                  
                  {/* Right Arrow */}
                  {currentTabIndex < tabs.length - 1 && (
                    <Pressable 
                      style={[styles.navArrow, styles.rightArrow]}
                      onPress={navigateToNext}
                      hitSlop={{ top: 25, bottom: 25, left: 15, right: 15 }} // Enhanced mobile touch targets
                    >
                      <Text style={styles.arrowText}>›</Text>
                    </Pressable>
                  )}
                </>
              )}
              
              {scrollable ? (
                <ScrollView 
                  style={styles.scrollContent}
                  onScroll={handleScroll}
                  scrollEventThrottle={16}
                  showsVerticalScrollIndicator={false}
                  contentContainerStyle={styles.scrollContainer}
                >
                  {children}
                </ScrollView>
              ) : (
                <View style={[styles.scrollContent, { paddingHorizontal: 0 }]}>
                  {children}
                </View>
              )}
              
              {/* Long Swipe Indicator */}
              {longSwipeIndicator && (
                <View style={[
                  styles.longSwipeIndicator,
                  { backgroundColor: getPageBackgroundColor(currentTab) },
                  longSwipeIndicator === 'left' ? styles.longSwipeIndicatorLeft : styles.longSwipeIndicatorRight
                ]}>
                  <Text style={styles.longSwipeIndicatorText}>
                    {longSwipeIndicator === 'left' ? '← Next Tab' : '→ Previous Tab'}
                  </Text>
                  <Text style={styles.longSwipeIndicatorSubtext}>
                    Long swipe detected (200px + 800ms)
                  </Text>
                </View>
              )}

              {/* Desktop Two-Finger Swipe Indicator */}
              {(isDesktop || isLargeScreen) && desktopSwipeIndicator && (
                <View style={[
                  styles.desktopSwipeIndicator,
                  { backgroundColor: getPageBackgroundColor(currentTab) },
                  desktopSwipeIndicator === 'left' ? styles.swipeIndicatorLeft : styles.swipeIndicatorRight
                ]}>
                  <Text style={styles.swipeIndicatorText}>
                    {desktopSwipeIndicator === 'left' ? '← Next Tab' : '→ Previous Tab'}
                  </Text>
                  <Text style={styles.swipeIndicatorSubtext}>
                    Two-finger touchpad swipe
                  </Text>
                </View>
              )}
              
              {/* Hamburger Menu removed as per user request */}
            </View>
          </PanGestureHandler>
        </TapGestureHandler>
      </TapGestureHandler>
    </TapGestureHandler>
  </>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingTop: 40, // Doubled container padding: 20 * 2 = 40px for enhanced visibility
  },
  scrollContent: {
    flex: 1,
    opacity: 1, // Make scroll view visible
  },
  scrollContainer: {
    flexGrow: 1,
    paddingTop: 20, // Reduced since top tab indicator is removed
    paddingBottom: 20, // Reduced bottom padding since bottom navigation is removed
  },
  swipeIndicator: { 
    alignItems: 'center', 
    paddingVertical: 20, // Mobile optimized padding
    paddingHorizontal: 20, // Mobile optimized padding: consistent with screen padding
    marginVertical: 20, // Mobile optimized margin spacing
    opacity: 0.7,
    borderRadius: 8,
  },
  swipeText: { 
    color: '#9fb3c8', 
    fontSize: 11, 
    fontStyle: 'italic',
    textShadowColor: '#000000',
    textShadowOffset: { width: 0.5, height: 0.5 },
    textShadowRadius: 1,
    marginBottom: 18, // Triple margin: 6 * 3 = 18
  },
  tabIndicator: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    gap: 72, // Doubled spacing: 36 * 2 = 72
  },
  tabDot: {
    width: 12, // Divided by 5: 60 / 5 = 12
    height: 12, // Divided by 5: 60 / 5 = 12
    borderRadius: 6, // Divided by 5: 30 / 5 = 6
    backgroundColor: 'transparent', // Removed background
    borderWidth: 1, // Reduced border for smaller size: 3 / 3 = 1
    borderColor: '#4a5568',
  },
  tabDotActive: {
    backgroundColor: 'transparent', // Removed background
    width: 16, // Divided by 5: 80 / 5 = 16
    height: 16, // Divided by 5: 80 / 5 = 16
    borderRadius: 8, // Divided by 5: 40 / 5 = 8
    borderWidth: 2, // Reduced border for smaller size: 4 / 2 = 2
    borderColor: '#3b82f6',
  },
  navArrow: {
    position: 'absolute',
    top: '60%', // Moved down by 20% from center (50% + 10% = 60%)
    width: 32, // Increased width for better mobile touch targets
    height: 68, // Increased height for better mobile touch targets
    backgroundColor: 'rgba(59, 130, 246, 0.85)', // Slightly more opaque for better mobile visibility
    borderRadius: 16, // Increased border radius proportionally
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 10,
    marginTop: -34, // Adjusted for new height
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 5, // Slightly larger shadow for mobile
    elevation: 6, // Increased elevation for mobile
  },
  leftArrow: {
    left: 8, // Mobile optimized left position
    borderTopRightRadius: 12,
    borderBottomRightRadius: 12,
    borderTopLeftRadius: 4,
    borderBottomLeftRadius: 4,
  },
  rightArrow: {
    right: 8, // Mobile optimized right position
    borderTopLeftRadius: 12,
    borderBottomLeftRadius: 12,
    borderTopRightRadius: 4,
    borderBottomRightRadius: 4,
  },
  arrowText: {
    color: '#ffffff',
    fontSize: 24, // Increased font size for better mobile visibility
    fontWeight: 'bold',
    textShadowColor: '#000000',
    textShadowOffset: { width: 1, height: 1 },
    textShadowRadius: 2,
  },
  desktopSwipeIndicator: {
    position: 'absolute',
    top: '50%',
    backgroundColor: 'rgba(59, 130, 246, 0.95)',
    borderRadius: 12,
    paddingHorizontal: 30, // Mobile optimized padding: 50% of original for better mobile fit
    paddingVertical: 20, // Mobile optimized padding
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 6, // Reduced shadow for mobile
    elevation: 8, // Reduced elevation for mobile
    zIndex: 1500,
    marginTop: -30, // Mobile optimized margin
    borderWidth: 2,
    borderColor: 'rgba(255, 255, 255, 0.2)',
  },
  swipeIndicatorLeft: {
    left: 30, // Mobile optimized left position: 50% of original
  },
  swipeIndicatorRight: {
    right: 30, // Mobile optimized right position: 50% of original
  },
  swipeIndicatorText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 2,
    textAlign: 'center',
  },
  swipeIndicatorSubtext: {
    color: '#e0e7ff',
    fontSize: 11,
    textAlign: 'center',
    opacity: 0.9,
  },
  longSwipeIndicator: {
    position: 'absolute',
    top: '40%',
    backgroundColor: 'rgba(59, 130, 246, 0.95)',
    borderRadius: 16,
    paddingHorizontal: 30, // Mobile optimized padding: 50% of original for better mobile fit
    paddingVertical: 20, // Mobile optimized padding
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.4,
    shadowRadius: 8, // Reduced shadow for mobile
    elevation: 10, // Reduced elevation for mobile
    zIndex: 2000,
    marginTop: -30, // Mobile optimized margin
    borderWidth: 2,
    borderColor: 'rgba(255, 255, 255, 0.2)',
  },
  longSwipeIndicatorLeft: {
    left: 30, // Mobile optimized left position: 50% of original
  },
  longSwipeIndicatorRight: {
    right: 30, // Mobile optimized right position: 50% of original
  },
  longSwipeIndicatorText: {
    color: '#ffffff',
    fontSize: 18, // Larger text for long swipe
    fontWeight: '700',
    marginBottom: 6,
    textAlign: 'center',
    textShadowColor: '#000000',
    textShadowOffset: { width: 1, height: 1 },
    textShadowRadius: 2,
  },
  longSwipeIndicatorSubtext: {
    color: '#e0e7ff',
    fontSize: 12,
    textAlign: 'center',
    opacity: 0.95,
    fontStyle: 'italic',
  },
  // Top tab indicator styles
  topTabIndicator: {
    position: 'absolute',
    top: 80, // Doubled top position: 40 * 2 = 80px for enhanced spacing
    left: 0,
    right: 0,
    alignItems: 'center',
    paddingHorizontal: 40, // Doubled horizontal padding: 20 * 2 = 40px
    paddingVertical: 50, // Doubled vertical padding: 25 * 2 = 50px 
    zIndex: 100,
    minHeight: 140, // Doubled height: 70 * 2 = 140px for generous spacing
  },
  topTabText: {
    color: '#9fb3c8',
    fontSize: 14,
    fontWeight: '600',
    textAlign: 'center',
    textShadowColor: '#000000',
    textShadowOffset: { width: 0.5, height: 0.5 },
    textShadowRadius: 1,
    marginBottom: 8,
  },
});