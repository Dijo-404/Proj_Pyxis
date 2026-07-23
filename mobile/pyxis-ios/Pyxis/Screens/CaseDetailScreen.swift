import SwiftUI

/// Case Detail — a native port of `CaseDetailScreen.tsx`. A risk-summary strip
/// and six sub-tabs (Transactions, Twin, Gemma timeline, Scenarios, Evidence
/// matrix, Decision). The header carries a magic-wand button that opens Ask
/// Gemma; the Transactions / Gemma tabs open the isolated agent sandbox.
struct CaseDetailScreen: View {
    let caseId: String

    @EnvironmentObject private var workspace: WorkspaceStore
    @EnvironmentObject private var router: Router

    enum Tab: String, CaseIterable {
        case transactions, twin, investigation, scenarios, evidence, decision
        var label: String {
            switch self {
            case .transactions: return "Transactions"
            case .twin: return "Twin"
            case .investigation: return "Gemma"
            case .scenarios: return "Scenarios"
            case .evidence: return "Evidence"
            case .decision: return "Decision"
            }
        }
    }

    @State private var tab: Tab = .transactions

    private var riskCase: RiskCase? { workspace.caseBy(id: caseId) }

    var body: some View {
        Group {
            if let data = riskCase {
                content(data)
            } else {
                VStack { Spacer(); Text("Case not found").foregroundColor(PyxisColor.textMuted); Spacer() }
            }
        }
        .background(PyxisColor.bg)
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .principal) {
                NavTitle(
                    title: riskCase?.customerName ?? "Case",
                    subtitle: riskCase.map { "\($0.id) · \($0.customerType)" }
                )
            }
            ToolbarItem(placement: .navigationBarTrailing) {
                if let data = riskCase {
                    Button { router.push(.askGemma(caseId: data.id)) } label: {
                        Icon(name: "magic", size: 16, color: PyxisColor.onPrimary)
                            .frame(width: 32, height: 32)
                            .background(PyxisColor.primary)
                            .clipShape(RoundedRectangle(cornerRadius: 10, style: .continuous))
                    }
                }
            }
        }
    }

    private func content(_ data: RiskCase) -> some View {
        let band = riskBand(data.currentRisk)
        return VStack(spacing: 0) {
            // Risk summary strip
            HStack(spacing: Spacing.md) {
                VStack(alignment: .leading, spacing: 0) {
                    Text("Current risk")
                        .font(.system(size: FontSize.tiny, weight: .semibold))
                        .foregroundColor(PyxisColor.textMuted)
                    HStack(alignment: .firstTextBaseline, spacing: 0) {
                        Text("\(data.currentRisk)")
                            .font(.system(size: FontSize.h2, weight: .black))
                            .foregroundColor(band.color)
                        Text(" / 100")
                            .font(.system(size: FontSize.small, weight: .semibold))
                            .foregroundColor(PyxisColor.textMuted)
                    }
                }
                Divider().frame(height: 36)
                VStack(alignment: .leading, spacing: 0) {
                    Text("Initial anomaly")
                        .font(.system(size: FontSize.tiny, weight: .semibold))
                        .foregroundColor(PyxisColor.textMuted)
                    Text("\(data.anomalyScore) / 100")
                        .font(.system(size: FontSize.h3, weight: .bold))
                        .foregroundColor(PyxisColor.text)
                }
                Divider().frame(height: 36)
                RiskBadge(score: data.currentRisk)
                Spacer(minLength: 0)
            }
            .padding(Spacing.md)
            .background(band.soft)
            .clipShape(RoundedRectangle(cornerRadius: Radius.md, style: .continuous))
            .padding(.horizontal, Spacing.lg)

            // Tabs
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: Spacing.sm) {
                    ForEach(Tab.allCases, id: \.self) { key in
                        Button { tab = key } label: {
                            Text(key.label)
                                .font(.system(size: FontSize.small, weight: .bold))
                                .foregroundColor(tab == key ? PyxisColor.onPrimary : PyxisColor.textMuted)
                                .padding(.horizontal, Spacing.lg)
                                .frame(height: 38)
                                .background(tab == key ? PyxisColor.primary : PyxisColor.surface)
                                .overlay(Capsule().stroke(tab == key ? PyxisColor.primary : PyxisColor.border, lineWidth: 1))
                                .clipShape(Capsule())
                        }
                        .buttonStyle(.plain)
                    }
                }
                .padding(.horizontal, Spacing.lg)
                .padding(.vertical, Spacing.md)
            }

            ScrollView(showsIndicators: false) {
                VStack(alignment: .leading, spacing: 0) {
                    switch tab {
                    case .transactions:
                        TransactionsTab(data: data) { router.push(.sandbox(caseId: data.id)) }
                    case .twin:
                        TwinTab(data: data)
                    case .investigation:
                        InvestigationTab(
                            data: data,
                            onAskGemma: { router.push(.askGemma(caseId: data.id)) },
                            onOpenSandbox: { router.push(.sandbox(caseId: data.id)) }
                        )
                    case .scenarios:
                        ScenarioTab(data: data)
                    case .evidence:
                        EvidenceTab(data: data)
                    case .decision:
                        DecisionTab(data: data)
                    }
                    Spacer().frame(height: Spacing.xxl)
                }
                .padding(.horizontal, Spacing.lg)
                .padding(.top, Spacing.xs)
            }
        }
    }
}

