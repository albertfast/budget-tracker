import React, { useEffect, useRef } from 'react';
import { View, Text, StyleSheet, Animated, Easing, ImageBackground } from 'react-native';
import Svg, { Circle, Defs, LinearGradient as SvgLinearGradient, Stop, Path } from 'react-native-svg';

const AnimatedCircle = Animated.createAnimatedComponent(Circle);

interface FinancialData {
  label: string;
  value: number;
  color: string;
  size: number;
  current: number;
  target: number;
  unit: string;
  icon: string;
}

interface CircleProgressProps {
  data: FinancialData;
  index: number;
}

const CircleProgress: React.FC<CircleProgressProps> = ({ data, index }) => {
  const strokeWidth = 14;
  const radius = (data.size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  
  const animatedValue = useRef(new Animated.Value(0)).current;
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const scaleAnim = useRef(new Animated.Value(0.7)).current;
  const pulseAnim = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    // Progress Animation
    const progressTarget = ((100 - Math.min(data.value, 100)) / 100) * circumference;
    
    Animated.parallel([
      Animated.timing(animatedValue, {
        toValue: progressTarget,
        duration: 1800,
        delay: index * 250,
        easing: Easing.out(Easing.cubic),
        useNativeDriver: false,
      }),
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 1000,
        delay: index * 250,
        useNativeDriver: true,
      }),
      Animated.spring(scaleAnim, {
        toValue: 1,
        delay: index * 250,
        friction: 4,
        tension: 40,
        useNativeDriver: true,
      }),
    ]).start();

    // Subtle pulse animation loop
    Animated.loop(
      Animated.sequence([
        Animated.timing(pulseAnim, {
          toValue: 1.05,
          duration: 2000,
          easing: Easing.inOut(Easing.ease),
          useNativeDriver: true,
        }),
        Animated.timing(pulseAnim, {
          toValue: 1,
          duration: 2000,
          easing: Easing.inOut(Easing.ease),
          useNativeDriver: true,
        }),
      ])
    ).start();
  }, [data.value, circumference, index]);

  return (
    <Animated.View
      style={[
        styles.circleContainer, 
        { 
          width: data.size, 
          height: data.size,
          opacity: fadeAnim,
          transform: [{ scale: Animated.multiply(scaleAnim, pulseAnim) }]
        }
      ]}
    >
      <Svg
        width={data.size}
        height={data.size}
        viewBox={`0 0 ${data.size} ${data.size}`}
        style={{ transform: [{ rotate: '-90deg' }] }}
      >
        <Defs>
          <SvgLinearGradient
            id={`gradient-${data.label.toLowerCase()}`}
            x1="0%"
            y1="0%"
            x2="100%"
            y2="100%"
          >
            <Stop offset="0%" stopColor={data.color} stopOpacity={1} />
            <Stop offset="100%" stopColor={data.color} stopOpacity={0.5} />
          </SvgLinearGradient>
        </Defs>

        {/* Background circle with glow */}
        <Circle
          cx={data.size / 2}
          cy={data.size / 2}
          r={radius}
          fill="none"
          stroke="rgba(255, 255, 255, 0.05)"
          strokeWidth={strokeWidth}
        />

        {/* Progress circle with gradient and glow */}
        <AnimatedCircle
          cx={data.size / 2}
          cy={data.size / 2}
          r={radius}
          fill="none"
          stroke={`url(#gradient-${data.label.toLowerCase()})`}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={animatedValue}
          strokeLinecap="round"
          opacity={0.95}
        />
      </Svg>

      {/* Center content with icon and percentage */}
      <View style={[styles.centerContent, { width: data.size, height: data.size }]}>
        <Animated.Text
          style={[
            styles.iconText, 
            { 
              opacity: fadeAnim,
              transform: [{ scale: scaleAnim }]
            }
          ]}
        >
          {data.icon}
        </Animated.Text>
        <Animated.Text
          style={[
            styles.percentageText, 
            { 
              color: data.color,
              opacity: fadeAnim,
              fontSize: data.size * 0.18,
            }
          ]}
        >
          {Math.round(data.value)}%
        </Animated.Text>
      </View>
    </Animated.View>
  );
};

interface FinancialActivityRingsProps {
  title?: string;
  budgetUsed?: number;
  savingsGoal?: number;
  investmentsGrowth?: number;
}

