import Link from "next/link";

import { AppShell } from "@/components/AppShell";
import { DataTable } from "@/components/DataTable";
import { ProgressIndex } from "@/components/ProgressIndex";
import { StatusBadge } from "@/components/StatusBadge";
import { getLifecycleScore, lifecycleLabels } from "@/lib/lifecycle";
import { buildings } from "@/lib/mock-data";

export default function PassportsPage() {
  return (
    <AppShell title="Building Passports">
      <DataTable
        rows={buildings}
        columns={[
          { key: "passportNo", header: "Passport No.", render: (row) => <Link href={`/buildings/${row.id}/passport`} className="font-semibold text-[#0F172A] underline decoration-[#CBD5E1] underline-offset-4 hover:decoration-[#D95A4E]">{row.passportNo}</Link> },
          { key: "jobNo", header: "Job No.", render: (row) => row.jobNo },
          { key: "buildingName", header: "Building", render: (row) => row.projectName },
          { key: "city", header: "City", render: (row) => row.city },
          { key: "passportStatus", header: "Passport Status", render: (row) => <StatusBadge status={row.passportStatus} /> },
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
    </AppShell>
  );
}
