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

## Phase 3 — Enhanced UX (clusters, region filters, map/list split tuning)

### Scope
- Add marker clustering for dense destination sets.
- Add region filters that coordinate between sidebar list and map markers.
- Tune responsive map/list layout split for desktop and mobile.

### Acceptance criteria
- Cluster behavior reduces marker overlap without hiding discoverability.
- Region filter updates both visible list items and plotted markers consistently.
- Selection state remains stable when filters are toggled.
- Desktop and mobile split layouts avoid clipping/overflow regressions.
- Keyboard users can reach filters, list items, and selected map destination context.

### Rollback / fallback
- Feature-toggle clusters and region filters independently from base map.
- If enhanced controls regress UX/performance, fall back to Phase 2 read-only marker experience.
- Preserve map/list synchronization contract even when enhancements are disabled.

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
