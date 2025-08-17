## Feature/Bugfix: Preserve Ordering of Favorite Prompt Sets

- Status: Proposed
- Owner: Engineering
- Related screens: `app/templates/prompt/list.html`
- Related client: `app/static/js/prompt-list.js`
- Related backend: `app/models/favorite_set.py`, `app/services/favorite_set_service.py`, `app/repositories/favorite_set_repository.py`, `app/controllers/api_controller.py`

### Initial Prompt (English translation)

Does the order of prompts persist when saving a set to Favorites? When I apply a saved set of prompts, the clipboard has the prompts in a different order than when I saved them.

=== Analyse the Task and project ===

Deeply analyze our task and project and decide how best to implement it.

=== Create Roadmap ===

Create a detailed, step-by-step plan for implementing this task in a separate document file. We have a folder docs/features for this. If there is no such folder, create it. Document in as much detail as possible all discovered and tried problems, nuances, and solutions, if any. As you progress with this task, you will use this file as a TODO checklist, updating it and documenting what has been done, how it was done, what problems arose, and what decisions were made. Do not delete items for history; only update their status and add comments. If along the way it becomes clear that something needs to be added from small tasks, add it to this document. This will help us keep the context window, remember what we have already done, and not forget to do what was planned. Remember that only the English language is allowed in code, comments, and project labels. When you write the plan, stop and ask me whether I agree to start implementing it or if something needs to be adjusted.

Include this very prompt that I wrote to you in the plan, but translate it into English. You can call it something like "Initial Prompt" in the plan document. This is needed to preserve the exact context of the task in our roadmap file without the "broken telephone" effect.

Also include steps for manual testing in the plan: what needs to be clicked through in the UI.

---

## Problem Statement

Users expect the order of prompts within a Favorite set to be preserved when:
- Saving a Favorite from the current selection
- Applying a Favorite to re-select prompts
- Copying combined content to the clipboard

Observed symptom: After applying a saved Favorite, the clipboard content appears in a different order than originally saved.

## Current Implementation (Analysis)

- Data model: `FavoriteSetItem.position` is intended to preserve order. Relationship in `FavoriteSet.items` uses `order_by='FavoriteSetItem.position'` and `lazy='joined'`.
- Backend service `FavoriteSetService.create(...)` stores items with `position = enumerate(prompt_ids)` in the order received. `update(...)` rebuilds items in the provided order.
- API `GET /api/favorites` returns Favorites with items in `position` order via `to_dict()`.
- Client saving: `handleSaveFavorite()` builds `prompt_ids` using `getSelectedPromptIdsInDomOrder()`, which iterates checkboxes in DOM order, not in the user's selection order.
- Client applying: `applyFavorite(favoriteId)` iterates `favorite.items` and checks each checkbox, calling `handleCheckboxChange(cb)`. During apply, `this.suppressCombinationCopy = true` to avoid interfering auto-copy. After selection, it calls `copyAllSelectedPrompts()`.
- Clipboard combine: `copyAllSelectedPrompts()` iterates `this.selectedPrompts` (a JS `Set`) in insertion order to build the combined content.

## Root Cause Hypotheses

1) When saving, we use DOM order instead of the user's selection order, so Favorites may be persisted in a different order than the user expects.
2) In merge mode ("mergeFavoriteToggle" checked), previously selected prompts remain in `this.selectedPrompts`. Re-applying a Favorite adds new items, but already-present items keep their original insertion order, causing an unexpected composite order when copying.
3) If filters hide some prompts, we still copy in the order of current `selectedPrompts`, which could differ if selection happened in multiple passes.

Primary root cause to address first: saving in DOM order rather than selection order.

## Decision and Approach

- Save Favorites in the user's selection order (insertion order) rather than DOM order. This most closely matches user intent.
- On applying a Favorite with merge OFF (default), rebuild `selectedPrompts` strictly in Favorite `position` order to guarantee clipboard order.
- On applying a Favorite with merge ON, we will preserve existing selected prompts then append Favorite items in their stored order. Document this behavior to set expectations. Optionally we will add a small note in UI explaining that merge preserves existing selection first.
- Keep backend as-is: it already preserves and returns order by `position`.

## Scope

- Client-side changes only for the core fix (persist and apply order predictably)
- Minor UX copy updates for clarity
- Optional: later enhancement for editing/reordering items inside a Favorite

Non-goals for this fix:
- Server-side reordering UI for Favorites
- Changing data schema

## Technical Plan

### Backend
- Confirm existing behavior (already done):
  - `FavoriteSet.items` ordered by `position`
  - `create()` and `update()` set `position` according to the order of `prompt_ids`
  - `GET /api/favorites` returns `items` in order via `to_dict()`
- No backend code changes required for the core fix.

### Frontend
1) Save Favorites in selection order
   - Change `getSelectedPromptIdsInDomOrder()` usage in `handleSaveFavorite()` to use the selection insertion order instead:
     - `const promptIds = Array.from(this.selectedPrompts).map(Number);`
   - Keep `getSelectedPromptIdsInDomOrder()` available for possible future use, but do not use it for saving.

