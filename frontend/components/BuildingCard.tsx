import Link from "next/link";

import { HealthScoreBadge } from "@/components/HealthScoreBadge";
import { ProgressIndex } from "@/components/ProgressIndex";
import { StatusBadge } from "@/components/StatusBadge";
import type { Building } from "@/lib/mock-data";
import { lifecycleLabels } from "@/lib/lifecycle";
import { fppKpiTerms } from "@/lib/progress-index";

type BuildingCardProps = {
  building: Building;
};

export function BuildingCard({ building }: BuildingCardProps) {
  return (
    <Link
      href={`/buildings/${building.id}`}
      className="fop-card block p-5 transition hover:-translate-y-0.5 hover:border-[#D95A4E]/30 hover:shadow-md"
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-lg font-semibold tracking-normal text-[#0F172A]">{building.name}</h3>
          <p className="mt-1 text-sm text-[#64748B]">{building.city}</p>
          <div className="mt-3 flex flex-wrap gap-2 text-xs font-semibold uppercase tracking-[0.14em] text-[#64748B]">
            <span>Job No. {building.jobNo}</span>
            <span>Passport No. {building.passportNo}</span>
          </div>
        </div>
        <HealthScoreBadge score={building.healthScore} />
      </div>
      <div className="mt-5 flex flex-wrap items-center gap-3">
        <StatusBadge status={lifecycleLabels[building.lifecycleStage]} />
        <span className="text-sm text-[#64748B]">{building.openItems} open items</span>
        <span className="text-sm text-[#64748B]">{building.passportStatus}</span>
      </div>
      <div className="mt-5">
        <ProgressIndex score={building.healthScore} label={fppKpiTerms.buildingHealthIndex} size="sm" variant="compact" showScore={false} />
      </div>
    </Link>
  );
}

