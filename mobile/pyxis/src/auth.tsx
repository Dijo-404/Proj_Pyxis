/** Minimal in-memory auth for the prototype. Hardcoded demo credential. */

import React, { createContext, useContext, useMemo, useState } from 'react';
import { DEMO_USER } from './mockData';
import { User } from './types';

const VALID_EMAIL = 'prie@gmail.com';
const VALID_PASSWORD = '123456';

interface AuthState {
  user: User | null;
  signIn: (email: string, password: string) => { ok: boolean; error?: string };
  signOut: () => void;
}

const AuthContext = createContext<AuthState | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);

  const value = useMemo<AuthState>(
    () => ({
      user,
      signIn: (email, password) => {
        const normalized = email.trim().toLowerCase();
        if (normalized === VALID_EMAIL && password === VALID_PASSWORD) {
          setUser(DEMO_USER);
          return { ok: true };
        }
        return { ok: false, error: 'Invalid email or password. Try prie@gmail.com / 123456' };
      },
      signOut: () => setUser(null),
    }),
    [user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
