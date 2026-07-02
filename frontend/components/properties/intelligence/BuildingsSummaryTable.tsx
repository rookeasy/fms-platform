import Link from "next/link";

import { StatusBadge } from "@/components/StatusBadge";
import { formatControlledValue } from "@/lib/controlled-values";
import type { PropertyBuildingIntelligence } from "@/lib/fms-api";

type BuildingsSummaryTableProps = {
  buildings: PropertyBuildingIntelligence[];
};

export function BuildingsSummaryTable({ buildings }: BuildingsSummaryTableProps) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <h4 className="font-semibold text-slate-950">Buildings Summary</h4>
      <div className="mt-4 overflow-x-auto">
        <table className="w-full min-w-[820px] text-left text-sm">
          <thead className="border-b border-slate-200 text-xs uppercase text-slate-500">
            <tr>
              <th className="py-2 pr-4">Record</th>
              <th className="py-2 pr-4">Health</th>
              <th className="py-2 pr-4">Assets</th>
              <th className="py-2 pr-4">Documents</th>
              <th className="py-2 pr-4">Passport</th>
              <th className="py-2 pr-4">Deficiencies</th>
              <th className="py-2 pr-4">Status</th>
            </tr>
          </thead>
          <tbody>
            {buildings.map((building) => (
              <tr key={building.id} className="border-b border-slate-100 last:border-b-0">
                <td className="py-3 pr-4">
                  <Link href={`/buildings/${building.id}`} className="font-semibold text-slate-950 underline">
                    {building.name}
                  </Link>
                  <p className="text-xs text-slate-500">{building.bpid ?? formatControlledValue(building.building_type ?? "")}</p>
                </td>
                <td className="py-3 pr-4">{building.health_score ?? "Not scored"}</td>
                <td className="py-3 pr-4">{building.asset_count}</td>
                <td className="py-3 pr-4">{building.document_count}</td>
                <td className="py-3 pr-4">{building.passport_record_count}</td>
                <td className="py-3 pr-4">{building.open_deficiency_count}</td>
                <td className="py-3 pr-4">
                  <StatusBadge status={formatControlledValue(building.readiness_status)} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
