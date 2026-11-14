# AI-generated code: written with an AI coding assistant (Claude Code)
# during the NASA Space Apps Challenge 2026 hackathon (2026-11-14).
"""Shared helpers of the relation-card experiment (branch data-lab).

Loading, verbatim checks of the card spec against references.json, the
forbidden-word scan, range arithmetic and deterministic JSON output. No text
or rule of an experiment is written here: it is all in spec/relation_cards.json.
"""
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "pipeline" / "spec"
OUT = ROOT / "data" / "pipeline" / "cards"
CARDS_SPEC = SPEC / "relation_cards.json"


class SpecError(SystemExit):
    pass


def fail(msg):
    raise SpecError("relation cards: " + msg)


def load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(obj, indent=1, ensure_ascii=False, allow_nan=False) + "\n"
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def num(x, nd=6):
    """A plain JSON number: None for missing, int for whole counts, rounded float otherwise."""
    if x is None:
        return None
    if isinstance(x, bool):
        return x
    if isinstance(x, int):
        return x
    try:
        f = float(x)
    except (TypeError, ValueError):
        return x
    if math.isnan(f):
        return None
    return round(f, nd) + 0.0  # + 0.0 turns -0.0 into 0.0


def fmt(x):
    """Number as text, without a trailing '.0'."""
    return "{:g}".format(float(x)) if not isinstance(x, int) else str(x)


# ---------------------------------------------------------------- references

def load_items():
    refs = load_json(SPEC / "references.json")
    items = {}
    for ref in refs["references"]:
        for it in ref["items"]:
            if it["id"] in items:
                fail("duplicate item id " + it["id"])
            items[it["id"]] = {"item": it, "reference": ref}
    return items


def item_field(items, item_id, field):
    if item_id not in items:
        fail("item not in references.json: " + item_id)
    it = items[item_id]["item"]
    if field not in it:
        fail("item %s has no field %s" % (item_id, field))
    return it[field]


def value_at(items, ref):
    """'ITEM:key.path' -> the value in the item's 'values' (integers index lists)."""
    item_id, _, path = ref.partition(":")
    cur = item_field(items, item_id, "values")
    for part in path.split("."):
        if isinstance(cur, list):
            cur = cur[int(part)]
        elif isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            fail("no value %s" % ref)
    return cur


def check_words(items, entry, allowed_fields):
    """A words entry {'item', 'field', 'words'} or {'item', 'field': 'values', 'key'}."""
    field = entry["field"]
    if field not in allowed_fields:
        fail("field %s not allowed here (%s)" % (field, entry["item"]))
    src = item_field(items, entry["item"], field)
    if field == "values":
        if entry.get("key") not in src:
            fail("values key %s not in %s" % (entry.get("key"), entry["item"]))
        return " ".join(src[entry["key"]].keys()) if isinstance(src[entry["key"]], dict) else str(src[entry["key"]])
    if entry["words"] not in src:
        fail("words not verbatim in %s.%s: %r" % (entry["item"], field, entry["words"]))
    return entry["words"]


def verify_cards(spec, items):
    """Stop if a card does not match its items. Returns the gravity vocabulary."""
    vocab = load_json(SPEC / "findings.json")["_meta"]["gravity_vocabulary"]
    factors = spec["_meta"]["units"]["pressure_to_kpa"]
    nd = spec["_meta"]["units"]["rounding_kpa_decimals"]
    statuses = set(spec["_meta"]["status_values"])
    seen = set()
    for card in spec["cards"]:
        cid = card["id"]
        if cid in seen:
            fail("duplicate card " + cid)
        seen.add(cid)
        for iid in card["source_items"]:
            if iid not in items:
                fail("%s: source item %s not in references.json" % (cid, iid))
        for st in card["statement"]:
            check_words(items, st, ("text", "quote", "where"))
        for axis, v in card["validity"].items():
            for nu in v.get("not_used", []):
                check_words(items, nu, ("text", "quote", "where", "note"))
            if v["words"] == "unstated":
                if v["normalized"] != "unstated":
                    fail("%s.%s: words unstated but a normalized value" % (cid, axis))
                continue
            texts = [check_words(items, w, ("text", "quote", "values")) for w in v["words"]]
            joined = " ".join(texts)
            low = joined.lower()
            norm = v["normalized"]
            if norm in ("unstated", "as_written"):
                continue
            if axis == "gravity":
                for level in norm:
                    if not any(re.search(r"(?<![\w-])" + re.escape(w.lower()) + r"(?![\w-])", low) for w in vocab[level]):
                        fail("%s: gravity level %s has no vocabulary word in %r" % (cid, level, joined))
            elif axis == "material":
                for name in norm:
                    if name not in joined:
                        fail("%s: material %s not in the words" % (cid, name))
            elif axis in ("pressure", "oxygen", "flow"):
                for aw in norm["as_written"]:
                    if fmt(aw["value"]) not in joined:
                        fail("%s.%s: as-written value %s not in the words" % (cid, axis, aw["value"]))
                if axis == "pressure":
                    conv = sorted({round(aw["value"] * factors[aw["unit"]], nd) for aw in norm["as_written"]})
                    have = sorted(norm["values"]) if norm["kind"] == "points" else sorted({norm["min"], norm["max"]})
                    if conv != have:
                        fail("%s: pressure %s is not the as-written values times the unit factors %s" % (cid, have, conv))
                elif norm["kind"] == "range":
                    if sorted({aw["value"] for aw in norm["as_written"]}) != sorted({norm["min"], norm["max"]}):
                        fail("%s.%s: range ends are not the as-written values" % (cid, axis))
        st = card["check"].get("status")
        for key in ("status_if_met", "status_if_not_met", "status_if_none", "status_if_refused"):
            if key in card["check"].get("criterion", {}):
                if card["check"]["criterion"][key] not in statuses:
                    fail("%s: unknown status %s" % (cid, card["check"]["criterion"][key]))
        if st is not None and st not in statuses:
            fail("%s: unknown status %s" % (cid, st))
        if not card["in_our_references"]:
            words = card["check"].get("absence_search", [])
            if not words:
                fail("%s: not in our references but no absence_search" % cid)
            for iid, rec in sorted(items.items()):
                for field in ("text", "quote", "where", "note"):
                    txt = str(rec["item"].get(field, "")).lower()
                    for w in words:
                        if w.lower() in txt:
                            fail("%s: '%s' found in %s.%s; the card says no item states it" % (cid, w, iid, field))
    return vocab


