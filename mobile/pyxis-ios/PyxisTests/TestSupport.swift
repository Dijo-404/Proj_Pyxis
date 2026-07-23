import Foundation
@testable import Pyxis

/// A `URLProtocol` stub that returns canned responses, so `APIClient` /
/// `WorkspaceStore` can be exercised without a live backend.
final class StubURLProtocol: URLProtocol {
    /// (statusCode, body) keyed by URL path suffix.
    nonisolated(unsafe) static var responder: ((URL) -> (Int, Data))?

    override class func canInit(with request: URLRequest) -> Bool { true }
    override class func canonicalRequest(for request: URLRequest) -> URLRequest { request }

    override func startLoading() {
        guard let url = request.url, let responder = StubURLProtocol.responder else {
            client?.urlProtocol(self, didFailWithError: URLError(.badURL))
            return
        }
        let (status, data) = responder(url)
        let response = HTTPURLResponse(url: url, statusCode: status, httpVersion: nil, headerFields: ["Content-Type": "application/json"])!
        client?.urlProtocol(self, didReceive: response, cacheStoragePolicy: .notAllowed)
        client?.urlProtocol(self, didLoad: data)
        client?.urlProtocolDidFinishLoading(self)
    }

    override func stopLoading() {}

    /// A URLSession wired to this stub.
    static func makeSession() -> URLSession {
        let config = URLSessionConfiguration.ephemeral
        config.protocolClasses = [StubURLProtocol.self]
        return URLSession(configuration: config)
    }
}

enum Fixtures {
    /// A minimal-but-complete bootstrap payload with one case carrying a full
    /// (empty-collection) sandbox trace.
    static let bootstrapJSON = """
    {
      "reviewer": { "reviewer_id": "REV-1", "name": "Ada Reviewer", "email": "ada@pyxis.local", "role": "Compliance Reviewer" },
      "dashboard": {
        "transactions_analyzed": 1200, "open_cases": 3, "critical_cases": 1,
        "pending_reviews": 2, "cleared_today": 4, "false_positive_rate": 2.5,
        "flagged_trend": [ { "label": "Mon", "value": 3 }, { "label": "Tue", "value": 5 } ]
      },
      "cases": [ \(caseJSON) ],
      "model_runtime": { "provider": "ollama", "model": "gemma3:4b", "base_url": "http://127.0.0.1:11434", "local_only": true }
    }
    """

    static let caseJSON = """
    {
      "case_id": "CASE-1", "customer_id": "CUST-1", "customer_name": "Acme Corp",
      "customer_type": "BUSINESS", "business": "Imports",
      "trigger_transaction_id": "TXN-9", "trigger_summary": "Large outbound", "trigger_amount": "₹5,00,000",
      "risk_score": 82.4, "status": "OPEN", "created_at": "2026-01-01T00:00:00Z",
      "scenarios": [ { "scenario_id": "S1", "category": "SUSPICIOUS", "name": "Layering pattern", "description": "desc", "match_score": 73.6 } ],
      "decision_critical_evidence": { "question": "Q?", "why_it_matters": "because", "recommended_action": "do x" },
      "recommended_actions": [ "Step one", "Step two" ],
      "workspace_data": {
        "anomaly_score": 80,
        "financial_twin": [ { "label": "Avg txn", "normal": "10,000", "current": "5,00,000", "deviated": true } ],
        "investigation": [ { "label": "Collected evidence", "done": true } ],
        "scenario_evidence": { "S1": { "supporting": ["a"], "contradicting": [], "unknown": ["b"] } },
        "evidence_matrix": [ { "signal": "Amount deviation", "byScenario": { "S1": "MATCH" } } ],
        "counterfactual": [ { "condition": "If verified", "from": 80, "to": 30 } ],
        "sandbox": {
          "runId": "RUN-1", "model": "gemma3:4b", "runtime": "ollama", "boundaryHeld": true,
          "seed": 42, "totalDurationMs": 1234,
          "anomaly": { "score": 80, "deviationLevel": "Severe", "signals": [], "matters": "x", "markedRisk": "y" },
          "stages": [], "flow": { "nodes": [], "edges": [] }, "transactions": [], "branches": []
        }
      }
    }
    """
}
