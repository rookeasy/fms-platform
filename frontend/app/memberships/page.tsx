import { AppShell } from "@/components/AppShell";
import { DataTable } from "@/components/DataTable";

const memberships = [
  { group: "Portfolio Admins", members: "4", access: "Full" },
  { group: "Property Managers", members: "18", access: "Operational" },
  { group: "Auditors", members: "6", access: "Read Only" }
];

export default function MembershipsPage() {
  return (
    <AppShell title="Memberships">
      <DataTable
        rows={memberships}
        columns={[
          { key: "group", header: "Group", render: (row) => row.group },
          { key: "members", header: "Members", render: (row) => row.members },
          { key: "access", header: "Access", render: (row) => row.access }
        ]}
      />
    </AppShell>
  );
}
