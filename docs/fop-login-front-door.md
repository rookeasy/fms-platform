# FOP Login Front Door

## Purpose

FMS-0029 introduces the public front door for the Fuzion Operating Platform. The root route now presents FOP as the entry point for Building Protection Passport&trade;, Digital Closeout, property readiness, and building operations. The `/login` route provides the branded MVP sign-in surface for Fuzion Tech Inc.

## Local URLs

- Front door: `http://localhost:3000`
- Login: `http://localhost:3000/login`
- Dashboard: `http://localhost:3000/dashboard`
- Properties: `http://localhost:3000/properties`
- Buildings: `http://localhost:3000/buildings`

## Future Production URL Options

Possible production entry points include:

- `https://operations.fuziontech.ca`
- `https://fop.fuziontech.ca`
- `https://passport.fuziontech.ca`
- `https://closeout.fuziontech.ca`

The final URL should match the production identity decision for whether FOP is positioned as the parent operating platform, the Passport portal, or the Digital Closeout workspace.

## MVP Limitations

- Authentication remains placeholder-only.
- The login form does not validate credentials against a production identity provider.
- The sign-in and demo paths route directly to `/dashboard`.
- No backend auth, security policy, session handling, MFA, password reset, SSO, or role enforcement changes are included.
- Public/private route protection is not implemented in this phase.

## Future Auth Roadmap

- Add production identity provider integration.
- Implement session handling and route protection.
- Add organization-aware login routing.
- Support role-based post-login destinations.
- Add password reset or passwordless magic-link flows if selected.
- Add MFA for administrative and customer-facing accounts.
- Add audit logging for login and session events.
- Add invitation-based onboarding for property managers, building owners, technicians, engineers, and read-only viewers.
