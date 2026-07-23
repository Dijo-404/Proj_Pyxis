import XCTest
@testable import Pyxis

final class WorkspaceMapperTests: XCTestCase {
    private func decodeBootstrap() throws -> RawBootstrap {
        let data = Fixtures.bootstrapJSON.data(using: .utf8)!
        return try JSONDecoder().decode(RawBootstrap.self, from: data)
    }

    func testMapsBootstrapEnvelope() throws {
        let payload = try WorkspaceMapper.map(decodeBootstrap())

        XCTAssertEqual(payload.reviewer.id, "REV-1")
        XCTAssertEqual(payload.reviewer.email, "ada@pyxis.local")
        XCTAssertEqual(payload.dashboard.transactionsAnalyzed, 1200)
        XCTAssertEqual(payload.dashboard.falsePositiveRate, 2.5, accuracy: 0.001)
        XCTAssertEqual(payload.flaggedTrend.map(\.label), ["Mon", "Tue"])
        XCTAssertEqual(payload.modelRuntime.model, "gemma3:4b")
        XCTAssertTrue(payload.modelRuntime.localOnly)
        XCTAssertEqual(payload.cases.count, 1)
    }

    func testMapsCaseFieldsAndRounding() throws {
        let payload = try WorkspaceMapper.map(decodeBootstrap())
        let c = payload.cases[0]

        XCTAssertEqual(c.id, "CASE-1")
        // triggerSummary concatenates summary and amount with a middot.
        XCTAssertEqual(c.triggerSummary, "Large outbound · ₹5,00,000")
        // currentRisk rounds risk_score; anomalyScore comes from workspace_data.
        XCTAssertEqual(c.currentRisk, 82)
        XCTAssertEqual(c.anomalyScore, 80)
        XCTAssertEqual(c.status, .open)

        // Scenario match score rounds, and per-scenario evidence is merged in.
        let s = c.scenarios[0]
        XCTAssertEqual(s.matchScore, 74)
        XCTAssertEqual(s.supporting, ["a"])
        XCTAssertEqual(s.unknown, ["b"])
        XCTAssertEqual(s.category, .suspicious)

        // Twin / evidence matrix / counterfactual come through.
        XCTAssertEqual(c.twin.first?.deviated, true)
        XCTAssertEqual(c.evidence.first?.byScenario["S1"], .match)
        XCTAssertEqual(c.counterfactual.first?.to, 30)
        XCTAssertEqual(c.criticalQuestion.question, "Q?")
        XCTAssertEqual(c.saferWorkflow, ["Step one", "Step two"])
        XCTAssertEqual(c.sandbox.runId, "RUN-1")
        XCTAssertTrue(c.sandbox.boundaryHeld)
    }

    func testStatusMapping() {
        XCTAssertEqual(WorkspaceMapper.mapStatus("UNDER_REVIEW"), .inReview)
        XCTAssertEqual(WorkspaceMapper.mapStatus("AWAITING_EVIDENCE"), .inReview)
        XCTAssertEqual(WorkspaceMapper.mapStatus("CLOSED"), .cleared)
        XCTAssertEqual(WorkspaceMapper.mapStatus("ESCALATED"), .escalated)
        XCTAssertEqual(WorkspaceMapper.mapStatus("SUSPICIOUS"), .suspicious)
        XCTAssertEqual(WorkspaceMapper.mapStatus("WHATEVER"), .open)
    }

    func testMissingSandboxThrows() throws {
        // A case whose workspace_data omits the sandbox trace must throw,
        // mirroring the RN client guard.
        let json = """
        {
          "case_id": "CASE-2", "customer_id": "CUST-2", "customer_name": "No Sandbox",
          "customer_type": "INDIVIDUAL", "business": "n/a",
          "trigger_transaction_id": "TXN-1", "trigger_summary": "s", "trigger_amount": "₹1",
          "risk_score": 10.0, "status": "OPEN", "created_at": "2026-01-01T00:00:00Z",
          "scenarios": [], "decision_critical_evidence": null, "recommended_actions": [],
          "workspace_data": {}
        }
        """
        let raw = try JSONDecoder().decode(RawCase.self, from: json.data(using: .utf8)!)
        XCTAssertThrowsError(try WorkspaceMapper.mapCase(raw))
    }
}
