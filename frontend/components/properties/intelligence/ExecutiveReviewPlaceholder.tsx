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
    <div className="fop-card p-5">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h4 className="font-semibold tracking-normal text-white">{title}</h4>
          <p className="mt-1 text-sm text-[#B6C1CF]">{message}</p>
        </div>
        <StatusBadge status={formatControlledValue(status)} />
      </div>
      <p className="mt-4 text-xs font-medium uppercase text-[#7D8CA3]">Calculated {new Date(calculatedAt).toLocaleString()}</p>
    </div>
  );
}

