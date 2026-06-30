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
      className="block rounded-lg border border-slate-200 bg-white p-5 shadow-sm transition hover:border-slate-300 hover:shadow"
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-lg font-semibold text-slate-950">{building.name}</h3>
          <p className="mt-1 text-sm text-slate-600">{building.address}</p>
        </div>
        <HealthScoreBadge score={building.healthScore} />
      </div>
      <div className="mt-5 flex flex-wrap items-center gap-3">
        <StatusBadge status={building.status} />
        <span className="text-sm text-slate-600">{building.openItems} open items</span>
        <span className="text-sm text-slate-600">{building.type}</span>
      </div>
    </Link>
  );
}
