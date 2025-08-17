## Feature: Clipboard Reliability and Clear Selection Button Restoration

### Initial Prompt

User report (translated to English):

"For some reason, I get a red pop-up at the bottom saying 'Failed to copy to clipboard' when I click on a prompt card. However, everything is actually copied to the clipboard fine. Also, there used to be a reset/clear selected prompts button, but now it’s gone.

=== Analyse the Task and project ===

Deeply analyze our task and project and decide how best to implement it.

==================================================

=== Create Roadmap ===

Create a detailed, step-by-step action plan for implementing this task in a separate document file. We have a folder docs/features for this. If there is no such folder, create it. Capture in the document as comprehensively as possible all discovered and tried problems, nuances, and solutions, if any. As you progress in implementing this task, you will use this file as a to-do checklist; you will update this file and document what has been done, how it was done, what problems arose, and what decisions were made. For the history, do not delete items; you can only update their status and comment. If, during implementation, it becomes clear that something needs to be added from tasks, add it to this document. This will help us maintain context, remember what has already been done, and not forget to do what was planned. Remember that only the English language is allowed in the code and comments, project labels. When you write the plan, stop and ask me if I agree to start implementing it or if anything needs to be adjusted in it.

Include in the plan this prompt that I wrote to you, but translate it into English. You can call it something like 'Initial Prompt' in the plan document. This is needed so that we keep the task-setting context in our roadmap file as accurately as possible without the 'broken telephone' effect.

Also include steps for manual testing in the plan, i.e., what needs to be clicked in the interface."

---

### Summary

- Symptom 1: An erroneous error toast "Failed to copy to clipboard" appears when clicking a prompt card, even though the content is actually copied successfully.
- Symptom 2: The UI button that clears the current selection (and previously also emptied the clipboard) is missing from the prompts list action bar.

### Context and Current Implementation (as discovered)

- The prompts list page is powered by `app/static/js/prompt-list.js` and template `app/templates/prompt/list.html`.
- Clipboard writes are performed through `navigator.clipboard.writeText` in multiple places:
  - `PromptListManager.copyToClipboard(text, buttonElement)` – shows success toast on resolve, error toast on reject.
  - Auto-copy flows:
    - On checkbox click (`handleCheckboxClick`) a delayed `copyAllSelectedPrompts()` runs.
    - Combination selection flow (`handleCheckboxChange` -> `handleCombinationCopy`) may trigger another clipboard write almost simultaneously.
- Toasts: `PromptListManager.showToast` delegates to `window.showToast` if present (from `app/static/js/main.js`), otherwise uses a fallback bootstrap toast builder.
- Clear Selection button: `createActionButtons()` programmatically creates two buttons (Copy Selected and Clear Selection) and inserts them into the action bar before `#mergeBtn`.
  - It queries `const actionsBar = document.querySelector('.d-flex.justify-content-between.align-items-center')` then `const actionsDiv = actionsBar.querySelector('div')` and attempts `insertBefore` relative to `#mergeBtn`.
  - In template, the right-hand controls container is `<div class="d-flex align-items-center gap-2">...` containing `#mergeBtn`.

### Problem Statement

1) Intermittent false-negative error toast during copy:
   - Likely caused by multiple rapid `navigator.clipboard.writeText` calls (e.g., combination copy + auto multi-copy) executed in close succession, where one resolves and another rejects due to timing/gesture constraints or overlapping writes.
   - Another potential cause: passing a non-button element (e.g., checkbox) to the success-visual routine (`showCopySuccess`) in the combination handler, but this should not directly cause the error toast (it would more likely lead to a harmless UI glitch). The error toast is strictly tied to a rejected clipboard promise.

2) Clear Selection button not visible:
   - The injection logic assumes a specific DOM structure. If `actionsBar.querySelector('div')` returns an unexpected node (or layout changed), the insertion may fail, preventing the button from appearing.
   - If the feature silently fails (e.g., an exception thrown before button creation), subsequent UI code might still run, masking the cause.

### Goals and Acceptance Criteria

- Clipboard UX:
  - No erroneous "Failed to copy to clipboard" toasts when copying succeeds.
  - Copy feedback is consistent and displayed once per user intent.
  - Combination selection and auto multi-copy do not conflict.

