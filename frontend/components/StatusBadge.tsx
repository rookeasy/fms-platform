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
    normalized.includes("operational") ||
    normalized.includes("active")
      ? "bg-[#FFF1EE] text-[#9F342A] ring-[#F1C8C2]"
      : normalized.includes("ready") || normalized.includes("complete")
        ? "bg-emerald-50 text-emerald-700 ring-emerald-200"
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
