import type { Building, LifecycleStage } from "@/lib/mock-data";
import type { Building as ApiBuilding } from "@/lib/fms-api";

export const lifecycleLabels: Record<LifecycleStage, string> = {
  build: "BUILD",
  advise: "ADVISE",
  protect: "PROTECT"
};

export const lifecycleDescriptions: Record<LifecycleStage, string> = {
  build: "Design, estimating, engineering, construction, closeout, and occupancy readiness.",
  advise: "Document intelligence, AI review, compliance guidance, risk recommendations, and decision support.",
  protect: "Occupied record, inspections, service, deficiency management, renewals, and lifecycle management."
};

export function getLifecycleStageFromStatus(status?: string | null): LifecycleStage {
  if (status === "completed_occupied") {
    return "protect";
  }
  return "build";
}

export function getLifecycleScore(stage: LifecycleStage) {
  if (stage === "build") {
    return 28;
  }
  if (stage === "advise") {
    return 58;
  }
  return 92;
}

export function getApiBuildingLifecycle(building: ApiBuilding): LifecycleStage {
  return getLifecycleStageFromStatus(building.status);
}

export function getMockBuildingLifecycle(building: Building): LifecycleStage {
  return building.lifecycleStage;
}

export function getOccupancyStatus(status?: string | null) {
  return status === "completed_occupied" ? "Occupied" : "Pre-occupancy";
}
