# Feature: Favorite Prompt Combinations

Status: Draft

Owner: Engineering

Related screens: `prompt/list.html`

## Problem Statement

Users frequently select the same groups of prompts together. Today, multi-select exists only in the client and is ephemeral. There is no way to save a frequently used selection and re-apply it quickly. We need user-scoped "favorite combinations" to save and recall sets of prompts.

## Goals

- Persist user-scoped favorite combinations of prompts (ordered list of prompt IDs).
- Quick apply: one click to select all prompts from a favorite in the list view.
- Create from current selection; rename; delete; reorder prompts within a favorite.
- Non-blocking UX with clear feedback and accessible controls.
- Server-backed storage with API; resilient client cache; secure (per-user isolation).

## Non-Goals (for v1)

- Sharing favorites between users/teams.
- Versioning favorites or tracking usage analytics.
- Cross-page global hotkeys beyond the list view.

## Current State (Analysis)

- UI: `app/static/js/prompt-list.js` maintains `selectedPrompts` in a Set and drives combined content panel. No persistence of combinations.
- Template: `app/templates/prompt/list.html` renders prompt cards with checkboxes and a combined content panel.
- Backend: Repository/Service architecture with SQLAlchemy models, REST API in `app/controllers/api_controller.py`. No models for favorites.
- Auth: `flask_login` guards most endpoints; we should require login for all favorites operations.

## Design Overview

### Data Model

Two tables to represent user-defined combinations and their ordered items:

- FavoriteSet
  - id: int (PK)
  - user_id: int (FK -> users.id, indexed)
  - name: str (required, unique per user)
  - description: str (optional)
  - is_active: bool (default true)
  - created_at: datetime (default now)

- FavoriteSetItem
  - id: int (PK)
  - favorite_set_id: int (FK -> favorite_set.id, indexed, cascade delete)
  - prompt_id: int (FK -> prompts.id, indexed)
  - position: int (for ordering)
  - created_at: datetime (default now)

Rationale: normalized schema enables ordering, validation, and efficient queries. Simpler JSON storage was considered but rejected to keep queries and integrity checks straightforward.

### API (JSON)

Base path: `/api/favorites`

- GET `/api/favorites` → 200: `{ favorites: [ { id, name, description, items: [ {prompt_id, position} ] } ] }`
- POST `/api/favorites` (login required) body: `{ name, description?, prompt_ids: [int] }` → 201 with created favorite
- PUT `/api/favorites/<id>` body: `{ name?, description?, prompt_ids? }` → 200 with updated favorite
- DELETE `/api/favorites/<id>` → 204
- Optional convenience: POST `/api/favorites/<id>/apply` → 200 `{ prompt_ids: [...] }` (client can also apply from cached list without extra round-trip)

Validation rules:
- `name` required on create; unique per user (case-insensitive).
- `prompt_ids` must reference active prompts (or allow inactive with a warning badge in UI).

### Service Layer

`FavoriteSetService` encapsulates business logic:
- `list_for_user(user_id)`
- `create(user_id, name, description, prompt_ids)`
- `update(user_id, favorite_id, name?, description?, prompt_ids?)`
- `delete(user_id, favorite_id)`
- Enforces ownership, uniqueness, and ordering.

### Repository Layer

`FavoriteSetRepository` and `FavoriteSetItemRepository` extend `BaseRepository`, adding:
- `get_by_user(user_id)`
- `get_with_items(favorite_id, user_id)`
- `exists_by_name(user_id, name)`

### UI/UX

Placement: Prompt List page toolbar and Combined Content panel.

Controls:
- "Save selection as Favorite" button (enabled when `selectedPrompts.size > 0`). Opens modal to enter `name` and optional description.
- "Favorites" dropdown with search; items show count and quick actions: Apply, Edit, Delete.
- Manage modal: rename, reorder prompts inside a favorite (drag-and-drop), save.
- Feedback: toasts/snackbars on success/error; disabled states during requests.
- A11y: buttons are reachable via keyboard; ARIA labels; focus management in modals.

Behavior:
- Apply replaces current selection by default (configurable via toggle "Merge with current selection").
- If any `prompt_id` is not visible due to filters, we still select it; the counter reflects the total selected; a non-blocking notice indicates some items are filtered out.

Performance:
- Fetch favorites once on page load; cache in memory. Optionally keep a read-through cache in `localStorage` with ETag/version to avoid stale UI between sessions.

Error Handling:
- API errors are shown as inline form errors or toasts. 401/403 leads to login or permission warning.

## Implementation Plan (Checklist)

1) Database & Models
- [x] Create SQLAlchemy models: `FavoriteSet`, `FavoriteSetItem` in `app/models/` with `to_dict()` including ordered items.
- [x] Alembic migration: create tables, indexes, FKs with cascade on `favorite_set` → `favorite_set_item`.
    - Applied to DB: `C:\Users\eL\Dropbox\Programming\CursorProjects\prompt-manager\instance\prompt_manager.db`.

2) Repositories
- [x] Implement `FavoriteSetRepository` and `FavoriteSetItemRepository` in `app/repositories/` following existing pattern.

3) Service Layer
- [x] Implement `FavoriteSetService` in `app/services/` with validation rules and ownership checks.

