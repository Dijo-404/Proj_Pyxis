import SwiftUI

/// App entry point. Builds the lightweight dependency graph (manual init
/// injection, mirroring the RN app's provider composition) and injects the
/// shared stores + API client into the SwiftUI environment.
@main
struct PyxisApp: App {
    @StateObject private var workspace: WorkspaceStore
    @StateObject private var auth: AuthStore
    @StateObject private var router = Router()
    private let api: APIClient

    init() {
        let client = APIClient()
        let workspaceStore = WorkspaceStore(api: client)
        _workspace = StateObject(wrappedValue: workspaceStore)
        _auth = StateObject(wrappedValue: AuthStore(workspace: workspaceStore))
        api = client
    }

    var body: some Scene {
        WindowGroup {
            RootView()
                .environmentObject(workspace)
                .environmentObject(auth)
                .environmentObject(router)
                .environment(\.apiClient, api)
        }
    }
}
