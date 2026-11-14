INFERENCE MAP: LUNAR HABITAT

AI-generated (Claude Code) on 2026-11-14, branch data-lab. Not reviewed by a person or a combustion specialist.
A map of what the held documents say must be known and of what the held items and PSI tests show.
Not a criterion, not a research plan of the team. The state of a link is the team's reading of the items.
NASA and investigators' documents cited: dated 2003 to 2024 (28 documents in all, 3 with no year in
references.json; the challenge page CHALLENGE-2026 is counted but not dated in this range).
They do not say what NASA considers open today.

Question: What would have to be established before a material-flammability criterion could be set for a lunar habitat (oxygen 30% or more, pressure 10.2 psi or less, lunar gravity)?
Environment used by the rule: oxygen 30% or more, pressure 70.327 kPa (10.2 psia) or less, gravity lunar.
  bounds from CH.moonbase; gravity from pipeline/spec/scenarios.json lunar_habitat gravity_level.
State: established = one result item or counted PSI test states every required condition of the link;
       partly = items or tests held, at other conditions or stating fewer of them; missing = none held.
       (L1 is a specification link: established only by an item of type requirement.)

PART 1. A PATH ALREADY WALKED: Is the normal-gravity screening test conservative in microgravity?
  The steps are in the order of the procedure, not in the order of the years; a proposal fed back to the criterion (CP2003.prev.margin) is older than the results.

  1. existing criterion
     "The purpose of this test is to determine if a material, when exposed to a standard ignition source, will self-extinguish and not transfer burning debris, which can ignite adjacent materials."
       [6001B.T1.purpose, NASA-STD-6001B, 2011]
     "Test 1 shall evaluate the candidate material in the worst-case atmosphere to which the material could be exposed."
       [6001B.T1.focr59, NASA-STD-6001B, 2011]
     "A material is self-extinguishing if no specimen burns more than 15 cm and no specimen propagates a flame by transfer of burning debris."
       [6001B.T1.pass, NASA-STD-6001B, 2011; team wording of the document, not a verbatim quote]

  2. doubt stated
     "More understanding on relationship between 1-g test methods to microgravity performance."
       [CP2003.prev.1g, NASA-CP-2003-212103, 2003]
     "Is the NASA STD 6001, Test 1 configuration conservative or non-conservative in assessing material flammability in reduced gravity"
       [CP2004.flam.q1, NASA-CP-2004-213205-VOL1, 2004]

  3. hypothesis
     "BASS–II tests the hypothesis that materials in microgravity, with adequate ventilation, burn as well if not better than the same material in normal gravity with other conditions being identical (pressure, O2 concentration, temperature, etc.)."
       [PSI-25 hypothesis, 2022 (PSI record release date 31-Dec-2022)]
     "However, it may not be conservative for flammability in space."
       [PSI-25 hypothesis, 2022 (PSI record release date 31-Dec-2022)]

  4. test designed to discriminate
     "One objective of the BASS–II tests is to identify what is the worst case for material flammability in spacecraft environments, and how does that compare to the terrestrial upward burning used to screen the materials for safe use aboard spacecraft."
       [BASS2TM.objective, NASA-TM-20210011385, 2021]
     "Many of the tests focused on finding a minimum oxygen concentration or flow velocity where a material will burn in space, to compare with the Earth-based limits."
       [ICES19.minimum, ICES-2019-BASS2, 2019]

  5. result
     "BASS-II PMMA: minimum oxygen concentration in the flammability boundary from the concurrent (stagnation-flow) rod tests 13.6% O2; minimum flammable value for the opposed-flow rods 16.3% O2 (no comparable boundary was obtained for opposed flow); normal-gravity PMMA extinction limits 17% O2 (downward spread) and 15.4% O2 (upward spread)."
       [ICES19.limits, ICES-2019-BASS2, 2019; team wording of the document, not a verbatim quote]
     "Test 1 is not conservative: materials can burn at lower oxygen levels in microgravity than on Earth."
       [RG.test1, NP-2015-10-034-JSC, 2015; team wording of the document, not a verbatim quote]
     "Oxygen margins of safety (low-gravity limit minus 1g limit, % O2 by mole) were negative by as much as -5.75 (lunar gravity, Mylar G at 10.2 psia); the largest at Martian gravity was -3.35 (Nomex HT90-40) and at 0g -4.1 (Mylar G). Normal-gravity screening tests may not be conservative. The low-g limits come from 5 s drop tests and their extinction criteria are not the same as in 1g."
       [OF2012.margin, NTRS-20130010991, 2012; team wording of the document, not a verbatim quote]

  6. scale-up designed
     "The specific objectives of these three experiments are to (1) determine how rapidly a large scale fire grows in low-gravity and (2) investigate the low-g flammability limits compared to those obtained in NASA’s normal gravity material flammability screening test."
       [SAF16.objectives, ICES-2016-SAFFIRE, 2016]
     "The objective of the tests to be conducted on Saffire-II is to investigate the low-gravity Maximum Oxygen Concentration (MOC) flammability limits in long-term low gravity."
       [SAF16.saffire2, ICES-2016-SAFFIRE, 2016]
     "Quantifying the difference in flammability limits for large samples is the objective of the Saffire-II experiments."
       [SAF16b.saffire2, IAASS-2016-SAFFIRE, 2016]

  7. scale-up result
     no item held (searched for: an item that states a low-gravity flammability limit measured on Saffire-II)

  8. fed back to the criterion
     "A modified Test 1 measures the actual upward flammability limit (akin to the Limiting Oxygen Index) so that the margin of safety in the use environment can be assessed."
       [TB14639.modified, TASKBOOK-14639, 2022; team wording of the document, not a verbatim quote]
     "Augment existing go/no go criteria with a quantitative test method which provides ranking or indication of flammability margin, e.g. LOI or radiation panel."
       [CP2003.prev.margin, NASA-CP-2003-212103, 2003]

  9. criterion revised
     no item held (searched for: an item that states a change of NASA-STD-6001 Test 1 made on the basis of the low-gravity results)

  10. still open
     "Material flammability in partial gravity remains a major gap for exploration missions."
       [TB008.gaps, OCHMO-TB-008, year not stated in references.json]
     "Normal-gravity flammability tests do not correlate with flammability in ventilated, micro- or reduced-gravity conditions."
       [TB14639.gap, TASKBOOK-14639, 2022; team wording of the document, not a verbatim quote]

