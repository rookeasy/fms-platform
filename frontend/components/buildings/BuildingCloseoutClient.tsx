"use client";

import Link from "next/link";
import { CheckCircle2, CircleAlert, FileText } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";

import { EmptyState } from "@/components/EmptyState";
import { ErrorState } from "@/components/ErrorState";
import { LoadingState } from "@/components/LoadingState";
import { PassportSection } from "@/components/PassportSection";
import { StatusBadge } from "@/components/StatusBadge";
import { formatControlledValue } from "@/lib/controlled-values";
import {
  type Asset,
  type Building,
  type DocumentRecord,
  getBuilding,
  listBuildingAssets,
  listBuildingDocuments,
  listBuildings
} from "@/lib/fms-api";

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
  "Fuzion Fire Service ITM Transition",
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
  const [resolvedBuildingId, setResolvedBuildingId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadCloseout = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const nextBuildingId = await resolveBuildingId(buildingId);
      const [loadedBuilding, loadedAssets, loadedDocuments] = await Promise.all([
        getBuilding(nextBuildingId),
        listBuildingAssets(nextBuildingId),
        listBuildingDocuments(nextBuildingId)
      ]);
      setResolvedBuildingId(nextBuildingId);
      setBuilding(loadedBuilding);
      setAssets(loadedAssets);
      setDocuments(loadedDocuments);
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
    return CLOSEOUT_SECTIONS.map((section) => ({
      section,
      documents: documents.filter((document) => extractSection(document) === section)
    }));
  }, [documents]);

  const completedSections = groupedDocuments.filter((group) => group.documents.length > 0).length;
  const missingSections = groupedDocuments.filter((group) => group.documents.length === 0);
  const clientVisibleCount = documents.filter((document) => document.is_public_to_client).length;
  const passportRecordCount = documents.filter((document) => document.is_passport_record).length;
  const isReadyForHandover = missingSections.length === 0 && documents.length > 0 && assets.length > 0;
  const primaryEvidence = documents[0] ?? null;

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
      <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-sm font-medium text-slate-500">{building.bpid}</p>
            <h2 className="mt-2 text-2xl font-semibold text-slate-950">{building.name}</h2>
            <p className="mt-1 text-slate-600">
              {[building.address_line_1, building.city, building.province_state, building.postal_code].filter(Boolean).join(", ")}
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <StatusBadge status={isReadyForHandover ? "Ready for Handover" : "Missing Items"} />
            {resolvedBuildingId ? (
              <Link href={`/buildings/${resolvedBuildingId}`} className="h-10 rounded-md border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-800">
                Building Profile
              </Link>
            ) : null}
          </div>
        </div>
      </section>

      <div className="grid gap-4 md:grid-cols-4">
        {[
          ["Sections Complete", `${completedSections}/${CLOSEOUT_SECTIONS.length}`],
          ["Evidence Records", `${documents.length}`],
          ["Client Visible", `${clientVisibleCount}`],
          ["Passport Records", `${passportRecordCount}`]
        ].map(([title, value]) => (
          <div key={title} className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
            <p className="text-sm font-medium text-slate-500">{title}</p>
            <p className="mt-2 text-2xl font-semibold text-slate-950">{value}</p>
          </div>
        ))}
      </div>

      <div className="grid gap-6 xl:grid-cols-[360px_1fr]">
        <div className="space-y-6">
          <PassportSection title="Closeout Checklist">
            <div className="space-y-3">
              {groupedDocuments.map((group) => {
                const complete = group.documents.length > 0;
                return (
                  <div key={group.section} className="flex items-start gap-3 rounded-md border border-slate-200 p-3">
                    {complete ? <CheckCircle2 className="mt-0.5 text-emerald-600" size={18} /> : <CircleAlert className="mt-0.5 text-amber-600" size={18} />}
                    <div>
                      <div className="text-sm font-semibold text-slate-950">{group.section}</div>
                      <div className="text-xs text-slate-600">{complete ? `${group.documents.length} evidence record(s)` : "Missing evidence"}</div>
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
                ["Contractor", fieldFromDescription(primaryEvidence, "Contractor") ?? "Fuzion Fire Inc."],
                ["Approving Authority", fieldFromDescription(primaryEvidence, "Approving authority") ?? building.ahj_name],
                ["Asset Register", `${assets.length} asset(s)`],
                ["Status", isReadyForHandover ? "Ready for Handover" : "Missing Items"]
              ].map(([label, value]) => (
                <div key={label}>
                  <dt className="text-xs font-semibold uppercase text-slate-500">{label}</dt>
                  <dd className="mt-1 text-sm text-slate-900">{value || "-"}</dd>
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
                    <div key={document.id} className="rounded-md border border-slate-200 p-4">
                      <div className="flex flex-wrap items-start justify-between gap-3">
                        <div className="min-w-0">
                          <div className="flex items-center gap-2">
                            <FileText size={16} className="text-slate-500" />
                            <h3 className="text-sm font-semibold text-slate-950">{document.title}</h3>
                          </div>
                          <p className="mt-1 text-sm text-slate-600">{formatControlledValue(document.document_type)}</p>
                          <p className="mt-2 text-sm text-slate-700">{fieldFromDescription(document, "Evidence purpose") || document.description || "-"}</p>
                          {fieldFromDescription(document, "System/location") ? (
                            <p className="mt-2 text-xs font-semibold uppercase text-slate-500">
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
