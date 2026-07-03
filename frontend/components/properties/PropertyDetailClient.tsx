"use client";

import Link from "next/link";
import { Building2, FileText, ShieldCheck, Wrench } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";

import { EmptyState } from "@/components/EmptyState";
import { ErrorState } from "@/components/ErrorState";
import { LoadingState } from "@/components/LoadingState";
import { StatusBadge } from "@/components/StatusBadge";
import { PropertyIntelligencePanel } from "@/components/properties/PropertyIntelligencePanel";
import { formatControlledValue } from "@/lib/controlled-values";
import {
  type Asset,
  type Building,
  type Campus,
  type DocumentRecord,
  type Organization,
  type PropertyIntelligence,
  type PropertyRecord,
  getProperty,
  getPropertyIntelligence,
  listBuildingAssets,
  listBuildingDocuments,
  listBuildings,
  listCampuses,
  listOrganizations
} from "@/lib/fms-api";

type PropertyDetailClientProps = {
  propertyId: string;
};

type BuildingEvidence = {
  building: Building;
  assets: Asset[];
  documents: DocumentRecord[];
};

function fullAddress(property: PropertyRecord) {
  return [property.address_line_1, property.city, property.province_state, property.postal_code].filter(Boolean).join(", ");
}

function isSharedInfrastructure(building: Building) {
  const name = building.name.toLowerCase();
  return building.building_type === "shared_infrastructure" || name.includes("shared") || name.includes("common parking");
}

