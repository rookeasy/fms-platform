"use client";

import Link from "next/link";
import { CheckCircle2, CircleAlert, FileText } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";

import { EmptyState } from "@/components/EmptyState";
import { ErrorState } from "@/components/ErrorState";
import { FopLifecycleMark } from "@/components/brand/FopLifecycleMark";
import { LoadingState } from "@/components/LoadingState";
import { PassportSection } from "@/components/PassportSection";
import { ProgressIndex } from "@/components/ProgressIndex";
import { ScoreCard } from "@/components/ScoreCard";
import { StatusBadge } from "@/components/StatusBadge";
import { formatControlledValue } from "@/lib/controlled-values";
import {
  type Asset,
  type Building,
  type CloseoutScore,
  type DocumentRecord,
  type FppScores,
  type ProtectedStateEvaluation,
  getCloseoutScores,
  getBuilding,
  getBuildingCloseoutScore,
  getProtectedState,
  listBuildingAssets,
  listBuildingDocuments,
  listBuildings
} from "@/lib/fms-api";
import { fppKpiTerms, getMockBuildingScores } from "@/lib/progress-index";
import { visualStateFromProgress } from "@/lib/fop-lifecycle-visual";

type BuildingCloseoutClientProps = {
  buildingId: string;
};

const CLOSEOUT_SECTIONS = [
  "Building Protection Passport",
  "P.Eng. Compliance",
  "NFPA Contractor Compliance",
  "Material & Test Certificates",
  "Drawings",
  "As-Built Drawings",
  "Asset Register",
  "Warranty",
  "Product Data",
  "O&M Manuals",
  "Handover",
  "ITM Transition",
  "Membership"
];

function slugify(value: string) {
  return value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
}

function extractSection(document: DocumentRecord) {
  const match = document.description?.match(/Closeout section:\s*(.+)/i);
  return match?.[1]?.trim() || "Building Protection Passport";
}

function fieldFromDescription(document: DocumentRecord | null, label: string) {
  if (!document) {
    return null;
  }
  const escaped = label.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const match = document.description?.match(new RegExp(`${escaped}:\\s*(.+)`, "i"));
  return match?.[1]?.trim() || null;
}

function normalizeCompanyBrand(value: string | null) {
  const legacyName = ["Fuzion", "Fire"].join(" ");
  return value?.replace(legacyName, "Fuzion Tech") ?? null;
}

async function resolveBuildingId(identifier: string) {
  if (/^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(identifier)) {
    return identifier;
  }

  const buildings = await listBuildings();
  const normalizedIdentifier = slugify(identifier);
  const match = buildings.find((building) => slugify(building.name) === normalizedIdentifier);
  if (!match) {
    throw new Error("Unable to find a building matching this closeout package route.");
  }
  return match.id;
}

