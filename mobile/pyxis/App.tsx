/**
 * Pyxis — Adaptive Financial Compliance & Risk Triage.
 * @format
 */

import React from 'react';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { AuthProvider } from './src/auth';
import RootNavigator from './src/RootNavigator';
import { WorkspaceProvider } from './src/workspace';

function App() {
  return (
    <SafeAreaProvider>
      <WorkspaceProvider>
        <AuthProvider>
          <RootNavigator />
        </AuthProvider>
      </WorkspaceProvider>
    </SafeAreaProvider>
  );
}

export default App;
