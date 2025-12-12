import React, { useEffect, useRef } from 'react';
import { View, Text, StyleSheet, Animated, Easing, ImageBackground } from 'react-native';
import Svg, { Circle, Defs, LinearGradient, Stop } from 'react-native-svg';

const AnimatedCircle = Animated.createAnimatedComponent(Circle);

interface FinancialData {
  label: string;
  value: number;
  color: string;
  size: number;
  current: number;
  target: number;
  unit: string;
}

interface CircleProgressProps {
  data: FinancialData;
  index: number;
}

const CircleProgress: React.FC<CircleProgressProps> = ({ data, index }) => {
  const strokeWidth = 12;
  const radius = (data.size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  
  const animatedValue = useRef(new Animated.Value(0)).current;
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const scaleAnim = useRef(new Animated.Value(0.8)).current;

  useEffect(() => {
    // Progress Animation
    const progressTarget = ((100 - Math.min(data.value, 100)) / 100) * circumference;
    
    Animated.parallel([
      Animated.timing(animatedValue, {
        toValue: progressTarget,
        duration: 1500,
        delay: index * 200,
        easing: Easing.out(Easing.cubic),
        useNativeDriver: false, // SVG strokeDashoffset doesn't support native driver
      }),
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 800,
        delay: index * 200,
        useNativeDriver: true,
      }),
      Animated.timing(scaleAnim, {
        toValue: 1,
        duration: 800,
        delay: index * 200,
        easing: Easing.out(Easing.back(1.5)),
        useNativeDriver: true,
      }),
    ]).start();
  }, [data.value, circumference, index]);

  return (
    <Animated.View
      style={[
        styles.circleContainer, 
        { 
          width: data.size, 
          height: data.size,
          opacity: fadeAnim,
          transform: [{ scale: scaleAnim }]
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
          <LinearGradient
            id={`gradient-${data.label.toLowerCase()}`}
            x1="0%"
            y1="0%"
            x2="100%"
            y2="100%"
          >
            <Stop offset="0%" stopColor={data.color} stopOpacity={1} />
            <Stop offset="100%" stopColor={data.color} stopOpacity={0.6} />
          </LinearGradient>
        </Defs>

        {/* Background circle */}
        <Circle
          cx={data.size / 2}
          cy={data.size / 2}
          r={radius}
          fill="none"
          stroke="#1a2332"
          strokeWidth={strokeWidth}
          opacity={0.3}
        />

        {/* Progress circle with animation */}
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
        />
      </Svg>

      {/* Center percentage */}
      <View style={[styles.centerContent, { width: data.size, height: data.size }]}>
        <Animated.Text
          style={[
            styles.percentageText, 
            { 
              color: data.color,
              opacity: fadeAnim,
              transform: [{ scale: scaleAnim }]
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
      color: "#FF6B6B",
      size: 160,
      current: 0, 
      target: 0,
      unit: "%",
    },
    {
      label: "SAVINGS",
      value: savingsGoal,
      color: "#4ECDC4",
      size: 120,
      current: 0,
      target: 0,
      unit: "%",
    },
    {
      label: "INVEST",
      value: investmentsGrowth,
      color: "#FFD93D",
      size: 80,
      current: 0,
      target: 0,
      unit: "%",
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
    <LinearGradient
      colors={['#1a2332', '#0a0e27', '#050714']}
      start={{ x: 0, y: 0 }}
      end={{ x: 1, y: 1 }}
      style={styles.container}
    >
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
              transform: [{ translateX: detailsTranslate }]
            }
          ]}
        >
          {financialData.map((activity) => (
            <View key={activity.label} style={styles.detailRow}>
              <View style={styles.labelContainer}>
                <View style={[styles.colorDot, { backgroundColor: activity.color }]} />
                <Text style={styles.labelText}>{activity.label}</Text>
              </View>
              <View style={styles.valueContainer}>
                <Text style={[styles.valueText, { color: activity.color }]}>
                  {Math.round(activity.value)}%
                </Text>
              </View>
            </View>
          ))}
        </Animated.View>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    borderRadius: 20,
    padding: 20,
    margin: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  title: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#fff',
    textAlign: 'center',
    marginBottom: 20,
  },
  ringsContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    height: 180,
    marginBottom: 20,
  },
  ringWrapper: {
    position: 'absolute',
  },
  circleContainer: {
    position: 'absolute',
    justifyContent: 'center',
    alignItems: 'center',
  },
  centerContent: {
    position: 'absolute',
    justifyContent: 'center',
    alignItems: 'center',
  },
  percentageText: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  detailsContainer: {
    gap: 12,
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
  },
  labelContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  colorDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  labelText: {
    fontSize: 14,
    fontWeight: '500',
    color: '#9fb3c8',
  },
  valueContainer: {
    flexDirection: 'row',
    alignItems: 'baseline',
  },
  valueText: {
    fontSize: 16,
    fontWeight: 'bold',
  },
});
