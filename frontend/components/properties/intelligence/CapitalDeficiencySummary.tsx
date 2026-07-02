import { StatusBadge } from "@/components/StatusBadge";
import { formatControlledValue } from "@/lib/controlled-values";
import type { PropertyCapitalSummary, PropertyDeficiencySummary } from "@/lib/fms-api";

type CapitalDeficiencySummaryProps = {
  capital: PropertyCapitalSummary;
  deficiencies: PropertyDeficiencySummary;
};

export function CapitalDeficiencySummary({ capital, deficiencies }: CapitalDeficiencySummaryProps) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <h4 className="font-semibold text-slate-950">Deficiency / Capital Summary</h4>
        <StatusBadge status={formatControlledValue(capital.planning_status)} />
      </div>
      <dl className="mt-4 grid gap-4 sm:grid-cols-2">
        <div>
          <dt className="text-sm font-medium text-slate-500">Capital Exposure</dt>
          <dd className="mt-1 text-2xl font-semibold text-slate-950">${capital.replacement_cost_estimate.toLocaleString()}</dd>
        </div>
        <div>
          <dt className="text-sm font-medium text-slate-500">Near-Term Assets</dt>
          <dd className="mt-1 text-2xl font-semibold text-slate-950">{capital.near_term_asset_count}</dd>
        </div>
        <div>
          <dt className="text-sm font-medium text-slate-500">Open Deficiencies</dt>
          <dd className="mt-1 text-2xl font-semibold text-slate-950">{deficiencies.open}</dd>
        </div>
        <div>
          <dt className="text-sm font-medium text-slate-500">Critical / High</dt>
          <dd className="mt-1 text-2xl font-semibold text-slate-950">{deficiencies.critical_or_high}</dd>
        </div>
      </dl>
      {capital.by_building.length ? (
        <div className="mt-5 space-y-2">
          {capital.by_building.slice(0, 4).map((building) => (
            <div key={building.building_id} className="flex items-center justify-between gap-3 text-sm">
              <span className="font-medium text-slate-700">{building.building_name}</span>
              <span className="text-slate-500">${building.replacement_cost_estimate.toLocaleString()}</span>
            </div>
          ))}
        </div>
      ) : null}
    </div>
  );
}
