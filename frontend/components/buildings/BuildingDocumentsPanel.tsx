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
          <button type="button" onClick={() => setSelectedDocument(document)} className="text-left font-semibold text-white">
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
            className="flex h-9 w-9 items-center justify-center rounded-md border border-white/15 text-[#B6C1CF]"
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
        <h3 className="text-lg font-semibold tracking-normal text-white">Documents</h3>
        <p className="text-sm text-[#B6C1CF]">Secure building document metadata and local MVP storage.</p>
      </div>

      <form onSubmit={handleUpload} className="fop-card p-5">
        <div className="grid gap-4 md:grid-cols-3">
          <label className="text-sm font-medium text-[#B6C1CF]">
            Title
            <input name="title" required className="mt-1 h-10 w-full rounded-md border border-white/15 px-3 text-sm" />
          </label>
          <label className="text-sm font-medium text-[#B6C1CF]">
            Document Type
            <select
              name="document_type"
              value={documentType}
              onChange={(event) => setDocumentType(event.target.value)}
              className="mt-1 h-10 w-full rounded-md border border-white/15 px-3 text-sm"
            >
              {documentTypes.map((type) => (
                <option key={type.key} value={type.key}>
                  {type.label}
                </option>
              ))}
            </select>
          </label>
          <label className="text-sm font-medium text-[#B6C1CF]">
            Related Asset
            <select name="asset_id" className="mt-1 h-10 w-full rounded-md border border-white/15 px-3 text-sm">
              <option value="">Building level</option>
              {assets.map((asset) => (
                <option key={asset.id} value={asset.id}>
                  {asset.name}
                </option>
              ))}
            </select>
          </label>
          <label className="text-sm font-medium text-[#B6C1CF] md:col-span-2">
            File
            <input name="file" type="file" required className="mt-1 block w-full text-sm text-[#B6C1CF]" />
          </label>
          <div className="flex flex-wrap items-end gap-4">
            <label className="flex items-center gap-2 text-sm font-medium text-[#B6C1CF]">
              <input name="is_public_to_client" type="checkbox" value="true" className="h-4 w-4 rounded border-white/15" />
              Client Visible
            </label>
            <label className="flex items-center gap-2 text-sm font-medium text-[#B6C1CF]">
              <input name="is_passport_record" type="checkbox" value="true" className="h-4 w-4 rounded border-white/15" />
              Passport Record
            </label>
          </div>
        </div>
        <label className="mt-4 block text-sm font-medium text-[#B6C1CF]">
          Description
          <textarea name="description" className="mt-1 min-h-20 w-full rounded-md border border-white/15 px-3 py-2 text-sm" />
        </label>
        <div className="mt-5 flex justify-end">
          <button
            type="submit"
            disabled={isSubmitting}
            className="fop-button-primary disabled:cursor-not-allowed disabled:bg-slate-300"
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
            className={`h-9 rounded-xl border px-3 text-sm font-semibold transition ${
              filter === key ? "border-[#FF6B5F] bg-[#FF6B5F] text-[#050A18]" : "border-white/15 bg-white/5 text-[#B6C1CF] hover:border-white/30"
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
        <aside className="fop-card grid gap-5 p-5 lg:grid-cols-[1fr_360px]">
          <div>
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <h4 className="text-base font-semibold text-white">{selectedDocument.title}</h4>
                <p className="text-sm text-[#B6C1CF]">{formatControlledValue(selectedDocument.document_type)}</p>
              </div>
              <button type="button" onClick={() => setSelectedDocument(null)} className="text-sm font-semibold text-[#B6C1CF]">
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
                  <dt className="text-xs font-semibold uppercase text-[#7D8CA3]">{label}</dt>
                  <dd className="mt-1 text-sm text-[#DCE5F2]">{value || "-"}</dd>
                </div>
              ))}
            </dl>
            <a
              href={getDocumentDownloadUrl(selectedDocument.id)}
              className="fop-button-secondary mt-5"
            >
              <Download size={16} />
              Download
            </a>
          </div>
          <div className="rounded-2xl border border-white/10 bg-white/[0.035] p-4">
            <div className="flex items-center gap-2 text-sm font-semibold text-white">
              <History size={16} />
              Version History
            </div>
            <div className="mt-3 space-y-2">
              {versionHistory.map((document) => (
                <div key={document.id} className="rounded-md border border-white/10 bg-white/5 p-3 text-sm">
                  <div className="font-semibold text-white">v{document.version_number}</div>
                  <div className="text-[#B6C1CF]">{new Date(document.created_at).toLocaleString()}</div>
                </div>
              ))}
            </div>
            <form onSubmit={handleVersionUpload} className="mt-4 space-y-3">
              <label className="block text-sm font-medium text-[#B6C1CF]">
                Replacement File
                <input
                  type="file"
                  onChange={(event) => setReplacementFile(event.target.files?.[0] ?? null)}
                  className="mt-1 block w-full text-sm text-[#B6C1CF]"
                />
              </label>
              <button
                type="submit"
                disabled={isSubmitting || !replacementFile}
                className="fop-button-primary w-full disabled:cursor-not-allowed disabled:bg-slate-300"
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


