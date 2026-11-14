# Structured argument: lunar habitat, material flammability ranking

**Team computation and team reasoning (AI-drafted), not a NASA conclusion, not safety guidance; a research exploration tool.**

*AI-generated (Claude Code), 2026-11-14. Not human-reviewed. Branch data-lab, experiment, not for merge.*

A structured argument (claim, inference, evidence, defeater, undeveloped claim) for one question about the lunar habitat: can a flammability ranking of materials obtained in normal-gravity ground tests be carried to the lunar-habitat atmosphere and gravity? It shows how the argument is built and where it rests on documents, on team reasoning, or on nothing held. It gives no verdict and sets no criterion.

Node kinds: CLAIM (a sentence that can be true or false), INFERENCE (why the children would support the claim; team reasoning, basis 'documented' if a reference item states the step, 'team' if none does), EVIDENCE (a reference item or a count copied from a data file; no team text), DEFEATER (a way an inference or one of its assumptions could fail; 'documented' or 'logical'), UNDEVELOPED (a claim with no evidence held, with the items that ask for the study).

## Summary (counts only, no verdict)

- claims: 8
- undeveloped claims: 3
- evidence leaves: 32 (reference items 28, counts 4; distinct reference items 26)
- evidence access levels: abstract_only 5, full_text_read 20, read_by_teammate 3
- inferences by basis: documented 0, team 8
- assumptions stated: 105
- defeaters by basis: documented 133, logical 58
- inferences with no defeater yet: none
- added by the review pass: 86 assumptions, 167 defeaters
- assumptions with no recorded defeater: 86. An assumption with no recorded defeater has not been shown to hold.
- Counts only. No overall verdict is computed or implied.

Per inference (counts only):

| Inference | Assumptions (review pass) | Defeaters documented | Defeaters logical | Of the inference as a whole | Defeaters added by review pass | Assumptions with no recorded defeater |
|---|---|---|---|---|---|---|
| I0 | 15 (11) | 23 | 6 | 7 | 25 | 11 (numbers 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15) |
| I1 | 13 (11) | 18 | 5 | 15 | 21 | 11 (numbers 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13) |
| I2 | 11 (9) | 17 | 7 | 13 | 20 | 9 (numbers 3, 4, 5, 6, 7, 8, 9, 10, 11) |
| I3 | 14 (11) | 24 | 7 | 9 | 26 | 11 (numbers 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14) |
| I3.1 | 11 (10) | 8 | 8 | 12 | 15 | 10 (numbers 2, 3, 4, 5, 6, 7, 8, 9, 10, 11) |
| I4 | 17 (13) | 23 | 6 | 15 | 24 | 13 (numbers 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17) |
| I4.1 | 11 (10) | 5 | 10 | 12 | 14 | 10 (numbers 2, 3, 4, 5, 6, 7, 8, 9, 10, 11) |
| I5 | 13 (11) | 15 | 9 | 11 | 22 | 11 (numbers 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13) |

An assumption with no recorded defeater has not been shown to hold.

## Tree

