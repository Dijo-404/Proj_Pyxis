export type ViewKey = 'overview' | 'cases' | 'scenarios' | 'evidence' | 'reports';

export type RiskLevel = 'Critical' | 'High' | 'Medium' | 'Low';
export type CaseStatus =
  | 'Open'
  | 'Escalated'
  | 'In review'
  | 'Pending documents'
  | 'Cleared'
  | 'Suspicious'
  | 'Closed';
export type ScenarioCategory = 'Suspicious' | 'Legitimate' | 'Uncertain';
export type EvidenceState = 'Match' | 'Contradict' | 'Unknown' | 'Partial';

export interface RiskCase {
  id: string;
  customerId: string;
  customer: string;
  segment: string;
  trigger: string;
  amount: string;
  score: number;
  risk: RiskLevel;
  status: CaseStatus;
  updated: string;
  owner: string;
  location: string;
  anomalies: string[];
  anomalyScore: number;
  scenarios: Scenario[];
  evidenceRows: EvidenceRow[];
  evidenceItems: Array<{
    id: string;
    description: string;
    type: string;
    status: string;
    source: string;
  }>;
  criticalQuestion: {
    question: string;
    whyItMatters: string;
    recommendedAction: string;
  };
  counterfactual: Array<{ condition: string; from: number; to: number }>;
  recommendedActions: string[];
}

export interface Scenario {
  id: string;
  name: string;
  category: ScenarioCategory;
  score: number;
  summary: string;
  supporting: number;
  contradicting: number;
  missing: number;
  supportingItems: string[];
  contradictingItems: string[];
  missingItems: string[];
}

export interface EvidenceRow {
  signal: string;
  source: string;
  states: Record<string, EvidenceState>;
}

export interface Report {
  id: string;
  caseId: string;
  customer: string;
  type: string;
  generated: string;
  status: 'Ready' | 'Draft';
}

export interface DashboardData {
  transactionsAnalyzed: number;
  openCases: number;
  criticalCases: number;
  pendingReviews: number;
  clearedToday: number;
  falsePositiveRate: number;
  flaggedTrend: Array<{ label: string; value: number }>;
}

export interface Reviewer {
  id: string;
  name: string;
  email: string;
  role: string;
}

export interface WorkspacePayload {
  reviewer: Reviewer;
  dashboard: DashboardData;
  cases: RiskCase[];
  reports: Report[];
  model: string;
}