- Clear Selection button:
  - Button is reliably present in the action bar on the prompts list page.
  - Button enables/disables based on selection count.
  - Clicking it clears selected checkboxes, empties combined content, and (optionally) clears the clipboard with proper feedback.

- Regression safety:
  - Existing copy buttons and the Combined Content panel continue to work.
  - Keyboard shortcuts continue to work (Ctrl/Cmd+C, Ctrl/Cmd+Shift+C, Ctrl/Cmd+P, etc.).

### Root Cause Hypotheses (to verify)

- H1: Dual/overlapping clipboard writes (combination copy + auto multi-copy) lead to one resolved write and one rejected write; the rejected path triggers the red error toast despite overall success.
- H2: The DOM insertion target for the Clear Selection button changed (or is queried too broadly), so `insertBefore` misses `#mergeBtn` or uses the wrong container, resulting in the button not being mounted.
- H3: `showCopySuccess` receives non-button nodes (e.g., checkbox) for some flows, causing UI feedback inconsistencies (less likely to trigger error toast, but worth polishing).

### Implementation Plan (Step-by-step)

1) Instrumentation and defensive guards
   - Add a simple Copy operation mutex/queue:
     - Introduce an `isClipboardWriteInProgress` flag or promise queue in `PromptListManager`.
     - Serialize clipboard writes: if a write is in-flight, either coalesce subsequent requests within a short window (e.g., 200–300ms) or enqueue one final write.
     - Track `lastSuccessfulCopyAt` timestamp to suppress error toasts if a failure occurs within a short grace period after a success (to avoid mixed success/error UX when coalescing).

2) De-duplicate copy triggers
   - In `handleCheckboxChange` + `handleCheckboxClick`:
     - If a combination copy was triggered for this user action, skip the subsequent auto multi-copy for that same action (use a single-intent guard, e.g., `suppressCombinationCopy` + a one-shot token for the current gesture).
   - Ensure that only one copy path runs per click/gesture.

3) Make `showCopySuccess` robust
   - If `buttonElement` is not a button (e.g., `input[type=checkbox]`), skip icon swap and only show a toast, or locate an appropriate sibling button for visual feedback.
   - Avoid any DOM operations that rely on `innerHTML` for non-container elements.

4) Harden Clear Selection button mounting
   - Update `createActionButtons()` to locate the right container more robustly:
     - Prefer querying the specific container `.d-flex.align-items-center.gap-2` if present, falling back to current approach.
     - If `#mergeBtn` not found, append both buttons at the end of the controls container.
   - Add null checks and early returns with console warnings rather than failing silently.

5) UX refinements
   - Ensure success toasts are shown only once per user action.
   - Keep clear and consistent tooltip text updates for checkbox and buttons.
   - Maintain keyboard shortcuts (including Ctrl/Cmd+Shift+C to clear selection and clipboard).

6) Documentation and code quality
   - Keep changes small, well-separated, and covered with comments explaining the rationale (race conditions, serialization of clipboard operations).
   - Follow SOLID/DRY/KISS and keep separation of concerns in `PromptListManager` methods.

### To-Do Checklist (will be updated during implementation)

- [x] Verify overlapping clipboard write calls during card click flows (single vs. combination selection).
- [x] Implement clipboard write serialization/coalescing.
- [x] Suppress duplicate toasts/errors for coalesced operations.
- [x] Add gesture-intent guard to choose exactly one copy path per click.
- [ ] Make `showCopySuccess` no-op for non-button elements, or redirect to a nearby UI button.
  - Status: Done (no-op for non-button elements).
- [ ] Improve Clear Selection button injection logic (robust container targeting and fallback).
  - Status: Done. Buttons now reliably mount in the main actions bar (not sidebar) with relocation if previously misplaced.
- [x] Re-test tooltips and button enabled/disabled states. (Marked done without manual verification per user request)
- [x] Ensure no regressions for Combined Content panel copy/clear. (Marked done without manual verification per user request)
- [x] Verify keyboard shortcuts. (Marked done without manual verification per user request)
- [x] Update this document with outcomes and any discovered nuances.
 - [x] Adjust actions bar layout to place buttons on a new line below the title.
 - [x] Improve button text contrast in dark theme (ensure `--text-inverse` is white for colored buttons).

### Manual Testing Plan

General environment:
- Browser: latest Chrome/Edge.
- Page: prompts list (`/prompts`). Ensure multiple prompts exist.

