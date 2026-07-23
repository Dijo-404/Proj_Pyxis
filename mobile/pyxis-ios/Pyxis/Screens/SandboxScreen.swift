import SwiftUI

/// Agent Sandbox — a native port of `SandboxScreen.tsx`. The isolated
/// per-customer simulation: isolation-boundary banner, run metadata, the
/// anomaly breakdown with gauge + signal contributions, the expandable agent
/// pipeline, the neural-network transaction branch graph (tap a node for the
/// anomaly explanation), and the follow-the-money flow.
struct SandboxScreen: View {
    let caseId: String
    @EnvironmentObject private var workspace: WorkspaceStore

    private var riskCase: RiskCase? { workspace.caseBy(id: caseId) }

    var body: some View {
        Group {
            if let data = riskCase {
                content(data)
            } else {
                VStack { Spacer(); Text("Sandbox unavailable").foregroundColor(PyxisColor.textMuted); Spacer() }
            }
        }
        .background(PyxisColor.bg)
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .principal) {
                NavTitle(
                    title: "Agent Sandbox",
                    subtitle: riskCase.map { "\($0.customerName) · \($0.sandbox.runId)" }
                )
            }
        }
    }

    private func content(_ data: RiskCase) -> some View {
        let sb = data.sandbox
        let band = riskBand(sb.anomaly.score)
        return ScrollView(showsIndicators: false) {
            VStack(alignment: .leading, spacing: Spacing.md) {
                boundaryBanner(sb)
                metaChips(sb)

                SectionTitle("Why this is flagged")
                anomalyCard(sb, band: band)
                signalCard(sb, band: band)

                SectionTitle("Agent run · \(sb.stages.count) stages")
                ForEach(Array(sb.stages.enumerated()), id: \.element.id) { index, stage in
                    StageCard(stage: stage, last: index == sb.stages.count - 1)
                }

                SectionTitle("Transaction branch graph")
                BranchGraph(data: data)

                SectionTitle("Follow the money")
                MoneyFlow(data: data)

                Spacer().frame(height: Spacing.xxl)
            }
            .padding(Spacing.lg)
        }
    }

    private func boundaryBanner(_ sb: Sandbox) -> some View {
        HStack(spacing: Spacing.sm) {
            Icon(name: "lock", size: 14, color: PyxisColor.primaryDark)
            Text("Isolated simulation · synthetic data · local Gemma only. " + (sb.boundaryHeld ? "Boundary held — nothing left the device." : "Boundary breached."))
                .font(.system(size: FontSize.small, weight: .semibold))
                .foregroundColor(PyxisColor.primaryDark)
            Spacer(minLength: 0)
        }
        .padding(Spacing.md)
        .background(PyxisColor.primarySoft)
        .clipShape(RoundedRectangle(cornerRadius: Radius.md, style: .continuous))
    }

    private func metaChips(_ sb: Sandbox) -> some View {
        VStack(alignment: .leading, spacing: Spacing.sm) {
            HStack(spacing: Spacing.sm) {
                Chip(label: sb.model, icon: "microchip", color: PyxisColor.text, soft: PyxisColor.surfaceAlt)
                Chip(label: sb.runtime, icon: "server", color: PyxisColor.text, soft: PyxisColor.surfaceAlt)
                Spacer(minLength: 0)
            }
            HStack(spacing: Spacing.sm) {
                Chip(label: "seed \(sb.seed)", icon: "hashtag", color: PyxisColor.textMuted, soft: PyxisColor.surfaceAlt)
                Chip(label: String(format: "%.2fs total", Double(sb.totalDurationMs) / 1000), icon: "clock-o", color: PyxisColor.textMuted, soft: PyxisColor.surfaceAlt)
                Spacer(minLength: 0)
            }
        }
    }

    private func anomalyCard(_ sb: Sandbox, band: RiskBand) -> some View {
        Card {
            VStack(alignment: .leading, spacing: 0) {
                HStack(alignment: .center, spacing: Spacing.lg) {
                    ScoreGauge(value: sb.anomaly.score, color: band.color, label: "ANOMALY", caption: sb.anomaly.deviationLevel)
                    VStack(alignment: .leading, spacing: 4) {
                        Text("Why it matters")
                            .font(.system(size: FontSize.tiny, weight: .heavy)).tracking(0.5)
                            .foregroundColor(PyxisColor.textFaint)
                        Text(sb.anomaly.matters)
                            .font(.system(size: FontSize.small))
                            .foregroundColor(PyxisColor.text)
                    }
                }
                PyxisDivider()
                Text("Why it is marked as risk")
                    .font(.system(size: FontSize.tiny, weight: .heavy)).tracking(0.5)
                    .foregroundColor(PyxisColor.textFaint)
                Text(sb.anomaly.markedRisk)
                    .font(.system(size: FontSize.small))
                    .foregroundColor(PyxisColor.text)
                    .padding(.top, 4)
            }
        }
    }

    private func signalCard(_ sb: Sandbox, band: RiskBand) -> some View {
        Card {
            VStack(alignment: .leading, spacing: Spacing.md) {
                Text("Signal contributions")
                    .font(.system(size: FontSize.body, weight: .heavy))
                    .foregroundColor(PyxisColor.text)
                ForEach(sb.anomaly.signals) { signal in
                    VStack(alignment: .leading, spacing: 6) {
                        HStack {
                            Icon(name: signal.fired ? "dot-circle-o" : "circle-o", size: 12, color: signal.fired ? band.color : PyxisColor.textFaint)
                            Text(signal.label)
                                .font(.system(size: FontSize.small, weight: signal.fired ? .bold : .semibold))
                                .foregroundColor(signal.fired ? PyxisColor.text : PyxisColor.textFaint)
                            Spacer()
                            Text(signal.value)
                                .font(.system(size: FontSize.small, weight: .heavy))
                                .foregroundColor(signal.fired ? band.color : PyxisColor.textFaint)
                        }
                        if signal.fired {
                            ProgressBar(value: Double(signal.contribution), color: band.color, height: 6)
                        }
                        Text(signal.why)
                            .font(.system(size: FontSize.tiny))
                            .foregroundColor(PyxisColor.textMuted)
                    }
                }
            }
        }
    }
}

