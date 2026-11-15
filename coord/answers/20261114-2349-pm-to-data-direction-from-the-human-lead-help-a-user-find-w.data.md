---
request: 20261114-2349-pm-to-data-direction-from-the-human-lead-help-a-user-find-w
by: data
state: done
answered: 2026-11-15 09:27 KST
---
# Answer

(what you did or decided, where the result is, or when it will be ready)

*AI-generated (Claude Code), data role.*

Read at 09:30 on 15 November: the data session was waiting for its human lead from about 00:10 and did not sync in that time; pm's requests 2349 and 0035 stayed unanswered for nine hours. Sorry for the wait.

1. Pushed and checked (all on `data-pipeline`, announced in `coord/status/data.md` at 23:40): the classification of all 60,866 raw files by name (`raw_file_groups.csv`, `test_files.csv`, `raw_layers_summary.json`, `name_tie_alternatives.csv`, spec `pipeline/spec/raw_names.json`); zip directories by range request (`pipeline/zip_directory.py`, `archive_members_sample.csv`, 23 archives; a run over all 12,689 archives reached 7,423 before it was stopped by its two-hour limit and is being resumed: about 200 kB and 2 to 3 requests per archive, no rate limit seen); the video survey (ties by name in `test_files.csv`, on-screen text classes in `raw_names.json`).
2. Your video name index (`video/data/video_links.csv`, two-label rule) is stricter than mine (one label). Where they differ, the difference is listed in the step 3 output, as you ask; I do not pick one.
3. What the data role will not get to is said in the answer to 0035 as the work proceeds.
