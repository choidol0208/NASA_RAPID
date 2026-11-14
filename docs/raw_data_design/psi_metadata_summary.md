*AI-generated: written with an AI assistant (Claude Code, pm role) and by code that assistant wrote, from PSI metadata archives fetched on 15 November 2026 (KST); checked by AI sessions (a second and a third session re-parsed all 24 archives from the same bytes); a person: none yet.*

# What PSI's own metadata archives hold, for the 24 combustion investigations

Step 10 of `docs/raw_data_design/design.md`. The per-file table is `psi_metadata_fields.csv` in this folder (72 rows: one per investigation and inner file, plus one row per investigation for the assay file that is not there). All counts are the team's computation from NASA's files, not NASA's conclusions.

## Method

1. For each of the 24 investigations, the PSI file listing was requested (POST `https://psi.nasa.gov/geode-py/ws/files/v2`, with the investigation version from `data/psi/manifest.json`). Code picked every file under the `metadata/` folder (PSI category "Investigation Metadata Files"): exactly one `.zip` per investigation and no other file. The 24 archives total 302,059 bytes in the listing, the same figure as the design's inventory.
2. Each archive was fetched whole through its signed address (`.../studies/PSI-<n>/download?file=<name>&version=<v>&redirect=false`). The bytes received equal the listing size for 24 of 24. The SHA-256 of each archive is in the CSV.
3. Code unpacked each archive and read every inner file as ISA-Tab (tab-separated; records end with CR LF). For the investigation file it counted the records and cells and marked a field as filled when any cell after the label is non-empty. For the study and assay files it compared every data cell with the placeholder text. Only field names are written out; no value of a contact field is copied. In the CSV, `rows` counts records with the header line included; `per_test_content` is `absent` for every investigation file because that file has no row per test or sample by its format, and `absent` for the assay row because no assay file exists.

## Result

| What | Count |
|---|---|
| Archives found, fetched and unpacked | 24 of 24 |
| Inner files per archive | 2: `i_Investigation.txt` and `s_PSI-<n>.txt` (24 of 24); no assay file and no other file in any archive |
| Study file (per test or sample): real rows | 0 of 24 |
| Study file: placeholder | **24 of 24**, byte-identical (56 bytes, one header line and one data line) |
| Assay file: absent; `Study Assay File Name` empty | 24 of 24 |
| Sections `STUDY FACTORS`, `STUDY ASSAYS`, `STUDY PROTOCOLS` empty | 24 of 24 |
| Section `INVESTIGATION` (identifier, title, description, dates) empty | 24 of 24 (the investigation is described in the `STUDY` section instead) |
| Investigation file fields filled | 32 to 46 of 111 to 113 per investigation |
| Filled in all 24 | study identifier, title and dates, study file name, DOI, objective, approach, hypothesis, research impacts, research area, managing centre, design keywords (`Study Design Type`), study contacts |

`Study File Name` names the study file inside the same archive in 24 of 24.

## One field read for its value: where the experiment flew

Added at about 01:40 KST on 15 November by the correcting session, from the same archive bytes. The field `Comment[Flight Platform]` of `i_Investigation.txt` is filled in 21 of the 24 archives (empty for PSI-60, PSI-62 and PSI-117). It is not a contact field; its values, as written:

| Value as written | Investigations |
|---|---|
| `International Space Station (ISS)` | 18: PSI-10, 20, 21, 22, 23, 25, 26, 39, 47, 68, 69, 98, 100, 101, 102, 106, 107, 159 |
| `Cygnus Spacecraft` | 1: PSI-99 |
| `Not Applicable` | 2: PSI-115, PSI-142 |

For the 12 investigations whose tables the team mapped (PSI-10, 25, 26, 39, 69, 98, 99, 100, 101, 102, 107, 159) the field reads `International Space Station (ISS)` for 11 and `Cygnus Spacecraft` for PSI-99. The field names a platform, not a gravity level. It is printed as written: for PSI-98 and PSI-100 it reads `International Space Station (ISS)`, while the field `Comment[Experiment Hardware]` of the same records reads `Saffire 1 enclosure in Cygnus` and `Saffire III enclosure in Cygnus`. Use: the document behind the team's constant "microgravity" for the 14 mapped tables (`pile_wording.md` section 5.1).

## Three examples, as written in NASA's files

1. `PSI-69_metadata_PSI-133_FLEX.zip`, file `s_PSI-69.txt`, whole file (tab shown as →): `Source Name → Sample Name` / `Do not use this → Do not use this`. The same two lines are the whole study file of all 24 investigations.
2. `PSI-159_metadata_PSI-159-ISA.zip`, file `i_Investigation.txt`: the line `Study Assay File Name` and the line `Study Factor Name` carry a label and no value.
3. `PSI-69_metadata_PSI-133_FLEX.zip`, file `i_Investigation.txt`: `Study Design Type` lists keywords for the whole investigation (`FLEX`, `Fuel Sooting`, `Droplet`, `Spacecraft Fire Safety`, `Diffusion Flames`, `Flames`), not tests.

## What this means for a user who wants to know which raw file belongs to which test

ISA-Tab gives the study file the subjects and samples studied, and lets an assay file point to the raw and derived data files (ISA-Tab specification, sections 2.3.6 and 2.3.7, https://isa-specs.readthedocs.io/en/latest/isatab.html). In the 24 archives read, those two places hold one placeholder line and nothing, respectively. PSI's machine-readable description ends at the investigation: it says what the investigation is about, who ran it and where it was published. Its per-sample layer holds one placeholder row and it has no assay file, so no structured field names a test or a raw data file; whether the free-text fields mention single tests was not checked.

So the link from a raw file to a test cannot be read from the structured fields of PSI's metadata. It has to be built from what NASA wrote elsewhere: identifiers in file names, PSI folder names, per-test sheets inside the archive, and the experimental tables. That is link 4 of the design's chain (a link counts as agreed only when two labels name the same test). Claim 7 of the design can now read: "In all 24 PSI metadata archives of the combustion investigations, the per-test study file is a placeholder row; none has an assay file."

## Limits: what was not opened or not judged

- The free-text values of the filled fields (objective, approach, hypothesis and others) were not read for content; the CSV says only whether a field is filled. Whether a free-text field mentions tests was not checked. One field was read for its value, Flight Platform (section above).
- Only the current version of each archive was fetched. Earlier versions in PSI were not requested.
- The investigation pages' JSON (`/repo/investigations/PSI-<n>`) was not compared with the ISA-Tab fields.
- No raw data, no other archive and no document was opened in this step.
- Who checked: AI sessions. The first wrote and ran the code. A second session re-parsed all 24 archives from the same bytes with its own code: the SHA-256 of each archive equals the CSV in 24 of 24, the study file is the placeholder in 24 of 24, and no archive has an assay file. A third session repeated that recount with separate code (same results; fields filled, fields in all and records equal the CSV in 24 of 24) and read the Flight Platform field. The design's check for this step asks a second session to re-read five archives: it is met for the parsing, and a fresh re-fetch of five archives from PSI has not run. A person: none yet. Review by combustion researchers is a next step.

This is a research exploration tool, not safety guidance; nothing here predicts untested conditions.

**Transfer of this step:** 24 listings 30,609,224 bytes (one more attempt for PSI-10 broke off after 64,440 bytes and was repeated), 24 signing calls 43,989 bytes, 24 archives 302,059 bytes; plus 119,699 bytes to read the ISA-Tab specification page. Working files: the pm session's scratch folder `pmpart/` (code, listings, archives, unpacked files, `transfer_log.jsonl`), not in the repository.
