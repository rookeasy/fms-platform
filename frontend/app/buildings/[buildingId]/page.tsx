import Link from "next/link";

import { AppShell } from "@/components/AppShell";
import { DashboardCard } from "@/components/DashboardCard";
import { HealthScoreBadge } from "@/components/HealthScoreBadge";
import { StatusBadge } from "@/components/StatusBadge";
import { getBuilding } from "@/lib/mock-data";

type BuildingDetailPageProps = {
  params: { buildingId: string };
};

export default function BuildingDetailPage({ params }: BuildingDetailPageProps) {
  const building = getBuilding(params.buildingId);

  return (
    <AppShell title={building.name}>
      <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-sm font-medium text-slate-500">{building.type}</p>
            <h2 className="mt-2 text-2xl font-semibold text-slate-950">{building.name}</h2>
            <p className="mt-1 text-slate-600">{building.address}</p>
          </div>
          <HealthScoreBadge score={building.healthScore} />
        </div>
        <div className="mt-5 flex flex-wrap items-center gap-3">
          <StatusBadge status={building.status} />
          <span className="text-sm text-slate-600">Manager: {building.manager}</span>
          <Link className="text-sm font-semibold text-slate-950 underline" href={`/buildings/${building.id}/passport`}>
            View passport
          </Link>
        </div>
      </section>
      <div className="mt-6 grid gap-4 md:grid-cols-3">
        <DashboardCard title="Open Items" value={`${building.openItems}`} detail="Mock portfolio data" />
        <DashboardCard title="Last Inspection" value={building.lastInspection} detail="No backend connection" />
        <DashboardCard title="Health Score" value={`${building.healthScore}%`} detail="Mock scoring model" />
      </div>
    </AppShell>
  );
}
