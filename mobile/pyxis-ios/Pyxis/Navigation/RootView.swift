import SwiftUI

/// Root navigator, mirroring `RootNavigator.tsx`: auth-gated (unauthenticated →
/// Login; authenticated → the app stack), with the workspace loading / error /
/// content states. Uses a single `NavigationStack` driven by the centralized
/// `Router`, so pushed screens (queue / case / ask / sandbox) present
/// full-screen without the floating tab bar — matching the RN flow.
struct RootView: View {
    @EnvironmentObject private var auth: AuthStore
    @EnvironmentObject private var workspace: WorkspaceStore
    @EnvironmentObject private var router: Router

    var body: some View {
        Group {
            if auth.user == nil {
                LoginScreen()
            } else {
                mainStack
            }
        }
        .task {
            if workspace.data == nil { await workspace.refresh() }
        }
    }

    private var mainStack: some View {
        NavigationStack(path: $router.path) {
            rootContent
                .navigationDestination(for: Route.self) { route in
                    switch route {
                    case .queue:
                        CaseQueueScreen()
                    case .caseDetail(let caseId):
                        CaseDetailScreen(caseId: caseId)
                    case .askGemma(let caseId):
                        AskGemmaScreen(caseId: caseId)
                    case .sandbox(let caseId):
                        SandboxScreen(caseId: caseId)
                    }
                }
        }
        .tint(PyxisColor.primary)
    }

    @ViewBuilder
    private var rootContent: some View {
        if workspace.data == nil && workspace.loading {
            LoadingView()
        } else if workspace.data == nil, let error = workspace.error {
            BackendErrorView(message: error) {
                Task { await workspace.refresh() }
            }
        } else {
            ZStack(alignment: .bottom) {
                Group {
                    switch router.selectedTab {
                    case .dashboard: DashboardScreen()
                    case .risks: CustomerRiskScreen()
                    case .profile: ProfileScreen()
                    }
                }
                BottomNav(active: router.selectedTab) { router.select($0) }
            }
        }
    }
}

/// Full-screen loading state, mirroring the RN loading view.
struct LoadingView: View {
    var body: some View {
        VStack(spacing: 14) {
            ProgressView().tint(PyxisColor.primary).controlSize(.large)
            Text("Loading the local compliance workspace…")
                .font(.system(size: FontSize.body))
                .foregroundColor(PyxisColor.textMuted)
                .multilineTextAlignment(.center)
        }
        .padding(28)
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(PyxisColor.bg)
        .toolbar(.hidden, for: .navigationBar)
    }
}

/// Full-screen backend-unavailable state with retry, mirroring the RN error view.
struct BackendErrorView: View {
    let message: String
    let retry: () -> Void

    var body: some View {
        VStack(spacing: 14) {
            Text("Backend unavailable")
                .font(.system(size: 20, weight: .bold))
                .foregroundColor(PyxisColor.text)
            Text(message)
                .font(.system(size: FontSize.body))
                .foregroundColor(PyxisColor.textMuted)
                .multilineTextAlignment(.center)
            Button(action: retry) {
                Text("Retry")
                    .font(.system(size: FontSize.body, weight: .bold))
                    .foregroundColor(PyxisColor.onPrimary)
                    .padding(.horizontal, 24)
                    .padding(.vertical, 12)
                    .background(PyxisColor.primary)
            }
            .buttonStyle(.plain)
            .padding(.top, 6)
        }
        .padding(28)
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(PyxisColor.bg)
        .toolbar(.hidden, for: .navigationBar)
    }
}
