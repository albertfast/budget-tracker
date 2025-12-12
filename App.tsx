import 'react-native-gesture-handler';
import * as React from 'react';
import { StyleSheet } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { Ionicons } from '@expo/vector-icons'; // or react-native-vector-icons
import { AuthProvider } from './src/context/AuthContext';

import HomeScreen from './src/screens/HomeScreen';
import TransactionsScreen from './src/screens/TransactionsScreen';
import AddScreen from './src/screens/AddScreen';
import ConnectAccountScreen from './src/screens/ConnectAccountScreen';
import AccountScreen from './src/screens/AccountScreen';

const Tab = createBottomTabNavigator();

export default function App() {
  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <AuthProvider>
        <NavigationContainer>
          <Tab.Navigator
            screenOptions={({ route }) => ({
              headerShown: false,
              tabBarStyle: { 
                backgroundColor: '#0f172a',
                borderTopWidth: 0,
                height: 70,
                paddingBottom: 10,
                paddingTop: 10,
                elevation: 20,
                shadowColor: '#000',
                shadowOffset: { width: 0, height: -4 },
                shadowOpacity: 0.3,
                shadowRadius: 12,
              },
              tabBarActiveTintColor: '#3b82f6',   
              tabBarInactiveTintColor: '#64748b',
              tabBarIconStyle: { marginTop: 0 },   
              tabBarLabelStyle: { 
                marginBottom: 0,
                fontSize: 12,
                fontWeight: '600',
              },
              tabBarIcon: ({ focused, color, size }) => {
                let iconName: keyof typeof Ionicons.glyphMap = 'home-outline';

                if (route.name === 'Home') {
                  iconName = focused ? 'home' : 'home-outline';
                } else if (route.name === 'Transactions') {
                  iconName = focused ? 'list' : 'list-outline';
                } else if (route.name === 'Add') {
                  iconName = focused ? 'add-circle' : 'add-circle-outline';
                } else if (route.name === 'Connect Account') {
                  iconName = focused ? 'link' : 'link-outline';
                } else if (route.name === 'Account') {
                  iconName = focused ? 'person' : 'person-outline';
                }

                return <Ionicons name={iconName} size={focused ? 28 : 24} color={color} />;
              },
            })}
          >
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
