import { AppShell } from "@/components/AppShell";
import { DataTable } from "@/components/DataTable";
import { StatusBadge } from "@/components/StatusBadge";

const certificates = [
  { name: "Fire Alarm Certificate", building: "Harbour Tower", status: "Current" },
  { name: "Elevator License", building: "King Station Offices", status: "Needs Review" },
  { name: "Backflow Test", building: "Lakeside Residence", status: "Current" }
];

export default function CertificatesPage() {
  return (
    <AppShell title="Certificates">
      <DataTable
        rows={certificates}
        columns={[
          { key: "name", header: "Certificate", render: (row) => row.name },
          { key: "building", header: "Building", render: (row) => row.building },
          { key: "status", header: "Status", render: (row) => <StatusBadge status={row.status} /> }
        ]}
      />
    </AppShell>
  );
}
