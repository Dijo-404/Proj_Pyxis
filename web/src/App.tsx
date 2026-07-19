import { useEffect, useMemo, useState } from 'react';
import {
  Activity,
  ArrowRight,
  Bell,
  Check,
  ChevronDown,
  ChevronRight,
  CircleHelp,
  ClipboardCheck,
  Clock3,
  Database,
  Download,
  FileBarChart,
  FileText,
  Gauge,
  LayoutDashboard,
  LockKeyhole,
  Menu,
  MessageSquareText,
  Network,
  Plus,
  Search,
  ShieldCheck,
  SlidersHorizontal,
  Sparkles,
  TriangleAlert,
  UserRound,
  X,
  type LucideIcon,
} from 'lucide-react';
import { askCaseGemma, generateCaseReport, loadWorkspace } from './api';
import type {
  CaseStatus,
  DashboardData,
  EvidenceState,
  Report,
  RiskCase,
  RiskLevel,
  ViewKey,
  WorkspacePayload,
} from './types';

const navItems: { key: ViewKey; label: string; icon: LucideIcon }[] = [
  { key: 'overview', label: 'Overview', icon: LayoutDashboard },
  { key: 'cases', label: 'Case queue', icon: ClipboardCheck },
  { key: 'scenarios', label: 'Scenario arena', icon: Network },
  { key: 'evidence', label: 'Evidence', icon: Database },
  { key: 'reports', label: 'Reports', icon: FileBarChart },
];

const viewTitles: Record<ViewKey, string> = {
  overview: 'Overview',
  cases: 'Case queue',
  scenarios: 'Scenario arena',
  evidence: 'Evidence workspace',
  reports: 'Reports',
};

function toClass(value: string) {
  return value.toLowerCase().replaceAll(' ', '-');
}

