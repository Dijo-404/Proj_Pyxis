import SwiftUI

/// Decision tab of the case detail screen — ports the RN `DecisionTab`:
/// decision-critical hero, counterfactual "how evidence changes the risk",
/// recommended safer workflow, and the reviewer decision + report actions wired
/// to `POST /cases/{id}/review` and `POST /reports/{id}/generate`.
struct DecisionTab: View {
    let data: RiskCase

    @EnvironmentObject private var auth: AuthStore
    @EnvironmentObject private var workspace: WorkspaceStore
    @Environment(\.apiClient) private var api

    @State private var action: ReviewAction? = nil
    @State private var reason = ""
    @State private var submitting = false
    @State private var submitError: String? = nil
    @State private var resultingStatus: String? = nil

    enum ReportState { case idle, generating, error, done }
    @State private var reportState: ReportState = .idle
    @State private var reportError: String? = nil

    private var canSubmit: Bool {
        guard let action else { return false }
        return action != .close && !reason.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty && !submitting
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            criticalHero
            SectionTitle("How evidence changes the risk")
            counterfactualCard
            SectionTitle("Recommended safer workflow")
            saferWorkflowCard
            SectionTitle("Reviewer decision")
            decisionGrid
            if action != nil { reasonField }
            if let resultingStatus { confirmation(resultingStatus) }
            if let submitError {
                Text(submitError)
                    .font(.system(size: FontSize.small))
                    .foregroundColor(PyxisColor.critical)
                    .padding(.top, Spacing.md)
            }
            PrimaryButton(title: "Submit decision", action: submitDecision, loading: submitting, disabled: !canSubmit)
                .padding(.top, Spacing.lg)

            if reportState == .done {
                confirmBox("Compliance report generated for \(data.id).")
            }
            if let reportError {
                Text(reportError)
                    .font(.system(size: FontSize.small))
                    .foregroundColor(PyxisColor.critical)
                    .padding(.top, Spacing.md)
            }
            PrimaryButton(title: "Generate compliance report", action: generateReport, loading: reportState == .generating, variant: .outline)
                .padding(.top, Spacing.md)
        }
    }

    // MARK: Sections

    private var criticalHero: some View {
        VStack(alignment: .leading, spacing: 0) {
            Text("DECISION-CRITICAL EVIDENCE")
                .font(.system(size: FontSize.tiny, weight: .heavy)).tracking(1)
                .foregroundColor(PyxisColor.primaryLight)
            Text(data.criticalQuestion.question)
                .font(.system(size: FontSize.h3, weight: .bold))
                .foregroundColor(PyxisColor.onPrimary)
                .padding(.top, Spacing.sm)
            Text(data.criticalQuestion.whyItMatters)
                .font(.system(size: FontSize.small))
                .foregroundColor(Color.white.opacity(0.75))
                .padding(.top, Spacing.md)
            HStack(alignment: .top, spacing: Spacing.sm) {
                Icon(name: "arrow-circle-right", size: 16, color: PyxisColor.accent)
                Text(data.criticalQuestion.recommendedAction)
                    .font(.system(size: FontSize.small))
                    .foregroundColor(PyxisColor.onPrimary)
            }
            .padding(Spacing.md)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(Color.white.opacity(0.1))
            .clipShape(RoundedRectangle(cornerRadius: Radius.md, style: .continuous))
            .padding(.top, Spacing.md)
        }
        .padding(Spacing.lg)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(PyxisColor.text)
        .clipShape(RoundedRectangle(cornerRadius: Radius.lg, style: .continuous))
        .floatingShadow()
        .padding(.bottom, Spacing.lg)
    }

    private var counterfactualCard: some View {
        Card {
            VStack(alignment: .leading, spacing: 0) {
                ForEach(Array(data.counterfactual.enumerated()), id: \.offset) { index, cf in
                    HStack {
                        Text(cf.condition)
                            .font(.system(size: FontSize.small))
                            .foregroundColor(PyxisColor.text)
                            .frame(maxWidth: .infinity, alignment: .leading)
                        HStack(spacing: Spacing.sm) {
                            Text("\(cf.from)")
                                .font(.system(size: FontSize.h3, weight: .bold))
                                .foregroundColor(riskBand(cf.from).color)
                            Icon(name: "long-arrow-right", size: 14, color: PyxisColor.textFaint)
                            Text("\(cf.to)")
                                .font(.system(size: FontSize.h3, weight: .bold))
                                .foregroundColor(riskBand(cf.to).color)
                        }
                    }
                    .padding(.vertical, Spacing.md)
                    .overlay(alignment: .top) {
                        if index > 0 { Rectangle().fill(PyxisColor.divider).frame(height: 1) }
                    }
                }
                Text("Scenario-based estimates, not guaranteed predictions.")
                    .font(.system(size: FontSize.tiny))
                    .italic()
                    .foregroundColor(PyxisColor.textFaint)
                    .padding(.top, Spacing.sm)
            }
        }
    }

    private var saferWorkflowCard: some View {
        Card {
            VStack(alignment: .leading, spacing: 0) {
                ForEach(Array(data.saferWorkflow.enumerated()), id: \.offset) { index, step in
                    HStack(alignment: .top, spacing: Spacing.md) {
                        Text("\(index + 1)")
                            .font(.system(size: FontSize.tiny, weight: .heavy))
                            .foregroundColor(PyxisColor.primaryDark)
                            .frame(width: 24, height: 24)
                            .background(PyxisColor.primarySoft)
                            .clipShape(Circle())
                        Text(step)
                            .font(.system(size: FontSize.small))
                            .foregroundColor(PyxisColor.text)
                        Spacer()
                    }
                    .padding(.vertical, Spacing.sm)
                }
            }
        }
    }

    private var decisionGrid: some View {
        FlowLayout(spacing: Spacing.md) {
            decisionButton("Clear", color: PyxisColor.low, value: .clear)
            decisionButton("Request Evidence", color: PyxisColor.medium, value: .requestMoreEvidence)
            decisionButton("Escalate", color: PyxisColor.accent, value: .escalate)
            decisionButton("Mark Suspicious", color: PyxisColor.critical, value: .markSuspicious)
        }
    }

    private func decisionButton(_ label: String, color: Color, value: ReviewAction) -> some View {
        let active = action == value
        return Button {
            action = value
            resultingStatus = nil
            submitError = nil
        } label: {
            Text(label)
                .font(.system(size: FontSize.small, weight: .heavy))
                .foregroundColor(active ? PyxisColor.onPrimary : color)
                .frame(width: 165, height: 50)
                .background(active ? color : Color.clear)
                .overlay(RoundedRectangle(cornerRadius: Radius.md, style: .continuous).stroke(color, lineWidth: 1.5))
                .clipShape(RoundedRectangle(cornerRadius: Radius.md, style: .continuous))
        }
        .buttonStyle(.plain)
    }

    private var reasonField: some View {
        TextField("Reason for this decision (required)", text: $reason, axis: .vertical)
            .font(.system(size: FontSize.small))
            .foregroundColor(PyxisColor.text)
            .padding(Spacing.md)
            .frame(minHeight: 60, alignment: .topLeading)
            .background(PyxisColor.surface)
            .overlay(RoundedRectangle(cornerRadius: Radius.md, style: .continuous).stroke(PyxisColor.border, lineWidth: 1))
            .clipShape(RoundedRectangle(cornerRadius: Radius.md, style: .continuous))
            .padding(.top, Spacing.md)
    }

    private func confirmation(_ status: String) -> some View {
        confirmBox("Decision recorded: \(action.map(Self.label) ?? ""). Case status is now \(status). An audit log entry has been written for \(data.id).")
    }

    private func confirmBox(_ text: String) -> some View {
        Text(text)
            .font(.system(size: FontSize.small))
            .foregroundColor(PyxisColor.text)
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding(Spacing.md)
            .background(PyxisColor.lowSoft)
            .clipShape(RoundedRectangle(cornerRadius: Radius.md, style: .continuous))
            .padding(.top, Spacing.lg)
    }

    // MARK: Actions

    private func submitDecision() {
        guard let action, action != .close, let user = auth.user else { return }
        submitting = true
        submitError = nil
        Task {
            do {
                let status = try await api.submitReview(
                    caseId: data.id,
                    reviewerId: user.id,
                    action: action,
                    reason: reason.trimmingCharacters(in: .whitespacesAndNewlines)
                )
                resultingStatus = status
                await workspace.refresh()
            } catch {
                submitError = (error as? PyxisError)?.errorDescription ?? "Unable to record this decision."
            }
            submitting = false
        }
    }

    private func generateReport() {
        guard let user = auth.user else { return }
        reportState = .generating
        reportError = nil
        Task {
            do {
                _ = try await api.generateReport(caseId: data.id, reviewerId: user.id)
                reportState = .done
            } catch {
                reportError = (error as? PyxisError)?.errorDescription ?? "Unable to generate the report."
                reportState = .error
            }
        }
    }

    static func label(_ a: ReviewAction) -> String {
        switch a {
        case .clear: return "Clear / Legitimate"
        case .requestMoreEvidence: return "Request more evidence"
        case .escalate: return "Escalated"
        case .markSuspicious: return "Marked suspicious"
        case .close: return "Closed"
        }
    }
}
