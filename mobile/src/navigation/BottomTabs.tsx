import * as React from 'react';
import { Text } from 'react-native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import HomeScreen from '@/screens/HomeScreen';
import TransactionsScreen from '@/screens/TransactionsScreen';
import AddScreen from '@/screens/AddScreen';
import AccountScreen from '@/screens/AccountScreen';
import CompanyScreeningScreen from '@/screens/CompanyScreeningScreen';
import FinancialAnalysisScreenTwo from '@/screens/FinancialAnalysisScreenTwo';
import ConnectAccountScreen from '@/screens/ConnectAccountScreen';
import PortfolioChartScreen from '@/screens/PortfolioChartScreen';

type RootTabParamList = {
  Home: undefined;
  Transactions: undefined;
  Add: undefined;
  Screening: undefined;
  FinancialAnalysisTwo: undefined;
  'Connect Account': undefined;
  PortfolioChart: undefined;
  Account: undefined;
};

const Tab = createBottomTabNavigator<RootTabParamList>();

export default function BottomTabs() {
  return (
    <Tab.Navigator
      screenOptions={{
        headerShown: false,
        tabBarStyle: { 
          backgroundColor: '#0b1220',
          borderTopColor: '#1a2442',
          borderTopWidth: 1,
          paddingBottom: 8,
          paddingTop: 8,
          height: 65,
        },
        tabBarActiveTintColor: '#2196F3',
        tabBarInactiveTintColor: '#7a8fa5',
        tabBarLabelStyle: {
          fontSize: 11,
          fontWeight: '600',
          marginTop: 4,
        },
      }}
    >
      <Tab.Screen 
        name="Home" 
        component={HomeScreen}
        options={{
          tabBarLabel: 'Home',
          tabBarIcon: ({ color }) => <Text style={{ fontSize: 24 }}>🏠</Text>,
        }}
      />
      <Tab.Screen 
        name="Transactions" 
        component={TransactionsScreen}
        options={{
          tabBarLabel: 'Transactions',
          tabBarIcon: ({ color }) => <Text style={{ fontSize: 24 }}>💳</Text>,
        }}
      />
      <Tab.Screen 
        name="Screening" 
        component={CompanyScreeningScreen}
        options={{
          tabBarButton: () => null, // Hide from tab bar - access via Home screen
        }}
      />
      <Tab.Screen 
        name="Add" 
        component={AddScreen}
        options={{
          tabBarLabel: 'Add',
          tabBarIcon: ({ color }) => <Text style={{ fontSize: 24 }}>➕</Text>,
        }}
      />
      <Tab.Screen 
        name="Account" 
        component={AccountScreen}
        options={{
          tabBarLabel: 'Account',
          tabBarIcon: ({ color }) => <Text style={{ fontSize: 24 }}>👤</Text>,
        }}
      />
      {/* Hidden screens - accessible via navigation but not shown in tab bar */}
      <Tab.Screen 
        name="FinancialAnalysisTwo" 
        component={FinancialAnalysisScreenTwo}
        options={{
          tabBarButton: () => null, // Hide from tab bar
        }}
      />
      <Tab.Screen 
        name="Connect Account" 
        component={ConnectAccountScreen}
        options={{
          tabBarButton: () => null, // Hide from tab bar
        }}
      />
      <Tab.Screen 
        name="PortfolioChart" 
        component={PortfolioChartScreen}
        options={{
          tabBarButton: () => null, // Hide from tab bar
        }}
      />
    </Tab.Navigator>
  );
}
