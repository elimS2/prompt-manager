# User Access Allowlist and Approval Workflow — Roadmap

## Initial Prompt

I would now like to do the following: predefine email mailboxes that are allowed access. If they are not allowed, then even if they sign in through Google, show that access is not granted. “Wait for administrator approval.” For me, as the administrator, show somewhere in the panel or on the users page the user who is waiting for approval. That means we also need to create a users page.

For this feature let’s create a separate roadmap.

=== Analyse the Task and project ===

Deeply analyze our task, our project and decide how to best implement this.

==================================================

=== Create Roadmap ===

Create a detailed, comprehensive step-by-step plan for implementing this task in a separate file-document. We have a folder docs/features for this. If there is no such folder, create it. Document in as much detail as possible all the identified and tried problems, nuances and solutions, if any. As you progress on implementing this task, you will use this file as a to-do checklist, update this file and document what has been done, how it has been done, what problems have arisen and what decisions have been made. For history, do not delete items; only update their status and comment. If during implementation it becomes clear that something needs to be added, add it to this document. This will help us keep the context window, remember what we have already done and not forget to do what was planned. Remember that only the English language is allowed in the code, comments and project labels. When you write the plan, stop and ask me if I agree to start implementing it or if something needs to be adjusted in it.

Also include steps for manual testing in the plan, i.e., what needs to be clicked in the interface.

==================================================

=== SOLID, DRY, KISS, UI/UX, etc ===

Follow the principles: SOLID, DRY, KISS, Separation of Concerns, Single Level of Abstraction, Clean Code Practices.
Follow UI/UX principles: User-Friendly, Intuitive, Consistency, Accessibility, Feedback, Simplicity, Aesthetic & Modern, Performance, Responsive Design.
Use Best Practices.


## 1) Current State Analysis (Project)

- Framework: Flask app with blueprints, SQLAlchemy models, Flask-Migrate.
- AuthN: Google OAuth integration exists (Authlib + Flask-Login). `User` model present with fields (`google_sub`, `email`, `role`, `is_active`, timestamps).
- AuthZ: No fine-grained access control yet; no allowlist/approval workflow.
- Config: `env.example` includes `ADMINS=...` (emails), OAuth variables, and cookie settings.
- UI: Jinja templates, Bootstrap 5; no Users management page.

Implication: Build an access-control layer on top of existing OAuth login, introducing an allowlist and an approval workflow, plus an admin-only Users page.


## 2) Goals and Non-Goals

- Goals
  - Maintain a predefined allowlist of emails permitted to access the app.
  - If a user signs in via Google but is not allowlisted, do not grant access; show a message: access not granted, waiting for admin approval.
  - Allow non-allowlisted users to create a “pending access” record so the admin can approve them later without redeploying.
  - Provide an admin-only Users page listing pending users and actions to approve/disable.
  - Keep code, labels, and comments in English.

- Non-Goals (phase 1)
  - Email delivery for approval notifications.
  - SSO providers beyond Google.
  - Complex RBAC; we will stick to simple roles (`admin`, `user`) and a status flag.


## 3) High-Level Design

- Data Model
  - Extend `users` with an explicit `status` column: one of `active`, `pending`, `disabled`.
    - Default `active` for allowlisted or admin users.
    - `pending` for users who signed in but are not allowlisted.
    - `disabled` for revoked accounts.
  - New table `email_allowlist` to store allowlisted emails (and optional default role per email):
    - `id`, `email` (unique, lowercase), `default_role` (default `user`), `note`, timestamps.
  - Optional audit fields on `users`: `approved_at`, `approved_by_user_id`.

- Configuration
  - Support pre-seeding admins via `ADMINS` env (already present) — any login with an admin email becomes `admin/active` regardless of allowlist.
  - Optional `ACCESS_POLICY` env with values:
    - `allowlist_strict`: Only allowlisted or admin can access; others remain pending.
    - `allowlist_then_approval` (default): Not on allowlist => create pending record and show "awaiting approval" page; admin can approve.

- Backend Services
  - `UserService` additions:
    - `determine_access(profile)` — resolve allowlist/admin/pending status.
    - `approve_user(user_id, role)` — set status to `active`, optionally update role, set audit fields.
    - `disable_user(user_id)` — set status to `disabled`.
  - `AllowlistService` (or methods on `UserRepository`) to CRUD allowlist entries.

