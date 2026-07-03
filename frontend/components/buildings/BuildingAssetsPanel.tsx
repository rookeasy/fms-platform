"use client";

import { Edit, Plus, Trash2 } from "lucide-react";
import { useMemo, useState } from "react";

import { DataTable, type DataTableColumn } from "@/components/DataTable";
import { EmptyState } from "@/components/EmptyState";
import { StatusBadge } from "@/components/StatusBadge";
import { AssetForm } from "@/components/buildings/AssetForm";
import { formatControlledValue } from "@/lib/controlled-values";
import type { Asset, AssetPayload, AssetType } from "@/lib/fms-api";

type BuildingAssetsPanelProps = {
  assets: Asset[];
  assetTypes: AssetType[];
  isSubmitting: boolean;
  onCreate: (payload: AssetPayload) => Promise<void>;
  onUpdate: (assetId: string, payload: AssetPayload) => Promise<void>;
  onDelete: (assetId: string) => Promise<void>;
};

export function BuildingAssetsPanel({
  assets,
  assetTypes,
  isSubmitting,
  onCreate,
  onUpdate,
  onDelete
}: BuildingAssetsPanelProps) {
  const [isAdding, setIsAdding] = useState(false);
  const [editingAsset, setEditingAsset] = useState<Asset | null>(null);
  const [selectedAsset, setSelectedAsset] = useState<Asset | null>(null);

  const columns = useMemo<Array<DataTableColumn<Asset>>>(
    () => [
      {
        key: "name",
        header: "Asset",
        render: (asset) => (
          <button type="button" onClick={() => setSelectedAsset(asset)} className="text-left font-semibold text-white">
            {asset.name}
          </button>
        )
      },
      { key: "type", header: "Type", render: (asset) => asset.asset_type?.name ?? "Unknown" },
      { key: "status", header: "Status", render: (asset) => <StatusBadge status={formatControlledValue(asset.status)} /> },
      { key: "condition", header: "Condition", render: (asset) => formatControlledValue(asset.condition_rating) || "-" },
      {
        key: "actions",
        header: "Actions",
        render: (asset) => (
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setEditingAsset(asset)}
              className="fop-button-secondary h-9 w-9 px-0"
              aria-label={`Edit ${asset.name}`}
              title={`Edit ${asset.name}`}
            >
              <Edit size={16} />
            </button>
            <button
              type="button"
              onClick={() => void onDelete(asset.id)}
              className="flex h-9 w-9 items-center justify-center rounded-xl border border-rose-200 bg-white/5 text-rose-700 transition hover:bg-rose-50"
              aria-label={`Remove ${asset.name}`}
              title={`Remove ${asset.name}`}
            >
              <Trash2 size={16} />
            </button>
          </div>
        )
      }
    ],
    [onDelete]
  );

  return (
    <section className="space-y-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-lg font-semibold tracking-normal text-white">Assets</h3>
          <p className="text-sm text-[#B6C1CF]">Building-owned fire protection assets.</p>
        </div>
        <button
          type="button"
          onClick={() => setIsAdding((value) => !value)}
          className="fop-button-primary"
        >
          <Plus size={16} />
          Add Asset
        </button>
      </div>

      {isAdding ? <AssetForm assetTypes={assetTypes} isSubmitting={isSubmitting} submitLabel="Create Asset" onSubmit={onCreate} /> : null}

      {editingAsset ? (
        <AssetForm
          asset={editingAsset}
          assetTypes={assetTypes}
          isSubmitting={isSubmitting}
          submitLabel="Update Asset"
          onSubmit={async (payload) => {
            await onUpdate(editingAsset.id, payload);
            setEditingAsset(null);
          }}
        />
      ) : null}

      {assets.length ? <DataTable columns={columns} rows={assets} /> : <EmptyState title="No assets yet." message="Add the first protected building asset." />}

      {selectedAsset ? (
        <aside className="fop-card p-5">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <h4 className="text-base font-semibold text-white">{selectedAsset.name}</h4>
              <p className="text-sm text-[#B6C1CF]">{selectedAsset.asset_type?.name ?? "Unknown asset type"}</p>
            </div>
            <button type="button" onClick={() => setSelectedAsset(null)} className="text-sm font-semibold text-[#B6C1CF]">
              Close
            </button>
          </div>
          <dl className="mt-4 grid gap-3 md:grid-cols-3">
            {[
              ["Asset Tag", selectedAsset.asset_tag],
              ["Location", selectedAsset.location_description],
              ["Manufacturer", selectedAsset.manufacturer],
              ["Model", selectedAsset.model],
              ["Serial Number", selectedAsset.serial_number],
              ["Installed", selectedAsset.installation_date],
              ["Status", formatControlledValue(selectedAsset.status)],
              ["Condition", formatControlledValue(selectedAsset.condition_rating)],
              ["Notes", selectedAsset.notes]
            ].map(([label, value]) => (
              <div key={label}>
                <dt className="text-xs font-semibold uppercase text-[#7D8CA3]">{label}</dt>
                <dd className="mt-1 text-sm text-[#DCE5F2]">{value || "-"}</dd>
              </div>
            ))}
          </dl>
        </aside>
      ) : null}
    </section>
  );
}

