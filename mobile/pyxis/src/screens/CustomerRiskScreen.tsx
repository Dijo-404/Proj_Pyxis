import React from 'react';
import { ScrollView, StyleSheet, Text, TouchableOpacity, View, ImageBackground } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import {
  Card,
  ProgressBar,
  RiskBadge,
  SectionTitle,
} from '../components/ui';
import Icon from '../components/Icon';
import { font, radius, spacing } from '../theme';
import { RiskCase } from '../types';
import { useWorkspace } from '../workspace';

function getRiskColor(risk: number): string {
  if (risk >= 80) return '#000000ff';
  if (risk >= 50) return '#000000ff';
  return '#000000ff';
}

export default function CustomerRiskScreen({
  onOpenCase,
}: {
  onOpenCase: (id: string) => void;
}) {
  const { data } = useWorkspace();
  const cases = data?.cases ?? [];
  return (
    <ImageBackground
      source={require('../../assets/risk.jpg')}
      style={styles.backgroundImage}
      blurRadius={6}>
      <View style={styles.overlay}>
        <SafeAreaView style={styles.root} edges={['top']}>
          <View style={styles.header}>
            <Text style={styles.headerTitle}>Customer Risk</Text>
          </View>
          <ScrollView
            contentContainerStyle={styles.content}
            showsVerticalScrollIndicator={false}>
        <SectionTitle>Customer risk & safer workflow</SectionTitle>

        {cases.map(c => (
          <CustomerRiskCard key={c.id} data={c} onPress={() => onOpenCase(c.id)} />
        ))}

        <View style={{ height: spacing.xxl }} />
      </ScrollView>
        </SafeAreaView>
      </View>
    </ImageBackground>
  );
}

function CustomerRiskCard({
  data,
  onPress,
}: {
  data: RiskCase;
  onPress: () => void;
}) {
  const nextStep = data.saferWorkflow[0];
  return (
    <TouchableOpacity activeOpacity={0.9} onPress={onPress}>
      <Card style={styles.custCard}>
        <View style={styles.custHead}>
          <View style={[styles.custAvatar, { backgroundColor: '#1A1A1A' }]}>
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
            <Icon name="compass" set="feather" size={16} color="white" />
          </View>
          <View style={{ flex: 1 }}>
            <Text style={styles.saferTitle}>Safer workflow</Text>
            <Text style={styles.saferText} numberOfLines={2}>
              {nextStep}
            </Text>
          </View>
          <Icon name="angle-right" size={20} color="white" style={styles.chevron} />
        </View>
      </Card>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  backgroundImage: { flex: 1 },
  overlay: { flex: 1, backgroundColor: 'rgba(255, 255, 255, 0)' },
  root: { flex: 1, },
  header: {
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: font.h3,
    fontWeight: '800',
    color: '#FFFFFF',
  },
  content: { padding: spacing.lg, paddingBottom: spacing.xxl },
  sectionTitle: { fontSize: font.h3, fontWeight: '700', color: '#FFFFFF' },
  custCard: {
    marginBottom: spacing.md,
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: spacing.lg,
    borderWidth: 1.5,
    borderColor: '#F0F0F0',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.1,
    shadowRadius: 16,
    elevation: 3,
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
    backgroundColor: '#F5F5F5',
    borderRadius: radius.md,
    padding: spacing.md,
    marginTop: spacing.md,
    borderWidth: 1,
    borderColor: '#EEEEEE',
  },
  saferGlyph: {
    width: 34,
    height: 34,
    borderRadius: 10,
    backgroundColor: '#363636ff',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: spacing.md,
  },
  saferTitle: { fontSize: font.tiny, color: '#000000', fontWeight: '800', letterSpacing: 0.3 },
  saferText: { fontSize: font.small, color: '#000000ff', marginTop: 2, lineHeight: 18 },
  chevron: { marginLeft: spacing.sm, color: '#999999' },
});
