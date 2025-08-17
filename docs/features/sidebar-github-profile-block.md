## Sidebar GitHub Profile Block (Roadmap)

### Initial Prompt (English)

Add a block at the bottom of the sidebar, something like this (copied from another project):

```html
<div class="server-info-row">
  <a href="https://github.com/elimS2" target="_blank" class="github-link">
    <span class="nav-icon nav-icon-github"></span>
    <span class="github-text">GitHub: elimS2</span>
    <img class="github-avatar" src="https://github.com/elimS2.png?size=50" alt="elimS2 avatar" width="25" height="25" loading="lazy" decoding="async" referrerpolicy="no-referrer" onerror="this.style.display='none'">
  </a>
}</div>
```

Analyze the task and the project in depth and decide how best to implement it.

Create a detailed, step-by-step action plan in a separate document inside `docs/features`. If the folder does not exist, create it. Document discovered nuances, problems, and solutions. Use this file as a to-do checklist; update it during implementation without removing historic points (only update status and comment). If new subtasks arise during implementation, add them here. Remember that only English is allowed in code and comments in the project.

When the plan is written, stop and ask for my approval to start implementing or to adjust the plan if needed. Include manual testing steps describing what to click in the UI.

### Context and Current State

- **Stack**: Flask + Jinja2, Bootstrap 5, custom theme tokens (`theme-*` classes), Bootstrap Icons (`bi` classes), custom static assets under `app/static`.
- **Navigation and layout**: Global nav lives in `app/templates/base.html`. There is no global "sidebar" layout, but the prompt list view uses a left column as a sidebar for filters:
  - `app/templates/prompt/list.html` has a `row` with `col-md-3` (filters sidebar) + `col-md-9` (content).
- **Target location**: The new block should appear at the bottom of the filters sidebar on the prompt list page (and optionally be reusable for other pages that also have sidebars in the future).

### Goals

- Add a compact, theme-aware GitHub profile block at the bottom of the sidebar in `prompt/list.html`.
- Make the block reusable via a Jinja partial to avoid duplication (DRY) and to support future sidebars.
- Use existing design system conventions: theme tokens (`theme-*`), Bootstrap utilities, and Bootstrap Icons.
- Ensure accessibility (proper `alt`, focus styles, keyboard navigation, `rel` attributes).
- Maintain performance (lazy-loaded avatar image) and graceful error handling (avatar fallback).

### Non-Goals

- Creating a global application-wide sticky sidebar layout. We will scope to the prompt list page sidebar. The partial will be reusable, but we will only integrate it where a sidebar exists today.
- Implementing user-specific dynamic content beyond the owner GitHub link. We will add light configuration hooks.

### UX and Design Guidelines

- **Visual**: Small card-like row with subtle border using `theme-border` and `theme-surface`. Use a GitHub icon (`bi bi-github`), the label `GitHub: <username>`, and a small circular avatar.
- **Placement**: After the Filters card content, as the last element in the sidebar column. Optionally allow the block to be sticky at the bottom on tall screens if we decide to enhance later.
- **Responsive**: Avatar shrinks gracefully; text truncates with ellipsis if needed; avoid overflow.
- **Accessibility**: Use descriptive link text, `alt` text on image, `rel="noopener noreferrer"` together with `target="_blank"`, and sufficient color contrast via theme classes.

Note: Removed the `card-footer` from the partial to avoid an unwanted vertical white bar beneath the link area. The card body now serves as the entire interactive surface.

### Technical Design

- **Partial**: Create `app/templates/partials/sidebar_profile_block.html` to encapsulate the block. Keep it independent and theme-aware.
- **Inclusion**: Include the partial at the bottom of the sidebar column in `app/templates/prompt/list.html`.
- **Styling**: Prefer Bootstrap utilities (`d-flex`, `align-items-center`, `gap-*`, `text-truncate`) and existing theme classes. Add minimal custom CSS in `app/static/css/style.css` only if necessary.
- **Config**: Add optional config keys in `config/base.py` (e.g., `OWNER_GITHUB_USERNAME`, `OWNER_GITHUB_URL`, `OWNER_GITHUB_AVATAR_URL`). Provide safe defaults matching `elimS2`.
- **Avatar Fallback**: Use `onerror` to hide the `img` if the avatar fails to load or show a default icon (`bi-person-circle`).

