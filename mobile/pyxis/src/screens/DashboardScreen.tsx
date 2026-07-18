import React from 'react';
import { ScrollView, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useAuth } from '../auth';
import {
  Card,
  MiniBarChart,
  ProgressBar,
  RiskBadge,
  SectionTitle,
  StatTile,
} from '../components/ui';
import Icon from '../components/Icon';
import { CASES, DASHBOARD, FLAGGED_TREND } from '../mockData';
import { colors, font, radius, riskBand, shadow, spacing } from '../theme';
import { RiskCase } from '../types';

export default function DashboardScreen({
  onOpenCase,
  onOpenQueue,
}: {
  onOpenCase: (id: string) => void;
  onOpenQueue: () => void;
}) {
  const { user, signOut } = useAuth();

  const critical = CASES.filter(c => c.currentRisk >= 80);
  const portfolioRisk = Math.round(
    CASES.reduce((s, c) => s + c.currentRisk, 0) / CASES.length,
  );

  return (
    <SafeAreaView style={styles.root} edges={['top']}>
      <ScrollView
        contentContainerStyle={styles.content}
        showsVerticalScrollIndicator={false}>
        {/* Header */}
        <View style={styles.header}>
          <View style={styles.avatar}>
            <Text style={styles.avatarText}>
              {user?.name.charAt(0) ?? 'P'}
            </Text>
          </View>
          <View style={{ flex: 1 }}>
            <Text style={styles.welcome}>Welcome back</Text>
            <Text style={styles.userName}>{user?.name}</Text>
          </View>
          <TouchableOpacity style={styles.logout} onPress={signOut}>
            <Icon name="sign-out" size={13} color={colors.textMuted} style={styles.logoutIcon} />
            <Text style={styles.logoutText}>Sign out</Text>
          </TouchableOpacity>
        </View>

        {/* Portfolio risk hero — orange gradient-like card */}
        <View style={styles.hero}>
          <Text style={styles.heroLabel}>Portfolio risk exposure</Text>
          <View style={styles.heroRow}>
            <Text style={styles.heroValue}>{portfolioRisk}</Text>
            <Text style={styles.heroOutOf}> / 100</Text>
          </View>
          <ProgressBar
            value={portfolioRisk}
            color={colors.onPrimary}
            track="rgba(255,255,255,0.3)"
            height={10}
          />
          <View style={styles.heroFooter}>
            <Text style={styles.heroFootText}>
              {critical.length} critical · {DASHBOARD.openCases} open cases
            </Text>
            <View style={styles.heroTag}>
              <View style={styles.onlineDot} />
              <Text style={styles.heroTagText}>Local Gemma · online</Text>
            </View>
          </View>
        </View>

        {/* Command Center stats (§27 Screen 2) */}
        <View style={styles.statGrid}>
          <StatTile
            icon="bar-chart"
            value={DASHBOARD.transactionsAnalyzed.toLocaleString()}
            label="Transactions analyzed"
            delta="+12%"
          />
          <StatTile
            icon="folder-open"
            value={DASHBOARD.openCases}
            label="Open risk cases"
            accent={colors.accent}
            delta="+2"
          />
        </View>
        <View style={styles.statGrid}>
          <StatTile
            icon="exclamation-triangle"
            value={DASHBOARD.criticalCases}
            label="Critical cases"
            accent={colors.critical}
          />
          <StatTile
            icon="clock-o"
            value={DASHBOARD.pendingReviews}
            label="Pending reviews"
            accent={colors.medium}
          />
        </View>

        {/* Flagged trend chart */}
        <Card style={styles.block}>
          <SectionTitle
            right={<Text style={styles.tagMuted}>This week</Text>}>
            Flagged transactions
          </SectionTitle>
          <MiniBarChart data={FLAGGED_TREND} color={colors.accent} />
          <View style={styles.legendRow}>
            <View style={styles.legendItem}>
              <View style={[styles.legendDot, { backgroundColor: colors.low }]} />
              <Text style={styles.legendText}>
                Cleared today: {DASHBOARD.clearedToday}
              </Text>
            </View>
            <View style={styles.legendItem}>
              <View style={[styles.legendDot, { backgroundColor: colors.primary }]} />
              <Text style={styles.legendText}>
                False-positive rate: {DASHBOARD.falsePositiveRate}%
              </Text>
            </View>
          </View>
        </Card>

        {/* Per-user risk & safer workflow */}
        <SectionTitle
          right={
            <TouchableOpacity onPress={onOpenQueue}>
              <Text style={styles.link}>View queue</Text>
            </TouchableOpacity>
          }>
          Customer risk & safer workflow
        </SectionTitle>

        {CASES.map(c => (
          <CustomerRiskCard key={c.id} data={c} onPress={() => onOpenCase(c.id)} />
        ))}

        <View style={{ height: spacing.xxl }} />
      </ScrollView>
    </SafeAreaView>
  );
}

