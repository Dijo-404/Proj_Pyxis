import SwiftUI

/// Reusable UI primitives for the Pyxis iOS app, ported from
/// `mobile/pyxis/src/components/ui.tsx`.

// MARK: - Card

struct Card<Content: View>: View {
    var padded: Bool = true
    let content: Content

    init(padded: Bool = true, @ViewBuilder content: () -> Content) {
        self.padded = padded
        self.content = content()
    }

    var body: some View {
        content
            .padding(padded ? Spacing.lg : 0)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(PyxisColor.surface)
            .clipShape(RoundedRectangle(cornerRadius: Radius.lg, style: .continuous))
            .cardShadow()
    }
}

// MARK: - Section title

struct SectionTitle<Right: View>: View {
    let title: String
    @ViewBuilder var right: Right

    init(_ title: String, @ViewBuilder right: () -> Right) {
        self.title = title
        self.right = right()
    }

    var body: some View {
        HStack {
            Text(title)
                .font(.system(size: FontSize.h3, weight: .bold))
                .foregroundColor(PyxisColor.text)
            Spacer()
            right
        }
        .padding(.bottom, Spacing.md)
    }
}

extension SectionTitle where Right == EmptyView {
    init(_ title: String) {
        self.init(title) { EmptyView() }
    }
}

// MARK: - Pill

struct Pill: View {
    let label: String
    let color: Color
    let soft: Color

    var body: some View {
        Text(label)
            .font(.system(size: FontSize.tiny, weight: .bold))
            .tracking(0.3)
            .foregroundColor(color)
            .padding(.horizontal, Spacing.md)
            .padding(.vertical, 5)
            .background(soft)
            .clipShape(Capsule())
    }
}

// MARK: - Risk badge

struct RiskBadge: View {
    let score: Int

    var body: some View {
        let band = riskBand(score)
        return HStack(spacing: 6) {
            Circle()
                .fill(band.color)
                .frame(width: 7, height: 7)
            Text("\(band.label) · \(score)")
                .font(.system(size: FontSize.small, weight: .bold))
                .foregroundColor(band.color)
        }
        .padding(.horizontal, Spacing.md)
        .padding(.vertical, 6)
        .background(band.soft)
        .clipShape(Capsule())
    }
}

// MARK: - Progress bar

struct ProgressBar: View {
    let value: Double // 0-100
    var color: Color = PyxisColor.primary
    var track: Color = PyxisColor.divider
    var height: CGFloat = 8

    var body: some View {
        let clamped = max(0, min(100, value))
        GeometryReader { geo in
            ZStack(alignment: .leading) {
                Capsule().fill(track)
                Capsule()
                    .fill(color)
                    .frame(width: geo.size.width * clamped / 100)
            }
        }
        .frame(height: height)
        .clipShape(Capsule())
    }
}

// MARK: - Primary button

struct PrimaryButton: View {
    let title: String
    let action: () -> Void
    var loading: Bool = false
    var disabled: Bool = false
    var variant: Variant = .solid
    var color: Color = PyxisColor.primary
    var icon: String? = nil

    enum Variant { case solid, outline }

    var body: some View {
        let isOutline = variant == .outline
        let fg = isOutline ? color : PyxisColor.onPrimary
        Button(action: action) {
            ZStack {
                if loading {
                    ProgressView().tint(fg)
                } else {
                    HStack(spacing: Spacing.sm) {
                        if let icon { Icon(name: icon, size: 16, color: fg) }
                        Text(title)
                            .font(.system(size: FontSize.body, weight: .bold))
                            .foregroundColor(fg)
                    }
                }
            }
            .frame(maxWidth: .infinity)
            .frame(height: 52)
            .background(
                RoundedRectangle(cornerRadius: Radius.md, style: .continuous)
                    .fill(isOutline ? Color.clear : color)
            )
            .overlay(
                RoundedRectangle(cornerRadius: Radius.md, style: .continuous)
                    .stroke(color, lineWidth: isOutline ? 1.5 : 0)
            )
            .opacity(disabled || loading ? 0.6 : 1)
        }
        .disabled(disabled || loading)
        .buttonStyle(.plain)
    }
}

// MARK: - Stat tile

struct StatTile: View {
    let value: String
    let label: String
    var delta: String? = nil
    var accent: Color = PyxisColor.primary
    var icon: String? = nil

