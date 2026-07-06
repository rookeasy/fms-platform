"use client";

import { Archive, Download, Edit3, FileUp, History, ShieldCheck, Upload, Users } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { DataTable, type DataTableColumn } from "@/components/DataTable";
import { EmptyState } from "@/components/EmptyState";
import { StatusBadge } from "@/components/StatusBadge";
import { documentTypes, formatControlledValue } from "@/lib/controlled-values";
import { getDocumentDownloadUrl, type Asset, type DocumentMetadataPayload, type DocumentRecord } from "@/lib/fms-api";

type BuildingDocumentsPanelProps = {
  buildingId: string;
  assets: Asset[];
  documents: DocumentRecord[];
  isSubmitting: boolean;
  onUpload: (formData: FormData) => Promise<void>;
  onUploadVersion: (documentId: string, formData: FormData) => Promise<void>;
  onUpdate: (documentId: string, payload: Partial<DocumentMetadataPayload>) => Promise<DocumentRecord | void>;
  onArchive: (documentId: string) => Promise<void>;
};

type FilterValue = "all" | "passport" | "client";

export function BuildingDocumentsPanel({
  buildingId,
  assets,
  documents,
  isSubmitting,
  onUpload,
  onUploadVersion,
  onUpdate,
  onArchive
}: BuildingDocumentsPanelProps) {
  const [selectedDocument, setSelectedDocument] = useState<DocumentRecord | null>(null);
  const [editingDocument, setEditingDocument] = useState<DocumentRecord | null>(null);
  const [filter, setFilter] = useState<FilterValue>("all");
  const [documentType, setDocumentType] = useState(documentTypes[0]?.key ?? "other");
  const [replacementFile, setReplacementFile] = useState<File | null>(null);
  const [actionDocumentId, setActionDocumentId] = useState<string | null>(null);

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

  useEffect(() => {
    if (selectedDocument) {
      setSelectedDocument(documents.find((document) => document.id === selectedDocument.id) ?? null);
    }
    if (editingDocument) {
      setEditingDocument(documents.find((document) => document.id === editingDocument.id) ?? null);
    }
  }, [documents, editingDocument, selectedDocument]);

  const columns = useMemo<Array<DataTableColumn<DocumentRecord>>>(
    () => [
      {
        key: "title",
        header: "Document",
        render: (document) => (
          <button type="button" onClick={() => setSelectedDocument(document)} className="text-left font-semibold text-[#0F172A] underline decoration-[#CBD5E1] underline-offset-4 hover:decoration-[#D95A4E]">
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
            className="flex h-9 w-9 items-center justify-center rounded-md border border-[#E2E8F0] bg-white text-[#64748B] transition hover:border-[#D95A4E]/35 hover:text-[#0F172A]"
            aria-label={`Download ${document.title}`}
            title={`Download ${document.title}`}
          >
            <Download size={16} />
          </a>
        )
      },
      {
        key: "actions",
        header: "Actions",
        render: (document) => (
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => setEditingDocument(document)}
              className="inline-flex h-9 items-center gap-2 rounded-md border border-[#E2E8F0] bg-white px-3 text-xs font-semibold text-[#475569] transition hover:border-[#D95A4E]/35 hover:text-[#0F172A]"
            >
              <Edit3 size={14} />
              Edit
            </button>
            <button
              type="button"
              disabled={isSubmitting || actionDocumentId === document.id}
              onClick={() => void handleToggle(document, "is_passport_record")}
              className={`inline-flex h-9 items-center gap-2 rounded-md border px-3 text-xs font-semibold transition disabled:cursor-not-allowed disabled:opacity-60 ${
                document.is_passport_record
                  ? "border-[#D95A4E] bg-[#FFF1EE] text-[#9F342A]"
                  : "border-[#E2E8F0] bg-white text-[#475569] hover:border-[#D95A4E]/35 hover:text-[#0F172A]"
              }`}
            >
              <ShieldCheck size={14} />
              Passport
            </button>
            <button
              type="button"
              disabled={isSubmitting || actionDocumentId === document.id}
              onClick={() => void handleToggle(document, "is_public_to_client")}
              className={`inline-flex h-9 items-center gap-2 rounded-md border px-3 text-xs font-semibold transition disabled:cursor-not-allowed disabled:opacity-60 ${
                document.is_public_to_client
                  ? "border-[#D95A4E] bg-[#FFF1EE] text-[#9F342A]"
                  : "border-[#E2E8F0] bg-white text-[#475569] hover:border-[#D95A4E]/35 hover:text-[#0F172A]"
              }`}
            >
              <Users size={14} />
              Client
            </button>
            <button
              type="button"
              disabled={isSubmitting || actionDocumentId === document.id}
              onClick={() => void handleArchive(document)}
              className="inline-flex h-9 items-center gap-2 rounded-md border border-[#E2E8F0] bg-white px-3 text-xs font-semibold text-[#64748B] transition hover:border-red-200 hover:bg-red-50 hover:text-red-700 disabled:cursor-not-allowed disabled:opacity-60"
            >
              <Archive size={14} />
              Archive
            </button>
          </div>
        )
      }
    ],
    [actionDocumentId, isSubmitting]
  );

  async function handleToggle(document: DocumentRecord, field: "is_passport_record" | "is_public_to_client") {
    setActionDocumentId(document.id);
    try {
      await onUpdate(document.id, { [field]: !document[field] });
    } finally {
      setActionDocumentId(null);
    }
  }

  async function handleArchive(document: DocumentRecord) {
    const confirmed = window.confirm(`Archive "${document.title}"? It will be removed from the visible document list.`);
    if (!confirmed) {
      return;
    }
    setActionDocumentId(document.id);
    try {
      await onArchive(document.id);
      if (selectedDocument?.id === document.id) {
        setSelectedDocument(null);
      }
      if (editingDocument?.id === document.id) {
        setEditingDocument(null);
      }
    } finally {
      setActionDocumentId(null);
    }
  }

  async function handleEditSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!editingDocument) {
      return;
    }
    const formData = new FormData(event.currentTarget);
    const assetId = String(formData.get("asset_id") ?? "");
    const payload: Partial<DocumentMetadataPayload> = {
      title: String(formData.get("title") ?? "").trim(),
      document_type: String(formData.get("document_type") ?? editingDocument.document_type),
      description: String(formData.get("description") ?? "").trim() || null,
      asset_id: assetId || null,
      is_public_to_client: formData.get("is_public_to_client") === "true",
      is_passport_record: formData.get("is_passport_record") === "true"
    };
    setActionDocumentId(editingDocument.id);
    try {
      const updatedDocument = await onUpdate(editingDocument.id, payload);
      setEditingDocument(null);
      if (updatedDocument && selectedDocument?.id === updatedDocument.id) {
        setSelectedDocument(updatedDocument);
      }
    } finally {
      setActionDocumentId(null);
    }
  }

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
        <h3 className="text-lg font-semibold tracking-normal text-[#0F172A]">Documents</h3>
        <p className="text-sm text-[#64748B]">Secure building document metadata and local MVP storage.</p>
      </div>

      <form onSubmit={handleUpload} className="fop-card p-5">
        <div className="grid gap-4 md:grid-cols-3">
          <label className="text-sm font-medium text-[#475569]">
            Title
            <input name="title" required className="mt-1 h-10 w-full rounded-md border border-white/15 px-3 text-sm" />
          </label>
          <label className="text-sm font-medium text-[#475569]">
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
          <label className="text-sm font-medium text-[#475569]">
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
          <label className="text-sm font-medium text-[#475569] md:col-span-2">
            File
            <input name="file" type="file" required className="mt-1 block w-full text-sm text-[#475569]" />
          </label>
          <div className="flex flex-wrap items-end gap-4">
            <label className="flex items-center gap-2 text-sm font-medium text-[#475569]">
              <input name="is_public_to_client" type="checkbox" value="true" className="h-4 w-4 rounded border-white/15" />
              Client Visible
            </label>
            <label className="flex items-center gap-2 text-sm font-medium text-[#475569]">
              <input name="is_passport_record" type="checkbox" value="true" className="h-4 w-4 rounded border-white/15" />
              Passport Record
            </label>
          </div>
        </div>
        <label className="mt-4 block text-sm font-medium text-[#475569]">
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
              filter === key ? "border-[#D95A4E] bg-[#D95A4E] text-white" : "border-[#E2E8F0] bg-white text-[#475569] hover:border-[#D95A4E]/30"
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

      {editingDocument ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#0F172A]/55 px-4 py-6 backdrop-blur-sm">
          <form onSubmit={handleEditSubmit} className="w-full max-w-2xl rounded-2xl border border-[#E2E8F0] bg-white p-6 shadow-[0_24px_64px_rgba(15,23,42,0.18)]">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <p className="fop-label">Document Controls</p>
                <h4 className="mt-2 text-xl font-semibold text-[#0F172A]">Edit document metadata</h4>
              </div>
              <button type="button" onClick={() => setEditingDocument(null)} className="text-sm font-semibold text-[#64748B] hover:text-[#0F172A]">
                Close
              </button>
            </div>
            <div className="mt-5 grid gap-4 md:grid-cols-2">
              <label className="text-sm font-medium text-[#475569]">
                Title
                <input name="title" required defaultValue={editingDocument.title} className="mt-1 h-10 w-full rounded-md border border-[#E2E8F0] px-3 text-sm" />
              </label>
              <label className="text-sm font-medium text-[#475569]">
                Document Type
                <select name="document_type" defaultValue={editingDocument.document_type} className="mt-1 h-10 w-full rounded-md border border-[#E2E8F0] px-3 text-sm">
                  {documentTypes.map((type) => (
                    <option key={type.key} value={type.key}>
                      {type.label}
                    </option>
                  ))}
                </select>
              </label>
              <label className="text-sm font-medium text-[#475569] md:col-span-2">
                Related Asset
                <select name="asset_id" defaultValue={editingDocument.asset_id ?? ""} className="mt-1 h-10 w-full rounded-md border border-[#E2E8F0] px-3 text-sm">
                  <option value="">Building level</option>
                  {assets.map((asset) => (
                    <option key={asset.id} value={asset.id}>
                      {asset.name}
                    </option>
                  ))}
                </select>
              </label>
              <label className="text-sm font-medium text-[#475569] md:col-span-2">
                Description
                <textarea name="description" defaultValue={editingDocument.description ?? ""} className="mt-1 min-h-24 w-full rounded-md border border-[#E2E8F0] px-3 py-2 text-sm" />
              </label>
              <label className="flex items-center gap-2 text-sm font-medium text-[#475569]">
                <input name="is_public_to_client" type="checkbox" value="true" defaultChecked={editingDocument.is_public_to_client} className="h-4 w-4 rounded border-[#CBD5E1] accent-[#D95A4E]" />
                Client Visible
              </label>
              <label className="flex items-center gap-2 text-sm font-medium text-[#475569]">
                <input name="is_passport_record" type="checkbox" value="true" defaultChecked={editingDocument.is_passport_record} className="h-4 w-4 rounded border-[#CBD5E1] accent-[#D95A4E]" />
                Passport Record
              </label>
            </div>
            <div className="mt-6 flex justify-end gap-3">
              <button type="button" onClick={() => setEditingDocument(null)} className="fop-button-secondary">
                Cancel
              </button>
              <button type="submit" disabled={isSubmitting || actionDocumentId === editingDocument.id} className="fop-button-primary disabled:cursor-not-allowed disabled:bg-slate-300">
                Save Changes
              </button>
            </div>
          </form>
        </div>
      ) : null}
    </section>
  );
}


