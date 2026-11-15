---
request: 20261115-1648-pm-to-catalog-challenge-fit-check-five-small-changes-in-scorin
by: catalog
state: done
answered: 2026-11-15 16:56 KST
---
# Answer

*AI-generated (Claude Code), catalog role.*

Done in config **1.5.3** on `catalog-scoring`. Weights are unchanged and no demo top 3 changed. Your sources were checked first.

1. **`warnings.partial_gravity`:** your text word for word, with your second notice appended in the same message, so the page needs no new warning code.
   - I checked the claims against `pipeline/spec/references.json` (`OF2012.table1`, `OF2012.margin`, `TB008.gaps`):
     - at lunar gravity both limits (ULOI* and MOC*) are below the 0 g and 1 g values for Mylar G, Ultem 1000 and Nomex HT90-40;
     - at Martian gravity they are below both for Ultem and Nomex, and Mylar G lies between;
     - the drops lasted 5.18 s; TB-008 says "a major gap".
   - Unit test `ChallengeFit1648` pins the sources in the text.
2. **`warnings.not_understood`:** your text word for word.
3. **`artemis` removed** from `presets.lunar_habitat.aliases`. "Artemis II smoke alarm" now reads as detection with no environment: SAME, SAME-R, SAME-SIM.
4. **`presets.mars_habitat.source`: changed example.** The NASA source we cite, NASA/TP-2010-216134 Table 10 (`EAWG.atmospheres`), recommends **8.0 psia with 32% O2** for landers and surface habitats. 34% is the maximum for materials testing and certification (`EAWG.testing`), and 8.2 psia does not appear in that recommendation. So the text reads: "…type an oxygen and a pressure to place tests (for example 32% O2 at 8.0 psi, a lander and surface-habitat atmosphere recommended in NASA/TP-2010-216134)." If the deck or submission uses "34% at 8.2 psi" as a NASA atmosphere, please change it the same way.
5. **"combustion chamber" and "연소실" removed** from `keywords.out_of_scope`:
   - "ACME combustion chamber 40% oxygen" now ranks ACME-CFI-G, ACME-BRE, ACME-FLAME-DESIGN;
   - "hybrid rocket combustion chamber fire" stays out of scope.
   - I did not add the optional reason sentence to `warnings.out_of_scope`.

Smaller items:
- **`warnings.o2_above_all`:** the clause is appended, with one correction. **Two** investigations reach 85%, both in inverse-flame oxidizer streams: ACME-CFI-G-C02 and ACME-FLAME-DESIGN-C02. The text says "The highest O2 in PSI, 85% in ACME Flame Design and ACME CFI-G, was the oxidizer stream of an inverse flame, not the surrounding atmosphere."
- **METHOD "129 of 136" and the header in `scoring/__init__.py`:** fixed at 16:16 (`b2bceac`).
- **SLICE hardware:** filled only with the record's own words. The PSI-106 `experimentHardware` field is empty, and the record's approach says "The SLICE apparatus consisted of a fan-driven flow duct…", so the cell reads "fan-driven flow duct (record approach text)". The record does not name the MSG or SPICE. The catalog takes values only from PSI records and tables, so the challenge-statement part is left out; its `source_notes` still says "Uses the SPICE fan-driven flow duct in the MSG."

Checks:
- 83 unit tests; 45 of 45 scenarios; parity 106 of 106; source check clean;
- `web/check_integration.py`: 33 results, 0 broken joins;
- weights match the derivation; reading order up to date.

Rebuild the AI layer if it stores warning texts.
