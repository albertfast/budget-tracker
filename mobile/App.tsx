import 'react-native-gesture-handler';
import * as React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import HomeScreen from './src/screens/HomeScreen';
import TransactionsScreen from './src/screens/TransactionsScreen';
import AddScreen from './src/screens/AddScreen';
import ConnectAccountScreen from './src/screens/ConnectAccountScreen';
import AccountScreen from './src/screens/AccountScreen';
import { AuthProvider } from './src/context/AuthContext';

const Tab = createBottomTabNavigator();

export default function App() {
  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <AuthProvider>
        <NavigationContainer>
          <Tab.Navigator screenOptions={{ 
          headerShown: false, 
          tabBarStyle: { display: 'none' }, // Hide bottom tabs
          tabBarActiveTintColor: '#0b1220', 
          tabBarInactiveTintColor: '#666' 
          }}>
            <Tab.Screen name="Home" component={HomeScreen} />
            <Tab.Screen name="Transactions" component={TransactionsScreen} />
            <Tab.Screen name="Add" component={AddScreen} />
            <Tab.Screen name="Connect Account" component={ConnectAccountScreen} />
            <Tab.Screen name="Account" component={AccountScreen} />
          </Tab.Navigator>
        </NavigationContainer>
      </AuthProvider>
    </GestureHandlerRootView>
  );
}

const styles = StyleSheet.create({});
