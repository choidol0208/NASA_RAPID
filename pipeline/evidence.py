# AI-generated code: written with an AI coding assistant (Claude Code)
# during the NASA Space Apps Challenge 2026 hackathon (2026-11-14).
"""Evidence packages: for one environment, the recorded tests behind each need.

An environment is a scenario of spec/scenarios.json, or a cell of the coverage
grid: one oxygen bin x one pressure bin of spec/coverage.json, treated as a
scenario whose ranges are the bin edges, with no flow range and no gravity
level. For every environment this module writes one JSON file with, per
information need: the counts of usable tests by match tier, the matched tests
with their recorded values and source columns, the indicators recomputed over
the matched tests, the gap codes, and fixed sentences filled with those
numbers.

This module computes nothing that the engine does not compute. Status and
counts are the rows returned by run.match_environments (the same rows that are
written to scenario_needs.csv and atmosphere_cells.csv), indicators come from
run.indicators, values and source columns from the tests in memory. It holds
no sentence and no experiment knowledge: every text is a template in
spec/statements.json, and a template that names a field the block does not
have stops the run.

Outputs (data/pipeline/)
    evidence/scenario_<id>.json           one package per scenario
    evidence/cell_<o2_bin>__<p_bin>.json  one package per coverage cell
    evidence/index.json                   the list of packages, status per need
    atmosphere_cells.csv                  scenario_needs.csv for the cells

Called at the end of run.main():  evidence.write(engine, ...), where engine is
the run module (this module does not import it).
"""
import json
import os
import re

import pandas as pd

MATCHED = ("atmosphere", "oxygen_only", "pressure_only")
TIERS = MATCHED + ("other",)
RANGE_VARS = {"o2_pct": "o2", "pressure_kpa": "pressure", "flow_cms": "flow"}
# name in the package -> column of scenario_needs.csv / atmosphere_cells.csv
COUNTS = {"usable_tests": "usable_tests", "atmosphere": "tests_atmosphere",
          "oxygen_only": "tests_oxygen_only", "pressure_only": "tests_pressure_only",
          "other": "tests_other", "recorded_outside_objective": "tests_recorded_outside_objective",
          "matched_flow_in_range": "matched_tests_flow_in_range",
          "matched_flow_not_recorded": "matched_tests_flow_not_recorded",
          "matched_same_gravity": "matched_tests_same_gravity",
          "matched_added_gas": "matched_tests_co2_or_helium_added"}
TOKEN = re.compile(r"\{([a-z0-9_]+)\}|\[([a-z0-9_]+)\|([^|\[\]{}]*)\|([^|\[\]{}]*)\]")


def inv_number(investigation_id):
    return int(investigation_id.split("-")[1])


def plain(v):
    """A JSON value: numpy scalars become Python scalars, NaN becomes null."""
    if hasattr(v, "item"):
        v = v.item()
    return None if isinstance(v, float) and v != v else v


def shown(v):
    """A field as written in a sentence."""
    if isinstance(v, (list, tuple)):
        return ", ".join(shown(x) for x in v)
    if isinstance(v, float) and v == int(v):
        return str(int(v))
    return str(v)


