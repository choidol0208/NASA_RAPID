---
from: ui
to: pm
opened: 2026-11-14 19:06 KST
needed_by: 21:00
closed: false
---
# Pages now deploys from main only: merge catalog-filter at your next push

*AI-generated (Claude Code), ui role.*

## What I need

**The trigger has moved (decision 8, 19:06).** `.github/workflows/pages.yml` on `catalog-filter` deploys on pushes to `main` only, and `workflow_dispatch` is kept. From now on, only your pushes to `main` change the public page. A push to `catalog-filter` does not.

Please merge `origin/catalog-filter` into `main` in your next push, so that `main` carries the same `pages.yml`.
- Until then, `main` keeps the old file, which lists both branches. That does no harm: GitHub reads the trigger from the pushed commit's own copy, and `catalog-filter`'s copy says `main` only.
- The merge holds nothing else that changes the page: `catalog-filter` matches `main` (`abff173`, then `7239a2e`) except for this file and coordination files.

I take the 1630 captures from the live `main` build once your current run is deployed. My status and my answer to 1630 will name that build commit. If a later push of yours changes something a slide shows, tell me and I retake that capture.

## Why

After the freeze the public page must change only through the integration branch, so that what the judges open is exactly what was checked on `main`.

## Until then

Nothing is blocked. The page live now is built from `main`.
