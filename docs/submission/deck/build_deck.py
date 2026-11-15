# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""Build the seven-slide deck of Fire Evidence Explorer.

    python3 docs/submission/deck/build_deck.py            # numbers.json, slides.html, speaker_notes.md
    python3 docs/submission/deck/build_deck.py --pdf      # the same, then ../slides.pdf and preview/
    bash docs/submission/deck/refresh.sh                  # retake the captures of the page, then --pdf

What it does
  (a) reads every number shown on a slide from the repository's files and writes each one,
      with its source file and the way it was computed, to numbers.json;
  (b) stops with an error when a number it needs cannot be computed, when two files that
      should agree do not, or when a capture shows other values than the files (or was taken
      under another scoring config than the repository's);
  (c) renders slides.html: one page, 7 slides of 1920 x 1080 CSS pixels, inline CSS, inline
      SVG charts, captures referenced from img/;
  (d) writes speaker_notes.md: one note per slide, 60 words or fewer, with the same numbers.

Standard library only. Needs Node.js 18 or later on the PATH for one check
(web/parity_check.py). It calls no language model.
Fonts and network: the deck uses the page's own two fonts (Barlow Semi Condensed for headings
and numbers, Atkinson Hyperlegible for text; SIL Open Font License, logged in
compliance/SOURCES.md), loaded with the Google Fonts <link> that web/index.html uses, which
this script copies from that file. slides.html therefore needs the network for its fonts (the
system font stack is only the fallback); slides.pdf embeds them and is self-contained. With
--pdf, Chrome may reach fonts.googleapis.com and fonts.gstatic.com and no other host, and the
build stops if the PDF embeds any other font than those two families.
It writes only numbers.json, slides.html, speaker_notes.md and the crops of the captures
(img/crop/: each slide's part of a capture, cut out so that the PDF holds nothing else), next to this file; with
--pdf also ../slides.pdf and preview/slide-N.png (needs Google Chrome).

The things a person edits are near the top: TEAM_NAME, ASSISTANT_MEASURED and the block
WORDING. The recorded assistant answer of slide 6 is chosen in capture.mjs
(RECORDED_CONVERSATION, RECORDED_TURN).
"""
import csv
import datetime
import glob
import hashlib
import html
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import zlib

sys.dont_write_bytecode = True  # importing scoring/ must not write __pycache__ outside this folder

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

# ======================================================================================
# 1. THE TWO CONSTANTS A PERSON FILLS
# ======================================================================================

# The team's name as registered on the Space Apps team page. While it is None, slide 1
# shows a visible placeholder chip "[team name]".
# "RAPID": docs/submission/slides_outline.md, Open point 1 (given by the human lead on
# 15 November 2026, 15:15 KST, as recorded there). Set it back to None to show the chip.
TEAM_NAME = "RAPID"

# Measured results of the conversational assistant. Fill them from
# data/insights/assistant_eval.json after the evaluation has run; never by estimate.
# While any value is None, the deck shows a visible chip "to be measured" in its place,
# slide 6 takes the title WORDING["s6"]["title_unmeasured"], and box 3 says
# "measurement in progress".
def _assistant_measured():
    """The assistant's measured values, read from data/insights/assistant_eval.json when it exists
    (written by python3 -m ai.assistant.evaluate); None values while it does not."""
    import json as _json, os as _os
    f = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "..", "..", "data", "insights", "assistant_eval.json")
    if not _os.path.exists(f):
        return {"correct_full_pipeline": None, "questions_in_set": None, "correct_single_call": None}
    with open(f, encoding="utf-8") as fh:
        d = _json.load(fh)
    full, one = d["arms"]["full"]["metrics"], d["arms"]["single_call"]["metrics"]
    pct = lambda m: f"{round(100 * m['reading_accuracy']['overall'])}%"
    return {
        "correct_full_pipeline": pct(full),                 # share of the scored fields of the request read correctly
        "questions_in_set": str(d["n_questions"]),
        "correct_single_call": pct(one),
        "numbers_full": str(full["numbers_unsupported"]["count"]), "numbers_single": str(one["numbers_unsupported"]["count"]),
        "wording_full": str(full["forbidden_wording"]), "wording_single": str(one["forbidden_wording"]),
    }


ASSISTANT_MEASURED = _assistant_measured()

# The check of the video reader (frames compared by an AI session) is stated in
# video/README.md; its per-frame sheet is not in the repository, so the figure cannot be
# recounted. True: the slide shows it with the visible tag "stated in video/README.md, not
# recounted". False: box 4 shows the clips and rows only.
# False since 15 November 2026: the outline (Open point 6) keeps the figure only once the team
# lead has resolved the "not recounted" label, which has not happened.
VIDEO_FRAME_CHECK_ON_SLIDE = False

# The team's logo: lockup B ("program", the stepped mark and the word RAPID) of the team lead's logo kit,
# the version for light backgrounds, copied unchanged from the kit (outlined SVG, 509 x 172 at 1x, its clear
# space of 28 px at 1x inside the file; the kit's minimum display width for B is 120 px). Shown on slide 1 in
# the team block (in place of the word RAPID, which the lockup carries) and small on slide 7 beside the links.
# None: no logo; slide 1 shows the team name as text and slide 7 shows the links alone. The file is not
# committed until the team lead has said under which terms it goes into the public repository.
TEAM_LOGO = None   # the human lead decided on 15 November (17:40 KST) to submit without the team logo
TEAM_LOGO_SIZE = (509, 171.99)     # the SVG's viewBox, used for the aspect ratio
TEAM_LOGO_MIN_WIDTH = 120          # the kit's minimum display width for lockup B, CSS px

PUBLIC_URL = "https://choidol0208.github.io/NASA_RAPID/"
METHOD_URL = PUBLIC_URL + "how.html"
AI_MARK = "Built with AI assistance (Claude)"

# The quoted result shown as the example on slide 4: its id in data/pipeline/results_by_need.json
# ("findings"). The quotation, its conditions, its group and its source are read from that file.
QUOTED_EXAMPLE = "LUCI25.sibal_spread"

# The page's two font families (web/index.html loads them from Google Fonts; SIL Open Font
# License, logged in compliance/SOURCES.md). The PDF must embed these and no other font.
PAGE_FONTS = ("Atkinson Hyperlegible", "Barlow Semi Condensed")
FONT_HOSTS = ("fonts.googleapis.com", "fonts.gstatic.com")

# ======================================================================================
# 2. WORDING  (edit the words here; {names} are filled with values computed from files)
#    **text** is set in bold. No number that comes from a file is typed here.
# ======================================================================================
WORDING = {
    "s1": {
        "kicker": "NASA Space Apps Challenge 2026 · Challenge: Flame in Freefall",
        "title": "Fire Evidence Explorer shows which NASA fire tests fit what you build, and where their evidence stops.",
        "product_label": "Product",
        "product": "Fire Evidence Explorer",
        "team_label": "Team",
        "team_placeholder": "[team name]",
        "logo_alt": "Team {team} logo: a stepped mark and the word RAPID",
        "lead": "Type what you build and where; see the closest NASA investigations and where the evidence stops. Example finding: for a lunar habitat ({o2}% oxygen or more and {kpa} kPa or less), PSI holds no counted fire test, and solid-fuel tests end at {solid_o2}% oxygen.",
        "link_label": "Public page, opens without a login",
        "link_hint": "Try the example \"{example_button}\".",
        "caption": "Capture of the team's own page, {capture_date}, one line quoting the challenge hidden; not AI-generated.",
        "caption_dashboard": "The dashboard for \"{example_button}\": the input as read, three key figures, five tabs. Capture of the team's own page, {capture_date}; not AI-generated.",
        "alt_dashboard": "The dashboard of Fire Evidence Explorer for the example lunar habitat cotton fabric: the request and how it was read, three key figures, a note on gravity, five tabs each with a one-line description, and the first result",
        "footer": "Research exploration tool built on NASA PSI data. Match scores and counts are Team RAPID's computation from NASA PSI data.",
        "note": "We are {team}. NASA publishes its microgravity fire experiments as open data, but a designer cannot easily find, compare or interpret them. Our page starts from what you want to build. It finds the closest NASA investigations, shows what their recorded tests hold and where the data are, and says where the evidence stops.",
    },
    "s2": {
        "kicker": "The data · NASA's PSI archive",
        "title": "NASA's combustion archive holds {archive_tb} TB in {archive_files} files; its experimental tables are {exp_files} small files.",
        "left_head": "NASA PSI (Physical Sciences Informatics): combustion",
        "left_stats": [("{archive_tb} TB", "listed"), ("{archive_files}", "files"), ("{investigations}", "investigations")],
        "right_head": "Its experimental tables, the files that list tests",
        "right_stats": [("{exp_mb} MB", "in all"), ("{exp_files}", "files"), ("{tables_read}", "read into tests"), ("{tests}", "tests in them")],
        "bar1_head": "Bytes by kind of file",
        "bar1_total": "{archive_tb} TB, file listing of {listing_date}",
        "bar1_archive": "Zip archives {pct_archive}%",
        "bar1_video": "Video {pct_video}%",
        "bar1_other": "All other kinds {pct_other}%; the {exp_files} experimental tables ({exp_mb} MB) are in here",
        "bar2_head": "Files by what the name carries",
        "bar2_total": "{archive_files} files",
        "bar2_test": ("{name_test}", "name a test"),
        "bar2_day": ("{name_day}", "name a test day or session"),
        "bar2_none": ("{name_none}", "name neither"),
        "rest": "Outside the {exp_files} tables, only a file's name ties it to a test or a test day; {name_none} names carry neither.",
        "caption": "By file name and PSI category; no file opened. Team RAPID's computation from NASA PSI data.",
        "footer": "Source: NASA PSI file listing, {listing_date}.",
        "note": "NASA's PSI archive lists {archive_tb} terabytes for {investigations} combustion investigations. Almost all of it is zip archives and video. The tables that list tests are {exp_files} small files; we read {tables_read} of them into {tests} tests. For everything else, the only link to a test is the NASA identifier or the test number in a file name.",
    },
    "s3": {
        "kicker": "Find · the closest investigations, a worked example",
        "title": "For cotton fabric in a lunar habitat, rules show {top1} and {top2} closest, and {top3} as the closest tested at {o2}% oxygen, and say why.",
        "input_head": "You type",
        "input_value": "lunar habitat cotton fabric",
        "input_hint": "or press the example \"{example_button}\"",
        "read_head": "The page reads it as (all shown and editable)",
        "read_rows": [
            ("Preset", "oxygen {o2}%, pressure {kpa} kPa ({psi} psi), airflow {flow}"),
            ("Your words", "{gravity} gravity; {material} {fuel_class}: a {fuel_phase} that {melt}, a {regime} {shape}"),
            ("Default", "purpose \"{concern}\""),
        ],
        "rank_head": "Closest of {investigations} investigations",
        "rank_note_team": "{score_label} 0 to 100, for this question only",              # when the page's label names the team ("team score")
        "rank_note_other": "team's {score_label} 0 to 100, for this question only",   # for any other label of the page ("match score")
        "why": "Why:",
        "gap": "Largest gap:",
        "tag3": "Tagged \"{tag3}\".",
        "rule": "**Third place:** when your oxygen is not air and none of the top {results_word} was tested at it, third place goes to the best result that was. {top3} is {rank3_ordinal} by score.",
        "consider_head": "Points to consider",
        "consider": [
            "**Gravity:** none of the {results_word} meets {gravity} gravity; every PSI test ran in microgravity (near-weightlessness).",
            "**Oxygen and pressure:** no counted test at {o2}% oxygen or more and {kpa} kPa ({psi} psi) or less (slide 4). The Saffire fabrics were tested below {o2}% oxygen, at a pressure the team assumed (unverified); {top3}'s oxygen is met, its pressure documented in its record.",
            "**Airflow:** the Saffire runs are near a ventilated cabin; {top3}'s is not.",
            "**Fuel:** the Saffire fabric matches; {top3} burns gas.",
        ],
        "shot_alt": "Head of result card {n} of the page for lunar habitat cotton fabric: {name}, {label} {score}, and its closest test configuration",
        "footer": "Match scores and order are Team RAPID's computation from NASA PSI data. Card heads: captures of the team's own page (config {config_version}), {capture_date}; not AI-generated.",
        "note": "Type lunar habitat cotton fabric. The preset fills {o2} percent oxygen and {kpa} kilopascals; your words give lunar gravity and the fabric. Rules, not a language model, compare it with {configs} test configurations. Two Saffire fabric tests lead; {top3} follows, tested at your oxygen. A query without a material ranks without a fuel comparison, and the page says so.",
    },
    "s4": {
        "kicker": "Compare · counted tests, question by question",
        "title": "A lunar habitat has counted tests for {lunar_needs_word} of {needs_word} fire-safety questions; the ISS cabin has {iss_needs_word}.",
        "table_head": "Counted tests in the environment's range",
        "col_question": "Fire-safety question",
        "col_iss": "ISS cabin",
        "col_lunar": "Lunar habitat",
        "oxygen_only": "oxygen only",
        "mixed_both": "{n} oxygen and pressure",
        "mixed_oxygen": "{n} oxygen only",
        "both": "oxygen and pressure",
        "callout": "Lunar habitat at {o2}% oxygen or more and {kpa} kPa ({psi} psi) or less: **[[no counted test.]]**",
        "sub": "All {s1_tests} in its column are just above {kpa} kPa: fuel droplets at [[{s1_pmin} to {s1_pmax} kPa]], inside the team's counting range, not inside the habitat's bound.",
        "col_range_iss": "{iss_o2_range} oxygen, {iss_p_range}",
        "col_range_lunar": "{lunar_o2_range} oxygen, {lunar_p_range}",
        "legend_both": "Oxygen and pressure in range",
        "legend_oxygen": "Oxygen only: the test's oxygen is in range and NASA's table records no pressure for it",
        "legend_zero": "No counted test in the range",
        "ranges": "Ranges under each column: the team's bins for counting.",
        "subtitle": "A counted test is a recorded test whose investigators or a NASA document state that purpose.",
        "definition": "The {needs_word} questions are Team RAPID's draft from NASA and standards documents.",
        "quoted_head": "Quoted first, per question",
        "quoted": "**{q_results}** results quoted from NASA documents and the investigators' papers, **{q_values}** with printed values; for the lunar habitat, **{q_lunar_at}** state its oxygen and pressure, **{q_lunar_about}** one of its conditions.",
        "quoted2": "Example, {q_need}: {q_quote} ({q_material}, simulated {q_gravity} gravity, {q_pressure_words}; LUCI slides, NTRS {q_ntrs}; a related NASA experiment, quoted, nothing computed from it).",
        "footer": "Counts are Team RAPID's computation from NASA PSI tables. Quoted results in their authors' words; their order is the team's fixed rule, with no weights. Every test ran in microgravity; the page does not treat that as a bound for lunar gravity (slide 7).",
        "note": "Compared by counted tests, not by scores. A test counts for a question only if its investigators or a NASA document state that purpose. ISS cabin: {iss_needs_word} of {needs_word} questions, {iss_oxygen_only_word} on oxygen alone, as their tables record no pressure. Lunar habitat: {lunar_needs_word}, from {s1_tests} droplet tests just above {kpa} kilopascals. Ignition and smoke: no counted test in either.",
    },
    "s5": {
        "kicker": "Locate · where the data are, example: lunar habitat",
        "title": "For each question, the page shows where the data are: NASA's tables, the archive, or no record.",
        "pile1_head": "In NASA's tables",
        "pile1_question": "Extinction conditions",
        "pile1_unit": "counted droplet tests",
        "pile1_text": "Fuel droplets at [[{s1_pmin} to {s1_pmax} kPa]]: inside the team's range ({lunar_p_range}), above the {kpa} kPa ({psi} psi) bound.",
        "strip_p_band": "{s1_tests} counted tests",
        "strip_p_marker": "habitat: {kpa} kPa or less",
        "strip_p_axis": "pressure, kPa",
        "pile2_head": "In the archive, not in a table",
        "pile2_question": "The {inside_tests} tests inside the ranges ({s1_tests} counted, {inside_not_counted} recorded but not counted)",
        "pile2_unit": "files",
        "pile2_text": "({files_gb} GB, {files_pct}% of the bytes) carry the NASA identifier or the test number of one of these tests in their name.",
        "pile2_text_agree": "**Two labels agree** for {files_agree}: two of the file's name, its folder and a sheet's printed test number name the same test.",
        "pile2_text2": "Values in the {sheets} test sheets: read from NASA's file, not adopted, not counted.",
        "pile3_head": "No record in PSI",
        "pile3_head_tail": "(listing of {listing_date})",
        "pile3_question": "Flammability limit",
        "pile3_unit": "counted tests inside the ranges",
        "pile3_text": "All {p1_tests} counted tests have oxygen [[{p1_o2min} to {p1_o2max}%]] in NASA's table.",
        "pile3_small": "This gap is not unprocessed data: PSI's tables hold no counted test of this question inside these ranges (listing of {listing_date}).",
        "strip_band": "{p1_tests} counted tests",
        "strip_marker": "habitat: {o2}% or more",
        "strip_axis": "oxygen, %",
        "shot_head": "On the page",
        "shot_line": "The tab \"Where the data are\" shows these three piles for each question.",
        "strip_head": "Tied by name; only zip directories fetched",
        "strip1_head": "Videos:",
        "strip1": "{videos} ({videos_gb} GB); two labels agree for {videos_agree}.",
        "strip2_head": "Archives:",
        "strip2": "directories of {archives} of {archives_in_listing} zip archives read; {fetched_gb} GB fetched for {archives_tb} TB.",
        "footer": "Counts are Team RAPID's computation from PSI's file listing and NASA's tables.",
        "note": "The page sorts each question's data into three piles. Code follows NASA's identifiers in file and folder names, without downloading the files; a link counts only where two labels agree. Videos are tied the same way. For the lunar habitat, the flammability gap is not unprocessed data: every counted test has its oxygen in NASA's table, below {o2} percent.",
    },
    "s6": {
        "kicker": "SI · where it is used, and how it is checked",
        "title_measured": "SI with a measured check; code for every number.",
        "title_unmeasured": "Four uses of SI and how each is checked",
        "subtitle": "SI is the challenge's word for AI. Code computes every count and rank; the public page runs no model.",
        "col_use": "Use",
        "col_check": "Its check",
        "boxes": [
            {
                "name": "Rule-based ranking",
                "tag": "plain code, not SI",
                "does": "Rules score {configs} test configurations against your input, with fixed weights per question type.",
                "check": "**{val_pass} of {val_total}** test scenarios pass (expected answers written by an AI session). The page's scorer equals Python on **{par_ok} of {par_total}** queries.",
            },
            {
                "name": "Local language model",
                "tag": "card summaries",
                "does": "It wrote sentences that each cite NASA sentences.",
                "check": "**{proposed}** sentences written; code gates and AI reviews removed **{removed}**; **{shown}** shown, labelled \"AI-generated\".",
            },
            {
                "name": "Conversational assistant",
                "tag": "prototype, measured",
                "does": "understand → plan → look up → write → check → deliver",
                "does_note": "Small model steps with code checks between them; it looks up counts, tests and quoted results.",
                "check_measured": "**{a_set}** questions: request read correctly **{a_full}** (one model call **{a_single}**); numbers outside the cited facts **{a_num_full}** (one call **{a_num_single}**).",
                "check_unmeasured": "{a_chip}",
            },
            {
                "name": "Video reader",
                "tag": "",
                "does": "It copies the numbers NASA's video shows on screen.",
                "check": "**{clips}** BASS-II clips, **{video_rows}** rows copied from NASA's on-screen display. Flame timing failed; removed.",
                "check_with_frames": "**{clips}** BASS-II clips, **{video_rows}** rows copied from NASA's on-screen display; none wrong in **{frames}** frames checked by an AI session {not_recounted_tag}. Flame timing failed; removed.",
                "not_recounted_tag": "stated in video/README.md, not recounted",
            },
        ],
        "placeholder": "to be measured",
        "placeholder_all": "Measured results: in progress",
        "model_head": "Model",
        "model": "OpenAI gpt-oss:20b (Apache-2.0), run locally through Ollama; no paid API; the public page runs no model.",
        "shot_head": "One recorded answer, replayed on the page",
        "live_head": "A conversation on the local install",
        "live_alt_user": "The request typed into the assistant: lunar habitat cotton fabric",
        "live_alt_read": "How the request was read: each value is a button that changes it",
        "live_alt_answer": "The assistant's answer with citation numbers and the label that a local language model wrote it",
        "live_alt_form": "The box for a follow-up question, with the name of the connected model",
        "live_alt_whole": "The whole card of one conversation with the assistant: the request, six steps with what each did, how the request was read with each value as a button, the answer with citation numbers and its label, folds for what the checks removed and for the facts, suggested next questions, and the box for a follow-up",
        "live_cap": "The whole answer card on the local install, {capture_date}. Capture of the team's own page, not AI-generated; its sentences are by the local model or, where tagged, team code.",
        "shot_alt_question": "The question of the recorded turn as the page shows it",
        "shot_alt": "The recorded answer of the conversational assistant as the page replays it: two sentences with their citation numbers, the label that it was recorded with the local model, and the line of the checks",
        "shot_cap": "The steps and the panels of the answer are not shown. Captures of the team's own page, {capture_date}; the picture is not AI-generated, the two sentences in it were written by the local model after a clarifying question (\"Which environment is this for?\").",
        "note_measured": "We use SI only where a check can measure it. Rules rank; no model touches a number. One local open-weight model wrote card sentences; code gates and AI reviews removed {removed} of {proposed}. The assistant chains small model steps with code checks between them. The video reader copies NASA's on-screen numbers; its flame timing failed, so we dropped it.",
        "note_unmeasured": "We use SI in four places, each with a check. Rules rank; no model touches a number. One local open-weight model wrote card sentences; gates and AI reviews removed {removed} of {proposed}. The assistant chains small model steps with code checks; its measurement is in progress. The video reader copies NASA's on-screen numbers; its flame timing failed and was dropped.",
        "footer": "Code written with Claude Code (Anthropic); every file says so. Model sentences reviewed by a second AI session: {reviewed_ai} of {proposed} (those left after code gates and a first reading).",
    },
    "s7": {
        "kicker": "Limits · and what comes next",
        "title": "The page says where the evidence stops; review by combustion researchers comes next.",
        "limits_head": "Limits",
        "limits": "Every test ran in microgravity; no prediction outside the recorded tests is offered; counts and rankings are Team RAPID's computation from NASA PSI data. Checked by code and AI sessions.",
        "gravity_head": "Gravity",
        "gravity": "The challenge suggests that the two ends of the gravity scale could bound partial gravity. We do not treat them as bounds: NASA drop-tower tests found lower oxygen limits at lunar gravity than at both 0 g and 1 g, for all {of_materials_word} materials tested ({of_cite}).",
        "model_head": "Enough for a model?",
        "model": "{labels_pass} of {labels} outcome labels in NASA's tables gives a first sign that a simple model beats guessing; no model shipped.",
        "next_head": "Next",
        "next": ["Review by combustion researchers", "A person's spot check of file links", "A re-measurement of the assistant"],
        "caption_read": "Recorded tests by oxygen, all pressures; solid fuels end at {solid_o2}%. Gas-flame tests at {o2}% or more are recorded, none counted at {kpa} kPa or less (slide 4). Squares: Saffire flight samples from a paper, not in PSI, not counted. Numbered dashed lines: cited atmospheres (listed on the page).",
        "link_label": "Public page, opens without a login",
        "method_label": "Method: how AI is used and checked, how the score works",
        "footer": "Research exploration tool built on NASA PSI data. References: the NASA PSI dataset DOI on every result; the full list is on the project page. Map: Team RAPID's plot from NASA PSI tables, a capture of the team's own page ({capture_date}); not AI-generated.",
        "note": "A research exploration tool built on NASA PSI data. Every test here ran in microgravity. The challenge suggests the two ends of the gravity scale could bound partial gravity; NASA drop-tower tests found lower oxygen limits at lunar gravity than at both, so we do not treat them as bounds. Next: review by combustion researchers and re-measuring the assistant.",
    },
}

# ======================================================================================
# 3. NUMBERS: read from the repository's files, cross-checked, and recorded with their source
# ======================================================================================

class BuildError(SystemExit):
    pass


def fail(msg):
    raise BuildError("build_deck.py: CANNOT BUILD. " + msg)


def need(cond, msg):
    if not cond:
        fail(msg)


def path(rel):
    p = os.path.join(ROOT, rel)
    need(os.path.exists(p), f"File not found: {rel}")
    return p


def read_json(rel):
    with open(path(rel), encoding="utf-8") as fh:
        return json.load(fh)


def read_csv(rel):
    with open(path(rel), newline="", encoding="utf-8") as fh:
        lines = [ln for ln in fh if not ln.startswith("#")]
    rows = list(csv.DictReader(lines))
    need(rows, f"No rows in {rel}")
    return rows


def fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def fi(n):
    return f"{int(n):,}"


WORDS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve"]


def word(n):
    need(0 <= n < len(WORDS), f"No number word for {n}")
    return WORDS[n]


def long_date(iso):
    d = datetime.datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return f"{d.day} {d.strftime('%B %Y')}"


NUMBERS = {}   # key -> {value, shown_as, slides, source, how}
CHECKS = []    # cross-checks that passed
V = {}         # key -> the text put on a slide
CAP = {}       # file name -> its entry in img/captures.json (boxes, check, time, scoring config)

ORDINALS = ["zeroth", "first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth", "eleventh", "twelfth"]


def ordinal(n):
    need(0 <= n < len(ORDINALS), f"No ordinal word for {n}")
    return ORDINALS[n]


def plain_reason(text):
    """A reason line of the scorer ('why', 'main_gap') in the slide's words. Nothing is added: 'O2' is written
    'oxygen', a range dash 'to', the dimension word that opens a bracket is left out ('(fuel SIBAL ...' -> '(SIBAL ...'),
    an inner bracket becomes a comma, and the scorer's token for a missing regime is dropped."""
    parts, depth, cur = [], 0, ""
    for ch in text:
        depth += ch == "("
        depth -= ch == ")"
        if ch == ";" and depth == 0:
            parts.append(cur.strip())
            cur = ""
        else:
            cur += ch
    parts.append(cur.strip())
    out = []
    for part in parts:
        m = re.fullmatch(r"(.+?) \((.*)\)", part)
        need(m, f"The scorer's reason line has a form this script does not know: '{part}'")
        head, body = m.group(1), m.group(2)
        body = re.sub(r"^(?:fuel|flow|O2|pressure|sample shape|purpose|diluent) ", "", body)
        body = body.replace(" (regime n/a)", "")
        body = re.sub(r" \(([^()]*)\)", r", \1", body)
        need("(" not in body and ")" not in body, f"The scorer's reason line has a bracket this script does not know: '{part}'")
        out.append(f"{head} ({body})".replace("O2", "oxygen").replace("\u2013", " to ").replace("_", " "))
    return "; ".join(out)


def put(key, value, shown, slides, source, how):
    NUMBERS[key] = {"value": value, "shown_as": shown, "slides": slides, "source": source, "how": how}
    V[key] = shown


def checked(text):
    CHECKS.append(text)


def run_check(args, pattern, what):
    """Run one of the repository's own checks (read-only) and read its result line."""
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    try:
        out = subprocess.run([sys.executable, "-B"] + args, cwd=ROOT, env=env, capture_output=True, text=True, timeout=600)
    except Exception as ex:  # noqa: BLE001
        fail(f"{what}: could not run ({type(ex).__name__}: {ex})")
    m = re.search(pattern, out.stdout)
    need(m, f"{what}: result line not found (exit {out.returncode}). stderr: {out.stderr.strip()[-400:]}")
    need(out.returncode == 0, f"{what}: the check itself failed (exit {out.returncode}): {m.group(0)}")
    return int(m.group(1)), int(m.group(2))


def compute():
    # ---- the archive (slides 1, 2, 5) -------------------------------------------------
    inv = read_json("data/pipeline/raw_inventory.json")
    tot = inv["_meta"]["totals"]
    kinds = tot["by_kind"]
    groups = read_csv("data/pipeline/raw_file_groups.csv")
    layers = read_json("data/pipeline/raw_layers_summary.json")["overall"]
    catalog = read_csv("data/catalog/investigations.csv")

    need(tot["investigations"] == len(inv["investigations"]) == len(catalog),
         "The number of investigations differs between raw_inventory.json and data/catalog/investigations.csv")
    put("investigations", tot["investigations"], fi(tot["investigations"]), [2, 3],
        "data/pipeline/raw_inventory.json; data/catalog/investigations.csv",
        "_meta.totals.investigations; equal to the investigations listed and to the rows of the catalog")

    files, nbytes = tot["files"], tot["bytes"]
    need(sum(int(g["files"]) for g in groups) == files == layers["files"],
         "The file total differs between raw_inventory.json, raw_file_groups.csv and raw_layers_summary.json")
    need(sum(k["bytes"] for k in kinds.values()) == nbytes and sum(k["files"] for k in kinds.values()) == files,
         "by_kind does not add up to the totals in raw_inventory.json")
    checked("60,866-style file total equal in raw_inventory.json, raw_file_groups.csv and raw_layers_summary.json; by_kind adds up")
    put("archive_files", files, fi(files), [2], "data/pipeline/raw_inventory.json",
        "_meta.totals.files; equal to the sum of 'files' in raw_file_groups.csv")
    put("archive_tb", nbytes, f"{nbytes / 1e12:.2f}", [2], "data/pipeline/raw_inventory.json",
        "_meta.totals.bytes / 10^12 (decimal terabytes), two decimals")
    put("listing_date", inv["_meta"]["listings_fetched_at"], long_date(inv["_meta"]["listings_fetched_at"]), [2, 5],
        "data/pipeline/raw_inventory.json", "_meta.listings_fetched_at, date part")

    need("archive" in kinds and "video" in kinds and "experimental_table" in kinds, "by_kind lacks archive, video or experimental_table")
    other_kinds = [k for k in kinds if k not in ("archive", "video")]
    other_bytes = sum(kinds[k]["bytes"] for k in other_kinds)
    for key, b, how in (("pct_archive", kinds["archive"]["bytes"], "by_kind.archive.bytes"),
                        ("pct_video", kinds["video"]["bytes"], "by_kind.video.bytes"),
                        ("pct_other", other_bytes, f"bytes of the {len(other_kinds)} other kinds ({', '.join(sorted(other_kinds))})")):
        put(key, b, f"{100 * b / nbytes:.2f}", [2], "data/pipeline/raw_inventory.json", f"{how} / _meta.totals.bytes, in percent, two decimals")
    put("exp_files", kinds["experimental_table"]["files"], fi(kinds["experimental_table"]["files"]), [2],
        "data/pipeline/raw_inventory.json", "_meta.totals.by_kind.experimental_table.files")
    put("exp_mb", kinds["experimental_table"]["bytes"], f"{kinds['experimental_table']['bytes'] / 1e6:.1f}", [2],
        "data/pipeline/raw_inventory.json", "_meta.totals.by_kind.experimental_table.bytes / 10^6, one decimal")

    tests = read_csv("data/pipeline/tests.csv")
    by_id = {t["test_id"]: t for t in tests}
    need(len(by_id) == len(tests), "tests.csv has a repeated test_id")
    put("tests", len(tests), fi(len(tests)), [2], "data/pipeline/tests.csv", "rows")
    put("tables_read", len({t["source_file"] for t in tests}), fi(len({t["source_file"] for t in tests})), [2],
        "data/pipeline/tests.csv", "distinct values of source_file")
    need(all(t["gravity_level"] == "microgravity" for t in tests),
         "A test in tests.csv is not at microgravity: the deck's sentences on gravity no longer hold")
    checked("every row of tests.csv has gravity_level microgravity")

    names = {}
    for key, col, lay in (("name_test", "files_tied_to_a_test", "test"), ("name_day", "files_tied_to_a_day_or_session", "day_or_session"),
                          ("name_none", "files_not_tied", "none")):
        n = sum(int(g[col]) for g in groups)
        need(n == layers["names"][lay]["files"], f"{col} differs between raw_file_groups.csv and raw_layers_summary.json")
        names[key] = n
        put(key, n, fi(n), [2], "data/pipeline/raw_file_groups.csv; data/pipeline/raw_layers_summary.json",
            f"sum of {col}; equal to overall.names.{lay}.files")
    need(sum(names.values()) == files, "The three name classes do not add up to the file total")
    checked("files by name (test, day or session, none) add up to the file total and agree in two files")

    # ---- the six questions, ISS cabin and lunar habitat (slides 1, 4) ----------------------
    sneeds = read_csv("data/pipeline/scenario_needs.csv")
    table = {}
    for sid in ("iss", "lunar_habitat"):
        rows = [r for r in sneeds if r["scenario_id"] == sid]
        need(rows, f"scenario_needs.csv has no rows for {sid}")
        table[sid] = [{"id": r["need_id"], "need": r["need"], "both": int(r["tests_atmosphere"]), "oxygen": int(r["tests_oxygen_only"]),
                       "pressure": int(r["tests_pressure_only"]), "counted": int(r["usable_tests"])} for r in rows]
        for c in table[sid]:
            c["in_range"] = c["both"] + c["oxygen"] + c["pressure"]
            need(c["pressure"] == 0, f"{sid} {c['id']} has tests matched on pressure only: slide 4 has no wording for that case")
    need([c["id"] for c in table["iss"]] == [c["id"] for c in table["lunar_habitat"]], "The two scenarios list different questions")
    oxy_only = sum(1 for c in table["iss"] if c["oxygen"] > 0 and c["both"] == 0)
    put("iss_oxygen_only", oxy_only, fi(oxy_only), ["note 4"], "data/pipeline/scenario_needs.csv",
        "questions of scenario iss whose tests in range all have tests_oxygen_only (no test with oxygen and pressure)")
    V["iss_oxygen_only_word"] = word(oxy_only)
    for sid in ("iss", "lunar_habitat"):
        for c in table[sid]:
            if c["id"] in ("P2", "D2"):
                need(c["in_range"] == 0 and c["counted"] == 0 and c["need"].split()[0] in ("Ignition", "Smoke"),
                     "Ignition or smoke now has a counted test: reword the speaker note of slide 4")
    n_needs = len(table["iss"])
    put("needs", n_needs, fi(n_needs), [1, 4], "data/pipeline/scenario_needs.csv", "rows per scenario (iss, lunar_habitat)")
    V["needs_word"] = word(n_needs)
    for sid, key in (("iss", "iss"), ("lunar_habitat", "lunar")):
        k = sum(1 for c in table[sid] if c["in_range"] > 0)
        put(f"{key}_needs", k, fi(k), [4], "data/pipeline/scenario_needs.csv",
            f"questions of scenario {sid} with tests_atmosphere + tests_oxygen_only + tests_pressure_only above 0")
        V[f"{key}_needs_word"] = word(k)
        for c in table[sid]:
            NUMBERS[f"table_{key}_{c['id']}"] = {
                "value": {"in_range": c["in_range"], "oxygen_and_pressure": c["both"], "oxygen_only": c["oxygen"]},
                "shown_as": fi(c["in_range"]), "slides": [4], "source": "data/pipeline/scenario_needs.csv",
                "how": f"scenario {sid}, need {c['id']} ({c['need']}): tests_atmosphere + tests_oxygen_only + tests_pressure_only"}

    # the ranges each environment is counted in, and the pillar of the questions without a counted test
    spec = read_json("pipeline/spec/scenarios.json")
    spec_by = {s["id"]: s for s in (spec["scenarios"] if isinstance(spec, dict) and "scenarios" in spec else spec)}
    need("iss" in spec_by and "lunar_habitat" in spec_by, "pipeline/spec/scenarios.json lacks iss or lunar_habitat")

    def rng_text(r, unit, sep):
        lo, hi = r.get("min"), r.get("max")
        hi_txt = f"{hi:g}" if r.get("max_inclusive", False) else f"below {hi:g}"   # pipeline/check.py: max is exclusive unless max_inclusive
        if lo is None:
            need(hi is not None, "A range in scenarios.json has neither a minimum nor a maximum")
            return ("up to " + hi_txt if r.get("max_inclusive", False) else hi_txt) + unit
        need(r.get("min_inclusive", True) and hi is not None, "A range in scenarios.json has an exclusive minimum or no maximum: reword slide 4")
        return f"{lo:g}{sep}{hi_txt}{unit}"

    for sid, key in (("iss", "iss"), ("lunar_habitat", "lunar")):
        rg = spec_by[sid]["ranges"]
        put(f"{key}_o2_range", rg["o2_pct"], rng_text(rg["o2_pct"], "%", " to "), [4], "pipeline/spec/scenarios.json",
            f"scenarios[{sid}].ranges.o2_pct (max exclusive unless max_inclusive, as in pipeline/check.py in_range)")
        put(f"{key}_p_range", rg["pressure_kpa"], rng_text(rg["pressure_kpa"], " kPa", " to "), [4, 5] if key == "lunar" else [4],
            "pipeline/spec/scenarios.json", f"scenarios[{sid}].ranges.pressure_kpa (max exclusive unless max_inclusive)")
    lun = spec_by["lunar_habitat"]
    needs_spec = read_json("pipeline/spec/needs.json")
    pillars = {x["id"]: x.get("pillar") for x in needs_spec["needs"] if isinstance(x, dict) and "id" in x}
    need(pillars.get("D2") and pillars.get("P2"), "pipeline/spec/needs.json gives no pillar for D2 or P2")
    put("d2_pillar", pillars["D2"], pillars["D2"], [4], "pipeline/spec/needs.json", "needs[id = D2].pillar (Smoke generation conditions)")
    put("p2_pillar", pillars["P2"], pillars["P2"], [4], "pipeline/spec/needs.json", "needs[id = P2].pillar (Ignition)")

    # ---- the scorer (slide 3): the worked example "lunar habitat cotton fabric" ------------
    sys.path.insert(0, ROOT)
    try:
        from scoring import scorer
    except Exception as ex:  # noqa: BLE001
        fail(f"Could not import scoring.scorer ({type(ex).__name__}: {ex})")
    query = WORDING["s3"]["input_value"]
    out = scorer.rank(query)
    res = out["results"]
    need(len(res) == 3, "The scorer did not return three results for the worked example of slide 3")
    V["results_word"] = word(len(res))
    need(all(0 <= r["score"] <= 100 for r in out["ranking"]), "A score lies outside 0 to 100: reword slide 3 ('team score 0 to 100')")
    need(len(out["ranking"]) == tot["investigations"], "The scorer's ranking does not cover every investigation")
    sc, src = out["scenario"], out["sources"]
    need(all(str(src.get(k, "")).startswith("preset:") for k in ("o2_pct", "pressure_kpa", "flow_state")),
         "The scorer no longer takes oxygen, pressure and airflow from the preset: reword slide 3 (read_rows)")
    text_keys = ("gravity", "fuel_material", "fuel_class", "fuel_phase", "melt_behavior", "thermal_regime", "sample_geometry")
    need(all(src.get(k) == "text" for k in text_keys), "The scorer no longer reads gravity and the material from the user's words: reword slide 3 (read_rows)")
    need(src.get("concern") == "default", "The purpose of the question is no longer a default: reword slide 3 (read_rows)")
    need(sc.get("gravity") == "lunar" and sc.get("flow_state") == "ventilated", "The worked example is no longer read as lunar gravity and ventilated")
    need(sc.get("fuel_phase") == "solid" and sc.get("melt_behavior") == "chars" and sc.get("thermal_regime") == "thin" and sc.get("sample_geometry") == "flat_sheet",
         "The material of the worked example is no longer read as a solid that chars, a thin flat sheet: reword slide 3 (read_rows)")
    cfg = read_json("scoring/scoring_config.json")
    need(out["config_version"] == cfg["version"], "config_version of the scorer output differs from scoring_config.json")
    need(lun["nominal"]["o2_pct"] == sc["o2_pct"] and lun["nominal"]["pressure_kpa"] == sc["pressure_kpa"],
         "The scorer's lunar preset differs from the nominal values of lunar_habitat in pipeline/spec/scenarios.json")
    checked("the scorer's lunar preset equals the nominal oxygen and pressure of lunar_habitat in pipeline/spec/scenarios.json")
    how_rank = f"python3 -c \"from scoring import scorer; scorer.rank('{query}')\""
    S_SC = "scoring/scorer.py (preset lunar_habitat)"
    put("config_version", cfg["version"], cfg["version"], [3], "scoring/scoring_config.json", "version")
    put("o2", sc["o2_pct"], f"{sc['o2_pct']:g}", [3, 4, 5], S_SC, how_rank + ": scenario.o2_pct, source preset")
    put("kpa", sc["pressure_kpa"], f"{sc['pressure_kpa']:g}", [3, 4], S_SC, how_rank + ": scenario.pressure_kpa, source preset")
    put("psi", sc["pressure_kpa"] / 6.894757, f"{sc['pressure_kpa'] / 6.894757:.1f}", [3, 4], S_SC, "scenario.pressure_kpa / 6.894757 kPa per psi, one decimal")
    put("flow", sc["flow_state"], sc["flow_state"], [3], S_SC, how_rank + ": scenario.flow_state, source preset")
    put("gravity", sc["gravity"], sc["gravity"], [3], "scoring/scorer.py", how_rank + ": scenario.gravity, source text (the user's words)")
    for key, field in (("material", "fuel_material"), ("fuel_class", "fuel_class"), ("fuel_phase", "fuel_phase"), ("melt", "melt_behavior"),
                       ("regime", "thermal_regime"), ("shape", "sample_geometry")):
        put(key, sc[field], str(sc[field]).replace("_", " "), [3], "scoring/scorer.py", how_rank + f": scenario.{field}, source text (the user's words)")
    put("concern", sc["concern"], sc["concern"], [3], "scoring/scorer.py", how_rank + ": scenario.concern, source default")
    with open(path("web/index.html"), encoding="utf-8") as fh:
        index_html = fh.read()
    m = re.search(r'<button[^>]*data-q="' + re.escape(query) + r'"[^>]*>([^<]+)</button>', index_html)
    need(m, f"web/index.html has no example button for '{query}': reword slide 3 (input_hint)")
    put("example_button", m.group(1).strip(), m.group(1).strip(), [1, 3], "web/index.html", f"text of the example button whose data-q is '{query}'")
    for i, r in enumerate(res, 1):
        put(f"top{i}", r["investigation_id"], r["investigation_id"], [3], "scoring/scorer.py; scoring/scoring_config.json", how_rank + f": results[{i - 1}].investigation_id")
        put(f"score{i}", r["score"], f"{r['score']:.1f}", [3], "scoring/scorer.py; scoring/scoring_config.json", how_rank + f": results[{i - 1}].score")
        put(f"why{i}", r["why"], plain_reason(r["why"]), [3], "scoring/scorer.py", how_rank + f": results[{i - 1}].why, with 'O2' written 'oxygen', the dimension word inside the brackets left out and an inner bracket turned into a comma")
        put(f"gap{i}", r["main_gap"], plain_reason(r["main_gap"]), [3], "scoring/scorer.py", how_rank + f": results[{i - 1}].main_gap, reworded in the same way")
    need(res[0]["investigation_id"].startswith("SAFFIRE") and res[1]["investigation_id"].startswith("SAFFIRE"),
         "The first two results are no longer the two Saffire fabric tests: reword slide 3 (consider, note)")
    need(res[0]["score"] >= res[1]["score"], "Result 1 no longer has the higher score: check slide 3")
    codes = [{w["code"] for w in r["warnings"]} for r in res]
    need(res[2].get("complementary") == "o2" and "complementary" in codes[2],
         "Result 3 no longer holds its place by the oxygen rule (scoring/METHOD.md 1.5): reword slide 3 (rule, tag3, note)")
    by_score = 1 + sum(1 for r in out["ranking"] if r["score"] > res[2]["score"])
    need(by_score > 3, "Result 3 is now among the three highest scores: reword slide 3 (rule)")
    put("rank3_by_score", by_score, fi(by_score), [3], "scoring/scorer.py", how_rank + ": 1 + the number of entries of 'ranking' with a higher score than results[2]")
    V["rank3_ordinal"] = ordinal(by_score)
    with open(path("web/app.js"), encoding="utf-8") as fh:
        m = re.search(r'r\.complementary \? h\("span", \{ class: "tag" \}, "([^"]+)"\)', fh.read())
    need(m, "web/app.js no longer writes the tag of a result included for its oxygen: reword slide 3 (tag3)")
    with open(path("web/app.js"), encoding="utf-8") as fh:
        m2 = re.search(r'class: "score"(?:, title: [A-Z_]+)? \}, String\(r\.score\), h\("small", \{\}, "([^"]+)"\)', fh.read())
    need(m2, "web/app.js no longer writes the label under a result's score: reword slide 3 (rank_note)")
    put("score_label", m2.group(1), m2.group(1), [3], "web/app.js (renderResults)", "the label the page writes under a result's score; the slide uses the same words")
    put("tag3", m.group(1), m.group(1), [3], "web/app.js (renderResults)", "the tag text the page writes on a result whose field 'complementary' is set")
    comp = [{c["id"]: (c["status"], c.get("basis")) for c in r["compliance"]} for r in res]
    reqs = {q["id"]: q["dimension"] for q in out["requirements"]}
    need([reqs.get(f"R{i}") for i in range(1, 6)] == ["gravity", "o2", "pressure", "flow", "fuel"], "The scorer's requirement ids changed: check slide 3 (consider)")
    need(all(c["R1"][0] == "not_met" for c in comp), "Gravity is no longer 'not met' for all three results: reword slide 3")
    need(comp[0]["R2"] == ("not_met", "table") and comp[1]["R2"] == ("not_met", "table") and comp[2]["R2"] == ("met", "table"),
         "Oxygen is no longer 'not met' (table) for results 1 and 2 and 'met' (table) for result 3: reword slide 3")
    need(comp[0]["R3"] == ("unverified", "assumed") and comp[1]["R3"] == ("unverified", "assumed") and "fallback" in codes[0] and "fallback" in codes[1]
         and comp[2]["R3"] == ("documented", "record"),
         "Pressure is no longer 'unverified' (assumed) for results 1 and 2 and 'documented' (record) for result 3: reword slide 3")
    need(comp[0]["R4"][0] == "near" and comp[1]["R4"][0] == "near" and comp[2]["R4"][0] == "not_met",
         "Airflow is no longer 'near' for results 1 and 2 and 'not met' for result 3: reword slide 3")
    need(comp[0]["R5"][0] == "met" and comp[1]["R5"][0] == "met" and comp[2]["R5"][0] == "not_met" and "gas_for_solid" in codes[2],
         "Fuel is no longer 'met' for results 1 and 2 and 'not met' (a gas) for result 3: reword slide 3")
    configs = read_csv("data/catalog/configurations.csv")
    cfg_by = {c["config_id"]: c for c in configs}
    need(all(r["config_id"] in cfg_by for r in res), "A result's configuration is not in data/catalog/configurations.csv")
    need(all(fnum(cfg_by[r["config_id"]]["o2_max_pct"]) < sc["o2_pct"] for r in res[:2])
         and fnum(cfg_by[res[2]["config_id"]]["o2_min_pct"]) <= sc["o2_pct"] <= fnum(cfg_by[res[2]["config_id"]]["o2_max_pct"]),
         "configurations.csv no longer shows results 1 and 2 tested below the input oxygen and result 3 tested at it: reword slide 3")
    top_codes = {w["code"] for w in out["warnings"]}
    plain = scorer.rank("lunar habitat")
    need("partial_gravity" in top_codes and "no_material" not in top_codes and "no_material" in {w["code"] for w in plain["warnings"]},
         "The warnings changed (partial_gravity on the example; no_material only on a query without a material): reword the note of slide 3")
    NUMBERS["compliance_slide_3"] = {"value": [{k: list(v) for k, v in c.items()} for c in comp], "shown_as": None, "slides": [3],
                                     "source": "scoring/scorer.py", "how": how_rank + ": results[i].compliance (status, basis) per requirement R1 to R7; the points to consider of slide 3 restate R1 to R5"}
    checked("scorer, worked example: values from the preset, the user's words and the default as slide 3 says; results 1 and 2 are Saffire fabric tests; "
            "result 3 holds its place by the oxygen rule; gravity, oxygen, pressure, airflow and fuel statuses as the points to consider say; "
            "'no_material' is raised for 'lunar habitat' and not for the example")
    put("configs", len(configs), fi(len(configs)), [6], "data/catalog/configurations.csv", "rows")

    # ---- the results quoted from NASA's documents (slide 4) --------------------------------
    rs = read_json("data/pipeline/results_summary.json")["counts"]
    rbn = read_json("data/pipeline/results_by_need.json")
    fnd = rbn["findings"]
    quoted = [f for f in fnd.values() if f.get("kind") == "result"]
    need(len(quoted) == rs["results"] and sum(1 for f in quoted if f.get("printed_values")) == rs["results_with_printed_values"],
         "results_summary.json and results_by_need.json disagree on the number of quoted results or of those with printed values")
    lun_blocks = next((s for s in rbn["scenarios"] if s["id"] == "lunar_habitat"), None)
    need(lun_blocks, "results_by_need.json has no scenario lunar_habitat")
    by_group = {}
    for blk in lun_blocks["needs"]:
        for e in blk["found"]["entries"] + blk["found"]["entries_tagged_for_all_questions"]:
            by_group.setdefault(e["group"], set()).add(e["finding_id"])
    lg = rs["per_scenario_group"]["lunar_habitat"]
    need(len(by_group.get("at_environment", ())) == lg["at_environment"] and len(by_group.get("about_a_stated_condition", ())) == lg["about_a_stated_condition"],
         "The lunar-habitat groups of results_by_need.json differ from results_summary.json")
    checked("quoted results: results_summary.json equals a recount of results_by_need.json (results, with printed values, the two lunar-habitat groups)")
    S_RS = "data/pipeline/results_summary.json; data/pipeline/results_by_need.json"
    put("q_results", rs["results"], fi(rs["results"]), [4], S_RS, "counts.results; equal to the findings of kind 'result'")
    put("q_values", rs["results_with_printed_values"], fi(rs["results_with_printed_values"]), [4], S_RS, "counts.results_with_printed_values; equal to the results that hold printed_values")
    put("q_lunar_at", lg["at_environment"], fi(lg["at_environment"]), [4], S_RS, "counts.per_scenario_group.lunar_habitat.at_environment; equal to the distinct results of that group in the lunar-habitat blocks")
    put("q_lunar_about", lg["about_a_stated_condition"], fi(lg["about_a_stated_condition"]), [4], S_RS,
        "counts.per_scenario_group.lunar_habitat.about_a_stated_condition; equal to the distinct results of that group in the lunar-habitat blocks")
    ex = fnd.get(QUOTED_EXAMPLE)
    need(ex and ex.get("kind") == "result" and ex.get("quote"), f"results_by_need.json holds no quoted result {QUOTED_EXAMPLE}")
    need(len(ex["needs"]) == 1, "The example result is tagged for more than one question: reword slide 4 (quoted)")
    blk = next(b for b in lun_blocks["needs"] if b["need_id"] == ex["needs"][0])
    entry = next((e for e in blk["found"]["entries"] if e["finding_id"] == QUOTED_EXAMPLE), None)
    need(entry and entry["group"] == "about_a_stated_condition" and list(entry["matched_on"]) == ["gravity_level"]
         and set(entry["not_stated"]) == {"o2_pct", "pressure_kpa"},
         "The example result is no longer in the group 'about one stated condition' on its gravity level alone: reword slide 4 (quoted)")
    labels = {g["id"]: g["label"] for g in rbn["_meta"]["order_rule"]["groups"]}
    need(ex["conditions"]["gravity_level"] == "lunar" and "simulated" in ex["text"] and ex["conditions"]["material"]
         and len(ex["condition_words"].get("pressure", [])) == 1,
         "The example result no longer states simulated lunar gravity, a material and its pressure in words: reword slide 4 (quoted)")
    m = re.search(r"NTRS (\d+)", entry["source"]["version"])
    need(m and entry["source"]["url"].endswith(m.group(1)) and "Lunar Combustion Investigation" in entry["source"]["title"] and "slides" in entry["source"]["title"],
         "The source of the example result is no longer the LUCI slides with an NTRS number: reword slide 4 (quoted)")
    need(ex["relation"].startswith("related NASA experiment, not a PSI investigation"), "The example result no longer carries its relation note")
    S_RB = "data/pipeline/results_by_need.json"
    put("q_quote", ex["quote"], '"' + ex["quote"] + '"', [4], S_RB, f"findings['{QUOTED_EXAMPLE}'].quote, copied exactly, between quotation marks")
    put("q_need", blk["need"], blk["need"].lower(), [4], S_RB, f"need of the lunar-habitat block that lists the result ({blk['need_id']}), in lower case")
    put("q_material", ex["conditions"]["material"], ex["conditions"]["material"], [4], S_RB, f"findings['{QUOTED_EXAMPLE}'].conditions.material")
    put("q_gravity", ex["conditions"]["gravity_level"], ex["conditions"]["gravity_level"], [4], S_RB,
        f"findings['{QUOTED_EXAMPLE}'].conditions.gravity_level; the item's text says the gravity was simulated by centrifugal acceleration")
    put("q_pressure_words", ex["condition_words"]["pressure"][0], ex["condition_words"]["pressure"][0], [4], S_RB, f"findings['{QUOTED_EXAMPLE}'].condition_words.pressure (no number is printed)")
    put("q_ntrs", m.group(1), m.group(1), [4], S_RB, "source.version of the entry (NTRS number); the same number ends source.url")
    put("q_group", entry["group"], labels[entry["group"]], [4], S_RB, f"group of the entry in the lunar-habitat block {blk['need_id']}; label from _meta.order_rule.groups")
    q_position = 1 + [e["finding_id"] for e in blk["found"]["entries"]].index(QUOTED_EXAMPLE)

    # ---- counted tests and the lunar gap (slides 3, 4, 5) ----------------------------------
    need_tests = read_csv("data/pipeline/need_tests.csv")
    stated = {}
    for r in need_tests:
        if r["objective_link"] == "stated":
            stated.setdefault(r["need_id"], set()).add(r["test_id"])
    counted = set().union(*stated.values())
    need(all(t in by_id for t in counted), "need_tests.csv names a test that is not in tests.csv")
    for c in table["lunar_habitat"]:
        need(c["counted"] == len(stated.get(c["id"], ())), f"usable_tests of {c['id']} differs from the stated rows of need_tests.csv")
    o2, kpa = sc["o2_pct"], sc["pressure_kpa"]

    def in_gap(t):
        o, p = fnum(t["o2_pct"]), fnum(t["pressure_kpa"])
        return t["o2_basis"] == "ambient" and o is not None and p is not None and o >= o2 and p <= kpa

    gap_counted = [t for t in counted if in_gap(by_id[t])]
    need(len(gap_counted) == 0,
         f"{len(gap_counted)} counted test(s) now lie at {o2:g}% oxygen or more and {kpa:g} kPa or less: the deck's central sentence no longer holds")
    put("gap_counted", 0, "no counted test", [3, 4], "data/pipeline/tests.csv; data/pipeline/need_tests.csv",
        f"tests with objective_link = stated, ambient o2_pct >= {o2:g} and pressure_kpa <= {kpa:g}: 0")
    NUMBERS["gap_recorded_not_on_a_slide"] = {
        "value": sum(1 for t in tests if in_gap(t)), "shown_as": None, "slides": [],
        "source": "data/pipeline/tests.csv",
        "how": "recorded tests (counted or not) with ambient o2_pct and pressure_kpa in the same region; the reason the deck says 'no counted test' and never 'no recorded test'"}

    stests = read_csv("data/pipeline/scenario_tests.csv")
    inside = [r["test_id"] for r in stests if r["scenario_id"] == "lunar_habitat" and r["o2_match"] == "in" and r["pressure_match"] == "in"]
    s1_inside = [t for t in inside if t in stated.get("S1", ())]
    s1_row = next(c for c in table["lunar_habitat"] if c["id"] == "S1")
    need(len(s1_inside) == s1_row["both"] == s1_row["in_range"], "The counted extinction tests inside the lunar ranges differ between scenario_tests.csv and scenario_needs.csv")
    need(all(by_id[t]["sample_geometry"] == "droplet" for t in s1_inside), "A counted test inside the lunar ranges is not a droplet test: reword slides 4 and 5")
    press = [fnum(by_id[t]["pressure_kpa"]) for t in s1_inside]
    need(all(p is not None and p > kpa for p in press), "A counted test inside the lunar ranges is at or below the pressure limit")
    need(all(p < lun["ranges"]["pressure_kpa"]["max"] for p in press), "A counted extinction test inside the lunar ranges lies above the counting range: reword slides 4 and 5")
    put("s1_tests", len(s1_inside), fi(len(s1_inside)), [4, 5], "data/pipeline/scenario_tests.csv; need_tests.csv; scenario_needs.csv",
        "lunar_habitat tests with o2_match = in and pressure_match = in that are counted for S1; equal to tests_atmosphere of S1")
    put("s1_pmin", min(press), f"{min(press):.1f}", [4, 5], "data/pipeline/tests.csv", "lowest pressure_kpa of those tests, one decimal")
    put("s1_pmax", max(press), f"{max(press):.1f}", [4, 5], "data/pipeline/tests.csv", "highest pressure_kpa of those tests, one decimal")
    put("inside_tests", len(inside), fi(len(inside)), [5], "data/pipeline/scenario_tests.csv", "lunar_habitat rows with o2_match = in and pressure_match = in")
    not_counted = [t for t in inside if t not in counted]
    need(len(not_counted) == len(inside) - len(s1_inside) and not (set(inside) - set(s1_inside)) & counted,
         "A test inside the lunar ranges is counted for a question other than extinction: reword slide 5 (pile2_question)")
    put("inside_not_counted", len(not_counted), fi(len(not_counted)), [5], "data/pipeline/scenario_tests.csv; data/pipeline/need_tests.csv",
        "tests inside the lunar ranges with no row objective_link = stated in need_tests.csv (inside_tests minus the counted extinction tests)")

    tf = read_json("data/pipeline/test_files.json")["scenarios"]
    need("lunar_habitat" in tf and set(tf["lunar_habitat"]) == set(inside), "test_files.json does not list exactly the tests inside the lunar ranges")
    seen = {}
    for t in tf["lunar_habitat"].values():
        for f in t["file_list"]:
            seen[f["psi_file_id"]] = (int(f["bytes"]), f["link_state"])
    fbytes = sum(b for b, _ in seen.values())
    agree = sum(1 for _, s in seen.values() if s == "two_labels_agree")
    put("files", len(seen), fi(len(seen)), [5], "data/pipeline/test_files.json", "distinct psi_file_id over the file lists of the tests of scenarios.lunar_habitat")
    put("files_gb", fbytes, f"{fbytes / 1e9:.1f}", [5], "data/pipeline/test_files.json", "sum of bytes of those files / 10^9, one decimal")
    put("files_pct", fbytes / nbytes, f"{100 * fbytes / nbytes:.2f}", [5], "data/pipeline/test_files.json; data/pipeline/raw_inventory.json",
        "bytes of those files / _meta.totals.bytes, in percent, two decimals")
    put("files_agree", agree, fi(agree), [5], "data/pipeline/test_files.json", "those files with link_state = two_labels_agree")

    sheets = read_csv("data/pipeline/flex_sheet_vs_table.csv")
    read_sheets = {r["psi_file_name"] for r in sheets if r["test_id"] in s1_inside}
    need(all(r["state"].startswith("read from NASA's file, not adopted") for r in sheets if r["test_id"] in s1_inside),
         "A test-sheet row is no longer marked 'read from NASA's file, not adopted'")
    need(len(read_sheets) == len(s1_inside), "The number of test sheets read differs from the number of counted tests inside the ranges")
    put("sheets", len(read_sheets), fi(len(read_sheets)), [5], "data/pipeline/flex_sheet_vs_table.csv", "distinct psi_file_name among the rows of the counted tests inside the lunar ranges")

    p1 = stated.get("P1", set())
    p1_row = next(c for c in table["lunar_habitat"] if c["id"] == "P1")
    p1_o2 = [fnum(by_id[t]["o2_pct"]) for t in p1]
    need(p1 and all(o is not None for o in p1_o2), "A counted flammability-limit test has no oxygen value in tests.csv: reword slide 5, third pile")
    need(max(p1_o2) < o2 and p1_row["in_range"] == 0, "A counted flammability-limit test is now inside the lunar oxygen range: slide 5, third pile, no longer holds")
    put("p1_tests", len(p1), fi(len(p1)), [5], "data/pipeline/need_tests.csv", "rows with need_id = P1 and objective_link = stated")
    put("p1_inside", p1_row["in_range"], fi(p1_row["in_range"]), [5], "data/pipeline/scenario_needs.csv", "lunar_habitat, P1: tests_atmosphere + tests_oxygen_only + tests_pressure_only")
    put("p1_o2min", min(p1_o2), f"{min(p1_o2):g}", [5], "data/pipeline/tests.csv", "lowest o2_pct of the counted P1 tests")
    put("p1_o2max", max(p1_o2), f"{max(p1_o2):g}", [5], "data/pipeline/tests.csv", "highest o2_pct of the counted P1 tests")

    vids = read_csv("video/data/video_links.csv")
    vbytes = sum(int(v["bytes"]) for v in vids)
    need(len(vids) == kinds["video"]["files"] and vbytes == kinds["video"]["bytes"], "video_links.csv differs from by_kind.video in raw_inventory.json")
    checked("video_links.csv rows and bytes equal by_kind.video of raw_inventory.json")
    put("videos", len(vids), fi(len(vids)), [5], "video/data/video_links.csv", "rows")
    put("videos_gb", vbytes, f"{vbytes / 1e9:.0f}", [5], "video/data/video_links.csv", "sum of bytes / 10^9, no decimal")
    put("videos_agree", sum(1 for v in vids if v["link_state"] == "two_labels_agree"), fi(sum(1 for v in vids if v["link_state"] == "two_labels_agree")), [5],
        "video/data/video_links.csv", "rows with link_state = two_labels_agree")
    arch = read_csv("data/pipeline/archive_summary.csv")
    fetched, listed = sum(int(a["bytes_fetched"]) for a in arch), sum(int(a["listing_bytes"]) for a in arch)
    put("archives", len(arch), fi(len(arch)), [5], "data/pipeline/archive_summary.csv", "rows (archives whose zip directory was read)")
    atot = read_json("data/pipeline/archive_summary_totals.json")["overall"]
    need(atot["archives_listed"] == len(arch) and atot["archives_in_listing"] == kinds["archive"]["files"]
         and atot["bytes_fetched"] == sum(int(a["bytes_fetched"]) for a in arch),
         "archive_summary_totals.json differs from archive_summary.csv or from by_kind.archive of raw_inventory.json")
    checked("archives: archive_summary_totals.json equals archive_summary.csv (rows, bytes fetched) and by_kind.archive.files")
    put("archives_in_listing", atot["archives_in_listing"], fi(atot["archives_in_listing"]), [5],
        "data/pipeline/archive_summary_totals.json; data/pipeline/raw_inventory.json", "overall.archives_in_listing; equal to by_kind.archive.files")
    put("fetched_gb", fetched, f"{fetched / 1e9:.2f}", [5], "data/pipeline/archive_summary.csv", "sum of bytes_fetched / 10^9, two decimals")
    put("archives_tb", listed, f"{listed / 1e12:.1f}", [5], "data/pipeline/archive_summary.csv", "sum of listing_bytes / 10^12, one decimal")

    # ---- the four uses of SI (slide 6) -----------------------------------------------------
    need(shutil.which("node"), "Node.js is not on the PATH: web/parity_check.py cannot run, so the parity figure of slide 6 cannot be computed")
    vp, vt = run_check(["validation/run_validation.py", "--report", os.devnull], r"\*\*(\d+)/(\d+) scenarios passed\*\*", "validation/run_validation.py")
    need(vt == len(read_json("validation/scenarios.json")["scenarios"]), "The validation run did not cover every scenario of validation/scenarios.json")
    put("val_pass", vp, fi(vp), [6], "validation/run_validation.py; validation/scenarios.json", "run now with --report /dev/null (nothing written): scenarios passed")
    put("val_total", vt, fi(vt), [6], "validation/run_validation.py; validation/scenarios.json", "the same run: scenarios in the set")
    po, pt = run_check(["web/parity_check.py"], r"parity: (\d+)/(\d+) queries identical", "web/parity_check.py")
    put("par_ok", po, fi(po), [6], "web/parity_check.py (web/scorer.js against scoring/scorer.py)", "run now: queries with identical results")
    put("par_total", pt, fi(pt), [6], "web/parity_check.py", "the same run: queries compared")

    q = read_json("data/insights/quality.json")
    removed = q["dropped_by_gates"] + q["removed_before_review"]["n"] + q["removed_by_review"]
    need(q["proposed"] - removed == q["shipped_model_sentences"], "quality.json: written minus removed is not the number shown")
    need(q.get("recount_ok") is True, "quality.json says its own recount failed")
    put("proposed", q["proposed"], fi(q["proposed"]), [6], "data/insights/quality.json", "proposed")
    put("removed", removed, fi(removed), [6], "data/insights/quality.json",
        f"dropped_by_gates ({q['dropped_by_gates']}) + removed_before_review.n ({q['removed_before_review']['n']}) + removed_by_review ({q['removed_by_review']})")
    put("shown", q["shipped_model_sentences"], fi(q["shipped_model_sentences"]), [6], "data/insights/quality.json", "shipped_model_sentences; equal to proposed minus removed")
    put("reviewed_ai", q["reviewed_ai_session"], fi(q["reviewed_ai_session"]), [6], "data/insights/quality.json", "reviewed_ai_session")
    put("reviewed_person", q["reviewed_person"], fi(q["reviewed_person"]), [6, 7], "data/insights/quality.json", "reviewed_person")
    need(q["reviewed_person"] == 0, "reviewed_person is no longer 0: read the footers and slide 7 again before using the deck")
    need(q["reviewed_ai_session"] == q["proposed"] - q["dropped_by_gates"] - q["removed_before_review"]["n"],
         "quality.json: the sentences reviewed by an AI session are no longer those left after the code gates and the first reading: reword the footer of slide 6")
    checked("quality.json: reviewed_ai_session = proposed - dropped_by_gates - removed_before_review.n")

    # ---- the gravity point of slide 7: NASA drop-tower limits (Olson and Ferkul 2012, Table I) ----
    of_rows = [r for r in read_csv("data/pipeline/findings.csv") if r["finding_id"].startswith("OF2012.table1#")]
    need(of_rows, "data/pipeline/findings.csv holds no row of OF2012.table1: slide 7 (gravity) cannot be checked")
    of_text = of_rows[0]["text"]
    mats = re.findall(r"([A-Z][\w-]*(?: [\w-]+)?) at [\d.]+ psia: 1g ULOI ([\d.]+) and MOC ([\d.]+); Martian ULOI\* [\d.]+ and MOC\* [\d.]+; "
                      r"Lunar ULOI\* ([\d.]+) and MOC\* ([\d.]+); 0g ULOI\* ([\d.]+) and MOC\* ([\d.]+)", of_text)
    need(len(mats) == len(of_rows) and "drop tower" in of_text, "OF2012.table1 in findings.csv no longer reads as one drop-tower row per material: check slide 7 (gravity)")
    for m_ in mats:
        g1, lun_, g0 = (float(m_[1]) + float(m_[2])) / 2, (float(m_[3]) + float(m_[4])) / 2, (float(m_[5]) + float(m_[6])) / 2
        need(lun_ < g1 and lun_ < g0, f"OF2012 Table I: the lunar limit of {m_[0]} is not lower than both 0 g and 1 g: reword slide 7 (gravity)")
    put("of_materials", len(mats), fi(len(mats)), [7], "data/pipeline/findings.csv (OF2012.table1; NTRS-20130010991, AIAA 2012-3492)",
        "materials in Table I whose mean lunar ULOI*/MOC* is below both the 0 g and the 1 g mean (all of them)")
    V["of_materials_word"] = word(len(mats))
    refs = read_json("pipeline/spec/references.json")
    ref_list = refs["references"] if isinstance(refs, dict) and "references" in refs else refs
    of_ref = next((r for r in ref_list if isinstance(r, dict) and r.get("id") == of_rows[0]["reference_id"]), None)
    need(of_ref and "Olson, Ferkul" in of_ref["title"] and "2012" in of_ref["version"], "pipeline/spec/references.json no longer lists the Olson and Ferkul 2012 paper: check slide 7")
    V["of_cite"] = "Olson and Ferkul 2012"
    checked("slide 7 gravity: OF2012 Table I in findings.csv gives lunar limits below 0 g and 1 g for every material; reference listed in pipeline/spec/references.json")

    settings = read_json("video/settings/bass2.json")
    clip_files = sorted(glob.glob(os.path.join(path("video/data/team_transcription_bass2_onscreen_readings"), "*.csv")))
    need(len(clip_files) == len(settings["clips"]), "The number of reading files differs from the clips in video/settings/bass2.json")
    vrows = 0
    for cf in clip_files:
        with open(cf, newline="", encoding="utf-8") as fh:
            vrows += sum(1 for _ in csv.reader(fh)) - 1
    manifest = read_json("video/data/team_transcription_bass2_onscreen_readings/reading_manifest.json")
    need(vrows == sum(c["rows"] for c in manifest["clips"]), "The rows of the reading files differ from reading_manifest.json")
    put("clips", len(settings["clips"]), fi(len(settings["clips"])), [6], "video/settings/bass2.json; video/data/team_transcription_bass2_onscreen_readings/*.csv",
        "clips in the settings; equal to the number of CSV files")
    put("video_rows", vrows, fi(vrows), [6], "video/data/team_transcription_bass2_onscreen_readings/*.csv", "data rows of the CSV files; equal to the rows in reading_manifest.json")
    with open(path("video/README.md"), encoding="utf-8") as fh:
        vreadme = fh.read()
    m = re.search(r"Together: (\d+) frames, about [\d,]+ values compared, none wrong", vreadme)
    need(m, "video/README.md no longer states the frame check ('Together: N frames ... none wrong')")
    need("failed its check" in vreadme and "was removed" in vreadme, "video/README.md no longer says that the flame signal failed its check and was removed")
    put("frames", int(m.group(1)), fi(int(m.group(1))), [6] if VIDEO_FRAME_CHECK_ON_SLIDE else [], "video/README.md, 'How it was checked'",
        "STATED, NOT RECOUNTED: read from the sentence 'Together: N frames, ... none wrong'; the per-frame check sheet is not in the repository")

    mr = read_json("data/insights/model_readiness.json")
    passing = [r for r in mr["rows"] if "indicative" in r["verdict"]]
    need("no fitted model" in mr["shipped"], "model_readiness.json no longer says that no fitted model is shipped")
    put("labels", len(mr["rows"]), fi(len(mr["rows"])), [7], "data/insights/model_readiness.json", "rows (outcome labels assessed)")
    put("labels_pass", len(passing), fi(len(passing)), [7], "data/insights/model_readiness.json", "rows whose verdict says 'indicative' (a simple model beat the base rate)")
    need(len(passing) == 1, "The number of outcome labels that pass is no longer 1: reword slide 7 ('passes')")
    V["labels_word"], V["labels_pass_word"] = word(len(mr["rows"])), word(len(passing))

    # ---- the captures must be current and must show the numbers computed above -------------
    caps = read_json("docs/submission/deck/img/captures.json")
    CAP.update({c["file"]: c for c in caps["captures"]})
    used = ["top.png", "cotton_top3.png", "lunar_found.png", "lunar_piles_s1.png", "lunar_evidence_map.png"]
    if "assistant_recorded.png" in CAP:
        used.append("assistant_recorded.png")
    for extra in ("dashboard.png", "assistant_live.png"):   # the dashboard as a whole (slide 1); one live conversation (slide 6)
        if extra in CAP:
            used.append(extra)
    for f in used:
        need(f in CAP, f"img/captures.json has no entry for {f}: retake the captures (bash docs/submission/deck/refresh.sh)")
        c = CAP[f]
        need(c.get("scoring_config") == cfg["version"],
             f"img/{f} was taken under scoring config {c.get('scoring_config')}, the repository is at {cfg['version']}: retake the captures (bash docs/submission/deck/refresh.sh)")
        with open(path(f"docs/submission/deck/img/{f}"), "rb") as fh:
            digest = hashlib.sha256(fh.read()).hexdigest()
        need(digest == c.get("sha256"), f"img/{f} is not the picture that img/captures.json describes: retake the captures (bash docs/submission/deck/refresh.sh)")
        need(set(PAGE_FONTS) <= set(c.get("fonts_loaded", [])), f"img/{f} was taken without the page's fonts ({', '.join(PAGE_FONTS)}): retake it")
        need(set(c.get("outside_hosts", [])) <= set(FONT_HOSTS), f"img/{f}: the page reached a host other than its font hosts")
        if f != "top.png" and f != "assistant_recorded.png":
            need("q=" + query.replace(" ", "%20") in c["url"], f"img/{f} was not taken for the query '{query}'")
    checked(f"captures on the slides ({', '.join(used)}): taken under scoring config {cfg['version']}, with the page's two fonts, the file equal to its manifest entry")
    if "assistant_recorded.png" in CAP:
        rec = CAP["assistant_recorded.png"]
        need(caps["_meta"].get("recorded_assistant", {}).get("recorded_ready") is True,
             "img/assistant_recorded.png is in the manifest although the recording was not marked ready (ai/assistant/_runtime/RECORDED_READY): retake the captures")
        need((rec.get("recorded_answer") or {}).get("origin") == "model" and rec["check"].get("by_model") is True and rec["check"]["citations"] >= 1
             and str(rec["check"]["label"]).startswith("Recorded on ") and "no model runs on this page" in rec["check"]["label"],
             "img/assistant_recorded.png does not show a model-written answer with citation numbers and the 'Recorded on' label: choose another turn in capture.mjs")
        NUMBERS["recorded_answer_slide_6"] = {"value": {"conversation": rec.get("conversation"), "turn": rec.get("turn"), "recorded_at": rec.get("recorded_at"),
                                                        "model": rec.get("recorded_model"), "question": rec["check"].get("question"), "answer": rec["check"]["answer"],
                                                        "citation_marks": rec["check"]["citations"], "checks_line": rec["check"]["gates"]},
                                              "shown_as": None, "slides": [6], "source": "data/insights/assistant_recorded.json; docs/submission/deck/img/captures.json",
                                              "how": "the recorded turn chosen in capture.mjs (RECORDED_CONVERSATION, RECORDED_TURN), as the page replayed it for the capture; shown as a picture, nothing is retyped"}
    if "dashboard.png" in CAP:
        dash = CAP["dashboard.png"]["check"]
        need(len(dash["tabs"]) == 5 and len(dash["tab_lines"]) == 5 and dash["first_card"] == res[0]["investigation_id"],
             "img/dashboard.png does not show five tabs with their lines and the first result: retake the capture")
    if "assistant_live.png" in CAP:
        live = CAP["assistant_live.png"]
        lc = live["check"]
        need(live.get("live") is True and lc["mode"] == "live" and lc["by_model"] is True and lc["citations"] >= 1
             and str(lc["label"]).startswith("Written by a local language model") and lc["editable_values"] >= 1 and query in str(lc["question"]),
             "img/assistant_live.png does not show a model-written answer with citation numbers, its label and values that can be changed: take it again "
             "(DECK_LIVE=1 node docs/submission/deck/capture.mjs http://127.0.0.1:<port of the local assistant server>/)")
        NUMBERS["live_answer_slide_6"] = {"value": {"model": live.get("live_model"), "question": lc["question"], "answer": lc["answer"], "citation_marks": lc["citations"],
                                                    "label": lc["label"], "checks_line": lc["gates"], "answered": lc.get("answered"), "values_read": lc["values"]},
                                          "shown_as": None, "slides": [6], "source": "docs/submission/deck/img/captures.json (assistant_live.png)",
                                          "how": "one turn asked on the local assistant server with the language model answering, as the page showed it for the capture; shown as a picture, nothing is retyped"}
    top = CAP["top.png"]["check"]
    need(top["challengeLineShown"] is False and V["example_button"] in top["examples"],
         "img/top.png shows the line that quotes the challenge statement, or lacks the example button of slide 3: retake the capture")
    cards = CAP["cotton_top3.png"]["check"]
    need(len(cards) == 3, "img/cotton_top3.png does not hold three result cards: retake the capture")
    for i, card in enumerate(cards, 1):
        r = res[i - 1]
        need(card["rank"] == str(i) and card["name"] == r["investigation_id"] and fnum(card["score"].split()[0]) == round(r["score"], 1)
             and card["score"].split(None, 1)[1].lower() == V["score_label"].lower(),
             f"img/cotton_top3.png does not show result {i} as {V[f'top{i}']} {V[f'score{i}']}: retake the capture")
        need(card["why"] == "Why: " + r["why"] and card["gap"] == "Largest gap: " + r["main_gap"],
             f"img/cotton_top3.png: the reason or the largest gap of result {i} differs from the scorer's: retake the capture")
        need(card["details_open"] == [False], f"img/cotton_top3.png: 'Details and sources' of card {i} is not closed: retake the capture")
        need("and the order are Team RAPID's computation from NASA PSI data" in card["note"], "img/cotton_top3.png lacks the note that scores and order are the team's computation")
    need(V["tag3"] in cards[2]["tags"], f"img/cotton_top3.png: card 3 does not carry the tag '{V['tag3']}'")
    found = CAP["lunar_found.png"]["check"]
    need(len(found["items"]) >= q_position and found["items"][q_position - 1]["quote"] == ex["quote"] and found["items"][q_position - 1]["group"] == V["q_group"]
         and found["items"][q_position - 1]["relation"] == ex["relation"],
         "img/lunar_found.png does not show the example result of slide 4 with its quotation, group and relation: retake the capture or choose another example (QUOTED_EXAMPLE)")
    need("Quotations of NASA documents" in found["head"] and "no weights" in found["head"], "img/lunar_found.png: the section's note changed: read slide 4 again")
    V["q_item_box"] = f"item{q_position}"
    piles = CAP["lunar_piles_s1.png"]["check"]
    need(piles["summary"].startswith("Extinction conditions") and len(piles["piles"]) == 3
         and f"{V['s1_tests']} tests counted for this question" in piles["piles"][0] and f"{V['s1_pmin']} to {V['s1_pmax']} kPa" in piles["piles"][0]
         and piles["piles"][2].startswith("No record in PSI (listing of " + V["listing_date"] + ")"),
         "img/lunar_piles_s1.png does not show the counted extinction tests of slide 5 or the third pile's name: retake the capture")
    solid_o2 = [fnum(t["o2_pct"]) for t in tests if t["fuel_phase"] == "solid" and t["o2_basis"] == "ambient" and fnum(t["o2_pct"]) is not None]
    emap = CAP["lunar_evidence_map.png"]["check"]["text"]
    need(f"ends at {max(solid_o2):g}%" in emap and f"your input: {o2:g}% O2" in emap,
         "img/lunar_evidence_map.png does not show the solid-fuel end and the input computed from tests.csv: retake the capture")
    NUMBERS["solid_o2_max_in_capture"] = {"value": max(solid_o2), "shown_as": f"{max(solid_o2):g}", "slides": [7],
                                          "source": "data/pipeline/tests.csv; docs/submission/deck/img/captures.json",
                                          "how": "highest ambient o2_pct of a solid-fuel test; the evidence-map capture prints the same value ('ends at ...')"}
    V["solid_o2"] = f"{max(solid_o2):g}"
    gas_hi = [t for t in tests if t["fuel_phase"] == "gas" and t["o2_basis"] == "ambient" and (fnum(t["o2_pct"]) or 0) >= o2]
    need(gas_hi, "No recorded gas-flame test at the input oxygen or more: reword the caption of slide 7")
    NUMBERS["gas_recorded_at_input_o2_not_on_a_slide"] = {
        "value": len(gas_hi), "shown_as": None, "slides": ["7 caption, in words"], "source": "data/pipeline/tests.csv",
        "how": f"gas-fuel tests with ambient o2_pct >= {o2:g} (any pressure); the caption of slide 7 says they are recorded, and gap_counted says none at or below {kpa:g} kPa is counted"}
    checked("captures: cotton_top3.png shows the scorer's three results, scores, reasons and largest gaps with 'Details and sources' closed; "
            "lunar_found.png shows the example quotation in its group; lunar_piles_s1.png shows the counted extinction tests; "
            "lunar_evidence_map.png shows the solid-fuel end and the input; top.png shows the example button and not the challenge quotation")
    V["capture_date"] = long_date(CAP["top.png"]["taken_at"])
    need(all(long_date(CAP[f]["taken_at"]) == V["capture_date"] for f in used), "The captures on the slides were taken on different days: check the captions")
    NUMBERS["captures_on_slides"] = {"value": {f: {"taken_at": CAP[f]["taken_at"], "sha256": CAP[f]["sha256"], "scoring_config": CAP[f]["scoring_config"]} for f in used},
                                     "shown_as": None, "slides": [1, 3, 7] + ([6] if ("assistant_recorded.png" in used or "assistant_live.png" in used) else []),
                                     "source": "docs/submission/deck/img/captures.json",
                                     "how": "the captures the build checks, each with its time, its SHA-256 and the scoring config of the page build it was taken from; "
                                            "dashboard.png (slide 1; top.png when it is absent), cotton_top3.png (slide 3), lunar_evidence_map.png (slide 7) and assistant_live.png (slide 6; assistant_recorded.png when it is absent) are shown; "
                                            "lunar_found.png and lunar_piles_s1.png are not shown (too small to read at slide size) and only prove that the page prints the quotation of slide 4 and the counted tests of slide 5"}
    return table


# ======================================================================================
# 4. RENDERING
# ======================================================================================

def esc(s):
    return html.escape(str(s), quote=True)


def chip(text):
    return f'<span class="todo">{esc(text)}</span>'


def fmt(template, **extra):
    """Fill {names}, escape for HTML, then turn **x** into bold. Values in `raw` are HTML."""
    raw = extra.pop("raw", {})
    nb = extra.pop("nb", True)   # False inside SVG text and attributes, where a <span> is not allowed
    vals = dict(V, **extra)
    marks = {}
    for k, h in raw.items():
        marks[k] = f"\u0001{k}\u0002"
    try:
        text = template.format_map(dict(vals, **marks))
    except KeyError as ex:
        fail(f"The wording uses {{{ex.args[0]}}}, which no file gives a value for")
    text = esc(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\[\[(.+?)\]\]", (r'<span class="nb">\1</span>' if nb else r"\1"), text)   # [[x]]: keep x on one line
    if nb:
        text = re.sub(r"(?<![\w>/])([A-Za-z0-9]+(?:-[A-Za-z0-9]+)+)(?![\w<])", r'<span class="nb">\1</span>', text)
        # a number never parts from its unit at a line end ("70.3 kPa", "12.8 TB", "20 cm/s")
        text = re.sub(r"(?<![\w.,])(\d[\d.,]*\d|\d) (kPa|psi|TB|GB|MB|mm/s|cm/s)(?![\w/])", r'<span class="nb">\1 \2</span>', text)
    for k, h in raw.items():
        text = text.replace(marks[k], h)
    return text


def png_size(rel):
    with open(os.path.join(HERE, rel), "rb") as fh:
        head = fh.read(24)
    need(head[:8] == b"\x89PNG\r\n\x1a\n", f"{rel} is not a PNG file")
    return struct.unpack(">II", head[16:24])


CROP_DIR = "img/crop"
CROPS_MADE = set()


def _png_chunk(kind, data):
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def crop_png(src_rel, x0, y0, x1, y1):
    """Write the pixel box [x0, x1) x [y0, y1) of an 8-bit RGB or RGBA, non-interlaced PNG to img/crop/,
    so that slides.html and slides.pdf hold only the part a slide shows. Standard library only;
    the same input gives the same bytes. Returns the path relative to this folder."""
    with open(os.path.join(HERE, src_rel), "rb") as fh:
        data = fh.read()
    digest = hashlib.sha256(data).hexdigest()[:10]
    out_rel = f"{CROP_DIR}/{os.path.splitext(os.path.basename(src_rel))[0]}_{x0}_{y0}_{x1}_{y1}_{digest}.png"
    CROPS_MADE.add(out_rel)
    out_abs = os.path.join(HERE, out_rel)
    if os.path.exists(out_abs):
        return out_rel
    need(data[:8] == b"\x89PNG\r\n\x1a\n", f"{src_rel} is not a PNG file")
    pos, idat, hdr = 8, [], None
    while pos < len(data):
        n, = struct.unpack(">I", data[pos:pos + 4])
        kind, body = data[pos + 4:pos + 8], data[pos + 8:pos + 8 + n]
        pos += 12 + n
        if kind == b"IHDR":
            hdr = struct.unpack(">IIBBBBB", body)
        elif kind == b"IDAT":
            idat.append(body)
        elif kind == b"IEND":
            break
    need(hdr is not None, f"{src_rel} has no IHDR chunk")
    w, h, depth, ctype, _, _, interlace = hdr
    need(depth == 8 and ctype in (2, 6) and interlace == 0, f"{src_rel}: only 8-bit RGB or RGBA, non-interlaced PNG files can be cropped")
    need(0 <= x0 < x1 <= w and 0 <= y0 < y1 <= h, f"The crop of {src_rel} lies outside the picture")
    bpp = 3 if ctype == 2 else 4
    raw = zlib.decompress(b"".join(idat))
    stride = w * bpp
    need(len(raw) == h * (stride + 1), f"{src_rel}: unexpected image data length")
    prev = bytearray(stride)
    out_rows = []
    for y in range(y1):
        f = raw[y * (stride + 1)]
        line = bytearray(raw[y * (stride + 1) + 1:(y + 1) * (stride + 1)])
        if f == 1:
            for i in range(bpp, stride):
                line[i] = (line[i] + line[i - bpp]) & 255
        elif f == 2:
            line = bytearray((a + b) & 255 for a, b in zip(line, prev))
        elif f == 3:
            for i in range(stride):
                line[i] = (line[i] + (((line[i - bpp] if i >= bpp else 0) + prev[i]) >> 1)) & 255
        elif f == 4:
            for i in range(stride):
                a = line[i - bpp] if i >= bpp else 0
                b = prev[i]
                c = prev[i - bpp] if i >= bpp else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line[i] = (line[i] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        else:
            need(f == 0, f"{src_rel}: unknown PNG filter {f}")
        if y >= y0:
            out_rows.append(b"\x00" + bytes(line[x0 * bpp:x1 * bpp]))
        prev = line
    png = (b"\x89PNG\r\n\x1a\n" + _png_chunk(b"IHDR", struct.pack(">IIBBBBB", x1 - x0, y1 - y0, 8, ctype, 0, 0, 0))
           + _png_chunk(b"IDAT", zlib.compress(b"".join(out_rows), 9)) + _png_chunk(b"IEND", b""))
    os.makedirs(os.path.join(HERE, CROP_DIR), exist_ok=True)
    with open(out_abs, "wb") as fh:
        fh.write(png)
    return out_rel


def shot(file, x0, y0, x1, y1, width, alt, cls=""):
    """A crop of a capture, in the capture's CSS pixels (its pixels / 2), shown `width` px wide.
    The crop is cut out of the picture (img/crop/), so the page and the PDF hold nothing else."""
    pw, ph = png_size(os.path.join("img", file))
    cw, ch = pw / 2, ph / 2
    need(0 <= x0 < x1 <= cw + 0.5 and 0 <= y0 < y1 <= ch + 0.5, f"The crop of img/{file} lies outside the picture")
    rel = crop_png(os.path.join("img", file), int(round(x0 * 2)), int(round(y0 * 2)), min(pw, int(round(x1 * 2))), min(ph, int(round(y1 * 2))))
    s = width / (x1 - x0)
    return (f'<div class="shot {cls}" style="width:{width:.0f}px;height:{(y1 - y0) * s:.1f}px">'
            f'<img src="{esc(rel)}" alt="{esc(alt)}" style="width:100%;height:100%;left:0;top:0"></div>')


def cap_box(file, name):
    """A named box of a capture (CSS px inside the capture), as capture.mjs measured it on the page."""
    need(file in CAP and name in CAP[file].get("boxes_css_px", {}), f"img/captures.json gives no box '{name}' for {file}: retake the captures (refresh.sh)")
    b = CAP[file]["boxes_css_px"][name]
    return b["x"], b["y"], b["x"] + b["width"], b["y"] + b["height"]


def cap_size(file):
    c = CAP[file]["clip_css_px"]
    return c["width"], c["height"]


def slide(n, kicker, title, body, footer, subtitle=""):
    head, _, tail = kicker.partition(" · ")
    sub = f'<p class="subtitle">{subtitle}</p>' if subtitle else ""
    k = f'<b>{esc(head)}</b>' + (f' · {esc(tail)}' if tail else "")
    return f'''
<section class="frame" id="s{n}"><div class="slide s{n}">
<div class="kicker">{k}</div>
<header class="head"><h1 class="title">{title}</h1>{sub}</header>
<div class="content">{body}</div>
<div class="footer"><div class="ftext">{footer}</div><div class="fmark">{esc(AI_MARK)}<span class="num">{n} / 7</span></div></div>
</div></section>'''


def slide1():
    w = WORDING["s1"]
    team = esc(TEAM_NAME) if TEAM_NAME else chip(w["team_placeholder"])
    team_html = f'<div class="big">{team}</div>'
    if TEAM_LOGO:
        team_html = team_logo(300, w["logo_alt"].format(team=TEAM_NAME or ""), "teamlogo")
    link = PUBLIC_URL.replace("https://", "")
    ax0, _, ax1, _ = cap_box("top.png", "ask")
    _, _, _, vy1 = cap_box("top.png", "verbs")
    _, ey0, _, _ = cap_box("top.png", "eyebrow")   # page design v2: the start page is centred; the crop starts at its title
    cw, ch = cap_size("top.png")
    x0, x1 = max(0, ax0 - 24), min(cw, ax1 + 24)
    y0 = max(0, ey0 - 20)
    picture = shot("top.png", x0, y0, x1, min(ch, vy1 + 2), 680, "The start page of Fire Evidence Explorer: the product name, the line on what to type, the notice line, the question What are you building, and where, six example buttons, and the three cards Find, Compare, Interpret")
    caption = w["caption"]
    if "dashboard.png" in CAP:
        # the dashboard after the worked example says more about the product than the empty start page
        gx0, _, gx1, _ = cap_box("dashboard.png", "glance")
        _, cy0, _, _ = cap_box("dashboard.png", "card1")
        dw, dh = cap_size("dashboard.png")
        dx0, dx1 = max(0, gx0 - 24), min(dw, gx1 + 24)
        pic_w, max_h = 840, 590
        dy1 = min(dh, cy0 + 120, (dx1 - dx0) * max_h / pic_w)
        picture = shot("dashboard.png", dx0, 0, dx1, dy1, pic_w, w["alt_dashboard"], "cut")
        caption = w["caption_dashboard"]
    body = f'''<div class="cols">
<div class="col" style="width:800px">
  <div class="pair"><div class="lbl">{esc(w["product_label"])}</div><div class="big">{esc(w["product"])}</div></div>
  <div class="pair"><div class="lbl">{esc(w["team_label"])}</div>{team_html}</div>
  <p class="lead">{fmt(w["lead"])}</p>
  <div class="linkband"><div class="lbl">{esc(w["link_label"])}</div><a href="{esc(PUBLIC_URL)}">{esc(link)}</a><p>{fmt(w["link_hint"])}</p></div>
</div>
<div class="col" style="width:840px">
  {picture}
  <p class="cap">{fmt(caption)}</p>
</div></div>'''
    return slide(1, w["kicker"], fmt(w["title"]), body, fmt(w["footer"]))


def team_logo(width, alt, cls):
    """The team's logo (TEAM_LOGO), unchanged, `width` CSS px wide; its clear space is inside the file."""
    need(os.path.isfile(os.path.join(HERE, TEAM_LOGO)), f"TEAM_LOGO {TEAM_LOGO} is missing: copy it from the logo kit, or set TEAM_LOGO = None")
    need(width >= TEAM_LOGO_MIN_WIDTH, f"The team logo is drawn {width} px wide, under the kit's minimum of {TEAM_LOGO_MIN_WIDTH} px")
    h = width * TEAM_LOGO_SIZE[1] / TEAM_LOGO_SIZE[0]
    return f'<img class="{cls}" src="{esc(TEAM_LOGO)}" alt="{esc(alt)}" width="{width}" height="{h:.1f}">'


def stats(items):
    return "".join(f'<div class="stat"><div class="v">{fmt(v)}</div><div class="l">{fmt(l)}</div></div>' for v, l in items)


def slide2():
    w = WORDING["s2"]
    W = 1728
    nb = NUMBERS["archive_tb"]["value"]
    xa = W * NUMBERS["pct_archive"]["value"] / nb
    xv = W * NUMBERS["pct_video"]["value"] / nb
    xo = W - xa - xv
    if xo < 10:   # the sliver of "all other kinds" is drawn at least 10 px wide, taken from the archive segment; its label gives the value
        xa -= 10 - xo
        xo = 10.0
    bar1 = f'''<svg class="chart" viewBox="0 0 {W} 176" width="{W}" height="176" role="img" aria-label="{fmt(w["bar1_head"], nb=False)}">
<text x="{xa + xv / 2 - 22:.1f}" y="26" text-anchor="end" class="t26">{fmt(w["bar1_video"], nb=False)}</text>
<path d="M{xa + xv / 2 - 16:.1f} 17 H{xa + xv / 2:.1f} V44" class="lead-line"/>
<rect x="0" y="44" width="{xa:.2f}" height="84" fill="#17202b"/>
<rect x="{xa:.2f}" y="44" width="{xv:.2f}" height="84" fill="#2346c4"/>
<rect x="{xa + xv:.2f}" y="44" width="{xo:.2f}" height="84" fill="#b36b00"/>
<text x="28" y="98" class="t34 on-dark">{fmt(w["bar1_archive"], nb=False)}</text>
<path d="M{W - xo / 2:.1f} 128 V157 H{W - xo / 2 - 16:.1f}" class="lead-line"/>
<text x="{W - xo / 2 - 22:.1f}" y="166" text-anchor="end" class="t26">{fmt(w["bar1_other"], nb=False)}</text>
</svg>'''
    f = NUMBERS["archive_files"]["value"]
    segs, x = [], 0.0
    for key, cls in (("name_test", "seg-a"), ("name_day", "seg-b"), ("name_none", "seg-c")):
        wd = W * NUMBERS[key]["value"] / f
        big, lab = w["bar2_" + key.split("_")[1]]
        segs.append(f'<rect x="{x:.2f}" y="1" width="{wd:.2f}" height="96" class="{cls}"/>'
                    f'<text x="{x + 24:.1f}" y="43" class="t34 {cls}-t">{fmt(big, nb=False)}</text>'
                    f'<text x="{x + 24:.1f}" y="79" class="t26 {cls}-t">{fmt(lab, nb=False)}</text>')
        x += wd
    bar2 = f'<svg class="chart" viewBox="0 0 {W} 98" width="{W}" height="98" role="img" aria-label="{fmt(w["bar2_head"], nb=False)}">{"".join(segs)}</svg>'
    body = f'''<div class="panels">
  <div class="panel dark"><div class="ph">{fmt(w["left_head"])}</div><div class="stats" style="grid-template-columns:repeat({len(w["left_stats"])},auto)">{stats(w["left_stats"])}</div></div>
  <div class="panel"><div class="ph">{fmt(w["right_head"])}</div><div class="stats" style="grid-template-columns:repeat({len(w["right_stats"])},auto)">{stats(w["right_stats"])}</div></div>
</div>
<div class="barhead"><span>{fmt(w["bar1_head"])}</span><span class="tot">{fmt(w["bar1_total"])}</span></div>
{bar1}
<div class="barhead" style="margin-top:18px"><span>{fmt(w["bar2_head"])}</span><span class="tot">{fmt(w["bar2_total"])}</span></div>
{bar2}
<p class="rest">{fmt(w["rest"])}</p><p class="cap">{fmt(w["caption"])}</p>'''
    return slide(2, w["kicker"], fmt(w["title"]), body, fmt(w["footer"]))


def slide3():
    w = WORDING["s3"]
    rows = "".join(f'<div class="rrow"><span class="rsrc">{esc(s)}</span><span class="rval">{fmt(t)}</span></div>' for s, t in w["read_rows"])
    items = "".join(f"<li>{fmt(t)}</li>" for t in w["consider"])
    cards = []
    for i in (1, 2, 3):
        cx0, cy0, cx1, _ = cap_box("cotton_top3.png", f"card{i}")
        _, sy0, _, _ = cap_box("cotton_top3.png", f"strip{i}")
        alt = w["shot_alt"].format(n=i, name=V[f"top{i}"], score=V[f"score{i}"], label=V["score_label"])
        tag = " " + fmt(w["tag3"]) if i == 3 else ""
        cards.append(f'''<div class="rcard">{shot("cotton_top3.png", cx0, cy0 + 14, cx1, sy0 - 6, 850, alt, "cut")}
  <p class="wg"><b>{esc(w["why"])}</b> {fmt("{why%d}." % i)} <b>{esc(w["gap"])}</b> {fmt("{gap%d}." % i)}{tag}</p></div>''')
    body = f'''<div class="cols">
<div class="col" style="width:830px">
  <div class="blk typedrow"><div class="lbl">{esc(w["input_head"])}</div><div class="typed">{esc(w["input_value"])}</div><div class="hint">{fmt(w["input_hint"])}</div></div>
  <div class="blk"><div class="lbl">{esc(w["read_head"])}</div>{rows}</div>
  <div class="blk"><div class="lbl">{esc(w["consider_head"])}</div><ul class="tight">{items}</ul></div>
  <p class="rule">{fmt(w["rule"])}</p>
</div>
<div class="col" style="width:850px">
  <div class="lbl">{fmt(w["rank_head"])} <span class="lblnote">· {fmt(w["rank_note_team" if "team" in V["score_label"] else "rank_note_other"])}</span></div>
  {"".join(cards)}
</div></div>'''
    return slide(3, w["kicker"], fmt(w["title"]), body, fmt(w["footer"]))


def cell(c, w):
    if c["in_range"] == 0:
        return '<td class="zero"><span class="n">0</span></td>'
    if c["both"] and c["oxygen"]:
        cls = "mixed"
        note = (f'<span class="si both"></span>{fmt(w["mixed_both"], n=fi(c["both"]))}<br>'
                f'<span class="si oxy"></span>{fmt(w["mixed_oxygen"], n=fi(c["oxygen"]))}')
    elif c["both"]:
        cls, note = "both", fmt(w["both"])
    else:
        cls, note = "oxy", fmt(w["oxygen_only"])
    return f'<td class="{cls}"><span class="n">{fi(c["in_range"])}</span><span class="q">{note}</span></td>'


def slide4(table):
    w = WORDING["s4"]
    rows = "".join(f'<tr><th>{esc(i["need"].replace(" generation conditions", " generation"))}</th>{cell(i, w)}{cell(l, w)}</tr>'
                   for i, l in zip(table["iss"], table["lunar_habitat"]))
    body = f'''<div class="cols">
<div class="col" style="width:1060px">
<table class="needs">
<colgroup><col style="width:330px"><col style="width:385px"><col style="width:345px"></colgroup>
<thead><tr><th>{esc(w["col_question"])}</th><th>{esc(w["col_iss"])}<span class="rng">{fmt(w["col_range_iss"])}</span></th><th>{esc(w["col_lunar"])}<span class="rng">{fmt(w["col_range_lunar"])}</span></th></tr></thead>
<tbody>{rows}</tbody>
</table>
<div class="quoted"><p><b class="qh">{esc(w["quoted_head"])}:</b> {fmt(w["quoted"])}</p><p>{fmt(w["quoted2"])}</p></div>
</div>
<div class="col" style="width:620px">
  <div class="callout">{fmt(w["callout"])}</div>
  <p class="sub">{fmt(w["sub"])}</p>
  <div class="lbl">{esc(w["table_head"])}</div>
  <ul class="legend">
    <li><span class="sw both"></span>{esc(w["legend_both"])}</li>
    <li><span class="sw oxy"></span>{esc(w["legend_oxygen"])}</li>
    <li><span class="sw zero"></span>{esc(w["legend_zero"])}</li>
  </ul>
  <p class="ranges">{fmt(w["ranges"])} {fmt(w["definition"])}</p>
</div></div>'''
    return slide(4, w["kicker"], fmt(w["title"]), body, fmt(w["footer"]), fmt(w["subtitle"]))


def range_strip(a0, a1, ticks, lo, hi, mark, side, band_label, marker_label, axis_label, aria):
    """Slide 5: where the counted tests lie (blue band) against the habitat's value (amber), to scale.
    side 'right': the habitat is at `mark` or more; side 'left': at `mark` or less.
    The two labels sit on two rows above the band, so that neither runs into the other."""
    W = 496
    need(a0 < min(lo, mark) and max(hi, mark) < a1, f"The strip '{aria}' does not hold its values: widen its axis")
    pad = 18  # room for the first and last tick label
    x = lambda v: pad + (v - a0) / (a1 - a0) * (W - 2 * pad)  # noqa: E731
    yb, hb = 56, 30            # top and height of the band
    ya = yb + hb               # the axis
    tk = "".join(f'<line x1="{x(t):.1f}" y1="{ya}" x2="{x(t):.1f}" y2="{ya + 8}" class="ax"/><text x="{x(t):.1f}" y="{ya + 30}" text-anchor="middle" class="t22">{t:g}</text>'
                 for t in ticks)
    if side == "right":
        shade = f'<rect x="{x(mark):.1f}" y="{yb}" width="{x(a1) - x(mark):.1f}" height="{hb}" fill="#ffe6ad"/>'
        labels = (f'<text x="{x(lo):.1f}" y="20" class="t24b" fill="#2346c4">{band_label}</text>'
                  f'<text x="{x(a1):.1f}" y="47" text-anchor="end" class="t24b" fill="#8a5300">{marker_label}</text>')
    else:
        shade = f'<rect x="{x(a0):.1f}" y="{yb}" width="{x(mark) - x(a0):.1f}" height="{hb}" fill="#ffe6ad"/>'
        labels = (f'<text x="{x(a0):.1f}" y="20" class="t24b" fill="#8a5300">{marker_label}</text>'
                  f'<text x="{x(lo):.1f}" y="47" class="t24b" fill="#2346c4">{band_label}</text>')
    return f'''<svg class="chart" viewBox="0 0 {W} {ya + 58}" width="{W}" height="{ya + 58}" role="img" aria-label="{esc(aria)}">
{shade}
<rect x="{x(lo):.1f}" y="{yb}" width="{x(hi) - x(lo):.1f}" height="{hb}" fill="#2346c4"/>
<line x1="{x(a0):.1f}" y1="{ya}" x2="{x(a1):.1f}" y2="{ya}" class="ax"/>
<line x1="{x(mark):.1f}" y1="{yb - 4}" x2="{x(mark):.1f}" y2="{ya + 8}" stroke="#8a5300" stroke-width="3"/>
{tk}
{labels}
<text x="{x(a1):.1f}" y="{ya + 54}" text-anchor="end" class="t20">{axis_label}</text>
</svg>'''


def slide5():
    w = WORDING["s5"]
    n = NUMBERS
    kpa = n["kpa"]["value"]
    p0, p1 = int(kpa) - 1, int(n["s1_pmax"]["value"]) + 2
    strip_p = range_strip(p0, p1, range(p0, p1 + 1), n["s1_pmin"]["value"], n["s1_pmax"]["value"], kpa, "left",
                          fmt(w["strip_p_band"], nb=False), fmt(w["strip_p_marker"], nb=False), fmt(w["strip_p_axis"], nb=False),
                          "Pressure of the counted tests and of the habitat, to scale")
    o0 = 5 * int(n["p1_o2min"]["value"] // 5)
    o1 = 5 * (int(n["o2"]["value"]) // 5 + 1)
    strip_o = range_strip(o0, o1 + 1, range(o0, o1 + 1, 5), n["p1_o2min"]["value"], n["p1_o2max"]["value"], n["o2"]["value"], "right",
                          fmt(w["strip_band"], nb=False), fmt(w["strip_marker"], nb=False), fmt(w["strip_axis"], nb=False),
                          "Oxygen of the counted tests and of the habitat, to scale")
    body = f'''<div class="piles">
  <div class="pile p1"><div class="phd">{fmt(w["pile1_head"])}</div>
    <div class="pq">{fmt(w["pile1_question"])}</div>
    <div class="pn"><span class="n">{V["s1_tests"]}</span><span class="u">{fmt(w["pile1_unit"])}</span></div>
    <p>{fmt(w["pile1_text"])}</p>
    {strip_p}</div>
  <div class="pile p2"><div class="phd">{fmt(w["pile2_head"])}</div>
    <div class="pq">{fmt(w["pile2_question"])}</div>
    <div class="pn"><span class="n">{V["files"]}</span><span class="u">{fmt(w["pile2_unit"])}</span></div>
    <p>{fmt(w["pile2_text"])}</p><p>{fmt(w["pile2_text_agree"])}</p><p>{fmt(w["pile2_text2"])}</p></div>
  <div class="pile p3"><div class="phd">{fmt(w["pile3_head"])} <span>{fmt(w["pile3_head_tail"])}</span></div>
    <div class="pq">{fmt(w["pile3_question"])}</div>
    <div class="pn"><span class="n">{V["p1_inside"]}</span><span class="u">{fmt(w["pile3_unit"])}</span></div>
    <p>{fmt(w["pile3_text"])}</p>
    {strip_o}
    <p class="small">{fmt(w["pile3_small"])}</p></div>
</div>
<div class="band5">
  <div class="b5shot"><div class="lbl">{esc(w["shot_head"])}</div><p>{fmt(w["shot_line"])}</p></div>
  <div class="strip"><div class="lbl">{esc(w["strip_head"])}</div><div><b>{esc(w["strip1_head"])}</b> {fmt(w["strip1"])}</div><div><b>{esc(w["strip2_head"])}</b> {fmt(w["strip2"])}</div></div>
</div>'''
    return slide(5, w["kicker"], fmt(w["title"]), body, fmt(w["footer"]))


ARROW = '<svg class="arrow" viewBox="0 0 24 16" width="24" height="16" aria-hidden="true"><path d="M1 8H21M14 2l7 6-7 6" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'


def slide6():
    w = WORDING["s6"]
    measured = all(v is not None for v in ASSISTANT_MEASURED.values())
    a = {k: (esc(v) if v is not None else chip(w["placeholder"])) for k, v in ASSISTANT_MEASURED.items()}
    araw = {"a_full": a["correct_full_pipeline"], "a_set": a["questions_in_set"], "a_single": a["correct_single_call"],
            "a_num_full": a.get("numbers_full", ""), "a_num_single": a.get("numbers_single", ""), "a_word_full": a.get("wording_full", ""), "a_word_single": a.get("wording_single", ""),
            "a_chip": chip(w["placeholder_all"])}   # while any value is None: one chip, so that nothing can look like a value
    picture = "assistant_recorded.png" in CAP   # taken by capture.mjs only once the new recording is marked ready
    rows = []
    for i, b in enumerate(w["boxes"], 1):
        if i == 3:
            check = fmt(b["check_measured"] if measured else b["check_unmeasured"], raw=araw)
            # the chain of steps (b["does"]) is said in the speaker note; the slide keeps one line
            does = f"<p>{fmt(b['does_note'])}</p>"
        elif i == 4 and VIDEO_FRAME_CHECK_ON_SLIDE:
            check = fmt(b["check_with_frames"], raw={"not_recounted_tag": f'<span class="tagnote">{esc(b["not_recounted_tag"])}</span>'})
            does = f"<p>{fmt(b['does'])}</p>"
        else:
            check = fmt(b["check"])
            does = f"<p>{fmt(b['does'])}</p>"
        tag = f' <span class="tag">{esc(b["tag"])}</span>' if b["tag"] else ""
        rows.append(f'<div class="use"><div class="un">{i}</div><div class="uw"><h3>{esc(b["name"])}{tag}</h3>{does}</div><div class="uc"><p>{check}</p></div></div>')
    uses = f'''<div class="usehead"><span></span><span>{esc(w["col_use"])}</span><span>{esc(w["col_check"])}</span></div>
{"".join(rows)}
<div class="modelband"><b>{esc(w["model_head"])}:</b> {fmt(w["model"])}</div>'''
    if "assistant_live.png" in CAP:
        # the whole card, as a visitor sees it after an answer (the human lead: show the whole, not parts of it)
        L = "assistant_live.png"
        lw, lh = cap_size(L)
        max_w, max_h = 560, 566
        width = min(max_w, max_h * lw / lh)
        body = f'''<div class="cols withshot">
<div class="col" style="width:1120px">{uses}</div>
<div class="col" style="width:{max_w}px"><div class="lbl">{esc(w["live_head"])}</div>
  {shot(L, 0, 0, lw, lh, width, w["live_alt_whole"])}
  <p class="cap" style="font-size:19px;line-height:25px">{fmt(w["live_cap"])}</p></div>
</div>'''
    elif picture:
        x0, _, x1, _ = cap_box("assistant_recorded.png", "chat")
        _, qy0, _, qy1 = cap_box("assistant_recorded.png", "question")
        _, ay0, _, _ = cap_box("assistant_recorded.png", "answer")
        _, _, _, gy1 = cap_box("assistant_recorded.png", "gates")
        width = 560
        body = f'''<div class="cols withshot">
<div class="col" style="width:1120px">{uses}</div>
<div class="col" style="width:{width}px"><div class="lbl">{esc(w["shot_head"])}</div>
  {shot("assistant_recorded.png", x0 - 4, qy0 - 6, x1 + 4, qy1 + 6, width, w["shot_alt_question"])}
  <div style="height:8px"></div>
  {shot("assistant_recorded.png", x0 - 4, ay0 - 6, x1 + 4, gy1 + 6, width, w["shot_alt"])}
  <p class="cap">{fmt(w["shot_cap"])}</p></div>
</div>'''
    else:
        body = uses
    return slide(6, w["kicker"], fmt(w["title_measured"] if measured else w["title_unmeasured"]), body, fmt(w["footer"]), fmt(w["subtitle"]))


def slide7():
    w = WORDING["s7"]
    nxt = "".join(f"<li>{esc(t)}</li>" for t in w["next"])
    _, ty0, _, _ = cap_box("lunar_evidence_map.png", "title")
    _, _, _, my1 = cap_box("lunar_evidence_map.png", "map")
    cw, _ = cap_size("lunar_evidence_map.png")
    body = f'''<div class="cols">
<div class="col" style="width:620px">
  <div class="blk"><div class="lbl">{esc(w["limits_head"])}</div><p>{fmt(w["limits"])}</p></div>
  <div class="blk"><div class="lbl">{esc(w["gravity_head"])}</div><p>{fmt(w["gravity"])}</p></div>
  <div class="blk"><div class="lbl">{esc(w["model_head"])}</div><p>{fmt(w["model"])}</p></div>
  {('<div class="logo7">' + team_logo(200, WORDING["s1"]["logo_alt"].format(team=TEAM_NAME or ""), "teamlogo7") + '</div>') if TEAM_LOGO else ""}
</div>
<div class="col" style="width:1060px">
  {shot("lunar_evidence_map.png", 0, ty0 - 4, cw, my1 + 6, 1040, "The evidence map of the page for lunar habitat cotton fabric: recorded tests on the oxygen axis for gas flames, fuel droplets and solid fuels; the solid-fuel tests end at " + V["solid_o2"] + " percent oxygen and the input is marked at " + V["o2"] + " percent")}
  <p class="capread">{fmt(w["caption_read"])}</p>
  <div class="row7">
    <div class="blk next7"><div class="lbl">{esc(w["next_head"])}</div><ol class="tight">{nxt}</ol></div>
    <div class="pair link bottom"><div class="lbl">{esc(w["link_label"])}</div><a href="{esc(PUBLIC_URL)}">{esc(PUBLIC_URL.replace("https://", ""))}</a>
      <div class="lbl second">{esc(w["method_label"])}</div><a class="small" href="{esc(METHOD_URL)}">{esc(METHOD_URL.replace("https://", ""))}</a></div>
  </div>
</div></div>'''
    return slide(7, w["kicker"], fmt(w["title"]), body, fmt(w["footer"]))


CSS = r"""
:root{--paper:#f6f7f4;--grid:#e9ece7;--ink:#17202b;--ink2:#4e5968;--rule:#cfd6d1;--blue:#2346c4;--blue-soft:#dfe6fb;
--amber:#8a5300;--amber-fill:#ffe6ad;--red:#9c2418;--red-fill:#fbe1dd;--white:#fff;--s:1;
--font:"Atkinson Hyperlegible",system-ui,-apple-system,"Segoe UI",sans-serif;
--display:"Barlow Semi Condensed","Atkinson Hyperlegible",system-ui,sans-serif}
*{box-sizing:border-box;-webkit-print-color-adjust:exact;print-color-adjust:exact}
html{background:#2b3440}
body{margin:0;color:var(--ink);font-family:var(--font)}
b,strong{font-weight:700}
.deck{display:flex;flex-direction:column;align-items:center;gap:24px;padding:24px 0}
.frame{width:calc(1920px*var(--s));height:calc(1080px*var(--s));overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,.35)}
.slide{position:relative;width:1920px;height:1080px;overflow:hidden;transform:scale(var(--s));transform-origin:0 0;
 background-color:var(--paper);background-image:linear-gradient(var(--grid) 1px,transparent 1px),linear-gradient(90deg,var(--grid) 1px,transparent 1px);background-size:48px 48px}
html.only{background:var(--paper)} html.only .deck{padding:0;gap:0} html.only .frame{display:none;box-shadow:none} html.only .frame.on{display:block}
@page{size:1920px 1080px;margin:0}
@media print{html{background:none}.deck{display:block;padding:0}
 .frame{width:1920px!important;height:1080px!important;box-shadow:none;break-after:page;break-inside:avoid}
 .frame:last-child{break-after:auto}.slide{transform:none!important}}

.kicker{position:absolute;left:96px;right:96px;top:78px;font-family:var(--display);font-size:24px;line-height:28px;letter-spacing:.09em;text-transform:uppercase;color:var(--ink2);font-weight:600}
.kicker b{color:var(--blue);font-weight:700}
.head{position:absolute;left:96px;right:96px;top:114px}
.title{margin:0;font-family:var(--display);font-size:64px;line-height:68px;font-weight:700;letter-spacing:-.005em;text-wrap:balance}
.subtitle{display:block;margin-top:10px;font-size:27px;line-height:36px;font-weight:400;letter-spacing:0;color:var(--ink2)}
.content{position:absolute;left:96px;right:96px;top:276px;height:672px}
.footer{position:absolute;left:96px;right:96px;bottom:50px;min-height:60px;border-top:1px solid var(--rule);padding-top:10px;display:flex;justify-content:space-between;align-items:flex-start;gap:48px;font-size:18px;line-height:25px;color:var(--ink2)}
.ftext{flex:1;text-wrap:pretty}
.fmark{white-space:nowrap;font-weight:700}
.num{display:inline-block;margin-left:22px;color:var(--ink);font-family:var(--display);font-weight:700;font-size:22px}
p{margin:0;text-wrap:pretty}
.nb{white-space:nowrap}
.cols{display:flex;justify-content:space-between;height:100%}
.col{display:flex;flex-direction:column}
.lbl{font-family:var(--display);font-size:22px;line-height:26px;letter-spacing:.08em;text-transform:uppercase;font-weight:700;color:var(--blue);margin-bottom:6px}
.cap{font-size:22px;line-height:29px;color:var(--ink2);margin-top:12px;text-wrap:pretty}
.todo{display:inline-block;padding:1px 12px;border:3px dashed var(--amber);border-radius:8px;background:var(--amber-fill);color:#5a3600;font-weight:700;white-space:nowrap}
.shot{position:relative;overflow:hidden;border:1px solid var(--rule);border-radius:8px;background:var(--white);flex:none}
.shot img{position:absolute;max-width:none;display:block}
.shot.cut{border-bottom:0;border-radius:8px 8px 0 0}
.shot.cut::after{content:"";position:absolute;left:0;right:0;bottom:0;height:12px;background:linear-gradient(rgba(246,247,244,0),var(--paper))}
.blk{margin-bottom:22px}
.blk p,.blk li{font-size:26px;line-height:34px;text-wrap:pretty}
ul.tight,ol.tight{margin:0;padding-left:28px}
ul.tight li,ol.tight li{margin-bottom:6px}
svg.chart{display:block;font-family:var(--font)}
svg .t20{font-size:20px;fill:var(--ink2)} svg .t22{font-size:22px;fill:var(--ink2)} svg .t24b{font-size:23px;font-weight:700}
svg .t26{font-size:25px;fill:var(--ink)} svg .t34{font-family:var(--display);font-size:36px;font-weight:700}
svg .on-dark{fill:#fff}
svg .lead-line{fill:none;stroke:var(--ink2);stroke-width:2}
svg .ax{stroke:var(--ink2);stroke-width:2}
.link a{font-family:var(--display);font-size:34px;line-height:40px;font-weight:700;color:var(--blue);text-decoration:underline;text-underline-offset:5px;white-space:nowrap}

/* slide 1 */
.s1 .pair{margin-bottom:22px}
.s1 .big{font-family:var(--display);font-size:44px;line-height:48px;font-weight:700}
.teamlogo,.teamlogo7{display:block}
.s1 .teamlogo{margin:-6px 0 0 -16px}
.logo7{margin-top:auto;margin-left:-11px}
.s7 .col:first-child .blk{margin-bottom:12px}
.s1 .lead{font-size:32px;line-height:45px;margin:6px 0 0}
.linkband{margin-top:auto;background:var(--white);border:2px solid var(--blue);border-radius:10px;padding:16px 26px 16px}
.linkband a{display:block;font-family:var(--display);font-size:50px;line-height:56px;font-weight:700;color:var(--blue);text-decoration:underline;text-underline-offset:6px;white-space:nowrap}
.linkband p{font-size:24px;line-height:32px;color:var(--ink2);margin-top:6px}

/* slide 2 */
.panels{display:flex;gap:32px;margin-bottom:22px}
.panel{flex:1;background:var(--white);border:2px solid var(--blue);border-radius:10px;padding:16px 26px 18px}
.panel.dark{background:var(--ink);border-color:var(--ink);color:#fff}
.ph{font-size:24px;line-height:30px;font-weight:700;color:var(--ink2);margin-bottom:6px}
.panel.dark .ph{color:#b8c2cf}
.stats{display:grid;gap:0 36px;align-items:end;justify-content:space-between}
.stat .v{font-family:var(--display);font-size:66px;line-height:68px;font-weight:700;white-space:nowrap}
.stat .l{font-size:25px;line-height:32px}
.panel:not(.dark) .stat .v{color:var(--blue)}
.barhead{display:flex;justify-content:space-between;align-items:baseline;font-family:var(--display);font-size:30px;line-height:36px;font-weight:700;margin-bottom:2px}
.barhead .tot{font-family:var(--font);font-weight:400;color:var(--ink2);font-size:24px}
svg .seg-a{fill:var(--blue)} svg .seg-b{fill:#b9c6f3} svg .seg-c{fill:#fff;stroke:var(--ink2);stroke-width:2}
svg .seg-a-t{fill:#fff} svg .seg-b-t{fill:var(--ink)} svg .seg-c-t{fill:var(--ink)}
.s2 .rest{font-size:26px;line-height:35px;font-weight:700;margin-top:16px}
.s2 .cap{margin-top:4px}

/* slide 3 */
.typedrow{display:flex;align-items:center;gap:16px}
.typedrow .lbl{margin:0;white-space:nowrap}
.lblnote{font-family:var(--font);font-size:20px;font-weight:400;letter-spacing:0;text-transform:none;color:var(--ink2)}
.s3 .typed{font-size:28px;line-height:38px;font-weight:700;background:var(--white);border:2px solid var(--ink);border-radius:8px;padding:5px 16px;white-space:nowrap}
.s3 .hint{font-size:21px;line-height:26px;color:var(--ink2)}
.rrow{display:flex;gap:14px;align-items:baseline;font-size:24px;line-height:31px;background:var(--white);border:1px solid var(--rule);border-radius:8px;padding:5px 14px;margin-bottom:6px}
.rsrc{flex:none;width:128px;font-family:var(--display);font-size:20px;letter-spacing:.06em;text-transform:uppercase;font-weight:700;color:var(--ink2)}
.s3 .blk{margin-bottom:11px}
.s3 .blk p,.s3 .blk li{font-size:25px;line-height:32px}
.s3 .title{font-size:56px;line-height:60px}
.s3 ul.tight li{margin-bottom:4px}
.s3 .rule{font-size:24px;line-height:31px;margin-top:2px;border-left:8px solid var(--ink2);padding-left:16px}
.rcard{margin-bottom:10px}
.s3 .wg{font-size:24px;line-height:31px;margin-top:6px;text-wrap:pretty}
.s3 .rcard{margin-bottom:22px}

/* slide 4 */
table.needs{border-collapse:separate;border-spacing:0 5px;width:100%;margin-top:-5px;table-layout:fixed}
table.needs th{font-family:var(--display);font-size:29px;line-height:32px;text-align:left;font-weight:600;padding:0 20px 0 0;white-space:nowrap}
table.needs thead th{font-size:26px;font-weight:700;padding:0 14px 2px;color:var(--ink2)}
table.needs thead th:first-child{padding-left:0}
table.needs td{height:50px;padding:0 14px;border-radius:8px;border:2px solid transparent;vertical-align:middle;background-clip:padding-box}
table.needs tbody td+td{border-left:8px solid transparent}
table.needs td .n{font-family:var(--display);font-size:40px;line-height:44px;font-weight:700;display:inline-block;min-width:66px;vertical-align:middle}
table.needs td .q{font-size:22px;line-height:23px;display:inline-block;vertical-align:middle;max-width:240px}
table.needs td.mixed .q{max-width:300px;white-space:nowrap}
table.needs td.mixed{background-color:var(--white);border-color:var(--blue)}
table.needs td.mixed .q{font-weight:700}
.si{display:inline-block;width:16px;height:14px;border-radius:3px;margin-right:6px;vertical-align:0}
.si.both{background:var(--blue)} .si.oxy{background:var(--amber-fill);border:1px solid #d9b55c}
table.needs td.both{background-color:var(--blue);color:#fff}
table.needs td.oxy{background-color:var(--amber-fill);color:#4a2c00}
table.needs td.zero{background-color:transparent;color:#7a8490}
table.needs td.zero .n{font-weight:500;border:2px dashed #aab2bb;border-radius:8px;min-width:54px;text-align:center;line-height:40px}
.quoted{margin-top:6px;border-top:1px solid var(--rule);padding-top:8px}
.quoted p{font-size:25px;line-height:32px;margin-bottom:8px;text-wrap:pretty}
.quoted .qh{font-family:var(--display);font-size:23px;letter-spacing:.06em;text-transform:uppercase;color:var(--blue)}
.callout{background:var(--red-fill);border-left:10px solid var(--red);border-radius:8px;padding:14px 22px;font-size:29px;line-height:38px;color:#6d160d}
.callout b{font-weight:700}
.s4 .sub{font-size:25px;line-height:33px;margin:12px 0 16px;text-wrap:pretty}
.s4 .content{top:306px;height:642px}
table.needs thead th .rng{display:block;font-family:var(--font);font-size:20px;line-height:24px;font-weight:400;letter-spacing:0;color:var(--ink2);white-space:normal}
table.needs thead th{vertical-align:bottom}
ul.legend{list-style:none;margin:0;padding:0}
ul.legend li{position:relative;padding-left:50px;font-size:24px;line-height:31px;margin-bottom:8px}
.sw{position:absolute;left:0;top:3px;width:36px;height:24px;border-radius:6px}
.sw.both{background:var(--blue)} .sw.oxy{background:var(--amber-fill);border:1px solid #d9b55c} .sw.zero{border:2px dashed #aab2bb}
.s4 .ranges{font-size:24px;line-height:32px;color:var(--ink2);margin-top:14px;border-top:1px solid var(--rule);padding-top:12px}
.s4 .def{font-size:21px;line-height:28px;color:var(--ink2);margin-top:10px;border-top:1px solid var(--rule);padding-top:10px}

/* slide 5 */
.piles{display:flex;gap:28px;align-items:stretch}
.pile{flex:1;background:var(--white);border:1px solid var(--rule);border-top:12px solid var(--ink2);border-radius:10px;padding:10px 26px 12px}
.pile.p1{border-top-color:var(--blue)} .pile.p2{border-top-color:#c98200} .pile.p3{border-top-color:var(--ink)}
.phd{font-family:var(--display);font-size:32px;line-height:36px;font-weight:700}
.phd span{font-family:var(--font);font-size:21px;font-weight:400;color:var(--ink2);white-space:nowrap}
.pq{font-size:24px;line-height:30px;color:var(--ink2);font-weight:700;margin-top:4px}
.pn{display:flex;align-items:baseline;gap:14px;margin:0 0 4px}
.pn .n{font-family:var(--display);font-size:72px;line-height:72px;font-weight:700}
.p1 .pn .n{color:var(--blue)} .p2 .pn .n{color:var(--amber)}
.pn .u{font-size:24px;line-height:29px;font-weight:700}
.pile p{font-size:25px;line-height:32px;margin-bottom:8px}
.pile p.small{font-size:22px;line-height:28px;color:var(--ink2);margin:2px 0 0}
.pile svg{margin:2px 0}
.band5{display:flex;justify-content:space-between;gap:40px;margin-top:14px}
.b5shot{flex:none;width:820px;border-left:8px solid var(--blue);padding-left:18px}
.b5shot p{font-size:25px;line-height:33px}
.strip{flex:1;font-size:24px;line-height:32px;border-left:8px solid var(--ink2);padding:0 0 0 18px;align-self:flex-start}
.strip b{font-weight:700}

/* slide 6 */
.usehead{display:grid;grid-template-columns:64px 700px 1fr;font-family:var(--display);font-size:22px;line-height:26px;letter-spacing:.08em;text-transform:uppercase;font-weight:700;color:var(--blue);margin-bottom:6px}
.usehead span{padding-left:20px}
.usehead span:last-child{padding-left:24px}
.use{display:grid;grid-template-columns:64px 700px 1fr;background:var(--white);border:1px solid var(--rule);border-radius:10px;height:130px;margin-bottom:10px;overflow:hidden}
.un{background:var(--ink);color:#fff;font-family:var(--display);font-size:44px;font-weight:700;display:flex;align-items:center;justify-content:center}
.uw{padding:8px 14px 8px 20px;display:flex;flex-direction:column;justify-content:center}
.uw h3{margin:0 0 3px;font-family:var(--display);font-size:32px;line-height:34px;font-weight:700}
.uw p{font-size:24px;line-height:30px;color:var(--ink2)}
.uw p.steps{font-size:23px;line-height:30px;color:var(--ink);font-weight:700}
.arrow{color:var(--blue);vertical-align:-1px;margin:0 2px}
.tag{display:inline-block;font-family:var(--font);font-size:20px;line-height:28px;font-weight:700;border:1px solid var(--ink2);border-radius:14px;padding:0 10px;color:var(--ink2);vertical-align:middle;white-space:nowrap}
.uc{border-left:1px solid var(--rule);padding:8px 18px 8px 22px;display:flex;align-items:center}
.uc p{font-size:24px;line-height:31px}
.uc .todo{font-size:22px;line-height:28px;border-width:2px;padding:0 8px}
.tagnote{font-size:22px;font-style:italic;font-weight:400;color:var(--ink2)}
.modelband{margin-top:2px;font-size:24px;line-height:32px;background:var(--white);border:2px solid var(--ink);border-radius:10px;padding:12px 22px}
.modelband b{font-weight:700}
.withshot .usehead,.withshot .use{grid-template-columns:52px 570px 1fr}
.withshot .use{height:auto;min-height:124px;margin-bottom:8px}
.withshot .un{font-size:38px}
.withshot .uw{padding:8px 12px 8px 16px}
.withshot .uw h3{font-size:28px;line-height:31px}
.withshot .uw p,.withshot .uc p{font-size:24px;line-height:31px}
.withshot .uw p{text-wrap:balance}
.withshot .uw p.steps{font-size:19px;line-height:26px}
.withshot .arrow{width:18px;margin:0}
.withshot .uc{padding:8px 14px 8px 16px}
.withshot .tag{font-size:20px;line-height:26px;padding:0 8px}
.withshot .modelband{font-size:24px;line-height:31px;padding:10px 18px}
.withshot .cap{font-size:22px;line-height:29px;margin-top:10px}

/* slide 7 */
.s7 .blk{margin-bottom:18px}
.s7 .blk p,.s7 .blk li{font-size:26px;line-height:34px}
.row7{display:flex;gap:28px;align-items:flex-end;margin-top:auto}
.row7 .next7{flex:1;margin:0}
.row7 .pair.bottom{flex:none;margin-top:0}
.s7 .capread{font-size:22px;line-height:29px;margin-top:10px;text-wrap:pretty}
.s7 .row7 ol.tight li{margin-bottom:2px}
.s7 .pair.bottom{margin-top:auto;background:var(--white);border:2px solid var(--blue);border-radius:10px;padding:12px 22px 14px}
.s7 .lbl.second{margin-top:10px;color:var(--ink2);font-size:19px;letter-spacing:.05em}
.s7 .link a.small{font-size:27px;line-height:32px}
"""

JS = r"""
// AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
// Screen view: scale the stacked slides to the window. ?only=N shows slide N alone at 1920 x 1080.
(function () {
  var root = document.documentElement;
  var m = /[?&]only=(\d+)/.exec(location.search);
  if (m) {
    root.classList.add('only');
    var f = document.getElementById('s' + m[1]);
    if (f) f.classList.add('on');
  }
  function fit() {
    var s = m ? 1 : Math.max(0.2, Math.min(1.5, (window.innerWidth - 48) / 1920));
    root.style.setProperty('--s', String(s));
  }
  fit();
  window.addEventListener('resize', fit);
})();
"""


def font_links():
    """The Google Fonts tags of web/index.html, copied so that the deck loads the page's fonts the same way."""
    with open(path("web/index.html"), encoding="utf-8") as fh:
        tags = re.findall(r'<link rel="(?:preconnect|stylesheet)" href="https://fonts\.(?:googleapis|gstatic)\.com[^>]*>', fh.read())
    sheet = [t for t in tags if 'rel="stylesheet"' in t]
    need(len(sheet) == 1 and all(f.replace(" ", "+") in sheet[0] for f in PAGE_FONTS),
         "web/index.html no longer loads Atkinson Hyperlegible and Barlow Semi Condensed with one Google Fonts <link>: check the deck's fonts")
    return "\n".join(tags)


def render(table):
    slides = [slide1(), slide2(), slide3(), slide4(table), slide5(), slide6(), slide7()]
    need(len(slides) == 7, "The deck must have exactly 7 slides")
    return f'''<!-- AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon. -->
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Fire Evidence Explorer: project demo, 7 slides</title>
<meta name="description" content="Seven slides on Fire Evidence Explorer, a research exploration tool built on NASA PSI data. Match scores and counts are Team RAPID's computation from NASA PSI data. Built with AI assistance (Claude).">
<meta name="generator" content="docs/submission/deck/build_deck.py (AI-generated code, Claude)">
{font_links()}
<style>{CSS}</style>
</head>
<body>
<main class="deck">{"".join(slides)}
</main>
<script>{JS}</script>
</body>
</html>
'''


NOTE_MAX_WORDS = 60


def speaker_notes():
    measured = all(v is not None for v in ASSISTANT_MEASURED.values())
    team = f"team {TEAM_NAME}" if TEAM_NAME else WORDING["s1"]["team_placeholder"]
    out = ["<!-- AI-generated text: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon. -->",
           "# Speaker notes, seven slides", "",
           "Draft written by an AI assistant (Claude) for the team to rewrite in its own words. Written by `build_deck.py` from its block WORDING; "
           "the numbers are filled from the repository's files (`numbers.json`). Do not edit this file: edit WORDING and rebuild. "
           f"Each note has {NOTE_MAX_WORDS} words or fewer. Checked by code and AI sessions.", ""]
    for n in range(1, 8):
        w = WORDING[f"s{n}"]
        title = w.get("title") or w["title_measured" if measured else "title_unmeasured"]
        note = w.get("note") or w["note_measured" if measured else "note_unmeasured"]
        try:
            title, note = title.format_map(V), note.format_map(dict(V, team=team))
        except KeyError as ex:
            fail(f"The speaker note of slide {n} uses {{{ex.args[0]}}}, which no file gives a value for")
        words = len(note.split())
        need(words <= NOTE_MAX_WORDS, f"The speaker note of slide {n} has {words} words; the limit is {NOTE_MAX_WORDS}")
        out += [f"## Slide {n}", "", f"Title on the slide: {title}", "", f"Note ({words} words): {note}", ""]
    return "\n".join(out)


def git_commit():
    try:
        out = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True, timeout=20)
        return out.stdout.strip() or None
    except Exception:  # noqa: BLE001
        return None


CHROME = os.environ.get("CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
PDF_MAX_BYTES = 10 * 1000 * 1000


def pdf_fonts(pdf):
    """The names of the fonts a PDF embeds: with pdffonts (poppler) when it is installed, else read from the
    PDF's own /FontName and /BaseFont entries. Returns (names, how)."""
    tool = shutil.which("pdffonts")
    if tool:
        out = subprocess.run([tool, pdf], capture_output=True, text=True, timeout=120)
        need(out.returncode == 0, f"pdffonts could not read slides.pdf: {out.stderr.strip()[-300:]}")
        rows = out.stdout.splitlines()[2:]
        need(rows, "pdffonts lists no font in slides.pdf")
        need(all(re.search(r"\byes\s+(yes|no)\s+(yes|no)\s+\d+\s+\d+\s*$", r) for r in rows), "slides.pdf uses a font that is not embedded (pdffonts, column 'emb')")
        return sorted({r.split()[0] for r in rows}), "pdffonts"
    with open(pdf, "rb") as fh:
        data = fh.read()
    names = {m.decode("latin-1") for m in re.findall(rb"/(?:FontName|BaseFont)\s*/([^\s/<>\[\]()]+)", data)}
    need(names, "No font name found in slides.pdf")
    return sorted(names), "the PDF's /FontName and /BaseFont entries"


def print_outputs(profile_dir):
    """Print slides.html to ../slides.pdf and to preview/slide-N.png with headless Chrome.
    Chrome may reach the two hosts of the page's fonts and no other: every other host name is unresolvable.
    The PDF must have 7 pages of 16:9, stay under 10 MB and embed the page's two font families only."""
    need(os.path.exists(CHROME), f"Google Chrome not found at {CHROME} (set the environment variable CHROME)")
    import tempfile
    made = None
    if not profile_dir:
        made = profile_dir = tempfile.mkdtemp(prefix="deck-chrome-")
    rules = "MAP * ~NOTFOUND , EXCLUDE 127.0.0.1 , " + " , ".join("EXCLUDE " + h for h in FONT_HOSTS)
    flags = ["--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1", "--no-first-run",
             "--no-default-browser-check", "--disable-background-networking", "--disable-component-update", "--disable-sync",
             "--disable-default-apps", "--disable-extensions", f"--host-resolver-rules={rules}",
             "--virtual-time-budget=20000",   # lets the web fonts arrive before the page is printed or photographed
             f"--user-data-dir={profile_dir}"]
    url = "file://" + os.path.join(HERE, "slides.html").replace(" ", "%20")
    pdf = os.path.abspath(os.path.join(HERE, "..", "slides.pdf"))
    try:
        subprocess.run([CHROME] + flags + ["--no-pdf-header-footer", f"--print-to-pdf={pdf}", url], capture_output=True, timeout=300)
        need(os.path.exists(pdf), "Chrome did not write slides.pdf")
        with open(pdf, "rb") as fh:
            data = fh.read()
        pages = len(re.findall(rb"/Type\s*/Page(?![a-zA-Z])", data))
        need(pages == 7, f"slides.pdf has {pages} pages, not 7")
        need(len(data) < PDF_MAX_BYTES, f"slides.pdf is {len(data):,} bytes: over 10 MB")
        boxes = {tuple(float(x) for x in m.split()) for m in (b.decode("latin-1") for b in re.findall(rb"/MediaBox\s*\[([^\]]+)\]", data))}
        need(boxes and all(len(b) == 4 and abs((b[2] - b[0]) * 9 - (b[3] - b[1]) * 16) < 1 for b in boxes), f"slides.pdf has a page that is not 16:9 (MediaBox {sorted(boxes)})")
        fonts, how = pdf_fonts(pdf)
        fams = [f.replace(" ", "") for f in PAGE_FONTS]
        stray = [f for f in fonts if not any(fam in f for fam in fams)]
        need(not stray, f"slides.pdf embeds a font that is not one of the page's two families ({', '.join(stray)}): the web fonts did not load, "
                        "or a character is missing from them. Check the network for " + ", ".join(FONT_HOSTS) + " and build again")
        need(all(any(fam in f for f in fonts) for fam in fams), f"slides.pdf does not embed both of the page's font families (found {', '.join(fonts)})")
        os.makedirs(os.path.join(HERE, "preview"), exist_ok=True)
        for n in range(1, 8):
            png = os.path.join(HERE, "preview", f"slide-{n}.png")
            if os.path.exists(png):
                os.remove(png)
            subprocess.run([CHROME] + flags + ["--window-size=1920,1080", f"--screenshot={png}", f"{url}?only={n}"], capture_output=True, timeout=300)
            need(os.path.exists(png) and png_size(os.path.join("preview", f"slide-{n}.png")) == (1920, 1080),
                 f"preview/slide-{n}.png was not written at 1920 x 1080")
    finally:
        if made:
            shutil.rmtree(made, ignore_errors=True)
    box = sorted(boxes)[0]
    print(f"build_deck.py: slides.pdf written: {pages} pages of {box[2] - box[0]:g} x {box[3] - box[1]:g} pt (16:9), {len(data):,} bytes; "
          f"fonts embedded ({how}): {', '.join(fonts)}; preview/slide-1.png to slide-7.png written")


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Build the seven-slide deck (numbers.json, slides.html; with --pdf also ../slides.pdf and preview/).")
    ap.add_argument("--pdf", action="store_true", help="also print ../slides.pdf and preview/slide-N.png with headless Google Chrome")
    ap.add_argument("--chrome-profile", default=None, help="folder for Chrome's temporary profile (default: a temporary folder, removed afterwards)")
    args = ap.parse_args()
    table = compute()
    page = render(table)
    notes = speaker_notes()
    missing = sorted(src for src in set(re.findall(r'src="(img/[^"]+)"', page)) if not os.path.exists(os.path.join(HERE, src)))
    need(not missing, f"Captures not found: {missing}")
    for old in glob.glob(os.path.join(HERE, CROP_DIR, "*.png")):   # crops of an earlier build that no slide uses now
        if os.path.relpath(old, HERE).replace(os.sep, "/") not in CROPS_MADE:
            os.remove(old)
    need(not re.search(r'(?:src|href)="(?!img/|https://choidol0208\.github\.io/NASA_RAPID/|https://fonts\.googleapis\.com|https://fonts\.gstatic\.com)', page),
         "slides.html would need a file or URL outside img/, the public page and the two font hosts")
    meta = {
        "what": "Every number shown on the seven slides, with the file it comes from and the way it was computed. Team RAPID's computation from NASA PSI files and the team's own checks.",
        "AI-generated": True,
        "built_by": "docs/submission/deck/build_deck.py (AI-generated code, written with Claude; no language model ran to build it)",
        "built_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "git_commit": git_commit(),
        "reviewed_by_a_person": 0,
        "units": "TB, GB and MB are decimal (10^12, 10^9, 10^6 bytes)",
        "fonts": "Barlow Semi Condensed (headings and numbers) and Atkinson Hyperlegible (text), SIL Open Font License, loaded from Google Fonts with the <link> of web/index.html; "
                 "slides.html needs the network for them, slides.pdf embeds them",
    }
    placeholders = {
        "TEAM_NAME": TEAM_NAME,
        "ASSISTANT_MEASURED": ASSISTANT_MEASURED,
        "note": "None means that the slide shows a visible placeholder chip instead of a value.",
        "slide_6_title": WORDING["s6"]["title_measured" if all(v is not None for v in ASSISTANT_MEASURED.values()) else "title_unmeasured"],
        "VIDEO_FRAME_CHECK_ON_SLIDE": VIDEO_FRAME_CHECK_ON_SLIDE,
    }
    with open(os.path.join(HERE, "numbers.json"), "w", encoding="utf-8") as fh:
        json.dump({"_meta": meta, "placeholders": placeholders, "numbers": NUMBERS, "cross_checks_passed": CHECKS}, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    with open(os.path.join(HERE, "slides.html"), "w", encoding="utf-8") as fh:
        fh.write(page)
    with open(os.path.join(HERE, "speaker_notes.md"), "w", encoding="utf-8") as fh:
        fh.write(notes)
    print(f"build_deck.py: {len(NUMBERS)} numbers written to numbers.json; 7 slides written to slides.html; 7 notes written to speaker_notes.md")
    todo = (["TEAM_NAME"] if TEAM_NAME is None else []) + [f"ASSISTANT_MEASURED[{k!r}]" for k, v in ASSISTANT_MEASURED.items() if v is None]
    if todo:
        print("build_deck.py: placeholders still shown: " + ", ".join(todo))
    if args.pdf:
        print_outputs(args.chrome_profile)
    return 0


if __name__ == "__main__":
    sys.exit(main())
