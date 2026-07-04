import { AppShell } from "@/components/AppShell";
import { DataTable } from "@/components/DataTable";
import { StatusBadge } from "@/components/StatusBadge";
import { workOrders } from "@/lib/mock-data";

export default function WorkOrdersPage() {
  return (
    <AppShell title="Work Orders">
      <div className="space-y-6">
        <section className="fop-card p-6">
          <p className="fop-label">Work</p>
          <h2 className="mt-2 text-xl font-semibold text-white">Field Work Requiring Action</h2>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-[#B6C1CF]">
            Work orders focus on the building, Passport, assignment, inspection context, deficiencies, and completion state.
          </p>
        </section>
        <DataTable
          rows={workOrders}
          columns={[
            { key: "building", header: "Building", render: (row) => <span className="font-semibold text-white">{row.building}</span> },
            { key: "passportNo", header: "Passport", render: (row) => row.passportNo },
            { key: "id", header: "Work Order", render: (row) => row.id },
            { key: "status", header: "Status", render: (row) => <StatusBadge status={row.status} /> },
            { key: "technician", header: "Assigned Technician", render: (row) => `Tech ${row.jobNo.slice(-2)}` },
            { key: "inspection", header: "Inspection", render: (row) => (row.priority === "High" ? "Required" : "Scheduled") },
            { key: "deficiencies", header: "Deficiencies", render: (row) => (row.priority === "High" ? "Open" : "Review") },
            { key: "completion", header: "Completion", render: (row) => (row.status === "Active" ? "In Progress" : "Pending") }
          ]}
        />
      </div>
    </AppShell>
  );
}
