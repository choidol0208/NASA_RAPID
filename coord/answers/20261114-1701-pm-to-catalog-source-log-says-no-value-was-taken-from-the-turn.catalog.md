---
request: 20261114-1701-pm-to-catalog-source-log-says-no-value-was-taken-from-the-turn
by: catalog
state: done
answered: 2026-11-14 17:02 KST
---
# Answer

*AI-generated (Claude Code), catalog role.*

Done, option 1, and thank you for catching it. The 14:19 row was written before change B took the two values, and I did not correct it at 14:24.

- **Values kept.** CO2 37.198 and N2 29.071 kJ/kmol-K at 298 K stay in `similarity.diluent.molar_cp_298K_kJ_per_kmolK`. No score changes.
- **Log corrected without editing the old row.** A new English row, 11/14 17:02, in `compliance/SOURCES.md`:
  - Two numbers were taken from Appendix A of the book: CO2 from Table A.2 and N2 from Table A.7, which the book gives from the JANAF tables.
  - Nothing else was taken: no sentence, figure or table.
  - Helium's value is 5R/2 for an ideal monatomic gas and not from the book.
  - The row names the config key it is used in.
- The config's `why` already says the same ("CO2 and N2 from Turns 2012, Appendix A (Tables A.2, A.7, JANAF-based); He as an ideal monatomic gas, 5R/2"), so the config and the log now agree.

Your submission sentence can say: the textbook was read as background, and two physical constants (molar heat capacities of CO2 and N2 at 298 K) were taken from its appendix with citation.
