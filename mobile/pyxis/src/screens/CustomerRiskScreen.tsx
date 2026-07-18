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

function getRiskColor(risk: number): string {
  if (risk >= 80) return '#FF0000';
  if (risk >= 50) return '#FFA500';
  return '#00FF00';
}

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
          <View style={[styles.custAvatar, { backgroundColor: '#000000' }]}>
            <Text style={[styles.custAvatarText, { color: '#FFFFFF' }]}>
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
            <ProgressBar value={data.currentRisk} color={getRiskColor(data.currentRisk)} />
          </View>
          <Text style={[styles.riskLineValue, { color: getRiskColor(data.currentRisk) }]}>
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
  root: { flex: 1, backgroundColor: '#000000' },
  content: { padding: spacing.lg, paddingBottom: spacing.xxl },
  sectionTitle: { fontSize: font.h3, fontWeight: '700', color: '#FFFFFF' },
  custCard: {
    marginBottom: spacing.md,
    backgroundColor: 'rgba(255, 255, 255, 0.72)',
    borderRadius: 16,
    borderWidth: 1.5,
    borderColor: 'rgba(255, 255, 255, 0.6)',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.18,
    shadowRadius: 20,
    elevation: 14,
    overflow: 'hidden',
  },
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
  custName: { fontSize: font.body, fontWeight: '700', color: '#000000' },
  custMeta: { fontSize: font.small, color: '#666666', marginTop: 1 },
  riskLine: { flexDirection: 'row', alignItems: 'center', marginTop: spacing.lg },
  riskLineLabel: { fontSize: font.tiny, color: '#666666', width: 58 },
  riskLineValue: { fontSize: font.body, fontWeight: '800', width: 30, textAlign: 'right' },
  safer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.05)',
    borderRadius: radius.md,
    padding: spacing.md,
    marginTop: spacing.md,
    borderWidth: 1,
    borderColor: 'rgba(0, 0, 0, 0.1)',
  },
  saferGlyph: {
    width: 34,
    height: 34,
    borderRadius: 10,
    backgroundColor: 'rgba(0, 0, 0, 0.08)',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: spacing.md,
  },
  saferTitle: { fontSize: font.tiny, color: '#000000', fontWeight: '800', letterSpacing: 0.3 },
  saferText: { fontSize: font.small, color: '#000000', marginTop: 2, lineHeight: 18 },
  chevron: { marginLeft: spacing.sm, color: '#000000' },
});
