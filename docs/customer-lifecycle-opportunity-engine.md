# FMS-0024 Customer Lifecycle & Building Opportunity Engine

FMS-0024 defines the future Customer Lifecycle & Building Opportunity Engine for FMS. This is a specification only; it does not introduce schema, API, frontend, automation, CRM, or workflow code.

## Purpose

The Customer Lifecycle & Building Opportunity Engine will help Fuzion Fire convert completed prime-contract work into long-term service relationships. It treats each building as a living account context, not a one-time project record.

The engine should help internal teams identify, prioritize, and track lifecycle opportunities for:

- Inspection, Testing, and Maintenance contracts
- FMS memberships
- Building Protection Passport adoption
- Advisory reviews
- Capital planning
- Retrofit and modernization planning
- Client retention and relationship expansion

## Strategic Concept

Every prime contract completed by Fuzion Fire should be loaded into FMS as a reference building and treated as a lifecycle sales lead for ITM service, FMS membership, and future advisory opportunities.

The strategic idea is simple: a completed project creates trusted building knowledge. FMS should preserve that knowledge, expose it to the right internal teams, and turn it into structured follow-up opportunities without relying on memory, spreadsheets, or disconnected CRM notes.

FMS should become the bridge between project delivery and recurring customer relationships.

## Lifecycle Flow

1. Prime contract is completed by Fuzion Fire.
2. Building is added or confirmed in FMS.
3. Core building profile, contacts, assets, document metadata, and Passport-ready records are captured.
4. The building receives lifecycle status badges.
5. Opportunity records are created or suggested for ITM, membership, advisory, and capital planning paths.
6. Internal owners review, qualify, and advance opportunities.
7. Converted opportunities become active service relationships, memberships, or advisory engagements.
8. Ongoing service activity refreshes lifecycle KPIs and future opportunity signals.

## Lifecycle Stages

- `prime_contract_identified`: A Fuzion Fire prime contract has been identified as a candidate building record.
- `reference_building_created`: Building profile exists in FMS with initial project context.
- `passport_ready`: Core building, asset, contact, and document metadata is sufficient for Passport demonstration or client onboarding.
- `itm_lead`: Building is a candidate for recurring inspection, testing, and maintenance service.
- `itm_proposed`: ITM scope or proposal is in progress.
- `itm_converted`: ITM service relationship has been won.
- `membership_candidate`: Building is a candidate for FMS membership.
- `membership_proposed`: Membership offer has been presented or prepared.
- `membership_active`: Building or client has an active FMS membership.
- `advisory_candidate`: Building has known complexity, aging systems, deficiencies, capital risk, or owner interest.
- `advisory_active`: Advisory or capital planning engagement is active.
- `relationship_active`: Building has at least one active recurring or advisory relationship.
- `relationship_dormant`: Building has no active follow-up or recent engagement.
- `archived`: Building is no longer part of active lifecycle tracking.

## Building Opportunity Types

- `itm_service_contract`: Recurring inspection, testing, and maintenance agreement.
- `fms_membership`: Subscription or membership relationship tied to FMS value.
- `passport_onboarding`: Client-facing Building Protection Passport onboarding.
- `advisory_review`: Engineering, risk, compliance, or building protection advisory review.
- `capital_planning`: Budgeting and sequencing for major repairs, replacements, or upgrades.
- `retrofit_modernization`: System modernization, expansion, or code-driven retrofit.
- `deficiency_repair_program`: Bundled correction of known deficiencies or risk items.
- `document_digitization`: Conversion of drawings, certificates, reports, and records into structured Passport metadata.
- `owner_training`: Building owner, manager, or facilities team enablement.
- `multi_building_expansion`: Expansion from one building relationship into a portfolio relationship.

## Opportunity Statuses

- `suggested`: System or internal rule has identified a possible opportunity.
- `new`: Opportunity has been created and awaits review.
- `qualified`: Internal owner has confirmed the opportunity is worth pursuing.
- `nurture`: Opportunity is valid but not ready for active pursuit.
- `proposal_needed`: Scope, pricing, or proposal package is needed.
- `proposal_sent`: Proposal has been delivered to the client.
- `negotiation`: Client is reviewing, discussing, or requesting changes.
- `won`: Opportunity converted.
- `lost`: Opportunity was declined or awarded elsewhere.
- `deferred`: Client or internal team has paused the opportunity for a known reason.
- `closed_no_action`: Opportunity should not be pursued.

## Core Business Rules

- Every completed Fuzion Fire prime contract should be evaluated for creation as a reference building in FMS.
- The engine must not create duplicate building records when a building already exists.
- The engine should reuse existing organizations, contacts, assets, documents, and relationship records when reliable matches exist.
- Real client data must not be overwritten by inferred lifecycle data.
- Lifecycle stages should be derived from explicit records where possible, not only free-text notes.
- A building can have multiple active opportunity types at the same time.
- Opportunity status changes should be auditable.
- Client-visible Passport records should be distinct from internal-only opportunity records.
- A won ITM opportunity should update relationship status without automatically creating work orders or inspections.
- A won membership opportunity should update membership lifecycle status without automatically creating billing or auth changes.
- Advisory and capital planning opportunities should remain separate from deficiencies unless a later phase explicitly links them.
- Lost and closed opportunities should preserve history for reporting and future analysis.

