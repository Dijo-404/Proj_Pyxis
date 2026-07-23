import SwiftUI
import UIKit

/// Login screen — a native port of `LoginScreen.tsx`. Teal hero over a white
/// sheet, email + password with the same validation rules (valid email and a
/// password of at least six characters), remember-me toggle, and the local-only
/// privacy note.
struct LoginScreen: View {
    @EnvironmentObject private var auth: AuthStore

    @State private var email = ""
    @State private var password = ""
    @State private var remember = true
    @State private var error: String? = nil

    var body: some View {
        ZStack(alignment: .top) {
            PyxisColor.primary.ignoresSafeArea()

            ScrollView {
                VStack(spacing: 0) {
                    hero
                    sheet
                }
            }
            .scrollDismissesKeyboard(.interactively)
        }
    }

    private var hero: some View {
        VStack(alignment: .leading, spacing: 0) {
            HStack(spacing: Spacing.sm) {
                Icon(name: "compass", size: 20, color: PyxisColor.onPrimary)
                    .frame(width: 34, height: 34)
                    .background(Color.white.opacity(0.2))
                    .clipShape(RoundedRectangle(cornerRadius: 10, style: .continuous))
                Text("PYXIS")
                    .font(.system(size: FontSize.h3, weight: .black))
                    .tracking(2)
                    .foregroundColor(PyxisColor.onPrimary)
            }
            .padding(.top, Spacing.lg)
            .padding(.bottom, Spacing.xl)

            Text("Log in to stay on\ntop of your risk cases.")
                .font(.system(size: FontSize.h1, weight: .heavy))
                .foregroundColor(PyxisColor.onPrimary)

            Text("Private, on-premise financial compliance intelligence powered by Gemma.")
                .font(.system(size: FontSize.small))
                .foregroundColor(Color.white.opacity(0.85))
                .padding(.top, Spacing.md)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(.horizontal, Spacing.xl)
        .padding(.bottom, Spacing.xxl)
    }

    private var sheet: some View {
        VStack(spacing: Spacing.md) {
            Icon(name: "user", size: 32, color: .white)
                .frame(width: 72, height: 72)
                .background(PyxisColor.primary)
                .clipShape(Circle())
                .padding(.top, 5)
                .padding(.bottom, Spacing.xl)

            field(icon: "envelope-o", placeholder: "Email address", text: $email, secure: false)
                .textInputAutocapitalization(.never)
                .keyboardType(.emailAddress)
            field(icon: "lock", placeholder: "Password", text: $password, secure: true)

            HStack {
                Button {
                    remember.toggle()
                } label: {
                    HStack(spacing: Spacing.sm) {
                        ZStack {
                            RoundedRectangle(cornerRadius: 6, style: .continuous)
                                .stroke(remember ? PyxisColor.primary : PyxisColor.border, lineWidth: 1.5)
                                .background(
                                    RoundedRectangle(cornerRadius: 6, style: .continuous)
                                        .fill(remember ? PyxisColor.primary : Color.clear)
                                )
                                .frame(width: 20, height: 20)
                            if remember {
                                Icon(name: "check", size: 12, color: PyxisColor.onPrimary)
                            }
                        }
                        Text("Remember Me")
                            .font(.system(size: FontSize.small))
                            .foregroundColor(PyxisColor.textMuted)
                    }
                }
                .buttonStyle(.plain)
                Spacer()
                Text("Forgot Password?")
                    .font(.system(size: FontSize.small, weight: .bold))
                    .foregroundColor(PyxisColor.primary)
            }
            .padding(.vertical, Spacing.sm)

            if let error {
                Text(error)
                    .font(.system(size: FontSize.small))
                    .foregroundColor(PyxisColor.critical)
                    .frame(maxWidth: .infinity, alignment: .leading)
            }

            PrimaryButton(title: "Login", action: login)
                .padding(.top, Spacing.lg)

            HStack(alignment: .top, spacing: Spacing.sm) {
                Icon(name: "shield", size: 15, color: PyxisColor.textFaint)
                Text("No customer data leaves this device — all reasoning runs on the local Gemma runtime.")
                    .font(.system(size: FontSize.tiny))
                    .foregroundColor(PyxisColor.textFaint)
                Spacer(minLength: 0)
            }
            .padding(.top, Spacing.xl)
        }
        .padding(.horizontal, Spacing.xl)
        .padding(.top, Spacing.xxl)
        .padding(.bottom, Spacing.xxl)
        .frame(maxWidth: .infinity)
        .background(PyxisColor.surface)
        .clipShape(RoundedCorner(radius: Radius.xl, corners: [.topLeft, .topRight]))
        .offset(y: -Spacing.xl)
    }

    private func field(icon: String, placeholder: String, text: Binding<String>, secure: Bool) -> some View {
        HStack(spacing: Spacing.md) {
            Icon(name: icon, size: 16, color: PyxisColor.textFaint)
            Group {
                if secure {
                    SecureField(placeholder, text: text)
                } else {
                    TextField(placeholder, text: text)
                }
            }
            .font(.system(size: FontSize.body))
            .foregroundColor(PyxisColor.text)
        }
        .padding(.horizontal, Spacing.lg)
        .frame(height: 54)
        .background(PyxisColor.bg)
        .clipShape(RoundedRectangle(cornerRadius: Radius.md, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: Radius.md, style: .continuous)
                .stroke(PyxisColor.border, lineWidth: 1)
        )
    }

    private func login() {
        error = nil
        let result = auth.signIn(email: email, password: password)
        if !result.ok { error = result.error ?? "Login failed" }
    }
}

/// A rounded-corner shape for selectively rounding the top of the login sheet.
struct RoundedCorner: Shape {
    var radius: CGFloat
    var corners: UIRectCorner

    func path(in rect: CGRect) -> Path {
        Path(UIBezierPath(
            roundedRect: rect,
            byRoundingCorners: corners,
            cornerRadii: CGSize(width: radius, height: radius)
        ).cgPath)
    }
}
