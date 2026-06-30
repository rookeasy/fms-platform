import { AppShell } from "@/components/AppShell";
import { DataTable } from "@/components/DataTable";
import { StatusBadge } from "@/components/StatusBadge";

const deficiencies = [
  { id: "DF-301", building: "King Station Offices", severity: "High", status: "Open" },
  { id: "DF-300", building: "Lakeside Residence", severity: "Medium", status: "In Review" },
  { id: "DF-299", building: "Harbour Tower", severity: "Low", status: "Open" }
];

export default function DeficienciesPage() {
  return (
    <AppShell title="Deficiencies">
      <DataTable
        rows={deficiencies}
        columns={[
          { key: "id", header: "ID", render: (row) => row.id },
          { key: "building", header: "Building", render: (row) => row.building },
          { key: "severity", header: "Severity", render: (row) => <StatusBadge status={row.severity} /> },
          { key: "status", header: "Status", render: (row) => row.status }
        ]}
      />
    </AppShell>
  );
}
