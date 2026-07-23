import Foundation

/// Domain types for Pyxis, mirroring `mobile/pyxis/src/types.ts` and the
/// persisted API data shapes. These are the presentation-facing models the
/// view models expose; the raw wire shapes live in `Networking/WorkspaceDTO`.

enum ScenarioCategory: String, Codable {
    case legitimate = "LEGITIMATE"
    case suspicious = "SUSPICIOUS"
    case uncertain = "UNCERTAIN"
}

enum EvidenceStatus: String, Codable {
    case match = "MATCH"
    case contradict = "CONTRADICT"
    case unknown = "UNKNOWN"
    case partial = "PARTIAL"
}

enum CaseStatus: String, Codable {
    case open = "OPEN"
    case inReview = "IN_REVIEW"
    case escalated = "ESCALATED"
    case cleared = "CLEARED"
    case suspicious = "SUSPICIOUS"
}

/// Reviewer actions. `CLOSE` exists in the contract but is not a selectable
/// decision in the UI, matching the RN app.
enum ReviewAction: String, Codable {
    case clear = "CLEAR"
    case requestMoreEvidence = "REQUEST_MORE_EVIDENCE"
    case escalate = "ESCALATE"
    case markSuspicious = "MARK_SUSPICIOUS"
    case close = "CLOSE"
}

struct User: Identifiable, Equatable {
    let id: String
    let name: String
    let email: String
    let role: String
}

struct TwinMetric: Identifiable, Codable, Equatable {
    var id: String { label }
    let label: String
    let normal: String
    let current: String
    /// true when current activity deviates from the trusted baseline
    let deviated: Bool
}

struct Scenario: Identifiable, Equatable {
    let id: String
    let category: ScenarioCategory
    let name: String
    let description: String
    let matchScore: Int // 0-100
    let supporting: [String]
    let contradicting: [String]
    let unknown: [String]
}

struct EvidenceRow: Identifiable, Equatable {
    var id: String { signal }
    let signal: String
    /// status keyed by scenario id
    let byScenario: [String: EvidenceStatus]
}

struct CounterfactualStep: Identifiable, Codable, Equatable {
    var id: String { condition }
    let condition: String
    let from: Int
    let to: Int
}

struct InvestigationStep: Identifiable, Codable, Equatable {
    var id: String { label }
    let label: String
    let done: Bool
    let detail: String?
}

struct CriticalQuestion: Equatable {
    let question: String
    let whyItMatters: String
    let recommendedAction: String
}

struct RiskCase: Identifiable, Equatable {
    let id: String
    let customerId: String
    let customerName: String
    let customerType: String
    let business: String
    let triggerTransaction: String
    let triggerSummary: String
    let anomalyScore: Int
    let currentRisk: Int
    let status: CaseStatus
    let createdAt: String
    // detail payload
    let twin: [TwinMetric]
    let investigation: [InvestigationStep]
    let scenarios: [Scenario]
    let evidence: [EvidenceRow]
    let criticalQuestion: CriticalQuestion
    let counterfactual: [CounterfactualStep]
    let saferWorkflow: [String]
    /// Per-customer isolated AI agent sandbox simulation.
    let sandbox: Sandbox
}

struct DashboardStats: Equatable {
    let transactionsAnalyzed: Int
    let openCases: Int
    let criticalCases: Int
    let pendingReviews: Int
    let clearedToday: Int
    let falsePositiveRate: Double // percentage
}

struct TrendPoint: Identifiable, Equatable {
    var id: String { label }
    let label: String
    let value: Int
}

struct ModelRuntime: Equatable {
    let provider: String
    let model: String
    let localOnly: Bool
}

/// The fully-mapped workspace payload, mirroring `WorkspacePayload` in api.ts.
struct WorkspacePayload: Equatable {
    let reviewer: User
    let dashboard: DashboardStats
    let flaggedTrend: [TrendPoint]
    let cases: [RiskCase]
    let modelRuntime: ModelRuntime
}