function CustomerRiskCard({
  data,
  onPress,
}: {
  data: RiskCase;
  onPress: () => void;
}) {
  const band = riskBand(data.currentRisk);
  const nextStep = data.saferWorkflow[0];
  return (
    <TouchableOpacity activeOpacity={0.9} onPress={onPress}>
      <Card style={styles.custCard}>
        <View style={styles.custHead}>
          <View style={[styles.custAvatar, { backgroundColor: band.soft }]}>
            <Text style={[styles.custAvatarText, { color: band.color }]}>
              {data.customerName.charAt(0)}
            </Text>
          </View>
          <View style={{ flex: 1 }}>
            <Text style={styles.custName} numberOfLines={1}>
              {data.customerName}
            </Text>
            <Text style={styles.custMeta}>
              {data.customerType} · {data.business}
            </Text>
          </View>
          <RiskBadge score={data.currentRisk} />
        </View>

        <View style={styles.riskLine}>
          <Text style={styles.riskLineLabel}>Risk score</Text>
          <View style={{ flex: 1, marginHorizontal: spacing.md }}>
            <ProgressBar value={data.currentRisk} color={band.color} />
          </View>
          <Text style={[styles.riskLineValue, { color: band.color }]}>
            {data.currentRisk}
          </Text>
        </View>

        {/* Safer workflow — the recommended next step */}
        <View style={styles.safer}>
          <View style={styles.saferGlyph}>
            <Icon name="compass" set="feather" size={16} color={colors.primaryDark} />
          </View>
          <View style={{ flex: 1 }}>
            <Text style={styles.saferTitle}>Safer workflow</Text>
            <Text style={styles.saferText} numberOfLines={2}>
              {nextStep}
            </Text>
          </View>
          <Icon name="angle-right" size={20} color={colors.textFaint} style={styles.chevron} />
        </View>
      </Card>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.bg },
  content: { padding: spacing.lg, paddingBottom: spacing.xxl },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.lg,
  },
  avatar: {
    width: 44,
    height: 44,
    borderRadius: 14,
    backgroundColor: colors.primary,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: spacing.md,
  },
  avatarText: { color: colors.onPrimary, fontSize: font.h3, fontWeight: '800' },
  welcome: { color: colors.textMuted, fontSize: font.small },
  userName: { color: colors.text, fontSize: font.h3, fontWeight: '800' },
  logout: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.md,
    paddingVertical: 6,
    borderRadius: radius.pill,
    backgroundColor: colors.surface,
    ...shadow.card,
  },
  logoutIcon: { marginRight: 6 },
  logoutText: { color: colors.textMuted, fontSize: font.small, fontWeight: '600' },
  hero: {
    backgroundColor: colors.accent,
    borderRadius: radius.lg,
    padding: spacing.lg,
    marginBottom: spacing.lg,
    ...shadow.floating,
  },
  heroLabel: { color: 'rgba(255,255,255,0.9)', fontSize: font.small, fontWeight: '600' },
  heroRow: { flexDirection: 'row', alignItems: 'flex-end', marginVertical: spacing.sm },
  heroValue: { color: colors.onPrimary, fontSize: 44, fontWeight: '900', lineHeight: 46 },
  heroOutOf: { color: 'rgba(255,255,255,0.85)', fontSize: font.h3, fontWeight: '700', marginBottom: 6 },
  heroFooter: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginTop: spacing.md,
  },
  heroFootText: { color: colors.onPrimary, fontSize: font.small, fontWeight: '600' },
  heroTag: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.22)',
    paddingHorizontal: spacing.md,
    paddingVertical: 4,
    borderRadius: radius.pill,
  },
  onlineDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: colors.onPrimary,
    marginRight: 6,
  },
  heroTagText: { color: colors.onPrimary, fontSize: font.tiny, fontWeight: '700' },
  statGrid: { flexDirection: 'row', gap: spacing.md, marginBottom: spacing.md },
  block: { marginTop: spacing.sm, marginBottom: spacing.lg },
  tagMuted: { color: colors.textFaint, fontSize: font.small, fontWeight: '600' },
  legendRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: spacing.md,
  },
  legendItem: { flexDirection: 'row', alignItems: 'center' },
  legendDot: { width: 8, height: 8, borderRadius: 4, marginRight: 6 },
  legendText: { fontSize: font.tiny, color: colors.textMuted },
  link: { color: colors.primary, fontSize: font.small, fontWeight: '700' },
  custCard: { marginBottom: spacing.md },
  custHead: { flexDirection: 'row', alignItems: 'center' },
  custAvatar: {
    width: 42,
    height: 42,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: spacing.md,
  },
  custAvatarText: { fontSize: font.h3, fontWeight: '800' },
  custName: { fontSize: font.body, fontWeight: '700', color: colors.text },
  custMeta: { fontSize: font.small, color: colors.textMuted, marginTop: 1 },
  riskLine: { flexDirection: 'row', alignItems: 'center', marginTop: spacing.lg },
  riskLineLabel: { fontSize: font.tiny, color: colors.textFaint, width: 58 },
  riskLineValue: { fontSize: font.body, fontWeight: '800', width: 30, textAlign: 'right' },
  safer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.surfaceAlt,
    borderRadius: radius.md,
    padding: spacing.md,
    marginTop: spacing.md,
  },
  saferGlyph: {
    width: 34,
    height: 34,
    borderRadius: 10,
    backgroundColor: colors.primarySoft,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: spacing.md,
  },
  saferTitle: { fontSize: font.tiny, color: colors.primaryDark, fontWeight: '800', letterSpacing: 0.3 },
  saferText: { fontSize: font.small, color: colors.text, marginTop: 2, lineHeight: 18 },
  chevron: { marginLeft: spacing.sm },
});