    var body: some View {
        Card {
            VStack(alignment: .leading, spacing: 0) {
                HStack {
                    if let icon {
                        Icon(name: icon, size: 15, color: accent)
                            .frame(width: 30, height: 30)
                            .background(accent.opacity(0.1))
                            .clipShape(RoundedRectangle(cornerRadius: 9, style: .continuous))
                    } else {
                        Spacer().frame(height: 20)
                    }
                    Spacer()
                    if let delta {
                        Text(delta)
                            .font(.system(size: FontSize.tiny, weight: .bold))
                            .foregroundColor(accent)
                    }
                }
                Text(value)
                    .font(.system(size: FontSize.h2, weight: .bold))
                    .foregroundColor(PyxisColor.text)
                    .padding(.top, Spacing.sm)
                Text(label)
                    .font(.system(size: FontSize.small))
                    .foregroundColor(PyxisColor.textMuted)
                    .padding(.top, 2)
            }
        }
    }
}

// MARK: - Mini bar chart (no external deps)

struct MiniBarChart: View {
    let data: [TrendPoint]
    var color: Color = PyxisColor.primary
    var height: CGFloat = 120

    var body: some View {
        let maxValue = max(data.map(\.value).max() ?? 1, 1)
        HStack(alignment: .bottom, spacing: 0) {
            ForEach(data) { point in
                VStack(spacing: 6) {
                    Spacer(minLength: 0)
                    Capsule()
                        .fill(color)
                        .frame(
                            width: 14,
                            height: max(6, CGFloat(point.value) / CGFloat(maxValue) * (height - 34))
                        )
                    Text(point.label)
                        .font(.system(size: FontSize.tiny))
                        .foregroundColor(PyxisColor.textFaint)
                }
                .frame(maxWidth: .infinity)
            }
        }
        .frame(height: height)
    }
}

// MARK: - Score gauge (native ring)

struct ScoreGauge: View {
    let value: Int // 0-100
    var size: CGFloat = 120
    var color: Color = PyxisColor.critical
    var label: String? = nil
    var caption: String? = nil

    var body: some View {
        let clamped = max(0, min(100, value))
        let stroke = size * 0.09
        VStack(spacing: 6) {
            ZStack {
                Circle()
                    .stroke(PyxisColor.divider, lineWidth: stroke)
                Circle()
                    .trim(from: 0, to: CGFloat(clamped) / 100)
                    .stroke(color, style: StrokeStyle(lineWidth: stroke, lineCap: .round))
                    .rotationEffect(.degrees(-90))
                VStack(spacing: 0) {
                    Text("\(clamped)")
                        .font(.system(size: size * 0.28, weight: .black))
                        .foregroundColor(color)
                    if let label {
                        Text(label)
                            .font(.system(size: FontSize.tiny, weight: .bold))
                            .tracking(0.4)
                            .foregroundColor(PyxisColor.textMuted)
                    }
                }
            }
            .frame(width: size, height: size)
            if let caption {
                Text(caption)
                    .font(.system(size: FontSize.tiny))
                    .foregroundColor(PyxisColor.textFaint)
            }
        }
    }
}

// MARK: - Chip

struct Chip: View {
    let label: String
    var icon: String? = nil
    var color: Color = PyxisColor.textMuted
    var soft: Color = PyxisColor.surfaceAlt

    var body: some View {
        HStack(spacing: 5) {
            if let icon { Icon(name: icon, size: 11, color: color) }
            Text(label)
                .font(.system(size: FontSize.tiny, weight: .bold))
                .tracking(0.2)
                .foregroundColor(color)
        }
        .padding(.horizontal, Spacing.md)
        .padding(.vertical, 5)
        .background(soft)
        .clipShape(Capsule())
    }
}

// MARK: - Divider

struct PyxisDivider: View {
    var body: some View {
        Rectangle()
            .fill(PyxisColor.divider)
            .frame(height: 1)
            .padding(.vertical, Spacing.md)
    }
}

// MARK: - Labeled row

struct LabelValue: View {
    let label: String
    let value: String

    var body: some View {
        HStack {
            Text(label)
                .font(.system(size: FontSize.small))
                .foregroundColor(PyxisColor.textMuted)
            Spacer()
            Text(value)
                .font(.system(size: FontSize.small, weight: .semibold))
                .foregroundColor(PyxisColor.text)
                .lineLimit(1)
        }
        .padding(.vertical, 7)
    }
}

// MARK: - Inline nav title + subtitle (native principal toolbar helper)

struct NavTitle: View {
    let title: String
    var subtitle: String? = nil

    var body: some View {
        VStack(spacing: 1) {
            Text(title)
                .font(.system(size: FontSize.h3, weight: .bold))
                .foregroundColor(PyxisColor.text)
                .lineLimit(1)
            if let subtitle {
                Text(subtitle)
                    .font(.system(size: FontSize.tiny))
                    .foregroundColor(PyxisColor.textMuted)
            }
        }
    }
}