Scenarios:
1) Single selection via card click
   - Click on a prompt card background (not on inner buttons).
   - Expected: checkbox toggles ON, exactly one success toast appears; no error toast.
   - Clipboard: contains that prompt’s content (or formatted block if designed so).

2) Second selection shortly after first (combination flow)
   - Click first card, then quickly click second card.
   - Expected: exactly one copy operation (combination or multi-copy) with success toast; no error toast; no double toasts.

3) Copy Selected button
   - Select 2–3 prompts and click "Copy Selected".
   - Expected: one success toast; clipboard contains combined content; no error toast.

4) Clear Selection button visibility and behavior
   - On page load, verify the presence of "Clear Selection" button (disabled).
   - Select multiple prompts; button becomes enabled and tooltip updates.
   - Click "Clear Selection": all checkboxes deselected, combined content cleared, optional clipboard cleared, appropriate success toast shown.

5) Combined Content panel
   - Toggle panel on; select prompts; verify textarea content, counts, and "Copy" enabled state.
   - Use panel "Copy"; verify success without error toast.
   - Use panel "Clear"; content cleared and counts update.

6) Keyboard shortcuts
   - Ctrl/Cmd+C with selections -> copies once, success toast only.
   - Ctrl/Cmd+Shift+C -> clears selection and (optionally) clipboard, success toast.
   - Ctrl/Cmd+P -> toggles Combined Content panel.

7) Favorites application flow (edge for auto-copy)
   - Apply a Favorite with multiple items; ensure it does not emit conflicting copies/toasts.

### Risks and Mitigations

- Risk: Over-serialization might drop legitimate user-initiated copies.
  - Mitigation: Short coalescing window and last-write-wins behavior.
- Risk: DOM structure changes again later.
  - Mitigation: Use resilient selectors and fallbacks; console warnings for diagnostics.
- Risk: Platform-specific clipboard issues.
  - Mitigation: Graceful fallbacks and clear UX messaging.

### Deliverables

- Updated `app/static/js/prompt-list.js` with:
  - Clipboard write serialization and de-duplication of toasts.
  - Robust `createActionButtons()` and `showCopySuccess()`.
- No template changes required unless button placement needs minor adjustment.
- Updated docs: this file with status updates and outcomes.

### Status Log

- 2025-08-17: Implemented clipboard write serialization in `PromptListManager`:
  - Added `isClipboardWriteInProgress`, `clipboardQueue`, `lastSuccessfulCopyAt`, and `clipboardErrorSuppressionMs`.
  - Introduced `enqueueClipboardWrite` and `processClipboardQueue` to serialize writes.
  - Updated `copyToClipboard` and `clearSelectionAndClipboard` to use the queue.
  - Suppress error toast if a failure occurs within a short window after a success to avoid mixed UX.
  - Next: add gesture-intent guard to ensure only one copy path runs per user action.
- 2025-08-17: Added gesture-intent guard:
  - Introduced `skipNextAutoCopy` flag.
  - When combination copy is triggered from fast sequential selections, we set the flag and skip the subsequent auto multi-copy from the click handler, preventing duplicate copy operations and toasts.
- 2025-08-17: Hardened Clear Selection button insertion:
  - `createActionButtons()` now targets the right-side controls container robustly (prefers `.d-flex.align-items-center.gap-2`, falls back to `#mergeBtn` parent, then to a reasonable DIV fallback).
  - Prevents duplicate creation if buttons already exist.
  - Initializes tooltips defensively.
  - If buttons were previously rendered elsewhere, they are moved into the correct controls container.
- 2025-08-17: UX refinement for copy success visuals:
  - `showCopySuccess` now no-ops for non-button elements (e.g., checkboxes), avoiding unintended DOM changes while keeping success toasts intact.
 - 2025-08-17: Actions bar layout updated:
   - Moved actions (Favorites, Toggle Panel, Merge, Create) to a separate row below the "Prompts" title for improved clarity and to avoid sidebar interference.
 - 2025-08-17: Dark theme contrast fix:
   - Updated `--text-inverse` in dark theme to white to ensure readable text on primary/colored buttons.
 - 2025-08-17: Finalization note:
   - Per user request, manual UX verification and keyboard shortcut checks were skipped. Remaining checklist items were marked complete based on implementation state.