// MARK: - Actor / verified metadata

private enum ActorMeta {
    static func label(_ a: Actor) -> String { a == .gemma ? "Gemma" : "Local code" }
    static func color(_ a: Actor) -> Color { a == .gemma ? PyxisColor.uncertain : PyxisColor.primary }
    static func soft(_ a: Actor) -> Color { a == .gemma ? Color(hex: 0xEEEAFA) : PyxisColor.primarySoft }
    static func icon(_ a: Actor) -> String { a == .gemma ? "magic" : "calculator" }
}

private enum VerifiedMeta {
    static func color(_ v: FlowVerified) -> Color {
        switch v { case .verified: return PyxisColor.low; case .unknown: return PyxisColor.medium; case .flagged: return PyxisColor.critical }
    }
    static func soft(_ v: FlowVerified) -> Color {
        switch v { case .verified: return PyxisColor.lowSoft; case .unknown: return PyxisColor.mediumSoft; case .flagged: return PyxisColor.criticalSoft }
    }
    static func icon(_ v: FlowVerified) -> String {
        switch v { case .verified: return "check-circle"; case .unknown: return "question-circle"; case .flagged: return "exclamation-circle" }
    }
    static func label(_ v: FlowVerified) -> String {
        switch v { case .verified: return "Verified"; case .unknown: return "Unknown"; case .flagged: return "Flagged" }
    }
}

// MARK: - Stage card

private struct StageCard: View {
    let stage: AgentStage
    let last: Bool
    @State private var open = false

