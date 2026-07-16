"use client";

import Link from "next/link";
import { ClipboardCheck, FileSearch, FolderOpen, ShieldCheck, Wrench } from "lucide-react";
import { useCallback, useEffect, useState } from "react";

import { EmptyState } from "@/components/EmptyState";
import { ErrorState } from "@/components/ErrorState";
import { LoadingState } from "@/components/LoadingState";
import { StatusBadge } from "@/components/StatusBadge";
import { formatControlledValue } from "@/lib/controlled-values";
import { type SohoPassportReadiness, getPropertyPassportReadiness } from "@/lib/fms-api";

type SohoPassportReadinessClientProps = {
  propertyId: string;
};

function scoreTone(score: number) {
  if (score >= 90) {
    return "text-emerald-300";
  }
  if (score >= 60) {
    return "text-sky-300";
  }
  return "text-coral-300";
}

export function SohoPassportReadinessClient({ propertyId }: SohoPassportReadinessClientProps) {
  const [readiness, setReadiness] = useState<SohoPassportReadiness | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadReadiness = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      setReadiness(await getPropertyPassportReadiness(propertyId));
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "Unable to load SOHO Passport readiness.");
    } finally {
      setIsLoading(false);
    }
  }, [propertyId]);

  useEffect(() => {
    void loadReadiness();
  }, [loadReadiness]);

  if (isLoading) {
    return <LoadingState label="Loading SOHO readiness" />;
  }

  if (error && !readiness) {
    return <ErrorState message={error} onRetry={() => void loadReadiness()} />;
  }

  if (!readiness) {
    return <EmptyState title="Readiness record not found." message="The requested SOHO workspace could not be loaded." />;
  }

  return (
    <div className="space-y-6">
      <section className="fop-card p-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-sm font-medium text-[#7D8CA3]">SOHO Phase I Production Passport Load</p>
            <h2 className="mt-2 text-2xl font-semibold text-white">{readiness.property.name}</h2>
            <p className="mt-1 text-[#B6C1CF]">Buildings Under Protection™ readiness workspace</p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <StatusBadge status={readiness.readiness_state} />
            <StatusBadge status={formatControlledValue(readiness.protected_state_status)} />
          </div>
        </div>
        <div className="mt-5 grid gap-4 md:grid-cols-5">
          {[
            { label: "Records", value: `${readiness.records_present}/${readiness.expected_records}` },
            { label: "Closeout", value: `${readiness.closeout_score}%`, className: scoreTone(readiness.closeout_score) },
            { label: "Evidence Complete", value: readiness.evidence_categories_complete },
            { label: "Missing Evidence", value: readiness.evidence_categories_missing },
            { label: "Client Visible", value: readiness.client_visible_evidence_count }
          ].map((item) => (
            <div key={item.label}>
              <p className="text-sm font-medium text-[#7D8CA3]">{item.label}</p>
              <p className={`mt-1 text-2xl font-semibold ${item.className ?? "text-white"}`}>{item.value}</p>
            </div>
          ))}
        </div>
        <div className="mt-5 flex flex-wrap items-center gap-3 border-t border-white/10 pt-4 text-sm">
          <ClipboardCheck size={18} className="text-sky-300" />
          <span className="font-medium text-white">Next action:</span>
          <span className="text-[#B6C1CF]">{readiness.next_action}</span>
        </div>
      </section>

      {error ? <ErrorState message={error} onRetry={() => void loadReadiness()} /> : null}

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {readiness.records.map((record) => (
          <article key={record.role} className="fop-card p-5">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="font-semibold text-white">{record.label}</p>
                <p className="mt-1 text-sm text-[#7D8CA3]">{record.building?.name ?? "Record not mapped"}</p>
              </div>
              <StatusBadge status={record.readiness_state} />
            </div>
            <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
              <div>
                <p className="text-[#7D8CA3]">Closeout</p>
                <p className={`font-semibold ${scoreTone(record.closeout_score)}`}>{record.closeout_score}%</p>
              </div>
              <div>
                <p className="text-[#7D8CA3]">Passport</p>
                <p className="font-semibold text-white">{record.passport_status}</p>
              </div>
              <div>
                <p className="text-[#7D8CA3]">Evidence</p>
                <p className="font-semibold text-white">{record.documents_count}</p>
              </div>
              <div>
                <p className="text-[#7D8CA3]">Assets</p>
                <p className="font-semibold text-white">{record.assets_count}</p>
              </div>
            </div>
            <div className="mt-4 space-y-2 text-sm">
              <p className="font-medium text-white">Next</p>
              <p className="text-[#B6C1CF]">{record.next_action}</p>
            </div>
            {record.building ? (
              <div className="mt-5 flex flex-wrap gap-2">
                <Link className="inline-flex items-center gap-2 rounded-md border border-white/10 px-3 py-2 text-sm font-medium text-white hover:border-white/30" href={record.library_url ?? `/buildings/${record.building.id}/library`}>
                  <FolderOpen size={15} />
                  Evidence
                </Link>
                <Link className="inline-flex items-center gap-2 rounded-md border border-white/10 px-3 py-2 text-sm font-medium text-white hover:border-white/30" href={record.passport_url ?? `/buildings/${record.building.id}/passport`}>
                  <ShieldCheck size={15} />
                  Passport
                </Link>
              </div>
            ) : null}
          </article>
        ))}
      </section>

      <section className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="fop-card p-5">
          <div className="flex items-center gap-2">
            <FileSearch size={18} className="text-sky-300" />
            <h3 className="text-lg font-semibold text-white">Missing Evidence</h3>
          </div>
          <div className="mt-4 space-y-2">
            {readiness.blocking_items.slice(0, 16).map((item) => (
              <div key={item} className="rounded-md border border-white/10 px-3 py-2 text-sm text-[#B6C1CF]">
                {item}
              </div>
            ))}
            {!readiness.blocking_items.length ? <EmptyState title="No blockers recorded." message="The current records do not report missing readiness blockers." /> : null}
          </div>
        </div>

        <div className="fop-card p-5">
          <div className="flex items-center gap-2">
            <Wrench size={18} className="text-sky-300" />
            <h3 className="text-lg font-semibold text-white">Handover Controls</h3>
          </div>
          <div className="mt-4 space-y-4">
            {readiness.records.filter((record) => record.present).map((record) => (
              <div key={record.role} className="border-b border-white/10 pb-4 last:border-b-0 last:pb-0">
                <p className="font-medium text-white">{record.label}</p>
                <dl className="mt-2 space-y-1 text-sm">
                  <div className="flex justify-between gap-3">
                    <dt className="text-[#7D8CA3]">Recipient</dt>
                    <dd className="text-right text-[#B6C1CF]">{record.handover?.owner_property_manager_recipient ?? "Not recorded"}</dd>
                  </div>
                  <div className="flex justify-between gap-3">
                    <dt className="text-[#7D8CA3]">Delivery</dt>
                    <dd className="text-right text-[#B6C1CF]">{record.handover?.delivery_status ?? "Not Started"}</dd>
                  </div>
                  <div className="flex justify-between gap-3">
                    <dt className="text-[#7D8CA3]">Portal</dt>
                    <dd className="text-right text-[#B6C1CF]">{record.handover?.portal_access_status}</dd>
                  </div>
                  <div className="flex justify-between gap-3">
                    <dt className="text-[#7D8CA3]">Version</dt>
                    <dd className="text-right text-[#B6C1CF]">{record.handover?.passport_version ?? "Unversioned"}</dd>
                  </div>
                </dl>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
