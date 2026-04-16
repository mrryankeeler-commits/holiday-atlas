# Selection state transition checklist

This checklist validates that `S.loc` is the single selected-location authority and that all selection entry points run through the same selection function (`setSelectedLocation` via `selLoc` / `selLocFromDeepLink`).

## Preconditions
- Load the app with a healthy `data/locations/index.json`.
- Start on `#explorer` so the detail panel is visible.

## Deterministic checks

1. **List → map sync**
   - Click destination **A** in the sidebar list.
   - Confirm destination **A** button has `.active` class.
   - Confirm destination **A** marker uses active marker style.
   - Confirm hero title/country match destination **A** and the tab resets to **Climate**.

2. **Map → detail sync**
   - Click destination **B** marker on the map.
   - Confirm destination **B** button has `.active` class.
   - Confirm destination **B** marker uses active marker style (previous marker no longer active).
   - Confirm hero + tab-body content update to destination **B**.

3. **Filtered list with active selection retained**
   - Select destination **C**.
   - Enter a search query that excludes **C** from sidebar results.
   - Confirm the warning text appears: `Selected destination is not in current filter.`
   - Confirm map still highlights destination **C** marker.
   - Clear search; confirm destination **C** button is active again.

4. **Deep-link selection path (future entry point contract)**
   - In browser console, run `selLocFromDeepLink('<valid-id>')`.
   - Confirm sidebar active state, marker active state, and detail hero/tab all update to that location.

## Expected invariants
- Selection writes happen only through `setSelectedLocation`.
- Rendering hooks always run after selection state writes:
  - sidebar active state,
  - map active marker,
  - detail content refresh (when explorer view is active).
