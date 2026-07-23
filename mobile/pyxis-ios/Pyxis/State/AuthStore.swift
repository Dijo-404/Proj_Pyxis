import Foundation
import Combine

/// Local session state, mirroring `mobile/pyxis/src/auth.tsx`. The reviewer
/// identity comes from the backend workspace when the signed-in email matches;
/// otherwise a local reviewer identity is synthesized.
@MainActor
final class AuthStore: ObservableObject {
    @Published private(set) var user: User?

    private let workspace: WorkspaceStore

    init(workspace: WorkspaceStore) {
        self.workspace = workspace
    }

    struct SignInResult {
        let ok: Bool
        let error: String?
    }

    func signIn(email: String, password: String) -> SignInResult {
        let normalized = email.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        guard Self.isValidEmail(normalized), password.count >= 6 else {
            return SignInResult(
                ok: false,
                error: "Enter a valid email and a password of at least six characters."
            )
        }

        if let reviewer = workspace.data?.reviewer,
           reviewer.email.lowercased() == normalized {
            user = reviewer
        } else {
            let handle = normalized.split(separator: "@").first.map(String.init) ?? normalized
            let displayName = handle
                .replacingOccurrences(of: ".", with: " ")
                .replacingOccurrences(of: "_", with: " ")
                .replacingOccurrences(of: "-", with: " ")
            user = User(
                id: "LOCAL-\(handle.uppercased())",
                name: displayName,
                email: normalized,
                role: "Compliance Reviewer"
            )
        }
        return SignInResult(ok: true, error: nil)
    }

    func signOut() {
        user = nil
    }

    /// Ports the RN regex `/^[^@]+@[^@]+\.[^@]+$/`.
    private static func isValidEmail(_ value: String) -> Bool {
        let pattern = "^[^@]+@[^@]+\\.[^@]+$"
        return value.range(of: pattern, options: .regularExpression) != nil
    }
}
