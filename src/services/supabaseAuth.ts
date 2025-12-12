import * as AuthSession from 'expo-auth-session';
import * as WebBrowser from 'expo-web-browser';
import { Platform } from 'react-native';
import Constants from 'expo-constants';
import { supabase, storage, supabaseUrl } from './supabaseClient';

const { makeRedirectUri } = AuthSession;

WebBrowser.maybeCompleteAuthSession();
// Warm up the browser to improve startup time
void WebBrowser.warmUpAsync();

const redirectTo = (() => {
  if (Platform.OS === 'web') {
    return typeof window !== 'undefined' ? window.location.origin : 'http://localhost:8081';
  }
  
  // For mobile (Expo Go), we let makeRedirectUri detect the correct scheme (exp://)
  // We set preferLocalhost to false to ensure we get the LAN IP, which is required for physical devices.
  const uri = makeRedirectUri({
    path: 'auth/callback',
    preferLocalhost: false,
  });

  console.log('---------------------------------------------------');
  console.log('⚠️  Supabase Redirect URL:', uri);
  console.log('ACTION REQUIRED: Ensure this EXACT URL is in your Supabase Redirect URLs list!');
  console.log('NOTE: If your Wi-Fi IP changes, you must update Supabase.');
  console.log('---------------------------------------------------');
  return uri;
})();

console.log('---------------------------------------------------');
console.log('⚠️  Supabase Redirect URL:', redirectTo);
console.log('---------------------------------------------------');

export async function signInWithEmail(email: string, password: string) {
  const { data, error } = await supabase.auth.signInWithPassword({ email, password });
  if (error) throw error;
  return data.session;
}

export async function signUpWithEmail(email: string, password: string, username?: string) {
  const { data, error } = await supabase.auth.signUp({ email, password });
  if (error) throw error;
  const user = data.user;
  // Optionally set username in profiles after signup
  if (user && username && username.trim()) {
    await supabase.from('profiles').upsert(
      { id: user.id, email, username: username.trim() },
      { onConflict: 'id' }
    );
  }
  return user;
}

export async function signOut() {
  try {
    const { error } = await supabase.auth.signOut();
    if (error) console.warn('Sign out error (ignored):', error);
  } catch (e) {
    console.warn('Sign out exception (ignored):', e);
  }
  
  // Force local cleanup. If the token was invalid (403), signOut might fail 
  // to clear local storage, leaving the user in a "logged in" state locally.
  try {
    if (supabaseUrl && storage) {
      // Extract project ref from URL (e.g., https://xyz.supabase.co -> xyz)
      // Handle both https://ojcvjsxmshdvyxryunvk.supabase.co and xyz.supabase.co
      const tempUrl = supabaseUrl.startsWith('http') ? supabaseUrl : `https://${supabaseUrl}`;
      const hostname = new URL(tempUrl).hostname;
      const projectRef = hostname.split('.')[0];
      const storageKey = `sb-${projectRef}-auth-token`;
      
      await storage.removeItem(storageKey);
    }
  } catch (cleanupError) {
    console.warn('Failed to manually clear session storage:', cleanupError);
  }
}

export async function signInWithGoogle() {
  if (Platform.OS === 'web') {
    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: typeof window !== 'undefined' ? window.location.origin : undefined,
        queryParams: {
          prompt: 'select_account',
        },
      },
    });
    if (error) throw error;
    return null; // Web redirects, so no session returned immediately
  }

  const { data, error } = await supabase.auth.signInWithOAuth({
    provider: 'google',
    options: {
      redirectTo,
      skipBrowserRedirect: true,
      queryParams: {
        // Optional: force select account
        prompt: 'select_account',
      },
    },
  });
  if (error) throw error;

  // Open browser for OAuth
  const authUrl = data?.url;
  if (!authUrl) throw new Error('Failed to get OAuth URL');

  console.log('[Auth] Opening Auth Session URL:', authUrl);
  const result = await WebBrowser.openAuthSessionAsync(authUrl, redirectTo);
  if (result.type !== 'success') throw new Error('Google sign-in cancelled');

  // Parse the result URL to handle both Implicit (access_token) and PKCE (code) flows
  const url = result.url;
  const params: Record<string, string> = {};
  
  // Extract params from both query (?) and hash (#)
  const queryString = url.split('?')[1];
  const hashString = url.split('#')[1];

  if (queryString) {
    queryString.split('&').forEach(param => {
      const [key, value] = param.split('=');
      params[key] = decodeURIComponent(value);
    });
  }
  if (hashString) {
    hashString.split('&').forEach(param => {
      const [key, value] = param.split('=');
      params[key] = decodeURIComponent(value);
    });
  }

  if (params.error) throw new Error(params.error_description || params.error);

  // Case 1: Implicit Grant (access_token returned directly)
  if (params.access_token && params.refresh_token) {
    const { data: sessionData, error: sessionError } = await supabase.auth.setSession({
      access_token: params.access_token,
      refresh_token: params.refresh_token,
    });
    if (sessionError) throw sessionError;
    return sessionData.session;
  }

  // Case 2: PKCE (code returned)
  if (params.code) {
    const { data: sessionData, error: exchangeError } = await supabase.auth.exchangeCodeForSession(params.code);
    if (exchangeError) throw exchangeError;
    return sessionData.session;
  }

  // Fallback: If we can't find tokens or code, throw error
  throw new Error('No session data found in redirect URL');
}

export async function resolveEmailFromIdentifier(identifier: string): Promise<string> {
  // If it's an email, return as-is
  if (identifier.includes('@')) return identifier;
  // Otherwise try to resolve username -> email from public.profiles
  const { data, error } = await supabase
    .from('profiles')
    .select('email')
    .eq('username', identifier)
    .maybeSingle();
  if (error) throw error;
  if (!data?.email) throw new Error('Username not found');
  return data.email;
}