    var body: some View {
        let color = ActorMeta.color(stage.actor)
        HStack(alignment: .top, spacing: 0) {
            VStack(spacing: 2) {
                Icon(name: ActorMeta.icon(stage.actor), size: 12, color: PyxisColor.onPrimary)
                    .frame(width: 28, height: 28)
                    .background(color)
                    .clipShape(Circle())
                    .padding(.top, Spacing.md)
                if !last {
                    Rectangle().fill(PyxisColor.divider).frame(width: 2).frame(maxHeight: .infinity)
                }
            }
            .frame(width: 34)

            Card {
                VStack(alignment: .leading, spacing: 0) {
                    Button { withAnimation { open.toggle() } } label: {
                        VStack(alignment: .leading, spacing: 0) {
                            HStack {
                                Text(stage.title)
                                    .font(.system(size: FontSize.body, weight: .heavy))
                                    .foregroundColor(PyxisColor.text)
                                Spacer()
                                Chip(label: ActorMeta.label(stage.actor), icon: ActorMeta.icon(stage.actor), color: color, soft: ActorMeta.soft(stage.actor))
                            }
                            Text(stage.summary)
                                .font(.system(size: FontSize.small))
                                .foregroundColor(PyxisColor.textMuted)
                                .padding(.top, 4)
                            HStack {
                                Text("\(stage.durationMs) ms")
                                    .font(.system(size: FontSize.tiny, weight: .bold))
                                    .foregroundColor(PyxisColor.textFaint)
                                Spacer()
                                Text(open ? "Hide detail" : "Show detail")
                                    .font(.system(size: FontSize.tiny, weight: .bold))
                                    .foregroundColor(PyxisColor.primary)
                            }
                            .padding(.top, Spacing.sm)
                        }
                    }
                    .buttonStyle(.plain)

                    if open { detail }
                }
            }
            .padding(.bottom, Spacing.sm)
        }
    }

    private var detail: some View {
        VStack(alignment: .leading, spacing: 0) {
            ioLabel("INPUT")
            ioText(stage.input)
            ioLabel("OUTPUT")
            ioText(stage.output)
            if let calls = stage.toolCalls, !calls.isEmpty {
                ioLabel("DETERMINISTIC TOOL CALLS")
                ForEach(calls) { call in
                    VStack(alignment: .leading, spacing: 3) {
                        (Text(call.tool).font(.system(size: FontSize.small, weight: .bold)).foregroundColor(PyxisColor.primaryDark)
                         + Text("(\(call.args))").font(.system(size: FontSize.tiny)).foregroundColor(PyxisColor.textMuted))
                        HStack(spacing: 6) {
                            Icon(name: "long-arrow-right", size: 12, color: PyxisColor.textFaint)
                            Text(call.result)
                                .font(.system(size: FontSize.small))
                                .foregroundColor(PyxisColor.text)
                        }
                    }
                    .padding(Spacing.sm)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(PyxisColor.surfaceAlt)
                    .clipShape(RoundedRectangle(cornerRadius: Radius.sm, style: .continuous))
                    .padding(.top, Spacing.sm)
                }
            }
        }
        .padding(.top, Spacing.md)
        .overlay(alignment: .top) { Rectangle().fill(PyxisColor.divider).frame(height: 1) }
    }

    private func ioLabel(_ text: String) -> some View {
        Text(text)
            .font(.system(size: FontSize.tiny, weight: .heavy)).tracking(0.5)
            .foregroundColor(PyxisColor.textFaint)
            .padding(.top, Spacing.sm)
            .padding(.bottom, 4)
    }
    private func ioText(_ text: String) -> some View {
        Text(text).font(.system(size: FontSize.small)).foregroundColor(PyxisColor.text)
    }
}

// MARK: - Branch graph

private struct BranchGraph: View {
    let data: RiskCase
    @State private var selected: CustomerTransaction? = nil

    private let graphHeight: CGFloat = 320
    private let nodeRadius: CGFloat = 15

    private func branch(_ id: String) -> BranchNode? { data.sandbox.branches.first { $0.id == id } }
    private func txn(for branchId: String) -> CustomerTransaction? {
        guard let tid = branch(branchId)?.transactionId else { return nil }
        return data.sandbox.transactions.first { $0.id == tid }
    }

