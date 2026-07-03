export const fuzionTokens = {
  colors: {
    background: "#050A18",
    surface: "#0B1224",
    elevatedSurface: "#111827",
    textPrimary: "#FFFFFF",
    textSecondary: "#B6C1CF",
    textMuted: "#7D8CA3",
    accent: "#FF6B5F",
    accentSoft: "#FFB4AD",
    success: "#10B981",
    warning: "#F59E0B",
    error: "#EF4444",
    border: "rgba(255,255,255,0.10)",
    borderStrong: "rgba(255,255,255,0.18)"
  },
  typography: {
    fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
    h1: "text-3xl font-semibold tracking-normal text-white sm:text-4xl",
    h2: "text-xl font-semibold tracking-normal text-white",
    h3: "text-base font-semibold tracking-normal text-white",
    body: "text-sm leading-6 text-[#B6C1CF]",
    small: "text-xs leading-5 text-[#7D8CA3]",
    label: "text-[11px] font-semibold uppercase tracking-[0.18em] text-[#7D8CA3]"
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
    card: "shadow-[0_18px_60px_rgba(0,0,0,0.24)]",
    panel: "shadow-[0_24px_80px_rgba(0,0,0,0.38)]",
    glow: "shadow-[0_0_32px_rgba(255,107,95,0.18)]"
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
