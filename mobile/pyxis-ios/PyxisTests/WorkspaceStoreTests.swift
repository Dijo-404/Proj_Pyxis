import XCTest
@testable import Pyxis

@MainActor
final class WorkspaceStoreTests: XCTestCase {
    private func makeStore() -> WorkspaceStore {
        let api = APIClient(baseURL: URL(string: "http://127.0.0.1:8000/api/v1"), session: StubURLProtocol.makeSession())
        return WorkspaceStore(api: api)
    }

    func testRefreshLoadsWorkspace() async {
        StubURLProtocol.responder = { _ in (200, Fixtures.bootstrapJSON.data(using: .utf8)!) }
        let store = makeStore()
        await store.refresh()
        XCTAssertFalse(store.loading)
        XCTAssertNil(store.error)
        XCTAssertEqual(store.data?.cases.count, 1)
        XCTAssertNotNil(store.caseBy(id: "CASE-1"))
    }

    func testRefreshSurfacesBackendError() async {
        StubURLProtocol.responder = { _ in
            (503, #"{"error":{"message":"Backend down"}}"#.data(using: .utf8)!)
        }
        let store = makeStore()
        await store.refresh()
        XCTAssertNil(store.data)
        XCTAssertEqual(store.error, "Backend down")
    }
}
