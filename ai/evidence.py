# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""Evidence packets: every PSI record's prose split into numbered, citable units.

For each of the 24 records in data/psi/catalog/ the fields title, objective,
approach, hypothesis and researchImpacts are split into sentences. Each unit
keeps its exact character offsets into the original field string, so
record[field][char_start:char_end] == unit text, always. A citation is then an
ID lookup (PSI-25 / OBJ-2), and a quoted sentence is always shown with the
label of the field it came from ('Stated hypothesis:'), so a hypothesis can
never be shown as a result.

Splitting (standard library only; nltk is not used):
1. Lines. A newline ends a unit, except a soft wrap: a newline after a line that
   does not end in . ! ? or : and before a line that starts with a lower-case letter.
2. A list marker at the start of a line ('1.', '1)', '(a)', 'A.', a bullet) is not
   part of the unit text; it is kept in list_marker.
3. Sentences: . ! or ? (plus closing quotes or brackets), then whitespace, then a
   capital letter, digit or opening bracket. No split after e.g., i.e., vs., Dr.,
   et al., approx., Fig., No., etc. and similar, or after a single capital initial
   or a dotted abbreviation (U.S.). Decimals never split (no whitespace follows the point).

No model is used. Publications are never split or sent to a model; the record's
publication count, DOIs and related investigations are copied.

    python3 ai/evidence.py            # writes data/insights/evidence.json
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ai import config, meta as metamod  # noqa: E402

EVIDENCE_PATH = config.INSIGHTS_DIR / "evidence.json"

# field name -> (unit id prefix, visible label printed before every quote)
FIELDS = {
    "title": ("TTL", "Record title:"),
    "objective": ("OBJ", "Stated objective:"),
    "approach": ("APP", "Planned approach:"),
    "hypothesis": ("HYP", "Stated hypothesis:"),
    "researchImpacts": ("IMP", "Impact statement in the record:"),
}
LICENSE_NOT_STATED = "not stated in the record"
# The design's list (may, might, could, would, expected, potential, suggest, preliminary) plus
# inflections and a few more modal words, so that a hedge gate errs on the strict side.
HEDGE_WORDS = ("may", "might", "could", "would", "should", "expected", "potential", "potentially",
               "suggest", "suggests", "suggested", "preliminary", "possible", "possibly", "likely", "believe")
MIN_QUOTABLE_WORDS = 6

PROTECT = {"e.g.", "i.e.", "vs.", "p.", "pp.", "dr.", "al.", "approx.", "fig.", "figs.", "no.", "nos.",
           "etc.", "eq.", "eqs.", "ref.", "refs.", "cf.", "ca.", "mr.", "ms.", "prof.", "st.", "vol."}

_MARKER = re.compile(r"(?:\(?\d{1,2}\.?\)|\d{1,2}\.|\([A-Za-z]\)|[A-Za-z][.)]|[•●▪◦‣∙·*\-–—])[ \t]+")
_URL = re.compile(r"https?://|doi\.org/|\bdoi:", re.I)
_AUTHOR = re.compile(r"\b[A-Z][A-Za-z'-]+, (?:[A-Z]\.){1,3}(?:,| and\b)")
_BOUNDARY = re.compile(r"[.!?]+[\"'”’)\]]*(?=\s+[\"“‘(\[]?[A-Z0-9])")
_HEDGE = re.compile(r"\b(" + "|".join(HEDGE_WORDS) + r")\b", re.I)
_BARE_MARKER = re.compile(r"^\(?(?:\d{1,3}|[A-Za-z]|[ivxIVX]{1,4})[.)]?$")


# ---------------------------------------------------------------------- splitter

def _blocks(text):
    """Yield (start, end) of line blocks, joining soft-wrapped lines."""
    start = 0
    for m in re.finditer(r"\n", text):
        nl = m.start()
        before = text[start:nl].rstrip()
        after = text[nl + 1:].lstrip(" \t")
        # a soft wrap: the line breaks inside a sentence
        soft = bool(before) and before[-1] not in ".!?:" and (
            after[:1].islower() or before[-1] in ",;(-" or re.search(r"\b(?:and|or|of|the)$", before) is not None)
        if not soft:
            yield start, nl
            start = nl + 1
    yield start, len(text)


def _protected(text, punct_start):
    """True when the period at punct_start ends an abbreviation or initial, not a sentence."""
    j = punct_start
    while j > 0 and not text[j - 1].isspace():
        j -= 1
    token = text[j:punct_start + 1]
    token = re.split(r"[(\[\"'“‘]", token)[-1]  # '27(Vol.' -> 'Vol.'
    low = token.lower()
    if low in PROTECT:
        return True
    if re.fullmatch(r"[A-Z]\.", token):  # single capital initial
        return True
    if re.fullmatch(r"(?:[A-Za-z]\.){2,}", token):  # U.S., i.e. written without spaces
        return True
    return False


