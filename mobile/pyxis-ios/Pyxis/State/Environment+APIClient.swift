import SwiftUI

/// Lightweight dependency injection: the shared `APIClient` is threaded through
/// the SwiftUI environment (manual init injection, no heavy DI framework —
/// matching the RN app which had no DI container).
private struct APIClientKey: EnvironmentKey {
    static let defaultValue = APIClient()
}

extension EnvironmentValues {
    var apiClient: APIClient {
        get { self[APIClientKey.self] }
        set { self[APIClientKey.self] = newValue }
    }
}
