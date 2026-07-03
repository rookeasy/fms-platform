import type { LucideIcon } from "lucide-react";

import { StatusBadge } from "@/components/StatusBadge";
import { formatControlledValue } from "@/lib/controlled-values";
import type { PropertyIntelligenceScore } from "@/lib/fms-api";

type IntelligenceScoreCardProps = {
  score: PropertyIntelligenceScore;
  icon: LucideIcon;
};

function scoreColor(score: PropertyIntelligenceScore) {
  if (score.label === "Property Risk") {
    if (score.score >= 70) return "text-red-700";
    if (score.score >= 35) return "text-amber-700";
    return "text-emerald-700";
  }
  if (score.score >= 80) return "text-emerald-700";
  if (score.score >= 60) return "text-amber-700";
  return "text-red-700";
}

export function IntelligenceScoreCard({ score, icon: Icon }: IntelligenceScoreCardProps) {
  return (
    <div className="fop-card p-5">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[#7D8CA3]">{score.label}</p>
          <p className={`mt-3 text-3xl font-semibold tracking-normal ${scoreColor(score)}`}>{score.score}</p>
        </div>
        <Icon className="text-slate-400" size={18} />
      </div>
      <div className="mt-3">
        <StatusBadge status={formatControlledValue(score.status)} />
      </div>
    </div>
  );
}

