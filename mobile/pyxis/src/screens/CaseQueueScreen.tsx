import React, { useState } from 'react';
import { ScrollView, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Card, ProgressBar, RiskBadge } from '../components/ui';
import { CASES } from '../mockData';
import { colors, font, radius, riskBand, spacing } from '../theme';
import { CaseStatus, RiskCase } from '../types';
import ScreenHeader from '../components/ScreenHeader';

type SortKey = 'urgency' | 'anomaly' | 'uncertainty';

const STATUS_META: Record<CaseStatus, { label: string; color: string; soft: string }> = {
  OPEN: { label: 'Open', color: colors.high, soft: colors.highSoft },
  IN_REVIEW: { label: 'In review', color: colors.primary, soft: colors.primarySoft },
  ESCALATED: { label: 'Escalated', color: colors.critical, soft: colors.criticalSoft },
  CLEARED: { label: 'Cleared', color: colors.low, soft: colors.lowSoft },
  SUSPICIOUS: { label: 'Suspicious', color: colors.critical, soft: colors.criticalSoft },
};

export default function CaseQueueScreen({
  onBack,
  onOpenCase,
}: {
  onBack: () => void;
  onOpenCase: (id: string) => void;
}) {
  const [sort, setSort] = useState<SortKey>('urgency');

  const sorted = [...CASES].sort((a, b) => {
    if (sort === 'anomaly') return b.anomalyScore - a.anomalyScore;
    if (sort === 'uncertainty') {
      const u = (c: RiskCase) =>
        c.scenarios.filter(s => s.category === 'UNCERTAIN').reduce((m, s) => Math.max(m, s.matchScore), 0);
      return u(b) - u(a);
    }
    return b.currentRisk - a.currentRisk; // urgency
  });

  return (
    <SafeAreaView style={styles.root} edges={['top']}>
      <ScreenHeader title="Risk Case Queue" subtitle={`${CASES.length} active cases`} onBack={onBack} />
      <View style={styles.sortRow}>
        {(['urgency', 'anomaly', 'uncertainty'] as SortKey[]).map(k => (
          <TouchableOpacity
            key={k}
            onPress={() => setSort(k)}
            style={[styles.sortChip, sort === k && styles.sortChipOn]}>
            <Text style={[styles.sortText, sort === k && styles.sortTextOn]}>
              {k === 'urgency' ? 'Urgency' : k === 'anomaly' ? 'Anomaly' : 'Uncertainty'}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      <ScrollView contentContainerStyle={styles.list} showsVerticalScrollIndicator={false}>
        {sorted.map(c => {
          const band = riskBand(c.currentRisk);
          const status = STATUS_META[c.status];
          return (
            <TouchableOpacity key={c.id} activeOpacity={0.9} onPress={() => onOpenCase(c.id)}>
              <Card style={styles.card}>
                <View style={styles.topRow}>
                  <Text style={styles.caseId}>{c.id}</Text>
                  <View style={[styles.statusPill, { backgroundColor: status.soft }]}>
                    <Text style={[styles.statusText, { color: status.color }]}>{status.label}</Text>
                  </View>
                </View>
                <Text style={styles.customer}>{c.customerName}</Text>
                <Text style={styles.summary} numberOfLines={2}>
                  {c.triggerSummary}
                </Text>
                <View style={styles.metaRow}>
                  <View style={{ flex: 1 }}>
                    <View style={styles.scoreRow}>
                      <Text style={styles.scoreLabel}>Anomaly {c.anomalyScore}</Text>
                      <Text style={styles.scoreLabel}>Risk {c.currentRisk}</Text>
                    </View>
                    <ProgressBar value={c.currentRisk} color={band.color} />
                  </View>
                  <RiskBadge score={c.currentRisk} />
                </View>
              </Card>
            </TouchableOpacity>
          );
        })}
        <View style={{ height: spacing.xxl }} />
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.bg },
  sortRow: { flexDirection: 'row', paddingHorizontal: spacing.lg, gap: spacing.sm, marginBottom: spacing.sm },
  sortChip: {
    paddingHorizontal: spacing.lg,
    paddingVertical: 7,
    borderRadius: radius.pill,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
  },
  sortChipOn: { backgroundColor: colors.primary, borderColor: colors.primary },
  sortText: { fontSize: font.small, color: colors.textMuted, fontWeight: '600' },
  sortTextOn: { color: colors.onPrimary },
  list: { padding: spacing.lg, paddingTop: spacing.sm },
  card: { marginBottom: spacing.md },
  topRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  caseId: { fontSize: font.small, color: colors.textFaint, fontWeight: '700', letterSpacing: 0.5 },
  statusPill: { paddingHorizontal: spacing.md, paddingVertical: 4, borderRadius: radius.pill },
  statusText: { fontSize: font.tiny, fontWeight: '800' },
  customer: { fontSize: font.h3, fontWeight: '800', color: colors.text, marginTop: spacing.sm },
  summary: { fontSize: font.small, color: colors.textMuted, marginTop: 4, lineHeight: 19 },
  metaRow: { flexDirection: 'row', alignItems: 'center', marginTop: spacing.lg, gap: spacing.md },
  scoreRow: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 6 },
  scoreLabel: { fontSize: font.tiny, color: colors.textMuted, fontWeight: '600' },
});
