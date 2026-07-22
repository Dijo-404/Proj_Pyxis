/**
 * @format
 */

import { API_BASE_URL, askGemma, generateReport, loadWorkspace, submitReview } from '../src/api';

function mockFetchOnce(body: unknown, ok = true, status = 200) {
  (globalThis as any).fetch = jest.fn().mockResolvedValue({
    ok,
    status,
    json: async () => body,
  });
}

describe('loadWorkspace', () => {
  it('maps a raw bootstrap payload into camelCase workspace data', async () => {
    mockFetchOnce({
      reviewer: { reviewer_id: 'R-1', name: 'Ada', email: 'ada@bank.test', role: 'Compliance Reviewer' },
      dashboard: {
        transactions_analyzed: 100,
        open_cases: 2,
        critical_cases: 1,
        pending_reviews: 3,
        cleared_today: 4,
        false_positive_rate: 5.5,
        flagged_trend: [{ label: 'Mon', value: 3 }],
      },
      cases: [
        {
          case_id: 'CASE-1',
          customer_id: 'CUST-1',
          customer_name: 'Acme Co',
          customer_type: 'Business',
          business: 'Retail',
          trigger_transaction_id: 'TXN-1',
          trigger_summary: 'Large transfer',
          trigger_amount: '$10,000',
          risk_score: 82.4,
          status: 'ESCALATED',
          created_at: '2026-01-01T00:00:00Z',
          scenarios: [
            {
              scenario_id: 'SCN-1',
              category: 'SUSPICIOUS',
              name: 'Layering',
              description: null,
              match_score: 91.2,
            },
          ],
          decision_critical_evidence: null,
          recommended_actions: ['Request source of funds'],
          workspace_data: { sandbox: { runId: 'RUN-1' } },
        },
      ],
      model_runtime: { provider: 'local', model: 'gemma', local_only: true },
    });

    const workspace = await loadWorkspace();

    expect(workspace.reviewer).toEqual({
      id: 'R-1',
      name: 'Ada',
      email: 'ada@bank.test',
      role: 'Compliance Reviewer',
    });
    expect(workspace.dashboard.transactionsAnalyzed).toBe(100);
    expect(workspace.cases).toHaveLength(1);
    const [risked] = workspace.cases;
    expect(risked.id).toBe('CASE-1');
    expect(risked.currentRisk).toBe(82);
    expect(risked.status).toBe('ESCALATED');
    expect(risked.scenarios[0].description).toBe('No scenario description provided.');
    expect(risked.criticalQuestion.question).toContain('additional evidence');
  });

  it('throws when a case is missing its persisted sandbox trace', async () => {
    mockFetchOnce({
      reviewer: { reviewer_id: 'R-1', name: 'Ada', email: 'a@b.c', role: 'Reviewer' },
      dashboard: {
        transactions_analyzed: 0,
        open_cases: 0,
        critical_cases: 0,
        pending_reviews: 0,
        cleared_today: 0,
        false_positive_rate: 0,
        flagged_trend: [],
      },
      cases: [
        {
          case_id: 'CASE-2',
          customer_id: 'CUST-2',
          customer_name: 'X',
          customer_type: 'Business',
          business: 'Retail',
          trigger_transaction_id: 'TXN-2',
          trigger_summary: 'x',
          trigger_amount: '$1',
          risk_score: 10,
          status: 'OPEN',
          created_at: '2026-01-01T00:00:00Z',
          scenarios: [],
          decision_critical_evidence: null,
          recommended_actions: [],
          workspace_data: {},
        },
      ],
      model_runtime: { provider: 'local', model: 'gemma', local_only: true },
    });

    await expect(loadWorkspace()).rejects.toThrow('missing its persisted sandbox trace');
  });
});

describe('request error handling', () => {
  it('surfaces the server error message on a non-ok response', async () => {
    mockFetchOnce({ error: { message: 'case not found' } }, false, 404);
    await expect(askGemma('CASE-1', 'R-1', 'why?')).rejects.toThrow('case not found');
  });
});

describe('submitReview', () => {
  it('posts the review action and reason to the case review endpoint', async () => {
    mockFetchOnce({ resulting_status: 'CLEARED' });
    const result = await submitReview('CASE-1', 'R-1', 'CLEAR', 'Confirmed legitimate payroll run.');

    expect(result.resultingStatus).toBe('CLEARED');
    const [url, init] = (globalThis.fetch as jest.Mock).mock.calls[0];
    expect(url).toBe(`${API_BASE_URL}/cases/CASE-1/review`);
    expect(init.method).toBe('POST');
    expect(JSON.parse(init.body)).toEqual({
      reviewer_id: 'R-1',
      action: 'CLEAR',
      reason: 'Confirmed legitimate payroll run.',
    });
  });
});

describe('generateReport', () => {
  it('posts to the report generation endpoint', async () => {
    mockFetchOnce({ report_id: 'RPT-1', html_path: '/tmp/RPT-1.html' });
    const result = await generateReport('CASE-1', 'R-1');

    expect(result).toEqual({ reportId: 'RPT-1', htmlPath: '/tmp/RPT-1.html' });
    const [url, init] = (globalThis.fetch as jest.Mock).mock.calls[0];
    expect(url).toBe(`${API_BASE_URL}/reports/CASE-1/generate`);
    expect(JSON.parse(init.body)).toEqual({ generated_by: 'R-1', include_pdf: false });
  });
});
