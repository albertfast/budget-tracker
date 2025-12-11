import { Platform } from 'react-native';

// Default to the IP that was working previously, but allow override via env var
// For Android Emulator, 10.0.2.2 points to the host's localhost
// For iOS Simulator, localhost works
// For physical device, use the LAN IP
const DEFAULT_API_URL = Platform.select({
  android: 'http://10.0.2.2:8001', // Default for Android Emulator
  ios: 'http://localhost:8001',    // Default for iOS Simulator
  default: 'http://192.168.1.223:8001' // Fallback / Physical device default
});

export const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || DEFAULT_API_URL;

console.log('API_BASE_URL configured as:', API_BASE_URL);