# ---------------------------------------------------------------- wording

def forbidden_check(spec, text, where):
    for w in spec["_meta"]["forbidden_words"]:
        if re.search(r"\b" + re.escape(w) + r"\b", text, flags=re.IGNORECASE):
            fail("forbidden word '%s' in %s: %r" % (w, where, text))


def scan_spec_texts(spec):
    m = spec["_meta"]
    for k, v in m["status_values"].items():
        forbidden_check(spec, v, "status_values." + k)
    for k, v in m["gate"]["sentences"].items():
        forbidden_check(spec, v, "gate.sentences." + k)
        if re.search(r"\d", v):
            fail("digit in template gate.sentences." + k)
    for k, v in m["gate"]["axis_values"].items():
        forbidden_check(spec, v, "gate.axis_values." + k)
    forbidden_check(spec, m["gate"]["overall_note"], "gate.overall_note")
    for card in spec["cards"]:
        cid = card["id"]
        forbidden_check(spec, card["title"], cid + ".title")
        forbidden_check(spec, card["check"]["description"], cid + ".check.description")
        if "criterion" in card["check"]:
            forbidden_check(spec, card["check"]["criterion"]["text"], cid + ".criterion")
        for k in ("status_reason",):
            if k in card["check"]:
                forbidden_check(spec, card["check"][k], cid + "." + k)
        if "placebo" in card["check"]:
            forbidden_check(spec, card["check"]["placebo"]["description"], cid + ".placebo")
        for k, v in card["caption"].items():
            forbidden_check(spec, v, cid + ".caption." + k)


def load_spec():
    spec = load_json(CARDS_SPEC)
    items = load_items()
    vocab = verify_cards(spec, items)
    scan_spec_texts(spec)
    return spec, items, vocab


# ---------------------------------------------------------------- ranges

RANGE_DEFAULTS = {"min": None, "max": None, "min_inclusive": True, "max_inclusive": False}


def full_range(r):
    out = dict(RANGE_DEFAULTS)
    out.update({k: r[k] for k in r if k in RANGE_DEFAULTS})
    return out


def _lower_ok(inner, outer):
    """inner's lower end lies inside outer's lower end."""
    if outer["min"] is None:
        return True
    if inner["min"] is None:
        return False
    if inner["min"] > outer["min"]:
        return True
    if inner["min"] == outer["min"]:
        return outer["min_inclusive"] or not inner["min_inclusive"]
    return False


def _upper_ok(inner, outer):
    if outer["max"] is None:
        return True
    if inner["max"] is None:
        return False
    if inner["max"] < outer["max"]:
        return True
    if inner["max"] == outer["max"]:
        return outer["max_inclusive"] or not inner["max_inclusive"]
    return False


def contains(outer, inner):
    return _lower_ok(inner, outer) and _upper_ok(inner, outer)


def value_in(r, x):
    low = r["min"] is None or x > r["min"] or (x == r["min"] and r["min_inclusive"])
    high = r["max"] is None or x < r["max"] or (x == r["max"] and r["max_inclusive"])
    return low and high


def overlaps(a, b):
    """Two ranges share at least one value."""
    lo = [(r["min"], r["min_inclusive"]) for r in (a, b) if r["min"] is not None]
    hi = [(r["max"], r["max_inclusive"]) for r in (a, b) if r["max"] is not None]
    if not lo or not hi:
        return True
    lmax = max(v for v, _ in lo)
    lin = all(inc for v, inc in lo if v == lmax)
    hmin = min(v for v, _ in hi)
    hin = all(inc for v, inc in hi if v == hmin)
    if lmax < hmin:
        return True
    return lmax == hmin and lin and hin


def render_range(r, unit):
    lo = "(-inf" if r["min"] is None else ("[" if r["min_inclusive"] else "(") + fmt(r["min"])
    hi = "+inf)" if r["max"] is None else fmt(r["max"]) + ("]" if r["max_inclusive"] else ")")
    return "%s, %s %s" % (lo, hi, unit)