PART 2. THE MAP (one line per link)
  ROOT  material flammability assessed for the habitat
      L1    [partly] the atmosphere the material is evaluated in
      L2    [established] whether the normal-gravity screening test is conservative at reduced gravity
          L2.1  [partly] the flow speed and direction at which to compare
      L3    [partly] flammability in a high-oxygen, low-pressure, reduced-gravity atmosphere
          L3.1  [partly] the limiting oxygen and flow in partial gravity
          L3.2  [partly] the effect of total pressure at the habitat oxygen
          L3.3  [partly] ignition at high oxygen
      L4    [partly] flame growth and spread in real situations
      L5    [missing] non-flaming and smoldering combustion

PART 3. THE QUOTES BEHIND EACH LINK

ROOT  material flammability assessed for the habitat
  claim:
    "Material flammability must be assessed in relevant cabin atmospheres and gravity levels for exploration transit vehicles and habitats."
      [TB008.assess, OCHMO-TB-008, year not stated in references.json]
  why it is a precondition of a criterion:
    "Test 1 shall evaluate the candidate material in the worst-case atmosphere to which the material could be exposed."
      [6001B.T1.focr59, NASA-STD-6001B, 2011]
    "The worst-case anticipated use environment (most hazardous pressure, temperature, material thickness, and fluid exposure conditions) shall be used in the evaluation of material suitability."
      [6001B.focr12, NASA-STD-6001B, 2011]
  verification:
    "It is pass-fail and is only valid at the atmosphere tested."
      [ICES14.onlyvalid, ICES-2014-179, 2014]

