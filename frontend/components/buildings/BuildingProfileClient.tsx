"use client";

import Link from "next/link";
import { RefreshCcw } from "lucide-react";
import { useCallback, useEffect, useState } from "react";

import { DashboardCard } from "@/components/DashboardCard";
import { EmptyState } from "@/components/EmptyState";
import { ErrorState } from "@/components/ErrorState";
import { LoadingState } from "@/components/LoadingState";
import { StatusBadge } from "@/components/StatusBadge";
import { BuildingContactsPanel } from "@/components/buildings/BuildingContactsPanel";
import { BuildingForm } from "@/components/buildings/BuildingForm";
import { formatControlledValue } from "@/lib/controlled-values";
import {
  type Building,
  type BuildingContact,
  type BuildingContactPayload,
  type BuildingPayload,
  createBuildingContact,
  deleteBuildingContact,
  getBuilding,
  listBuildingContacts,
  updateBuilding
} from "@/lib/fms-api";

type BuildingProfileClientProps = {
  buildingId: string;
};

export function BuildingProfileClient({ buildingId }: BuildingProfileClientProps) {
  const [building, setBuilding] = useState<Building | null>(null);
  const [contacts, setContacts] = useState<BuildingContact[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadBuilding = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [loadedBuilding, loadedContacts] = await Promise.all([
        getBuilding(buildingId),
        listBuildingContacts(buildingId)
      ]);
      setBuilding(loadedBuilding);
      setContacts(loadedContacts);
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "Unable to load building profile.");
    } finally {
      setIsLoading(false);
    }
  }, [buildingId]);

  useEffect(() => {
    void loadBuilding();
  }, [loadBuilding]);

  async function handleUpdate(payload: BuildingPayload) {
    setIsSubmitting(true);
    setError(null);
    try {
      const updatedBuilding = await updateBuilding(buildingId, payload);
      setBuilding(updatedBuilding);
      setIsEditing(false);
    } catch (updateError) {
      setError(updateError instanceof Error ? updateError.message : "Unable to update building.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleCreateContact(payload: BuildingContactPayload) {
    setIsSubmitting(true);
    setError(null);
    try {
      const contact = await createBuildingContact(buildingId, payload);
      setContacts((value) => [...value, contact]);
    } catch (contactError) {
      setError(contactError instanceof Error ? contactError.message : "Unable to add contact.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleDeleteContact(contactId: string) {
    setIsSubmitting(true);
    setError(null);
    try {
      await deleteBuildingContact(contactId);
      setContacts((value) => value.filter((contact) => contact.id !== contactId));
    } catch (contactError) {
      setError(contactError instanceof Error ? contactError.message : "Unable to remove contact.");
    } finally {
      setIsSubmitting(false);
    }
  }

  if (isLoading) {
    return <LoadingState label="Loading building profile" />;
  }

  if (error && !building) {
    return <ErrorState message={error} onRetry={() => void loadBuilding()} />;
  }

  if (!building) {
    return <EmptyState title="Building not found." message="The requested building could not be loaded." />;
  }

  return (
    <div className="space-y-6">
      <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-sm font-medium text-slate-500">{building.bpid}</p>
            <h2 className="mt-2 text-2xl font-semibold text-slate-950">{building.name}</h2>
            <p className="mt-1 text-slate-600">
              {[building.address_line_1, building.city, building.province_state, building.postal_code]
                .filter(Boolean)
                .join(", ")}
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <StatusBadge status={formatControlledValue(building.status)} />
            <button
              type="button"
              onClick={() => void loadBuilding()}
              className="flex h-10 w-10 items-center justify-center rounded-md border border-slate-300 text-slate-700"
              aria-label="Refresh building"
              title="Refresh building"
            >
              <RefreshCcw size={18} />
            </button>
            <button
              type="button"
              onClick={() => setIsEditing((value) => !value)}
              className="h-10 rounded-md bg-slate-950 px-4 text-sm font-semibold text-white"
            >
              {isEditing ? "Close" : "Edit Building"}
            </button>
          </div>
        </div>
        <div className="mt-5 flex flex-wrap gap-3 text-sm text-slate-600">
          <span>{formatControlledValue(building.building_type)}</span>
          {building.owner_name ? <span>Owner: {building.owner_name}</span> : null}
          {building.property_manager_name ? <span>Manager: {building.property_manager_name}</span> : null}
          <Link href={`/buildings/${building.id}/passport`} className="font-semibold text-slate-950 underline">
            View Passport
          </Link>
        </div>
      </section>

      {error ? <ErrorState message={error} onRetry={() => void loadBuilding()} /> : null}

      {isEditing ? (
        <BuildingForm building={building} submitLabel="Update Building" isSubmitting={isSubmitting} onSubmit={handleUpdate} />
      ) : null}

      <div className="grid gap-4 md:grid-cols-3">
        <DashboardCard title="Building Type" value={formatControlledValue(building.building_type)} detail="Controlled by FMS-0010" />
        <DashboardCard title="Contacts" value={`${contacts.length}`} detail="Building-specific contacts" />
        <DashboardCard title="Status" value={formatControlledValue(building.status)} detail="Registry status" />
      </div>

      <section className="grid gap-6 xl:grid-cols-[1fr_420px]">
        <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <h3 className="text-lg font-semibold text-slate-950">Building Details</h3>
          <dl className="mt-4 grid gap-4 md:grid-cols-2">
            {[
              ["Occupancy Classification", building.occupancy_classification],
              ["Construction Year", building.construction_year],
              ["Storeys", building.number_of_storeys],
              ["Total Area Sq Ft", building.total_area_sq_ft],
              ["AHJ", building.ahj_name],
              ["Fire Department", building.fire_department],
              ["Insurance Provider", building.insurance_provider],
              ["Notes", building.notes]
            ].map(([label, value]) => (
              <div key={String(label)}>
                <dt className="text-sm font-medium text-slate-500">{label}</dt>
                <dd className="mt-1 text-sm text-slate-950">{value || "-"}</dd>
              </div>
            ))}
          </dl>
        </div>
        <BuildingContactsPanel
          contacts={contacts}
          isSubmitting={isSubmitting}
          onCreate={handleCreateContact}
          onDelete={handleDeleteContact}
        />
      </section>
    </div>
  );
}
