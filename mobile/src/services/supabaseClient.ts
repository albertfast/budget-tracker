import 'react-native-get-random-values';
import 'react-native-url-polyfill/auto';
import { createClient } from '@supabase/supabase-js';
import Constants from 'expo-constants';

const supabaseUrl = (Constants.expoConfig?.extra as any)?.SUPABASE_URL as string;
const supabaseAnonKey = (Constants.expoConfig?.extra as any)?.SUPABASE_ANON_KEY as string;

if (!supabaseUrl || !supabaseAnonKey) {
  // eslint-disable-next-line no-console
  console.warn('[Supabase] Missing SUPABASE_URL or SUPABASE_ANON_KEY in app.json extra');
}

// Try to use AsyncStorage if available; fall back to in-memory storage
let storage: any;
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

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
    detectSessionInUrl: false, // handled by AuthSession on native
    storage,
  },
});

export default supabase;