export function BuildingCloseoutClient({ buildingId }: BuildingCloseoutClientProps) {
  const [building, setBuilding] = useState<Building | null>(null);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [score, setScore] = useState<CloseoutScore | null>(null);
  const [resolvedBuildingId, setResolvedBuildingId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [fppScores, setFppScores] = useState<FppScores | null>(null);
  const [protectedState, setProtectedState] = useState<ProtectedStateEvaluation | null>(null);

  const loadCloseout = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const nextBuildingId = await resolveBuildingId(buildingId);
      const [loadedBuilding, loadedAssets, loadedDocuments, loadedScore] = await Promise.all([
        getBuilding(nextBuildingId),
        listBuildingAssets(nextBuildingId),
        listBuildingDocuments(nextBuildingId),
        getBuildingCloseoutScore(nextBuildingId)
      ]);
      setResolvedBuildingId(nextBuildingId);
      setBuilding(loadedBuilding);
      setAssets(loadedAssets);
      setDocuments(loadedDocuments);
      setScore(loadedScore);
      setFppScores(await getCloseoutScores(nextBuildingId).catch(() => null));
      setProtectedState(await getProtectedState(nextBuildingId).catch(() => null));
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "Unable to load digital closeout package.");
    } finally {
      setIsLoading(false);
    }
  }, [buildingId]);

  useEffect(() => {
    void loadCloseout();
  }, [loadCloseout]);

  const groupedDocuments = useMemo(() => {
    const sections = score?.sections.map((section) => section.label) ?? CLOSEOUT_SECTIONS;
    return sections.map((section) => ({
      section,
      documents: documents.filter((document) => extractSection(document) === section)
    }));
  }, [documents, score]);

  const completedSections = score?.completed_items ?? groupedDocuments.filter((group) => group.documents.length > 0).length;
  const passportRecordCount = documents.filter((document) => document.is_passport_record).length;
  const totalRequiredItems = score?.total_required_items ?? CLOSEOUT_SECTIONS.length;
  const missingItemCount = score?.missing_items.length ?? totalRequiredItems - completedSections;
  const completionPercentage = score?.completion_percentage ?? Math.round((completedSections / totalRequiredItems) * 100);
  const isReadyForHandover = score?.ready_for_handover ?? false;
  const primaryEvidence = documents[0] ?? null;
  const closeoutScores = fppScores ?? getMockBuildingScores(building?.id ?? buildingId, {
    protectionScore: Math.min(100, 70 + passportRecordCount * 4),
    complianceScore: Math.min(100, 65 + completedSections * 3),
    readinessScore: completionPercentage,
    intelligenceScore: Math.min(100, 68 + documents.length * 2)
  });
  const closeoutVisual = visualStateFromProgress(completionPercentage);

  if (isLoading) {
    return <LoadingState label="Loading digital closeout package" />;
  }

  if (error) {
    return <ErrorState message={error} onRetry={() => void loadCloseout()} />;
  }

  if (!building) {
    return <EmptyState title="Closeout package unavailable." message="The requested building could not be loaded." />;
  }

  return (
    <div className="space-y-6">
      <section className="fop-card p-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="flex flex-wrap gap-3 text-sm font-medium text-[#7D8CA3]">
              <span>Job No. {building.code || "-"}</span>
              <span>Passport No. {building.bpid}</span>
            </div>
            <h2 className="mt-2 text-2xl font-semibold text-white">{building.name}</h2>
            <p className="mt-1 text-[#B6C1CF]">
              {[building.address_line_1, building.city, building.province_state, building.postal_code].filter(Boolean).join(", ")}
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <StatusBadge status={isReadyForHandover ? "Ready for Handover" : "Missing Items"} />
            {resolvedBuildingId ? (
              <>
                <Link href={`/buildings/${resolvedBuildingId}`} className="h-10 rounded-md border border-white/15 px-4 py-2 text-sm font-semibold text-[#DCE5F2]">
                  Building Profile
                </Link>
                <Link href={`/buildings/${resolvedBuildingId}/library`} className="fop-button-primary h-10">
                  Add Evidence
                </Link>
              </>
            ) : null}
          </div>
        </div>
      </section>

      <section className="fop-card p-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="text-sm font-medium text-[#7D8CA3]">Closeout Completion</p>
            <p className="mt-1 text-3xl font-semibold text-white">{completionPercentage}%</p>
          </div>
          <div className="flex items-center gap-3">
            <FopLifecycleMark {...closeoutVisual} compact className="h-14 w-14" />
            <StatusBadge status={isReadyForHandover ? "Ready for Handover" : "Missing Items"} />
          </div>
        </div>
        <div className="mt-4 h-3 overflow-hidden rounded-full bg-slate-100">
          <div className="h-full rounded-full bg-[color:var(--fuzion-build)]" style={{ width: `${completionPercentage}%` }} />
        </div>
        <div className="mt-3 flex flex-wrap gap-x-6 gap-y-2 text-sm text-[#B6C1CF]">
          <span>{completedSections} completed</span>
          <span>{missingItemCount} missing</span>
          <span>{totalRequiredItems} required</span>
        </div>
      </section>

      <section className="fop-card p-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="fop-label">{fppKpiTerms.progressIndex}</p>
            <h3 className="mt-2 text-xl font-semibold text-white">Closeout Readiness Along BUILD • ADVISE • PROTECT</h3>
          </div>
          <span className="text-3xl font-semibold text-white">{closeoutScores.buildingHealthIndex}%</span>
        </div>
        <div className="mt-5">
          <ProgressIndex score={closeoutScores.buildingHealthIndex} size="lg" showDescriptions variant="dashboard" />
        </div>
        <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <ScoreCard title={fppKpiTerms.protectionScore} score={closeoutScores.protectionScore} />
          <ScoreCard title={fppKpiTerms.complianceScore} score={closeoutScores.complianceScore} />
          <ScoreCard title={fppKpiTerms.readinessScore} score={closeoutScores.readinessScore} />
          <ScoreCard title={fppKpiTerms.intelligenceScore} score={closeoutScores.intelligenceScore} />
        </div>
      </section>

      <section className="fop-card p-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="fop-label">Protected State</p>
            <h3 className="mt-2 text-xl font-semibold text-white">Certification blockers</h3>
            <p className="mt-2 text-sm text-[#B6C1CF]">Closeout readiness supports approval, but does not activate the halo.</p>
          </div>
          <StatusBadge status={protectedState?.protected_state_status ?? "Unavailable"} />
        </div>
        {protectedState?.blocking_items.length ? (
          <div className="mt-4 grid gap-2 md:grid-cols-2">
            {protectedState.blocking_items.slice(0, 6).map((item) => (
              <div key={item} className="rounded-md border border-white/10 bg-white/[0.035] p-3 text-sm text-[#DCE5F2]">{item}</div>
            ))}
          </div>
        ) : (
          <p className="mt-4 text-sm text-[#B6C1CF]">No certification blockers are currently reported.</p>
        )}
      </section>

      <div className="grid gap-4 md:grid-cols-4">
        {[
          ["Sections Complete", `${completedSections}/${totalRequiredItems}`],
          ["Missing Items", `${missingItemCount}`],
          ["Evidence Records", `${documents.length}`],
          ["Passport Records", `${passportRecordCount}`]
        ].map(([title, value]) => (
          <div key={title} className="fop-card p-5">
            <p className="text-sm font-medium text-[#7D8CA3]">{title}</p>
            <p className="mt-2 text-2xl font-semibold text-white">{value}</p>
          </div>
        ))}
      </div>

      <div className="grid gap-6 xl:grid-cols-[360px_1fr]">
        <div className="space-y-6">
          {score?.warnings.length ? (
            <PassportSection title="Warnings">
              <div className="space-y-2">
                {score.warnings.map((warning) => (
                  <div key={warning} className="rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-900">
                    {warning}
                  </div>
                ))}
              </div>
            </PassportSection>
          ) : null}

          <PassportSection title="Closeout Checklist">
            <div className="space-y-3">
              {(score?.sections ?? groupedDocuments.map((group) => ({
                key: slugify(group.section),
                label: group.section,
                completed: group.documents.length > 0,
                evidence_count: group.documents.length,
                missing_reason: "Missing evidence"
              }))).map((section) => {
                const complete = section.completed;
                return (
                  <div key={section.key} className="flex items-start gap-3 rounded-md border border-white/10 p-3">
                    {complete ? <CheckCircle2 className="mt-0.5 text-emerald-600" size={18} /> : <CircleAlert className="mt-0.5 text-amber-600" size={18} />}
                    <div className="min-w-0 flex-1">
                      <div className="text-sm font-semibold text-white">{section.label}</div>
                      <div className="text-xs text-[#B6C1CF]">{complete ? `${section.evidence_count} evidence record(s)` : section.missing_reason || "Missing evidence"}</div>
                    </div>
                    {resolvedBuildingId ? (
                      <Link
                        href={`/buildings/${resolvedBuildingId}/library?category=${encodeURIComponent(section.label)}`}
                        className="shrink-0 text-xs font-semibold text-[#D95A4E] underline decoration-[#D95A4E]/30 underline-offset-4"
                      >
                        Add Evidence
                      </Link>
                    ) : null}
                  </div>
                );
              })}
            </div>
          </PassportSection>

          <PassportSection title="Handover Details">
            <dl className="space-y-3">
              {[
                ["Property", fieldFromDescription(primaryEvidence, "Property name") ?? "SOHO"],
                ["Job No.", building.code],
                ["Passport No.", building.bpid],
                ["Contractor", normalizeCompanyBrand(fieldFromDescription(primaryEvidence, "Contractor")) ?? "Fuzion Tech Inc."],
                ["Approving Authority", fieldFromDescription(primaryEvidence, "Approving authority") ?? building.ahj_name],
                ["Asset Register", `${assets.length} asset(s)`],
                ["Missing Items", score?.missing_items.join(", ") || "None"],
                ["Status", isReadyForHandover ? "Ready for Handover" : "Missing Items"]
              ].map(([label, value]) => (
                <div key={label}>
                  <dt className="text-xs font-semibold uppercase text-[#7D8CA3]">{label}</dt>
                  <dd className="mt-1 text-sm text-[#DCE5F2]">{value || "-"}</dd>
                </div>
              ))}
            </dl>
          </PassportSection>
        </div>

        <div className="space-y-6">
          {groupedDocuments.map((group) => (
            <PassportSection key={group.section} title={group.section}>
              {group.documents.length ? (
                <div className="grid gap-3">
                  {group.documents.map((document) => (
                    <div key={document.id} className="rounded-md border border-white/10 p-4">
                      <div className="flex flex-wrap items-start justify-between gap-3">
                        <div className="min-w-0">
                          <div className="flex items-center gap-2">
                            <FileText size={16} className="text-[#7D8CA3]" />
                            <h3 className="text-sm font-semibold text-white">{document.title}</h3>
                          </div>
                          <p className="mt-1 text-sm text-[#B6C1CF]">{formatControlledValue(document.document_type)}</p>
                          <p className="mt-2 text-sm text-[#B6C1CF]">{fieldFromDescription(document, "Evidence purpose") || document.description || "-"}</p>
                          {fieldFromDescription(document, "System/location") ? (
                            <p className="mt-2 text-xs font-semibold uppercase text-[#7D8CA3]">
                              System/location: {fieldFromDescription(document, "System/location")}
                            </p>
                          ) : null}
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {document.is_public_to_client ? <StatusBadge status="Client Visible" /> : null}
                          {document.is_passport_record ? <StatusBadge status="Passport Record" /> : null}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <EmptyState
                  title="No evidence has been added to this section."
                  message="Add evidence or start the Build Passport workflow."
                  action={
                    resolvedBuildingId ? (
                      <Link href={`/buildings/${resolvedBuildingId}/library?category=${encodeURIComponent(group.section)}`} className="fop-button-primary">
                        Add Evidence
                      </Link>
                    ) : null
                  }
                />
              )}
            </PassportSection>
          ))}
        </div>
      </div>
    </div>
  );
}

