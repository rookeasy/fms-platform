"use client";

import Link from "next/link";
import { BookOpen, FilePlus2, RefreshCcw, ShieldCheck } from "lucide-react";
import { useCallback, useEffect, useState } from "react";

import { DataTable, type DataTableColumn } from "@/components/DataTable";
import { EmptyState } from "@/components/EmptyState";
import { ErrorState } from "@/components/ErrorState";
import { FopLifecycleMark } from "@/components/brand/FopLifecycleMark";
import { LoadingState } from "@/components/LoadingState";
import { StatusBadge } from "@/components/StatusBadge";
import { formatControlledValue } from "@/lib/controlled-values";
import { type BuildingLibraryIndexItem, listBuildingLibraryIndex } from "@/lib/fms-api";
import { visualStateFromLibraryIndex } from "@/lib/fop-lifecycle-visual";

function formatDate(value?: string | null) {
  if (!value) {
    return "-";
  }
  return new Intl.DateTimeFormat("en-CA", { month: "short", day: "numeric", year: "numeric" }).format(new Date(value));
}

export function BuildingLibraryIndexClient() {
  const [items, setItems] = useState<BuildingLibraryIndexItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadLibrary = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      setItems(await listBuildingLibraryIndex());
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "Unable to load Building Library.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadLibrary();
  }, [loadLibrary]);

  const columns: Array<DataTableColumn<BuildingLibraryIndexItem>> = [
    {
      key: "building",
      header: "Building / Property",
      render: (item) => (
        <div className="flex items-center gap-3">
          <FopLifecycleMark {...visualStateFromLibraryIndex(item)} compact className="h-10 w-10" />
          <div>
            <Link href={item.library_url} className="font-semibold text-[#0F172A] underline decoration-[#CBD5E1] underline-offset-4 hover:decoration-[#D95A4E]">
              {item.building_name}
            </Link>
            <div className="mt-1 text-xs text-[#64748B]">{item.property_name || "Property not assigned"}</div>
          </div>
        </div>
      )
    },
    { key: "job", header: "Job No.", render: (item) => item.job_no || "-" },
    { key: "passport", header: "Passport No.", render: (item) => item.passport_no || "-" },
    { key: "evidence", header: "Evidence Items", render: (item) => item.total_evidence_items },
    {
      key: "completion",
      header: "Passport Completion",
      render: (item) => (
        <div className="min-w-32">
          <div className="flex items-center justify-between text-xs font-semibold text-[#475569]">
            <span>{item.passport_completion_percentage}%</span>
          </div>
          <div className="mt-2 h-2 rounded-full bg-[#E2E8F0]">
            <div className="h-2 rounded-full bg-[color:var(--fop-protect)]" style={{ width: `${item.passport_completion_percentage}%` }} />
          </div>
        </div>
      )
    },
    { key: "missing", header: "Missing Items", render: (item) => item.missing_evidence_count },
    { key: "updated", header: "Last Updated", render: (item) => formatDate(item.last_updated) },
    {
      key: "status",
      header: "Status",
      render: (item) => (
        <div className="flex flex-wrap gap-2">
          <StatusBadge status={item.closeout_readiness_state} />
          <StatusBadge status={item.lifecycle_stage} />
        </div>
      )
    },
    {
      key: "actions",
      header: "Actions",
      render: (item) => (
        <div className="flex flex-wrap gap-2">
          <Link href={item.library_url} className="fop-button-secondary min-h-9 px-3 text-xs">
            <BookOpen size={14} />
            View Library
          </Link>
          <Link href={`${item.library_url}?workflow=build-passport`} className="fop-button-primary min-h-9 px-3 text-xs">
            <ShieldCheck size={14} />
            Build Passport
          </Link>
        </div>
      )
    }
  ];

  if (isLoading) {
    return <LoadingState label="Loading Building Library" />;
  }

  if (error) {
    return <ErrorState message={error} onRetry={() => void loadLibrary()} />;
  }

  return (
    <div className="space-y-6">
      <section className="fop-card p-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="fop-label">Building Library</p>
            <h2 className="mt-2 text-2xl font-semibold tracking-normal text-[#0F172A]">Evidence that builds the Passport</h2>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-[#64748B]">
              Review building evidence, closeout readiness, and Passport completion without losing the existing /documents route.
            </p>
          </div>
          <button type="button" onClick={() => void loadLibrary()} className="fop-button-secondary">
            <RefreshCcw size={16} />
            Refresh
          </button>
        </div>
        <div className="mt-5 grid gap-3 md:grid-cols-4">
          <div className="rounded-md border border-[#E2E8F0] bg-[#F8FAFC] p-4">
            <p className="text-xs font-semibold uppercase text-[#64748B]">Buildings</p>
            <p className="mt-1 text-2xl font-semibold text-[#0F172A]">{items.length}</p>
          </div>
          <div className="rounded-md border border-[#E2E8F0] bg-[#F8FAFC] p-4">
            <p className="text-xs font-semibold uppercase text-[#64748B]">Evidence Items</p>
            <p className="mt-1 text-2xl font-semibold text-[#0F172A]">{items.reduce((total, item) => total + item.total_evidence_items, 0)}</p>
          </div>
          <div className="rounded-md border border-[#E2E8F0] bg-[#F8FAFC] p-4">
            <p className="text-xs font-semibold uppercase text-[#64748B]">Ready</p>
            <p className="mt-1 text-2xl font-semibold text-[color:var(--fop-protect-text)]">{items.filter((item) => item.closeout_readiness_state === "Ready for Passport").length}</p>
          </div>
          <div className="rounded-md border border-[#E2E8F0] bg-[#F8FAFC] p-4">
            <p className="text-xs font-semibold uppercase text-[#64748B]">Lifecycle</p>
            <p className="mt-1 text-sm font-semibold text-[#0F172A]">BUILD • ADVISE • PROTECT</p>
          </div>
        </div>
      </section>

      {items.length ? (
        <DataTable rows={items} columns={columns} />
      ) : (
        <EmptyState
          title="No building evidence is available yet."
          message="Add a building first, then add evidence to strengthen its Building Protection Passport."
          action={
            <Link href="/buildings" className="fop-button-primary">
              <FilePlus2 size={16} />
              Open Buildings
            </Link>
          }
        />
      )}
    </div>
  );
}