def split_field(text):
    """Split one field string. Returns a list of {start, end, list_marker} with text[start:end] the unit."""
    out = []
    for block, (b0, b1) in enumerate(_blocks(text)):
        s = b0
        while s < b1 and text[s].isspace():
            s += 1
        if s >= b1:
            continue
        marker = None
        m = _MARKER.match(text, s, b1)
        if m and m.end() < b1:
            marker = text[s:m.end()].strip()
            s = m.end()
        pieces, cur = [], s
        for bm in _BOUNDARY.finditer(text, s, b1):
            if text[bm.start()] == "." and _protected(text, bm.start()):
                continue
            pieces.append((cur, bm.end()))
            cur = bm.end()
        pieces.append((cur, b1))
        first = True
        for p0, p1 in pieces:
            while p0 < p1 and text[p0].isspace():
                p0 += 1
            while p1 > p0 and text[p1 - 1].isspace():
                p1 -= 1
            if p1 > p0:
                out.append({"start": p0, "end": p1, "list_marker": marker if first else None,
                            "block": block, "in_list_item": marker is not None})
                first = False
    return out


# ---------------------------------------------------------------------- units

def normalise(text):
    """NFKC, straight quotes, collapsed whitespace, lower case: the cross-record comparison key."""
    t = unicodedata.normalize("NFKC", text)
    t = t.translate({0x2018: "'", 0x2019: "'", 0x201C: '"', 0x201D: '"'})
    return re.sub(r"\s+", " ", t).strip().lower()


def _unit(inv, field, k, text, span):
    pre, label = FIELDS[field]
    s = text[span["start"]:span["end"]]
    words = len(s.split())
    heading = s.rstrip().endswith(":")
    bare = bool(_BARE_MARKER.match(s.strip()))
    # a literature reference inside a narrative field (PSI-21 lists four in its hypothesis field)
    reference_like = bool(_URL.search(s)) or len(_AUTHOR.findall(s)) >= 2
    hedges = sorted({h.lower() for h in _HEDGE.findall(s)})
    return {
        "id": f"{pre}-{k}",
        "field": field,
        "prefix": label,
        "source": f"{inv}.{field}",
        "text": s,
        "char_start": span["start"],
        "char_end": span["end"],
        "words": words,
        "quotable": (field != "title" and words >= MIN_QUOTABLE_WORDS and not heading and not bare
                     and not reference_like),
        "reference_like": reference_like,
        "hedged": bool(hedges),
        "hedge_words": hedges,
        "list_marker": span["list_marker"],
        "under_heading": None,
        "shared_with": [],
    }


def _acc_key(acc):
    return int(acc.split("-")[1])


def load_records():
    recs = {}
    for p in sorted(config.PSI_CATALOG_DIR.glob("PSI-*.json"), key=lambda p: _acc_key(p.stem)):
        recs[p.stem] = json.loads(p.read_text(encoding="utf-8"))
    return recs


def build(records=None):
    """Build the evidence payload (without _meta) from the PSI catalog records."""
    records = records or load_records()
    manifest = json.loads(config.PSI_MANIFEST.read_text(encoding="utf-8"))
    man = {x["accession"]: x for x in manifest["investigations"]}
    out = {}
    for inv, rec in records.items():
        units = []
        for field in FIELDS:
            text = rec.get(field) or ""
            if not text.strip():
                continue
            spans = ([{"start": len(text) - len(text.lstrip()), "end": len(text.rstrip()), "list_marker": None,
                       "block": 0, "in_list_item": False}]
                     if field == "title" else split_field(text))
            heading = None  # the latest lead-in line ending with ':' in this field
            ref_blocks = set()  # line blocks that hold a literature reference
            for k, span in enumerate(spans, 1):
                u = _unit(inv, field, k, text, span)
                if u["reference_like"]:
                    ref_blocks.add(span["block"])
                elif span["block"] in ref_blocks or (span["in_list_item"] and any(
                        _URL.search(text[x["start"]:x["end"]]) or len(_AUTHOR.findall(text[x["start"]:x["end"]])) >= 2
                        for x in spans if x["block"] == span["block"])):
                    u["reference_like"], u["quotable"] = True, False  # rest of a reference (journal, year, pages)
                if text[u["char_start"]:u["char_end"]] != u["text"]:
                    raise AssertionError(f"offset round-trip failed: {inv} {u['id']}")
                if span["in_list_item"]:
                    u["under_heading"] = heading  # a list item: read it together with its lead-in line
                elif u["text"].endswith(":"):
                    heading = u["id"]
                else:
                    heading = None  # ordinary prose ends the list
                units.append(u)
        pubs = rec.get("publications") or []
        dois = []
        for p in pubs:
            d = (p.get("doi") or "").strip()
            if d and d not in dois:
                dois.append(d)
        related = [x.strip() for x in (rec.get("related_glds") or "").split(",") if x.strip()]
        out[inv] = {
            "title": rec.get("title") or "",
            "acronym": rec.get("investigationAcronym") or man.get(inv, {}).get("acronym") or "",
            "license": (rec.get("licenseIdentifier") or "").strip() or LICENSE_NOT_STATED,
            "dataset_doi": rec.get("doi") or man.get(inv, {}).get("doi") or None,
            "units": units,
            "pub_count": len(pubs),
            "dois": dois,
            "related": related,
        }
    # cross-record duplicates
    index = {}
    for inv, r in out.items():
        for u in r["units"]:
            if u["field"] == "title":
                continue
            index.setdefault(normalise(u["text"]), set()).add(inv)
    for inv, r in out.items():
        for u in r["units"]:
            if u["field"] == "title":
                continue
            others = index[normalise(u["text"])] - {inv}
            u["shared_with"] = sorted(others, key=_acc_key)
    return {"records": out}


