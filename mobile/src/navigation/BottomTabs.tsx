import * as React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import HomeScreen from '@/screens/HomeScreen';
import TransactionsScreen from '@/screens/TransactionsScreen';
import AddScreen from '@/screens/AddScreen';
import AccountScreen from '@/screens/AccountScreen';

type RootTabParamList = {
  Home: undefined;
  Transactions: undefined;
  Add: undefined;
  Account: undefined;
};

const Tab = createBottomTabNavigator<RootTabParamList>();

export default function BottomTabs() {
  return (
    <Tab.Navigator
      screenOptions={{
        headerShown: false,
        tabBarStyle: { display: 'none' }, // Hide bottom tabs
        tabBarActiveTintColor: '#0b1220',
        tabBarInactiveTintColor: '#666'
      }}
    >
      <Tab.Screen name="Home" component={HomeScreen} />
      <Tab.Screen name="Transactions" component={TransactionsScreen} />
      <Tab.Screen name="Add" component={AddScreen} />
      <Tab.Screen name="Account" component={AccountScreen} />
    </Tab.Navigator>
  );
}
