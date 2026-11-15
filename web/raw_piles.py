"""Builds the "three piles" block of the dashboard (pm request 20261115-0035, step 8 of
docs/raw_data_design/design.md): for an environment and each fire-safety question, where the data
are: in NASA's tables / in the archive but not in a table / no record in PSI.

AI-generated code: written with an AI assistant (Claude Code, ui role) during the NASA Space Apps
Challenge 2026 hackathon (2026-11-15). No language model runs here or on the page: every sentence is a
fixed template of docs/raw_data_design/pile_wording.md with its slots filled from the team's files.

Inputs (read-only):
- placements: data/pipeline/scenario_tests.csv (oxygen and pressure match per test), checked against
  the placement fixture F1 of pile_wording.md;
- locations: data/pipeline/question_chain.csv when the data role has written it, else the prototype
  docs/raw_data_design/prototype/chain_lunar_habitat.csv (lunar habitat only);
- file links: data/pipeline/file_links_summary.json when it exists, else the prototype
  lunar_summary.json and lunar_links_PSI-*.json (lunar habitat only);
- tests.csv, need_tests.csv, values_long.csv, raw_inventory.json, pipeline/spec/{needs,scenarios,
  answers,references,raw_columns}.json, data/catalog/investigations.csv,
  docs/raw_data_design/psi_metadata_summary.md (the Flight Platform field).
A check that fails raises PileError, and web/build.py stops.
"""
import collections
import csv
import json
import os
import re

SCENARIOS = ["lunar_habitat", "iss"]  # the two demo environments get the full block (pm 0035)
# the other environments get the header line and the bars only (pm 0035: "the other four environments the bars only")
BARS_ONLY = ["mars_habitat", "spacesuit", "exploration_8_2_34", "exploration_10_2_26_5"]

PLACEMENT_LABEL = {
    "inside": "inside",
    "cannot_be_placed_from_table": "cannot be placed from the tables",
    "oxygen_of_oxidizer_stream": "oxygen recorded for an oxidizer stream",
    "outside_by_recorded_value": "outside by a recorded value",
    "no_range_set": "no range set",
}
PLACEMENT_ORDER = list(PLACEMENT_LABEL)
# the prototype chain's names, mapped to the names of pile_wording.md section 2
PLACEMENT_ALIASES = {"outside_by_table_value": "outside_by_recorded_value", "oxygen_is_of_oxidizer_stream": "oxygen_of_oxidizer_stream"}
LOCATION_ALIASES = {"raw_file_column": "raw_file_column_seen", "not_found_in_sampled_files": "not_found_in_files_opened"}

# Placement fixture F1 (pile_wording.md section 0): S1 counts over all 1,824 tests, and the solid-fuel scope.
F1 = {
    ("lunar_habitat", "all"): {"inside": 26, "cannot_be_placed_from_table": 676, "oxygen_of_oxidizer_stream": 63, "outside_by_recorded_value": 1059},
    ("lunar_habitat", "solid"): {"inside": 0, "cannot_be_placed_from_table": 237, "outside_by_recorded_value": 139},
    ("iss", "all"): {"inside": 179, "cannot_be_placed_from_table": 739, "oxygen_of_oxidizer_stream": 106, "outside_by_recorded_value": 800},
    ("mars_habitat", "all"): {"no_range_set": 1824},
}

VAR_WORDS = {
    "test_end": "how the burn ended", "extinction_diameter_mm": "extinction diameter", "flow_event": "flow event",
    "flow_cms": "flow speed", "flow_min_cms": "lowest flow speed", "co2_pct": "carbon dioxide in the atmosphere",
    "he_pct": "helium in the atmosphere", "burn_time_s": "burn time", "burn_length_cm": "burn length",
    "o2_consumed_pct_points": "oxygen consumed", "spread_rate_mm_s": "spread rate", "hot_ignition": "hot ignition",
    "co_produced_ppm": "carbon monoxide produced", "co2_produced_pct_points": "carbon dioxide produced",
    "co_to_co2_molar_ratio": "ratio of carbon monoxide to carbon dioxide", "smoke_particle_size_um": "smoke particle size",
    "o2_pct": "oxygen", "pressure_kpa": "pressure", "fuel_material": "fuel", "sample_geometry": "sample shape",
    "sample_thickness_mm": "sample thickness", "flow_direction": "flow direction", "gravity_level": "gravity",
}
FUEL_FORM = {"liquid": "fuel-droplet tests", "gas": "gas flames", "solid": "solid-fuel tests"}
FUEL_FORM_OF = {"liquid": "fuel-droplet tests", "gas": "gas flames", "solid": "solid-fuel tests"}
PLATFORM_WORDS = {"International Space Station (ISS)": "the ISS", "Cygnus Spacecraft": "the Cygnus spacecraft"}
BANNED = ["safe", "unsafe", "will", "predict", "likely"]
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


class PileError(RuntimeError):
    pass


