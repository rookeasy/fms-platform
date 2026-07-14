export type ApiEnvelope<T> = {
  data: T;
};

export type FmsApiError = {
  error?: {
    code?: string;
    message?: string;
    details?: unknown;
  };
};

export type Organization = {
  id: string;
  name: string;
  legal_name?: string | null;
  organization_type: string;
  status: string;
};

export type Building = {
  id: string;
  organization_id: string;
  property_id?: string | null;
  campus_id?: string | null;
  bpid: string;
  code?: string | null;
  name: string;
  address_line_1: string;
  address_line_2?: string | null;
  city: string;
  province_state: string;
  postal_code?: string | null;
  country: string;
  latitude?: number | null;
  longitude?: number | null;
  building_type: string;
  occupancy_classification?: string | null;
  construction_year?: number | null;
  number_of_storeys?: number | null;
  total_area_sq_ft?: number | null;
  owner_name?: string | null;
  property_manager_name?: string | null;
  fire_department?: string | null;
  ahj_name?: string | null;
  insurance_provider?: string | null;
  status: string;
  project_classification?: string | null;
  passport_eligible?: boolean;
  passport_status?: string;
  passport_issue_date?: string | null;
  passport_version?: string | null;
  client_handover_status?: string | null;
  notes?: string | null;
};

export type BuildingPayload = Omit<Building, "id" | "bpid">;

export type PropertyRecord = {
  id: string;
  organization_id: string;
  name: string;
  property_type: string;
  status: string;
  address_line_1?: string | null;
  address_line_2?: string | null;
  city?: string | null;
  province_state?: string | null;
  postal_code?: string | null;
  country?: string | null;
  owner_name?: string | null;
  property_manager_name?: string | null;
  notes?: string | null;
  campus_count: number;
  building_count: number;
  created_at: string;
  updated_at: string;
};

export type PropertyPayload = Omit<PropertyRecord, "id" | "campus_count" | "building_count" | "created_at" | "updated_at">;

export type Campus = {
  id: string;
  organization_id: string;
  property_id?: string | null;
  name: string;
  campus_type: string;
  status: string;
  address_line_1?: string | null;
  address_line_2?: string | null;
  city?: string | null;
  province_state?: string | null;
  postal_code?: string | null;
  country?: string | null;
  notes?: string | null;
  building_count: number;
  created_at: string;
  updated_at: string;
};

export type CampusPayload = Omit<Campus, "id" | "building_count" | "created_at" | "updated_at">;

export type PropertyCampusSummary = {
  properties: number;
  campuses: number;
  assigned_buildings: number;
  unassigned_buildings: number;
};

export type SearchResult = {
  id: string;
  type: "organization" | "property" | "campus" | "building" | "asset" | "document" | "passport";
  title: string;
  subtitle: string;
  matched_field: string;
  url: string;
};

export type BuildingContact = {
  id: string;
  organization_id: string;
  building_id: string;
  contact_type: string;
  name: string;
  company?: string | null;
  job_title?: string | null;
  email?: string | null;
  phone?: string | null;
  mobile?: string | null;
  is_primary: boolean;
  is_emergency_contact: boolean;
  notes?: string | null;
};

export type BuildingContactPayload = Omit<BuildingContact, "id" | "organization_id" | "building_id">;

export type AssetType = {
  id: string;
  name: string;
  code: string;
  category?: string | null;
  description?: string | null;
  default_inspection_frequency_months?: number | null;
};

export type Asset = {
  id: string;
  organization_id: string;
  building_id: string;
  source_document_id?: string | null;
  asset_type_id: string;
  asset_type?: AssetType | null;
  name: string;
  asset_tag?: string | null;
  location_description?: string | null;
  manufacturer?: string | null;
  model?: string | null;
  serial_number?: string | null;
  status: string;
  installation_date?: string | null;
  warranty_expiry_date?: string | null;
  condition_rating?: string | null;
  inspection_frequency_months?: number | null;
  last_inspected_at?: string | null;
  next_inspection_due_at?: string | null;
  replacement_cost_estimate?: number | null;
  remaining_useful_life_years?: number | null;
  notes?: string | null;
  created_at: string;
  updated_at: string;
};

