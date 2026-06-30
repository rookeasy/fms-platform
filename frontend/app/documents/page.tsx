import { AppShell } from "@/components/AppShell";
import { DataTable } from "@/components/DataTable";

const documents = [
  { name: "Fire Safety Plan", building: "Harbour Tower", updated: "2026-06-12" },
  { name: "Insurance Binder", building: "King Station Offices", updated: "2026-06-08" },
  { name: "Reserve Study", building: "Lakeside Residence", updated: "2026-05-29" }
];

export default function DocumentsPage() {
  return (
    <AppShell title="Documents">
      <DataTable
        rows={documents}
        columns={[
          { key: "name", header: "Document", render: (row) => row.name },
          { key: "building", header: "Building", render: (row) => row.building },
          { key: "updated", header: "Updated", render: (row) => row.updated }
        ]}
      />
    </AppShell>
  );
}
