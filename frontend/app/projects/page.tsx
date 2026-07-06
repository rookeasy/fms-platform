import Link from "next/link";

import { AppShell } from "@/components/AppShell";
import { DataTable } from "@/components/DataTable";
import { ProgressIndex } from "@/components/ProgressIndex";
import { StatusBadge } from "@/components/StatusBadge";
import { lifecycleLabels } from "@/lib/lifecycle";
import { projectEvents } from "@/lib/mock-data";
import { getLifecycleScore } from "@/lib/lifecycle";

export default function ProjectsPage() {
  return (
    <AppShell title="Projects">
      <div className="space-y-6">
        <section className="fop-card p-6">
          <p className="fop-label">Lifecycle Events</p>
          <h2 className="mt-2 text-2xl font-semibold text-white">Projects Attach to Building Passports</h2>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-[#B6C1CF]">
            A project is an event in the building lifecycle. The permanent record remains the Building Protection Passport.
          </p>
        </section>
        <DataTable
          rows={projectEvents}
          columns={[
            { key: "jobNo", header: "Job No.", render: (row) => row.jobNo },
            { key: "projectName", header: "Project", render: (row) => row.projectName },
            { key: "city", header: "City", render: (row) => row.city },
            { key: "status", header: "Project Status", render: (row) => <StatusBadge status={row.status} /> },
            {
              key: "passports",
              header: "Linked Building Passport(s)",
              render: (row) => (
                <div className="space-y-1">
                  {row.linkedPassports.map((passportNo, index) => (
                    <Link key={passportNo} href={`/buildings/${row.buildingIds[index]}`} className="block font-semibold text-[#0F172A] underline decoration-[#CBD5E1] underline-offset-4 hover:decoration-[#D95A4E]">
                      {passportNo}
                    </Link>
                  ))}
                </div>
              )
            },
            {
              key: "lifecycle",
              header: "Lifecycle",
              render: (row) => (
                <div className="min-w-44">
                  <div className="mb-1 text-xs font-semibold text-[#B6C1CF]">{lifecycleLabels[row.lifecycleStage]}</div>
                  <ProgressIndex score={getLifecycleScore(row.lifecycleStage)} size="sm" variant="compact" showScore={false} />
                </div>
              )
            }
          ]}
        />
      </div>
    </AppShell>
  );
}
