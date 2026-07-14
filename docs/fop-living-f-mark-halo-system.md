# FOP Living F Mark and Halo System

## Concept

The approved FOP identity is the Living F plus the official Halo™ O and a minimal white P.

The mark reinforces BUILD • ADVISE • PROTECT without replacing those customer-facing words.

## Living F Anatomy

- Vertical element: PROTECT™ in Electric Lime `#8CFF1A`
- Upper horizontal: ADVISE™ in Titanium Silver `#BFC5CF`
- Lower horizontal: BUILD™ in Electric Blue `#1F7BFF`

The F is the expressive and structural lifecycle element.

## Halo Anatomy

The O is the official Halo™.

The Halo™ represents:

- Continuous Protection
- Building Lifecycle
- Buildings Under Protection™
- Stewardship
- Executive Intelligence

The Halo should render as an electrified blue circular ring using `#26B6FF` with subtle energy effects.

The Halo is the primary visual element of the platform.

## P Anatomy

The P is white.

It is minimal.

It has no additional decoration.

## Approved Palette

- Primary Background: Midnight `#071223`
- BUILD: Electric Blue `#1F7BFF`
- ADVISE: Titanium Silver `#BFC5CF`
- PROTECT: Electric Lime `#8CFF1A`
- Halo: Electrified Blue `#26B6FF`
- White: `#FFFFFF`

## Progress Behaviour

When only one completion percentage is available, the frontend maps it conservatively:

- 0-33%: BUILD fills
- 34-66%: BUILD remains active and ADVISE fills
- 67-99%: BUILD and ADVISE remain active and PROTECT fills
- Backend-approved protected state: full FOP mark with authoritative Halo treatment

Incomplete segments remain low-opacity neutral forms.

## Protected-State Halo Rule

Operational halo eligibility remains backend-authoritative:

- certification status must be `approved`
- `halo_eligible` must be true
- certification must not be suspended or revoked

Passport Issued, Passport Delivered, Ready for Passport, closeout progress, and frontend-only progress do not activate protected-state status.

## Usage Examples

Use the mark in:

- Mission Control health and lifecycle summaries
- Building profile lifecycle status
- Building Protection Passport headers
- Building Library and Build Passport workflow
- Passport onboarding queue rows
- Closeout readiness views
- Login, sidebar, favicon, loading, and empty states

## Misuse Examples

Do not use replacement lifecycle names.

Do not replace BUILD • ADVISE • PROTECT with colour names.

Do not use rainbow gradients.

Do not use BMW-like blue/red styling.

Do not overdecorate the mark.

Do not imply formal certification when the backend Protected State record is not approved.

## Implementation

The reusable mark lives in:

`frontend/components/brand/FopLifecycleMark.tsx`

Lifecycle visual mapping lives in:

`frontend/lib/fop-lifecycle-visual.ts`

Design tokens live in:

`frontend/lib/design-tokens.ts`

Global CSS variables live in:

`frontend/app/globals.css`
