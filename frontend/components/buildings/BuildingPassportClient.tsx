"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { EmptyState } from "@/components/EmptyState";
import { ErrorState } from "@/components/ErrorState";
import { ProgressIndex } from "@/components/ProgressIndex";
import { LoadingState } from "@/components/LoadingState";
import { PassportSection } from "@/components/PassportSection";
import { StatusBadge } from "@/components/StatusBadge";
import { Timeline } from "@/components/Timeline";
import { formatControlledValue } from "@/lib/controlled-values";
import { getBuildingScores, getDocumentDownloadUrl, getPassport, type FppScores, type PassportSummary } from "@/lib/fms-api";
import { getApiBuildingLifecycle, lifecycleLabels } from "@/lib/lifecycle";
import { fppKpiTerms, getMockBuildingScores } from "@/lib/progress-index";

type BuildingPassportClientProps = {
  buildingId: string;
};

export function BuildingPassportClient({ buildingId }: BuildingPassportClientProps) {
  const [passport, setPassport] = useState<PassportSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [fppScores, setFppScores] = useState<FppScores | null>(null);

  const loadPassport = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      setPassport(await getPassport(buildingId));
      setFppScores(await getBuildingScores(buildingId).catch(() => null));
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
  const healthScore = passport.health_score.score ?? 82;
  const buildingScores = fppScores ?? getMockBuildingScores(passport.building.id, {
    protectionScore: healthScore,
    complianceScore: Math.max(0, Math.min(100, healthScore + 4)),
    readinessScore: Math.max(0, Math.min(100, healthScore - 2)),
    intelligenceScore: Math.max(0, Math.min(100, healthScore - 7))
  });
  const lifecycleStage = getApiBuildingLifecycle(passport.building);

  return (
    <div className="space-y-6">
      <section className="fop-card p-6">
        <div className="grid gap-6 xl:grid-cols-[1fr_520px]">
          <div>
            <div className="flex flex-wrap gap-3 text-sm font-medium text-[#7D8CA3]">
              <span>Passport No. {passport.building.bpid}</span>
              <span>Job No. {passport.building.code || "-"}</span>
            </div>
            <h2 className="text-2xl font-semibold text-white">{passport.building.name}</h2>
            <p className="mt-1 text-[#B6C1CF]">
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
          <div className="grid gap-3 sm:grid-cols-3">
            <div className="rounded-xl border border-white/10 bg-white/[0.035] p-4">
              <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[#7D8CA3]">Lifecycle Stage</p>
              <p className="mt-2 text-xl font-semibold text-white">{lifecycleLabels[lifecycleStage]}</p>
            </div>
            <div className="rounded-xl border border-white/10 bg-white/[0.035] p-4">
              <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[#7D8CA3]">{fppKpiTerms.protectionScore}</p>
              <p className="mt-2 text-xl font-semibold text-white">{buildingScores.protectionScore}%</p>
            </div>
            <div className="rounded-xl border border-white/10 bg-white/[0.035] p-4">
              <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[#7D8CA3]">{fppKpiTerms.buildingHealthIndex}</p>
              <p className="mt-2 text-xl font-semibold text-white">{buildingScores.buildingHealthIndex}%</p>
            </div>
          </div>
        </div>
        <div className="mt-5 flex flex-wrap items-center justify-between gap-4 border-t border-white/10 pt-5">
          <ProgressIndex score={buildingScores.buildingHealthIndex} size="sm" variant="compact" showScore={false} />
          <Link href={`/buildings/${passport.building.id}`} className="h-10 rounded-md border border-white/15 px-4 py-2 text-sm font-semibold text-[#DCE5F2]">
            Building Profile
          </Link>
        </div>
      </section>

      <div className="grid gap-6 xl:grid-cols-[1fr_380px]">
        <div className="space-y-6">
          <PassportSection title="Contacts">
            {passport.contacts.length ? (
              <div className="grid gap-3 md:grid-cols-2">
                {passport.contacts.map((contact) => (
                  <div key={contact.id} className="rounded-md border border-white/10 p-4">
                    <div className="font-semibold text-white">{contact.name}</div>
                    <div className="text-sm text-[#B6C1CF]">{formatControlledValue(contact.contact_type)}</div>
                    <div className="mt-2 text-sm text-[#B6C1CF]">{contact.email || contact.phone || "-"}</div>
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
                  <div key={asset.id} className="rounded-md border border-white/10 p-4">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <div className="font-semibold text-white">{asset.name}</div>
                      <StatusBadge status={formatControlledValue(asset.status)} />
                    </div>
                    <div className="mt-1 text-sm text-[#B6C1CF]">{asset.asset_type?.name ?? "Unknown asset type"}</div>
                    <div className="mt-2 text-sm text-[#B6C1CF]">{formatControlledValue(asset.condition_rating) || "Condition unknown"}</div>
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
                  <div key={document.id} className="flex flex-wrap items-center justify-between gap-3 rounded-md border border-white/10 p-4">
                    <div>
                      <div className="font-semibold text-white">{document.title}</div>
                      <div className="text-sm text-[#B6C1CF]">
                        {formatControlledValue(document.document_type)} - v{document.version_number}
                      </div>
                    </div>
                    <a href={getDocumentDownloadUrl(document.id)} className="h-9 rounded-md border border-white/15 px-3 py-2 text-sm font-semibold text-[#DCE5F2]">
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
          <PassportSection title="Membership">
            <div className="text-lg font-semibold text-white">{passport.membership.plan ?? "No active plan"}</div>
            <p className="mt-1 text-sm text-[#B6C1CF]">{formatControlledValue(passport.membership.status)}</p>
          </PassportSection>
        </div>
      </div>
    </div>
  );
}