// MARK: - Scenario category metadata

enum ScenarioCatMeta {
    static func color(_ c: ScenarioCategory) -> Color {
        switch c {
        case .legitimate: return PyxisColor.legit
        case .suspicious: return PyxisColor.suspicious
        case .uncertain: return PyxisColor.uncertain
        }
    }
    static func soft(_ c: ScenarioCategory) -> Color {
        switch c {
        case .legitimate: return PyxisColor.lowSoft
        case .suspicious: return PyxisColor.criticalSoft
        case .uncertain: return Color(hex: 0xEEEAFA)
        }
    }
    static func label(_ c: ScenarioCategory) -> String {
        switch c {
        case .legitimate: return "Legitimate"
        case .suspicious: return "Suspicious"
        case .uncertain: return "Uncertain"
        }
    }
}

// MARK: - Transactions tab

private struct TransactionsTab: View {
    let data: RiskCase
    let onOpenSandbox: () -> Void
    @State private var open: String? = nil

    var body: some View {
        let risky = data.sandbox.transactions.filter(\.risky).sorted { $0.riskScore > $1.riskScore }
        let clean = data.sandbox.transactions.filter { !$0.risky }
        VStack(alignment: .leading, spacing: 0) {
            HStack(spacing: Spacing.md) {
                summaryTile(count: risky.count, label: "Risky", color: PyxisColor.critical, soft: PyxisColor.criticalSoft)
                summaryTile(count: clean.count, label: "Non-risky", color: PyxisColor.low, soft: PyxisColor.lowSoft)
            }
            .padding(.bottom, Spacing.lg)

            if !risky.isEmpty {
                SectionTitle("Flagged as risk")
                ForEach(risky) { txn in row(txn) }
            }

            SectionTitle("Non-risky activity")
            ForEach(clean) { txn in row(txn) }

            PrimaryButton(title: "Open the branch graph in Sandbox", action: onOpenSandbox, variant: .outline, icon: "flask")
                .padding(.top, Spacing.lg)
        }
    }

    private func summaryTile(count: Int, label: String, color: Color, soft: Color) -> some View {
        VStack(spacing: 2) {
            Text("\(count)")
                .font(.system(size: FontSize.h1, weight: .black))
                .foregroundColor(color)
            Text(label)
                .font(.system(size: FontSize.small, weight: .bold))
                .foregroundColor(PyxisColor.textMuted)
        }
        .frame(maxWidth: .infinity)
        .padding(Spacing.md)
        .background(soft)
        .clipShape(RoundedRectangle(cornerRadius: Radius.md, style: .continuous))
    }

    private func row(_ txn: CustomerTransaction) -> some View {
        TransactionRow(txn: txn, open: open == txn.id) {
            open = open == txn.id ? nil : txn.id
        }
        .padding(.bottom, Spacing.md)
    }
}

struct TransactionRow: View {
    let txn: CustomerTransaction
    let open: Bool
    let onToggle: () -> Void

