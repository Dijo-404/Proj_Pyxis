import SwiftUI

/// Central icon component. The RN app used FontAwesome + Feather glyphs; on iOS
/// we translate those to the equivalent SF Symbols (per HIG) so the UI reads as
/// a real native product. `Icon(name:)` accepts the original RN glyph names so
/// screen code stays a close mirror of the React Native source.
struct Icon: View {
    let name: String
    var size: CGFloat = 18
    var color: Color = PyxisColor.text

    var body: some View {
        Image(systemName: Icon.symbol(for: name))
            .font(.system(size: size, weight: .semibold))
            .foregroundColor(color)
    }

    /// Map an RN (FontAwesome / Feather) glyph name to an SF Symbol.
    static func symbol(for name: String) -> String {
        switch name {
        case "compass": return "safari"
        case "user": return "person.fill"
        case "envelope-o", "envelope": return "envelope"
        case "lock": return "lock.fill"
        case "check": return "checkmark"
        case "shield": return "shield.fill"
        case "sign-out": return "rectangle.portrait.and.arrow.right"
        case "bar-chart": return "chart.bar.fill"
        case "folder-open": return "folder.fill"
        case "exclamation-triangle": return "exclamationmark.triangle.fill"
        case "clock-o": return "clock"
        case "home": return "house.fill"
        case "angle-right": return "chevron.right"
        case "angle-left": return "chevron.left"
        case "bell": return "bell.fill"
        case "sliders": return "slider.horizontal.3"
        case "magic": return "wand.and.stars"
        case "flask": return "testtube.2"
        case "bolt": return "bolt.fill"
        case "check-circle": return "checkmark.circle.fill"
        case "times-circle": return "xmark.circle.fill"
        case "question-circle": return "questionmark.circle.fill"
        case "adjust": return "circle.lefthalf.filled"
        case "arrow-circle-right": return "arrow.right.circle.fill"
        case "long-arrow-right": return "arrow.right"
        case "long-arrow-down": return "arrow.down"
        case "level-down": return "arrow.turn.down.right"
        case "paper-plane": return "paperplane.fill"
        case "microchip": return "cpu"
        case "server": return "server.rack"
        case "hashtag": return "number"
        case "calculator": return "function"
        case "exclamation-circle": return "exclamationmark.circle.fill"
        case "exclamation": return "exclamationmark"
        case "dot-circle-o": return "smallcircle.filled.circle"
        case "circle-o": return "circle"
        case "times": return "xmark"
        case "sign-in": return "arrow.right.to.line"
        case "university": return "building.columns.fill"
        default: return "circle"
        }
    }
}
