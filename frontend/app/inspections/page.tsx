import { AppShell } from "@/components/AppShell";
import { DataTable } from "@/components/DataTable";
import { ProgressIndex } from "@/components/ProgressIndex";
import { inspections } from "@/lib/mock-data";
import { fppKpiTerms, getMockBuildingScores } from "@/lib/progress-index";

export default function InspectionsPage() {
  return (
    <AppShell title="Inspections">
      <div className="space-y-6">
        <section className="fop-card p-6">
          <p className="fop-label">{fppKpiTerms.complianceScore}</p>
          <h2 className="mt-2 text-xl font-semibold text-white">Inspection Readiness Index</h2>
          <div className="mt-5">
            <ProgressIndex score={89} size="lg" showDescriptions variant="dashboard" />
          </div>
        </section>
        <DataTable
          rows={inspections}
          columns={[
            { key: "id", header: "ID", render: (row) => row.id },
            { key: "jobNo", header: "Job No.", render: (row) => row.jobNo },
            { key: "passportNo", header: "Passport No.", render: (row) => row.passportNo },
            { key: "building", header: "Building", render: (row) => row.building },
            { key: "type", header: "Type", render: (row) => row.type },
            { key: "date", header: "Date", render: (row) => row.date },
            {
              key: "compliance",
              header: fppKpiTerms.complianceScore,
              render: (row) => {
                const score = getMockBuildingScores(row.id).complianceScore;
                return (
                  <div className="min-w-40">
                    <div className="mb-1 text-right text-xs font-semibold text-white">{score}%</div>
                    <ProgressIndex score={score} size="sm" variant="compact" showScore={false} />
                  </div>
                );
              }
            }
          ]}
        />
      </div>
    </AppShell>
  );
}