L1 [partly] the atmosphere the material is evaluated in   (parent ROOT; required conditions: o2, pressure)
  claim:
    "Design requirements need to specify pressure and % O2 combinations permitted in the habitable volume"
      [TB008.o2, OCHMO-TB-008, year not stated in references.json]
  why it is a precondition of a criterion:
    "Test 1 shall evaluate the candidate material in the worst-case atmosphere to which the material could be exposed."
      [6001B.T1.focr59, NASA-STD-6001B, 2011]
    "The test atmosphere shall consist of a mixture of GOX and GN2, with the oxygen level being the highest that the material could witness in use conditions."
      [6001B.T1.o2level, NASA-STD-6001B, 2011]
  established:
    none
  partly:
    TB14639.worstcase [criterion; O2 30%, 70.327 kPa]: inside on o2, pressure
    OF2012.test1env [criterion; O2 30%, 70.327 kPa]: inside on o2, pressure
    EAWG.atmospheres [design_value; no condition stated]: inside on none
    EA.8.2-34 [design_value; no condition stated]: inside on none
  missing:
    o2+pressure: an item states every required condition, but none is of the kind the rule counts (a requirement)
  what would close it (as the documents state it):
    "These recommendations will also require materials ignition and flammability testing and certification to 34% oxygen concentration."
      [EAWG.testing, NASA-TP-2010-216134, 2010]
  verification (what the documents say limits or supports such a result):
    "Failure of any one specimen constitutes failure of the material in that test environment."
      [6001B.T1.failenv, NASA-STD-6001B, 2011]

L2 [established] whether the normal-gravity screening test is conservative at reduced gravity   (parent ROOT; required conditions: pressure, gravity)
  claim:
    "Is the NASA STD 6001, Test 1 configuration conservative or non-conservative in assessing material flammability in reduced gravity"
      [CP2004.flam.q1, NASA-CP-2004-213205-VOL1, 2004]
  why it is a precondition of a criterion:
    "Normal-gravity flammability tests do not correlate with flammability in ventilated, micro- or reduced-gravity conditions."
      [TB14639.gap, TASKBOOK-14639, 2022; team wording of the document, not a verbatim quote]
  established:
    OF2012.table1 (Mylar G) [result; 70.327 kPa, gravity normal/martian/lunar/microgravity]: inside on pressure, gravity
    OF2012.table1 (Ultem 1000) [result; 70.327 kPa, gravity normal/martian/lunar/microgravity]: inside on pressure, gravity
  partly:
    OF2012.table1 (Nomex HT90-40) [result; 101.353 kPa, gravity normal/martian/lunar/microgravity]: inside on gravity
    OF2012.margin [result; gravity lunar/martian/microgravity/normal]: inside on gravity
    RG.test1 [result; gravity microgravity]: inside on none
    ICES19.limits [result; no condition stated]: inside on none
    SAE2008.uloi [result; gravity normal/microgravity]: inside on none
    SAE2008.table1 [result; gravity normal/microgravity]: inside on none
    PSI P1 (Flammability limit): 133 counted tests (PSI-25, PSI-99); inside by condition: pressure 0, gravity 0; on all: 0
  missing:
    PSI P1 gap code: pressure:not_recorded
    PSI P1 gap code: gravity:no_usable_test_at_lunar
  what would close it (as the documents state it):
    "A modified Test 1 measures the actual upward flammability limit (akin to the Limiting Oxygen Index) so that the margin of safety in the use environment can be assessed."
      [TB14639.modified, TASKBOOK-14639, 2022; team wording of the document, not a verbatim quote]
    "Augment existing go/no go criteria with a quantitative test method which provides ranking or indication of flammability margin, e.g. LOI or radiation panel."
      [CP2003.prev.margin, NASA-CP-2003-212103, 2003]
  verification (what the documents say limits or supports such a result):
    "Oxygen margins of safety (low-gravity limit minus 1g limit, % O2 by mole) were negative by as much as -5.75 (lunar gravity, Mylar G at 10.2 psia); the largest at Martian gravity was -3.35 (Nomex HT90-40) and at 0g -4.1 (Mylar G). Normal-gravity screening tests may not be conservative. The low-g limits come from 5 s drop tests and their extinction criteria are not the same as in 1g."
      [OF2012.margin, NTRS-20130010991, 2012; team wording of the document, not a verbatim quote]

