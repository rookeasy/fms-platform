"use client";

import type { FormEvent } from "react";

import { buildingStatuses, buildingTypes } from "@/lib/controlled-values";
import type { Building, BuildingPayload, Organization } from "@/lib/fms-api";

type BuildingFormProps = {
  building?: Building;
  organizations?: Organization[];
  selectedOrganizationId?: string;
  submitLabel: string;
  isSubmitting: boolean;
  onSubmit: (payload: BuildingPayload) => Promise<void>;
};

function getFormValue(form: HTMLFormElement, name: string) {
  return String(new FormData(form).get(name) ?? "").trim();
}

function getOptionalNumber(form: HTMLFormElement, name: string) {
  const value = getFormValue(form, name);
  return value ? Number(value) : null;
}

export function BuildingForm({
  building,
  organizations = [],
  selectedOrganizationId,
  submitLabel,
  isSubmitting,
  onSubmit
}: BuildingFormProps) {
  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const payload: BuildingPayload = {
      organization_id: getFormValue(form, "organization_id"),
      name: getFormValue(form, "name"),
      address_line_1: getFormValue(form, "address_line_1"),
      address_line_2: getFormValue(form, "address_line_2") || null,
      city: getFormValue(form, "city"),
      province_state: getFormValue(form, "province_state"),
      postal_code: getFormValue(form, "postal_code") || null,
      country: getFormValue(form, "country") || "Canada",
      latitude: getOptionalNumber(form, "latitude"),
      longitude: getOptionalNumber(form, "longitude"),
      building_type: getFormValue(form, "building_type"),
      occupancy_classification: getFormValue(form, "occupancy_classification") || null,
      construction_year: getOptionalNumber(form, "construction_year"),
      number_of_storeys: getOptionalNumber(form, "number_of_storeys"),
      total_area_sq_ft: getOptionalNumber(form, "total_area_sq_ft"),
      owner_name: getFormValue(form, "owner_name") || null,
      property_manager_name: getFormValue(form, "property_manager_name") || null,
      fire_department: getFormValue(form, "fire_department") || null,
      ahj_name: getFormValue(form, "ahj_name") || null,
      insurance_provider: getFormValue(form, "insurance_provider") || null,
      status: getFormValue(form, "status") || "active",
      notes: getFormValue(form, "notes") || null
    };

    await onSubmit(payload);
    if (!building) {
      form.reset();
    }
  }

  const organizationId = building?.organization_id ?? selectedOrganizationId ?? organizations[0]?.id ?? "";

  return (
    <form onSubmit={handleSubmit} className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Organization</span>
          <select
            name="organization_id"
            defaultValue={organizationId}
            disabled={Boolean(building)}
            required
            className="mt-2 h-11 w-full rounded-md border border-slate-300 px-3 text-sm"
          >
            <option value="" disabled>
              Select organization
            </option>
            {organizations.map((organization) => (
              <option key={organization.id} value={organization.id}>
                {organization.name}
              </option>
            ))}
            {building && !organizations.some((organization) => organization.id === building.organization_id) ? (
              <option value={building.organization_id}>{building.organization_id}</option>
            ) : null}
          </select>
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Building Name</span>
          <input name="name" required defaultValue={building?.name} className="mt-2 h-11 w-full rounded-md border border-slate-300 px-3 text-sm" />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Building Type</span>
          <select name="building_type" required defaultValue={building?.building_type ?? "commercial"} className="mt-2 h-11 w-full rounded-md border border-slate-300 px-3 text-sm">
            {buildingTypes.map((type) => (
              <option key={type.key} value={type.key}>
                {type.label}
              </option>
            ))}
          </select>
        </label>
        <label className="block md:col-span-2">
          <span className="text-sm font-medium text-slate-700">Address Line 1</span>
          <input name="address_line_1" required defaultValue={building?.address_line_1} className="mt-2 h-11 w-full rounded-md border border-slate-300 px-3 text-sm" />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Address Line 2</span>
          <input name="address_line_2" defaultValue={building?.address_line_2 ?? ""} className="mt-2 h-11 w-full rounded-md border border-slate-300 px-3 text-sm" />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">City</span>
          <input name="city" required defaultValue={building?.city} className="mt-2 h-11 w-full rounded-md border border-slate-300 px-3 text-sm" />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Province / State</span>
          <input name="province_state" required defaultValue={building?.province_state ?? "ON"} className="mt-2 h-11 w-full rounded-md border border-slate-300 px-3 text-sm" />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Postal Code</span>
          <input name="postal_code" defaultValue={building?.postal_code ?? ""} className="mt-2 h-11 w-full rounded-md border border-slate-300 px-3 text-sm" />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Country</span>
          <input name="country" defaultValue={building?.country ?? "Canada"} className="mt-2 h-11 w-full rounded-md border border-slate-300 px-3 text-sm" />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Status</span>
          <select name="status" defaultValue={building?.status ?? "active"} className="mt-2 h-11 w-full rounded-md border border-slate-300 px-3 text-sm">
            {buildingStatuses.map((status) => (
              <option key={status.key} value={status.key}>
                {status.label}
              </option>
            ))}
          </select>
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Owner Name</span>
          <input name="owner_name" defaultValue={building?.owner_name ?? ""} className="mt-2 h-11 w-full rounded-md border border-slate-300 px-3 text-sm" />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Property Manager</span>
          <input name="property_manager_name" defaultValue={building?.property_manager_name ?? ""} className="mt-2 h-11 w-full rounded-md border border-slate-300 px-3 text-sm" />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">AHJ</span>
          <input name="ahj_name" defaultValue={building?.ahj_name ?? ""} className="mt-2 h-11 w-full rounded-md border border-slate-300 px-3 text-sm" />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Fire Department</span>
          <input name="fire_department" defaultValue={building?.fire_department ?? ""} className="mt-2 h-11 w-full rounded-md border border-slate-300 px-3 text-sm" />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Insurance Provider</span>
          <input name="insurance_provider" defaultValue={building?.insurance_provider ?? ""} className="mt-2 h-11 w-full rounded-md border border-slate-300 px-3 text-sm" />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Occupancy Classification</span>
          <input name="occupancy_classification" defaultValue={building?.occupancy_classification ?? ""} className="mt-2 h-11 w-full rounded-md border border-slate-300 px-3 text-sm" />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Construction Year</span>
          <input name="construction_year" type="number" min="0" defaultValue={building?.construction_year ?? ""} className="mt-2 h-11 w-full rounded-md border border-slate-300 px-3 text-sm" />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Storeys</span>
          <input name="number_of_storeys" type="number" min="0" defaultValue={building?.number_of_storeys ?? ""} className="mt-2 h-11 w-full rounded-md border border-slate-300 px-3 text-sm" />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Total Area Sq Ft</span>
          <input name="total_area_sq_ft" type="number" min="0" step="0.01" defaultValue={building?.total_area_sq_ft ?? ""} className="mt-2 h-11 w-full rounded-md border border-slate-300 px-3 text-sm" />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Latitude</span>
          <input name="latitude" type="number" step="0.0000001" defaultValue={building?.latitude ?? ""} className="mt-2 h-11 w-full rounded-md border border-slate-300 px-3 text-sm" />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Longitude</span>
          <input name="longitude" type="number" step="0.0000001" defaultValue={building?.longitude ?? ""} className="mt-2 h-11 w-full rounded-md border border-slate-300 px-3 text-sm" />
        </label>
        <label className="block md:col-span-2 xl:col-span-3">
          <span className="text-sm font-medium text-slate-700">Notes</span>
          <textarea name="notes" defaultValue={building?.notes ?? ""} className="mt-2 min-h-24 w-full rounded-md border border-slate-300 px-3 py-2 text-sm" />
        </label>
      </div>
      <div className="mt-5 flex justify-end">
        <button type="submit" disabled={isSubmitting} className="h-11 rounded-md bg-slate-950 px-5 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-slate-400">
          {isSubmitting ? "Saving..." : submitLabel}
        </button>
      </div>
    </form>
  );
}
