# Project Atlas Day v2

## Purpose

Project Atlas Day v2 refines the Fuzion Operating Platform into a light, durable enterprise operating environment. The daily application UI should feel calm, professional, engineering-led, and built for long-term operational use while preserving a stronger branded treatment on login and public entry surfaces.

This is a presentation layer refresh only. Routes, API calls, authentication behavior, data structures, and backend behavior remain unchanged.

## Palette

- Primary navy: `#0F172A`
- Secondary navy: `#1E293B`
- Warm white: `#FAFAF8`
- Surface white: `#FFFFFF`
- Soft grey: `#F8FAFC`
- Border: `#E2E8F0`
- Slate text: `#475569`
- Muted text: `#64748B`
- Soft coral: `#D95A4E`
- Success: `#16A34A`
- Warning: `#D97706`
- Critical: `#DC2626`
- Advise blue: `#2563EB`

## Typography Guidance

Typography should be restrained and legible. Page titles use confident weight without oversized startup-style scale. Body copy should favor short operational language, generous line-height, and strong contrast against warm white or white surfaces.

## Spacing Guidance

Atlas Day v2 favors generous spacing, clear groupings, and fewer competing panels. Cards, tables, forms, and dashboards should use consistent padding, subtle borders, and minimal shadows. Layouts should avoid dense visual stacking unless the page is explicitly a work queue or data table.

## Coral Usage Rule

Coral is reserved for:

- protected state
- active state
- primary action
- current lifecycle state

Coral should not be used as random decoration. If a visual element does not communicate action, protected status, or current state, use navy, blue, slate, white, or grey instead.

## BUILD / ADVISE / PROTECT Colour System

- BUILD: navy `#0F172A`
- ADVISE: professional blue `#2563EB`
- PROTECT: soft coral `#D95A4E`

The same mapping should be used for lifecycle badges, progress indicators, dashboard charts, passport sections, property views, building views, and closeout readiness visuals.

## Logo / Mark Guidance

The FOP mark should remain simple and timeless. Only the F carries the motion or fading-line language. The O and P remain clean type. Streaks should be fewer, wider, smoother, and quieter. Avoid harsh glow effects, bright orange, or noisy technical decoration.

## Atlas Day vs Atlas Night

Atlas Day is the default daily working environment:

- warm white page background
- white cards
- soft grey panels
- subtle borders
- minimal shadows
- restrained motion

Atlas Night remains suitable for login, public front door, branded demos, or future command-center displays, but should use deep navy rather than pure black.

## Application UI Rules

- Sidebar may use deep navy, but main content should remain light.
- Top bar should stay minimal and should not compete with page content.
- Tables should use clean rows, subtle dividers, and readable spacing.
- Forms should use strong labels, accessible focus states, and white fields.
- KPI cards should be quiet and data-first.
- Motion should be limited to short, purposeful transitions.

## Login / Marketing Rules

Login and public entry pages may be more branded than the application shell. They should still avoid harsh black, excessive glow, and overly animated treatment. Use FOP / Fuzion Operating Platform, BUILD • ADVISE • PROTECT, and Buildings Under Protection™.

## Port 3000 Development Note

The FOP frontend is intended to run at:

```powershell
http://localhost:3000
```

If Next.js starts on `3001`, another process is likely occupying `3000`. On Windows, identify the stale process with:

```powershell
netstat -ano | findstr :3000
```

Then terminate the specific stale process only after confirming the PID:

```powershell
taskkill /PID <PID> /F
```

Do not add automatic process killing to app startup unless it becomes an explicit development tooling decision.
