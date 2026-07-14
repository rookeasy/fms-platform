"use client";

import { Archive, Brain, Check, Download, Edit3, FileUp, History, ShieldCheck, Upload, Users, X } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { DataTable, type DataTableColumn } from "@/components/DataTable";
import { EmptyState } from "@/components/EmptyState";
import { StatusBadge } from "@/components/StatusBadge";
import { documentStatuses, documentTypes, evidenceCategories, formatControlledValue } from "@/lib/controlled-values";
import {
  approveAllDocumentAssetSuggestions,
  approveDocumentAssetSuggestion,
  getDocumentDownloadUrl,
  listDocumentAssetSuggestions,
  rejectDocumentAssetSuggestion,
  type Asset,
  type DocumentAssetSuggestion,
  type DocumentMetadataPayload,
  type DocumentRecord
} from "@/lib/fms-api";

type BuildingDocumentsPanelProps = {
  buildingId: string;
  assets: Asset[];
  documents: DocumentRecord[];
  isSubmitting: boolean;
  presetEvidenceCategory?: string | null;
  libraryMode?: boolean;
  onUpload: (formData: FormData) => Promise<void>;
  onUploadVersion: (documentId: string, formData: FormData) => Promise<void>;
  onUpdate: (documentId: string, payload: Partial<DocumentMetadataPayload>) => Promise<DocumentRecord | void>;
  onArchive: (documentId: string) => Promise<void>;
  onAssetsChanged?: () => Promise<void>;
};

type FilterValue = "all" | "passport" | "client" | "internal" | "drawings" | "certificates" | "compliance" | "warranty" | "om" | "photos" | "archived";

