# AI-generated code: written with an AI coding assistant (Claude Code)
# during the NASA Space Apps Challenge 2026 hackathon (2026-11-14).
"""What the PSI raw files hold for the variables the tables lack.

For every PSI investigation and every standard variable used by a need
(spec/needs.json), one state per group of tests, decided by a fixed rule from
data/pipeline/tests.csv and spec/raw_columns.json:

  no_test_table                the investigation has no per-test table
  in_table                     the test has a value in tests.csv
  column_in_sampled_raw_file   the test has no value; an opened sample file of a
                               group of the investigation has an entry (a header,
                               key or label) named for the variable
  documented_only              no value and no entry; a sentence of a record or a
                               paper states it for the whole table
                               (spec/sources.json 'documented_elsewhere')
  not_in_sampled_files         none of the above

The states are tried in this order. A test of an investigation with a value
for n of its N tests is split: n tests in_table, N-n tests in the next state.

Run after run.py (python3 pipeline/raw_gaps.py). Writes, in data/pipeline/:
  gap_states.csv         investigation x variable x state
  need_gap_states.csv    scenario x need x required or outcome variable x state
  retrieval_queue.csv    investigation x variable x file group still to read
  raw_values_effect.json what raw_values.csv would change if adopted (nothing
                         is adopted; no pipeline output is changed)

evidence.py imports this module for the 'raw_state' fields of the packages.
No value of a raw file ever becomes a value of tests.csv. Every sentence is in
spec/statements.json ('raw_state') or spec/raw_columns.json (_meta). Same
inputs give the same bytes: fixed order, no timestamps.
"""
import csv
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SPEC = os.path.join(HERE, "spec")
OUT = os.path.join(ROOT, "data", "pipeline")

