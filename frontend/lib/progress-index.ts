export type FppScoreSet = {
  protectionScore: number;
  complianceScore: number;
  readinessScore: number;
  intelligenceScore: number;
};

export type BuildingHealthScores = FppScoreSet & {
  buildingHealthIndex: number;
};

export const fppKpiTerms = {
  protectionScore: "Protection Score™",
  complianceScore: "Compliance Score™",
  readinessScore: "Readiness Score™",
  intelligenceScore: "Intelligence Score™",
  buildingHealthIndex: "Building Health Index™",
  progressIndex: "FPP Progress Index™"
} as const;

export const lifecycleStages = [
  { key: "build", label: "BUILD", description: "Create systems.", color: "#0F172A" },
  { key: "advise", label: "ADVISE", description: "Deliver intelligence.", color: "#2563EB" },
  { key: "protect", label: "PROTECT", description: "Sustain operations.", color: "#D95A4E" }
] as const;

export function clampScore(score: number) {
  if (!Number.isFinite(score)) {
    return 0;
  }
  return Math.max(0, Math.min(100, Math.round(score)));
}

export function calculateBuildingHealthIndex(scores: FppScoreSet) {
  return clampScore(
    (scores.protectionScore + scores.complianceScore + scores.readinessScore + scores.intelligenceScore) / 4
  );
}

export function getProgressStatus(score: number): "low" | "medium" | "high" | "complete" {
  const value = clampScore(score);
  if (value >= 98) {
    return "complete";
  }
  if (value >= 80) {
    return "high";
  }
  if (value >= 60) {
    return "medium";
  }
  return "low";
}

export function getMockBuildingScores(seed: string, overrides: Partial<FppScoreSet> = {}): BuildingHealthScores {
  const hash = Array.from(seed).reduce((total, character) => total + character.charCodeAt(0), 0);
  const scores: FppScoreSet = {
    protectionScore: clampScore(76 + (hash % 18)),
    complianceScore: clampScore(78 + (hash % 16)),
    readinessScore: clampScore(72 + (hash % 21)),
    intelligenceScore: clampScore(68 + (hash % 19)),
    ...overrides
  };

  return {
    ...scores,
    buildingHealthIndex: calculateBuildingHealthIndex(scores)
  };
}
