# Google OAuth 2.0 Authentication Integration — Roadmap

## Initial Prompt

I want to attach Google authorization. What do I need for this?

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

- Framework: Flask application with blueprints (`prompt_bp`, `api_bp`), SQLAlchemy models, Flask-Migrate.
- Config: `config/` with `BaseConfig`, environment-specific configs; sensible cookie/CSRF defaults present.
- Persistence: SQLite (dev) or Postgres (prod) via SQLAlchemy; Alembic migrations available.
- UI: Jinja templates with a shared `base.html`, no existing authentication affordances.
- Auth: No user model, no session-based auth, no OAuth integration.
- Architecture style: layered with `models/`, `repositories/`, `services/`, `controllers/`, which we will preserve for new auth functionality.

Implication: We will introduce a minimal, cohesive authentication module following the existing layering: new `models/user.py`, `repositories/user_repository.py`, `services/user_service.py`, and `controllers/auth_controller.py`. We will add an OAuth client service and optionally Flask-Login for session management.


## 2) Goals and Non-Goals

- Goals
  - Enable sign-in with Google via OAuth 2.0 (Authorization Code with PKCE not required for server-based app, standard flow with state).
  - Create a persistent `User` on first login; update last login on subsequent logins.
  - Maintain user session; expose user context to the UI (avatar/name/email).
  - Provide logout.
  - Gate write actions (create/edit/delete) behind authentication while keeping read actions public initially.

- Non-Goals (phase 1)
  - Roles/permissions beyond a simple optional `role` field.
  - Multi-identity linking or providers other than Google.
  - API token issuance.


## 3) Design Decisions

- OAuth client library: Authlib for Flask (`authlib.integrations.flask_client.OAuth`).
  - Rationale: actively maintained, widely used, simple integration, supports Google out of the box.
- Session management: Flask-Login for session mgmt and `login_required` decorator.
  - Rationale: Clean separation, built-in helpers, integrates well with Flask.
- Data model: Introduce `User` model with fields: `id`, `google_sub`, `email` (unique), `name`, `picture_url`, `role` (optional, default `user`), `is_active`, `created_at`, `updated_at`, `last_login_at`.
- New blueprint: `auth_bp` for `/auth/login`, `/auth/callback`, `/auth/logout`.
- Configuration via environment variables: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `OAUTH_GOOGLE_REDIRECT_URI`, optional `OAUTH_GOOGLE_ALLOWED_HD` to restrict to a Google Workspace domain.
- Security: Use OAuth `state` to mitigate CSRF; keep cookie settings aligned with existing config; in production, ensure HTTPS and consider `SameSite=Lax` or `None` when needed.
- UI/UX: Add "Sign in with Google" button in header; show user avatar/name; include logout in a user menu.
- Backward compatibility: Read-only pages remain public; write actions guarded with `login_required`.


## 4) Implementation Plan (Checklist)

- [x] Add dependencies
  - [x] Add `Authlib` and `Flask-Login` to `requirements*.txt`.
  - [x] Update lockfiles if any; verify installation in dev environment.

