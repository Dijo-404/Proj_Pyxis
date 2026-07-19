import React, { useState } from 'react';
import {
  Dimensions,
  Modal,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from '../components/Icon';
import ScreenHeader from '../components/ScreenHeader';
import {
  Card,
  Chip,
  Divider,
  ProgressBar,
  ScoreGauge,
  SectionTitle,
} from '../components/ui';
import { colors, font, radius, riskBand, shadow, spacing } from '../theme';
import { Actor, AgentStage, CustomerTransaction, FlowNode, RiskCase } from '../types';
import { useWorkspace } from '../workspace';

/** Actor styling — Gemma reasoning vs deterministic local code. */
const ACTOR_META: Record<Actor, { label: string; color: string; soft: string; icon: string }> = {
  GEMMA: { label: 'Gemma', color: colors.uncertain, soft: '#EEEAFA', icon: 'magic' },
  DETERMINISTIC: { label: 'Local code', color: colors.primary, soft: colors.primarySoft, icon: 'calculator' },
};

const VERIFIED_META: Record<
  NonNullable<FlowNode['verified']>,
  { color: string; soft: string; icon: string; label: string }
> = {
  VERIFIED: { color: colors.low, soft: colors.lowSoft, icon: 'check-circle', label: 'Verified' },
  UNKNOWN: { color: colors.medium, soft: colors.mediumSoft, icon: 'question-circle', label: 'Unknown' },
  FLAGGED: { color: colors.critical, soft: colors.criticalSoft, icon: 'exclamation-circle', label: 'Flagged' },
};

export default function SandboxScreen({
  caseId,
  onBack,
}: {
  caseId: string;
  onBack: () => void;
}) {
  const { data: workspace } = useWorkspace();
  const data = workspace?.cases.find(item => item.id === caseId);

  if (!data) {
    return (
      <SafeAreaView style={styles.root} edges={['top']}>
        <ScreenHeader title="Sandbox unavailable" onBack={onBack} />
      </SafeAreaView>
    );
  }

  const sb = data.sandbox;
  const band = riskBand(sb.anomaly.score);

  return (
    <SafeAreaView style={styles.root} edges={['top']}>
      <ScreenHeader
        title="Agent Sandbox"
        subtitle={`${data.customerName} · ${sb.runId}`}
        onBack={onBack}
      />
      <ScrollView contentContainerStyle={styles.body} showsVerticalScrollIndicator={false}>
        {/* Isolation boundary banner */}
        <View style={styles.boundary}>
          <Icon name="lock" size={14} color={colors.primaryDark} style={styles.boundaryIcon} />
          <Text style={styles.boundaryText}>
            Isolated simulation · synthetic data · local Gemma only.{' '}
            {sb.boundaryHeld ? 'Boundary held — nothing left the device.' : 'Boundary breached.'}
          </Text>
        </View>

        {/* Run meta */}
        <View style={styles.metaRow}>
          <Chip icon="microchip" label={sb.model} color={colors.text} soft={colors.surfaceAlt} />
          <Chip icon="server" label={sb.runtime} color={colors.text} soft={colors.surfaceAlt} />
        </View>
        <View style={styles.metaRow}>
          <Chip icon="hashtag" label={`seed ${sb.seed}`} color={colors.textMuted} soft={colors.surfaceAlt} />
          <Chip
            icon="clock-o"
            label={`${(sb.totalDurationMs / 1000).toFixed(2)}s total`}
            color={colors.textMuted}
            soft={colors.surfaceAlt}
          />
        </View>

        {/* Anomaly breakdown — why this transaction matters / is marked risk */}
        <SectionTitle>Why this is flagged</SectionTitle>
        <Card>
          <View style={styles.gaugeRow}>
            <ScoreGauge value={sb.anomaly.score} color={band.color} label="ANOMALY" caption={sb.anomaly.deviationLevel} />
            <View style={styles.gaugeText}>
              <Text style={styles.mattersLabel}>Why it matters</Text>
              <Text style={styles.mattersText}>{sb.anomaly.matters}</Text>
            </View>
          </View>
          <Divider />
          <Text style={styles.mattersLabel}>Why it is marked as risk</Text>
          <Text style={styles.mattersText}>{sb.anomaly.markedRisk}</Text>
        </Card>

        {/* Signal contributions */}
        <Card style={styles.block}>
          <Text style={styles.cardHead}>Signal contributions</Text>
          {sb.anomaly.signals.map(sig => (
            <View key={sig.key} style={styles.sigRow}>
              <View style={styles.sigHead}>
                <View style={styles.sigLabelWrap}>
                  <Icon
                    name={sig.fired ? 'dot-circle-o' : 'circle-o'}
                    size={12}
                    color={sig.fired ? band.color : colors.textFaint}
                    style={styles.sigDot}
                  />
                  <Text style={[styles.sigLabel, !sig.fired && styles.sigMuted]}>{sig.label}</Text>
                </View>
                <Text style={[styles.sigValue, { color: sig.fired ? band.color : colors.textFaint }]}>
                  {sig.value}
                </Text>
              </View>
              {sig.fired ? (
                <>
                  <ProgressBar value={sig.contribution} color={band.color} height={6} />
                  <Text style={styles.sigWhy}>{sig.why}</Text>
                </>
              ) : (
                <Text style={styles.sigWhy}>{sig.why}</Text>
              )}
            </View>
          ))}
        </Card>

        {/* Agent pipeline */}
        <SectionTitle>Agent run · {sb.stages.length} stages</SectionTitle>
        {sb.stages.map((stage, i) => (
          <StageCard key={stage.kind} stage={stage} last={i === sb.stages.length - 1} />
        ))}

        {/* Neural-network transaction branch graph */}
        <SectionTitle>Transaction branch graph</SectionTitle>
        <BranchGraph data={data} />

        {/* Follow the money */}
        <SectionTitle>Follow the money</SectionTitle>
        <MoneyFlow data={data} />

        <View style={{ height: spacing.xxl }} />
      </ScrollView>
    </SafeAreaView>
  );
}

function StageCard({ stage, last }: { stage: AgentStage; last: boolean }) {
  const [open, setOpen] = useState(false);
  const actor = ACTOR_META[stage.actor];
  return (
    <View style={styles.stageWrap}>
      <View style={styles.stageRail}>
        <View style={[styles.stageDot, { backgroundColor: actor.color }]}>
          <Icon name={actor.icon} size={12} color={colors.onPrimary} />
        </View>
        {!last && <View style={styles.stageLine} />}
      </View>
      <Card style={styles.stageCard}>
        <TouchableOpacity activeOpacity={0.9} onPress={() => setOpen(o => !o)}>
          <View style={styles.stageTop}>
            <Text style={styles.stageTitle}>{stage.title}</Text>
            <Chip label={actor.label} icon={actor.icon} color={actor.color} soft={actor.soft} />
          </View>
          <Text style={styles.stageSummary}>{stage.summary}</Text>
          <View style={styles.stageFoot}>
            <Text style={styles.stageDuration}>{stage.durationMs} ms</Text>
            <Text style={styles.stageExpand}>{open ? 'Hide detail' : 'Show detail'}</Text>
          </View>
        </TouchableOpacity>

        {open && (
          <View style={styles.stageDetail}>
            <Text style={styles.ioLabel}>INPUT</Text>
            <Text style={styles.ioText}>{stage.input}</Text>
            <Text style={styles.ioLabel}>OUTPUT</Text>
            <Text style={styles.ioText}>{stage.output}</Text>
            {stage.toolCalls?.length ? (
              <>
                <Text style={styles.ioLabel}>DETERMINISTIC TOOL CALLS</Text>
                {stage.toolCalls.map((tc, idx) => (
                  <View key={idx} style={styles.toolCall}>
                    <Text style={styles.toolName}>
                      {tc.tool}
                      <Text style={styles.toolArgs}>({tc.args})</Text>
                    </Text>
                    <View style={styles.toolResultRow}>
                      <Icon name="long-arrow-right" size={12} color={colors.textFaint} style={styles.toolArrow} />
                      <Text style={styles.toolResult}>{tc.result}</Text>
                    </View>
                  </View>
                ))}
              </>
            ) : null}
          </View>
        )}
      </Card>
    </View>
  );
}

/* ---------- Neural-network-style transaction branch graph ----------
 * Each customer's transactions are laid out as nodes on a free canvas,
 * connected to their parent transaction(s) like a small neural net. Risky
 * nodes are colored and pulse-free (static) red/orange; tapping any node
 * opens a popup explaining the anomaly (or confirming it's clean). */
const GRAPH_W = Dimensions.get('window').width - spacing.lg * 2 - spacing.lg * 2; // card padding
const GRAPH_H = 320;
const NODE_R = 15;

function BranchGraph({ data }: { data: RiskCase }) {
  const { branches, transactions } = data.sandbox;
  const [selected, setSelected] = useState<CustomerTransaction | null>(null);
  const byId = (id: string) => branches.find(b => b.id === id);
  const txnFor = (branchId: string) =>
    transactions.find(t => t.id === byId(branchId)?.transactionId);

  return (
    <Card style={styles.graphCard}>
      <View style={styles.graphLegendRow}>
        <View style={styles.graphLegendItem}>
          <View style={[styles.graphLegendDot, { backgroundColor: colors.critical }]} />
          <Text style={styles.graphLegendText}>risky node</Text>
        </View>
        <View style={styles.graphLegendItem}>
          <View style={[styles.graphLegendDot, { backgroundColor: colors.low }]} />
          <Text style={styles.graphLegendText}>clean node</Text>
        </View>
      </View>

      <View style={[styles.graphCanvas, { height: GRAPH_H }]}>
        {/* edges */}
        {branches.flatMap(n =>
          n.parents.map(pid => {
            const parent = byId(pid);
            if (!parent) return null;
            return (
              <Edge
                key={`${pid}-${n.id}`}
                x1={parent.x * GRAPH_W}
                y1={parent.y * GRAPH_H}
                x2={n.x * GRAPH_W}
                y2={n.y * GRAPH_H}
              />
            );
          }),
        )}
        {/* nodes */}
        {branches.map(n => {
          const t = txnFor(n.id);
          if (!t) return null;
          const color = t.risky ? colors.critical : colors.low;
          return (
            <TouchableOpacity
              key={n.id}
              activeOpacity={0.8}
              onPress={() => setSelected(t)}
              style={[
                styles.graphNode,
                {
                  left: n.x * GRAPH_W - NODE_R,
                  top: n.y * GRAPH_H - NODE_R,
                  backgroundColor: color,
                  width: NODE_R * 2,
                  height: NODE_R * 2,
                  borderRadius: NODE_R,
                },
              ]}>
              {t.risky ? <Icon name="exclamation" size={12} color={colors.onPrimary} /> : (
                <Icon name="check" size={11} color={colors.onPrimary} />
              )}
              <Text style={styles.graphNodeLabel} numberOfLines={1}>
                {t.amount}
              </Text>
            </TouchableOpacity>
          );
        })}
      </View>
      <Text style={styles.graphNote}>
        Each node is a real transaction for this customer; branches trace which activity fed into
        which. Tap any node to see why it was — or wasn't — treated as risk.
      </Text>

      <TxnPopup transaction={selected} onClose={() => setSelected(null)} />
    </Card>
  );
}

/** Straight connector line, drawn as a thin rotated View (no SVG deps). */
function Edge({ x1, y1, x2, y2 }: { x1: number; y1: number; x2: number; y2: number }) {
  const dx = x2 - x1;
  const dy = y2 - y1;
  const length = Math.sqrt(dx * dx + dy * dy);
  const angle = (Math.atan2(dy, dx) * 180) / Math.PI;
  return (
    <View
      style={[
        styles.graphEdge,
        {
          width: length,
          left: x1,
          top: y1,
          transform: [{ rotate: `${angle}deg` }],
        },
      ]}
    />
  );
}

/** Popup shown when a graph node is tapped — the anomaly explanation. */
function TxnPopup({
  transaction,
  onClose,
}: {
  transaction: CustomerTransaction | null;
  onClose: () => void;
}) {
  return (
    <Modal visible={!!transaction} transparent animationType="fade" onRequestClose={onClose}>
      <TouchableOpacity style={styles.modalBackdrop} activeOpacity={1} onPress={onClose}>
        <TouchableOpacity activeOpacity={1} style={styles.modalCard} onPress={() => {}}>
          {transaction ? (
            <>
              <View style={styles.modalTop}>
                <View
                  style={[
                    styles.modalBadge,
                    { backgroundColor: transaction.risky ? colors.criticalSoft : colors.lowSoft },
                  ]}>
                  <Icon
                    name={transaction.risky ? 'exclamation-triangle' : 'check-circle'}
                    size={14}
                    color={transaction.risky ? colors.critical : colors.low}
                  />
                  <Text
                    style={[
                      styles.modalBadgeText,
                      { color: transaction.risky ? colors.critical : colors.low },
                    ]}>
                    {transaction.risky ? `Risk ${transaction.riskScore}/100` : 'Clean'}
                  </Text>
                </View>
                <TouchableOpacity onPress={onClose} hitSlop={10}>
                  <Icon name="times" size={18} color={colors.textFaint} />
                </TouchableOpacity>
              </View>

              <Text style={styles.modalTitle}>{transaction.label}</Text>
              <Text style={styles.modalMeta}>
                {transaction.id} · {transaction.timestamp} · {transaction.direction === 'IN' ? '+' : '−'}
                {transaction.amount}
              </Text>

              <Divider />

              <Text style={styles.modalSectionLabel}>WHAT'S WRONG (OR NOT)</Text>
              <Text style={styles.modalExplain}>{transaction.explanation}</Text>

              {transaction.firedSignals.length > 0 ? (
                <>
                  <Text style={[styles.modalSectionLabel, { marginTop: spacing.md }]}>
                    SIGNALS THAT FIRED
                  </Text>
                  <View style={styles.modalSignals}>
                    {transaction.firedSignals.map(s => (
                      <View key={s} style={styles.modalSignalChip}>
                        <Icon name="bolt" size={10} color={colors.critical} style={{ marginRight: 4 }} />
                        <Text style={styles.modalSignalText}>{s}</Text>
                      </View>
                    ))}
                  </View>
                </>
              ) : (
                <Text style={styles.modalClean}>No anomaly signals fired for this transaction.</Text>
              )}
            </>
          ) : null}
        </TouchableOpacity>
      </TouchableOpacity>
    </Modal>
  );
}

/* Follow-the-money: source -> customer -> beneficiaries (§27 Screen 9). */
function MoneyFlow({ data }: { data: RiskCase }) {
  const { nodes, edges } = data.sandbox.flow;
  const source = nodes.find(n => n.kind === 'SOURCE');
  const customer = nodes.find(n => n.kind === 'CUSTOMER');
  const beneficiaries = nodes.filter(n => n.kind === 'BENEFICIARY');
  const inbound = edges.find(e => e.to === customer?.id);

  return (
    <Card>
      {/* Source */}
      {source ? <FlowNodeRow node={source} caption={inbound?.amount} /> : null}
      <ConnectorDown />
      {/* Customer */}
      {customer ? <FlowNodeRow node={customer} highlight /> : null}
      <View style={styles.fanLabel}>
        <Icon name="level-down" size={13} color={colors.textFaint} />
        <Text style={styles.fanText}>
          redistributed to {beneficiaries.length} account{beneficiaries.length === 1 ? '' : 's'}
        </Text>
      </View>
      {/* Beneficiaries */}
      {beneficiaries.map(n => {
        const edge = edges.find(e => e.to === n.id);
        return <FlowNodeRow key={n.id} node={n} caption={edge?.amount} indent />;
      })}
    </Card>
  );
}

function FlowNodeRow({
  node,
  caption,
  highlight,
  indent,
}: {
  node: FlowNode;
  caption?: string;
  highlight?: boolean;
  indent?: boolean;
}) {
  const v = node.verified ? VERIFIED_META[node.verified] : null;
  const icon =
    node.kind === 'SOURCE' ? 'sign-in' : node.kind === 'CUSTOMER' ? 'university' : 'user';
  const tint = highlight ? colors.primary : v ? v.color : colors.textMuted;
  return (
    <View style={[styles.flowRow, indent && styles.flowIndent]}>
      <View style={[styles.flowIcon, { backgroundColor: (v?.soft ?? colors.surfaceAlt) }]}>
        <Icon name={icon} size={15} color={tint} />
      </View>
      <View style={{ flex: 1 }}>
        <Text style={styles.flowLabel} numberOfLines={1}>
          {node.label}
        </Text>
        {caption ? <Text style={styles.flowAmount}>{caption}</Text> : null}
      </View>
      {v ? <Chip label={v.label} icon={v.icon} color={v.color} soft={v.soft} /> : null}
    </View>
  );
}

function ConnectorDown() {
  return (
    <View style={styles.connector}>
      <Icon name="long-arrow-down" size={16} color={colors.textFaint} />
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.bg },
  body: { padding: spacing.lg, paddingTop: spacing.xs },

  boundary: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.primarySoft,
    borderRadius: radius.md,
    padding: spacing.md,
    marginBottom: spacing.md,
  },
  boundaryIcon: { marginRight: spacing.sm },
  boundaryText: { flex: 1, fontSize: font.small, color: colors.primaryDark, lineHeight: 18, fontWeight: '600' },

  metaRow: { flexDirection: 'row', gap: spacing.sm, marginBottom: spacing.sm, flexWrap: 'wrap' },

  block: { marginTop: spacing.md },
  cardHead: { fontSize: font.body, fontWeight: '800', color: colors.text, marginBottom: spacing.md },

  gaugeRow: { flexDirection: 'row', alignItems: 'center' },
  gaugeText: { flex: 1, marginLeft: spacing.lg },
  mattersLabel: {
    fontSize: font.tiny,
    fontWeight: '800',
    color: colors.textFaint,
    letterSpacing: 0.5,
    marginBottom: 4,
    marginTop: spacing.sm,
  },
  mattersText: { fontSize: font.small, color: colors.text, lineHeight: 20 },

  sigRow: { marginBottom: spacing.md },
  sigHead: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginBottom: 6 },
  sigLabelWrap: { flexDirection: 'row', alignItems: 'center', flex: 1 },
  sigDot: { marginRight: spacing.sm },
  sigLabel: { fontSize: font.small, fontWeight: '700', color: colors.text },
  sigMuted: { color: colors.textFaint, fontWeight: '600' },
  sigValue: { fontSize: font.small, fontWeight: '800' },
  sigWhy: { fontSize: font.tiny, color: colors.textMuted, marginTop: 5, lineHeight: 16 },

  // Stage pipeline
  stageWrap: { flexDirection: 'row', marginBottom: spacing.sm },
  stageRail: { width: 34, alignItems: 'center' },
  stageDot: {
    width: 28,
    height: 28,
    borderRadius: 14,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: spacing.md,
  },
  stageLine: { flex: 1, width: 2, backgroundColor: colors.divider, marginVertical: 2 },
  stageCard: { flex: 1, marginBottom: spacing.sm },
  stageTop: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  stageTitle: { fontSize: font.body, fontWeight: '800', color: colors.text, flex: 1, marginRight: spacing.sm },
  stageSummary: { fontSize: font.small, color: colors.textMuted, marginTop: 4, lineHeight: 18 },
  stageFoot: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: spacing.sm,
  },
  stageDuration: { fontSize: font.tiny, color: colors.textFaint, fontWeight: '700' },
  stageExpand: { fontSize: font.tiny, color: colors.primary, fontWeight: '700' },
  stageDetail: { marginTop: spacing.md, borderTopWidth: 1, borderTopColor: colors.divider, paddingTop: spacing.md },
  ioLabel: {
    fontSize: font.tiny,
    fontWeight: '800',
    color: colors.textFaint,
    letterSpacing: 0.5,
    marginBottom: 4,
    marginTop: spacing.sm,
  },
  ioText: { fontSize: font.small, color: colors.text, lineHeight: 19 },
  toolCall: {
    backgroundColor: colors.surfaceAlt,
    borderRadius: radius.sm,
    padding: spacing.sm,
    marginTop: spacing.sm,
  },
  toolName: { fontSize: font.small, fontWeight: '700', color: colors.primaryDark },
  toolArgs: { fontSize: font.tiny, fontWeight: '400', color: colors.textMuted },
  toolResultRow: { flexDirection: 'row', alignItems: 'center', marginTop: 3 },
  toolArrow: { marginRight: 6 },
  toolResult: { flex: 1, fontSize: font.small, color: colors.text },

  // Money flow
  flowRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: spacing.sm,
  },
  flowIndent: { paddingLeft: spacing.xl },
  flowIcon: {
    width: 38,
    height: 38,
    borderRadius: 11,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: spacing.md,
  },
  flowLabel: { fontSize: font.body, fontWeight: '700', color: colors.text },
  flowAmount: { fontSize: font.small, color: colors.textMuted, marginTop: 1 },
  connector: { alignItems: 'center', paddingVertical: 2 },
  fanLabel: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingLeft: spacing.sm,
    paddingVertical: spacing.sm,
  },
  fanText: { fontSize: font.tiny, color: colors.textFaint, marginLeft: spacing.sm, fontWeight: '600' },

  // Branch graph
  graphCard: { overflow: 'hidden' },
  graphLegendRow: { flexDirection: 'row', gap: spacing.lg, marginBottom: spacing.md },
  graphLegendItem: { flexDirection: 'row', alignItems: 'center' },
  graphLegendDot: { width: 8, height: 8, borderRadius: 4, marginRight: 6 },
  graphLegendText: { fontSize: font.tiny, color: colors.textMuted, fontWeight: '600' },
  graphCanvas: {
    width: '100%',
    backgroundColor: colors.surfaceAlt,
    borderRadius: radius.md,
    overflow: 'hidden',
  },
  graphEdge: {
    position: 'absolute',
    height: 2,
    backgroundColor: colors.border,
    transformOrigin: 'left center' as never,
  },
  graphNode: {
    position: 'absolute',
    alignItems: 'center',
    justifyContent: 'center',
    ...shadow.card,
  },
  graphNodeLabel: {
    position: 'absolute',
    top: NODE_R * 2 + 3,
    fontSize: 9,
    fontWeight: '700',
    color: colors.text,
    width: 64,
    left: -22,
    textAlign: 'center',
  },
  graphNote: { fontSize: font.tiny, color: colors.textMuted, marginTop: spacing.lg, lineHeight: 16 },

  // Transaction popup modal
  modalBackdrop: {
    flex: 1,
    backgroundColor: 'rgba(15,29,38,0.55)',
    alignItems: 'center',
    justifyContent: 'center',
    padding: spacing.xl,
  },
  modalCard: {
    width: '100%',
    maxWidth: 420,
    backgroundColor: colors.surface,
    borderRadius: radius.lg,
    padding: spacing.lg,
    ...shadow.floating,
  },
  modalTop: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  modalBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.md,
    paddingVertical: 5,
    borderRadius: radius.pill,
    gap: 6,
  },
  modalBadgeText: { fontSize: font.tiny, fontWeight: '800' },
  modalTitle: { fontSize: font.h3, fontWeight: '800', color: colors.text, marginTop: spacing.md },
  modalMeta: { fontSize: font.tiny, color: colors.textFaint, marginTop: 3, fontWeight: '600' },
  modalSectionLabel: {
    fontSize: font.tiny,
    fontWeight: '800',
    color: colors.textFaint,
    letterSpacing: 0.5,
    marginBottom: 6,
  },
  modalExplain: { fontSize: font.small, color: colors.text, lineHeight: 20 },
  modalSignals: { flexDirection: 'row', flexWrap: 'wrap', gap: spacing.sm },
  modalSignalChip: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.criticalSoft,
    paddingHorizontal: spacing.sm,
    paddingVertical: 4,
    borderRadius: radius.pill,
  },
  modalSignalText: { fontSize: font.tiny, color: colors.critical, fontWeight: '700' },
  modalClean: { fontSize: font.small, color: colors.low, fontWeight: '600' },
});
