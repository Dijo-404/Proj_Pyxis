import type {
  DashboardData,
  EvidenceRow,
  EvidenceState,
  Report,
  Reviewer,
  RiskCase,
  RiskLevel,
  Scenario,
  WorkspacePayload,
} from './types';

const API_BASE_URL = '/api/v1';

interface RawCase {
  case_id: string;
  customer_id: string;
  customer_name: string;
  customer_type: string;
  business: string;
  trigger_transaction_id: string;
  trigger_summary: string;
  trigger_amount: string;
  assigned_to: string;
  location: string;
  risk_score: number;
  risk_level: string;
  status: string;
  anomalies: string[];
  created_at: string;
  updated_at: string;
  recommended_actions: string[];
  decision_critical_evidence: {
    question?: string;
    why_it_matters?: string;
    recommended_action?: string;
  } | null;
  scenarios: Array<{
    scenario_id: string;
    name: string;
    category: string;
    match_score: number;
    description: string | null;
  }>;
  evidence: Array<{
    evidence_id: string;
    description: string;
    evidence_type: string;
    status: string;
    source_reference: string;
  }>;
  workspace_data: {
    anomaly_score?: number;
    scenario_evidence?: Record<string, {
      supporting: string[];
      contradicting: string[];
      unknown: string[];
    }>;
    evidence_matrix?: Array<{
      signal: string;
      source: string;
      byScenario: Record<string, string>;
    }>;
    counterfactual?: Array<{ condition: string; from: number; to: number }>;
  };
}

interface RawReport {
  report_id: string;
  case_id: string;
  status: string;
  created_at: string;
  generated_by: string;
}

interface RawBootstrap {
  reviewer: { reviewer_id: string; name: string; email: string; role: string };
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
  reports: RawReport[];
  model_runtime: { model: string };
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...init?.headers },
  });
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.error?.message ?? `Request failed with HTTP ${response.status}`);
  }
  return response.json() as Promise<T>;
}

function riskLevel(value: string): RiskLevel {
  const formatted = value.charAt(0) + value.slice(1).toLowerCase();
  return (['Critical', 'High', 'Medium', 'Low'].includes(formatted) ? formatted : 'Medium') as RiskLevel;
}

function caseStatus(value: string): RiskCase['status'] {
  const statuses: Record<string, RiskCase['status']> = {
    OPEN: 'Open',
    ESCALATED: 'Escalated',
    UNDER_REVIEW: 'In review',
    AWAITING_EVIDENCE: 'Pending documents',
    CLEARED: 'Cleared',
    SUSPICIOUS: 'Suspicious',
    CLOSED: 'Closed',
  };
  return statuses[value] ?? 'Open';
}

function evidenceState(value: string): EvidenceState {
  const states: Record<string, EvidenceState> = {
    MATCH: 'Match',
    CONTRADICT: 'Contradict',
    UNKNOWN: 'Unknown',
    PARTIAL: 'Partial',
  };
  return states[value] ?? 'Unknown';
}

function mapCase(raw: RawCase): RiskCase {
  const scenarioEvidence = raw.workspace_data.scenario_evidence ?? {};
  const scenarios: Scenario[] = raw.scenarios.map(item => {
    const evidence = scenarioEvidence[item.scenario_id] ?? {
      supporting: [],
      contradicting: [],
      unknown: [],
    };
    return {
      id: item.scenario_id,
      name: item.name,
      category: item.category === 'SUSPICIOUS'
        ? 'Suspicious'
        : item.category === 'LEGITIMATE'
          ? 'Legitimate'
          : 'Uncertain',
      score: Math.round(item.match_score),
      summary: item.description ?? 'No scenario description provided.',
      supporting: evidence.supporting.length,
      contradicting: evidence.contradicting.length,
      missing: evidence.unknown.length,
      supportingItems: evidence.supporting,
      contradictingItems: evidence.contradicting,
      missingItems: evidence.unknown,
    };
  });
  const evidenceRows: EvidenceRow[] = (raw.workspace_data.evidence_matrix ?? []).map(row => ({
    signal: row.signal,
    source: row.source,
    states: Object.fromEntries(
      Object.entries(row.byScenario).map(([scenarioId, state]) => [scenarioId, evidenceState(state)]),
    ),
  }));
  const critical = raw.decision_critical_evidence ?? {};
  return {
    id: raw.case_id,
    customerId: raw.customer_id,
    customer: raw.customer_name,
    segment: `${raw.customer_type} · ${raw.business}`,
    trigger: raw.trigger_summary,
    amount: raw.trigger_amount,
    score: Math.round(raw.risk_score),
    risk: riskLevel(raw.risk_level),
    status: caseStatus(raw.status),
    updated: new Intl.DateTimeFormat('en-IN', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(raw.updated_at)),
    owner: raw.assigned_to,
    location: raw.location,
    anomalies: raw.anomalies,
    anomalyScore: raw.workspace_data.anomaly_score ?? Math.round(raw.risk_score),
    scenarios,
    evidenceRows,
    evidenceItems: raw.evidence.map(item => ({
      id: item.evidence_id,
      description: item.description,
      type: item.evidence_type,
      status: item.status,
      source: item.source_reference,
    })),
    criticalQuestion: {
      question: critical.question ?? 'What additional evidence would resolve this case?',
      whyItMatters: critical.why_it_matters ?? 'The investigation remains unresolved.',
      recommendedAction: critical.recommended_action ?? 'Request verified supporting evidence.',
    },
    counterfactual: raw.workspace_data.counterfactual ?? [],
    recommendedActions: raw.recommended_actions,
  };
}

function mapReport(raw: RawReport, cases: RiskCase[]): Report {
  const relatedCase = cases.find(item => item.id === raw.case_id);
  return {
    id: raw.report_id,
    caseId: raw.case_id,
    customer: relatedCase?.customer ?? raw.case_id,
    type: 'Compliance review',
    generated: new Intl.DateTimeFormat('en-IN', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(raw.created_at)),
    status: raw.status === 'GENERATED' ? 'Ready' : 'Draft',
  };
}

export async function loadWorkspace(): Promise<WorkspacePayload> {
  const raw = await request<RawBootstrap>('/workspace/bootstrap');
  const cases = raw.cases.map(mapCase);
  const reviewer: Reviewer = {
    id: raw.reviewer.reviewer_id,
    name: raw.reviewer.name,
    email: raw.reviewer.email,
    role: raw.reviewer.role,
  };
  const dashboard: DashboardData = {
    transactionsAnalyzed: raw.dashboard.transactions_analyzed,
    openCases: raw.dashboard.open_cases,
    criticalCases: raw.dashboard.critical_cases,
    pendingReviews: raw.dashboard.pending_reviews,
    clearedToday: raw.dashboard.cleared_today,
    falsePositiveRate: raw.dashboard.false_positive_rate,
    flaggedTrend: raw.dashboard.flagged_trend,
  };
  return {
    reviewer,
    dashboard,
    cases,
    reports: raw.reports.map(report => mapReport(report, cases)),
    model: raw.model_runtime.model,
  };
}

export async function askCaseGemma(caseId: string, reviewerId: string, question: string) {
  return request<{ answer: string }>(`/cases/${caseId}/ask-gemma`, {
    method: 'POST',
    body: JSON.stringify({ reviewer_id: reviewerId, question }),
  });
}

export async function generateCaseReport(caseId: string, reviewerId: string): Promise<RawReport> {
  return request<RawReport>(`/reports/${caseId}/generate`, {
    method: 'POST',
    body: JSON.stringify({ generated_by: reviewerId, include_pdf: false }),
  });
}
