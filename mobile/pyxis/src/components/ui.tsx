/** Reusable UI primitives for the Pyxis prototype. */

import React from 'react';
import {
  ActivityIndicator,
  StyleProp,
  StyleSheet,
  Text,
  TextStyle,
  TouchableOpacity,
  View,
  ViewStyle,
} from 'react-native';
import { colors, font, radius, riskBand, shadow, spacing } from '../theme';
import Icon from './Icon';

/* ---------- Card ---------- */
export function Card({
  children,
  style,
  padded = true,
}: {
  children: React.ReactNode;
  style?: StyleProp<ViewStyle>;
  padded?: boolean;
}) {
  return (
    <View style={[styles.card, padded && styles.cardPad, style]}>{children}</View>
  );
}

/* ---------- Section heading ---------- */
export function SectionTitle({
  children,
  right,
}: {
  children: React.ReactNode;
  right?: React.ReactNode;
}) {
  return (
    <View style={styles.sectionRow}>
      <Text style={styles.sectionTitle}>{children}</Text>
      {right}
    </View>
  );
}

/* ---------- Pill / tag ---------- */
export function Pill({
  label,
  color,
  soft,
}: {
  label: string;
  color: string;
  soft: string;
}) {
  return (
    <View style={[styles.pill, { backgroundColor: soft }]}>
      <Text style={[styles.pillText, { color }]}>{label}</Text>
    </View>
  );
}

/* ---------- Risk badge (derives band from score) ---------- */
export function RiskBadge({ score }: { score: number }) {
  const band = riskBand(score);
  return (
    <View style={[styles.riskBadge, { backgroundColor: band.soft }]}>
      <View style={[styles.riskDot, { backgroundColor: band.color }]} />
      <Text style={[styles.riskText, { color: band.color }]}>
        {band.label} · {score}
      </Text>
    </View>
  );
}

/* ---------- Horizontal progress / match bar ---------- */
export function ProgressBar({
  value, // 0-100
  color = colors.primary,
  track = colors.divider,
  height = 8,
}: {
  value: number;
  color?: string;
  track?: string;
  height?: number;
}) {
  const clamped = Math.max(0, Math.min(100, value));
  return (
    <View style={[styles.track, { height, borderRadius: height, backgroundColor: track }]}>
      <View
        style={{
          width: `${clamped}%`,
          height,
          borderRadius: height,
          backgroundColor: color,
        }}
      />
    </View>
  );
}

/* ---------- Buttons ---------- */
export function PrimaryButton({
  title,
  onPress,
  loading,
  disabled,
  style,
  variant = 'solid',
  color = colors.primary,
  icon,
  iconSet = 'fa',
}: {
  title: string;
  onPress: () => void;
  loading?: boolean;
  disabled?: boolean;
  style?: StyleProp<ViewStyle>;
  variant?: 'solid' | 'outline';
  color?: string;
  icon?: string;
  iconSet?: 'fa' | 'feather';
}) {
  const isOutline = variant === 'outline';
  const fg = isOutline ? color : colors.onPrimary;
  return (
    <TouchableOpacity
      activeOpacity={0.85}
      onPress={onPress}
      disabled={disabled || loading}
      style={[
        styles.btn,
        isOutline
          ? { backgroundColor: 'transparent', borderWidth: 1.5, borderColor: color }
          : { backgroundColor: color },
        (disabled || loading) && { opacity: 0.6 },
        style,
      ]}>
      {loading ? (
        <ActivityIndicator color={fg} />
      ) : (
        <View style={styles.btnRow}>
          {icon ? <Icon name={icon} set={iconSet} size={16} color={fg} style={styles.btnIcon} /> : null}
          <Text style={[styles.btnText, { color: fg }]}>{title}</Text>
        </View>
      )}
    </TouchableOpacity>
  );
}

