"use client";

import Link from "next/link";
import { Building2, CheckCircle2, Layers3, Map, Plus } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";

import { DataTable, type DataTableColumn } from "@/components/DataTable";
import { EmptyState } from "@/components/EmptyState";
import { ErrorState } from "@/components/ErrorState";
import { LoadingState } from "@/components/LoadingState";
import { ProgressIndex } from "@/components/ProgressIndex";
import { StatusBadge } from "@/components/StatusBadge";
import { formatControlledValue } from "@/lib/controlled-values";
import {
  type Building,
  type Campus,
  type PropertyCloseoutScore,
  type PropertyCampusSummary,
  type PropertyRecord,
  type PortfolioScores,
  assignBuildingToPropertyCampus,
  createCampus,
  createProperty,
  getPropertyCloseoutScore,
  getPropertyCampusSummary,
  listBuildings,
  listCampuses,
  getPortfolioScores,
  listOrganizations,
  listProperties
} from "@/lib/fms-api";
import { fppKpiTerms, getMockBuildingScores } from "@/lib/progress-index";

const propertyTypes = [
  "single_site",
  "campus",
  "portfolio",
  "mixed_use",
  "multi_building_residential_development",
  "industrial",
  "residential",
  "commercial",
  "institutional",
  "other"
];

type SummaryItem = {
  label: string;
  value: number;
  icon: LucideIcon;
};

function optionLabel(value: string) {
  return formatControlledValue(value) || value;
}

