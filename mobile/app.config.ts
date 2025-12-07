import { ExpoConfig, ConfigContext } from 'expo/config';

export default ({ config }: ConfigContext): ExpoConfig => ({
  ...config,
  name: 'SmartBudget',
  slug: 'smartbudget',
  version: '0.1.0',
  orientation: 'portrait',
  assetBundlePatterns: ['**/*'],
  platforms: ['ios', 'android', 'web'],
  scheme: 'smartbudget',
  plugins: [
    'expo-asset',
    'expo-web-browser'
  ],
  extra: {
    SUPABASE_URL: process.env.EXPO_PUBLIC_SUPABASE_URL,
    SUPABASE_ANON_KEY: process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY,
  },
});
