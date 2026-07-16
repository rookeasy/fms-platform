"use client";

import { useId } from "react";

import type { FopLifecycleVisualStatus } from "@/lib/fop-lifecycle-visual";
import { visualStateFromProgress, wholeFLifecycleTokens } from "@/lib/fop-lifecycle-visual";

type FopLifecycleMarkProps = {
  status?: FopLifecycleVisualStatus;
  progress?: number;
  overallProgress?: number;
  saturation?: number;
  color?: string;
  textColor?: string;
  compact?: boolean;
  showStatusLabel?: boolean;
  showLabels?: boolean;
  halo?: boolean;
  haloEligible?: boolean;
  certificationStatus?: string;
  accessibleLabel?: string;
  label?: string;
  className?: string;
  title?: string;
};

function clamp(value: number) {
  return Math.max(0, Math.min(100, value));
}

function haloAllowed(status: FopLifecycleVisualStatus, halo?: boolean, haloEligible?: boolean, certificationStatus?: string) {
  if (status !== "protected") {
    return false;
  }
  if (certificationStatus) {
    return certificationStatus === "approved" && haloEligible === true;
  }
  return halo === true || haloEligible === true;
}

export function FopLifecycleMark({
  status,
  progress,
  overallProgress = 100,
  saturation,
  color,
  textColor,
  compact = false,
  showStatusLabel,
  showLabels = false,
  halo,
  haloEligible,
  certificationStatus,
  accessibleLabel,
  label,
  className = "",
  title
}: FopLifecycleMarkProps) {
  const id = useId().replace(/:/g, "");
  const mapped = visualStateFromProgress(progress ?? overallProgress, halo === true);
  const resolvedStatus = status ?? mapped.status;
  const token = wholeFLifecycleTokens[resolvedStatus];
  const resolvedLabel = label ?? token.label;
  const resolvedColor = color ?? token.color;
  const resolvedTextColor = textColor ?? token.textColor;
  const resolvedSaturation = clamp(saturation ?? mapped.saturation);
  const resolvedHalo = haloAllowed(resolvedStatus, halo ?? mapped.halo, haloEligible, certificationStatus);
  const svgLabel = title ?? accessibleLabel ?? `Fuzion building lifecycle: ${resolvedLabel}`;
  const labelVisible = (showStatusLabel || showLabels) && !compact;
  const width = labelVisible ? 92 : 64;
  const height = labelVisible ? 86 : 64;
  const opacity = 0.38 + resolvedSaturation / 100 * 0.62;

  return (
    <svg
      className={className}
      width={width}
      height={height}
      viewBox={`0 0 ${width} ${height}`}
      role="img"
      aria-label={svgLabel}
      xmlns="http://www.w3.org/2000/svg"
    >
      <title>{svgLabel}</title>
      <defs>
        <filter id={`${id}Halo`} x="-45%" y="-45%" width="190%" height="190%" colorInterpolationFilters="sRGB">
          <feGaussianBlur stdDeviation="2.5" result="blur" />
          <feColorMatrix in="blur" type="matrix" values="0 0 0 0 1 0 0 0 0 0.48 0 0 0 0 0.4 0 0 0 0.24 0" result="coralGlow" />
          <feMerge>
            <feMergeNode in="coralGlow" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>

      {resolvedHalo ? (
        <circle
          cx="32"
          cy="32"
          r="27"
          fill="none"
          stroke="var(--fuzion-halo)"
          strokeWidth="4"
          opacity="0.72"
          filter={`url(#${id}Halo)`}
        />
      ) : null}

      <path
        d="M14 10H52V22H28V30H47V42H28V54H14V10Z"
        fill={resolvedColor}
        opacity={opacity}
        className="transition-[fill,opacity] duration-300 ease-out motion-reduce:transition-none"
      />
      <path d="M14 10H52V22H28V30H47V42H28V54H14V10Z" fill="none" stroke="rgba(7,18,35,0.16)" />

      {labelVisible ? (
        <text
          x="32"
          y="78"
          fill={resolvedTextColor}
          fontFamily="Inter, Arial, sans-serif"
          fontSize="9"
          fontWeight="800"
          letterSpacing="1.4"
          textAnchor="middle"
        >
          {resolvedLabel}
        </text>
      ) : null}
    </svg>
  );
}
