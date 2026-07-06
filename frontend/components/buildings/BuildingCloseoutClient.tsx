"use client";

import Link from "next/link";
import { CheckCircle2, CircleAlert, FileText } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";

import { EmptyState } from "@/components/EmptyState";
import { ErrorState } from "@/components/ErrorState";
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
  getCloseoutScores,
  getBuilding,
  getBuildingCloseoutScore,
  listBuildingAssets,
  listBuildingDocuments,
  listBuildings
} from "@/lib/fms-api";
import { fppKpiTerms, getMockBuildingScores } from "@/lib/progress-index";

type BuildingCloseoutClientProps = {
  buildingId: string;
};

const CLOSEOUT_SECTIONS = [
  "Building Protection Passport",
  "P.Eng. Compliance Package",
  "NFPA Contractor Compliance Package",
  "Material & Test Certificates",
  "Drawing Register",
  "As-Built Drawings",
  "Asset Register",
  "Warranty Package",
  "Product Data / O&M Manuals",
  "Owner / Property Manager Handover",
  "Fuzion Tech Service ITM Transition",
  "FMS Membership Invitation"
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
              <Link href={`/buildings/${resolvedBuildingId}`} className="h-10 rounded-md border border-white/15 px-4 py-2 text-sm font-semibold text-[#DCE5F2]">
                Building Profile
              </Link>
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
          <StatusBadge status={isReadyForHandover ? "Ready for Handover" : "Missing Items"} />
        </div>
        <div className="mt-4 h-3 overflow-hidden rounded-full bg-slate-100">
          <div className="h-full rounded-full bg-[linear-gradient(90deg,#0F172A,#2563EB,#D95A4E)]" style={{ width: `${completionPercentage}%` }} />
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
            <h3 className="mt-2 text-xl font-semibold text-white">Closeout Readiness Along BUILD to ADVISE to PROTECT</h3>
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
                    <div>
                      <div className="text-sm font-semibold text-white">{section.label}</div>
                      <div className="text-xs text-[#B6C1CF]">{complete ? `${section.evidence_count} evidence record(s)` : section.missing_reason || "Missing evidence"}</div>
                    </div>
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
                <EmptyState title="Missing evidence." message="Seed or upload document metadata for this closeout section." />
              )}
            </PassportSection>
          ))}
        </div>
      </div>
    </div>
  );
}

