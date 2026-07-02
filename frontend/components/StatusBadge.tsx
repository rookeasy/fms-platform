import { cn } from "@/lib/utils";

type StatusBadgeProps = {
  status: string;
};

export function StatusBadge({ status }: StatusBadgeProps) {
  const tone =
    status === "Operational" || status === "Complete" || status === "Current" || status === "Ready for Handover"
      ? "bg-emerald-50 text-emerald-700 ring-emerald-200"
      : status === "At Risk" || status === "High" || status === "Expired"
        ? "bg-rose-50 text-rose-700 ring-rose-200"
        : "bg-amber-50 text-amber-700 ring-amber-200";

  return (
    <span
      className={cn(
        "inline-flex min-h-7 items-center rounded-full px-3 text-xs font-semibold ring-1",
        tone
      )}
    >
      {status}
    </span>
  );
}
