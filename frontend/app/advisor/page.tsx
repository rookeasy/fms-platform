import { AppShell } from "@/components/AppShell";
import { PassportSection } from "@/components/PassportSection";
import { ProgressIndex } from "@/components/ProgressIndex";
import { StatusBadge } from "@/components/StatusBadge";
import { fuzionBrand } from "@/lib/brand";
import { lifecycleSummary } from "@/lib/mock-data";
import { fppKpiTerms, getMockBuildingScores } from "@/lib/progress-index";
import { getPortfolioScores } from "@/lib/fms-api";

const recommendations = [
  "Review closeout packages with missing warranty, O&M, or ITM transition evidence.",
  "Prioritize properties with readiness below 80% before handover meetings.",
  "Convert completed handover buildings into service and inspection follow-up work."
];

export default async function MissionBriefingPage() {
  const fallbackScores = getMockBuildingScores("advisor-portfolio", {
    protectionScore: 83,
    complianceScore: 86,
    readinessScore: 79,
    intelligenceScore: 82
  });
  const scores = await getPortfolioScores().catch(() => ({
    ...fallbackScores,
    scoreDrivers: [
      "Annual sprinkler inspection expired.",
      "Fire pump report is missing.",
      "Two deficiencies remain unresolved.",
      "Updated drawings have not been uploaded."
    ]
  }));
  const missionBriefing = [
    `${lifecycleSummary.build} buildings are entering BUILD or active delivery.`,
    `${lifecycleSummary.advise} buildings are advancing through ADVISE review.`,
    `${lifecycleSummary.protect} buildings have reached PROTECT as operating records.`,
    `Portfolio Health is ${scores.buildingHealthIndex}% across the current building registry.`,
    `Highest-priority buildings: ${lifecycleSummary.lowestProtectionScores.map((building) => building.projectName).slice(0, 3).join(", ")}.`
  ];
  const scoreMovementExplanation = scores.scoreDrivers.join(" ");

  return (
    <AppShell title="Mission Briefing">
      <div className="space-y-6">
        <section className="fop-card p-6">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <p className="fop-label">Mission Briefing</p>
              <h2 className="mt-2 text-2xl font-semibold tracking-normal text-white">How are we advancing buildings toward PROTECT?</h2>
              <p className="mt-2 max-w-3xl text-sm leading-6 text-[#B6C1CF]">
                Mission Briefing is the executive intelligence layer for BUILD, ADVISE, and PROTECT movement across {fuzionBrand.shortName}.
              </p>
            </div>
            <StatusBadge status="Mission Briefing" />
          </div>
        </section>

        <section className="fop-card p-6">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <p className="fop-label">Portfolio Health Movement</p>
              <h2 className="mt-2 text-xl font-semibold text-white">{fppKpiTerms.protectionScore} Movement</h2>
              <p className="mt-2 max-w-3xl text-sm leading-6 text-[#B6C1CF]">
                {scoreMovementExplanation}
              </p>
            </div>
            <span className="text-3xl font-semibold text-white">{scores.protectionScore}%</span>
          </div>
          <div className="mt-5">
            <ProgressIndex score={scores.protectionScore} size="lg" showDescriptions variant="dashboard" />
          </div>
        </section>

        <div className="grid gap-6 lg:grid-cols-[1fr_360px]">
          <PassportSection title="Mission Briefing">
            <div className="space-y-3">
              {missionBriefing.map((item) => (
                <div key={item} className="rounded-xl border border-white/10 bg-white/[0.035] p-4 text-sm text-[#B6C1CF]">
                  {item}
                </div>
              ))}
            </div>
          </PassportSection>

          <PassportSection title="Highest Priority Buildings">
            <div className="space-y-3">
              {lifecycleSummary.lowestProtectionScores.slice(0, 4).map((building) => (
                <div key={building.id} className="rounded-xl border border-white/10 bg-white/[0.035] p-4">
                  <p className="text-sm font-semibold text-white">{building.projectName}</p>
                  <p className="mt-1 text-xs text-[#B6C1CF]">
                    {building.passportNo} · {building.healthScore}% · {building.lifecycleStage.toUpperCase()}
                  </p>
                </div>
              ))}
            </div>
          </PassportSection>
        </div>

        <PassportSection title="Recommended Focus">
          <div className="grid gap-3 md:grid-cols-3">
            {recommendations.map((recommendation) => (
              <div key={recommendation} className="rounded-xl border border-white/10 bg-white/[0.035] p-4 text-sm text-[#B6C1CF]">
                {recommendation}
              </div>
            ))}
          </div>
        </PassportSection>
      </div>
    </AppShell>
  );
}
