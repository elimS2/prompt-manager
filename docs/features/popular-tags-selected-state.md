# Popular Tags: Selected State and Tag Toggling

## Initial Prompt

User request (translated to English):

"On the page at `http://127.0.0.1:5001/prompts` there is a block with tags that can be clicked and selected. But it is unclear which tags are currently selected. This is the section called Popular Tags.

=== Analyse the Task and project ===

Deeply analyze our task and project and decide how best to implement this.

==================================================

=== Create Roadmap ===

Create a detailed, step-by-step action plan for implementing this task in a separate document file. We have a folder `docs/features` for this. If there is no such folder, create it. Document all discovered and tested problems, nuances, and solutions as thoroughly as possible in the document, if any exist. As you progress with the implementation of this task, you will use this file as a to-do checklist, update it, and document what has been done, how it was done, what problems arose, and what solutions were adopted. For history, do not delete items; only update their status and comment. If during implementation it becomes clear that something needs to be added, add it to this document. This will help us preserve context and remember what has already been done and not forget what was planned. Remember that only the English language is allowed in code, comments, and project labels. When you write the plan, stop and ask me whether I agree to start implementing it or if something needs to be adjusted.

Also include steps for manual testing in the plan — i.e., what to click in the interface."

---

## Overview

On the prompts list page, the Popular Tags block allows users to click tags and filter the list by `tags` query params. However, there is no visual indication of which tags are currently selected. This leads to confusion and discoverability issues.

This feature will:
- Show a clear selected state for tags in the Popular Tags block.
- Support toggling a tag on/off (add/remove from filter).
- Keep the selected state consistent across initial server-rendered HTML and dynamic updates performed by JavaScript.
- Maintain accessibility (aria states, keyboard navigation) and visual consistency with the design system.

Non-goals:
- Changing the underlying filtering semantics beyond toggling tags.
- Building a full “chips” selected-tags toolbar (optional future enhancement).

## Current State Analysis

- Template: `app/templates/prompt/list.html` renders the Popular Tags list from `popular_tags`.
- Controller: `app/controllers/prompt_controller.py#index` provides `popular_tags` and `filters` (including existing `tags` query parameters).
- JS: `app/static/js/prompt-list.js` handles clicks on `.tag-filter` elements via `applyTagFilter(tagElement)`, which appends a `tags` param and navigates. It does not toggle off a tag if already selected, and it does not mark selected tags visually.
- Dynamic tags: Popular tags can be re-rendered via `renderPopularTags()` when status (Active/Inactive/All) changes through an AJAX endpoint.
- CSS: Tags are styled via `.tag` and `.tag-filter`; no distinct selected state is defined.

Pain points:
- No visual state for selected tags.
- No toggle behavior (clicking an already-selected tag should remove it).
- Dynamic re-render does not preserve selected state styling.

## Goals and Acceptance Criteria

Functional:
- When a tag is present in the current URL query params `tags`, it is visually highlighted in the Popular Tags block.
- Clicking a non-selected tag adds it to the URL (as today) and navigates.
- Clicking a selected tag removes it from the URL and navigates (toggle off).
- Dynamic re-render of Popular Tags (after status changes) correctly reflects the selected state.

Accessibility:
- Tag elements expose `role="button"` and toggle `aria-pressed` to reflect state.
- Keyboard navigation continues to work: Enter/Space activates, Escape clears focus.

UX/UI:
- Selected tags have a distinct visual treatment (outline/border, contrast-safe) in light/dark themes.
- Counts remain visible and readable in both states.

Performance:
- No significant regressions; DOM updates remain minimal and efficient.

## Design Decisions

- Use URL as the single source of truth for selected tags. Both SSR and JS will derive selection from `URLSearchParams`.
- Keep the existing anchor structure, augment with `selected` class and `aria-pressed`.
- Implement toggle logic in JS to add/remove the tag from query params.
- SSR will add `selected` class conditionally for initial load so that no flash of incorrect state occurs before JS binds.

## Implementation Plan (Checklist)

1) Backend — Data Availability
- [x] Confirm `filters.tags` contains the list of selected tags on initial render.
- [x] No schema changes required; ensure controller keeps passing `filters` to the template.

2) Template — Initial Selected State (SSR)
- [x] Update `app/templates/prompt/list.html` to add `selected` CSS class when `item.tag.name` is in `filters.tags`.
- [x] Add `aria-pressed="true|false"` and `role="button"` to each `.tag-filter`.
- [ ] Consider adding a small “Selected” pill or check icon inside the tag (optional if style-only is sufficient).

3) JavaScript — Toggle Behavior and State Sync
- [x] Update `applyTagFilter(tagElement)` in `app/static/js/prompt-list.js`:
  - Read current `URLSearchParams` for all `tags`.
  - If `tagName` is present: remove it and navigate.
  - Else: append it and navigate.
