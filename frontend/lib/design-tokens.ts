export const fuzionTokens = {
  colors: {
    background: "#FFFFFF",
    appBackground: "#F8FAFC",
    surface: "#FFFFFF",
    elevatedSurface: "#F8FAFC",
    textPrimary: "#071223",
    textSecondary: "#334155",
    textMuted: "#64748B",
    accent: "#126BFF",
    accentSoft: "#EAF2FF",
    platform: "#0B1F3A",
    primaryNavy: "#0B1F3A",
    secondaryNavy: "#0B1D36",
    build: "#126BFF",
    advise: "#BFC5CE",
    protect: "#86EE62",
    halo: "#FF7A66",
    white: "#FFFFFF",
    buildText: "#0B55D9",
    adviseText: "#475569",
    protectText: "#2F7D22",
    haloText: "#B94738",
    buildSoft: "#EAF2FF",
    adviseSoft: "#F1F5F9",
    protectSoft: "#F0FCEB",
    haloSoft: "#FFF1EE",
    lifecycleBase: "#E2E8F0",
    success: "#2F7D22",
    warning: "#7C6F1E",
    error: "#B42318",
    border: "#E2E8F0",
    borderStrong: "#CBD5E1"
  },
  typography: {
    fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
    h1: "text-3xl font-semibold tracking-normal text-[color:var(--text-primary)] sm:text-4xl",
    h2: "text-xl font-semibold tracking-normal text-[color:var(--text-primary)]",
    h3: "text-base font-semibold tracking-normal text-[color:var(--text-primary)]",
    body: "text-sm leading-6 text-[color:var(--text-secondary)]",
    small: "text-xs leading-5 text-[color:var(--text-muted)]",
    label: "text-[11px] font-semibold uppercase tracking-[0.18em] text-[color:var(--fop-build)]"
  },
  spacing: {
    pageX: "px-4 sm:px-6 lg:px-8",
    pageY: "py-6",
    sectionGap: "space-y-6",
    cardPadding: "p-5"
  },
  radius: {
    sm: "rounded-md",
    md: "rounded-lg",
    lg: "rounded-xl",
    xl: "rounded-2xl"
  },
  shadows: {
    card: "shadow-sm",
    panel: "shadow-[0_18px_44px_rgba(15,23,42,0.08)]",
    glow: "shadow-[0_0_0_3px_rgba(18,107,255,0.12)]"
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
    cssVariable: "--fuzion-build",
    value: fuzionTokens.colors.build,
    textValue: fuzionTokens.colors.buildText,
    label: "BUILD"
  },
  advise: {
    cssVariable: "--fuzion-advise",
    value: fuzionTokens.colors.advise,
    textValue: fuzionTokens.colors.adviseText,
    label: "ADVISE"
  },
  protect: {
    cssVariable: "--fuzion-protect",
    value: fuzionTokens.colors.protect,
    textValue: fuzionTokens.colors.protectText,
    label: "PROTECT"
  }
} as const;