    var body: some View {
        let tint = txn.risky ? PyxisColor.critical : PyxisColor.low
        Button(action: onToggle) {
            Card {
                VStack(alignment: .leading, spacing: 0) {
                    HStack(spacing: Spacing.md) {
                        Circle().fill(tint).frame(width: 9, height: 9)
                        VStack(alignment: .leading, spacing: 2) {
                            Text(txn.label)
                                .font(.system(size: FontSize.body, weight: .bold))
                                .foregroundColor(PyxisColor.text)
                            Text("\(txn.id) · \(txn.timestamp)")
                                .font(.system(size: FontSize.tiny))
                                .foregroundColor(PyxisColor.textFaint)
                        }
                        Spacer()
                        VStack(alignment: .trailing, spacing: 2) {
                            Text("\(txn.direction == .incoming ? "+" : "−")\(txn.amount)")
                                .font(.system(size: FontSize.body, weight: .bold))
                                .foregroundColor(PyxisColor.text)
                            Text(txn.reason)
                                .font(.system(size: FontSize.tiny, weight: .bold))
                                .foregroundColor(tint)
                        }
                    }
                    if open {
                        VStack(alignment: .leading, spacing: Spacing.md) {
                            Text(txn.explanation)
                                .font(.system(size: FontSize.small))
                                .foregroundColor(PyxisColor.text)
                            if !txn.firedSignals.isEmpty {
                                FlowLayout(spacing: Spacing.sm) {
                                    ForEach(txn.firedSignals, id: \.self) { signal in
                                        signalChip(signal)
                                    }
                                }
                            }
                        }
                        .padding(.top, Spacing.md)
                        .overlay(alignment: .top) {
                            Rectangle().fill(PyxisColor.divider).frame(height: 1)
                        }
                    }
                    Text(open ? "Tap to collapse" : "Tap for anomaly detail")
                        .font(.system(size: FontSize.tiny))
                        .foregroundColor(PyxisColor.textFaint)
                        .frame(maxWidth: .infinity)
                        .padding(.top, Spacing.sm)
                }
            }
        }
        .buttonStyle(.plain)
    }

    private func signalChip(_ text: String) -> some View {
        HStack(spacing: 4) {
            Icon(name: "bolt", size: 10, color: PyxisColor.critical)
            Text(text)
                .font(.system(size: FontSize.tiny, weight: .bold))
                .foregroundColor(PyxisColor.critical)
        }
        .padding(.horizontal, Spacing.sm)
        .padding(.vertical, 4)
        .background(PyxisColor.criticalSoft)
        .clipShape(Capsule())
    }
}

// MARK: - Twin tab

private struct TwinTab: View {
    let data: RiskCase

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            SectionTitle("Financial Twin · normal vs current")
            Card {
                VStack(spacing: 0) {
                    HStack {
                        Text("NORMAL")
                            .font(.system(size: FontSize.tiny, weight: .heavy)).tracking(0.6)
                            .foregroundColor(PyxisColor.low)
                            .frame(maxWidth: .infinity, alignment: .leading)
                        Text("CURRENT")
                            .font(.system(size: FontSize.tiny, weight: .heavy)).tracking(0.6)
                            .foregroundColor(PyxisColor.accent)
                            .frame(maxWidth: .infinity, alignment: .trailing)
                    }
                    .padding(.bottom, Spacing.sm)
                    ForEach(Array(data.twin.enumerated()), id: \.element.id) { index, metric in
                        HStack(alignment: .top) {
                            VStack(alignment: .leading, spacing: 2) {
                                Text(metric.label)
                                    .font(.system(size: FontSize.tiny, weight: .semibold))
                                    .foregroundColor(PyxisColor.textFaint)
                                Text(metric.normal)
                                    .font(.system(size: FontSize.body, weight: .bold))
                                    .foregroundColor(PyxisColor.text)
                            }
                            .frame(maxWidth: .infinity, alignment: .leading)
                            VStack(alignment: .trailing, spacing: 4) {
                                Text(metric.current)
                                    .font(.system(size: FontSize.body, weight: .bold))
                                    .foregroundColor(metric.deviated ? PyxisColor.accent : PyxisColor.text)
                                if metric.deviated {
                                    Text("deviation")
                                        .font(.system(size: FontSize.tiny, weight: .bold))
                                        .foregroundColor(PyxisColor.accent)
                                        .padding(.horizontal, Spacing.sm)
                                        .padding(.vertical, 2)
                                        .background(PyxisColor.accentSoft)
                                        .clipShape(Capsule())
                                } else {
                                    Text("within range")
                                        .font(.system(size: FontSize.tiny, weight: .semibold))
                                        .foregroundColor(PyxisColor.low)
                                }
                            }
                            .frame(maxWidth: .infinity, alignment: .trailing)
                        }
                        .padding(.vertical, Spacing.md)
                        .overlay(alignment: .top) {
                            if index > 0 { Rectangle().fill(PyxisColor.divider).frame(height: 1) }
                        }
                    }
                }
            }
            Text("The Adaptive Financial Twin represents this customer's trusted normal behavior. It updates only after a reviewer clears the activity (trust-gated learning).")
                .font(.system(size: FontSize.small))
                .foregroundColor(PyxisColor.textMuted)
                .padding(.top, Spacing.lg)
        }
    }
}

// MARK: - Investigation (Gemma) tab

