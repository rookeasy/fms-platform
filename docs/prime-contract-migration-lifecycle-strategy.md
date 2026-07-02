# FMS-0025 Prime Contract Migration & Lifecycle Conversion Strategy

FMS-0025 defines the documentation-only strategy for migrating completed Fuzion Fire prime contracts into FMS and converting those records into long-term lifecycle customer relationships.

No code, schema, automation, CRM integration, dashboard, or workflow implementation is included in this phase.

## Purpose

The purpose of FMS-0025 is to define how completed prime contracts become permanent Building Protection Passport™ records and structured lifecycle opportunities inside FMS.

This strategy gives Fuzion Fire a repeatable way to preserve project knowledge, protect institutional memory, strengthen customer relationships, and create recurring value after construction or project delivery is complete.

## Vision

Every completed Fuzion Fire prime contract shall become a permanent Building Protection Passport™ and lifecycle customer relationship managed within FMS.

FMS should become the operational memory and lifecycle growth platform for every building Fuzion Fire touches. A completed project should not disappear into folders, inboxes, drawings, or individual memory. It should become an active building record with useful metadata, contacts, assets, documents, relationship status, and future opportunity paths.

## Business Philosophy

Prime contract work creates trust, technical knowledge, and a natural reason to continue the client relationship. FMS should turn that moment into a structured lifecycle program.

The business philosophy is:

- Every project creates future service potential.
- Every building deserves a durable protection record.
- Every completed contract should create a follow-up motion.
- Every document, asset, contact, and project note can become sales and service intelligence.
- Every client relationship should be measured over the life of the building, not only the life of the contract.

## Migration Objectives

- Convert completed prime contracts into structured FMS building records.
- Establish a permanent Building Protection Passport™ foundation for each migrated building.
- Capture enough building, asset, contact, and document metadata to support future client conversations.
- Identify ITM, membership, advisory, and capital planning opportunities.
- Create a consistent internal workflow for review, ownership, follow-up, and conversion.
- Provide leadership with visibility into post-project conversion performance.
- Reduce reliance on disconnected spreadsheets, personal notes, and ad hoc follow-up.

## Migration Scope

In scope:

- Completed Fuzion Fire prime contracts.
- Building profile creation or matching.
- Organization and contact association.
- Representative fire protection asset capture.
- Document metadata capture.
- Passport readiness assessment.
- Internal relationship and opportunity classification.
- Follow-up ownership and lifecycle conversion strategy.

Out of scope for this documentation phase:

- Database schema changes.
- Data import tooling.
- Automated document parsing.
- CRM synchronization.
- Inspections, deficiencies, work orders, reports, certificates, billing, memberships, or auth changes.
- Client-facing portal changes.
- AI-assisted workflows.

## Migration Levels

FMS should support staged migration quality levels so Fuzion Fire can begin with practical records and enrich them over time.

### Level 1: Building Stub

- Building name
- Address or representative address
- Owner, manager, or client organization when known
- Prime contract reference
- Basic notes
- Migration source

Use this level when only minimal project information is available.

### Level 2: Reference Building

- Complete building profile
- Primary contacts
- Representative asset list
- Core document metadata
- Internal project notes
- Lifecycle status

Use this level for internal knowledge capture and early sales follow-up.

### Level 3: Passport Ready

- Building profile reviewed
- Contacts reviewed
- Asset list reviewed
- Client-visible document metadata selected
- Passport records marked
- Internal-only sales notes separated from client-facing records

Use this level for product demonstrations, client onboarding, and membership conversations.

### Level 4: Lifecycle Active

- ITM, membership, advisory, or capital planning opportunity exists
- Internal owner assigned
- Next action date defined
- Relationship status is current
- Dashboard KPIs include the building

Use this level when the building is actively managed as a customer relationship.

### Level 5: Strategic Account

- Multi-building or high-value client context exists
- Building lifetime value is estimated
- Executive or leadership visibility is required
- Multiple opportunity paths may be active
- Capital planning or advisory potential is meaningful

Use this level for key accounts and portfolio expansion.

## Source Documents

Migration should use available project and contract artifacts as source material, including:

- Prime contract summaries
- Project closeout packages
- Approved drawings
- Shop drawings
- As-built drawings
- Hydraulic calculations
- Material and test certificates
- Fire pump or backflow records
- Owner manuals
- Turnover documents
- Project manager notes
- Estimating files
- Client correspondence
- Warranty documents
- Site photos
- Existing spreadsheets or project trackers

Source documents should be treated as internal migration inputs unless they are explicitly reviewed and marked as client visible.

## Required Building Record

Each migrated prime contract should produce or reuse one building record with:

- Building name
- Organization or owner relationship
- Address fields
- City, province/state, postal code, and country
- Building type
- Occupancy or use context where known
- Property manager or owner contact where known
- Fire department or AHJ where known
- Notes describing the prime contract and migration context
- Passport readiness status
- Relationship status
- Source prime contract reference

The migration process must avoid duplicate building records. When a matching building already exists, migration should enrich lifecycle classification through future approved workflows rather than creating a second record.

## Lifecycle Opportunities

Each migrated building should be evaluated for lifecycle opportunities:

- ITM service contract
- FMS membership
- Building Protection Passport™ onboarding
- Advisory review
- Capital planning
- Retrofit or modernization
- Deficiency repair program
- Document digitization
- Owner or facility team training
- Portfolio expansion

