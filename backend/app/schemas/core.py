from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DataResponse(BaseModel):
    data: object


class ListResponse(BaseModel):
    data: list[object]


class OrganizationBase(BaseModel):
    name: str
    legal_name: str | None = None
    organization_type: str = "client"
    status: str = "active"
    phone: str | None = None
    email: str | None = None
    website: str | None = None
    address_line_1: str | None = None
    address_line_2: str | None = None
    city: str | None = None
    province_state: str | None = None
    postal_code: str | None = None
    country: str | None = "Canada"
    billing_contact_name: str | None = None
    billing_contact_email: str | None = None
    billing_contact_phone: str | None = None
    notes: str | None = None


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    name: str | None = None
    legal_name: str | None = None
    organization_type: str | None = None
    status: str | None = None
    phone: str | None = None
    email: str | None = None
    website: str | None = None
    address_line_1: str | None = None
    address_line_2: str | None = None
    city: str | None = None
    province_state: str | None = None
    postal_code: str | None = None
    country: str | None = None
    billing_contact_name: str | None = None
    billing_contact_email: str | None = None
    billing_contact_phone: str | None = None
    notes: str | None = None


class OrganizationRead(OrganizationBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserBase(BaseModel):
    auth_provider_user_id: str | None = None
    email: str
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    job_title: str | None = None
    status: str = "active"


class UserCreate(UserBase):
    pass


class UserInvite(BaseModel):
    organization_id: UUID
    email: str
    first_name: str | None = None
    last_name: str | None = None
    role: str


class UserUpdate(BaseModel):
    auth_provider_user_id: str | None = None
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    job_title: str | None = None
    status: str | None = None


class UserRead(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RoleRead(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    is_system_role: bool

    model_config = ConfigDict(from_attributes=True)


class OrganizationUserCreate(BaseModel):
    organization_id: UUID
    user_id: UUID
    role_id: UUID
    status: str = "active"


class OrganizationUserUpdate(BaseModel):
    status: str | None = None


class OrganizationUserRead(BaseModel):
    id: UUID
    organization_id: UUID
    user_id: UUID
    role_id: UUID
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PropertyBase(BaseModel):
    organization_id: UUID
    name: str
    property_type: str = "single_site"
    status: str = "active"
    address_line_1: str | None = None
    address_line_2: str | None = None
    city: str | None = None
    province_state: str | None = None
    postal_code: str | None = None
    country: str | None = "Canada"
    owner_name: str | None = None
    property_manager_name: str | None = None
    notes: str | None = None


class PropertyCreate(PropertyBase):
    pass


class PropertyUpdate(BaseModel):
    name: str | None = None
    property_type: str | None = None
    status: str | None = None
    address_line_1: str | None = None
    address_line_2: str | None = None
    city: str | None = None
    province_state: str | None = None
    postal_code: str | None = None
    country: str | None = None
    owner_name: str | None = None
    property_manager_name: str | None = None
    notes: str | None = None


class PropertyRead(PropertyBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    campus_count: int = 0
    building_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class CampusBase(BaseModel):
    organization_id: UUID
    property_id: UUID | None = None
    name: str
    campus_type: str = "campus"
    status: str = "active"
    address_line_1: str | None = None
    address_line_2: str | None = None
    city: str | None = None
    province_state: str | None = None
    postal_code: str | None = None
    country: str | None = "Canada"
    notes: str | None = None


class CampusCreate(CampusBase):
    pass


class CampusUpdate(BaseModel):
    property_id: UUID | None = None
    name: str | None = None
    campus_type: str | None = None
    status: str | None = None
    address_line_1: str | None = None
    address_line_2: str | None = None
    city: str | None = None
    province_state: str | None = None
    postal_code: str | None = None
    country: str | None = None
    notes: str | None = None


class CampusRead(CampusBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    building_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class BuildingAssignment(BaseModel):
    property_id: UUID | None = None
    campus_id: UUID | None = None


class PropertyCampusSummary(BaseModel):
    properties: int
    campuses: int
    assigned_buildings: int
    unassigned_buildings: int


class SearchResult(BaseModel):
    id: str
    type: str
    title: str
    subtitle: str
    matched_field: str
    url: str


class PropertyIntelligenceScore(BaseModel):
    score: int
    label: str
    status: str
    drivers: list[str] = []


class PropertyIntelligenceCount(BaseModel):
    label: str
    value: int | float
    status: str = "neutral"


class PropertyBuildingIntelligence(BaseModel):
    id: UUID
    name: str
    building_type: str | None = None
    bpid: str | None = None
    asset_count: int
    document_count: int
    passport_record_count: int
    open_deficiency_count: int
    overdue_work_order_count: int
    readiness_status: str


class PropertyIntelligenceFactorRead(BaseModel):
    category: str
    factor_key: str
    label: str
    severity: str = "info"
    source_type: str | None = None
    source_id: UUID | None = None
    impact_score: int = 0
    metadata: dict = Field(default_factory=dict)


class PropertyHealthSummary(BaseModel):
    score: int
    status: str
    label: str = "Property Health"
    building_count: int = 0
    active_building_count: int = 0
    shared_infrastructure_count: int = 0
    drivers: list[str] = Field(default_factory=list)
    factors: list[PropertyIntelligenceFactorRead] = Field(default_factory=list)


class PropertyConfidenceSummary(BaseModel):
    score: int
    status: str
    label: str = "Property Confidence Index"
    addressed_building_count: int = 0
    assets_with_condition_count: int = 0
    documents_with_visibility_count: int = 0
    data_gap_count: int = 0
    drivers: list[str] = Field(default_factory=list)
    factors: list[PropertyIntelligenceFactorRead] = Field(default_factory=list)


class PropertyRiskSummary(BaseModel):
    score: int
    status: str
    label: str = "Property Risk"
    open_deficiency_count: int = 0
    critical_or_high_deficiency_count: int = 0
    overdue_work_order_count: int = 0
    expired_document_count: int = 0
    poor_condition_asset_count: int = 0
    drivers: list[str] = Field(default_factory=list)
    factors: list[PropertyIntelligenceFactorRead] = Field(default_factory=list)


class PropertyReadinessSummary(BaseModel):
    score: int
    status: str
    label: str = "Property Readiness"
    ready_for_handover: bool = False
    checklist: list[dict] = Field(default_factory=list)
    drivers: list[str] = Field(default_factory=list)
    factors: list[PropertyIntelligenceFactorRead] = Field(default_factory=list)


class PropertyPassportSummary(BaseModel):
    score: int
    status: str
    label: str = "Property Passport"
    passport_records: int = 0
    client_visible_records: int = 0
    building_count: int = 0
    shared_infrastructure_count: int = 0
    completeness_score: int = 0
    drivers: list[str] = Field(default_factory=list)
    factors: list[PropertyIntelligenceFactorRead] = Field(default_factory=list)


class PropertyCapitalSummary(BaseModel):
    replacement_cost_estimate: float = 0
    near_term_asset_count: int = 0
    open_deficiency_count: int = 0
    planning_status: str = "placeholder"
    assets_missing_replacement_cost_count: int = 0
    by_building: list[dict] = Field(default_factory=list)


class PropertyDeficiencySummary(BaseModel):
    open: int = 0
    critical_or_high: int = 0
    by_severity: dict[str, int] = Field(default_factory=dict)
    by_status: dict[str, int] = Field(default_factory=dict)
    by_building: list[dict] = Field(default_factory=list)


class PropertyIntelligenceSnapshotRead(BaseModel):
    id: UUID | None = None
    calculation_version: str = "m7-001"
    calculated_at: datetime
    health_score: int
    confidence_score: int
    risk_score: int
    readiness_score: int
    passport_score: int


class PropertyIntelligenceRead(BaseModel):
    property: PropertyRead
    calculated_at: datetime
    health: PropertyIntelligenceScore
    confidence: PropertyIntelligenceScore
    risk: PropertyIntelligenceScore
    readiness: PropertyIntelligenceScore
    passport: PropertyIntelligenceScore
    executive_summary: str
    counts: list[PropertyIntelligenceCount]
    buildings: list[PropertyBuildingIntelligence]
    health_summary: PropertyHealthSummary | None = None
    confidence_summary: PropertyConfidenceSummary | None = None
    risk_summary: PropertyRiskSummary | None = None
    readiness_summary: PropertyReadinessSummary | None = None
    passport_rollup: PropertyPassportSummary | None = None
    passport_summary: dict
    capital_summary: PropertyCapitalSummary
    deficiency_summary: PropertyDeficiencySummary
    readiness_checklist: list[dict]
    executive_review: dict
    latest_snapshot: PropertyIntelligenceSnapshotRead | None = None


class BuildingBase(BaseModel):
    organization_id: UUID
    name: str
    code: str | None = None
    address_line_1: str
    address_line_2: str | None = None
    city: str
    province_state: str
    postal_code: str | None = None
    country: str = "Canada"
    latitude: float | None = None
    longitude: float | None = None
    building_type: str
    occupancy_classification: str | None = None
    construction_year: int | None = None
    number_of_storeys: int | None = Field(default=None, ge=0)
    total_area_sq_ft: float | None = Field(default=None, ge=0)
    owner_name: str | None = None
    property_manager_name: str | None = None
    fire_department: str | None = None
    ahj_name: str | None = None
    insurance_provider: str | None = None
    status: str = "active"
    project_classification: str | None = None
    passport_eligible: bool = False
    passport_status: str = "Not Started"
    passport_issue_date: date | None = None
    passport_version: str | None = None
    client_handover_status: str | None = None
    notes: str | None = None


class BuildingCreate(BuildingBase):
    pass


class BuildingUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    address_line_1: str | None = None
    address_line_2: str | None = None
    city: str | None = None
    province_state: str | None = None
    postal_code: str | None = None
    country: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    building_type: str | None = None
    occupancy_classification: str | None = None
    construction_year: int | None = None
    number_of_storeys: int | None = Field(default=None, ge=0)
    total_area_sq_ft: float | None = Field(default=None, ge=0)
    owner_name: str | None = None
    property_manager_name: str | None = None
    fire_department: str | None = None
    ahj_name: str | None = None
    insurance_provider: str | None = None
    status: str | None = None
    project_classification: str | None = None
    passport_eligible: bool | None = None
    passport_status: str | None = None
    passport_issue_date: date | None = None
    passport_version: str | None = None
    client_handover_status: str | None = None
    notes: str | None = None


class BuildingRead(BuildingBase):
    id: UUID
    property_id: UUID | None = None
    campus_id: UUID | None = None
    bpid: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProtectedStateAction(BaseModel):
    reason: str | None = None
    notes: str | None = None


class ProtectedStateCriterion(BaseModel):
    key: str
    label: str
    status: str
    message: str


class ProtectedStateCertificationRead(BaseModel):
    id: UUID
    organization_id: UUID
    building_id: UUID
    property_id: UUID | None = None
    status: str
    evaluation_version: str
    evaluated_at: datetime | None = None
    evaluated_by: str | None = None
    approved_at: datetime | None = None
    approved_by: str | None = None
    suspended_at: datetime | None = None
    revoked_at: datetime | None = None
    reason: str | None = None
    notes: str | None = None
    criteria_snapshot: dict | None = None

    model_config = ConfigDict(from_attributes=True)


class ProtectedStateEvaluationRead(BaseModel):
    building_id: UUID
    protected_state_status: str
    halo_eligible: bool
    criteria_total: int
    criteria_passed: int
    criteria_failed: int
    criteria_unknown: int
    criteria: list[ProtectedStateCriterion] = Field(default_factory=list)
    blocking_items: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    evaluated_at: datetime
    evaluation_version: str
    certification_record_id: UUID | None = None
    approved_at: datetime | None = None
    approved_by: str | None = None


class PassportOnboardingQueueItem(BaseModel):
    project: str
    property: str | None = None
    building_id: UUID
    building: str
    job_no: str | None = None
    passport_no: str | None = None
    project_classification: str
    completion_status: str
    closeout_score: int
    missing_items: list[str] = Field(default_factory=list)
    passport_eligible: bool
    passport_status: str
    passport_issue_date: date | None = None
    passport_version: str | None = None
    client_handover_status: str | None = None
    protected_state_status: str = "review_required"
    halo_eligible: bool = False
    next_action: str
    closeout_url: str
    passport_url: str


class SohoReadinessCategory(BaseModel):
    key: str
    label: str
    status: str
    evidence_count: int = 0
    missing_reason: str | None = None


class SohoReadinessHandover(BaseModel):
    owner_property_manager_recipient: str | None = None
    delivery_status: str | None = None
    delivery_date: date | None = None
    portal_access_status: str = "Not Configured"
    notes: str | None = None
    next_itm_action: str
    client_visible_evidence_count: int = 0
    passport_version: str | None = None


class SohoReadinessRecord(BaseModel):
    role: str
    label: str
    building: BuildingRead | None = None
    expected: bool = True
    present: bool = False
    duplicate_count: int = 0
    completion_status: str
    closeout_score: int = 0
    documents_count: int = 0
    passport_record_count: int = 0
    client_visible_evidence_count: int = 0
    assets_count: int = 0
    asset_suggestions_pending: int = 0
    asset_suggestions_approved: int = 0
    contacts_count: int = 0
    missing_items: list[str] = Field(default_factory=list)
    evidence_categories: list[SohoReadinessCategory] = Field(default_factory=list)
    passport_status: str = "Not Started"
    passport_eligible: bool = False
    protected_state_status: str = "review_required"
    halo_eligible: bool = False
    readiness_state: str = "Not Ready"
    next_action: str
    library_url: str | None = None
    passport_url: str | None = None
    protected_state_url: str | None = None
    handover: SohoReadinessHandover | None = None


class SohoPassportReadinessRead(BaseModel):
    property: PropertyRead
    readiness_state: str
    closeout_score: int = 0
    expected_records: int = 0
    records_present: int = 0
    duplicate_records: int = 0
    evidence_categories_complete: int = 0
    evidence_categories_missing: int = 0
    client_visible_evidence_count: int = 0
    passport_status: str = "Not Started"
    protected_state_status: str = "review_required"
    blocking_items: list[str] = Field(default_factory=list)
    missing_items: list[str] = Field(default_factory=list)
    next_action: str
    records: list[SohoReadinessRecord] = Field(default_factory=list)


class EvidenceCategorySummary(BaseModel):
    category: str
    item_count: int = 0
    complete: bool = False
    status: str = "Missing"
    latest_revision: str | None = None
    latest_date: datetime | None = None
    missing: bool = True


class BuildingLibraryIndexItem(BaseModel):
    building_id: UUID
    building_name: str
    property_id: UUID | None = None
    property_name: str | None = None
    job_no: str | None = None
    passport_no: str | None = None
    total_evidence_items: int = 0
    passport_completion_percentage: int = 0
    closeout_readiness_state: str
    last_updated: datetime | None = None
    missing_evidence_count: int = 0
    lifecycle_stage: str
    status: str
    library_url: str
    passport_url: str


class BuildingLibraryRead(BaseModel):
    building: BuildingRead
    property: PropertyRead | None = None
    total_evidence_items: int = 0
    passport_completion_percentage: int = 0
    closeout_readiness_state: str
    last_updated: datetime | None = None
    missing_evidence_count: int = 0
    lifecycle_stage: str
    categories: list[EvidenceCategorySummary] = Field(default_factory=list)
    documents: list["DocumentRead"] = Field(default_factory=list)
    missing_items: list[str] = Field(default_factory=list)
    closeout_score: "CloseoutScore"


class BuildingContactBase(BaseModel):
    contact_type: str
    name: str
    company: str | None = None
    job_title: str | None = None
    email: str | None = None
    phone: str | None = None
    mobile: str | None = None
    is_primary: bool = False
    is_emergency_contact: bool = False
    notes: str | None = None


class BuildingContactCreate(BuildingContactBase):
    pass


class BuildingContactUpdate(BaseModel):
    contact_type: str | None = None
    name: str | None = None
    company: str | None = None
    job_title: str | None = None
    email: str | None = None
    phone: str | None = None
    mobile: str | None = None
    is_primary: bool | None = None
    is_emergency_contact: bool | None = None
    notes: str | None = None


class BuildingContactRead(BuildingContactBase):
    id: UUID
    organization_id: UUID
    building_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AssetTypeRead(BaseModel):
    id: UUID
    name: str
    code: str
    category: str | None = None
    description: str | None = None
    default_inspection_frequency_months: int | None = None

    model_config = ConfigDict(from_attributes=True)


class AssetBase(BaseModel):
    asset_type_id: UUID
    name: str
    asset_tag: str | None = None
    location_description: str | None = None
    manufacturer: str | None = None
    model: str | None = None
    serial_number: str | None = None
    status: str = "active"
    installation_date: date | None = None
    warranty_expiry_date: date | None = None
    condition_rating: str | None = None
    inspection_frequency_months: int | None = Field(default=None, ge=0)
    last_inspected_at: datetime | None = None
    next_inspection_due_at: datetime | None = None
    replacement_cost_estimate: float | None = Field(default=None, ge=0)
    remaining_useful_life_years: int | None = None
    notes: str | None = None


class AssetCreate(AssetBase):
    pass


class AssetUpdate(BaseModel):
    asset_type_id: UUID | None = None
    name: str | None = None
    asset_tag: str | None = None
    location_description: str | None = None
    manufacturer: str | None = None
    model: str | None = None
    serial_number: str | None = None
    status: str | None = None
    installation_date: date | None = None
    warranty_expiry_date: date | None = None
    condition_rating: str | None = None
    inspection_frequency_months: int | None = Field(default=None, ge=0)
    last_inspected_at: datetime | None = None
    next_inspection_due_at: datetime | None = None
    replacement_cost_estimate: float | None = Field(default=None, ge=0)
    remaining_useful_life_years: int | None = None
    notes: str | None = None


class AssetRead(AssetBase):
    id: UUID
    organization_id: UUID
    building_id: UUID
    source_document_id: UUID | None = None
    created_at: datetime
    updated_at: datetime
    asset_type: AssetTypeRead | None = None

    model_config = ConfigDict(from_attributes=True)


class DocumentBase(BaseModel):
    document_type: str
    title: str
    description: str | None = None
    property_id: UUID | None = None
    asset_id: UUID | None = None
    evidence_category: str | None = None
    drawing_number: str | None = None
    revision: str | None = None
    issue_date: date | None = None
    status: str = "draft"
    effective_date: date | None = None
    expiry_date: date | None = None
    is_public_to_client: bool = False
    is_passport_record: bool = False
    internal_only: bool = True
    notes: str | None = None


class DocumentCreate(DocumentBase):
    original_filename: str | None = None
    storage_bucket: str | None = None
    storage_key: str | None = None
    file_mime_type: str | None = None
    file_size_bytes: int | None = None


class DocumentUpdate(BaseModel):
    document_type: str | None = None
    title: str | None = None
    description: str | None = None
    property_id: UUID | None = None
    building_id: UUID | None = None
    asset_id: UUID | None = None
    evidence_category: str | None = None
    drawing_number: str | None = None
    revision: str | None = None
    issue_date: date | None = None
    status: str | None = None
    effective_date: date | None = None
    expiry_date: date | None = None
    is_public_to_client: bool | None = None
    is_passport_record: bool | None = None
    internal_only: bool | None = None
    notes: str | None = None


class DocumentRead(DocumentBase):
    id: UUID
    organization_id: UUID
    building_id: UUID | None = None
    original_filename: str | None = None
    storage_bucket: str | None = None
    storage_key: str | None = None
    file_mime_type: str | None = None
    file_size_bytes: int | None = None
    version_number: int
    parent_document_id: UUID | None = None
    generated_by_system: bool
    extraction_status: str = "pending"
    extraction_source: str | None = None
    extraction_summary: dict | None = None
    archived_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentAssetSuggestionUpdate(BaseModel):
    suggested_asset_type: str | None = None
    suggested_name: str | None = None
    location_description: str | None = None
    manufacturer: str | None = None
    model: str | None = None
    notes: str | None = None


class DocumentAssetSuggestionRead(BaseModel):
    id: UUID
    organization_id: UUID
    document_id: UUID
    building_id: UUID | None = None
    asset_type_id: UUID | None = None
    approved_asset_id: UUID | None = None
    suggested_asset_type: str
    suggested_name: str
    location_description: str | None = None
    manufacturer: str | None = None
    model: str | None = None
    confidence: int
    evidence_snippet: str | None = None
    extraction_source: str = "rule_based"
    review_status: str
    reviewed_at: datetime | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PassportTimelineItem(BaseModel):
    event_type: str
    label: str
    occurred_at: datetime
    record_id: UUID


class PassportSummary(BaseModel):
    building: BuildingRead
    contacts: list[BuildingContactRead]
    assets: list[AssetRead]
    documents: list[DocumentRead]
    timeline: list[PassportTimelineItem]
    health_score: dict
    membership: dict


class CloseoutSectionStatus(BaseModel):
    key: str
    label: str
    status: str
    completed: bool
    required: bool = True
    evidence_count: int = 0
    evidence_labels: list[str] = Field(default_factory=list)
    missing_reason: str | None = None


class CloseoutScore(BaseModel):
    completion_percentage: int
    total_required_items: int
    completed_items: int
    missing_items: list[str]
    ready_for_handover: bool
    warnings: list[str] = Field(default_factory=list)
    sections: list[CloseoutSectionStatus]


class PropertyCloseoutBuildingScore(BaseModel):
    building_id: UUID
    building_name: str
    completion_percentage: int
    completed_items: int
    total_required_items: int
    ready_for_handover: bool
    missing_items: list[str] = Field(default_factory=list)


class PropertyCloseoutScore(CloseoutScore):
    property_id: UUID
    property_name: str
    building_count: int
    ready_building_count: int
    buildings: list[PropertyCloseoutBuildingScore] = Field(default_factory=list)
