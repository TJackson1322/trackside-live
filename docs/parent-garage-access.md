# Parent-managed Driver Garage: implementation plan

Status: DESIGN ONLY. No accounts, authorization, private storage, or uploads are active.

## Access policy
- A parent/guardian owns an account and can manage one or more driver garages.
- A parent can invite another verified parent/guardian to a specific garage.
- Drivers can have a read-only account only when age-appropriate and permitted by a parent.
- Other drivers, other parents, and public visitors have no access to private garage records.
- Every database read/write must check the authenticated user's membership in the requested garage. Never trust driver IDs supplied by a browser alone.
- Parent consent and applicable child privacy requirements must be addressed before collecting information about minors.
- Do not use a public repository or a client-side-only store for confidential data.

## Proposed private database tables (future migrations)
users(id, email_unique, password_hash_or_identity_provider_id, email_verified_at, created_at)
drivers(id, public_profile_id_nullable, display_name, created_at)
garages(id, driver_id_unique, created_at)
garage_memberships(id, garage_id, user_id, role, invited_by_user_id, accepted_at, revoked_at)
garage_setups(id, garage_id, created_by_user_id, track_name, event_date, tire_pressures_json, setup_json, track_conditions_json, created_at, updated_at)
garage_notes(id, garage_id, created_by_user_id, note_encrypted_or_private_text, created_at)
audit_events(id, garage_id, actor_user_id, action, timestamp)

Membership role: parent_admin or driver_viewer. Only parent_admin may invite/revoke members or edit setup data. Revoking access must take effect on the server immediately.

## Security gates before enabling forms
1. Choose a maintained identity provider with verified email, secure sessions, rate limits, and password reset.
2. Deploy a non-public database; keep secrets in environment variables, never GitHub.
3. Enforce per-garage authorization in every route and query; test cross-account access denial.
4. Add CSRF protection, secure cookies, HTTPS, audit logs, backup and retention controls.
5. Design child privacy and parent-consent flow before collecting minor information.
6. Test access revocation and invitation expiry; add secure upload validation only later.

This document is an architecture plan, not evidence of working security controls.
