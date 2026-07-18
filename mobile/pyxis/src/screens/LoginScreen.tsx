import React, { useState } from 'react';
import {
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useAuth } from '../auth';
import Icon from '../components/Icon';
import { PrimaryButton } from '../components/ui';
import { colors, font, radius, spacing } from '../theme';

export default function LoginScreen() {
  const { signIn } = useAuth();
  const [email, setEmail] = useState('prie@gmail.com');
  const [password, setPassword] = useState('123456');
  const [remember, setRemember] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const onLogin = () => {
    setError(null);
    setLoading(true);
    // brief delay to feel like a request
    setTimeout(() => {
      const res = signIn(email, password);
      setLoading(false);
      if (!res.ok) setError(res.error ?? 'Login failed');
    }, 350);
  };

  return (
    <View style={styles.root}>
      {/* Teal hero */}
      <View style={styles.hero}>
        <SafeAreaView edges={['top']}>
          <View style={styles.brandRow}>
            <View style={styles.logoMark}>
              <Icon name="compass" set="feather" size={20} color={colors.onPrimary} />
            </View>
            <Text style={styles.brand}>PYXIS</Text>
          </View>
          <Text style={styles.heroTitle}>Log in to stay on{'\n'}top of your risk cases.</Text>
          <Text style={styles.heroSub}>
            Private, on-premise financial compliance intelligence powered by Gemma.
          </Text>
        </SafeAreaView>
      </View>

      {/* Login sheet */}
      <KeyboardAvoidingView
        style={styles.sheetWrap}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
        <ScrollView
          contentContainerStyle={styles.sheet}
          keyboardShouldPersistTaps="handled"
          showsVerticalScrollIndicator={false}>
          <Text style={styles.sheetTitle}>Login</Text>
          <View style={styles.signupRow}>
            <Text style={styles.muted}>Compliance officer access</Text>
          </View>

          <Field
            icon="envelope-o"
            placeholder="Email address"
            value={email}
            onChangeText={setEmail}
            autoCapitalize="none"
            keyboardType="email-address"
          />
          <Field
            icon="lock"
            placeholder="Password"
            value={password}
            onChangeText={setPassword}
            secureTextEntry
          />

          <View style={styles.rowBetween}>
            <TouchableOpacity
              style={styles.rememberRow}
              activeOpacity={0.7}
              onPress={() => setRemember(r => !r)}>
              <View style={[styles.checkbox, remember && styles.checkboxOn]}>
                {remember ? <Icon name="check" size={12} color={colors.onPrimary} /> : null}
              </View>
              <Text style={styles.muted}>Remember Me</Text>
            </TouchableOpacity>
            <Text style={styles.link}>Forgot Password?</Text>
          </View>

          {error ? <Text style={styles.error}>{error}</Text> : null}

          <PrimaryButton
            title="Login"
            onPress={onLogin}
            loading={loading}
            style={styles.loginBtn}
          />

          <View style={styles.hintBox}>
            <Text style={styles.hintText}>
              Demo credentials · prie@gmail.com / 123456
            </Text>
          </View>

          <View style={styles.privacyRow}>
            <Icon name="shield" size={15} color={colors.textFaint} style={styles.privacyGlyph} />
            <Text style={styles.privacyText}>
              No customer data leaves this device — all reasoning runs on the local Gemma runtime.
            </Text>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </View>
  );
}

function Field({
  icon,
  ...props
}: { icon: string } & React.ComponentProps<typeof TextInput>) {
  return (
    <View style={styles.field}>
      <Icon name={icon} size={16} color={colors.textFaint} style={styles.fieldIcon} />
      <TextInput
        placeholderTextColor={colors.textFaint}
        style={styles.input}
        {...props}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.primary },
  hero: {
    paddingHorizontal: spacing.xl,
    paddingBottom: spacing.xxl,
    backgroundColor: colors.primary,
  },
  brandRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: spacing.lg,
    marginBottom: spacing.xl,
  },
  logoMark: {
    width: 34,
    height: 34,
    borderRadius: 10,
    backgroundColor: 'rgba(255,255,255,0.2)',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: spacing.sm,
  },
  brand: { color: colors.onPrimary, fontSize: font.h3, fontWeight: '900', letterSpacing: 2 },
  heroTitle: {
    color: colors.onPrimary,
    fontSize: font.h1,
    fontWeight: '800',
    lineHeight: 34,
  },
  heroSub: {
    color: 'rgba(255,255,255,0.85)',
    fontSize: font.small,
    marginTop: spacing.md,
    lineHeight: 20,
  },
  sheetWrap: { flex: 1 },
  sheet: {
    backgroundColor: colors.surface,
    borderTopLeftRadius: radius.xl,
    borderTopRightRadius: radius.xl,
    padding: spacing.xl,
    paddingTop: spacing.xxl,
    flexGrow: 1,
    marginTop: -spacing.xl,
  },
  sheetTitle: { fontSize: font.h1, fontWeight: '800', color: colors.text, textAlign: 'center' },
  signupRow: { alignItems: 'center', marginTop: spacing.xs, marginBottom: spacing.xl },
  muted: { color: colors.textMuted, fontSize: font.small },
  field: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.bg,
    borderRadius: radius.md,
    paddingHorizontal: spacing.lg,
    height: 54,
    marginBottom: spacing.md,
    borderWidth: 1,
    borderColor: colors.border,
  },
  fieldIcon: { marginRight: spacing.md },
  input: { flex: 1, fontSize: font.body, color: colors.text },
  rowBetween: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginVertical: spacing.sm,
  },
  rememberRow: { flexDirection: 'row', alignItems: 'center' },
  checkbox: {
    width: 20,
    height: 20,
    borderRadius: 6,
    borderWidth: 1.5,
    borderColor: colors.border,
    marginRight: spacing.sm,
    alignItems: 'center',
    justifyContent: 'center',
  },
  checkboxOn: { backgroundColor: colors.primary, borderColor: colors.primary },
  link: { color: colors.primary, fontSize: font.small, fontWeight: '700' },
  error: {
    color: colors.critical,
    fontSize: font.small,
    marginTop: spacing.sm,
    marginBottom: spacing.xs,
  },
  loginBtn: { marginTop: spacing.lg },
  hintBox: {
    marginTop: spacing.lg,
    backgroundColor: colors.primarySoft,
    borderRadius: radius.md,
    padding: spacing.md,
    alignItems: 'center',
  },
  hintText: { color: colors.primaryDark, fontSize: font.small, fontWeight: '600' },
  privacyRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: spacing.xl,
    paddingHorizontal: spacing.xs,
  },
  privacyGlyph: { marginRight: spacing.sm },
  privacyText: { flex: 1, color: colors.textFaint, fontSize: font.tiny, lineHeight: 16 },
});