L2.1 [partly] the flow speed and direction at which to compare   (parent L2; required conditions: gravity, flow)
  claim:
    "The question of conservatism of Test 1 therefore may rest on the determination of velocity and flow direction at which to compare."
      [CP2004.flam.velocity, NASA-CP-2004-213205-VOL1, 2004]
  why it is a precondition of a criterion:
    "The goal is to obtain the microgravity flammability map for select materials to provide information on the sensitivity of the material’s flammability to ventilation flow, ambient oxygen concentration and possibly pressure, to find the fundamental limiting oxygen concentration in microgravity."
      [RG.map, NP-2015-10-034-JSC, 2015]
  established:
    none
  partly:
    ICES19.limits [result; no condition stated]: inside on none
    SAE2008.table1 [result; gravity normal/microgravity]: inside on none
    SAF.result [result; flow 20 cm/s]: inside on flow
    ICES19.fanoff [result; no condition stated]: inside on none
    PSI P1 (Flammability limit): 133 counted tests (PSI-25, PSI-99); inside by condition: gravity 0, flow 123; on all: 0
  missing:
    gravity: no evidence item or counted PSI test of this link is inside on this condition
    PSI P1 gap code: gravity:no_usable_test_at_lunar
  what would close it (as the documents state it):
    "There is a need for additional microgravity data on the effects of oxygen and flow on ignition, combustion and flame propagation for real engineering materials."
      [CP2003.prev.o2flow, NASA-CP-2003-212103, 2003]
  verification (what the documents say limits or supports such a result):
    no item held

L3 [partly] flammability in a high-oxygen, low-pressure, reduced-gravity atmosphere   (parent ROOT; required conditions: o2, pressure, gravity)
  claim:
    "How do the flammability and ignitability of materials change in high-O2 mole fraction, low-pressure, reduced gravity environments?"
      [CP2004.flam.q6, NASA-CP-2004-213205-VOL1, 2004]
  why it is a precondition of a criterion:
    "Partial gravity levels affect the whole chain of the fire safety strategy, with expected consequences on flammability, flame spread rate, smoke production, detection, mitigation, and clean-up."
      [TB008.partialg, OCHMO-TB-008, year not stated in references.json]
  established:
    none
  partly:
    OF2012.table1 (Mylar G) [result; 70.327 kPa, gravity normal/martian/lunar/microgravity]: inside on pressure, gravity
    OF2012.table1 (Ultem 1000) [result; 70.327 kPa, gravity normal/martian/lunar/microgravity]: inside on pressure, gravity
    OF2012.table1 (Nomex HT90-40) [result; 101.353 kPa, gravity normal/martian/lunar/microgravity]: inside on gravity
    H2011.cannot (MOC at 10.2 psia) [result; 70.327 kPa]: inside on pressure
    H2011.cannot (fails at 25.9% oxygen and 14.7 psia) [result; O2 25.9%, 101.353 kPa]: inside on none
    SAE2008.table1 [result; gravity normal/microgravity]: inside on none
    ICES19.fanoff [result; no condition stated]: inside on none
    PSI P1 (Flammability limit): 133 counted tests (PSI-25, PSI-99); inside by condition: o2 0, pressure 0, gravity 0; on all: 0
    PSI P2 (Ignition): 0 counted tests (none); inside by condition: o2 0, pressure 0, gravity 0; on all: 0
  missing:
    o2: no evidence item or counted PSI test of this link is inside on this condition
    PSI P1 gap code: oxygen:no_usable_test_in_range
    PSI P1 gap code: pressure:not_recorded
    PSI P1 gap code: gravity:no_usable_test_at_lunar
    PSI P2 gap code: need:no_usable_test
    stated open:
      "Material flammability in partial gravity remains a major gap for exploration missions."
        [TB008.gaps, OCHMO-TB-008, year not stated in references.json]
    stated open:
      "PSI holds no partial-gravity combustion data yet; the page names LUCI as a future source."
        [CH.partial_gravity, CHALLENGE-2026, 2026; team wording of the document, not a verbatim quote; access: read_by_teammate]
  what would close it (as the documents state it):
    "These recommendations will also require materials ignition and flammability testing and certification to 34% oxygen concentration."
      [EAWG.testing, NASA-TP-2010-216134, 2010]
    "calls for research into fire and fire extinguisher use in the appropriate environments. These include elevated oxygen at reduced pressure and partial gravity environments."
      [WP21X.research, WP-2021-FIRE-EXTINGUISHER, 2021]
  verification (what the documents say limits or supports such a result):
    "The knowledge afforded by this technique allows extrapolations of flammability behaviour to conditions not specifically tested and this could potentially result in significant cost and time savings.[6]"
      [ISO16697.extrapolation, ISO-TS-16697, 2012; access: abstract_only]