export type AssetPayload = Omit<Asset, "id" | "organization_id" | "building_id" | "asset_type" | "created_at" | "updated_at">;

export type DocumentRecord = {
  id: string;
  organization_id: string;
  property_id?: string | null;
  building_id?: string | null;
  asset_id?: string | null;
  document_type: string;
  title: string;
  description?: string | null;
  evidence_category?: string | null;
  drawing_number?: string | null;
  revision?: string | null;
  issue_date?: string | null;
  status: string;
  original_filename?: string | null;
  storage_bucket?: string | null;
  storage_key?: string | null;
  file_mime_type?: string | null;
  file_size_bytes?: number | null;
  version_number: number;
  parent_document_id?: string | null;
  generated_by_system: boolean;
  effective_date?: string | null;
  expiry_date?: string | null;
  is_public_to_client: boolean;
  is_passport_record: boolean;
  internal_only: boolean;
  extraction_status: "pending" | "processing" | "review_required" | "approved" | "rejected" | "failed" | string;
  extraction_source?: string | null;
  extraction_summary?: Record<string, unknown> | null;
  archived_at?: string | null;
  notes?: string | null;
  created_at: string;
  updated_at: string;
};

export type DocumentMetadataPayload = Pick<
  DocumentRecord,
  | "document_type"
  | "title"
  | "description"
  | "property_id"
  | "building_id"
  | "asset_id"
  | "evidence_category"
  | "drawing_number"
  | "revision"
  | "issue_date"
  | "status"
  | "effective_date"
  | "expiry_date"
  | "is_public_to_client"
  | "is_passport_record"
  | "internal_only"
  | "notes"
>;

export type DocumentAssetSuggestion = {
  id: string;
  organization_id: string;
  document_id: string;
  building_id?: string | null;
  asset_type_id?: string | null;
  approved_asset_id?: string | null;
  suggested_asset_type: string;
  suggested_name: string;
  location_description?: string | null;
  manufacturer?: string | null;
  model?: string | null;
  confidence: number;
  evidence_snippet?: string | null;
  extraction_source: string;
  review_status: "review_required" | "approved" | "rejected" | string;
  reviewed_at?: string | null;
  notes?: string | null;
  created_at: string;
  updated_at: string;
};

export type DocumentAssetSuggestionPayload = Partial<
  Pick<DocumentAssetSuggestion, "suggested_asset_type" | "suggested_name" | "location_description" | "manufacturer" | "model" | "notes">
>;

export type PassportSummary = {
  building: Building;
  contacts: BuildingContact[];
  assets: Asset[];
  documents: DocumentRecord[];
  timeline: Array<{
    event_type: string;
    label: string;
    occurred_at: string;
    record_id: string;
  }>;
  health_score: {
    status: string;
    score: number | null;
  };
  membership: {
    status: string;
    plan: string | null;
  };
};

export type ProtectedStateCriterion = {
  key: string;
  label: string;
  status: "passed" | "failed" | "unknown" | string;
  message: string;
};

export type ProtectedStateEvaluation = {
  building_id: string;
  protected_state_status: "not_eligible" | "review_required" | "eligible" | "approved" | "suspended" | "revoked" | string;
  halo_eligible: boolean;
  criteria_total: number;
  criteria_passed: number;
  criteria_failed: number;
  criteria_unknown: number;
  criteria: ProtectedStateCriterion[];
  blocking_items: string[];
  warnings: string[];
  evaluated_at: string;
  evaluation_version: string;
  certification_record_id?: string | null;
  approved_at?: string | null;
  approved_by?: string | null;
};

export type PassportOnboardingQueueItem = {
  project: string;
  property?: string | null;
  building_id: string;
  building: string;
  job_no?: string | null;
  passport_no?: string | null;
  project_classification: "active" | "completed" | "service-only" | "design-only" | "archived" | string;
  completion_status: string;
  closeout_score: number;
  missing_items: string[];
  passport_eligible: boolean;
  passport_status: string;
  passport_issue_date?: string | null;
  passport_version?: string | null;
  client_handover_status?: string | null;
  protected_state_status: string;
  halo_eligible: boolean;
  next_action: string;
  closeout_url: string;
  passport_url: string;
};

