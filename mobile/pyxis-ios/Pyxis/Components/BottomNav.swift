import SwiftUI

/// Floating bottom navigation, a native port of `components/BottomNav.tsx`.
/// A translucent pill with three circular items (dashboard / risks / profile);
/// the active item is a filled black circle, matching the product design. SF
/// Symbols replace the Feather glyphs.
struct BottomNav: View {
    let active: AppTab
    let onSelect: (AppTab) -> Void

    var body: some View {
        HStack(spacing: Spacing.sm) {
            ForEach(AppTab.allCases, id: \.self) { tab in
                Button { onSelect(tab) } label: {
                    Image(systemName: tab.sfSymbol)
                        .font(.system(size: 20, weight: .semibold))
                        .foregroundColor(active == tab ? .white : Color(hex: 0x9A9A9A))
                        .frame(width: 46, height: 46)
                        .background(active == tab ? Color.black : Color.clear)
                        .clipShape(Circle())
                        .overlay(
                            Circle().stroke(active == tab ? Color.black : Color.black.opacity(0.27), lineWidth: 1.5)
                        )
                        .scaleEffect(active == tab ? 1.1 : 1)
                        .animation(.spring(response: 0.35, dampingFraction: 0.7), value: active)
                }
                .buttonStyle(.plain)
            }
        }
        .padding(.horizontal, Spacing.sm)
        .frame(height: 68)
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 38, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 38, style: .continuous)
                .stroke(Color.white.opacity(0.6), lineWidth: 1.5)
        )
        .shadow(color: Color.black.opacity(0.18), radius: 10, x: 0, y: 10)
        .padding(.bottom, Spacing.lg)
    }
}
