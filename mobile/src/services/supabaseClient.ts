import 'react-native-get-random-values'; // Needed for UUID + crypto in supabase-js
import 'react-native-url-polyfill/auto'; // Ensures URL/URLSearchParams exist on native
import { createClient } from '@supabase/supabase-js';
import Constants from 'expo-constants';

const configExtra = (Constants.expoConfig?.extra || {}) as Record<string, string | undefined>;
export const supabaseUrl =
  process.env.EXPO_PUBLIC_SUPABASE_URL ||
  process.env.SUPABASE_URL ||
  (configExtra.SUPABASE_URL as string);
const supabaseAnonKey =
  process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY ||
  process.env.SUPABASE_ANON_KEY ||
  (configExtra.SUPABASE_ANON_KEY as string);

if (!supabaseUrl || !supabaseAnonKey) {
  // eslint-disable-next-line no-console
  console.warn('[Supabase] Missing SUPABASE_URL or SUPABASE_ANON_KEY. Set EXPO_PUBLIC_SUPABASE_URL and EXPO_PUBLIC_SUPABASE_ANON_KEY.');
} else {
  console.log('[Supabase] Initialized with URL:', supabaseUrl);
}

// Try to use AsyncStorage if available; fall back to in-memory storage
export let storage: any;
try {
  // eslint-disable-next-line @typescript-eslint/no-var-requires
  storage = require('@react-native-async-storage/async-storage').default;
} catch (e) {
  const mem = new Map<string, string>();
  storage = {
    getItem: async (key: string) => mem.get(key) ?? null,
    setItem: async (key: string, value: string) => {
      mem.set(key, value);
    },
    removeItem: async (key: string) => {
      mem.delete(key);
    },
  } as any;
}

import { Platform } from 'react-native';

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
    detectSessionInUrl: Platform.OS === 'web', // Enable on web
    storage: Platform.OS === 'web' ? undefined : storage, // Use default storage (localStorage) on web
  },
});

export default supabase;
