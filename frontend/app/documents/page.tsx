import { AppShell } from "@/components/AppShell";
import { DataTable } from "@/components/DataTable";
import { buildings } from "@/lib/mock-data";

const documents = buildings.slice(0, 8).map((building) => ({
  name: "FPP Passport Evidence Record",
  jobNo: building.jobNo,
  passportNo: building.passportNo,
  building: building.projectName,
  updated: building.status === "completed_occupied" ? "Historical" : "In Progress"
}));

export default function DocumentsPage() {
  return (
    <AppShell title="Documents">
      <DataTable
        rows={documents}
        columns={[
          { key: "name", header: "Document", render: (row) => row.name },
          { key: "jobNo", header: "Job No.", render: (row) => row.jobNo },
          { key: "passportNo", header: "Passport No.", render: (row) => row.passportNo },
          { key: "building", header: "Building", render: (row) => row.building },
          { key: "updated", header: "Updated", render: (row) => row.updated }
        ]}
      />
    </AppShell>
  );
}