# ---------------------------------------------------------------- statements
class Statements:
    """The templates of spec/statements.json and the rules for filling them."""

    def __init__(self, spec, ops):
        self.spec, self.ops, self.checked = spec, ops, set()

    def stop(self, message):
        raise SystemExit("statements.json: " + message)

    def fill(self, text, fields, where):
        def one(m):
            name = m.group(1) or m.group(2)
            if name not in fields:
                self.stop(f"{where}: '{name}' is not a field of the block; fields: {sorted(fields)}")
            if fields[name] is None:
                self.stop(f"{where}: field '{name}' is empty here; add a 'when' condition")
            if m.group(1):
                return shown(fields[name])
            return m.group(3) if fields[name] == 1 else m.group(4)

        if set("{}") & set(TOKEN.sub("", text)):
            self.stop(f"{where}: unreadable placeholder in: {text}")
        return " ".join(TOKEN.sub(one, text).split())

    def holds(self, cond, fields):
        value, op, target = fields[cond[0]], cond[1], cond[2]
        if value is None or target is None:
            return op in ("==", "!=") and self.ops[op](value, target)
        try:
            return self.ops[op](value, target)
        except TypeError:
            self.stop(f"condition {cond}: the field holds {value!r}, which cannot be compared with {target!r}")

    def check(self, section, fields):
        """Once per section: every template against the fields of its block
        and against the documented field list, used or not in this run."""
        if section in self.checked:
            return
        self.checked.add(section)
        documented = {} if section in self.spec.get("sections_without_need_fields", []) \
            else dict(self.spec["fields"]["need"])
        documented.update(self.spec["fields"].get(section, {}))
        if set(documented) != set(fields):
            self.stop(f"'fields' of section '{section}' differ from the block: "
                      f"{sorted(set(documented) ^ set(fields))}")
        ids = [st["id"] for st in self.spec["statements"][section]]
        if len(ids) != len(set(ids)):
            self.stop(f"section '{section}': an id is used twice")
        for st in self.spec["statements"][section]:
            where = f"statement '{st['id']}'"
            names = [a or b for a, b, _, _ in TOKEN.findall(st["text"] + " " + st.get("code", ""))]
            for cond in st["when"]:
                if len(cond) != 3 or cond[1] not in self.ops:
                    self.stop(f"{where}: condition {cond} is not [field, operator, value]")
                names.append(cond[0])
            allowed = set(fields) - (set() if "each_value" in st else {"values"})
            unknown = sorted(set(names) - allowed)
            if unknown:
                self.stop(f"{where}: {unknown} not among the fields of the block: {sorted(allowed)}")
            value_fields = self.spec["fields"]["value"]
            unknown = sorted({a or b for a, b, _, _ in TOKEN.findall(st.get("each_value", ""))}
                             - set(value_fields))
            if unknown:
                self.stop(f"{where}: {unknown} not among the fields of a value: {sorted(value_fields)}")

    def render(self, section, fields, where, exactly_one=False, code=None, values=None):
        """The sentences of a section that apply to a block, in spec order."""
        self.check(section, fields)
        out = []
        for st in self.spec["statements"][section]:
            name = f"statement '{st['id']}' in {where}"
            if not all(self.holds(c, fields) for c in st["when"]):
                continue
            if code is not None and self.fill(st["code"], fields, name) != code:
                continue
            block = fields
            if "each_value" in st:
                block = {**fields, "values": st["join"].join(
                    self.fill(st["each_value"], v, name) for v in values)}
            out.append({"id": st["id"], "text": self.fill(st["text"], block, name)})
        if exactly_one and len(out) != 1:
            self.stop(f"section '{section}': {len(out)} sentences apply to {where}"
                      + (f", code {code}" if code else "") + "; exactly one is required")
        return out


# -------------------------------------------------------------- environments
def full_range(r, defaults):
    return None if r is None else {k: {**defaults, **r}[k] for k in defaults}


def scenario_environments(scen_spec):
    return [{**sc, "kind": "scenario", "file": f"scenario_{sc['id']}.json"}
            for sc in scen_spec["scenarios"]]


def cell_environments(cov, texts, statements):
    """Every oxygen bin x pressure bin of coverage.json as an environment."""
    o2, pressure = cov["dimensions"]["o2_pct"], cov["dimensions"]["pressure_kpa"]
    cells = []
    for o in o2["bins"]:
        for p in pressure["bins"]:
            fields = {"o2_bin": o["id"], "o2_label": o["label"], "o2_rationale": o2["rationale"],
                      "pressure_bin": p["id"], "pressure_label": p["label"],
                      "pressure_rationale": pressure["rationale"]}
            if set(fields) != set(texts["fields"]):
                statements.stop(f"'cell.fields' differ from the fields of a cell: {sorted(fields)}")
            edges = ("min", "max", "min_inclusive", "max_inclusive")
            cell_id = f"cell_{o['id']}__{p['id']}"
            cells.append({
                "id": cell_id, "kind": "cell", "file": f"{cell_id}.json",
                "label": statements.fill(texts["label"], fields, "cell.label"),
                "ranges": {"o2_pct": {k: o[k] for k in edges},
                           "pressure_kpa": {k: p[k] for k in edges}},
                "gravity_level": None, "basis": [],
                "note": statements.fill(texts["note"], fields, "cell.note"),
                "o2_bin": o["id"], "pressure_bin": p["id"]})
    return cells


