import SwiftUI

/// Profile tab — a native port of `ProfileScreen.tsx`. Reviewer identity,
/// a user-information card, a preferences list, and the sign-out action.
struct ProfileScreen: View {
    @EnvironmentObject private var auth: AuthStore

    var body: some View {
        ScrollView(showsIndicators: false) {
            VStack(alignment: .leading, spacing: Spacing.lg) {
                profileHeader
                userInfoCard
                preferencesCard
                signOutButton
                Spacer().frame(height: Spacing.xxl)
            }
            .padding(Spacing.lg)
        }
        .background(PyxisColor.bg)
        .toolbar(.hidden, for: .navigationBar)
    }

    private var profileHeader: some View {
        HStack(alignment: .top, spacing: Spacing.lg) {
            Text(String(auth.user?.name.prefix(1) ?? "P"))
                .font(.system(size: FontSize.h1, weight: .black))
                .foregroundColor(PyxisColor.onPrimary)
                .frame(width: 70, height: 70)
                .background(PyxisColor.primary)
                .clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous))
                .cardShadow()
            VStack(alignment: .leading, spacing: Spacing.xs) {
                Text(auth.user?.name ?? "")
                    .font(.system(size: FontSize.h2, weight: .bold))
                    .foregroundColor(PyxisColor.text)
                Text(auth.user?.role ?? "")
                    .font(.system(size: FontSize.small))
                    .foregroundColor(PyxisColor.textMuted)
                Text(auth.user?.email ?? "")
                    .font(.system(size: FontSize.tiny))
                    .foregroundColor(PyxisColor.textFaint)
            }
            Spacer()
        }
    }

    private var userInfoCard: some View {
        Card {
            VStack(alignment: .leading, spacing: 0) {
                Text("User Information")
                    .font(.system(size: FontSize.h3, weight: .bold))
                    .foregroundColor(PyxisColor.text)
                    .padding(.bottom, Spacing.sm)
                PyxisDivider()
                infoRow(label: "Officer ID", value: auth.user?.id ?? "")
                infoRow(label: "Role", value: auth.user?.role ?? "")
                infoRow(label: "Email", value: auth.user?.email ?? "")
            }
        }
    }

    private func infoRow(label: String, value: String) -> some View {
        HStack {
            Text(label)
                .font(.system(size: FontSize.small))
                .foregroundColor(PyxisColor.textMuted)
            Spacer()
            Text(value)
                .font(.system(size: FontSize.small, weight: .semibold))
                .foregroundColor(PyxisColor.text)
        }
        .padding(.vertical, Spacing.md)
    }

    private var preferencesCard: some View {
        Card {
            VStack(alignment: .leading, spacing: 0) {
                Text("Preferences")
                    .font(.system(size: FontSize.h3, weight: .bold))
                    .foregroundColor(PyxisColor.text)
                    .padding(.bottom, Spacing.sm)
                PyxisDivider()
                prefRow(icon: "bell", text: "Notifications")
                prefRow(icon: "shield", text: "Security")
                prefRow(icon: "sliders", text: "Settings")
            }
        }
    }

    private func prefRow(icon: String, text: String) -> some View {
        HStack(spacing: Spacing.md) {
            Icon(name: icon, size: 16, color: PyxisColor.primary)
                .frame(width: 36, height: 36)
                .background(PyxisColor.primarySoft)
                .clipShape(RoundedRectangle(cornerRadius: 10, style: .continuous))
            Text(text)
                .font(.system(size: FontSize.body, weight: .semibold))
                .foregroundColor(PyxisColor.text)
            Spacer()
            Icon(name: "angle-right", size: 16, color: PyxisColor.textFaint)
        }
        .padding(.vertical, Spacing.md)
    }

    private var signOutButton: some View {
        Button(action: auth.signOut) {
            HStack(spacing: Spacing.sm) {
                Icon(name: "sign-out", size: 16, color: PyxisColor.critical)
                Text("Sign Out")
                    .font(.system(size: FontSize.body, weight: .bold))
                    .foregroundColor(PyxisColor.critical)
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, Spacing.lg)
            .background(PyxisColor.critical.opacity(0.08))
            .clipShape(RoundedRectangle(cornerRadius: Radius.md, style: .continuous))
            .overlay(
                RoundedRectangle(cornerRadius: Radius.md, style: .continuous)
                    .stroke(PyxisColor.critical.opacity(0.19), lineWidth: 1.5)
            )
        }
        .buttonStyle(.plain)
    }
}
