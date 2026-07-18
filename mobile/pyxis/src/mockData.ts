/**
 * Mock investigation data for the Pyxis prototype.
 * Grounded in the architecture "Best Demo Story" (§36) plus a few extra cases
 * so each customer shows a distinct risk profile and safer-workflow guidance.
 */

import { DashboardStats, RiskCase, User } from './types';

export const DEMO_USER: User = {
  id: 'OFFICER-12',
  name: 'Priyan Kannaa',
  email: 'prie@gmail.com',
  role: 'Compliance Officer',
};

export const DASHBOARD: DashboardStats = {
  transactionsAnalyzed: 18420,
  openCases: 7,
  criticalCases: 2,
  pendingReviews: 4,
  clearedToday: 11,
  falsePositiveRate: 6.2,
};

/** Small weekly series for the dashboard trend chart (transactions flagged). */
export const FLAGGED_TREND: { label: string; value: number }[] = [
  { label: 'Mon', value: 3 },
  { label: 'Tue', value: 5 },
  { label: 'Wed', value: 4 },
  { label: 'Thu', value: 8 },
  { label: 'Fri', value: 6 },
  { label: 'Sat', value: 2 },
  { label: 'Sun', value: 7 },
];

export const CASES: RiskCase[] = [
  {
    id: 'CASE-1001',
    customerId: 'CUST-001',
    customerName: 'Nusantara Textiles',
    customerType: 'Business',
    business: 'Textile Retail',
    triggerTransaction: 'TXN-100234',
    triggerSummary:
      '₹12,00,000 received from a new international sender; ₹9,50,000 redistributed to 5 accounts within 40 min.',
    anomalyScore: 89,
    currentRisk: 84,
    status: 'OPEN',
    createdAt: '2026-07-18 10:02',
    twin: [
      { label: 'Typical amount', normal: '₹45K', current: '₹12L', deviated: true },
      { label: 'Transactions / day', normal: '3', current: '17', deviated: true },
      { label: 'Geography', normal: 'India only', current: 'Foreign inbound', deviated: true },
      { label: 'Beneficiaries', normal: '8 known', current: '5 new', deviated: true },
      { label: 'Active hours', normal: '08:00–21:00', current: '10:02', deviated: false },
      { label: 'Channel', normal: 'Mobile banking', current: 'Mobile banking', deviated: false },
    ],
    investigation: [
      { label: 'Amount deviation detected', done: true, detail: 'z-score 6.4 vs P95 range' },
      { label: 'Rapid fund movement detected', done: true, detail: '₹9.5L out in 40 min' },
      { label: 'Beneficiary novelty detected', done: true, detail: '5 first-seen accounts' },
      { label: 'Document context analyzed', done: true, detail: 'Export invoice found' },
      { label: 'Competing scenarios generated', done: true, detail: '3 scenarios ranked' },
      { label: 'Decision-critical evidence isolated', done: true },
    ],
    scenarios: [
      {
        id: 'SCN-1',
        category: 'SUSPICIOUS',
        name: 'Transaction Layering',
        description: 'Large incoming funds followed by rapid redistribution to new accounts.',
        matchScore: 84,
        supporting: [
          'Large incoming transaction',
          'Rapid outbound redistribution',
          'Five new beneficiaries',
        ],
        contradicting: ['Valid export invoice on file'],
        unknown: ['Beneficiaries verified as suppliers?'],
      },
      {
        id: 'SCN-2',
        category: 'LEGITIMATE',
        name: 'Legitimate Business Payment',
        description: 'Genuine supplier settlement following a large export order.',
        matchScore: 71,
        supporting: [
          'Valid invoice exists',
          'Sender name matches invoice',
          'Customer recently registered for exports',
        ],
        contradicting: ['Beneficiaries are brand new'],
        unknown: ['Are receiving accounts known suppliers?'],
      },
      {
        id: 'SCN-3',
        category: 'SUSPICIOUS',
        name: 'Account Takeover',
        description: 'Unauthorized control of the account draining funds.',
        matchScore: 17,
        supporting: ['Unusual transaction volume'],
        contradicting: ['Same device', 'Usual login hours', 'Known channel'],
        unknown: [],
      },
    ],
    evidence: [
      { signal: 'Invoice exists', byScenario: { 'SCN-1': 'CONTRADICT', 'SCN-2': 'MATCH', 'SCN-3': 'UNKNOWN' } },
      { signal: 'Rapid fund movement', byScenario: { 'SCN-1': 'MATCH', 'SCN-2': 'CONTRADICT', 'SCN-3': 'PARTIAL' } },
      { signal: 'New beneficiaries', byScenario: { 'SCN-1': 'MATCH', 'SCN-2': 'UNKNOWN', 'SCN-3': 'UNKNOWN' } },
      { signal: 'Sender verified', byScenario: { 'SCN-1': 'CONTRADICT', 'SCN-2': 'MATCH', 'SCN-3': 'CONTRADICT' } },
      { signal: 'Supplier relationship', byScenario: { 'SCN-1': 'UNKNOWN', 'SCN-2': 'UNKNOWN', 'SCN-3': 'UNKNOWN' } },
    ],
    criticalQuestion: {
      question: 'Are the five receiving accounts verified business suppliers?',
      whyItMatters:
        'Verified supplier relationships strongly support the legitimate business scenario and would drop the risk from High to Low.',
      recommendedAction: 'Request supplier invoices and relationship records for the five beneficiaries.',
    },
    counterfactual: [
      { condition: 'If invoice is verified', from: 84, to: 72 },
      { condition: 'If sender is a verified customer', from: 72, to: 61 },
      { condition: 'If beneficiaries are verified suppliers', from: 61, to: 28 },
    ],
    saferWorkflow: [
      'Verify beneficiary supplier relationships before clearing.',
      'Request supplier invoices for the five new accounts.',
      'Confirm source of funds with the international sender.',
      'Keep the case out of the normal baseline until resolved.',
    ],
  },
  {
    id: 'CASE-1002',
    customerId: 'CUST-014',
    customerName: 'Meridian Freight Co.',
    customerType: 'Business',
    business: 'Logistics',
    triggerTransaction: 'TXN-100781',
    triggerSummary: 'Structured cash deposits of ₹1.9L each across 6 branches in one day.',
    anomalyScore: 92,
    currentRisk: 88,
    status: 'ESCALATED',
    createdAt: '2026-07-18 09:14',
    twin: [
      { label: 'Typical amount', normal: '₹80K', current: '₹1.9L ×6', deviated: true },
      { label: 'Deposit channel', normal: 'Digital', current: 'Cash / branch', deviated: true },
      { label: 'Locations / day', normal: '1', current: '6', deviated: true },
      { label: 'Geography', normal: 'Chennai', current: '6 cities', deviated: true },
    ],
    investigation: [
      { label: 'Threshold-avoidance pattern detected', done: true, detail: 'All below ₹2L reporting limit' },
      { label: 'Multi-location clustering detected', done: true },
      { label: 'Document context analyzed', done: true, detail: 'No matching invoices' },
      { label: 'Competing scenarios generated', done: true },
    ],
    scenarios: [
      {
        id: 'SCN-1',
        category: 'SUSPICIOUS',
        name: 'Structuring',
        description: 'Deposits deliberately kept below the reporting threshold.',
        matchScore: 90,
        supporting: ['All deposits below ₹2L', 'Six locations same day', 'No commercial explanation'],
        contradicting: [],
        unknown: ['Source of cash'],
      },
      {
        id: 'SCN-2',
        category: 'UNCERTAIN',
        name: 'Insufficient Evidence',
        description: 'Business rationale possible but undocumented.',
        matchScore: 40,
        supporting: ['Established account age'],
        contradicting: ['No invoices'],
        unknown: ['Source of funds', 'Business justification'],
      },
    ],
    evidence: [
      { signal: 'Below threshold', byScenario: { 'SCN-1': 'MATCH', 'SCN-2': 'PARTIAL' } },
      { signal: 'Multi-location', byScenario: { 'SCN-1': 'MATCH', 'SCN-2': 'UNKNOWN' } },
      { signal: 'Invoice exists', byScenario: { 'SCN-1': 'CONTRADICT', 'SCN-2': 'UNKNOWN' } },
      { signal: 'Source of funds', byScenario: { 'SCN-1': 'UNKNOWN', 'SCN-2': 'UNKNOWN' } },
    ],
    criticalQuestion: {
      question: 'What is the documented source of the deposited cash?',
      whyItMatters:
        'A verifiable cash source is the single fact that separates structuring from a legitimate cash-heavy business.',
      recommendedAction: 'Request source-of-funds documentation and daily sales records.',
    },
    counterfactual: [
      { condition: 'If sales records match deposits', from: 88, to: 55 },
      { condition: 'If source of funds is documented', from: 55, to: 30 },
    ],
    saferWorkflow: [
      'Do not clear without documented source of funds.',
      'Request daily sales records across all six branches.',
      'Keep escalated pending EDD (enhanced due diligence).',
    ],
  },
  {
    id: 'CASE-1003',
    customerId: 'CUST-233',
    customerName: 'Aarav Menon',
    customerType: 'Individual',
    business: 'Salaried',
    triggerTransaction: 'TXN-101120',
    triggerSummary: '₹8,50,000 outbound property payment to a registered developer.',
    anomalyScore: 63,
    currentRisk: 34,
    status: 'IN_REVIEW',
    createdAt: '2026-07-17 16:40',
    twin: [
      { label: 'Typical amount', normal: '₹35K', current: '₹8.5L', deviated: true },
      { label: 'Beneficiary', normal: 'Known', current: 'Registered developer', deviated: false },
      { label: 'Geography', normal: 'India', current: 'India', deviated: false },
      { label: 'Source of funds', normal: '—', current: 'Home loan disbursed', deviated: false },
    ],
    investigation: [
      { label: 'Amount deviation detected', done: true },
      { label: 'Beneficiary lookup completed', done: true, detail: 'RERA-registered developer' },
      { label: 'Source-of-funds matched', done: true, detail: 'Home loan disbursement' },
      { label: 'Competing scenarios generated', done: true },
    ],
    scenarios: [
      {
        id: 'SCN-1',
        category: 'LEGITIMATE',
        name: 'Property Purchase',
        description: 'One-off large payment funded by a disbursed home loan.',
        matchScore: 86,
        supporting: ['Registered developer', 'Loan disbursement matches amount', 'Single transaction'],
        contradicting: [],
        unknown: [],
      },
      {
        id: 'SCN-2',
        category: 'UNCERTAIN',
        name: 'Insufficient Evidence',
        description: 'Large amount unusual for this profile.',
        matchScore: 22,
        supporting: ['Amount above P95'],
        contradicting: ['Loan documentation present'],
        unknown: [],
      },
    ],
    evidence: [
      { signal: 'Registered beneficiary', byScenario: { 'SCN-1': 'MATCH', 'SCN-2': 'CONTRADICT' } },
      { signal: 'Source of funds', byScenario: { 'SCN-1': 'MATCH', 'SCN-2': 'UNKNOWN' } },
      { signal: 'Single transaction', byScenario: { 'SCN-1': 'MATCH', 'SCN-2': 'CONTRADICT' } },
    ],
    criticalQuestion: {
      question: 'Does the sale agreement match the payment amount and developer?',
      whyItMatters: 'A matching agreement fully explains the deviation as a legitimate one-off purchase.',
      recommendedAction: 'Attach the sale agreement to close the case as legitimate.',
    },
    counterfactual: [{ condition: 'If sale agreement is attached', from: 34, to: 12 }],
    saferWorkflow: [
      'Attach sale agreement, then clear as legitimate.',
      'Once cleared, allow the twin to learn the new higher-value baseline gradually.',
    ],
  },
  {
    id: 'CASE-1004',
    customerId: 'CUST-089',
    customerName: 'Lotus Exports',
    customerType: 'Business',
    business: 'Handicraft Export',
    triggerTransaction: 'TXN-101455',
    triggerSummary: 'First-ever transfer to a high-risk jurisdiction (₹4,20,000).',
    anomalyScore: 71,
    currentRisk: 58,
    status: 'OPEN',
    createdAt: '2026-07-17 11:05',
    twin: [
      { label: 'Typical amount', normal: '₹1.2L', current: '₹4.2L', deviated: true },
      { label: 'Geography', normal: 'India, UAE', current: 'High-risk jurisdiction', deviated: true },
      { label: 'Beneficiary', normal: 'Known', current: 'New', deviated: true },
    ],
    investigation: [
      { label: 'Geographic novelty detected', done: true },
      { label: 'Amount deviation detected', done: true },
      { label: 'Document context analyzed', done: true, detail: 'Purchase order present' },
      { label: 'Competing scenarios generated', done: true },
    ],
    scenarios: [
      {
        id: 'SCN-1',
        category: 'LEGITIMATE',
        name: 'Business Expansion',
        description: 'New sourcing relationship in a new market.',
        matchScore: 64,
        supporting: ['Purchase order present', 'Consistent with export business'],
        contradicting: [],
        unknown: ['Counterparty due diligence'],
      },
      {
        id: 'SCN-2',
        category: 'SUSPICIOUS',
        name: 'High-Risk Counterparty',
        description: 'Transfer to an unverified party in a high-risk jurisdiction.',
        matchScore: 52,
        supporting: ['High-risk jurisdiction', 'New beneficiary'],
        contradicting: ['Purchase order present'],
        unknown: ['Counterparty legitimacy'],
      },
    ],
    evidence: [
      { signal: 'Purchase order', byScenario: { 'SCN-1': 'MATCH', 'SCN-2': 'CONTRADICT' } },
      { signal: 'High-risk geography', byScenario: { 'SCN-1': 'PARTIAL', 'SCN-2': 'MATCH' } },
      { signal: 'Counterparty verified', byScenario: { 'SCN-1': 'UNKNOWN', 'SCN-2': 'UNKNOWN' } },
    ],
    criticalQuestion: {
      question: 'Is the overseas counterparty a legitimate registered entity?',
      whyItMatters: 'Counterparty legitimacy separates genuine expansion from high-risk exposure.',
      recommendedAction: 'Run counterparty screening and request registration documents.',
    },
    counterfactual: [
      { condition: 'If counterparty screening passes', from: 58, to: 33 },
      { condition: 'If registration documents verified', from: 33, to: 20 },
    ],
    saferWorkflow: [
      'Screen the overseas counterparty before releasing further transfers.',
      'Request registration and beneficial-ownership documents.',
      'Apply enhanced monitoring on the new corridor.',
    ],
  },
];

export function getCaseById(id: string): RiskCase | undefined {
  return CASES.find(c => c.id === id);
}