- Controllers / Routes
  - Auth callback: after obtaining Google profile, enforce access policy:
    - If email is admin or in allowlist => `active`, proceed to `login_user`.
    - Else => ensure `User` exists with `pending` status; do NOT `login_user`; redirect to `/access/pending` with a friendly message.
  - Users management page (admin-only):
    - `GET /admin/users` — list with filters: Pending (default), Active, Disabled.
    - `POST /admin/users/{id}/approve` — approve and optionally assign role.
    - `POST /admin/users/{id}/disable` — disable account.
    - `GET/POST /admin/allowlist` — simple CRUD for allowlist entries (MVP: add/remove).

- UI/UX
  - Add a dedicated `/access/pending` page explaining the approval process and showing the signed-in email (from last attempt) without exposing PII in logs.
  - Admin Users page with clear filters, table layout, and actions (Approve, Disable). Accessible from navbar for admins.
  - Consistent flash messages and loading states; responsive and accessible.

- Security
  - Never log raw emails in INFO logs; keep PII out of logs.
  - Admin-only routes protected by role check; CSRF enabled for forms.
  - Database uniqueness constraints (email) remain enforced; lower-case normalization.


## 4) Implementation Plan (Checklist)

- [x] Configuration
  - [x] Add `ACCESS_POLICY` to config with default `allowlist_then_approval`.
  - [x] Document `ADMINS` handling (seed admin role on first login).

- [x] Data model and migrations
  - [x] Add `status` column to `users` (Enum/String), values: `active`, `pending`, `disabled`; index on `status`.
  - [x] Add optional audit fields: `approved_at`, `approved_by_user_id` (nullable FK to `users.id`).
  - [x] Create `email_allowlist` table: `id`, `email` (unique), `default_role`, `note`, timestamps.
  - [x] Alembic migration scripts created and applied in development.

- [x] Repository and services
  - [x] `AllowlistRepository` with methods: `get_by_email`, `list` (MVP); (add/remove planned in admin CRUD step).
  - [x] Extend `UserRepository` with `list_by_status(status)` and helpers (kept minimal; service handles audit).
  - [x] Extend `UserService.find_or_create_from_google` to enforce allowlist + status logic and normalize email.
  - [x] New service methods: `approve_user`, `disable_user`, `list_pending_users`.

- [x] Controllers
  - [x] Update `auth_controller.callback` to:
    - [x] Normalize email to lowercase in service; detect admin via `ADMINS` and set `role='admin'` and `status='active'`.
    - [x] If email is in allowlist => ensure `status='active'` and log in.
    - [x] If not allowlisted => create/update user with `status='pending'`; do not log in; redirect to `/access/pending` with guidance.
  - [x] Add `/access/pending` route and template.
  - [x] New `admin_bp` with admin routes:
    - [x] `GET /admin/users` (list + filters), `POST /admin/users/{id}/approve`, `POST /admin/users/{id}/disable`.
  - [x] `GET/POST /admin/allowlist` (MVP: add/remove entries).

- [x] UI/UX
  - [ ] Create `templates/access/pending.html` with clear message and minimal guidance.
  - [ ] Create `templates/admin/users.html` with table, filters, actions (Bootstrap buttons, CSRF-protected forms or small HTMX fetches).
  - [ ] Add navbar entry “Users” for admins only.

- [ ] Observability
  - [x] Add structured logs for approval actions (no PII; reference user ids).
  - [x] Add admin audit trail fields updates upon approval/disable.

- [ ] Testing
  - [ ] Unit tests for policy decisions in `UserService` (allowlist/admin/pending/disabled).
  - [ ] Integration tests covering callback outcomes (active vs pending vs disabled).
  - [ ] View tests for admin routes authorization.

- [ ] Documentation
  - [ ] Update `README.md` (env vars, flows, admin page overview).
  - [ ] Keep this feature file updated with statuses and notes.

- [ ] Rollout
  - [ ] Backfill: existing users become `active` unless explicitly disabled; document behavior.
  - [ ] Seed allowlist for known team emails; set `ADMINS`.
  - [ ] Verify in staging/dev before production.


## 5) Data Model Details