### Implementation Plan (Checklist)

1) Create the partial
   - [x] Add `app/templates/partials/sidebar_profile_block.html` with a compact, theme-aware layout using Bootstrap utilities and icons.
   - [x] Expose variables for username/profile/avatar via include kwargs with safe defaults. (Config wiring comes later.)
   - [x] Ensure `rel="noopener noreferrer"` and lazy-loading.

2) Wire it into the sidebar
   - [x] Update `app/templates/prompt/list.html` to include the partial as the last element inside the left `col-md-3` sidebar.
   - [x] Ensure spacing (`mt-3`) and separation (`theme-border`/`border-top`) if necessary for clarity. (Currently uses a self-contained card with `mt-3`.)

3) Optional layout enhancement (if needed for true bottom alignment)
   - [ ] If strict bottom alignment is required regardless of sidebar content height, wrap the sidebar column content with a `d-flex flex-column` container and apply `mt-auto` to the block so it docks to the bottom of the column.

4) Styling
   - [ ] Attempt with only Bootstrap utilities and theme tokens.
   - [ ] If something small is missing (e.g., avatar rounding), add minimal CSS to `app/static/css/style.css` following existing conventions.

5) Config
   - [x] Add config keys to `config/base.py` with defaults for `elimS2`.
   - [x] Inject into Jinja via a context processor in `app/__init__.py` as `owner_github_username`, `owner_github_url`, `owner_github_avatar_url`.
   - [x] Optionally override via environment-specific configs if desired.

6) QA and Accessibility
   - [x] Validate keyboard navigation, focus order, and visible focus.
   - [x] Verify color contrast in both light/dark via the theme toggle.
   - [x] Confirm avatar loads and degrades gracefully.

7) Documentation
   - [x] Update this roadmap with outcomes and any deviations.
   - [x] Add a brief note to `docs/design-system.md` if any new class patterns are introduced. (No new patterns needed; reused Bootstrap utilities and theme tokens.)

### QA Results

- Visual check on Prompts list page: block rendered as last item in sidebar; no extra white bar (card footer removed).
- Theme toggle (light/dark): colors consistent and readable.
- Responsive: no overflow on small screens; link remains easily tappable; text truncates.
- Accessibility: tab focus visible; link text descriptive; avatar has `alt`; external link uses `rel="noopener noreferrer"`.
- Automated checks: test suite and linter passed with no new issues.

### Manual Testing Steps

- Open `Prompts` list page.
- Verify the GitHub block is visible at the bottom of the left sidebar.
- Click the `GitHub: elimS2` link; confirm it opens in a new tab to the correct profile.
- Confirm the avatar renders as a 25x25 (or similar) circle. Temporarily break the avatar URL to test the fallback behavior.
- Toggle theme (light/dark) and ensure the block respects theme colors and remains readable.
- Resize to small viewport: confirm layout does not overflow; text truncates gracefully; tap target size remains usable.
- Navigate with keyboard (Tab): ensure focus moves to the link and the focus ring is visible.

### Risks and Mitigations

- **Layout conflicts in sidebar**: If the sidebar content grows, the block might not be at the literal bottom of the viewport. Mitigate by optionally using `d-flex`/`mt-auto` container approach if strict bottom docking is desired.
- **Avatar load failures**: Use `onerror` attribute to hide the image or switch to an icon.
- **Design drift**: Rely on theme tokens and Bootstrap utilities to stay consistent with the design system.

### Success Criteria

- Block appears reliably at the bottom of the sidebar on the prompt list page.
- Visual style is consistent with the rest of the app and readable in all themes.
- No layout regressions on the page; Lighthouse/Accessiblity checks remain green.

### Rollback Plan

- Revert the include in `prompt/list.html` and delete the partial. Remove optional config keys if added.

### Estimate

- Implementation: 1–2 hours
- QA + polish: 30–45 minutes

### Open Questions

- Should the block also appear on other pages with sidebars (e.g., tags view) or remain exclusive to the prompt list?
- Do we want the block strictly docked to the bottom of the viewport (sticky) on tall screens, or simply placed last in the sidebar flow?


