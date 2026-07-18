/**
 * Lightweight state-based navigator for the prototype (no navigation deps).
 * Gated by auth: unauthenticated -> Login, authenticated -> app stack.
 */

import React, { useState } from 'react';
import { StatusBar } from 'react-native';
import { useAuth } from './auth';
import AskGemmaScreen from './screens/AskGemmaScreen';
import CaseDetailScreen from './screens/CaseDetailScreen';
import CaseQueueScreen from './screens/CaseQueueScreen';
import DashboardScreen from './screens/DashboardScreen';
import LoginScreen from './screens/LoginScreen';
import { colors } from './theme';

type Route =
  | { name: 'dashboard' }
  | { name: 'queue' }
  | { name: 'case'; caseId: string }
  | { name: 'ask'; caseId: string };

export default function RootNavigator() {
  const { user } = useAuth();
  const [stack, setStack] = useState<Route[]>([{ name: 'dashboard' }]);

  const push = (r: Route) => setStack(s => [...s, r]);
  const pop = () => setStack(s => (s.length > 1 ? s.slice(0, -1) : s));

  if (!user) {
    return (
      <>
        <StatusBar barStyle="light-content" backgroundColor={colors.primary} />
        <LoginScreen />
      </>
    );
  }

  const route = stack[stack.length - 1];

  return (
    <>
      <StatusBar barStyle="dark-content" backgroundColor={colors.bg} />
      {route.name === 'dashboard' && (
        <DashboardScreen
          onOpenCase={id => push({ name: 'case', caseId: id })}
          onOpenQueue={() => push({ name: 'queue' })}
        />
      )}
      {route.name === 'queue' && (
        <CaseQueueScreen
          onBack={pop}
          onOpenCase={id => push({ name: 'case', caseId: id })}
        />
      )}
      {route.name === 'case' && (
        <CaseDetailScreen
          caseId={route.caseId}
          onBack={pop}
          onAskGemma={id => push({ name: 'ask', caseId: id })}
        />
      )}
      {route.name === 'ask' && <AskGemmaScreen caseId={route.caseId} onBack={pop} />}
    </>
  );
}
