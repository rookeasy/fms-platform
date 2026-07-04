"use client";

import { useEffect, useState } from "react";

import { clampScore, getProgressStatus, lifecycleStages } from "@/lib/progress-index";

type ProgressIndexProps = {
  score: number;
  label?: string;
  size?: "sm" | "md" | "lg";
  showDescriptions?: boolean;
  showScore?: boolean;
  status?: "low" | "medium" | "high" | "complete";
  variant?: "default" | "compact" | "card" | "dashboard";
};

const sizeStyles = {
  sm: { track: "h-1.5", dot: "h-3 w-3", label: "text-[10px]", gap: "gap-2" },
  md: { track: "h-2", dot: "h-4 w-4", label: "text-xs", gap: "gap-3" },
  lg: { track: "h-2.5", dot: "h-5 w-5", label: "text-sm", gap: "gap-4" }
};

const statusLabel = {
  low: "Needs attention",
  medium: "Developing",
  high: "Strong",
  complete: "Complete"
};

export function ProgressIndex({
  score,
  label,
  size = "md",
  showDescriptions = false,
  showScore = true,
  status,
  variant = "default"
}: ProgressIndexProps) {
  const normalizedScore = clampScore(score);
  const [displayScore, setDisplayScore] = useState(0);
  const resolvedStatus = status ?? getProgressStatus(normalizedScore);
  const styles = sizeStyles[size];
  const isCompact = variant === "compact";

  useEffect(() => {
    const frame = window.requestAnimationFrame(() => setDisplayScore(normalizedScore));
    return () => window.cancelAnimationFrame(frame);
  }, [normalizedScore]);

  return (
    <div
      className={variant === "card" || variant === "dashboard" ? "rounded-xl border border-white/10 bg-white/[0.035] p-4" : ""}
      aria-label={`${label ?? "FPP Progress Index"}: ${normalizedScore}% ${statusLabel[resolvedStatus]}`}
    >
      {(label || showScore) && !isCompact ? (
        <div className="mb-3 flex items-center justify-between gap-3">
          <div>
            {label ? <p className="text-sm font-semibold text-white">{label}</p> : null}
            <p className="text-xs text-[#7D8CA3]">{statusLabel[resolvedStatus]}</p>
          </div>
          {showScore ? <span className="text-sm font-semibold text-white">{normalizedScore}%</span> : null}
        </div>
      ) : null}

      <div className="relative py-4">
        <div className={`relative ${styles.track} overflow-hidden rounded-full bg-[rgba(125,140,163,0.28)]`}>
          <div
            className={`${styles.track} rounded-full bg-[linear-gradient(90deg,#FF6B5F_0%,#2DD4BF_52%,#60A5FA_100%)] transition-[width] duration-700 ease-out`}
            style={{ width: `${displayScore}%` }}
          />
        </div>
        <div
          className={`absolute top-1/2 -translate-x-1/2 -translate-y-1/2 rounded-full border border-white/70 bg-white shadow-[0_0_24px_rgba(96,165,250,0.5)] transition-[left] duration-700 ease-out motion-safe:animate-[fpp-score-pulse_700ms_ease-out_1] ${styles.dot}`}
          style={{ left: `${displayScore}%` }}
        >
          <span className="sr-only">{normalizedScore}%</span>
        </div>
      </div>

      <div className={`grid grid-cols-3 ${styles.gap}`}>
        {lifecycleStages.map((stage) => (
          <div key={stage.key} className={stage.key === "build" ? "text-left" : stage.key === "advise" ? "text-center" : "text-right"}>
            <p className={`${styles.label} font-semibold tracking-[0.16em]`} style={{ color: stage.color }}>
              {stage.label}
            </p>
            {showDescriptions && !isCompact ? <p className="mt-1 text-xs leading-5 text-[#B6C1CF]">{stage.description}</p> : null}
          </div>
        ))}
      </div>
    </div>
  );
}
