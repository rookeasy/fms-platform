"use client";

import { useEffect, useState } from "react";

import { assetConditionRatings, assetStatuses } from "@/lib/controlled-values";
import type { Asset, AssetPayload, AssetType } from "@/lib/fms-api";

type AssetFormProps = {
  asset?: Asset | null;
  assetTypes: AssetType[];
  isSubmitting: boolean;
  submitLabel: string;
  onSubmit: (payload: AssetPayload) => Promise<void>;
};

const emptyAsset: AssetPayload = {
  asset_type_id: "",
  name: "",
  asset_tag: "",
  location_description: "",
  manufacturer: "",
  model: "",
  serial_number: "",
  status: "active",
  installation_date: "",
  warranty_expiry_date: "",
  condition_rating: "unknown",
  inspection_frequency_months: undefined,
  last_inspected_at: undefined,
  next_inspection_due_at: undefined,
  replacement_cost_estimate: undefined,
  remaining_useful_life_years: undefined,
  notes: ""
};

export function AssetForm({ asset, assetTypes, isSubmitting, submitLabel, onSubmit }: AssetFormProps) {
  const [values, setValues] = useState<AssetPayload>(emptyAsset);

  useEffect(() => {
    setValues(
      asset
        ? {
            asset_type_id: asset.asset_type_id,
            name: asset.name,
            asset_tag: asset.asset_tag ?? "",
            location_description: asset.location_description ?? "",
            manufacturer: asset.manufacturer ?? "",
            model: asset.model ?? "",
            serial_number: asset.serial_number ?? "",
            status: asset.status,
            installation_date: asset.installation_date ?? "",
            warranty_expiry_date: asset.warranty_expiry_date ?? "",
            condition_rating: asset.condition_rating ?? "unknown",
            inspection_frequency_months: asset.inspection_frequency_months ?? undefined,
            last_inspected_at: asset.last_inspected_at ?? undefined,
            next_inspection_due_at: asset.next_inspection_due_at ?? undefined,
            replacement_cost_estimate: asset.replacement_cost_estimate ?? undefined,
            remaining_useful_life_years: asset.remaining_useful_life_years ?? undefined,
            notes: asset.notes ?? ""
          }
        : { ...emptyAsset, asset_type_id: assetTypes[0]?.id ?? "" }
    );
  }, [asset, assetTypes]);

  function updateValue(key: keyof AssetPayload, value: string) {
    setValues((current) => ({
      ...current,
      [key]:
        key === "inspection_frequency_months" ||
        key === "remaining_useful_life_years" ||
        key === "replacement_cost_estimate"
          ? value
            ? Number(value)
            : undefined
          : value
    }));
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await onSubmit(values);
    if (!asset) {
      setValues({ ...emptyAsset, asset_type_id: assetTypes[0]?.id ?? "" });
    }
  }

  return (
    <form onSubmit={handleSubmit} className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <div className="grid gap-4 md:grid-cols-2">
        <label className="text-sm font-medium text-slate-700">
          Asset Name
          <input
            required
            value={values.name}
            onChange={(event) => updateValue("name", event.target.value)}
            className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-sm"
          />
        </label>
        <label className="text-sm font-medium text-slate-700">
          Asset Type
          <select
            required
            value={values.asset_type_id}
            onChange={(event) => updateValue("asset_type_id", event.target.value)}
            className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-sm"
          >
            {assetTypes.map((assetType) => (
              <option key={assetType.id} value={assetType.id}>
                {assetType.name}
              </option>
            ))}
          </select>
        </label>
        <label className="text-sm font-medium text-slate-700">
          Asset Tag
          <input
            value={values.asset_tag ?? ""}
            onChange={(event) => updateValue("asset_tag", event.target.value)}
            className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-sm"
          />
        </label>
        <label className="text-sm font-medium text-slate-700">
          Status
          <select
            value={values.status}
            onChange={(event) => updateValue("status", event.target.value)}
            className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-sm"
          >
            {assetStatuses.map((status) => (
              <option key={status.key} value={status.key}>
                {status.label}
              </option>
            ))}
          </select>
        </label>
        <label className="text-sm font-medium text-slate-700">
          Condition
          <select
            value={values.condition_rating ?? "unknown"}
            onChange={(event) => updateValue("condition_rating", event.target.value)}
            className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-sm"
          >
            {assetConditionRatings.map((condition) => (
              <option key={condition.key} value={condition.key}>
                {condition.label}
              </option>
            ))}
          </select>
        </label>
        <label className="text-sm font-medium text-slate-700">
          Location
          <input
            value={values.location_description ?? ""}
            onChange={(event) => updateValue("location_description", event.target.value)}
            className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-sm"
          />
        </label>
        <label className="text-sm font-medium text-slate-700">
          Manufacturer
          <input
            value={values.manufacturer ?? ""}
            onChange={(event) => updateValue("manufacturer", event.target.value)}
            className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-sm"
          />
        </label>
        <label className="text-sm font-medium text-slate-700">
          Model
          <input
            value={values.model ?? ""}
            onChange={(event) => updateValue("model", event.target.value)}
            className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-sm"
          />
        </label>
        <label className="text-sm font-medium text-slate-700">
          Serial Number
          <input
            value={values.serial_number ?? ""}
            onChange={(event) => updateValue("serial_number", event.target.value)}
            className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-sm"
          />
        </label>
        <label className="text-sm font-medium text-slate-700">
          Installation Date
          <input
            type="date"
            value={values.installation_date ?? ""}
            onChange={(event) => updateValue("installation_date", event.target.value)}
            className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-sm"
          />
        </label>
      </div>
      <label className="mt-4 block text-sm font-medium text-slate-700">
        Notes
        <textarea
          value={values.notes ?? ""}
          onChange={(event) => updateValue("notes", event.target.value)}
          className="mt-1 min-h-24 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
        />
      </label>
      <div className="mt-5 flex justify-end">
        <button
          type="submit"
          disabled={isSubmitting || assetTypes.length === 0}
          className="h-10 rounded-md bg-red-700 px-4 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-slate-300"
        >
          {isSubmitting ? "Saving" : submitLabel}
        </button>
      </div>
    </form>
  );
}
