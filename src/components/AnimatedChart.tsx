import React, { useEffect, useRef } from 'react';
import { View, StyleSheet, Dimensions, Animated, Text, Easing, ImageBackground } from 'react-native';
import Svg, { Line, Defs, LinearGradient as SvgLinearGradient, Stop, Rect, Text as SvgText } from 'react-native-svg';

const AnimatedRect = Animated.createAnimatedComponent(Rect);

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
  const chartWidth = width - 80;
  const chartHeight = 240;
  
  // Handle empty data case
  const safeData = data.length > 0 ? data : Array(6).fill({ month: '', amount: 0, color: '#3b82f6' });
  
  const barWidth = (chartWidth / safeData.length) * 0.7;
  const spacing = (chartWidth / safeData.length) * 0.3;

  const maxValue = Math.max(...safeData.map(d => d.amount), 100);

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
    <ImageBackground
      source={require('../public/images/image-1765508315456.png')}
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

        {/* Summary Stats */}
        <View style={styles.statsRow}>
          <View style={styles.statBox}>
            <Text style={styles.statValue}>${(safeData.reduce((sum, d) => sum + d.amount, 0) / 1000).toFixed(1)}k</Text>
            <Text style={styles.statLabel}>Total</Text>
          </View>
          <View style={styles.statBox}>
            <Text style={styles.statValue}>${(safeData.reduce((sum, d) => sum + d.amount, 0) / safeData.length / 1000).toFixed(1)}k</Text>
            <Text style={styles.statLabel}>Average</Text>
          </View>
          <View style={styles.statBox}>
            <Text style={styles.statValue}>${(Math.max(...safeData.map(d => d.amount)) / 1000).toFixed(1)}k</Text>
            <Text style={styles.statLabel}>Peak</Text>
          </View>
        </View>

        <View style={styles.chartContainer}>
          {/* Modern Chart with SVG Bars */}
          <Svg width={chartWidth} height={chartHeight + 40} style={styles.chartSvg}>
            <Defs>
              {safeData.map((item, idx) => (
                <SvgLinearGradient
                  key={`gradient-${idx}`}
                  id={`barGradient-${idx}`}
                  x1="0%"
                  y1="0%"
                  x2="0%"
                  y2="100%"
                >
                  <Stop offset="0%" stopColor={item.color} stopOpacity={0.9} />
                  <Stop offset="100%" stopColor={item.color} stopOpacity={0.4} />
                </SvgLinearGradient>
              ))}
            </Defs>

            {/* Grid lines - subtle */}
            {[0, 1, 2, 3, 4].map((i) => (
              <Line
                key={`grid-${i}`}
                x1={0}
                y1={(chartHeight / 4) * i}
                x2={chartWidth}
                y2={(chartHeight / 4) * i}
                stroke="rgba(255, 255, 255, 0.1)"
                strokeWidth="1"
                strokeDasharray="4 4"
              />
            ))}

            {/* Animated Bars with Gradient */}
            {safeData.map((item, index) => {
              const barHeight = (item.amount / maxValue) * (chartHeight - 20);
              const x = index * (barWidth + spacing) + spacing / 2;
              const y = chartHeight - barHeight;
              
              const animHeight = useRef(new Animated.Value(chartHeight)).current;
              const animOpacity = useRef(new Animated.Value(0)).current;

              useEffect(() => {
                Animated.parallel([
                  Animated.timing(animHeight, {
                    toValue: y,
                    duration: 1000,
                    delay: index * 120,
                    easing: Easing.out(Easing.cubic),
                    useNativeDriver: false,
                  }),
                  Animated.timing(animOpacity, {
                    toValue: 1,
                    duration: 600,
                    delay: index * 120,
                    useNativeDriver: false,
                  }),
                ]).start();
              }, [barHeight, index]);

              return (
                <AnimatedRect
                  key={`bar-${index}`}
                  x={x}
                  y={animHeight}
                  width={barWidth}
                  height={barHeight}
                  fill={`url(#barGradient-${index})`}
                  rx={6}
                  ry={6}
                  opacity={animOpacity}
                />
              );
            })}

            {/* X-axis labels */}
            {safeData.map((item, index) => {
              const x = index * (barWidth + spacing) + spacing / 2 + barWidth / 2;
              
              return (
                <SvgText
                  key={`label-${index}`}
                  x={x}
                  y={chartHeight + 25}
                  fontSize={13}
                  fontWeight="600"
                  fill="#9fb3c8"
                  textAnchor="middle"
                >
                  {item.month}
                </SvgText>
              );
            })}
          </Svg>
        </View>
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
    opacity: 0.55,
  },
  overlay: {
    backgroundColor: 'rgba(15, 23, 42, 0.50)',
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
    marginBottom: 20,
    letterSpacing: 0.5,
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 24,
    gap: 12,
  },
  statBox: {
    flex: 1,
    backgroundColor: 'rgba(59, 130, 246, 0.1)',
    borderRadius: 12,
    padding: 12,
    borderWidth: 1,
    borderColor: 'rgba(59, 130, 246, 0.2)',
    alignItems: 'center',
  },
  statValue: {
    fontSize: 18,
    fontWeight: '700',
    color: '#3b82f6',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 11,
    fontWeight: '600',
    color: '#9fb3c8',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  chartContainer: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  chartSvg: {
    overflow: 'visible',
  },
});
