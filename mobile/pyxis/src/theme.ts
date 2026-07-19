/**
 * Pyxis design tokens.
 * Teal primary / orange accent, matching the approved product reference.
 */

export const colors = {
  // Brand
  primary: '#1BA7A0', // teal
  primaryDark: '#0E6E6A',
  primaryLight: '#5FD0C9',
  primarySoft: '#E4F6F5',

  accent: '#F2792B', // orange
  accentSoft: '#FDEBDD',

  // Surfaces
  bg: '#F4F6F8',
  surface: '#FFFFFF',
  surfaceAlt: '#F0FBFA',

  // Text
  text: '#0F1D26',
  textMuted: '#5B6B76',
  textFaint: '#93A1AB',
  onPrimary: '#FFFFFF',

  // Risk semantics
  critical: '#E4453A',
  criticalSoft: '#FDE5E3',
  high: '#F2792B',
  highSoft: '#FDEBDD',
  medium: '#E0A83B',
  mediumSoft: '#FBF1DC',
  low: '#2FA96B',
  lowSoft: '#E0F4EA',

  // Scenario categories
  legit: '#2FA96B',
  suspicious: '#E4453A',
  uncertain: '#8A7BD8',

  border: '#E4E9ED',
  divider: '#EEF1F4',
  shadow: '#0F1D26',
} as const;

export const spacing = {
  xs: 4,
  sm: 8,
  md: 12,
  lg: 16,
  xl: 24,
  xxl: 32,
} as const;

export const radius = {
  sm: 8,
  md: 12,
  lg: 18,
  xl: 26,
  pill: 999,
} as const;

export const font = {
  h1: 28,
  h2: 22,
  h3: 18,
  body: 15,
  small: 13,
  tiny: 11,
} as const;

export const shadow = {
  card: {
    shadowColor: colors.shadow,
    shadowOpacity: 0.06,
    shadowRadius: 14,
    shadowOffset: { width: 0, height: 6 },
    elevation: 3,
  },
  floating: {
    shadowColor: colors.shadow,
    shadowOpacity: 0.12,
    shadowRadius: 20,
    shadowOffset: { width: 0, height: 10 },
    elevation: 8,
  },
} as const;

/** Map a numeric risk score (0-100) to a semantic risk band. */
export function riskBand(score: number): {
  label: string;
  color: string;
  soft: string;
} {
  if (score >= 80) return { label: 'Critical', color: colors.critical, soft: colors.criticalSoft };
  if (score >= 60) return { label: 'High', color: colors.high, soft: colors.highSoft };
  if (score >= 35) return { label: 'Medium', color: colors.medium, soft: colors.mediumSoft };
  return { label: 'Low', color: colors.low, soft: colors.lowSoft };
}
