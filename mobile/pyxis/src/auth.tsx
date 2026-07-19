/** Local session state. Reviewer identity comes from the backend workspace. */

import React, { createContext, useContext, useMemo, useState } from 'react';
import { User } from './types';
import { useWorkspace } from './workspace';

interface AuthState {
  user: User | null;
  signIn: (email: string, password: string) => { ok: boolean; error?: string };
  signOut: () => void;
}

const AuthContext = createContext<AuthState | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const { data } = useWorkspace();

  const value = useMemo<AuthState>(
    () => ({
      user,
      signIn: (email, password) => {
        const normalized = email.trim().toLowerCase();
        if (/^[^@]+@[^@]+\.[^@]+$/.test(normalized) && password.length >= 6) {
          const reviewer = data?.reviewer;
          setUser(
            reviewer && reviewer.email.toLowerCase() === normalized
              ? reviewer
              : {
                  id: `LOCAL-${normalized.split('@')[0].toUpperCase()}`,
                  name: normalized.split('@')[0].replace(/[._-]/g, ' '),
                  email: normalized,
                  role: 'Compliance Reviewer',
                },
          );
          return { ok: true };
        }
        return { ok: false, error: 'Enter a valid email and a password of at least six characters.' };
      },
      signOut: () => setUser(null),
    }),
    [data?.reviewer, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
