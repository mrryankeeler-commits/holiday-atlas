# Map Rollout Plan

## Objective
Roll out map functionality safely while preserving the current destination-list browsing experience as a reliable fallback.

## Phase 1 — Welcome page + navigation into explorer

### Scope
- Keep the welcome-first flow as the default entry point.
- Ensure users can move from welcome to explorer using the primary CTA and URL hash navigation.

### Acceptance criteria
- Welcome view is the default on first load unless a valid deep link/hash targets explorer.
- “Explore map” CTA moves users into explorer without losing selected destination context.
- Hash navigation supports `#welcome` and `#explorer`, and browser back/forward preserves view.
- If destination details fail to load, users see an explicit error state and can still navigate destination list controls.

### Rollback / fallback
- Roll back by forcing welcome-only mode (disable explorer entry points in UI while leaving data loading intact).
- If any explorer regressions occur, keep welcome and list navigation active while temporarily hiding map interactions.

---

## Phase 2 — Read-only plotted map + marker click selects destination

### Scope
- Enable map rendering with plotted markers from `data/locations/index.json` coordinates.
- Marker click selects destination and syncs with sidebar/list selection.
- Map is read-only (no editing/dragging destination data).

### Acceptance criteria
- Map loads when feature flag is enabled.
- Each destination with valid coordinates appears as a marker.
- Clicking a marker updates selected destination and detail panel.
- Active destination marker visually updates when list or marker selection changes.
- If map library fails to load, fallback message is shown and list-based browsing still works.

### Rollback / fallback
- Immediate rollback path: set map feature flag to disabled in `app.js`.
- Operational fallback: keep map panel visible only with status/fallback message and preserve full list-based explorer flow.
- If map initialization errors occur, fail closed (no map interactions), but keep destination browsing fully available.

---

## Phase 3 — Enhanced UX (region filters, map/list split tuning)

### Scope
- Add region filters that coordinate between sidebar list and map markers.
- Tune responsive map/list layout split for desktop and mobile.

### Acceptance criteria
- Region filter updates both visible list items and plotted markers consistently.
- Selection state remains stable when filters are toggled.
- Desktop and mobile split layouts avoid clipping/overflow regressions.
- Keyboard users can reach filters, list items, and selected map destination context.

### Rollback / fallback
- Feature-toggle region filters independently from base map.
- If enhanced controls regress UX/performance, fall back to Phase 2 read-only marker experience.
- Preserve map/list synchronization contract even when enhancements are disabled.

### Phase 3 execution tickets (prioritized)

Delivery order:
1. Marker visibility/differentiation
2. Region filters
3. Responsive split tuning

#### P3-1 — Marker prominence refresh
**Priority:** P0 (ship first)

**Engineering tasks**
- Increase default marker legibility at baseline zoom (size, stroke/contrast, z-index layering).
- Add explicit selected-marker prominence treatment that remains visible over nearby markers.
- Ensure list-selection to marker-selection sync is instant and idempotent.
- Keep fallback behavior unchanged when map enhancements are disabled.

**Measurable acceptance criteria**
- At initial `#explorer` load, ≥95% of non-overlapping markers are visually distinguishable at default zoom.
- Selecting from list or map updates the same destination state within one interaction (no double-click required).
- Selected marker style remains visually distinct against surrounding markers at all desktop breakpoints.
- With enhancement toggle off, Phase 2 marker rendering and list browsing still function without JS errors (fallback integrity).

**QA checklist (manual in `#explorer`)**
1. Open `#explorer` with marker enhancements enabled.
2. Without zooming, visually confirm markers are readable against the basemap.
3. Click a list item; verify the corresponding marker becomes highlighted immediately.
4. Click a different marker; verify sidebar selection and detail panel update to the same destination.
5. Disable marker-enhancement toggle; reload `#explorer`; verify Phase 2 behavior still works and no console errors appear.

**Completion notes / rollback toggle**
- Shipped increment: Marker prominence baseline and selected-state contrast refresh.
- Rollback toggle used: `featureFlags.mapMarkerProminence` (set `false` to return to Phase 2 marker styling).

#### P3-2 — Marker differentiation
**Priority:** P0 (ship first, paired with P3-1)

**Engineering tasks**
- Differentiate marker states (`default`, `hover`, `selected`, `filtered-out`) with non-color-only cues.
- Ensure state legend/tooltip copy (if present) aligns with marker semantics.
- Preserve keyboard reachability to selected destination context when state changes originate from keyboard navigation.

**Measurable acceptance criteria**
- Each marker state is distinguishable by at least two signals (e.g., size + outline, not only color).
- Keyboard selection of list items updates marker state and keeps focused list item visible.
- Filtered-out markers are either hidden or de-emphasized consistently with active filter state, with no stale highlighted marker.
- With differentiation toggle off, map remains usable with base Phase 2 interaction model (fallback integrity).

