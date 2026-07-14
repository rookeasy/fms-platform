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
      className={variant === "card" || variant === "dashboard" ? "rounded-xl border border-[#E2E8F0] bg-[#F8FAFC] p-4" : ""}
      aria-label={`${label ?? "FPP Progress Index"}: ${normalizedScore}% ${statusLabel[resolvedStatus]}`}
    >
      {(label || showScore) && !isCompact ? (
        <div className="mb-3 flex items-center justify-between gap-3">
          <div>
            {label ? <p className="text-sm font-semibold text-[#0F172A]">{label}</p> : null}
            <p className="text-xs text-[#64748B]">{statusLabel[resolvedStatus]}</p>
          </div>
          {showScore ? <span className="text-sm font-semibold text-[#0F172A]">{normalizedScore}%</span> : null}
        </div>
      ) : null}

      <div className="relative py-4">
        <div className={`relative ${styles.track} overflow-hidden rounded-full bg-[#CBD5E1]`}>
          <div
            className={`${styles.track} rounded-full bg-[linear-gradient(90deg,var(--fop-build)_0%,var(--fop-advise)_52%,var(--fop-protect)_100%)] transition-[width] duration-700 ease-out`}
            style={{ width: `${displayScore}%` }}
          />
        </div>
        <div
          className={`absolute top-1/2 -translate-x-1/2 -translate-y-1/2 rounded-full border bg-white shadow-[0_0_0_4px_rgba(23,105,255,0.12)] transition-[left] duration-700 ease-out motion-safe:animate-[fpp-score-pulse_700ms_ease-out_1] ${styles.dot}`}
          style={{ left: `${displayScore}%`, borderColor: "var(--fop-build)" }}
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
            {showDescriptions && !isCompact ? <p className="mt-1 text-xs leading-5 text-[#64748B]">{stage.description}</p> : null}
          </div>
        ))}
      </div>
    </div>
  );
}