private struct InvestigationTab: View {
    let data: RiskCase
    let onAskGemma: () -> Void
    let onOpenSandbox: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            SectionTitle("Gemma investigation timeline")
            Card {
                VStack(spacing: 0) {
                    ForEach(Array(data.investigation.enumerated()), id: \.element.id) { index, step in
                        HStack(alignment: .top, spacing: Spacing.sm) {
                            VStack(spacing: 2) {
                                ZStack {
                                    Circle()
                                        .fill(step.done ? PyxisColor.primary : PyxisColor.surface)
                                        .overlay(Circle().stroke(step.done ? PyxisColor.primary : PyxisColor.border, lineWidth: 2))
                                        .frame(width: 22, height: 22)
                                    if step.done { Icon(name: "check", size: 11, color: PyxisColor.onPrimary) }
                                }
                                if index < data.investigation.count - 1 {
                                    Rectangle().fill(PyxisColor.primaryLight).frame(width: 2).frame(maxHeight: .infinity)
                                }
                            }
                            .frame(width: 30)
                            VStack(alignment: .leading, spacing: 2) {
                                Text(step.label)
                                    .font(.system(size: FontSize.body, weight: .semibold))
                                    .foregroundColor(PyxisColor.text)
                                if let detail = step.detail {
                                    Text(detail)
                                        .font(.system(size: FontSize.small))
                                        .foregroundColor(PyxisColor.textMuted)
                                }
                            }
                            .padding(.bottom, Spacing.lg)
                            Spacer()
                        }
                    }
                }
            }
            HStack(alignment: .top, spacing: Spacing.sm) {
                Icon(name: "shield", size: 15, color: PyxisColor.primaryDark)
                Text("Gemma reasons over trusted computed evidence only. It flags risk and requires review — it never declares guilt or overrides the compliance officer.")
                    .font(.system(size: FontSize.small))
                    .foregroundColor(PyxisColor.primaryDark)
            }
            .padding(Spacing.md)
            .background(PyxisColor.primarySoft)
            .clipShape(RoundedRectangle(cornerRadius: Radius.md, style: .continuous))
            .padding(.top, Spacing.md)

            PrimaryButton(title: "Open isolated agent sandbox", action: onOpenSandbox, icon: "flask")
                .padding(.top, Spacing.lg)
            PrimaryButton(title: "Ask Gemma about this case", action: onAskGemma, variant: .outline, icon: "magic")
                .padding(.top, Spacing.md)
        }
    }
}

// MARK: - Scenario tab

private struct ScenarioTab: View {
    let data: RiskCase
    @State private var openId: String? = nil

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            SectionTitle("Scenario arena")
            ForEach(data.scenarios) { scenario in
                ScenarioCard(scenario: scenario, open: openId == scenario.id) {
                    openId = openId == scenario.id ? nil : scenario.id
                }
                .padding(.bottom, Spacing.md)
            }
        }
        .onAppear { if openId == nil { openId = data.scenarios.first?.id } }
    }
}

private struct ScenarioCard: View {
    let scenario: Scenario
    let open: Bool
    let onToggle: () -> Void

    var body: some View {
        let color = ScenarioCatMeta.color(scenario.category)
        Card {
            VStack(alignment: .leading, spacing: 0) {
                Button(action: onToggle) {
                    VStack(alignment: .leading, spacing: 0) {
                        HStack {
                            Pill(label: ScenarioCatMeta.label(scenario.category), color: color, soft: ScenarioCatMeta.soft(scenario.category))
                            Spacer()
                            Text("\(scenario.matchScore)%")
                                .font(.system(size: FontSize.h2, weight: .black))
                                .foregroundColor(color)
                        }
                        Text(scenario.name)
                            .font(.system(size: FontSize.h3, weight: .bold))
                            .foregroundColor(PyxisColor.text)
                            .padding(.vertical, Spacing.sm)
                        ProgressBar(value: Double(scenario.matchScore), color: color)
                        Text(scenario.description)
                            .font(.system(size: FontSize.small))
                            .foregroundColor(PyxisColor.textMuted)
                            .padding(.top, Spacing.sm)
                    }
                }
                .buttonStyle(.plain)

                if open {
                    VStack(alignment: .leading, spacing: 0) {
                        EvidenceList(title: "Supporting", items: scenario.supporting, color: PyxisColor.low, icon: "check-circle")
                        EvidenceList(title: "Contradicting", items: scenario.contradicting, color: PyxisColor.critical, icon: "times-circle")
                        EvidenceList(title: "Unknown", items: scenario.unknown, color: PyxisColor.medium, icon: "question-circle")
                    }
                    .padding(.top, Spacing.md)
                    .overlay(alignment: .top) { Rectangle().fill(PyxisColor.divider).frame(height: 1) }
                }
                Text(open ? "Tap to collapse" : "Tap for evidence")
                    .font(.system(size: FontSize.tiny))
                    .foregroundColor(PyxisColor.textFaint)
                    .frame(maxWidth: .infinity)
                    .padding(.top, Spacing.sm)
            }
        }
    }
}

