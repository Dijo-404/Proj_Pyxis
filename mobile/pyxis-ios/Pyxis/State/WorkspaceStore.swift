import Foundation
import Combine

/// Observable workspace state, mirroring `mobile/pyxis/src/workspace.tsx`.
/// Loads the persistent compliance workspace from the backend and exposes
/// loading / error / data to the whole app.
@MainActor
final class WorkspaceStore: ObservableObject {
    @Published private(set) var data: WorkspacePayload?
    @Published private(set) var loading = true
    @Published private(set) var error: String?

    private let api: APIClient

    init(api: APIClient) {
        self.api = api
    }

    func refresh() async {
        loading = true
        error = nil
        do {
            data = try await api.loadWorkspace()
        } catch {
            self.error = (error as? PyxisError)?.errorDescription
                ?? "Unable to load workspace"
        }
        loading = false
    }

    /// Look up a case by id, used by the detail / ask / sandbox screens.
    func caseBy(id: String) -> RiskCase? {
        data?.cases.first { $0.id == id }
    }
}