```
C0 CLAIM: A ranking of materials by flammability obtained in normal-gravity ground tests can be carried over, in the same order, to the lunar-habitat atmosphere and to lunar gravity.
  I0 INFERENCE [basis: team; team reasoning (AI-drafted), not a NASA statement]: The top claim is split by the conditions under which a ranking is obtained. A ranking can be carried over only if the ground test yields an order at all (C1), the target atmosphere is fixed (C2), the order holds across the change of total pressure (C3), the order holds across the change of gravity and of the flow that gravity sets (C4), and the two changes taken together do not alter it (C5). E0a names total pressure, temperature, convective flow and gravity level as the conditions at which an oxygen threshold is determined; E0b states that fire-limit results do not necessarily apply to conditions that do not reproduce the test. Neither item states this split; it is the team's.
      assumption 1: The conditions through which the order could change are the oxygen concentration and total pressure of the atmosphere, the gravity level, and the flow that gravity sets.
      assumption 2: Temperature, material thickness and sample size are held as in the ground test.
      assumption 3: Pressure and gravity can be examined one at a time before their combination is examined.
      assumption 4: An order of oxygen thresholds is what the top claim means by a flammability ranking.
      assumption 5 [added by review pass]: The listed sub-claims together are enough for the top claim; the inference states only that each is necessary.
      assumption 6 [added by review pass]: Every material in the ranking is tested by the same method, facility, ignition source and pass criterion at every condition compared, and the same set of materials is tested throughout.
      assumption 7 [added by review pass]: Differences between the materials' thresholds are larger than the scatter of the measurement, so a definite order exists to be carried.
      assumption 8 [added by review pass]: The threshold quantity has the same definition at normal and at reduced gravity (OF2012.margin states that the low-gravity extinction criteria differ).
      assumption 9 [added by review pass]: The habitat atmosphere has the same diluent as the ground test, an oxygen-nitrogen mixture.
      assumption 10 [added by review pass]: Forced ventilation and its direction do not change the order, although the ground test is run with no air flow.
      assumption 11 [added by review pass]: Each material's flammability changes monotonically between normal gravity and the reduced-gravity levels tested, so results at other gravity levels say something about lunar gravity.
      assumption 12 [added by review pass]: Results from drop-tower or orbital facilities are comparable with ground-chamber results for ordering purposes.
      assumption 13 [added by review pass]: Evidence obtained on a few materials applies to the materials to be ranked.
      assumption 14 [added by review pass]: Flaming combustion is the only mode that matters for the ranking; smoldering and non-flaming combustion do not reorder materials.
      assumption 15 [added by review pass]: A single target atmosphere will be fixed (C2), although the held documents give several recommended atmospheres and a control box.
      D0a DEFEATER of assumption 2 [basis: documented (6001B.def.worstcase)]: 6001B.def.worstcase names temperature and material thickness among the most hazardous conditions. This argument develops neither, so the order could change through them.
          quote: Worst-case anticipated use environment: Most hazardous pressure, temperature, material thickness, and/or fluid exposure conditions.
      D0b DEFEATER of assumption 4 [basis: documented (CP2004.flam.fist)]: CP2004.flam.fist names time to ignition, fire spread rate, material properties and critical heat flux for ranking the hazards of materials. An order of oxygen thresholds need not agree with an order by these quantities.
          quote: Develop a flammability test method to rank the hazards of materials used on spacecraft using time to ignition, fire spread rate, material properties, critical heat flux
      D0c DEFEATER of assumption 2 [basis: documented (SAF16b.saffire2)]: SAF16b.saffire2 states that quantifying the difference in flammability limits for large samples is an objective. A ranking from small ground specimens may not carry over to large samples.
          quote: Quantifying the difference in flammability limits for large samples is the objective of the Saffire-II experiments.
      D0d DEFEATER of assumption 1 [basis: logical]: The split treats the named conditions as the only paths by which the order could change. A path not named here, such as the strength of the ignition source or the diluent gas, is not examined.
      D0e DEFEATER of the inference [basis: logical; added by review pass]: The inference states its sub-claims only as necessary conditions ('can be carried over only if'). Holding every necessary condition does not entail the top claim; no warrant is given that the listed sub-claims together are enough, so even with all of them held the step to the top claim is open.
      D0f DEFEATER of the inference [basis: documented (TB14639.gap); added by review pass]: TB14639.gap states that normal-gravity flammability tests do not correlate with flammability in ventilated, micro- or reduced-gravity conditions. This attacks the carry-over that the split is built to support, not only one branch of it.
          item words (verbatim): "Normal-gravity flammability tests do not correlate with flammability in ventilated, micro- or reduced-gravity conditions."
      D0g DEFEATER of the inference [basis: documented (D2863.validity); added by review pass]: D2863.validity states that when end-use conditions change it is not always possible to predict changes in the measured characteristics, and that results are valid only for the test's exposure conditions. The item is the ASTM D2863 oxygen-index method (flowing gas), not Test 1, read as abstract only; it still limits any carry-over of a threshold-based order to untested conditions.
          item words (verbatim): "Therefore, the results are valid only for the fire-test-exposure conditions described in this test method."
      D0h DEFEATER of the inference [basis: documented (G125.conditions); added by review pass]: E0b is placed under C0 as support, but its words state that results do not necessarily apply to any condition that does not faithfully reproduce the test conditions. Read plainly it limits the top claim rather than supporting the split. The item is from ASTM G125, a different method from Test 1, read as abstract only.
          item words (verbatim): "However, its results do not necessarily apply to any condition that does not faithfully reproduce the conditions during test."
      D0i DEFEATER of the inference [basis: documented (CH.partial_gravity); added by review pass]: CH.partial_gravity states that PSI holds no partial-gravity combustion data yet. The gravity branch of the split (C4) cannot be evidenced at lunar gravity from the challenge's own data source; the item is a teammate's reading with no quote held.
          item words (verbatim): "PSI holds no partial-gravity combustion data yet"
      D0j DEFEATER of the inference [basis: documented (EAWG.atmospheres); added by review pass]: The split needs one fixed target atmosphere (C2). EAWG.atmospheres gives more than one recommended surface-habitat atmosphere and a control box around each, and calls them recommendations, not requirements. If the target cannot be fixed, the pressure and combination branches have no endpoint and the split cannot close.
          item words (verbatim): "Recommendations, not requirements."
      D0k DEFEATER of the inference [basis: logical; added by review pass]: The top claim asks that the whole order carry over. The split treats this as one yes-or-no property, but an order can be kept for some pairs of materials and reversed for others, and two materials whose thresholds differ by less than the scatter of the measurement have no fixed order to carry. The split gives no way to state or examine a partial result.
      D0l DEFEATER of assumption 1 [basis: documented (CP2004.flam.velocity); added by review pass]: CP2004.flam.velocity names flow direction, as well as velocity, as what a comparison with Test 1 rests on. Flow direction is not in the list of conditions.
          item words (verbatim): "The question of conservatism of Test 1 therefore may rest on the determination of velocity and flow direction at which to compare."
      D0m DEFEATER of assumption 1 [basis: documented (G125.scope); added by review pass]: G125.scope names fire-propagation direction and geometrical features among the test conditions of a threshold limit. Neither is in the list. The item is ASTM G125, read as abstract only, a different method from Test 1.
          item words (verbatim): "fire-propagation directions, and various other geometrical features of common systems"
      D0n DEFEATER of assumption 1 [basis: documented (TM217036.threshold); added by review pass]: TM217036.threshold ties the reduced-gravity threshold to the local convective velocity. The assumption admits only the flow that gravity sets; a local velocity set by forced ventilation is left out of the list, while the ground test is run with no air flow (6001B.T1.noflow).
          item words (verbatim): "is a function of the local convective velocity"
      D0o DEFEATER of assumption 1 [basis: documented (EAWG.need); added by review pass]: EAWG.need lists diluent gas beside pressure, gravity and oxygen mole fraction as an effect on material flammability. D0d names the diluent gas as a logical doubt; this item gives it a documented basis. The ground test fixes the diluent as nitrogen (6001B.T1.o2level).
          item words (verbatim): "Effects of pressure, gravity, oxygen mole fraction, and diluent gas on material flammability."
      D0p DEFEATER of assumption 1 [basis: documented (CP2003.prev.smolder); added by review pass]: CP2003.prev.smolder names non-flaming and smoldering combustion in microgravity as a gap and states that the standard flammability tests do not take smoldering into account. A change of combustion mode is a path by which the order could change that the list does not name.
          item words (verbatim): "the standard flammability tests do not take smoldering into account"
      D0q DEFEATER of assumption 1 [basis: documented (ISO16697.scope); added by review pass]: E0a is cited for the conditions of a threshold, but its own words name a standard ignition source and temperature among them, and the first assumption drops both (temperature is moved to the second assumption with no item behind it). The item is the scope of a threshold method read as abstract only, not Test 1; it does not say these are the only paths by which an order could change and says nothing about ranking. Its 'convective flow' is not 'the flow that gravity sets': the same technical specification speaks of forced convective velocity thresholds (ISO16697.otherlimits).
          item words (verbatim): "when a material exposed to a standard ignition source self-extinguishes at a given constant total pressure, temperature, convective flow, and gravity-level conditions"
      D0r DEFEATER of assumption 2 [basis: documented (H2011.worstcase); added by review pass]: H2011.worstcase states that Test 1 is run at the combination of thickness, pressure, oxygen concentration and temperature that makes the material most flammable. 'Held as in the ground test' then means a different thickness and temperature per material, not one common held value, and need not match the thickness and temperature of the material as used in the habitat.
          item words (verbatim): "test pressure, oxygen concentration, and temperature that make the material most flammable"
      D0s DEFEATER of assumption 2 [basis: documented (CP2003.prev.thickthin); added by review pass]: CP2003.prev.thickthin states that the relationship between flame spread over thermally thick and thin materials must still be established. Materials of different thickness in one ranking may respond differently to the change of gravity or pressure, so thickness can reorder them even if each is held at its test value.
          item words (verbatim): "A better understanding of the relationship between flame spread across thermally thick and thin materials must be established."
      D0t DEFEATER of assumption 2 [basis: documented (CP2004.flam.q5); added by review pass]: CP2004.flam.q5 is an open organizing question, from small-scale experiments to large-scale fires. With D0c it limits the assumption that the specimen size of the ground test stands for the habitat.
          item words (verbatim): "How will flames grow and spread in real situations?"
      D0u DEFEATER of assumption 2 [basis: logical; added by review pass]: The assumption is stated about the habitat, where temperature, thickness and size are set by design and use, not by the team. Asserting that they are held at test values is an unexamined claim about the target, not a condition the argument can impose; if it fails, the branches that rely on it carry nothing over.
      D0v DEFEATER of assumption 3 [basis: documented (URBAN14.loc); added by review pass]: URBAN14.loc attributes the strong pressure dependence of the limiting oxygen concentration of Nomex HT90-40, found in a quiescent environment, to kinetic or flow effects. In a quiescent ground test the flow is buoyant, set by gravity, so part of the pressure effect may act through the same flow that gravity sets; the two factors need not be separable.
          item words (verbatim): "The strong dependence on pressure suggests either kinetic effects or flow effects."
      D0w DEFEATER of assumption 3 [basis: documented (H2006.table2); added by review pass]: The pressure-step values held in H2006.table2 are at normal gravity and quiescent. Examining pressure one at a time therefore means examining it only at normal gravity; whether the pressure effect is the same at lunar gravity is what the one-at-a-time step cannot show.
          item words (verbatim): "normal gravity, quiescent"
      D0x DEFEATER of assumption 3 [basis: documented (THOMSEN18.care); added by review pass]: THOMSEN18.care comes from a paper on simulating concurrent flame spread in reduced gravity by reducing ambient pressure (its title), so the held literature itself treats the two factors as linked, and the item warns that the link changes as low pressure affects the chemical kinetics. This limits treating pressure and gravity as separate steps.
          item words (verbatim): "eventually low pressure will affect the chemical kinetics of the process"
      D0y DEFEATER of assumption 3 [basis: logical; added by review pass]: Examining each factor with the other held at its ground value cannot reveal an interaction. If the combination branch is not developed, the separate pressure and gravity branches give no support to the combined change the top claim needs, and the decomposition only defers the whole question to the combination branch.
      D0z DEFEATER of assumption 4 [basis: documented (RG.map); added by review pass]: RG.map describes flammability as a map over ventilation flow, oxygen and possibly pressure, with the limiting oxygen concentration found over it. A ranking by one threshold measured at one flow need not agree with a ranking by the limit over the map.
          item words (verbatim): "ventilation flow, ambient oxygen concentration and possibly pressure, to find the fundamental limiting oxygen concentration in microgravity"
      D0aa DEFEATER of assumption 4 [basis: documented (OF2012.margin); added by review pass]: OF2012.margin states that the low-gravity limits use extinction criteria that are not the same as in normal gravity. An order of oxygen thresholds compared across gravity levels then compares different quantities, so the meaning fixed by this assumption does not stay the same across the change the claim is about.
          item words (verbatim): "their extinction criteria are not the same as in 1g"
      D0ab DEFEATER of assumption 4 [basis: documented (TB008.materials); added by review pass]: TB008.materials names ignition temperature, combustion rate and explosion potential as the properties asked of cabin materials. An order by oxygen threshold need not agree with orders by these; this adds to D0b.
          item words (verbatim): "must have high ignition temperatures, slow combustion rates, and low potential for explosion"
      D0ac DEFEATER of assumption 4 [basis: logical; added by review pass]: Which oxygen threshold is meant is not fixed: the highest concentration at which all specimens pass and the concentration at which about half fail are different definitions (D1a raises this under I1, not here). Without choosing one, the top claim has no single ranking to carry.
    E0a EVIDENCE
        item: ISO16697.scope (definition), ISO-TS-16697; access: abstract_only
          text (team wording in references.json): The oxygen concentration threshold is determined at a given constant total pressure, temperature, convective flow and gravity level.
          quote (as printed): "This Technical Specification provides a method to determine the oxygen concentration threshold when a material exposed to a standard ignition source self-extinguishes at a given constant total pressure, temperature, convective flow, and gravity-level conditions."
          where: Clause 1 Scope (the same sentence is the ISO catalogue abstract, with 'ISO/TS 16697:2012' in place of 'This Technical Specification')
          url: https://www.iso.org/standard/57450.html
        covers (only what the item states):
          facility: not stated in the item
          flow: not stated in the item
          gravity: not stated in the item
          materials: not stated in the item
          oxygen: not stated in the item
          pressure: not stated in the item
    E0b EVIDENCE
        item: G125.conditions (limitation), ASTM-G125; access: abstract_only
          text (team wording in references.json): Results of the fire-limit test do not necessarily apply to any condition that does not faithfully reproduce the conditions during test; limits measured at one set of conditions are not necessarily the lowest thresholds at which combustion can occur.
          quote (as printed): "However, its results do not necessarily apply to any condition that does not faithfully reproduce the conditions during test."
          where: Scope 1.3, public page https://www.astm.org/g0125-00r23.html. Significance and Use 5.1 adds: 'Flammability limits measured at one set of conditions are not necessarily the lowest thresholds at which combustion can occur.'
          url: https://www.astm.org/g0125-00r23.html
        covers (only what the item states):
          facility: not stated in the item
          flow: not stated in the item
          gravity: not stated in the item
          materials: not stated in the item
          oxygen: not stated in the item
          pressure: not stated in the item
    C1 CLAIM: The normal-gravity ground test of the held standard yields a quantity by which materials can be put in order, not only a pass or a fail.
      I1 INFERENCE [basis: team; team reasoning (AI-drafted), not a NASA statement]: Test 1 as written gives a pass or a fail at one atmosphere (E1a, E1b). The same standard defines the maximum oxygen concentration at which specimens pass (E1c), and researchers define an upward limiting oxygen index from the same burn-length criterion and a modified Test 1 that measures it (E1d, E1e). Such a threshold can put materials in order; no held item states this step. CP2003.prev.margin recommends adding to the go/no-go criteria a quantitative test method that provides a ranking or an indication of flammability margin.
          assumption 1: The maximum oxygen concentration and the upward limiting oxygen index put the same materials in the same order.
          assumption 2: The pressure at which a threshold was measured is recorded with it, so that thresholds measured at the same pressure can be compared.
          assumption 3 [added by review pass]: Thresholds compared to form an order are measured with the same specimen thickness, size, temperature, mounting, quiescent gas and ignition source, not only at the same pressure.
          assumption 4 [added by review pass]: A search for an oxygen threshold, or a modified Test 1, still counts as the normal-gravity ground test of the held standard named in C1, and not as a nonstandard test under 6001B.focr57.
          assumption 5 [added by review pass]: Threshold values repeat between determinations and between laboratories closely enough that the order between two materials does not flip; no held item states the spread, and SAE2008.table1 and OF2012.table1 print different normal-gravity MOC values for one material at the same pressure.
          assumption 6 [added by review pass]: The oxygen step and the number of specimens per step are fine enough to separate the materials to be ordered, and ties are handled by a stated rule; none is given.
          assumption 7 [added by review pass]: MOC and ULOI are judged against the same pass criterion, although MOC uses the full acceptance criteria, including burning debris, and the OF2012 ULOI uses burn length only.
          assumption 8 [added by review pass]: 'The maximum oxygen concentration' is one quantity across the held items, although 6001B.T1.moc, ISO16697.moc and OF2012.uloi define it differently.
          assumption 9 [added by review pass]: Every material to be ranked has a threshold inside the testable oxygen range; materials with only a bound are excluded or handled by a stated rule.
          assumption 10 [added by review pass]: Thresholds have been determined, at one common set of conditions, for the materials to be ranked; no evidence leaf under C1 holds such a table (H2006.table2 and OF2012.table1 are held but not cited here, and OF2012.table1 mixes pressures).
          assumption 11 [added by review pass]: The basis item's example 'LOI' can stand for the quiescent upward MOC or ULOI that the inference uses.
          assumption 12 [added by review pass]: A single threshold gives one order whatever failure rate is chosen for it (all specimens pass, or about half fail).
          assumption 13 [added by review pass]: An order by flaming-ignition threshold stands for 'flammability' although the standard tests leave out smoldering (CP2003.prev.smolder).
          D1a DEFEATER of assumption 1 [basis: documented (ISO16697.moc)]: ISO16697.moc defines MOC as the highest oxygen concentration where all samples pass and ULOI as the concentration where about half of the samples fail. The two definitions need not give the same order.
              quote: highest oxygen concentration where all samples tested (at least five) pass the test criteria described in Clause 4
          D1b DEFEATER of the inference [basis: documented (D2863.caveat)]: D2863.caveat states that correlation of the oxygen index with burning characteristics under actual use conditions is not implied.
              text: Correlation with burning characteristics under actual use conditions is not implied.
          D1c DEFEATER of assumption 1 [basis: documented (OF2012.uloi); added by review pass]: MOC and ULOI are not tied to the same pass criterion. 6001B.T1.moc ties MOC to the acceptance criteria of Test 1, which 6001B.T1.pass makes two-part: burn length, and no flame spread by burning debris. OF2012.uloi ties the normal-gravity ULOI to the burn-length criterion only. For a material that drops burning debris, MOC is cut by the debris criterion and ULOI is not, so the two can put such materials in different orders. The inference's wording 'from the same burn-length criterion' hides this.
              item words (verbatim): "passes the NASA STD 6001 Test 1 burn length criterion approximately half the time"
          D1d DEFEATER of assumption 1 [basis: documented (OF2012.uloi); added by review pass]: The held items do not use one MOC. OF2012.uloi defines the normal-gravity MOC as the concentration where at least five samples passed and at least one failed one oxygen step higher; 6001B.T1.moc requires only that at least five pass; ISO16697.moc requires that all samples tested pass. The assumption treats 'the maximum oxygen concentration' as one quantity, and the OF2012 form builds the oxygen step into the value, which limits how finely materials can be told apart.
              item words (verbatim): "where at least one sample failed in the environment that contained 1 percent more oxygen by volume"
          D1e DEFEATER of the inference [basis: documented (SAE2008.table1); added by review pass]: Two held NASA reports print different normal-gravity MOC values for Ultem 1000 at the same pressure: SAE2008.table1 (the cell in item words, with an asterisk the item does not explain) and OF2012.table1 (value cited below). No held item states how much a threshold varies between determinations. Where two materials' thresholds lie within that spread, the threshold does not fix their order.
              item words (verbatim): "'24% O2, 10.2 psia*' (1g MOC, Ultem 1000)"
              cited value OF2012.table1 ["rows", {"material": "Ultem 1000"}, "moc_o2_pct_1g"] = 23.0
              cited value OF2012.table1 ["rows", {"material": "Ultem 1000"}, "pressure_psia"] = 10.2
          D1f DEFEATER of assumption 2 [basis: documented (OF2012.table1); added by review pass]: In the held data thresholds were measured at different pressures: OF2012.table1 prints Nomex HT90-40 at another pressure from Mylar G and Ultem 1000 (values cited below), and H2007.fixedpressure is at a single pressure of its own. Recording the pressure shows the mismatch but does not supply a same-pressure measurement; materials measured only at different pressures get no order from this step.
              item words (verbatim): "Nomex HT90-40 at 14.7 psia"
              cited value OF2012.table1 ["rows", {"material": "Mylar G"}, "pressure_psia"] = 10.2
              cited value OF2012.table1 ["rows", {"material": "Ultem 1000"}, "pressure_psia"] = 10.2
              cited value OF2012.table1 ["rows", {"material": "Nomex HT90-40"}, "pressure_psia"] = 14.7
          D1g DEFEATER of assumption 2 [basis: documented (H2006.range); added by review pass]: H2006.range states that total pressure moves the threshold more for materials with higher thresholds. Thresholds compared at one pressure therefore give an order for that pressure only. The assumption allows comparison within one pressure but does not say which pressure the order of C1 belongs to, and orders measured at different pressures can cross.
              item words (verbatim): "The effect of total pressure on oxygen concentration flammability thresholds is greater for materials with higher thresholds"
          D1h DEFEATER of assumption 2 [basis: documented (H2011.worstcase); added by review pass]: H2011.worstcase defines the Test 1 configuration as a combination of thickness, pressure, oxygen concentration and temperature. Matching pressure alone does not make two thresholds comparable when thickness or temperature differ; this assumption names pressure only.
              item words (verbatim): "test pressure, oxygen concentration, and temperature that make the material most flammable"
          D1i DEFEATER of the inference [basis: documented (6001B.focr57); added by review pass]: C1 speaks of the normal-gravity ground test of the held standard. E1e is a modified Test 1, and 6001B.T1.focr59 sets Test 1 at the worst-case atmosphere. Under 6001B.focr57 a deviation from standard test conditions makes the test nonstandard. A ULOI from a modified Test 1, or from runs at atmospheres other than the worst case, is then a nonstandard result, not one of the held standard as written. MOC is defined inside the standard (6001B.T1.moc), so this hits the ULOI branch hardest.
              item words (verbatim): "the test shall be identified as nonstandard and the results annotated as nonstandard"
          D1j DEFEATER of the inference [basis: documented (CP2003.prev.margin); added by review pass]: The item named in the inference does not state the step. CP2003.prev.margin is typed knowledge_gap and recommends that a quantitative method be added. It names LOI or a radiation panel, not MOC or ULOI, and asks for 'ranking or indication of flammability margin', so a method that gives only a margin would meet it. It does not say that an oxygen threshold puts materials in order.
              item words (verbatim): "Augment existing go/no go criteria with a quantitative test method which provides ranking or indication of flammability margin, e.g. LOI or radiation panel."
          D1k DEFEATER of the inference [basis: documented (D2863.oi); added by review pass]: If the basis item's example 'LOI' is the oxygen index of D2863.oi, it is measured in a flowing oxygen-nitrogen mixture, while Test 1 is run with no air flow (6001B.T1.noflow). The method the basis item names would then not be the MOC or ULOI method the inference relies on, and the same gap weakens D1b, which carries an oxygen-index caveat over to MOC and ULOI. The items do not themselves state that LOI is the D2863 index.
              item words (verbatim): "in a flowing mixture of oxygen and nitrogen that will just support flaming combustion"
          D1l DEFEATER of the inference [basis: documented (CP2004.flam.fist); added by review pass]: After the basis item, ranking was still listed as work to be done: CP2004.flam.fist calls for developing a method to rank material hazards, by quantities other than an oxygen threshold. This cuts against reading the held Test 1 framework as already yielding the ordering quantity. D0b uses the same item against I0, not against I1.
              item words (verbatim): "Develop a flammability test method to rank the hazards of materials used on spacecraft"
          D1m DEFEATER of the inference [basis: documented (CP2003.prev.smolder); added by review pass]: CP2003.prev.smolder states that the standard flammability tests do not take smoldering into account. An order by flaming-ignition threshold says nothing about non-flaming or smoldering behaviour, so 'put in order by flammability' covers one mode of burning only.
              item words (verbatim): "the standard flammability tests do not take smoldering into account"
          D1n DEFEATER of the inference [basis: documented (ICES14.fixedpressure); added by review pass]: ICES14.fixedpressure describes thresholds found by lowering oxygen until a chosen failure rate is seen. The threshold is then a point on a probability-of-failure curve picked by the tester (MOC: all pass; ULOI: about half fail). If two materials' curves differ in width, choosing a different failure rate can swap their order.
              item words (verbatim): "oxygen concentration is decreased for each set of five tests until the desired failure rate is observed"
          D1o DEFEATER of the inference [basis: documented (G125.conditions); added by review pass]: G125.conditions limits fire-limit results to conditions that reproduce the test. Any order a threshold gives is at most an order at the exact test conditions: specimen, configuration, quiescent gas and ignition source. The inference does not say this.
              item words (verbatim): "its results do not necessarily apply to any condition that does not faithfully reproduce the conditions during test"
          D1p DEFEATER of the inference [basis: documented (6001B.T1.pass); added by review pass]: E1a is cited for 'Test 1 as written gives a pass or a fail at one atmosphere'. The item states only the self-extinguishing criterion, burn length and no transfer of burning debris; it names no atmosphere, and the material-level fail rule is in another item (6001B.T1.failenv), not cited. The 'one atmosphere' part rests on E1b alone.
              item words (verbatim): "no specimen propagates a flame by transfer of burning debris"
          D1q DEFEATER of the inference [basis: documented (6001B.T1.moc); added by review pass]: E1c defines MOC only. It states no pressure, no oxygen step and no procedure for finding MOC, does not say that MOC is a required output of Test 1, and does not say that MOC orders materials. The inference then treats it as the same quantity as the MOC of OF2012.uloi, whose definition differs.
              item words (verbatim): "The maximum oxygen concentration at which at least five specimens pass the acceptance criteria of this test."
          D1r DEFEATER of the inference [basis: documented (TB14639.modified); added by review pass]: E1e describes a modified Test 1 that measures an upward flammability limit 'akin to the Limiting Oxygen Index' so that the margin in the use environment can be assessed. It does not name ULOI, does not mention ranking, and is a Task Book task description, not a standard or a test result.
              item words (verbatim): "A modified Test 1 measures the actual upward flammability limit (akin to the Limiting Oxygen Index)"
          D1s DEFEATER of the inference [basis: logical; added by review pass]: Some materials have no threshold inside the oxygen range a facility can reach: they pass at the highest oxygen tested or fail at the lowest. Such materials have only a bound, not a value, and cannot be put in order among themselves or against materials with measured thresholds on the same side.
          D1t DEFEATER of the inference [basis: logical; added by review pass]: A threshold comes from a few specimens per step and a finite oxygen step. Materials whose thresholds fall in the same step tie, and materials within the scatter of repeat determinations can swap order from one campaign to the next. The order among closely spaced materials may be an artifact of sampling, not a property of the materials.
          D1u DEFEATER of assumption 1 [basis: logical; added by review pass]: Even where both quantities have been measured for some materials and agree, that shows nothing about materials measured only one way. A mixed list, with MOC for some materials and ULOI for others, cannot be merged into one order without assuming this assumption itself.
          D1v DEFEATER of assumption 1 [basis: logical; added by review pass]: ULOI is defined by an approximate failure fraction, not an exact one. Laboratories that bracket it differently can report different ULOI values for the same material, so the gap between ULOI and MOC depends on procedure as well as on the material, and the two orders can differ for that reason alone.
          D1w DEFEATER of the inference [basis: logical; added by review pass]: Ordering by one number per material assumes that the thresholds of different materials do not cross as conditions vary within the ground test itself: thickness, temperature, specimen size, ignition source. If they cross, which order is obtained depends on which condition was chosen, and that choice is not fixed under C1.
        E1a EVIDENCE
            item: 6001B.T1.pass (acceptance_criterion), NASA-STD-6001B; access: full_text_read
              text (team wording in references.json): A material is self-extinguishing if no specimen burns more than 15 cm and no specimen propagates a flame by transfer of burning debris.
              where: 7.1.3a [FOCR 64]
              url: https://standards.nasa.gov/sites/default/files/standards/NASA/B-w/CHANGE-3/3/2025_06_25_NASA-STD-6001B_w_Change_3_FINAL_Admin-Change-FINAL.pdf
            covers (only what the item states):
              facility: not stated in the item
              flow: not stated in the item
              gravity: not stated in the item
              materials: not stated in the item
              oxygen: not stated in the item
              pressure: not stated in the item
        E1b EVIDENCE
            item: ICES14.onlyvalid (limitation), ICES-2014-179; access: full_text_read
              text (team wording in references.json): Test 1 is pass-fail and is only valid at the atmosphere tested.
              quote (as printed): "It is pass-fail and is only valid at the atmosphere tested."
              where: I: Introduction, p. 2 (sentence before, which opens with a drop capital: '[T]EST 1 of STD-6001[1] is an upward flame spread test to determine if a material is safe to use in a particular environment.')
              url: https://ntrs.nasa.gov/citations/20150004099
            covers (only what the item states):
              facility: not stated in the item
              flow: not stated in the item
              gravity: not stated in the item
              materials: not stated in the item
              oxygen: not stated in the item
              pressure: not stated in the item
        E1c EVIDENCE
            item: 6001B.T1.moc (definition), NASA-STD-6001B; access: full_text_read
              text (team wording in references.json): Maximum Oxygen Concentration (MOC): the maximum oxygen concentration at which at least five specimens pass the acceptance criteria of Test 1.
              quote (as printed): "Maximum Oxygen Concentration: The maximum oxygen concentration at which at least five specimens pass the acceptance criteria of this test."
              where: 7.1.4c
              url: https://standards.nasa.gov/sites/default/files/standards/NASA/B-w/CHANGE-3/3/2025_06_25_NASA-STD-6001B_w_Change_3_FINAL_Admin-Change-FINAL.pdf
            covers (only what the item states):
              facility: not stated in the item
              flow: not stated in the item
              gravity: not stated in the item
              materials: not stated in the item
              oxygen: not stated in the item
              pressure: not stated in the item
        E1d EVIDENCE
            item: OF2012.uloi (definition), NTRS-20130010991; access: full_text_read
              text (team wording in references.json): 1g ULOI: the oxygen concentration at which a material passes the NASA-STD-6001 Test 1 burn length criterion approximately half the time. 1g MOC: the oxygen concentration where at least five samples passed and at least one sample failed at 1 percent more oxygen by volume.
              quote (as printed): "The 1g ULOI is defined as the oxygen concentration at which a material passes the NASA STD 6001 Test 1 burn length criterion approximately half the time."
              where: p. 2 (the next sentence defines 1g MOC: 'the oxygen concentration where at least five samples passed the burning criterion (according to the NASA STD 6001 Test 1 definition) and where at least one sample failed in the environment that contained 1 percent more oxygen by volume')
              url: https://ntrs.nasa.gov/citations/20130010991
            covers (only what the item states):
              facility: not stated in the item
              flow: not stated in the item
              gravity: "1g ULOI"
              materials: not stated in the item
              oxygen: not stated in the item
              pressure: not stated in the item
        E1e EVIDENCE
            item: TB14639.modified (definition), TASKBOOK-14639; access: full_text_read
              text (team wording in references.json): A modified Test 1 measures the actual upward flammability limit (akin to the Limiting Oxygen Index) so that the margin of safety in the use environment can be assessed.
              where: Task Description
              url: https://taskbook.nasaprs.com/tbp/tbpdf.cfm?id=14639
            covers (only what the item states):
              facility: not stated in the item
              flow: not stated in the item
              gravity: not stated in the item
              materials: not stated in the item
              oxygen: not stated in the item
              pressure: not stated in the item
    C2 CLAIM: The held documents fix one atmosphere, an oxygen concentration and a total pressure, for a lunar habitat at which the order would have to hold.
      I2 INFERENCE [basis: team; team reasoning (AI-drafted), not a NASA statement]: The items name atmospheres for a Moon base, for landers and surface habitats, or for the most severe spacecraft environment (E2a to E2d). E2e states that design requirements need to specify the pressure and oxygen combinations permitted in the habitable volume. If one combination were fixed for the lunar habitat, the target of the carry-over would be defined. The items do not all name the same combination.
          assumption 1: The atmosphere named on the challenge page for a Moon base is the one a lunar-habitat ranking would be carried to.
          assumption 2: The atmosphere stays within its stated control band during use.
          assumption 3 [added by review pass]: An atmosphere is fully specified by oxygen concentration and total pressure; diluent gas and temperature are taken as fixed or irrelevant (EAWG.need and ISO16697.scope name further variables).
          assumption 4 [added by review pass]: The target of the carry-over is the nominal habitat atmosphere rather than the worst-case anticipated use environment that NASA-STD-6001B uses for material evaluation (6001B.focr12, 6001B.T1.o2level).
          assumption 5 [added by review pass]: A lunar habitat has one atmosphere throughout its habitable volume and over its life; no zone, phase (pre-breathe, airlock, suit interface) or off-nominal state needs its own target.
          assumption 6 [added by review pass]: Atmospheres named for landers, generic surface habitats, spacecraft or the ISS pre-breathe environment transfer to a lunar habitat; none of E2b to E2d names the Moon in its item text.
          assumption 7 [added by review pass]: The items are contemporaneous or the latest one is current; no item states which document governs the lunar habitat today.
          assumption 8 [added by review pass]: The held set of documents is complete enough that 'not fixed in the held set' can be read as 'not fixed'.
          assumption 9 [added by review pass]: Quantities across items share a basis (mole or volume percent; absolute or gauge pressure), so combinations can be compared as same or different.
          assumption 10 [added by review pass]: A single point target is what the downstream claims (C3 to C5) need, rather than a region (control box, one-sided bounds, 'combinations permitted').
          assumption 11 [added by review pass]: The challenge statement is an authoritative source for a design atmosphere, ranking above NASA design reports read in full.
          D2a DEFEATER of the inference [basis: documented (EAWG.atmospheres)]: EAWG.atmospheres calls its atmospheres recommendations, not requirements, and lists more than one pair for surface habitats.
              text: Recommended nominal atmospheres: 14.7 psia / 21% O2; 10.2 psia / 26.5% O2; 8.0 psia / 32% O2 (landers, surface habitats); 7.6 psia / 32% O2 (surface habitats). Control box +/-0.2 psia and +/-2.0% O2. Recommendations, not requirements.
          D2b DEFEATER of the inference [basis: documented (EA.8.2-34)]: EA.8.2-34 states that one recommended exploration atmosphere was altered after a re-evaluation; the target can move.
              text: After re-evaluation in 2012 the 8.0 psia / 32% O2 environment was altered to 8.2 psia / 34% O2.
          D2c DEFEATER of assumption 1 [basis: documented (EAWG.testing)]: EAWG.testing asks for materials ignition and flammability testing and certification to an oxygen concentration above the lower bound that CH.moonbase names.
              quote: These recommendations will also require materials ignition and flammability testing and certification to 34% oxygen concentration.
          D2d DEFEATER of assumption 1 [basis: documented (CH.moonbase)]: CH.moonbase words the Moon-base atmosphere as expected and likely; it is an expectation, not a specification, and the item was read by another session of the team.
              text: Moon Base and pressurized-rover atmosphere expected between spacesuit and Earth conditions: oxygen likely 30% or more, pressure 10.2 psi or less.
          D2e DEFEATER of the inference [basis: logical; added by review pass]: The inference ends by stating that the items do not all name the same combination, and its only route to C2 is a conditional ('If one combination were fixed...') whose antecedent is never asserted. As written it argues for the negation of C2, not for C2. Either C2 is restated as the negative or marked undeveloped, or the inference does not support its claim.
          D2f DEFEATER of the inference [basis: documented (TB008.o2); added by review pass]: E2e states a need ('need to specify'), not that a lunar-habitat requirement exists, and it says 'combinations permitted' in the plural, which points to a permitted set, not one atmosphere. As a child of C2 it supports the absence of a fixed target rather than its presence.
              item words (verbatim): "Design requirements need to specify pressure and % O2 combinations permitted in the habitable volume"
          D2g DEFEATER of the inference [basis: documented (SMAC.atmospheres); added by review pass]: Another held document lists two different total pressures as proposed atmospheres for upcoming missions, without naming the lunar habitat. The held set carries more than one candidate target and labels them as proposals.
              item words (verbatim): "10.2 and 8.2 psia as proposed atmospheres for upcoming missions"
          D2h DEFEATER of assumption 1 [basis: documented (ICES14.trend); added by review pass]: A held conference paper takes the test target to be the lowest expected total pressure for a spacecraft, an exploration atmosphere other than the challenge-page wording. The held items do not name one target. The words are from the item's 'where' field, the sentence before its quote.
              item words (verbatim): "start at the lowest expected total pressure for a spacecraft"
          D2i DEFEATER of assumption 1 [basis: documented (6001B.focr12); added by review pass]: Under the standard the evaluation target is the worst-case anticipated use environment, not the nominal habitat atmosphere. A ranking carried to the nominal Moon-base atmosphere would be carried to a target the standard does not use for material evaluation, and that target also includes temperature and thickness, not only oxygen and pressure.
              item words (verbatim): "The worst-case anticipated use environment (most hazardous pressure, temperature, material thickness, and fluid exposure conditions) shall be used in the evaluation of material suitability."
          D2j DEFEATER of assumption 1 [basis: documented (CH.moonbase); added by review pass]: The challenge-page item gives each variable as a one-sided bound, not a value, so it names an open region of atmospheres, not one combination; it covers 'Moon Base and pressurized-rover' together; and it writes 'psi', not 'psia', so whether the pressure is absolute is not stated in the item. This differs from D2d, which addresses only the 'expected' and 'likely' wording and the access level.
              item words (verbatim): "oxygen likely 30% or more, pressure 10.2 psi or less"
          D2k DEFEATER of assumption 1 [basis: logical; added by review pass]: The assumption raises one of the evidence leaves to define the target, and picks the one with the weakest access level (read by a teammate, no quote held) over items read in full, without giving a reason. The selection is unargued team reasoning.
          D2l DEFEATER of assumption 1 [basis: logical; added by review pass]: A Moon base on a challenge statement need not be the habitable volume whose materials are ranked: landers, pressurized rovers, airlocks and transfer vehicles serving the same base can run other atmospheres, and materials can move between them. The assumption equates one named volume with all volumes in which the ranked materials will be used.
          D2m DEFEATER of assumption 2 [basis: documented (6001B.T1.o2level); added by review pass]: The standard sets the test oxygen at the highest level the material could witness in use, which is not the controlled nominal band. Whether the atmosphere stays within its band is therefore not the question the standard asks; the relevant target is the extreme witnessed value, including off-nominal conditions.
              item words (verbatim): "with the oxygen level being the highest that the material could witness in use conditions"
          D2n DEFEATER of assumption 2 [basis: documented (EAWG.atmospheres); added by review pass]: Even if the assumption holds, a stated control band is a region, not a point; an order would have to hold at every point of the box, so staying within the band does not reduce the target to the one atmosphere C2 names.
              item words (verbatim): "Control box +/-0.2 psia and +/-2.0% O2."
          D2o DEFEATER of assumption 2 [basis: documented (ICES19.sensors); added by review pass]: ICES19.sensors states that on-board sensors were used to determine oxygen depletion during burns, so the oxygen around a burning sample is documented to change during an event. The item concerns an experiment's test volume, not a habitat; it shows only that the atmosphere during a fire is not the pre-fire atmosphere, which the assumption does not address.
              item words (verbatim): "to determine oxygen depletion, extinction oxygen concentrations"
          D2p DEFEATER of assumption 2 [basis: logical; added by review pass]: Fire concerns off-nominal states: leaks, oxygen-system faults, repressurization, suit and airlock interfaces, and local enrichment near oxygen sources or in poorly mixed pockets, which weaker buoyant mixing in reduced gravity may let persist. The assumption covers only the nominal bulk atmosphere, the state least relevant to a fire.
          D2q DEFEATER of the inference [basis: documented (EAWG.need); added by review pass]: C2 defines an atmosphere as an oxygen concentration and a total pressure only. A held NASA report names diluent gas as a separate variable of material flammability, and the items under C2 do not state the diluent, so even an agreed oxygen-pressure pair would not fix the atmosphere at which the order must hold.
              item words (verbatim): "Effects of pressure, gravity, oxygen mole fraction, and diluent gas on material flammability."
          D2r DEFEATER of the inference [basis: documented (ISO16697.scope); added by review pass]: A threshold is defined at a stated temperature and convective flow as well as pressure. The one atmosphere of C2 leaves temperature unfixed, so the target of the carry-over stays underdetermined even if oxygen and pressure were agreed.
              item words (verbatim): "at a given constant total pressure, temperature, convective flow, and gravity-level conditions"
          D2s DEFEATER of the inference [basis: documented (OF2012.test1env); added by review pass]: The combination in E2b is identified in another held item as the pre-breathe environment on the ISS for spacewalks, and both items say 'currently'. E2b names an ISS environment of a given date, not a lunar-habitat atmosphere; that its numbers agree with the challenge-page bound is not evidence that either is the lunar target.
              item words (verbatim): "which is the pre-breath environment on the ISS for spacewalks"
          D2t DEFEATER of the inference [basis: documented (EA.8.2-34); added by review pass]: E2d states only that one environment was altered; it names no vehicle, habitat or the Moon, is read as abstract only, and comes from an evidence report on hypobaric hypoxia, not on flammability. The inference's grouping of E2a to E2d as atmospheres for a Moon base, landers, surface habitats or the most severe spacecraft environment is not supported by this item's words.
              item words (verbatim): "was altered to"
          D2u DEFEATER of the inference [basis: logical; added by review pass]: The items come from different dates and programmes, and at least one records a later change; the inference treats a set of time-stamped proposals as if they could converge on a current target. Without a statement of which document is current for the lunar habitat, agreement or disagreement among them says little about what is fixed.
          D2v DEFEATER of the inference [basis: logical; added by review pass]: The items do not state a common basis for their quantities: some give oxygen as mole fraction, some as a percent without saying volume or mole, and one gives pressure without saying absolute or gauge. Comparing combinations across items, and judging whether they are the same, assumes a common basis the items do not state.
          D2w DEFEATER of the inference [basis: logical; added by review pass]: C2 is about the held documents. A requirement that fixes a lunar-habitat atmosphere could exist in documents not held, and held items could be superseded by documents not held; the inference cannot tell 'not fixed' from 'not found in the held set'.
          D2x DEFEATER of the inference [basis: documented (CH.moonbase); added by review pass]: The lunar habitat is defined in two places that the argument uses side by side. CH.moonbase, the bound used in C2 and E2a, sets only a lower bound on oxygen and an upper bound on pressure. The scenario lunar_habitat in pipeline/spec/scenarios.json, whose evidence package supplies the counts under C3.1 and C4.1, has the same nominal pair but adds an oxygen cap that its note calls the team's and a pressure range that its note says reaches above the bound (ranges cited below). The counts and the bound therefore do not describe the same target.
              item words (verbatim): "oxygen likely 30% or more, pressure 10.2 psi or less"
              cited value pipeline/spec/scenarios.json ["scenarios", {"id": "lunar_habitat"}, "nominal"] = {"o2_pct": 30.0, "pressure_kpa": 70.3}
              cited value pipeline/spec/scenarios.json ["scenarios", {"id": "lunar_habitat"}, "ranges"] = {"o2_pct": {"max": 36, "max_inclusive": true, "min": 30}, "pressure_kpa": {"max": 85.8, "min": null}}
              cited value CH.moonbase [] = {"o2_pct_min": 30, "pressure_psia_max": 10.2}
        E2a EVIDENCE
            item: CH.moonbase (design_value), CHALLENGE-2026; access: read_by_teammate
              text (team wording in references.json): Moon Base and pressurized-rover atmosphere expected between spacesuit and Earth conditions: oxygen likely 30% or more, pressure 10.2 psi or less.
              where: Potential considerations: Spacesuits and oxygen concentration
              url: https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/
            covers (only what the item states):
              facility: not stated in the item
              flow: not stated in the item
              gravity: not stated in the item
              materials: not stated in the item
              oxygen: "oxygen likely 30% or more"
              pressure: "pressure 10.2 psi or less"
        E2b EVIDENCE
            item: TB14639.worstcase (design_value), TASKBOOK-14639; access: full_text_read
              text (team wording in references.json): Test 1 is conducted in the most severe environment expected in the spacecraft, currently 30% oxygen at 10.2 psia.
              where: Task Description
              url: https://taskbook.nasaprs.com/tbp/tbpdf.cfm?id=14639
            covers (only what the item states):
              facility: not stated in the item
              flow: not stated in the item
              gravity: not stated in the item
              materials: not stated in the item
              oxygen: "30% oxygen"
              pressure: "10.2 psia"
        E2c EVIDENCE
            item: EAWG.atmospheres (design_value), NASA-TP-2010-216134; access: full_text_read
              text (team wording in references.json): Recommended nominal atmospheres: 14.7 psia / 21% O2; 10.2 psia / 26.5% O2; 8.0 psia / 32% O2 (landers, surface habitats); 7.6 psia / 32% O2 (surface habitats). Control box +/-0.2 psia and +/-2.0% O2. Recommendations, not requirements.
              where: Executive Summary; Table 10
              url: https://www.nasa.gov/wp-content/uploads/2023/03/henninger-8.2-34-atm-tp216134-2010.pdf
            covers (only what the item states):
              facility: not stated in the item
              flow: not stated in the item
              gravity: not stated in the item
              materials: not stated in the item
              oxygen: "14.7 psia / 21% O2; 10.2 psia / 26.5% O2; 8.0 psia / 32% O2 (landers, surface habitats); 7.6 psia / 32% O2 (surface habitats)"
              pressure: "14.7 psia / 21% O2; 10.2 psia / 26.5% O2; 8.0 psia / 32% O2 (landers, surface habitats); 7.6 psia / 32% O2 (surface habitats)"
        E2d EVIDENCE
            item: EA.8.2-34 (design_value), NTRS-20150021491; access: abstract_only
              text (team wording in references.json): After re-evaluation in 2012 the 8.0 psia / 32% O2 environment was altered to 8.2 psia / 34% O2.
              where: Abstract
              url: https://ntrs.nasa.gov/citations/20150021491
            covers (only what the item states):
              facility: not stated in the item
              flow: not stated in the item
              gravity: not stated in the item
              materials: not stated in the item
              oxygen: "8.2 psia / 34% O2"
              pressure: "8.2 psia / 34% O2"
        E2e EVIDENCE
            item: TB008.o2 (recommendation), OCHMO-TB-008; access: full_text_read
              text (team wording in references.json): Design requirements need to specify the pressure and percent O2 combinations permitted in the habitable volume.
              quote (as printed): "Design requirements need to specify pressure and % O2 combinations permitted in the habitable volume"
              where: Fire Prevention and Material Flammability
              url: https://www.nasa.gov/wp-content/uploads/2023/12/ochmo-tb-008-fire-protection.pdf
            covers (only what the item states):
              facility: not stated in the item
              flow: not stated in the item
              gravity: not stated in the item
              materials: not stated in the item
              oxygen: not stated in the item
              pressure: not stated in the item
    C3 CLAIM: An order of oxygen thresholds measured at one total pressure in normal gravity is kept at the total pressure of the lunar habitat.
      I3 INFERENCE [basis: team; team reasoning (AI-drafted), not a NASA statement]: The held ground studies measured oxygen thresholds of the same materials at more than one total pressure in normal gravity (E3a, E3c) and report that the threshold depends on total pressure (E3b, E3f, E3g), primarily on oxygen concentration and to a lesser extent on total pressure (E3d, E3e). If the change with pressure had the same direction and a similar size for every material ranked, the order at one pressure would be kept at another. C3.1 asks whether the NASA PSI tables could check this.
          assumption 1: The change of threshold with total pressure has the same direction and a similar size for the materials being ranked.
          assumption 2: The lunar-habitat pressure lies inside the pressure range of the held studies, so no extrapolation is needed.
          assumption 3: Results on pressure obtained in normal gravity apply in the same way at lunar gravity.
          assumption 4 [added by review pass]: The order at the reference pressure is itself resolved: the thresholds of the ranked materials differ by more than the test step and the test-to-test scatter.
          assumption 5 [added by review pass]: The materials being ranked are among the materials tested in the held pressure studies, with the same thickness, form and lot.
          assumption 6 [added by review pass]: Different threshold quantities (MOC, ULOI, limiting oxygen concentration for flame spread, general flammability) share the same pressure dependence, so evidence on one can stand for another.
          assumption 7 [added by review pass]: The threshold varies monotonically and nearly linearly with pressure between and beyond the tested points, for every ranked material and not only for materials in the MOC band that H2011.linear names.
          assumption 8 [added by review pass]: The lunar habitat has one known total pressure; the candidate atmospheres differ and one was altered.
          assumption 9 [added by review pass]: The pressure dependence measured near each material's own threshold applies at the habitat oxygen concentration.
          assumption 10 [added by review pass]: The habitat diluent is nitrogen, as in the held tests; EAWG.need names diluent gas as a separate variable.
          assumption 11 [added by review pass]: The quiescent, no-flow test condition (6001B.T1.noflow) stands for a ventilated habitat; the inference does not address flow.
          assumption 12 [added by review pass]: Test temperature, ignition source and facility are the same across the studies combined and as in the case of use.
          assumption 13 [added by review pass]: Statements worded 'generally' or 'to a lesser extent' (SAE2008.mocpressure, LANGE.lesser) apply to each material being ranked, not only on average.
          assumption 14 [added by review pass]: Checking whether PSI tables record pressure (C3.1) bears on whether pressure dependence can be checked, although the PSI flight tests were run at one nominal pressure and in microgravity, not in normal gravity.
          D3a DEFEATER of assumption 1 [basis: documented (H2006.range)]: H2006.range states that the effect of total pressure on oxygen concentration thresholds is greater for materials with higher thresholds. An effect that differs between materials can change their order.
              quote: To determine if this relationship holds outside the 48.2 to 101.3 kPa (7 to 14.7 psia) range further testing is recommended.
          D3b DEFEATER of assumption 1 [basis: documented (SAE2008.mocpressure)]: SAE2008.mocpressure names a few fuels, which appear to have halogen species in common, with a stronger dependence on pressure.
              quote: The Test 1 materials flammability data published by WSTF (ref. 7) demonstrate that the 1g MOCs are not generally a strong function of pressure but instead vary primarily with oxygen concentration.
          D3c DEFEATER of assumption 1 [basis: documented (URBAN14.loc)]: URBAN14.loc reports a strong dependence on pressure for one material, against the lesser extent stated in LANGE.lesser.
              quote: The strong dependence on pressure suggests either kinetic effects or flow effects.
          D3d DEFEATER of the inference [basis: documented (H2011.cannot)]: H2011.cannot states that, for at least one material tested, a material that meets its threshold at one atmosphere would fail Test 1 at another atmosphere with less oxygen and a higher total pressure.
              quote: For at least one of the materials tested, the data indicate that a material with an MOC of 30% oxygen at 10.2 psia would fail NASA-STD-(I)-6001B Test 1 at 25.9% oxygen and 14.7 psia.
          D3e DEFEATER of assumption 3 [basis: logical]: No held item measures the pressure dependence of a threshold at lunar gravity; the assumption that it is the same as in normal gravity rests on no document.
          D3f DEFEATER of assumption 1 [basis: documented (H2006.table2); added by review pass]: In the held values of H2006.table2 (cited below) the order of materials changes between pressure columns: Viton A is above Silicone and Zytel 42 in the lowest-pressure column and below both in the middle column, and Silicone is above Zytel 42 in the lowest-pressure column, level with it in the middle column and below it in the highest. The item gives no uncertainty or test step, so whether a difference of one point is resolved is not confirmed.
              item words (verbatim): "Maximum oxygen concentration (MOC, vol %) which consistently results in self-extinguishment, at 48.2, 85.3 and 101.3 kPa total pressure"
              cited value H2006.table2 ["moc_vol_pct_by_total_pressure_kpa", "columns_kpa"] = [48.2, 85.3, 101.3]
              cited value H2006.table2 ["moc_vol_pct_by_total_pressure_kpa", "Viton A"] = [29, 21, 21]
              cited value H2006.table2 ["moc_vol_pct_by_total_pressure_kpa", "Silicone"] = [28, 23, 21]
              cited value H2006.table2 ["moc_vol_pct_by_total_pressure_kpa", "Zytel 42"] = [25, 23, 23]
          D3g DEFEATER of assumption 1 [basis: documented (H2011.linear); added by review pass]: E3f, which the inference cites to show a pressure dependence, gives the slope of MOC against total pressure across its materials as ranging several-fold (values cited below). The same leaf that shows a pressure dependence states that its size differs between materials, against 'a similar size'.
              item words (verbatim): "The maximum slope was -0.975% oxygen/psia and the minimum was -0.251% oxygen/psia"
              cited value H2011.linear ["moc_slope_pct_o2_per_psia_max"] = -0.975
              cited value H2011.linear ["moc_slope_pct_o2_per_psia_min"] = -0.251
          D3h DEFEATER of assumption 1 [basis: documented (OF2012.uloi); added by review pass]: OF2012.uloi defines the normal-gravity MOC by a step of one percent oxygen. Two materials whose MOCs lie within one step have no resolved order at the reference pressure, so even a small difference in pressure slope can reverse or tie them at another pressure.
              item words (verbatim): "at least one sample failed at 1 percent more oxygen by volume"
          D3i DEFEATER of assumption 1 [basis: logical; added by review pass]: 'Similar size' is not defined. Whether an order is kept depends on comparing the gap between two materials' thresholds with the difference of their slopes times the pressure change. The inference states neither gaps nor slope differences for any pair of ranked materials, so even if the assumption holds the conclusion does not follow for closely spaced materials.
          D3j DEFEATER of assumption 1 [basis: logical; added by review pass]: The held pressure studies tested their own sets of materials. The materials the team wants to rank may not be in those sets, and for those materials the assumption has no evidence at all.
          D3k DEFEATER of assumption 1 [basis: logical; added by review pass]: Same direction and a similar mean slope do not exclude curves that bend differently between the tested pressures, so two materials' threshold curves can still cross between test points.
          D3l DEFEATER of assumption 2 [basis: documented (H2006.range); added by review pass]: H2006.range limits its pressure relationship to the tested range and recommends further testing outside it (range cited below). CH.moonbase gives the Moon-base pressure only as an upper bound, with no lower bound, so the habitat pressure is not shown to lie inside that range.
              item words (verbatim): "To determine if this relationship holds outside the 48.2 to 101.3 kPa (7 to 14.7 psia) range further testing is recommended."
              cited value H2006.range ["pressure_kpa_range"] = [48.2, 101.3]
          D3m DEFEATER of assumption 2 [basis: documented (H2011.linear); added by review pass]: H2011.linear states its approximately linear dependence only for materials in a stated MOC band, and the item states no pressure range. For materials outside that band, and for any pressure, the item sets no range inside which interpolation would hold.
              item words (verbatim): "For materials with MOC in the range 25-35% oxygen the data indicate an approximately linear dependence of MOC on total pressure"
          D3n DEFEATER of assumption 2 [basis: documented (EAWG.atmospheres); added by review pass]: EAWG.atmospheres lists more than one candidate pressure for surface habitats and calls them recommendations, not requirements; EA.8.2-34 records that one was altered. The total pressure of the lunar habitat is not one fixed value, so whether it lies inside any range cannot be settled.
              item words (verbatim): "Recommendations, not requirements."
          D3o DEFEATER of assumption 2 [basis: documented (THOMSEN18.care); added by review pass]: THOMSEN18.care warns that low pressure eventually affects the chemical kinetics, so trends found at higher pressure may not carry over as pressure is lowered. The paper is about concurrent flame spread (its title), not thresholds, which limits this defeater but does not remove it.
              item words (verbatim): "eventually low pressure will affect the chemical kinetics of the process"
          D3p DEFEATER of assumption 2 [basis: logical; added by review pass]: Lying between tested pressures still requires interpolation. With only a few test pressures per material, behaviour between them is assumed, not measured, so 'no extrapolation' does not mean 'no inference beyond the data'.
          D3q DEFEATER of assumption 3 [basis: documented (URBAN14.loc); added by review pass]: URBAN14.loc attributes the strong pressure dependence it found possibly to flow effects. If part of the pressure dependence is a flow effect, it can change when the gravity level changes the flow, so a normal-gravity pressure slope cannot simply be carried over.
              item words (verbatim): "The strong dependence on pressure suggests either kinetic effects or flow effects."
          D3r DEFEATER of assumption 3 [basis: documented (OF2012.table1); added by review pass]: OF2012.table1 gives, at the same reduced pressure, lunar-minus-normal-gravity oxygen shifts for Mylar G and for Ultem 1000 that differ (values cited below). The gravity effect is material-dependent, and each material has lunar values at only one pressure, so how pressure and gravity interact cannot be read from it.
              item words (verbatim): "oxygen margin of safety (delta O2 %) -3.1 Martian, -5.75 Lunar, -4.1 0g"
              cited value OF2012.table1 ["rows", {"material": "Mylar G"}, "delta_o2_pct_lunar"] = -5.75
              cited value OF2012.table1 ["rows", {"material": "Ultem 1000"}, "delta_o2_pct_lunar"] = -2.8
              cited value OF2012.table1 ["rows", {"material": "Mylar G"}, "pressure_psia"] = 10.2
              cited value OF2012.table1 ["rows", {"material": "Ultem 1000"}, "pressure_psia"] = 10.2
          D3s DEFEATER of assumption 3 [basis: documented (ICES19.fanoff); added by review pass]: ICES19.fanoff names high-oxygen low-pressure atmospheres and partial gravity as conditions in which a flame may survive without ventilation. Both act on the role of flow, so a pressure effect measured in normal gravity need not carry over to partial gravity.
              item words (verbatim): "ventilation may not be necessary for a flame to survive in high-oxygen low-pressure atmospheres or in partial gravity"
          D3t DEFEATER of assumption 3 [basis: documented (TB008.gaps); added by review pass]: TB008.gaps calls material flammability in partial gravity a major gap for exploration missions; the assumption carries a normal-gravity pressure result into that gap.
              item words (verbatim): "Material flammability in partial gravity remains a major gap for exploration missions."
          D3u DEFEATER of assumption 3 [basis: documented (TB008.assess); added by review pass]: TB008.assess asks that material flammability be assessed in the relevant cabin atmospheres and gravity levels; carrying a normal-gravity pressure result to lunar gravity does not do that.
              item words (verbatim): "Material flammability must be assessed in relevant cabin atmospheres and gravity levels for exploration transit vehicles and habitats."
          D3v DEFEATER of assumption 3 [basis: documented (TB14639.gap); added by review pass]: TB14639.gap states that normal-gravity flammability tests do not correlate with reduced-gravity flammability. D4c uses it against I4; it bears on this assumption as well.
              item words (verbatim): "Normal-gravity flammability tests do not correlate with flammability in ventilated, micro- or reduced-gravity conditions."
          D3w DEFEATER of assumption 3 [basis: logical; added by review pass]: In a quiescent upward test the gas flow at the flame comes from buoyancy, which depends on both gravity and gas density. A pressure slope measured in normal gravity can include a buoyancy contribution that is different at lunar gravity.
          D3x DEFEATER of the inference [basis: documented (ICES19.pressure); added by review pass]: The inference says C3.1 asks whether the NASA PSI tables could check the pressure step. ICES19.pressure states that BASS-II did not vary pressure. A recorded pressure is not a varied pressure, so even if C3.1 holds it cannot test the first or the third assumption.
              item words (verbatim): "Pressure was not varied from 1 atmosphere."
          D3y DEFEATER of the inference [basis: documented (ICES14.onlyvalid); added by review pass]: ICES14.onlyvalid states that Test 1 is only valid at the atmosphere tested. Carrying an order from one total pressure to another runs against the stated validity of the test whose results are being ordered.
              item words (verbatim): "It is pass-fail and is only valid at the atmosphere tested."
          D3z DEFEATER of the inference [basis: documented (G125.conditions); added by review pass]: G125.conditions states that fire-limit results do not necessarily apply to conditions not reproduced in the test, and that limits measured at one set of conditions are not necessarily the lowest thresholds. The spec uses it under I0, not here.
              item words (verbatim): "However, its results do not necessarily apply to any condition that does not faithfully reproduce the conditions during test."
          D3aa DEFEATER of the inference [basis: documented (EAWG.need); added by review pass]: EAWG.need lists the effects of pressure, gravity, oxygen mole fraction and diluent gas on material flammability as a research and technology need. The inference treats the pressure effect as known well enough to carry orders, against a NASA working group that lists it as a need.
              item words (verbatim): "Effects of pressure, gravity, oxygen mole fraction, and diluent gas on material flammability."
          D3ab DEFEATER of the inference [basis: logical; added by review pass]: The evidence mixes different threshold quantities: MOC (H2006, H2011), ULOI and MOC (H2007), limiting oxygen concentration for flame spread (URBAN14), and general flammability (LANGE, ICES14). A pressure dependence shown for one quantity is not shown for another, yet the inference treats them as one threshold.
          D3ac DEFEATER of the inference [basis: documented (H2007.fixedpressure); added by review pass]: The inference cites E3c for thresholds of the same materials measured at more than one total pressure. The item states a single fixed total pressure, so one of the two leaves for that premise does not support it, and the item does not state that its materials are those of H2006.
              item words (verbatim): "determined at a fixed total pressure of"
          D3ad DEFEATER of the inference [basis: documented (LANGE.lesser); added by review pass]: E3e is a general statement, in a contractor report on atmosphere design, about materials flammability, not about oxygen thresholds or any material. It reports no measurement and says nothing about whether the pressure effect differs between materials, which is what the order depends on.
              item words (verbatim): "materials flammability depends strongly on oxygen concentration (volume percent) and to a lesser extent on total pressure"
          D3ae DEFEATER of the inference [basis: documented (ICES14.both); added by review pass]: E3g states only that material flammability is a function of both pressure and oxygen, in a section on testing at constant oxygen partial pressure. It says nothing about the oxygen-concentration threshold, any material, or whether the pressure effect is alike across materials.
              item words (verbatim): "Material flammability, on the other hand, is a function of both pressure and oxygen."
        E3a EVIDENCE
            item: H2006.table2 (published_result), JTE-2006-HIRSCH; access: full_text_read
              text (team wording in references.json): Maximum oxygen concentration (MOC, vol %) which consistently results in self-extinguishment, at 48.2, 85.3 and 101.3 kPa total pressure, normal gravity, quiescent, for eleven materials (values in 'values').
              quote (as printed): "TABLE 2 — Oxygen concentration, oxygen partial pressure and total pressure flammability limits for selected materials at ambient initial temperatures"
              where: Table 2, p. 4 (page viewed as an image; all cells agree with the text layer)
              url: https://ntrs.nasa.gov/citations/20070005041
            covers (only what the item states):
              facility: not stated in the item
              flow: "quiescent"
              gravity: "normal gravity"
              materials: "eleven materials"
              oxygen: not stated in the item
              pressure: "at 48.2, 85.3 and 101.3 kPa total pressure"
        E3b EVIDENCE
            item: H2006.depends (published_result), JTE-2006-HIRSCH; access: full_text_read
              text (team wording in references.json): For the range of total pressures tested, the oxygen concentration and oxygen partial pressure flammability thresholds are a near linear function of total pressure; the thresholds depend on the total pressure.
              quote (as printed): "The oxygen concentration/oxygen partial pressure flammability thresholds depend on the total pressure and appear to increase with increasing oxygen concentration (and oxygen partial pressure)."
              where: Abstract, p. 1 (the sentence before it: 'For the range of total pressures tested, the oxygen concentration and oxygen partial pressure flammability thresholds show a near linear function of total pressure.')
              url: https://ntrs.nasa.gov/citations/20070005041
            covers (only what the item states):
              facility: not stated in the item
              flow: not stated in the item
              gravity: not stated in the item
              materials: not stated in the item
              oxygen: not stated in the item
              pressure: "For the range of total pressures tested"
        E3c EVIDENCE
            item: H2007.fixedpressure (published_result), NTRS-20070018178; access: full_text_read
              text (team wording in references.json): The oxygen concentration flammability thresholds (ULOI, MOC) were determined at a fixed total pressure of 70.1 kPa.
              quote (as printed): "The oxygen concentration flammability thresholds were determined at a fixed total pressure of 70.1 kPa."
              where: 2. Experimental, PDF page 3; Table 2 is titled 'Upward Limiting Oxygen Indices (ULOI) and Maximum Oxygen Concentrations when Self-Extinguishment Occurs (MOC) for Selected Materials at 70.1 kPa Total Pressures'
              url: https://ntrs.nasa.gov/citations/20070018178
            covers (only what the item states):
              facility: not stated in the item
              flow: not stated in the item
              gravity: not stated in the item
              materials: not stated in the item
              oxygen: not stated in the item
              pressure: "a fixed total pressure of 70.1 kPa"
        E3d EVIDENCE
            item: SAE2008.mocpressure (published_result), SAE-2008-01-2055; access: abstract_only
              text (team wording in references.json): The Test 1 flammability data published by White Sands show that the 1g MOCs are not generally a strong function of pressure but vary primarily with oxygen concentration; a few fuels, which appear to have halogen species in common, have a stronger dependence on pressure.
              quote (as printed): "The Test 1 materials flammability data published by WSTF (ref. 7) demonstrate that the 1g MOCs are not generally a strong function of pressure but instead vary primarily with oxygen concentration."
              where: Discussion, p. 6 of NASA/TM-2008-215260 (the NASA edition of SAE 2008-01-2055)
              url: https://doi.org/10.4271/2008-01-2055
            covers (only what the item states):
              facility: "The Test 1 flammability data published by White Sands"
              flow: not stated in the item
              gravity: "1g MOCs"
              materials: "a few fuels, which appear to have halogen species in common"
              oxygen: not stated in the item
              pressure: not stated in the item
        E3e EVIDENCE
            item: LANGE.lesser (published_result), NASA-CR-2005-213689; access: full_text_read
              text (team wording in references.json): Materials flammability depends strongly on oxygen concentration (volume percent) and to a lesser extent on total pressure, in contrast with human respiration, which depends primarily on oxygen partial pressure.
              quote (as printed): "By contrast with human respiration that depends primarily on oxygen partial pressure in the atmosphere, materials flammability depends strongly on oxygen concentration (volume percent) and to a lesser extent on total pressure."
              where: 2.3.1 Flammability, p. 11
              url: https://ntrs.nasa.gov/citations/20050185597
            covers (only what the item states):
              facility: not stated in the item
              flow: not stated in the item
              gravity: not stated in the item
              materials: not stated in the item
              oxygen: not stated in the item
              pressure: not stated in the item
        E3f EVIDENCE
            item: H2011.linear (published_result), AIAA-2011-5067; access: full_text_read
              text (team wording in references.json): For materials with MOC in the range 25-35% oxygen the data indicate an approximately linear dependence of MOC on total pressure; slope between -0.975 and -0.251 % oxygen per psia, average -0.607.
              quote (as printed): "The maximum slope was -0.975% oxygen/psia and the minimum was -0.251% oxygen/psia, with an average of -0.607% oxygen/psia."
              where: I. Introduction, p. 2, after 'For materials with maximum oxygen concentrations (MOCs) at which extinguishment occurs in the range of 25-35% oxygen, the data indicate there is an approximately linear dependence of MOCs on total pressure Pt having the form: MOC = m Pt + b (1)'
              url: https://ntrs.nasa.gov/citations/20110008636
            covers (only what the item states):
              facility: not stated in the item
              flow: not stated in the item
              gravity: not stated in the item
              materials: "For materials with MOC in the range 25-35% oxygen"
              oxygen: not stated in the item
              pressure: not stated in the item
        E3g EVIDENCE
            item: ICES14.both (published_result), ICES-2014-179; access: full_text_read
              text (team wording in references.json): Material flammability is a function of both pressure and oxygen.
              quote (as printed): "Material flammability, on the other hand, is a function of both pressure and oxygen."
              where: IV: Proposed Normoxic Upward Limiting Pressure (NULP), p. 8
              url: https://ntrs.nasa.gov/citations/20150004099
            covers (only what the item states):
              facility: not stated in the item
              flow: not stated in the item
              gravity: not stated in the item
              materials: not stated in the item
              oxygen: not stated in the item
              pressure: not stated in the item
        C3.1 CLAIM: The NASA PSI tests that the team counts for the flammability-limit need record the total pressure of each test.
          I3.1 INFERENCE [basis: team; team reasoning (AI-drafted), not a NASA statement]: The claim is checked by setting the number of tests counted for the need beside the number of those tests whose total pressure is recorded in the experimental tables (E3.1a, E3.1b). Both are team counts of the evidence package for the lunar habitat.
              assumption 1: The tests that the team counts for the flammability-limit need (rules in pipeline/README.md) are the PSI tests that bear on oxygen thresholds.
              assumption 2 [added by review pass]: 'Recorded in the experimental tables as mapped by the pipeline' is what C3.1 means by recording the total pressure of each test; the claim does not say tables, and PSI raw data and investigator papers hold pressure information outside them (PSISAF.pressure_column, SAF17.sensors).
              assumption 3 [added by review pass]: The pipeline's table mapping has picked up every pressure column the PSI files contain; pipeline/README.md says the Saffire raw-data 'Ambient Pressure' column is not mapped.
              assumption 4 [added by review pass]: There is a decision rule saying which relation between the two counts would support the claim and which would count against it; the inference states none.
              assumption 5 [added by review pass]: E3.1b counts the same population as E3.1a; it counts tests of tier 'other', and equals the counted tests only because every counted test is of that tier in this package.
              assumption 6 [added by review pass]: Counts computed inside the lunar-habitat evidence package bear on a claim about the counted PSI tests in general; C3.1 is not scenario-specific, but its evidence is.
              assumption 7 [added by review pass]: An investigation-level nominal statement, or a model assumption, of the pressure does not count as a per-test record; the inference relies on this distinction but does not say it, and the counting rule treats such statements as meeting the pressure condition.
              assumption 8 [added by review pass]: Pressures, if recorded, would vary across tests enough to check a pressure dependence; without this C3.1 has no bearing on C3.
              assumption 9 [added by review pass]: Orbital (microgravity) PSI tests are relevant to C3, a claim about normal-gravity thresholds at different pressures.
              assumption 10 [added by review pass]: The two counts are computed correctly and reproducibly by the pipeline; no independent check is cited.
              assumption 11 [added by review pass]: The two investigations in the count (BASS-II and Saffire-II) can be pooled, although their pressure documentation differs in kind.
              D3.1a DEFEATER of the inference [basis: logical]: A pressure absent from the experimental tables may be stated in an investigator's paper or a PSI record; the count reads the tables only.
              D3.1b DEFEATER of the inference [basis: logical; added by review pass]: The inference does not say which result of the comparison would support the claim and which would count against it. As written it describes a check, not a warrant: whatever the two counts are, the claim is said to be checked. The package shows no counted test with a pressure in the tables, so its own children count against C3.1, and the inference still sits under C3.1 as if it held the claim up.
              D3.1c DEFEATER of the inference [basis: documented (PSISAF.pressure_column); added by review pass]: PSISAF.pressure_column states that the NASA PSI raw data hold an 'Ambient Pressure' column for each Saffire-I and Saffire-II sample. A count that reads only the mapped experimental tables cannot tell whether the PSI tests record a pressure; for the Saffire-II tests in the count a per-sample pressure record exists outside the mapped tables. D3.1a states this doubt in logical form; this item makes it documented.
                  item words (verbatim): "has a column 'Ambient Pressure' with unit 'PSIA'"
              D3.1d DEFEATER of the inference [basis: documented (SAF17.sensors); added by review pass]: SAF17.sensors states that pressure was recorded upstream of the fuel in the Saffire flow duct. A zero count of pressures in the tables then reads a property of the team's table mapping, not of the tests.
                  item words (verbatim): "Oxygen concentration, carbon dioxide, and pressure were also recorded just upstream of the fuel in the flow duct."
              D3.1e DEFEATER of the inference [basis: documented (PSIBASS2.procedure); added by review pass]: PSIBASS2.procedure states that the BASS-II documents record no pressure reading. For the BASS-II part of the count the route of D3.1a (a pressure stated in a PSI record) is not open, so the two investigations in the count differ in kind and one count of 'recorded' merges them.
                  item words (verbatim): "No pressure reading is recorded in the procedure, the data FAQ or the test matrix."
              D3.1f DEFEATER of the inference [basis: documented (ICES15.cstr); added by review pass]: ICES15.cstr states that the glovebox dilution model assumes constant pressure and uses a nominal pressure in its oxygen calculation. A statement about the whole investigation that rests on an assumed pressure is not a record of the pressure of each test, so documented pressure is not recorded pressure when the claim is judged.
                  item words (verbatim): "The glovebox dilution model assumes constant pressure, temperature and volume"
              D3.1g DEFEATER of the inference [basis: documented (MSG.negative); added by review pass]: MSG.negative states that the glovebox working volume is held below the pressure of the crew living area, with no magnitude given. A cabin-level nominal pressure cannot be taken as the pressure of each BASS-II test, which widens the gap between what the claim asks and what any document gives.
                  item words (verbatim): "held at a negative pressure with respect to the crew living area"
              D3.1h DEFEATER of the inference [basis: documented (ICES19.pressure); added by review pass]: ICES19.pressure states that BASS-II did not vary pressure. I3 says C3.1 asks whether the PSI tables could check the pressure dependence of a threshold order. Tests at one pressure cannot show a change with pressure, so a favourable answer to C3.1 would not bear on C3.
                  item words (verbatim): "Pressure was not varied from 1 atmosphere."
              D3.1i DEFEATER of the inference [basis: logical; added by review pass]: The counted tests were flown in orbit, while C3 concerns thresholds measured at different total pressures in normal gravity. A pressure record for these tests, whatever its form, does not reach the normal-gravity claim that C3.1 is placed under.
              D3.1j DEFEATER of the inference [basis: logical; added by review pass]: The counted set is admitted under a team rule that lets a sentence about the whole table meet the pressure condition. Counting recorded pressures inside a set already admitted by documented pressure is circular: the population was chosen while the pressure question was waived, so the count cannot test whether pressure is recorded for the tests that bear on the need.
              D3.1k DEFEATER of the inference [basis: logical; added by review pass]: E3.1b is the count of pressures recorded for the counted tests of tier 'other' (its path names usable_elsewhere), not for the counted tests as such. It equals the latter only because every counted test of this package is of tier 'other'; the inference does not state that condition, and it would not hold for a scenario whose ranges matched some tests.
              D3.1l DEFEATER of the inference [basis: logical; added by review pass]: The covers of E3.1a and E3.1b record the package's target (lunar gravity and the scenario's oxygen and pressure ranges), not the conditions of the counted tests, which in the team's mapping are microgravity tests with no pressure in the tables. A reader of covers beside a count can take them for the tests' conditions.
              D3.1m DEFEATER of assumption 1 [basis: documented (FLEX.objectives); added by review pass]: FLEX.objectives states a flammability-boundary objective for FLEX, for liquid fuels. In the evidence package FLEX (PSI-69) is counted for another need and not for this one, and its tests record oxygen and pressure (entry cited below). If FLEX tests bear on oxygen thresholds, the counted set is not the set of PSI tests that do, and it leaves out tests whose tables hold a pressure.
                  item words (verbatim): "map the flammability boundaries for liquid fuel combustion in reduced gravity"
                  cited value data/pipeline/evidence/scenario_lunar_habitat.json ["environment", "recorded_tests", {"investigation_id": "PSI-69"}] = {"atmosphere": 17, "counted_for": ["S1"], "fuel_phase": "liquid", "investigation_id": "PSI-69", "oxygen_only": 0, "pressure_only": 0, "title": "Flame Extinguishment Experiment"}
              D3.1n DEFEATER of assumption 1 [basis: documented (NIEHAUS15.expected); added by review pass]: NIEHAUS15.expected states that the Saffire-II sample was chosen for a flammability limit close to the expected test atmosphere, cabin air. Each Saffire-II test holds one oxygen level near cabin air, so a single test bears on a threshold only as one point near air; whether it bears on oxygen thresholds in the sense of the need is the team's reading.
                  item words (verbatim): "Silicone was chosen because its flammability limit is close to the expected test atmosphere"
              D3.1o DEFEATER of assumption 1 [basis: logical; added by review pass]: The counting rule accepts burn time and oxygen consumed as outcome variables, which no document read names as a measure of a flammability limit. Tests admitted only through those variables may not bear on oxygen thresholds, so the counted set can hold tests outside the need as well as miss tests inside it.
              D3.1p DEFEATER of assumption 1 [basis: logical; added by review pass]: The count also drops tests whose objective link is not supported and tests with no oxygen value in the table. A test that bears on a threshold but has an unsupported objective link or a missing cell is outside the count, so the assumption equates a team filter with a physical property of the tests.
            E3.1a EVIDENCE (count): data/pipeline/evidence/scenario_lunar_habitat.json ["needs", {"need_id": "P1"}, "counts", "usable_tests"] = 133
                file note: Counts of recorded NASA PSI tests. Team computation, not a NASA conclusion and not safety guidance.
                covers (the environment of the evidence package the count belongs to, team ranges; null = not set; not the conditions of the tests):
                  facility: not stated in the file
                  flow: null
                  gravity: "lunar"
                  materials: not stated in the file
                  oxygen: {"max": 36, "max_inclusive": true, "min": 30, "min_inclusive": true}
                  pressure: {"max": 85.8, "max_inclusive": false, "min": null, "min_inclusive": true}
            E3.1b EVIDENCE (count): data/pipeline/evidence/scenario_lunar_habitat.json ["needs", {"need_id": "P1"}, "usable_elsewhere", "pressure_kpa", "recorded"] = 0
                file note: Counts of recorded NASA PSI tests. Team computation, not a NASA conclusion and not safety guidance.
                covers (the environment of the evidence package the count belongs to, team ranges; null = not set; not the conditions of the tests):
                  facility: not stated in the file
                  flow: null
                  gravity: "lunar"
                  materials: not stated in the file
                  oxygen: {"max": 36, "max_inclusive": true, "min": 30, "min_inclusive": true}
                  pressure: {"max": 85.8, "max_inclusive": false, "min": null, "min_inclusive": true}
    C4 CLAIM: An order of oxygen thresholds measured in normal gravity is kept at lunar gravity.
      I4 INFERENCE [basis: team; team reasoning (AI-drafted), not a NASA statement]: E4a prints, for the same materials, thresholds in normal gravity and at lunar gravity; the OF2012 items (E4a, E4b) are the only held items with values at lunar gravity (team search of references.json). Comparing the order of the materials in the normal-gravity rows and in the lunar rows of E4a bears directly on the claim. E4c and E4d compare normal gravity with microgravity, not with lunar gravity. E4e and E4f state that normal-gravity tests do not match flammability in reduced gravity. A shift of every threshold by the same amount would keep the order; the claim needs the shift to be similar across materials, not absent.
          assumption 1: Thresholds from short drop-tower tests stand for thresholds in lasting lunar gravity.
          assumption 2: The extinction criteria used in low gravity and in normal gravity measure the same property.
          assumption 3: The flow in the low-gravity tests stands for the flow in a lunar habitat.
          assumption 4: The materials in E4a stand for the materials to be ranked.
          assumption 5 [added by review pass]: Which threshold defines the order (ULOI, MOC, or their mean as used in the margin) is fixed in advance, and the order is the same under each choice; in E4a Ultem 1000 and Nomex HT90-40 tie by normal-gravity ULOI but not by normal-gravity MOC.
          assumption 6 [added by review pass]: A tie counts either as a kept order or as a lost one; the claim does not say which.
          assumption 7 [added by review pass]: Differences between materials in E4a are larger than test resolution and scatter; none is stated.
          assumption 8 [added by review pass]: Values printed at different pressures in E4a can be placed in a single order.
          assumption 9 [added by review pass]: The gravity effect does not depend on pressure or oxygen level, so an order kept at the pressures of E4a is also kept at the habitat's lower pressure and higher oxygen.
          assumption 10 [added by review pass]: The way lunar gravity was produced in the drop tower, not stated in the item, reproduces lunar buoyant flow without adding accelerations or flows of its own.
          assumption 11 [added by review pass]: The normal-gravity thresholds in E4a are the normal-gravity ground-test ranking of the top claim; standard Test 1 is pass or fail and gives no order (ICES14.onlyvalid).
          assumption 12 [added by review pass]: Sample geometry, thickness, ignition source and ignition energy were the same in the normal-gravity and low-gravity runs of E4a.
          assumption 13 [added by review pass]: Ignitability and flame persistence change with gravity by the same amount for every material.
          assumption 14 [added by review pass]: Gravity effects between zero and normal gravity are monotone, so the microgravity items (E4c, E4d) say something about the lunar level; the margins in E4a do not change steadily with gravity level.
          assumption 15 [added by review pass]: An order kept among the few materials of E4a carries to other materials.
          assumption 16 [added by review pass]: The team transcription of Table I in OF2012.table1 matches the printed table; the item's quote is only the table title, so its numbers are checked against team wording, not against the source.
          assumption 17 [added by review pass]: A single rig's results stand for lunar gravity without independent replication.
          D4a DEFEATER of the inference [basis: documented (OF2012.table1)]: OF2012.table1 states a different oxygen margin for each material at lunar gravity. Margins that differ between materials can change their order.
              quote: Table I: Limiting Oxygen Molar Concentrations and Oxygen Margin of Safety for Different Gravity Levels
          D4b DEFEATER of assumption 2 [basis: documented (OF2012.margin)]: OF2012.margin states that the low-gravity limits come from drop tests and that their extinction criteria are not the same as in normal gravity.
              text: Oxygen margins of safety (low-gravity limit minus 1g limit, % O2 by mole) were negative by as much as -5.75 (lunar gravity, Mylar G at 10.2 psia); the largest at Martian gravity was -3.35 (Nomex HT90-40) and at 0g -4.1 (Mylar G). Normal-gravity screening tests may not be conservative. The low-g limits come from 5 s drop tests and their extinction criteria are not the same as in 1g.
          D4c DEFEATER of the inference [basis: documented (TB14639.gap)]: TB14639.gap states that normal-gravity flammability tests do not correlate with flammability in ventilated, micro- or reduced-gravity conditions.
              text: Normal-gravity flammability tests do not correlate with flammability in ventilated, micro- or reduced-gravity conditions.
          D4d DEFEATER of assumption 3 [basis: documented (TM217036.threshold)]: TM217036.threshold states that the oxygen threshold in reduced gravity is a function of the local convective velocity. An order given without its flow is not defined.
              quote: However, the oxygen threshold has been shown to be lower in reduced-gravity and is a function of the local convective velocity. Therefore, the objective of this task was to determine the oxygen flammability threshold in reduced-gravity for materials identified by NASA Materials and Processes personnel and quantify the difference from thresholds determined in normal gravity.
          D4e DEFEATER of assumption 4 [basis: documented (OF2012.table1)]: OF2012.table1 prints one of its materials at a different pressure from the other two, so a comparison across all of its materials mixes pressure with material.
              quote: Table I: Limiting Oxygen Molar Concentrations and Oxygen Margin of Safety for Different Gravity Levels
          D4f DEFEATER of the inference [basis: documented (OF2012.table1); added by review pass]: In the held values of OF2012.table1 (cited below) Ultem 1000 is above Nomex HT90-40 by normal-gravity MOC and level with it by normal-gravity ULOI; at lunar gravity the two are level by both ULOI* and MOC*. By MOC, a strict order at normal gravity becomes a tie at lunar gravity; Mylar G stays lowest under both quantities. The only direct comparison held therefore does not show the order kept for that pair, and whether it counts as kept or lost depends on the quantity chosen and on how a tie is counted, which the inference fixes for neither. Nomex HT90-40 was tested at another pressure from the other two, so this pair also mixes pressure with gravity.
              item words (verbatim): "Ultem 1000 at 10.2 psia: 1g ULOI 23.5 and MOC 23.0"
              cited value OF2012.table1 ["rows", {"material": "Mylar G"}, "pressure_psia"] = 10.2
              cited value OF2012.table1 ["rows", {"material": "Mylar G"}, "uloi_o2_pct_1g"] = 21.2
              cited value OF2012.table1 ["rows", {"material": "Mylar G"}, "moc_o2_pct_1g"] = 20.0
              cited value OF2012.table1 ["rows", {"material": "Mylar G"}, "uloi_star_o2_pct_lunar"] = 15.6
              cited value OF2012.table1 ["rows", {"material": "Mylar G"}, "moc_star_o2_pct_lunar"] = 14.1
              cited value OF2012.table1 ["rows", {"material": "Ultem 1000"}, "pressure_psia"] = 10.2
              cited value OF2012.table1 ["rows", {"material": "Ultem 1000"}, "uloi_o2_pct_1g"] = 23.5
              cited value OF2012.table1 ["rows", {"material": "Ultem 1000"}, "moc_o2_pct_1g"] = 23.0
              cited value OF2012.table1 ["rows", {"material": "Ultem 1000"}, "uloi_star_o2_pct_lunar"] = 21.0
              cited value OF2012.table1 ["rows", {"material": "Ultem 1000"}, "moc_star_o2_pct_lunar"] = 19.9
              cited value OF2012.table1 ["rows", {"material": "Nomex HT90-40"}, "pressure_psia"] = 14.7
              cited value OF2012.table1 ["rows", {"material": "Nomex HT90-40"}, "uloi_o2_pct_1g"] = 23.5
              cited value OF2012.table1 ["rows", {"material": "Nomex HT90-40"}, "moc_o2_pct_1g"] = 22.1
              cited value OF2012.table1 ["rows", {"material": "Nomex HT90-40"}, "uloi_star_o2_pct_lunar"] = 21.0
              cited value OF2012.table1 ["rows", {"material": "Nomex HT90-40"}, "moc_star_o2_pct_lunar"] = 19.9
          D4g DEFEATER of the inference [basis: documented (OF2012.table1); added by review pass]: In OF2012.table1 (values cited below) the margin does not change steadily with gravity level, and the pattern differs by material: for Mylar G the lunar margin is the most negative of the low-gravity levels, for Nomex HT90-40 the Martian margin is. A material's shift at zero gravity does not tell its shift at lunar gravity, which undercuts any use of the microgravity items (E4c, E4d), or of an interpolation between zero and normal gravity, to say something about the lunar order.
              item words (verbatim): "delta O2 % -3.35 Martian, -2.35 Lunar, -0.3 0g"
              cited value OF2012.table1 ["rows", {"material": "Mylar G"}, "delta_o2_pct_martian"] = -3.1
              cited value OF2012.table1 ["rows", {"material": "Mylar G"}, "delta_o2_pct_lunar"] = -5.75
              cited value OF2012.table1 ["rows", {"material": "Mylar G"}, "delta_o2_pct_0g"] = -4.1
              cited value OF2012.table1 ["rows", {"material": "Nomex HT90-40"}, "delta_o2_pct_martian"] = -3.35
              cited value OF2012.table1 ["rows", {"material": "Nomex HT90-40"}, "delta_o2_pct_lunar"] = -2.35
              cited value OF2012.table1 ["rows", {"material": "Nomex HT90-40"}, "delta_o2_pct_0g"] = -0.3
          D4h DEFEATER of assumption 1 [basis: documented (OF2012.table1); added by review pass]: OF2012.table1 defines its lunar thresholds by whether the flame went out or survived within the drop. A flame that survived the full drop may still go out later, and the time to extinction can differ from material to material, so each lunar value is bounded by the drop duration and could move by a different amount in lasting lunar gravity. The order read from the lunar rows is an order of drop-limited values.
              item words (verbatim): "MOC* is the maximum oxygen concentration at which the flame self-extinguished during the drop, ULOI* the minimum at which it survived the full drop; these criteria are not the same as in 1g."
          D4i DEFEATER of assumption 1 [basis: documented (SAF16.saffire2); added by review pass]: SAF16.saffire2 names MOC limits in long-term low gravity as something still to be investigated, apart from short-duration tests. The item is about microgravity, not lunar gravity, but it shows that the investigators did not treat short-duration limits as standing for long-duration ones. U4.2 cites the same item as a study asked, not as a defeater of I4.
              item words (verbatim): "investigate the low-gravity Maximum Oxygen Concentration (MOC) flammability limits in long-term low gravity"
          D4j DEFEATER of assumption 1 [basis: logical; added by review pass]: A drop tower gives free fall; a lunar gravity level inside a falling package has to be produced by some rig, and the item does not say how. Such a rig can add accelerations, start-up transients or induced flows that a lunar habitat does not have, and they can affect materials differently.
          D4k DEFEATER of assumption 3 [basis: documented (ICES19.fanoff); added by review pass]: ICES19.fanoff suggests that in partial gravity a flame may survive without ventilation, so the flow that sustains it is set by buoyancy as well as by the fan. The flow at lunar gravity is then not the forced flow of microgravity tests, and E4a states no flow at all, so the flow at which its lunar order holds is not known.
              item words (verbatim): "ventilation may not be necessary for a flame to survive in high-oxygen low-pressure atmospheres or in partial gravity"
          D4l DEFEATER of assumption 3 [basis: documented (ICES19.boundary); added by review pass]: ICES19.boundary describes a threshold that does not change in one direction with flow: it has a branch at low flow and another at high flow. The boundaries of two materials can then cross as flow changes, so an order read at one flow, or at an unstated flow, may reverse at another. This goes beyond D4d: even with the flow stated, an order at one flow does not carry to the habitat's flow.
              item words (verbatim): "with a quenching branch at low flow and a blowoff branch at high flow"
          D4m DEFEATER of assumption 3 [basis: documented (ICES19.limits); added by review pass]: For the single material in ICES19.limits (values cited below), whether the low-gravity value lies below or between the normal-gravity values depends on the flow configuration chosen (concurrent or opposed) and on the normal-gravity spread direction (downward or upward). The size and even the sign of the shift depend on configuration, so a comparison of shifts across materials needs the configuration fixed and matched to the habitat.
              item words (verbatim): "minimum flammable value for the opposed-flow rods"
              cited value ICES19.limits ["o2_pct_min_concurrent_rod"] = 13.6
              cited value ICES19.limits ["o2_pct_min_opposed_rod"] = 16.3
              cited value ICES19.limits ["o2_pct_1g_downward"] = 17
              cited value ICES19.limits ["o2_pct_1g_upward"] = 15.4
          D4n DEFEATER of assumption 3 [basis: documented (ISO16697.scope); added by review pass]: ISO16697.scope defines a threshold only at a stated convective flow and gravity level. E4a states no flow, so its lunar values are not thresholds in this sense until the flow is known.
              item words (verbatim): "The oxygen concentration threshold is determined at a given constant total pressure, temperature, convective flow and gravity level."
          D4o DEFEATER of assumption 3 [basis: documented (CP2004.flam.velocity); added by review pass]: CP2004.flam.velocity states that the comparison with Test 1 depends on the velocity and flow direction chosen for it. The item is cited in U4.3, but the inference does not use it against this assumption, which it contradicts directly.
              item words (verbatim): "The question of conservatism of Test 1 therefore may rest on the determination of velocity and flow direction at which to compare."
          D4p DEFEATER of the inference [basis: documented (URBAN14.loc); added by review pass]: The material that E4a prints at another pressure, Nomex HT90-40, is the one for which URBAN14.loc reports a strong dependence of the limiting oxygen concentration on pressure. Its place in the order at the pressure of the other two materials cannot be read from E4a, and it belongs to the pair whose order is in question. This adds to D4e.
              item words (verbatim): "the authors report a strong dependence on pressure"
          D4q DEFEATER of the inference [basis: documented (H2006.range); added by review pass]: Correcting the Nomex HT90-40 rows of E4a to the pressure of the other materials would shift them by an amount that depends on the threshold itself, which differs between normal and lunar gravity. No single correction puts all rows of E4a on a common pressure, so the gravity effect and the pressure effect cannot be separated in the item.
              item words (verbatim): "is greater for materials with higher thresholds"
          D4r DEFEATER of assumption 2 [basis: documented (RG.ignite); added by review pass]: If ignition gets easier in low gravity, a low-gravity threshold read from whether a flame was established and survived mixes ignitability with flame persistence. The ignition part can change by a different amount for each material, so the low-gravity and normal-gravity limits may not rank the same property.
              item words (verbatim): "Materials are easier to ignite in low gravity because of reduced natural convective cooling from the fuel surface."
          D4s DEFEATER of assumption 4 [basis: documented (CP2003.prev.thickthin); added by review pass]: E4a does not state sample thickness. If its materials are of one thermal regime, an order kept among them says nothing about thick or thin habitat materials, since the thick-thin relationship is stated as not yet established.
              item words (verbatim): "A better understanding of the relationship between flame spread across thermally thick and thin materials must be established."
          D4t DEFEATER of assumption 4 [basis: logical; added by review pass]: E4a holds only a handful of materials. An order kept among them cannot show that the order is kept for other pairs: pairs whose normal-gravity thresholds lie close together are the ones most likely to swap, and E4a has only one such pair, which ties.
          D4u DEFEATER of the inference [basis: documented (TB008.gaps); added by review pass]: NASA's technical brief calls material flammability in partial gravity a major gap. Resting C4 on a single drop-tower table sits against that statement.
              item words (verbatim): "Material flammability in partial gravity remains a major gap for exploration missions."
          D4v DEFEATER of the inference [basis: documented (G125.conditions); added by review pass]: A normal-gravity order is a result at one set of conditions. G125.conditions says such results do not necessarily apply to a condition, such as lunar gravity, that does not reproduce the test.
              item words (verbatim): "its results do not necessarily apply to any condition that does not faithfully reproduce the conditions during test"
          D4w DEFEATER of the inference [basis: documented (OF2012.margin); added by review pass]: E4b is named among the only held items with values at lunar gravity, but it gives one lunar value, a margin rather than a threshold, for one material. It cannot yield an order by itself, and its own words (screening tests may not be conservative; criteria not the same as in normal gravity) speak against the claim.
              item words (verbatim): "Normal-gravity screening tests may not be conservative."
          D4x DEFEATER of the inference [basis: documented (SAE2008.uloi); added by review pass]: E4c gives only an upper bound on the size of the shift from normal to zero gravity. It says nothing about whether the shift is similar across materials, which is what the inference says C4 needs; it is read as abstract only, names no material, facility, flow or pressure, and is about zero gravity, not lunar gravity.
              item words (verbatim): "were greater than those in 0g by up to 4% oxygen mole fraction"
          D4y DEFEATER of the inference [basis: documented (ICES19.limits); added by review pass]: E4d is about a single material, PMMA, so it cannot speak to an order across materials. Its normal-gravity values are downward and upward spread extinction limits, not Test 1 ULOI or MOC, so they are not the normal-gravity quantity of E4a.
              item words (verbatim): "BASS-II PMMA"
          D4z DEFEATER of the inference [basis: logical; added by review pass]: E4a gives no scatter, repeat count or bracket width for any value. Differences between materials, and the tie between two of them, may lie within test resolution, so the item can show neither that the order is kept nor that it is lost.
          D4aa DEFEATER of the inference [basis: logical; added by review pass]: E4a and E4b are one paper, one facility and one set of drop-tower runs. An order seen in one rig may reflect that rig's flow, ignition and timing rather than lunar gravity, and no independent item at lunar gravity is held to check it.
          D4ab DEFEATER of the inference [basis: logical; added by review pass]: The inference says that comparing the orders in E4a bears directly on the claim, but it never states the outcome of that comparison. A reader cannot tell whether the team takes E4a to support C4, to undercut it, or to leave it open, so the inference is not open to attack on that point.
          D4ac DEFEATER of the inference [basis: logical; added by review pass]: E4e and E4f say that normal-gravity tests do not correlate with, or are not conservative relative to, reduced-gravity flammability. If those statements hold generally, C4 fails unless lunar gravity is an exception, and nothing held shows that it is. The inference lists these items as children of C4 without saying how a claim they contradict is supported by them.
        E4a EVIDENCE
            item: OF2012.table1 (published_result), NTRS-20130010991; access: full_text_read
              text (team wording in references.json): Limiting oxygen molar concentrations (% O2) from Table I. Mylar G at 10.2 psia: 1g ULOI 21.2 and MOC 20.0; Martian ULOI* 18.0 and MOC* 17.0; Lunar ULOI* 15.6 and MOC* 14.1; 0g ULOI* 17.0 and MOC* 16.0; oxygen margin of safety (delta O2 %) -3.1 Martian, -5.75 Lunar, -4.1 0g. Ultem 1000 at 10.2 psia: 1g ULOI 23.5 and MOC 23.0; Martian ULOI* 22.0 and MOC* 21.1; Lunar ULOI* 21.0 and MOC* 19.9; 0g ULOI* 24.0 and MOC* 23.0; delta O2 % -1.7 Martian, -2.8 Lunar, 0.25 0g. Nomex HT90-40 at 14.7 psia: 1g ULOI 23.5 and MOC 22.1; Martian ULOI* 19.9 and MOC* 19.0; Lunar ULOI* 21.0 and MOC* 19.9; 0g ULOI* 23.0 and MOC* 22.0; delta O2 % -3.35 Martian, -2.35 Lunar, -0.3 0g. Delta O2 % is the mean of the low-gravity ULOI* and MOC* minus the mean of the 1g ULOI and MOC (Eq. 1). The low-gravity limits come from 5.18 s drop tower tests: MOC* is the maximum oxygen concentration at which the flame self-extinguished during the drop, ULOI* the minimum at which it survived the full drop; these criteria are not the same as in 1g.
              quote (as printed): "Table I: Limiting Oxygen Molar Concentrations and Oxygen Margin of Safety for Different Gravity Levels"
              where: Table I, p. 6
              url: https://ntrs.nasa.gov/citations/20130010991
            covers (only what the item states):
              facility: "5.18 s drop tower tests"
              flow: not stated in the item
              gravity: "1g"; "Martian"; "Lunar"; "0g"
              materials: "Mylar G"; "Ultem 1000"; "Nomex HT90-40"
              oxygen: not stated in the item
              pressure: "Mylar G at 10.2 psia"; "Ultem 1000 at 10.2 psia"; "Nomex HT90-40 at 14.7 psia"
        E4b EVIDENCE
            item: OF2012.margin (published_result), NTRS-20130010991; access: full_text_read
              text (team wording in references.json): Oxygen margins of safety (low-gravity limit minus 1g limit, % O2 by mole) were negative by as much as -5.75 (lunar gravity, Mylar G at 10.2 psia); the largest at Martian gravity was -3.35 (Nomex HT90-40) and at 0g -4.1 (Mylar G). Normal-gravity screening tests may not be conservative. The low-g limits come from 5 s drop tests and their extinction criteria are not the same as in 1g.
              where: Table I (p. 6); p. 7; Conclusions (p. 8)
              url: https://ntrs.nasa.gov/citations/20130010991
            covers (only what the item states):
              facility: "5 s drop tests"
              flow: not stated in the item
              gravity: "lunar gravity"; "Martian gravity"; "0g"
              materials: "Mylar G"; "Nomex HT90-40"
              oxygen: not stated in the item
              pressure: "Mylar G at 10.2 psia"
        E4c EVIDENCE
            item: SAE2008.uloi (published_result), SAE-2008-01-2055; access: abstract_only
              text (team wording in references.json): 1g Upward Limiting Oxygen Index (ULOI) and 1g Maximum Oxygen Concentration (MOC) were greater than those in 0g by up to 4% oxygen mole fraction.
              where: Abstract
              url: https://doi.org/10.4271/2008-01-2055
            covers (only what the item states):
              facility: not stated in the item
              flow: not stated in the item
              gravity: "1g"; "0g"
              materials: not stated in the item
              oxygen: not stated in the item
              pressure: not stated in the item
        E4d EVIDENCE
            item: ICES19.limits (published_result), ICES-2019-BASS2; access: full_text_read
              text (team wording in references.json): BASS-II PMMA: minimum oxygen concentration in the flammability boundary from the concurrent (stagnation-flow) rod tests 13.6% O2; minimum flammable value for the opposed-flow rods 16.3% O2 (no comparable boundary was obtained for opposed flow); normal-gravity PMMA extinction limits 17% O2 (downward spread) and 15.4% O2 (upward spread).
              where: Sections D, F
              url: https://hdl.handle.net/2346/84505
            covers (only what the item states):
              facility: "BASS-II"
              flow: "concurrent (stagnation-flow) rod tests"; "opposed-flow rods"
              gravity: "normal-gravity"
              materials: "BASS-II PMMA"
              oxygen: not stated in the item
              pressure: not stated in the item
        E4e EVIDENCE
            item: TB14639.gap (knowledge_gap), TASKBOOK-14639; access: full_text_read
              text (team wording in references.json): Normal-gravity flammability tests do not correlate with flammability in ventilated, micro- or reduced-gravity conditions.
              where: Task Description
              url: https://taskbook.nasaprs.com/tbp/tbpdf.cfm?id=14639
            covers (only what the item states):
              facility: not stated in the item
              flow: "ventilated"
              gravity: "micro- or reduced-gravity conditions"
              materials: not stated in the item
              oxygen: not stated in the item
              pressure: not stated in the item
        E4f EVIDENCE
            item: RG.test1 (published_result), NP-2015-10-034-JSC; access: full_text_read
              text (team wording in references.json): Test 1 is not conservative: materials can burn at lower oxygen levels in microgravity than on Earth.
              where: Highlights and Lessons Learned: Low-Stretch (Low-Velocity) Flames, p. 31
              url: https://www.nasa.gov/wp-content/uploads/2016/05/np-2015-10-034-jsc_combustion_in_reduced_gravity-iss-mini-book-011116-508.pdf
            covers (only what the item states):
              facility: not stated in the item
              flow: not stated in the item
              gravity: "microgravity"
              materials: not stated in the item
              oxygen: not stated in the item
              pressure: not stated in the item
        C4.1 CLAIM: The NASA PSI data hold flammability-limit tests recorded at lunar gravity.
          I4.1 INFERENCE [basis: team; team reasoning (AI-drafted), not a NASA statement]: E4.1c, the challenge page, states that PSI holds no partial-gravity combustion data yet. E4.1a is the team's count of PSI tests for the flammability-limit need in the lunar-habitat package, and E4.1b the count of those tests that match the package's oxygen or pressure and are recorded at the package's gravity level. The claim is true only if the challenge page is out of date or the counts show tests at lunar gravity.
              assumption 1: The gravity level recorded for each PSI test (from the investigation's constants in sources.json) is correct.
              assumption 2 [added by review pass]: The investigations mapped in sources.json are every PSI investigation that holds combustion tests, and PSI has not gained investigations since the team's download.
              assumption 3 [added by review pass]: The counting rule of the need (material, starting oxygen, at least one outcome) would keep a lunar-gravity flammability test if PSI held one.
              assumption 4 [added by review pass]: The gravity vocabulary of sources.json has a value for lunar gravity, so a lunar test could ever be marked 'same' for the package.
              assumption 5 [added by review pass]: A lunar-gravity test would fall in the package's oxygen range, or its oxygen and pressure ranges; otherwise E4.1b would never count it.
              assumption 6 [added by review pass]: 'Recorded at lunar gravity' has a fixed meaning (lasting lunar gravity, or a short drop-tower or aircraft simulation), and the challenge page and the counts use the same meaning.
              assumption 7 [added by review pass]: The challenge page's 'partial-gravity combustion data' includes lunar-gravity flammability-limit tests and is about PSI as a whole.
              assumption 8 [added by review pass]: The teammate's paraphrase in CH.partial_gravity matches the page's wording; the item has no quote and was not read by the session that wrote the argument.
              assumption 9 [added by review pass]: The challenge page is correct about PSI, not only current; the inference names only 'out of date' as a way for it to fail.
              assumption 10 [added by review pass]: Each PSI table holds tests at a single gravity level, so one constant per table can describe every test in it.
              assumption 11 [added by review pass]: The two counts are independent lines of evidence, although both come from the same team mapping.
              D4.1a DEFEATER of the inference [basis: logical]: E4.1b counts only the tests matched to the package's oxygen or pressure; a lunar-gravity test outside those ranges would not appear in it.
              D4.1b DEFEATER of the inference [basis: documented (SAF17.pressure); added by review pass]: SAF17.pressure states that the Saffire tests were run at normal pressure, above the package's pressure range, and the package records the oxygen of all counted tests below its oxygen range (values cited below). No counted test reaches the matched tiers, so the zero in E4.1b comes from the atmosphere filter and would hold whatever gravity the tests had.
                  item words (verbatim): "All tests were performed at normal pressure (1 atm)"
                  cited value data/pipeline/evidence/scenario_lunar_habitat.json ["needs", {"need_id": "P1"}, "usable_elsewhere", "o2_pct"] = {"max": 22.2, "min": 13.6, "not_ambient": 0, "recorded": 133, "unit": "% by volume"}
                  cited value data/pipeline/evidence/scenario_lunar_habitat.json ["environment", "ranges"] = {"flow_cms": null, "o2_pct": {"max": 36, "max_inclusive": true, "min": 30, "min_inclusive": true}, "pressure_kpa": {"max": 85.8, "max_inclusive": false, "min": null, "min_inclusive": true}}
                  cited value data/pipeline/evidence/scenario_lunar_habitat.json ["needs", {"need_id": "P1"}, "counts"] = {"atmosphere": 0, "matched_added_gas": 0, "matched_flow_in_range": 0, "matched_flow_not_recorded": 0, "matched_same_gravity": 0, "other": 133, "oxygen_only": 0, "pressure_only": 0, "recorded_outside_objective": 2, "usable_tests": 133}
              D4.1c DEFEATER of the inference [basis: documented (ICES19.pressure); added by review pass]: ICES19.pressure states that BASS-II varied oxygen only over a range below the package's oxygen range and did not vary pressure from one atmosphere. No counted BASS-II test can reach the matched tiers, so E4.1b has no case on which to test the gravity question.
                  item words (verbatim): "BASS-II varied oxygen from 13% to 22%"
              D4.1d DEFEATER of the inference [basis: documented (OF2012.table1); added by review pass]: A held document prints flammability limits at lunar gravity from drop-tower tests, so lunar-gravity limit data exist outside the counted tables. The inference does not check whether such data were deposited in a PSI investigation that sources.json does not map; the item does not say whether they are in PSI.
                  item words (verbatim): "Lunar ULOI* 15.6 and MOC* 14.1"
              D4.1e DEFEATER of the inference [basis: documented (OF2012.table1); added by review pass]: The claim's phrase 'recorded at lunar gravity' is not defined. Lunar gravity can be produced briefly in a drop tower, as this item reports. Whether such a short test counts decides whether the claim is true, and neither the inference nor its evidence settles it.
                  item words (verbatim): "The low-gravity limits come from 5.18 s drop tower tests"
              D4.1f DEFEATER of the inference [basis: logical; added by review pass]: The disjunction in the inference ('true only if the challenge page is out of date or the counts show tests at lunar gravity') leaves out other routes: PSI could hold lunar-gravity tests in an investigation that sources.json does not map, or in a table the counting rule rejects for lack of a starting oxygen or an outcome, or the page could be wrong rather than out of date. In each case the claim is true and neither branch shows it.
              D4.1g DEFEATER of the inference [basis: logical; added by review pass]: Every gravity constant in sources.json is the word microgravity, so no counted test can ever be marked 'same' for a lunar package. A zero in E4.1b is fixed by how the team built the mapping, not observed in the data, and the counts cannot serve as an independent check on the challenge page.
              D4.1h DEFEATER of the inference [basis: logical; added by review pass]: E4.1a is a count of tests at any gravity, all carrying the team's microgravity constant. It bears on the claim only through the gravity constant of each table, and the inference does not say how a count of microgravity tests supports or weakens a claim about lunar-gravity tests.
              D4.1i DEFEATER of the inference [basis: logical; added by review pass]: The inference is attached as support to C4.1, but its text and evidence argue that C4.1 is false. Inside the argument tree the node reads as support for a claim that its own evidence contradicts, unless the tool shows the direction.
              D4.1j DEFEATER of the inference [basis: logical; added by review pass]: The challenge-page statement is dated by the word 'yet', and the date the teammate read it is not part of the evidence. PSI may have added data since then, for example from the future source the page names, and nothing in E4.1c shows when it was true.
              D4.1k DEFEATER of the inference [basis: logical; added by review pass]: The inference describes E4.1b as the tests that match the package's oxygen or pressure, but the count covers only tests of tiers 'atmosphere' and 'oxygen_only' (pipeline/evidence.py), so a test matched on pressure alone is not in it. D4.1a repeats the same wording.
              D4.1l DEFEATER of the inference [basis: documented (CH.partial_gravity); added by review pass]: E4.1c is a teammate's paraphrase of the challenge page, with no quote held and no date of reading, and the inference writes it as the page's own statement. The item speaks of partial-gravity combustion data in general, not of flammability-limit tests at lunar gravity.
                  item words (verbatim): "PSI holds no partial-gravity combustion data yet"
              D4.1m DEFEATER of assumption 1 [basis: logical; added by review pass]: A constant is set once per table, not per test. If a PSI table mixes flight rows with ground or reference rows, the constant mislabels some tests. The assumption speaks of each test, but the mapping holds only one value per investigation.
              D4.1n DEFEATER of assumption 1 [basis: logical; added by review pass]: Even if every constant is correct, the assumption covers only the investigations that sources.json maps. A lunar-gravity investigation in PSI with no entry in sources.json is outside the assumption, and the inference still reads the counts as if they covered PSI as a whole.
              D4.1o DEFEATER of assumption 1 [basis: logical; added by review pass]: The constants are the team's mapping, and no reference item is cited for any of them. The assumption is checked against no document and rests on team assignment alone.
            E4.1a EVIDENCE (count): data/pipeline/evidence/scenario_lunar_habitat.json ["needs", {"need_id": "P1"}, "counts", "usable_tests"] = 133
                file note: Counts of recorded NASA PSI tests. Team computation, not a NASA conclusion and not safety guidance.
                covers (the environment of the evidence package the count belongs to, team ranges; null = not set; not the conditions of the tests):
                  facility: not stated in the file
                  flow: null
                  gravity: "lunar"
                  materials: not stated in the file
                  oxygen: {"max": 36, "max_inclusive": true, "min": 30, "min_inclusive": true}
                  pressure: {"max": 85.8, "max_inclusive": false, "min": null, "min_inclusive": true}
            E4.1b EVIDENCE (count): data/pipeline/evidence/scenario_lunar_habitat.json ["needs", {"need_id": "P1"}, "counts", "matched_same_gravity"] = 0
                file note: Counts of recorded NASA PSI tests. Team computation, not a NASA conclusion and not safety guidance.
                covers (the environment of the evidence package the count belongs to, team ranges; null = not set; not the conditions of the tests):
                  facility: not stated in the file
                  flow: null
                  gravity: "lunar"
                  materials: not stated in the file
                  oxygen: {"max": 36, "max_inclusive": true, "min": 30, "min_inclusive": true}
                  pressure: {"max": 85.8, "max_inclusive": false, "min": null, "min_inclusive": true}
            E4.1c EVIDENCE
                item: CH.partial_gravity (knowledge_gap), CHALLENGE-2026; access: read_by_teammate
                  text (team wording in references.json): PSI holds no partial-gravity combustion data yet; the page names LUCI as a future source.
                  where: Potential considerations: Partial-gravity data
                  url: https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/
                covers (only what the item states):
                  facility: not stated in the item
                  flow: not stated in the item
                  gravity: "partial-gravity"
                  materials: not stated in the item
                  oxygen: not stated in the item
                  pressure: not stated in the item
        U4.2 UNDEVELOPED: Oxygen thresholds of materials have been measured in lasting lunar gravity, longer than a drop-tower test.
            evidence: no item held
            study asked for by CP2003.roadmap.limit (NASA-CP-2003-212103): "Determine limiting O2 and flow for flame propagation on practical materials in µg and partial-g"
            study asked for by CH.partial_gravity (CHALLENGE-2026): PSI holds no partial-gravity combustion data yet; the page names LUCI as a future source.
            study asked for by SAF16.saffire2 (ICES-2016-SAFFIRE): "The objective of the tests to be conducted on Saffire-II is to investigate the low-gravity Maximum Oxygen Concentration (MOC) flammability limits in long-term low gravity."
            study asked for by SMT.gap.flammability (ICES-2016-SAFFIRE): "Growth rate of fire hazard"
            study asked for by TB008.gaps (OCHMO-TB-008): "Material flammability in partial gravity remains a major gap for exploration missions."
        U4.3 UNDEVELOPED: The ventilation flow speed and direction of a lunar habitat, at which an order of thresholds would be compared, are stated in the held documents.
            evidence: no item held
            study asked for by CP2004.flam.velocity (NASA-CP-2004-213205-VOL1): "The question of conservatism of Test 1 therefore may rest on the determination of velocity and flow direction at which to compare."
            study asked for by CP2003.prev.o2flow (NASA-CP-2003-212103): "There is a need for additional microgravity data on the effects of oxygen and flow on ignition, combustion and flame propagation for real engineering materials."
    C5 CLAIM: The combined change to high oxygen, low total pressure and lunar gravity leaves the order of materials unchanged.
      I5 INFERENCE [basis: team; team reasoning (AI-drafted), not a NASA statement]: E5a prints lunar-gravity thresholds for materials whose column heading names the same total pressure as the upper bound in E5b; these are the only held values that combine reduced pressure and lunar gravity. Whether their order is the same as at normal gravity at that pressure bears on the claim for those materials only. No held item measures the three conditions acting together on an order of materials (U5.1).
          assumption 1: The order of the materials of E5a under reduced pressure and lunar gravity says something about other materials.
          assumption 2: Effects that are small one at a time stay small when they act together.
          assumption 3 [added by review pass]: An order of two materials counts as an order of materials in the sense of C5; only a pair is held at the reduced pressure.
          assumption 4 [added by review pass]: Comparing lunar and normal gravity at one fixed reduced pressure stands for the combined change from the ground-test atmosphere to the habitat atmosphere that C5 names.
          assumption 5 [added by review pass]: The high-oxygen part of C5 is addressed by an order of oxygen thresholds that lie below the habitat oxygen; no held value is at the habitat oxygen.
          assumption 6 [added by review pass]: The upper bound of the E5b pressure range stands for the whole range; lower habitat pressures behave the same.
          assumption 7 [added by review pass]: 'psi' in CH.moonbase is absolute total pressure, the same quantity as 'psia' in OF2012.table1.
          assumption 8 [added by review pass]: Thresholds from drop tests and from normal-gravity tests rank materials the same way, although the item states that the criteria differ.
          assumption 9 [added by review pass]: Lunar gravity as obtained in the drop facility, and over a short drop, stands for lasting lunar gravity.
          assumption 10 [added by review pass]: The unstated flow, temperature, thickness and diluent of the drop tests match between materials and match the habitat.
          assumption 11 [added by review pass]: Differences between the two materials' thresholds are larger than the test scatter or resolution, which the item does not state.
          assumption 12 [added by review pass]: A kept order counts as support for 'unchanged', although only a reversal can bear decisively on the pair.
          assumption 13 [added by review pass]: The ground-test ranking of C0 is the normal-gravity order at the same reduced pressure; if the ground ranking was obtained at another atmosphere, the normal-gravity column of E5a is not the ranking to be carried over.
          D5a DEFEATER of assumption 1 [basis: logical]: A comparison of few materials can show that an order changes, but it cannot show that the order is kept for other materials.
          D5b DEFEATER of assumption 2 [basis: documented (WP21X.atmosphere)]: WP21X.atmosphere states that at the planned exploration conditions materials that are non-flammable become flammable. A change of category under the combined conditions bears on the order.
              quote: At these conditions, materials that are non-flammable become flammable, and flammable materials require lower ignition energy and burn faster with greater temperature and heat release rates than in normal atmosphere.
          D5c DEFEATER of assumption 1 [basis: documented (OF2012.table1); added by review pass]: OF2012.table1 prints Nomex HT90-40 at another pressure from the other two materials (values cited below), so the held values that combine reduced pressure and lunar gravity cover a pair of materials, not three. An order of a pair is the thinnest possible base for a statement about other materials.
              item words (verbatim): "Nomex HT90-40 at 14.7 psia"
              cited value OF2012.table1 ["rows", {"material": "Mylar G"}, "pressure_psia"] = 10.2
              cited value OF2012.table1 ["rows", {"material": "Ultem 1000"}, "pressure_psia"] = 10.2
              cited value OF2012.table1 ["rows", {"material": "Nomex HT90-40"}, "pressure_psia"] = 14.7
          D5d DEFEATER of assumption 1 [basis: documented (H2006.range); added by review pass]: H2006.range states that the effect of total pressure on oxygen concentration thresholds is greater for materials with higher thresholds. The pressure part of the combined change is therefore material-dependent, and what holds for the pair in E5a need not hold for materials with other thresholds.
              item words (verbatim): "The effect of total pressure on oxygen concentration flammability thresholds is greater for materials with higher thresholds"
          D5e DEFEATER of assumption 1 [basis: documented (SAE2008.mocpressure); added by review pass]: SAE2008.mocpressure names a few fuels, apparently sharing halogen species, with a stronger dependence on pressure. Materials of another chemistry than the pair in E5a can respond to the reduced pressure differently, so the pair's behaviour does not transfer by chemistry.
              item words (verbatim): "a few fuels, which appear to have halogen species in common, have a stronger dependence on pressure"
          D5f DEFEATER of assumption 1 [basis: logical; added by review pass]: Two materials whose thresholds lie far apart keep their order more easily than two whose thresholds lie close. A kept order of one pair says nothing about pairs that lie closer together, which are the pairs whose order is most at stake.
          D5g DEFEATER of assumption 2 [basis: documented (OF2012.margin); added by review pass]: OF2012.margin reports its most negative margin at lunar gravity for a material at reduced pressure. The gravity effect measured at reduced pressure is the largest in the item, so the premise that each effect is small is not shown for the only combined case held.
              item words (verbatim): "were negative by as much as -5.75 (lunar gravity, Mylar G at 10.2 psia)"
          D5h DEFEATER of assumption 2 [basis: documented (ICES19.fanoff); added by review pass]: ICES19.fanoff reports that earlier quiescent tests at elevated oxygen suggest ventilation may not be needed for a flame to survive in high-oxygen low-pressure atmospheres or in partial gravity. The role of flow then changes under these conditions, a change that tests of one condition at a time would not show.
              item words (verbatim): "ventilation may not be necessary for a flame to survive in high-oxygen low-pressure atmospheres or in partial gravity"
          D5i DEFEATER of assumption 2 [basis: documented (URBAN14.loc); added by review pass]: URBAN14.loc attributes a strong pressure dependence to kinetic or flow effects. If pressure acts through the flow that gravity also sets, the two changes act on the same path and need not add as separate small effects.
              item words (verbatim): "The strong dependence on pressure suggests either kinetic effects or flow effects."
          D5j DEFEATER of assumption 2 [basis: documented (THOMSEN18.care); added by review pass]: THOMSEN18.care states that low pressure will eventually affect the chemical kinetics. A mechanism that only appears at low pressure is not captured by a pressure effect measured near ambient and added to a gravity effect.
              item words (verbatim): "eventually low pressure will affect the chemical kinetics of the process"
          D5k DEFEATER of assumption 2 [basis: documented (URBAN14.normoxic); added by review pass]: URBAN14.normoxic states that at constant oxygen partial pressure a fire resistant material can become flammable depending on the ambient pressure. A change of category is a step, not a small shift, and it can follow from the pressure part of the combination alone.
              item words (verbatim): "it is possible that a fire resistant material can become flammable depending on the ambient pressure"
          D5l DEFEATER of assumption 2 [basis: logical; added by review pass]: The assumption presupposes that the pressure effect and the gravity effect are each small, but the argument establishes neither: C3 and C4 carry their own open defeaters. The assumption rests on a premise the argument does not hold.
          D5m DEFEATER of assumption 2 [basis: logical; added by review pass]: Near a threshold, two shifts that are each small can together carry one material across the boundary while another stays on its side, so an order can flip under the combination although neither change flips it alone.
          D5n DEFEATER of the inference [basis: documented (OF2012.table1); added by review pass]: OF2012.table1 states that the low-gravity limits use criteria (self-extinguished during the drop; survived the full drop) that are not the same as in normal gravity. Asking whether the lunar-gravity order equals the normal-gravity order compares orders of two different quantities.
              item words (verbatim): "MOC* is the maximum oxygen concentration at which the flame self-extinguished during the drop, ULOI* the minimum at which it survived the full drop; these criteria are not the same as in 1g."
          D5o DEFEATER of the inference [basis: documented (EAWG.atmospheres); added by review pass]: EAWG.atmospheres recommends surface-habitat atmospheres at lower total pressures than the pressure of the pair in E5a. E5b gives that pressure only as an upper bound, so E5a covers at most the upper end of the habitat range and says nothing about the lower pressures named for surface habitats.
              item words (verbatim): "8.0 psia / 32% O2 (landers, surface habitats); 7.6 psia / 32% O2 (surface habitats)"
          D5p DEFEATER of the inference [basis: documented (TM217036.threshold); added by review pass]: TM217036.threshold states that the oxygen threshold in reduced gravity is a function of the local convective velocity. E5a states no flow, so the lunar-gravity order it gives is not tied to any flow and cannot be compared at a habitat flow.
              item words (verbatim): "is a function of the local convective velocity"
          D5q DEFEATER of the inference [basis: documented (G125.conditions); added by review pass]: G125.conditions states that fire-limit results do not necessarily apply to conditions that do not faithfully reproduce the test. A short drop-tower test at a single pressure does not reproduce a habitat at high oxygen in lasting lunar gravity.
              item words (verbatim): "its results do not necessarily apply to any condition that does not faithfully reproduce the conditions during test"
          D5r DEFEATER of the inference [basis: documented (TB008.gaps); added by review pass]: TB008.gaps names material flammability in partial gravity as a major open gap. The inference leans on drop-tower lunar values for the combined case while the held technical brief calls that area a major gap.
              item words (verbatim): "Material flammability in partial gravity remains a major gap for exploration missions."
          D5s DEFEATER of the inference [basis: documented (EAWG.needs.flammability); added by review pass]: EAWG.needs.flammability lists diluent gas beside pressure, gravity and oxygen as a variable of material flammability. Neither C5 nor E5a states the diluent, so a habitat diluent other than that of the drop tests is not examined.
              item words (verbatim): "Effects of pressure, gravity, oxygen mole fraction, and diluent gas on material flammability."
          D5t DEFEATER of the inference [basis: logical; added by review pass]: E5a sets lunar and normal gravity side by side at the same reduced pressure. It therefore tests the change of gravity at a fixed reduced pressure, not the combined change from the ground-test atmosphere to the habitat atmosphere that C5 names, and the change to high oxygen does not enter it at all.
          D5u DEFEATER of the inference [basis: logical; added by review pass]: E5a gives thresholds, not behaviour at the habitat oxygen. If every threshold of the pair lies below the habitat oxygen, both materials burn there, and an order of thresholds need not be the order of how they burn at that oxygen.
          D5v DEFEATER of the inference [basis: logical; added by review pass]: The item gives no scatter or test resolution for its values. A difference between two thresholds that is within the resolution of the test cannot fix an order, whether kept or reversed.
          D5w DEFEATER of the inference [basis: logical; added by review pass]: A flame that survives a short drop may still go out later, and one that is dying may not have finished within the drop. An order from short drops need not be the order in lasting lunar gravity.
          D5x DEFEATER of the inference [basis: logical; added by review pass]: CH.moonbase gives its pressure in psi without saying absolute or total, while E5a prints psia. The match of the two pressures that the inference states is read into the items, not stated by them.
        E5a EVIDENCE
            item: OF2012.table1 (published_result), NTRS-20130010991; access: full_text_read
              text (team wording in references.json): Limiting oxygen molar concentrations (% O2) from Table I. Mylar G at 10.2 psia: 1g ULOI 21.2 and MOC 20.0; Martian ULOI* 18.0 and MOC* 17.0; Lunar ULOI* 15.6 and MOC* 14.1; 0g ULOI* 17.0 and MOC* 16.0; oxygen margin of safety (delta O2 %) -3.1 Martian, -5.75 Lunar, -4.1 0g. Ultem 1000 at 10.2 psia: 1g ULOI 23.5 and MOC 23.0; Martian ULOI* 22.0 and MOC* 21.1; Lunar ULOI* 21.0 and MOC* 19.9; 0g ULOI* 24.0 and MOC* 23.0; delta O2 % -1.7 Martian, -2.8 Lunar, 0.25 0g. Nomex HT90-40 at 14.7 psia: 1g ULOI 23.5 and MOC 22.1; Martian ULOI* 19.9 and MOC* 19.0; Lunar ULOI* 21.0 and MOC* 19.9; 0g ULOI* 23.0 and MOC* 22.0; delta O2 % -3.35 Martian, -2.35 Lunar, -0.3 0g. Delta O2 % is the mean of the low-gravity ULOI* and MOC* minus the mean of the 1g ULOI and MOC (Eq. 1). The low-gravity limits come from 5.18 s drop tower tests: MOC* is the maximum oxygen concentration at which the flame self-extinguished during the drop, ULOI* the minimum at which it survived the full drop; these criteria are not the same as in 1g.
              quote (as printed): "Table I: Limiting Oxygen Molar Concentrations and Oxygen Margin of Safety for Different Gravity Levels"
              where: Table I, p. 6
              url: https://ntrs.nasa.gov/citations/20130010991
            covers (only what the item states):
              facility: "5.18 s drop tower tests"
              flow: not stated in the item
              gravity: "1g"; "Martian"; "Lunar"; "0g"
              materials: "Mylar G"; "Ultem 1000"; "Nomex HT90-40"
              oxygen: not stated in the item
              pressure: "Mylar G at 10.2 psia"; "Ultem 1000 at 10.2 psia"; "Nomex HT90-40 at 14.7 psia"
        E5b EVIDENCE
            item: CH.moonbase (design_value), CHALLENGE-2026; access: read_by_teammate
              text (team wording in references.json): Moon Base and pressurized-rover atmosphere expected between spacesuit and Earth conditions: oxygen likely 30% or more, pressure 10.2 psi or less.
              where: Potential considerations: Spacesuits and oxygen concentration
              url: https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/
            covers (only what the item states):
              facility: not stated in the item
              flow: not stated in the item
              gravity: not stated in the item
              materials: not stated in the item
              oxygen: "oxygen likely 30% or more"
              pressure: "pressure 10.2 psi or less"
        U5.1 UNDEVELOPED: The effect of high oxygen, low total pressure and lunar gravity acting together on the order of materials has been measured.
            evidence: no item held
            study asked for by CP2004.flam.q6 (NASA-CP-2004-213205-VOL1): "How do the flammability and ignitability of materials change in high-O2 mole fraction, low-pressure, reduced gravity environments?"
            study asked for by WP21X.research (WP-2021-FIRE-EXTINGUISHER): "calls for research into fire and fire extinguisher use in the appropriate environments. These include elevated oxygen at reduced pressure and partial gravity environments."
            study asked for by EAWG.needs.flammability (NASA-TP-2010-216134): "Effects of pressure, gravity, oxygen mole fraction, and diluent gas on material flammability."
            study asked for by EAWG.testing (NASA-TP-2010-216134): "These recommendations will also require materials ignition and flammability testing and certification to 34% oxygen concentration."
```

