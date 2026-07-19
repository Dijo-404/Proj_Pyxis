/** Domain types for Pyxis, mirroring the persisted API data shapes. */

export type ScenarioCategory = 'LEGITIMATE' | 'SUSPICIOUS' | 'UNCERTAIN';
export type EvidenceStatus = 'MATCH' | 'CONTRADICT' | 'UNKNOWN' | 'PARTIAL';
export type CaseStatus = 'OPEN' | 'IN_REVIEW' | 'ESCALATED' | 'CLEARED' | 'SUSPICIOUS';
export type ReviewAction =
  | 'CLEAR'
  | 'REQUEST_MORE_EVIDENCE'
  | 'ESCALATE'
  | 'MARK_SUSPICIOUS'
  | 'CLOSE';

export interface User {
  id: string;
  name: string;
  email: string;
  role: string;
}

export interface TwinMetric {
  label: string;
  normal: string;
  current: string;
  /** true when current activity deviates from the trusted baseline */
  deviated: boolean;
}

export interface Scenario {
  id: string;
  category: ScenarioCategory;
  name: string;
  description: string;
  matchScore: number; // 0-100
  supporting: string[];
  contradicting: string[];
  unknown: string[];
}

export interface EvidenceRow {
  signal: string;
  /** status keyed by scenario id */
  byScenario: Record<string, EvidenceStatus>;
}

export interface CounterfactualStep {
  condition: string;
  from: number;
  to: number;
}

export interface InvestigationStep {
  label: string;
  done: boolean;
  detail?: string;
}

export interface RiskCase {
  id: string;
  customerId: string;
  customerName: string;
  customerType: string;
  business: string;
  triggerTransaction: string;
  triggerSummary: string;
  anomalyScore: number;
  currentRisk: number;
  status: CaseStatus;
  createdAt: string;
  // detail payload
  twin: TwinMetric[];
  investigation: InvestigationStep[];
  scenarios: Scenario[];
  evidence: EvidenceRow[];
  criticalQuestion: {
    question: string;
    whyItMatters: string;
    recommendedAction: string;
  };
  counterfactual: CounterfactualStep[];
  saferWorkflow: string[];
  /** Per-customer isolated AI agent sandbox simulation. */
  sandbox: Sandbox;
}

export interface DashboardStats {
  transactionsAnalyzed: number;
  openCases: number;
  criticalCases: number;
  pendingReviews: number;
  clearedToday: number;
  falsePositiveRate: number; // percentage
}

/* ============================================================
 * Sandbox / AI Agent Playground types
 * (sandbox.md — one isolated agent simulation per customer)
 * ============================================================ */

/** The nine stages of the isolated agent simulation flow (sandbox.md). */
export type AgentStageKind =
  | 'CONTEXT_BUILDER'
  | 'ORCHESTRATOR'
  | 'SCENARIO_GENERATOR'
  | 'DETERMINISTIC_TOOLS'
  | 'SIMULATOR_SCORER'
  | 'EVIDENCE_CRITIC'
  | 'DECISION_EVIDENCE'
  | 'REPORT_WRITER';

/** Who performed a stage — Gemma reasoning vs. deterministic local code. */
export type Actor = 'GEMMA' | 'DETERMINISTIC';

/** A single deterministic tool invocation Gemma requested during a stage. */
export interface ToolCall {
  /** Registered local tool name, e.g. calculate_amount_deviation. */
  tool: string;
  args: string;
  /** Human-readable result the tool returned to the agent. */
  result: string;
}

/** One stage in the per-customer agent sandbox run. */
export interface AgentStage {
  kind: AgentStageKind;
  title: string;
  actor: Actor;
  /** One-line summary of what this stage did. */
  summary: string;
  /** What the stage received as input (compact evidence package view). */
  input: string;
  /** What the stage produced. */
  output: string;
  /** Deterministic tool calls requested during this stage (if any). */
  toolCalls?: ToolCall[];
  /** Simulated wall-clock cost, ms — expresses "how" the run executes. */
  durationMs: number;
}

/** A raw deviation signal with the math and the reason it matters. */
export interface AnomalySignal {
  key: string;
  label: string;
  /** e.g. "z-score", "percentile", "ratio". */
  metric: string;
  /** Computed value as a display string, e.g. "6.4σ". */
  value: string;
  /** 0-100 contribution of this signal to the anomaly score. */
  contribution: number;
  /** Deterministic explanation of WHY this signal fired. */
  why: string;
  fired: boolean;
}

/** The anomaly-score computation, exposed so the run is auditable. */
export interface AnomalyBreakdown {
  score: number; // 0-100 initial anomaly score
  deviationLevel: 'Mild' | 'Moderate' | 'Severe';
  signals: AnomalySignal[];
  /** Plain-language "why this transaction matters" headline. */
  matters: string;
  /** Plain-language "why it is marked as risk" headline. */
  markedRisk: string;
}

/** A node in the money-flow graph (Follow the Money). */
export interface FlowNode {
  id: string;
  label: string;
  kind: 'SOURCE' | 'CUSTOMER' | 'BENEFICIARY';
  /** Verification state for beneficiaries. */
  verified?: 'VERIFIED' | 'UNKNOWN' | 'FLAGGED';
  amount?: string;
}

/** One transaction in a customer's activity history — risky or clean. */
export interface CustomerTransaction {
  id: string;
  label: string;
  amount: string;
  timestamp: string;
  direction: 'IN' | 'OUT';
  /** Whether this transaction deviates from the customer's trusted twin. */
  risky: boolean;
  /** 0-100, only meaningful when risky. */
  riskScore: number;
  /** One-line reason shown on the node / list row. */
  reason: string;
  /** Full anomaly explanation shown in the detail popup. */
  explanation: string;
  /** Deterministic signals that fired for this transaction, if risky. */
  firedSignals: string[];
}

/** A node in the neural-network-style transaction branch graph. */
export interface BranchNode {
  id: string;
  transactionId: string;
  /** Normalized position within the graph canvas, 0-1. */
  x: number;
  y: number;
  /** Which upstream node(s) feed into this one. */
  parents: string[];
}

/** The isolated sandbox simulation attached to one customer/case. */
export interface Sandbox {
  /** Isolated run id — each customer gets their own sandbox (sandbox.md). */
  runId: string;
  /** Local model + runtime the simulation ran against. */
  model: string;
  runtime: string;
  /** Whether the simulation boundary held (all data synthetic + local). */
  boundaryHeld: boolean;
  seed: number;
  totalDurationMs: number;
  anomaly: AnomalyBreakdown;
  stages: AgentStage[];
  flow: {
    nodes: FlowNode[];
    /** edges as [fromId, toId, amount] */
    edges: { from: string; to: string; amount: string }[];
  };
  /** This customer's transaction history, feeding the risk/non-risk list. */
  transactions: CustomerTransaction[];
  /** Neural-network-style branch layout over `transactions`, for the playground graph. */
  branches: BranchNode[];
}
