"use client";

import Link from "next/link";
import { RefreshCcw } from "lucide-react";
import { useCallback, useEffect, useState } from "react";

import { DashboardCard } from "@/components/DashboardCard";
import { EmptyState } from "@/components/EmptyState";
import { ErrorState } from "@/components/ErrorState";
import { LoadingState } from "@/components/LoadingState";
import { StatusBadge } from "@/components/StatusBadge";
import { BuildingAssetsPanel } from "@/components/buildings/BuildingAssetsPanel";
import { BuildingContactsPanel } from "@/components/buildings/BuildingContactsPanel";
import { BuildingDocumentsPanel } from "@/components/buildings/BuildingDocumentsPanel";
import { BuildingForm } from "@/components/buildings/BuildingForm";
import { formatControlledValue } from "@/lib/controlled-values";
import {
  type Building,
  type Asset,
  type AssetPayload,
  type AssetType,
  type BuildingContact,
  type BuildingContactPayload,
  type BuildingPayload,
  type Campus,
  type DocumentRecord,
  type PropertyRecord,
  createAsset,
  createBuildingContact,
  deleteAsset,
  deleteBuildingContact,
  getBuilding,
  getProperty,
  listAssetTypes,
  listBuildingAssets,
  listBuildingContacts,
  listBuildingDocuments,
  listCampuses,
  updateAsset,
  uploadDocument,
  uploadDocumentVersion,
  updateBuilding
} from "@/lib/fms-api";

type BuildingProfileClientProps = {
  buildingId: string;
};