# ------------------------------------------------------------------ packages
class Builder:
    def __init__(self, engine, tests, links, obj_links, needs, var_spec):
        self.engine, self.tests, self.links, self.needs = engine, tests, links, needs
        self.variables, self.derived = var_spec["variables"], var_spec["derived"]
        self.units = {k: v["unit"] for k, v in {**self.variables, **self.derived}.items()}
        self.by_id = {t["test_id"]: t for t in tests}
        self.usable = {}
        for row in links.itertuples():
            if row.objective_link == "stated":
                self.usable.setdefault(row.need_id, set()).add(row.test_id)
        self.objective = {}
        for row in obj_links.to_dict("records"):
            self.objective.setdefault(row["need_id"], []).append(
                {k: row[k] for k in ("investigation_id", "record_field", "quote")})
        self.ref_items = {}
        for r in engine.spec("references.json")["references"]:
            for i in r["items"]:
                self.ref_items[i["id"]] = {"item_id": i["id"], "type": i["type"], "text": i["text"],
                                           "where": i["where"], "title": r["title"],
                                           "version": r["version"], "url": r["url"],
                                           "access": r["access"], "quote": i.get("quote")}
        self.sources = engine.spec("sources.json")["sources"]
        self.ind_spec = engine.spec("indicators.json")
        self.ind_by_id = {i["id"]: i for i in self.ind_spec["indicators"]}
        self.texts = engine.spec("statements.json")
        self.statements = Statements(self.texts, engine.OPS)
        self.titles = {}

    def test_key(self, test_id):
        return inv_number(self.by_id[test_id]["investigation_id"]), test_id

    def title(self, investigation_id):
        if investigation_id not in self.titles:
            path = os.path.join(self.engine.ROOT, "data", "psi", "catalog", f"{investigation_id}.json")
            with open(path, encoding="utf-8") as f:
                self.titles[investigation_id] = json.load(f)["title"]
        return self.titles[investigation_id]

    def references(self, item_ids, where):
        unknown = [i for i in item_ids if i not in self.ref_items]
        if unknown:
            raise SystemExit(f"{where}: unknown reference item {unknown}")
        return [self.ref_items[i] for i in item_ids]

    def documented(self, source_ids, where):
        """What a record or a paper says about a variable that the tables of
        these sources do not hold (sources.json 'documented_elsewhere'). The
        sentence is checked against the record or against references.json."""
        out = []
        for s in self.sources:
            if s["id"] not in source_ids:
                continue
            for d in s.get("documented_elsewhere", []):
                if "record_field" in d:
                    text = self.engine.record_text(s["investigation_id"], d["record_field"])
                    said_in = f"{s['investigation_id']}.{d['record_field']}"
                else:
                    item = self.ref_items.get(d["reference_item"])
                    if item is None:
                        raise SystemExit(f"sources.json {s['id']}: unknown reference item {d['reference_item']}")
                    text, said_in = item["quote"] or "", d["reference_item"]
                if d["quote"] not in text:
                    raise SystemExit(f"sources.json {s['id']}: sentence not found in {said_in}: {d['quote'][:60]}")
                out.append({"source_id": s["id"], "investigation_id": s["investigation_id"],
                            "variable": d["variable"],
                            "variable_label": self.texts["labels"].get(d["variable"], d["variable"]),
                            "quote": d["quote"], "said_in": said_in})
        return out

    def see_also(self, env):
        """Pointers of a scenario to records or table cells that are not in the
        counts; each is checked against its source."""
        out = []
        for p in env.get("see_also", []):
            if "record_field" in p:
                if p["quote"] not in self.engine.record_text(p["investigation_id"], p["record_field"]):
                    raise SystemExit(f"scenarios.json {env['id']}: sentence not found in "
                                     f"{p['investigation_id']}.{p['record_field']}")
            else:
                c = p["table_cell"]
                header, rows = self.engine.ingest(c["file"])
                cell = next((r[c["column"]] for n, r in rows if n == c["row"]), None)
                if cell != c["text"]:
                    raise SystemExit(f"scenarios.json {env['id']}: cell {c} holds {cell!r}")
            out.append({**p, "title": self.title(p["investigation_id"])})
        return out

    def recorded_tests(self, marks):
        """Every test matched to the environment, whatever need it is counted
        for: per investigation and fuel phase, the number of tests by tier."""
        cells = {}
        for t in self.tests:
            tier = marks[t["test_id"]]["tier"]
            if tier in MATCHED:
                key = (t["investigation_id"], plain(t.get("fuel_phase")) or self.texts["phase_not_recorded"])
                cells.setdefault(key, {x: 0 for x in MATCHED})[tier] += 1
        counted = {}
        for need in self.needs:
            for i in self.usable.get(need["id"], set()):
                t = self.by_id[i]
                if marks[i]["tier"] in MATCHED:
                    key = (t["investigation_id"],
                           plain(t.get("fuel_phase")) or self.texts["phase_not_recorded"])
                    counted.setdefault(key, [])
                    if need["id"] not in counted[key]:
                        counted[key].append(need["id"])
        rows = [{"investigation_id": inv, "title": self.title(inv), "fuel_phase": phase, **counts,
                 "counted_for": counted.get((inv, phase), [])}
                for (inv, phase), counts in sorted(cells.items(),
                                                   key=lambda kv: (inv_number(kv[0][0]), kv[0][1]))]
        sentences = []
        for row in rows:
            fields = {**row, "counted_for_n": len(row["counted_for"])}
            s = self.statements.render("environment", fields, f"recorded tests of {row['investigation_id']}",
                                       exactly_one=True)
            sentences.append({**s[0], "investigation_id": row["investigation_id"],
                              "fuel_phase": row["fuel_phase"]})
        return rows, sentences

    def environment(self, env):
        out = {"id": env["id"], "kind": env["kind"], "label": env["label"]}
        if env["kind"] == "scenario":
            out["nominal"] = env.get("nominal", {})
        out["ranges"] = {var: full_range(env["ranges"].get(var), self.engine.RANGE_DEFAULTS)
                         for var in RANGE_VARS}
        out["gravity_level"] = env["gravity_level"]
        out["basis"] = self.references(env.get("basis", []), f"environment {env['id']}")
        out["note"] = env.get("note", "")
        out["caveat"] = env.get("caveat")
        out["see_also"] = self.see_also(env)
        return out

    def indicator_entries(self, marks):
        """The indicators of indicators.json over the tests matched to the
        environment, as {need id: [one entry per indicator and group]}."""
        only = {i for i, m in marks.items() if m["tier"] in MATCHED}
        table, members = self.engine.indicators(
            self.tests, self.links, self.needs, self.ind_spec, self.variables, self.derived,
            set(self.ref_items), only=only)
        behind = {}
        for row in members.to_dict("records"):
            behind.setdefault((row["indicator_id"], row["group"]), []).append(row["test_id"])
        entries = {}
        for row in table.to_dict("records"):
            key = (row["indicator_id"], row["group"])
            ind = self.ind_by_id[row["indicator_id"]]
            if key not in entries:
                entries[key] = {
                    "indicator_id": row["indicator_id"], "need_id": row["need_id"],
                    "label": row["label"], "template": ind["template"],
                    "population": ind["population"], "group": row["group"],
                    "variable": plain(row["variable"]), "unit": plain(row["unit"]),
                    "n_tests": int(row["n_tests"]),
                    "investigation_ids": [x for x in row["investigation_ids"].split(";") if x],
                    "values": [],
                    "definition_ref": [x for x in row["definition_ref"].split(";") if x],
                    "compare_with": [x for x in row["compare_with"].split(";") if x],
                    "reading": row["reading"],
                    "test_ids": sorted(behind[key], key=self.test_key)}
            value = plain(row["value"])
            entries[key]["values"].append({"stat": row["stat"], "category": row["category"],
                                           "value": int(value) if row["stat"] == "count" else value})
        by_need = {}
        for entry in entries.values():
            assert entry["n_tests"] == len(entry["test_ids"]), entry["indicator_id"]
            by_need.setdefault(entry["need_id"], []).append(entry)
        return by_need

    def group_text(self, entry):
        """'a=x;b=y' of indicators.csv written with the texts of the spec."""
        t = self.texts["indicator_text"]
        names = self.ind_by_id[entry["indicator_id"]]["group_by"]
        if not names:
            return t["group_none"]
        m = re.fullmatch(";".join(re.escape(n) + "=(.*)" for n in names), entry["group"])
        if not m:
            raise SystemExit(f"indicator {entry['indicator_id']}: group not readable: {entry['group']}")
        return t["group_join"].join(
            self.statements.fill(t["group_item"], {"name": self.texts["labels"].get(n, n),
                                                   "value": v or t["group_value_empty"]},
                                 "indicator_text.group_item")
            for n, v in zip(names, m.groups()))

    def need_block(self, env, env_out, need, row, marks, indicators):
        ids = sorted(self.usable.get(need["id"], set()), key=self.test_key)
        tier = {i: marks[i]["tier"] for i in ids}
        counts = {name: int(row[column]) for name, column in COUNTS.items()}
        where = f"{env['id']} x {need['id']}"

        investigations = {}
        for i in ids:
            inv = self.by_id[i]["investigation_id"]
            investigations.setdefault(inv, {"investigation_id": inv, "title": self.title(inv),
                                            **{t: 0 for t in TIERS}})[tier[i]] += 1

        variables = list(dict.fromkeys(need["conditions_required"] + need.get("conditions_useful", [])
                                       + need["outcomes_any"]))
        matched = []
        for i in ids:
            if tier[i] not in MATCHED:
                continue
            t, m = self.by_id[i], marks[i]
            matched.append({
                "test_id": i, "investigation_id": t["investigation_id"], "source_id": t["source_id"],
                "tier": m["tier"], "o2_match": m["o2_pct"], "pressure_match": m["pressure_kpa"],
                "flow_match": m["flow_cms"], "gravity_match": m["gravity"],
                "added_gas": m["added_gas"], "fuel_phase": plain(t.get("fuel_phase")),
                "values": {v: {"value": plain(t[v]), "unit": self.units[v],
                               "source_column": t["_origin"][v]}
                           for v in variables if not self.engine.empty(t.get(v))},
                "flags": list(t["_flags"]),
                "source_file": t["source_file"], "source_row": t["source_row"]})

        rest = [self.by_id[i] for i in ids if tier[i] == "other"]
        elsewhere = {"tests": len(rest)}
        for var in ("o2_pct", "pressure_kpa"):
            recorded = [plain(t[var]) for t in rest if not self.engine.empty(t.get(var))
                        and (var != "o2_pct" or t.get("o2_basis") == "ambient")]
            elsewhere[var] = {"recorded": len(recorded),
                              "min": min(recorded) if recorded else None,
                              "max": max(recorded) if recorded else None,
                              "unit": self.units[var]}
        # same rule as the mark 'not_ambient' of run.match_environments
        elsewhere["o2_pct"]["not_ambient"] = sum(
            not self.engine.empty(t.get("o2_pct")) and t.get("o2_basis") != "ambient" for t in rest)
        elsewhere["investigation_ids"] = sorted({t["investigation_id"] for t in rest}, key=inv_number)

        matched_ranges = {}
        for var in ("o2_pct", "pressure_kpa"):
            recorded = [plain(self.by_id[m["test_id"]][var]) for m in matched
                        if not self.engine.empty(self.by_id[m["test_id"]].get(var))
                        and (var != "o2_pct" or self.by_id[m["test_id"]].get("o2_basis") == "ambient")]
            matched_ranges[var] = {"recorded": len(recorded),
                                   "min": min(recorded) if recorded else None,
                                   "max": max(recorded) if recorded else None,
                                   "unit": self.units[var]}
        phases = {}
        for t in matched:
            phases[t["fuel_phase"] or self.texts["phase_not_recorded"]] = \
                phases.get(t["fuel_phase"] or self.texts["phase_not_recorded"], 0) + 1
        documented = self.documented({self.by_id[i]["source_id"] for i in ids}, where)

        block = {"need_id": need["id"], "need": need["name"], "pillar": need["pillar"],
                 "reading": need.get("reading"), "note": need.get("note"),
                 "status": row["status"], "counts": counts,
                 "matched_by_fuel_phase": dict(sorted(phases.items())),
                 "matched_ranges": matched_ranges,
                 "documented_elsewhere": documented,
                 "objective": self.objective.get(need["id"], []),
                 "investigations": sorted(investigations.values(),
                                          key=lambda x: inv_number(x["investigation_id"])),
                 "matched_tests": matched, "usable_elsewhere": elsewhere,
                 "indicators": indicators}

        fields = {"environment_id": env_out["id"], "environment_kind": env_out["kind"],
                  "environment_label": env_out["label"], "gravity_level": env_out["gravity_level"]}
        for var, short in RANGE_VARS.items():
            fields[f"has_{short}_range"] = env_out["ranges"][var] is not None
        fields.update({k: block[k] for k in ("need_id", "need", "pillar", "status")})
        fields.update(counts)
        fields["atmosphere_or_oxygen_only"] = counts["atmosphere"] + counts["oxygen_only"]
        fields["matched_tests"] = len(matched)
        fields["matched_investigation_ids"] = sorted({t["investigation_id"] for t in matched},
                                                     key=inv_number)
        fields["elsewhere_investigation_ids"] = elsewhere["investigation_ids"]
        for var, short in (("o2_pct", "o2"), ("pressure_kpa", "pressure")):
            for k in ("recorded", "min", "max", "unit"):
                fields[f"elsewhere_{short}_{k}"] = elsewhere[var][k]
        fields["elsewhere_o2_not_ambient"] = elsewhere["o2_pct"]["not_ambient"]
        for var, short in (("o2_pct", "o2"), ("pressure_kpa", "pressure")):
            for k in ("recorded", "min", "max", "unit"):
                fields[f"matched_{short}_{k}"] = matched_ranges[var][k]
        fields["need_reading"] = need.get("reading")
        fields["need_note"] = need.get("note")
        fields["matched_fuel_phases"] = [f"{k} {v}" for k, v in sorted(phases.items())]

        st = self.statements
        sentences = st.render("status", fields, where, exactly_one=True)
        sentences += st.render("need", fields, where)
        gaps = []
        for code in [c for c in row["gaps"].split(";") if c]:
            s = st.render("gap", {**fields, "gap": code}, where, exactly_one=True, code=code)
            gaps.append({"code": code, "text": s[0]["text"]})
            sentences += s
        for doc in documented:
            s = st.render("documented", {**fields, **{"doc_" + k: v for k, v in doc.items()}},
                          where, exactly_one=True)
            sentences.append({**s[0], "source_id": doc["source_id"], "variable": doc["variable"]})
        for entry in indicators:
            pop = self.texts["indicator_text"]["population"]
            if entry["population"] not in pop:
                st.stop(f"indicator_text.population has no text for '{entry['population']}'")
            ind_fields = {**fields, **{k: entry[k] for k in (
                "indicator_id", "label", "template", "population", "group", "variable", "unit",
                "n_tests", "investigation_ids", "reading")},
                "population_text": pop[entry["population"]], "group_text": self.group_text(entry),
                "values": None}
            s = st.render("indicator", ind_fields, f"{where} x {entry['indicator_id']}",
                          exactly_one=True,
                          values=[{**v, "unit": entry["unit"]} for v in entry["values"]])
            sentences.append({**s[0], "indicator_id": entry["indicator_id"], "group": entry["group"]})
        block["gaps"] = gaps
        block["statements"] = sentences
        block["references"] = self.references(need.get("references", []), f"need {need['id']}")

        # the lists of the block and the row of the csv must tell the same numbers
        best = [t for t in matched if t["tier"] in ("atmosphere", "oxygen_only")]
        recount = {"usable_tests": len(ids), **{t: sum(v == t for v in tier.values()) for t in TIERS},
                   "recorded_outside_objective": counts["recorded_outside_objective"],
                   "matched_flow_in_range": sum(t["flow_match"] == "in" for t in best),
                   "matched_flow_not_recorded": sum(t["flow_match"] == "not_recorded" for t in best),
                   "matched_same_gravity": sum(t["gravity_match"] == "same" for t in best),
                   "matched_added_gas": sum(t["added_gas"] == "co2_or_helium" for t in best)}
        if (recount != counts or len(matched) != sum(counts[t] for t in MATCHED)
                or any(sum(x[t] for x in block["investigations"]) != counts[t] for t in TIERS)):
            raise SystemExit(f"evidence: {where}: the tests listed in the package give {recount}, "
                             f"the csv row gives {counts}")
        return block

    def package(self, env, rows, marks):
        env_out = self.environment(env)
        env_out["recorded_tests"], env_out["statements"] = self.recorded_tests(marks)
        indicators = self.indicator_entries(marks)
        return {"_meta": self.texts["package_meta"], "environment": env_out,
                "needs": [self.need_block(env, env_out, need, rows[need["id"]], marks,
                                          indicators.get(need["id"], []))
                          for need in self.needs]}


