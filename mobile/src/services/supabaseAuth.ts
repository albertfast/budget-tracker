import * as AuthSession from 'expo-auth-session';
import * as Linking from 'expo-linking';
import { supabase } from './supabaseClient';
import { makeRedirectUri } from 'expo-auth-session';

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
  const { error } = await supabase.auth.signOut();
  if (error) throw error;
}

export async function signInWithGoogle() {
  const redirectTo = makeRedirectUri({ scheme: 'smartbudget' });

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

  const result = await (AuthSession as any).startAsync({ authUrl });
  if (result.type !== 'success') throw new Error('Google sign-in cancelled');

  // Exchange code for session
  const url = result.url as string;
  const { error: exchangeError } = await supabase.auth.exchangeCodeForSession(url);
  if (exchangeError) throw exchangeError;

  // Return current session
  const { data: sessionData } = await supabase.auth.getSession();
  return sessionData.session;
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
