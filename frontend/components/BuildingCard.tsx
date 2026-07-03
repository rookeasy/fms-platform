import Link from "next/link";

import { HealthScoreBadge } from "@/components/HealthScoreBadge";
import { StatusBadge } from "@/components/StatusBadge";
import type { Building } from "@/lib/mock-data";

type BuildingCardProps = {
  building: Building;
};

export function BuildingCard({ building }: BuildingCardProps) {
  return (
    <Link
      href={`/buildings/${building.id}`}
      className="fop-card block p-5 transition hover:-translate-y-0.5 hover:border-white/15 hover:shadow-xl"
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-lg font-semibold tracking-normal text-white">{building.name}</h3>
          <p className="mt-1 text-sm text-[#B6C1CF]">{building.address}</p>
        </div>
        <HealthScoreBadge score={building.healthScore} />
      </div>
      <div className="mt-5 flex flex-wrap items-center gap-3">
        <StatusBadge status={building.status} />
        <span className="text-sm text-[#B6C1CF]">{building.openItems} open items</span>
        <span className="text-sm text-[#B6C1CF]">{building.type}</span>
      </div>
    </Link>
  );
}