export type EvidenceCategorySummary = {
  category: string;
  item_count: number;
  complete: boolean;
  status: string;
  latest_revision?: string | null;
  latest_date?: string | null;
  missing: boolean;
};

export type BuildingLibraryIndexItem = {
  building_id: string;
  building_name: string;
  property_id?: string | null;
  property_name?: string | null;
  job_no?: string | null;
  passport_no?: string | null;
  total_evidence_items: number;
  passport_completion_percentage: number;
  closeout_readiness_state: string;
  last_updated?: string | null;
  missing_evidence_count: number;
  lifecycle_stage: "BUILD" | "ADVISE" | "PROTECT" | string;
  status: string;
  library_url: string;
  passport_url: string;
};

export type BuildingLibrary = {
  building: Building;
  property?: PropertyRecord | null;
  total_evidence_items: number;
  passport_completion_percentage: number;
  closeout_readiness_state: string;
  last_updated?: string | null;
  missing_evidence_count: number;
  lifecycle_stage: "BUILD" | "ADVISE" | "PROTECT" | string;
  categories: EvidenceCategorySummary[];
  documents: DocumentRecord[];
  missing_items: string[];
  closeout_score: CloseoutScore;
};

export type CloseoutSectionStatus = {
  key: string;
  label: string;
  status: string;
  completed: boolean;
  required: boolean;
  evidence_count: number;
  evidence_labels: string[];
  missing_reason?: string | null;
};

export type CloseoutScore = {
  completion_percentage: number;
  total_required_items: number;
  completed_items: number;
  missing_items: string[];
  ready_for_handover: boolean;
  warnings: string[];
  sections: CloseoutSectionStatus[];
};

export type PropertyCloseoutBuildingScore = {
  building_id: string;
  building_name: string;
  completion_percentage: number;
  completed_items: number;
  total_required_items: number;
  ready_for_handover: boolean;
  missing_items: string[];
};

export type PropertyCloseoutScore = CloseoutScore & {
  property_id: string;
  property_name: string;
  building_count: number;
  ready_building_count: number;
  buildings: PropertyCloseoutBuildingScore[];
};

export type FppScores = {
  protectionScore: number;
  complianceScore: number;
  readinessScore: number;
  intelligenceScore: number;
  buildingHealthIndex: number;
  scoreDrivers: string[];
  lastCalculatedAt: string;
  targetType: string;
  targetId?: string | null;
  buildingId?: string | null;
};

export type PortfolioBuildingScores = FppScores & {
  buildingName: string;
};

export type PortfolioScores = {
  protectionScore: number;
  complianceScore: number;
  readinessScore: number;
  intelligenceScore: number;
  buildingHealthIndex: number;
  scoreDrivers: string[];
  lastCalculatedAt: string;
  buildingCount: number;
  buildings: PortfolioBuildingScores[];
};

export type PropertyIntelligenceScore = {
  score: number;
  label: string;
  status: string;
  drivers: string[];
};

export type PropertyIntelligenceCount = {
  label: string;
  value: number;
  status: string;
};

export type PropertyBuildingIntelligence = {
  id: string;
  name: string;
  building_type?: string | null;
  bpid?: string | null;
  asset_count: number;
  document_count: number;
  passport_record_count: number;
  open_deficiency_count: number;
  overdue_work_order_count: number;
  readiness_status: string;
  health_score?: number | null;
};

export type PropertyIntelligenceFactor = {
  category: string;
  factor_key: string;
  label: string;
  severity: string;
  source_type?: string | null;
  source_id?: string | null;
  impact_score: number;
  metadata: Record<string, unknown>;
};

export type PropertyHealthSummary = {
  score: number;
  status: string;
  label: string;
  building_count: number;
  active_building_count: number;
  shared_infrastructure_count: number;
  drivers: string[];
  factors: PropertyIntelligenceFactor[];
};

export type PropertyConfidenceSummary = {
  score: number;
  status: string;
  label: string;
  addressed_building_count: number;
  assets_with_condition_count: number;
  documents_with_visibility_count: number;
  data_gap_count: number;
  drivers: string[];
  factors: PropertyIntelligenceFactor[];
};

