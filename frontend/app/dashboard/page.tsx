import { AppShell } from "@/components/AppShell";
import { DashboardCard } from "@/components/DashboardCard";
import { DataTable } from "@/components/DataTable";
import { PassportSection } from "@/components/PassportSection";
import { StatusBadge } from "@/components/StatusBadge";
import { Timeline } from "@/components/Timeline";
import { dashboardMetrics, portfolioTimeline, workOrders } from "@/lib/mock-data";
import { fuzionBrand } from "@/lib/brand";

export default function DashboardPage() {
  return (
    <AppShell title="Dashboard">
      <div className="space-y-6">
        <section className="fop-card p-6">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <p className="fop-label">Mission Control</p>
              <h2 className="mt-2 text-2xl font-semibold tracking-normal text-white">Where operations need attention today</h2>
              <p className="mt-2 max-w-3xl text-sm leading-6 text-[#B6C1CF]">
                Monitor active work, readiness, risk, and the next best actions across {fuzionBrand.product}.
              </p>
            </div>
            <StatusBadge status="Operational" />
          </div>
        </section>

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {dashboardMetrics.map((metric) => (
            <DashboardCard key={metric.label} title={metric.label} value={metric.value} detail={metric.detail} />
          ))}
        </div>

        <div className="grid gap-4 lg:grid-cols-3">
          <PassportSection title="Critical Alerts">
            <div className="space-y-3 text-sm text-[#B6C1CF]">
              <p>Closeout records with missing evidence require review before handover.</p>
              <p>High-priority work should be validated against active building profiles.</p>
            </div>
          </PassportSection>
          <PassportSection title="Advisor Recommendation">
            <p className="text-sm leading-6 text-[#B6C1CF]">
              Ask Fuzion to identify which property or building should be moved from closeout into service conversion next.
            </p>
          </PassportSection>
          <PassportSection title="Next Actions">
            <div className="space-y-2 text-sm text-[#B6C1CF]">
              <p>Review active work orders.</p>
              <p>Check property readiness.</p>
              <p>Open the Advisor for prioritization.</p>
            </div>
          </PassportSection>
        </div>

        <div className="grid gap-6 xl:grid-cols-[1fr_360px]">
          <section>
            <div className="mb-3">
              <h2 className="text-xl font-semibold tracking-normal text-white">Active Work</h2>
              <p className="text-sm text-[#B6C1CF]">Open operational items and near-term execution context.</p>
            </div>
            <DataTable
              rows={workOrders}
              columns={[
                { key: "id", header: "Work Order", render: (row) => row.id },
                { key: "building", header: "Building", render: (row) => row.building },
                { key: "priority", header: "Priority", render: (row) => <StatusBadge status={row.priority} /> },
                { key: "status", header: "Status", render: (row) => row.status }
              ]}
            />
          </section>
          <section className="fop-card p-5">
            <h2 className="text-lg font-semibold tracking-normal text-white">Recent Activity</h2>
            <div className="mt-4">
              <Timeline items={portfolioTimeline} />
            </div>
          </section>
        </div>
      </div>
    </AppShell>
  );
}
