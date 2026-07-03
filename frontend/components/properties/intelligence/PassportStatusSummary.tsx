import { StatusBadge } from "@/components/StatusBadge";
import { formatControlledValue } from "@/lib/controlled-values";
import type { PropertyPassportSummary } from "@/lib/fms-api";

type PassportStatusSummaryProps = {
  passport: PropertyPassportSummary | null | undefined;
};

export function PassportStatusSummary({ passport }: PassportStatusSummaryProps) {
  return (
    <div className="fop-card p-5">
      <div className="flex items-start justify-between gap-3">
        <h4 className="font-semibold tracking-normal text-white">Passport Status Summary</h4>
        {passport ? <StatusBadge status={formatControlledValue(passport.status)} /> : null}
      </div>
      <dl className="mt-4 grid gap-4 sm:grid-cols-2">
        <div>
          <dt className="text-sm font-medium text-[#7D8CA3]">Completeness</dt>
          <dd className="mt-1 text-2xl font-semibold text-white">{passport?.completeness_score ?? 0}</dd>
        </div>
        <div>
          <dt className="text-sm font-medium text-[#7D8CA3]">Passport Records</dt>
          <dd className="mt-1 text-2xl font-semibold text-white">{passport?.passport_records ?? 0}</dd>
        </div>
        <div>
          <dt className="text-sm font-medium text-[#7D8CA3]">Client Visible</dt>
          <dd className="mt-1 text-2xl font-semibold text-white">{passport?.client_visible_records ?? 0}</dd>
        </div>
        <div>
          <dt className="text-sm font-medium text-[#7D8CA3]">Related Records</dt>
          <dd className="mt-1 text-2xl font-semibold text-white">{passport ? passport.building_count + passport.shared_infrastructure_count : 0}</dd>
        </div>
      </dl>
    </div>
  );
}

