"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { EmptyState } from "@/components/EmptyState";
import { ErrorState } from "@/components/ErrorState";
import { LoadingState } from "@/components/LoadingState";
import { PassportSection } from "@/components/PassportSection";
import { StatusBadge } from "@/components/StatusBadge";
import { Timeline } from "@/components/Timeline";
import { formatControlledValue } from "@/lib/controlled-values";
import { getDocumentDownloadUrl, getPassport, type PassportSummary } from "@/lib/fms-api";

type BuildingPassportClientProps = {
  buildingId: string;
};

export function BuildingPassportClient({ buildingId }: BuildingPassportClientProps) {
  const [passport, setPassport] = useState<PassportSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadPassport = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      setPassport(await getPassport(buildingId));
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "Unable to load Building Protection Passport.");
    } finally {
      setIsLoading(false);
    }
  }, [buildingId]);

  useEffect(() => {
    void loadPassport();
  }, [loadPassport]);

  if (isLoading) {
    return <LoadingState label="Loading Building Protection Passport" />;
  }

  if (error) {
    return <ErrorState message={error} onRetry={() => void loadPassport()} />;
  }

  if (!passport) {
    return <EmptyState title="Passport unavailable." message="The Building Protection Passport could not be loaded." />;
  }

  const timelineItems = passport.timeline.map((item) => ({
    title: item.label,
    date: new Date(item.occurred_at).toLocaleString(),
    description: formatControlledValue(item.event_type)
  }));

  return (
    <div className="space-y-6">
      <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <p className="text-sm font-medium text-slate-500">{passport.building.bpid}</p>
        <div className="mt-2 flex flex-wrap items-start justify-between gap-4">
          <div>
            <h2 className="text-2xl font-semibold text-slate-950">{passport.building.name}</h2>
            <p className="mt-1 text-slate-600">
              {[
                passport.building.address_line_1,
                passport.building.city,
                passport.building.province_state,
                passport.building.postal_code
              ]
                .filter(Boolean)
                .join(", ")}
            </p>
          </div>
          <Link href={`/buildings/${passport.building.id}`} className="h-10 rounded-md border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-800">
            Building Profile
          </Link>
        </div>
      </section>

      <div className="grid gap-6 xl:grid-cols-[1fr_380px]">
        <div className="space-y-6">
          <PassportSection title="Building Profile">
            <dl className="grid gap-4 sm:grid-cols-2">
              {[
                ["Building Type", formatControlledValue(passport.building.building_type)],
                ["Status", formatControlledValue(passport.building.status)],
                ["Owner", passport.building.owner_name],
                ["Property Manager", passport.building.property_manager_name],
                ["AHJ", passport.building.ahj_name],
                ["Fire Department", passport.building.fire_department]
              ].map(([label, value]) => (
                <div key={label}>
                  <dt className="text-sm font-medium text-slate-500">{label}</dt>
                  <dd className="mt-1 text-sm text-slate-950">{value || "-"}</dd>
                </div>
              ))}
            </dl>
          </PassportSection>

          <PassportSection title="Contacts">
            {passport.contacts.length ? (
              <div className="grid gap-3 md:grid-cols-2">
                {passport.contacts.map((contact) => (
                  <div key={contact.id} className="rounded-md border border-slate-200 p-4">
                    <div className="font-semibold text-slate-950">{contact.name}</div>
                    <div className="text-sm text-slate-600">{formatControlledValue(contact.contact_type)}</div>
                    <div className="mt-2 text-sm text-slate-700">{contact.email || contact.phone || "-"}</div>
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState title="No contacts." message="No building contacts are attached to this Passport." />
            )}
          </PassportSection>

          <PassportSection title="Assets">
            {passport.assets.length ? (
              <div className="grid gap-3 md:grid-cols-2">
                {passport.assets.map((asset) => (
                  <div key={asset.id} className="rounded-md border border-slate-200 p-4">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <div className="font-semibold text-slate-950">{asset.name}</div>
                      <StatusBadge status={formatControlledValue(asset.status)} />
                    </div>
                    <div className="mt-1 text-sm text-slate-600">{asset.asset_type?.name ?? "Unknown asset type"}</div>
                    <div className="mt-2 text-sm text-slate-700">{formatControlledValue(asset.condition_rating) || "Condition unknown"}</div>
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState title="No assets." message="No assets are attached to this Passport yet." />
            )}
          </PassportSection>

          <PassportSection title="Passport Documents">
            {passport.documents.length ? (
              <div className="grid gap-3">
                {passport.documents.map((document) => (
                  <div key={document.id} className="flex flex-wrap items-center justify-between gap-3 rounded-md border border-slate-200 p-4">
                    <div>
                      <div className="font-semibold text-slate-950">{document.title}</div>
                      <div className="text-sm text-slate-600">
                        {formatControlledValue(document.document_type)} - v{document.version_number}
                      </div>
                    </div>
                    <a href={getDocumentDownloadUrl(document.id)} className="h-9 rounded-md border border-slate-300 px-3 py-2 text-sm font-semibold text-slate-800">
                      Download
                    </a>
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState title="No Passport documents." message="Mark uploaded documents as Passport Records to include them here." />
            )}
          </PassportSection>
        </div>

        <div className="space-y-6">
          <PassportSection title="Timeline">
            {timelineItems.length ? <Timeline items={timelineItems} /> : <EmptyState title="No timeline records." message="Asset and document activity will appear here." />}
          </PassportSection>
          <PassportSection title="Health Score">
            <div className="text-3xl font-semibold text-slate-950">{passport.health_score.score ?? "-"}</div>
            <p className="mt-1 text-sm text-slate-600">{formatControlledValue(passport.health_score.status)}</p>
          </PassportSection>
          <PassportSection title="Membership">
            <div className="text-lg font-semibold text-slate-950">{passport.membership.plan ?? "No active plan"}</div>
            <p className="mt-1 text-sm text-slate-600">{formatControlledValue(passport.membership.status)}</p>
          </PassportSection>
        </div>
      </div>
    </div>
  );
}
