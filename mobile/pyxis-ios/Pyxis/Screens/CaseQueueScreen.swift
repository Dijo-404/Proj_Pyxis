import SwiftUI

/// Risk Case Queue — a native port of `CaseQueueScreen.tsx`. A sortable list of
/// active cases (urgency / anomaly / uncertainty) with status pills and risk
/// bars; tapping a row opens the case detail.
struct CaseQueueScreen: View {
    @EnvironmentObject private var workspace: WorkspaceStore
    @EnvironmentObject private var router: Router

    enum SortKey: String, CaseIterable {
        case urgency, anomaly, uncertainty
        var label: String { rawValue.prefix(1).uppercased() + rawValue.dropFirst() }
    }

    @State private var sort: SortKey = .urgency

    private var cases: [RiskCase] { workspace.data?.cases ?? [] }

    private var sorted: [RiskCase] {
        cases.sorted { a, b in
            switch sort {
            case .anomaly:
                return a.anomalyScore > b.anomalyScore
            case .uncertainty:
                return uncertainty(a) > uncertainty(b)
            case .urgency:
                return a.currentRisk > b.currentRisk
            }
        }
    }

    private func uncertainty(_ c: RiskCase) -> Int {
        c.scenarios.filter { $0.category == .uncertain }.map(\.matchScore).max() ?? 0
    }

    var body: some View {
        VStack(spacing: 0) {
            HStack(spacing: Spacing.sm) {
                ForEach(SortKey.allCases, id: \.self) { key in
                    Button { sort = key } label: {
                        Text(key.label)
                            .font(.system(size: FontSize.small, weight: .semibold))
                            .foregroundColor(sort == key ? PyxisColor.onPrimary : PyxisColor.textMuted)
                            .padding(.horizontal, Spacing.lg)
                            .padding(.vertical, 7)
                            .background(sort == key ? PyxisColor.primary : PyxisColor.surface)
                            .overlay(
                                Capsule().stroke(sort == key ? PyxisColor.primary : PyxisColor.border, lineWidth: 1)
                            )
                            .clipShape(Capsule())
                    }
                    .buttonStyle(.plain)
                }
                Spacer()
            }
            .padding(.horizontal, Spacing.lg)
            .padding(.bottom, Spacing.sm)

            ScrollView(showsIndicators: false) {
                VStack(spacing: Spacing.md) {
                    ForEach(sorted) { item in
                        Button { router.push(.caseDetail(caseId: item.id)) } label: {
                            CaseQueueRow(data: item)
                        }
                        .buttonStyle(.plain)
                    }
                    Spacer().frame(height: Spacing.xxl)
                }
                .padding(.horizontal, Spacing.lg)
                .padding(.top, Spacing.sm)
            }
        }
        .background(PyxisColor.bg)
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .principal) {
                NavTitle(title: "Risk Case Queue", subtitle: "\(cases.count) active cases")
            }
        }
    }
}

/// Status metadata mirroring `STATUS_META` in the RN queue screen.
enum CaseStatusMeta {
    static func label(_ status: CaseStatus) -> String {
        switch status {
        case .open: return "Open"
        case .inReview: return "In review"
        case .escalated: return "Escalated"
        case .cleared: return "Cleared"
        case .suspicious: return "Suspicious"
        }
    }

    static func color(_ status: CaseStatus) -> Color {
        switch status {
        case .open: return PyxisColor.high
        case .inReview: return PyxisColor.primary
        case .escalated, .suspicious: return PyxisColor.critical
        case .cleared: return PyxisColor.low
        }
    }

    static func soft(_ status: CaseStatus) -> Color {
        switch status {
        case .open: return PyxisColor.highSoft
        case .inReview: return PyxisColor.primarySoft
        case .escalated, .suspicious: return PyxisColor.criticalSoft
        case .cleared: return PyxisColor.lowSoft
        }
    }
}

private struct CaseQueueRow: View {
    let data: RiskCase

    var body: some View {
        Card {
            VStack(alignment: .leading, spacing: 0) {
                HStack {
                    Text(data.id)
                        .font(.system(size: FontSize.small, weight: .bold))
                        .tracking(0.5)
                        .foregroundColor(PyxisColor.textFaint)
                    Spacer()
                    Text(CaseStatusMeta.label(data.status))
                        .font(.system(size: FontSize.tiny, weight: .heavy))
                        .foregroundColor(CaseStatusMeta.color(data.status))
                        .padding(.horizontal, Spacing.md)
                        .padding(.vertical, 4)
                        .background(CaseStatusMeta.soft(data.status))
                        .clipShape(Capsule())
                }
                Text(data.customerName)
                    .font(.system(size: FontSize.h3, weight: .bold))
                    .foregroundColor(PyxisColor.text)
                    .padding(.top, Spacing.sm)
                Text(data.triggerSummary)
                    .font(.system(size: FontSize.small))
                    .foregroundColor(PyxisColor.textMuted)
                    .lineLimit(2)
                    .padding(.top, 4)

                HStack(spacing: Spacing.md) {
                    VStack(spacing: 6) {
                        HStack {
                            Text("Anomaly \(data.anomalyScore)")
                            Spacer()
                            Text("Risk \(data.currentRisk)")
                        }
                        .font(.system(size: FontSize.tiny, weight: .semibold))
                        .foregroundColor(PyxisColor.textMuted)
                        ProgressBar(value: Double(data.currentRisk), color: riskBand(data.currentRisk).color)
                    }
                    RiskBadge(score: data.currentRisk)
                }
                .padding(.top, Spacing.lg)
            }
        }
    }
}
