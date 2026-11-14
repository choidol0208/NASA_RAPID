# AI-generated code: written with an AI coding assistant (Claude Code)
# during the NASA Space Apps Challenge 2026 hackathon (2026-11-14).
"""Structured argument for one lunar-habitat question (experiment on branch data-lab).

Reads pipeline/spec/argument_lunar_habitat.json and pipeline/spec/references.json,
and the data files named by count pointers. Writes
data/pipeline/lab/argument_lunar_habitat.json and .md.

Node kinds: claim, evidence, inference, defeater, undeveloped. The script stops
(non-zero exit) if:
  - a node kind is unknown, an id is duplicated, or a referenced id is missing;
  - an evidence node names an unknown reference item, or a count pointer does
    not resolve to a number;
  - a 'covers' entry is not a verbatim part of the item field it names;
  - an inference (text or assumptions) contains a numeric token that is not in
    one of the evidence children of the claim it supports;
  - a defeater contains a numeric token that is not in its documented item
    (text, quote, values, or its verbatim 'item_words'; a logical defeater may
    contain none); a claim or an undeveloped claim
    contains any numeric token;
  - a 'documented' basis lacks an item id, or names an unknown one;
  - an assumption is not an object with 'text' (and optional 'added_by');
  - a defeater's 'item_words' are not verbatim in its item (a defeater added
    by the review pass with basis 'documented' must carry them), or one of its
    'cites' pointers does not resolve;
  - a claim has no children (a claim with no evidence is written as an
    'undeveloped' node), or has children but no inference;
  - a forbidden word appears in a team-written string.
It computes no verdict. The summary block holds counts only, per inference and
in total; an assumption with no recorded defeater is listed as such, which does
not mean it has been shown to hold.

Run: python3 pipeline/lab/argument.py
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import governance  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SPEC_PATH = ROOT / "pipeline" / "spec" / "argument_lunar_habitat.json"
REFS_PATH = ROOT / "pipeline" / "spec" / "references.json"
OUT_DIR = ROOT / "data" / "pipeline" / "lab"
OUT_NAME = "argument_lunar_habitat"

KINDS = ("claim", "evidence", "inference", "defeater", "undeveloped")
INFERENCE_BASES = ("documented", "team")
DEFEATER_BASES = ("documented", "logical")
CHILD_KINDS = ("claim", "evidence", "undeveloped")
REVIEW_TAG = "review pass"
NO_DEFEATER_NOTE = "An assumption with no recorded defeater has not been shown to hold."
NUM_RE = re.compile(r"(?<![A-Za-z0-9_.\-/])\d+(?:\.\d+)?(?![A-Za-z0-9_])")


def fail(msg):
    sys.stderr.write("argument: " + msg + "\n")
    sys.exit(1)


def load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


# ---------------------------------------------------------------- references

def load_items():
    items = {}
    for ref in load_json(REFS_PATH)["references"]:
        for it in ref["items"]:
            if it["id"] in items:
                fail("duplicate item id in references.json: " + it["id"])
            items[it["id"]] = (it, ref)
    return items


def item_copy(iid, items):
    it, ref = items[iid]
    out = {"item": iid, "type": it["type"], "text": it["text"], "where": it.get("where"),
           "document": ref["id"], "title": ref["title"], "url": ref.get("url"),
           "access": ref["access"]}
    if "quote" in it:
        out["quote"] = it["quote"]
    if "values" in it:
        out["values"] = it["values"]
    if "note" in it:
        out["note_in_references_json"] = it["note"]
    return out


# ---------------------------------------------------------------- numbers

def flatten_strings(v):
    if isinstance(v, dict):
        out = []
        for k in sorted(v):
            out += [str(k)] + flatten_strings(v[k])
        return out
    if isinstance(v, list):
        out = []
        for x in v:
            out += flatten_strings(x)
        return out
    if isinstance(v, bool) or v is None:
        return []
    if isinstance(v, (int, float)):
        return ["{:g}".format(v), repr(v)]
    return [str(v)]


def numbers_in(strings):
    nums = set()
    for s in strings:
        for m in NUM_RE.finditer(s):
            nums.add(abs(float(m.group(0))))
    return nums


class Stripper:
    """Removes ids and named identifiers before numbers are looked for."""

    def __init__(self, tokens):
        self.tokens = sorted(set(tokens), key=len, reverse=True)

    def __call__(self, s):
        for t in self.tokens:
            s = s.replace(t, " ")
        return s


# ---------------------------------------------------------------- count pointers

def resolve_path(obj, path, where):
    cur = obj
    for step in path:
        if isinstance(step, dict):
            if not isinstance(cur, list) or len(step) != 1:
                fail("bad selector %r in %s" % (step, where))
            (k, v), = step.items()
            hits = [x for x in cur if isinstance(x, dict) and x.get(k) == v]
            if len(hits) != 1:
                fail("selector %r matches %d entries in %s" % (step, len(hits), where))
            cur = hits[0]
        else:
            if not isinstance(cur, dict) or step not in cur:
                fail("key %r not found in %s" % (step, where))
            cur = cur[step]
    return cur


def load_data_file(rel, cache):
    if rel not in cache:
        p = (ROOT / rel).resolve()
        if ROOT not in p.parents or not p.is_file():
            fail("count pointer file not found: " + rel)
        cache[rel] = load_json(p)
    return cache[rel]


# ---------------------------------------------------------------- checks

def check_words(strings, words, where):
    pat = re.compile(r"\b(%s)\b" % "|".join(map(re.escape, words)), re.IGNORECASE)
    for s in strings:
        m = pat.search(s)
        if m:
            fail("forbidden word %r in %s: %r" % (m.group(1), where, s[:90]))


def team_strings(spec):
    meta = spec["_meta"]
    out = []
    for k, v in meta.items():
        if k == "forbidden_words":
            continue
        out += [x for x in flatten_strings(v)]
    for n in spec["nodes"]:
        for k in ("text",):
            if k in n:
                out.append(n[k])
        out += [a["text"] for a in n.get("assumptions", []) if isinstance(a, dict) and "text" in a]
    return out


def check_added_by(obj, where):
    if "added_by" in obj and obj["added_by"] != REVIEW_TAG:
        fail("%s: 'added_by' must be %r" % (where, REVIEW_TAG))


def resolve_cites(n, items, cache):
    out = []
    cites = n.get("cites", [])
    if not isinstance(cites, list):
        fail("defeater %s: 'cites' must be a list" % n["id"])
    for c in cites:
        if not isinstance(c, dict) or "path" not in c or ("item" in c) == ("file" in c):
            fail("defeater %s: a cite needs 'path' and exactly one of 'item' or 'file'" % n["id"])
        if "item" in c:
            if c["item"] not in items:
                fail("defeater %s: cite names unknown item %s" % (n["id"], c["item"]))
            it, _ = items[c["item"]]
            if "values" not in it:
                fail("defeater %s: item %s holds no 'values' to cite" % (n["id"], c["item"]))
            val = resolve_path(it["values"], c["path"], n["id"])
            out.append({"item": c["item"], "path": c["path"], "value": val})
        else:
            data = load_data_file(c["file"], cache)
            val = resolve_path(data, c["path"], n["id"])
            out.append({"file": c["file"], "path": c["path"], "value": val})
    return out


def resolve_covers(node, items, data, meta):
    covers = node.get("covers")
    keys = meta["covers_keys"]
    if not isinstance(covers, dict) or sorted(covers) != sorted(keys):
        fail("evidence %s: 'covers' must have exactly the keys %s" % (node["id"], ", ".join(keys)))
    out = {}
    for k in keys:
        v = covers[k]
        if "item" in node:
            if v == meta["not_stated"]:
                out[k] = v
                continue
            if not isinstance(v, list) or not v:
                fail("evidence %s covers.%s: give a list of verbatim words or '%s'" % (node["id"], k, meta["not_stated"]))
            it, _ = items[node["item"]]
            words = []
            for w in v:
                f = w.get("field")
                if f not in meta["covers_fields"] or f not in it:
                    fail("evidence %s covers.%s: field %r not allowed or absent" % (node["id"], k, f))
                if w["words"] not in it[f]:
                    fail("evidence %s covers.%s: %r is not verbatim in %s.%s" % (node["id"], k, w["words"], node["item"], f))
                words.append({"field": f, "words": w["words"]})
            out[k] = words
        else:
            if v == meta["not_stated_count"]:
                out[k] = v
                continue
            if not isinstance(v, dict) or "path" not in v:
                fail("evidence %s covers.%s: give a path into the count's file or '%s'" % (node["id"], k, meta["not_stated_count"]))
            out[k] = {"path": v["path"], "value": resolve_path(data, v["path"], node["id"])}
    return out


def main():
    spec = load_json(SPEC_PATH)
    meta = spec["_meta"]
    items = load_items()
    cache = {}

    check_words(team_strings(spec), meta["forbidden_words"], "pipeline/spec/argument_lunar_habitat.json")
    if meta["authorship"] != "team reasoning (AI-drafted), not a NASA statement":
        fail("_meta.authorship changed")

    nodes = {}
    for n in spec["nodes"]:
        if n.get("kind") not in KINDS:
            fail("unknown node kind %r (node %s)" % (n.get("kind"), n.get("id")))
        if n["id"] in nodes:
            fail("duplicate node id " + n["id"])
        nodes[n["id"]] = n

    # identifiers in team text are stripped before numbers are looked for
    all_text = " ".join(it["text"] + " " + it.get("quote", "") for it, _ in items.values())
    for t in meta["identifier_tokens"]:
        if t not in all_text:
            fail("identifier token %r is not written in any reference item" % t)
    strip = Stripper(list(items) + list(nodes) + meta["identifier_tokens"])

    # ---- tree
    if spec["top"] not in nodes or nodes[spec["top"]]["kind"] != "claim":
        fail("top must be a claim")
    parent = {}
    for n in nodes.values():
        if n["kind"] != "claim":
            continue
        ch = n.get("children")
        if not ch:
            fail("claim %s has no children; a claim with no evidence is written as an 'undeveloped' node" % n["id"])
        for c in ch:
            if c not in nodes:
                fail("child %s of %s not defined" % (c, n["id"]))
            if nodes[c]["kind"] not in CHILD_KINDS:
                fail("child %s of %s has kind %s" % (c, n["id"], nodes[c]["kind"]))
            if c in parent:
                fail("node %s has two parents (%s, %s)" % (c, parent[c], n["id"]))
            parent[c] = n["id"]
        inf = n.get("inference")
        if inf not in nodes or nodes[inf]["kind"] != "inference":
            fail("claim %s has children but no inference" % n["id"])
        if nodes[inf].get("supports") != n["id"]:
            fail("inference %s does not support claim %s" % (inf, n["id"]))
    seen = set()

    def reach(i):
        if i in seen:
            fail("cycle at " + i)
        seen.add(i)
        for c in nodes[i].get("children", []):
            reach(c)
    reach(spec["top"])
    for n in nodes.values():
        if n["kind"] in CHILD_KINDS and n["id"] not in seen:
            fail("node %s is not reachable from the top claim" % n["id"])
        if n["kind"] in ("claim", "undeveloped"):
            nums = numbers_in([strip(n["text"])])
            if nums:
                fail("%s %s contains a numeric token %s" % (n["kind"], n["id"], sorted(nums)))

    # ---- evidence
    resolved = {}
    for n in nodes.values():
        if n["kind"] != "evidence":
            continue
        if ("item" in n) == ("count" in n):
            fail("evidence %s must have exactly one of 'item' or 'count'" % n["id"])
        extra = set(n) - {"id", "kind", "item", "count", "covers"}
        if extra:
            fail("evidence %s carries free fields %s; evidence holds only an item id or a count pointer" % (n["id"], sorted(extra)))
        if "item" in n:
            if n["item"] not in items:
                fail("evidence %s: unknown item id %s" % (n["id"], n["item"]))
            r = {"id": n["id"], "kind": "evidence", "source": "reference_item"}
            r.update(item_copy(n["item"], items))
            r["covers"] = resolve_covers(n, items, None, meta)
            it, _ = items[n["item"]]
            pool = [it["text"], it.get("quote", ""), it.get("where") or ""] + flatten_strings(it.get("values", {}))
        else:
            c = n["count"]
            if not isinstance(c, dict) or "file" not in c or "path" not in c:
                fail("evidence %s: count pointer needs 'file' and 'path'" % n["id"])
            data = load_data_file(c["file"], cache)
            val = resolve_path(data, c["path"], n["id"])
            if isinstance(val, bool) or not isinstance(val, (int, float)):
                fail("evidence %s: count pointer does not resolve to a number" % n["id"])
            r = {"id": n["id"], "kind": "evidence", "source": "count", "file": c["file"], "path": c["path"],
                 "value": val, "file_note": data.get("_meta", {}).get("note")}
            r["covers"] = resolve_covers(n, items, data, meta)
            pool = flatten_strings(val)
        r["_numbers"] = numbers_in(pool)
        resolved[n["id"]] = r

    # ---- inferences
    for n in nodes.values():
        if n["kind"] != "inference":
            continue
        claim = nodes.get(n.get("supports"))
        if not claim or claim["kind"] != "claim" or claim.get("inference") != n["id"]:
            fail("inference %s: 'supports' must name the claim that names it" % n["id"])
        if n.get("authorship") != meta["authorship"]:
            fail("inference %s: authorship must be %r" % (n["id"], meta["authorship"]))
        if n.get("basis") not in INFERENCE_BASES:
            fail("inference %s: basis must be one of %s" % (n["id"], INFERENCE_BASES))
        if n["basis"] == "documented":
            if not n.get("item"):
                fail("inference %s: documented basis lacks an item id" % n["id"])
            if n["item"] not in items:
                fail("inference %s: unknown item id %s" % (n["id"], n["item"]))
        elif "item" in n:
            fail("inference %s: an item id is given with basis 'team'" % n["id"])
        if not isinstance(n.get("assumptions"), list) or not isinstance(n.get("defeaters"), list):
            fail("inference %s needs 'assumptions' and 'defeaters' lists" % n["id"])
        for i, a in enumerate(n["assumptions"]):
            if not isinstance(a, dict) or not isinstance(a.get("text"), str) or set(a) - {"text", "added_by"}:
                fail("inference %s assumption %d must be an object with 'text' and optional 'added_by'" % (n["id"], i + 1))
            check_added_by(a, "inference %s assumption %d" % (n["id"], i + 1))
        pool = set()
        for c in claim["children"]:
            if nodes[c]["kind"] == "evidence":
                pool |= resolved[c]["_numbers"]
        nums = numbers_in([strip(s) for s in [n["text"]] + [a["text"] for a in n["assumptions"]]])
        bad = sorted(nums - pool)
        if bad:
            fail("inference %s contains numeric tokens not in its evidence children: %s" % (n["id"], bad))
        for d in n["defeaters"]:
            if d not in nodes or nodes[d]["kind"] != "defeater" or nodes[d]["attacks"]["inference"] != n["id"]:
                fail("inference %s lists %s, which is not a defeater attacking it" % (n["id"], d))

    # ---- defeaters
    cited = {}
    for n in nodes.values():
        if n["kind"] != "defeater":
            continue
        att = n.get("attacks") or {}
        inf = nodes.get(att.get("inference"))
        if not inf or inf["kind"] != "inference" or n["id"] not in inf["defeaters"]:
            fail("defeater %s must attack an inference that lists it" % n["id"])
        a = att.get("assumption")
        if a is not None and not (isinstance(a, int) and 1 <= a <= len(inf["assumptions"])):
            fail("defeater %s: assumption index %r out of range" % (n["id"], a))
        if n.get("basis") not in DEFEATER_BASES:
            fail("defeater %s: basis must be one of %s" % (n["id"], DEFEATER_BASES))
        check_added_by(n, "defeater " + n["id"])
        cited[n["id"]] = resolve_cites(n, items, cache)
        if "item_words" in n:
            if n["basis"] != "documented":
                fail("defeater %s: 'item_words' given with basis 'logical'" % n["id"])
            if n.get("item") not in items:
                fail("defeater %s: unknown item id %s" % (n["id"], n.get("item")))
            it, _ = items[n["item"]]
            if not any(n["item_words"] in (it.get(f) or "") for f in meta["covers_fields"]):
                fail("defeater %s: item_words are not verbatim in %s: %r" % (n["id"], n["item"], n["item_words"][:90]))
        elif n.get("added_by") == REVIEW_TAG and n["basis"] == "documented":
            fail("defeater %s: a documented defeater of the review pass must carry 'item_words'" % n["id"])
        nums = numbers_in([strip(n["text"])])
        if n["basis"] == "documented":
            if not n.get("item"):
                fail("defeater %s: documented basis lacks an item id" % n["id"])
            if n["item"] not in items:
                fail("defeater %s: unknown item id %s" % (n["id"], n["item"]))
            it, _ = items[n["item"]]
            pool = numbers_in([it["text"], it.get("quote", ""), n.get("item_words", "")]
                              + flatten_strings(it.get("values", {})))
            if nums - pool:
                fail("defeater %s contains numeric tokens not in its item: %s" % (n["id"], sorted(nums - pool)))
        else:
            if "item" in n:
                fail("defeater %s: an item id is given with basis 'logical'" % n["id"])
            if nums:
                fail("defeater %s (logical) contains numeric tokens %s" % (n["id"], sorted(nums)))

    # ---- undeveloped
    for n in nodes.values():
        if n["kind"] != "undeveloped":
            continue
        sa = n.get("study_asked")
        if sa != meta["no_item"]:
            if not isinstance(sa, list) or not sa:
                fail("undeveloped %s: study_asked must list item ids or be '%s'" % (n["id"], meta["no_item"]))
            for i in sa:
                if i not in items:
                    fail("undeveloped %s: unknown item id %s" % (n["id"], i))

    result = build(spec, nodes, resolved, items, cited)
    md = render_md(result)
    text = json.dumps(result, indent=1, ensure_ascii=False, sort_keys=True, allow_nan=False) + "\n"
    write_text(OUT_DIR / (OUT_NAME + ".json"), text)
    write_text(OUT_DIR / (OUT_NAME + ".md"), md)
    s = result["summary"]
    print("argument: %d claims, %d undeveloped, %d evidence leaves, inferences %s, defeaters %s; wrote %s"
          % (s["claims"], s["undeveloped_claims"], s["evidence_leaves"]["total"],
             s["inferences_by_basis"], s["defeaters_by_basis"], (OUT_DIR / OUT_NAME).relative_to(ROOT)))


# ---------------------------------------------------------------- output

def build(spec, nodes, resolved, items, cited):
    meta = spec["_meta"]
    out_nodes = {}
    for nid in sorted(nodes):
        n = nodes[nid]
        k = n["kind"]
        if k == "evidence":
            r = dict(resolved[nid])
            r.pop("_numbers")
        elif k == "claim":
            r = {"id": nid, "kind": k, "text": n["text"], "inference": n["inference"], "children": n["children"]}
        elif k == "inference":
            r = {"id": nid, "kind": k, "supports": n["supports"], "text": n["text"],
                 "assumptions": [dict({"n": i + 1}, **a) for i, a in enumerate(n["assumptions"])],
                 "authorship": n["authorship"], "basis": n["basis"], "defeaters": n["defeaters"]}
            if n["basis"] == "documented":
                r["basis_item"] = item_copy(n["item"], items)
        elif k == "defeater":
            r = {"id": nid, "kind": k, "attacks": n["attacks"], "text": n["text"], "basis": n["basis"],
                 "authorship": meta["authorship"]}
            if n["basis"] == "documented":
                r["basis_item"] = item_copy(n["item"], items)
            for key in ("added_by", "item_words"):
                if key in n:
                    r[key] = n[key]
            if cited[nid]:
                r["cited_values"] = cited[nid]
        else:
            sa = n["study_asked"]
            r = {"id": nid, "kind": k, "text": n["text"], "evidence": meta["no_item"],
                 "study_asked": sa if sa == meta["no_item"] else [item_copy(i, items) for i in sa]}
        out_nodes[nid] = r

    def count(kind, key=None, val=None):
        return sum(1 for n in nodes.values() if n["kind"] == kind and (key is None or n.get(key) == val))

    ev_items = sorted({n["item"] for n in nodes.values() if n["kind"] == "evidence" and "item" in n})
    summary = {
        "claims": count("claim"),
        "undeveloped_claims": count("undeveloped"),
        "evidence_leaves": {"total": count("evidence"),
                            "reference_items": sum(1 for n in nodes.values() if n["kind"] == "evidence" and "item" in n),
                            "counts": sum(1 for n in nodes.values() if n["kind"] == "evidence" and "count" in n),
                            "distinct_reference_items": len(ev_items)},
        "inferences_by_basis": {b: count("inference", "basis", b) for b in INFERENCE_BASES},
        "assumptions": sum(len(n["assumptions"]) for n in nodes.values() if n["kind"] == "inference"),
        "defeaters_by_basis": {b: count("defeater", "basis", b) for b in DEFEATER_BASES},
        "inferences_with_no_defeater_yet": sorted(n["id"] for n in nodes.values()
                                                  if n["kind"] == "inference" and not n["defeaters"]),
        "assumptions_added_by_review_pass": sum(1 for n in nodes.values() if n["kind"] == "inference"
                                                for a in n["assumptions"] if a.get("added_by") == REVIEW_TAG),
        "defeaters_added_by_review_pass": sum(1 for n in nodes.values() if n["kind"] == "defeater"
                                              and n.get("added_by") == REVIEW_TAG),
        "assumptions_with_no_recorded_defeater": 0,
        "per_inference": {},
        "assumption_note": NO_DEFEATER_NOTE,
        "evidence_access_levels": {},
        "note": "Counts only. No overall verdict is computed or implied.",
    }
    for iid in sorted(n["id"] for n in nodes.values() if n["kind"] == "inference"):
        inf = nodes[iid]
        ds = [nodes[d] for d in inf["defeaters"]]
        attacked = {d["attacks"].get("assumption") for d in ds}
        bare = [i + 1 for i in range(len(inf["assumptions"])) if i + 1 not in attacked]
        summary["per_inference"][iid] = {
            "assumptions": len(inf["assumptions"]),
            "assumptions_added_by_review_pass": sum(1 for a in inf["assumptions"] if a.get("added_by") == REVIEW_TAG),
            "defeaters_by_basis": {b: sum(1 for d in ds if d["basis"] == b) for b in DEFEATER_BASES},
            "defeaters_added_by_review_pass": sum(1 for d in ds if d.get("added_by") == REVIEW_TAG),
            "defeaters_of_the_inference_as_a_whole": sum(1 for d in ds if d["attacks"].get("assumption") is None),
            "assumptions_with_no_recorded_defeater": len(bare),
            "assumption_numbers_with_no_recorded_defeater": bare,
        }
        summary["assumptions_with_no_recorded_defeater"] += len(bare)
    for n in nodes.values():
        if n["kind"] == "evidence" and "item" in n:
            acc = items[n["item"]][1]["access"]
            summary["evidence_access_levels"][acc] = summary["evidence_access_levels"].get(acc, 0) + 1
    return {
        "_meta": {
            "generated_by": meta["generated_by"],
            "header": meta["header"],
            "what_this_is": meta["what_this_is"],
            "method_sources": meta["method_sources"],
            "method_not_sourced": meta["method_not_sourced"],
            "method_sources_read": meta["method_sources_read"],
            "spec": "pipeline/spec/argument_lunar_habitat.json",
            "script": "pipeline/lab/argument.py",
        },
        "governed_by": governance.block(["L19", "L20", "L21"]),
        "top": spec["top"],
        "summary": summary,
        "nodes": out_nodes,
    }


def one_line(s):
    return " ".join(str(s).split())


def covers_text(cov):
    parts = []
    for k in sorted(cov):
        v = cov[k]
        if isinstance(v, str):
            parts.append("%s: %s" % (k, v))
        elif isinstance(v, list):
            parts.append("%s: %s" % (k, "; ".join('"%s"' % w["words"] for w in v)))
        else:
            parts.append("%s: %s" % (k, json.dumps(v["value"], sort_keys=True)))
    return parts


def item_lines(r, pad):
    L = []
    src = "%s (%s), %s; access: %s" % (r["item"], r["type"], r["document"], r["access"])
    L.append(pad + "item: " + src)
    L.append(pad + "  text (team wording in references.json): " + one_line(r["text"]))
    if "quote" in r:
        L.append(pad + '  quote (as printed): "' + one_line(r["quote"]) + '"')
    L.append(pad + "  where: " + one_line(r.get("where")))
    if r.get("url"):
        L.append(pad + "  url: " + r["url"])
    return L


def render_md(res):
    meta = res["_meta"]
    nodes = res["nodes"]
    s = res["summary"]
    L = ["# Structured argument: lunar habitat, material flammability ranking", ""]
    L.append("**" + meta["header"] + "**")
    L.append("")
    L.append("*" + meta["generated_by"] + " Branch data-lab, experiment, not for merge.*")
    L.append("")
    L.append(meta["what_this_is"])
    L.append("")
    L.append("Node kinds: CLAIM (a sentence that can be true or false), INFERENCE (why the children would support the claim; "
             "team reasoning, basis 'documented' if a reference item states the step, 'team' if none does), "
             "EVIDENCE (a reference item or a count copied from a data file; no team text), "
             "DEFEATER (a way an inference or one of its assumptions could fail; 'documented' or 'logical'), "
             "UNDEVELOPED (a claim with no evidence held, with the items that ask for the study).")
    L.append("")
    L.append("## Summary (counts only, no verdict)")
    L.append("")
    L.append("- claims: %d" % s["claims"])
    L.append("- undeveloped claims: %d" % s["undeveloped_claims"])
    L.append("- evidence leaves: %d (reference items %d, counts %d; distinct reference items %d)"
             % (s["evidence_leaves"]["total"], s["evidence_leaves"]["reference_items"],
                s["evidence_leaves"]["counts"], s["evidence_leaves"]["distinct_reference_items"]))
    L.append("- evidence access levels: " + ", ".join("%s %d" % kv for kv in sorted(s["evidence_access_levels"].items())))
    L.append("- inferences by basis: " + ", ".join("%s %d" % kv for kv in s["inferences_by_basis"].items()))
    L.append("- assumptions stated: %d" % s["assumptions"])
    L.append("- defeaters by basis: " + ", ".join("%s %d" % kv for kv in s["defeaters_by_basis"].items()))
    L.append("- inferences with no defeater yet: " + (", ".join(s["inferences_with_no_defeater_yet"]) or "none"))
    L.append("- added by the review pass: %d assumptions, %d defeaters"
             % (s["assumptions_added_by_review_pass"], s["defeaters_added_by_review_pass"]))
    L.append("- assumptions with no recorded defeater: %d. %s" % (s["assumptions_with_no_recorded_defeater"], s["assumption_note"]))
    L.append("- " + s["note"])
    L.append("")
    L.append("Per inference (counts only):")
    L.append("")
    L.append("| Inference | Assumptions (review pass) | Defeaters documented | Defeaters logical | Of the inference as a whole | "
             "Defeaters added by review pass | Assumptions with no recorded defeater |")
    L.append("|---|---|---|---|---|---|---|")
    for iid, p in s["per_inference"].items():
        bare = ", ".join(str(x) for x in p["assumption_numbers_with_no_recorded_defeater"])
        L.append("| %s | %d (%d) | %d | %d | %d | %d | %d%s |" % (
            iid, p["assumptions"], p["assumptions_added_by_review_pass"], p["defeaters_by_basis"]["documented"],
            p["defeaters_by_basis"]["logical"], p["defeaters_of_the_inference_as_a_whole"],
            p["defeaters_added_by_review_pass"], p["assumptions_with_no_recorded_defeater"],
            " (numbers " + bare + ")" if bare else ""))
    L.append("")
    L.append(s["assumption_note"])
    L.append("")
    L.append("## Tree")
    L.append("")
    L.append("```")

    def walk(nid, depth):
        n = nodes[nid]
        pad = "    " * depth
        if n["kind"] == "claim":
            L.append("%s%s CLAIM: %s" % (pad, nid, n["text"]))
            inf = nodes[n["inference"]]
            ip = pad + "  "
            basis = inf["basis"] + (" (" + inf["basis_item"]["item"] + ")" if inf["basis"] == "documented" else "")
            L.append("%s%s INFERENCE [basis: %s; %s]: %s" % (ip, inf["id"], basis, inf["authorship"], inf["text"]))
            if inf["basis"] == "documented":
                L.extend(item_lines(inf["basis_item"], ip + "    basis "))
            for a in inf["assumptions"]:
                tag = " [added by %s]" % a["added_by"] if "added_by" in a else ""
                L.append("%s    assumption %d%s: %s" % (ip, a["n"], tag, a["text"]))
            for d in inf["defeaters"]:
                dn = nodes[d]
                tgt = "assumption %d" % dn["attacks"]["assumption"] if dn["attacks"]["assumption"] else "the inference"
                b = dn["basis"] + (" (" + dn["basis_item"]["item"] + ")" if dn["basis"] == "documented" else "")
                tag = "; added by %s" % dn["added_by"] if "added_by" in dn else ""
                L.append("%s    %s DEFEATER of %s [basis: %s%s]: %s" % (ip, d, tgt, b, tag, dn["text"]))
                if dn["basis"] == "documented":
                    it = dn["basis_item"]
                    if "item_words" in dn:
                        L.append('%s        item words (verbatim): "%s"' % (ip, one_line(dn["item_words"])))
                    else:
                        L.append("%s        %s: %s" % (ip, "quote" if "quote" in it else "text", one_line(it.get("quote", it["text"]))))
                for cv in dn.get("cited_values", []):
                    src = cv["item"] if "item" in cv else cv["file"]
                    L.append("%s        cited value %s %s = %s" % (ip, src, json.dumps(cv["path"], ensure_ascii=False),
                                                              json.dumps(cv["value"], sort_keys=True, ensure_ascii=False)))
            if not inf["defeaters"]:
                L.append("%s    defeaters: none recorded yet" % ip)
            for c in n["children"]:
                walk(c, depth + 1)
        elif n["kind"] == "evidence":
            if n["source"] == "count":
                L.append("%s%s EVIDENCE (count): %s = %s" % (pad, nid, n["file"] + " " + json.dumps(n["path"]), n["value"]))
                if n.get("file_note"):
                    L.append("%s    file note: %s" % (pad, n["file_note"]))
            else:
                L.append("%s%s EVIDENCE" % (pad, nid))
                L.extend(item_lines(n, pad + "    "))
            if n["source"] == "count":
                L.append("%s    covers (the environment of the evidence package the count belongs to, team ranges; "
                         "null = not set; not the conditions of the tests):" % pad)
            else:
                L.append("%s    covers (only what the item states):" % pad)
            for c in covers_text(n["covers"]):
                L.append("%s      %s" % (pad, c))
        else:
            L.append("%s%s UNDEVELOPED: %s" % (pad, nid, n["text"]))
            L.append("%s    evidence: %s" % (pad, n["evidence"]))
            if isinstance(n["study_asked"], str):
                L.append("%s    study asked for: %s" % (pad, n["study_asked"]))
            else:
                for it in n["study_asked"]:
                    L.append('%s    study asked for by %s (%s): %s' % (pad, it["item"], it["document"],
                             '"' + one_line(it["quote"]) + '"' if "quote" in it else one_line(it["text"])))
    walk(res["top"], 0)
    L.append("```")
    L.append("")
    L.append("## Method")
    L.append("")
    for m in meta["method_sources"]:
        L.append("- %s. %s, %s. %s. Terms as found: %s. Taken: %s" % (m["title"], m["author"], m["year"], m["url"],
                                                                      m["terms_as_found"], m["taken"]))
    L.append("- " + meta["method_not_sourced"])
    L.append("- " + meta["method_sources_read"])
    L.append("")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main()
