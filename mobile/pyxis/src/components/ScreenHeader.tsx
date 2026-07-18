import React from 'react';
import { StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { colors, font, shadow, spacing } from '../theme';

export default function ScreenHeader({
  title,
  subtitle,
  onBack,
  right,
}: {
  title: string;
  subtitle?: string;
  onBack?: () => void;
  right?: React.ReactNode;
}) {
  return (
    <View style={styles.wrap}>
      {onBack ? (
        <TouchableOpacity style={styles.back} onPress={onBack} activeOpacity={0.7}>
          <Text style={styles.backGlyph}>‹</Text>
        </TouchableOpacity>
      ) : (
        <View style={styles.back} />
      )}
      <View style={styles.center}>
        <Text style={styles.title} numberOfLines={1}>
          {title}
        </Text>
        {subtitle ? <Text style={styles.subtitle}>{subtitle}</Text> : null}
      </View>
      <View style={styles.right}>{right}</View>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
  },
  back: {
    width: 40,
    height: 40,
    borderRadius: 12,
    backgroundColor: colors.surface,
    alignItems: 'center',
    justifyContent: 'center',
    ...shadow.card,
  },
  backGlyph: { fontSize: 28, color: colors.text, marginTop: -3 },
  center: { flex: 1, alignItems: 'center', paddingHorizontal: spacing.sm },
  title: { fontSize: font.h3, fontWeight: '800', color: colors.text },
  subtitle: { fontSize: font.tiny, color: colors.textMuted, marginTop: 1 },
  right: { width: 40, alignItems: 'flex-end' },
});