Multiple opportunities may be valid for one building at the same time.

## Relationship Statuses

Recommended relationship statuses:

- `prime_contract_complete`
- `migration_needed`
- `migration_in_progress`
- `reference_building`
- `passport_ready`
- `itm_candidate`
- `itm_active`
- `membership_candidate`
- `membership_active`
- `advisory_candidate`
- `capital_planning_candidate`
- `lifecycle_active`
- `strategic_account`
- `dormant`
- `archived`

Relationship status should represent the building relationship, not only a sales deal. Opportunity statuses should remain separate from relationship statuses.

## Dashboard KPIs

Future dashboards should measure:

- Completed prime contracts identified
- Prime contracts migrated into FMS
- Migration completion rate
- Buildings by migration level
- Passport-ready migrated buildings
- Migrated buildings missing contacts
- Migrated buildings missing asset metadata
- Migrated buildings missing document metadata
- ITM candidates created from migrated prime contracts
- ITM conversion rate
- Membership candidates created from migrated prime contracts
- Membership conversion rate
- Advisory and capital planning candidates
- Dormant migrated buildings
- Strategic accounts created from migrated prime contracts
- Average time from contract completion to FMS migration
- Average time from migration to first lifecycle follow-up

## Customer Lifetime Value

Customer lifetime value should estimate the total long-term commercial value of a client relationship across all buildings and opportunity types.

Recommended factors:

- Number of completed prime contracts
- Number of migrated buildings
- ITM annual recurring value
- FMS membership value
- Advisory engagement value
- Capital planning and retrofit potential
- Number of buildings in the client portfolio
- Relationship duration
- Historical win rate
- Strategic importance
- Client responsiveness

Customer lifetime value should be presented as an internal planning and prioritization measure, not as client-facing content.

## Building Maturity Index

The Building Maturity Index should summarize how ready a migrated building is for lifecycle management.

Suggested dimensions:

- Profile completeness
- Contact completeness
- Asset metadata completeness
- Document metadata completeness
- Passport readiness
- Client-visible record readiness
- Opportunity coverage
- Relationship owner assignment
- Follow-up recency
- Service or membership conversion status

Example maturity levels:

- `0 - Unmigrated`
- `1 - Stub`
- `2 - Reference Building`
- `3 - Passport Ready`
- `4 - Lifecycle Active`
- `5 - Strategic Account`

The maturity index should help teams prioritize cleanup, follow-up, and conversion work.

## Internal Workflow

1. Identify completed prime contract.
2. Check whether the building already exists in FMS.
3. Create or reuse the building record.
4. Attach or record source document metadata.
5. Capture representative assets.
6. Capture known contacts.
7. Add internal migration notes.
8. Assign migration level.
9. Determine Passport readiness.
10. Identify lifecycle opportunities.
11. Assign internal owner.
12. Set relationship status.
13. Set next follow-up date.
14. Review conversion progress in dashboards.
15. Update status after ITM, membership, advisory, or capital planning outcomes.

## Roles and Responsibilities

- Project team: Provides closeout context, source documents, and known building details.
- Operations team: Validates building, asset, contact, and document usefulness.
- Service team: Evaluates ITM opportunity fit.
- Sales team: Owns client follow-up, proposal movement, and relationship conversion.
- Leadership: Reviews dashboard KPIs, strategic accounts, and conversion outcomes.
- FMS administrator: Oversees data quality, permissions, lifecycle settings, and migration governance.
- Future CRM owner: Maintains external pipeline alignment once CRM integration exists.

## Automation Roadmap

Automation should be introduced gradually after the migration process is proven manually.

### Stage 1: Manual Migration Playbook

- Standardize required fields.
- Use checklists for migration levels.
- Manually tag lifecycle opportunities.
- Review dashboard requirements before implementation.

### Stage 2: Assisted Import

- Add structured import templates.
- Detect likely duplicate buildings.
- Validate required fields before import.
- Produce migration summaries and exception lists.

### Stage 3: Document Metadata Assistance

- Extract candidate document titles, types, and dates.
- Suggest Passport visibility.
- Keep human approval required before client-visible records are marked.

### Stage 4: Opportunity Suggestions

- Suggest ITM, membership, advisory, and capital planning opportunities based on building type, assets, documents, and contract context.
- Require internal approval before opportunities become active.

### Stage 5: CRM Sync

- Link FMS buildings and opportunities to CRM accounts, contacts, and deals.
- Sync selected statuses and identifiers.
- Preserve FMS as the source of truth for building and Passport intelligence.

### Stage 6: Lifecycle Intelligence

- Score migration readiness, conversion likelihood, customer lifetime value, and building maturity.
- Recommend follow-up priorities.
- Provide executive lifecycle portfolio views.

## Success Metrics

FMS-0025 should be considered successful when future implementation can demonstrate:

- Completed prime contracts are consistently captured in FMS.
- Migrated buildings are not duplicated.
- Passport-ready building records increase over time.
- ITM and membership opportunities are created from migrated projects.
- Follow-up happens faster after project completion.
- Leadership can see conversion rates from prime contract to lifecycle relationship.
- Sales and service teams share a single building context.
- Internal-only opportunity data remains separate from client-visible Passport records.
- Strategic accounts and portfolio expansion opportunities are easier to identify.
- Fuzion Fire can measure customer and building lifetime value from completed work.
