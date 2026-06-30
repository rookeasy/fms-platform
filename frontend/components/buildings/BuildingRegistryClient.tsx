"use client";

import Link from "next/link";
import { Plus, RefreshCcw } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";

import { DataTable } from "@/components/DataTable";
import { EmptyState } from "@/components/EmptyState";
import { ErrorState } from "@/components/ErrorState";
import { LoadingState } from "@/components/LoadingState";
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
      const nextOrganizationId = organizationId || loadedOrganizations[0]?.id || "";
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
          <p className="text-sm font-medium text-slate-500">Building Registry</p>
          <h2 className="text-2xl font-semibold text-slate-950">{selectedOrganizationName}</h2>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <select
            value={selectedOrganizationId}
            onChange={(event) => void handleOrganizationChange(event.target.value)}
            className="h-11 min-w-64 rounded-md border border-slate-300 bg-white px-3 text-sm"
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
            className="flex h-11 w-11 items-center justify-center rounded-md border border-slate-300 bg-white text-slate-700"
            aria-label="Refresh buildings"
            title="Refresh buildings"
          >
            <RefreshCcw size={18} />
          </button>
          <button
            type="button"
            onClick={() => setIsFormOpen((value) => !value)}
            className="flex h-11 items-center gap-2 rounded-md bg-slate-950 px-4 text-sm font-semibold text-white"
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
              className="h-11 rounded-md bg-slate-950 px-5 text-sm font-semibold text-white"
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
              key: "name",
              header: "Building Name",
              render: (building) => (
                <div>
                  <Link href={`/buildings/${building.id}`} className="font-semibold text-slate-950 underline">
                    {building.name}
                  </Link>
                  <p className="mt-1 text-xs text-slate-500">{building.bpid}</p>
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
              header: "Status",
              render: (building) => <StatusBadge status={formatControlledValue(building.status)} />
            },
            {
              key: "actions",
              header: "Actions",
              render: (building) => (
                <Link href={`/buildings/${building.id}`} className="text-sm font-semibold text-slate-950 underline">
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
