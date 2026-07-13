export const fuzionTokens = {
  colors: {
    background: "#FAFAF8",
    surface: "#FFFFFF",
    elevatedSurface: "#F8FAFC",
    textPrimary: "#0F172A",
    textSecondary: "#475569",
    textMuted: "#64748B",
    accent: "#D95A4E",
    accentSoft: "#FFF1EE",
    primaryNavy: "#0F172A",
    secondaryNavy: "#1E293B",
    build: "#0F172A",
    advise: "#D95A4E",
    protect: "#047857",
    buildSoft: "#E2E8F0",
    adviseSoft: "#FFF1EE",
    protectSoft: "#ECFDF5",
    lifecycleBase: "#CBD5E1",
    success: "#16A34A",
    warning: "#D97706",
    error: "#DC2626",
    border: "#E2E8F0",
    borderStrong: "#CBD5E1"
  },
  typography: {
    fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
    h1: "text-3xl font-semibold tracking-normal text-[#0F172A] sm:text-4xl",
    h2: "text-xl font-semibold tracking-normal text-[#0F172A]",
    h3: "text-base font-semibold tracking-normal text-[#0F172A]",
    body: "text-sm leading-6 text-[#334155]",
    small: "text-xs leading-5 text-[#64748B]",
    label: "text-[11px] font-semibold uppercase tracking-[0.18em] text-[#64748B]"
  },
  spacing: {
    pageX: "px-4 sm:px-6 lg:px-8",
    pageY: "py-6",
    sectionGap: "space-y-6",
    cardPadding: "p-5"
  },
  radius: {
    sm: "rounded-lg",
    md: "rounded-xl",
    lg: "rounded-2xl",
    xl: "rounded-3xl"
  },
  shadows: {
    card: "shadow-[0_12px_32px_rgba(15,23,42,0.06)]",
    panel: "shadow-[0_20px_48px_rgba(15,23,42,0.10)]",
    glow: "shadow-[0_0_0_3px_rgba(217,90,78,0.12)]"
  },
  transitions: {
    fast: "transition duration-200 ease-out",
    base: "transition duration-300 ease-out"
  },
  zIndex: {
    header: "z-40",
    overlay: "z-50"
  },
  breakpoints: {
    sm: "640px",
    md: "768px",
    lg: "1024px",
    xl: "1280px",
    "2xl": "1536px"
  }
} as const;

export const fopLifecycleTokens = {
  build: {
    cssVariable: "--fop-build",
    value: fuzionTokens.colors.build,
    label: "BUILD"
  },
  advise: {
    cssVariable: "--fop-advise",
    value: fuzionTokens.colors.advise,
    label: "ADVISE"
  },
  protect: {
    cssVariable: "--fop-protect",
    value: fuzionTokens.colors.protect,
    label: "PROTECT"
  }
} as const;