- [ ] Configuration
  - [x] Extend `env.example` with `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `OAUTH_GOOGLE_REDIRECT_URI`, `OAUTH_GOOGLE_ALLOWED_HD` (optional).
  - [x] Add configuration mapping in `config/base.py`.
  - [ ] Validate `SESSION_COOKIE_*` values for OAuth flows; document production expectations (HTTPS).

- [ ] Data model and migrations
  - [x] Create `app/models/user.py` with the `User` SQLAlchemy model.
  - [x] Register model in `app/models/__init__.py`.
  - [x] Generate Alembic migration; apply in dev.

- [ ] Repository and service layers
  - [x] `app/repositories/user_repository.py` (get_by_email, get_by_google_sub, upsert_from_google_profile).
  - [x] `app/services/user_service.py` (business logic to find/create users, update last login, domain restriction, activation rules).
  - [x] `app/services/oauth_service.py` for encapsulating OAuth client creation and Google provider registration.

- [ ] Controllers (blueprint)
  - [x] `app/controllers/auth_controller.py` with `auth_bp`.
  - [x] Routes: `/auth/login` (redirect to Google), `/auth/callback` (exchange code, validate, log user in), `/auth/logout`.
  - [x] Integrate Flask-Login: user loader, `login_user`, `logout_user`.

- [ ] Application wiring
  - [x] Initialize OAuth service and Flask-Login in `app/__init__.py` (application factory). Note: OAuth is lazily initialized via `get_oauth()`.
  - [x] Register `auth_bp` in app factory.
  - [x] Provide `current_user` to templates via context processor.

- [ ] Access control
  - [x] Wrap write endpoints in controllers with `login_required`.
  - [x] Decide which endpoints are protected in phase 1 (e.g., prompt create/edit/delete, tag create/delete).
  - [x] Protect read endpoints: `/`, `/prompts`, `/prompts/<id>`, `/prompts/search`, `/tags`, merge page.

- [ ] UI/UX updates
  - [x] Update `app/templates/base.html` header: show a "Sign in with Google" button when logged out; show avatar/name & menu when logged in.
  - [x] Add visual feedback during login redirect (loading state).
  - [ ] Ensure mobile responsiveness and theming consistency.

- [ ] Logging & Observability
  - [x] Add meaningful logs around login/callback/logout (no PII leakage).
  - [x] Ensure errors are reported by existing logging setup.

- [ ] Testing
  - [x] Unit tests for `user_service` and repository.
  - [x] Integration test simulating callback with mocked Google userinfo (where feasible).
  - [ ] Manual test plan (below).

- [ ] Documentation
  - [x] Update `README.md` with setup instructions for Google OAuth.
  - [ ] Keep this feature file updated with statuses and notes.

- [ ] Deployment
  - [ ] Configure OAuth credentials and redirect URIs in Google Cloud Console for each environment.
  - [ ] Set environment variables on servers; restart app; verify health.


## 5) Data Model

Proposed `User` table (SQLAlchemy model):

- `id`: Integer PK
- `google_sub`: String, unique, not null (Google subject identifier)
- `email`: String, unique, not null
- `name`: String, nullable
- `picture_url`: String, nullable
- `role`: Enum/String with default `user`
- `is_active`: Boolean with default `True`
- `created_at`, `updated_at`, `last_login_at`: DateTime

Indexes on `google_sub` and `email`.


## 6) OAuth Flow Details

- Login: redirect user to Google authorization URL with `scope=openid email profile`, send `state` token stored in session.
- Callback: verify `state`; exchange `code` for tokens; fetch userinfo (`https://openidconnect.googleapis.com/v1/userinfo`).
- Upsert: if user with `google_sub` or `email` exists, update fields; else create new.
- Session: call `login_user(user)`; store only user id in session; rely on Flask-Login for `current_user`.
- Logout: call `logout_user()`; redirect to home.
- Optional: restrict by hosted domain via `hd` parameter or post-login verification (`OAUTH_GOOGLE_ALLOWED_HD`).


## 7) Security Considerations

- Enforce `state` parameter validation.
- Do not store access/refresh tokens unless needed (we do not need them for now).
- Use HTTPS in production; set `SESSION_COOKIE_SECURE=True` in prod config (already present).
- Consider `SameSite=Lax` (default) for OAuth; if encountering issues with cross-site redirects, document fallback to `SameSite=None` with `Secure`.
- Sanitize and log minimal user information; avoid logging emails or tokens.


## 8) Manual Testing (UI Walkthrough)

Prerequisites: Google OAuth Client ID/Secret created in Google Cloud Console, redirect URI configured (e.g., `http://localhost:5001/auth/callback`). Environment variables set.

1. Start dev server.
2. Open the app home page.
3. Confirm the header shows a "Sign in with Google" button when logged out.
4. Click the button:
   - Verify redirection to Google consent screen.
   - Approve consent.
