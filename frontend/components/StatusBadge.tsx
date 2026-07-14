import { cn } from "@/lib/utils";

type StatusBadgeProps = {
  status: string;
};

export function StatusBadge({ status }: StatusBadgeProps) {
  const normalized = status.toLowerCase();
  const tone =
    normalized.includes("protect") ||
    normalized.includes("protected") ||
    normalized.includes("current") ||
    normalized.includes("operational")
      ? "bg-[color:var(--fop-protect-soft)] text-[color:var(--fop-protect-text)] ring-emerald-200"
      : normalized.includes("advise") || normalized.includes("review") || normalized.includes("advisory")
        ? "bg-[color:var(--fop-advise-soft)] text-[#334155] ring-[#DDE2EA]"
      : normalized.includes("build") || normalized.includes("active") || normalized.includes("draft") || normalized.includes("in progress")
        ? "bg-[#F8FAFC] text-[color:var(--fop-build-text)] ring-[#CBD5E1]"
      : normalized.includes("ready") || normalized.includes("complete")
        ? "bg-[color:var(--fop-protect-soft)] text-[color:var(--fop-protect-text)] ring-emerald-200"
      : normalized.includes("risk") ||
          normalized.includes("high") ||
          normalized.includes("expired") ||
          normalized.includes("critical") ||
          normalized.includes("missing")
        ? "bg-red-50 text-red-700 ring-red-200"
        : "bg-amber-50 text-amber-700 ring-amber-200";

  return (
    <span
      className={cn(
        "inline-flex min-h-7 items-center rounded-full px-3 text-xs font-semibold tracking-normal ring-1",
        tone
      )}
    >
      {status}
    </span>
  );
}