L3.1 [partly] the limiting oxygen and flow in partial gravity   (parent L3; required conditions: pressure, gravity, flow)
  claim:
    "Determine limiting O2 and flow for flame propagation on practical materials in µg and partial-g"
      [CP2003.roadmap.limit, NASA-CP-2003-212103, 2003]
  why it is a precondition of a criterion:
    "This Technical Specification provides a method to determine the oxygen concentration threshold when a material exposed to a standard ignition source self-extinguishes at a given constant total pressure, temperature, convective flow, and gravity-level conditions."
      [ISO16697.scope, ISO-TS-16697, 2012; access: abstract_only]
  established:
    none
  partly:
    OF2012.table1 (Mylar G) [result; 70.327 kPa, gravity normal/martian/lunar/microgravity]: inside on pressure, gravity
    OF2012.table1 (Ultem 1000) [result; 70.327 kPa, gravity normal/martian/lunar/microgravity]: inside on pressure, gravity
    OF2012.table1 (Nomex HT90-40) [result; 101.353 kPa, gravity normal/martian/lunar/microgravity]: inside on gravity
    ICES19.limits [result; no condition stated]: inside on none
    SAE2008.table1 [result; gravity normal/microgravity]: inside on none
    PSI P1 (Flammability limit): 133 counted tests (PSI-25, PSI-99); inside by condition: pressure 0, gravity 0, flow 123; on all: 0
  missing:
    pressure+gravity+flow: each condition is met by some item or test, but no single one is inside on all of them
    PSI P1 gap code: pressure:not_recorded
    PSI P1 gap code: gravity:no_usable_test_at_lunar
    stated open:
      "PSI holds no partial-gravity combustion data yet; the page names LUCI as a future source."
        [CH.partial_gravity, CHALLENGE-2026, 2026; team wording of the document, not a verbatim quote; access: read_by_teammate]
  what would close it (as the documents state it):
    "PSI holds no partial-gravity combustion data yet; the page names LUCI as a future source."
      [CH.partial_gravity, CHALLENGE-2026, 2026; team wording of the document, not a verbatim quote; access: read_by_teammate]
    "However, the oxygen threshold has been shown to be lower in reduced-gravity and is a function of the local convective velocity. Therefore, the objective of this task was to determine the oxygen flammability threshold in reduced-gravity for materials identified by NASA Materials and Processes personnel and quantify the difference from thresholds determined in normal gravity."
      [TM217036.threshold, NASA-TM-2011-217036, 2011]
  verification (what the documents say limits or supports such a result):
    "Thus, care should be taken interpreting and applying these results, particularly because eventually low pressure will affect the chemical kinetics of the process."
      [THOMSEN18.care, PROCI-2018-THOMSEN, 2018]

