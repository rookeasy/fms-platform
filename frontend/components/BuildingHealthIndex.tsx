import { ProgressIndex } from "@/components/ProgressIndex";
import { ScoreCard } from "@/components/ScoreCard";
import { fppKpiTerms, type BuildingHealthScores } from "@/lib/progress-index";

type BuildingHealthIndexProps = {
  scores: BuildingHealthScores;
  missionBriefing?: string;
};

export function BuildingHealthIndex({ scores, missionBriefing }: BuildingHealthIndexProps) {
  const scoreCards = [
    { title: fppKpiTerms.protectionScore, score: scores.protectionScore, detail: "Lifecycle protection readiness." },
    { title: fppKpiTerms.complianceScore, score: scores.complianceScore, detail: "Evidence, inspection, and code posture." },
    { title: fppKpiTerms.readinessScore, score: scores.readinessScore, detail: "Handover and operating readiness." },
    { title: fppKpiTerms.intelligenceScore, score: scores.intelligenceScore, detail: "Data completeness and advisory signal." }
  ];

  return (
    <section className="fop-card p-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="fop-label">{fppKpiTerms.progressIndex}</p>
          <h3 className="mt-2 text-xl font-semibold tracking-normal text-[#0F172A]">{fppKpiTerms.buildingHealthIndex}</h3>
          <p className="mt-1 max-w-2xl text-sm leading-6 text-[#64748B]">
            A unified BUILD • ADVISE • PROTECT view of building readiness, compliance, and operational resilience.
          </p>
        </div>
        <div className="text-right">
          <p className="text-4xl font-semibold text-[#0F172A]">{scores.buildingHealthIndex}%</p>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#64748B]">Overall</p>
        </div>
      </div>
      <div className="mt-6">
        <ProgressIndex score={scores.buildingHealthIndex} size="lg" showDescriptions variant="dashboard" />
      </div>
      <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {scoreCards.map((card) => (
          <ScoreCard key={card.title} title={card.title} score={card.score} detail={card.detail} />
        ))}
      </div>
      {missionBriefing ? (
        <div className="mt-5 rounded-xl border border-[#E2E8F0] bg-[#F8FAFC] p-4">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[color:var(--fop-advise-text)]">Mission Briefing</p>
          <p className="mt-2 text-sm leading-6 text-[#334155]">{missionBriefing}</p>
        </div>
      ) : null}
    </section>
  );
}
