"use client";

import Link from "next/link";
import { Plus, RefreshCcw } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";

import { DataTable } from "@/components/DataTable";
import { EmptyState } from "@/components/EmptyState";
import { ErrorState } from "@/components/ErrorState";
import { LoadingState } from "@/components/LoadingState";
import { ProgressIndex } from "@/components/ProgressIndex";
import { StatusBadge } from "@/components/StatusBadge";
import { BuildingForm } from "@/components/buildings/BuildingForm";
import { formatControlledValue } from "@/lib/controlled-values";
import {
  type Building,
  type BuildingPayload,
  type Organization,
  createBuilding,
  listBuildings,
  listOrganizations
} from "@/lib/fms-api";
import { getApiBuildingLifecycle, lifecycleLabels } from "@/lib/lifecycle";
import { fppKpiTerms, getMockBuildingScores } from "@/lib/progress-index";

export function BuildingRegistryClient() {
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [buildings, setBuildings] = useState<Building[]>([]);
  const [selectedOrganizationId, setSelectedOrganizationId] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async (organizationId = selectedOrganizationId) => {
    setIsLoading(true);
    setError(null);
    try {
      const loadedOrganizations = await listOrganizations();
      const fuzionOrganization = loadedOrganizations.find((organization) => organization.name === "Fuzion Tech Inc.");
      const nextOrganizationId = organizationId || fuzionOrganization?.id || loadedOrganizations[0]?.id || "";
      const loadedBuildings = await listBuildings(nextOrganizationId || undefined);
      setOrganizations(loadedOrganizations);
      setSelectedOrganizationId(nextOrganizationId);
      setBuildings(loadedBuildings);
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "Unable to load Building Registry.");
    } finally {
      setIsLoading(false);
    }
  }, [selectedOrganizationId]);

  useEffect(() => {
    void loadData("");
  }, [loadData]);

  async function handleOrganizationChange(organizationId: string) {
    setSelectedOrganizationId(organizationId);
    await loadData(organizationId);
  }

  async function handleCreate(payload: BuildingPayload) {
    setIsSubmitting(true);
    setError(null);
    try {
      await createBuilding(payload);
      setIsFormOpen(false);
      await loadData(payload.organization_id);
    } catch (createError) {
      setError(createError instanceof Error ? createError.message : "Unable to create building.");
    } finally {
      setIsSubmitting(false);
    }
  }

  const selectedOrganizationName = useMemo(
    () => organizations.find((organization) => organization.id === selectedOrganizationId)?.name ?? "All organizations",
    [organizations, selectedOrganizationId]
  );

  if (isLoading) {
    return <LoadingState label="Loading Building Registry" />;
  }

  if (error && buildings.length === 0) {
    return <ErrorState message={error} onRetry={() => void loadData()} />;
  }

  return (
    <div className="space-y-6">
      <section className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#7D8CA3]">Building Registry</p>
          <h2 className="mt-1 text-2xl font-semibold tracking-normal text-white">{selectedOrganizationName}</h2>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <select
            value={selectedOrganizationId}
            onChange={(event) => void handleOrganizationChange(event.target.value)}
            className="fop-field min-w-64 bg-white"
          >
            {organizations.map((organization) => (
              <option key={organization.id} value={organization.id}>
                {organization.name}
              </option>
            ))}
          </select>
          <button
            type="button"
            onClick={() => void loadData()}
            className="fop-button-secondary h-11 w-11 px-0"
            aria-label="Refresh buildings"
            title="Refresh buildings"
          >
            <RefreshCcw size={18} />
          </button>
          <button
            type="button"
            onClick={() => setIsFormOpen((value) => !value)}
            className="fop-button-primary"
          >
            <Plus size={18} />
            Add Building
          </button>
        </div>
      </section>

      {error ? <ErrorState message={error} onRetry={() => void loadData()} /> : null}

      {isFormOpen ? (
        <BuildingForm
          organizations={organizations}
          selectedOrganizationId={selectedOrganizationId}
          submitLabel="Create Building"
          isSubmitting={isSubmitting}
          onSubmit={handleCreate}
        />
      ) : null}

      {organizations.length === 0 ? (
        <EmptyState
          title="No organizations available."
          message="Create an organization through the backend API before adding buildings."
        />
      ) : buildings.length === 0 ? (
        <EmptyState
          title="No buildings yet."
          message="Create your first Building Protection Passport."
          action={
            <button
              type="button"
              onClick={() => setIsFormOpen(true)}
              className="fop-button-primary"
            >
              Add Building
            </button>
          }
        />
      ) : (
        <DataTable
          rows={buildings}
          columns={[
            {
              key: "job",
              header: "Job No.",
              render: (building) => <span className="font-semibold text-white">{building.code || "-"}</span>
            },
            {
              key: "name",
              header: "Building Name",
              render: (building) => (
                <div>
                  <Link href={`/buildings/${building.id}`} className="font-semibold text-white underline decoration-white/25 underline-offset-4 hover:decoration-[#FF6B5F]">
                    {building.name}
                  </Link>
                  <p className="mt-1 text-xs text-[#7D8CA3]">Passport No. {building.bpid}</p>
                </div>
              )
            },
            {
              key: "address",
              header: "Address",
              render: (building) =>
                [building.address_line_1, building.city, building.province_state].filter(Boolean).join(", ")
            },
            {
              key: "owner",
              header: "Owner / Manager",
              render: (building) => [building.owner_name, building.property_manager_name].filter(Boolean).join(" / ") || "-"
            },
            {
              key: "type",
              header: "Building Type",
              render: (building) => formatControlledValue(building.building_type)
            },
            {
              key: "status",
              header: "Lifecycle Stage",
              render: (building) => <StatusBadge status={lifecycleLabels[getApiBuildingLifecycle(building)]} />
            },
            {
              key: "fpp_index",
              header: fppKpiTerms.buildingHealthIndex,
              render: (building) => {
                const scores = getMockBuildingScores(building.id);
                return (
                  <div className="min-w-44">
                    <div className="mb-1 flex items-center justify-between gap-2 text-xs">
                      <span className="text-[#B6C1CF]">{fppKpiTerms.protectionScore}</span>
                      <span className="font-semibold text-white">{scores.protectionScore}%</span>
                    </div>
                    <ProgressIndex score={scores.buildingHealthIndex} size="sm" variant="compact" showScore={false} />
                  </div>
                );
              }
            },
            {
              key: "actions",
              header: "Actions",
              render: (building) => (
                <Link href={`/buildings/${building.id}`} className="text-sm font-semibold text-white underline decoration-white/25 underline-offset-4 hover:decoration-[#FF6B5F]">
                  View Building
                </Link>
              )
            }
          ]}
        />
      )}
    </div>
  );
}


