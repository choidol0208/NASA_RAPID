# Submission form fields, ready to paste

*AI-generated (Claude Code, pm role) on 15 November 2026 at about 17:45 KST for Team RAPID, NASA Space Apps Challenge 2026. Built from the repository files named below; every address in sections 7 and 8 was copied from a repository file by code, except the last pair of each list, which is the repository address plus the tracked path compliance/SOURCES.md. Paste the text inside each block as it stands.*

The form (saved copy "NASA Space Apps Challenge.html") has these fields, in this order: Project Name; Summary (required, counter 0/1500); Project Demonstration (required, one URL); Project (required, one URL); Project Details (required, rich text); Use of Super Intelligence (SI) (required, multi-select); NASA Data (required, pairs of Link Text and Link Url); Space Agency Partner & Other Data (pairs); two confirmation boxes; Lock, Save Progress, Submit for Judging.

Measured values of the assistant come from `data/insights/assistant_eval.json` (written 15 November 2026, 18:28 KST: the full pipeline and the one-call baseline on all 74 questions, two ablation arms on a fixed half of 38, the third not run for time).

## 1. Project Name

Proposal:

```
Fire Evidence Explorer
```

Alternative:

```
Where the Fire Evidence Stops
```

The proposal is the name on the page, the README and the deck. Neither carries a NASA name.

## 2. Summary

```
Fire Evidence Explorer is a public web dashboard over the 24 combustion investigations in NASA's Physical Sciences Informatics (PSI) archive. You describe what you are building and where, for example cotton fabric in a lunar habitat, and it answers in the challenge's three steps. Find: a rule-based ranking orders the investigations by how closely their tests match your environment and material, and says why. Compare: 1,824 tests from 14 NASA tables share one table, each value linked to its NASA row, and the page counts which tests bear on six fire-safety questions. Interpret: it quotes what NASA's documents report, then says for each question whether the values are in NASA's tables, only in the raw archive (60,866 files), or have no record in PSI. That shows where the evidence stops: for a lunar habitat there is no counted test at 30% oxygen or more and at or below 70.3 kPa. A local open-weight language model (gpt-oss:20b) wrote the summary sentences on the cards and, in the local install, answers questions; every sentence cites its sources and is checked by code. Designers and researchers see what to read first and which data are still missing.
```

Counts (by code): 1124 characters with spaces (limit 1,500); 186 words (asked: 50 to 200).

## 3. Project Demonstration

```
https://github.com/choidol0208/NASA_RAPID/blob/main/docs/submission/slides.pdf
```

What it is: the team's seven-slide deck (PDF, 7 pages, English) on GitHub; it opened without a login when checked at 17:19 KST. It is the deck file in the repository (`docs/submission/slides.pdf`), so a rebuilt deck must be committed and pushed before it shows here.

## 4. Project

```
https://choidol0208.github.io/NASA_RAPID/
```

The public page (GitHub Pages). The repository link, https://github.com/choidol0208/NASA_RAPID , stands in Project Details, with the method page and the challenge-fit document.

## 5. Project Details

Paste into the rich-text box. Each sub-heading is a short line of its own; make it bold in the editor if you like.

```
What it does and how it works

Fire Evidence Explorer is a public web page over the 24 combustion investigations in NASA's Physical Sciences Informatics (PSI) archive. You type what you build and where; it answers in three steps.

Find: code reads the query into conditions (oxygen, pressure, flow, fuel, sample shape, purpose) and compares them with 41 test configurations. Weighted similarities give a match score from 0 to 100. No language model produces or changes a score.

Compare: a pipeline reads 14 NASA tables into one table of 1,824 tests, each value linked to its NASA file and row. A test counts for one of six fire-safety questions only when its investigation states that question as a purpose.

Interpret: per question, the page quotes what NASA's documents report, then says whether the needed values are in NASA's tables, only in the raw archive (60,866 listed files, 13.47 TB), or have no record in PSI.

Worked example: type "lunar habitat cotton fabric". It reads cotton fabric, and 30% oxygen at 70.3 kPa from the challenge's lunar preset. The closest are SAFFIRE-II (match score 75.0) and SAFFIRE-I (74.5): Saffire burned a cotton-fiberglass fabric (fuel similarity 1.00) near 22% oxygen (oxygen similarity 0.24 and 0.22). The third place goes to the best result whose tested oxygen range includes 30%: ACME-BRE (62.6, a gas burner emulating a burning solid, 21 to 40%). Then: at 30% oxygen or more and at or below 70.3 kPa there is no counted test; none of the 139 solid-fuel tests that record oxygen is above 22.2%, and none records a pressure. The challenge statement suggests that microgravity and normal-gravity results could bound intermediate gravity; the page shows NASA drop-tower tests of three materials (Olson and Ferkul, AIAA 2012-3492, NTRS 20130010991, Table I) in which oxygen limits at lunar gravity were lower than at both 0 g and 1 g.

Benefits

From one description: the closest NASA experiments with DOIs, the matching tests as CSV with source rows, the raw files to open first, and the conditions with no counted test. Observed values, quoted NASA criteria and gaps stay apart.

Intended impact

Students, researchers and engineers see what NASA's tests cover for a crewed environment and what they leave open, so new experiments and data requests can target the gaps. Environments are compared by test counts: 4 of 6 questions have counted tests in an ISS cabin, 1 of 6 in a lunar habitat (17 FLEX droplet tests at 71.2 to 72.4 kPa, about 1 to 2 kPa above 70.3 kPa).

Tools, coding languages, hardware and software

Python 3.13 (pipeline, ranking, checks); JavaScript, HTML and CSS (static page; Node.js checks its ranking port against Python); shell. Hosting: GitHub Pages and Actions. Libraries: pandas, NumPy, scikit-learn, Pillow, Playwright with Chromium, FFmpeg. Language model: OpenAI gpt-oss:20b (open weights, Apache-2.0) through Ollama 0.40.16, run locally. Claude Code (Anthropic) wrote the code under the team's direction. Hardware: a MacBook Pro with an Apple M4 Pro chip and 48 GB of memory. The 83 unit tests of the ranking pass.

How it is creative

It shows where the evidence stops as plainly as what it holds, and starts from the question, not the archive: code follows NASA's test identifiers to the tables and raw files. The language model works inside code: it may only write sentences that cite numbered facts that code looked up, every number must appear in those facts, and a sentence that fails a check is removed.

What the team considered

It is a research exploration tool: no safety verdict, no prediction for an untested condition. Match scores and the order are Team RAPID's computation from NASA PSI data. 33 of 70 model-written card sentences are shown, after code checks and a second AI session's reading. The assistant runs in the local install (./install.sh, ./run.sh); the public page replays recorded answers. On 74 evaluation questions the full pipeline read 94% of the scored fields correctly (one model call: 84%) and showed no number outside its cited facts (one call: 36). The ranges and weights are the team's choices. Next: ask combustion researchers to check the rules; more environments; a pipeline re-run when PSI adds partial-gravity data.

Live page: https://choidol0208.github.io/NASA_RAPID/
How it works: https://choidol0208.github.io/NASA_RAPID/how.html
Source code: https://github.com/choidol0208/NASA_RAPID
Challenge fit: https://github.com/choidol0208/NASA_RAPID/blob/main/docs/submission/challenge_fit.md
```

Count (by code): 695 words (asked: 450 to 700). If the marker is replaced by longer text, keep the total at 700 words or fewer.

## 6. Use of Super Intelligence (SI)

The options of this multi-select are not in the saved page, so here is what the team used, in plain words. Tick every option that matches one of these.