export default function FinancialActivityRings({
  title = "Financial Activity",
  budgetUsed = 0,
  savingsGoal = 0,
  investmentsGrowth = 0,
}: FinancialActivityRingsProps) {
  
  const financialData: FinancialData[] = [
    {
      label: "BUDGET",
      value: budgetUsed,
      color: "#ef4444",
      size: 170,
      current: 0, 
      target: 0,
      unit: "%",
      icon: "💰",
    },
    {
      label: "SAVINGS",
      value: savingsGoal,
      color: "#06b6d4",
      size: 130,
      current: 0,
      target: 0,
      unit: "%",
      icon: "🏦",
    },
    {
      label: "INVEST",
      value: investmentsGrowth,
      color: "#f59e0b",
      size: 90,
      current: 0,
      target: 0,
      unit: "%",
      icon: "📈",
    },
  ];

  const titleFade = useRef(new Animated.Value(0)).current;
  const titleTranslate = useRef(new Animated.Value(-20)).current;
  const detailsFade = useRef(new Animated.Value(0)).current;
  const detailsTranslate = useRef(new Animated.Value(20)).current;

  useEffect(() => {
    Animated.parallel([
      Animated.timing(titleFade, {
        toValue: 1,
        duration: 600,
        useNativeDriver: true,
      }),
      Animated.timing(titleTranslate, {
        toValue: 0,
        duration: 600,
        easing: Easing.out(Easing.cubic),
        useNativeDriver: true,
      }),
      Animated.timing(detailsFade, {
        toValue: 1,
        duration: 500,
        delay: 600,
        useNativeDriver: true,
      }),
      Animated.timing(detailsTranslate, {
        toValue: 0,
        duration: 500,
        delay: 600,
        easing: Easing.out(Easing.cubic),
        useNativeDriver: true,
      }),
    ]).start();
  }, []);

  return (
    <ImageBackground
      source={require('../public/images/nature_collection_38_20250803_185759.png')}
      style={styles.container}
      imageStyle={styles.backgroundImage}
    >
      <View style={styles.overlay}>
        <Animated.Text
          style={[
            styles.title,
            {
              opacity: titleFade,
              transform: [{ translateY: titleTranslate }]
            }
          ]}
        >
          {title}
        </Animated.Text>

        <View style={styles.ringsContainer}>
          {financialData.map((data, index) => (
            <View key={data.label} style={styles.ringWrapper}>
              <CircleProgress data={data} index={index} />
            </View>
          ))}
        </View>

        <Animated.View
          style={[
            styles.detailsContainer,
            {
              opacity: detailsFade,
              transform: [{ translateY: detailsTranslate }]
            }
          ]}
        >
          {financialData.map((activity) => (
            <View key={activity.label} style={styles.detailRow}>
              <View style={styles.labelContainer}>
                <Text style={styles.iconEmoji}>{activity.icon}</Text>
                <Text style={styles.labelText}>{activity.label}</Text>
              </View>
              <View style={styles.valueContainer}>
                <View style={styles.progressBarContainer}>
                  <View 
                    style={[
                      styles.progressBarFill, 
                      { 
                        width: `${Math.min(activity.value, 100)}%`,
                        backgroundColor: activity.color,
                      }
                    ]} 
                  />
                </View>
                <Text style={[styles.valueText, { color: activity.color }]}>
                  {Math.round(activity.value)}%
                </Text>
              </View>
            </View>
          ))}
        </Animated.View>
      </View>
    </ImageBackground>
  );
}

const styles = StyleSheet.create({
  container: {
    borderRadius: 24,
    margin: 16,
    overflow: 'hidden',
  },
  backgroundImage: {
    opacity: 0.45,
  },
  overlay: {
    backgroundColor: 'rgba(15, 23, 42, 0.92)',
    borderRadius: 24,
    padding: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.4,
    shadowRadius: 12,
    elevation: 12,
  },
  title: {
    fontSize: 22,
    fontWeight: '800',
    color: '#fff',
    textAlign: 'center',
    marginBottom: 24,
    letterSpacing: 0.5,
  },
  ringsContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    height: 200,
    marginBottom: 28,
  },
  ringWrapper: {
    position: 'absolute',
  },
  circleContainer: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  centerContent: {
    position: 'absolute',
    justifyContent: 'center',
    alignItems: 'center',
    gap: 2,
  },
  iconText: {
    fontSize: 24,
    marginBottom: 2,
  },
  percentageText: {
    fontWeight: '800',
    letterSpacing: 0.5,
  },
  detailsContainer: {
    gap: 16,
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 16,
    backgroundColor: 'rgba(255, 255, 255, 0.03)',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.05)',
  },
  labelContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  iconEmoji: {
    fontSize: 20,
  },
  labelText: {
    fontSize: 15,
    fontWeight: '700',
    color: '#e2e8f0',
    letterSpacing: 0.5,
  },
  valueContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  progressBarContainer: {
    width: 80,
    height: 6,
    backgroundColor: 'rgba(255, 255, 255, 0.08)',
    borderRadius: 3,
    overflow: 'hidden',
  },
  progressBarFill: {
    height: '100%',
    borderRadius: 3,
  },
  valueText: {
    fontSize: 16,
    fontWeight: '800',
    minWidth: 45,
    textAlign: 'right',
  },
});
