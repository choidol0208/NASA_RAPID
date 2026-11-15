# History rewrite of 15 November 2026

*AI-generated (Claude Code, pm role), on the human lead's decision recorded in `coord/decisions.md`.*

## What was done

On 15 November 2026 between 19:26 and 19:28 KST the git history of the branches `main`, `catalog-filter`, `catalog-scoring` and `data-pipeline` on GitHub was rewritten and pushed with force, so that no commit on any branch holds the folder `scoring/reference/janaf/`.

That folder held five table files of the NIST-JANAF Thermochemical Tables (NIST Standard Reference Database 13: `C-095.txt`, `H-064.txt`, `He-001.txt`, `N-023.txt`, `O-029.txt`). The tables are copyrighted by the U.S. Secretary of Commerce (Standard Reference Data Act) and are not public domain, so the team may not redistribute them. They were committed on 14 November at 20:08 KST and deleted from the files on 14 November at 21:33 KST (`compliance/SOURCES.md`, row of 11/14 21:33), but 13 commits between those two times still held them, and every later commit had those 13 in its history.

`scoring/flame_temperature.py` reads the tables from a local download that is never committed (`.gitignore`). `scoring/flame_temperature.json` holds the flame temperatures and regression results that the script computed, not the tables.

## How

```
git clone --mirror <the repository>            # a fresh copy of GitHub, 15 November 18:53 KST
git filter-branch \
  --index-filter 'git rm -r -q --cached --ignore-unmatch scoring/reference/janaf' \
  --state-branch refs/rewrite-state/map \
  -- --ancestry-path=6202f9a0f05c9a5fd9fb00f9d95bf8488bffa26e ^99f8a25bbd44178634bda8cdac18ee244743c22f --branches
git push --force-with-lease=refs/heads/<branch>:<old id> <the repository> <new id>:refs/heads/<branch>   # four branches
```

Only the commit that added the folder and its descendants were rewritten: 261 of the 584 commits. The other 323 commits, the branch `data-lab` and pull request 1 keep their ids.

## What changed and what did not

| | |
|---|---|
| Commit ids | 261 commits have a new id. `history_rewrite_20261115_ids.tsv` lists every old id with its new id, its commit date and its subject. |
| Files | In the 13 commits that held the folder, the five files are gone. No other file changed in any commit; the files at the tip of every branch are identical to before. |
| Authors, dates, messages | Unchanged in every commit: author, committer, both dates, the message, and the order of the parents. |
| Signatures | 32 of the rewritten commits carried a signature. A signature covers the commit's content and cannot be kept when the commit changes, so these 32 are now unsigned. The 93 signed commits outside the rewritten set keep theirs. |

## Checks before the push

A script compared the rewritten copy with the untouched copy (not committed; its results are here):

- the 261 rewritten commits are exactly the commit that added the folder and its descendants; no two old commits map to one new commit;
- every rewritten commit keeps its author, committer, both dates, its message and the order of its parents, and its files differ from before only by the five table files;
- every branch has the same number of commits as before and the same files at its tip (`main` 574 commits, `catalog-filter` 562, `catalog-scoring` 559, `data-pipeline` 459, `data-lab` 193, unchanged);
- no commit on any branch, and not the pull request's commit, holds a path under `scoring/reference/janaf/`; none of the five files' objects or the folder's objects can be reached from them;
- none of the 316 numeric rows of the five tables appears in any of the 2,961 text files that can be reached.

Independent AI sessions then tried to refute the rewrite through four lenses (reachability of the tables, equivalence of the history, the push, references to commit ids), and a fifth was started to look for what the four had missed and was stopped before it reported, on the human lead's instruction to finish the work directly. The reachability and equivalence reviews could not refute the rewrite (the first also searched inside spreadsheet, slide and PDF files, and for runs of three values along a row or a column; it did not read text inside images). The push review found that the first push script could leave the public page on older files and could not be resumed; the script was changed to wait for each page deployment and to skip a branch that is already pushed, and the last deployment after the push was `main`'s. The references review listed the texts and links that cite old ids; they were corrected or noted in the commits that follow the push.

No person reviewed the rewrite.

## What a reader should know

- **Commit ids in older texts are the old ids.** Commit messages, coordination files (`coord/`), the two logs in `compliance/` and some documents cite ids from before the rewrite; they were not edited. Look an old id up in `history_rewrite_20261115_ids.tsv`.
- **GitHub may still show an old commit to someone who opens it by its full id**, with a note that it belongs to no branch, until GitHub removes unreferenced objects. Removing them at once is a request to GitHub Support that only the repository's owner can make; at 19:30 KST on 15 November, after the push, GitHub still returned the adding commit and one of the table files to a request by id, and that request to GitHub Support had not been made. The repository had no fork.
- **Copies made before the rewrite** (a clone, a fork, a download) still hold the old history. The team's own clones were reset as described below.

## For team members: bring a clone onto the new history

Do this before any `git pull`, `git merge`, `coord.py pull` or `git push`. A merge of an old local branch with the new history, once pushed, puts the removed files back into the history on GitHub.

```
git fetch origin
git status                      # commit or note anything that is not pushed
git checkout <your branch>
git branch backup-old-history   # only if you have commits that are not on GitHub; otherwise skip
git reset --hard origin/<your branch>
```

If you had commits that were not on GitHub: `git cherry-pick <id>` each of them onto the reset branch, then delete `backup-old-history` (`git branch -D backup-old-history`). `scripts/coord.py` refuses to merge a branch that still holds the removed history.
