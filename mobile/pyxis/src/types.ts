/** Domain types for the Pyxis prototype (mirrors the architecture data shapes). */

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
}

export interface DashboardStats {
  transactionsAnalyzed: number;
  openCases: number;
  criticalCases: number;
  pendingReviews: number;
  clearedToday: number;
  falsePositiveRate: number; // percentage
}