def dump(obj, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False, indent=1, allow_nan=False) + "\n")


def verify(out, folder):
    """Read the files back: every package must carry the status and the counts
    of its row in scenario_needs.csv or atmosphere_cells.csv."""
    rows = {}
    for name in ("scenario_needs.csv", "atmosphere_cells.csv"):
        table = pd.read_csv(os.path.join(out, name), dtype=str, keep_default_na=False)
        rows.update({(r["scenario_id"], r["need_id"]): r for r in table.to_dict("records")})
    with open(os.path.join(folder, "index.json"), encoding="utf-8") as f:
        index = json.load(f)["packages"]
    seen = set()
    for entry in index:
        with open(os.path.join(folder, entry["file"]), encoding="utf-8") as f:
            package = json.load(f)
        for block in package["needs"]:
            key = (package["environment"]["id"], block["need_id"])
            row = rows.get(key)
            same = row is not None and block["status"] == row["status"] == entry["status_by_need"][key[1]] \
                and all(block["counts"][name] == int(row[column]) for name, column in COUNTS.items()) \
                and [g["code"] for g in block["gaps"]] == [c for c in row["gaps"].split(";") if c]
            if not same:
                raise SystemExit(f"evidence: package {entry['file']}, need {key[1]}: status, counts or "
                                 f"gaps differ from the csv row {row}")
            seen.add(key)
    if seen != set(rows):
        raise SystemExit(f"evidence: csv rows without a package block: {sorted(set(rows) - seen)}")