4) API Controller
- [x] Add favorites endpoints to `app/controllers/api_controller.py` with `@login_required` and JSON validation decorators.
- [x] Ensure responses use `to_dict()` and proper status codes.

5) Web Controller (optional v1)
- [x] SSR param passthrough: `favorite_id` handled in `prompt_controller.index()`, auto-apply on load.

6) Frontend (JS + Templates)
- [x] In `app/templates/prompt/list.html`, add:
  - Favorites dropdown section in the toolbar.
  - Save current selection button.
- [x] In `app/static/js/prompt-list.js`, integrate favorites into `PromptListManager`:
  - Load favorites on init via `/api/favorites`.
  - Save current selection → POST.
  - Apply favorite → set checkboxes, update UI.
  - Delete favorite → remove from list.
- [x] Visual styling in `app/static/css/style.css`: minor spacing/hover tweaks (v1 minimal).
- [x] Save Favorite modal instead of `window.prompt`.
- [x] “Merge with current selection” toggle in dropdown.
- [x] Warning toast when some favorite items are hidden by active filters.

7) Security & Permissions
- [x] Endpoints guarded with `@login_required`; service enforces ownership (user_id checks).

8) Testing
- [x] Unit tests: service logic (`tests/unit/test_favorite_service.py`).
- [x] Integration tests: API endpoints (`tests/integration/test_favorite_api.py`).
- [ ] E2E/manual test passes (see below).

9) Docs & Observability
- [x] Update `docs/api/API.md` with `/api/favorites` and SSR deep-link note.
- [x] Plan updated with latest status.

10) Rollout
- [ ] Backward-compatible migration; deploy; verify healthchecks (pending deployment window).
- [ ] Optional feature flag `ENABLED_FAVORITES=true` (not required in dev; decide before prod).

## Manual Test Scenarios (UI)

Happy path
1. Open Prompt List while logged in.
2. Select 3 prompts via checkboxes; click "Save selection as Favorite".
3. Enter name "Daily drafting"; save. Toast appears; favorite appears in the dropdown.
4. Clear selection; open dropdown; click "Daily drafting" → all 3 prompts become selected; combined panel updates; counter matches 3.

Editing
1. Open favorites dropdown → Edit on an item.
2. Rename to "Daily drafting v2"; remove one prompt; save.
3. Apply again; only 2 prompts selected now; verify order respected in combined content.

Deleting
1. Delete a favorite; confirm dialog.
2. Dropdown no longer lists it. Refresh page → still gone.

Edge cases
1. Try to create a favorite with an existing name (case-insensitive) → inline error.
2. Apply a favorite containing a prompt that is currently filtered out by tag/status → selection counter shows full count; non-blocking notice mentions hidden items.
3. Logout and try calling API directly → 401.

Accessibility
1. Navigate to "Favorites" using keyboard; open dropdown; select and apply without mouse.
2. In modals, focus traps correctly; ESC closes.

## Risks & Mitigations

- Name collisions: enforce per-user unique names at DB and service levels.
- Large favorites: selection updates done in batches to avoid layout thrash; use `requestAnimationFrame`.
- Stale cache: cache keyed by user and invalidate upon any mutation.

## Open Questions

- Do we want a "merge vs replace selection" preference persisted per user? (v1: toggle remembered in `localStorage`).
- Should inactive prompts be allowed in favorites? (v1: allow; mark with a badge on apply.)

## Initial Prompt (verbatim, translated)

"I want to be able to add combinations of selected prompts to favorites. For example, I often use these combinations.

=== Analyse the Task and project ===

Deeply analyze our task, our project and decide how best to implement this.

=== Create Roadmap ===

Create a detailed, step-by-step plan for implementing this task in a separate file-document. We have a folder `docs/features` for this. If there is no such folder, create it. Document in the file as thoroughly as possible all discovered and tried problems, nuances, and solutions, if any. As you progress with implementing this task, you will use this file as a todo checklist, updating it and documenting what was done, how it was done, what problems arose, and what decisions were made. For history, do not delete items; you can only update their status and comment. If during implementation it becomes clear that something needs to be added from tasks, add it to this document. This will help us preserve context, remember what we have already done, and not forget to do what was planned. Remember that only the English language is allowed in the code and comments, and project labels.

When you write the plan, stop and ask me whether I agree to start implementing it or if something needs to be adjusted.

Also include in the plan steps for manual testing, i.e., what needs to be clicked in the interface.

=== SOLID, DRY, KISS, UI/UX, etc ===

Follow the principles: SOLID, DRY, KISS, Separation of Concerns, Single Level of Abstraction, Clean Code Practices.
Follow UI/UX principles: User-Friendly, Intuitive, Consistency, Accessibility, Feedback, Simplicity, Aesthetic & Modern, Performance, Responsive Design.
Use Best Practices."

## Acceptance Criteria

- User can save current selection as a named favorite.
- User can see a list of favorites and apply one with a single click.
- User can rename and delete favorites.
- Data persists per user across sessions; API covered by tests.
- UI is accessible and responsive; no regressions in prompt selection flow.

---

Please review this plan. Once approved, we will start implementing according to the checklist above.