export type PropertyRiskSummary = {
  score: number;
  status: string;
  label: string;
  open_deficiency_count: number;
  critical_or_high_deficiency_count: number;
  overdue_work_order_count: number;
  expired_document_count: number;
  poor_condition_asset_count: number;
  drivers: string[];
  factors: PropertyIntelligenceFactor[];
};

export type PropertyReadinessSummary = {
  score: number;
  status: string;
  label: string;
  ready_for_handover: boolean;
  checklist: Array<{ key?: string; label: string; complete: boolean }>;
  drivers: string[];
  factors: PropertyIntelligenceFactor[];
};

export type PropertyPassportSummary = {
  score: number;
  status: string;
  label: string;
  passport_records: number;
  client_visible_records: number;
  building_count: number;
  shared_infrastructure_count: number;
  completeness_score: number;
  drivers: string[];
  factors: PropertyIntelligenceFactor[];
};

export type PropertyCapitalSummary = {
  replacement_cost_estimate: number;
  near_term_asset_count: number;
  open_deficiency_count: number;
  planning_status: string;
  assets_missing_replacement_cost_count: number;
  by_building: Array<{
    building_id: string;
    building_name: string;
    replacement_cost_estimate: number;
    near_term_asset_count: number;
  }>;
};

export type PropertyDeficiencySummary = {
  open: number;
  critical_or_high: number;
  by_severity: Record<string, number>;
  by_status: Record<string, number>;
  by_building: Array<{
    building_id: string;
    building_name: string;
    open: number;
    critical_or_high: number;
  }>;
};

export type PropertyIntelligenceSnapshot = {
  id?: string | null;
  calculation_version: string;
  calculated_at: string;
  health_score: number;
  confidence_score: number;
  risk_score: number;
  readiness_score: number;
  passport_score: number;
};