export function BuildingProfileClient({ buildingId }: BuildingProfileClientProps) {
  const [building, setBuilding] = useState<Building | null>(null);
  const [property, setProperty] = useState<PropertyRecord | null>(null);
  const [campus, setCampus] = useState<Campus | null>(null);
  const [contacts, setContacts] = useState<BuildingContact[]>([]);
  const [assetTypes, setAssetTypes] = useState<AssetType[]>([]);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [activeTab, setActiveTab] = useState<"overview" | "assets" | "documents" | "contacts">("overview");
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
      const [loadedAssetTypes, loadedAssets, loadedDocuments, loadedProperty, loadedCampuses] = await Promise.all([
        listAssetTypes(),
        listBuildingAssets(buildingId),
        listBuildingDocuments(buildingId),
        loadedBuilding.property_id ? getProperty(loadedBuilding.property_id) : Promise.resolve(null),
        loadedBuilding.property_id ? listCampuses({ propertyId: loadedBuilding.property_id }) : Promise.resolve([])
      ]);
      setBuilding(loadedBuilding);
      setProperty(loadedProperty);
      setCampus(loadedCampuses.find((item) => item.id === loadedBuilding.campus_id) ?? null);
      setContacts(loadedContacts);
      setAssetTypes(loadedAssetTypes);
      setAssets(loadedAssets);
      setDocuments(loadedDocuments);
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

  async function handleCreateAsset(payload: AssetPayload) {
    setIsSubmitting(true);
    setError(null);
    try {
      const asset = await createAsset(buildingId, payload);
      setAssets((value) => [...value, asset]);
    } catch (assetError) {
      setError(assetError instanceof Error ? assetError.message : "Unable to add asset.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleUpdateAsset(assetId: string, payload: AssetPayload) {
    setIsSubmitting(true);
    setError(null);
    try {
      const asset = await updateAsset(assetId, payload);
      setAssets((value) => value.map((item) => (item.id === asset.id ? asset : item)));
    } catch (assetError) {
      setError(assetError instanceof Error ? assetError.message : "Unable to update asset.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleDeleteAsset(assetId: string) {
    setIsSubmitting(true);
    setError(null);
    try {
      await deleteAsset(assetId);
      setAssets((value) => value.filter((asset) => asset.id !== assetId));
    } catch (assetError) {
      setError(assetError instanceof Error ? assetError.message : "Unable to remove asset.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleUploadDocument(formData: FormData) {
    setIsSubmitting(true);
    setError(null);
    try {
      const document = await uploadDocument(formData);
      setDocuments((value) => [document, ...value]);
    } catch (documentError) {
      setError(documentError instanceof Error ? documentError.message : "Unable to upload document.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleUploadDocumentVersion(documentId: string, formData: FormData) {
    setIsSubmitting(true);
    setError(null);
    try {
      const document = await uploadDocumentVersion(documentId, formData);
      setDocuments((value) => [document, ...value]);
    } catch (documentError) {
      setError(documentError instanceof Error ? documentError.message : "Unable to upload document version.");
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
      <section className="fop-card p-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#7D8CA3]">{building.bpid}</p>
            <h2 className="mt-2 text-2xl font-semibold tracking-normal text-white">{building.name}</h2>
            <p className="mt-1 text-[#B6C1CF]">
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
              className="fop-button-secondary h-10 w-10 px-0"
              aria-label="Refresh building"
              title="Refresh building"
            >
              <RefreshCcw size={18} />
            </button>
            <button
              type="button"
              onClick={() => setIsEditing((value) => !value)}
              className="fop-button-primary h-10"
            >
              {isEditing ? "Close" : "Edit Building"}
            </button>
          </div>
        </div>
        <div className="mt-5 flex flex-wrap gap-3 text-sm text-[#B6C1CF]">
          <span>{formatControlledValue(building.building_type)}</span>
          {building.owner_name ? <span>Owner: {building.owner_name}</span> : null}
          {building.property_manager_name ? <span>Manager: {building.property_manager_name}</span> : null}
          {property ? (
            <Link href={`/properties/${property.id}`} className="font-semibold text-white underline decoration-white/25 underline-offset-4 hover:decoration-[#FF6B5F]">
              Property: {property.name}
            </Link>
          ) : null}
          {campus ? <span>Campus: {campus.name}</span> : null}
          <Link href={`/buildings/${building.id}/passport`} className="font-semibold text-white underline decoration-white/25 underline-offset-4 hover:decoration-[#FF6B5F]">
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
        <DashboardCard title="Assets" value={`${assets.length}`} detail="Building-owned records" />
      </div>

      <nav className="fop-card flex flex-wrap gap-2 p-2" aria-label="Building sections">
        {[
          ["overview", "Overview"],
          ["assets", "Assets"],
          ["documents", "Documents"],
          ["contacts", "Contacts"]
        ].map(([key, label]) => (
          <button
            key={key}
            type="button"
            onClick={() => setActiveTab(key as typeof activeTab)}
            className={`h-10 rounded-xl px-4 text-sm font-semibold transition ${
              activeTab === key ? "bg-[#050A18] text-white shadow-md" : "text-[#B6C1CF] hover:bg-white/10"
            }`}
          >
            {label}
          </button>
        ))}
      </nav>

      {activeTab === "overview" ? (
        <div className="fop-card p-5">
          <h3 className="text-lg font-semibold tracking-normal text-white">Building Details</h3>
          <dl className="mt-4 grid gap-4 md:grid-cols-2">
            {[
              ["Occupancy Classification", building.occupancy_classification],
              ["Construction Year", building.construction_year],
              ["Storeys", building.number_of_storeys],
              ["Total Area Sq Ft", building.total_area_sq_ft],
              ["AHJ", building.ahj_name],
              ["Fire Department", building.fire_department],
              ["Property / Campus", property ? `${property.name}${campus ? ` / ${campus.name}` : ""}` : null],
              ["Insurance Provider", building.insurance_provider],
              ["Notes", building.notes]
            ].map(([label, value]) => (
              <div key={String(label)}>
                <dt className="text-sm font-medium text-[#7D8CA3]">{label}</dt>
                <dd className="mt-1 text-sm text-white">{value || "-"}</dd>
              </div>
            ))}
          </dl>
        </div>
      ) : null}

      {activeTab === "assets" ? (
        <BuildingAssetsPanel
          assets={assets}
          assetTypes={assetTypes}
          isSubmitting={isSubmitting}
          onCreate={handleCreateAsset}
          onUpdate={handleUpdateAsset}
          onDelete={handleDeleteAsset}
        />
      ) : null}

      {activeTab === "documents" ? (
        <BuildingDocumentsPanel
          buildingId={building.id}
          assets={assets}
          documents={documents}
          isSubmitting={isSubmitting}
          onUpload={handleUploadDocument}
          onUploadVersion={handleUploadDocumentVersion}
        />
      ) : null}

      {activeTab === "contacts" ? (
        <BuildingContactsPanel
          contacts={contacts}
          isSubmitting={isSubmitting}
          onCreate={handleCreateContact}
          onDelete={handleDeleteContact}
        />
      ) : null}
    </div>
  );
}


