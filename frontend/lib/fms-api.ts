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
  bpid: string;
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
  notes?: string | null;
};

export type BuildingPayload = Omit<Building, "id" | "bpid">;

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
  building_id: string;
  asset_id?: string | null;
  document_type: string;
  title: string;
  description?: string | null;
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
  created_at: string;
  updated_at: string;
};

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

export async function updateDocument(documentId: string, payload: Partial<DocumentRecord>): Promise<DocumentRecord> {
  const response = await request<ApiEnvelope<DocumentRecord>>(`/documents/${documentId}`, {
    method: "PATCH",
    body: JSON.stringify(payload)
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
