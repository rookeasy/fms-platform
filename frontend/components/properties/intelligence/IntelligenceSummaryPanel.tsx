import { StatusBadge } from "@/components/StatusBadge";
import { formatControlledValue } from "@/lib/controlled-values";
import type {
  PropertyConfidenceSummary,
  PropertyHealthSummary,
  PropertyReadinessSummary,
  PropertyRiskSummary
} from "@/lib/fms-api";

type IntelligenceSummaryPanelProps = {
  title: string;
  summary: PropertyHealthSummary | PropertyConfidenceSummary | PropertyRiskSummary | PropertyReadinessSummary | null | undefined;
  metricRows: Array<{ label: string; value: string | number | boolean | null | undefined }>;
};

function displayValue(value: string | number | boolean | null | undefined) {
  if (typeof value === "boolean") return value ? "Yes" : "No";
  if (value === null || value === undefined || value === "") return "Not available";
  return value;
}

export function IntelligenceSummaryPanel({ title, summary, metricRows }: IntelligenceSummaryPanelProps) {
  return (
    <div className="fop-card p-5">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h4 className="font-semibold tracking-normal text-white">{title}</h4>
          {summary ? <p className="mt-1 text-sm text-[#7D8CA3]">{summary.label}</p> : null}
        </div>
        {summary ? <StatusBadge status={formatControlledValue(summary.status)} /> : null}
      </div>

      <dl className="mt-4 grid gap-3 sm:grid-cols-2">
        {metricRows.map((row) => (
          <div key={row.label}>
            <dt className="text-xs font-medium uppercase text-[#7D8CA3]">{row.label}</dt>
            <dd className="mt-1 text-sm font-semibold text-white">{displayValue(row.value)}</dd>
          </div>
        ))}
      </dl>

      {summary?.drivers?.length ? (
        <div className="mt-4 space-y-2">
          {summary.drivers.slice(0, 3).map((driver) => (
            <p key={driver} className="text-sm text-[#B6C1CF]">
              {driver}
            </p>
          ))}
        </div>
      ) : null}
    </div>
  );
}