**QA checklist (manual in `#explorer`)**
1. Open `#explorer` and Tab into destination list.
2. Use keyboard to change selected destination; verify marker selected-state updates.
3. Hover/click markers and verify `default/hover/selected` visual differences are clear.
4. Apply and clear a region filter; verify filtered marker states update consistently and no stale highlight remains.
5. Disable marker-differentiation toggle; reload and verify Phase 2 interactions still work.

**Completion notes / rollback toggle**
- Shipped increment: Marker state differentiation for hover/selected/filtered semantics.
- Rollback toggle used: `featureFlags.mapMarkerDifferentiation` (set `false` to use Phase 2 state styling).

#### P3-3 — Region filter sync
**Priority:** P1 (ship after marker visibility/differentiation)

**Engineering tasks**
- Add region filter controls and bind filter state to both list and map layers.
- Synchronize selected destination behavior when active selection becomes filtered out.
- Preserve keyboard navigation order and announcements/context for filter-driven updates.

**Measurable acceptance criteria**
- Changing region filter updates visible list rows and markers in the same render cycle.
- Selection sync rule is deterministic when filter excludes active destination (clear selection or move to first visible item per spec, consistently).
- Keyboard users can tab to filters, apply/change filters, and continue to list items without focus loss.
- With region-filter toggle off, explorer retains Phase 2 selection + map/list sync behavior (fallback integrity).

**QA checklist (manual in `#explorer`)**
1. Open `#explorer`; note currently selected destination.
2. Apply a region filter that includes the selected destination; verify list and markers both narrow to that region.
3. Apply a region filter that excludes selected destination; verify deterministic selection behavior per spec.
4. Use keyboard only (Tab/Shift+Tab/Enter/Space) to change filters and then select a list item; verify focus continuity.
5. Disable region-filter toggle; reload and verify full list/marker set returns with Phase 2 behavior.

**Completion notes / rollback toggle**
- Shipped increment: Region filter controls with synchronized map/list filtering.
- Rollback toggle used: `featureFlags.mapRegionFilters` (set `false` to disable filters and restore full set).

#### P3-4 — Responsive split tuning
**Priority:** P2 (ship last)

**Engineering tasks**
- Tune desktop split ratios and mobile stacking so key explorer controls remain visible.
- Remove clipping/overflow regressions in map panel, list panel, and detail content.
- Validate keyboard reachability across responsive breakpoints after layout changes.

**Measurable acceptance criteria**
- No horizontal clipping in `#explorer` at common widths (320, 375, 768, 900, 1280).
- Map and list remain independently usable at mobile widths; critical controls stay visible without overlap.
- Keyboard tab sequence reaches filters, list, selected destination context, and detail tabs at each tested breakpoint.
- With split-tuning toggle off, prior Phase 3 layout remains available and functional (fallback integrity).

**QA checklist (manual in `#explorer`)**
1. Open `#explorer` and test widths: 1280, 900, 768, 375, 320.
2. At each width, verify no clipped controls/text in map panel, filter bar, list, and detail area.
3. At each width, complete keyboard tab pass across filters → list → selected destination context → tabs.
4. Trigger selection changes from both map and list; verify no overlap/overflow occurs during updates.
5. Disable split-tuning toggle; reload and verify previous layout mode renders correctly.

**Completion notes / rollback toggle**
- Shipped increment: Responsive split and overflow corrections across desktop/mobile explorer layouts.
- Rollback toggle used: `featureFlags.mapResponsiveSplitTuning` (set `false` to restore prior split behavior).

---

## Production data readiness gate

Before enabling map in production:
- All entries in `data/locations/index.json` must include valid numeric coordinates within bounds:
  - latitude: `-90` to `90`
  - longitude: `-180` to `180`
- If any entry fails the gate, keep map disabled and show fallback messaging while list browsing remains available.

## Post-release QA checklist

### Mobile layout
- Validate at common breakpoints (e.g., ≤900px and narrow handset widths).
- Confirm map panel height is usable and does not hide destination list controls.
- Verify horizontal destination rail controls appear only when needed and remain tappable.

### Keyboard navigation
- Tab order reaches welcome CTA, destination search, destination list, map-adjacent controls, and tabbed content.
- Focus indicators are visible in all primary interactive areas.
- Selection changes via keyboard preserve content updates and do not trap focus.

### Performance with full destination set
- Verify initial explorer render remains responsive with full marker/data volume.
- Validate marker/select interactions remain smooth on mid-tier mobile devices.
- Confirm resize/reflow behavior does not cause repeated heavy map/chart re-renders.
- Check fallback behavior still performs correctly when map is feature-disabled or blocked.