## Customer Lifecycle KPIs

- Prime contracts loaded into FMS
- Percent of completed prime contracts converted to reference buildings
- Reference buildings with Passport-ready metadata
- Reference buildings with active ITM opportunities
- Prime-contract-to-ITM conversion rate
- Prime-contract-to-membership conversion rate
- Time from project completion to first lifecycle follow-up
- Open opportunity count by stage and owner
- Opportunity win rate by building type
- Opportunity value by type
- Buildings with dormant relationship status
- Buildings missing primary contact, asset, or document metadata
- Portfolio expansion opportunities by client organization

## Building Lifetime Value Concept

Building lifetime value is the estimated long-term commercial value of a building relationship across service, membership, advisory, and capital planning opportunities.

Future FMS phases should calculate or display building lifetime value using factors such as:

- Completed prime contract value
- Expected annual ITM value
- FMS membership value
- Advisory engagement potential
- Capital planning or retrofit potential
- Number of related buildings under the same owner or manager
- Relationship age and engagement history
- Risk complexity and asset density
- Probability of conversion by opportunity type

Initial versions may use simple manual estimates. Later versions may support weighted scoring, CRM deal values, historical conversion rates, and portfolio-level forecasting.

## Relationship Status Badges

FMS should show clear internal relationship badges on building and organization views:

- `Prime Contract Complete`
- `Reference Building`
- `Passport Ready`
- `ITM Lead`
- `ITM Proposed`
- `ITM Active`
- `Membership Candidate`
- `Membership Active`
- `Advisory Candidate`
- `Capital Planning Candidate`
- `Dormant Relationship`
- `Strategic Account`
- `Portfolio Expansion`

Badges should be internal by default unless a later phase explicitly exposes client-facing relationship indicators.

## Prime-Contract-to-Service Conversion Workflow

1. Project is completed.
2. Building is added to FMS or matched to an existing building.
3. Prime contract context is captured as internal notes and reference metadata.
4. Required contacts, assets, and document metadata are reviewed.
5. Building is tagged as `Reference Building`.
6. ITM service opportunity is created as `suggested` or `new`.
7. Internal owner qualifies the opportunity.
8. Proposal package is prepared.
9. Opportunity is marked `won`, `lost`, `deferred`, or `nurture`.
10. If won, relationship status changes to `ITM Active`.

## ITM Contract Conversion Workflow

1. Building is identified as an ITM candidate.
2. Existing asset and document metadata are reviewed.
3. Service scope is drafted from known systems and building risk.
4. Internal owner confirms decision-maker and timing.
5. ITM opportunity moves to `qualified`.
6. Proposal is generated outside or inside a future FMS workflow.
7. Opportunity moves through proposal, negotiation, and final status.
8. If won, FMS records the conversion and updates lifecycle KPIs.

FMS-0024 does not implement inspections, inspection templates, work orders, or service schedules.

## FMS Membership Conversion Workflow

1. Building has enough profile, contact, asset, and document metadata to demonstrate FMS value.
2. Membership opportunity is created or suggested.
3. Internal team selects the appropriate membership offer.
4. Client value is framed around Passport access, visibility, record continuity, and lifecycle support.
5. Opportunity is presented and tracked.
6. If won, relationship status changes to `Membership Active`.

FMS-0024 does not implement billing, subscription management, auth changes, or membership provisioning.

## Advisory/Capital Planning Opportunity Workflow

1. Building is flagged due to complexity, age, asset mix, known risk, document gaps, or strategic account value.
2. Advisory or capital planning opportunity is created.
3. Internal owner defines the advisory question or planning scope.
4. Supporting records are reviewed: assets, drawings, reports, Passport metadata, and service history when available.
5. Client conversation is planned.
6. Opportunity advances through qualification, proposal, and final outcome.
7. If won, future advisory deliverables may be linked to building records in later phases.

FMS-0024 does not implement reports, certificates, AI workflows, or capital planning modules.

## Internal Fuzion Fire Use Case

Fuzion Fire can use this engine to preserve project knowledge after construction or contract completion. A project that once lived in drawings, emails, and team memory becomes a structured building record with contacts, assets, documents, Passport readiness, and follow-up opportunities.

Sales, operations, leadership, and service teams should be able to answer:

- Which completed prime contracts have not been followed up for ITM?
- Which reference buildings are ready for a Passport demo?
- Which clients have multiple buildings and portfolio expansion potential?
- Which buildings have the strongest membership fit?
- Which buildings should receive advisory or capital planning attention?
- Which opportunities are stalled, dormant, won, lost, or deferred?

## Future CRM Integration Considerations