## Method

- Safety Case Notations: Alternatives for the Non-Graphically Inclined?. C. M. Holloway (NASA Langley Research Center), 2008. https://ntrs.nasa.gov/citations/20080042416. Terms as found: NTRS record: distribution PUBLIC; copyright determination GOV_PUBLIC_USE_PERMITTED. Taken: The element types of the Goal Structuring Notation as the paper lists them: goal (a claim to be established by an argument), strategy (how a goal is decomposed into sub-goals), solution (the evidence that a goal has been met), context, assumption, justification. Only the form is taken.
- Assurance Arguments for the Non-graphically-inclined: Two Approaches (NASA/TM-2017-219650). E. Heavner, C. M. Holloway (NASA Langley Research Center), 2017. https://ntrs.nasa.gov/citations/20170007188. Terms as found: NTRS record: distribution PUBLIC; copyright determination PUBLIC_USE_PERMITTED. Taken: The five elements of an argument as the memorandum defines them: conclusions, premises (some called evidence), warrants (why the truth of the premises should lead the reader to hold the conclusion true), contextual information, and assumptions (statements relied on but not elaborated or shown to be true). The 'inference' node here plays the role of the warrant or strategy. Only the form is taken.
- Making the Implicit Explicit: Towards an Assurance Case for DO-178C. C. M. Holloway (NASA Langley Research Center), 2013. https://ntrs.nasa.gov/citations/20140002745. Terms as found: NTRS record: copyright determination GOV_PUBLIC_USE_PERMITTED; conference paper, International System Safety Society, publication date 2013-08-12. Taken: The undeveloped entity of GSN: a mark on a goal or strategy indicating that the line of argument requires further development. Only the form is taken.
- The 'defeater' node kind (a way an inference or an assumption could fail) is not defined in the three sources above. Public sources on defeaters in assurance arguments (Software Engineering Institute reports on eliminative argumentation; an SRI report on defeaters) could not be opened from this session, so the kind is described here in the team's own words and is not attributed to any source.
- All three were downloaded from NTRS and read (text layer) on 2026-11-14; titles, years (NTRS publication date) and terms are as shown in their NTRS records.

