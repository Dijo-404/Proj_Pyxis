import SwiftUI

/// Customer Risk tab — a native port of `CustomerRiskScreen.tsx`. Blurred
/// backdrop, one card per case with a risk-score bar and the recommended
/// "safer workflow" next step; tapping a card opens the case detail.
struct CustomerRiskScreen: View {
    @EnvironmentObject private var workspace: WorkspaceStore
    @EnvironmentObject private var router: Router

    var body: some View {
        ZStack {
            Image("risk")
                .resizable()
                .scaledToFill()
                .blur(radius: 6)
                .ignoresSafeArea()

            VStack(spacing: 0) {
                Text("Customer Risk")
                    .font(.system(size: FontSize.h3, weight: .bold))
                    .foregroundColor(.white)
                    .padding(.vertical, Spacing.md)

                ScrollView(showsIndicators: false) {
                    VStack(alignment: .leading, spacing: Spacing.md) {
                        Text("Customer risk & safer workflow")
                            .font(.system(size: FontSize.h3, weight: .bold))
                            .foregroundColor(.white)
                            .padding(.bottom, Spacing.xs)

                        ForEach(workspace.data?.cases ?? []) { item in
                            Button { router.push(.caseDetail(caseId: item.id)) } label: {
                                CustomerRiskCard(data: item)
                            }
                            .buttonStyle(.plain)
                        }
                        Spacer().frame(height: Spacing.xxl)
                    }
                    .padding(Spacing.lg)
                }
            }
        }
        .toolbar(.hidden, for: .navigationBar)
    }
}

private struct CustomerRiskCard: View {
    let data: RiskCase

    var body: some View {
        let color = riskBand(data.currentRisk).color
        VStack(spacing: 0) {
            HStack(spacing: Spacing.md) {
                Text(String(data.customerName.prefix(1)))
                    .font(.system(size: FontSize.h3, weight: .bold))
                    .foregroundColor(.white)
                    .frame(width: 42, height: 42)
                    .background(Color(hex: 0x1A1A1A))
                    .clipShape(RoundedRectangle(cornerRadius: 12, style: .continuous))
                VStack(alignment: .leading, spacing: 1) {
                    Text(data.customerName)
                        .font(.system(size: FontSize.body, weight: .bold))
                        .foregroundColor(.black)
                        .lineLimit(1)
                    Text("\(data.customerType) · \(data.business)")
                        .font(.system(size: FontSize.small))
                        .foregroundColor(Color(hex: 0x666666))
                }
                Spacer()
                RiskBadge(score: data.currentRisk)
            }

            HStack(spacing: Spacing.md) {
                Text("Risk score")
                    .font(.system(size: FontSize.tiny))
                    .foregroundColor(Color(hex: 0x666666))
                    .frame(width: 58, alignment: .leading)
                ProgressBar(value: Double(data.currentRisk), color: color)
                Text("\(data.currentRisk)")
                    .font(.system(size: FontSize.body, weight: .bold))
                    .foregroundColor(color)
                    .frame(width: 30, alignment: .trailing)
            }
            .padding(.top, Spacing.lg)

            HStack(spacing: Spacing.md) {
                Icon(name: "compass", size: 16, color: .white)
                    .frame(width: 34, height: 34)
                    .background(Color(hex: 0x363636))
                    .clipShape(RoundedRectangle(cornerRadius: 10, style: .continuous))
                VStack(alignment: .leading, spacing: 2) {
                    Text("Safer workflow")
                        .font(.system(size: FontSize.tiny, weight: .bold))
                        .tracking(0.3)
                        .foregroundColor(.black)
                    Text(data.saferWorkflow.first ?? "")
                        .font(.system(size: FontSize.small))
                        .foregroundColor(.black)
                        .lineLimit(2)
                }
                Spacer()
                Icon(name: "angle-right", size: 20, color: Color(hex: 0x999999))
            }
            .padding(Spacing.md)
            .background(Color(hex: 0xF5F5F5))
            .clipShape(RoundedRectangle(cornerRadius: Radius.md, style: .continuous))
            .overlay(
                RoundedRectangle(cornerRadius: Radius.md, style: .continuous)
                    .stroke(Color(hex: 0xEEEEEE), lineWidth: 1)
            )
            .padding(.top, Spacing.md)
        }
        .padding(Spacing.lg)
        .background(Color.white)
        .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 16, style: .continuous)
                .stroke(Color(hex: 0xF0F0F0), lineWidth: 1.5)
        )
        .shadow(color: Color.black.opacity(0.1), radius: 8, x: 0, y: 8)
    }
}
