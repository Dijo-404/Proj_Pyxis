/**
 * Lightweight state-based navigator with no external navigation dependency.
 * Gated by auth: unauthenticated -> Login, authenticated -> app stack.
 */

import React, { useState } from 'react';
import { ActivityIndicator, StatusBar, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
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
import { useWorkspace } from './workspace';

type Route =
  | { name: 'tab'; tab: 'dashboard' | 'risks' | 'profile' }
  | { name: 'queue' }
  | { name: 'case'; caseId: string }
  | { name: 'ask'; caseId: string }
  | { name: 'sandbox'; caseId: string };

type Tab = 'dashboard' | 'risks' | 'profile';

export default function RootNavigator() {
  const { user } = useAuth();
  const { data, loading, error, refresh } = useWorkspace();
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

  if (loading) {
    return (
      <View style={styles.stateView}>
        <ActivityIndicator color={colors.primary} size="large" />
        <Text style={styles.stateText}>Loading the local compliance workspace…</Text>
      </View>
    );
  }

  if (error || !data) {
    return (
      <View style={styles.stateView}>
        <Text style={styles.errorTitle}>Backend unavailable</Text>
        <Text style={styles.stateText}>{error ?? 'No workspace data was returned.'}</Text>
        <TouchableOpacity style={styles.retryButton} onPress={refresh}>
          <Text style={styles.retryText}>Retry</Text>
        </TouchableOpacity>
      </View>
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

const styles = StyleSheet.create({
  stateView: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 28,
    backgroundColor: colors.bg,
  },
  stateText: { marginTop: 14, color: colors.textMuted, textAlign: 'center' },
  errorTitle: { fontSize: 20, fontWeight: '700', color: colors.text },
  retryButton: {
    marginTop: 20,
    paddingHorizontal: 24,
    paddingVertical: 12,
    backgroundColor: colors.primary,
  },
  retryText: { color: colors.onPrimary, fontWeight: '700' },
});