STATES = ["in_table", "column_in_sampled_raw_file", "documented_only", "not_in_sampled_files", "no_test_table"]
COL = "column_in_sampled_raw_file"
READABLE = ("sensor_reading_series", "value_per_test_in_a_results_file")
FORBIDDEN = re.compile(r"\b(safe|safely|acceptable|sufficient|sufficiently|representative|proven|proves)\b", re.I)


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def read_csv(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def inv_number(inv):
    return int(inv.split("-")[1])


def need_variables(needs):
    out = []
    for nd in needs:
        for k in ("conditions_required", "conditions_useful", "outcomes_any"):
            for v in nd[k]:
                if v not in out:
                    out.append(v)
    return out


def text_empty(v):
    return v is None or str(v).strip() == ""


def load(spec_dir=SPEC, out_dir=OUT):
    """The inputs that do not depend on a run: specs and the raw inventory."""
    return {"raw": read_json(os.path.join(spec_dir, "raw_columns.json")),
            "needs": read_json(os.path.join(spec_dir, "needs.json"))["needs"],
            "sources": read_json(os.path.join(spec_dir, "sources.json"))["sources"],
            "texts": read_json(os.path.join(spec_dir, "statements.json"))["raw_state"],
            "inventory": read_json(os.path.join(out_dir, "raw_inventory.json"))["investigations"]}


class States:
    """States per investigation and variable, and per test. 'tests' are rows
    with investigation_id, test_id, fuel_phase and the variables; 'empty' says
    whether a cell holds no value."""

    def __init__(self, inputs, tests, empty):
        self.inputs, self.empty = inputs, empty
        raw = inputs["raw"]
        self.meta = raw["_meta"]
        self.variables = need_variables(inputs["needs"])
        self.spec = {x["investigation_id"]: x for x in raw["investigations"]}
        self.tests = tests
        self.by_inv = {}
        for t in tests:
            self.by_inv.setdefault(t["investigation_id"], []).append(t)
        self.investigations = sorted({x["investigation_id"] for x in inputs["inventory"]}, key=inv_number)
        self.kinds = {x["investigation_id"]: x["by_kind"] for x in inputs["inventory"]}
        self.docs = {}
        for s in inputs["sources"]:
            for d in s.get("documented_elsewhere", []) or []:
                self.docs.setdefault((s["investigation_id"], d["variable"]), []).append(
                    d.get("reference_item") or ("record field " + d.get("record_field", "")))
        self.check_spec()
        self.cells = {(i, v): self._cell(i, v) for i in self.investigations for v in self.variables}

    # ------------------------------------------------------------ spec rules
    def check_spec(self):
        col_is, kinds = self.meta["column_is"], self.meta["header_kinds"]
        for inv in self.spec.values():
            groups = {g["group"]: g for g in inv["groups"]}
            for e in inv["entries"]:
                where = f"raw_columns.json {inv['investigation_id']} {e['group']} {e['header_as_written']!r}"
                if e["column_is"] not in col_is or e["header_kind"] not in kinds:
                    sys.exit(f"{where}: column_is or header_kind not in _meta")
                if e["standard_variable"] not in self.variables:
                    sys.exit(f"{where}: {e['standard_variable']} is not a variable of a need")
                g = groups.get(e["group"])
                if g is None or not e["has_values"]:
                    sys.exit(f"{where}: unknown group or no values")
                for k in ("name_pattern", "files_in_listing", "bytes_in_listing"):
                    if e[k] != g[k]:
                        sys.exit(f"{where}: {k} differs from its group")

    # ------------------------------------------------------------ per cell
    def _cell(self, inv, var):
        rows = self.by_inv.get(inv, [])
        spec = self.spec.get(inv, {"entries": [], "unopened_groups": [], "groups": []})
        if not rows:
            return {"no_test_table": True, "n": 0, "N": 0}
        n = sum(1 for t in rows if not self.empty(t.get(var)))
        cell = {"no_test_table": False, "n": n, "N": len(rows), "remainder": None}
        if n == len(rows):
            return cell
        entries = [e for e in spec["entries"] if e["standard_variable"] == var]
        if entries:
            groups = []
            for e in entries:
                if e["group"] not in [g["group"] for g in groups]:
                    groups.append({"group": e["group"], "name_pattern": e["name_pattern"],
                                   "files": e["files_in_listing"], "bytes": e["bytes_in_listing"]})
            kinds = list(dict.fromkeys(e["column_is"] for e in entries))
            all_files = all(e["sampling"] != "one file of the group was opened" for e in entries)
            cell["remainder"] = {"state": COL, "column_is": kinds, "entries": entries, "groups": groups,
                                 "all_files": all_files}
        elif (inv, var) in self.docs:
            cell["remainder"] = {"state": "documented_only", "documented_by": self.docs[(inv, var)], "groups": []}
        else:
            groups = [{"group": u["group"], "name_pattern": u["name_pattern"], "kind": u["kind"],
                       "files": u["files_in_listing"], "bytes": u["bytes_in_listing"]}
                      for u in spec.get("unopened_groups", [])]
            cell["remainder"] = {"state": "not_in_sampled_files", "groups": groups}
        return cell

    def unopened_text(self, inv, groups):
        k = self.kinds.get(inv, {})
        arch = k.get("archive", {}).get("files", 0)
        vid = k.get("video", {}).get("files", 0)
        parts = [f"archives {arch} files", f"videos {vid} files"]
        by = {}
        for g in groups:
            by.setdefault(g["kind"].replace("_", " "), [0, 0])
            by[g["kind"].replace("_", " ")][0] += 1
            by[g["kind"].replace("_", " ")][1] += g["files"]
        parts += [f"{kind} {ng} [group|groups] {nf} files".replace("[group|groups]", "group" if ng == 1 else "groups")
                  for kind, (ng, nf) in by.items()]
        return "; ".join(parts)

    def sentence(self, inv, state, rem):
        T = self.inputs["texts"]
        if state == COL:
            return T[COL + "_all_files"] if rem["all_files"] else T[COL]
        if state == "not_in_sampled_files":
            return T[state].format(unopened=self.unopened_text(inv, rem["groups"]))
        return T[state]

    # ------------------------------------------------------------ per test
    def test_state(self, t, var):
        """(state, column_is key) of one test for one variable."""
        if not self.empty(t.get(var)):
            return "in_table", ""
        rem = self.cells[(t["investigation_id"], var)]["remainder"]
        return rem["state"], "+".join(rem.get("column_is", []))

    def summary(self, var, tests):
        """States of a set of tests for one variable: one item per state,
        column kind and investigation, in fixed order."""
        items = {}
        for t in tests:
            st, kind = self.test_state(t, var)
            key = (STATES.index(st), kind, inv_number(t["investigation_id"]))
            if key not in items:
                inv = t["investigation_id"]
                rem = self.cells[(inv, var)]["remainder"] if st != "in_table" else None
                item = {"state": st, "column_is": kind.split("+") if kind else [], "investigation_id": inv, "tests": 0}
                if rem:
                    item["file_groups"] = [{k: g[k] for k in ("group", "name_pattern", "files", "bytes")}
                                           for g in rem["groups"]]
                    item["bytes"] = sum(g["bytes"] or 0 for g in rem["groups"])
                    if st == "documented_only":
                        item["documented_by"] = rem["documented_by"]
                item["sentence"] = self.sentence(inv, st, rem)
                items[key] = item
            items[key]["tests"] += 1
        return [items[k] for k in sorted(items)]


def unmatched_for_lack(var, o2_match, pressure_match, tier):
    """A counted test that the matching leaves unmatched because this variable
    is empty: tier 'other', this variable 'not_recorded' and the other
    atmosphere variable 'not_recorded' too (were this one recorded and in
    range, the tier would be oxygen_only or pressure_only). Flow and the other
    variables do not decide the tier."""
    if var not in ("o2_pct", "pressure_kpa") or tier != "other":
        return False
    mine, other = (o2_match, pressure_match) if var == "o2_pct" else (pressure_match, o2_match)
    return mine == "not_recorded" and other == "not_recorded"


# ---------------------------------------------------------------- outputs
def write_csv(path, cols, rows):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def gap_state_rows(S):
    rows = []
    for inv in S.investigations:
        for var in S.variables:
            c = S.cells[(inv, var)]
            base = {"investigation_id": inv, "variable": var, "tests_in_table": c["n"], "tests_mapped": c["N"],
                    "column_is": "", "entries": 0, "file_groups": "", "files": "", "bytes": "",
                    "headers_as_written": "", "link_to_table_row": "", "sampling": "", "documented_by": ""}
            if c["no_test_table"]:
                rows.append({**base, "state": "no_test_table", "tests_in_state": 0})
                continue
            if c["n"]:
                rows.append({**base, "state": "in_table", "tests_in_state": c["n"]})
            rem = c["remainder"]
            if rem is None:
                continue
            r = {**base, "state": rem["state"], "tests_in_state": c["N"] - c["n"]}
            if rem["groups"]:
                r["file_groups"] = " | ".join(g["group"] for g in rem["groups"])
                r["files"] = sum(g["files"] for g in rem["groups"])
                r["bytes"] = sum(g["bytes"] or 0 for g in rem["groups"])
            if rem["state"] == COL:
                es = rem["entries"]
                r.update(column_is="+".join(rem["column_is"]), entries=len(es),
                         headers_as_written=" | ".join(e["header_as_written"] for e in es),
                         link_to_table_row=" | ".join(dict.fromkeys(e["link_to_table_row"] for e in es)),
                         sampling=" | ".join(dict.fromkeys(e["sampling"] for e in es)))
            if rem["state"] == "documented_only":
                r["documented_by"] = " | ".join(rem["documented_by"])
            rows.append(r)
    return rows


def need_gap_rows(S, scenarios, need_tests, scen_tests):
    counted = {}
    for r in need_tests:
        if r["objective_link"] == "stated":
            counted.setdefault(r["need_id"], set()).add(r["test_id"])
    marks = {(r["scenario_id"], r["test_id"]): r for r in scen_tests}
    rows = []
    for sc in scenarios:
        for nd in S.inputs["needs"]:
            phases = (nd.get("scope") or {}).get("fuel_phase")
            scope = [t for t in S.tests if not phases or t["fuel_phase"] in phases]
            ids = counted.get(nd["id"], set())
            for role, var in [("required", v) for v in nd["conditions_required"]] + \
                    [("outcome", v) for v in nd["outcomes_any"]]:
                groups = {}
                for t in scope:
                    key = S.test_state(t, var)
                    g = groups.setdefault(key, [0, 0, 0])
                    g[0] += 1
                    if t["test_id"] in ids:
                        g[1] += 1
                        m = marks[(sc["id"], t["test_id"])]
                        if unmatched_for_lack(var, m["o2_match"], m["pressure_match"], m["tier"]):
                            g[2] += 1
                for (st, kind) in sorted(groups, key=lambda k: (STATES.index(k[0]), k[1])):
                    a, b, u = groups[(st, kind)]
                    rows.append({"scenario_id": sc["id"], "need_id": nd["id"], "role": role, "variable": var, "state": st,
                                 "column_is": kind, "in_scope_tests": len(scope), "counted_tests": len(ids),
                                 "in_scope_tests_in_state": a, "counted_tests_in_state": b,
                                 "counted_unmatched_for_lack_of_this_variable": u})
    return rows


def queue_rows(S, need_tests):
    counted = {}
    for r in need_tests:
        if r["objective_link"] == "stated":
            counted.setdefault(r["test_id"], set()).add(r["need_id"])
    uses = {v: [n["id"] for n in S.inputs["needs"] if v in n["conditions_required"] + n["conditions_useful"] + n["outcomes_any"]]
            for v in S.variables}
    supported = {n["id"]: {l["investigation_id"] for l in n.get("stated_by", []) if l["verdict"] == "supported"}
                 for n in S.inputs["needs"]}
    rows = []
    for inv in S.investigations:
        for var in S.variables:
            c = S.cells[(inv, var)]
            rem = c.get("remainder")
            if c["no_test_table"] or rem is None or rem["state"] not in (COL, "not_in_sampled_files"):
                continue
            empty = [t for t in S.by_inv[inv] if S.empty(t.get(var))]
            # a test lacks the value for a need only within the scope of a need that uses the variable
            # and links the investigation with verdict 'supported' (the link rule of the counts)
            lacking = [t for t in empty if any(in_scope(t, n) and inv in supported[n["id"]]
                                               for n in S.inputs["needs"] if n["id"] in uses[var])]
            if not lacking:
                continue
            cnt = [t for t in lacking if counted.get(t["test_id"], set()) & set(uses[var])]
            needs = sorted({n for t in cnt for n in counted[t["test_id"]] & set(uses[var])},
                           key=[n["id"] for n in S.inputs["needs"]].index)
            base = {"investigation_id": inv, "variable": var, "state": rem["state"],
                    "tests_without_value": len(empty),
                    "tests_lacking_value": len(lacking), "counted_tests_lacking_value": len(cnt),
                    "needs_counting_them": ";".join(needs)}
            if rem["state"] == COL:
                for g in rem["groups"]:
                    es = [e for e in rem["entries"] if e["group"] == g["group"]]
                    kinds = list(dict.fromkeys(e["column_is"] for e in es))
                    rows.append({**base, "file_group": g["group"], "name_pattern": g["name_pattern"],
                                 "kind": "+".join(kinds),
                                 "retrievable_by_reading": "yes" if any(k in READABLE for k in kinds) else "no",
                                 "headers_as_written": " | ".join(e["header_as_written"] for e in es),
                                 "files": g["files"], "bytes": "" if g["bytes"] is None else g["bytes"],
                                 "link_to_table_row": " | ".join(dict.fromkeys(e["link_to_table_row"] for e in es)),
                                 "sampling": " | ".join(dict.fromkeys(e["sampling"] for e in es))})
            else:
                for g in rem["groups"]:
                    rows.append({**base, "file_group": g["group"], "name_pattern": g["name_pattern"],
                                 "kind": g["kind"], "retrievable_by_reading": "no", "headers_as_written": "",
                                 "files": g["files"], "bytes": g["bytes"], "link_to_table_row": "not evident",
                                 "sampling": "not opened or not readable"})
    rows.sort(key=queue_key)
    for i, r in enumerate(rows, 1):
        r["rank"] = i
    return rows


def in_scope(t, need):
    phases = (need.get("scope") or {}).get("fuel_phase")
    return not phases or t["fuel_phase"] in phases


def queue_key(r):
    b = r["bytes"]
    return (-int(r["tests_lacking_value"]), (1, 0) if b in ("", None) else (0, int(b)),
            inv_number(r["investigation_id"]), r["variable"], r["file_group"])


# ---------------------------------------------------------------- effect
def bin_of(value, bins):
    for b in bins:
        lo = b["min"] is None or value > b["min"] or (value == b["min"] and b["min_inclusive"])
        hi = b["max"] is None or value < b["max"] or (value == b["max"] and b["max_inclusive"])
        if lo and hi:
            return b["id"]
    return None


def in_range(value, r):
    r = {"min": None, "max": None, "min_inclusive": True, "max_inclusive": False, **r}
    lo = r["min"] is None or value > r["min"] or (value == r["min"] and r["min_inclusive"])
    hi = r["max"] is None or value < r["max"] or (value == r["max"] and r["max_inclusive"])
    return lo and hi


def effect(S, raw_values, tests_by_id, scenarios, coverage, factor, need_tests):
    E = S.meta["effect"]
    bins = coverage["dimensions"]["pressure_kpa"]["bins"]
    saffire = []
    for r in raw_values:
        if r["extraction"] != "saffire_ambient_pressure" or not r["test_id"]:
            continue
        t = tests_by_id[r["test_id"]]
        lo, hi = round(float(r["min"]) * factor, 4), round(float(r["max"]) * factor, 4)
        b_lo, b_hi = bin_of(lo, bins), bin_of(hi, bins)
        sc = {}
        for s in scenarios:
            rng = s["ranges"].get("pressure_kpa")
            if rng is not None:
                sc[s["id"]] = {"min_in_range": in_range(lo, rng), "max_in_range": in_range(hi, rng)}
        saffire.append({"test_id": r["test_id"], "investigation_id": r["investigation_id"],
                        "psi_file_id": r["psi_file_id"], "n_readings": int(r["n_readings"]),
                        "min_as_stored_psia": r["min"], "max_as_stored_psia": r["max"],
                        "min_kpa": lo, "max_kpa": hi, "pressure_kpa_in_tests_csv": t["pressure_kpa"] or None,
                        "bin_of_min": b_lo, "bin_of_max": b_hi, "same_bin": b_lo == b_hi,
                        "scenario_pressure_ranges": sc,
                        "sentence": E["same_bin"] if b_lo == b_hi else E["different_bin"]})
    # SAME-R: tests with a stored size statistic, per statistic class
    d2 = next(n for n in S.inputs["needs"] if n["id"] == "D2")
    phases = d2["scope"]["fuel_phase"]
    supported = sorted({l["investigation_id"] for l in d2["stated_by"] if l["verdict"] == "supported"}, key=inv_number)
    scope = [t for t in S.tests if t["fuel_phase"] in phases and t["investigation_id"] in supported]
    scope_ids = {t["test_id"] for t in scope}
    req_ok = {t["test_id"] for t in scope if all(not S.empty(t.get(v)) for v in d2["conditions_required"])}
    classes = E["same_statistic_classes"]
    stats = []
    for name, headers in classes.items():
        values = {}
        for r in raw_values:
            if r["extraction"] != "same_particle_size_statistics" or not r["test_id"] or r["header_as_written"] not in headers:
                continue
            try:
                v = float(r["value"])
            except ValueError:
                continue
            if v != 0:
                values.setdefault(r["test_id"], set()).add((r["psi_file_id"], r["value"]))
        with_value = sorted(set(values) & scope_ids)
        files_differ = []
        for t in with_value:
            per_file = {}
            for fid, val in values[t]:
                per_file.setdefault(fid, set()).add(val)
            if len(per_file) > 1 and len({frozenset(v) for v in per_file.values()}) > 1:
                files_differ.append(t)
        units = sorted({r["unit_as_written"] or "not written" for r in raw_values
                        if r["extraction"] == "same_particle_size_statistics" and r["header_as_written"] in headers})
        stats.append({"statistic": name, "headers_as_written": headers, "units_as_written": units,
                      "d2_tests_in_scope_of_linked_investigations": len(scope),
                      "tests_with_a_stored_nonzero_value": len(with_value),
                      "of_which_meet_every_required_condition": len(set(with_value) & req_ok),
                      "tests_whose_files_hold_different_values": len(files_differ)})
    counted_d2 = sum(1 for r in need_tests if r["need_id"] == "D2" and r["objective_link"] == "stated")
    return {"_meta": {"generated_by": "AI-generated (Claude Code), 2026-11-14. Not human-reviewed.",
                      "written_by": "pipeline/raw_gaps.py", "rule": E["rule"],
                      "not_adopted": E["not_adopted"]},
            "saffire_pressure": {"factor_kpa_per_psi": factor, "factor_source": E["factor_source"],
                                 "arithmetic": E["arithmetic"], "bins": [b["id"] for b in bins],
                                 "tests": saffire,
                                 "tests_with_both_in_one_bin": sum(1 for x in saffire if x["same_bin"]),
                                 "sentence_choice": E["choice"]},
            "same_r_particle_size": {"need": "D2", "required_conditions": d2["conditions_required"],
                                     "outcomes_any": d2["outcomes_any"], "scope": d2["scope"],
                                     "linked_investigations_supported": supported,
                                     "d2_counted_tests_now": counted_d2,
                                     "d2_tests_in_scope_of_linked_investigations": len(scope),
                                     "d2_tests_of_linked_investigations_meeting_every_required_condition": len(req_ok),
                                     "statistics": stats, "would_the_count_change": E["d2_count"]},
            "not_adopted": E["not_adopted"]}


def main():
    inputs = load()
    tests = read_csv(os.path.join(OUT, "tests.csv"))
    need_tests = read_csv(os.path.join(OUT, "need_tests.csv"))
    scen_tests = read_csv(os.path.join(OUT, "scenario_tests.csv"))
    scenarios = read_json(os.path.join(SPEC, "scenarios.json"))["scenarios"]
    S = States(inputs, tests, text_empty)

    gcols = ["investigation_id", "variable", "state", "tests_in_state", "tests_in_table", "tests_mapped", "column_is",
             "entries", "file_groups", "files", "bytes", "headers_as_written", "link_to_table_row", "sampling", "documented_by"]
    write_csv(os.path.join(OUT, "gap_states.csv"), gcols, gap_state_rows(S))
    ncols = ["scenario_id", "need_id", "role", "variable", "state", "column_is", "in_scope_tests", "counted_tests",
             "in_scope_tests_in_state", "counted_tests_in_state", "counted_unmatched_for_lack_of_this_variable"]
    write_csv(os.path.join(OUT, "need_gap_states.csv"), ncols, need_gap_rows(S, scenarios, need_tests, scen_tests))
    qcols = ["rank", "investigation_id", "variable", "state", "file_group", "name_pattern", "kind", "retrievable_by_reading",
             "headers_as_written", "tests_without_value", "tests_lacking_value", "counted_tests_lacking_value", "needs_counting_them",
             "files", "bytes", "link_to_table_row", "sampling"]
    write_csv(os.path.join(OUT, "retrieval_queue.csv"), qcols, queue_rows(S, need_tests))

    raw_values = read_csv(os.path.join(OUT, "raw_values.csv"))
    factor = read_json(os.path.join(SPEC, "findings.json"))["_meta"]["units"]["psi_to_kpa"]
    eff = effect(S, raw_values, {t["test_id"]: t for t in tests}, scenarios,
                 read_json(os.path.join(SPEC, "coverage.json")), factor, need_tests)
    text = json.dumps(eff, indent=1, ensure_ascii=False) + "\n"
    for name in ("gap_states.csv", "need_gap_states.csv", "retrieval_queue.csv"):
        with open(os.path.join(OUT, name), encoding="utf-8") as f:
            bad = FORBIDDEN.findall(f.read())
        if bad:
            sys.exit(f"raw_gaps: forbidden word(s) {sorted(set(bad))} in {name}")
    if FORBIDDEN.findall(text):
        sys.exit("raw_gaps: forbidden word in raw_values_effect.json")
    with open(os.path.join(OUT, "raw_values_effect.json"), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print("raw_gaps: wrote gap_states.csv, need_gap_states.csv, retrieval_queue.csv, raw_values_effect.json")


if __name__ == "__main__":
    main()
