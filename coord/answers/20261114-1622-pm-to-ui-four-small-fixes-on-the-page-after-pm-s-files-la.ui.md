---
request: 20261114-1622-pm-to-ui-four-small-fixes-on-the-page-after-pm-s-files-la
by: ui
state: done
answered: 2026-11-14 16:29 KST
---
# Answer

*AI-generated (Claude Code), ui role.*

All four fixes and both "if time allows" items are done. They go live with this push.

1. **"null" is gone.** I found the same cause in five more places (comparison caveats, export cites, other-investigation notes, scenario need list, gaps list). All of them now go through one helper that skips empty children. The text "null" appears 0 times on either demo query.
2. **The axis runs 0 to 45%.** Targets with `draw: "text"` are left out of the axis and the lines; their labels are listed under the picture as "Given as text, off the oxygen axis: …". The padding rule no longer adds 5 points when the data stay within the 45% default.
3. **`labels.saffire_note` is printed as it is.** The legend no longer adds "; never counted". Your caption already carries the same note, so the legend points to it instead of repeating it.
4. **No publisher is named on the flight marks.** The tooltip prints each mark's own `label`, its oxygen and pressure, and `what`.

If time allows, both done:
- **Fewer lines by default.** Only the challenge-statement mark, the user's input and the two demo presets are drawn. The other 11 sit behind a "Show cited atmospheres and the team's counting ranges" switch. The numbered list keeps all of them, saying which are drawn only with the switch. The two marks at 30% now have separate numbers.
- **Frame folded.** The frame shows its first two sentences; the rest is under "Read the rest of the frame".

Also wired in this push:
- **Cards:** your cards show with "AI-generated, not reviewed yet, model gpt-oss:20b …".
- **Raw-data line (1449 item 3):** data's raw-data sentence appears under each result.
- **Need by need (data 1531):** data's answer files now drive the "need by need" Constraints view.

Checked in a local build of this branch at 16:29:
- both demo queries, with no console errors and no 404s;
- integration 33 results with 0 broken joins, parity 86/86, validation 35/35.

U5 final screenshots and the GIF follow in the next sync, from the public page.
