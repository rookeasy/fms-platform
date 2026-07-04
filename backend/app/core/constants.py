ORGANIZATION_TYPES = {
    "platform",
    "contractor",
    "owner",
    "property_manager",
    "developer",
    "institution",
    "consultant",
    "insurance",
    "ahj",
    "client",
    "other",
}

USER_STATUSES = {"invited", "active", "suspended", "disabled", "deleted"}
BUILDING_STATUSES = {"active", "completed_occupied", "inactive", "archived"}
ORGANIZATION_USER_STATUSES = {"invited", "active", "suspended", "disabled", "deleted"}

USER_ROLES = {
    "platform_admin",
    "organization_admin",
    "property_manager",
    "building_owner",
    "technician",
    "engineer",
    "readonly_viewer",
    "ahj_viewer",
}

BUILDING_CONTACT_TYPES = {
    "owner",
    "property_manager",
    "site_contact",
    "emergency_contact",
    "billing",
    "insurance",
    "engineer",
    "contractor",
    "ahj",
    "fire_department",
    "other",
}

ASSET_CATEGORIES = {
    "sprinkler",
    "standpipe",
    "fire_pump",
    "water_supply",
    "backflow",
    "fire_alarm",
    "suppression",
    "life_safety",
    "valve",
    "hydrant",
    "documentation",
    "other",
}

ASSET_STATUSES = {"active", "inactive", "out_of_service", "impaired", "removed", "replaced", "unknown"}
ASSET_CONDITION_RATINGS = {"excellent", "good", "fair", "poor", "critical", "unknown"}

DOCUMENT_TYPES = {
    "drawing",
    "hydraulic_calculation",
    "shop_drawing",
    "as_built_drawing",
    "permit",
    "engineering_letter",
    "inspection_report",
    "deficiency_report",
    "building_health_report",
    "annual_executive_review",
    "certificate",
    "building_protection_certificate",
    "material_test_certificate",
    "contractors_material_test_certificate",
    "backflow_test_report",
    "fire_pump_test_report",
    "sprinkler_test_report",
    "standpipe_test_report",
    "alarm_verification_report",
    "impairment_notice",
    "shutdown_notice",
    "quote",
    "invoice",
    "purchase_order",
    "work_order",
    "photo",
    "video",
    "manufacturer_data",
    "warranty",
    "owner_manual",
    "service_record",
    "passport_export",
    "other",
}

FILE_VISIBILITY_VALUES = {"internal_only", "client_visible", "passport_record", "public_verification"}

BUILDING_CREATED = "building_created"
BUILDING_UPDATED = "building_updated"
ASSET_CREATED = "asset_created"
ASSET_UPDATED = "asset_updated"
DOCUMENT_UPLOADED = "document_uploaded"
DOCUMENT_UPDATED = "document_updated"
