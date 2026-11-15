---
from: ui
to: pm
opened: 2026-11-15 15:49 KST
needed_by: 17:30
closed: true
---
# Cross-role check at 15:40: weight sampling on 1.5.1 hides the Weight check lines; stale numbers in the submission drafts and README

*AI-generated (Claude Code), ui role.* The human lead asked for a check that the work of the roles does not conflict. These are the points in paths you own. Each was read at about 15:40 KST from `main` 5fd795c, `catalog-filter` 9b0f961 and the public page (build 9b0f961).

## What I need

1. **Rerun the 8,000-draw weight sampling on config 1.5.2** (`data/insights/robustness.json`).
   - Every run there carries `config_version` 1.5.1, but the page reads config 1.5.2.
   - The page shows a card's "Weight check" line only when the two versions are equal (`robustRunFor` in `web/app.js`), so the public page shows **no Weight check line now**.
   - `docs/submission/submission_text.md` line 344 says "Each result card shows the outcome as its 'Weight check' line", and `slides_outline.md` quotes 88.4% from that run.
   - Catalog says the weights and the top 3s are unchanged in 1.5.2, so the numbers may stay the same. That has not been checked: please rerun it rather than relabel it.
2. **Submission text and slides outline**, where they quote things that changed:
   - "1.5.1": 7 places in the submission text and 10 in the slides outline (recounted at 15:52 on main fb55e13 merged into catalog-filter; the config is 1.5.2). The top 3s and scores they quote still match `rank()`. The ISS is BASS-II 93.4, SAFFIRE-I 92.1, SAFFIRE-II 92.1; the lunar habitat is FLEX 75.2, ACME-CFI-G 71.6, ACME-BRE 73.6; the smoke detector query is SAME 94.6, SAME-R 94.6, SAME-SIM 81.4.
   - "104 of 104" queries in parity: `python -B web/parity_check.py` now prints **106/106**.
   - Submission text line 746: "The lunar range reaches up to 85.8 kPa". Lines 150 and 802 and the page say "below 85.8 kPa", because `pipeline/spec/scenarios.json` has `max_inclusive: false`. The data role's answer files use the same "reaches up to 85.8 kPa" in `environment.caveat`. "Below" is the exact form.
3. **`README.md`** (yours): after your update it no longer has the old lunar order, "59 checks" or "99/99", but it names config 1.5.1 in 5 places. Its line 84 describes the "Weight check" line, which item 1 brings back.

## Why

Item 1 is the only place where the page and the submission text disagree on what the page shows. A judge who reads "Weight check line" and opens a card does not find one. Items 2 and 3 are numbers a judge can recompute.

## Until then

- The page keeps hiding the lines. That is correct: a sample of another config version describes another ranking. I do not change the rule.
- Also from this check, done on my side (`catalog-filter`):
  - **The captures your outline asks the ui role for are now defined in `web/capture_media.mjs`:**
    - `slide3_lunar_result.png`: the first three cards with Why and Largest gap; the team note, the raw-file line and the record summary are left out for this capture only.
    - `slide5_lunar_piles.png`: P1 and S1 open. It is 2216 x 6983 px, too tall for a slide as it is, so use boxes or tell me what to keep.
    - `slide6_ai_use.png`.
  - **Every capture works on today's page again.** The page is over 29,000 px tall now, and the old element and full-page screenshots timed out. Each capture now hides the other page blocks for that capture only.
  - **`CAPTURE_ONLY=a.png,b.png`** retakes only the named files.
  - Trial run against the public page at 15:47: 15 PNGs and the GIF written. Nothing is committed to `web/media/` until the freeze.
- No conflict found in the rest of the check:
  - no role edited another role's paths since the 13:28 split;
  - 1,703 quotations that appear both in the data role's answer files and in `results_by_need.json` have the same text;
  - `run_report.json` lists no scenario-preset mismatch;
  - no conflict markers in any branch.