L3.2 [partly] the effect of total pressure at the habitat oxygen   (parent L3; required conditions: o2, pressure)
  claim:
    "Effects of pressure, gravity, oxygen mole fraction, and diluent gas on material flammability."
      [EAWG.needs.flammability, NASA-TP-2010-216134, 2010]
  why it is a precondition of a criterion:
    "Material flammability, on the other hand, is a function of both pressure and oxygen."
      [ICES14.both, ICES-2014-179, 2014]
    "Worst-case anticipated use environment: Most hazardous pressure, temperature, material thickness, and/or fluid exposure conditions."
      [6001B.def.worstcase, NASA-STD-6001B, 2011]
  established:
    none
  partly:
    H2006.depends [result; no condition stated]: inside on none
    H2006.table2 (48.2 kPa) [result; 48.2 kPa, gravity normal]: inside on pressure
    H2006.table2 (85.3 kPa) [result; 85.3 kPa, gravity normal]: inside on none
    H2006.table2 (101.3 kPa) [result; 101.3 kPa, gravity normal]: inside on none
    H2007.fixedpressure [result; 70.1 kPa]: inside on pressure
    H2011.cannot (MOC at 10.2 psia) [result; 70.327 kPa]: inside on pressure
    H2011.cannot (fails at 25.9% oxygen and 14.7 psia) [result; O2 25.9%, 101.353 kPa]: inside on none
    H2011.linear [result; no condition stated]: inside on none
    ICES14.both [result; no condition stated]: inside on none
    ICES14.trend [result; no condition stated]: inside on none
    OF2012.normoxic [result; no condition stated]: inside on none
    LANGE.lesser [result; no condition stated]: inside on none
    URBAN14.loc [result; no condition stated]: inside on none
    URBAN14.normoxic [result; no condition stated]: inside on none
    SAE2008.mocpressure [result; gravity normal]: inside on none
    PSI P1 (Flammability limit): 133 counted tests (PSI-25, PSI-99); inside by condition: o2 0, pressure 0; on all: 0
  missing:
    o2: no evidence item or counted PSI test of this link is inside on this condition
    PSI P1 gap code: oxygen:no_usable_test_in_range
    PSI P1 gap code: pressure:not_recorded
  what would close it (as the documents state it):
    no item held
  verification (what the documents say limits or supports such a result):
    "To determine if this relationship holds outside the 48.2 to 101.3 kPa (7 to 14.7 psia) range further testing is recommended."
      [H2006.range, JTE-2006-HIRSCH, 2006]

L3.3 [partly] ignition at high oxygen   (parent L3; required conditions: o2, pressure, gravity)
  claim:
    "Develop understanding of ignition mechanisms for high oxygen concentration systems (flow friction and particle impact)."
      [EAWG.needs.ignition, NASA-TP-2010-216134, 2010]
  why it is a precondition of a criterion:
    "Materials used in pressurized cabins of spacecrafts must have high ignition temperatures, slow combustion rates, and low potential for explosion."
      [TB008.materials, OCHMO-TB-008, year not stated in references.json]
  established:
    none
  partly:
    RG.ignite [result; no condition stated]: inside on none
    PSI P2 (Ignition): 0 counted tests (none); inside by condition: o2 0, pressure 0, gravity 0; on all: 0
  missing:
    o2: no evidence item or counted PSI test of this link is inside on this condition
    pressure: no evidence item or counted PSI test of this link is inside on this condition
    gravity: no evidence item or counted PSI test of this link is inside on this condition
    PSI P2 gap code: need:no_usable_test
  what would close it (as the documents state it):
    "Constellation should institute a modified standard NASA flammability test to generate ignition threshold data for key spacecraft materials. This modified test will allow NASA to identify materials at risk from increases in oxygen concentration"
      [EAWG.ignthreshold, NASA-TP-2010-216134, 2010]
  verification (what the documents say limits or supports such a result):
    no item held

