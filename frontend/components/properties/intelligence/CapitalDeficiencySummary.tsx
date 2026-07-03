import { StatusBadge } from "@/components/StatusBadge";
import { formatControlledValue } from "@/lib/controlled-values";
import type { PropertyCapitalSummary, PropertyDeficiencySummary } from "@/lib/fms-api";

type CapitalDeficiencySummaryProps = {
  capital: PropertyCapitalSummary;
  deficiencies: PropertyDeficiencySummary;
};

export function CapitalDeficiencySummary({ capital, deficiencies }: CapitalDeficiencySummaryProps) {
  return (
    <div className="fop-card p-5">
      <div className="flex items-start justify-between gap-3">
        <h4 className="font-semibold tracking-normal text-white">Deficiency / Capital Summary</h4>
        <StatusBadge status={formatControlledValue(capital.planning_status)} />
      </div>
      <dl className="mt-4 grid gap-4 sm:grid-cols-2">
        <div>
          <dt className="text-sm font-medium text-[#7D8CA3]">Capital Exposure</dt>
          <dd className="mt-1 text-2xl font-semibold text-white">${capital.replacement_cost_estimate.toLocaleString()}</dd>
        </div>
        <div>
          <dt className="text-sm font-medium text-[#7D8CA3]">Near-Term Assets</dt>
          <dd className="mt-1 text-2xl font-semibold text-white">{capital.near_term_asset_count}</dd>
        </div>
        <div>
          <dt className="text-sm font-medium text-[#7D8CA3]">Open Deficiencies</dt>
          <dd className="mt-1 text-2xl font-semibold text-white">{deficiencies.open}</dd>
        </div>
        <div>
          <dt className="text-sm font-medium text-[#7D8CA3]">Critical / High</dt>
          <dd className="mt-1 text-2xl font-semibold text-white">{deficiencies.critical_or_high}</dd>
        </div>
      </dl>
      {capital.by_building.length ? (
        <div className="mt-5 space-y-2">
          {capital.by_building.slice(0, 4).map((building) => (
            <div key={building.building_id} className="flex items-center justify-between gap-3 text-sm">
              <span className="font-medium text-[#B6C1CF]">{building.building_name}</span>
              <span className="text-[#7D8CA3]">${building.replacement_cost_estimate.toLocaleString()}</span>
            </div>
          ))}
        </div>
      ) : null}
    </div>
  );
}