def _csv(path):
    with open(path, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def _json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def n_(x):
    return f"{int(x):,}"


def size(b):
    """One rounding rule for the whole block, decimal units (raw_inventory.json _meta.units)."""
    b = float(b)
    for unit, f in (("TB", 1e12), ("GB", 1e9), ("MB", 1e6), ("kB", 1e3)):
        if b >= f:
            v = b / f
            return f"{v:.2f} {unit}" if v < 100 else f"{v:.1f} {unit}"
    return f"{int(b)} bytes"


def plural(n, one, many):
    return one if int(n) == 1 else many


def num(v):
    s = f"{float(v):.1f}".rstrip("0").rstrip(".")
    return s


def cap(s):
    return s[:1].upper() + s[1:]


def listing_words(iso):
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", iso or "")
    if not m:
        raise PileError("raw_inventory.json: listings_fetched_at has no date")
    return f"{int(m.group(3))} {MONTHS[int(m.group(2)) - 1]} {m.group(1)}"


def range_words(rw, var, r):
    if not r:
        return None
    lo, hi = r.get("min"), r.get("max")
    w = rw[var]
    if lo is not None and hi is not None:
        t = w["both_max_inclusive" if r.get("max_inclusive") else "both_max_exclusive"]
    elif hi is not None:
        t = w["max_only_inclusive" if r.get("max_inclusive") else "max_only_exclusive"]
    else:
        t = w["min_only"]
    return t.replace("{min}", num(lo) if lo is not None else "").replace("{max}", num(hi) if hi is not None else "")


def joined(parts, last="and"):
    parts = [p for p in parts if p]
    if len(parts) <= 1:
        return "".join(parts)
    return ", ".join(parts[:-1]) + f" {last} " + parts[-1]


def placement_of(o2, p):
    """Placement of a test in an environment (design.md 3.1, link 2), from scenario_tests.csv."""
    if o2 == "not_specified" and p == "not_specified":
        return "no_range_set"
    if o2 == "in" and p == "in":
        return "inside"
    if o2 == "out" or p == "out":
        return "outside_by_recorded_value"
    if o2 == "not_ambient":
        return "oxygen_of_oxidizer_stream"
    return "cannot_be_placed_from_table"


def platform_values(root):
    """The Flight Platform field per investigation, from the table in psi_metadata_summary.md."""
    path = os.path.join(root, "docs", "raw_data_design", "psi_metadata_summary.md")
    out = {}
    if not os.path.exists(path):
        return out
    for line in open(path, encoding="utf-8"):
        m = re.match(r"\|\s*`([^`]+)`\s*\|\s*\d+:\s*(.+?)\s*\|\s*$", line)
        if not m:
            continue
        value, invs = m.group(1), m.group(2)
        nums = re.findall(r"\d+", invs)
        for k in nums:
            out[f"PSI-{k}"] = value
    return out


def build(root):
    P = lambda *a: os.path.join(root, *a)  # noqa: E731
    tests = {r["test_id"]: r for r in _csv(P("data", "pipeline", "tests.csv"))}
    st_all = _csv(P("data", "pipeline", "scenario_tests.csv"))
    need_tests = collections.defaultdict(dict)
    for r in _csv(P("data", "pipeline", "need_tests.csv")):
        need_tests[r["need_id"]][r["test_id"]] = r.get("objective_link", "")
    needs = _json(P("pipeline", "spec", "needs.json"))["needs"]
    scen = {s["id"]: s for s in _json(P("pipeline", "spec", "scenarios.json"))["scenarios"]}
    answers = _json(P("pipeline", "spec", "answers.json"))
    rw = answers["range_words"]
    forbidden = [w.lower() for w in answers.get("forbidden_words", []) if isinstance(w, str)]
    refs = {r["id"]: r for r in _json(P("pipeline", "spec", "references.json")).get("references", _json(P("pipeline", "spec", "references.json")))} \
        if isinstance(_json(P("pipeline", "spec", "references.json")), dict) else {}
    inv_meta = _json(P("data", "pipeline", "raw_inventory.json"))["_meta"]
    totals = inv_meta.get("totals") or {}
    archive_files, archive_bytes = totals.get("files"), totals.get("bytes")
    n_inv = totals.get("investigations")
    if not (archive_files and archive_bytes and n_inv):
        raise PileError("raw_inventory.json: _meta.totals lacks files, bytes or investigations")
    listing = listing_words(inv_meta.get("listings_fetched_at"))
    short = {r["psi_accession"]: r["investigation_id"] for r in _csv(P("data", "catalog", "investigations.csv"))}
    inv_label = lambda acc: f"{short.get(acc, acc)} ({acc})"  # noqa: E731
    raw_cols = {e["investigation_id"]: e for e in _json(P("pipeline", "spec", "raw_columns.json"))["investigations"]}
    platforms = platform_values(root)

    # o2 values per test as NASA's table writes them, with source column and file (for pile 3, ground 2)
    o2_src = {}
    col_count = collections.defaultdict(collections.Counter)
    for r in _csv(P("data", "pipeline", "values_long.csv")):
        if r["variable"] == "o2_pct" and r["test_id"] not in o2_src:
            o2_src[r["test_id"]] = (r.get("source_column", ""), r.get("source_file", ""))
        col_count[(r["investigation_id"], r["variable"])][r.get("source_column", "")] += 1
    # the table column of each outcome per investigation, as values_long.csv names it
    col_of = {k: c.most_common(1)[0][0] for k, c in col_count.items() if c and c.most_common(1)[0][0] and "constant" not in c.most_common(1)[0][0]}
    raw_cache = {}

    def table_cell(source_file, source_row, column):
        """The cell text as NASA's table file writes it, by the line the row starts on (header = line 1)."""
        if source_file not in raw_cache:
            path = P("data", "psi", "experimental_tables", source_file)
            if not os.path.exists(path):
                raw_cache[source_file] = None
            else:
                text = open(path, "rb").read()
                for enc in ("utf-8-sig", "cp1252", "latin-1"):
                    try:
                        text = text.decode(enc)
                        break
                    except UnicodeDecodeError:
                        continue
                import io
                rd = csv.reader(io.StringIO(text))
                hdr = next(rd)
                rows, start = {}, rd.line_num + 1
                for row in rd:
                    rows[start] = row
                    start = rd.line_num + 1
                raw_cache[source_file] = (hdr, rows)
        got = raw_cache[source_file]
        if not got or column not in got[0] or not str(source_row).isdigit():
            return None
        row = got[1].get(int(source_row))
        if row is None:
            return None
        i = got[0].index(column)
        return row[i] if i < len(row) else ""

    ro_path = P("data", "catalog", "reading_order.csv")
    reading_order = _csv(ro_path) if os.path.exists(ro_path) else []
    vs_path = P("video", "data", "video_links_summary.json")
    vsum = _json(vs_path) if os.path.exists(vs_path) else None
    fls_path = P("data", "pipeline", "file_links_summary.json")
    fls = _json(fls_path) if os.path.exists(fls_path) else None
    sheets_path = P("data", "pipeline", "flex_sheet_vs_table.csv")
    sheets = collections.defaultdict(dict)  # test_id -> key -> row (the 272 FLEX test sheets, pm 0035 step 4)
    if os.path.exists(sheets_path):
        for r in _csv(sheets_path):
            sheets[r["test_id"]][r["key"]] = r

    chain_path = P("data", "pipeline", "question_chain.csv")
    chain_src = "data/pipeline/question_chain.csv"
    if not os.path.exists(chain_path):
        chain_path = P("docs", "raw_data_design", "prototype", "chain_lunar_habitat.csv")
        chain_src = "docs/raw_data_design/prototype/chain_lunar_habitat.csv (prototype)"
    chain = []
    for r in _csv(chain_path):
        r = dict(r)
        r["placement"] = PLACEMENT_ALIASES.get(r["placement"], r["placement"])
        r["location"] = LOCATION_ALIASES.get(r["location"], r["location"])
        chain.append(r)

    out = {}
    all_text = []
    for sid in SCENARIOS:
        sc = scen[sid]
        ranges = sc.get("ranges") or {}
        st = [r for r in st_all if r["scenario_id"] == sid]
        place = {r["test_id"]: placement_of(r["o2_match"], r["pressure_match"]) for r in st}
        ch = [r for r in chain if r["scenario_id"] == sid]
        inside_all = sorted(t for t, p in place.items() if p == "inside")

        # F1 fixture: placements over all tests and over solid fuels
        for scope, want in ((s, w) for (s_id, s), w in F1.items() if s_id == sid):
            pool = [t for t in place if scope == "all" or tests[t]["fuel_phase"] == scope]
            got = collections.Counter(place[t] for t in pool)
            if any(got.get(k, 0) != v for k, v in want.items()) or sum(got.values()) != sum(want.values()):
                raise PileError(f"{sid} {scope}: placements {dict(got)} differ from fixture F1 {want}")

        o2w = range_words(rw, "o2_pct", ranges.get("o2_pct"))
        pw = range_words(rw, "pressure_kpa", ranges.get("pressure_kpa"))
        grav = sc.get("gravity_level") or ""
        header = [f"{sc['label']}: oxygen {o2w}, pressure {pw}, {grav if grav.endswith('gravity') else grav + ' gravity'}.",
                  f"NASA's PSI archive lists {n_(archive_files)} files ({size(archive_bytes)}) for {n_(n_inv)} combustion investigations (listing of {listing})."]

        # 1.3 and 1.4: file links (data's summary, else the lunar prototype)
        links = None
        if fls and sid in fls.get("scenarios", {}):
            # the data role's file links (pm 0035 step 3, data/pipeline/file_links_summary.json)
            s = fls["scenarios"][sid]
            ls = s.get("by_link_state", {})
            pairs = collections.Counter(f.get("candidate_tests", "") for f in s.get("labels_disagree_files", []))
            links = {"files": s["files_naming_inside_tests"], "bytes": s["bytes"], "share": s["bytes"] / archive_bytes,
                     "small_files": s["small_files"], "small_bytes": s["small_bytes"],
                     "agree": ls.get("two_labels_agree", {}).get("files", 0), "one": ls.get("one_label", {}).get("files", 0),
                     "disagree": ls.get("labels_disagree", {}).get("files", 0), "pairs": pairs,
                     "tests_inside": s["tests_inside"], "source": "data/pipeline/file_links_summary.json"}
            if links["tests_inside"] != len(inside_all):
                raise PileError(f"{sid} links: tests inside {links['tests_inside']} != {len(inside_all)} from scenario_tests.csv")
            if s["small_files"] + s["archive_and_video_files"] != s["files_naming_inside_tests"]:
                raise PileError(f"{sid} links: small plus archive files differ from the files naming the tests")
            # fixture F3 (pile_wording.md section 0)
            if sid == "lunar_habitat" and (links["files"], links["bytes"], links["agree"], links["one"], links["disagree"]) != (398, 104358456350, 336, 47, 15):
                raise PileError(f"lunar links differ from fixture F3: {links['files']}, {links['bytes']}, {links['agree']} / {links['one']} / {links['disagree']}")
        elif sid == "lunar_habitat":
            s = _json(P("docs", "raw_data_design", "prototype", "lunar_summary.json"))
            l69 = _json(P("docs", "raw_data_design", "prototype", "lunar_links_PSI-69.json"))
            l159 = _json(P("docs", "raw_data_design", "prototype", "lunar_links_PSI-159.json"))
            tot = s["files_naming_inside_tests"]["total"]
            folder = collections.Counter()
            for e in l69["by_label_and_folder"]:
                folder[e["folder"]] += e["files"]
            for e in l159["by_folder"]:
                folder[e["folder"]] += e["files"]
            if sum(folder.values()) != tot["files"]:
                raise PileError(f"lunar links: second-label files {sum(folder.values())} != {tot['files']}")
            other = collections.Counter()
            for test_no, _name, folder_path in l69.get("folder_names_another_test", []):
                m = re.search(r"FLEX_0*(\d+)", folder_path)
                other[(int(test_no), int(m.group(1)) if m else None)] += 1
            links = {"files": tot["files"], "bytes": tot["bytes"], "share": tot["share_of_archive_bytes"],
                     "small_files": tot["small_files"], "small_bytes": tot["small_bytes"],
                     "agree": folder.get("folder_agrees", 0), "no_test": folder.get("folder_names_no_test", 0),
                     "other_test": folder.get("folder_names_another_test", 0), "other_detail": other,
                     "tests_inside": s["tests_inside_o2_and_pressure"]["all"], "source": "docs/raw_data_design/prototype/lunar_summary.json, lunar_links_PSI-69.json, lunar_links_PSI-159.json (prototype)"}
            if links["tests_inside"] != len(inside_all):
                raise PileError(f"lunar links: tests inside {links['tests_inside']} != {len(inside_all)} from scenario_tests.csv")
        if links:
            big_files, big_bytes = links["files"] - links["small_files"], links["bytes"] - links["small_bytes"]
            header.append(f"{n_(links['files'])} of them ({size(links['bytes'])}, {links['share'] * 100:.2f}% of the bytes) carry in their name the NASA identifier or the test number of one of the {n_(links['tests_inside'])} tests recorded inside these oxygen and pressure ranges: {n_(links['small_files'])} files that are not an archive or a video recording ({size(links['small_bytes'])}) and {n_(big_files)} archives and video recordings ({size(big_bytes)}).")
            if "pairs" in links:
                # 1.4 in the data role's link states (its names win over the template's, pile_wording.md section 0)
                clauses = [f"Two labels that NASA wrote (file name, PSI folder, or the identifier inside a test sheet) name the same test for {n_(links['agree'])} of them"]
                if links["one"]:
                    clauses.append(f"{n_(links['one'])} {plural(links['one'], 'carries', 'carry')} one label")
                if links["disagree"]:
                    top = links["pairs"].most_common(2)
                    rest = links["disagree"] - sum(c for _, c in top)
                    det = joined([f"{n_(c)} {plural(c, 'file', 'files')} naming {p.replace('+', ' and ')}" for p, c in top] + ([f"{n_(rest)} more"] if rest > 0 else []))
                    clauses.append(f"for {n_(links['disagree'])} the labels name different tests ({det})")
                header.append("; ".join(clauses) + ". The team lists these cases and does not resolve them.")
            else:
                clauses = [f"File name and PSI folder name the same test for {n_(links['agree'])} of them"]
                if links["no_test"]:
                    clauses.append(f"{n_(links['no_test'])} {plural(links['no_test'], 'sits', 'sit')} in a folder that names no test")
                if links["other_test"]:
                    det = joined([f"{n_(c)} files of FLEX-{a} in a folder named after FLEX-{b}" for (a, b), c in sorted(links["other_detail"].items())])
                    clauses.append(f"{n_(links['other_test'])} {plural(links['other_test'], 'sits', 'sit')} in a folder that names another test ({det})")
                header.append("; ".join(clauses) + ". The team lists these cases and does not resolve them.")
        # 1.5 the tests inside
        if inside_all:
            by_inv = collections.defaultdict(list)
            for t in inside_all:
                by_inv[tests[t]["investigation_id"]].append(t)
            frags = []
            for acc, ts in sorted(by_inv.items(), key=lambda kv: -len(kv[1])):
                phases = {tests[t]["fuel_phase"] for t in ts}
                pk = sorted(float(tests[t]["pressure_kpa"]) for t in ts)
                pwd = f"{num(pk[0])} kPa" if pk[0] == pk[-1] else f"{num(pk[0])} to {num(pk[-1])} kPa"
                form = FUEL_FORM.get(phases.pop(), "tests") if len(phases) == 1 else "tests"
                frags.append(f"{len(ts)} {form} ({short.get(acc, acc)}, {pwd})")
            gl = collections.Counter(tests[t]["gravity_level"] for t in inside_all)
            gwords = next(iter(gl)) if len(gl) == 1 else joined([f"{k} for {v}" for k, v in gl.items()])
            header.append(f"The {len(inside_all)} tests are {joined(frags)}, all in {gwords}.")
        if links:
            header.append("A file that names a test is not shown to hold what a question needs. The counts are the team's computation from PSI's file listing and NASA's tables, not NASA's conclusions.")
            if sc.get("caveat"):
                header.append(sc["caveat"])

        need_out = []
        counted_list = []
        for nd in needs:
            nid, scope = nd["id"], (nd.get("scope") or {}).get("fuel_phase")
            pool = [t for t in place if not scope or tests[t]["fuel_phase"] in scope]
            scope_words = "all fuel phases" if not scope else joined([f"{p} fuels" for p in scope])
            seg = collections.Counter(place[t] for t in pool)
            if sum(seg.values()) != len(pool):
                raise PileError(f"{sid} {nid}: bar segments do not sum to the tests in scope")
            stated = {t for t, link in need_tests[nid].items() if link == "stated"}
            counted_list.append(f"{nid} {len(stated)}")
            segs = [(k, seg[k]) for k in PLACEMENT_ORDER if seg.get(k)]
            bar = f"{nd['name']} ({nid}), {n_(len(pool))} tests of {scope_words}: " + " | ".join(f"{PLACEMENT_LABEL[k]} {n_(v)}" for k, v in segs) + "."
            inside = [t for t in pool if place[t] == "inside"]
            counted_in = [t for t in inside if t in stated]
            # cross-check with the chain where it exists
            if ch:
                rows = [r for r in ch if r["need_id"] == nid and r["variable"] == "o2_pct" and r.get("row_kind", "quantity") == "quantity"]
                if rows:
                    c_inside = sum(int(r["in_scope_tests"] or 0) for r in rows if r["placement"] == "inside")
                    c_counted = sum(int(r["counted_tests"] or 0) for r in rows if r["placement"] == "inside")
                    if c_inside != len(inside) or c_counted != len(counted_in):
                        raise PileError(f"{sid} {nid}: chain inside {c_inside}/{c_counted} != {len(inside)}/{len(counted_in)}")
            p1, p2, shelf, p3 = [], [], [], []
            # ---- pile 1
            if not inside:
                p1.append(f"{n_(len(inside))} of the {n_(len(pool))} tests of {scope_words} are recorded inside these ranges.")
            for acc in sorted({tests[t]["investigation_id"] for t in counted_in}):
                ts = [t for t in counted_in if tests[t]["investigation_id"] == acc]
                phases = sorted({tests[t]["fuel_phase"] for t in ts})
                fuels = sorted({tests[t]["fuel_material"] for t in ts if tests[t]["fuel_material"]})
                o2s = sorted({float(tests[t]["o2_pct"]) for t in ts})
                o2words = joined([f"{num(v)}%" for v in o2s], "or") if len(o2s) <= 3 else f"{num(o2s[0])} to {num(o2s[-1])}%"
                pk = sorted(float(tests[t]["pressure_kpa"]) for t in ts)
                gl = sorted({tests[t]["gravity_level"] for t in ts})
                form = FUEL_FORM.get(phases[0], "tests") if len(phases) == 1 else "tests"
                s = (f"{len(ts)} {plural(len(ts), 'test', 'tests')} counted for this question: {inv_label(acc)} {form}, "
                     f"{' or '.join(phases)} {' or '.join(fuels)}, {' and '.join(gl)}, oxygen {o2words}, {num(pk[0])} to {num(pk[-1])} kPa.")
                if not (form in s and "kPa" in s and any(g in s for g in gl)):
                    raise PileError(f"{sid} {nid}: the counted-tests line lacks fuel form, gravity or pressure")
                p1.append(s)
                frs = []
                for v in nd.get("outcomes_any", []):
                    vals = [tests[t].get(v, "") for t in ts]
                    have = [x for x in vals if x not in ("", None)]
                    fr = f"{VAR_WORDS.get(v, v)} {len(have)} of {len(ts)}"
                    if have and v in ("test_end", "flow_event"):
                        cnt = collections.Counter(have)
                        fr += " (" + ", ".join(f"{c} {k}" for k, c in cnt.most_common()) + ")"
                    frs.append(fr)
                if frs:
                    p1.append("Recorded for them in NASA's table: " + "; ".join(frs) + ".")
                # 4.3 pile1.codes: the cell text of NASA's table file itself (tests.csv turns blank and dash both into empty)
                for v in nd.get("outcomes_any", []):
                    col = col_of.get((acc, v))
                    if not col:
                        continue
                    codes = collections.Counter()
                    for t in ts:
                        cell = table_cell(tests[t]["source_file"], tests[t]["source_row"], col)
                        if cell is None:
                            raise PileError(f"{sid} {nid}: {t} has no row {tests[t]['source_row']} or column {col!r} in {tests[t]['source_file']}")
                        c = cell.strip()
                        if c == "":
                            codes["blank"] += 1
                        elif c in ("-", "–", "—"):
                            codes["dash"] += 1
                        else:
                            try:
                                codes["zero" if float(c) == 0 else "number"] += 1
                            except ValueError:
                                codes["other"] += 1
                    # fixture F5 (design.md section 7): the 17 lunar FLEX tests write 4 numbers, 2 zeros, 8 blanks, 3 dashes
                    if (sid, nid, acc, v) == ("lunar_habitat", "S1", "PSI-69", "extinction_diameter_mm") and \
                            (codes["number"], codes["zero"], codes["blank"], codes["dash"]) != (4, 2, 8, 3):
                        raise PileError(f"lunar S1 extinction diameter codes {dict(codes)} differ from fixture F5 (4, 2, 8, 3)")
                    if (codes["blank"] or codes["dash"]) and not codes["other"]:
                        p1.append(f"{cap(VAR_WORDS.get(v, v))} as the table writes it: a number above zero for {codes['number']}, a zero for {codes['zero']}, blank for {codes['blank']}, a dash for {codes['dash']}.")
            not_counted = [t for t in inside if t not in stated]
            for acc in sorted({tests[t]["investigation_id"] for t in not_counted}):
                ts = [t for t in not_counted if tests[t]["investigation_id"] == acc]
                n_ns = sum(1 for t in ts if need_tests[nid].get(t) == "not_stated")
                n_no = sum(1 for t in ts if t not in need_tests[nid])
                if n_ns + n_no != len(ts):
                    raise PileError(f"{sid} {nid} {acc}: a test inside is not counted for a third reason")
                phases = sorted({tests[t]["fuel_phase"] for t in ts})
                pk = sorted(float(tests[t]["pressure_kpa"]) for t in ts)
                o2 = sorted(float(tests[t]["o2_pct"]) for t in ts)
                pwd = f"{num(pk[0])} kPa" if pk[0] == pk[-1] else f"{num(pk[0])} to {num(pk[-1])} kPa"
                reasons = []
                if n_ns:
                    reasons.append(f"for {n_ns} of them the PSI record of that investigation does not state this purpose, as the team read it")
                if n_no:
                    reasons.append(f"{n_no} {plural(n_no, 'holds', 'hold')} no outcome of this question in NASA's table")
                more = "more " if counted_in else ""
                o2wd = f"{num(o2[0])}%" if o2[0] == o2[-1] else f"{num(o2[0])} to {num(o2[-1])}%"
                p1.append(f"{len(ts)} {more}{plural(len(ts), 'test', 'tests')} inside the ranges: {FUEL_FORM_OF.get(phases[0], 'tests') if len(phases) == 1 else 'tests'} of {inv_label(acc)}, "
                          f"recorded at {pwd} and oxygen {o2wd}. Not counted: {'; '.join(reasons)}.")
            # ---- pile 3
            if grav and grav != "microgravity":
                gvals = collections.Counter(tests[t]["gravity_level"] for t in pool)
                if len(gvals) == 1 and next(iter(gvals)) != grav:
                    tables = len({tests[t]["source_file"] for t in pool})
                    invs = sorted({tests[t]["investigation_id"] for t in pool})
                    pv = collections.Counter(platforms.get(a) for a in invs)
                    if None in pv:
                        raise PileError(f"{sid} {nid}: Flight Platform not found for {[a for a in invs if a not in platforms]}")
                    frs = []
                    for value, c in pv.most_common():
                        words = PLATFORM_WORDS.get(value, value)
                        frs.append(f"{words} for {c} of the {len(invs)} mapped investigations" if c > 1 else
                                   f"{words} for {[a for a in invs if platforms[a] == value][0]}")
                    item = refs.get("CH.partial_gravity")
                    second = ""
                    if item:
                        clause = re.split(r";\s*", item["text"])[0].rstrip(".")
                        second = f" The challenge statement says that {clause} (reference item CH.partial_gravity, the team's summary)."
                    level = cap(grav if grav.endswith("gravity") else grav + " gravity")
                    p3.append(f"{level}: 0 of {n_(len(pool))} tests. Ground: the team's mapping sets {next(iter(gvals))} for each of the {tables} per-test tables ({n_(len(pool))} of {n_(len(pool))} tests); no table has a column for it; the PSI record's Flight Platform field names {joined(frs)}.{second}")
            counted_all = [t for t in pool if t in stated]
            if counted_all and ranges.get("o2_pct"):
                o2r = ranges["o2_pct"]
                sides = set()
                ok = True
                for t in counted_all:
                    row = next((r for r in st if r["test_id"] == t), None)
                    v = tests[t].get("o2_pct")
                    if not row or row["o2_match"] != "out" or not v:
                        ok = False
                        break
                    v = float(v)
                    sides.add("below" if o2r.get("min") is not None and v < o2r["min"] else "above" if o2r.get("max") is not None and v > o2r["max"] else "?")
                if ok and len(sides) == 1 and "?" not in sides:
                    side = sides.pop()
                    bound = o2r["min"] if side == "below" else o2r["max"]
                    vals = sorted(float(tests[t]["o2_pct"]) for t in counted_all)
                    by = collections.Counter(tests[t]["investigation_id"] for t in counted_all)
                    srcs = collections.Counter(o2_src.get(t, ("", "")) for t in counted_all)
                    if ("", "") in srcs:
                        raise PileError(f"{sid} {nid}: an oxygen value has no source column in values_long.csv")
                    p3.append(f"This gap is not unprocessed data: PSI's tables hold no counted test of this question inside these ranges (listing of {listing}). "
                              f"All {n_(len(counted_all))} counted tests ({joined([f'{c} {short.get(a, a)}' for a, c in by.most_common()])}) have their oxygen in NASA's table, "
                              f"between {num(vals[0])} and {num(vals[-1])}%, {side} this environment's {num(bound)}%. Placement uses the table value, so reading raw files does not move one of them in. "
                              f"Source: {'; '.join(f'column {c} of {f} ({k} tests)' for (c, f), k in srcs.most_common())}.")
            # ---- pile 2 (lines for the counted tests inside; data's chain gives the locations)
            for acc in sorted({tests[t]["investigation_id"] for t in counted_in}):
                n_in = sum(1 for t in counted_in if tests[t]["investigation_id"] == acc)
                rc = raw_cols.get(acc, {})
                # 7.1 to 7.3: the per-test sheets read by the data role's code (flex_sheet_vs_table.csv)
                tsh = [t for t in counted_in if tests[t]["investigation_id"] == acc and t in sheets]
                if tsh and "extinction_diameter_mm" in nd.get("outcomes_any", []):
                    agree = lambda t, k: (sheets[t].get(k) or {}).get("agreement", "").startswith("agrees")  # noqa: E731
                    files = {sheets[t]["CIR Test Number"]["psi_file_name"]: int(sheets[t]["CIR Test Number"]["bytes"] or 0) for t in tsh if "CIR Test Number" in sheets[t]}
                    read = len(files)
                    p2.append(f"Per-test sheets of these {len(tsh)} tests (FLEX-nnn_TestSheet.txt, {read} {plural(read, 'file', 'files')}, {n_(sum(files.values()))} bytes; {read} of {read} read). "
                              f"The identifier printed inside equals the table's in {sum(agree(t, 'CIR Test Number') for t in tsh)} of {read}. "
                              f"Pressure agrees with NASA's table in {sum(agree(t, 'Pressure (atm)') for t in tsh)} of {read}, oxygen in {sum(agree(t, 'O2 Mole Fraction') for t in tsh)} of {read}.")
                    TW = {"number": "a number above zero", "zero": "0", "blank": "blank", "dash": "a dash"}
                    SW = {"number": "a number", "nan": "nan", "zero": "0.00", "text": "text"}
                    cls = collections.defaultdict(list)
                    for t in tsh:
                        d = sheets[t].get("Dext (mm)")
                        if d:
                            cls[(d["table_form"], d["sheet_form"])].append((t, d["sheet_value_as_written"], d["table_cell_as_written"]))
                    order_t = ["number", "zero", "blank", "dash"]
                    order_s = ["number", "nan", "zero"]
                    # fixture F5 (design.md section 7): the 17 lunar sheets against NASA's table
                    if sid == "lunar_habitat" and acc == "PSI-69":
                        got = {k: len(v) for k, v in cls.items()}
                        want = {("number", "number"): 3, ("number", "nan"): 1, ("zero", "zero"): 2, ("blank", "number"): 2, ("blank", "nan"): 6, ("dash", "number"): 1, ("dash", "zero"): 1, ("dash", "nan"): 1}
                        if got != want:
                            raise PileError(f"lunar FLEX sheets against the table {got} differ from fixture F5")
                    for (tf, sf) in sorted(cls, key=lambda k: (order_t.index(k[0]) if k[0] in order_t else 9, order_s.index(k[1]) if k[1] in order_s else 9)):
                        items = cls[(tf, sf)]
                        ids = ", ".join(f"{t} ({v})" if sf == "number" else f"{t} (“{v}”)" if sf == "text" else (f"{t} (table {c})" if tf == "number" else t)
                                        for t, v, c in sorted(items, key=lambda x: int(x[0].split("-")[1])))
                        p2.append(f"Extinction diameter: NASA's table writes {TW.get(tf, tf)}, the sheet's line Dext (mm) writes {SW.get(sf, sf)}: {ids}. Read from NASA's file, not adopted, not counted.")
                    codes = [c for c in ("nan", "0.00") if any(sf == {"nan": "nan", "0.00": "zero"}[c] for (_, sf) in cls)] + \
                            (["a text in the sheet"] if any(sf == "text" for (_, sf) in cls) else []) + \
                            [c for c in ("a blank", "a dash") if any(tf == {"a blank": "blank", "a dash": "dash"}[c] for (tf, _) in cls)]
                    if codes:
                        p2.append(f"Read from NASA's raw files by the team's code. Not a table value, not counted. No file opened so far says what {joined(codes, 'or')} mean, or whether the sheet's line is the visible-flame extinction diameter of the table.")
                for r in [r for r in ch if r["need_id"] == nid and r["investigation_id"] == acc and r["placement"] == "inside" and int(r["counted_tests"] or 0) > 0 and r.get("row_kind", "quantity") == "quantity"]:
                    v = r["variable"]
                    if r["location"] == "raw_file_column_seen":
                        groups = [g.strip() for g in (r.get("file_groups") or "").split("|") if g.strip()]
                        ents = [e for e in rc.get("entries", []) if e.get("standard_variable") == v and e.get("group") in groups]
                        headers = sorted({e["header_as_written"] for e in ents})
                        p2.append(f"{cap(VAR_WORDS.get(v, v))}: not in NASA's table for {r['in_scope_tests']} of the {n_in} tests. "
                                  f"A header {' or '.join(headers)} was seen in {len(ents)} opened {plural(len(ents), 'file', 'files')} of the file {plural(len(groups), 'group', 'groups')} these belong to "
                                  f"({n_(r['files'])} files, {size(r['bytes'])}). Not read.")
                    elif r["location"] == "not_found_in_files_opened":
                        rel = [e for e in rc.get("related_columns_not_mapped", []) if e.get("for_variable") == v]
                        clause = ""
                        if rel:
                            hs = [h.strip() for e in rel for h in e["header_as_written"].split(", ") if h.strip()]
                            gs = {e.get("group") for e in rel}
                            reason = re.split(r";\s*", rel[0].get("not_mapped_because", ""))[0]
                            clause = f" ({len(hs)} {plural(len(hs), 'header', 'headers')} seen in {len(gs)} opened {plural(len(gs), 'file', 'files')} and not mapped: {', '.join(hs)}; {reason})"
                        un = [g for g in rc.get("unopened_groups", []) if g.get("kind") == "documents_not_opened"]
                        tail = ""
                        if un:
                            uf = sum(int(g.get("files_in_listing") or 0) for g in un)
                            ub = sum(int(g.get("bytes_in_listing") or 0) for g in un)
                            tail = f" Not opened: {n_(uf)} {plural(uf, 'file', 'files')} ({size(ub)}) in {len(un)} document {plural(len(un), 'group', 'groups')} of {inv_label(acc)}."
                        shelf.append(f"{cap(VAR_WORDS.get(v, v))}: not in NASA's table for {r['in_scope_tests']} of the {n_in} tests; no header in the files opened so far was accepted for it{clause}.{tail}")
            # ---- pile 2, the video sentence of docs/video_design/video_wording.md section 5 (lunar habitat, S1),
            # filled from pm's video/data/video_links_summary.json
            if vsum and sid == "lunar_habitat" and nid == "S1":
                q = vsum.get("scenarios", {}).get(sid, {})
                ins = q.get("by_question_and_placement", {}).get("S1", {}).get("inside", {})
                tin = q.get("tests_inside_the_ranges", {})
                flex = vsum.get("by_investigation", {}).get("PSI-69", {})
                ga = (tin.get("videos", {}).get("by_link_state", {}).get("two_labels_agree", {}))
                if ins and ins.get("no_video_tied_to_the_test") == ins.get("tests") == len(counted_in) and flex and ga:
                    gas_with = len({f["test_id"] for f in tin.get("two_labels_agree_files", [])})
                    gas_in = tin.get("by_investigation", {}).get("PSI-159", 0)
                    p2.append(f"Video. None of the {ins['tests']} counted droplet tests recorded inside these ranges has a video file tied to it. "
                              f"FLEX holds {n_(flex['files'])} video files ({flex['bytes'] / 1e9:.1f} GB); {n_(flex.get('id_not_in_table', 0))} of them carry 2013-2014 test points that NASA's table (2009 to 2011) does not list; "
                              f"their atmosphere is not stated in any file opened; they are not counted for any environment. "
                              f"{gas_with} of the {gas_in} gas-flame tests inside the ranges (CFI-G) have a video of the test ({n_(ga['files'])} files, {ga['bytes'] / 1e9:.2f} GB), "
                              f"but CFI-G counts for no question, and no readings were seen in the sampled CFI-G frames.")
                elif ins:
                    raise PileError("video_links_summary.json: the lunar S1 video sentence no longer applies (its ground in video_wording.md section 5 fails)")
            # ---- pile 2, the reading order (pile_wording.md section 9; catalog's data/catalog/reading_order.csv)
            order = []
            for r in sorted((r for r in reading_order if r["scenario_id"] == sid and r["need_id"] == nid), key=lambda r: int(r["order"])):
                files = int(r["files"] or 0)
                if r["state"] == "not_in_sampled_files":
                    ev = "not opened"
                elif r["state"] == "column_in_sampled_raw_file":
                    seen = files if "all files of the group" in (r.get("evidence") or "") else 1
                    ev = f"header seen in {seen} of {n_(files)} {plural(files, 'file', 'files')}"
                else:
                    raise PileError(f"reading_order.csv: state {r['state']!r} has no wording in pile_wording.md section 9")
                order.append(f"{r['order']}. {r['name_pattern']} ({short.get(r['investigation_id'], r['investigation_id'])}, {r['investigation_id']}):{n_(files)} {plural(files, 'file', 'files')}, {size(r['bytes'])}; target tests {n_(r['target_tests'])}; {ev}.")
            cannot = [t for t in pool if place[t] == "cannot_be_placed_from_table"]
            if cannot:
                byc = collections.Counter(tests[t]["investigation_id"] for t in cannot).most_common()
                top, rest = byc[:3], sum(c for _, c in byc[3:])
                lst = [f"{n_(c)} {short.get(a, a)} ({a})" for a, c in top] + ([f"{n_(rest)} others"] if rest else [])
                shelf.append(f"{n_(len(cannot))} tests cannot be placed: {joined(lst)}. The tables hold neither their oxygen nor their pressure, or only one of the two.")
            need_out.append({"id": nid, "name": nd["name"], "bar": bar,
                             "segments": [{"placement": k, "label": PLACEMENT_LABEL[k], "n": v} for k, v in segs],
                             "in_scope": len(pool), "pile1": p1, "pile2": p2, "shelf": shelf, "pile3": p3, "order": order,
                             "pile2_from_chain": bool(ch)})
        small = [f"Built by code from PSI's file listing of {listing} and NASA's per-test tables as the team mapped them. No language model writes or changes a line of this block.",
                 "\"Column seen\" means a header that an AI agent read in one opened file of a file group and that the data role's AI session opened again. It is not a measurement of the test, and the other files of the group were not opened.",
                 f"No value read from a raw file has entered a count. Counted tests: {', '.join(counted_list)}.",
                 "Recount by a second AI session: not yet. Read by a person: none yet.",
                 "A research exploration tool, not safety guidance. Counts and the reading order are the team's computation, not NASA's conclusions. Nothing here says what happens at a condition that was not tested."]
        pile3_label = f"No record in PSI (listing of {listing})"
        tm = len(tests)
        im = len({t["investigation_id"] for t in tests.values()})
        pile3_meaning = (f"No test at this condition is in PSI's per-test tables as the team mapped them ({n_(tm)} tests of {im} investigations), on one of three stated grounds, each printed with its source. "
                         f"The statement describes PSI's record on that date. The {n_inv - im} investigations that have no row per test are outside it.")
        glance = {"inside": len(inside_all), "no_range": False}
        if links:
            glance.update({"linked_files": links["files"], "archive_files": archive_files, "linked_share_pct": round(links["share"] * 100, 2)})
        out[sid] = {"scenario": sid, "label": sc["label"], "header": header, "needs": need_out, "small_print": small, "glance": glance,
                    "pile3_label": pile3_label, "pile3_meaning": pile3_meaning,
                    "order_header": ["Reading order: the team's rule, not a NASA priority. It says where to read first, not that the value is there.",
                                     "Rule: first, file groups in which a column for oxygen or pressure was seen for tests that cannot be placed; then file groups that could add a counted test; then file groups that could add a value to a test already counted inside. Within a class: more target tests first, then fewer bytes."],
                    "sources": {"placements": "data/pipeline/scenario_tests.csv", "chain": chain_src if ch else None,
                                "reading order": "data/catalog/reading_order.csv" if reading_order else None,
                                "links": links["source"] if links else None}}
        all_text += header + small + [pile3_label, pile3_meaning] + out[sid]["order_header"] + \
            [x for n in need_out for x in [n["bar"]] + n["pile1"] + n["pile2"] + n["shelf"] + n["pile3"] + n["order"]]

    # ---- the other environments: header line and bars only
    for sid in BARS_ONLY:
        sc = scen.get(sid)
        if not sc:
            continue
        ranges = sc.get("ranges") or {}
        st = [r for r in st_all if r["scenario_id"] == sid]
        if not st:
            continue
        place = {r["test_id"]: placement_of(r["o2_match"], r["pressure_match"]) for r in st}
        for scope, want in ((s, w) for (s_id, s), w in F1.items() if s_id == sid):
            got = collections.Counter(place[t] for t in place if scope == "all" or tests[t]["fuel_phase"] == scope)
            if dict(got) != want:
                raise PileError(f"{sid} {scope}: placements {dict(got)} differ from fixture F1 {want}")
        grav = sc.get("gravity_level") or ""
        gw = (f", {grav if grav.endswith('gravity') else grav + ' gravity'}" if grav else "")
        if ranges.get("o2_pct") and ranges.get("pressure_kpa"):
            header = [f"{sc['label']}: oxygen {range_words(rw, 'o2_pct', ranges['o2_pct'])}, pressure {range_words(rw, 'pressure_kpa', ranges['pressure_kpa'])}{gw}."]
        else:
            if any(p != "no_range_set" for p in place.values()):
                raise PileError(f"{sid}: no ranges, but a test is placed")
            header = [f"{sc['label']}: this environment sets no oxygen range and no pressure range, so no test is placed and no file is listed."]
        header.append(f"NASA's PSI archive lists {n_(archive_files)} files ({size(archive_bytes)}) for {n_(n_inv)} combustion investigations (listing of {listing}).")
        need_out = []
        for nd in needs:
            nid, scope = nd["id"], (nd.get("scope") or {}).get("fuel_phase")
            pool = [t for t in place if not scope or tests[t]["fuel_phase"] in scope]
            scope_words = "all fuel phases" if not scope else joined([f"{p} fuels" for p in scope])
            seg = collections.Counter(place[t] for t in pool)
            if sum(seg.values()) != len(pool):
                raise PileError(f"{sid} {nid}: bar segments do not sum to the tests in scope")
            segs = [(k, seg[k]) for k in PLACEMENT_ORDER if seg.get(k)]
            bar = f"{nd['name']} ({nid}), {n_(len(pool))} tests of {scope_words}: " + " | ".join(f"{PLACEMENT_LABEL[k]} {n_(v)}" for k, v in segs) + "."
            need_out.append({"id": nid, "name": nd["name"], "bar": bar, "segments": [{"placement": k, "label": PLACEMENT_LABEL[k], "n": v} for k, v in segs],
                             "in_scope": len(pool), "pile1": [], "pile2": [], "shelf": [], "pile3": [], "order": [], "pile2_from_chain": False})
        inside_all = sum(1 for p in place.values() if p == "inside")
        out[sid] = {"scenario": sid, "label": sc["label"], "bars_only": True, "header": header, "needs": need_out,
                    "small_print": ["Built by code from PSI's file listing of " + listing + " and NASA's per-test tables as the team mapped them. No language model writes or changes a line of this block.",
                                    "A research exploration tool, not safety guidance. Counts are the team's computation, not NASA's conclusions. Nothing here says what happens at a condition that was not tested."],
                    "glance": {"inside": inside_all, "no_range": not (ranges.get("o2_pct") and ranges.get("pressure_kpa"))},
                    "sources": {"placements": "data/pipeline/scenario_tests.csv"}}
        all_text += header + [n["bar"] for n in need_out]
    # word scan (whole words; "safety" is not "safe")
    for s in all_text:
        for w in BANNED + forbidden:
            if re.search(rf"\b{re.escape(w)}\b", s, re.I):
                raise PileError(f"banned word {w!r} in: {s[:120]}")
        if re.search(r"\bNone\b|\{|\}", s):
            raise PileError(f"unfilled slot in: {s[:120]}")
    return out


if __name__ == "__main__":
    import sys
    here = os.path.dirname(os.path.abspath(__file__))
    res = build(os.path.dirname(here))
    if "--print" in sys.argv:
        for sid, d in res.items():
            print("=" * 20, sid)
            for s in d["header"]:
                print("H:", s)
            for n in d["needs"]:
                print("--", n["bar"])
                for k in ("pile1", "pile2", "shelf", "pile3"):
                    for s in n[k]:
                        print(f"   [{k}] {s}")
            for s in d["small_print"]:
                print("S:", s)
    print("three piles: " + ", ".join(f"{k} ({len(v['needs'])} questions)" for k, v in res.items()))


# ---------------------------------------------------------------- the files of one test (pm 0035, item 4)
VIDEO_TIE = {  # docs/video_design/video_wording.md section 4 (tie phrases, per link state)
    "two_labels_agree": "video of this test (file name and PSI folder name the same test)",
    "day_only": "a video of that test day (which test is not known)",
    "id_not_in_table": "carries an identifier that NASA's table does not list",
    "none": "not tied to a test",
}
LINK_WORDS = {"two_labels_agree": "two labels agree", "one_label": "one label", "labels_disagree": "labels disagree",
              "id_not_in_table": "identifier not in the table", "day_only": "tied to a day only", "none": "not tied"}


def tie_phrase(f):
    st = f.get("link_state", "")
    if f.get("kind") != "video":
        return LINK_WORDS.get(st, st)
    if st == "one_label":
        return "tied by the folder name only" if "folder" in (f.get("labels_found") or "") and "name_" not in (f.get("labels_found") or "") else "tied by the file name only"
    if st == "labels_disagree":
        return f"labels disagree: {f.get('labels_found', '')}"
    return VIDEO_TIE.get(st, st)


def build_files(root):
    """Per scenario, the tests inside the ranges and the files whose name carries a label of each
    (data/pipeline/test_files.json, written by the data role's pipeline/file_links.py)."""
    path = os.path.join(root, "data", "pipeline", "test_files.json")
    if not os.path.exists(path):
        return {}
    tf = _json(path)
    out = {}
    for sid in SCENARIOS:
        tests = tf.get("scenarios", {}).get(sid)
        if not tests:
            continue
        doc = {}
        for tid, t in sorted(tests.items(), key=lambda kv: (kv[1].get("investigation_id", ""), kv[0])):
            rows = t.get("file_list", [])
            if len(rows) != int(t.get("files", len(rows))) or sum(int(r.get("bytes") or 0) for r in rows) != int(t.get("bytes", 0)):
                raise PileError(f"test_files.json {sid} {tid}: the file list does not sum to its files and bytes")
            big = [r for r in rows if r.get("kind") in ("archive", "video")]
            doc[tid] = {"investigation_id": t.get("investigation_id"), "fuel_phase": t.get("fuel_phase"),
                        "files": len(rows), "bytes": int(t.get("bytes", 0)),
                        "summary": f"{n_(len(rows))} {plural(len(rows), 'file', 'files')}, {size(t.get('bytes', 0))}: "
                                   f"{n_(len(rows) - len(big))} small {plural(len(rows) - len(big), 'file', 'files')} ({size(sum(int(r['bytes'] or 0) for r in rows if r not in big))}) and "
                                   f"{n_(len(big))} {plural(len(big), 'archive or video recording', 'archives and video recordings')} ({size(sum(int(r['bytes'] or 0) for r in big))}).",
                        "rows": [[r["file_name"], int(r.get("bytes") or 0), r.get("kind", ""), tie_phrase(r), r.get("labels_found", ""), r.get("psi_file_id", "")] for r in rows]}
        out[sid] = doc
    return out
