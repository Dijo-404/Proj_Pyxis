import Foundation

/// Human-readable error surfaced to the UI, mirroring the RN client which
/// throws `Error(body.error.message)`.
enum PyxisError: LocalizedError {
    case message(String)

    var errorDescription: String? {
        switch self {
        case .message(let text): return text
        }
    }
}

/// Backend error envelope: `{ "error": { "message": "..." } }`.
private struct APIErrorEnvelope: Decodable {
    struct Inner: Decodable { let message: String? }
    let error: Inner?
}

/// Networking layer for Pyxis — `URLSession` + async/await, matching the REST
/// endpoints, base URL and request/response shapes of `mobile/pyxis/src/api.ts`.
///
/// The iOS Simulator reaches the local FastAPI backend at `127.0.0.1:8000`
/// (the Android emulator used `10.0.2.2`). The base URL can be overridden via
/// the `PYXIS_API_BASE_URL` environment / Info.plist value for device testing.
struct APIClient {
    let baseURL: URL
    let session: URLSession

    static let defaultBaseURLString = "http://127.0.0.1:8000/api/v1"

    init(baseURL: URL? = nil, session: URLSession = .shared) {
        self.baseURL = baseURL ?? APIClient.resolveBaseURL()
        self.session = session
    }

    private static func resolveBaseURL() -> URL {
        if let override = Bundle.main.object(forInfoDictionaryKey: "PyxisAPIBaseURL") as? String,
           !override.isEmpty,
           let url = URL(string: override) {
            return url
        }
        if let env = ProcessInfo.processInfo.environment["PYXIS_API_BASE_URL"],
           let url = URL(string: env) {
            return url
        }
        return URL(string: defaultBaseURLString)!
    }

    private var jsonDecoder: JSONDecoder {
        // No global snake_case conversion: bootstrap/case fields carry explicit
        // snake_case CodingKeys, while the sandbox trace is camelCase.
        JSONDecoder()
    }

    // MARK: - Core request

    private func request<T: Decodable>(
        _ path: String,
        method: String = "GET",
        body: Data? = nil
    ) async throws -> T {
        guard let url = URL(string: baseURL.absoluteString + path) else {
            throw PyxisError.message("Invalid request path")
        }
        var req = URLRequest(url: url)
        req.httpMethod = method
        req.setValue("application/json", forHTTPHeaderField: "Content-Type")
        req.httpBody = body

        let data: Data
        let response: URLResponse
        do {
            (data, response) = try await session.data(for: req)
        } catch {
            throw PyxisError.message(error.localizedDescription)
        }

        guard let http = response as? HTTPURLResponse else {
            throw PyxisError.message("No HTTP response from the backend")
        }
        guard (200..<300).contains(http.statusCode) else {
            let envelope = try? JSONDecoder().decode(APIErrorEnvelope.self, from: data)
            let message = envelope?.error?.message ?? "Request failed with HTTP \(http.statusCode)"
            throw PyxisError.message(message)
        }

        do {
            return try jsonDecoder.decode(T.self, from: data)
        } catch {
            throw PyxisError.message("Unexpected response from the backend")
        }
    }

    // MARK: - Endpoints

    /// GET /workspace/bootstrap
    func loadWorkspace() async throws -> WorkspacePayload {
        let raw: RawBootstrap = try await request("/workspace/bootstrap")
        return try WorkspaceMapper.map(raw)
    }

    /// POST /cases/{caseId}/ask-gemma
    func askGemma(caseId: String, reviewerId: String, question: String) async throws -> String {
        struct Body: Encodable { let reviewer_id: String; let question: String }
        struct Answer: Decodable { let answer: String }
        let body = try JSONEncoder().encode(Body(reviewer_id: reviewerId, question: question))
        let response: Answer = try await request("/cases/\(caseId)/ask-gemma", method: "POST", body: body)
        return response.answer
    }

    /// POST /cases/{caseId}/review
    func submitReview(
        caseId: String,
        reviewerId: String,
        action: ReviewAction,
        reason: String
    ) async throws -> String {
        struct Body: Encodable { let reviewer_id: String; let action: String; let reason: String }
        struct Result: Decodable { let resulting_status: String }
        let body = try JSONEncoder().encode(
            Body(reviewer_id: reviewerId, action: action.rawValue, reason: reason)
        )
        let response: Result = try await request("/cases/\(caseId)/review", method: "POST", body: body)
        return response.resulting_status
    }

    /// POST /reports/{caseId}/generate
    func generateReport(caseId: String, reviewerId: String) async throws -> (reportId: String, htmlPath: String) {
        struct Body: Encodable { let generated_by: String; let include_pdf: Bool }
        struct Result: Decodable { let report_id: String; let html_path: String }
        let body = try JSONEncoder().encode(Body(generated_by: reviewerId, include_pdf: false))
        let response: Result = try await request("/reports/\(caseId)/generate", method: "POST", body: body)
        return (response.report_id, response.html_path)
    }
}
