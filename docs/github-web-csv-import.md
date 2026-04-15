# Importing climate data from GitHub Web (no terminal needed)

This workflow is for uploading mixed climate CSV batches from the GitHub website.

## 1) Upload files in GitHub Web

1. Open this repository in GitHub.
2. Go to `data/climate/uploads/`.
3. Click **Add file** → **Upload files**.
4. Upload your CSV (for example: `batch-2026-04.csv`).
5. Commit the upload to your working branch.

If you have known spelling variants, also update/upload:

- `data/climate/aliases.json`

Example aliases file:

```json
{
  "tiblisi-georgia": "tbilisi",
  "mostarr-bosnia-and-herzegovina": "mostar"
}
```

## 2) Run importer workflow in GitHub Web

1. Open **Actions** tab.
2. Click **Import climate CSV (GitHub Web friendly)**.
3. Click **Run workflow**.
4. Fill inputs:
   - `csv_path`: example `data/climate/uploads/batch-2026-04.csv`
   - `mode`:
     - `stage` = unknown/future locations go to `data/pending-locations/` only (not shown in app)
     - `create` = create missing `data/locations/<id>.json` and add to active index
5. Click **Run workflow**.

## 3) Review generated pull request

The workflow opens a PR automatically if changes were generated.

- Review changed files.
- Merge when ready.

## Notes

- Existing locations keep `busy/ac/fl` unchanged unless explicit score override columns are used with override flags.
- `avg` is required.
- Unknown staged records are stored as pending JSON and are not displayed until promoted into `data/locations/`.
