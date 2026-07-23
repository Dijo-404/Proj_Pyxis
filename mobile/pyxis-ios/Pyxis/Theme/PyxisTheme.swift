import SwiftUI

/// Pyxis design tokens.
///
/// A 1:1 native port of `mobile/pyxis/src/theme.ts` — teal primary / orange
/// accent, matching the approved product reference. Keeping the names and
/// values identical keeps the SwiftUI and React Native codebases conceptually
/// mirrored.
enum PyxisColor {
    // Brand
    static let primary = Color(hex: 0x1BA7A0) // teal
    static let primaryDark = Color(hex: 0x0E6E6A)
    static let primaryLight = Color(hex: 0x5FD0C9)
    static let primarySoft = Color(hex: 0xE4F6F5)

    static let accent = Color(hex: 0xF2792B) // orange
    static let accentSoft = Color(hex: 0xFDEBDD)

    // Surfaces
    static let bg = Color(hex: 0xF4F6F8)
    static let surface = Color(hex: 0xFFFFFF)
    static let surfaceAlt = Color(hex: 0xF0FBFA)

    // Text
    static let text = Color(hex: 0x0F1D26)
    static let textMuted = Color(hex: 0x5B6B76)
    static let textFaint = Color(hex: 0x93A1AB)
    static let onPrimary = Color(hex: 0xFFFFFF)

    // Risk semantics
    static let critical = Color(hex: 0xE4453A)
    static let criticalSoft = Color(hex: 0xFDE5E3)
    static let high = Color(hex: 0xF2792B)
    static let highSoft = Color(hex: 0xFDEBDD)
    static let medium = Color(hex: 0xE0A83B)
    static let mediumSoft = Color(hex: 0xFBF1DC)
    static let low = Color(hex: 0x2FA96B)
    static let lowSoft = Color(hex: 0xE0F4EA)

    // Scenario categories
    static let legit = Color(hex: 0x2FA96B)
    static let suspicious = Color(hex: 0xE4453A)
    static let uncertain = Color(hex: 0x8A7BD8)

    static let border = Color(hex: 0xE4E9ED)
    static let divider = Color(hex: 0xEEF1F4)
    static let shadow = Color(hex: 0x0F1D26)
}

enum Spacing {
    static let xs: CGFloat = 4
    static let sm: CGFloat = 8
    static let md: CGFloat = 12
    static let lg: CGFloat = 16
    static let xl: CGFloat = 24
    static let xxl: CGFloat = 32
}

enum Radius {
    static let sm: CGFloat = 8
    static let md: CGFloat = 12
    static let lg: CGFloat = 18
    static let xl: CGFloat = 26
    static let pill: CGFloat = 999
}

enum FontSize {
    static let h1: CGFloat = 28
    static let h2: CGFloat = 22
    static let h3: CGFloat = 18
    static let body: CGFloat = 15
    static let small: CGFloat = 13
    static let tiny: CGFloat = 11
}

/// A semantic risk band derived from a 0-100 score, mirroring `riskBand`.
struct RiskBand {
    let label: String
    let color: Color
    let soft: Color
}

func riskBand(_ score: Int) -> RiskBand {
    if score >= 80 { return RiskBand(label: "Critical", color: PyxisColor.critical, soft: PyxisColor.criticalSoft) }
    if score >= 60 { return RiskBand(label: "High", color: PyxisColor.high, soft: PyxisColor.highSoft) }
    if score >= 35 { return RiskBand(label: "Medium", color: PyxisColor.medium, soft: PyxisColor.mediumSoft) }
    return RiskBand(label: "Low", color: PyxisColor.low, soft: PyxisColor.lowSoft)
}

// MARK: - Shadows

extension View {
    /// Equivalent of the RN `shadow.card` token.
    func cardShadow() -> some View {
        shadow(color: PyxisColor.shadow.opacity(0.06), radius: 14 / 2, x: 0, y: 6)
    }

    /// Equivalent of the RN `shadow.floating` token.
    func floatingShadow() -> some View {
        shadow(color: PyxisColor.shadow.opacity(0.12), radius: 20 / 2, x: 0, y: 10)
    }
}

// MARK: - Hex color helper

extension Color {
    init(hex: UInt, alpha: Double = 1) {
        self.init(
            .sRGB,
            red: Double((hex >> 16) & 0xFF) / 255,
            green: Double((hex >> 8) & 0xFF) / 255,
            blue: Double(hex & 0xFF) / 255,
            opacity: alpha
        )
    }
}