def summary(payload):
    recs = payload["records"]
    per = {inv: len(r["units"]) for inv, r in recs.items()}
    allu = [u for r in recs.values() for u in r["units"]]
    return {
        "records": len(recs),
        "units_total": len(allu),
        "units_per_record": per,
        "units_max": max(per.values()),
        "quotable": sum(u["quotable"] for u in allu),
        "hedged": sum(u["hedged"] for u in allu),
        "shared": sum(bool(u["shared_with"]) for u in allu),
        "by_field": {f: sum(u["field"] == f for u in allu) for f in FIELDS},
    }


def write(path=EVIDENCE_PATH):
    payload = build()
    s = summary(payload)
    inputs = sorted(config.PSI_CATALOG_DIR.glob("PSI-*.json")) + [config.PSI_MANIFEST]
    block = metamod.meta(
        "ai/evidence.py", config.NO_MODEL, inputs,
        label=("AI-generated data file: built by code written with an AI assistant (Claude Code); no language "
               "model ran. Every unit text is copied verbatim from a NASA PSI record field "
               "(record[field][char_start:char_end]); the split into units, the IDs, the field labels and the "
               "quotable, hedged and shared_with flags are the team's code. PSI narrative text states what the "
               "record says, not a measured result."),
        field_labels={f: v[1] for f, v in FIELDS.items()},
        id_scheme="<FIELD>-<k>: TTL-1, OBJ-k, APP-k, HYP-k, IMP-k, numbered in field order from 1",
        quotable_rule=(f"not the title; at least {MIN_QUOTABLE_WORDS} words; does not end with a colon; not a bare "
                       "list number; not reference_like (contains a URL or DOI, or two or more 'Surname, X.' author "
                       "names)"),
        hedged_rule="contains as a whole word: " + ", ".join(HEDGE_WORDS),
        list_rule=("a unit that starts a list line keeps its marker in list_marker; under_heading names the "
                   "preceding unit of the same field that ends with a colon (its lead-in line), if any"),
        shared_rule="identical after NFKC, straight quotes, collapsed whitespace and lower case to a unit of another record",
        license_rule=f"copied from licenseIdentifier; empty is stored as '{LICENSE_NOT_STATED}'",
        counts={k: v for k, v in s.items() if k != "units_per_record"},
    )
    metamod.write_json(path, payload, block)
    return payload, s


# ---------------------------------------------------------------------- accessors for later components

_CACHE = {}


def load(path=EVIDENCE_PATH):
    """Return the parsed evidence.json (cached per path)."""
    path = Path(path)
    if path not in _CACHE:
        _CACHE[path] = json.loads(path.read_text(encoding="utf-8"))
    return _CACHE[path]


def record(investigation_id, ev=None):
    return (ev or load())["records"][investigation_id]


def units(investigation_id, field=None, quotable=None, ev=None):
    out = record(investigation_id, ev)["units"]
    if field is not None:
        out = [u for u in out if u["field"] == field]
    if quotable is not None:
        out = [u for u in out if u["quotable"] == quotable]
    return out


def unit(investigation_id, unit_id, ev=None):
    """Return one unit, e.g. unit('PSI-25', 'OBJ-2'). Raises KeyError if absent."""
    for u in record(investigation_id, ev)["units"]:
        if u["id"] == unit_id:
            return u
    raise KeyError(f"{investigation_id} has no unit {unit_id}")


def quote_line(u):
    """The display form of a quoted unit: <field label> "<sentence>"."""
    return f'{u["prefix"]} "{u["text"]}"'


if __name__ == "__main__":
    _, s = write()
    print(json.dumps({k: v for k, v in s.items()}, indent=1))
