import React, { useRef, useState } from 'react';
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
import ScreenHeader from '../components/ScreenHeader';
import Icon from '../components/Icon';
import { askGemma } from '../api';
import { useAuth } from '../auth';
import { colors, font, radius, spacing } from '../theme';
import { useWorkspace } from '../workspace';

interface Msg {
  role: 'user' | 'gemma';
  text: string;
}

const SUGGESTIONS = [
  'Why is this case high risk?',
  'What evidence supports layering?',
  'What supports a legitimate explanation?',
  'What information can change this decision?',
  'Summarize the case for a senior reviewer.',
];

export default function AskGemmaScreen({
  caseId,
  onBack,
}: {
  caseId: string;
  onBack: () => void;
}) {
  const { data: workspace } = useWorkspace();
  const { user } = useAuth();
  const data = workspace?.cases.find(item => item.id === caseId);
  const [messages, setMessages] = useState<Msg[]>([
    {
      role: 'gemma',
      text: `I'm analyzing ${data?.customerName ?? 'this case'} locally. Ask me anything about the evidence, scenarios, or the decision-critical question. All reasoning runs on the on-premise Gemma runtime.`,
    },
  ]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const scrollRef = useRef<ScrollView>(null);

  const send = async (text: string) => {
    const q = text.trim();
    if (!q || sending) return;
    setMessages(m => [...m, { role: 'user', text: q }]);
    setInput('');
    setSending(true);
    try {
      const response = await askGemma(caseId, user?.id ?? 'LOCAL-REVIEWER', q);
      setMessages(m => [...m, { role: 'gemma', text: response }]);
    } catch (requestError) {
      setMessages(m => [
        ...m,
        {
          role: 'gemma',
          text: requestError instanceof Error
            ? `Local model error: ${requestError.message}`
            : 'The local model could not answer this question.',
        },
      ]);
    } finally {
      setSending(false);
      requestAnimationFrame(() => scrollRef.current?.scrollToEnd({ animated: true }));
    }
  };

  return (
    <SafeAreaView style={styles.root} edges={['top']}>
      <ScreenHeader
        title="Ask Gemma"
        subtitle={data ? `${data.id} · local runtime` : undefined}
        onBack={onBack}
      />
      <KeyboardAvoidingView
        style={{ flex: 1 }}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        keyboardVerticalOffset={8}>
        <ScrollView
          ref={scrollRef}
          contentContainerStyle={styles.chat}
          showsVerticalScrollIndicator={false}>
          {messages.map((m, i) => (
            <View
              key={i}
              style={[styles.bubbleRow, m.role === 'user' ? styles.rowRight : styles.rowLeft]}>
              {m.role === 'gemma' && (
                <View style={styles.gemmaAvatar}>
                  <Icon name="magic" size={14} color={colors.onPrimary} />
                </View>
              )}
              <View style={[styles.bubble, m.role === 'user' ? styles.userBubble : styles.gemmaBubble]}>
                <Text style={[styles.bubbleText, m.role === 'user' && styles.userText]}>{m.text}</Text>
              </View>
            </View>
          ))}

          {messages.length <= 1 && (
            <View style={styles.suggestions}>
              {SUGGESTIONS.map(s => (
                <TouchableOpacity key={s} style={styles.suggestChip} onPress={() => send(s)}>
                  <Text style={styles.suggestText}>{s}</Text>
                </TouchableOpacity>
              ))}
            </View>
          )}
        </ScrollView>

        <View style={styles.inputBar}>
          <TextInput
            style={styles.input}
            placeholder="Ask about this case…"
            placeholderTextColor={colors.textFaint}
            value={input}
            onChangeText={setInput}
            onSubmitEditing={() => send(input)}
            returnKeyType="send"
          />
          <TouchableOpacity
            style={[styles.sendBtn, sending && styles.sendBtnDisabled]}
            disabled={sending}
            onPress={() => send(input)}>
            <Icon name="paper-plane" size={16} color={colors.onPrimary} />
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.bg },
  chat: { padding: spacing.lg, paddingBottom: spacing.xl },
  bubbleRow: { flexDirection: 'row', marginBottom: spacing.md, alignItems: 'flex-end' },
  rowLeft: { justifyContent: 'flex-start' },
  rowRight: { justifyContent: 'flex-end' },
  gemmaAvatar: {
    width: 30,
    height: 30,
    borderRadius: 9,
    backgroundColor: colors.primary,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: spacing.sm,
  },
  bubble: { maxWidth: '80%', borderRadius: radius.lg, padding: spacing.md },
  gemmaBubble: { backgroundColor: colors.surface, borderTopLeftRadius: 4 },
  userBubble: { backgroundColor: colors.primary, borderTopRightRadius: 4 },
  bubbleText: { fontSize: font.small, color: colors.text, lineHeight: 20 },
  userText: { color: colors.onPrimary },
  suggestions: { marginTop: spacing.md, gap: spacing.sm },
  suggestChip: {
    backgroundColor: colors.surface,
    borderRadius: radius.md,
    padding: spacing.md,
    borderWidth: 1,
    borderColor: colors.border,
  },
  suggestText: { fontSize: font.small, color: colors.primaryDark, fontWeight: '600' },
  inputBar: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing.md,
    backgroundColor: colors.surface,
    borderTopWidth: 1,
    borderTopColor: colors.border,
    gap: spacing.sm,
  },
  input: {
    flex: 1,
    backgroundColor: colors.bg,
    borderRadius: radius.pill,
    paddingHorizontal: spacing.lg,
    height: 46,
    fontSize: font.body,
    color: colors.text,
  },
  sendBtn: {
    width: 46,
    height: 46,
    borderRadius: 23,
    backgroundColor: colors.primary,
    alignItems: 'center',
    justifyContent: 'center',
  },
  sendBtnDisabled: { opacity: 0.5 },
});