export function PropertyDetailClient({ propertyId }: PropertyDetailClientProps) {
  const [property, setProperty] = useState<PropertyRecord | null>(null);
  const [organization, setOrganization] = useState<Organization | null>(null);
  const [campuses, setCampuses] = useState<Campus[]>([]);
  const [buildingEvidence, setBuildingEvidence] = useState<BuildingEvidence[]>([]);
  const [intelligence, setIntelligence] = useState<PropertyIntelligence | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadProperty = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const loadedProperty = await getProperty(propertyId);
      const [organizations, loadedCampuses, allBuildings, loadedIntelligence] = await Promise.all([
        listOrganizations(),
        listCampuses({ propertyId }),
        listBuildings(loadedProperty.organization_id),
        getPropertyIntelligence(propertyId)
      ]);
      const relatedBuildings = allBuildings.filter((building) => building.property_id === loadedProperty.id);
      const evidence = await Promise.all(
        relatedBuildings.map(async (building) => {
          const [assets, documents] = await Promise.all([
            listBuildingAssets(building.id),
            listBuildingDocuments(building.id)
          ]);
          return { building, assets, documents };
        })
      );

      setProperty(loadedProperty);
      setOrganization(organizations.find((item) => item.id === loadedProperty.organization_id) ?? null);
      setCampuses(loadedCampuses);
      setBuildingEvidence(evidence);
      setIntelligence(loadedIntelligence);
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "Unable to load property.");
    } finally {
      setIsLoading(false);
    }
  }, [propertyId]);

  useEffect(() => {
    void loadProperty();
  }, [loadProperty]);

  const sharedInfrastructure = buildingEvidence.filter((item) => isSharedInfrastructure(item.building));
  const regularBuildings = buildingEvidence.filter((item) => !isSharedInfrastructure(item.building));
  const assets = buildingEvidence.flatMap((item) => item.assets);
  const documents = buildingEvidence.flatMap((item) => item.documents);
  const passportDocuments = documents.filter((document) => document.is_passport_record);
  const clientVisibleDocuments = documents.filter((document) => document.is_public_to_client);
  const closeoutReady = useMemo(() => {
    const hasBuildingA = buildingEvidence.some((item) => item.building.name.toLowerCase().includes("building a"));
    const hasBuildingB = buildingEvidence.some((item) => item.building.name.toLowerCase().includes("building b"));
    return hasBuildingA && hasBuildingB && sharedInfrastructure.length > 0 && passportDocuments.length >= 5;
  }, [buildingEvidence, passportDocuments.length, sharedInfrastructure.length]);

  if (isLoading) {
    return <LoadingState label="Loading property" />;
  }

  if (error && !property) {
    return <ErrorState message={error} onRetry={() => void loadProperty()} />;
  }

  if (!property) {
    return <EmptyState title="Property not found." message="The requested property could not be loaded." />;
  }

  return (
    <div className="space-y-6">
      <section className="fop-card p-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-sm font-medium text-[#7D8CA3]">{organization?.name ?? "Organization"}</p>
            <h2 className="mt-2 text-2xl font-semibold text-white">{property.name}</h2>
            <p className="mt-1 text-[#B6C1CF]">{fullAddress(property) || "No address recorded"}</p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <StatusBadge status={formatControlledValue(property.status)} />
            <StatusBadge status={closeoutReady ? "Ready for Handover" : "Missing Items"} />
          </div>
        </div>
        <div className="mt-5 grid gap-4 md:grid-cols-4">
          <div>
            <p className="text-sm font-medium text-[#7D8CA3]">Type</p>
            <p className="mt-1 text-sm font-semibold text-white">{formatControlledValue(property.property_type)}</p>
          </div>
          <div>
            <p className="text-sm font-medium text-[#7D8CA3]">Campuses</p>
            <p className="mt-1 text-sm font-semibold text-white">{campuses.length}</p>
          </div>
          <div>
            <p className="text-sm font-medium text-[#7D8CA3]">Buildings</p>
            <p className="mt-1 text-sm font-semibold text-white">{regularBuildings.length}</p>
          </div>
          <div>
            <p className="text-sm font-medium text-[#7D8CA3]">Shared Infrastructure</p>
            <p className="mt-1 text-sm font-semibold text-white">{sharedInfrastructure.length}</p>
          </div>
        </div>
      </section>

      {error ? <ErrorState message={error} onRetry={() => void loadProperty()} /> : null}

      {intelligence ? <PropertyIntelligencePanel intelligence={intelligence} /> : null}

      <div className="grid gap-4 md:grid-cols-4">
        {[
          { label: "Related Buildings", value: buildingEvidence.length, icon: Building2 },
          { label: "Key Assets", value: assets.length, icon: Wrench },
          { label: "Documents", value: documents.length, icon: FileText },
          { label: "Passport Records", value: passportDocuments.length, icon: ShieldCheck }
        ].map((item) => {
          const Icon = item.icon;
          return (
            <div key={item.label} className="fop-card p-5">
              <div className="flex items-center justify-between gap-3">
                <p className="text-sm font-medium text-[#7D8CA3]">{item.label}</p>
                <Icon className="text-slate-400" size={18} />
              </div>
              <p className="mt-2 text-2xl font-semibold text-white">{item.value}</p>
            </div>
          );
        })}
      </div>

      <section className="space-y-3">
        <h3 className="text-lg font-semibold text-white">SOHO Phase I Structure</h3>
        <div className="grid gap-4 lg:grid-cols-3">
          {buildingEvidence.map(({ building, assets: buildingAssets, documents: buildingDocuments }) => (
            <Link key={building.id} href={`/buildings/${building.id}`} className="fop-card p-5 hover:border-white/30">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="font-semibold text-white">{building.name}</p>
                  <p className="mt-1 text-sm text-[#B6C1CF]">{formatControlledValue(building.building_type)}</p>
                </div>
                <StatusBadge status={formatControlledValue(building.status)} />
              </div>
              <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
                <div>
                  <p className="text-[#7D8CA3]">Assets</p>
                  <p className="font-semibold text-white">{buildingAssets.length}</p>
                </div>
                <div>
                  <p className="text-[#7D8CA3]">Evidence</p>
                  <p className="font-semibold text-white">{buildingDocuments.length}</p>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <div className="fop-card p-5">
          <h3 className="text-lg font-semibold text-white">Key Assets</h3>
          <div className="mt-4 space-y-3">
            {assets.slice(0, 12).map((asset) => (
              <div key={asset.id} className="flex items-center justify-between gap-3 border-b border-slate-100 pb-3 last:border-b-0 last:pb-0">
                <div>
                  <p className="text-sm font-semibold text-white">{asset.name}</p>
                  <p className="text-sm text-[#7D8CA3]">{asset.location_description || "No location"}</p>
                </div>
                <StatusBadge status={formatControlledValue(asset.status)} />
              </div>
            ))}
            {!assets.length ? <EmptyState title="No assets." message="Seed or add assets for this property." /> : null}
          </div>
        </div>

        <div className="fop-card p-5">
          <h3 className="text-lg font-semibold text-white">Document / Evidence Summary</h3>
          <dl className="mt-4 grid gap-4 sm:grid-cols-3">
            <div>
              <dt className="text-sm font-medium text-[#7D8CA3]">Total</dt>
              <dd className="mt-1 text-2xl font-semibold text-white">{documents.length}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-[#7D8CA3]">Client Visible</dt>
              <dd className="mt-1 text-2xl font-semibold text-white">{clientVisibleDocuments.length}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-[#7D8CA3]">Passport</dt>
              <dd className="mt-1 text-2xl font-semibold text-white">{passportDocuments.length}</dd>
            </div>
          </dl>
          <div className="mt-5 space-y-2">
            {documents.slice(0, 8).map((document) => (
              <div key={document.id} className="flex items-center justify-between gap-3 text-sm">
                <span className="font-medium text-white">{document.title}</span>
                <span className="text-[#7D8CA3]">{formatControlledValue(document.document_type)}</span>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}


