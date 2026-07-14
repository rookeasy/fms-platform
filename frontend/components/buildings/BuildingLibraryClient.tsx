"use client";

import Link from "next/link";
import { BookOpen, FilePlus2, RefreshCcw, ShieldCheck, Sparkles } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";

import { EmptyState } from "@/components/EmptyState";
import { ErrorState } from "@/components/ErrorState";
import { FopLifecycleMark } from "@/components/brand/FopLifecycleMark";
import { LoadingState } from "@/components/LoadingState";
import { StatusBadge } from "@/components/StatusBadge";
import { BuildingDocumentsPanel } from "@/components/buildings/BuildingDocumentsPanel";
import {
  type Asset,
  type BuildingLibrary,
  type DocumentRecord,
  type ProtectedStateEvaluation,
  archiveDocument,
  getBuildingLibrary,
  getProtectedState,
  listBuildingAssets,
  updateDocument,
  uploadDocument,
  uploadDocumentVersion
} from "@/lib/fms-api";
import { visualStateFromLibrary, visualStateWithProtectedState } from "@/lib/fop-lifecycle-visual";

type BuildingLibraryClientProps = {
  buildingId: string;
};

const workflowSteps = [
  "Select or upload files",
  "Review document classification",
  "Assign property, building, or shared infrastructure",
  "Review Passport Record and Client Visible settings",
  "Review AI metadata and asset suggestions",
  "Approve evidence",
  "Recalculate closeout and Passport completion",
  "Show remaining missing items"
];

function formatDate(value?: string | null) {
  if (!value) {
    return "-";
  }
  return new Intl.DateTimeFormat("en-CA", { month: "short", day: "numeric", year: "numeric" }).format(new Date(value));
}

