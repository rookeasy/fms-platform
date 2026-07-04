import { AppShell } from "@/components/AppShell";
import { DataTable } from "@/components/DataTable";
import { StatusBadge } from "@/components/StatusBadge";
import { buildings } from "@/lib/mock-data";

const deficiencies = buildings
  .filter((building) => building.status === "active")
  .slice(0, 5)
  .map((building) => ({
    id: `DF-${building.jobNo}`,
    jobNo: building.jobNo,
    passportNo: building.passportNo,
    building: building.projectName,
    severity: Number(building.jobNo) % 2 === 0 ? "Medium" : "High",
    status: "Open"
  }));

export default function DeficienciesPage() {
  return (
    <AppShell title="Deficiencies">
      <DataTable
        rows={deficiencies}
        columns={[
          { key: "id", header: "ID", render: (row) => row.id },
          { key: "jobNo", header: "Job No.", render: (row) => row.jobNo },
          { key: "passportNo", header: "Passport No.", render: (row) => row.passportNo },
          { key: "building", header: "Building", render: (row) => row.building },
          { key: "severity", header: "Severity", render: (row) => <StatusBadge status={row.severity} /> },
          { key: "status", header: "Status", render: (row) => row.status }
        ]}
      />
    </AppShell>
  );
}