export function PropertyCampusClient() {
  const [organizationId, setOrganizationId] = useState<string>("");
  const [properties, setProperties] = useState<PropertyRecord[]>([]);
  const [campuses, setCampuses] = useState<Campus[]>([]);
  const [buildings, setBuildings] = useState<Building[]>([]);
  const [summary, setSummary] = useState<PropertyCampusSummary | null>(null);
  const [closeoutScores, setCloseoutScores] = useState<Record<string, PropertyCloseoutScore>>({});
  const [selectedPropertyId, setSelectedPropertyId] = useState<string>("");
  const [portfolioScores, setPortfolioScores] = useState<PortfolioScores | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadProperties = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const organizations = await listOrganizations();
      const fuzionOrganization = organizations.find((organization) => organization.name === "Fuzion Tech Inc.");
      const nextOrganizationId = organizationId || fuzionOrganization?.id || organizations[0]?.id || "";
      setOrganizationId(nextOrganizationId);
      const [loadedSummary, loadedProperties, loadedCampuses, loadedBuildings] = await Promise.all([
        getPropertyCampusSummary(nextOrganizationId || undefined),
        listProperties(nextOrganizationId || undefined),
        listCampuses({ organizationId: nextOrganizationId || undefined }),
        listBuildings(nextOrganizationId || undefined)
      ]);
      const loadedCloseoutScores = await Promise.all(
        loadedProperties.map(async (property) => {
          try {
            return [property.id, await getPropertyCloseoutScore(property.id)] as const;
          } catch {
            return [property.id, null] as const;
          }
        })
      );
      setSummary(loadedSummary);
      setProperties(loadedProperties);
      setCampuses(loadedCampuses);
      setBuildings(loadedBuildings);
      setCloseoutScores(
        Object.fromEntries(loadedCloseoutScores.filter((entry): entry is readonly [string, PropertyCloseoutScore] => entry[1] !== null))
      );
      setPortfolioScores(await getPortfolioScores(nextOrganizationId || undefined).catch(() => null));
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "Unable to load Property & Campus Management.");
    } finally {
      setIsLoading(false);
    }
  }, [organizationId]);

  useEffect(() => {
    void loadProperties();
  }, [loadProperties]);

  const selectedProperty = properties.find((property) => property.id === selectedPropertyId) ?? properties[0] ?? null;
  const visibleCampuses = selectedProperty ? campuses.filter((campus) => campus.property_id === selectedProperty.id) : campuses;
  const unassignedBuildings = buildings.filter((building) => !building.property_id);
  const portfolioScoreRows = buildings
    .map((building) => {
      const apiScore = portfolioScores?.buildings.find((item) => item.buildingId === building.id);
      const closeoutCompletion = closeoutScores[building.property_id ?? ""]?.completion_percentage;
      const scores = apiScore ?? getMockBuildingScores(
        building.id,
        typeof closeoutCompletion === "number" ? { readinessScore: closeoutCompletion } : {}
      );
      return { building, scores };
    })
    .sort((a, b) => b.scores.buildingHealthIndex - a.scores.buildingHealthIndex);

  const propertyColumns = useMemo<Array<DataTableColumn<PropertyRecord>>>(
    () => [
      {
        key: "name",
        header: "Property",
        render: (property) => (
          <Link href={`/properties/${property.id}`} onClick={() => setSelectedPropertyId(property.id)} className="text-left font-semibold text-white underline">
            {property.name}
          </Link>
        )
      },
      { key: "type", header: "Type", render: (property) => optionLabel(property.property_type) },
      { key: "campuses", header: "Campuses", render: (property) => property.campus_count },
      { key: "buildings", header: "Buildings", render: (property) => property.building_count },
      { key: "status", header: "Status", render: (property) => <StatusBadge status={optionLabel(property.status)} /> }
    ],
    []
  );

  const campusColumns = useMemo<Array<DataTableColumn<Campus>>>(
    () => [
      { key: "name", header: "Campus", render: (campus) => <span className="font-semibold text-white">{campus.name}</span> },
      { key: "type", header: "Type", render: (campus) => optionLabel(campus.campus_type) },
      { key: "buildings", header: "Buildings", render: (campus) => campus.building_count },
      { key: "status", header: "Status", render: (campus) => <StatusBadge status={optionLabel(campus.status)} /> }
    ],
    []
  );

  async function handleCreateProperty(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!organizationId) {
      setError("Create an organization before creating properties.");
      return;
    }
    const form = event.currentTarget;
    const formData = new FormData(form);
    setIsSubmitting(true);
    setError(null);
    try {
      await createProperty({
        organization_id: organizationId,
        name: String(formData.get("name") || ""),
        property_type: String(formData.get("property_type") || "single_site"),
        status: "active",
        address_line_1: String(formData.get("address_line_1") || "") || null,
        city: String(formData.get("city") || "") || null,
        province_state: String(formData.get("province_state") || "") || null,
        postal_code: String(formData.get("postal_code") || "") || null,
        country: "Canada",
        owner_name: String(formData.get("owner_name") || "") || null,
        property_manager_name: String(formData.get("property_manager_name") || "") || null,
        notes: String(formData.get("notes") || "") || null
      });
      form.reset();
      await loadProperties();
    } catch (createError) {
      setError(createError instanceof Error ? createError.message : "Unable to create property.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleCreateCampus(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!organizationId) {
      setError("Create an organization before creating campuses.");
      return;
    }
    const form = event.currentTarget;
    const formData = new FormData(form);
    setIsSubmitting(true);
    setError(null);
    try {
      await createCampus({
        organization_id: organizationId,
        property_id: String(formData.get("property_id") || "") || null,
        name: String(formData.get("name") || ""),
        campus_type: String(formData.get("campus_type") || "campus"),
        status: "active",
        address_line_1: String(formData.get("address_line_1") || "") || null,
        city: String(formData.get("city") || "") || null,
        province_state: String(formData.get("province_state") || "") || null,
        postal_code: String(formData.get("postal_code") || "") || null,
        country: "Canada",
        notes: String(formData.get("notes") || "") || null
      });
      form.reset();
      await loadProperties();
    } catch (createError) {
      setError(createError instanceof Error ? createError.message : "Unable to create campus.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleAssignBuilding(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const formData = new FormData(form);
    const buildingId = String(formData.get("building_id") || "");
    if (!buildingId) {
      return;
    }
    setIsSubmitting(true);
    setError(null);
    try {
      await assignBuildingToPropertyCampus(buildingId, {
        property_id: String(formData.get("property_id") || "") || null,
        campus_id: String(formData.get("campus_id") || "") || null
      });
      form.reset();
      await loadProperties();
    } catch (assignError) {
      setError(assignError instanceof Error ? assignError.message : "Unable to assign building.");
    } finally {
      setIsSubmitting(false);
    }
  }

  if (isLoading) {
    return <LoadingState label="Loading Property & Campus Management" />;
  }

  return (
    <div className="space-y-6">
      <section className="fop-card p-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#7D8CA3]">Property Operations</p>
            <h2 className="mt-2 text-2xl font-semibold tracking-normal text-white">Property & Campus Management</h2>
            <p className="mt-1 max-w-3xl text-sm text-[#B6C1CF]">
              Organize buildings into properties, campuses, phases, and multi-building sites for portfolio operations.
            </p>
          </div>
          <StatusBadge status={summary?.unassigned_buildings ? "Needs Assignment" : "Complete"} />
        </div>
      </section>

      {error ? <ErrorState message={error} onRetry={() => void loadProperties()} /> : null}

      <div className="grid gap-4 md:grid-cols-4">
        {(
          [
            { label: "Properties", value: summary?.properties ?? 0, icon: Map },
            { label: "Campuses", value: summary?.campuses ?? 0, icon: Layers3 },
            { label: "Assigned Buildings", value: summary?.assigned_buildings ?? 0, icon: CheckCircle2 },
            { label: "Unassigned Buildings", value: summary?.unassigned_buildings ?? 0, icon: Building2 }
          ] satisfies SummaryItem[]
        ).map((item) => {
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

      {properties.length ? (
        <section className="space-y-4">
          <div>
            <h3 className="text-lg font-semibold text-white">Closeout Readiness</h3>
            <p className="text-sm text-[#B6C1CF]">Property-level handover status across assigned buildings.</p>
          </div>
          <div className="grid gap-4 lg:grid-cols-3">
            {properties.map((property) => {
              const closeoutScore = closeoutScores[property.id];
              const completion = closeoutScore?.completion_percentage ?? 0;
              return (
                <Link key={property.id} href={`/properties/${property.id}`} className="fop-card block p-5 transition hover:-translate-y-0.5 hover:shadow-xl">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-sm font-semibold text-white">{property.name}</p>
                      <p className="mt-1 text-xs text-[#7D8CA3]">
                        {closeoutScore ? `${closeoutScore.ready_building_count}/${closeoutScore.building_count} buildings ready` : "No score available"}
                      </p>
                    </div>
                    <StatusBadge status={closeoutScore?.ready_for_handover ? "Ready" : "Missing Items"} />
                  </div>
                  <div className="mt-4 flex items-center justify-between text-sm">
                    <span className="font-semibold text-white">{completion}%</span>
                    <span className="text-[#7D8CA3]">{closeoutScore?.missing_items.length ?? 0} missing</span>
                  </div>
                  <div className="mt-2 h-2 overflow-hidden rounded-full bg-slate-100">
                    <div className="h-full rounded-full bg-[color:var(--fuzion-build)]" style={{ width: `${completion}%` }} />
                  </div>
                </Link>
              );
            })}
          </div>
        </section>
      ) : null}

      {portfolioScoreRows.length ? (
        <section className="space-y-4">
          <div>
            <h3 className="text-lg font-semibold text-white">Portfolio FPP Index</h3>
            <p className="text-sm text-[#B6C1CF]">Buildings sorted by {fppKpiTerms.buildingHealthIndex} and {fppKpiTerms.protectionScore}.</p>
          </div>
          <div className="grid gap-4 xl:grid-cols-2">
            {portfolioScoreRows.map(({ building, scores }) => (
              <Link key={building.id} href={`/buildings/${building.id}`} className="fop-card block p-5 transition hover:-translate-y-0.5 hover:border-white/15">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <h4 className="text-base font-semibold text-white">{building.name}</h4>
                    <p className="mt-1 text-sm text-[#B6C1CF]">{[building.city, building.province_state].filter(Boolean).join(", ") || "Building location"}</p>
                    <div className="mt-2 flex flex-wrap gap-2 text-xs font-semibold uppercase tracking-[0.14em] text-[#7D8CA3]">
                      <span>Job No. {building.code || "-"}</span>
                      <span>Passport No. {building.bpid}</span>
                    </div>
                  </div>
                  <span className="text-2xl font-semibold text-white">{scores.buildingHealthIndex}%</span>
                </div>
                <div className="mt-4">
                  <ProgressIndex score={scores.buildingHealthIndex} size="sm" variant="compact" showScore={false} />
                </div>
                <div className="mt-4 grid gap-3 sm:grid-cols-2">
                  {[
                    [fppKpiTerms.protectionScore, scores.protectionScore],
                    [fppKpiTerms.complianceScore, scores.complianceScore],
                    [fppKpiTerms.readinessScore, scores.readinessScore],
                    [fppKpiTerms.intelligenceScore, scores.intelligenceScore]
                  ].map(([label, value]) => (
                    <div key={label} className="rounded-lg border border-[#E2E8F0] bg-[#F8FAFC] px-3 py-2">
                      <div className="flex items-center justify-between gap-3 text-xs">
                        <span className="text-[#B6C1CF]">{label}</span>
                        <span className="font-semibold text-white">{value}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              </Link>
            ))}
          </div>
        </section>
      ) : null}

      <div className="grid gap-6 xl:grid-cols-[1fr_420px]">
        <div className="space-y-6">
          <section className="space-y-4">
            <div>
              <h3 className="text-lg font-semibold text-white">Properties</h3>
              <p className="text-sm text-[#B6C1CF]">Top-level sites, portfolios, and managed properties.</p>
            </div>
            {properties.length ? <DataTable columns={propertyColumns} rows={properties} /> : <EmptyState title="No properties." message="Create the first managed property." />}
          </section>

          <section className="space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <h3 className="text-lg font-semibold text-white">Campuses</h3>
                <p className="text-sm text-[#B6C1CF]">
                  {selectedProperty ? `Showing campuses for ${selectedProperty.name}.` : "Campuses and phases across all properties."}
                </p>
              </div>
              {selectedProperty ? <StatusBadge status={`${selectedProperty.building_count} Building${selectedProperty.building_count === 1 ? "" : "s"}`} /> : null}
            </div>
            {visibleCampuses.length ? <DataTable columns={campusColumns} rows={visibleCampuses} /> : <EmptyState title="No campuses." message="Create a campus or phase for this property." />}
          </section>
        </div>

        <aside className="space-y-6">
          <form onSubmit={handleCreateProperty} className="fop-card p-5">
            <div className="flex items-center gap-2 text-sm font-semibold text-white">
              <Plus size={16} />
              Add Property
            </div>
            <div className="mt-4 grid gap-3">
              <input name="name" required placeholder="Property name" className="h-10 rounded-md border border-white/15 px-3 text-sm" />
              <select name="property_type" className="h-10 rounded-md border border-white/15 px-3 text-sm">
                {propertyTypes.map((type) => (
                  <option key={type} value={type}>
                    {optionLabel(type)}
                  </option>
                ))}
              </select>
              <input name="address_line_1" placeholder="Address" className="h-10 rounded-md border border-white/15 px-3 text-sm" />
              <div className="grid gap-3 sm:grid-cols-2">
                <input name="city" placeholder="City" className="h-10 rounded-md border border-white/15 px-3 text-sm" />
                <input name="province_state" placeholder="Province/State" className="h-10 rounded-md border border-white/15 px-3 text-sm" />
              </div>
              <input name="postal_code" placeholder="Postal code" className="h-10 rounded-md border border-white/15 px-3 text-sm" />
              <input name="owner_name" placeholder="Owner" className="h-10 rounded-md border border-white/15 px-3 text-sm" />
              <input name="property_manager_name" placeholder="Property manager" className="h-10 rounded-md border border-white/15 px-3 text-sm" />
              <textarea name="notes" placeholder="Notes" className="min-h-20 rounded-md border border-white/15 px-3 py-2 text-sm" />
            </div>
            <button type="submit" disabled={isSubmitting} className="fop-button-primary mt-4 w-full disabled:bg-slate-300">
              Create Property
            </button>
          </form>

          <form onSubmit={handleCreateCampus} className="fop-card p-5">
            <div className="flex items-center gap-2 text-sm font-semibold text-white">
              <Plus size={16} />
              Add Campus
            </div>
            <div className="mt-4 grid gap-3">
              <select name="property_id" defaultValue={selectedProperty?.id ?? ""} className="h-10 rounded-md border border-white/15 px-3 text-sm">
                <option value="">No property</option>
                {properties.map((property) => (
                  <option key={property.id} value={property.id}>
                    {property.name}
                  </option>
                ))}
              </select>
              <input name="name" required placeholder="Campus or phase name" className="h-10 rounded-md border border-white/15 px-3 text-sm" />
              <select name="campus_type" className="h-10 rounded-md border border-white/15 px-3 text-sm">
                {["campus", "phase", "complex", "site", "zone", "other"].map((type) => (
                  <option key={type} value={type}>
                    {optionLabel(type)}
                  </option>
                ))}
              </select>
              <input name="address_line_1" placeholder="Address" className="h-10 rounded-md border border-white/15 px-3 text-sm" />
              <div className="grid gap-3 sm:grid-cols-2">
                <input name="city" placeholder="City" className="h-10 rounded-md border border-white/15 px-3 text-sm" />
                <input name="province_state" placeholder="Province/State" className="h-10 rounded-md border border-white/15 px-3 text-sm" />
              </div>
              <input name="postal_code" placeholder="Postal code" className="h-10 rounded-md border border-white/15 px-3 text-sm" />
              <textarea name="notes" placeholder="Notes" className="min-h-20 rounded-md border border-white/15 px-3 py-2 text-sm" />
            </div>
            <button type="submit" disabled={isSubmitting} className="fop-button-primary mt-4 w-full disabled:bg-slate-300">
              Create Campus
            </button>
          </form>

          <form onSubmit={handleAssignBuilding} className="fop-card p-5">
            <div className="text-sm font-semibold text-white">Assign Building</div>
            <div className="mt-4 grid gap-3">
              <select name="building_id" required className="h-10 rounded-md border border-white/15 px-3 text-sm">
                <option value="">Select building</option>
                {unassignedBuildings.map((building) => (
                  <option key={building.id} value={building.id}>
                    {building.name}
                  </option>
                ))}
              </select>
              <select name="property_id" defaultValue={selectedProperty?.id ?? ""} className="h-10 rounded-md border border-white/15 px-3 text-sm">
                <option value="">No property</option>
                {properties.map((property) => (
                  <option key={property.id} value={property.id}>
                    {property.name}
                  </option>
                ))}
              </select>
              <select name="campus_id" className="h-10 rounded-md border border-white/15 px-3 text-sm">
                <option value="">No campus</option>
                {campuses.map((campus) => (
                  <option key={campus.id} value={campus.id}>
                    {campus.name}
                  </option>
                ))}
              </select>
            </div>
            <button type="submit" disabled={isSubmitting || !unassignedBuildings.length} className="fop-button-primary mt-4 w-full disabled:bg-slate-300">
              Assign Building
            </button>
          </form>
        </aside>
      </div>
    </div>
  );
}