- An AI coding assistant: Claude Code (Anthropic), with Claude models. It wrote the code, the data pipeline, the page, the documents (this text included) and the slide draft, under the team's direction. claude.ai chat sessions (Anthropic) wrote the first catalog, the first ranking rules, the first validation scenarios and one slide. The Exa web-search tool, used inside Claude Code, found and fetched standards and papers.
- A large language model inside the product: OpenAI gpt-oss:20b, open weights, Apache-2.0, run locally through Ollama 0.40.16. It writes the cited summary sentences on the investigation cards and the answers of the conversational assistant. Code checks every sentence against the sources it cites; no model produces or changes a ranking score.
- No AI-generated image, audio or video. The slides hold captures of the team's own page and charts drawn by code.
- How SI-generated code and data are acknowledged: the header comment of every code file says it was written with an AI assistant; the JSON data files carry a metadata field (`_meta`) that says which AI-written code built them and which model ran, if any, and `pipeline/README.md` names the AI-written script behind each CSV file; the README says so; on the page, model-written text carries the label "AI-generated" with the model's name, the method page `how.html` explains how AI is used and how it was checked, and the footer says the page was built with AI assistance.

If the form shows a text box, paste this (64 words):

```
Claude Code (Anthropic), an AI coding assistant, wrote the code, data pipeline, page, documents and slide draft under the team's direction. Inside the product, the local open-weight model OpenAI gpt-oss:20b (Apache-2.0, via Ollama) writes cited summary sentences and assistant answers; code checks every sentence against its sources. Code files, data files, the README and page labels say so. No AI-generated images, audio or video.
```

## 7. NASA Data

One pair per NASA data set or resource. Order: (a) the challenge's own resource, the PSI combustion repository; (b) the 24 PSI investigations, by DOI; (c) NASA documents and NTRS records used by the page; (d) the full list in the repository. If time is short, enter the pairs marked "enter these first" and then the last pair (the full list). The "Licence" line is for the team's own record; it does not go into the form.

