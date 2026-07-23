import SwiftUI

/// Centralized router / coordinator mirroring the RN `RootNavigator` graph 1:1:
///
/// - Three tabs: dashboard / risks / profile.
/// - A per-tab `NavigationStack` that pushes the queue, case detail, ask-gemma
///   and sandbox routes (same screen names, same flow order).
///
/// Back-button handling in the RN app translates to native swipe-back / the
/// navigation bar back button provided by `NavigationStack`.

enum AppTab: String, CaseIterable, Hashable {
    case dashboard
    case risks
    case profile

    var sfSymbol: String {
        switch self {
        case .dashboard: return "house.fill"
        case .risks: return "chart.bar.fill"
        case .profile: return "person.fill"
        }
    }
}

enum Route: Hashable {
    case queue
    case caseDetail(caseId: String)
    case askGemma(caseId: String)
    case sandbox(caseId: String)
}

@MainActor
final class Router: ObservableObject {
    @Published var selectedTab: AppTab = .dashboard
    @Published var path = NavigationPath()

    func push(_ route: Route) {
        path.append(route)
    }

    func pop() {
        if !path.isEmpty { path.removeLast() }
    }

    func popToRoot() {
        path = NavigationPath()
    }

    /// Switching tabs resets the pushed stack, matching the RN `switchTab`.
    func select(_ tab: AppTab) {
        selectedTab = tab
        popToRoot()
    }
}
