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

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}/api/v1${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {})
    },
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
