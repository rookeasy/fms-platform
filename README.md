# FOP Developer Toolkit

## Install

Copy `fop-dev.ps1` to:

```powershell
C:\Users\Adam\Documents\Projects\fms-platform\fop-dev.ps1
```

Then load it in PowerShell:

```powershell
. "C:\Users\Adam\Documents\Projects\fms-platform\fop-dev.ps1"
```

## Optional: Auto-load every time PowerShell opens

Run:

```powershell
notepad $PROFILE
```

Add this line:

```powershell
. "C:\Users\Adam\Documents\Projects\fms-platform\fop-dev.ps1"
```

Save and reopen PowerShell.

## Commands

```powershell
fop-root
fop-backend
fop-frontend
fop-migrate
fop-seed-soho
fop-clean-soho
fop-backend-run
fop-frontend-run
fop-typecheck
fop-check
fop-open
fop-status
```
