import { AppShell } from "@/components/AppShell";
import { DataTable } from "@/components/DataTable";

const users = [
  { name: "Avery Chen", role: "Portfolio Manager", status: "Active" },
  { name: "Maya Patel", role: "Property Manager", status: "Active" },
  { name: "Noah Williams", role: "Operations Lead", status: "Invited" }
];

export default function UsersPage() {
  return (
    <AppShell title="Users">
      <DataTable
        rows={users}
        columns={[
          { key: "name", header: "Name", render: (row) => row.name },
          { key: "role", header: "Role", render: (row) => row.role },
          { key: "status", header: "Status", render: (row) => row.status }
        ]}
      />
    </AppShell>
  );
}
