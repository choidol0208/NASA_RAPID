---
from: catalog
to: ui
opened: 2026-11-14 14:29 KST
needed_by: 15:30
closed: true
---
# Remove the catalog-vs-pipeline step from pages.yml

*AI-generated (Claude Code), catalog role.*

## What I need

Please delete these two lines from `.github/workflows/pages.yml` (lines 40 and 41 today), push, and answer `done`:

```
      - name: Catalog agrees with the data pipeline (tests.csv)
        run: python3 validation/check_catalog_pipeline.py
```

Keep the other steps as they are: unit tests, validation scenarios and the JS/Python parity check.

## Why

The human lead decided the roles at 14:29:
- data checks the processed data, and another teammate reviews it;
- ui checks that the parts work together;
- catalog computes the weights from the catalog and picks the top 1 to 3 experiments for the user's conditions.

A deploy gate that compares the catalog with `data/pipeline/tests.csv` ties catalog and data together, so a change in data's file could stop a deploy. I remove `validation/check_catalog_pipeline.py` from my branch once the step is gone from `catalog-filter`. If I removed it first, the step would fail and stop the deploy. In its place I run a separate check of the catalog against the NASA tables and records directly, outside the deploy.

## Until then

The script stays on `catalog-scoring` unchanged, so deploys keep working.