Where each address came from ("from:"): M = `data/psi/manifest.json` (the DOI, written as https://doi.org/ + DOI); S = `compliance/SOURCES.md`; R = `pipeline/spec/references.json`; T = `docs/submission/submission_text.md`; D = `README.md`. The last pair is the repository address (in `docs/submission/submission_text.md`) plus the path of a tracked file. Group (c) leaves out PSI download links (signed, they may expire) and addresses that repeat a DOI of group (b) (the SAME and SAME-R documents filed in PSI are reached through those DOIs).

1. [enter these first]
   Link Text: PSI Data Repository: Combustion Science (challenge resource), NASA PSI
   Link Url: https://psi.nasa.gov/physci/repo/search?q=combustion
   Licence: CC0-1.0 per investigation (PSI-10: none stated) | from: S, T
2. [enter these first]
   Link Text: SAFFIRE-II (PSI-99), NASA PSI
   Link Url: https://doi.org/10.60555/2chp-m469
   Licence: CC0-1.0 | from: M, T
3. [enter these first]
   Link Text: SAFFIRE-I (PSI-98), NASA PSI
   Link Url: https://doi.org/10.60555/0t15-1z43
   Licence: CC0-1.0 | from: M, T
4. [enter these first]
   Link Text: ACME BRE (PSI-20), NASA PSI
   Link Url: https://doi.org/10.60555/vb93-3y72
   Licence: CC0-1.0 | from: M, T
5. [enter these first]
   Link Text: BASS-II (PSI-25), NASA PSI
   Link Url: https://doi.org/10.60555/4qc4-de67
   Licence: CC0-1.0 | from: M, S, T
6. [enter these first]
   Link Text: FLEX (PSI-69), NASA PSI
   Link Url: https://doi.org/10.60555/mbq8-0451
   Licence: CC0-1.0 | from: M, T
7. [enter these first]
   Link Text: ACME CFI-G (PSI-159), NASA PSI
   Link Url: https://doi.org/10.60555/cyt1-kh64
   Licence: CC0-1.0 | from: M, T
8. [enter these first]
   Link Text: BASS (PSI-26), NASA PSI
   Link Url: https://doi.org/10.60555/58h4-dy80
   Licence: CC0-1.0 | from: M, T
9. [enter these first]
   Link Text: SAFFIRE-III (PSI-100), NASA PSI
   Link Url: https://doi.org/10.60555/040q-4h36
   Licence: CC0-1.0 | from: M, T
10. [enter these first]
   Link Text: SAME (PSI-102), NASA PSI
   Link Url: https://doi.org/10.60555/gd4k-8h62
   Licence: CC0-1.0 | from: M, S, R, T
11. [enter these first]
   Link Text: SAME-R (PSI-101), NASA PSI
   Link Url: https://doi.org/10.60555/2np7-jv14
   Licence: CC0-1.0 | from: M, S, R, T
12. [enter these first]
   Link Text: SPICE (PSI-107), NASA PSI
   Link Url: https://doi.org/10.60555/9kbh-e962
   Licence: CC0-1.0 | from: M, T
13.
   Link Text: CFI (PSI-39), NASA PSI
   Link Url: https://doi.org/10.60555/m6pj-a914
   Licence: CC0-1.0 | from: M, T
14.
   Link Text: ACME/Flame Design (PSI-10), NASA PSI
   Link Url: https://doi.org/10.60555/w4zy-bt45
   Licence: none stated in the PSI record | from: M, T
15.
   Link Text: FLEX-2 (PSI-68), NASA PSI
   Link Url: https://doi.org/10.60555/byp8-h018
   Licence: CC0-1.0 | from: M, T
16.
   Link Text: DAFT / DAFT-2 (PSI-47), NASA PSI
   Link Url: https://doi.org/10.60555/ztgj-d202
   Licence: CC0-1.0 | from: M, T
17.
   Link Text: SLICE (PSI-106), NASA PSI
   Link Url: https://doi.org/10.60555/pm12-rg61
   Licence: CC0-1.0 | from: M, T
18.
   Link Text: ACME CLD Flame (PSI-21), NASA PSI
   Link Url: https://doi.org/10.60555/23e1-9950
   Licence: CC0-1.0 | from: M, T
19.
   Link Text: ACME E-FIELD Flames (PSI-22), NASA PSI
   Link Url: https://doi.org/10.60555/se5a-8c73
   Licence: CC0-1.0 | from: M, T
20.
   Link Text: ACME s-Flame (PSI-23), NASA PSI
   Link Url: https://doi.org/10.60555/k57n-p030
   Licence: CC0-1.0 | from: M, T
21.
   Link Text: SPICE data analysis (PSI-60), NASA PSI
   Link Url: https://doi.org/10.60555/mzjm-yv57
   Licence: CC0-1.0 | from: M, T
22.
   Link Text: BASS flame spread modeling (PSI-62), NASA PSI
   Link Url: https://doi.org/10.60555/e9xp-ex83
   Licence: CC0-1.0 | from: M, T
23.
   Link Text: SAME smoke modeling (PSI-115), NASA PSI
   Link Url: https://doi.org/10.60555/q0v5-1v28
   Licence: CC0-1.0 | from: M, T
24.
   Link Text: Cool flame CFD analysis (PSI-117), NASA PSI
   Link Url: https://doi.org/10.60555/gz0q-b577
   Licence: CC0-1.0 | from: M, T
25.
   Link Text: Cool flame counterflow studies (PSI-142), NASA PSI
   Link Url: https://doi.org/10.60555/80qf-vj95
   Licence: CC0-1.0 | from: M, T
26.
   Link Text: Evaluating Material Flammability in Microgravity and Martian Gravity... (AIAA 2012-3492)
   Link Url: https://ntrs.nasa.gov/citations/20130010991
   Licence: Copyright belongs to the publisher and authors | from: S, R, T
27.
   Link Text: Flammability, Offgassing, and Compatibility Requirements and Test... (NASA-STD-6001B)
   Link Url: https://standards.nasa.gov/sites/default/files/standards/NASA/B-w/CHANGE-3/3/2025_06_25_NASA-STD-6001B_w_Change_3_FINAL_Admin-Change-FINAL.pdf
   Licence: Open for public reading | from: S, R, T
28.
   Link Text: NASA-STD-3001 Technical Brief: Fire Protection (OCHMO-TB-008 Rev A)
   Link Url: https://www.nasa.gov/wp-content/uploads/2023/12/ochmo-tb-008-fire-protection.pdf
   Licence: U.S. Government work, open for public reading | from: S, R, T
29.
   Link Text: Burning and Suppression of Solids-II (BASS-II) Summary Report (NASA/TM-20210011385)
   Link Url: https://ntrs.nasa.gov/citations/20210011385
   Licence: U.S. Government work, available for public use | from: S, R, T
30.
   Link Text: Detailed Results From the Flame Extinguishment Experiment (FLEX)... (NASA/TP-2015-216046)
   Link Url: https://ntrs.nasa.gov/citations/20150023456
   Licence: U.S. Government work, available for public use | from: S, R, T
31.
   Link Text: A Researcher's Guide to: Combustion Science (NP-2015-10-034-JSC)
   Link Url: https://www.nasa.gov/wp-content/uploads/2016/05/np-2015-10-034-jsc_combustion_in_reduced_gravity-iss-mini-book-011116-508.pdf
   Licence: U.S. Government work, available for public use | from: S, R, T
32.
   Link Text: NASA Spaceflight Human-System Standard, Volume 2: Human Factors,...
   Link Url: https://standards.nasa.gov/standard/NASA/NASA-STD-3001_VOL_2
   Licence: Open for public reading | from: S, R, T
33.
   Link Text: Recommendations for Exploration Spacecraft Internal Atmospheres: The... (NASA/TP-2010-216134)
   Link Url: https://www.nasa.gov/wp-content/uploads/2023/03/henninger-8.2-34-atm-tp216134-2010.pdf
   Licence: U.S. Government work, open for public reading | from: S, R, T
34.
   Link Text: Spacecraft Maximum Allowable Concentrations for Airborne Contaminants (JSC 20584 Rev D)
   Link Url: https://www.nasa.gov/wp-content/uploads/2026/02/jsc-20584-smacs-rev-d.pdf
   Licence: U.S. Government work, open for public reading | from: S, R, T
35.
   Link Text: Evidence Report: Risk of Hypobaric Hypoxia from the Exploration... (NTRS 20150021491)
   Link Url: https://ntrs.nasa.gov/citations/20150021491
   Licence: U.S. Government work, open for public reading | from: S, R, T
36.
   Link Text: Correlation of Normal Gravity Aerospace Materials Flammability Data...
   Link Url: https://taskbook.nasaprs.com/tbp/tbpdf.cfm?id=14639
   Licence: U.S. Government work, open for public reading | from: S, R, T
37.
   Link Text: Research Needs in Fire Safety for the Human Exploration and... (NASA/CP-2003-212103)
   Link Url: https://ntrs.nasa.gov/citations/20030053425
   Licence: U.S. Government work, open for public reading | from: S, R, T
38.
   Link Text: Research Requirements Document: Droplet Flame Extinguishment in...
   Link Url: https://www1.grc.nasa.gov/wp-content/uploads/FLEX_EIRD_v4.pdf
   Licence: U.S. Government work, open for public reading | from: S, R, T
39.
   Link Text: Preliminary Results from the Saffire VI Experiment (ICES-2024-365)
   Link Url: https://ntrs.nasa.gov/citations/20240002981
   Licence: Public NTRS document. The copyright notice says 'may include copyright material' | from: S, R, T
40.
   Link Text: Results of Large-Scale Spacecraft Flammability Tests, presentation... (NTRS 20170008805)
   Link Url: https://ntrs.nasa.gov/citations/20170008805
   Licence: terms not recorded by the team | from: S, R, T
41.
   Link Text: Saffire: A Novel Approach to Study of Spacecraft Fire Safety Using... (NTRS 20180005168)
   Link Url: https://ntrs.nasa.gov/citations/20180005168
   Licence: terms not recorded by the team | from: S, R, T
42.
   Link Text: Fire Safety Implications of Preliminary Results from Saffire IV and V... (ICES-2021-266)
   Link Url: https://ntrs.nasa.gov/citations/20210011521
   Licence: terms not recorded by the team | from: S, R, T
43.
   Link Text: Buoyancy Effects on Concurrent Flame Spread Over Thick PMMA (NTRS 20200000557)
   Link Url: https://ntrs.nasa.gov/citations/20200000557
   Licence: terms not recorded by the team | from: S, R, T
44.
   Link Text: NASA PSI, Saffire-I (PSI-98) and Saffire-II (PSI-99): telemetry graph...
   Link Url: https://psi.nasa.gov/physci/repo/data/investigations/PSI-99
   Licence: CC0-1.0 for both investigations, per the PSI records | from: S, R, T
45.
   Link Text: Particle Morphology and Size Results from the Smoke Aerosol... (NTRS 20130000422)
   Link Url: https://ntrs.nasa.gov/citations/20130000422
   Licence: terms not recorded by the team | from: S, R, T
46.
   Link Text: Final Report: Fire Prevention, Detection, and Suppression Project,... (NASA/TM-2011-217036)
   Link Url: https://ntrs.nasa.gov/citations/20110020262
   Licence: U.S. Government work, available for public use | from: S, R, T
47.
   Link Text: Strategic Research to Enable NASA's Exploration Missions Conference... (NASA/CP-2004-213205/VOL1)
   Link Url: https://ntrs.nasa.gov/citations/20040142351
   Licence: terms not recorded by the team | from: S, R, T
48.
   Link Text: Operation and Development Status of the Spacecraft Fire Experiments... (NTRS 20170000230)
   Link Url: https://ntrs.nasa.gov/citations/20170000230
   Licence: terms not recorded by the team | from: S, R, T
49.
   Link Text: The Spacecraft Fire Experiment (Saffire) - Objectives, Development... (NTRS 20170001636)
   Link Url: https://ntrs.nasa.gov/citations/20170001636
   Licence: terms not recorded by the team | from: S, R, T
50.
   Link Text: Research Questions and Challenges for Improved Spacecraft Fire... (NTRS 20210022143)
   Link Url: https://ntrs.nasa.gov/citations/20210022143
   Licence: terms not recorded by the team | from: S, R, T
51.
   Link Text: Topical: Recommendations for Fire Extinguisher Research for Crewed... (NTRS 20210023340)
   Link Url: https://ntrs.nasa.gov/citations/20210023340
   Licence: terms not recorded by the team | from: S, R, T
52.
   Link Text: Fire Safety in the Low-Gravity Spacecraft Environment (Friedman) (NASA/TM-1999-209285)
   Link Url: https://ntrs.nasa.gov/citations/19990063738
   Licence: terms not recorded by the team | from: S, R, T
53.
   Link Text: Results from on-board CSA-CP and CDM Sensor Readings during the... (ICES-2015-196)
   Link Url: https://ntrs.nasa.gov/citations/20150019858
   Licence: terms not recorded by the team | from: S, R, T
54.
   Link Text: Thickness and Fuel Preheating Effects on Material Flammability in... (NTRS 20140011099)
   Link Url: https://ntrs.nasa.gov/citations/20140011099
   Licence: terms not recorded by the team | from: S, R, T
55.
   Link Text: Gaseous Non-Premixed Flame Research Planned for the International... (NTRS 20140009169)
   Link Url: https://ntrs.nasa.gov/citations/20140009169
   Licence: terms not recorded by the team | from: S, R, T
56.
   Link Text: Recent Research on Flames of Gaseous Fuel Aboard the International... (NTRS 20210022542)
   Link Url: https://ntrs.nasa.gov/citations/20210022542
   Licence: terms not recorded by the team | from: S, R, T
57.
   Link Text: Cool-flame extinction during n-alkane droplet combustion in... (NTRS 20140006750)
   Link Url: https://ntrs.nasa.gov/citations/20140006750
   Licence: terms not recorded by the team | from: S, R, T
58.
   Link Text: Applying Flammability Limit Probabilities and the Normoxic Upward... (ICES-2014-179)
   Link Url: https://ntrs.nasa.gov/citations/20150004099
   Licence: terms not recorded by the team | from: S, R, T
59.
   Link Text: Pressure Effects on Oxygen Concentration Flammability Thresholds of... (NTRS 20070005041)
   Link Url: https://ntrs.nasa.gov/citations/20070005041
   Licence: preprint U.S. Government work | from: S, R, T
60.
   Link Text: Oxygen Concentration Flammability Thresholds of Selected Aerospace... (NTRS 20070018178)
   Link Url: https://ntrs.nasa.gov/citations/20070018178
   Licence: terms not recorded by the team | from: S, R, T
61.
   Link Text: Pressure Flammability Thresholds of Selected Aerospace Materials (NTRS 20100015582)
   Link Url: https://ntrs.nasa.gov/citations/20100015582
   Licence: terms not recorded by the team | from: S, R, T
62.
   Link Text: Selected Parametric Effects on Materials Flammability Limits (NTRS 20110008636)
   Link Url: https://ntrs.nasa.gov/citations/20110008636
   Licence: NTRS record: GOV_PUBLIC_USE_PERMITTED | from: S, R, T
63.
   Link Text: Bounding the Spacecraft Atmosphere Design Space for Future... (NASA/CR-2005-213689)
   Link Url: https://ntrs.nasa.gov/citations/20050185597
   Licence: terms not recorded by the team | from: S, R, T
64.
   Link Text: Microgravity Flammability of PMMA Rods in Concurrent Flow (NTRS 20150008961)
   Link Url: https://ntrs.nasa.gov/citations/20150008961
   Licence: terms not recorded by the team | from: S, R, T
65.
   Link Text: An Overview of the Microgravity Science Glovebox (MSG) Facility and... (NTRS 20140011630)
   Link Url: https://ntrs.nasa.gov/citations/20140011630
   Licence: terms not recorded by the team | from: S, R, T
66.
   Link Text: Buoyant Effects on the Flammability of Silicone Samples Planned for... (NTRS 20150022421)
   Link Url: https://ntrs.nasa.gov/citations/20150022421
   Licence: terms not recorded by the team | from: S, R, T
67.
   Link Text: Large-Scale Spacecraft Fire Safety Tests (NTRS 20150000894)
   Link Url: https://ntrs.nasa.gov/citations/20150000894
   Licence: terms not recorded by the team | from: S, R, T
68.
   Link Text: NASA PSI, BASS-II (PSI-25) raw-data documents: SRD_BASS-II.pdf,...
   Link Url: https://psi.nasa.gov/physci/repo/data/investigations/PSI-25
   Licence: CC0-1.0 | from: S, R, T
69.
   Link Text: Flammability, Offgassing, and Compatibility Requirements and Test... (NASA-STD-(I)-6001B)
   Link Url: https://ntrs.nasa.gov/citations/20110012152
   Licence: NASA documents; notice on each not read | from: S, R, T
70.
   Link Text: Standard Materials and Processes Requirements for Spacecraft (NASA-STD-6016C)
   Link Url: https://ntrs.nasa.gov/citations/20210021618
   Licence: NASA documents; notice on each not read | from: S, R, T
71.
   Link Text: Flammability Configuration Analysis for Spacecraft Applications (JSC 29353B)
   Link Url: https://ntrs.nasa.gov/citations/20150020937
   Licence: NASA documents; notice on each not read | from: S, R, T
72.
   Link Text: Concurrent flame growth, spread and extinction over composite fabric... (NTRS 20150008962)
   Link Url: https://ntrs.nasa.gov/citations/20150008962
   Licence: NTRS record: PUBLIC_USE_PERMITTED | from: S, R, T
73.
   Link Text: Effects of Confinement on Flame Spread in Microgravity (ICES-2020-407)
   Link Url: https://ntrs.nasa.gov/citations/20205004657
   Licence: NTRS record: GOV_PERMITTED | from: S, R, T
74.
   Link Text: Lunar Combustion Investigation: Flammability Results from a Rotating... (NTRS 20250010653)
   Link Url: https://ntrs.nasa.gov/citations/20250010653
   Licence: NTRS record: GOV_PERMITTED | from: S, R, T
75.
   Link Text: Material Ignition and Suppression Test (MIST) in Space Exploration... (NTRS 20150023467)
   Link Url: https://ntrs.nasa.gov/citations/20150023467
   Licence: NTRS record: PUBLIC_USE_PERMITTED | from: S, R, T
76.
   Link Text: Methanol Droplet Combustion in Oxygen-Inert Environments in... (NTRS 20130014061)
   Link Url: https://ntrs.nasa.gov/citations/20130014061
   Licence: NTRS record: PUBLIC_USE_PERMITTED | from: S, R, T
77.
   Link Text: Effects of Ambient Inert Gas Properties on Cool-Flame Combustion of... (NTRS 20205008449)
   Link Url: https://ntrs.nasa.gov/citations/20205008449
   Licence: NTRS record: PUBLIC_USE_PERMITTED | from: S, R, T
78.
   Link Text: The Water-Mist Fire Suppression Experiment (Mist): Preliminary... (NTRS 20040053582)
   Link Url: https://ntrs.nasa.gov/citations/20040053582
   Licence: NTRS record: GOV_PUBLIC_USE_PERMITTED | from: S, R, T
79.
   Link Text: Suppression and Structure of Low Strain Rate Nonpremixed Flames (NTRS 20040053579)
   Link Url: https://ntrs.nasa.gov/citations/20040053579
   Licence: NTRS record: GOV_PUBLIC_USE_PERMITTED | from: S, R, T
80.
   Link Text: Evaluation of Combustion Products from Large-Scale Spacecraft Fires... (NTRS 20210017343)
   Link Url: https://ntrs.nasa.gov/citations/20210017343
   Licence: NTRS record: MAY_INCLUDE_COPYRIGHT_MATERIAL | from: S, R, T
81.
   Link Text: Particle Morphology Results from the Smoke Aerosol Measurement... (NTRS 20150010172)
   Link Url: https://ntrs.nasa.gov/citations/20150010172
   Licence: NTRS record: PUBLIC_USE_PERMITTED | from: S, R, T
82.
   Link Text: Spacecraft Fire Detection: Smoke Properties and Transport in... (AIAA-2008-806)
   Link Url: https://ntrs.nasa.gov/citations/20080012612
   Licence: NTRS item U.S. Government work | from: S, R, T
83.
   Link Text: Properties of Smoke from Overheated Materials in Low-Gravity (NTRS 20120012884)
   Link Url: https://ntrs.nasa.gov/citations/20120012884
   Licence: NTRS record: PUBLIC_USE_PERMITTED | from: S, R, T
84.
   Link Text: Evaluation of Low-Gravity Smoke Particulate for Spacecraft Fire... (NTRS 20140006585)
   Link Url: https://ntrs.nasa.gov/citations/20140006585
   Licence: NTRS record: PUBLIC_USE_PERMITTED | from: S, R, T
85.
   Link Text: Safety Case Notations: Alternatives for the Non-Graphically Inclined?
   Link Url: https://ntrs.nasa.gov/citations/20080042416
   Licence: NTRS record: PUBLIC, GOV_PUBLIC_USE_PERMITTED | from: S, T
86.
   Link Text: NASA/TM-2017-219650
   Link Url: https://ntrs.nasa.gov/citations/20170007188
   Licence: NTRS record: PUBLIC_USE_PERMITTED | from: S, T
87.
   Link Text: Making the Implicit Explicit: Towards an Assurance Case for DO-178C
   Link Url: https://ntrs.nasa.gov/citations/20140002745
   Licence: NTRS record: GOV_PUBLIC_USE_PERMITTED | from: S, T
88.
   Link Text: NASA Systems Engineering Handbook, NASA/SP-2016-6105 Rev2
   Link Url: https://ntrs.nasa.gov/citations/20170001761
   Licence: U.S. Government work, available for public use | from: S, T
89.
   Link Text: Dietrich et al. (2014), Microgravity Sci Technol 26(2); Nayagam et al. (2012),...
   Link Url: https://ntrs.nasa.gov/citations/20120016855
   Licence: journal articles cited only | from: S, T
90.
   Link Text: de Ris (1969); Fernandez-Pello, Ray and Glassman (1981); Wichman (1992); Olson...
   Link Url: https://ntrs.nasa.gov/citations/19860018906
   Licence: journal articles cited only | from: S, T
91.
   Link Text: NASA-STD-6001B, Flammability, Offgassing, and Compatibility Requirements and...
   Link Url: https://standards.nasa.gov/standard/NASA/NASA-STD-6001
   Licence: U.S. Government work, available for public use | from: S, T
92.
   Link Text: NASA Science Mission Directorate, "Scientific Information Policy for the...
   Link Url: https://science.nasa.gov/spd-41/
   Licence: The document carries the distribution statement "Approved for public release" an | from: S, T
93.
   Link Text: Video design method source (NTRS PDF)
   Link Url: https://ntrs.nasa.gov/api/citations/20210021781/downloads/JASMAC%20ACME%20paper%2020210921.pdf
   Licence: NTRS: U.S. Government work | from: S, T
94.
   Link Text: Flame in Freefall challenge statement (NASA Space Apps Challenge 2026)
   Link Url: https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/
   Licence: public challenge page | from: S, R, T
95.
   Link Text: Full list of NASA sources with licences (project repository)
   Link Url: https://github.com/choidol0208/NASA_RAPID/blob/main/compliance/SOURCES.md
   Licence: Apache-2.0 (repository) | from: repo path compliance/SOURCES.md

95 pairs.

## 8. Space Agency Partner & Other Data

Everything used that is not NASA's: the model and its runtime, the AI tools, the fonts, Python and the libraries, hosting, and the non-NASA papers, standards and method sources of `compliance/SOURCES.md` and `pipeline/spec/references.json`. Same form; "Licence (team record)" is for the team's own record. The event's own rule pages (Submission Guide, Judging Guide) are not listed; the challenge statement stands in section 7. Two sources have no address in the repository and cannot be entered as a link: Space systems - Safety and compatibility of materials - Part 1: Determination of upward fl; Lahdelma and Salminen, SMAA-2, Operations Research 49(3), 2001 (method idea only). They stay in the full list.

1. [enter these first]
   Link Text: OpenAI gpt-oss:20b, open-weight language model (in the product)
   Link Url: https://ollama.com/library/gpt-oss
   Licence (team record): Apache-2.0 (confirmed from the licence text included with the model) | from: S, T
2. [enter these first]
   Link Text: Ollama 0.40.16, local model runtime
   Link Url: https://github.com/ollama/ollama
   Licence (team record): MIT (confirmed from the licence information on GitHub) | from: S, T
3. [enter these first]
   Link Text: Claude Code (Anthropic), AI coding assistant used to build the project
   Link Url: https://claude.com/claude-code
   Licence (team record): Commercial service of Anthropic, not open source | from: S, T
4. [enter these first]
   Link Text: claude.ai (Anthropic), Claude chat sessions used in development
   Link Url: https://claude.ai/
   Licence (team record): Commercial service of Anthropic, not open source | from: S, T
5. [enter these first]
   Link Text: Exa web search tool, used inside Claude Code
   Link Url: https://exa.ai/
   Licence (team record): Commercial service; terms not read (the terms page is a file download and was no | from: S, T
6. [enter these first]
   Link Text: Python 3.13.5 and its standard library
   Link Url: https://www.python.org
   Licence (team record): PSF-2.0 | from: S, T
7. [enter these first]
   Link Text: pandas (data pipeline)
   Link Url: https://github.com/pandas-dev/pandas
   Licence (team record): BSD-3-Clause | from: S, T
8. [enter these first]
   Link Text: GitHub Pages (hosting of the public page)
   Link Url: https://pages.github.com/
   Licence (team record): Service (no code included) | from: S, T
9. [enter these first]
   Link Text: Node.js (Python and browser ranking comparison)
   Link Url: https://nodejs.org/
   Licence (team record): MIT | from: S, T
10. [enter these first]
   Link Text: Playwright and Chromium (page checks and captures)
   Link Url: https://github.com/microsoft/playwright
   Licence (team record): Apache-2.0 (Playwright), BSD-3-Clause (Chromium) | from: S, T
11. [enter these first]
   Link Text: Atkinson Hyperlegible font (Google Fonts)
   Link Url: https://fonts.google.com/specimen/Atkinson+Hyperlegible
   Licence (team record): SIL Open Font License 1.1 | from: S, T
12. [enter these first]
   Link Text: Barlow Semi Condensed font (Google Fonts)
   Link Url: https://fonts.google.com/specimen/Barlow+Semi+Condensed
   Licence (team record): SIL Open Font License 1.1 | from: S, T
13.
   Link Text: NumPy
   Link Url: https://github.com/numpy/numpy
   Licence (team record): BSD-3-Clause | from: S, T
14.
   Link Text: scikit-learn (AI layer analysis scripts)
   Link Url: https://github.com/scikit-learn/scikit-learn
   Licence (team record): BSD-3-Clause | from: S, T
15.
   Link Text: Pillow (video reader tests)
   Link Url: https://github.com/python-pillow/Pillow
   Licence (team record): MIT-CMU (permissive; SPDX identifier MIT-CMU). Not bundled; needed only to run t | from: S, T
16.
   Link Text: FFmpeg (demo GIF, video decoding)
   Link Url: https://ffmpeg.org/
   Licence (team record): LGPL-2.1-or-later (some parts GPL-2.0-or-later) | from: S, T
17.
   Link Text: openpyxl (spreadsheet export)
   Link Url: https://foss.heptapod.net/openpyxl/openpyxl
   Licence (team record): MIT | from: S, T
18.
   Link Text: PptxGenJS (one slide)
   Link Url: https://github.com/gitbrent/PptxGenJS
   Licence (team record): MIT | from: S, T
19.
   Link Text: React (one slide)
   Link Url: https://github.com/facebook/react
   Licence (team record): MIT (licence field of the npm package, checked on registry.npmjs.org by the ui A | from: S, T
20.
   Link Text: react-icons (one slide)
   Link Url: https://github.com/react-icons/react-icons
   Licence (team record): MIT (react-icons, React), Apache-2.0 (sharp) | from: S, T
21.
   Link Text: sharp (slide icon images)
   Link Url: https://github.com/lovell/sharp
   Licence (team record): Apache-2.0 (licence field of the npm package, checked on registry.npmjs.org by t | from: S, T
22.
   Link Text: Tabler Icons (via react-icons)
   Link Url: https://github.com/tabler/tabler-icons
   Licence (team record): MIT | from: S, T
23.
   Link Text: GitHub Actions (publishing workflow)
   Link Url: https://github.com/actions
   Licence (team record): MIT | from: S, T
24.
   Link Text: Homebrew (optional install of Ollama on macOS)
   Link Url: https://brew.sh
   Licence (team record): BSD-2-Clause | from: S, T
25.
   Link Text: Ollama official install methods
   Link Url: https://ollama.com/download
   Licence (team record): MIT (Ollama, as already listed for Ollama 0.40.16) | from: S, T, D
26.
   Link Text: IBM Plex Sans KR and IBM Plex Mono fonts (internal data map page)
   Link Url: https://fonts.google.com/specimen/IBM+Plex+Sans+KR
   Licence (team record): SIL Open Font License 1.1 | from: S, T
27.
   Link Text: Apache License 2.0 text (project licence)
   Link Url: https://www.apache.org/licenses/LICENSE-2.0
   Licence (team record): Apache-2.0 | from: S, T
28.
   Link Text: gpt-oss-120b and gpt-oss-20b model card (OpenAI, arXiv)
   Link Url: https://arxiv.org/abs/2508.10925
   Licence (team record): CC BY 4.0 (paper, as the arXiv page states); the model materials are Apache-2.0 | from: S, T
29.
   Link Text: openai/gpt-oss-20b model page (Hugging Face)
   Link Url: https://huggingface.co/openai/gpt-oss-20b
   Licence (team record): the model is Apache-2.0 as the page states | from: S, T
30.
   Link Text: openai/gpt-oss repository README
   Link Url: https://github.com/openai/gpt-oss
   Licence (team record): Apache-2.0 (as the README states) | from: S, T
31.
   Link Text: Space systems - Safety and compatibility of materials - Method to... (ISO)
   Link Url: https://www.iso.org/standard/57450.html
   Licence (team record): Paid standard, copyright belongs to the issuing body | from: S, R, T
32.
   Link Text: Standard Test Method for Measuring the Minimum Oxygen Concentration... (ASTM International)
   Link Url: https://www.astm.org/d2863.html
   Licence (team record): Paid standard, copyright belongs to the issuing body | from: S, R, T
33.
   Link Text: Flammability Limits from BASS-II Testing in Microgravity Compared to... (49th International Conference on Environ)
   Link Url: https://hdl.handle.net/2346/84505
   Licence (team record): Copyright belongs to the publisher and authors | from: S, R, T
34.
   Link Text: Microgravity Flame Spread in Exploration Atmospheres: Pressure,... (SAE)
   Link Url: https://doi.org/10.4271/2008-01-2055
   Licence (team record): Copyright belongs to the publisher and authors | from: S, R, T
35.
   Link Text: The Saffire Experiment: Large-Scale Combustion aboard Spacecraft (10th U.S. National Combustion Meeting, C)
   Link Url: http://hdl.handle.net/20.500.11820/9397b059-72ed-41aa-8b7a-3ea8ba1bc795
   Licence (team record): Copyright belongs to the publisher and authors | from: S, R, T
36.
   Link Text: Evaluation of Spacecraft Smoke Detector Performance in the... (Fire Safety Journal)
   Link Url: https://pmc.ncbi.nlm.nih.gov/articles/PMC7918997/
   Licence (team record): Copyright belongs to the publisher and authors | from: S, R, T
37.
   Link Text: Droplet Combustion Experiments Aboard the International Space Station (Microgravity Science and Technology)
   Link Url: https://link.springer.com/article/10.1007/s12217-014-9372-2
   Licence (team record): Copyright belongs to the publisher and authors | from: S, R, T
38.
   Link Text: Results of Large-Scale Spacecraft Flammability Tests (47th International Conference on Environ)
   Link Url: https://hdl.handle.net/2346/73020
   Licence (team record): terms not recorded by the team | from: S, R, T
39.
   Link Text: Analysis of Saffire II two-sided concurrent flame spread over a thick... (48th International Conference on Environ)
   Link Url: http://hdl.handle.net/2346/74099
   Licence (team record): terms not recorded by the team | from: S, R, T
40.
   Link Text: The effect of duct size, sample size, and fuel composition on... (Combustion and Flame)
   Link Url: https://discovery.ucl.ac.uk/id/eprint/10164340/
   Licence (team record): terms not recorded by the team | from: S, R, T
41.
   Link Text: Pyrolysis Smoke Generated Under Low-Gravity Conditions (Aerosol Science and Technology 49(5), 31)
   Link Url: https://doi.org/10.1080/02786826.2015.1025125
   Licence (team record): Copyright 2015 American Association for Aerosol Research | from: S, R, T
42.
   Link Text: Recapturing a Future for Space Exploration: Life and Physical... (National Academies Press)
   Link Url: https://www.nationalacademies.org/read/13048/chapter/2
   Licence (team record): terms not recorded by the team | from: S, R, T
43.
   Link Text: On Simulating Concurrent Flame Spread in Reduced Gravity by Reducing... (Proceedings of the Combustion Institute)
   Link Url: https://pmc.ncbi.nlm.nih.gov/articles/PMC6907022/
   Licence (team record): terms not recorded by the team | from: S, R, T
44.
   Link Text: Standard Test Method for Measuring Liquid and Solid Material Fire... (ASTM International)
   Link Url: https://www.astm.org/g0125-00r23.html
   Licence (team record): Paid standard (as the entry's note records); terms not recorded by the team (add | from: S, R, T
45.
   Link Text: Turns, S. R., *An Introduction to Combustion: Concepts and Applications*, 3rd...
   Link Url: https://www.mheducation.com/
   Licence (team record): Copyrighted (McGraw-Hill). It was only read as background knowledge, and no sent | from: S, T
46.
   Link Text: OECD Guidance Document on the Validation of (Q)SAR Models, ENV/JM/MONO(2007)2,...
   Link Url: https://www.oecd.org/content/dam/oecd/en/publications/reports/2014/09/guidance-document-on-the-validation-of-quantitative-structure-activity-relationship-q-sar-models_g1ghcc68/9789264085442-en.pdf
   Licence (team record): not stated on the page | from: S, T
47.
   Link Text: NIST Dataplot Reference Manual, KENDALLS TAU
   Link Url: https://www.itl.nist.gov/div898/software/dataplot/refman2/auxillar/kendell.htm
   Licence (team record): not stated on the page | from: S, T
48.
   Link Text: NIST/SEMATECH e-Handbook of Statistical Methods, 7.2.6.2 Percentiles
   Link Url: https://www.itl.nist.gov/div898/handbook/prc/section2/prc262.htm
   Licence (team record): not stated on the page | from: S, T
49.
   Link Text: NIST SP 811, Guide for the Use of the SI, Appendix B
   Link Url: https://www.nist.gov/pml/special-publication-811/nist-guide-si-appendix-b-conversion-factors/nist-guide-si-appendix-b8
   Licence (team record): not stated on the page | from: S, T
50.
   Link Text: NIST-JANAF Thermochemical Tables, NIST SRD 13: N-023, O-029, C-095, H-064,...
   Link Url: https://janaf.nist.gov/
   Licence (team record): NIST Standard Reference Data, copyright U.S. Secretary of Commerce: not public d | from: S, T
51.
   Link Text: Mavin et al. (2009), Easy Approach to Requirements Syntax (EARS), IEEE RE'09,...
   Link Url: https://doi.org/10.1109/RE.2009.9
   Licence (team record): cited only, no text reproduced | from: S, T
52.
   Link Text: Guyatt et al. (2011), GRADE guidelines 8: indirectness, J Clin Epidemiol...
   Link Url: https://doi.org/10.1016/j.jclinepi.2011.04.014
   Licence (team record): cited only, no text reproduced | from: S, T
53.
   Link Text: Saaty (1980), The Analytic Hierarchy Process, McGraw-Hill; author's overview...
   Link Url: https://www.isahp-org.creativedecisions.net/uploads/1-how-to-make-a-decision-the-analytic-hierarchy-process-t-l-saaty.pdf
   Licence (team record): cited only; book (publisher copyright) | from: S, T
54.
   Link Text: Forman and Peniwati (1998), EJOR 108(1); Aczél and Saaty (1983), J Math Psych...
   Link Url: https://doi.org/10.1016/S0377-2217(97)00244-0
   Licence (team record): cited only, no text reproduced | from: S, T
55.
   Link Text: Rezaei (2015), Best-worst method, Omega 53
   Link Url: https://doi.org/10.1016/j.omega.2014.11.009
   Licence (team record): cited only, no text reproduced | from: S, T
56.
   Link Text: Grömping (2006), relaimpo, J Stat Softw 17(1); Lipovetsky and Conklin (2001),...
   Link Url: https://www.jstatsoft.org/v17/i01
   Licence (team record): open access (JSS) / journal article; cited only | from: S, T
57.
   Link Text: Efron and Tibshirani (1993), An Introduction to the Bootstrap, Chapman & Hall
   Link Url: https://doi.org/10.1201/9780429246593
   Licence (team record): cited only; book | from: S, T
58.
   Link Text: Genest and Zidek (1986), Combining probability distributions, Statistical...
   Link Url: https://doi.org/10.1214/ss/1177013825
   Licence (team record): open access; cited only | from: S, T
59.
   Link Text: Barron and Barrett (1996), Management Science 42(11); Lahdelma, Hokkanen and...
   Link Url: https://doi.org/10.1287/mnsc.42.11.1515
   Licence (team record): cited only, no text reproduced | from: S, T
60.
   Link Text: Gower (1971), Biometrics 27(4); Aamodt and Plaza (1994), AI Communications...
   Link Url: https://doi.org/10.2307/2528823
   Licence (team record): cited only, no text reproduced | from: S, T
61.
   Link Text: Law (1982), Recent advances in droplet vaporization and combustion, PECS 8(3)
   Link Url: https://doi.org/10.1016/0360-1285(82)90011-9
   Licence (team record): cited only, no text reproduced | from: S, T
62.
   Link Text: Huggett (1980), Fire and Materials 4(2); NIST SP 958 commentary; Thornton (1917)
   Link Url: https://nvlpubs.nist.gov/nistpubs/sp958-lide/html/280-282.html
   Licence (team record): journal articles cited only | from: S, T
63.
   Link Text: Takahashi, Linteris and Katta (2008), Combust Flame 155(1-2); Macek (1976),...
   Link Url: https://nvlpubs.nist.gov/nistpubs/Legacy/IR/nbsir76-1076.pdf
   Licence (team record): journal article cited only | from: S, T
64.
   Link Text: Fenimore and Martin (1966), Flammability of polymers, Combust Flame 10(2)
   Link Url: https://doi.org/10.1016/0010-2180(66)90059-9
   Licence (team record): cited only, no text reproduced | from: S, T
65.
   Link Text: Walters and Lyon (2001), Calculating Polymer Flammability from Molar Group...
   Link Url: https://rosap.ntl.bts.gov/view/dot/92724
   Licence (team record): U.S. Government work, available for public use | from: S, T
66.
   Link Text: Jomaas et al. (2015), Fire safety in space – beyond flammability testing of...
   Link Url: https://doi.org/10.1016/j.actaastro.2014.11.025
   Licence (team record): cited only, no text reproduced | from: S, T
67.
   Link Text: Halevy, Korn, Noy, Olston, Polyzotis, Roy, Whang, "Goods: Organizing Google's...
   Link Url: https://research.google/pubs/goods-organizing-googles-datasets/
   Licence (team record): The page states no licence | from: S, T
68.
   Link Text: Binette and Steorts, "(Almost) All of Entity Resolution", arXiv:2008.04443
   Link Url: https://arxiv.org/abs/2008.04443
   Licence (team record): arXiv.org perpetual non-exclusive license 1.0 | from: S, T
69.
   Link Text: Koutras et al., "Valentine: Evaluating Matching Techniques for Dataset...
   Link Url: https://arxiv.org/abs/2010.07386
   Licence (team record): arXiv.org perpetual non-exclusive license 1.0 | from: S, T
70.
   Link Text: Abedjan, Golab, Naumann, "Profiling relational data: a survey", VLDB Journal...
   Link Url: https://dspace.mit.edu/handle/1721.1/106176
   Licence (team record): The repository page says the article is made available under the publisher's pol | from: S, T
71.
   Link Text: Apache Parquet documentation, "Page Index"
   Link Url: https://parquet.apache.org/docs/file-format/pageindex/
   Licence (team record): Apache License 2.0, copyright Apache Software Foundation | from: S, T
72.
   Link Text: PKWARE, ".ZIP File Format Specification"
   Link Url: https://pkware.cachefly.net/webdocs/casestudies/APPNOTE.TXT
   Licence (team record): All rights reserved, PKWARE Inc. | from: S, T
73.
   Link Text: MDN Web Docs, "HTTP range requests"
   Link Url: https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Range_requests
   Licence (team record): Creative Commons licence | from: S, T
74.
   Link Text: RFC 9110, "HTTP Semantics", section 14.1.2 (byte ranges)
   Link Url: https://www.rfc-editor.org/rfc/rfc9110.html
   Licence (team record): Copyright 2022 IETF Trust and the document authors, all rights reserved | from: S, T
75.
   Link Text: Leskovec, Krause, Guestrin, Faloutsos, VanBriesen, Glance, "Cost-effective...
   Link Url: https://www.cs.cmu.edu/~jure/pubs/detect-kdd07.pdf
   Licence (team record): Copyright 2007 ACM; the notice on the paper allows copies for personal or classr | from: S, T
76.
   Link Text: Settles, "Active Learning Literature Survey", Computer Sciences Technical...
   Link Url: https://burrsettles.com/pub/settles.activelearning.pdf
   Licence (team record): Terms not stated in the document. Cited only | from: S, T
77.
   Link Text: Sahigara, Mansouri, Ballabio, Mauri, Consonni, Todeschini, "Comparison of...
   Link Url: https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6268288/fullTextXML
   Licence (team record): CC BY 3.0 (stated in the article). Cited only; four words are quoted in design.m | from: S, T
78.
   Link Text: Wikipedia, "Binomial proportion confidence interval"
   Link Url: https://en.wikipedia.org/wiki/Binomial_proportion_confidence_interval
   Licence (team record): CC BY-SA 4.0 (page footer). Cited only; the primary papers were not opened | from: S, T
79.
   Link Text: Wikipedia, "Rule of three (statistics)"
   Link Url: https://en.wikipedia.org/wiki/Rule_of_three_(statistics)
   Licence (team record): CC BY-SA 4.0 (page footer). Cited only; the primary papers were not opened | from: S, T
80.
   Link Text: Sawadogo and Darmont, "On data lake architectures and metadata management",...
   Link Url: https://ar5iv.labs.arxiv.org/html/2107.11152
   Licence (team record): The ar5iv page states no licence | from: S, T
81.
   Link Text: Wilkinson et al., "The FAIR Guiding Principles for scientific data management...
   Link Url: https://pmc.ncbi.nlm.nih.gov/articles/PMC4792175/
   Licence (team record): CC BY 4.0 (stated on the page; copyright 2016 Macmillan Publishers Limited). Cit | from: S, T
82.
   Link Text: ISA Model and Serialization Specifications 1.0, "ISA-Tab format"
   Link Url: https://isa-specs.readthedocs.io/en/latest/isatab.html
   Licence (team record): Terms not stated on the page | from: S, T
83.
   Link Text: W3C, "PROV Model Primer", 2013
   Link Url: https://www.w3.org/TR/prov-primer/
   Licence (team record): Copyright 2013 W3C, all rights reserved | from: S, T
84.
   Link Text: Korini and Bizer, "Column Type Annotation using ChatGPT", arXiv:2306.00745
   Link Url: https://arxiv.org/abs/2306.00745
   Licence (team record): arXiv.org perpetual non-exclusive license 1.0 | from: S, T
85.
   Link Text: Video design method source
   Link Url: https://api.drum.lib.umd.edu/server/api/core/bitstreams/87c81c92-a4f9-4f44-a306-3ce3469f0e65/content
   Licence (team record): NTRS: U.S. Government work | from: S, T
86.
   Link Text: Rubin (1976), Inference and missing data, Biometrika 63(3), 581–592,...
   Link Url: https://doi.org/10.1093/biomet/63.3.581
   Licence (team record): cited only, no text reproduced | from: S, T
87.
   Link Text: Efficient Guided Generation for Large Language Models
   Link Url: https://arxiv.org/abs/2307.09702
   Licence (team record): CC BY 4.0 | from: S, T
88.
   Link Text: Structured outputs
   Link Url: https://ollama.com/blog/structured-outputs
   Licence (team record): terms not stated on the page | from: S, T
89.
   Link Text: Ollama API reference (docs/api.md)
   Link Url: https://github.com/ollama/ollama/blob/main/docs/api.md
   Licence (team record): repository licensed MIT | from: S, T
90.
   Link Text: The harmony response format (OpenAI cookbook)
   Link Url: https://developers.openai.com/cookbook/articles/openai-harmony
   Licence (team record): terms not stated on the page | from: S, T
91.
   Link Text: Structured outputs (Claude API docs)
   Link Url: https://platform.claude.com/docs/en/build-with-claude/structured-outputs
   Licence (team record): terms not stated on the page | from: S, T
92.
   Link Text: Let Me Speak Freely? A Study on the Impact of Format Restrictions on...
   Link Url: https://arxiv.org/abs/2408.02442
   Licence (team record): CC BY-SA 4.0 | from: S, T
93.
   Link Text: Enabling Large Language Models to Generate Text with Citations
   Link Url: https://arxiv.org/abs/2305.14627
   Licence (team record): arXiv non-exclusive distribution licence 1.0 | from: S, T
94.
   Link Text: Citations (Claude API docs)
   Link Url: https://platform.claude.com/docs/en/build-with-claude/citations
   Licence (team record): terms not stated on the page | from: S, T
95.
   Link Text: Least-to-Most Prompting Enables Complex Reasoning in LLMs
   Link Url: https://arxiv.org/abs/2205.10625
   Licence (team record): arXiv non-exclusive distribution licence 1.0 | from: S, T
96.
   Link Text: ReAct: Synergizing Reasoning and Acting in Language Models
   Link Url: https://arxiv.org/abs/2210.03629
   Licence (team record): CC BY 4.0 | from: S, T
97.
   Link Text: Building effective agents
   Link Url: https://www.anthropic.com/engineering/building-effective-agents
   Licence (team record): terms not stated on the page | from: S, T
98.
   Link Text: Self-Consistency Improves Chain of Thought Reasoning in Language Models
   Link Url: https://arxiv.org/abs/2203.11171
   Licence (team record): CC BY 4.0 | from: S, T
99.
   Link Text: Reduce hallucinations (Claude docs)
   Link Url: https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations
   Licence (team record): terms not stated on the page | from: S, T
100.
   Link Text: Clarify When Necessary: Resolving Ambiguity Through Interaction with LMs
   Link Url: https://arxiv.org/abs/2311.09469
   Licence (team record): CC BY 4.0 | from: S, T
101.
   Link Text: Tool use with Claude (Claude API docs)
   Link Url: https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview
   Licence (team record): terms not stated on the page | from: S, T
102.
   Link Text: Chain-of-Verification Reduces Hallucination in LLMs
   Link Url: https://arxiv.org/abs/2309.11495
   Licence (team record): arXiv non-exclusive distribution licence 1.0 | from: S, T
103.
   Link Text: TRUE: Re-evaluating Factual Consistency Evaluation
   Link Url: https://arxiv.org/abs/2204.04991
   Licence (team record): CC BY 4.0 | from: S, T
104.
   Link Text: Ragas: Automated Evaluation of Retrieval Augmented Generation
   Link Url: https://arxiv.org/abs/2309.15217
   Licence (team record): CC BY 4.0 | from: S, T
105.
   Link Text: Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena
   Link Url: https://arxiv.org/abs/2306.05685
   Licence (team record): arXiv non-exclusive distribution licence 1.0 | from: S, T
106.
   Link Text: Demystifying evals for AI agents
   Link Url: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
   Licence (team record): terms not stated on the page | from: S, T
107.
   Link Text: Self-Refine: Iterative Refinement with Self-Feedback
   Link Url: https://arxiv.org/abs/2303.17651
   Licence (team record): CC BY 4.0 | from: S, T
108.
   Link Text: Large Language Models Cannot Self-Correct Reasoning Yet
   Link Url: https://arxiv.org/abs/2310.01798
   Licence (team record): CC BY 4.0 | from: S, T
109.
   Link Text: Know Your Limits: A Survey of Abstention in LLMs
   Link Url: https://arxiv.org/abs/2407.18418
   Licence (team record): CC BY 4.0 | from: S, T
110.
   Link Text: FrugalGPT: How to Use LLMs While Reducing Cost and Improving Performance
   Link Url: https://arxiv.org/abs/2305.05176
   Licence (team record): arXiv non-exclusive distribution licence 1.0 | from: S, T
111.
   Link Text: Lost in the Middle: How Language Models Use Long Contexts
   Link Url: https://arxiv.org/abs/2307.03172
   Licence (team record): arXiv non-exclusive distribution licence 1.0 | from: S, T
112.
   Link Text: Effective context engineering for AI agents
   Link Url: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
   Licence (team record): terms not stated on the page | from: S, T
113.
   Link Text: Not what you've signed up for: Compromising Real-World LLM-Integrated...
   Link Url: https://arxiv.org/abs/2302.12173
   Licence (team record): arXiv non-exclusive distribution licence 1.0 | from: S, T
114.
   Link Text: Defending Against Indirect Prompt Injection Attacks With Spotlighting
   Link Url: https://arxiv.org/abs/2403.14720
   Licence (team record): CC BY 4.0 | from: S, T
115.
   Link Text: Thinking (Ollama docs)
   Link Url: https://docs.ollama.com/capabilities/thinking
   Licence (team record): terms not stated on the page | from: S, T
116.
   Link Text: Extended thinking (Claude API docs)
   Link Url: https://platform.claude.com/docs/en/build-with-claude/extended-thinking
   Licence (team record): terms not stated on the page | from: S, T
117.
   Link Text: FActScore: Fine-grained Atomic Evaluation of Factual Precision in Long Form...
   Link Url: https://arxiv.org/abs/2305.14251
   Licence (team record): arXiv non-exclusive distribution licence 1.0 | from: S, T
118.
   Link Text: How we built our multi-agent research system
   Link Url: https://www.anthropic.com/engineering/multi-agent-research-system
   Licence (team record): terms not stated on the page | from: S, T
119.
   Link Text: Full list of all sources with licences (project repository)
   Link Url: https://github.com/choidol0208/NASA_RAPID/blob/main/compliance/SOURCES.md
   Licence (team record): Apache-2.0 (repository) | from: repo path compliance/SOURCES.md

119 pairs.

## 9. The two confirmation boxes

- Agree to Terms and Conditions: the team can tick it once the person who submits has read the Project Submission Guide and the Participant Terms and Conditions. Check first: every linked page is in English (the repository keeps Korean query words that the ranking accepts, each with an English gloss, by the lead's decision of 14 November).
- Confirm All Work is Original: true for what the team made with the AI tools listed in section 6, and every outside resource is in the two lists through their last pair (the full source list). Check first, from the "Open points" of `docs/submission/submission_text.md`: (1) five NIST-JANAF table files (copyright U.S. Secretary of Commerce) were removed from the repository but remain in its git history (commit 6202f9a); decide whether that is acceptable; (2) the page quotes short attributed passages from 64 reference documents (count at commit bd0b075) (at most 25 words from a non-NASA document); decide whether short quotes are acceptable; (3) three NASA quotes in `pipeline/spec/references.json` are longer than 40 words; (4) the terms of 32 reference entries and of the Exa tool are not recorded in the source log.

## 10. Checklist for the person who submits

1. Turn the Lock switch on.
2. Paste in the form's order: Project Name, Summary, Project Demonstration, Project, Project Details; tick the SI options; add the NASA Data pairs, then the Other Data pairs (first 12 of each, then the last pair, then the rest as time allows).
3. Press Save Progress.
4. Log out of the Space Apps site, or open a private window, open the team's public project page there, and click both links (Project Demonstration and Project) to see that each opens without a login.
5. Tick the two confirmation boxes once their checks above are done.
6. Press Submit for Judging (the team's plan: 19:00 KST; the official deadline is 23:59 KST, and the organisers recommend 23:55).
7. See the status "Project Submitted for Judging". Any later change needs a new Submit for Judging before the deadline.

## Markers left

- None left: the assistant's values are filled from `data/insights/assistant_eval.json`.
