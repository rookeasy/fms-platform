import { ProgressIndex } from "@/components/ProgressIndex";

type ScoreCardProps = {
  title: string;
  score: number;
  detail?: string;
  variant?: "default" | "dashboard";
};

export function ScoreCard({ title, score, detail, variant = "default" }: ScoreCardProps) {
  return (
    <section className="fop-card p-5">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-semibold text-[#0F172A]">{title}</p>
          {detail ? <p className="mt-1 text-xs leading-5 text-[#64748B]">{detail}</p> : null}
        </div>
        <span className="text-2xl font-semibold text-[#0F172A]">{score}%</span>
      </div>
      <div className="mt-4">
        <ProgressIndex score={score} size={variant === "dashboard" ? "md" : "sm"} variant="compact" showScore={false} />
      </div>
    </section>
  );
}
