import { AppShell } from "@/components/AppShell";
import { DashboardCard } from "@/components/DashboardCard";
import { DataTable } from "@/components/DataTable";
import { StatusBadge } from "@/components/StatusBadge";
import { Timeline } from "@/components/Timeline";
import { dashboardMetrics, portfolioTimeline, workOrders } from "@/lib/mock-data";

export default function DashboardPage() {
  return (
    <AppShell title="Dashboard">
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {dashboardMetrics.map((metric) => (
          <DashboardCard key={metric.label} title={metric.label} value={metric.value} detail={metric.detail} />
        ))}
      </div>
      <div className="mt-6 grid gap-6 xl:grid-cols-[1fr_360px]">
        <DataTable
          rows={workOrders}
          columns={[
            { key: "id", header: "Work Order", render: (row) => row.id },
            { key: "building", header: "Building", render: (row) => row.building },
            { key: "priority", header: "Priority", render: (row) => <StatusBadge status={row.priority} /> },
            { key: "status", header: "Status", render: (row) => row.status }
          ]}
        />
        <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-950">Portfolio Timeline</h2>
          <div className="mt-4">
            <Timeline items={portfolioTimeline} />
          </div>
        </section>
      </div>
    </AppShell>
  );
}
