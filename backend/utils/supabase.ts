// Supabase Client Configuration
import { createClient } from '@supabase/supabase-js';
import type { RealtimePostgresChangesFilter } from '@supabase/realtime-js';
import ConfigService from '../services/config';

const config = ConfigService;

export const supabase = createClient(
  config.supabase.url,
  config.supabase.anonKey,
  {
    auth: {
      persistSession: true,
      autoRefreshToken: true,
      detectSessionInUrl: true
    }
  }
);

// Auth helper functions
export const auth = {
  // Get current user
  getCurrentUser: () => supabase.auth.getUser(),
  
  // Sign in with email and password
  signIn: (email: string, password: string) => 
    supabase.auth.signInWithPassword({ email, password }),
  
  // Sign up with email and password
  signUp: (email: string, password: string, options?: any) => 
    supabase.auth.signUp({ email, password, options }),
  
  // Sign out
  signOut: () => supabase.auth.signOut(),
  
  // Reset password
  resetPassword: (email: string) => 
    supabase.auth.resetPasswordForEmail(email),
  
  // Update password
  updatePassword: (password: string) => 
    supabase.auth.updateUser({ password }),
  
  // Listen to auth changes
  onAuthStateChange: (callback: (event: any, session: any) => void) => 
    supabase.auth.onAuthStateChange(callback)
};

// Database helper functions
export const db = {
  // Generic select function
  select: (table: string, columns: string = '*', filters: any = {}) => {
    let query = supabase.from(table).select(columns);
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        query = query.eq(key, value);
      }
    });
    
    return query;
  },
  
  // Generic insert function
  insert: (table: string, data: any) => 
    supabase.from(table).insert(data),
  
  // Generic update function
  update: (table: string, data: any, filters: any) => {
    let query = supabase.from(table).update(data);
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        query = query.eq(key, value);
      }
    });
    
    return query;
  },
  
  // Generic delete function
  delete: (table: string, filters: any) => {
    let query = supabase.from(table).delete();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        query = query.eq(key, value);
      }
    });
    
    return query;
  }
};

// Real-time subscriptions
type PostgresChangeEvent = 'INSERT' | 'UPDATE' | 'DELETE' | '*';

export const subscribeToTable = (
  table: string,
  event: PostgresChangeEvent,
  callback: (payload: any) => void
) => {
  switch (event) {
    case '*':
      return supabase
        .channel(`table-changes-${table}`)
        .on(
          'postgres_changes',
          { event: '*', schema: 'public', table } satisfies RealtimePostgresChangesFilter<'*'>,
          callback
        )
        .subscribe();
    case 'INSERT':
      return supabase
        .channel(`table-changes-${table}`)
        .on(
          'postgres_changes',
          { event: 'INSERT', schema: 'public', table } satisfies RealtimePostgresChangesFilter<'INSERT'>,
          callback
        )
        .subscribe();
    case 'UPDATE':
      return supabase
        .channel(`table-changes-${table}`)
        .on(
          'postgres_changes',
          { event: 'UPDATE', schema: 'public', table } satisfies RealtimePostgresChangesFilter<'UPDATE'>,
          callback
        )
        .subscribe();
    case 'DELETE':
      return supabase
        .channel(`table-changes-${table}`)
        .on(
          'postgres_changes',
          { event: 'DELETE', schema: 'public', table } satisfies RealtimePostgresChangesFilter<'DELETE'>,
          callback
        )
        .subscribe();
    default:
      return supabase
        .channel(`table-changes-${table}`)
        .on(
          'postgres_changes',
          { event: '*', schema: 'public', table } satisfies RealtimePostgresChangesFilter<'*'>,
          callback
        )
        .subscribe();
  }
};

// Storage helper functions
export const storage = {
  // Upload file
  upload: (bucket: string, path: string, file: File) => 
    supabase.storage.from(bucket).upload(path, file),
  
  // Download file
  download: (bucket: string, path: string) => 
    supabase.storage.from(bucket).download(path),
  
  // Get public URL
  getPublicUrl: (bucket: string, path: string) => 
    supabase.storage.from(bucket).getPublicUrl(path),
  
  // Delete file
  delete: (bucket: string, paths: string[]) => 
    supabase.storage.from(bucket).remove(paths)
};

// Error handling helper
export const handleSupabaseError = (error: any): string => {
  if (error?.message) {
    return error.message;
  }
  
  if (typeof error === 'string') {
    return error;
  }
  
  return 'An unexpected error occurred';
};

// Connection check
export const checkConnection = async (): Promise<boolean> => {
  try {
    const { data, error } = await supabase.from('profiles').select('count').limit(1);
    return !error;
  } catch {
    return false;
  }
};

export default supabase;
