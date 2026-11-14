---
request: 20261114-1656-pm-to-all-english-only-before-submission-translate-the-kor
by: ui
state: done
answered: 2026-11-14 17:13 KST
---
# Answer

*AI-generated (Claude Code), ui role.*

Done for ui's files.

- `presentation/build_catalog_filter_slide.js`: the four lines of speaker notes, which were in Korean, are translated into English.
  - A dated line is added after them, because the notes describe the 10:30 version: 22 scenarios, the 85% burner stream as the oxygen maximum, and ±0.05 weights.
  - It names what changed since: 35 scenarios; the highest surrounding-atmosphere oxygen tested is 40%, and the burner stream is no longer compared with a habitat atmosphere; sensitivity is run at x0.5 and x1.5.
- `presentation/catalog_filter_slide.pptx`: the build script's npm dependencies and the theme file are not on this PC, so I did not rebuild the slide. I put the English notes into it in place instead, so the two files now agree.
  - The theme named its Korean-script font in Hangul; it is now spelled `Malgun Gothic`.
  - No Korean text is left in the file's XML. The slide face was English already.
- My answer to catalog 1332: its three Korean keywords now carry English glosses (gaseous fuel, jet flame, droplet).
- Checked again: no other file that ui owns (`web/` except the scorer port, `presentation/`, `.github/`, `app/`, ui's answers, `coord/status/ui.md`) holds Korean text.

New compliance rows from ui will be in English, and I will merge `main` before I append one.
