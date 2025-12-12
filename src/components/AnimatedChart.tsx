import React, { useEffect, useRef } from 'react';
import { View, StyleSheet, Dimensions, Animated, Text, Easing } from 'react-native';
import Svg, { Line } from 'react-native-svg';
import { LinearGradient } from 'expo-linear-gradient';

interface ChartData {
  month: string;
  amount: number;
  color: string;
}

export default function AnimatedChart({
  title = "Monthly Spending Trend",
  data = [],
}: {
  title?: string;
  data?: ChartData[];
}) {
  const { width } = Dimensions.get('window');
  const chartWidth = width - 64;
  const chartHeight = 200;
  
  // Handle empty data case
  const safeData = data.length > 0 ? data : Array(6).fill({ month: '', amount: 0, color: '#333' });
  
  const barWidth = (chartWidth / safeData.length) * 0.6;
  const spacing = (chartWidth / safeData.length) * 0.4;

  const maxValue = Math.max(...safeData.map(d => d.amount), 1);

  const titleFade = useRef(new Animated.Value(0)).current;
  const titleTranslate = useRef(new Animated.Value(-20)).current;

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

        <View style={styles.chartContainer}>
          {/* Grid lines using SVG */}
          <Svg width={chartWidth} height={chartHeight} style={styles.gridSvg}>
            {[0, 1, 2, 3, 4].map((i) => (
              <Line
                key={i}
                x1={0}
                y1={(chartHeight / 4) * i}
                x2={chartWidth}
                y2={(chartHeight / 4) * i}
                stroke="#ffffff"
                strokeWidth="1"
                opacity={0.15}
              />
            ))}
          </Svg>

        {/* Bars Container */}
        <View style={[styles.barsContainer, { width: chartWidth, height: chartHeight }]}>
          {safeData.map((item, index) => {
            const barHeight = (item.amount / maxValue) * chartHeight;
            const animHeight = useRef(new Animated.Value(0)).current;

            useEffect(() => {
              Animated.timing(animHeight, {
                toValue: barHeight,
                duration: 800,
                delay: index * 100,
                easing: Easing.out(Easing.cubic),
                useNativeDriver: false, // Height animation doesn't support native driver
              }).start();
            }, [barHeight, index]);

            return (
              <View 
                key={index} 
                style={[
                  styles.barWrapper, 
                  { 
                    left: index * (barWidth + spacing) + spacing / 2,
                    width: barWidth,
                  }
                ]}
              >
                <Animated.View
                  style={[
                    styles.bar,
                    {
                      backgroundColor: item.color,
                      width: '100%',
                      height: animHeight,
                    }
                  ]}
                />
              </View>
            );
          })}
        </View>

        {/* X-axis labels */}
        <View style={[styles.xAxisLabels, { width: chartWidth }]}>
          {safeData.map((item, index) => {
            const labelFade = useRef(new Animated.Value(0)).current;
            
            useEffect(() => {
              Animated.timing(labelFade, {
                toValue: 1,
                duration: 500,
                delay: 600 + index * 50,
                useNativeDriver: true,
              }).start();
            }, [index]);

            return (
              <Animated.Text
                key={index}
                style={[
                  styles.xLabel, 
                  { 
                    width: barWidth + spacing,
                    opacity: labelFade
                  }
                ]}
              >
                {item.month}
              </Animated.Text>
            );
          })}
        </View>
      </View>
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
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
    textAlign: 'center',
    marginBottom: 20,
  },
  chartContainer: {
    alignItems: 'center',
    position: 'relative',
    height: 230, // chartHeight + labels
  },
  gridSvg: {
    position: 'absolute',
    top: 0,
    left: 0,
  },
  barsContainer: {
    position: 'absolute',
    top: 0,
    left: 0,
    flexDirection: 'row',
  },
  barWrapper: {
    position: 'absolute',
    bottom: 0,
    justifyContent: 'flex-end',
    height: '100%',
  },
  bar: {
    borderTopLeftRadius: 4,
    borderTopRightRadius: 4,
    opacity: 0.8,
  },
  xAxisLabels: {
    position: 'absolute',
    bottom: -25,
    flexDirection: 'row',
    justifyContent: 'flex-start',
  },
  xLabel: {
    fontSize: 12,
    color: '#9fb3c8',
    textAlign: 'center',
  },
});
