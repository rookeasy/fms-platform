"use client";

import { CheckCircle2, PauseCircle, RotateCw, ShieldCheck, XCircle } from "lucide-react";

import { EmptyState } from "@/components/EmptyState";
import { StatusBadge } from "@/components/StatusBadge";
import type { ProtectedStateEvaluation } from "@/lib/fms-api";

type ProtectedStatePanelProps = {
  state: ProtectedStateEvaluation | null;
  isSubmitting?: boolean;
  onEvaluate?: () => void;
  onApprove?: () => void;
  onSuspend?: () => void;
  onRevoke?: () => void;
};

export function ProtectedStatePanel({
  state,
  isSubmitting = false,
  onEvaluate,
  onApprove,
  onSuspend,
  onRevoke
}: ProtectedStatePanelProps) {
  if (!state) {
    return <EmptyState title="Protected State unavailable." message="The certification service did not return an authoritative result." />;
  }
  const canApprove = state.protected_state_status === "eligible" && state.criteria_failed === 0 && state.criteria_unknown === 0;
  const isApproved = state.protected_state_status === "approved" && state.halo_eligible;
  const blockingItems = state.blocking_items.slice(0, 5);

  return (
    <section className="fop-card p-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="fop-label">Protected State</p>
          <h3 className="mt-2 text-xl font-semibold text-white">Authoritative Halo Eligibility</h3>
          <p className="mt-2 text-sm leading-6 text-[#B6C1CF]">
            The Living F halo appears only after explicit Protected State approval.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <StatusBadge status={state.protected_state_status} />
          <StatusBadge status={isApproved ? "Halo Eligible" : "No Halo"} />
        </div>
      </div>

      <div className="mt-5 grid gap-3 md:grid-cols-4">
        {[
          ["Passed", state.criteria_passed],
          ["Failed", state.criteria_failed],
          ["Unknown", state.criteria_unknown],
          ["Total", state.criteria_total]
        ].map(([label, value]) => (
          <div key={label} className="rounded-md border border-white/10 bg-white/[0.035] p-4">
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[#7D8CA3]">{label}</p>
            <p className="mt-2 text-2xl font-semibold text-white">{value}</p>
          </div>
        ))}
      </div>

      <div className="mt-5 grid gap-3 md:grid-cols-2">
        {state.criteria.map((criterion) => (
          <div key={criterion.key} className="rounded-md border border-white/10 bg-white/[0.035] p-3">
            <div className="flex items-center justify-between gap-3">
              <p className="text-sm font-semibold text-white">{criterion.label}</p>
              <StatusBadge status={criterion.status} />
            </div>
            <p className="mt-1 text-xs leading-5 text-[#B6C1CF]">{criterion.message}</p>
          </div>
        ))}
      </div>

      {blockingItems.length ? (
        <div className="mt-5 rounded-md border border-[#FCA5A5]/40 bg-[#FEF2F2] p-4">
          <p className="text-sm font-semibold text-[#991B1B]">Blocking items</p>
          <ul className="mt-2 space-y-1 text-sm text-[#7F1D1D]">
            {blockingItems.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      ) : null}

      <div className="mt-5 flex flex-wrap gap-2">
        {onEvaluate ? (
          <button type="button" onClick={onEvaluate} disabled={isSubmitting} className="fop-button-secondary h-10">
            <RotateCw size={16} />
            Evaluate
          </button>
        ) : null}
        {onApprove ? (
          <button type="button" onClick={onApprove} disabled={isSubmitting || !canApprove} className="fop-button-primary h-10">
            <ShieldCheck size={16} />
            Approve Protected State
          </button>
        ) : null}
        {onSuspend ? (
          <button type="button" onClick={onSuspend} disabled={isSubmitting} className="fop-button-secondary h-10">
            <PauseCircle size={16} />
            Suspend
          </button>
        ) : null}
        {onRevoke ? (
          <button type="button" onClick={onRevoke} disabled={isSubmitting} className="fop-button-secondary h-10">
            <XCircle size={16} />
            Revoke
          </button>
        ) : null}
        {isApproved ? <CheckCircle2 className="mt-2 text-[color:var(--fop-protect)]" size={20} /> : null}
      </div>
    </section>
  );
}
