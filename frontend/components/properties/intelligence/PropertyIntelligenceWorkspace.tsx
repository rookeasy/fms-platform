import type { PropertyIntelligence } from "@/lib/fms-api";

import { BuildingsSummaryTable } from "./BuildingsSummaryTable";
import { CapitalDeficiencySummary } from "./CapitalDeficiencySummary";
import { ExecutiveDashboardCards } from "./ExecutiveDashboardCards";
import { ExecutiveReviewPlaceholder } from "./ExecutiveReviewPlaceholder";
import { IntelligenceSummaryPanel } from "./IntelligenceSummaryPanel";
import { PassportStatusSummary } from "./PassportStatusSummary";
import { ReadinessChecklist } from "./ReadinessChecklist";

type PropertyIntelligenceWorkspaceProps = {
  intelligence: PropertyIntelligence;
};

export function PropertyIntelligenceWorkspace({ intelligence }: PropertyIntelligenceWorkspaceProps) {
  const health = intelligence.health_summary;
  const confidence = intelligence.confidence_summary;
  const risk = intelligence.risk_summary;
  const readiness = intelligence.readiness_summary;

  return (
    <section className="space-y-5">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h3 className="text-lg font-semibold text-white">Property Intelligence</h3>
          <p className="text-sm text-[#B6C1CF]">{intelligence.executive_summary}</p>
        </div>
      </div>

      <ExecutiveDashboardCards intelligence={intelligence} />

      <div className="grid gap-4 xl:grid-cols-2">
        <IntelligenceSummaryPanel
          title="Property Health"
          summary={health}
          metricRows={[
            { label: "Score", value: health?.score ?? intelligence.health.score },
            { label: "Buildings", value: health?.active_building_count },
            { label: "Shared Infrastructure", value: health?.shared_infrastructure_count },
            { label: "Total Records", value: health?.building_count }
          ]}
        />
        <IntelligenceSummaryPanel
          title="Property Confidence"
          summary={confidence}
          metricRows={[
            { label: "Score", value: confidence?.score ?? intelligence.confidence.score },
            { label: "Addressed Buildings", value: confidence?.addressed_building_count },
            { label: "Conditioned Assets", value: confidence?.assets_with_condition_count },
            { label: "Data Gaps", value: confidence?.data_gap_count }
          ]}
        />
        <IntelligenceSummaryPanel
          title="Property Risk"
          summary={risk}
          metricRows={[
            { label: "Score", value: risk?.score ?? intelligence.risk.score },
            { label: "Open Deficiencies", value: risk?.open_deficiency_count },
            { label: "Critical / High", value: risk?.critical_or_high_deficiency_count },
            { label: "Overdue Work Orders", value: risk?.overdue_work_order_count }
          ]}
        />
        <IntelligenceSummaryPanel
          title="Property Readiness"
          summary={readiness}
          metricRows={[
            { label: "Score", value: readiness?.score ?? intelligence.readiness.score },
            { label: "Ready for Handover", value: readiness?.ready_for_handover },
            { label: "Checklist Items", value: readiness?.checklist.length ?? intelligence.readiness_checklist.length },
            { label: "Status", value: readiness?.status ?? intelligence.readiness.status }
          ]}
        />
      </div>

      <BuildingsSummaryTable buildings={intelligence.buildings} />

      <div className="grid gap-4 xl:grid-cols-2">
        <ReadinessChecklist items={readiness?.checklist ?? intelligence.readiness_checklist} />
        <PassportStatusSummary passport={intelligence.passport_rollup} />
        <CapitalDeficiencySummary capital={intelligence.capital_summary} deficiencies={intelligence.deficiency_summary} />
        <ExecutiveReviewPlaceholder review={intelligence.executive_review} calculatedAt={intelligence.calculated_at} />
      </div>
    </section>
  );
}

