import Link from "next/link";

import { AppShell } from "@/components/AppShell";
import { DataTable } from "@/components/DataTable";
import { ProgressIndex } from "@/components/ProgressIndex";
import { ScoreCard } from "@/components/ScoreCard";
import { StatusBadge } from "@/components/StatusBadge";
import { Timeline } from "@/components/Timeline";
import { buildings, lifecycleSummary, portfolioTimeline } from "@/lib/mock-data";
import { getPortfolioScores } from "@/lib/fms-api";
import { getLifecycleScore, lifecycleLabels } from "@/lib/lifecycle";
import { fppKpiTerms, getMockBuildingScores } from "@/lib/progress-index";

const MISSION_TARGET = 1_000_000;

function formatNumber(value: number) {
  return new Intl.NumberFormat("en-US").format(value);
}

function formatMissionProgress(value: number) {
  return value < 0.01 ? value.toFixed(4) : value.toFixed(2);
}

export default async function MissionControlPage() {
  const fallbackScores = getMockBuildingScores("mission-control-portfolio", {
    protectionScore: 87,
    complianceScore: 94,
    readinessScore: 91,
    intelligenceScore: 78
  });
  const missionScores = await getPortfolioScores().catch(() => ({
    ...fallbackScores,
    scoreDrivers: ["Backend FPP portfolio scoring is unavailable, so Mission Control is showing a local fallback estimate."],
    lastCalculatedAt: new Date().toISOString(),
    buildingCount: 0,
    buildings: []
  }));

  const totalBuildings = Math.max(missionScores.buildingCount || 0, buildings.length);
  const buildingsProtected = lifecycleSummary.protect;
  const missionProgress = (buildingsProtected / MISSION_TARGET) * 100;
  const openDeficiencies = buildings.reduce((total, building) => total + building.openItems, 0);
  const buildingsAtRisk = buildings.filter((building) => building.healthScore < 70).length;
  const resolvedDeficiencies = Math.max(0, openDeficiencies - lifecycleSummary.overdueComplianceItems.length);
  const lifecycleStages = [
    {
      key: "build" as const,
      label: lifecycleLabels.build,
      description: "Create systems.",
      count: lifecycleSummary.build,
      color: "#F26B5E",
      score: getLifecycleScore("build")
    },
    {
      key: "advise" as const,
      label: lifecycleLabels.advise,
      description: "Deliver intelligence.",
      count: lifecycleSummary.advise,
      color: "#2DD4BF",
      score: getLifecycleScore("advise")
    },
    {
      key: "protect" as const,
      label: lifecycleLabels.protect,
      description: "Sustain operations.",
      count: lifecycleSummary.protect,
      color: "#60A5FA",
      score: getLifecycleScore("protect")
    }
  ];
  const missionBriefing = [
    `${lifecycleSummary.build} buildings are currently in BUILD.`,
    `${lifecycleSummary.advise} buildings are currently in ADVISE.`,
    `${buildingsProtected} buildings have reached PROTECT.`,
    `Portfolio Health is ${missionScores.buildingHealthIndex}%.`,
    `${resolvedDeficiencies} deficiencies are marked resolved or historical.`,
    `${buildingsAtRisk} buildings require immediate attention.`
  ];
  const missionEvents = [
    {
      title: "BUILD to ADVISE",
      date: "Current",
      description: lifecycleSummary.advise > 0 ? `${lifecycleSummary.advise} buildings are in ADVISE review.` : "ADVISE movement will populate once lifecycle events are persisted.",
      tone: "warning" as const
    },
    {
      title: "ADVISE to PROTECT",
      date: "Current",
      description: `${buildingsProtected} building records are operating in PROTECT.`,
      tone: "success" as const
    },
    ...portfolioTimeline
  ];

  return (
    <AppShell title="Mission Control">
      <div className="space-y-8">
        <section className="relative overflow-hidden rounded-2xl border border-white/10 bg-[#050A18] p-8 shadow-[0_24px_80px_rgba(0,0,0,0.32)]">
          <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.04)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.04)_1px,transparent_1px)] bg-[size:48px_48px] opacity-20" />
          <div className="relative grid gap-8 xl:grid-cols-[1fr_420px] xl:items-end">
            <div>
              <p className="fop-label">Mission</p>
              <h1 className="mt-4 max-w-4xl text-4xl font-semibold tracking-normal text-white md:text-5xl">{"Protect 1,000,000 Buildings\u2122"}</h1>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/[0.045] p-6 backdrop-blur">
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#7D8CA3]">{"Buildings Protected\u2122"}</p>
              <p className="mt-4 text-7xl font-semibold tracking-normal text-white">{formatNumber(buildingsProtected)}</p>
              <div className="mt-6 h-3 overflow-hidden rounded-full bg-white/[0.08]">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-[#F26B5E] via-[#2DD4BF] to-[#60A5FA]"
                  style={{ width: `${Math.max(0.5, Math.min(missionProgress, 100))}%` }}
                />
              </div>
              <div className="mt-4 flex items-center justify-between text-sm">
                <span className="text-[#B6C1CF]">
                  {formatNumber(buildingsProtected)} / {formatNumber(MISSION_TARGET)}
                </span>
                <span className="font-semibold text-[#FFB4AD]">{formatMissionProgress(missionProgress)}%</span>
              </div>
            </div>
          </div>
        </section>

        <section className="fop-card p-7">
          <p className="fop-label">Lifecycle Overview</p>
          <div className="mt-5 grid gap-5 md:grid-cols-3">
            {lifecycleStages.map((stage) => {
              const percent = totalBuildings > 0 ? Math.round((stage.count / totalBuildings) * 100) : 0;
              return (
                <div key={stage.key} className="rounded-xl border border-white/10 bg-white/[0.035] p-5">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <p className="text-xs font-semibold uppercase tracking-[0.2em]" style={{ color: stage.color }}>
                        {stage.label}
                      </p>
                      <p className="mt-2 text-sm text-[#7D8CA3]">{stage.description}</p>
                    </div>
                    <p className="text-4xl font-semibold text-white">{stage.count}</p>
                  </div>
                  <div className="mt-5">
                    <ProgressIndex score={stage.score} size="sm" variant="compact" showScore={false} />
                  </div>
                  <p className="mt-4 text-xs font-semibold uppercase tracking-[0.16em] text-[#7D8CA3]">{percent}% of records</p>
                </div>
              );
            })}
          </div>
        </section>

        <section className="grid gap-5 xl:grid-cols-[340px_1fr]">
          <div className="fop-card p-6">
            <p className="fop-label">Mission Health</p>
            <h2 className="mt-3 text-xl font-semibold tracking-normal text-white">Average Building Health</h2>
            <p className="mt-5 text-6xl font-semibold text-white">{missionScores.buildingHealthIndex}%</p>
          </div>
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <ScoreCard title={fppKpiTerms.protectionScore} score={missionScores.protectionScore} variant="dashboard" />
            <ScoreCard title={fppKpiTerms.complianceScore} score={missionScores.complianceScore} variant="dashboard" />
            <ScoreCard title="Readiness™" score={missionScores.readinessScore} variant="dashboard" />
            <ScoreCard title="Intelligence™" score={missionScores.intelligenceScore} variant="dashboard" />
          </div>
        </section>

        <section className="fop-card p-7">
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="fop-label">Mission Briefing</p>
              <h2 className="mt-2 text-2xl font-semibold tracking-normal text-white">Executive Summary</h2>
            </div>
            <StatusBadge status="Mission Briefing" />
          </div>
          <div className="mt-6 grid gap-3 md:grid-cols-2">
            {missionBriefing.map((item) => (
              <div key={item} className="rounded-xl border border-white/10 bg-white/[0.035] p-4 text-sm leading-6 text-[#D7DEE8]">
                {item}
              </div>
            ))}
          </div>
        </section>

        <section>
          <div className="mb-4">
            <h2 className="text-xl font-semibold tracking-normal text-white">Buildings Requiring Attention</h2>
            <p className="text-sm text-[#B6C1CF]">Lowest Protection Score records for immediate review.</p>
          </div>
          <DataTable
            rows={lifecycleSummary.lowestProtectionScores}
            columns={[
              { key: "building", header: "Building", render: (row) => <span className="font-semibold text-white">{row.projectName}</span> },
              { key: "passportNo", header: "Passport No.", render: (row) => row.passportNo },
              { key: "lifecycleStage", header: "Lifecycle Stage", render: (row) => <StatusBadge status={lifecycleLabels[row.lifecycleStage]} /> },
              { key: "protectionScore", header: "Protection Score", render: (row) => `${row.healthScore}%` },
              {
                key: "action",
                header: "Action",
                render: (row) => (
                  <Link className="font-semibold text-[#F26B5E] transition hover:text-white" href={`/buildings/${row.id}`}>
                    Open Passport
                  </Link>
                )
              }
            ]}
          />
        </section>

        <section className="fop-card p-6">
          <h2 className="text-xl font-semibold tracking-normal text-white">Mission Timeline</h2>
          <div className="mt-5">
            <Timeline items={missionEvents} />
          </div>
        </section>
      </div>
    </AppShell>
  );
}