/* ---------- Key/value stat tile ---------- */
export function StatTile({
  value,
  label,
  delta,
  accent = colors.primary,
  icon,
}: {
  value: string | number;
  label: string;
  delta?: string;
  accent?: string;
  icon?: string;
}) {
  return (
    <Card style={styles.stat}>
      <View style={styles.statTop}>
        {icon ? (
          <View style={[styles.statIcon, { backgroundColor: accent + '1A' }]}>
            <Icon name={icon} size={15} color={accent} />
          </View>
        ) : (
          <View />
        )}
        {delta ? (
          <Text style={[styles.statDelta, { color: accent }]}>{delta}</Text>
        ) : null}
      </View>
      <Text style={[styles.statValue, { color: colors.text }]}>{value}</Text>
      <Text style={styles.statLabel}>{label}</Text>
    </Card>
  );
}

/* ---------- Simple bar chart (no external deps) ---------- */
export function MiniBarChart({
  data,
  color = colors.primary,
  height = 120,
}: {
  data: { label: string; value: number }[];
  color?: string;
  height?: number;
}) {
  const max = Math.max(...data.map(d => d.value), 1);
  return (
    <View style={[styles.chart, { height }]}>
      {data.map(d => (
        <View key={d.label} style={styles.chartCol}>
          <View style={styles.chartBarWrap}>
            <View
              style={{
                width: 14,
                height: Math.max(6, (d.value / max) * (height - 34)),
                borderRadius: 7,
                backgroundColor: color,
              }}
            />
          </View>
          <Text style={styles.chartLabel}>{d.label}</Text>
        </View>
      ))}
    </View>
  );
}

/* ---------- Divider ---------- */
export function Divider({ style }: { style?: StyleProp<ViewStyle> }) {
  return <View style={[styles.divider, style]} />;
}

/* ---------- Labeled row ---------- */
export function LabelValue({
  label,
  value,
  valueStyle,
}: {
  label: string;
  value: string;
  valueStyle?: StyleProp<TextStyle>;
}) {
  return (
    <View style={styles.lv}>
      <Text style={styles.lvLabel}>{label}</Text>
      <Text style={[styles.lvValue, valueStyle]} numberOfLines={1}>
        {value}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.surface,
    borderRadius: radius.lg,
    ...shadow.card,
  },
  cardPad: { padding: spacing.lg },
  sectionRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: spacing.md,
  },
  sectionTitle: { fontSize: font.h3, fontWeight: '700', color: colors.text },
  pill: {
    paddingHorizontal: spacing.md,
    paddingVertical: 5,
    borderRadius: radius.pill,
    alignSelf: 'flex-start',
  },
  pillText: { fontSize: font.tiny, fontWeight: '700', letterSpacing: 0.3 },
  riskBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.md,
    paddingVertical: 6,
    borderRadius: radius.pill,
  },
  riskDot: { width: 7, height: 7, borderRadius: 4, marginRight: 6 },
  riskText: { fontSize: font.small, fontWeight: '700' },
  track: { width: '100%', overflow: 'hidden' },
  btn: {
    height: 52,
    borderRadius: radius.md,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: spacing.lg,
  },
  btnRow: { flexDirection: 'row', alignItems: 'center' },
  btnIcon: { marginRight: spacing.sm },
  btnText: { fontSize: font.body, fontWeight: '700' },
  stat: { flex: 1, padding: spacing.md },
  statTop: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    minHeight: 20,
  },
  statIcon: {
    width: 30,
    height: 30,
    borderRadius: 9,
    alignItems: 'center',
    justifyContent: 'center',
  },
  statDelta: { fontSize: font.tiny, fontWeight: '700' },
  statValue: { fontSize: font.h2, fontWeight: '800', marginTop: spacing.sm },
  statLabel: { fontSize: font.small, color: colors.textMuted, marginTop: 2 },
  chart: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    justifyContent: 'space-between',
  },
  chartCol: { flex: 1, alignItems: 'center' },
  chartBarWrap: { flex: 1, justifyContent: 'flex-end' },
  chartLabel: { fontSize: font.tiny, color: colors.textFaint, marginTop: 6 },
  divider: { height: 1, backgroundColor: colors.divider, marginVertical: spacing.md },
  lv: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 7,
  },
  lvLabel: { fontSize: font.small, color: colors.textMuted },
  lvValue: { fontSize: font.small, fontWeight: '600', color: colors.text, maxWidth: '55%' },
});
