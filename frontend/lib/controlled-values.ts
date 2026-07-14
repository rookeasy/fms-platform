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

export const assetStatuses = [
  { key: "active", label: "Active" },
  { key: "inactive", label: "Inactive" },
  { key: "out_of_service", label: "Out of Service" },
  { key: "impaired", label: "Impaired" },
  { key: "removed", label: "Removed" },
  { key: "replaced", label: "Replaced" },
  { key: "unknown", label: "Unknown" }
];

export const assetConditionRatings = [
  { key: "excellent", label: "Excellent" },
  { key: "good", label: "Good" },
  { key: "fair", label: "Fair" },
  { key: "poor", label: "Poor" },
  { key: "critical", label: "Critical" },
  { key: "unknown", label: "Unknown" }
];

export const documentTypes = [
  { key: "drawing", label: "Drawing" },
  { key: "hydraulic_calculation", label: "Hydraulic Calculation" },
  { key: "shop_drawing", label: "Shop Drawing" },
  { key: "as_built_drawing", label: "As-Built Drawing" },
  { key: "permit", label: "Permit" },
  { key: "engineering_letter", label: "Engineering Letter" },
  { key: "inspection_report", label: "Inspection Report" },
  { key: "deficiency_report", label: "Deficiency Report" },
  { key: "building_health_report", label: "Building Health Report" },
  { key: "annual_executive_review", label: "Annual Executive Review" },
  { key: "certificate", label: "Certificate" },
  { key: "building_protection_certificate", label: "Building Protection Certificate" },
  { key: "material_test_certificate", label: "Material Test Certificate" },
  { key: "contractors_material_test_certificate", label: "Contractor's Material and Test Certificate" },
  { key: "backflow_test_report", label: "Backflow Test Report" },
  { key: "fire_pump_test_report", label: "Fire Pump Test Report" },
  { key: "sprinkler_test_report", label: "Sprinkler Test Report" },
  { key: "standpipe_test_report", label: "Standpipe Test Report" },
  { key: "alarm_verification_report", label: "Fire Alarm Verification Report" },
  { key: "impairment_notice", label: "Impairment Notice" },
  { key: "shutdown_notice", label: "Shutdown Notice" },
  { key: "quote", label: "Quote" },
  { key: "invoice", label: "Invoice" },
  { key: "purchase_order", label: "Purchase Order" },
  { key: "work_order", label: "Work Order" },
  { key: "photo", label: "Photo" },
  { key: "video", label: "Video" },
  { key: "manufacturer_data", label: "Manufacturer Data" },
  { key: "warranty", label: "Warranty" },
  { key: "owner_manual", label: "Owner Manual" },
  { key: "service_record", label: "Service Record" },
  { key: "passport_export", label: "Passport Export" },
  { key: "other", label: "Other" }
];

export const evidenceCategories = [
  "Building Protection Passport",
  "Drawings",
  "As-Built Drawings",
  "P.Eng. Compliance",
  "NFPA Contractor Compliance",
  "Material & Test Certificates",
  "Asset Register",
  "Warranty",
  "Product Data",
  "O&M Manuals",
  "Photos",
  "Handover",
  "ITM Transition",
  "Membership",
  "Other"
];

export const documentStatuses = [
  { key: "draft", label: "Draft" },
  { key: "accepted", label: "Accepted" },
  { key: "as-built", label: "As-Built" },
  { key: "superseded", label: "Superseded" },
  { key: "archived", label: "Archived" }
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
