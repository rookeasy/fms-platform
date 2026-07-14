"use client";

import { useId } from "react";

import type { FopLifecycleVisualStatus } from "@/lib/fop-lifecycle-visual";
import { visualStateFromProgress } from "@/lib/fop-lifecycle-visual";

type FopLifecycleMarkProps = {
  buildProgress?: number;
  adviseProgress?: number;
  protectProgress?: number;
  overallProgress?: number;
  status?: FopLifecycleVisualStatus;
  showLabels?: boolean;
  compact?: boolean;
  halo?: boolean;
  showWordmark?: boolean;
  className?: string;
  title?: string;
};

function clamp(value: number) {
  return Math.max(0, Math.min(100, value));
}

function segmentOpacity(progress: number, status?: FopLifecycleVisualStatus) {
  if (status === "protected") {
    return 1;
  }
  return progress > 0 ? 1 : 0.2;
}

export function FopLifecycleMark({
  buildProgress,
  adviseProgress,
  protectProgress,
  overallProgress = 100,
  status,
  showLabels = false,
  compact = false,
  halo,
  showWordmark = false,
  className = "",
  title
}: FopLifecycleMarkProps) {
  const id = useId().replace(/:/g, "");
  const mapped = visualStateFromProgress(overallProgress, status === "protected");
  const resolvedStatus = status ?? mapped.status;
  const resolvedBuild = clamp(buildProgress ?? mapped.buildProgress);
  const resolvedAdvise = clamp(adviseProgress ?? mapped.adviseProgress);
  const resolvedProtect = clamp(protectProgress ?? mapped.protectProgress);
  const showHalo = Boolean(halo ?? resolvedStatus === "protected");
  const label = title ?? `Lifecycle status: ${resolvedStatus.toUpperCase()}`;
  const labelsVisible = showLabels && !compact;
  const width = showWordmark ? 242 : 88;
  const height = 88;

  return (
    <svg
      className={className}
      width={width}
      height={height}
      viewBox={`0 0 ${width} ${height}`}
      role="img"
      aria-label={label}
      xmlns="http://www.w3.org/2000/svg"
    >
      <title>{label}</title>
      <defs>
        <filter id={`${id}Halo`} x="-40%" y="-40%" width="180%" height="180%" colorInterpolationFilters="sRGB">
          <feGaussianBlur stdDeviation="4.5" />
          <feColorMatrix type="matrix" values="1 0 0 0 0.91 0 1 0 0 0.47 0 0 1 0 0.45 0 0 0 0.36 0" />
          <feBlend in="SourceGraphic" mode="screen" />
        </filter>
        <clipPath id={`${id}BuildClip`}>
          <rect x="0" y="0" width={60 * (resolvedBuild / 100)} height="88" />
        </clipPath>
        <clipPath id={`${id}AdviseClip`}>
          <rect x="0" y="0" width={66 * (resolvedAdvise / 100)} height="88" />
        </clipPath>
        <clipPath id={`${id}ProtectClip`}>
          <rect x="0" y={82 - 76 * (resolvedProtect / 100)} width="88" height={76 * (resolvedProtect / 100)} />
        </clipPath>
      </defs>
      <rect x="1" y="1" width="86" height="86" rx="20" fill="#FFFFFF" stroke="#E2E8F0" />
      {showHalo ? (
        <path
          d="M20 17H67V31H35V39H59V53H35V72H20V17Z"
          fill="none"
          stroke="var(--fop-halo)"
          strokeWidth="7"
          strokeLinejoin="round"
          opacity="0.58"
          filter={`url(#${id}Halo)`}
        />
      ) : null}
      <g className="transition-opacity duration-300 ease-out motion-reduce:transition-none">
        <path d="M20 17H67V31H35V39H59V53H35V72H20V17Z" fill="#D8DEE7" opacity="0.42" />
        <path
          d="M20 17H35V72H20V17Z"
          fill="var(--fop-protect)"
          opacity={segmentOpacity(resolvedProtect, resolvedStatus)}
          clipPath={`url(#${id}ProtectClip)`}
        />
        <path
          d="M20 17H67V31H20V17Z"
          fill="var(--fop-advise)"
          opacity={segmentOpacity(resolvedAdvise, resolvedStatus)}
          clipPath={`url(#${id}AdviseClip)`}
        />
        <path
          d="M20 39H59V53H20V39Z"
          fill="var(--fop-build)"
          opacity={segmentOpacity(resolvedBuild, resolvedStatus)}
          clipPath={`url(#${id}BuildClip)`}
        />
        <path d="M20 17H67V31H35V39H59V53H35V72H20V17Z" fill="none" stroke="#0F172A" strokeOpacity="0.16" />
      </g>
      {labelsVisible ? (
        <g fontFamily="Inter, Arial, sans-serif" fontSize="6" fontWeight="800" letterSpacing="0.5" textAnchor="middle">
          <text x="46" y="26" fill="#0F172A">ADVISE</text>
          <text x="40" y="48" fill="#FFFFFF">BUILD</text>
          <text x="27" y="63" fill="#0F172A" transform="rotate(-90 27 63)">PROTECT</text>
        </g>
      ) : null}
      {showWordmark ? (
        <g fill="#0F172A" fontFamily="Inter, Arial, sans-serif" fontWeight="760">
          <text x="102" y="47" fontSize="34" letterSpacing="1.5">OP</text>
          <text x="103" y="65" fontSize="9" letterSpacing="2.4" fill="#64748B">BUILD • ADVISE • PROTECT</text>
        </g>
      ) : null}
    </svg>
  );
}
