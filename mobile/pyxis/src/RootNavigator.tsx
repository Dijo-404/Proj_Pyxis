/**
 * Lightweight state-based navigator for the prototype (no navigation deps).
 * Gated by auth: unauthenticated -> Login, authenticated -> app stack.
 */

import React, { useState } from 'react';
import { StatusBar, View } from 'react-native';
import { useAuth } from './auth';
import AskGemmaScreen from './screens/AskGemmaScreen';
import CaseDetailScreen from './screens/CaseDetailScreen';
import CaseQueueScreen from './screens/CaseQueueScreen';
import DashboardScreen from './screens/DashboardScreen';
import LoginScreen from './screens/LoginScreen';
import SandboxScreen from './screens/SandboxScreen';
import CustomerRiskScreen from './screens/CustomerRiskScreen';
import ProfileScreen from './screens/ProfileScreen';
import BottomNav from './components/BottomNav';
import { colors } from './theme';

type Route =
  | { name: 'tab'; tab: 'dashboard' | 'risks' | 'profile' }
  | { name: 'queue' }
  | { name: 'case'; caseId: string }
  | { name: 'ask'; caseId: string }
  | { name: 'sandbox'; caseId: string };

type Tab = 'dashboard' | 'risks' | 'profile';

export default function RootNavigator() {
  const { user } = useAuth();
  const [stack, setStack] = useState<Route[]>([{ name: 'tab', tab: 'dashboard' }]);
  const [activeTab, setActiveTab] = useState<Tab>('dashboard');

  const push = (r: Route) => setStack(s => [...s, r]);
  const pop = () => setStack(s => (s.length > 1 ? s.slice(0, -1) : s));
  const switchTab = (tab: Tab) => {
    setActiveTab(tab);
    setStack([{ name: 'tab', tab }]);
  };

  if (!user) {
    return (
      <>
        <StatusBar barStyle="light-content" backgroundColor={colors.primary} />
        <LoginScreen />
      </>
    );
  }

  const route = stack[stack.length - 1];
  const isTabView = route.name === 'tab';

  return (
    <>
      <StatusBar barStyle="dark-content" backgroundColor={colors.bg} />
      <View style={{ flex: 1 }}>
        {isTabView ? (
          <>
            {activeTab === 'dashboard' && (
              <DashboardScreen
                onOpenCase={id => push({ name: 'case', caseId: id })}
                onOpenQueue={() => push({ name: 'queue' })}
              />
            )}
            {activeTab === 'risks' && (
              <CustomerRiskScreen
                onOpenCase={id => push({ name: 'case', caseId: id })}
              />
            )}
            {activeTab === 'profile' && <ProfileScreen />}
            <BottomNav active={activeTab} onPress={switchTab} />
          </>
        ) : (
          <>
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
                onOpenSandbox={id => push({ name: 'sandbox', caseId: id })}
              />
            )}
            {route.name === 'ask' && <AskGemmaScreen caseId={route.caseId} onBack={pop} />}
            {route.name === 'sandbox' && <SandboxScreen caseId={route.caseId} onBack={pop} />}
          </>
        )}
      </View>
    </>
  );
}
