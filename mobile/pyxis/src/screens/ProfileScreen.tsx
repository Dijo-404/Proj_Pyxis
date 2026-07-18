import React from 'react';
import { ScrollView, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useAuth } from '../auth';
import { Card, Divider } from '../components/ui';
import Icon from '../components/Icon';
import { colors, font, radius, shadow, spacing } from '../theme';

export default function ProfileScreen() {
  const { user, signOut } = useAuth();

  return (
    <SafeAreaView style={styles.root} edges={['top']}>
      <ScrollView
        contentContainerStyle={styles.content}
        showsVerticalScrollIndicator={false}>
        {/* Profile header */}
        <View style={styles.profileHeader}>
          <View style={styles.avatar}>
            <Text style={styles.avatarText}>
              {user?.name.charAt(0) ?? 'P'}
            </Text>
          </View>
          <View style={{ flex: 1, marginLeft: spacing.lg }}>
            <Text style={styles.name}>{user?.name}</Text>
            <Text style={styles.role}>{user?.role}</Text>
            <Text style={styles.email}>{user?.email}</Text>
          </View>
        </View>

        {/* User info section */}
        <Card style={styles.section}>
          <Text style={styles.sectionTitle}>User Information</Text>
          <Divider />
          <View style={styles.infoRow}>
            <Text style={styles.label}>Officer ID</Text>
            <Text style={styles.value}>{user?.id}</Text>
          </View>
          <View style={styles.infoRow}>
            <Text style={styles.label}>Role</Text>
            <Text style={styles.value}>{user?.role}</Text>
          </View>
          <View style={styles.infoRow}>
            <Text style={styles.label}>Email</Text>
            <Text style={styles.value}>{user?.email}</Text>
          </View>
        </Card>

        {/* Preferences section */}
        <Card style={styles.section}>
          <Text style={styles.sectionTitle}>Preferences</Text>
          <Divider />
          <TouchableOpacity style={styles.prefRow}>
            <View style={styles.prefIcon}>
              <Icon name="bell" size={16} color={colors.primary} />
            </View>
            <Text style={styles.prefText}>Notifications</Text>
            <Icon name="angle-right" size={16} color={colors.textFaint} />
          </TouchableOpacity>
          <TouchableOpacity style={styles.prefRow}>
            <View style={styles.prefIcon}>
              <Icon name="shield" size={16} color={colors.primary} />
            </View>
            <Text style={styles.prefText}>Security</Text>
            <Icon name="angle-right" size={16} color={colors.textFaint} />
          </TouchableOpacity>
          <TouchableOpacity style={styles.prefRow}>
            <View style={styles.prefIcon}>
              <Icon name="sliders" size={16} color={colors.primary} />
            </View>
            <Text style={styles.prefText}>Settings</Text>
            <Icon name="angle-right" size={16} color={colors.textFaint} />
          </TouchableOpacity>
        </Card>

        {/* Logout button */}
        <TouchableOpacity
          style={styles.logoutBtn}
          activeOpacity={0.8}
          onPress={signOut}>
          <Icon name="sign-out" size={16} color={colors.critical} style={styles.logoutIcon} />
          <Text style={styles.logoutText}>Sign Out</Text>
        </TouchableOpacity>

        <View style={{ height: spacing.xxl }} />
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.bg },
  content: { padding: spacing.lg, paddingBottom: spacing.xxl },
  profileHeader: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: spacing.xl,
  },
  avatar: {
    width: 70,
    height: 70,
    borderRadius: 20,
    backgroundColor: colors.primary,
    alignItems: 'center',
    justifyContent: 'center',
    ...shadow.card,
  },
  avatarText: {
    color: colors.onPrimary,
    fontSize: font.h1,
    fontWeight: '900',
  },
  name: {
    fontSize: font.h2,
    fontWeight: '800',
    color: colors.text,
  },
  role: {
    fontSize: font.small,
    color: colors.textMuted,
    marginTop: spacing.xs,
  },
  email: {
    fontSize: font.tiny,
    color: colors.textFaint,
    marginTop: spacing.xs,
  },
  section: {
    marginBottom: spacing.lg,
    padding: spacing.lg,
  },
  sectionTitle: {
    fontSize: font.h3,
    fontWeight: '700',
    color: colors.text,
    marginBottom: spacing.sm,
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: spacing.md,
  },
  label: {
    fontSize: font.small,
    color: colors.textMuted,
  },
  value: {
    fontSize: font.small,
    fontWeight: '600',
    color: colors.text,
  },
  prefRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: spacing.md,
  },
  prefIcon: {
    width: 36,
    height: 36,
    borderRadius: 10,
    backgroundColor: colors.primarySoft,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: spacing.md,
  },
  prefText: {
    flex: 1,
    fontSize: font.body,
    fontWeight: '600',
    color: colors.text,
  },
  logoutBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: spacing.lg,
    paddingHorizontal: spacing.lg,
    backgroundColor: 'rgba(255,0,0,0.08)',
    borderRadius: radius.md,
    borderWidth: 1.5,
    borderColor: colors.critical + '30',
  },
  logoutIcon: {
    marginRight: spacing.sm,
  },
  logoutText: {
    fontSize: font.body,
    fontWeight: '700',
    color: colors.critical,
  },
});