export function BuildingDocumentsPanel({
  buildingId,
  assets,
  documents,
  isSubmitting,
  presetEvidenceCategory,
  libraryMode = false,
  onUpload,
  onUploadVersion,
  onUpdate,
  onArchive,
  onAssetsChanged
}: BuildingDocumentsPanelProps) {
  const [selectedDocument, setSelectedDocument] = useState<DocumentRecord | null>(null);
  const [editingDocument, setEditingDocument] = useState<DocumentRecord | null>(null);
  const [filter, setFilter] = useState<FilterValue>("all");
  const [documentType, setDocumentType] = useState(documentTypes[0]?.key ?? "other");
  const [uploadCategory, setUploadCategory] = useState("");
  const [uploadProgress, setUploadProgress] = useState<string | null>(null);
  const [replacementFile, setReplacementFile] = useState<File | null>(null);
  const [actionDocumentId, setActionDocumentId] = useState<string | null>(null);
  const [reviewingDocument, setReviewingDocument] = useState<DocumentRecord | null>(null);
  const [suggestions, setSuggestions] = useState<DocumentAssetSuggestion[]>([]);
  const [isReviewLoading, setIsReviewLoading] = useState(false);

  const filteredDocuments = documents.filter((document) => {
    const searchable = `${document.document_type} ${document.evidence_category ?? ""}`.toLowerCase();
    if (filter === "passport") {
      return document.is_passport_record;
    }
    if (filter === "client") {
      return document.is_public_to_client;
    }
    if (filter === "internal") {
      return !document.is_public_to_client && !document.is_passport_record;
    }
    if (filter === "drawings") {
      return searchable.includes("drawing");
    }
    if (filter === "certificates") {
      return searchable.includes("certificate");
    }
    if (filter === "compliance") {
      return searchable.includes("compliance") || searchable.includes("p.eng") || searchable.includes("nfpa");
    }
    if (filter === "warranty") {
      return searchable.includes("warranty");
    }
    if (filter === "om") {
      return searchable.includes("o&m") || searchable.includes("manual") || searchable.includes("product data");
    }
    if (filter === "photos") {
      return searchable.includes("photo");
    }
    if (filter === "archived") {
      return document.status === "archived" || Boolean(document.archived_at);
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

  useEffect(() => {
    if (presetEvidenceCategory) {
      setUploadCategory(presetEvidenceCategory);
    }
  }, [presetEvidenceCategory]);

  const columns = useMemo<Array<DataTableColumn<DocumentRecord>>>(
    () => [
      {
        key: "title",
        header: "Evidence Item",
        render: (document) => (
          <button type="button" onClick={() => setSelectedDocument(document)} className="text-left font-semibold text-[#0F172A] underline decoration-[#CBD5E1] underline-offset-4 hover:decoration-[#D95A4E]">
            {document.title}
          </button>
        )
      },
      { key: "type", header: "Document Type", render: (document) => formatControlledValue(document.document_type) },
      { key: "evidence", header: "Evidence Category", render: (document) => document.evidence_category || "-" },
      { key: "status", header: "Status", render: (document) => <StatusBadge status={formatControlledValue(document.status)} /> },
      { key: "extraction", header: "Extraction", render: (document) => <StatusBadge status={formatControlledValue(document.extraction_status)} /> },
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
              onClick={() => void openExtractionReview(document)}
              className="inline-flex h-9 items-center gap-2 rounded-md border border-[#E2E8F0] bg-white px-3 text-xs font-semibold text-[#475569] transition hover:border-[#D95A4E]/35 hover:text-[#0F172A] disabled:cursor-not-allowed disabled:opacity-60"
            >
              <Brain size={14} />
              Review AI
            </button>
            <button
              type="button"
              onClick={() => setSelectedDocument(document)}
              className="inline-flex h-9 items-center gap-2 rounded-md border border-[#E2E8F0] bg-white px-3 text-xs font-semibold text-[#475569] transition hover:border-[#D95A4E]/35 hover:text-[#0F172A]"
            >
              <FileUp size={14} />
              Supersede
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
      const nextValue = !document[field];
      await onUpdate(document.id, {
        [field]: nextValue,
        internal_only:
          field === "is_passport_record"
            ? !(nextValue || document.is_public_to_client)
            : !(document.is_passport_record || nextValue)
      });
    } finally {
      setActionDocumentId(null);
    }
  }

  async function openExtractionReview(document: DocumentRecord) {
    setReviewingDocument(document);
    setIsReviewLoading(true);
    try {
      setSuggestions(await listDocumentAssetSuggestions(document.id));
    } finally {
      setIsReviewLoading(false);
    }
  }

  async function handleApproveSuggestion(suggestion: DocumentAssetSuggestion) {
    if (!reviewingDocument) {
      return;
    }
    setActionDocumentId(reviewingDocument.id);
    try {
      const updated = await approveDocumentAssetSuggestion(reviewingDocument.id, suggestion.id);
      setSuggestions((value) => value.map((item) => (item.id === updated.id ? updated : item)));
      await onAssetsChanged?.();
    } finally {
      setActionDocumentId(null);
    }
  }

  async function handleRejectSuggestion(suggestion: DocumentAssetSuggestion) {
    if (!reviewingDocument) {
      return;
    }
    setActionDocumentId(reviewingDocument.id);
    try {
      const updated = await rejectDocumentAssetSuggestion(reviewingDocument.id, suggestion.id);
      setSuggestions((value) => value.map((item) => (item.id === updated.id ? updated : item)));
    } finally {
      setActionDocumentId(null);
    }
  }

  async function handleApproveAllSuggestions() {
    if (!reviewingDocument) {
      return;
    }
    setActionDocumentId(reviewingDocument.id);
    try {
      const updated = await approveAllDocumentAssetSuggestions(reviewingDocument.id);
      setSuggestions((value) => value.map((item) => updated.find((next) => next.id === item.id) ?? item));
      await onAssetsChanged?.();
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
      evidence_category: String(formData.get("evidence_category") ?? "").trim() || null,
      drawing_number: String(formData.get("drawing_number") ?? "").trim() || null,
      revision: String(formData.get("revision") ?? "").trim() || null,
      issue_date: String(formData.get("issue_date") ?? "").trim() || null,
      status: String(formData.get("status") ?? editingDocument.status),
      notes: String(formData.get("notes") ?? "").trim() || null,
      is_public_to_client: formData.get("is_public_to_client") === "true",
      is_passport_record: formData.get("is_passport_record") === "true",
      internal_only: !(formData.get("is_public_to_client") === "true" || formData.get("is_passport_record") === "true")
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
    const fileInput = form.elements.namedItem("file") as HTMLInputElement | null;
    const files = Array.from(fileInput?.files ?? []);
    for (const [index, file] of files.entries()) {
      const nextFormData = new FormData();
      formData.forEach((value, key) => {
        if (key !== "file") {
          nextFormData.append(key, value);
        }
      });
      nextFormData.set("file", file);
      nextFormData.set("building_id", buildingId);
      if (files.length > 1) {
        nextFormData.set("title", file.name);
      }
      setUploadProgress(`Adding evidence ${index + 1} of ${files.length}`);
      await onUpload(nextFormData);
    }
    form.reset();
    setDocumentType(documentTypes[0]?.key ?? "other");
    setUploadCategory("");
    setUploadProgress(null);
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
    if (selectedDocument.evidence_category) {
      formData.set("evidence_category", selectedDocument.evidence_category);
    }
    formData.set("status", selectedDocument.status || "draft");
    if (selectedDocument.asset_id) {
      formData.set("asset_id", selectedDocument.asset_id);
    }
    await onUploadVersion(selectedDocument.parent_document_id ?? selectedDocument.id, formData);
    setReplacementFile(null);
  }

  return (
    <section className="space-y-5">
      <div>
        <h3 className="text-lg font-semibold tracking-normal text-[#0F172A]">{libraryMode ? "Evidence Workspace" : "Building Library"}</h3>
        <p className="text-sm text-[#64748B]">Add evidence that strengthens the Building Protection Passport.</p>
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
          <label className="text-sm font-medium text-[#475569]">
            Evidence Category
            <select
              name="evidence_category"
              value={uploadCategory}
              onChange={(event) => setUploadCategory(event.target.value)}
              className="mt-1 h-10 w-full rounded-md border border-white/15 px-3 text-sm"
            >
              <option value="">Auto classify</option>
              {evidenceCategories.map((category) => (
                <option key={category} value={category}>
                  {category}
                </option>
              ))}
            </select>
          </label>
          <label className="text-sm font-medium text-[#475569]">
            Status
            <select name="status" defaultValue="draft" className="mt-1 h-10 w-full rounded-md border border-white/15 px-3 text-sm">
              {documentStatuses.map((status) => (
                <option key={status.key} value={status.key}>
                  {status.label}
                </option>
              ))}
            </select>
          </label>
          <label className="text-sm font-medium text-[#475569]">
            Revision
            <input name="revision" className="mt-1 h-10 w-full rounded-md border border-white/15 px-3 text-sm" />
          </label>
          <label className="text-sm font-medium text-[#475569]">
            Issue Date
            <input name="issue_date" type="date" className="mt-1 h-10 w-full rounded-md border border-white/15 px-3 text-sm" />
          </label>
          <label className="text-sm font-medium text-[#475569] md:col-span-2">
            Evidence File(s)
            <input name="file" type="file" multiple required className="mt-1 block w-full text-sm text-[#475569]" />
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
            {uploadProgress ?? (isSubmitting ? "Adding Evidence" : "Add Evidence")}
          </button>
        </div>
      </form>

      <div className="flex flex-wrap gap-2">
        {[
          ["all", "All"],
          ["passport", "Passport Records"],
          ["client", "Client Visible"],
          ["internal", "Internal"],
          ["drawings", "Drawings"],
          ["certificates", "Certificates"],
          ["compliance", "Compliance"],
          ["warranty", "Warranty"],
          ["om", "O&M"],
          ["photos", "Photos"],
          ["archived", "Archived"]
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
        <EmptyState title="No evidence has been added to this section." message="Add evidence or start the Build Passport workflow." />
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
                ["Evidence Category", selectedDocument.evidence_category],
                ["Drawing No.", selectedDocument.drawing_number],
                ["Revision", selectedDocument.revision],
                ["Issue Date", selectedDocument.issue_date],
                ["Extraction", formatControlledValue(selectedDocument.extraction_status)],
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
              <label className="text-sm font-medium text-[#475569]">
                Evidence Category
                <select name="evidence_category" defaultValue={editingDocument.evidence_category ?? ""} className="mt-1 h-10 w-full rounded-md border border-[#E2E8F0] px-3 text-sm">
                  <option value="">Auto classify</option>
                  {evidenceCategories.map((category) => (
                    <option key={category} value={category}>
                      {category}
                    </option>
                  ))}
                </select>
              </label>
              <label className="text-sm font-medium text-[#475569]">
                Status
                <select name="status" defaultValue={editingDocument.status} className="mt-1 h-10 w-full rounded-md border border-[#E2E8F0] px-3 text-sm">
                  {documentStatuses.map((status) => (
                    <option key={status.key} value={status.key}>
                      {status.label}
                    </option>
                  ))}
                </select>
              </label>
              <label className="text-sm font-medium text-[#475569]">
                Drawing No.
                <input name="drawing_number" defaultValue={editingDocument.drawing_number ?? ""} className="mt-1 h-10 w-full rounded-md border border-[#E2E8F0] px-3 text-sm" />
              </label>
              <label className="text-sm font-medium text-[#475569]">
                Revision
                <input name="revision" defaultValue={editingDocument.revision ?? ""} className="mt-1 h-10 w-full rounded-md border border-[#E2E8F0] px-3 text-sm" />
              </label>
              <label className="text-sm font-medium text-[#475569]">
                Issue Date
                <input name="issue_date" type="date" defaultValue={editingDocument.issue_date ?? ""} className="mt-1 h-10 w-full rounded-md border border-[#E2E8F0] px-3 text-sm" />
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
              <label className="text-sm font-medium text-[#475569] md:col-span-2">
                Notes
                <textarea name="notes" defaultValue={editingDocument.notes ?? ""} className="mt-1 min-h-20 w-full rounded-md border border-[#E2E8F0] px-3 py-2 text-sm" />
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

      {reviewingDocument ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#0F172A]/55 px-4 py-6 backdrop-blur-sm">
          <div className="max-h-[86vh] w-full max-w-5xl overflow-y-auto rounded-2xl border border-[#E2E8F0] bg-white p-6 shadow-[0_24px_64px_rgba(15,23,42,0.18)]">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <p className="fop-label">AI Review</p>
                <h4 className="mt-2 text-xl font-semibold text-[#0F172A]">{reviewingDocument.title}</h4>
                <p className="mt-1 text-sm text-[#64748B]">
                  {formatControlledValue(reviewingDocument.extraction_status)} via {reviewingDocument.extraction_source || "rule based extraction"}
                </p>
              </div>
              <div className="flex gap-2">
                <button
                  type="button"
                  disabled={!suggestions.some((item) => item.review_status === "review_required") || actionDocumentId === reviewingDocument.id}
                  onClick={() => void handleApproveAllSuggestions()}
                  className="fop-button-primary disabled:cursor-not-allowed disabled:bg-slate-300"
                >
                  <Check size={16} />
                  Approve All
                </button>
                <button type="button" onClick={() => setReviewingDocument(null)} className="fop-button-secondary">
                  Close
                </button>
              </div>
            </div>

            <div className="mt-5 grid gap-3 md:grid-cols-3">
              {[
                ["Evidence", reviewingDocument.evidence_category || "Auto classified"],
                ["Drawing / Revision", [reviewingDocument.drawing_number, reviewingDocument.revision].filter(Boolean).join(" / ") || "-"],
                ["Source", reviewingDocument.original_filename || "-"]
              ].map(([label, value]) => (
                <div key={label} className="rounded-md border border-[#E2E8F0] bg-[#F8FAFC] p-4">
                  <p className="text-xs font-semibold uppercase text-[#64748B]">{label}</p>
                  <p className="mt-1 text-sm font-semibold text-[#0F172A]">{value}</p>
                </div>
              ))}
            </div>

            <div className="mt-5 overflow-x-auto rounded-md border border-[#E2E8F0]">
              <table className="min-w-full divide-y divide-[#E2E8F0] text-sm">
                <thead className="bg-[#F8FAFC]">
                  <tr>
                    {["Suggested Asset", "Location", "Confidence", "Evidence", "Status", "Actions"].map((header) => (
                      <th key={header} className="px-4 py-3 text-left text-[11px] font-semibold uppercase text-[#64748B]">
                        {header}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#E2E8F0]">
                  {isReviewLoading ? (
                    <tr>
                      <td className="px-4 py-5 text-[#64748B]" colSpan={6}>Loading suggestions...</td>
                    </tr>
                  ) : suggestions.length ? (
                    suggestions.map((suggestion) => (
                      <tr key={suggestion.id}>
                        <td className="px-4 py-3">
                          <div className="font-semibold text-[#0F172A]">{suggestion.suggested_name}</div>
                          <div className="text-xs text-[#64748B]">{suggestion.suggested_asset_type}</div>
                        </td>
                        <td className="px-4 py-3 text-[#475569]">{suggestion.location_description || "-"}</td>
                        <td className="px-4 py-3 text-[#475569]">{suggestion.confidence}%</td>
                        <td className="max-w-64 px-4 py-3 text-[#475569]">{suggestion.evidence_snippet || "-"}</td>
                        <td className="px-4 py-3"><StatusBadge status={formatControlledValue(suggestion.review_status)} /></td>
                        <td className="px-4 py-3">
                          {suggestion.review_status === "review_required" ? (
                            <div className="flex gap-2">
                              <button type="button" onClick={() => void handleApproveSuggestion(suggestion)} className="fop-button-secondary min-h-9 px-3">
                                <Check size={15} />
                                Approve
                              </button>
                              <button type="button" onClick={() => void handleRejectSuggestion(suggestion)} className="fop-button-secondary min-h-9 px-3">
                                <X size={15} />
                                Reject
                              </button>
                            </div>
                          ) : suggestion.approved_asset_id ? (
                            <span className="text-xs font-semibold text-emerald-700">Asset linked</span>
                          ) : null}
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td className="px-4 py-5 text-[#64748B]" colSpan={6}>No asset suggestions were generated for this document.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      ) : null}
    </section>
  );
}


