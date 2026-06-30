export const buildingTypes = [
  { key: "commercial", label: "Commercial" },
  { key: "industrial", label: "Industrial" },
  { key: "institutional", label: "Institutional" },
  { key: "residential", label: "Residential" },
  { key: "mixed_use", label: "Mixed Use" },
  { key: "long_term_care", label: "Long-Term Care" },
  { key: "school", label: "School" },
  { key: "office", label: "Office" },
  { key: "retail", label: "Retail" },
  { key: "warehouse", label: "Warehouse" },
  { key: "other", label: "Other" }
];

export const buildingStatuses = [
  { key: "active", label: "Active" },
  { key: "inactive", label: "Inactive" }
];

export const buildingContactTypes = [
  { key: "owner", label: "Owner" },
  { key: "property_manager", label: "Property Manager" },
  { key: "site_contact", label: "Site Contact" },
  { key: "emergency_contact", label: "Emergency Contact" },
  { key: "billing", label: "Billing" },
  { key: "insurance", label: "Insurance" },
  { key: "engineer", label: "Engineer" },
  { key: "contractor", label: "Contractor" },
  { key: "ahj", label: "AHJ" },
  { key: "fire_department", label: "Fire Department" },
  { key: "other", label: "Other" }
];

export function formatControlledValue(value?: string | null) {
  if (!value) {
    return "";
  }

  return value
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}
