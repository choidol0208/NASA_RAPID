---
request: 20261114-1709-pm-to-ui-one-labelled-sentence-and-a-link-for-the-video-s
by: ui
state: done
answered: 2026-11-14 17:56 KST
---
# Answer

*AI-generated (Claude Code), ui role.*

Done. It goes live with the push that carries this answer; my status names the build.

- **Where:** on the BASS-II (PSI-25) result card, directly under its "Raw data in PSI" line, the place you named second. It shows whenever BASS-II is among the results, for example for `ISS`, and not otherwise. I did not put it under "Take the data with you", where it would show for every query, including those without BASS-II.
- **Text:** your sentence word for word (compared with your request by script), followed by the link "(video/README.md)" to `video/README.md` at the built commit.
- **Shown only when** the build has `video/README.md`. `web/build.py` flags it as `repo:video/README.md` in `build.json`, as it does for the evidence packages.
- **Rules kept:** it is one line. The page reads no file under `video/`, and no number from the pilot reaches a ranking, a summary, a count or a scenario text.

Checked on a local build: ISS shows the line once, on BASS-II; lunar habitat shows none. No console errors, no 404s. Integration check: 33 results, 0 broken joins.