private struct EvidenceList: View {
    let title: String
    let items: [String]
    let color: Color
    let icon: String

    var body: some View {
        if !items.isEmpty {
            VStack(alignment: .leading, spacing: 3) {
                Text(title)
                    .font(.system(size: FontSize.tiny, weight: .heavy)).tracking(0.5)
                    .foregroundColor(color)
                    .padding(.bottom, 1)
                ForEach(items, id: \.self) { item in
                    HStack(alignment: .top, spacing: 0) {
                        Icon(name: icon, size: 13, color: color).frame(width: 18)
                        Text(item)
                            .font(.system(size: FontSize.small))
                            .foregroundColor(PyxisColor.text)
                    }
                }
            }
            .padding(.bottom, Spacing.md)
        }
    }
}

// MARK: - Evidence matrix tab

enum EvidenceStatusSymbol {
    static func icon(_ s: EvidenceStatus) -> String {
        switch s {
        case .match: return "check-circle"
        case .contradict: return "times-circle"
        case .unknown: return "question-circle"
        case .partial: return "adjust"
        }
    }
    static func color(_ s: EvidenceStatus) -> Color {
        switch s {
        case .match: return PyxisColor.low
        case .contradict: return PyxisColor.critical
        case .unknown: return PyxisColor.medium
        case .partial: return PyxisColor.accent
        }
    }
}

private struct EvidenceTab: View {
    let data: RiskCase
    private let allStatuses: [EvidenceStatus] = [.match, .contradict, .unknown, .partial]

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            SectionTitle("Evidence matrix")
            Card(padded: false) {
                ScrollView(.horizontal, showsIndicators: false) {
                    VStack(spacing: 0) {
                        HStack(spacing: 0) {
                            Text("Signal")
                                .frame(width: 150, alignment: .leading)
                                .font(.system(size: FontSize.tiny, weight: .heavy))
                                .foregroundColor(PyxisColor.textMuted)
                                .padding(.leading, Spacing.xs)
                            ForEach(data.scenarios) { scenario in
                                Text(scenario.name.split(separator: " ").first.map(String.init) ?? scenario.name)
                                    .frame(width: 78)
                                    .font(.system(size: FontSize.tiny, weight: .heavy))
                                    .foregroundColor(PyxisColor.textMuted)
                                    .lineLimit(1)
                            }
                        }
                        .padding(.bottom, Spacing.sm)
                        .overlay(alignment: .bottom) { Rectangle().fill(PyxisColor.border).frame(height: 1) }

                        ForEach(Array(data.evidence.enumerated()), id: \.element.id) { index, row in
                            HStack(spacing: 0) {
                                Text(row.signal)
                                    .frame(width: 150, alignment: .leading)
                                    .font(.system(size: FontSize.small, weight: .semibold))
                                    .foregroundColor(PyxisColor.text)
                                    .padding(.leading, Spacing.xs)
                                ForEach(data.scenarios) { scenario in
                                    ZStack {
                                        if let status = row.byScenario[scenario.id] {
                                            Icon(name: EvidenceStatusSymbol.icon(status), size: 18, color: EvidenceStatusSymbol.color(status))
                                        } else {
                                            Text("–").foregroundColor(PyxisColor.textFaint)
                                        }
                                    }
                                    .frame(width: 78)
                                }
                            }
                            .padding(.vertical, Spacing.md)
                            .background(index % 2 == 1 ? PyxisColor.surfaceAlt : Color.clear)
                        }
                    }
                    .padding(Spacing.md)
                }
            }
            FlowLayout(spacing: Spacing.sm) {
                ForEach(allStatuses, id: \.self) { status in
                    HStack(spacing: 6) {
                        Icon(name: EvidenceStatusSymbol.icon(status), size: 14, color: EvidenceStatusSymbol.color(status))
                        Text(status.rawValue.lowercased())
                            .font(.system(size: FontSize.tiny, weight: .semibold))
                            .foregroundColor(PyxisColor.textMuted)
                    }
                    .padding(.horizontal, Spacing.md)
                    .padding(.vertical, 6)
                    .background(PyxisColor.surface)
                    .clipShape(Capsule())
                    .cardShadow()
                }
            }
            .padding(.top, Spacing.md)
        }
    }
}
