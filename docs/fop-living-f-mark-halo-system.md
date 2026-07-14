# FOP Living F Mark and Halo System

## Concept

The F mark is a live visual status indicator for the building lifecycle.

It represents BUILD • ADVISE • PROTECT without replacing those words in customer-facing language.

The OP wordmark remains neutral, static, and timeless.

## F Anatomy

- Top arm: ADVISE
- Middle arm: BUILD
- Vertical stem: PROTECT

The F is the expressive lifecycle element. The OP wordmark is not recoloured by building status.

## Colour Palette

- BUILD: electric royal blue `#1769FF`
- ADVISE: soft platinum silver `#DDE2EA`
- PROTECT: pastel highlighter green `#A8E96A`
- HALO: soft Fuzion coral `#E97872`

Coral is a protected-state halo signal. It is not a lifecycle segment colour.

## Progress Behaviour

When only one completion percentage is available, the frontend maps it conservatively:

- 0-33%: BUILD fills
- 34-66%: BUILD remains active and ADVISE fills
- 67-99%: BUILD and ADVISE remain active and PROTECT fills
- 100% with an explicit protected state: full F with coral halo

Incomplete segments remain low-opacity neutral forms.

## Halo Eligibility Rule

The halo may appear only when the mapped status is `protected`.

Current protected mappings:

- Passport Issued
- Passport Delivered
- Explicit completed/protected frontend use

The halo must not appear:

- on incomplete buildings
- on warning states
- on general cards
- on buttons
- as decoration
- before the building or Passport has reached a completed protected state

## Accessibility

The reusable mark includes an accessible label such as `Lifecycle status: BUILD` or `Lifecycle status: PROTECTED`.

Status text should appear beside the mark where the mark communicates building state.

The mark uses restrained transitions and respects reduced-motion through CSS transition controls.

Colour is never the only status signal; text labels and badges remain present.

## Usage Examples

Use the living mark in:

- Mission Control health and lifecycle summaries
- Building profile lifecycle status
- Building Protection Passport headers
- Building Library and Build Passport workflow
- Passport onboarding queue rows
- Closeout readiness views

Use the static complete mark in:

- login
- front door
- favicon
- exported brand files
- print or document contexts

## Misuse Examples

Do not use the halo as a decorative glow.

Do not put the halo on incomplete lifecycle states.

Do not recolour the OP wordmark by building status.

Do not replace BUILD • ADVISE • PROTECT with colour names.

Do not imply formal certification when the underlying business state is not known.

## Current Frontend Status Mapping

The helper lives in:

`frontend/lib/fop-lifecycle-visual.ts`

Current mappings:

- `Building Registered`, active construction, or low progress: BUILD
- `Documents Imported`, `Closeout Incomplete`, review states, or mid progress: ADVISE
- `Ready for Passport`, `Assets Verified`, or high incomplete progress: PROTECT
- `Passport Issued` or `Passport Delivered`: PROTECTED with halo

When data is insufficient, the UI uses conservative visual progress and does not show the halo.

## Future Certification Plaque and QR Mark Use

Future phases may create a protected-state plaque or QR-linked mark for buildings with completed Passport and protection criteria.

That future mark should use the same halo rule and must be backed by explicit certification logic before being presented as an authoritative protected state.