- `users` additions
  - `status`: String(20), not null, default `active`, indexed. Allowed values: `active`, `pending`, `disabled`.
  - `approved_at`: DateTime, nullable.
  - `approved_by_user_id`: Integer FK to `users.id`, nullable.

- `email_allowlist`
  - Columns: `id` (PK), `email` (unique, not null, lowercase), `default_role` (String(50), default `user`), `note` (String(255), nullable), `created_at`, `updated_at`.

Constraints: unique index on `email`; all emails stored in lowercase.


## 6) Flow Logic (Auth Callback)

1. After Google userinfo:
   - Normalize `email = email.lower()`.
   - If `email in ADMINS` => ensure user exists with `role='admin'`, `status='active'`; `login_user`.
   - Else if `email in email_allowlist` => ensure `status='active'`; `login_user`.
   - Else (not allowlisted):
     - Ensure a `User` exists or is created with `status='pending'` and captured profile info.
     - Do not call `login_user`; redirect to `/access/pending` with a flash message.
2. Admin approves in `/admin/users` => set `status='active'`, optionally assign role; the next login will succeed.
3. Disabled users (`status='disabled'`) are always rejected with a flash message and redirected to `/access/pending`.


## 7) Security Considerations

- Keep PII out of logs; use user ids for audit messages.
- Protect admin endpoints with role checks and CSRF.
- Validate inputs for allowlist CRUD; normalize emails.
- Consider rate limits on approval actions if exposed over API.


## 8) Manual Testing (UI Walkthrough)

Prerequisites:
- Configure `ADMINS=you@example.com` in environment.
- Seed `email_allowlist` with one team email (non-admin).
- Set `ACCESS_POLICY=allowlist_then_approval` (default assumed).

Steps:
1. Open the app (logged out). Header shows “Sign in with Google”.
2. Log in with an allowlisted non-admin email:
   - Expect successful login, normal access (`status=active`).
3. Log out. Log in with a non-allowlisted email:
   - Expect redirect to `/access/pending` page.
   - Verify that a `User` record exists with `status=pending`.
4. As admin, open `Admin → Users` page:
   - Default filter shows `Pending` users.
   - Approve the pending user.
5. Log out (if needed) and log in again with the previously pending user:
   - Expect successful login now (`status=active`).
6. Disable a user from the admin Users page:
   - Attempt to log in as that user; expect redirect to `/access/pending` with a “disabled” notice.
7. Allowlist CRUD:
   - Add an email to allowlist; log in as that email; expect direct success.
   - Remove from allowlist; user should remain `active` unless explicitly disabled; document behavior.

Negative tests:
- Attempt to access `/admin/users` as a non-admin: expect 403 or redirect.
- Tamper with approve/disable POST without CSRF token: expect rejection.


## 9) Acceptance Criteria

- Emails in allowlist (or in `ADMINS`) can log in and access the app.
- Non-allowlisted users become `pending` and see the `/access/pending` page after OAuth; they cannot access protected routes.
- Admin can view pending users and approve/disable them.
- Security and UX principles followed; documentation and tests added.


## 10) Open Questions

- Should we send email notifications to admins upon new pending requests? (Out of scope for phase 1.)
- Should we expose a self-service “Request access” form when not using Google login? (Probably not needed.)
- After removing from allowlist, should an `active` user remain active or revert to pending? (Proposed: remain active until explicitly disabled.)


## 11) Work Log (to be updated during implementation)

- 2025-— Planned: Add `status` to users; add `email_allowlist` table; update services/controllers; create admin Users page.
 - 2025-08-10T23:45:39Z — Done: Configured ACCESS_POLICY, parsed ADMINS; env.example updated.
 - 2025-08-10T23:55:00Z — Done: Added models (users status/audit, email_allowlist); created migration 7900128ca2d6; applied.
 - 2025-08-11T00:10:00Z — Done: Implemented repositories and UserService with access policy; normalized email handling.
 - 2025-08-11T00:25:00Z — Done: Updated OAuth callback to respect status; added /access/pending route/template; error-path redirects to pending.
 - 2025-08-11T00:40:00Z — Done: Implemented admin_bp (Users approve/disable; Allowlist CRUD); registered blueprint; added Admin menu in navbar.
 - 2025-08-11T00:50:00Z — Done: Added structured admin action logs; improved dark theme table contrast; prevented status downgrade after approval.


