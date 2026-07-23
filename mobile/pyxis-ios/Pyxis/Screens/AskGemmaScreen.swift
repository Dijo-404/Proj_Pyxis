import SwiftUI
import UIKit

/// Ask Gemma — a native port of `AskGemmaScreen.tsx`. A local-runtime chat over
/// a single case: seeded greeting, suggestion chips, and a send bar wired to
/// `POST /cases/{id}/ask-gemma`. Errors are surfaced inline as a Gemma bubble,
/// matching the RN behavior.
struct AskGemmaScreen: View {
    let caseId: String

    @EnvironmentObject private var workspace: WorkspaceStore
    @EnvironmentObject private var auth: AuthStore
    @Environment(\.apiClient) private var api

    private static let suggestions = [
        "Why is this case high risk?",
        "What evidence supports layering?",
        "What supports a legitimate explanation?",
        "What information can change this decision?",
        "Summarize the case for a senior reviewer."
    ]

    struct Message: Identifiable {
        let id = UUID()
        enum Role { case user, gemma }
        let role: Role
        let text: String
    }

    @State private var messages: [Message] = []
    @State private var input = ""
    @State private var sending = false

    private var riskCase: RiskCase? { workspace.caseBy(id: caseId) }

    var body: some View {
        VStack(spacing: 0) {
            ScrollViewReader { proxy in
                ScrollView(showsIndicators: false) {
                    VStack(alignment: .leading, spacing: Spacing.md) {
                        ForEach(messages) { message in
                            bubble(message)
                        }
                        if messages.count <= 1 {
                            VStack(spacing: Spacing.sm) {
                                ForEach(Self.suggestions, id: \.self) { suggestion in
                                    Button { send(suggestion) } label: {
                                        Text(suggestion)
                                            .font(.system(size: FontSize.small, weight: .semibold))
                                            .foregroundColor(PyxisColor.primaryDark)
                                            .frame(maxWidth: .infinity, alignment: .leading)
                                            .padding(Spacing.md)
                                            .background(PyxisColor.surface)
                                            .clipShape(RoundedRectangle(cornerRadius: Radius.md, style: .continuous))
                                            .overlay(
                                                RoundedRectangle(cornerRadius: Radius.md, style: .continuous)
                                                    .stroke(PyxisColor.border, lineWidth: 1)
                                            )
                                    }
                                    .buttonStyle(.plain)
                                }
                            }
                            .padding(.top, Spacing.md)
                        }
                        Color.clear.frame(height: 1).id("bottom")
                    }
                    .padding(Spacing.lg)
                }
                .onChange(of: messages.count) { _ in
                    withAnimation { proxy.scrollTo("bottom", anchor: .bottom) }
                }
            }

            inputBar
        }
        .background(PyxisColor.bg)
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .principal) {
                NavTitle(title: "Ask Gemma", subtitle: riskCase.map { "\($0.id) · local runtime" })
            }
        }
        .onAppear(perform: seedGreeting)
    }

    private func bubble(_ message: Message) -> some View {
        HStack(alignment: .bottom, spacing: Spacing.sm) {
            if message.role == .gemma {
                Icon(name: "magic", size: 14, color: PyxisColor.onPrimary)
                    .frame(width: 30, height: 30)
                    .background(PyxisColor.primary)
                    .clipShape(RoundedRectangle(cornerRadius: 9, style: .continuous))
                gemmaText(message.text)
                Spacer(minLength: 40)
            } else {
                Spacer(minLength: 40)
                Text(message.text)
                    .font(.system(size: FontSize.small))
                    .foregroundColor(PyxisColor.onPrimary)
                    .padding(Spacing.md)
                    .background(PyxisColor.primary)
                    .clipShape(BubbleShape(isUser: true))
            }
        }
    }

    private func gemmaText(_ text: String) -> some View {
        Text(text)
            .font(.system(size: FontSize.small))
            .foregroundColor(PyxisColor.text)
            .padding(Spacing.md)
            .background(PyxisColor.surface)
            .clipShape(BubbleShape(isUser: false))
    }

    private var inputBar: some View {
        HStack(spacing: Spacing.sm) {
            TextField("Ask about this case…", text: $input)
                .font(.system(size: FontSize.body))
                .foregroundColor(PyxisColor.text)
                .padding(.horizontal, Spacing.lg)
                .frame(height: 46)
                .background(PyxisColor.bg)
                .clipShape(Capsule())
                .submitLabel(.send)
                .onSubmit { send(input) }
            Button { send(input) } label: {
                Icon(name: "paper-plane", size: 16, color: PyxisColor.onPrimary)
                    .frame(width: 46, height: 46)
                    .background(PyxisColor.primary)
                    .clipShape(Circle())
                    .opacity(sending ? 0.5 : 1)
            }
            .disabled(sending)
            .buttonStyle(.plain)
        }
        .padding(Spacing.md)
        .background(PyxisColor.surface)
        .overlay(alignment: .top) {
            Rectangle().fill(PyxisColor.border).frame(height: 1)
        }
    }

    private func seedGreeting() {
        guard messages.isEmpty else { return }
        let name = riskCase?.customerName ?? "this case"
        messages = [Message(
            role: .gemma,
            text: "I'm analyzing \(name) locally. Ask me anything about the evidence, scenarios, or the decision-critical question. All reasoning runs on the on-premise Gemma runtime."
        )]
    }

    private func send(_ text: String) {
        let question = text.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !question.isEmpty, !sending else { return }
        messages.append(Message(role: .user, text: question))
        input = ""
        sending = true
        Task {
            let reviewerId = auth.user?.id ?? "LOCAL-REVIEWER"
            do {
                let answer = try await api.askGemma(caseId: caseId, reviewerId: reviewerId, question: question)
                messages.append(Message(role: .gemma, text: answer))
            } catch {
                let message = (error as? PyxisError)?.errorDescription
                let text = message.map { "Local model error: \($0)" }
                    ?? "The local model could not answer this question."
                messages.append(Message(role: .gemma, text: text))
            }
            sending = false
        }
    }
}

/// Chat bubble with one squared-off top corner, matching the RN styling.
private struct BubbleShape: Shape {
    let isUser: Bool

    func path(in rect: CGRect) -> Path {
        let corners: UIRectCorner = isUser
            ? [.topLeft, .bottomLeft, .bottomRight]
            : [.topRight, .bottomLeft, .bottomRight]
        return Path(UIBezierPath(
            roundedRect: rect,
            byRoundingCorners: corners,
            cornerRadii: CGSize(width: Radius.lg, height: Radius.lg)
        ).cgPath)
    }
}