5. Upon redirect back to the app:
   - Expect to land on the prior page or home; header shows user avatar/name.
   - Verify a `User` record is created/updated in DB.
6. Navigate to a write action (e.g., create prompt):
   - When logged out: should be redirected to login.
   - When logged in: allowed to proceed and save.
7. Use the user menu to Logout:
   - Verify session cleared; header shows "Sign in with Google".
8. Negative tests:
   - Tamper with `state` (simulate) -> callback should reject.
   - Try accessing protected URL without login -> redirect to login.


## 9) Rollout Plan

- Phase 1: Optional login enabled; protect write endpoints. Read-only public.
- Phase 2 (optional): Add domain restriction and admin role for sensitive operations.


## 10) Potential Risks and Mitigations

- Redirect URI mismatch — Double-check URIs in Google Cloud Console per environment.
- Cookie `SameSite` quirks — Use `Lax`; if issues arise, switch to `None` + `Secure` in prod only.
- CSRF/state failures — Ensure consistent session storage and state management.
- User uniqueness — Prefer `google_sub` as canonical; reconcile by email if needed on first login.


## 11) Open Questions

- Should we restrict logins to a specific Google Workspace domain?
- Which exact routes must be protected in phase 1? All create/edit/delete for prompts and tags?
- Do we need a minimal admin role now or defer to later?


## 12) Acceptance Criteria

- A user can sign in with Google and see their identity in the UI.
- A `User` record is persisted and updated on subsequent logins.
- Write actions are blocked for unauthenticated users.
- Logout clears the session.
- Documentation and manual testing steps are complete.


## 13) Work Log (to be updated during implementation)

- 2025-— Pending: Created roadmap; awaiting approval to implement.
- 2025-— Done: Added dependencies (Authlib, Flask-Login) to requirements; updated dev/prod requirements; installed in dev environment.
- 2025-— Done: Added `User` model, generated and applied Alembic migration; fixed Alembic template issue.
- 2025-— Done: Implemented `UserRepository`, `UserService` (Google upsert), `OAuth` service; added `auth_bp` with login/callback/logout; integrated `Flask-Login` and registered blueprint in app factory.
 - 2025-08-10T19:22:23Z — Done: Added context processor to expose `current_user` to templates.
 - 2025-08-10T19:25:25Z — Done: Added loading feedback for Google login button; wired JS handler in `main.js` and data attribute in `base.html`.
 - 2025-08-10T19:26:58Z — Done: Protected write routes in `prompt_controller` with `login_required`.
 - 2025-08-10T19:29:16Z — Done: Protected API write endpoints with `login_required` in `api_controller`.
 - 2025-08-10T19:31:00Z — Fix: Added dynamic fallback for `redirect_uri` (uses `url_for('auth.callback', _external=True)` when env not set); ensure GCP Authorized redirect URIs include `http://localhost:5001/auth/callback` and `http://127.0.0.1:5001/auth/callback`.
 - 2025-08-10T22:41:35Z — Incident: OAuth callback failed with `mismatching_state` due to redirect/session mismatch; improved callback error handling and unified dynamic redirect_uri.
 - 2025-08-10T22:41:35Z — Incident: DB mismatch (`no such table: users`). Root cause: migrations applied to a different SQLite file than the app was using. Resolution: added startup logs for sanitized DB URI and resolved absolute SQLite path; standardized on instance DB; backed up DB; ran `flask db upgrade` against `instance/prompt_manager.db`. Added `scripts/db_introspect.py` for DB introspection.
 - 2025-08-10T22:44:15Z — Observability: Added structured info logs for OAuth login initiation, token receipt, user login/logout; improved warning/exception messages (no PII).
 - 2025-08-10T22:51:50Z — Docs: Updated README with Google OAuth setup, DB migration notes, and troubleshooting; confirmed manual checks passed in dev.