export function BuildingLibraryClient({ buildingId }: BuildingLibraryClientProps) {
  const searchParams = useSearchParams();
  const [library, setLibrary] = useState<BuildingLibrary | null>(null);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [presetCategory, setPresetCategory] = useState<string | null>(searchParams.get("category"));
  const [isWorkflowOpen, setIsWorkflowOpen] = useState(searchParams.get("workflow") === "build-passport");
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [protectedState, setProtectedState] = useState<ProtectedStateEvaluation | null>(null);

  const loadLibrary = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [loadedLibrary, loadedAssets] = await Promise.all([
        getBuildingLibrary(buildingId),
        listBuildingAssets(buildingId)
      ]);
      setLibrary(loadedLibrary);
      setAssets(loadedAssets);
      setProtectedState(await getProtectedState(buildingId).catch(() => null));
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "Unable to load Building Library.");
    } finally {
      setIsLoading(false);
    }
  }, [buildingId]);

  useEffect(() => {
    void loadLibrary();
  }, [loadLibrary]);

  useEffect(() => {
    const category = searchParams.get("category");
    if (category) {
      setPresetCategory(category);
    }
    if (searchParams.get("workflow") === "build-passport") {
      setIsWorkflowOpen(true);
    }
  }, [searchParams]);

  async function handleUploadDocument(formData: FormData) {
    setIsSubmitting(true);
    setError(null);
    try {
      await uploadDocument(formData);
      await loadLibrary();
    } catch (documentError) {
      setError(documentError instanceof Error ? documentError.message : "Unable to add evidence.");
      throw documentError;
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleUploadDocumentVersion(documentId: string, formData: FormData) {
    setIsSubmitting(true);
    setError(null);
    try {
      await uploadDocumentVersion(documentId, formData);
      await loadLibrary();
    } catch (documentError) {
      setError(documentError instanceof Error ? documentError.message : "Unable to supersede evidence.");
      throw documentError;
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleUpdateDocument(documentId: string, payload: Parameters<typeof updateDocument>[1]): Promise<DocumentRecord> {
    setIsSubmitting(true);
    setError(null);
    try {
      const document = await updateDocument(documentId, payload);
      await loadLibrary();
      return document;
    } catch (documentError) {
      setError(documentError instanceof Error ? documentError.message : "Unable to update evidence.");
      throw documentError;
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleArchiveDocument(documentId: string) {
    setIsSubmitting(true);
    setError(null);
    try {
      await archiveDocument(documentId);
      await loadLibrary();
    } catch (documentError) {
      setError(documentError instanceof Error ? documentError.message : "Unable to archive evidence.");
      throw documentError;
    } finally {
      setIsSubmitting(false);
    }
  }

  if (isLoading) {
    return <LoadingState label="Loading Building Library" />;
  }

  if (error && !library) {
    return <ErrorState message={error} onRetry={() => void loadLibrary()} />;
  }

  if (!library) {
    return <EmptyState title="Building Library unavailable." message="The requested building library could not be loaded." />;
  }

  const building = library.building;
  const lifecycleVisual = visualStateWithProtectedState(visualStateFromLibrary(library), protectedState);

  return (
    <div className="space-y-6">
      <section className="fop-card p-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="flex flex-wrap gap-3 text-xs font-semibold uppercase tracking-[0.18em] text-[#64748B]">
              <span>Job No. {building.code || "-"}</span>
              <span>BPID / Passport No. {building.bpid}</span>
              <span>{library.lifecycle_stage}</span>
            </div>
            <h2 className="mt-2 text-2xl font-semibold tracking-normal text-[#0F172A]">{building.name}</h2>
            <p className="mt-1 text-sm text-[#64748B]">{library.property?.name || "Property not assigned"}</p>
          </div>
          <FopLifecycleMark {...lifecycleVisual} showLabels className="h-24 w-24" />
          <div className="flex flex-wrap gap-2">
            <Link href={`/buildings/${building.id}/closeout`} className="fop-button-secondary">
              <BookOpen size={16} />
              Open Closeout
            </Link>
            <Link href={`/buildings/${building.id}/passport`} className="fop-button-secondary">
              <ShieldCheck size={16} />
              Open Passport
            </Link>
            <button type="button" onClick={() => setIsWorkflowOpen(true)} className="fop-button-primary">
              <Sparkles size={16} />
              Build Passport
            </button>
            <button type="button" onClick={() => setPresetCategory("Building Protection Passport")} className="fop-button-primary">
              <FilePlus2 size={16} />
              Add Evidence
            </button>
            <button type="button" onClick={() => void loadLibrary()} className="fop-button-secondary h-10 w-10 px-0" aria-label="Refresh library" title="Refresh library">
              <RefreshCcw size={16} />
            </button>
          </div>
        </div>

        <div className="mt-5 grid gap-3 md:grid-cols-5">
          <div className="rounded-md border border-[#E2E8F0] bg-[#F8FAFC] p-4">
            <p className="text-xs font-semibold uppercase text-[#64748B]">Passport Completion</p>
            <p className="mt-1 text-2xl font-semibold text-[color:var(--fop-protect-text)]">{library.passport_completion_percentage}%</p>
          </div>
          <div className="rounded-md border border-[#E2E8F0] bg-[#F8FAFC] p-4">
            <p className="text-xs font-semibold uppercase text-[#64748B]">Closeout Readiness</p>
            <div className="mt-2"><StatusBadge status={library.closeout_readiness_state} /></div>
          </div>
          <div className="rounded-md border border-[#E2E8F0] bg-[#F8FAFC] p-4">
            <p className="text-xs font-semibold uppercase text-[#64748B]">Evidence Items</p>
            <p className="mt-1 text-2xl font-semibold text-[#0F172A]">{library.total_evidence_items}</p>
          </div>
          <div className="rounded-md border border-[#E2E8F0] bg-[#F8FAFC] p-4">
            <p className="text-xs font-semibold uppercase text-[#64748B]">Missing Items</p>
            <p className="mt-1 text-2xl font-semibold text-[#0F172A]">{library.missing_evidence_count}</p>
          </div>
          <div className="rounded-md border border-[#E2E8F0] bg-[#F8FAFC] p-4">
            <p className="text-xs font-semibold uppercase text-[#64748B]">Last Updated</p>
            <p className="mt-1 text-sm font-semibold text-[#0F172A]">{formatDate(library.last_updated)}</p>
          </div>
        </div>
        <div className="mt-4 flex flex-wrap items-center gap-2">
          <StatusBadge status={protectedState?.protected_state_status ?? "Protected State Unavailable"} />
          <StatusBadge status={protectedState?.halo_eligible ? "Halo Eligible" : "No Halo"} />
        </div>
      </section>

      {error ? <ErrorState message={error} onRetry={() => void loadLibrary()} /> : null}

      <section className="space-y-3">
        <div className="flex flex-wrap items-end justify-between gap-3">
          <div>
            <p className="fop-label">Evidence Categories</p>
            <h3 className="mt-2 text-xl font-semibold text-[#0F172A]">Passport evidence coverage</h3>
          </div>
          <button type="button" onClick={() => setIsWorkflowOpen(true)} className="fop-button-primary">
            <ShieldCheck size={16} />
            Build Passport
          </button>
        </div>
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {library.categories.map((category) => (
            <article key={category.category} className="rounded-md border border-[#E2E8F0] bg-white p-4">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h4 className="font-semibold text-[#0F172A]">{category.category}</h4>
                  <p className="mt-1 text-xs text-[#64748B]">
                    {category.item_count} item{category.item_count === 1 ? "" : "s"} • {category.latest_revision ? `Rev ${category.latest_revision}` : "No revision"} • {formatDate(category.latest_date)}
                  </p>
                </div>
                <StatusBadge status={category.status} />
              </div>
              <div className="mt-4 flex flex-wrap gap-2">
                <button type="button" onClick={() => setPresetCategory(category.category)} className="fop-button-secondary min-h-9 px-3 text-xs">
                  <FilePlus2 size={14} />
                  Add Evidence
                </button>
                <button type="button" onClick={() => setPresetCategory(category.category)} className="fop-button-secondary min-h-9 px-3 text-xs">
                  View Evidence
                </button>
              </div>
            </article>
          ))}
        </div>
      </section>

      <BuildingDocumentsPanel
        buildingId={building.id}
        assets={assets}
        documents={library.documents}
        isSubmitting={isSubmitting}
        presetEvidenceCategory={presetCategory}
        libraryMode
        onUpload={handleUploadDocument}
        onUploadVersion={handleUploadDocumentVersion}
        onUpdate={handleUpdateDocument}
        onArchive={handleArchiveDocument}
        onAssetsChanged={loadLibrary}
      />

      {isWorkflowOpen ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#0F172A]/55 px-4 py-6 backdrop-blur-sm">
          <div className="w-full max-w-3xl rounded-md border border-[#E2E8F0] bg-white p-6 shadow-[0_24px_64px_rgba(15,23,42,0.18)]">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <p className="fop-label">Build Passport</p>
                <h3 className="mt-2 text-xl font-semibold text-[#0F172A]">Guided evidence workflow</h3>
                <p className="mt-2 text-sm leading-6 text-[#64748B]">
                  This MVP guides evidence readiness and review. Final Passport PDF generation is intentionally outside this phase.
                </p>
              </div>
              <FopLifecycleMark {...lifecycleVisual} compact className="h-16 w-16" />
              <button type="button" onClick={() => setIsWorkflowOpen(false)} className="fop-button-secondary">
                Close
              </button>
            </div>
            <ol className="mt-5 space-y-3">
              {workflowSteps.map((step, index) => (
                <li key={step} className="flex items-center gap-3 rounded-md border border-[#E2E8F0] bg-[#F8FAFC] p-3">
                  <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-[#D95A4E] text-xs font-semibold text-white">{index + 1}</span>
                  <span className="text-sm font-medium text-[#334155]">{step}</span>
                </li>
              ))}
            </ol>
            <div className="mt-5 flex flex-wrap justify-end gap-3">
              <button type="button" onClick={() => setPresetCategory("Building Protection Passport")} className="fop-button-secondary">
                <FilePlus2 size={16} />
                Add Passport Evidence
              </button>
              <Link href={`/buildings/${building.id}/closeout`} className="fop-button-primary">
                Review Remaining Items
              </Link>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
