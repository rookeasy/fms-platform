import { AppShell } from "@/components/AppShell";
import { DataTable } from "@/components/DataTable";
import { StatusBadge } from "@/components/StatusBadge";
import { workOrders } from "@/lib/mock-data";

export default function WorkOrdersPage() {
  return (
    <AppShell title="Work Orders">
      <DataTable
        rows={workOrders}
        columns={[
          { key: "id", header: "ID", render: (row) => row.id },
          { key: "building", header: "Building", render: (row) => row.building },
          { key: "priority", header: "Priority", render: (row) => <StatusBadge status={row.priority} /> },
          { key: "status", header: "Status", render: (row) => row.status }
        ]}
      />
    </AppShell>
  );
}
