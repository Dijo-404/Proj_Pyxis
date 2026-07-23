import Foundation

/// Sandbox / AI Agent Playground types (`sandbox.md` — one isolated agent
/// simulation per customer). These decode directly from the camelCase
/// `workspace_data.sandbox` object persisted by the backend, matching the RN
/// `Sandbox` type exactly.

/// The stages of the isolated agent simulation flow (sandbox.md).
enum AgentStageKind: String, Codable {
    case contextBuilder = "CONTEXT_BUILDER"
    case orchestrator = "ORCHESTRATOR"
    case scenarioGenerator = "SCENARIO_GENERATOR"
    case deterministicTools = "DETERMINISTIC_TOOLS"
    case simulatorScorer = "SIMULATOR_SCORER"
    case evidenceCritic = "EVIDENCE_CRITIC"
    case decisionEvidence = "DECISION_EVIDENCE"
    case reportWriter = "REPORT_WRITER"
}

/// Who performed a stage — Gemma reasoning vs. deterministic local code.
enum Actor: String, Codable {
    case gemma = "GEMMA"
    case deterministic = "DETERMINISTIC"
}

/// A single deterministic tool invocation Gemma requested during a stage.
struct ToolCall: Codable, Equatable, Identifiable {
    var id: String { tool + args }
    let tool: String
    let args: String
    let result: String
}

/// One stage in the per-customer agent sandbox run.
struct AgentStage: Codable, Equatable, Identifiable {
    var id: String { kind.rawValue }
    let kind: AgentStageKind
    let title: String
    let actor: Actor
    let summary: String
    let input: String
    let output: String
    let toolCalls: [ToolCall]?
    let durationMs: Int
}

/// A raw deviation signal with the math and the reason it matters.
struct AnomalySignal: Codable, Equatable, Identifiable {
    var id: String { key }
    let key: String
    let label: String
    let metric: String
    let value: String
    let contribution: Int
    let why: String
    let fired: Bool
}

/// The anomaly-score computation, exposed so the run is auditable.
struct AnomalyBreakdown: Codable, Equatable {
    let score: Int
    let deviationLevel: String // Mild | Moderate | Severe
    let signals: [AnomalySignal]
    let matters: String
    let markedRisk: String
}

enum FlowNodeKind: String, Codable {
    case source = "SOURCE"
    case customer = "CUSTOMER"
    case beneficiary = "BENEFICIARY"
}

enum FlowVerified: String, Codable {
    case verified = "VERIFIED"
    case unknown = "UNKNOWN"
    case flagged = "FLAGGED"
}

/// A node in the money-flow graph (Follow the Money).
struct FlowNode: Codable, Equatable, Identifiable {
    let id: String
    let label: String
    let kind: FlowNodeKind
    let verified: FlowVerified?
    let amount: String?
}

struct FlowEdge: Codable, Equatable, Identifiable {
    var id: String { from + to }
    let from: String
    let to: String
    let amount: String
}

struct FlowGraph: Codable, Equatable {
    let nodes: [FlowNode]
    let edges: [FlowEdge]
}

enum TransactionDirection: String, Codable {
    case incoming = "IN"
    case outgoing = "OUT"
}

/// One transaction in a customer's activity history — risky or clean.
struct CustomerTransaction: Codable, Equatable, Identifiable {
    let id: String
    let label: String
    let amount: String
    let timestamp: String
    let direction: TransactionDirection
    let risky: Bool
    let riskScore: Int
    let reason: String
    let explanation: String
    let firedSignals: [String]
}

/// A node in the neural-network-style transaction branch graph.
struct BranchNode: Codable, Equatable, Identifiable {
    let id: String
    let transactionId: String
    let x: Double
    let y: Double
    let parents: [String]
}

/// The isolated sandbox simulation attached to one customer/case.
struct Sandbox: Codable, Equatable {
    let runId: String
    let model: String
    let runtime: String
    let boundaryHeld: Bool
    let seed: Int
    let totalDurationMs: Int
    let anomaly: AnomalyBreakdown
    let stages: [AgentStage]
    let flow: FlowGraph
    let transactions: [CustomerTransaction]
    let branches: [BranchNode]
}