- [x] Update `renderPopularTags(tags)` to compute selected state by reading current URL params and applying `selected` class and `aria-pressed` to the generated tag markup.
- [x] Ensure `initTagFilters()` is re-bound after dynamic render.

4) CSS — Selected Style
- [x] Add `.tag-filter.selected` style in `app/static/css/style.css`:
  - Clear visual differentiation (border/outline increase, slight shadow or inner ring, and improved contrast).
  - Respect theme variables and accessibility contrast ratios.
- [ ] Optional: Add `.tag-filter .tag-check-icon` styles if we include an icon.

5) UX Polish and A11y
- [x] Ensure `aria-pressed` is correct on initial SSR and after dynamic updates.
- [x] Maintain `tabindex="0"` for keyboard access.
- [x] Maintain existing tooltip/title behavior; ensure not to conflict with state indication.

6) Edge Cases & Robustness
- [x] Handle duplicate `tags` params gracefully (de-duplicate in JS before navigation).
- [ ] Case sensitivity: POLICY PENDING — propose to treat tag names as case-insensitive in UI matching (normalize to exact names from backend when appending to URL), while backend stores canonical casing.
- [x] If no tags are selected, no elements have `selected` class.
- [x] If a tag disappears due to status change, selection remains in the URL but won’t be represented in the Popular block; this is acceptable. Clear All Filters already exists.

7) Documentation & References
- [x] Cross-link this feature with `docs/features/contextual-tag-filtering.md` as it also updates Popular Tags dynamically.
- [x] Document reference in `docs/features/enhanced-prompt-list.md`.

8) Validation & Rollout
- [x] Manual testing across browsers (Chromium-based, Firefox, Safari if possible).
- [x] Verify performance and no layout shift.
- [x] Gate behind no flags; changes are minimal and backward compatible.

## Manual Testing Scenarios

Initial Load (SSR)
- Navigate to `/prompts?tags=python&tags=cli`.
- Expected: `python` and `cli` tags in Popular Tags block are visually selected and have `aria-pressed="true"`.

SSR Regression Check
- Navigate to `/prompts` (no `tags` params).
- Expected: No tags have `selected` class; no visual regression; keyboard focus and hover still work.

Toggle On
- On `/prompts`, click a non-selected tag `ai`.
- Expected: page navigates to `/prompts?tags=ai` and `ai` appears selected after load.

Toggle Off
- On `/prompts?tags=ai&tags=ml`, click `ai` again.
- Expected: page navigates to `/prompts?tags=ml`; `ai` is not selected, `ml` remains selected.

Dynamic Update (Status Change)
- Switch status filter from Active to Inactive.
- Expected: Popular Tags re-render; any tag present in URL shows as selected if it still appears. No JS errors. A11y attrs updated.

De-duplication
- Manually navigate to `/prompts?tags=ai&tags=ai` and click `ai`.
- Expected: URL becomes `/prompts` (removed), no duplicates remain; no errors.

Keyboard Navigation
- Focus a tag via Tab, press Enter/Space to toggle.
- Expected: Behavior matches click; `aria-pressed` reflects state after navigation.

Accessibility
- Inspect in devtools: `role="button"` and `aria-pressed` are correct.
- Check contrast of selected tags in both default and theme variants.

Cross-Browser
- Validate in Chrome/Edge, Firefox, and Safari (if available): no layout shift, smooth behavior.

## Risks and Mitigations

- Contrast and theme consistency: validate with the theme system; adjust CSS tokens if needed.
- URL param management: ensure removal of all duplicates; centralize helper for manipulating `URLSearchParams` to avoid subtle bugs.
- Dynamic mismatch: SSR and JS must compute selection the same way; both derive from URL to avoid drift.

## Future Enhancements (Optional)

- Show a compact “Selected Tags” row with chips and per-chip remove buttons.
- Add a small check icon within selected tag for clearer affordance.
- Add a quick “Clear selected tags” link next to the section header.
- Persist selection in session storage for quick back/forward navigation recovery.

## Definition of Done

- Selected tags are visually indicated in Popular Tags (SSR and dynamically rendered states).
- Clicking a selected tag removes it from filters; clicking an unselected tag adds it.
- A11y states are correct (`role`, `aria-pressed`).
- Manual tests pass across supported browsers.
- No regressions in tag fetching and status-driven updates.

## Work Log (to be updated during implementation)

- 2025-08-17T13:20:05Z — Created roadmap; awaiting approval to implement.
- 2025-08-17T13:20:05Z — Implemented SSR selected state, JS toggling, dynamic selected rendering, and CSS selected style.
- 2025-08-17T13:40:47Z — Adjusted selected tag tone to teal/turquoise (`--tag-selected-*` tokens) for stronger contrast vs default blue; removed borders.