    var body: some View {
        Card {
            VStack(alignment: .leading, spacing: 0) {
                HStack(spacing: Spacing.lg) {
                    legend(color: PyxisColor.critical, text: "risky node")
                    legend(color: PyxisColor.low, text: "clean node")
                }
                .padding(.bottom, Spacing.md)

                GeometryReader { geo in
                    let w = geo.size.width
                    let h = graphHeight
                    ZStack(alignment: .topLeading) {
                        // edges
                        Path { path in
                            for node in data.sandbox.branches {
                                for pid in node.parents {
                                    guard let parent = branch(pid) else { continue }
                                    path.move(to: CGPoint(x: parent.x * w, y: parent.y * h))
                                    path.addLine(to: CGPoint(x: node.x * w, y: node.y * h))
                                }
                            }
                        }
                        .stroke(PyxisColor.border, lineWidth: 2)

                        // nodes + labels
                        ForEach(data.sandbox.branches) { node in
                            if let t = txn(for: node.id) {
                                nodeView(t)
                                    .position(x: node.x * w, y: node.y * h)
                                Text(t.amount)
                                    .font(.system(size: 9, weight: .bold))
                                    .foregroundColor(PyxisColor.text)
                                    .lineLimit(1)
                                    .frame(width: 64)
                                    .position(x: node.x * w, y: node.y * h + nodeRadius + 12)
                            }
                        }
                    }
                }
                .frame(height: graphHeight)
                .background(PyxisColor.surfaceAlt)
                .clipShape(RoundedRectangle(cornerRadius: Radius.md, style: .continuous))

                Text("Each node is a real transaction for this customer; branches trace which activity fed into which. Tap any node to see why it was — or wasn't — treated as risk.")
                    .font(.system(size: FontSize.tiny))
                    .foregroundColor(PyxisColor.textMuted)
                    .padding(.top, Spacing.lg)
            }
        }
        .sheet(item: $selected) { txn in
            TransactionDetailSheet(transaction: txn)
                .presentationDetents([.medium, .large])
        }
    }

    private func nodeView(_ t: CustomerTransaction) -> some View {
        Button { selected = t } label: {
            Icon(name: t.risky ? "exclamation" : "check", size: t.risky ? 12 : 11, color: PyxisColor.onPrimary)
                .frame(width: nodeRadius * 2, height: nodeRadius * 2)
                .background(t.risky ? PyxisColor.critical : PyxisColor.low)
                .clipShape(Circle())
                .cardShadow()
        }
        .buttonStyle(.plain)
    }

    private func legend(color: Color, text: String) -> some View {
        HStack(spacing: 6) {
            Circle().fill(color).frame(width: 8, height: 8)
            Text(text).font(.system(size: FontSize.tiny, weight: .semibold)).foregroundColor(PyxisColor.textMuted)
        }
    }
}

/// Node-tap detail — presented as a native sheet (the RN app used a centered
/// modal card; a sheet is the HIG-native equivalent).
private struct TransactionDetailSheet: View {
    let transaction: CustomerTransaction
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 0) {
                HStack {
                    HStack(spacing: 6) {
                        Icon(name: transaction.risky ? "exclamation-triangle" : "check-circle", size: 14, color: transaction.risky ? PyxisColor.critical : PyxisColor.low)
                        Text(transaction.risky ? "Risk \(transaction.riskScore)/100" : "Clean")
                            .font(.system(size: FontSize.tiny, weight: .heavy))
                            .foregroundColor(transaction.risky ? PyxisColor.critical : PyxisColor.low)
                    }
                    .padding(.horizontal, Spacing.md)
                    .padding(.vertical, 5)
                    .background(transaction.risky ? PyxisColor.criticalSoft : PyxisColor.lowSoft)
                    .clipShape(Capsule())
                    Spacer()
                    Button { dismiss() } label: { Icon(name: "times", size: 18, color: PyxisColor.textFaint) }
                        .buttonStyle(.plain)
                }

                Text(transaction.label)
                    .font(.system(size: FontSize.h3, weight: .bold))
                    .foregroundColor(PyxisColor.text)
                    .padding(.top, Spacing.md)
                Text("\(transaction.id) · \(transaction.timestamp) · \(transaction.direction == .incoming ? "+" : "−")\(transaction.amount)")
                    .font(.system(size: FontSize.tiny, weight: .semibold))
                    .foregroundColor(PyxisColor.textFaint)
                    .padding(.top, 3)

                PyxisDivider()

                Text("WHAT'S WRONG (OR NOT)")
                    .font(.system(size: FontSize.tiny, weight: .heavy)).tracking(0.5)
                    .foregroundColor(PyxisColor.textFaint)
                    .padding(.bottom, 6)
                Text(transaction.explanation)
                    .font(.system(size: FontSize.small))
                    .foregroundColor(PyxisColor.text)

                if !transaction.firedSignals.isEmpty {
                    Text("SIGNALS THAT FIRED")
                        .font(.system(size: FontSize.tiny, weight: .heavy)).tracking(0.5)
                        .foregroundColor(PyxisColor.textFaint)
                        .padding(.top, Spacing.md)
                        .padding(.bottom, 6)
                    FlowLayout(spacing: Spacing.sm) {
                        ForEach(transaction.firedSignals, id: \.self) { signal in
                            HStack(spacing: 4) {
                                Icon(name: "bolt", size: 10, color: PyxisColor.critical)
                                Text(signal).font(.system(size: FontSize.tiny, weight: .bold)).foregroundColor(PyxisColor.critical)
                            }
                            .padding(.horizontal, Spacing.sm)
                            .padding(.vertical, 4)
                            .background(PyxisColor.criticalSoft)
                            .clipShape(Capsule())
                        }
                    }
                } else {
                    Text("No anomaly signals fired for this transaction.")
                        .font(.system(size: FontSize.small, weight: .semibold))
                        .foregroundColor(PyxisColor.low)
                        .padding(.top, Spacing.md)
                }
                Spacer(minLength: 0)
            }
            .padding(Spacing.lg)
        }
        .presentationDragIndicator(.visible)
    }
}

