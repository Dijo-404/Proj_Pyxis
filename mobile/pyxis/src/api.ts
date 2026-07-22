import { Platform } from 'react-native';
import { DashboardStats, EvidenceStatus, RiskCase, Sandbox, User } from './types';

const API_HOST = Platform.OS === 'android' ? '10.0.2.2' : '127.0.0.1';
export const API_BASE_URL = `http://${API_HOST}:8000/api/v1`;

interface RawScenario {
  scenario_id: string;
  category: 'LEGITIMATE' | 'SUSPICIOUS' | 'UNCERTAIN';
  name: string;
  description: string | null;
  match_score: number;
}

interface RawCase {
  case_id: string;
  customer_id: string;
  customer_name: string;
  customer_type: string;
  business: string;
  trigger_transaction_id: string;
  trigger_summary: string;
  trigger_amount: string;
  risk_score: number;
  status: string;
  created_at: string;
  scenarios: RawScenario[];
  decision_critical_evidence: {
    question?: string;
    why_it_matters?: string;
    recommended_action?: string;
  } | null;
  recommended_actions: string[];
  workspace_data: {
    anomaly_score?: number;
    financial_twin?: RiskCase['twin'];
    investigation?: RiskCase['investigation'];
    scenario_evidence?: Record<string, {
      supporting: string[];
      contradicting: string[];
      unknown: string[];
    }>;
    evidence_matrix?: Array<{
      signal: string;
      byScenario: Record<string, EvidenceStatus>;
    }>;
    counterfactual?: RiskCase['counterfactual'];
    sandbox?: Sandbox;
  };
}

interface RawBootstrap {
  reviewer: {
    reviewer_id: string;
    name: string;
    email: string;
    role: string;
  };
  dashboard: {
    transactions_analyzed: number;
    open_cases: number;
    critical_cases: number;
    pending_reviews: number;
    cleared_today: number;
    false_positive_rate: number;
    flagged_trend: Array<{ label: string; value: number }>;
  };
  cases: RawCase[];
  model_runtime: {
    provider: string;
    model: string;
    local_only: boolean;
  };
}

export interface WorkspacePayload {
  reviewer: User;
  dashboard: DashboardStats;
  flaggedTrend: Array<{ label: string; value: number }>;
  cases: RiskCase[];
  modelRuntime: RawBootstrap['model_runtime'];
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...init?.headers },
  });
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    const message = body?.error?.message ?? `Request failed with HTTP ${response.status}`;
    throw new Error(message);
  }
  return response.json() as Promise<T>;
}

function mapStatus(status: string): RiskCase['status'] {
  if (status === 'UNDER_REVIEW' || status === 'AWAITING_EVIDENCE') return 'IN_REVIEW';
  if (status === 'CLOSED') return 'CLEARED';
  if (status === 'OPEN' || status === 'ESCALATED' || status === 'CLEARED' || status === 'SUSPICIOUS') {
    return status;
  }
  return 'OPEN';
}

function mapCase(raw: RawCase): RiskCase {
  const workspace = raw.workspace_data;
  const critical = raw.decision_critical_evidence ?? {};
  if (!workspace.sandbox) {
    throw new Error(`Case ${raw.case_id} is missing its persisted sandbox trace`);
  }
  return {
    id: raw.case_id,
    customerId: raw.customer_id,
    customerName: raw.customer_name,
    customerType: raw.customer_type,
    business: raw.business,
    triggerTransaction: raw.trigger_transaction_id,
    triggerSummary: `${raw.trigger_summary} · ${raw.trigger_amount}`,
    anomalyScore: workspace.anomaly_score ?? Math.round(raw.risk_score),
    currentRisk: Math.round(raw.risk_score),
    status: mapStatus(raw.status),
    createdAt: raw.created_at,
    twin: workspace.financial_twin ?? [],
    investigation: workspace.investigation ?? [],
    scenarios: raw.scenarios.map(scenario => {
      const evidence = workspace.scenario_evidence?.[scenario.scenario_id];
      return {
        id: scenario.scenario_id,
        category: scenario.category,
        name: scenario.name,
        description: scenario.description ?? 'No scenario description provided.',
        matchScore: Math.round(scenario.match_score),
        supporting: evidence?.supporting ?? [],
        contradicting: evidence?.contradicting ?? [],
        unknown: evidence?.unknown ?? [],
      };
    }),
    evidence: workspace.evidence_matrix ?? [],
    criticalQuestion: {
      question: critical.question ?? 'What additional evidence would resolve this case?',
      whyItMatters: critical.why_it_matters ?? 'The case remains unresolved.',
      recommendedAction: critical.recommended_action ?? 'Request additional verified evidence.',
    },
    counterfactual: workspace.counterfactual ?? [],
    saferWorkflow: raw.recommended_actions,
    sandbox: workspace.sandbox,
  };
}

export async function loadWorkspace(): Promise<WorkspacePayload> {
  const raw = await request<RawBootstrap>('/workspace/bootstrap');
  return {
    reviewer: {
      id: raw.reviewer.reviewer_id,
      name: raw.reviewer.name,
      email: raw.reviewer.email,
      role: raw.reviewer.role,
    },
    dashboard: {
      transactionsAnalyzed: raw.dashboard.transactions_analyzed,
      openCases: raw.dashboard.open_cases,
      criticalCases: raw.dashboard.critical_cases,
      pendingReviews: raw.dashboard.pending_reviews,
      clearedToday: raw.dashboard.cleared_today,
      falsePositiveRate: raw.dashboard.false_positive_rate,
    },
    flaggedTrend: raw.dashboard.flagged_trend.map(point => ({
      label: point.label,
      value: point.value,
    })),
    cases: raw.cases.map(mapCase),
    modelRuntime: raw.model_runtime,
  };
}

export async function askGemma(
  caseId: string,
  reviewerId: string,
  question: string,
): Promise<string> {
  const response = await request<{ answer: string }>(`/cases/${caseId}/ask-gemma`, {
    method: 'POST',
    body: JSON.stringify({ reviewer_id: reviewerId, question }),
  });
  return response.answer;
}

export type ReviewActionInput = 'CLEAR' | 'REQUEST_MORE_EVIDENCE' | 'ESCALATE' | 'MARK_SUSPICIOUS';

export async function submitReview(
  caseId: string,
  reviewerId: string,
  action: ReviewActionInput,
  reason: string,
): Promise<{ resultingStatus: string }> {
  const response = await request<{ resulting_status: string }>(`/cases/${caseId}/review`, {
    method: 'POST',
    body: JSON.stringify({ reviewer_id: reviewerId, action, reason }),
  });
  return { resultingStatus: response.resulting_status };
}

export async function generateReport(
  caseId: string,
  reviewerId: string,
): Promise<{ reportId: string; htmlPath: string }> {
  const response = await request<{ report_id: string; html_path: string }>(
    `/reports/${caseId}/generate`,
    {
      method: 'POST',
      body: JSON.stringify({ generated_by: reviewerId, include_pdf: false }),
    },
  );
  return { reportId: response.report_id, htmlPath: response.html_path };
}
