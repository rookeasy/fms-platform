import { AppShell } from "@/components/AppShell";
import { DataTable } from "@/components/DataTable";
import { ProgressIndex } from "@/components/ProgressIndex";
import { fppKpiTerms } from "@/lib/progress-index";

const memberships = [
  { group: "Portfolio Admins", members: "4", access: "Full" },
  { group: "Property Managers", members: "18", access: "Operational" },
  { group: "Auditors", members: "6", access: "Read Only" }
];

export default function MembershipsPage() {
  return (
    <AppShell title="Memberships">
      <div className="space-y-6">
        <section className="fop-card p-6">
          <p className="fop-label">Member Buildings</p>
          <h2 className="mt-2 text-xl font-semibold text-white">{fppKpiTerms.progressIndex} for FPP Membership Conversion</h2>
          <p className="mt-2 text-sm leading-6 text-[#B6C1CF]">
            Use BUILD to ADVISE to PROTECT as the common sales and operations language for member building readiness.
          </p>
          <div className="mt-5">
            <ProgressIndex score={84} size="lg" showDescriptions variant="dashboard" />
          </div>
        </section>
        <DataTable
          rows={memberships}
          columns={[
            { key: "group", header: "Group", render: (row) => row.group },
            { key: "members", header: "Members", render: (row) => row.members },
            { key: "access", header: "Access", render: (row) => row.access }
          ]}
        />
      </div>
    </AppShell>
  );
}