def write(engine, tests, links, obj_links, needs, var_spec, scenario_rows, scenario_marks):
    """Write the packages, the index and atmosphere_cells.csv. scenario_rows and
    scenario_marks are what run.match_scenarios returned for scenario_needs.csv.
    Returns the number of packages."""
    b = Builder(engine, tests, links, obj_links, needs, var_spec)
    scenarios = scenario_environments(engine.spec("scenarios.json"))
    cells = cell_environments(engine.spec("coverage.json"), b.texts["cell"], b.statements)
    # the cells go through the same matching as the scenarios; their test rows
    # are not kept, so scenario_tests.csv holds the named scenarios only
    _, cell_rows, cell_marks = engine.match_environments(tests, links, needs, cells)
    bins = {c["id"]: c for c in cells}
    table = pd.DataFrame([{"scenario_id": r["scenario_id"], "o2_bin": bins[r["scenario_id"]]["o2_bin"],
                           "pressure_bin": bins[r["scenario_id"]]["pressure_bin"],
                           **{k: v for k, v in r.items() if k != "scenario_id"}} for r in cell_rows])
    table.to_csv(os.path.join(engine.OUT, "atmosphere_cells.csv"), index=False)

    rows = {}
    for r in scenario_rows.to_dict("records") + cell_rows:
        rows.setdefault(r["scenario_id"], {})[r["need_id"]] = r
    marks = {**scenario_marks, **cell_marks}
    folder = os.path.join(engine.OUT, "evidence")
    os.makedirs(folder, exist_ok=True)
    index = []
    for env in scenarios + cells:
        package = b.package(env, rows[env["id"]], marks[env["id"]])
        dump(package, os.path.join(folder, env["file"]))
        e = package["environment"]
        index.append({"id": e["id"], "kind": e["kind"], "label": e["label"], "file": env["file"],
                      "ranges": e["ranges"], "gravity_level": e["gravity_level"],
                      "caveat": e["caveat"],
                      "status_by_need": {n["need_id"]: n["status"] for n in package["needs"]},
                      "status_text_by_need": {n["need_id"]: n["statements"][0]["text"]
                                              for n in package["needs"]}})
    dump({"_meta": b.texts["index_meta"], "packages": index}, os.path.join(folder, "index.json"))
    # a package of an environment that is no longer in the specs is removed
    keep = {e["file"] for e in index} | {"index.json"}
    for name in sorted(os.listdir(folder)):
        if name.endswith(".json") and name not in keep:
            os.remove(os.path.join(folder, name))
    verify(engine.OUT, folder)
    return len(index)
