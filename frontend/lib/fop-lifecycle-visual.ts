import type { Building, BuildingLibrary, BuildingLibraryIndexItem, PassportOnboardingQueueItem, ProtectedStateEvaluation } from "@/lib/fms-api";
import type { LifecycleStage } from "@/lib/mock-data";

export type FopLifecycleVisualStatus = "build" | "advise" | "protect" | "protected";

export type FopLifecycleVisualState = {
  status: FopLifecycleVisualStatus;
  buildProgress: number;
  adviseProgress: number;
  protectProgress: number;
  overallProgress: number;
  halo: boolean;
  label: string;
};

const PROTECT_PASSPORT_STATUSES = new Set(["Ready for Passport", "Assets Verified"]);
const ADVISE_PASSPORT_STATUSES = new Set(["Documents Imported", "Closeout Incomplete", "Building Registered"]);

function clampProgress(value: number) {
  return Math.max(0, Math.min(100, Math.round(value)));
}

export function visualStateFromProgress(progress: number, protectedComplete = false): FopLifecycleVisualState {
  const overallProgress = clampProgress(progress);
  const buildProgress = clampProgress(Math.min(overallProgress, 33) / 33 * 100);
  const adviseProgress = clampProgress(Math.max(0, Math.min(overallProgress - 33, 33)) / 33 * 100);
  const protectProgress = clampProgress(Math.max(0, overallProgress - 66) / 34 * 100);
  const status: FopLifecycleVisualStatus =
    protectedComplete && overallProgress >= 100
      ? "protected"
      : overallProgress >= 67
        ? "protect"
        : overallProgress >= 34
          ? "advise"
          : "build";

  return {
    status,
    buildProgress,
    adviseProgress,
    protectProgress,
    overallProgress,
    halo: status === "protected",
    label: `Lifecycle status: ${status.toUpperCase()}`
  };
}

export function visualStateFromStatus(status?: string | null, progress = 0): FopLifecycleVisualState {
  const normalized = (status ?? "").trim();
  if (PROTECT_PASSPORT_STATUSES.has(normalized)) {
    return {
      status: "protect",
      buildProgress: 100,
      adviseProgress: 100,
      protectProgress: Math.max(68, clampProgress(progress)),
      overallProgress: Math.max(68, clampProgress(progress)),
      halo: false,
      label: "Lifecycle status: PROTECT"
    };
  }
  if (ADVISE_PASSPORT_STATUSES.has(normalized)) {
    return {
      status: "advise",
      buildProgress: 100,
      adviseProgress: Math.max(55, clampProgress(progress)),
      protectProgress: 0,
      overallProgress: Math.max(34, clampProgress(progress)),
      halo: false,
      label: "Lifecycle status: ADVISE"
    };
  }
  return visualStateFromProgress(progress);
}

export function visualStateWithProtectedState(
  base: FopLifecycleVisualState,
  protectedState?: ProtectedStateEvaluation | null
): FopLifecycleVisualState {
  if (protectedState?.protected_state_status === "approved" && protectedState.halo_eligible) {
    return {
      status: "protected",
      buildProgress: 100,
      adviseProgress: 100,
      protectProgress: 100,
      overallProgress: 100,
      halo: true,
      label: "Lifecycle status: PROTECTED"
    };
  }
  return { ...base, halo: false, status: base.status === "protected" ? "protect" : base.status };
}

export function visualStateFromLifecycleStage(stage: LifecycleStage): FopLifecycleVisualState {
  if (stage === "protect") {
    return visualStateFromProgress(88);
  }
  if (stage === "advise") {
    return visualStateFromProgress(56);
  }
  return visualStateFromProgress(28);
}

export function visualStateFromBuilding(building: Building, progress = 0): FopLifecycleVisualState {
  if (building.passport_status) {
    return visualStateFromStatus(building.passport_status, progress);
  }
  if (building.status === "completed_occupied") {
    return visualStateFromProgress(Math.max(progress, 82));
  }
  return visualStateFromProgress(progress || 28);
}

export function visualStateFromLibrary(library: BuildingLibrary): FopLifecycleVisualState {
  return visualStateFromStatus(library.building.passport_status, library.passport_completion_percentage);
}

export function visualStateFromLibraryIndex(item: BuildingLibraryIndexItem): FopLifecycleVisualState {
  return visualStateFromStatus(item.status, item.passport_completion_percentage);
}

export function visualStateFromPassportQueueItem(item: PassportOnboardingQueueItem): FopLifecycleVisualState {
  return visualStateWithProtectedState(visualStateFromStatus(item.passport_status, item.closeout_score), {
    building_id: item.building_id,
    protected_state_status: item.protected_state_status,
    halo_eligible: item.halo_eligible,
    criteria_total: 0,
    criteria_passed: 0,
    criteria_failed: 0,
    criteria_unknown: 0,
    criteria: [],
    blocking_items: [],
    warnings: [],
    evaluated_at: "",
    evaluation_version: ""
  });
}
