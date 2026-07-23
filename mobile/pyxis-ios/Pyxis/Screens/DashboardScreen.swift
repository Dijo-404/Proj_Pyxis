import SwiftUI

/// Dashboard tab — a native port of `DashboardScreen.tsx`. Blurred backdrop,
/// a reviewer header with sign-out, the portfolio-risk hero, command-center
/// stat tiles and the flagged-transactions trend chart.
///
/// In the RN app the "open queue" / "open case" handlers were wired but never
/// surfaced; here the "Open risk cases" tile navigates to the case queue so the
/// fully-built queue screen is reachable (honoring that wired intent).
struct DashboardScreen: View {
    @EnvironmentObject private var auth: AuthStore
    @EnvironmentObject private var workspace: WorkspaceStore
    @EnvironmentObject private var router: Router

    var body: some View {
        ZStack {
            Image("dash")
                .resizable()
                .scaledToFill()
                .blur(radius: 6)
                .ignoresSafeArea()

            if let data = workspace.data {
                content(data)
            }
        }
        .toolbar(.hidden, for: .navigationBar)
    }

    private func content(_ data: WorkspacePayload) -> some View {
        let cases = data.cases
        let critical = cases.filter { $0.currentRisk >= 80 }
        let portfolioRisk = cases.isEmpty
            ? 0
            : Int((Double(cases.map(\.currentRisk).reduce(0, +)) / Double(cases.count)).rounded())

        return ScrollView(showsIndicators: false) {
            VStack(spacing: Spacing.lg) {
                header
                hero(portfolioRisk: portfolioRisk, criticalCount: critical.count, openCases: data.dashboard.openCases)
                statGrid(data.dashboard)
                trendCard(data)
                Spacer().frame(height: Spacing.xxl)
            }
            .padding(Spacing.lg)
        }
    }

    private var header: some View {
        HStack(spacing: Spacing.md) {
            Icon(name: "user", size: 24, color: .white)
                .frame(width: 48, height: 48)
                .background(Color.black)
                .clipShape(Circle())
            VStack(alignment: .leading, spacing: 0) {
                Text("Welcome back")
                    .font(.system(size: FontSize.small))
                    .foregroundColor(PyxisColor.textMuted)
                Text(auth.user?.name ?? "")
                    .font(.system(size: FontSize.h3, weight: .bold))
                    .foregroundColor(PyxisColor.text)
            }
            Spacer()
            Button(action: auth.signOut) {
                HStack(spacing: 6) {
                    Icon(name: "sign-out", size: 13, color: PyxisColor.textMuted)
                    Text("Sign out")
                        .font(.system(size: FontSize.small, weight: .semibold))
                        .foregroundColor(PyxisColor.textMuted)
                }
                .padding(.horizontal, Spacing.md)
                .padding(.vertical, 6)
                .background(PyxisColor.surface)
                .clipShape(Capsule())
                .cardShadow()
            }
            .buttonStyle(.plain)
        }
    }

    private func hero(portfolioRisk: Int, criticalCount: Int, openCases: Int) -> some View {
        ZStack {
            Image("hero").resizable().scaledToFill()
            Color.black.opacity(0.05)
            VStack(alignment: .leading, spacing: Spacing.sm) {
                Text("Portfolio risk exposure")
                    .font(.system(size: FontSize.small, weight: .semibold))
                    .foregroundColor(Color.white.opacity(0.9))
                HStack(alignment: .bottom, spacing: 0) {
                    Text("\(portfolioRisk)")
                        .font(.system(size: 44, weight: .black))
                        .foregroundColor(PyxisColor.onPrimary)
                    Text(" / 100")
                        .font(.system(size: FontSize.h3, weight: .bold))
                        .foregroundColor(Color.white.opacity(0.85))
                        .padding(.bottom, 6)
                }
                ProgressBar(value: Double(portfolioRisk), color: PyxisColor.onPrimary, track: Color.white.opacity(0.3), height: 10)
                HStack {
                    Text("\(criticalCount) critical · \(openCases) open cases")
                        .font(.system(size: FontSize.small, weight: .semibold))
                        .foregroundColor(PyxisColor.onPrimary)
                    Spacer()
                    HStack(spacing: 6) {
                        Circle().fill(PyxisColor.onPrimary).frame(width: 6, height: 6)
                        Text("Local Gemma · online")
                            .font(.system(size: FontSize.tiny, weight: .bold))
                            .foregroundColor(PyxisColor.onPrimary)
                    }
                    .padding(.horizontal, Spacing.md)
                    .padding(.vertical, 4)
                    .background(Color.white.opacity(0.22))
                    .clipShape(Capsule())
                }
                .padding(.top, Spacing.xs)
            }
            .padding(Spacing.lg)
        }
        .clipShape(RoundedRectangle(cornerRadius: Radius.lg, style: .continuous))
        .floatingShadow()
    }

    private func statGrid(_ dashboard: DashboardStats) -> some View {
        VStack(spacing: Spacing.md) {
            HStack(spacing: Spacing.md) {
                StatTile(
                    value: dashboard.transactionsAnalyzed.formatted(),
                    label: "Transactions analyzed",
                    delta: "+12%",
                    icon: "bar-chart"
                )
                Button { router.push(.queue) } label: {
                    StatTile(
                        value: "\(dashboard.openCases)",
                        label: "Open risk cases",
                        delta: "+2",
                        accent: PyxisColor.accent,
                        icon: "folder-open"
                    )
                }
                .buttonStyle(.plain)
            }
            HStack(spacing: Spacing.md) {
                StatTile(
                    value: "\(dashboard.criticalCases)",
                    label: "Critical cases",
                    accent: PyxisColor.critical,
                    icon: "exclamation-triangle"
                )
                StatTile(
                    value: "\(dashboard.pendingReviews)",
                    label: "Pending reviews",
                    accent: PyxisColor.medium,
                    icon: "clock-o"
                )
            }
        }
    }

    private func trendCard(_ data: WorkspacePayload) -> some View {
        Card {
            VStack(alignment: .leading, spacing: 0) {
                SectionTitle("Flagged transactions") {
                    Text("This week")
                        .font(.system(size: FontSize.small, weight: .semibold))
                        .foregroundColor(PyxisColor.textFaint)
                }
                MiniBarChart(data: data.flaggedTrend, color: PyxisColor.accent)
                HStack {
                    legendItem(color: PyxisColor.low, text: "Cleared today: \(data.dashboard.clearedToday)")
                    Spacer()
                    legendItem(color: PyxisColor.primary, text: "False-positive rate: \(data.dashboard.falsePositiveRate.clean)%")
                }
                .padding(.top, Spacing.md)
            }
        }
    }

    private func legendItem(color: Color, text: String) -> some View {
        HStack(spacing: 6) {
            Circle().fill(color).frame(width: 8, height: 8)
            Text(text)
                .font(.system(size: FontSize.tiny))
                .foregroundColor(PyxisColor.textMuted)
        }
    }
}

extension Double {
    /// Render without a trailing ".0" (matches JS number formatting).
    var clean: String {
        truncatingRemainder(dividingBy: 1) == 0
            ? String(Int(self))
            : String(self)
    }
}
