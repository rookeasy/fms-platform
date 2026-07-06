import Link from "next/link";

import { AppShell } from "@/components/AppShell";
import { DataTable } from "@/components/DataTable";
import { StatusBadge } from "@/components/StatusBadge";
import { buildings } from "@/lib/mock-data";

export default function CloseoutRegistryPage() {
  return (
    <AppShell title="Closeout">
      <DataTable
        rows={buildings}
        columns={[
          { key: "jobNo", header: "Job No.", render: (row) => row.jobNo },
          { key: "passportNo", header: "Passport No.", render: (row) => row.passportNo },
          { key: "building", header: "Building", render: (row) => <Link href={`/buildings/${row.id}/closeout`} className="font-semibold text-[#0F172A] underline decoration-[#CBD5E1] underline-offset-4 hover:decoration-[#D95A4E]">{row.projectName}</Link> },
          { key: "city", header: "City", render: (row) => row.city },
          { key: "closeoutStatus", header: "Closeout Status", render: (row) => <StatusBadge status={row.closeoutStatus} /> },
          { key: "occupancyStatus", header: "Occupancy", render: (row) => row.occupancyStatus }
        ]}
      />
    </AppShell>
  );
}
