import { cn } from "@/lib/utils";

type StatusBadgeProps = {
  status: string;
};

export function StatusBadge({ status }: StatusBadgeProps) {
  const normalized = status.toLowerCase();
  const tone =
    normalized.includes("ready") ||
    normalized.includes("complete") ||
    normalized.includes("current") ||
    normalized.includes("operational") ||
    normalized.includes("active")
      ? "bg-emerald-50 text-emerald-700 ring-emerald-200"
      : normalized.includes("risk") ||
          normalized.includes("high") ||
          normalized.includes("expired") ||
          normalized.includes("critical") ||
          normalized.includes("missing")
        ? "bg-red-500/12 text-red-200 ring-red-400/25"
        : "bg-amber-500/12 text-amber-200 ring-amber-400/25";

  const darkTone =
    normalized.includes("ready") ||
    normalized.includes("complete") ||
    normalized.includes("current") ||
    normalized.includes("operational") ||
    normalized.includes("active")
      ? "bg-emerald-500/12 text-emerald-200 ring-emerald-400/25"
      : tone;

  return (
    <span
      className={cn(
        "inline-flex min-h-7 items-center rounded-full px-3 text-xs font-semibold tracking-normal ring-1",
        darkTone
      )}
    >
      {status}
    </span>
  );
}
