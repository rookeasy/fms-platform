import { AppShell } from "@/components/AppShell";
import { DataTable } from "@/components/DataTable";
import { inspections } from "@/lib/mock-data";

export default function InspectionsPage() {
  return (
    <AppShell title="Inspections">
      <DataTable
        rows={inspections}
        columns={[
          { key: "id", header: "ID", render: (row) => row.id },
          { key: "building", header: "Building", render: (row) => row.building },
          { key: "type", header: "Type", render: (row) => row.type },
          { key: "date", header: "Date", render: (row) => row.date }
        ]}
      />
    </AppShell>
  );
}
