import Link from "next/link";

import { AppShell } from "@/components/AppShell";
import { FopLifecycleMark } from "@/components/brand/FopLifecycleMark";
import { DataTable } from "@/components/DataTable";
import { ProgressIndex } from "@/components/ProgressIndex";
import { ScoreCard } from "@/components/ScoreCard";
import { StatusBadge } from "@/components/StatusBadge";
import { Timeline } from "@/components/Timeline";
import { fuzionBrand } from "@/lib/brand";
import { fopLifecycleTokens } from "@/lib/design-tokens";
import { getPortfolioScores, listPassportOnboardingQueue } from "@/lib/fms-api";
import { visualStateFromLifecycleStage, visualStateFromProgress } from "@/lib/fop-lifecycle-visual";
import { getLifecycleScore, lifecycleLabels } from "@/lib/lifecycle";
import { buildings, lifecycleSummary, portfolioTimeline } from "@/lib/mock-data";
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
  const passportQueue = await listPassportOnboardingQueue().catch(() => []);

  const totalBuildings = Math.max(missionScores.buildingCount || 0, buildings.length);
  const buildingsProtected = passportQueue.filter((row) => row.protected_state_status === "approved" && row.halo_eligible).length;
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
      color: fopLifecycleTokens.build.value,
      score: getLifecycleScore("build")
    },
    {
      key: "advise" as const,
      label: lifecycleLabels.advise,
      description: "Deliver intelligence.",
      count: lifecycleSummary.advise,
      color: fopLifecycleTokens.advise.textValue,
      score: getLifecycleScore("advise")
    },
    {
      key: "protect" as const,
      label: lifecycleLabels.protect,
      description: "Sustain operations.",
      count: lifecycleSummary.protect,
      color: fopLifecycleTokens.protect.textValue,
      score: getLifecycleScore("protect")
    }
  ];
  const missionBriefing = [
    `${lifecycleSummary.build} buildings are currently in BUILD.`,
    `${lifecycleSummary.advise} buildings are currently in ADVISE.`,
    `${buildingsProtected} buildings have reached approved protected state.`,
    `Portfolio Health is ${missionScores.buildingHealthIndex}%.`,
    `${resolvedDeficiencies} deficiencies are marked resolved or historical.`,
    `${buildingsAtRisk} buildings require immediate attention.`
  ];
  const missionEvents = [
    {
      title: "BUILD • ADVISE",
      date: "Current",
      description: lifecycleSummary.advise > 0 ? `${lifecycleSummary.advise} buildings are in ADVISE review.` : "ADVISE movement will populate once lifecycle events are persisted.",
      tone: "warning" as const
    },
    {
      title: "ADVISE • PROTECT",
      date: "Current",
      description: `${buildingsProtected} building records have approved protected-state eligibility.`,
      tone: "success" as const
    },
    ...portfolioTimeline
  ];

  return (
    <AppShell title="Mission Control">
      <div className="space-y-6">
        <section className="rounded-xl border border-[color:var(--border)] bg-white p-6 shadow-sm">
          <div className="flex flex-wrap items-start justify-between gap-6">
            <div className="flex items-start gap-4">
              <FopLifecycleMark compact status="protect" className="h-16 w-14 shrink-0" title="FOP Living F mark" />
              <div>
                <p className="fop-label">{fuzionBrand.missionControlName}</p>
                <h1 className="mt-2 text-3xl font-semibold tracking-normal text-[color:var(--text-primary)]">Mission Control</h1>
                <p className="mt-2 max-w-2xl text-sm leading-6 text-[color:var(--text-secondary)]">
                  Portfolio intelligence for BUILD • ADVISE • PROTECT, focused on what has changed and what should happen next.
                </p>
              </div>
            </div>
            <div className="min-w-[220px] rounded-lg border border-[color:var(--border)] bg-[color:var(--surface-elevated)] p-4">
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[color:var(--text-muted)]">Buildings Under Protection™</p>
              <p className="mt-2 text-4xl font-semibold tracking-normal text-[color:var(--text-primary)]">{formatNumber(buildingsProtected)}</p>
              <div className="mt-4 h-2 overflow-hidden rounded-full bg-slate-200">
                <div
                  className="h-full rounded-full bg-[color:var(--fop-build)]"
                  style={{ width: `${Math.max(0.5, Math.min(missionProgress, 100))}%` }}
                />
              </div>
              <div className="mt-3 flex items-center justify-between text-xs">
                <span className="text-[color:var(--text-muted)]">
                  {formatNumber(buildingsProtected)} / {formatNumber(MISSION_TARGET)}
                </span>
                <span className="font-semibold text-[color:var(--fop-build-text)]">{formatMissionProgress(missionProgress)}%</span>
              </div>
            </div>
          </div>
        </section>

        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <ScoreCard title={fppKpiTerms.protectionScore} score={missionScores.protectionScore} variant="dashboard" />
          <ScoreCard title={fppKpiTerms.complianceScore} score={missionScores.complianceScore} variant="dashboard" />
          <ScoreCard title="Readiness™" score={missionScores.readinessScore} variant="dashboard" />
          <ScoreCard title="Intelligence™" score={missionScores.intelligenceScore} variant="dashboard" />
        </section>

        <section className="fop-card p-6">
          <p className="fop-label">Lifecycle Overview</p>
          <div className="mt-5 grid gap-4 md:grid-cols-3">
            {lifecycleStages.map((stage) => {
              const percent = totalBuildings > 0 ? Math.round((stage.count / totalBuildings) * 100) : 0;
              return (
                <div key={stage.key} className="rounded-lg border border-[color:var(--border)] bg-white p-5">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <p className="text-xs font-semibold uppercase tracking-[0.2em]" style={{ color: stage.color }}>
                        {stage.label}
                      </p>
                      <p className="mt-2 text-sm text-[color:var(--text-muted)]">{stage.description}</p>
                    </div>
                    <p className="text-4xl font-semibold text-[color:var(--text-primary)]">{stage.count}</p>
                  </div>
                  <div className="mt-5">
                    <ProgressIndex score={stage.score} size="sm" variant="compact" showScore={false} />
                  </div>
                  <p className="mt-4 text-xs font-semibold uppercase tracking-[0.16em] text-[color:var(--text-muted)]">{percent}% of records</p>
                </div>
              );
            })}
          </div>
        </section>

        <section className="grid gap-5 xl:grid-cols-[340px_1fr]">
          <div className="fop-card p-6">
            <p className="fop-label">Mission Health</p>
            <div className="mt-3 flex items-start justify-between gap-4">
              <div>
                <h2 className="text-xl font-semibold tracking-normal text-[color:var(--text-primary)]">Average Building Health</h2>
                <p className="mt-5 text-6xl font-semibold text-[color:var(--text-primary)]">{missionScores.buildingHealthIndex}%</p>
              </div>
              <FopLifecycleMark {...visualStateFromProgress(missionScores.buildingHealthIndex)} compact className="h-16 w-14" />
            </div>
          </div>
          <div className="fop-card p-6">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="fop-label">Mission Briefing</p>
                <h2 className="mt-2 text-2xl font-semibold tracking-normal text-[color:var(--text-primary)]">Executive Summary</h2>
              </div>
              <StatusBadge status="Mission Briefing" />
            </div>
            <div className="mt-5 grid gap-3 md:grid-cols-2">
              {missionBriefing.map((item) => (
                <div key={item} className="rounded-lg border border-[color:var(--border)] bg-[color:var(--surface-elevated)] p-4 text-sm leading-6 text-[color:var(--text-secondary)]">
                  {item}
                </div>
              ))}
            </div>
          </div>
        </section>

        <section>
          <div className="mb-4">
            <h2 className="text-xl font-semibold tracking-normal text-[color:var(--text-primary)]">Buildings Requiring Attention</h2>
            <p className="text-sm text-[color:var(--text-muted)]">Lowest Protection Score records for immediate review.</p>
          </div>
          <DataTable
            rows={lifecycleSummary.lowestProtectionScores}
            columns={[
              { key: "building", header: "Building", render: (row) => <span className="font-semibold text-[color:var(--text-primary)]">{row.projectName}</span> },
              { key: "passportNo", header: "Passport No.", render: (row) => row.passportNo },
              {
                key: "lifecycleStage",
                header: "Lifecycle Stage",
                render: (row) => {
                  const visual = visualStateFromLifecycleStage(row.lifecycleStage);
                  return (
                    <div className="flex items-center gap-2">
                      <FopLifecycleMark {...visual} compact className="h-9 w-8" />
                      <StatusBadge status={lifecycleLabels[row.lifecycleStage]} />
                    </div>
                  );
                }
              },
              { key: "protectionScore", header: "Protection Score", render: (row) => `${row.healthScore}%` },
              {
                key: "action",
                header: "Action",
                render: (row) => (
                  <Link className="font-semibold text-[color:var(--fop-build-text)] transition hover:text-[color:var(--text-primary)]" href={`/buildings/${row.id}`}>
                    Open Passport
                  </Link>
                )
              }
            ]}
          />
        </section>

        <section className="fop-card p-6">
          <h2 className="text-xl font-semibold tracking-normal text-[color:var(--text-primary)]">Mission Timeline</h2>
          <div className="mt-5">
            <Timeline items={missionEvents} />
          </div>
        </section>
      </div>
    </AppShell>
  );
}
