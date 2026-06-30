import { cn } from "@/lib/utils";

type HealthScoreBadgeProps = {
  score: number;
};

export function HealthScoreBadge({ score }: HealthScoreBadgeProps) {
  const tone =
    score >= 85
      ? "bg-emerald-600 text-white"
      : score >= 70
        ? "bg-amber-500 text-white"
        : "bg-rose-600 text-white";

  return (
    <span className={cn("inline-flex h-10 w-14 items-center justify-center rounded-md text-sm font-bold", tone)}>
      {score}
    </span>
  );
}