L4 [partly] flame growth and spread in real situations   (parent ROOT; required conditions: o2, pressure, gravity)
  claim:
    "How will flames grow and spread in real situations?"
      [CP2004.flam.q5, NASA-CP-2004-213205-VOL1, 2004]
  why it is a precondition of a criterion:
    "The amount and arrangement of flammable materials are controlled to prevent the spread of fire in the vehicle; any potential fire is isolated in defined areas by firebreaks or other techniques (described in JSC 29353) without propagation paths to other areas."
      [6001B.6.1.2.spread, NASA-STD-6001B, 2011]
  established:
    none
  partly:
    SAF456.conditions (IV-1) [result; O2 22%, 100 kPa, flow 20 cm/s]: inside on none
    SAF456.conditions (V-2) [result; O2 26.2%, 70.7 kPa, flow 20 cm/s]: inside on none
    SAF456.conditions (VI-2) [result; O2 31%, 54.1 kPa, flow 20 cm/s]: inside on o2, pressure
    SAF456.conditions (VI-3) [result; O2 30.3%, 54.6 kPa, flow 20 cm/s]: inside on o2, pressure
    SAF456.conditions (VI-4) [result; O2 28.8%, 55.2 kPa, flow 20 cm/s]: inside on pressure
    SAF45.table2 (I-1, II-5, II-6, III-1) [result; O2 21%, 100 kPa]: inside on none
    SAF45.table2 (IV-1) [result; O2 22%, 100 kPa]: inside on none
    SAF45.table2 (V-2) [result; O2 26.2%, 70.7 kPa]: inside on none
    SAF.result [result; flow 20 cm/s]: inside on none
    SAE2008.spread [result; no condition stated]: inside on none
    PSI P3 (Flame spread and growth): 2 counted tests (PSI-98); inside by condition: o2 0, pressure 0, gravity 0; on all: 0
  missing:
    gravity: no evidence item or counted PSI test of this link is inside on this condition
    PSI P3 gap code: oxygen:no_usable_test_in_range
    PSI P3 gap code: pressure:not_recorded
    PSI P3 gap code: gravity:no_usable_test_at_lunar
    stated open:
      "Rate of fire spread anticipated in space platforms under realistic fire scenarios"
        [CP2003.resp.spread, NASA-CP-2003-212103, 2003]
  what would close it (as the documents state it):
    "Determine flammability and flame spread of plastic and composite materials in partial-g for variations in flow and imposed heat flux"
      [CP2003.roadmap.spread, NASA-CP-2003-212103, 2003]
  verification (what the documents say limits or supports such a result):
    "Note the distinction between fire growth, a safety issue, and flame growth, a research and possibly safety issue."
      [CP2003.resp.growth, NASA-CP-2003-212103, 2003]

L5 [missing] non-flaming and smoldering combustion   (parent ROOT; required conditions: o2, pressure, gravity)
  claim:
    "How does the propensity for non-flaming/smoldering combustion of materials change in high-O2 mole fraction, low-pressure, reduced gravity environments?"
      [CP2004.flam.q7, NASA-CP-2004-213205-VOL1, 2004]
  why it is a precondition of a criterion:
    "Non-flaming and smoldering combustion in microgravity is named as a gap; the standard flammability tests do not take smoldering into account."
      [CP2003.prev.smolder, NASA-CP-2003-212103, 2003; team wording of the document, not a verbatim quote]
  established:
    none
  partly:
    none
  missing:
    o2: no evidence item or counted PSI test of this link is inside on this condition
    pressure: no evidence item or counted PSI test of this link is inside on this condition
    gravity: no evidence item or counted PSI test of this link is inside on this condition
    stated open:
      "Need to understand the implications of non-flaming and smoldering combustion in microgravity with respect to ISS engineering materials."
        [CP2003.prev.smolder, NASA-CP-2003-212103, 2003]
  what would close it (as the documents state it):
    no item held
  verification (what the documents say limits or supports such a result):
    no item held

Fields marked "no item held": walked path step 'scale-up result'; walked path step 'criterion revised'; L2.1 verification; L3.2 what_would_close_it; L3.3 verification; L5 what_would_close_it; L5 verification
