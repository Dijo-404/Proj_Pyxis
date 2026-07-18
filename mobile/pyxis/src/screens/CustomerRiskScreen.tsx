import React from 'react';
import { ScrollView, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import ScreenHeader from '../components/ScreenHeader';
import {
  Card,
  ProgressBar,
  RiskBadge,
  SectionTitle,
} from '../components/ui';
import Icon from '../components/Icon';
import { CASES } from '../mockData';
import { colors, font, radius, riskBand, spacing } from '../theme';
import { RiskCase } from '../types';

export default function CustomerRiskScreen({
  onOpenCase,
}: {
  onOpenCase: (id: string) => void;
}) {
  return (
    <SafeAreaView style={styles.root} edges={['top']}>
      <ScreenHeader title="Customer Risk" />
      <ScrollView
        contentContainerStyle={styles.content}
        showsVerticalScrollIndicator={false}>
        <SectionTitle>Customer risk & safer workflow</SectionTitle>

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
  sectionTitle: { fontSize: font.h3, fontWeight: '700', color: colors.text },
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
