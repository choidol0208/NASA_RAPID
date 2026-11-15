---
from: pm
to: all
opened: 2026-11-15 19:32 KST
needed_by: -
closed: false
---
# History rewritten on GitHub at 19:26 to 19:28: reset your clone before any pull, merge or push

## What I need

**Before any `git pull`, `git merge`, `coord.py pull` or `git push`, bring your clone onto the new history.** On 15 November between 19:26 and 19:28 KST pm rewrote the history of `main`, `catalog-filter`, `catalog-scoring` and `data-pipeline` on GitHub and pushed with force (the human lead's decision, `coord/decisions.md`), so that no commit holds the five NIST-JANAF table files of `scoring/reference/janaf/`. 261 of 584 commits have a new id; the files at the tip of every branch are the same as before. `data-lab` is unchanged. Details: `docs/history_rewrite_20261115.md`.

Your clone still holds the old history. If you merge the new branch into your old one and push, the removed files come back into the history on GitHub (git's own hint "git pull before pushing again" does exactly that). Do this instead, in your clone, with B = your branch (`data-pipeline`, `catalog-filter` or `catalog-scoring`):

```
git status --short                 # tracked changes: commit them now (untracked files are not touched below)
git log --oneline origin/B..B      # BEFORE fetching: your commits that are not on GitHub. Note their ids.
git fetch origin
git checkout B
git branch -m B old-B              # keeps your old branch under another name; never push old-B
git checkout -b B origin/B
git cherry-pick <ids noted above, oldest first>     # only if there were any
git merge-base --is-ancestor 6202f9a0f05c9a5fd9fb00f9d95bf8488bffa26e HEAD && echo "STOP: still the old history" || echo "ok: new history"
git branch -D old-B                # when the line above says ok and your commits are on B
```

Then `python3 scripts/coord.py pull` works as before. `scripts/coord.py` on `main` now refuses to merge a branch that still holds the removed history.

One text of the catalog role states the old situation. **catalog, please correct it:** `scoring/BUILDUP.md` line 305, "They stay in earlier commits, since pushed history is not rewritten." Suggested: "On 15 November 2026 they were also removed from the git history of every branch (`docs/history_rewrite_20261115.md`)."

Commit ids in status files, requests and answers written before 19:26 are old ids. They are left as they are; `docs/history_rewrite_20261115_ids.tsv` gives the new id of each.

## Why

A push from a clone with the old history undoes the removal.

## Until then

pm checks after every fetch that no branch on GitHub descends from the old commit, and says so in `coord/status/pm.md`.
