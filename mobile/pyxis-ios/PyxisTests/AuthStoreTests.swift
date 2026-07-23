import XCTest
@testable import Pyxis

@MainActor
final class AuthStoreTests: XCTestCase {
    private func makeStores() -> (WorkspaceStore, AuthStore) {
        let api = APIClient(baseURL: URL(string: "http://127.0.0.1:8000/api/v1"), session: StubURLProtocol.makeSession())
        let workspace = WorkspaceStore(api: api)
        let auth = AuthStore(workspace: workspace)
        return (workspace, auth)
    }

    func testRejectsInvalidEmail() {
        let (_, auth) = makeStores()
        let result = auth.signIn(email: "not-an-email", password: "secret123")
        XCTAssertFalse(result.ok)
        XCTAssertNil(auth.user)
    }

    func testRejectsShortPassword() {
        let (_, auth) = makeStores()
        let result = auth.signIn(email: "user@pyxis.local", password: "12345")
        XCTAssertFalse(result.ok)
        XCTAssertNil(auth.user)
    }

    func testSynthesizesLocalReviewerWhenNoMatch() {
        let (_, auth) = makeStores()
        let result = auth.signIn(email: "Casey.Jones@bank.test", password: "goodpassword")
        XCTAssertTrue(result.ok)
        XCTAssertEqual(auth.user?.id, "LOCAL-CASEY.JONES")
        XCTAssertEqual(auth.user?.name, "casey jones")
        XCTAssertEqual(auth.user?.role, "Compliance Reviewer")
    }

    func testUsesBackendReviewerWhenEmailMatches() async {
        let (workspace, auth) = makeStores()
        StubURLProtocol.responder = { _ in (200, Fixtures.bootstrapJSON.data(using: .utf8)!) }
        await workspace.refresh()

        let result = auth.signIn(email: "ada@pyxis.local", password: "goodpassword")
        XCTAssertTrue(result.ok)
        XCTAssertEqual(auth.user?.id, "REV-1")
        XCTAssertEqual(auth.user?.name, "Ada Reviewer")
    }

    func testSignOutClearsUser() {
        let (_, auth) = makeStores()
        _ = auth.signIn(email: "user@pyxis.local", password: "goodpassword")
        XCTAssertNotNil(auth.user)
        auth.signOut()
        XCTAssertNil(auth.user)
    }
}
