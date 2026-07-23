import Foundation

/// Raw wire shapes and the case-mapping logic, ported 1:1 from
/// `mobile/pyxis/src/api.ts`. The bootstrap envelope and case fields are
/// snake_case (hence explicit `CodingKeys`), while the nested
/// `workspace_data.sandbox` / financial-twin objects are camelCase and decode
/// by their exact Swift property names — so the JSONDecoder must NOT apply
/// `.convertFromSnakeCase` globally.

// MARK: - Raw bootstrap

struct RawReviewer: Decodable {
    let reviewer_id: String
    let name: String
    let email: String
    let role: String
}

struct RawTrendPoint: Decodable {
    let label: String
    let value: Int
}

struct RawDashboard: Decodable {
    let transactions_analyzed: Int
    let open_cases: Int
    let critical_cases: Int
    let pending_reviews: Int
    let cleared_today: Int
    let false_positive_rate: Double
    let flagged_trend: [RawTrendPoint]
}

struct RawModelRuntime: Decodable {
    let provider: String
    let model: String
    let local_only: Bool
}

struct RawScenario: Decodable {
    let scenario_id: String
    let category: ScenarioCategory
    let name: String
    let description: String?
    let match_score: Double
}

struct RawScenarioEvidence: Decodable {
    let supporting: [String]
    let contradicting: [String]
    let unknown: [String]
}

struct RawEvidenceMatrixRow: Decodable {
    let signal: String
    let byScenario: [String: EvidenceStatus]
}

struct RawDecisionCritical: Decodable {
    let question: String?
    let why_it_matters: String?
    let recommended_action: String?
}

struct RawWorkspaceData: Decodable {
    let anomaly_score: Int?
    let financial_twin: [TwinMetric]?
    let investigation: [InvestigationStep]?
    let scenario_evidence: [String: RawScenarioEvidence]?
    let evidence_matrix: [RawEvidenceMatrixRow]?
    let counterfactual: [CounterfactualStep]?
    let sandbox: Sandbox?
}

struct RawCase: Decodable {
    let case_id: String
    let customer_id: String
    let customer_name: String
    let customer_type: String
    let business: String
    let trigger_transaction_id: String
    let trigger_summary: String
    let trigger_amount: String
    let risk_score: Double
    let status: String
    let created_at: String
    let scenarios: [RawScenario]
    let decision_critical_evidence: RawDecisionCritical?
    let recommended_actions: [String]
    let workspace_data: RawWorkspaceData
}

struct RawBootstrap: Decodable {
    let reviewer: RawReviewer
    let dashboard: RawDashboard
    let cases: [RawCase]
    let model_runtime: RawModelRuntime
}

// MARK: - Mapping (ports mapStatus / mapCase / loadWorkspace)

enum WorkspaceMapper {
    static func mapStatus(_ status: String) -> CaseStatus {
        switch status {
        case "UNDER_REVIEW", "AWAITING_EVIDENCE": return .inReview
        case "CLOSED": return .cleared
        case "OPEN": return .open
        case "ESCALATED": return .escalated
        case "CLEARED": return .cleared
        case "SUSPICIOUS": return .suspicious
        default: return .open
        }
    }

    /// Ports `mapCase`. Throws when a case is missing its persisted sandbox
    /// trace, exactly like the RN client.
    static func mapCase(_ raw: RawCase) throws -> RiskCase {
        let workspace = raw.workspace_data
        guard let sandbox = workspace.sandbox else {
            throw PyxisError.message("Case \(raw.case_id) is missing its persisted sandbox trace")
        }
        let critical = raw.decision_critical_evidence
        let riskRounded = Int(raw.risk_score.rounded())

        let scenarios: [Scenario] = raw.scenarios.map { scenario in
            let evidence = workspace.scenario_evidence?[scenario.scenario_id]
            return Scenario(
                id: scenario.scenario_id,
                category: scenario.category,
                name: scenario.name,
                description: scenario.description ?? "No scenario description provided.",
                matchScore: Int(scenario.match_score.rounded()),
                supporting: evidence?.supporting ?? [],
                contradicting: evidence?.contradicting ?? [],
                unknown: evidence?.unknown ?? []
            )
        }

        let evidence: [EvidenceRow] = (workspace.evidence_matrix ?? []).map {
            EvidenceRow(signal: $0.signal, byScenario: $0.byScenario)
        }

        return RiskCase(
            id: raw.case_id,
            customerId: raw.customer_id,
            customerName: raw.customer_name,
            customerType: raw.customer_type,
            business: raw.business,
            triggerTransaction: raw.trigger_transaction_id,
            triggerSummary: "\(raw.trigger_summary) · \(raw.trigger_amount)",
            anomalyScore: workspace.anomaly_score ?? riskRounded,
            currentRisk: riskRounded,
            status: mapStatus(raw.status),
            createdAt: raw.created_at,
            twin: workspace.financial_twin ?? [],
            investigation: workspace.investigation ?? [],
            scenarios: scenarios,
            evidence: evidence,
            criticalQuestion: CriticalQuestion(
                question: critical?.question ?? "What additional evidence would resolve this case?",
                whyItMatters: critical?.why_it_matters ?? "The case remains unresolved.",
                recommendedAction: critical?.recommended_action ?? "Request additional verified evidence."
            ),
            counterfactual: workspace.counterfactual ?? [],
            saferWorkflow: raw.recommended_actions,
            sandbox: sandbox
        )
    }

    static func map(_ raw: RawBootstrap) throws -> WorkspacePayload {
        WorkspacePayload(
            reviewer: User(
                id: raw.reviewer.reviewer_id,
                name: raw.reviewer.name,
                email: raw.reviewer.email,
                role: raw.reviewer.role
            ),
            dashboard: DashboardStats(
                transactionsAnalyzed: raw.dashboard.transactions_analyzed,
                openCases: raw.dashboard.open_cases,
                criticalCases: raw.dashboard.critical_cases,
                pendingReviews: raw.dashboard.pending_reviews,
                clearedToday: raw.dashboard.cleared_today,
                falsePositiveRate: raw.dashboard.false_positive_rate
            ),
            flaggedTrend: raw.dashboard.flagged_trend.map { TrendPoint(label: $0.label, value: $0.value) },
            cases: try raw.cases.map(mapCase),
            modelRuntime: ModelRuntime(
                provider: raw.model_runtime.provider,
                model: raw.model_runtime.model,
                localOnly: raw.model_runtime.local_only
            )
        )
    }
}
