# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""Every fixed sentence of the assistant (ai/assistant/DESIGN.md sections 3, 4.6, 7, 9.5, 10.3, 12.5).

Nothing here is a fact: templates hold no digit, every number is a {slot} filled from a team file by
code. Every text passes ai.checks.check_template (ai/assistant/test_check.py runs it).
"""

# ---------------------------------------------------------------- intents (3.1)
INTENTS = ("find_investigations", "compare_environments", "question_evidence", "where_data", "modelling_data",
           "equipment_research", "earth_applications", "explain", "help", "out_of_scope")

INTENT_DESCRIPTIONS = {
    "find_investigations": "Which NASA investigations are closest to what the user builds or where (a crewed "
                           "environment, a material, a kind of fire).",
    "compare_environments": "Compare two or three environments, such as the ISS cabin and a lunar base.",
    "question_evidence": "What NASA's recorded tests and documents hold for a fire-safety question (flammability, "
                         "ignition, flame spread, extinction, combustion products, smoke) in an environment.",
    "where_data": "Where the data are: in NASA's tables, in the archive but unprocessed, or no record; which raw "
                  "files belong to a test.",
    "modelling_data": "Data that could support predictive modelling of flammability or fire: which tables, "
                      "variables, units, how many rows, what is missing.",
    "equipment_research": "Research behind a kind of fire-safety equipment or control: smoke and gas detection, "
                          "extinguishing agents and suppression, material selection, ventilation.",
    "earth_applications": "What the PSI records say about applications on Earth.",
    "explain": "Explain a term, a label or how a number on the page was computed.",
    "help": "What the assistant can do; greetings.",
    "out_of_scope": "Anything outside NASA's combustion experiments in weightlessness and fire safety in crewed "
                    "environments (for example rocket engines).",
}

INTENT_LABELS = {
    "find_investigations": "closest investigations", "compare_environments": "a comparison of environments",
    "question_evidence": "what the recorded tests say", "where_data": "where the data are",
    "modelling_data": "data for modelling", "equipment_research": "research behind equipment",
    "earth_applications": "applications on Earth", "explain": "an explanation", "help": "help",
    "out_of_scope": "outside this tool",
}

FLAG_DESCRIPTIONS = {
    "asks_verdict": "the user asks whether something is safe, allowed, good enough, or what to choose.",
    "asks_prediction": "the user asks what would happen at some conditions, or for a value at a condition.",
}

# ---------------------------------------------------------------- equipment kinds (3.2)
EQUIPMENT = {
    "detection": {"label": "Smoke and gas detection", "questions": ["D1", "D2"],
                  "keywords": ["smoke", "detector", "detection", "sensor", "particle", "soot", "carbon monoxide",
                               "aerosol"]},
    "suppression": {"label": "Extinguishing agents and suppression", "questions": ["S1"],
                    "keywords": ["suppress", "suppressant", "suppression", "extinguish", "extinguishment",
                                 "extinction", "agent", "inert", "carbon dioxide", "helium"]},
    "material_selection": {"label": "Material selection", "questions": ["P1", "P2", "P3"],
                           "keywords": ["flammability", "material", "fabric", "ignition", "spread", "oxygen index",
                                        "burning"]},
    "ventilation": {"label": "Ventilation and flow control", "questions": ["P1", "P3", "S1"],
                    "keywords": ["flow", "ventilation", "fan", "air flow", "velocity", "opposed", "concurrent",
                                 "quiescent"]},
}

GRAVITY_LABELS = {"microgravity": "microgravity", "lunar": "lunar gravity", "martian": "Martian gravity",
                  "earth": "Earth gravity"}
FLOW_LABELS = {"quiescent": "still air", "opposed": "flow against the flame", "concurrent": "flow with the flame",
               "ventilated": "ventilated"}

# ---------------------------------------------------------------- clarifying questions and assumptions (4.6)
CLARIFY = {
    "environment": "Which environment is this for?",
    "equipment": "Which kind of fire-safety equipment or control do you mean?",
    "term": "Which term or number do you want explained?",
    "investigations": "Which investigation do you mean? These names are close: {names}.",
    "conflict": "I read this two ways: {a} or {b}. Which one do you mean?",
}
CLARIFY_EARTH = "Earth, sea-level air"
CLARIFY_OTHER_ATMOSPHERE = "Another atmosphere (type oxygen and pressure)"

ASSUME_PRESET = "{label}: {value}, from the {preset} preset."
ASSUME_QUESTIONS = "Questions: all fire-safety questions of the team's list, because the message names none."
ASSUME_COMPARE = "Compared with: {label}, because the message names one environment."
ASSUME_CONFLICT_RULES = "Read as {a} (the readings differed; the rule parser's reading is used)."
ASSUME_CONFLICT_MODEL = "Read as {a} (the readings differed; the first model reading is used)."
ASSUME_CELL = ("Counts use the cell of the team's coverage grid that holds your oxygen and pressure, because "
               "they lie outside the ranges of the {preset} preset.")
ASSUME_COMPARE_ONLY = "Looked up {label} only; ask again for {others}."
ASSUME_NAMES = "Investigations: {names} all match the name {name}."
ASSUME_UNGROUNDED = "Left out: {field} {value}, because the message does not state it."

FIELD_WORDS = {"environment.o2_pct": "Oxygen", "environment.pressure_kpa": "Pressure",
               "environment.gravity": "Gravity", "environment.flow": "Flow"}

# ---------------------------------------------------------------- notices (9.5)
NOTICES = {
    "refuse_verdict": ("This tool gives no safety verdict: it does not judge whether a material, an atmosphere "
                       "or a design is fit for use. Below is what NASA's recorded tests and documents hold for "
                       "the question, each with its source."),
    "refuse_prediction": ("This tool gives no estimate of what a fire does at conditions the recorded tests did "
                          "not reach, and it offers no fitted model. Below is where your conditions lie against "
                          "the recorded ranges, with the closest recorded tests."),
    "not_in_files": "The team's files do not hold this. To answer it, the files would have to hold {needed}.",
    "out_of_scope": ("This is outside what this tool looks at: NASA's combustion experiments in weightlessness "
                     "from the PSI archive, read for fire safety in crewed environments such as spacecraft, "
                     "stations, bases on the Moon and Mars, and rovers."),
    "help": ("Tell me what you are building and where, in your own words: a cabin, a base on the Moon, a rover or "
             "a spacesuit, a material, a kind of fire-safety equipment, or a fire-safety question. I look up "
             "NASA's recorded tests and documents in the team's files and answer with their sources."),
    "fallback": ("The language model's sentences did not pass the checks, so this answer is put together by team "
                 "code from the facts."),
    # separate texts by the reason of the fallback (added after the red-team run of 15 Nov: the one text above was
    # also shown when the model's reply was not in the required form, which said something untrue)
    "fallback_write": ("The language model's reply was missing or not in the required form, so this answer is put "
                       "together by team code from the facts."),
    "fallback_check": ("The model checker's reply was missing or not in the required form, so the model's sentences "
                       "are not shown and this answer is put together by team code from the facts."),
    "no_model": "No language model ran for this answer: it is put together by team code from the facts.",
}

NEEDED = {
    "material": "a record of tests of {words} in one of PSI's per-test tables",
    "investigation": "a PSI combustion investigation named {name}; the 24 in the team's files are listed in the "
                     "ranking",
    "term": "a definition of '{term}' in the team's specifications",
    "search": "a sentence of the PSI records that uses the words {keywords}",
}

ERROR = "Something went wrong on the assistant server. The dashboard below still works."

# ---------------------------------------------------------------- step labels (10.3)
STEPS = {
    "understand": "Reading your request",
    "plan": "Choosing what to look up",
    "lookup": "Looking up the team's files",
    "write": "Writing from the facts",
    "check": "Checking every sentence",
    "deliver": "Done",
}
SUMMARY = {
    "understand_live": "Read {readers} times ({model_readings} by the model, once by the rule parser); {agree} of "
                       "{fields} fields agree.",
    "understand_no_model": "Read by the rule parser (no language model).",
    "understand_set": "Taken as you set it.",
    "plan": "Looking up {labels}.",
    "plan_none": "Nothing to look up for this message.",
    "lookup": "{facts} facts from {files} files.",
    "write_model": "{written} sentences written by the local model.",
    "write_template": "Answer put together by team code from the facts.",
    "check": "{written} sentences written, {removed} removed by the checks, {repaired} repaired.",
    "check_model": " Model check: {yes} of {checked} supported.",
    "check_none": "No model sentences to check.",
    "check_skipped": " No model check was possible, so no model sentence is shown.",
    "deliver": "Done in {seconds} s with {calls} model calls.",
    "clarify": "One question before looking anything up.",
}

ANSWER_LABELS = {
    "model": ("Written by a local language model (gpt-oss:20b) from the facts shown; every sentence shown passed the "
              "code checks and a second model check. No person reviewed this answer. A research exploration tool, "
              "not safety guidance."),
    "template": ("Put together by team code from the facts shown; no language model wrote it. A research "
                 "exploration tool, not safety guidance."),
    "recorded": ("Recorded on {date} with the local language model (gpt-oss:20b) and replayed here; no model runs "
                 "on this page. Every model sentence shown passed the code checks and a second model check when it "
                 "was recorded. No person reviewed these answers. A research exploration tool, not safety guidance."),
}

# ---------------------------------------------------------------- tools (7)
TOOL_LABELS = {
    "rank_investigations": "the team's ranking of the investigations",
    "counts_per_question": "counts of recorded tests per fire-safety question",
    "tested_range": "where your values lie against the recorded tests",
    "where_the_data_are": "where the data are: NASA's tables, the archive, or no record",
    "tests_table": "the recorded tests in range",
    "modelling_data": "data for predictive modelling",
    "equipment_research": "research behind this kind of equipment",
    "earth_applications": "what the records say about Earth",
    "search_records": "a keyword search of the NASA record sentences",
    "criteria": "criteria in NASA documents",
    "published_results": "results quoted from NASA's documents for this question",
    "files_of_test": "the raw files of a test",
    "investigation_card": "the investigation's record",
    "explain": "definitions from the team's specifications",
}

LIMITS = {
    "rank_investigations": ("The ranking is the team's similarity score over the catalog, not NASA's conclusion and "
                            "not a fire-safety judgement."),
    "counts_per_question": ("A count says how many recorded tests hold the variables of a question; it is not a "
                            "result for this environment and not a judgement of it."),
    "tested_range": "Lying inside the recorded span is not a result at your condition: the span says only where "
                    "tests were run.",
    "where_gap_states": ("A file that names a test is not known to hold a given quantity; 'not found in the files "
                         "opened' is a statement about the files opened."),
    "tests_table": ("Values are copied as NASA's tables give them, through the team's tests.csv; an empty cell is "
                    "not a zero and not a 'no'."),
    "equipment_research": ("The link from a kind of equipment to questions and investigations is the team's rule, "
                           "not NASA's; the quoted sentences are the records' own words."),
    "earth_applications": ("These are the records' own statements of possible applications on Earth; the team has "
                           "not assessed them."),
    "search_records": ("A keyword search over the {n} numbered sentences of the {k} PSI records; a sentence that "
                       "does not use these words is not found."),
    "criteria": "Criteria are quoted from the documents listed; this tool does not apply them to your design.",
    # published_results (added 15 November, after the question set was frozen)
    "published_results": ("These are quotations of NASA documents and of the investigators' papers. The order is "
                          "the team's fixed rule by the conditions each statement gives, with no weights; the team compares nothing with a "
                          "criterion and computes nothing from these values."),
    "published_results_panel": ("{limit} A research exploration tool, not safety guidance. Every quoted result and printed value can be filtered in "
                                "data/pipeline/results_flat.csv: {url}"),
    "files_of_test": ("A file that names a test is not known to hold a given quantity; no file was opened for this "
                      "list."),
}

T = {
    # rank_investigations
    "rank_list": "Closest to this input by the team's ranking, in order: {list}.",
    "rank_result": "{name} ({acc}): closest configuration {config}; {why}.",
    "rank_gap": "{name} ({acc}): {gap}.",
    # counts_per_question
    "counts_cell": "These counts are for a cell of the team's coverage grid, not for your exact values: {label}.",
    # tested_range
    "range_o2": ("{phase} in the team's tables: oxygen of the surrounding atmosphere recorded for {k} of {n}, from "
                 "{lo} to {hi}%{your}."),
    "range_o2_none": "{phase} in the team's tables: oxygen of the surrounding atmosphere recorded for {k} of {n}{your}.",
    "range_o2_your": "; your {value}% is {position}",
    "range_o2_preset": "; the preset's {value}% is {position}",
    "range_p": "{phase}: pressure recorded for {k} of {n}{span}{your}.",
    "range_p_span": ", from {lo} to {hi} kPa",
    "range_p_your": "; your {value} kPa is {position}",
    "range_p_preset": "; the preset's {value} kPa is {position}",
    "range_stream": ("{m} {phase_lower} record the oxygen of an oxidizer stream (an inverse flame), not of a "
                     "surrounding atmosphere; they are left out of the oxygen span."),
    # where_the_data_are (gap states)
    "gap_state": "{need} ({nid}), {var}: {k} of {n} counted tests are in the state '{state}'.",
    "reading_order": ("By the team's reading order (a rule over counts and bytes, not NASA's priority), the first "
                      "file group listed for {var} is {pattern} of {inv} ({files} files, {size})."),
    # tests_table
    "tests_tiers": "{n} recorded tests lie in this environment's ranges or in one of them{qwords}: {tiers}.",
    "tests_tiers_parts": ("{a} with oxygen and pressure both inside, {o} with oxygen inside and no pressure in the "
                          "table, {p} with pressure inside and no oxygen in the table"),
    "tests_cell": "{n} recorded tests have oxygen and pressure both inside this cell{qwords}.",
    "tests_qwords": " and are counted for {need} ({nid})",
    "tests_inv": "{k} of them are {phase} of {name} ({acc}).",
    "tests_cell_limit": "For this cell the tests are those whose recorded oxygen and pressure fall in its bins.",
    "tests_first": "First {n} of {total} rows; the full list is in {file}.",
    # modelling_data
    "ready_row": "{label} ({inv}): {n} tests usable for this label; the team's diagnostic says: {verdict}.",
    "ready_none": "No row of the team's modelling diagnostic is about {need} ({nid}).",
    "ready_need": ("{need} ({nid}): {counted} counted tests; a counted test holds {required} and at least one of "
                   "{outcomes}."),
    # equipment_research
    "equip_list": "By the team's rule, {label} relates to {questions} and to these investigations: {list}.",
    "equip_need": "{need} ({nid}): {n} tests are counted in the team's tables.",
    # NASA sentences
    "nasa_sentence": "{name} ({acc}) record, {field}: \"{sentence}\"",
    # criteria
    "criterion_quote": "{ref}, {where}: \"{quote}\"",
    "criterion_text": "{ref}, {where}, as the team's reference list states it: {text}",
    # published_results (added 15 November)
    "result_quote": "{kind}{doc}, {where}{relation}: \"{quote}\" The team's group for {env}: {group}.",
    "result_relation": " ({relation})",
    "result_counts": ("Question {nid}, {env}: {n} quoted results of NASA's documents are tagged for this question "
                      "and {v} of them carry printed values; by the team's grouping, {a} state oxygen and pressure "
                      "inside this environment's ranges, {b} state one of its conditions inside and none outside, "
                      "and {c} state none of these conditions."),
    "result_none": "Question {nid}, {env}: no quoted result of NASA's documents in the team's file is in these groups.",
    # files_of_test
    "files_level": ("{files} files ({size}) carry the identifier or the test number of {test} in their name, at "
                    "the level '{level}'."),
    "files_kinds": "By kind: {kinds}.",
    "files_none": ("No file of the PSI listing (listing of 14 November 2026) carries the identifier or the test "
                   "number of {test} in its name."),
    # investigation_card
    "card": "{name} ({acc}): {title}; platform {platform}; operations {period}; {tests} tests listed in the catalog{ai}.",
    "card_no_tests": "{name} ({acc}): {title}; platform {platform}; operations {period}; no test count in the catalog{ai}.",
    "card_ai": " (catalog values extracted by an AI session from the PSI record, not checked by a person)",
}

FIELD_LABELS = {"objective": "stated objective", "hypothesis": "stated hypothesis", "approach": "planned approach",
                "researchImpacts": "impact statement", "title": "record title"}
PHASE_WORDS = {"solid": "Solid-fuel tests", "liquid": "Fuel-droplet tests", "gas": "Gas-flame tests"}
PHASE_OF = {"solid": "solid-fuel tests", "liquid": "fuel-droplet tests", "gas": "gas-flame tests",
            "aerosol": "aerosol tests"}
POSITION = {"below": "below the lowest recorded value", "within": "within the recorded span",
            "above": "above the highest recorded value", "none": "not comparable, no value recorded"}
STATE_WORDS = {"in_table": "in NASA's table",
               "column_in_sampled_raw_file": "a column was seen in a sampled raw file, values not read",
               "documented_only": "stated in a document, not in a table",
               "not_in_sampled_files": "not found in the files opened", "no_test_table": "no per-test table"}
TIER_WORDS = {"atmosphere": "oxygen and pressure both inside", "oxygen_only": "oxygen inside, no pressure in the table",
              "pressure_only": "pressure inside, no oxygen in the table", "cell": "inside this cell"}

# ---------------------------------------------------------------- follow-ups (9.1)
FOLLOWUPS = {
    "find_investigations": ["Where are the raw data of these tests?",
                            "What do NASA documents state as criteria for flame spread?"],
    "compare_environments": ["Which recorded tests lie inside the lunar habitat ranges?",
                             "Where are the raw data for the ISS cabin?"],
    "question_evidence": ["Where are the raw data of these tests?",
                          "Which NASA investigations are closest to this environment?"],
    "where_data": ["Which data could support a model of flame extinction?",
                   "What do the records say about smoke detection?"],
    "modelling_data": ["Where are the raw data of the extinction tests?",
                       "What does the readiness verdict mean?"],
    "equipment_research": ["Which recorded tests hold combustion products?",
                           "Which recorded tests hold extinction conditions?"],
    "earth_applications": ["Which NASA investigations study smoke detection?",
                           "Which data could support a model of flame extinction?"],
    "explain": ["Which NASA investigations are closest to a lunar habitat?",
                "What does a counted test mean?"],
    "help": ["Which NASA experiments are closest to a cotton fabric fire in a lunar habitat?",
             "What research is behind smoke detectors for spacecraft?"],
    "out_of_scope": ["Which NASA experiments are closest to a cotton fabric fire in a lunar habitat?",
                     "What do the records say about applications on Earth?"],
}