FMS should eventually integrate with a CRM without forcing FMS to become the CRM of record for every sales activity.

Recommended integration principles:

- FMS remains the building, asset, Passport, and lifecycle intelligence system.
- CRM remains the external pipeline, activity, and revenue forecasting system where appropriate.
- Building opportunities should support external CRM identifiers.
- Organization and contact matching should be deliberate and auditable.
- Opportunity stage mappings should be configurable.
- CRM sync should avoid overwriting trusted FMS building data.
- FMS should be able to show CRM-linked status without requiring every user to leave the platform.
- Duplicate detection should account for building name, address, organization, and external CRM IDs.

Potential future integrations include HubSpot, Salesforce, Microsoft Dynamics, or a lightweight CSV/import-export bridge.

## Security/Permissions Considerations

- Lifecycle opportunity data is internal by default.
- Client-visible Passport data must remain separate from internal sales notes and opportunity values.
- Only authorized internal users should see opportunity value, probability, sales notes, and conversion status.
- Client users should not see internal lifecycle badges unless explicitly designed for client display.
- Audit history should capture lifecycle stage and opportunity status changes.
- CRM identifiers and sync status should be protected from unauthorized modification.
- Role-based permissions should distinguish viewers, service users, sales users, managers, and platform administrators.
- Future exports must avoid leaking internal notes into client-facing Passport packages.

## Reporting/Dashboard Requirements

Future dashboards should include:

- Lifecycle pipeline by opportunity type
- Conversion funnel from prime contract to reference building to ITM or membership
- Opportunity status board by owner
- Dormant relationship list
- Passport-ready buildings without active membership
- ITM candidates without proposals
- Membership candidates by building type
- Advisory and capital planning candidates
- Building lifetime value ranking
- Strategic account and portfolio expansion views
- Data completeness score for lifecycle readiness
- Upcoming follow-up dates and stale opportunities

Reports should support filtering by organization, building type, region, lifecycle stage, opportunity type, owner, status, and estimated value.

## Recommended Future Data Model

Future implementation should consider adding or extending models such as:

- `customer_lifecycle_profiles`
  - `organization_id`
  - `building_id`
  - `lifecycle_stage`
  - `relationship_status`
  - `source_prime_contract_reference`
  - `passport_readiness_status`
  - `building_lifetime_value_estimate`
  - `last_lifecycle_review_at`
  - `next_follow_up_at`
  - `internal_notes`
- `building_opportunities`
  - `organization_id`
  - `building_id`
  - `opportunity_type`
  - `status`
  - `owner_user_id`
  - `estimated_value`
  - `probability`
  - `expected_close_date`
  - `source`
  - `external_crm_id`
  - `won_at`
  - `lost_at`
  - `closed_reason`
- `building_relationship_badges`
  - `organization_id`
  - `building_id`
  - `badge_type`
  - `source`
  - `is_client_visible`
  - `created_by_user_id`
- `opportunity_events`
  - `organization_id`
  - `building_opportunity_id`
  - `event_type`
  - `from_status`
  - `to_status`
  - `notes`
  - `created_by_user_id`
- `crm_sync_links`
  - `organization_id`
  - `entity_type`
  - `entity_id`
  - `provider`
  - `external_id`
  - `last_synced_at`
  - `sync_status`

These models should be introduced only after the current building, asset, contact, document, Passport, and membership concepts are stable enough to support lifecycle workflows cleanly.

## Recommended Future Implementation Phases

### Phase 1: Specification Review and Data Model Design

- Review FMS-0024 with Fuzion Fire stakeholders.
- Confirm lifecycle stages, opportunity types, and statuses.
- Decide which fields are manual, derived, or synced.
- Produce schema migration plan.

### Phase 2: Backend Lifecycle Foundation

- Add lifecycle and opportunity models.
- Add CRUD services and API routes.
- Add audit events for status changes.
- Add server-side business rule validation.

### Phase 3: Internal Building Lifecycle UI

- Add lifecycle badges to building profiles.
- Add opportunity panels to building detail pages.
- Add simple create/update/status workflows.
- Keep all lifecycle data internal-only.

### Phase 4: Dashboards and Reporting

- Add lifecycle pipeline dashboard.
- Add conversion funnel reporting.
- Add dormant relationship and follow-up views.
- Add building lifetime value ranking.

### Phase 5: Conversion Workflows

- Add guided workflows for prime-contract-to-service, ITM conversion, membership conversion, and advisory opportunities.
- Add reminders and next-step tracking.
- Add management review views.

### Phase 6: CRM Integration

- Add external CRM link fields.
- Implement import/export or API sync.
- Add duplicate detection and sync conflict handling.
- Keep FMS building data authoritative for Passport and lifecycle intelligence.

### Phase 7: Advanced Intelligence

- Add scoring for Passport readiness, conversion likelihood, and building lifetime value.
- Add recommendations based on asset mix, document completeness, service history, and portfolio patterns.
- Evaluate AI-assisted summaries only after permission, audit, and data quality foundations are mature.
