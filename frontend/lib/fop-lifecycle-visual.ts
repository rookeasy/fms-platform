import type { Building, BuildingLibrary, BuildingLibraryIndexItem, PassportOnboardingQueueItem, ProtectedStateEvaluation } from "@/lib/fms-api";
import type { LifecycleStage } from "@/lib/mock-data";

export type FopLifecycleVisualStatus = "build" | "advise" | "protect" | "protected" | "neutral";

export type FopLifecycleVisualState = {
  status: FopLifecycleVisualStatus;
  overallProgress: number;
  saturation: number;
  color: string;
  textColor: string;
  halo: boolean;
  label: string;
  accessibleLabel: string;
};

const BUILD_STATUSES = new Set(["Building Registered", "Not Started"]);
const ADVISE_STATUSES = new Set(["Documents Imported", "Assets Verified", "Closeout Incomplete", "Ready for Passport"]);
const PROTECT_STATUSES = new Set(["Ready for Protected-State Review", "Passport Issued", "Passport Delivered"]);

export const wholeFLifecycleTokens: Record<FopLifecycleVisualStatus, { color: string; textColor: string; label: string }> = {
  build: { color: "var(--fuzion-build)", textColor: "var(--fuzion-build-text)", label: "BUILD" },
  advise: { color: "var(--fuzion-advise)", textColor: "var(--fuzion-advise-text)", label: "ADVISE" },
  protect: { color: "var(--fuzion-protect)", textColor: "var(--fuzion-protect-text)", label: "PROTECT" },
  protected: { color: "var(--fuzion-protect)", textColor: "var(--fuzion-protect-text)", label: "PROTECTED" },
  neutral: { color: "var(--fuzion-platform)", textColor: "var(--text-secondary)", label: "Lifecycle pending" }
};

function clampProgress(value: number) {
  return Math.max(0, Math.min(100, Math.round(value)));
}

function state(status: FopLifecycleVisualStatus, progress: number, halo = false): FopLifecycleVisualState {
  const token = wholeFLifecycleTokens[status];
  const overallProgress = clampProgress(progress);
  const saturation = status === "neutral" ? 36 : Math.max(42, overallProgress);
  return {
    status,
    overallProgress,
    saturation,
    color: token.color,
    textColor: token.textColor,
    halo,
    label: token.label,
    accessibleLabel: `Building lifecycle status: ${token.label}`
  };
}

export function visualStateFromProgress(progress: number, protectedComplete = false): FopLifecycleVisualState {
  const overallProgress = clampProgress(progress);
  if (protectedComplete && overallProgress >= 100) {
    return state("protected", 100, true);
  }
  if (overallProgress >= 78) {
    return state("protect", overallProgress);
  }
  if (overallProgress >= 40) {
    return state("advise", overallProgress);
  }
  if (overallProgress > 0) {
    return state("build", overallProgress);
  }
  return state("neutral", 0);
}

export function visualStateFromStatus(status?: string | null, progress = 0): FopLifecycleVisualState {
  const normalized = (status ?? "").trim();
  if (PROTECT_STATUSES.has(normalized)) {
    return state("protect", Math.max(78, clampProgress(progress)));
  }
  if (ADVISE_STATUSES.has(normalized)) {
    return state("advise", Math.max(45, clampProgress(progress)));
  }
  if (BUILD_STATUSES.has(normalized)) {
    return state("build", Math.max(18, clampProgress(progress)));
  }
  return visualStateFromProgress(progress);
}

export function visualStateWithProtectedState(
  base: FopLifecycleVisualState,
  protectedState?: ProtectedStateEvaluation | null
): FopLifecycleVisualState {
  if (protectedState?.protected_state_status === "approved" && protectedState.halo_eligible) {
    return state("protected", 100, true);
  }
  return { ...base, status: base.status === "protected" ? "protect" : base.status, halo: false };
}

export function visualStateFromLifecycleStage(stage: LifecycleStage): FopLifecycleVisualState {
  if (stage === "protect") {
    return state("protect", 88);
  }
  if (stage === "advise") {
    return state("advise", 56);
  }
  return state("build", 28);
}

export function visualStateFromBuilding(building: Building, progress = 0): FopLifecycleVisualState {
  if (building.passport_status) {
    return visualStateFromStatus(building.passport_status, progress);
  }
  if (building.status === "completed_occupied" || building.status === "completed") {
    return state("protect", Math.max(progress, 82));
  }
  if (building.status === "active") {
    return state("build", Math.max(progress, 28));
  }
  return visualStateFromProgress(progress);
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
