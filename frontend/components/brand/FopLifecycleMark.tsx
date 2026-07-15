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
  return progress > 0 ? 1 : 0.22;
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
  className = "",
  title
}: FopLifecycleMarkProps) {
  const id = useId().replace(/:/g, "");
  const mapped = visualStateFromProgress(overallProgress, status === "protected");
  const resolvedStatus = status ?? mapped.status;
  const resolvedBuild = clamp(buildProgress ?? mapped.buildProgress);
  const resolvedAdvise = clamp(adviseProgress ?? mapped.adviseProgress);
  const resolvedProtect = clamp(protectProgress ?? mapped.protectProgress);
  const label = title ?? `FOP lifecycle status: ${resolvedStatus.toUpperCase()}`;
  const labelsVisible = showLabels && !compact;
  const width = labelsVisible ? 118 : 70;
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
        <clipPath id={`${id}BuildClip`}>
          <rect x="0" y="0" width={58 * (resolvedBuild / 100)} height="88" />
        </clipPath>
        <clipPath id={`${id}AdviseClip`}>
          <rect x="0" y="0" width={66 * (resolvedAdvise / 100)} height="88" />
        </clipPath>
        <clipPath id={`${id}ProtectClip`}>
          <rect x="0" y={82 - 76 * (resolvedProtect / 100)} width="52" height={76 * (resolvedProtect / 100)} />
        </clipPath>
        <filter id={`${id}Halo`} x="-45%" y="-45%" width="190%" height="190%" colorInterpolationFilters="sRGB">
          <feGaussianBlur stdDeviation="2.5" result="blur" />
          <feColorMatrix in="blur" type="matrix" values="0 0 0 0 1 0 0 0 0 0.45 0 0 0 0 0.38 0 0 0 0.24 0" result="coralGlow" />
          <feMerge>
            <feMergeNode in="coralGlow" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>

      {halo ? (
        <circle
          cx="38"
          cy="45"
          r="34"
          fill="none"
          stroke="var(--fop-halo)"
          strokeWidth="4"
          opacity="0.7"
          filter={`url(#${id}Halo)`}
        />
      ) : null}

      <g className="transition-opacity duration-300 ease-out motion-reduce:transition-none">
        <path d="M18 16H34V74H18V16Z" fill="#E2E8F0" />
        <path d="M18 16H66V31H18V16Z" fill="#E2E8F0" />
        <path d="M18 40H58V55H18V40Z" fill="#E2E8F0" />
        <path
          d="M18 16H34V74H18V16Z"
          fill="var(--fop-protect)"
          opacity={segmentOpacity(resolvedProtect, resolvedStatus)}
          clipPath={`url(#${id}ProtectClip)`}
        />
        <path
          d="M18 16H66V31H18V16Z"
          fill="var(--fop-advise)"
          opacity={segmentOpacity(resolvedAdvise, resolvedStatus)}
          clipPath={`url(#${id}AdviseClip)`}
        />
        <path
          d="M18 40H58V55H18V40Z"
          fill="var(--fop-build)"
          opacity={segmentOpacity(resolvedBuild, resolvedStatus)}
          clipPath={`url(#${id}BuildClip)`}
        />
        <path d="M18 16H66V31H34V40H58V55H34V74H18V16Z" fill="none" stroke="rgba(7,18,35,0.16)" />
      </g>

      {labelsVisible ? (
        <g fontFamily="Inter, Arial, sans-serif" fontSize="6" fontWeight="800" letterSpacing="0.5" textAnchor="middle">
          <text x="44" y="26" fill="#071223">ADVISE</text>
          <text x="39" y="50" fill="#FFFFFF">BUILD</text>
          <text x="27" y="66" fill="#071223" transform="rotate(-90 27 66)">PROTECT</text>
        </g>
      ) : null}
    </svg>
  );
}
