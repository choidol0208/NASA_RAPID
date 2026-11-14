# AI-generated code: written with an AI coding assistant (Claude Code)
# during the NASA Space Apps Challenge 2026 hackathon (2026-11-14).
"""Model map: recount, check and render (branch data-lab, experiment).

Reads pipeline/lab/model_map.json, recounts the classes of the decision
points, writes the counts into its _meta, checks the map (every governing or
candidate key is a model of the map; an 'established' point names a model;
quotes of non-NASA sources have at most 25 words; no forbidden word in team
text) and writes pipeline/lab/model_map.md, derived from the JSON only.

Run: python3 pipeline/lab/model_map_md.py
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
JSON_PATH = HERE / "model_map.json"
MD_PATH = HERE / "model_map.md"
FORBIDDEN = ("safe", "acceptable", "sufficient", "representative", "proven")
NASA_HOSTS = ("nasa.gov",)
QUOTE_KEYS = ("quote", "caveat", "para_", "also_found", "definition_on_page", "scope_caveat", "exactness")
HEADLINE = ("A mapping is \"established\" only if an opened source defines exactly that operation "
            "(or it is elementary mathematics whose definition is the model).")


def fail(msg):
    raise SystemExit("model map: " + msg)


def is_quote_key(k):
    return any(k.startswith(q) or q in k for q in QUOTE_KEYS)


def scan(obj, where):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if not is_quote_key(k):
                scan(v, where + "." + k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            scan(v, "%s[%d]" % (where, i))
    elif isinstance(obj, str):
        for w in FORBIDDEN:
            if re.search(r"\b" + w + r"\b", obj, re.IGNORECASE):
                fail("forbidden word '%s' in team text %s" % (w, where))


def counts_of(points):
    c = {"decision_points": len(points), "established": 0, "established_elementary": 0,
         "established_named_external_model": 0, "team_rule": 0, "team_rule_with_candidate_model": 0,
         "spec_judgement": 0}
    for p in points:
        cls = p["classification"]
        c[cls] += 1
        if cls == "established":
            c["established_elementary" if p["governing_model"] == "ELEM" else "established_named_external_model"] += 1
        if cls == "team_rule" and p.get("candidate_model"):
            c["team_rule_with_candidate_model"] += 1
    return c


def check(m):
    models = m["_meta"]["models"]
    ids = set()
    for p in m["decision_points"]:
        if p["id"] in ids:
            fail("duplicate id " + p["id"])
        ids.add(p["id"])
        if p["classification"] not in ("established", "team_rule", "spec_judgement"):
            fail("unknown class " + p["id"])
        gm = p.get("governing_model")
        if p["classification"] == "established" and gm not in models:
            fail(p["id"] + " established without a model of the map")
        if p["classification"] != "established" and gm:
            fail(p["id"] + " is not established but names a governing model")
        if p.get("candidate_model") and p["candidate_model"] not in models:
            fail(p["id"] + " candidate model unknown: " + p["candidate_model"])
    for k, mod in models.items():
        url = mod.get("url") or ""
        q = mod.get("quote")
        if q and not any(h in url for h in NASA_HOSTS) and len(q.split()) > 25:
            fail("quote of %s has %d words (non-NASA source, limit 25)" % (k, len(q.split())))
        for kk, v in mod.items():
            if isinstance(v, str) and (kk.startswith("para_") or kk.startswith("caveat")) and len(v.split()) > 25:
                fail("%s.%s has more than 25 words" % (k, kk))
    scan(m["decision_points"], "decision_points")
    scan({k: {kk: vv for kk, vv in v.items()} for k, v in models.items()}, "models")
    scan(m["what_mathematics_cannot_remove"], "what_mathematics_cannot_remove")


def cell(x):
    return "" if x is None else str(x).replace("|", "/").replace("\n", " ")


def governing(p):
    if p["classification"] == "established":
        return p["governing_model"]
    s = p["model_name"]
    return s + (" (candidate: %s)" % p["candidate_model"] if p.get("candidate_model") else "")


def render(m):
    c = m["_meta"]["counts"]
    models = m["_meta"]["models"]
    L = ["# Model map (corrected, branch data-lab)", "",
         "*AI-generated (Claude Code), 2026-11-14. Not human-reviewed. Derived from `pipeline/lab/model_map.json` "
         "by `pipeline/lab/model_map_md.py`; edit the JSON, not this file.*", "",
         "Counts over %d decision points: established %d (elementary mathematics %d, named external model %d), "
         "team rule %d (of which %d name a candidate model that defines a related operation), spec-time judgement %d. %s"
         % (c["decision_points"], c["established"], c["established_elementary"], c["established_named_external_model"],
            c["team_rule"], c["team_rule_with_candidate_model"], c["spec_judgement"], HEADLINE), "",
         m["_meta"]["corrected_from"] + ".", "", "## Models (opened sources)", "",
         "| key | model | source | quote (verbatim, short) | opened by | what it does not define |", "|---|---|---|---|---|---|"]
    for k in sorted(models):
        mod = models[k]
        L.append("| %s | %s | %s | %s | %s | %s |" % (k, cell(mod.get("name")), cell(mod.get("url") or mod.get("source")),
                                                   cell(mod.get("quote")), cell(mod.get("opened_by")),
                                                   cell(mod.get("defines_only") or mod.get("exactness") or "")))
    L += ["", "## Decision points", "",
          "| id | where | operation | class | governed by | differs from model / stretch | must change |",
          "|---|---|---|---|---|---|---|"]
    for p in m["decision_points"]:
        diff = p.get("differs_from_model", "")
        if p.get("verifier"):
            diff += " Verifier: " + p["verifier"]
        if p.get("finding_count"):
            diff += " Count: " + p["finding_count"]
        L.append("| %s | %s | %s | %s | %s | %s | %s |" % (p["id"], cell(p["where"].replace("/home/user/nasa_rapid_lab/", "").replace("/home/user/nasa_rapid/", "main:")),
                                                         cell(p["operation"]), p["classification"], cell(governing(p)),
                                                         cell(diff), cell(p.get("must_change"))))
    L += ["", "## Physical and decision models for held data (nothing computed unless stated)", "",
          "| id | model | source | validity | apply | refuse |", "|---|---|---|---|---|---|"]
    for p in m["physical_models"]:
        L.append("| %s | %s | %s | %s | %s | %s |" % (p["id"], cell(p["model"]), cell(p["source"]), cell(p.get("validity")),
                                                   cell(p.get("apply")), cell(p.get("refuse"))))
    L += ["", "## Plan", ""]
    for s in m["plan"]:
        L.append("- %d. %s (%s): %s" % (s["step"], s["model"], s.get("status", ""), s.get("refusal", "")))
    L += ["", "## What mathematics cannot remove", ""]
    for w in m["what_mathematics_cannot_remove"]:
        L.append("- %s: %s." % (w["choice"], w["made_by"]))
    L += ["", "## Not re-checked", ""] + ["- " + x for x in m["_meta"].get("not_rechecked", [])]
    return "\n".join(L) + "\n"


def main():
    m = json.load(open(JSON_PATH, encoding="utf-8"))
    m["_meta"]["counts"] = counts_of(m["decision_points"])
    m["_meta"]["counts_sentence"] = HEADLINE
    check(m)
    with open(JSON_PATH, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(m, indent=1, ensure_ascii=False) + "\n")
    with open(MD_PATH, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(render(m))
    print(json.dumps(m["_meta"]["counts"]))


if __name__ == "__main__":
    main()
