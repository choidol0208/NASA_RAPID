---
request: 20261114-1734-pm-to-data-28-review-rows-without-a-verdict-10-quotes-18-te
by: data
state: done
answered: 2026-11-14 17:54 KST
---
# Answer

(what you did or decided, where the result is, or when it will be ready)

*AI-generated (Claude Code), data role.*

All 28 rows have a verdict on `data-pipeline` (`reviewer_kind = ai_session`, `reviewer_role = data`; one AI reader this time, the conducting session, not two).

- **Quotes (10):** 8 `relevant`, 2 `not_relevant`: `PSI-23 ... IMP-1` ("The impact of this work consists of both practical and fundamental aspects.") and `PSI-69 ... IMP-1` ("... are significant and multifaceted."). Both are verbatim and say nothing when shown alone.
- **Template sentences (18):** all `wording_ok`. Numbers in them were recounted from `tests.csv`, `scenario_tests.csv` and `need_tests.csv`: PSI-159 179 ambient and 154 inverse, PSI-69 274, PSI-10 207 and 120, PSI-39 79; the 17 counted lunar tests at 30 to 34% oxygen and 71.2 to 72.4 kPa; the 20 PSI-159 flames at 30% oxygen or more and at or below 10.2 psi; the Olson and Ferkul lunar limits lower than both the 1 g and the 0 g limits for each of the three materials (`OF2012.table1`); the monitoring ranges for HCN, HCl and HF in `3001.T6.2-3`.

**PSI-21 model sentence: stays `supported`.** The quote row was `not_relevant` only because the label "Impact statement" misdescribes a sentence that states a goal. The model sentence calls it "a goal of the study" and attributes it to the record, which is what the sentence is. The two verdicts do not conflict.

**Lunar and Martian gravity gap sentence: yes, let it follow the new wording.** "none was run at lunar gravity" reads as a fact taken from the tables; the gravity level is a constant the team set per table from the PSI record. Suggested: "The team's source mapping classes every mapped test as a microgravity test (a table constant, not a table column); none is classed as a lunar- or Martian-gravity test." My `wording_ok` on the old text was too lenient; if the text changes, the row loses its verdict and I give it again.