// MARK: - Follow the money

private struct MoneyFlow: View {
    let data: RiskCase

    var body: some View {
        let nodes = data.sandbox.flow.nodes
        let edges = data.sandbox.flow.edges
        let source = nodes.first { $0.kind == .source }
        let customer = nodes.first { $0.kind == .customer }
        let beneficiaries = nodes.filter { $0.kind == .beneficiary }
        let inbound = edges.first { $0.to == customer?.id }

        return Card {
            VStack(alignment: .leading, spacing: 0) {
                if let source {
                    FlowNodeRow(node: source, caption: inbound?.amount)
                }
                connectorDown
                if let customer {
                    FlowNodeRow(node: customer, highlight: true)
                }
                HStack(spacing: Spacing.sm) {
                    Icon(name: "level-down", size: 13, color: PyxisColor.textFaint)
                    Text("redistributed to \(beneficiaries.count) account\(beneficiaries.count == 1 ? "" : "s")")
                        .font(.system(size: FontSize.tiny, weight: .semibold))
                        .foregroundColor(PyxisColor.textFaint)
                }
                .padding(.leading, Spacing.sm)
                .padding(.vertical, Spacing.sm)
                ForEach(beneficiaries) { node in
                    FlowNodeRow(node: node, caption: edges.first { $0.to == node.id }?.amount, indent: true)
                }
            }
        }
    }

    private var connectorDown: some View {
        Icon(name: "long-arrow-down", size: 16, color: PyxisColor.textFaint)
            .frame(maxWidth: .infinity)
            .padding(.vertical, 2)
    }
}

private struct FlowNodeRow: View {
    let node: FlowNode
    var caption: String? = nil
    var highlight: Bool = false
    var indent: Bool = false

    var body: some View {
        let verified = node.verified
        let icon = node.kind == .source ? "sign-in" : (node.kind == .customer ? "university" : "user")
        let tint = highlight ? PyxisColor.primary : (verified.map(VerifiedMeta.color) ?? PyxisColor.textMuted)
        return HStack(spacing: Spacing.md) {
            Icon(name: icon, size: 15, color: tint)
                .frame(width: 38, height: 38)
                .background(verified.map(VerifiedMeta.soft) ?? PyxisColor.surfaceAlt)
                .clipShape(RoundedRectangle(cornerRadius: 11, style: .continuous))
            VStack(alignment: .leading, spacing: 1) {
                Text(node.label)
                    .font(.system(size: FontSize.body, weight: .bold))
                    .foregroundColor(PyxisColor.text)
                    .lineLimit(1)
                if let caption {
                    Text(caption).font(.system(size: FontSize.small)).foregroundColor(PyxisColor.textMuted)
                }
            }
            Spacer()
            if let verified {
                Chip(label: VerifiedMeta.label(verified), icon: VerifiedMeta.icon(verified), color: VerifiedMeta.color(verified), soft: VerifiedMeta.soft(verified))
            }
        }
        .padding(.vertical, Spacing.sm)
        .padding(.leading, indent ? Spacing.xl : 0)
    }
}