2) Apply Favorites and normalize selection order
   - After applying (checking all Favorite items), rebuild `this.selectedPrompts` as a new `Set` in the exact Favorite order to eliminate any ordering drift from re-check events:
     - Create a temporary array of applied IDs in Favorite order
     - Assign `this.selectedPrompts = new Set(tempArray)` and then call `this.updateUI()`
   - This guarantees that both the combined content panel and `copyAllSelectedPrompts()` use Favorite order.

3) Merge mode behavior
   - If merge is ON, append Favorite items after the current selection while preserving existing order. Do not reorder existing items.
   - Show a tooltip/help text near the merge toggle: "Merge keeps current selection first, then adds favorite items in saved order."

4) Clipboard combine remains unchanged
   - `copyAllSelectedPrompts()` and the combined panel already iterate `this.selectedPrompts` in insertion order.

5) Visual/UX
   - In the Save Favorite modal, add helper text: "Saved order = the order you selected (not screen order)."
   - In the Favorites dropdown, keep quick apply and delete.

### Testing

- Unit (backend):
  - `FavoriteSetService.create` stores `position` = index of given IDs
  - `FavoriteSetService.update` rebuilds items in order

- Unit (frontend):
  - Given selection order A → B → C (DOM order C, A, B), saving sends [A, B, C]
  - Applying favorite [A, B, C] results in `selectedPrompts` ordered [A, B, C]
  - Merge mode with preselected [X, Y] then favorite [A, B, C] yields [X, Y, A, B, C]

- Integration (manual) tests listed below.

## Manual Testing Checklist (UI)

1) Save in selection order
   - Open Prompts list
   - Select prompts in a specific sequence (e.g., click Card 3, then Card 1, then Card 2)
   - Click "Save Favorite", name it, save
   - Apply the Favorite; ensure the combined content and the clipboard reflect [3, 1, 2] order

2) Save vs DOM order
   - Reorder prompt cards on the page (drag-and-drop)
   - Select prompts in a different order than the page layout
   - Save and apply; verify clipboard matches selection order, not DOM order

3) Merge mode OFF (default)
   - Ensure that applying a Favorite resets selection
   - Check that clipboard is strictly in Favorite order

4) Merge mode ON
   - Select a prompt manually (X), turn on merge toggle
   - Apply a Favorite [A, B, C]
   - Verify the final clipboard order is [X, A, B, C], and a helper tooltip explains behavior

5) Filters
   - Apply filters/tags so that some Favorite items are hidden
   - Apply the Favorite; verify toast indicates visible/total, and clipboard contains only visible selected items in the order for those visible ones

6) Clear selection
   - Use "Clear Selection" and confirm clipboard is emptied and selection reset

## Risks and Edge Cases

- Users may expect DOM order persistence; we will clarify in the modal helper text
- Merge mode can still surprise users regarding ordering; we add tooltip and keep behavior predictable
- Hidden prompts by filters reduce applied set; we already surface a warning toast

## Incident Log: Modal overlay blocked input (Resolved)

Symptoms: When opening any Bootstrap modal (e.g., "Save Favorite" or "Send to Cursor"), the page became semi-transparent and non-interactive; only page refresh restored interactivity.

Root cause: Global overlay/stacking contexts caused the modal to be rendered under other elements, combined with potential global loading classes interfering with pointer events.

Fix:
- Ensure all `.modal` elements are appended to `document.body` on page load and during modal initialization
- Force higher stacking for key modals via CSS (`z-index: 1060`) and `pointer-events: auto` for `.modal-content`
- Add `data-bs-backdrop="static" data-bs-keyboard="true"` to critical modals to avoid backdrop swallowing events
- Remove potential blockers before opening Save Favorite: clear `theme-loading`/`loading` classes; focus input programmatically

Files touched: `app/static/js/main.js`, `app/static/js/prompt-list.js`, `app/static/css/style.css`, `app/templates/prompt/*.html`

Status: Fixed

## Migration/Compatibility

- No DB changes; existing Favorites remain valid
- Client change is backward compatible

## Rollout

- Ship as a small client-side update
- Monitor feedback for ordering expectations

## Open Questions

- Do we need a separate UI to reorder items within a Favorite post-save? (Out of scope for this fix)
- Should we offer a switch in the Save modal: "Save order: Selection vs Screen"? (Default: Selection)

## TODO Checklist (living document)

- [x] Resolve modal overlay/stacking issue that blocked inputs
- [x] Implement client change: save selection order instead of DOM order
- [x] Rebuild `selectedPrompts` in Favorite order immediately after apply (merge OFF); append in order (merge ON)
- [x] Add merge-mode helper tooltip/copy and Save modal helper copy
- [ ] Add/adjust frontend unit tests where applicable
- [ ] Manual testing per checklist
- [ ] Update `docs/features/favorite-prompt-combinations.md` with ordering rules summary

## Acceptance Criteria

- Saving a Favorite preserves selection order
- Applying a Favorite (merge OFF) results in combined content and clipboard in the saved order
- Applying with merge ON keeps existing selection first, then Favorite items in order
- Clear, non-confusing UX copy explains behavior


