import { StatusBadge } from "@/components/StatusBadge";
import { formatControlledValue } from "@/lib/controlled-values";

type ExecutiveReviewPlaceholderProps = {
  review: Record<string, unknown>;
  calculatedAt: string;
};

export function ExecutiveReviewPlaceholder({ review, calculatedAt }: ExecutiveReviewPlaceholderProps) {
  const status = typeof review.status === "string" ? review.status : "placeholder";
  const title = typeof review.title === "string" ? review.title : "Executive Review";
  const message = typeof review.message === "string" ? review.message : "Executive review generation is reserved for a future phase.";

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h4 className="font-semibold text-slate-950">{title}</h4>
          <p className="mt-1 text-sm text-slate-600">{message}</p>
        </div>
        <StatusBadge status={formatControlledValue(status)} />
      </div>
      <p className="mt-4 text-xs font-medium uppercase text-slate-500">Calculated {new Date(calculatedAt).toLocaleString()}</p>
    </div>
  );
}