function App() {
  const [activeView, setActiveView] = useState<ViewKey>('overview');
  const [query, setQuery] = useState('');
  const [riskFilter, setRiskFilter] = useState<'All' | RiskLevel>('All');
  const [workspaceData, setWorkspaceData] = useState<WorkspacePayload | null>(null);
  const [selectedCase, setSelectedCase] = useState<RiskCase | null>(null);
  const [drawerCase, setDrawerCase] = useState<RiskCase | null>(null);
  const [menuOpen, setMenuOpen] = useState(false);
  const [assistantOpen, setAssistantOpen] = useState(false);
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [toast, setToast] = useState('');
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState('');
  const cases = workspaceData?.cases ?? [];

  async function refreshWorkspace() {
    setLoading(true);
    setLoadError('');
    try {
      const payload = await loadWorkspace();
      setWorkspaceData(payload);
      setReports(payload.reports);
      setSelectedCase(current =>
        payload.cases.find(item => item.id === current?.id) ?? payload.cases[0] ?? null,
      );
    } catch (error) {
      setLoadError(error instanceof Error ? error.message : 'Unable to load the workspace');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void refreshWorkspace();
  }, []);

  const filteredCases = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    return cases.filter((item) => {
      const matchesQuery =
        !normalized ||
        [item.id, item.customer, item.trigger, item.owner]
          .join(' ')
          .toLowerCase()
          .includes(normalized);
      const matchesRisk = riskFilter === 'All' || item.risk === riskFilter;
      return matchesQuery && matchesRisk;
    });
  }, [cases, query, riskFilter]);

  function navigate(view: ViewKey) {
    setActiveView(view);
    setMenuOpen(false);
  }

  function openScenario(item: RiskCase) {
    setSelectedCase(item);
    setDrawerCase(null);
    navigate('scenarios');
  }

  function showToast(message: string) {
    setToast(message);
    window.setTimeout(() => setToast(''), 2600);
  }

  async function generateReport() {
    if (!selectedCase || !workspaceData) return;
    showToast(`Generating ${selectedCase.id} locally…`);
    try {
      await generateCaseReport(selectedCase.id, workspaceData.reviewer.id);
      await refreshWorkspace();
      showToast(`Report for ${selectedCase.id} generated locally`);
    } catch (error) {
      showToast(error instanceof Error ? error.message : 'Report generation failed');
    }
  }

  if (loading) {
    return <div className="bootstrap-state"><Sparkles size={28} /><h1>Loading local workspace</h1><p>Reading persisted cases from FastAPI and SQLite.</p></div>;
  }

  if (loadError || !workspaceData || !selectedCase) {
    return <div className="bootstrap-state error"><TriangleAlert size={28} /><h1>Backend unavailable</h1><p>{loadError || 'The workspace did not return any cases.'}</p><button className="button primary" onClick={() => void refreshWorkspace()}>Retry connection</button></div>;
  }

  return (
    <div className="app-shell">
      <div className="utility-bar">
        <div className="utility-left">
          <span>Private deployment</span>
          <span>India South</span>
          <span className="utility-secure"><LockKeyhole size={12} /> Data remains local</span>
        </div>
        <div className="utility-right">
          <span className="system-ready"><i /> All systems operational</span>
          <button onClick={() => showToast('Help center opened')}>Help</button>
        </div>
      </div>

      <header className="top-nav">
        <div className="brand-area">
          <button className="mobile-menu" aria-label="Toggle navigation" onClick={() => setMenuOpen(!menuOpen)}>
            {menuOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
          <button className="brand" onClick={() => navigate('overview')} aria-label="Pyxis home">
            <span className="brand-mark" aria-hidden="true"><span /></span>
            <span className="brand-name">PYXIS</span>
            <span className="brand-product">Compliance intelligence</span>
          </button>
        </div>
        <div className="top-search">
          <Search size={17} aria-hidden="true" />
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            onFocus={() => activeView === 'overview' && setActiveView('cases')}
            placeholder="Search cases, customers or transactions"
            aria-label="Search cases"
          />
          <kbd>⌘ K</kbd>
        </div>
        <div className="top-actions">
          <button className="icon-button help-button" aria-label="Help" onClick={() => showToast('Help center opened')}>
            <CircleHelp size={19} />
          </button>
          <div className="notification-wrap">
            <button
              className="icon-button notification-button"
              aria-label="Notifications"
              aria-expanded={notificationsOpen}
              onClick={() => setNotificationsOpen(!notificationsOpen)}
            >
              <Bell size={19} /><span className="notification-count">2</span>
            </button>
            {notificationsOpen && (
              <div className="notification-panel">
                <div className="popover-heading"><span>Notifications</span><button onClick={() => setNotificationsOpen(false)}><X size={16} /></button></div>
                <button onClick={() => { setNotificationsOpen(false); openScenario(cases[1] ?? cases[0]); }}>
                  <TriangleAlert size={17} />
                  <span><strong>{(cases[1] ?? cases[0]).id} requires review</strong><small>{(cases[1] ?? cases[0]).customer} · risk score {(cases[1] ?? cases[0]).score}</small></span>
                </button>
                <button onClick={() => { setNotificationsOpen(false); navigate('evidence'); }}>
                  <FileText size={17} />
                  <span><strong>Decision-critical evidence pending</strong><small>{selectedCase.id} · {selectedCase.criticalQuestion.recommendedAction}</small></span>
                </button>
              </div>
            )}
          </div>
          <button className="profile-button" onClick={() => showToast('Profile menu opened')}>
            <span className="profile-initials">{workspaceData.reviewer.name.split(' ').map(part => part[0]).slice(0, 2).join('')}</span>
            <span className="profile-copy"><strong>{workspaceData.reviewer.name}</strong><small>{workspaceData.reviewer.role}</small></span>
            <ChevronDown size={15} />
          </button>
        </div>
      </header>

      <div className="workspace">
        <aside className={`side-nav ${menuOpen ? 'is-open' : ''}`}>
          <div className="nav-label">Workspace</div>
          <nav aria-label="Primary navigation">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.key}
                  className={activeView === item.key ? 'active' : ''}
                  aria-current={activeView === item.key ? 'page' : undefined}
                  onClick={() => navigate(item.key)}
                >
                  <Icon size={18} /><span>{item.label}</span>
                  {item.key === 'cases' && <span className="nav-count">{workspaceData.dashboard.openCases}</span>}
                </button>
              );
            })}
          </nav>
          <div className="side-nav-bottom">
            <div className="nav-label">Local intelligence</div>
            <div className="model-status">
              <span className="model-icon"><Sparkles size={17} /></span>
              <span><strong>{workspaceData.model}</strong><small><i /> Ready · Ollama local</small></span>
            </div>
            <button className="assistant-launch" onClick={() => setAssistantOpen(true)}>
              <MessageSquareText size={18} /><span>Ask Gemma</span><ArrowRight size={16} />
            </button>
          </div>
        </aside>

        {menuOpen && <button className="nav-scrim" aria-label="Close navigation" onClick={() => setMenuOpen(false)} />}

        <main className="main-content">
          <div className="breadcrumb"><span>Pyxis</span><ChevronRight size={14} /><strong>{viewTitles[activeView]}</strong></div>
          {activeView === 'overview' && (
            <OverviewPage
              dashboard={workspaceData.dashboard}
              cases={filteredCases}
              onOpenCase={setDrawerCase}
              onOpenEvidence={(item) => { setSelectedCase(item); navigate('evidence'); }}
              onNavigate={navigate}
            />
          )}
          {activeView === 'cases' && (
            <CasesPage
              items={filteredCases}
              query={query}
              riskFilter={riskFilter}
              onQueryChange={setQuery}
              onRiskFilterChange={setRiskFilter}
              onOpenCase={setDrawerCase}
            />
          )}
          {activeView === 'scenarios' && (
            <ScenariosPage cases={cases} selectedCase={selectedCase} onSelectCase={setSelectedCase} onNavigate={navigate} />
          )}
          {activeView === 'evidence' && <EvidencePage selectedCase={selectedCase} onToast={showToast} />}
          {activeView === 'reports' && (
            <ReportsPage reports={reports} onGenerate={() => void generateReport()} onToast={showToast} />
          )}
        </main>
      </div>

      {drawerCase && (
        <CaseDrawer item={drawerCase} onClose={() => setDrawerCase(null)} onOpenScenario={openScenario} />
      )}
      {assistantOpen && <AssistantDrawer selectedCase={selectedCase} reviewerId={workspaceData.reviewer.id} onClose={() => setAssistantOpen(false)} />}
      {toast && <div className="toast"><Check size={17} />{toast}</div>}
    </div>
  );
}

