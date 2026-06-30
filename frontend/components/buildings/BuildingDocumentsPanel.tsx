"use client";

import { Download, FileUp, History, Upload } from "lucide-react";
import { useMemo, useState } from "react";

import { DataTable, type DataTableColumn } from "@/components/DataTable";
import { EmptyState } from "@/components/EmptyState";
import { StatusBadge } from "@/components/StatusBadge";
import { documentTypes, formatControlledValue } from "@/lib/controlled-values";
import { getDocumentDownloadUrl, type Asset, type DocumentRecord } from "@/lib/fms-api";

type BuildingDocumentsPanelProps = {
  buildingId: string;
  assets: Asset[];
  documents: DocumentRecord[];
  isSubmitting: boolean;
  onUpload: (formData: FormData) => Promise<void>;
  onUploadVersion: (documentId: string, formData: FormData) => Promise<void>;
};

type FilterValue = "all" | "passport" | "client";

export function BuildingDocumentsPanel({
  buildingId,
  assets,
  documents,
  isSubmitting,
  onUpload,
  onUploadVersion
}: BuildingDocumentsPanelProps) {
  const [selectedDocument, setSelectedDocument] = useState<DocumentRecord | null>(null);
  const [filter, setFilter] = useState<FilterValue>("all");
  const [documentType, setDocumentType] = useState(documentTypes[0]?.key ?? "other");
  const [replacementFile, setReplacementFile] = useState<File | null>(null);

  const filteredDocuments = documents.filter((document) => {
    if (filter === "passport") {
      return document.is_passport_record;
    }
    if (filter === "client") {
      return document.is_public_to_client;
    }
    return true;
  });

  const versionHistory = useMemo(() => {
    if (!selectedDocument) {
      return [];
    }
    const familyId = selectedDocument.parent_document_id ?? selectedDocument.id;
    return documents
      .filter((document) => document.id === familyId || document.parent_document_id === familyId)
      .sort((left, right) => right.version_number - left.version_number);
  }, [documents, selectedDocument]);

  const columns = useMemo<Array<DataTableColumn<DocumentRecord>>>(
    () => [
      {
        key: "title",
        header: "Document",
        render: (document) => (
          <button type="button" onClick={() => setSelectedDocument(document)} className="text-left font-semibold text-slate-950">
            {document.title}
          </button>
        )
      },
      { key: "type", header: "Type", render: (document) => formatControlledValue(document.document_type) },
      { key: "version", header: "Version", render: (document) => `v${document.version_number}` },
      {
        key: "visibility",
        header: "Visibility",
        render: (document) => (
          <div className="flex flex-wrap gap-2">
            {document.is_passport_record ? <StatusBadge status="Passport Record" /> : null}
            {document.is_public_to_client ? <StatusBadge status="Client Visible" /> : null}
            {!document.is_passport_record && !document.is_public_to_client ? <StatusBadge status="Internal Only" /> : null}
          </div>
        )
      },
      {
        key: "download",
        header: "Download",
        render: (document) => (
          <a
            href={getDocumentDownloadUrl(document.id)}
            className="flex h-9 w-9 items-center justify-center rounded-md border border-slate-300 text-slate-700"
            aria-label={`Download ${document.title}`}
            title={`Download ${document.title}`}
          >
            <Download size={16} />
          </a>
        )
      }
    ],
    []
  );

  async function handleUpload(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const formData = new FormData(form);
    formData.set("building_id", buildingId);
    await onUpload(formData);
    form.reset();
    setDocumentType(documentTypes[0]?.key ?? "other");
  }

  async function handleVersionUpload(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedDocument || !replacementFile) {
      return;
    }
    const formData = new FormData();
    formData.set("file", replacementFile);
    formData.set("title", selectedDocument.title);
    formData.set("document_type", selectedDocument.document_type);
    formData.set("is_public_to_client", String(selectedDocument.is_public_to_client));
    formData.set("is_passport_record", String(selectedDocument.is_passport_record));
    if (selectedDocument.description) {
      formData.set("description", selectedDocument.description);
    }
    if (selectedDocument.asset_id) {
      formData.set("asset_id", selectedDocument.asset_id);
    }
    await onUploadVersion(selectedDocument.parent_document_id ?? selectedDocument.id, formData);
    setReplacementFile(null);
  }

  return (
    <section className="space-y-5">
      <div>
        <h3 className="text-lg font-semibold text-slate-950">Documents</h3>
        <p className="text-sm text-slate-600">Secure building document metadata and local MVP storage.</p>
      </div>

      <form onSubmit={handleUpload} className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
        <div className="grid gap-4 md:grid-cols-3">
          <label className="text-sm font-medium text-slate-700">
            Title
            <input name="title" required className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-sm" />
          </label>
          <label className="text-sm font-medium text-slate-700">
            Document Type
            <select
              name="document_type"
              value={documentType}
              onChange={(event) => setDocumentType(event.target.value)}
              className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-sm"
            >
              {documentTypes.map((type) => (
                <option key={type.key} value={type.key}>
                  {type.label}
                </option>
              ))}
            </select>
          </label>
          <label className="text-sm font-medium text-slate-700">
            Related Asset
            <select name="asset_id" className="mt-1 h-10 w-full rounded-md border border-slate-300 px-3 text-sm">
              <option value="">Building level</option>
              {assets.map((asset) => (
                <option key={asset.id} value={asset.id}>
                  {asset.name}
                </option>
              ))}
            </select>
          </label>
          <label className="text-sm font-medium text-slate-700 md:col-span-2">
            File
            <input name="file" type="file" required className="mt-1 block w-full text-sm text-slate-700" />
          </label>
          <div className="flex flex-wrap items-end gap-4">
            <label className="flex items-center gap-2 text-sm font-medium text-slate-700">
              <input name="is_public_to_client" type="checkbox" value="true" className="h-4 w-4 rounded border-slate-300" />
              Client Visible
            </label>
            <label className="flex items-center gap-2 text-sm font-medium text-slate-700">
              <input name="is_passport_record" type="checkbox" value="true" className="h-4 w-4 rounded border-slate-300" />
              Passport Record
            </label>
          </div>
        </div>
        <label className="mt-4 block text-sm font-medium text-slate-700">
          Description
          <textarea name="description" className="mt-1 min-h-20 w-full rounded-md border border-slate-300 px-3 py-2 text-sm" />
        </label>
        <div className="mt-5 flex justify-end">
          <button
            type="submit"
            disabled={isSubmitting}
            className="flex h-10 items-center gap-2 rounded-md bg-red-700 px-4 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-slate-300"
          >
            <Upload size={16} />
            {isSubmitting ? "Uploading" : "Upload Document"}
          </button>
        </div>
      </form>

      <div className="flex flex-wrap gap-2">
        {[
          ["all", "All"],
          ["passport", "Passport Records"],
          ["client", "Client Visible"]
        ].map(([key, label]) => (
          <button
            key={key}
            type="button"
            onClick={() => setFilter(key as FilterValue)}
            className={`h-9 rounded-md border px-3 text-sm font-semibold ${
              filter === key ? "border-red-700 bg-red-50 text-red-800" : "border-slate-300 bg-white text-slate-700"
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {filteredDocuments.length ? (
        <DataTable columns={columns} rows={filteredDocuments} />
      ) : (
        <EmptyState title="No documents yet." message="Upload the first building document." />
      )}

      {selectedDocument ? (
        <aside className="grid gap-5 rounded-lg border border-slate-200 bg-white p-5 shadow-sm lg:grid-cols-[1fr_360px]">
          <div>
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <h4 className="text-base font-semibold text-slate-950">{selectedDocument.title}</h4>
                <p className="text-sm text-slate-600">{formatControlledValue(selectedDocument.document_type)}</p>
              </div>
              <button type="button" onClick={() => setSelectedDocument(null)} className="text-sm font-semibold text-slate-700">
                Close
              </button>
            </div>
            <dl className="mt-4 grid gap-3 md:grid-cols-2">
              {[
                ["Filename", selectedDocument.original_filename],
                ["Version", `v${selectedDocument.version_number}`],
                ["MIME Type", selectedDocument.file_mime_type],
                ["File Size", selectedDocument.file_size_bytes ? `${selectedDocument.file_size_bytes} bytes` : null],
                ["Passport Record", selectedDocument.is_passport_record ? "Yes" : "No"],
                ["Client Visible", selectedDocument.is_public_to_client ? "Yes" : "No"],
                ["Description", selectedDocument.description]
              ].map(([label, value]) => (
                <div key={label}>
                  <dt className="text-xs font-semibold uppercase text-slate-500">{label}</dt>
                  <dd className="mt-1 text-sm text-slate-800">{value || "-"}</dd>
                </div>
              ))}
            </dl>
            <a
              href={getDocumentDownloadUrl(selectedDocument.id)}
              className="mt-5 inline-flex h-10 items-center gap-2 rounded-md border border-slate-300 px-4 text-sm font-semibold text-slate-800"
            >
              <Download size={16} />
              Download
            </a>
          </div>
          <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
            <div className="flex items-center gap-2 text-sm font-semibold text-slate-950">
              <History size={16} />
              Version History
            </div>
            <div className="mt-3 space-y-2">
              {versionHistory.map((document) => (
                <div key={document.id} className="rounded-md border border-slate-200 bg-white p-3 text-sm">
                  <div className="font-semibold text-slate-950">v{document.version_number}</div>
                  <div className="text-slate-600">{new Date(document.created_at).toLocaleString()}</div>
                </div>
              ))}
            </div>
            <form onSubmit={handleVersionUpload} className="mt-4 space-y-3">
              <label className="block text-sm font-medium text-slate-700">
                Replacement File
                <input
                  type="file"
                  onChange={(event) => setReplacementFile(event.target.files?.[0] ?? null)}
                  className="mt-1 block w-full text-sm text-slate-700"
                />
              </label>
              <button
                type="submit"
                disabled={isSubmitting || !replacementFile}
                className="flex h-10 w-full items-center justify-center gap-2 rounded-md bg-slate-950 px-4 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-slate-300"
              >
                <FileUp size={16} />
                Upload New Version
              </button>
            </form>
          </div>
        </aside>
      ) : null}
    </section>
  );
}
