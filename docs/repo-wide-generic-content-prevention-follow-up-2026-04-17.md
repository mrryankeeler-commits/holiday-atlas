# Follow-up Work Item: Repository-wide Generic Content Prevention (2026-04-17)

## Objective
Prevent templated copy from re-entering destination records by combining a full-content audit pass, validator hardening, CI enforcement, and ingestion workflow guardrails.

## Scope
- All files matching `data/locations/*.json`, excluding `data/locations/index.json`.
- Quality controls for fields:
  - `desc`
  - `hls[]`
  - `todo[].name`
  - `todo[].desc`
  - `sweet`
  - `prac.bestFor[]`
  - `prac.alerts[]`

## Deliverables

### 1) Full repository audit + remediation queue
- Run repository-wide audit against all scoped fields above.
- Produce a remediation list grouped by **country → location id**.
- Split fixes into small quality-controlled batches (max 3 locations per batch, per AGENTS policy).
- Track each batch in a checklist doc under `docs/location-qa-checklists/` with owner/date/status.

### 2) Validator hardening (`scripts/validate_locations.py`)
Add new/stronger checks for:
- Templated `todo[].name` constructions that are currently passing.
- Broader boilerplate pattern variants across `hls[]`, `todo[].desc`, and related short-form fields.
- Explicit detection of phrase families such as:
  - “seasonal benchmark” variants
  - “balanced mix” variants
  - “short break or longer stay” variants
- Optional specificity heuristics (warn/fail thresholds) for:
  - `desc`
  - `todo` entries
  - Heuristics can include destination-token presence and/or named-entity style signals.

### 3) CI fail-fast enforcement
- Ensure CI fails PRs when validator flags generic content.
- Confirm workflow coverage for changes touching:
  - `data/locations/*.json`
  - `scripts/validate_locations.py`
  - relevant docs/checklist workflow files.
- Add/adjust status checks so this validator cannot be bypassed in normal PR flow.

### 4) Uploader and contributor workflow guardrails
- Add a pre-commit or pre-upload step that runs `python3 scripts/validate_locations.py`.
- Add/update merge checklist gate requiring destination-specific examples before approval.
- Ensure checklist language references scoped fields (not just `desc`/`sweet`).

### 5) Documentation + policy updates
- Update repository guidance docs and AGENTS checklist wording to make these checks mandatory for new location ingestion.
- Cross-link validator behavior, CI requirements, and contributor checklist steps so the policy is discoverable in one pass.

## Acceptance criteria
- [ ] Audit artifact exists and lists all flagged entries, grouped by country/location.
- [ ] Remediation batches are defined and linked to QA checklists.
- [ ] `scripts/validate_locations.py` flags newly targeted template classes (`todo[].name`, phrase-family variants, expanded `hls[]` patterns).
- [ ] CI workflow demonstrably fails on validator violations.
- [ ] Pre-commit/pre-upload path runs validator locally before PR.
- [ ] Docs/AGENTS guidance clearly marks checks as mandatory for ingestion.

## Suggested execution order
1. Baseline scan + grouped remediation backlog generation.
2. Validator rule expansion with test fixtures/examples.
3. CI and pre-commit enforcement updates.
4. Documentation/checklist updates.
5. Remediation batches rollout in ≤3-location increments.

## Notes
- Keep enforcement strict enough to block known boilerplate while avoiding false positives on concise but specific copy.
- Prefer deterministic signatures for hard fails, and use heuristic specificity checks behind documented thresholds.