function PageHeading({
  eyebrow,
  title,
  description,
  action,
}: {
  eyebrow: string;
  title: string;
  description: string;
  action?: React.ReactNode;
}) {
  return (
    <section className="page-heading">
      <div>
        <p>{eyebrow}</p>
        <h1>{title}</h1>
        <span>{description}</span>
      </div>
      {action && <div className="page-heading-action">{action}</div>}
    </section>
  );
}

function OverviewPage({
  dashboard,
  cases: visibleCases,
  onOpenCase,
  onOpenEvidence,
  onNavigate,
}: {
  dashboard: DashboardData;
  cases: RiskCase[];
  onOpenCase: (item: RiskCase) => void;
  onOpenEvidence: (item: RiskCase) => void;
  onNavigate: (view: ViewKey) => void;
}) {
  const flaggedThisWeek = dashboard.flaggedTrend.reduce((total, day) => total + day.value, 0);
  const focusCase = visibleCases[0];
  const focusPotential = focusCase?.counterfactual[focusCase.counterfactual.length - 1]?.to ?? focusCase?.score ?? 0;
  const metrics: { label: string; value: string; meta: string; icon: LucideIcon; tone?: string }[] = [
    { label: 'Transactions analyzed', value: dashboard.transactionsAnalyzed.toLocaleString('en-IN'), meta: `${flaggedThisWeek} flagged this week`, icon: Activity },
    { label: 'Open risk cases', value: String(dashboard.openCases), meta: `${dashboard.clearedToday} cleared today`, icon: ClipboardCheck },
    { label: 'Critical cases', value: String(dashboard.criticalCases), meta: 'Requires attention', icon: TriangleAlert, tone: 'danger' },
    { label: 'Pending reviews', value: String(dashboard.pendingReviews), meta: `${dashboard.falsePositiveRate}% false-positive rate`, icon: Clock3 },
  ];

  return (
    <>
      <PageHeading
        eyebrow={new Intl.DateTimeFormat('en-IN', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' }).format(new Date())}
        title="Compliance command center"
        description="Prioritize risk, compare plausible scenarios, and keep every decision evidence-backed."
        action={<button className="button primary" onClick={() => onNavigate('cases')}><Plus size={17} />New investigation</button>}
      />

      <section className="metric-grid" aria-label="Portfolio summary">
        {metrics.map((metric) => {
          const Icon = metric.icon;
          return (
            <article className={`metric-card ${metric.tone ?? ''}`} key={metric.label}>
              <div className="metric-top"><span>{metric.label}</span><Icon size={20} /></div>
              <strong>{metric.value}</strong>
              <small>{metric.meta}</small>
            </article>
          );
        })}
      </section>

      <section className="overview-grid">
        <article className="panel activity-panel">
          <div className="panel-heading">
            <div><p>Portfolio activity</p><h2>Flagged transaction trend</h2></div>
            <button className="text-button">Last 7 days <ChevronDown size={15} /></button>
          </div>
          <div className="chart-summary"><strong>{flaggedThisWeek}</strong><span>flagged this week<br /><b>persisted transaction signals</b></span></div>
          <BarChart data={dashboard.flaggedTrend} />
        </article>

        <article className="panel decision-panel">
          <div className="panel-heading">
            <div><p>Decision-critical evidence</p><h2>One question can change the risk</h2></div>
            <span className="case-reference">{focusCase?.id ?? 'No matching case'}</span>
          </div>
          {focusCase ? (
            <>
              <blockquote>{focusCase.criticalQuestion.question}</blockquote>
              <p className="decision-copy">{focusCase.criticalQuestion.whyItMatters}</p>
              <div className="risk-shift">
                <span><small>Current</small><strong>{focusCase.score}</strong></span>
                <div><i style={{ width: `${focusCase.score}%` }} /><ArrowRight size={17} /></div>
                <span><small>Potential</small><strong>{focusPotential}</strong></span>
              </div>
              <button className="button tertiary" onClick={() => onOpenEvidence(focusCase)}>Review requested evidence <ArrowRight size={17} /></button>
            </>
          ) : <p className="decision-copy">Clear the current search to review the highest-impact evidence request.</p>}
        </article>
      </section>

      <section className="section-block">
        <div className="section-heading">
          <div><p>Investigation queue</p><h2>Cases requiring attention</h2></div>
          <button className="text-link" onClick={() => onNavigate('cases')}>View all cases <ArrowRight size={16} /></button>
        </div>
        <CaseTable items={visibleCases.slice(0, 5)} onOpenCase={onOpenCase} />
      </section>

      <section className="bottom-grid">
        <article className="panel workflow-panel">
          <div className="panel-heading"><div><p>Safer workflow</p><h2>Recommended next actions</h2></div><ShieldCheck size={22} /></div>
          {visibleCases.slice(0, 3).map((item, index) => (
            <button className="action-row" key={item.id} onClick={() => onOpenCase(item)}>
              <span className="action-index">0{index + 1}</span>
              <span><strong>{item.recommendedActions[0] ?? item.criticalQuestion.recommendedAction}</strong><small>{item.id} · {item.risk} risk</small></span>
              <ArrowRight size={17} />
            </button>
          ))}
        </article>
        <article className="panel local-panel">
          <div className="local-visual" aria-hidden="true">
            <span className="core-node"><Sparkles size={20} /></span>
            <span className="node n1" /><span className="node n2" /><span className="node n3" /><span className="node n4" />
          </div>
          <div className="local-copy">
            <p>Private by architecture</p>
            <h2>Intelligence stays inside your boundary</h2>
            <span>Case data, prompts, and Gemma inference run entirely within the institution-controlled deployment.</span>
            <div className="local-facts"><span><LockKeyhole size={15} />No cloud transfer</span><span><Database size={15} />Local evidence only</span></div>
          </div>
        </article>
      </section>
    </>
  );
}

function BarChart({ data }: { data: DashboardData['flaggedTrend'] }) {
  const max = Math.max(...data.map(item => item.value), 1);
  return (
    <div className="bar-chart" aria-label="Flagged transactions over seven days">
      {data.map((item) => (
        <div className="bar-column" key={item.label}>
          <div className="bar-track"><span style={{ height: `${Math.max(8, (item.value / max) * 100)}%` }}><i>{item.value}</i></span></div>
          <small>{item.label}</small>
        </div>
      ))}
    </div>
  );
}

function CasesPage({
  items,
  query,
  riskFilter,
  onQueryChange,
  onRiskFilterChange,
  onOpenCase,
}: {
  items: RiskCase[];
  query: string;
  riskFilter: 'All' | RiskLevel;
  onQueryChange: (value: string) => void;
  onRiskFilterChange: (value: 'All' | RiskLevel) => void;
  onOpenCase: (item: RiskCase) => void;
}) {
  const openCount = items.filter(item => !['Cleared', 'Closed', 'Suspicious'].includes(item.status)).length;
  const criticalCount = items.filter(item => item.risk === 'Critical').length;
  const reviewCount = items.filter(item => ['In review', 'Pending documents'].includes(item.status)).length;
  return (
    <>
      <PageHeading
        eyebrow="Investigation workspace"
        title="Case queue"
        description="Review prioritized alerts and move each case toward an explainable human decision."
        action={<button className="button primary" onClick={() => onQueryChange('')}><Plus size={17} />Import case</button>}
      />
      <section className="queue-summary">
        <span><strong>{openCount}</strong> open</span><span><strong>{criticalCount}</strong> critical</span><span><strong>{reviewCount}</strong> awaiting review</span><span><strong>{items.length}</strong> visible cases</span>
      </section>
      <section className="filter-bar">
        <label className="case-search"><Search size={17} /><input value={query} onChange={(event) => onQueryChange(event.target.value)} placeholder="Search the case queue" /></label>
        <div className="risk-tabs" role="tablist" aria-label="Filter by risk">
          {(['All', 'Critical', 'High', 'Medium', 'Low'] as const).map((risk) => (
            <button key={risk} role="tab" aria-selected={riskFilter === risk} onClick={() => onRiskFilterChange(risk)}>{risk}</button>
          ))}
        </div>
        <button className="button filter-button"><SlidersHorizontal size={17} />Filters</button>
      </section>
      <div className="table-meta"><span>{items.length} cases</span><span>Sorted by risk score</span></div>
      <CaseTable items={items} onOpenCase={onOpenCase} />
      {items.length === 0 && <div className="empty-state"><Search size={24} /><h2>No cases found</h2><p>Try a different customer, case ID, or risk filter.</p><button className="text-link" onClick={() => { onQueryChange(''); onRiskFilterChange('All'); }}>Clear filters</button></div>}
    </>
  );
}

function CaseTable({ items, onOpenCase }: { items: RiskCase[]; onOpenCase: (item: RiskCase) => void }) {
  return (
    <>
      <div className="data-table-wrap case-table-wrap">
        <table className="data-table">
          <thead><tr><th>Case</th><th>Customer</th><th>Trigger</th><th>Risk</th><th>Status</th><th>Owner</th><th><span className="sr-only">Open</span></th></tr></thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id} onClick={() => onOpenCase(item)}>
                <td><strong className="case-id">{item.id}</strong><small>{item.updated}</small></td>
                <td><strong>{item.customer}</strong><small>{item.segment}</small></td>
                <td><span className="trigger-copy">{item.trigger}</span><small>{item.amount}</small></td>
                <td><span className={`risk-score risk-${toClass(item.risk)}`}><strong>{item.score}</strong><small>{item.risk}</small></span></td>
                <td><StatusBadge status={item.status} /></td>
                <td><span className="owner"><UserRound size={15} />{item.owner}</span></td>
                <td><button className="row-open" aria-label={`Open ${item.id}`}><ChevronRight size={18} /></button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="case-card-list">
        {items.map((item) => (
          <button className="case-list-card" key={item.id} onClick={() => onOpenCase(item)}>
            <span className="case-list-top">
              <span><strong className="case-id">{item.id}</strong><small>{item.updated}</small></span>
              <span className={`risk-score risk-${toClass(item.risk)}`}><strong>{item.score}</strong><small>{item.risk}</small></span>
            </span>
            <span className="case-list-customer"><strong>{item.customer}</strong><small>{item.segment}</small></span>
            <span className="case-list-trigger">{item.trigger}</span>
            <span className="case-list-bottom"><StatusBadge status={item.status} /><span>{item.amount}</span><ChevronRight size={18} /></span>
          </button>
        ))}
      </div>
    </>
  );
}

function StatusBadge({ status }: { status: CaseStatus }) {
  return <span className={`status-badge status-${toClass(status)}`}><i />{status}</span>;
}

function ScenariosPage({
  cases,
  selectedCase,
  onSelectCase,
  onNavigate,
}: {
  cases: RiskCase[];
  selectedCase: RiskCase;
  onSelectCase: (item: RiskCase) => void;
  onNavigate: (view: ViewKey) => void;
}) {
  return (
    <>
      <PageHeading
        eyebrow={`${selectedCase.id} · ${selectedCase.customer}`}
        title="Scenario arena"
        description="Compare competing explanations against the same trusted evidence—without collapsing uncertainty too early."
        action={
          <label className="case-picker"><span>Active case</span><select value={selectedCase.id} onChange={(event) => { const nextCase = cases.find((item) => item.id === event.target.value); if (nextCase) onSelectCase(nextCase); }}>{cases.map((item) => <option key={item.id} value={item.id}>{item.id} · {item.customer}</option>)}</select></label>
        }
      />
      <section className="case-context">
        <div><span>Current risk</span><strong>{selectedCase.score}</strong><small>{selectedCase.risk}</small></div>
        <div><span>Trigger transaction</span><strong>{selectedCase.amount}</strong><small>{selectedCase.trigger}</small></div>
        <div><span>Anomaly signal</span><strong>{selectedCase.anomalyScore}</strong><small>Deterministic signal score</small></div>
        <div><span>Investigation</span><strong>{selectedCase.evidenceItems.length}</strong><small>Persisted evidence items</small></div>
      </section>
      <section className="section-block scenario-section">
        <div className="section-heading"><div><p>Competing explanations</p><h2>Ranked by evidence match</h2></div><span className="method-note"><ShieldCheck size={16} />Human review required</span></div>
        <div className="scenario-grid">
          {selectedCase.scenarios.map((scenario, index) => (
            <article className={`scenario-card category-${toClass(scenario.category)}`} key={scenario.id}>
              <div className="scenario-top"><span className="category-label">{scenario.category}</span><span>0{index + 1}</span></div>
              <h3>{scenario.name}</h3>
              <p>{scenario.summary}</p>
              <div className="match-score"><span><strong>{scenario.score}%</strong> evidence match</span><div><i style={{ width: `${scenario.score}%` }} /></div></div>
              <div className="scenario-counts"><span><b className="match-mark">✓</b>{scenario.supporting} supporting</span><span><b className="contradict-mark">×</b>{scenario.contradicting} contradicting</span><span><b className="unknown-mark">?</b>{scenario.missing} unknown</span></div>
            </article>
          ))}
        </div>
      </section>
      <EvidenceMatrix selectedCase={selectedCase} />
      <section className="critical-banner">
        <div className="critical-icon"><Gauge size={26} /></div>
        <div><p>Decision-critical question</p><h2>{selectedCase.criticalQuestion.question}</h2><span>{selectedCase.criticalQuestion.whyItMatters} Modeled risk could move from {selectedCase.score} to {selectedCase.counterfactual[selectedCase.counterfactual.length - 1]?.to ?? selectedCase.score}.</span></div>
        <button className="button inverse" onClick={() => onNavigate('evidence')}>Open evidence request <ArrowRight size={17} /></button>
      </section>
    </>
  );
}

function EvidenceMatrix({ selectedCase }: { selectedCase: RiskCase }) {
  const symbol: Record<EvidenceState, string> = { Match: '✓', Contradict: '×', Unknown: '?', Partial: '◐' };
  return (
    <section className="section-block evidence-matrix-section">
      <div className="section-heading"><div><p>Evidence matrix</p><h2>Signal-by-scenario comparison</h2></div><div className="matrix-legend">{(['Match', 'Contradict', 'Partial', 'Unknown'] as EvidenceState[]).map((state) => <span key={state}><b className={`state-${toClass(state)}`}>{symbol[state]}</b>{state}</span>)}</div></div>
      <div className="data-table-wrap">
        <table className="evidence-table">
          <thead><tr><th>Evidence signal</th><th>Source</th>{selectedCase.scenarios.map((scenario) => <th key={scenario.id}>{scenario.name}</th>)}</tr></thead>
          <tbody>{selectedCase.evidenceRows.map((row) => <tr key={row.signal}><td><strong>{row.signal}</strong></td><td>{row.source}</td>{selectedCase.scenarios.map((scenario) => { const state = row.states[scenario.id] ?? 'Unknown'; return <td key={scenario.id}><span className={`evidence-state state-${toClass(state)}`}><b>{symbol[state]}</b>{state}</span></td>; })}</tr>)}</tbody>
        </table>
      </div>
    </section>
  );
}

function EvidencePage({ selectedCase, onToast }: { selectedCase: RiskCase; onToast: (message: string) => void }) {
  const [requested, setRequested] = useState(false);
  const potentialRisk = selectedCase.counterfactual[selectedCase.counterfactual.length - 1]?.to ?? selectedCase.score;
  const statusLabel = (status: string) => status === 'VERIFIED' ? 'Verified' : status === 'MISSING' ? 'Awaiting' : status === 'CONTRADICTED' ? 'Contradicted' : 'Review needed';
  const verifiedCount = selectedCase.evidenceItems.filter(item => item.status === 'VERIFIED').length;
  const awaitingCount = selectedCase.evidenceItems.filter(item => item.status === 'MISSING').length;
  const reviewCount = selectedCase.evidenceItems.filter(item => item.status === 'UNVERIFIED').length;
  const contradictionCount = selectedCase.evidenceItems.filter(item => item.type === 'CONTRADICTING').length;
  const coverage = selectedCase.evidenceItems.length === 0 ? 0 : Math.round((verifiedCount / selectedCase.evidenceItems.length) * 100);
  return (
    <>
      <PageHeading
        eyebrow={`${selectedCase.id} · Evidence workspace`}
        title="Resolve what matters most"
        description="Collect, verify, and trace the evidence behind every scenario and human decision."
        action={<button className="button primary" onClick={() => { setRequested(true); onToast('Evidence request sent securely'); }}><Plus size={17} />Request evidence</button>}
      />
      {requested && <div className="inline-notification success"><Check size={18} /><span><strong>Evidence request sent</strong>{selectedCase.criticalQuestion.recommendedAction}</span><button onClick={() => setRequested(false)}><X size={17} /></button></div>}
      <section className="evidence-layout">
        <div className="evidence-main">
          <article className="critical-question-card">
            <p>Highest decision impact</p>
            <h2>{selectedCase.criticalQuestion.question}</h2>
            <span>{selectedCase.criticalQuestion.whyItMatters}</span>
            <div className="impact-track"><span>{selectedCase.score} <small>Current</small></span><div><i /><i /><i /></div><span>{potentialRisk} <small>If verified</small></span></div>
          </article>
          <section className="section-block evidence-list-block">
            <div className="section-heading"><div><p>Collected evidence</p><h2>Case evidence</h2></div><span className="method-note">{selectedCase.evidenceItems.length} items · {verifiedCount} verified</span></div>
            {selectedCase.evidenceItems.map((item) => {
              const label = statusLabel(item.status);
              return (
                <button className="evidence-item" key={item.id} onClick={() => onToast(`${item.id} opened`)}>
                  <span className="document-icon"><FileText size={19} /></span>
                  <span><strong>{item.description}</strong><small>{item.type} · {item.source}</small></span>
                  <span className={`verification verification-${toClass(label)}`}>{label}</span>
                  <ChevronRight size={18} />
                </button>
              );
            })}
          </section>
        </div>
        <aside className="evidence-aside">
          <div className="panel-heading"><div><p>Evidence quality</p><h2>Coverage</h2></div><strong className="coverage-score">{coverage}%</strong></div>
          <div className="coverage-bar"><i style={{ width: `${coverage}%` }} /></div>
          <dl><div><dt>Verified</dt><dd>{verifiedCount}</dd></div><div><dt>Awaiting</dt><dd>{awaitingCount}</dd></div><div><dt>Needs review</dt><dd>{reviewCount}</dd></div><div><dt>Contradictions</dt><dd>{contradictionCount}</dd></div></dl>
          <div className="trust-note"><ShieldCheck size={19} /><span><strong>Trusted inputs only</strong>Gemma can cite these items, but cannot create or modify evidence.</span></div>
        </aside>
      </section>
    </>
  );
}

function ReportsPage({ reports, onGenerate, onToast }: { reports: Report[]; onGenerate: () => void; onToast: (message: string) => void }) {
  function downloadReport(report: Report) {
    const content = `PYXIS COMPLIANCE REPORT\n${report.id}\nCase: ${report.caseId}\nCustomer: ${report.customer}\nType: ${report.type}\nGenerated: ${report.generated}\n\nGenerated locally from persisted synthetic case evidence.`;
    const url = URL.createObjectURL(new Blob([content], { type: 'text/plain' }));
    const link = document.createElement('a');
    link.href = url;
    link.download = `${report.id}.txt`;
    link.click();
    URL.revokeObjectURL(url);
    onToast(`${report.id} downloaded`);
  }

  return (
    <>
      <PageHeading eyebrow="Evidence-backed output" title="Reports" description="Generate audit-ready reports locally from verified evidence, review decisions, and case history." action={<button className="button primary" onClick={onGenerate}><Plus size={17} />Generate report</button>} />
      <section className="report-summary">
        <article><FileBarChart size={22} /><span><strong>{reports.length}</strong><small>Reports this month</small></span></article>
        <article><ShieldCheck size={22} /><span><strong>Traceable</strong><small>Evidence citations</small></span></article>
        <article><Clock3 size={22} /><span><strong>Ollama</strong><small>Local generation</small></span></article>
      </section>
      <section className="section-block">
        <div className="section-heading"><div><p>Report library</p><h2>Recent reports</h2></div><button className="button filter-button"><SlidersHorizontal size={17} />Filter</button></div>
        <div className="data-table-wrap"><table className="report-table"><thead><tr><th>Report ID</th><th>Case</th><th>Customer</th><th>Report type</th><th>Generated</th><th>Status</th><th></th></tr></thead><tbody>{reports.map((report) => <tr key={report.id}><td><strong className="case-id">{report.id}</strong></td><td>{report.caseId}</td><td><strong>{report.customer}</strong></td><td>{report.type}</td><td>{report.generated}</td><td><span className="status-badge status-in-review"><i />{report.status}</span></td><td><button className="download-button" aria-label={`Download ${report.id}`} onClick={() => downloadReport(report)}><Download size={17} />Download</button></td></tr>)}</tbody></table></div>
      </section>
      <section className="report-note"><LockKeyhole size={22} /><div><h2>Local generation, complete traceability</h2><p>Reports are assembled inside your deployment boundary. Every material claim links back to computed signals, documents, or a recorded human review.</p></div></section>
    </>
  );
}

function CaseDrawer({ item, onClose, onOpenScenario }: { item: RiskCase; onClose: () => void; onOpenScenario: (item: RiskCase) => void }) {
  return (
    <div className="drawer-layer" role="dialog" aria-modal="true" aria-labelledby="case-drawer-title">
      <button className="drawer-scrim" aria-label="Close case details" onClick={onClose} />
      <aside className="case-drawer">
        <div className="drawer-heading"><div><p>{item.id}</p><h2 id="case-drawer-title">{item.customer}</h2></div><button className="icon-button" onClick={onClose} aria-label="Close"><X size={20} /></button></div>
        <div className="drawer-risk"><div><span>Current risk</span><strong>{item.score}</strong><small>{item.risk}</small></div><StatusBadge status={item.status} /></div>
        <dl className="case-facts"><div><dt>Customer ID</dt><dd>{item.customerId}</dd></div><div><dt>Amount</dt><dd>{item.amount}</dd></div><div><dt>Owner</dt><dd>{item.owner}</dd></div><div><dt>Location</dt><dd>{item.location}</dd></div></dl>
        <section className="drawer-section"><p>Trigger</p><h3>{item.trigger}</h3></section>
        <section className="drawer-section"><p>Detected anomalies</p><ul>{item.anomalies.map((anomaly) => <li key={anomaly}><TriangleAlert size={16} />{anomaly}</li>)}</ul></section>
        <section className="drawer-section next-action"><p>Recommended next action</p><h3>{item.recommendedActions[0] ?? item.criticalQuestion.recommendedAction}</h3><span>This is guidance for the assigned compliance officer, not an automated decision.</span></section>
        <div className="drawer-actions"><button className="button primary" onClick={() => onOpenScenario(item)}>Open investigation <ArrowRight size={17} /></button><button className="button secondary" onClick={onClose}>Close</button></div>
      </aside>
    </div>
  );
}

function AssistantDrawer({ selectedCase, reviewerId, onClose }: { selectedCase: RiskCase; reviewerId: string; onClose: () => void }) {
  const [messages, setMessages] = useState<{ role: 'assistant' | 'user'; text: string }[]>([
    { role: 'assistant', text: `I’m grounded in verified evidence for ${selectedCase.id}. Ask about risk drivers, competing scenarios, or the next safest action.` },
  ]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);

  async function ask(prompt: string) {
    const cleanPrompt = prompt.trim();
    if (!cleanPrompt || sending) return;
    setMessages((current) => [...current, { role: 'user', text: cleanPrompt }]);
    setInput('');
    setSending(true);
    try {
      const response = await askCaseGemma(selectedCase.id, reviewerId, cleanPrompt);
      setMessages((current) => [...current, { role: 'assistant', text: response.answer }]);
    } catch (error) {
      setMessages((current) => [...current, { role: 'assistant', text: error instanceof Error ? error.message : 'Local Gemma could not answer this question.' }]);
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="drawer-layer assistant-layer" role="dialog" aria-modal="true" aria-labelledby="assistant-title">
      <button className="drawer-scrim" aria-label="Close assistant" onClick={onClose} />
      <aside className="assistant-drawer">
        <div className="assistant-heading"><div className="assistant-symbol"><Sparkles size={20} /></div><div><p>Local case assistant</p><h2 id="assistant-title">Ask Gemma</h2></div><button className="icon-button" onClick={onClose} aria-label="Close"><X size={20} /></button></div>
        <div className="assistant-scope"><LockKeyhole size={15} /><span>Grounded in {selectedCase.id} · No external data access</span></div>
        <div className="message-list">{messages.map((message, index) => <div key={`${message.role}-${index}`} className={`message ${message.role}`}><span>{message.role === 'assistant' ? <Sparkles size={15} /> : 'PK'}</span><p>{message.text}</p></div>)}</div>
        {messages.length === 1 && <div className="quick-prompts"><p>Suggested questions</p>{['What is driving the risk score?', 'Compare the top two scenarios', 'What evidence should I request next?'].map((prompt) => <button key={prompt} disabled={sending} onClick={() => void ask(prompt)}>{prompt}<ArrowRight size={15} /></button>)}</div>}
        {sending && <div className="assistant-thinking"><Sparkles size={15} />Gemma is analyzing persisted evidence…</div>}
        <form className="assistant-input" onSubmit={(event) => { event.preventDefault(); void ask(input); }}><textarea value={input} onChange={(event) => setInput(event.target.value)} placeholder="Ask about this case" rows={2} disabled={sending} /><button className="button primary" aria-label="Send question" type="submit" disabled={sending || !input.trim()}><ArrowRight size={18} /></button></form>
        <p className="assistant-disclaimer">Gemma summarizes trusted evidence. Final decisions remain with the compliance officer.</p>
      </aside>
    </div>
  );
}

export default App;
