import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { supabase } from '../services/supabaseClient';
import type { Session, User } from '@supabase/supabase-js';

// Define types locally
interface SmartBudgetUser {
  id: string;
  email?: string;
  full_name?: string;
  avatar_url?: string;
  default_currency?: string;
}

interface AuthContextValue {
  session: Session | null;
  user: User | null;
  profile: SmartBudgetUser | null;
  loading: boolean;
  signOut: () => Promise<void>;
  refreshSession: () => Promise<void>;
  signIn: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  signUp: (email: string, password: string, fullName?: string) => Promise<{ success: boolean; error?: string }>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [session, setSession] = useState<Session | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [profile, setProfile] = useState<SmartBudgetUser | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    (async () => {
      const { data } = await supabase.auth.getSession();
      if (!mounted) return;
      setSession(data.session);
      setUser(data.session?.user ?? null);
      
      if (data.session?.user) {
        // Fetch user profile from profiles table
        const { data: profileData } = await supabase
          .from('profiles')
          .select('*')
          .eq('id', data.session.user.id)
          .single();
        
        if (profileData) {
          setProfile(profileData as SmartBudgetUser);
        }
      }
      
      setLoading(false);
    })();

    const { data: sub } = supabase.auth.onAuthStateChange(async (_event, s) => {
      setSession(s);
      setUser(s?.user ?? null);
      
      if (s?.user) {
        // Fetch user profile from profiles table
        const { data: profileData } = await supabase
          .from('profiles')
          .select('*')
          .eq('id', s.user.id)
          .single();
        
        if (profileData) {
          setProfile(profileData as SmartBudgetUser);
        }
      } else {
        setProfile(null);
      }
    });

    return () => {
      mounted = false;
      sub.subscription.unsubscribe();
    };
  }, []);

  const value = useMemo<AuthContextValue>(() => ({
    session,
    user,
    profile,
    loading,
    signOut: async () => {
      const { error } = await supabase.auth.signOut();
      if (error) {
        console.error('Error signing out:', error);
      }
    },
    refreshSession: async () => {
      const { data } = await supabase.auth.getSession();
      setSession(data.session);
      setUser(data.session?.user ?? null);
      
      if (data.session?.user) {
        // Fetch user profile from profiles table
        const { data: profileData } = await supabase
          .from('profiles')
          .select('*')
          .eq('id', data.session.user.id)
          .single();
        
        if (profileData) {
          setProfile(profileData as SmartBudgetUser);
        }
      }
    },
    signIn: async (email: string, password: string) => {
      try {
        const { data, error } = await supabase.auth.signInWithPassword({
          email,
          password,
        });
        
        if (error) {
          return {
            success: false,
            error: error.message
          };
        }
        
        return {
          success: !!data.user,
        };
      } catch (error: any) {
        return {
          success: false,
          error: error.message || 'Unknown error occurred'
        };
      }
    },
    signUp: async (email: string, password: string, fullName?: string) => {
      try {
        const { data, error } = await supabase.auth.signUp({
          email,
          password,
          options: {
            data: {
              full_name: fullName || '',
            }
          }
        });
        
        if (error) {
          return {
            success: false,
            error: error.message
          };
        }
        
        return {
          success: !!data.user,
        };
      } catch (error: any) {
        return {
          success: false,
          error: error.message || 'Unknown error occurred'
        };
      }
    }
  }), [session, user, profile, loading]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextValue => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
};
