import { AppShell } from "@/components/AppShell";
import { PassportSection } from "@/components/PassportSection";
import { StatusBadge } from "@/components/StatusBadge";
import { Timeline } from "@/components/Timeline";
import { getBuilding, portfolioTimeline } from "@/lib/mock-data";

type BuildingPassportPageProps = {
  params: { buildingId: string };
};

export default function BuildingPassportPage({ params }: BuildingPassportPageProps) {
  const building = getBuilding(params.buildingId);

  return (
    <AppShell title={`${building.name} Passport`}>
      <div className="grid gap-6 xl:grid-cols-[1fr_380px]">
        <div className="space-y-6">
          <PassportSection title="Building Identity" description="Mock profile details for shell review.">
            <dl className="grid gap-4 sm:grid-cols-2">
              <div>
                <dt className="text-sm font-medium text-slate-500">Address</dt>
                <dd className="mt-1 text-slate-950">{building.address}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-slate-500">Type</dt>
                <dd className="mt-1 text-slate-950">{building.type}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-slate-500">Manager</dt>
                <dd className="mt-1 text-slate-950">{building.manager}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-slate-500">Status</dt>
                <dd className="mt-1">
                  <StatusBadge status={building.status} />
                </dd>
              </div>
            </dl>
          </PassportSection>
          <PassportSection title="Compliance Snapshot">
            <div className="grid gap-3 sm:grid-cols-3">
              {["Fire Safety", "Elevators", "Insurance"].map((item) => (
                <div key={item} className="rounded-md border border-slate-200 p-4">
                  <p className="font-medium text-slate-950">{item}</p>
                  <p className="mt-1 text-sm text-slate-600">Current</p>
                </div>
              ))}
            </div>
          </PassportSection>
        </div>
        <PassportSection title="Activity Timeline">
          <Timeline items={portfolioTimeline} />
        </PassportSection>
      </div>
    </AppShell>
  );
}
