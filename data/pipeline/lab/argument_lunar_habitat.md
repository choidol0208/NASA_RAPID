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
- inferences by basis: documented 1, team 7
- assumptions stated: 19
- defeaters by basis: documented 19, logical 5
- inferences with no defeater yet: none
- Counts only. No overall verdict is computed or implied.

## Tree

```
C0 CLAIM: A ranking of materials by flammability obtained in normal-gravity ground tests can be carried over, in the same order, to the lunar-habitat atmosphere and to lunar gravity.
  I0 INFERENCE [basis: team; team reasoning (AI-drafted), not a NASA statement]: The top claim is split by the conditions under which a ranking is obtained. A ranking can be carried over only if the ground test yields an order at all (C1), the target atmosphere is fixed (C2), the order holds across the change of total pressure (C3), the order holds across the change of gravity and of the flow that gravity sets (C4), and the two changes taken together do not alter it (C5). E0a names total pressure, temperature, convective flow and gravity level as the conditions at which an oxygen threshold is determined; E0b states that fire-limit results do not necessarily apply to conditions that do not reproduce the test. Neither item states this split; it is the team's.
      assumption 1: The conditions through which the order could change are the oxygen concentration and total pressure of the atmosphere, the gravity level, and the flow that gravity sets.
      assumption 2: Temperature, material thickness and sample size are held as in the ground test.
      assumption 3: Pressure and gravity can be examined one at a time before their combination is examined.
      assumption 4: An order of oxygen thresholds is what the top claim means by a flammability ranking.
      D0a DEFEATER of assumption 2 [basis: documented (6001B.def.worstcase)]: 6001B.def.worstcase names temperature and material thickness among the most hazardous conditions. This argument develops neither, so the order could change through them.
          quote: Worst-case anticipated use environment: Most hazardous pressure, temperature, material thickness, and/or fluid exposure conditions.
      D0b DEFEATER of assumption 4 [basis: documented (CP2004.flam.fist)]: CP2004.flam.fist names time to ignition, fire spread rate, material properties and critical heat flux for ranking the hazards of materials. An order of oxygen thresholds need not agree with an order by these quantities.
          quote: Develop a flammability test method to rank the hazards of materials used on spacecraft using time to ignition, fire spread rate, material properties, critical heat flux
      D0c DEFEATER of assumption 2 [basis: documented (SAF16b.saffire2)]: SAF16b.saffire2 states that quantifying the difference in flammability limits for large samples is an objective. A ranking from small ground specimens may not carry over to large samples.
          quote: Quantifying the difference in flammability limits for large samples is the objective of the Saffire-II experiments.
      D0d DEFEATER of assumption 1 [basis: logical]: The split treats the named conditions as the only paths by which the order could change. A path not named here, such as the strength of the ignition source or the diluent gas, is not examined.
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
      I1 INFERENCE [basis: documented (CP2003.prev.margin); team reasoning (AI-drafted), not a NASA statement]: Test 1 as written gives a pass or a fail at one atmosphere (E1a, E1b). The same standard defines the maximum oxygen concentration at which specimens pass (E1c), and researchers define an upward limiting oxygen index from the same burn-length criterion and a modified Test 1 that measures it (E1d, E1e). Such a threshold can put materials in order. CP2003.prev.margin states this step: augment the go/no-go criteria with a quantitative test method that provides a ranking or an indication of flammability margin.
          basis item: CP2003.prev.margin (knowledge_gap), NASA-CP-2003-212103; access: full_text_read
          basis   text (team wording in references.json): Recommendation of the prevention working group: add to the go/no-go criteria a quantitative test method that ranks materials or indicates a flammability margin.
          basis   quote (as printed): "Augment existing go/no go criteria with a quantitative test method which provides ranking or indication of flammability margin, e.g. LOI or radiation panel."
          basis   where: Fire Prevention and Material Flammability, Issue 2, item 1, p. 8
          basis   url: https://ntrs.nasa.gov/citations/20030053425
          assumption 1: The maximum oxygen concentration and the upward limiting oxygen index put the same materials in the same order.
          assumption 2: The pressure at which a threshold was measured is recorded with it, so that thresholds measured at the same pressure can be compared.
          D1a DEFEATER of assumption 1 [basis: documented (ISO16697.moc)]: ISO16697.moc defines MOC as the highest oxygen concentration where all samples pass and ULOI as the concentration where about half of the samples fail. The two definitions need not give the same order.
              quote: highest oxygen concentration where all samples tested (at least five) pass the test criteria described in Clause 4
          D1b DEFEATER of the inference [basis: documented (D2863.caveat)]: D2863.caveat states that correlation of the oxygen index with burning characteristics under actual use conditions is not implied.
              text: Correlation with burning characteristics under actual use conditions is not implied.
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
          D2a DEFEATER of the inference [basis: documented (EAWG.atmospheres)]: EAWG.atmospheres calls its atmospheres recommendations, not requirements, and lists more than one pair for surface habitats.
              text: Recommended nominal atmospheres: 14.7 psia / 21% O2; 10.2 psia / 26.5% O2; 8.0 psia / 32% O2 (landers, surface habitats); 7.6 psia / 32% O2 (surface habitats). Control box +/-0.2 psia and +/-2.0% O2. Recommendations, not requirements.
          D2b DEFEATER of the inference [basis: documented (EA.8.2-34)]: EA.8.2-34 states that one recommended exploration atmosphere was altered after a re-evaluation; the target can move.
              text: After re-evaluation in 2012 the 8.0 psia / 32% O2 environment was altered to 8.2 psia / 34% O2.
          D2c DEFEATER of assumption 1 [basis: documented (EAWG.testing)]: EAWG.testing asks for materials ignition and flammability testing and certification to an oxygen concentration above the lower bound that CH.moonbase names.
              quote: These recommendations will also require materials ignition and flammability testing and certification to 34% oxygen concentration.
          D2d DEFEATER of assumption 1 [basis: documented (CH.moonbase)]: CH.moonbase words the Moon-base atmosphere as expected and likely; it is an expectation, not a specification, and the item was read by another session of the team.
              text: Moon Base and pressurized-rover atmosphere expected between spacesuit and Earth conditions: oxygen likely 30% or more, pressure 10.2 psi or less.
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
          D3a DEFEATER of assumption 1 [basis: documented (H2006.range)]: H2006.range states that the effect of total pressure on oxygen concentration thresholds is greater for materials with higher thresholds. An effect that differs between materials can change their order.
              quote: To determine if this relationship holds outside the 48.2 to 101.3 kPa (7 to 14.7 psia) range further testing is recommended.
          D3b DEFEATER of assumption 1 [basis: documented (SAE2008.mocpressure)]: SAE2008.mocpressure names a few fuels, which appear to have halogen species in common, with a stronger dependence on pressure.
              quote: The Test 1 materials flammability data published by WSTF (ref. 7) demonstrate that the 1g MOCs are not generally a strong function of pressure but instead vary primarily with oxygen concentration.
          D3c DEFEATER of assumption 1 [basis: documented (URBAN14.loc)]: URBAN14.loc reports a strong dependence on pressure for one material, against the lesser extent stated in LANGE.lesser.
              quote: The strong dependence on pressure suggests either kinetic effects or flow effects.
          D3d DEFEATER of the inference [basis: documented (H2011.cannot)]: H2011.cannot states that, for at least one material tested, a material that meets its threshold at one atmosphere would fail Test 1 at another atmosphere with less oxygen and a higher total pressure.
              quote: For at least one of the materials tested, the data indicate that a material with an MOC of 30% oxygen at 10.2 psia would fail NASA-STD-(I)-6001B Test 1 at 25.9% oxygen and 14.7 psia.
          D3e DEFEATER of assumption 3 [basis: logical]: No held item measures the pressure dependence of a threshold at lunar gravity; the assumption that it is the same as in normal gravity rests on no document.
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
              D3.1a DEFEATER of the inference [basis: logical]: A pressure absent from the experimental tables may be stated in an investigator's paper or a PSI record; the count reads the tables only.
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
              D4.1a DEFEATER of the inference [basis: logical]: E4.1b counts only the tests matched to the package's oxygen or pressure; a lunar-gravity test outside those ranges would not appear in it.
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
          D5a DEFEATER of assumption 1 [basis: logical]: A comparison of few materials can show that an order changes, but it cannot show that the order is kept for other materials.
          D5b DEFEATER of assumption 2 [basis: documented (WP21X.atmosphere)]: WP21X.atmosphere states that at the planned exploration conditions materials that are non-flammable become flammable. A change of category under the combined conditions bears on the order.
              quote: At these conditions, materials that are non-flammable become flammable, and flammable materials require lower ignition energy and burn faster with greater temperature and heat release rates than in normal atmosphere.
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

