import React, { useState } from 'react';
import { ScrollView, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import ScreenHeader from '../components/ScreenHeader';
import Icon from '../components/Icon';
import { Card, Pill, PrimaryButton, ProgressBar, RiskBadge, SectionTitle } from '../components/ui';
import { getCaseById } from '../mockData';
import { colors, font, radius, riskBand, shadow, spacing } from '../theme';
import {
  CustomerTransaction,
  EvidenceStatus,
  ReviewAction,
  RiskCase,
  Scenario,
  ScenarioCategory,
} from '../types';

type Tab = 'transactions' | 'twin' | 'investigation' | 'scenarios' | 'evidence' | 'decision';

const TABS: { key: Tab; label: string }[] = [
  { key: 'transactions', label: 'Transactions' },
  { key: 'twin', label: 'Twin' },
  { key: 'investigation', label: 'Gemma' },
  { key: 'scenarios', label: 'Scenarios' },
  { key: 'evidence', label: 'Evidence' },
  { key: 'decision', label: 'Decision' },
];

const CAT_META: Record<ScenarioCategory, { color: string; soft: string; label: string }> = {
  LEGITIMATE: { color: colors.legit, soft: colors.lowSoft, label: 'Legitimate' },
  SUSPICIOUS: { color: colors.suspicious, soft: colors.criticalSoft, label: 'Suspicious' },
  UNCERTAIN: { color: colors.uncertain, soft: '#EEEAFA', label: 'Uncertain' },
};

export default function CaseDetailScreen({
  caseId,
  onBack,
  onAskGemma,
  onOpenSandbox,
}: {
  caseId: string;
  onBack: () => void;
  onAskGemma: (id: string) => void;
  onOpenSandbox: (id: string) => void;
}) {
  const data = getCaseById(caseId);
  const [tab, setTab] = useState<Tab>('transactions');

  if (!data) {
    return (
      <SafeAreaView style={styles.root} edges={['top']}>
        <ScreenHeader title="Case not found" onBack={onBack} />
      </SafeAreaView>
    );
  }

  const band = riskBand(data.currentRisk);

  return (
    <SafeAreaView style={styles.root} edges={['top']}>
      <ScreenHeader
        title={data.customerName}
        subtitle={`${data.id} · ${data.customerType}`}
        onBack={onBack}
        right={
          <TouchableOpacity onPress={() => onAskGemma(data.id)} style={styles.askBtn}>
            <Icon name="magic" size={16} color={colors.onPrimary} />
          </TouchableOpacity>
        }
      />

      {/* Risk summary strip */}
      <View style={[styles.strip, { backgroundColor: band.soft }]}>
        <View>
          <Text style={styles.stripLabel}>Current risk</Text>
          <Text style={[styles.stripValue, { color: band.color }]}>
            {data.currentRisk}
            <Text style={styles.stripOut}> / 100</Text>
          </Text>
        </View>
        <View style={styles.stripDivider} />
        <View>
          <Text style={styles.stripLabel}>Initial anomaly</Text>
          <Text style={styles.stripValueSm}>{data.anomalyScore} / 100</Text>
        </View>
        <View style={styles.stripDivider} />
        <RiskBadge score={data.currentRisk} />
      </View>

      {/* Tabs */}
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.tabRow}>
        {TABS.map(t => (
          <TouchableOpacity
            key={t.key}
            onPress={() => setTab(t.key)}
            style={[styles.tab, tab === t.key && styles.tabOn]}>
            <Text style={[styles.tabText, tab === t.key && styles.tabTextOn]}>{t.label}</Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      <ScrollView contentContainerStyle={styles.body} showsVerticalScrollIndicator={false}>
        {tab === 'transactions' && (
          <TransactionsTab data={data} onOpenSandbox={() => onOpenSandbox(data.id)} />
        )}
        {tab === 'twin' && <TwinTab data={data} />}
        {tab === 'investigation' && (
          <InvestigationTab
            data={data}
            onAskGemma={() => onAskGemma(data.id)}
            onOpenSandbox={() => onOpenSandbox(data.id)}
          />
        )}
        {tab === 'scenarios' && <ScenarioTab data={data} />}
        {tab === 'evidence' && <EvidenceTab data={data} />}
        {tab === 'decision' && <DecisionTab data={data} />}
        <View style={{ height: spacing.xxl }} />
      </ScrollView>
    </SafeAreaView>
  );
}

/* ---------- Transactions: risky vs non-risky for this customer ---------- */
function TransactionsTab({ data, onOpenSandbox }: { data: RiskCase; onOpenSandbox: () => void }) {
  const [open, setOpen] = useState<string | null>(null);
  const risky = data.sandbox.transactions.filter(t => t.risky);
  const clean = data.sandbox.transactions.filter(t => !t.risky);

  return (
    <View>
      <View style={styles.txnSummaryRow}>
        <View style={[styles.txnSummaryTile, { backgroundColor: colors.criticalSoft }]}>
          <Text style={[styles.txnSummaryValue, { color: colors.critical }]}>{risky.length}</Text>
          <Text style={styles.txnSummaryLabel}>Risky</Text>
        </View>
        <View style={[styles.txnSummaryTile, { backgroundColor: colors.lowSoft }]}>
          <Text style={[styles.txnSummaryValue, { color: colors.low }]}>{clean.length}</Text>
          <Text style={styles.txnSummaryLabel}>Non-risky</Text>
        </View>
      </View>

      {risky.length > 0 && (
        <>
          <SectionTitle>Flagged as risk</SectionTitle>
          {risky
            .sort((a, b) => b.riskScore - a.riskScore)
            .map(t => (
              <TxnRow key={t.id} t={t} open={open === t.id} onToggle={() => setOpen(open === t.id ? null : t.id)} />
            ))}
        </>
      )}

      <SectionTitle>Non-risky activity</SectionTitle>
      {clean.map(t => (
        <TxnRow key={t.id} t={t} open={open === t.id} onToggle={() => setOpen(open === t.id ? null : t.id)} />
      ))}

      <PrimaryButton
        title="Open the branch graph in Sandbox"
        icon="flask"
        onPress={onOpenSandbox}
        variant="outline"
        style={{ marginTop: spacing.lg }}
      />
    </View>
  );
}

function TxnRow({ t, open, onToggle }: { t: CustomerTransaction; open: boolean; onToggle: () => void }) {
  const tint = t.risky ? colors.critical : colors.low;
  return (
    <TouchableOpacity activeOpacity={0.9} onPress={onToggle}>
      <Card style={styles.txnCard}>
        <View style={styles.txnTop}>
          <View style={[styles.txnDot, { backgroundColor: tint }]} />
          <View style={{ flex: 1 }}>
            <Text style={styles.txnLabel}>{t.label}</Text>
            <Text style={styles.txnMeta}>
              {t.id} · {t.timestamp}
            </Text>
          </View>
          <View style={{ alignItems: 'flex-end' }}>
            <Text style={styles.txnAmount}>
              {t.direction === 'IN' ? '+' : '−'}
              {t.amount}
            </Text>
            <Text style={[styles.txnReason, { color: tint }]}>{t.reason}</Text>
          </View>
        </View>
        {open ? (
          <View style={styles.txnDetail}>
            <Text style={styles.txnExplain}>{t.explanation}</Text>
            {t.firedSignals.length > 0 ? (
              <View style={styles.txnSignals}>
                {t.firedSignals.map(s => (
                  <View key={s} style={styles.txnSignalChip}>
                    <Icon name="bolt" size={10} color={colors.critical} style={{ marginRight: 4 }} />
                    <Text style={styles.txnSignalText}>{s}</Text>
                  </View>
                ))}
              </View>
            ) : null}
          </View>
        ) : null}
        <Text style={styles.expandHint}>{open ? 'Tap to collapse' : 'Tap for anomaly detail'}</Text>
      </Card>
    </TouchableOpacity>
  );
}

/* ---------- Financial Twin (§27 Screen 4) ---------- */
function TwinTab({ data }: { data: RiskCase }) {
  return (
    <View>
      <SectionTitle>Financial Twin · normal vs current</SectionTitle>
      <Card>
        <View style={styles.twinHeadRow}>
          <Text style={[styles.twinHeadCol, { color: colors.low }]}>NORMAL</Text>
          <Text style={[styles.twinHeadCol, { color: colors.accent, textAlign: 'right' }]}>CURRENT</Text>
        </View>
        {data.twin.map((m, i) => (
          <View key={m.label} style={[styles.twinRow, i > 0 && styles.twinBorder]}>
            <View style={styles.twinLeft}>
              <Text style={styles.twinLabel}>{m.label}</Text>
              <Text style={styles.twinNormal}>{m.normal}</Text>
            </View>
            <View style={styles.twinRight}>
              <Text style={[styles.twinCurrent, m.deviated && { color: colors.accent }]}>
                {m.current}
              </Text>
              {m.deviated ? (
                <View style={styles.deviatedTag}>
                  <Text style={styles.deviatedText}>deviation</Text>
                </View>
              ) : (
                <Text style={styles.okTag}>within range</Text>
              )}
            </View>
          </View>
        ))}
      </Card>
      <Text style={styles.note}>
        The Adaptive Financial Twin represents this customer's trusted normal behavior. It updates
        only after a reviewer clears the activity (trust-gated learning).
      </Text>
    </View>
  );
}

/* ---------- Gemma Investigation (§27 Screen 5) ---------- */
function InvestigationTab({
  data,
  onAskGemma,
  onOpenSandbox,
}: {
  data: RiskCase;
  onAskGemma: () => void;
  onOpenSandbox: () => void;
}) {
  return (
    <View>
      <SectionTitle>Gemma investigation timeline</SectionTitle>
      <Card>
        {data.investigation.map((step, i) => (
          <View key={step.label} style={styles.stepRow}>
            <View style={styles.stepRail}>
              <View style={[styles.stepDot, step.done && styles.stepDotDone]}>
                {step.done ? <Icon name="check" size={11} color={colors.onPrimary} /> : null}
              </View>
              {i < data.investigation.length - 1 && <View style={styles.stepLine} />}
            </View>
            <View style={styles.stepBody}>
              <Text style={styles.stepLabel}>{step.label}</Text>
              {step.detail ? <Text style={styles.stepDetail}>{step.detail}</Text> : null}
            </View>
          </View>
        ))}
      </Card>
      <View style={styles.aiSafety}>
        <Icon name="shield" size={15} color={colors.primaryDark} style={styles.aiSafetyGlyph} />
        <Text style={styles.aiSafetyText}>
          Gemma reasons over trusted computed evidence only. It flags risk and requires review — it
          never declares guilt or overrides the compliance officer.
        </Text>
      </View>
      <PrimaryButton
        title="Open isolated agent sandbox"
        icon="flask"
        onPress={onOpenSandbox}
        style={{ marginTop: spacing.lg }}
      />
      <PrimaryButton
        title="Ask Gemma about this case"
        icon="magic"
        onPress={onAskGemma}
        variant="outline"
        style={{ marginTop: spacing.md }}
      />
    </View>
  );
}

/* ---------- Scenario Arena (§27 Screen 6) ---------- */
function ScenarioTab({ data }: { data: RiskCase }) {
  const [openId, setOpenId] = useState<string | null>(data.scenarios[0]?.id ?? null);
  return (
    <View>
      <SectionTitle>Scenario arena</SectionTitle>
      {data.scenarios.map(s => (
        <ScenarioCard key={s.id} s={s} open={openId === s.id} onToggle={() => setOpenId(openId === s.id ? null : s.id)} />
      ))}
    </View>
  );
}

function ScenarioCard({ s, open, onToggle }: { s: Scenario; open: boolean; onToggle: () => void }) {
  const cat = CAT_META[s.category];
  return (
    <Card style={styles.scenCard}>
      <TouchableOpacity activeOpacity={0.9} onPress={onToggle}>
        <View style={styles.scenTop}>
          <Pill label={cat.label} color={cat.color} soft={cat.soft} />
          <Text style={[styles.scenScore, { color: cat.color }]}>{s.matchScore}%</Text>
        </View>
        <Text style={styles.scenName}>{s.name}</Text>
        <ProgressBar value={s.matchScore} color={cat.color} />
        <Text style={styles.scenDesc}>{s.description}</Text>
      </TouchableOpacity>
      {open && (
        <View style={styles.scenDetail}>
          <EvidenceList title="Supporting" items={s.supporting} color={colors.low} icon="check-circle" />
          <EvidenceList title="Contradicting" items={s.contradicting} color={colors.critical} icon="times-circle" />
          <EvidenceList title="Unknown" items={s.unknown} color={colors.medium} icon="question-circle" />
        </View>
      )}
      <Text style={styles.expandHint}>{open ? 'Tap to collapse' : 'Tap for evidence'}</Text>
    </Card>
  );
}

function EvidenceList({
  title,
  items,
  color,
  icon,
}: {
  title: string;
  items: string[];
  color: string;
  icon: string;
}) {
  if (items.length === 0) return null;
  return (
    <View style={styles.evList}>
      <Text style={[styles.evTitle, { color }]}>{title}</Text>
      {items.map(it => (
        <View key={it} style={styles.evItem}>
          <Icon name={icon} size={13} color={color} style={styles.evGlyph} />
          <Text style={styles.evText}>{it}</Text>
        </View>
      ))}
    </View>
  );
}

/* ---------- Evidence Matrix (§27 Screen 7) ---------- */
const STATUS_SYMBOL: Record<EvidenceStatus, { icon: string; color: string }> = {
  MATCH: { icon: 'check-circle', color: colors.low },
  CONTRADICT: { icon: 'times-circle', color: colors.critical },
  UNKNOWN: { icon: 'question-circle', color: colors.medium },
  PARTIAL: { icon: 'adjust', color: colors.accent },
};

function EvidenceTab({ data }: { data: RiskCase }) {
  return (
    <View>
      <SectionTitle>Evidence matrix</SectionTitle>
      <Card padded={false} style={styles.matrixCard}>
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          <View>
            <View style={styles.matrixHead}>
              <Text style={[styles.matrixSignal, styles.matrixHeadText]}>Signal</Text>
              {data.scenarios.map(s => (
                <Text key={s.id} style={[styles.matrixCell, styles.matrixHeadText]} numberOfLines={1}>
                  {s.name.split(' ')[0]}
                </Text>
              ))}
            </View>
            {data.evidence.map((row, i) => (
              <View key={row.signal} style={[styles.matrixRow, i % 2 === 1 && styles.matrixRowAlt]}>
                <Text style={styles.matrixSignal}>{row.signal}</Text>
                {data.scenarios.map(s => {
                  const st = row.byScenario[s.id];
                  const sym = st ? STATUS_SYMBOL[st] : null;
                  return (
                    <View key={s.id} style={styles.matrixCell}>
                      {sym ? (
                        <Icon name={sym.icon} size={18} color={sym.color} />
                      ) : (
                        <Text style={[styles.matrixSym, { color: colors.textFaint }]}>–</Text>
                      )}
                    </View>
                  );
                })}
              </View>
            ))}
          </View>
        </ScrollView>
      </Card>
      <View style={styles.matrixLegend}>
        {(Object.keys(STATUS_SYMBOL) as EvidenceStatus[]).map(k => (
          <View key={k} style={styles.legendChip}>
            <Icon name={STATUS_SYMBOL[k].icon} size={14} color={STATUS_SYMBOL[k].color} />
            <Text style={styles.legendChipText}>{k.toLowerCase()}</Text>
          </View>
        ))}
      </View>
    </View>
  );
}

/* ---------- Decision-Critical Evidence + Counterfactual + Review (§27 Screens 8/11) ---------- */
function DecisionTab({ data }: { data: RiskCase }) {
  const [action, setAction] = useState<ReviewAction | null>(null);

  return (
    <View>
      {/* Decision-critical hero */}
      <View style={styles.critHero}>
        <Text style={styles.critLabel}>DECISION-CRITICAL EVIDENCE</Text>
        <Text style={styles.critQuestion}>{data.criticalQuestion.question}</Text>
        <Text style={styles.critWhy}>{data.criticalQuestion.whyItMatters}</Text>
        <View style={styles.critAction}>
          <Icon name="arrow-circle-right" size={16} color={colors.accent} style={styles.critActionGlyph} />
          <Text style={styles.critActionText}>{data.criticalQuestion.recommendedAction}</Text>
        </View>
      </View>

      {/* Counterfactual (§19) */}
      <SectionTitle>How evidence changes the risk</SectionTitle>
      <Card>
        {data.counterfactual.map((cf, i) => {
          const fromBand = riskBand(cf.from);
          const toBand = riskBand(cf.to);
          return (
            <View key={i} style={[styles.cfRow, i > 0 && styles.twinBorder]}>
              <Text style={styles.cfCond}>{cf.condition}</Text>
              <View style={styles.cfScores}>
                <Text style={[styles.cfScore, { color: fromBand.color }]}>{cf.from}</Text>
                <Icon name="long-arrow-right" size={14} color={colors.textFaint} style={styles.cfArrow} />
                <Text style={[styles.cfScore, { color: toBand.color }]}>{cf.to}</Text>
              </View>
            </View>
          );
        })}
        <Text style={styles.cfNote}>Scenario-based estimates, not guaranteed predictions.</Text>
      </Card>

      {/* Safer workflow list */}
      <SectionTitle>Recommended safer workflow</SectionTitle>
      <Card>
        {data.saferWorkflow.map((step, i) => (
          <View key={i} style={styles.wfRow}>
            <View style={styles.wfNum}>
              <Text style={styles.wfNumText}>{i + 1}</Text>
            </View>
            <Text style={styles.wfText}>{step}</Text>
          </View>
        ))}
      </Card>

      {/* Reviewer decision (§27 Screen 11) */}
      <SectionTitle>Reviewer decision</SectionTitle>
      <View style={styles.decisionGrid}>
        <DecisionButton label="Clear" color={colors.low} active={action === 'CLEAR'} onPress={() => setAction('CLEAR')} />
        <DecisionButton
          label="Request Evidence"
          color={colors.medium}
          active={action === 'REQUEST_MORE_EVIDENCE'}
          onPress={() => setAction('REQUEST_MORE_EVIDENCE')}
        />
        <DecisionButton label="Escalate" color={colors.accent} active={action === 'ESCALATE'} onPress={() => setAction('ESCALATE')} />
        <DecisionButton
          label="Mark Suspicious"
          color={colors.critical}
          active={action === 'MARK_SUSPICIOUS'}
          onPress={() => setAction('MARK_SUSPICIOUS')}
        />
      </View>

      {action ? (
        <View style={styles.decisionConfirm}>
          <Text style={styles.decisionConfirmText}>
            Decision recorded: <Text style={{ fontWeight: '800' }}>{labelFor(action)}</Text>. An audit
            log entry has been written for {data.id}.
          </Text>
        </View>
      ) : null}
      <PrimaryButton
        title="Generate compliance report"
        onPress={() => setAction(action ?? 'REQUEST_MORE_EVIDENCE')}
        variant="outline"
        style={{ marginTop: spacing.lg }}
      />
    </View>
  );
}

function DecisionButton({
  label,
  color,
  active,
  onPress,
}: {
  label: string;
  color: string;
  active: boolean;
  onPress: () => void;
}) {
  return (
    <TouchableOpacity
      activeOpacity={0.85}
      onPress={onPress}
      style={[
        styles.decisionBtn,
        { borderColor: color },
        active && { backgroundColor: color },
      ]}>
      <Text style={[styles.decisionBtnText, { color: active ? colors.onPrimary : color }]}>
        {label}
      </Text>
    </TouchableOpacity>
  );
}

function labelFor(a: ReviewAction): string {
  switch (a) {
    case 'CLEAR':
      return 'Clear / Legitimate';
    case 'REQUEST_MORE_EVIDENCE':
      return 'Request more evidence';
    case 'ESCALATE':
      return 'Escalated';
    case 'MARK_SUSPICIOUS':
      return 'Marked suspicious';
    default:
      return 'Closed';
  }
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.bg },
  askBtn: {
    width: 40,
    height: 40,
    borderRadius: 12,
    backgroundColor: colors.primary,
    alignItems: 'center',
    justifyContent: 'center',
  },
  strip: {
    flexDirection: 'row',
    alignItems: 'center',
    marginHorizontal: spacing.lg,
    borderRadius: radius.md,
    padding: spacing.md,
    gap: spacing.md,
  },
  stripLabel: { fontSize: font.tiny, color: colors.textMuted, fontWeight: '600' },
  stripValue: { fontSize: font.h2, fontWeight: '900' },
  stripOut: { fontSize: font.small, color: colors.textMuted, fontWeight: '600' },
  stripValueSm: { fontSize: font.h3, fontWeight: '800', color: colors.text },
  stripDivider: { width: 1, alignSelf: 'stretch', backgroundColor: 'rgba(0,0,0,0.08)' },
  tabRow: { paddingHorizontal: spacing.lg, paddingVertical: spacing.md, gap: spacing.sm },
  tab: {
    paddingHorizontal: spacing.lg,
    paddingVertical: 8,
    borderRadius: radius.pill,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    height: 38,
    justifyContent: 'center',
  },
  tabOn: { backgroundColor: colors.primary, borderColor: colors.primary },
  tabText: { fontSize: font.small, color: colors.textMuted, fontWeight: '700' },
  tabTextOn: { color: colors.onPrimary },
  body: { paddingHorizontal: spacing.lg, paddingTop: spacing.xs },

  // Transactions
  txnSummaryRow: { flexDirection: 'row', gap: spacing.md, marginBottom: spacing.lg },
  txnSummaryTile: { flex: 1, borderRadius: radius.md, padding: spacing.md, alignItems: 'center' },
  txnSummaryValue: { fontSize: font.h1, fontWeight: '900' },
  txnSummaryLabel: { fontSize: font.small, fontWeight: '700', color: colors.textMuted, marginTop: 2 },
  txnCard: { marginBottom: spacing.md },
  txnTop: { flexDirection: 'row', alignItems: 'center' },
  txnDot: { width: 9, height: 9, borderRadius: 5, marginRight: spacing.md },
  txnLabel: { fontSize: font.body, fontWeight: '700', color: colors.text },
  txnMeta: { fontSize: font.tiny, color: colors.textFaint, marginTop: 2 },
  txnAmount: { fontSize: font.body, fontWeight: '800', color: colors.text },
  txnReason: { fontSize: font.tiny, fontWeight: '700', marginTop: 2 },
  txnDetail: { marginTop: spacing.md, borderTopWidth: 1, borderTopColor: colors.divider, paddingTop: spacing.md },
  txnExplain: { fontSize: font.small, color: colors.text, lineHeight: 19 },
  txnSignals: { flexDirection: 'row', flexWrap: 'wrap', gap: spacing.sm, marginTop: spacing.md },
  txnSignalChip: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.criticalSoft,
    paddingHorizontal: spacing.sm,
    paddingVertical: 4,
    borderRadius: radius.pill,
  },
  txnSignalText: { fontSize: font.tiny, color: colors.critical, fontWeight: '700' },

  // Twin
  twinHeadRow: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: spacing.sm },
  twinHeadCol: { flex: 1, fontSize: font.tiny, fontWeight: '800', letterSpacing: 0.6 },
  twinRow: { flexDirection: 'row', justifyContent: 'space-between', paddingVertical: spacing.md },
  twinBorder: { borderTopWidth: 1, borderTopColor: colors.divider },
  twinLeft: { flex: 1 },
  twinRight: { flex: 1, alignItems: 'flex-end' },
  twinLabel: { fontSize: font.tiny, color: colors.textFaint, fontWeight: '600' },
  twinNormal: { fontSize: font.body, color: colors.text, fontWeight: '700', marginTop: 2 },
  twinCurrent: { fontSize: font.body, color: colors.text, fontWeight: '700' },
  deviatedTag: {
    backgroundColor: colors.accentSoft,
    paddingHorizontal: spacing.sm,
    paddingVertical: 2,
    borderRadius: radius.pill,
    marginTop: 4,
  },
  deviatedText: { fontSize: font.tiny, color: colors.accent, fontWeight: '700' },
  okTag: { fontSize: font.tiny, color: colors.low, fontWeight: '600', marginTop: 4 },
  note: { fontSize: font.small, color: colors.textMuted, marginTop: spacing.lg, lineHeight: 20 },

  // Investigation
  stepRow: { flexDirection: 'row' },
  stepRail: { width: 30, alignItems: 'center' },
  stepDot: {
    width: 22,
    height: 22,
    borderRadius: 11,
    borderWidth: 2,
    borderColor: colors.border,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.surface,
  },
  stepDotDone: { backgroundColor: colors.primary, borderColor: colors.primary },
  stepLine: { flex: 1, width: 2, backgroundColor: colors.primaryLight, marginVertical: 2 },
  stepBody: { flex: 1, paddingBottom: spacing.lg, paddingLeft: spacing.sm },
  stepLabel: { fontSize: font.body, color: colors.text, fontWeight: '600' },
  stepDetail: { fontSize: font.small, color: colors.textMuted, marginTop: 2 },
  aiSafety: {
    flexDirection: 'row',
    backgroundColor: colors.primarySoft,
    borderRadius: radius.md,
    padding: spacing.md,
    marginTop: spacing.md,
  },
  aiSafetyGlyph: { marginRight: spacing.sm, marginTop: 1 },
  aiSafetyText: { flex: 1, fontSize: font.small, color: colors.primaryDark, lineHeight: 19 },

  // Scenario
  scenCard: { marginBottom: spacing.md },
  scenTop: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  scenScore: { fontSize: font.h2, fontWeight: '900' },
  scenName: { fontSize: font.h3, fontWeight: '800', color: colors.text, marginVertical: spacing.sm },
  scenDesc: { fontSize: font.small, color: colors.textMuted, marginTop: spacing.sm, lineHeight: 19 },
  scenDetail: { marginTop: spacing.md, borderTopWidth: 1, borderTopColor: colors.divider, paddingTop: spacing.md },
  evList: { marginBottom: spacing.md },
  evTitle: { fontSize: font.tiny, fontWeight: '800', letterSpacing: 0.5, marginBottom: 4 },
  evItem: { flexDirection: 'row', alignItems: 'flex-start', marginBottom: 3 },
  evGlyph: { width: 18, marginTop: 2 },
  evText: { flex: 1, fontSize: font.small, color: colors.text, lineHeight: 19 },
  expandHint: { fontSize: font.tiny, color: colors.textFaint, marginTop: spacing.sm, textAlign: 'center' },

  // Evidence matrix
  matrixCard: { padding: spacing.md },
  matrixHead: { flexDirection: 'row', paddingBottom: spacing.sm, borderBottomWidth: 1, borderBottomColor: colors.border },
  matrixHeadText: { fontWeight: '800', color: colors.textMuted, fontSize: font.tiny },
  matrixRow: { flexDirection: 'row', alignItems: 'center', paddingVertical: spacing.md },
  matrixRowAlt: { backgroundColor: colors.surfaceAlt },
  matrixSignal: { width: 150, fontSize: font.small, color: colors.text, fontWeight: '600', paddingLeft: spacing.xs },
  matrixCell: { width: 78, alignItems: 'center' },
  matrixSym: { fontSize: 18, fontWeight: '900' },
  matrixLegend: { flexDirection: 'row', flexWrap: 'wrap', gap: spacing.sm, marginTop: spacing.md },
  legendChip: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.surface,
    paddingHorizontal: spacing.md,
    paddingVertical: 6,
    borderRadius: radius.pill,
    gap: 6,
    ...shadow.card,
  },
  legendChipText: { fontSize: font.tiny, color: colors.textMuted, fontWeight: '600' },

  // Decision
  critHero: {
    backgroundColor: colors.text,
    borderRadius: radius.lg,
    padding: spacing.lg,
    marginBottom: spacing.lg,
    ...shadow.floating,
  },
  critLabel: { color: colors.primaryLight, fontSize: font.tiny, fontWeight: '800', letterSpacing: 1 },
  critQuestion: { color: colors.onPrimary, fontSize: font.h3, fontWeight: '800', marginTop: spacing.sm, lineHeight: 25 },
  critWhy: { color: 'rgba(255,255,255,0.75)', fontSize: font.small, marginTop: spacing.md, lineHeight: 20 },
  critAction: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginTop: spacing.md,
    backgroundColor: 'rgba(255,255,255,0.1)',
    borderRadius: radius.md,
    padding: spacing.md,
  },
  critActionGlyph: { marginRight: spacing.sm, marginTop: 1 },
  critActionText: { flex: 1, color: colors.onPrimary, fontSize: font.small, lineHeight: 19 },
  cfRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingVertical: spacing.md },
  cfCond: { flex: 1, fontSize: font.small, color: colors.text, paddingRight: spacing.md },
  cfScores: { flexDirection: 'row', alignItems: 'center' },
  cfScore: { fontSize: font.h3, fontWeight: '800' },
  cfArrow: { marginHorizontal: spacing.sm },
  cfNote: { fontSize: font.tiny, color: colors.textFaint, marginTop: spacing.sm, fontStyle: 'italic' },
  wfRow: { flexDirection: 'row', alignItems: 'flex-start', paddingVertical: spacing.sm },
  wfNum: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: colors.primarySoft,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: spacing.md,
  },
  wfNumText: { color: colors.primaryDark, fontSize: font.tiny, fontWeight: '800' },
  wfText: { flex: 1, fontSize: font.small, color: colors.text, lineHeight: 20 },
  decisionGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: spacing.md },
  decisionBtn: {
    width: '47%',
    flexGrow: 1,
    height: 50,
    borderRadius: radius.md,
    borderWidth: 1.5,
    alignItems: 'center',
    justifyContent: 'center',
  },
  decisionBtnText: { fontSize: font.small, fontWeight: '800' },
  decisionConfirm: {
    marginTop: spacing.lg,
    backgroundColor: colors.lowSoft,
    borderRadius: radius.md,
    padding: spacing.md,
  },
  decisionConfirmText: { fontSize: font.small, color: colors.text, lineHeight: 20 },
});
