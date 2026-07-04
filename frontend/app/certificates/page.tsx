import { AppShell } from "@/components/AppShell";
import { DataTable } from "@/components/DataTable";
import { StatusBadge } from "@/components/StatusBadge";
import { buildings } from "@/lib/mock-data";

const certificates = buildings.slice(0, 6).map((building) => ({
  name: "FPP Certificate Record",
  jobNo: building.jobNo,
  passportNo: building.passportNo,
  building: building.projectName,
  status: building.status === "completed_occupied" ? "Current / Historical" : "Pending / In Progress"
}));

export default function CertificatesPage() {
  return (
    <AppShell title="Certificates">
      <DataTable
        rows={certificates}
        columns={[
          { key: "name", header: "Certificate", render: (row) => row.name },
          { key: "jobNo", header: "Job No.", render: (row) => row.jobNo },
          { key: "passportNo", header: "Passport No.", render: (row) => row.passportNo },
          { key: "building", header: "Building", render: (row) => row.building },
          { key: "status", header: "Status", render: (row) => <StatusBadge status={row.status} /> }
        ]}
      />
    </AppShell>
  );
}