export type PropertyIntelligence = {
  property: PropertyRecord;
  calculated_at: string;
  health: PropertyIntelligenceScore;
  confidence: PropertyIntelligenceScore;
  risk: PropertyIntelligenceScore;
  readiness: PropertyIntelligenceScore;
  passport: PropertyIntelligenceScore;
  executive_summary: string;
  counts: PropertyIntelligenceCount[];
  buildings: PropertyBuildingIntelligence[];
  health_summary?: PropertyHealthSummary | null;
  confidence_summary?: PropertyConfidenceSummary | null;
  risk_summary?: PropertyRiskSummary | null;
  readiness_summary?: PropertyReadinessSummary | null;
  passport_rollup?: PropertyPassportSummary | null;
  passport_summary: Record<string, unknown>;
  capital_summary: PropertyCapitalSummary;
  deficiency_summary: PropertyDeficiencySummary;
  readiness_checklist: Array<{ key?: string; label: string; complete: boolean }>;
  executive_review: Record<string, unknown>;
  latest_snapshot?: PropertyIntelligenceSnapshot | null;
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers);
  const isFormData = init?.body instanceof FormData;
  if (!isFormData && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${API_BASE_URL}/api/v1${path}`, {
    ...init,
    headers,
    cache: "no-store"
  });

  if (!response.ok) {
    let message = "Unable to complete request.";
    try {
      const body = (await response.json()) as FmsApiError;
      message = body.error?.message ?? message;
    } catch {
      message = response.statusText || message;
    }
    throw new Error(message);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export async function listOrganizations(): Promise<Organization[]> {
  const response = await request<ApiEnvelope<Organization[]>>("/organizations");
  return response.data;
}

export async function listBuildings(organizationId?: string): Promise<Building[]> {
  const suffix = organizationId ? `?organization_id=${organizationId}` : "";
  const response = await request<ApiEnvelope<Building[]>>(`/buildings${suffix}`);
  return response.data;
}

export async function globalSearch(query: string, type?: SearchResult["type"]): Promise<SearchResult[]> {
  const searchParams = new URLSearchParams();
  searchParams.set("q", query);
  if (type) {
    searchParams.set("type", type);
  }
  const response = await request<ApiEnvelope<SearchResult[]>>(`/search?${searchParams.toString()}`);
  return response.data;
}

export async function getPropertyCampusSummary(organizationId?: string): Promise<PropertyCampusSummary> {
  const suffix = organizationId ? `?organization_id=${organizationId}` : "";
  const response = await request<ApiEnvelope<PropertyCampusSummary>>(`/properties/summary${suffix}`);
  return response.data;
}

export async function listProperties(organizationId?: string): Promise<PropertyRecord[]> {
  const suffix = organizationId ? `?organization_id=${organizationId}` : "";
  const response = await request<ApiEnvelope<PropertyRecord[]>>(`/properties${suffix}`);
  return response.data;
}

export async function getProperty(propertyId: string): Promise<PropertyRecord> {
  const response = await request<ApiEnvelope<PropertyRecord>>(`/properties/${propertyId}`);
  return response.data;
}

export async function getPropertyIntelligence(propertyId: string): Promise<PropertyIntelligence> {
  const response = await request<ApiEnvelope<PropertyIntelligence>>(`/properties/${propertyId}/intelligence`);
  return response.data;
}

export async function createProperty(payload: PropertyPayload): Promise<PropertyRecord> {
  const response = await request<ApiEnvelope<PropertyRecord>>("/properties", {
    method: "POST",
    body: JSON.stringify(payload)
  });
  return response.data;
}

export async function listCampuses(params?: { organizationId?: string; propertyId?: string }): Promise<Campus[]> {
  const searchParams = new URLSearchParams();
  if (params?.organizationId) {
    searchParams.set("organization_id", params.organizationId);
  }
  if (params?.propertyId) {
    searchParams.set("property_id", params.propertyId);
  }
  const suffix = searchParams.toString() ? `?${searchParams.toString()}` : "";
  const response = await request<ApiEnvelope<Campus[]>>(`/campuses${suffix}`);
  return response.data;
}

export async function createCampus(payload: CampusPayload): Promise<Campus> {
  const response = await request<ApiEnvelope<Campus>>("/campuses", {
    method: "POST",
    body: JSON.stringify(payload)
  });
  return response.data;
}

export async function assignBuildingToPropertyCampus(
  buildingId: string,
  payload: { property_id?: string | null; campus_id?: string | null }
): Promise<Building> {
  const response = await request<ApiEnvelope<Building>>(`/buildings/${buildingId}/property-campus`, {
    method: "PATCH",
    body: JSON.stringify(payload)
  });
  return response.data;
}

export async function getBuilding(buildingId: string): Promise<Building> {
  const response = await request<ApiEnvelope<Building>>(`/buildings/${buildingId}`);
  return response.data;
}

export async function createBuilding(payload: BuildingPayload): Promise<Building> {
  const response = await request<ApiEnvelope<Building>>("/buildings", {
    method: "POST",
    body: JSON.stringify(payload)
  });
  return response.data;
}

export async function updateBuilding(buildingId: string, payload: Partial<BuildingPayload>): Promise<Building> {
  const response = await request<ApiEnvelope<Building>>(`/buildings/${buildingId}`, {
    method: "PATCH",
    body: JSON.stringify(payload)
  });
  return response.data;
}

export async function listBuildingContacts(buildingId: string): Promise<BuildingContact[]> {
  const response = await request<ApiEnvelope<BuildingContact[]>>(`/buildings/${buildingId}/contacts`);
  return response.data;
}

export async function createBuildingContact(
  buildingId: string,
  payload: BuildingContactPayload
): Promise<BuildingContact> {
  const response = await request<ApiEnvelope<BuildingContact>>(`/buildings/${buildingId}/contacts`, {
    method: "POST",
    body: JSON.stringify(payload)
  });
  return response.data;
}

export async function updateBuildingContact(
  contactId: string,
  payload: Partial<BuildingContactPayload>
): Promise<BuildingContact> {
  const response = await request<ApiEnvelope<BuildingContact>>(`/building-contacts/${contactId}`, {
    method: "PATCH",
    body: JSON.stringify(payload)
  });
  return response.data;
}

export async function deleteBuildingContact(contactId: string): Promise<void> {
  await request<void>(`/building-contacts/${contactId}`, {
    method: "DELETE"
  });
}

export async function listAssetTypes(): Promise<AssetType[]> {
  const response = await request<ApiEnvelope<AssetType[]>>("/asset-types");
  return response.data;
}

export async function listBuildingAssets(buildingId: string): Promise<Asset[]> {
  const response = await request<ApiEnvelope<Asset[]>>(`/buildings/${buildingId}/assets`);
  return response.data;
}

export async function createAsset(buildingId: string, payload: AssetPayload): Promise<Asset> {
  const response = await request<ApiEnvelope<Asset>>(`/buildings/${buildingId}/assets`, {
    method: "POST",
    body: JSON.stringify(payload)
  });
  return response.data;
}

export async function updateAsset(assetId: string, payload: Partial<AssetPayload>): Promise<Asset> {
  const response = await request<ApiEnvelope<Asset>>(`/assets/${assetId}`, {
    method: "PATCH",
    body: JSON.stringify(payload)
  });
  return response.data;
}

export async function deleteAsset(assetId: string): Promise<void> {
  await request<void>(`/assets/${assetId}`, {
    method: "DELETE"
  });
}

export async function listBuildingDocuments(buildingId: string): Promise<DocumentRecord[]> {
  const response = await request<ApiEnvelope<DocumentRecord[]>>(`/buildings/${buildingId}/documents`);
  return response.data;
}

export async function listBuildingLibraryIndex(organizationId?: string): Promise<BuildingLibraryIndexItem[]> {
  const suffix = organizationId ? `?organization_id=${organizationId}` : "";
  const response = await request<ApiEnvelope<BuildingLibraryIndexItem[]>>(`/documents/library${suffix}`);
  return response.data;
}

export async function getBuildingLibrary(buildingId: string): Promise<BuildingLibrary> {
  const response = await request<ApiEnvelope<BuildingLibrary>>(`/buildings/${buildingId}/library`);
  return response.data;
}

export async function uploadDocument(formData: FormData): Promise<DocumentRecord> {
  const response = await request<ApiEnvelope<DocumentRecord>>("/documents/upload", {
    method: "POST",
    body: formData
  });
  return response.data;
}

export async function uploadDocumentVersion(documentId: string, formData: FormData): Promise<DocumentRecord> {
  const response = await request<ApiEnvelope<DocumentRecord>>(`/documents/${documentId}/new-version`, {
    method: "POST",
    body: formData
  });
  return response.data;
}

export async function updateDocument(documentId: string, payload: Partial<DocumentMetadataPayload>): Promise<DocumentRecord> {
  const response = await request<ApiEnvelope<DocumentRecord>>(`/documents/${documentId}`, {
    method: "PATCH",
    body: JSON.stringify(payload)
  });
  return response.data;
}

export async function listDocumentAssetSuggestions(documentId: string): Promise<DocumentAssetSuggestion[]> {
  const response = await request<ApiEnvelope<DocumentAssetSuggestion[]>>(`/documents/${documentId}/asset-suggestions`);
  return response.data;
}

export async function approveDocumentAssetSuggestion(
  documentId: string,
  suggestionId: string,
  payload?: DocumentAssetSuggestionPayload
): Promise<DocumentAssetSuggestion> {
  const response = await request<ApiEnvelope<DocumentAssetSuggestion>>(`/documents/${documentId}/asset-suggestions/${suggestionId}/approve`, {
    method: "POST",
    body: JSON.stringify(payload ?? {})
  });
  return response.data;
}

export async function rejectDocumentAssetSuggestion(documentId: string, suggestionId: string): Promise<DocumentAssetSuggestion> {
  const response = await request<ApiEnvelope<DocumentAssetSuggestion>>(`/documents/${documentId}/asset-suggestions/${suggestionId}/reject`, {
    method: "POST"
  });
  return response.data;
}

export async function approveAllDocumentAssetSuggestions(documentId: string): Promise<DocumentAssetSuggestion[]> {
  const response = await request<ApiEnvelope<DocumentAssetSuggestion[]>>(`/documents/${documentId}/asset-suggestions/approve-all`, {
    method: "POST"
  });
  return response.data;
}

export async function archiveDocument(documentId: string): Promise<DocumentRecord> {
  const response = await request<ApiEnvelope<DocumentRecord>>(`/documents/${documentId}/archive`, {
    method: "POST"
  });
  return response.data;
}

export function getDocumentDownloadUrl(documentId: string): string {
  return `${API_BASE_URL}/api/v1/documents/${documentId}/download`;
}

export async function getPassport(buildingId: string): Promise<PassportSummary> {
  const response = await request<ApiEnvelope<PassportSummary>>(`/buildings/${buildingId}/passport`);
  return response.data;
}

export async function getProtectedState(buildingId: string): Promise<ProtectedStateEvaluation> {
  const response = await request<ApiEnvelope<ProtectedStateEvaluation>>(`/buildings/${buildingId}/protected-state`);
  return response.data;
}

export async function evaluateProtectedState(buildingId: string): Promise<ProtectedStateEvaluation> {
  const response = await request<ApiEnvelope<ProtectedStateEvaluation>>(`/buildings/${buildingId}/protected-state/evaluate`, {
    method: "POST"
  });
  return response.data;
}

export async function approveProtectedState(buildingId: string, reason?: string): Promise<ProtectedStateEvaluation> {
  const response = await request<ApiEnvelope<ProtectedStateEvaluation>>(`/buildings/${buildingId}/protected-state/approve`, {
    method: "POST",
    body: JSON.stringify({ reason })
  });
  return response.data;
}

export async function suspendProtectedState(buildingId: string, reason?: string): Promise<ProtectedStateEvaluation> {
  const response = await request<ApiEnvelope<ProtectedStateEvaluation>>(`/buildings/${buildingId}/protected-state/suspend`, {
    method: "POST",
    body: JSON.stringify({ reason })
  });
  return response.data;
}

export async function revokeProtectedState(buildingId: string, reason?: string): Promise<ProtectedStateEvaluation> {
  const response = await request<ApiEnvelope<ProtectedStateEvaluation>>(`/buildings/${buildingId}/protected-state/revoke`, {
    method: "POST",
    body: JSON.stringify({ reason })
  });
  return response.data;
}

export async function listPassportOnboardingQueue(organizationId?: string): Promise<PassportOnboardingQueueItem[]> {
  const suffix = organizationId ? `?organization_id=${organizationId}` : "";
  const response = await request<ApiEnvelope<PassportOnboardingQueueItem[]>>(`/passports/onboarding${suffix}`);
  return response.data;
}

export async function getBuildingCloseoutScore(buildingId: string): Promise<CloseoutScore> {
  const response = await request<ApiEnvelope<CloseoutScore>>(`/buildings/${buildingId}/closeout/score`);
  return response.data;
}

export async function getBuildingScores(buildingId: string): Promise<FppScores> {
  const response = await request<ApiEnvelope<FppScores>>(`/buildings/${buildingId}/scores`);
  return response.data;
}

export async function getBuildingHealthIndex(buildingId: string): Promise<FppScores> {
  const response = await request<ApiEnvelope<FppScores>>(`/buildings/${buildingId}/health-index`);
  return response.data;
}

export async function getPortfolioScores(organizationId?: string): Promise<PortfolioScores> {
  const suffix = organizationId ? `?organization_id=${organizationId}` : "";
  const response = await request<ApiEnvelope<PortfolioScores>>(`/portfolio/scores${suffix}`);
  return response.data;
}

export async function getProjectScores(projectId: string): Promise<FppScores> {
  const response = await request<ApiEnvelope<FppScores>>(`/projects/${projectId}/scores`);
  return response.data;
}

export async function getInspectionScores(inspectionId: string): Promise<FppScores> {
  const response = await request<ApiEnvelope<FppScores>>(`/inspections/${inspectionId}/scores`);
  return response.data;
}

export async function getCloseoutScores(closeoutId: string): Promise<FppScores> {
  const response = await request<ApiEnvelope<FppScores>>(`/closeout/${closeoutId}/scores`);
  return response.data;
}

export async function getPropertyCloseoutScore(propertyId: string): Promise<PropertyCloseoutScore> {
  const response = await request<ApiEnvelope<PropertyCloseoutScore>>(`/properties/${propertyId}/closeout/score`);
  return response.data;
}
