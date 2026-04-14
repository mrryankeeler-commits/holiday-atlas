# AGENTS.md

## Scope
These instructions apply to the entire repository.

## Project overview
Holiday Atlas is a static front-end app (`index.html`, `app.js`, `styles.css`) that renders destinations and monthly travel data.

## Data layout (source of truth)
- Destination manifest: `data/locations/index.json`
- One file per location: `data/locations/<id>.json`
- `id` must be lowercase kebab-case and match filename exactly.

## Task routing guidance
- “Add/edit a destination”:
  1) Update `data/locations/index.json`
  2) Update/create `data/locations/<id>.json`
- “Change rendering/UX”:
  - Edit `app.js` and/or `styles.css`
- “Change copy/static markup”:
  - Edit `index.html` (and `app.js` where strings are generated)

## Data contract
### index.json required fields
- `id`, `city`, `country`, `region`

### <id>.json required fields
- `id`, `city`, `country`, `region`, `desc`, `hls`, `todo`, `prac`, `sweet`, `months`

## Quality checks (before commit)
- JSON files parse
- Every `index.json` id has a corresponding `data/locations/<id>.json`
- Every location file id matches filename
- No duplicate ids

## Guardrails
- Do not reintroduce a single monolithic destinations file.
- Do not silently change schema; update this AGENTS.md when schema changes.
