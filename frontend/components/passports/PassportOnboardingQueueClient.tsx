"use client";

import Link from "next/link";
import { ArrowUpRight, ClipboardCheck, FileSearch } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";

import { DataTable } from "@/components/DataTable";
import { EmptyState } from "@/components/EmptyState";
import { ErrorState } from "@/components/ErrorState";
import { FopLifecycleMark } from "@/components/brand/FopLifecycleMark";
import { LoadingState } from "@/components/LoadingState";
import { StatusBadge } from "@/components/StatusBadge";
import { listPassportOnboardingQueue, type PassportOnboardingQueueItem } from "@/lib/fms-api";
import { visualStateFromPassportQueueItem } from "@/lib/fop-lifecycle-visual";

function scoreTone(score: number) {
  if (score >= 85) {
    return "bg-emerald-50 text-emerald-700 ring-emerald-200";
  }
  if (score >= 55) {
    return "bg-amber-50 text-amber-800 ring-amber-200";
  }
  return "bg-red-50 text-red-700 ring-red-200";
}

function MissingItems({ items }: { items: string[] }) {
  if (!items.length) {
    return <span className="text-sm font-medium text-emerald-700">None</span>;
  }
  const visible = items.slice(0, 2);
  const extra = items.length - visible.length;
  return (
    <div className="max-w-72 text-sm text-[#475569]">
      {visible.join(", ")}
      {extra > 0 ? ` +${extra} more` : ""}
    </div>
  );
}

export function PassportOnboardingQueueClient() {
  const [rows, setRows] = useState<PassportOnboardingQueueItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadQueue = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      setRows(await listPassportOnboardingQueue());
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "Unable to load Passport onboarding queue.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadQueue();
  }, [loadQueue]);

  const summary = useMemo(() => {
    const completed = rows.filter((row) => row.project_classification === "completed").length;
    const eligible = rows.filter((row) => row.passport_eligible).length;
    const ready = rows.filter((row) => row.passport_status === "Ready for Passport").length;
    const protectedApproved = rows.filter((row) => row.protected_state_status === "approved" && row.halo_eligible).length;
    const averageScore = rows.length ? Math.round(rows.reduce((total, row) => total + row.closeout_score, 0) / rows.length) : 0;
    return { completed, eligible, ready, protectedApproved, averageScore };
  }, [rows]);

  if (isLoading) {
    return <LoadingState label="Loading Passport onboarding queue" />;
  }

  if (error) {
    return <ErrorState message={error} onRetry={() => void loadQueue()} />;
  }

  if (!rows.length) {
    return <EmptyState title="No onboarding records yet." message="Run the completed Fuzion project onboarding script to populate the queue." />;
  }

  return (
    <div className="space-y-6">
      <section className="grid gap-4 md:grid-cols-5">
        {[
          ["Completed Prime Contracts", summary.completed],
          ["Passport Eligible", summary.eligible],
          ["Ready for Passport", summary.ready],
          ["Protected Approved", summary.protectedApproved],
          ["Average Closeout", `${summary.averageScore}%`]
        ].map(([label, value]) => (
          <div key={label} className="fop-card p-5">
            <p className="text-sm font-semibold text-[#64748B]">{label}</p>
            <p className="mt-2 text-3xl font-semibold text-[#0F172A]">{value}</p>
          </div>
        ))}
      </section>

      <DataTable
        rows={rows}
        columns={[
          {
            key: "project",
            header: "Project",
            render: (row) => (
              <div className="flex min-w-56 items-center gap-3">
                <FopLifecycleMark {...visualStateFromPassportQueueItem(row)} compact className="h-10 w-10" />
                <div>
                  <Link href={`/buildings/${row.building_id}`} className="font-semibold text-[#0F172A] underline decoration-[#CBD5E1] underline-offset-4 hover:decoration-[#D95A4E]">
                    {row.project}
                  </Link>
                  <div className="mt-1 text-xs text-[#64748B]">Job No. {row.job_no || "-"}</div>
                </div>
              </div>
            )
          },
          { key: "property", header: "Property", render: (row) => row.property || "Unassigned" },
          { key: "building", header: "Building", render: (row) => row.building },
          { key: "completion_status", header: "Completion", render: (row) => <StatusBadge status={row.completion_status} /> },
          {
            key: "closeout_score",
            header: "Closeout",
            render: (row) => (
              <span className={`inline-flex min-h-7 items-center rounded-full px-3 text-xs font-semibold ring-1 ${scoreTone(row.closeout_score)}`}>
                {row.closeout_score}%
              </span>
            )
          },
          { key: "missing_items", header: "Missing Items", render: (row) => <MissingItems items={row.missing_items} /> },
          { key: "passport_status", header: "Passport Status", render: (row) => <StatusBadge status={row.passport_status} /> },
          { key: "protected_state_status", header: "Protected State", render: (row) => <StatusBadge status={row.protected_state_status} /> },
          { key: "next_action", header: "Next Action", render: (row) => row.next_action },
          {
            key: "actions",
            header: "Open",
            render: (row) => (
              <div className="flex items-center gap-2">
                <Link href={row.closeout_url} className="fop-button-secondary min-h-9 px-3" title="Open closeout">
                  <ClipboardCheck size={16} />
                </Link>
                <Link href={row.passport_url} className="fop-button-secondary min-h-9 px-3" title="Open Passport">
                  <FileSearch size={16} />
                </Link>
                <Link href={`/buildings/${row.building_id}`} className="fop-button-secondary min-h-9 px-3" title="Open building">
                  <ArrowUpRight size={16} />
                </Link>
              </div>
            )
          }
        ]}
      />
    </div>
  );
}
