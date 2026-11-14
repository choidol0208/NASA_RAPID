# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""Verification gates for model-written sentences and team template text (design, component B).

Pure Python, standard library only. Every gate is a small function that returns
(ok, reason); reason is '' when ok. A sentence that fails a gate is rejected,
never edited by code. The gates show that each quote, number and name exists in
the cited NASA text and that an objective or hypothesis is not worded as a
result. They do not show that a paraphrase is faithful; that is why each model
sentence is also reviewed (component E).

Scope. The gates run on model-written sentences and on template text. They never
run on verbatim NASA quotations, which are shown as quotes with their field label.

Model sentences (check_sentence). `evidence` is the model's list of
{id, quote} (cards.json adds source, char_start, char_end):

  1  ids        every cited id exists in that record's packet; 1 to 3 items
  2  quote      after normalisation the quote is a substring of the cited unit,
                and has at least 5 words or is the whole unit; the sentence does not stop
                where a clipped quote stops in the middle of a phrase
  3  numbers    every numeral (with its unit, if any), every number word (one..twenty, the
                tens, hundred, thousand) and every quantity word (twice, half, ...) occurs
                as the same token in a cited quote; no unit conversion
  4  entities   every token with 2+ capitals or a capital and a digit, every capitalised
                mid-sentence word and every application word (lunar, habitat, crew,
                spacecraft, ...) occurs (ignoring case) in the record text
  5  policy     no advice or verdict word (should, must, recommend, safe, ensure, ...), and no
                prediction, coverage, 'never tested' or flammability-verdict wording (LP.WORDING)
  6  lint       the combustion-misconception linter (ai/lint_patterns.py)
  7  length     one complete sentence of at most 35 words that ends with a full stop, is not
                a bare subordinate clause and does not point at text the reader is not shown
                ('the following'); at most 3 summary sentences per card
  8  sources    every cited unit's source string resolves (ai/resolve.py)
  9  shared     not a gate: evidence that is entirely shared text is tagged with the other records
 10  modality   any objective/hypothesis/approach unit cited -> a frame ('aims to', ...);
                impact units only -> that frame or an attribution ('the record states');
                no result verb ('showed', 'found', ...) unless that verb is in the quote
 11  hedge      a cited quote with a hedge (may, could, expected, ...) -> the sentence keeps
                one; a certainty word (will, always, significantly, ...) only if a quote has it

Gates 2, 4, 7, 10 and 11 were tightened by the wording review on 14 November after reading the
69 candidates of the first batch (ai/runs/cards_20261114-v2-all24.jsonl); the cases are in
ai/test_checks.py (ReviewerGapTest). The check names stored in cards.json did not change.

Template statements (check_template): every numeral equals a value in the
statement's facts block; no score, rank number or 'best' and none of LP.WORDING; gate 5; gate 6; a
statement that cites inverse-flame sources says 'burner stream' or 'inverse'.

Quoted NASA text. The wording gates (5, 6, banned, wording) do not read a span inside quotation marks
that is verbatim NASA text (strip_nasa_quotes); text written by the team or the model is always read.

    python3 -m unittest ai.test_checks -v
"""
import csv
import json
import re
import sys
from functools import lru_cache
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ai import config, evidence as evmod, lint_patterns as LP, resolve  # noqa: E402

MAX_WORDS = 35
MAX_SUMMARY_SENTENCES = 3
MAX_EVIDENCE = 3
MIN_QUOTE_WORDS = 5

# names of the per-sentence checks stored in cards.json sentences[].checks
CHECK_NAMES = ("ids_ok", "quote_ok", "numbers_ok", "entities_ok", "policy_ok", "lint_ok", "length_ok",
               "sources_ok", "modality_ok", "hedge_ok")
TEMPLATE_CHECK_NAMES = ("numbers_ok", "banned_ok", "policy_ok", "lint_ok", "inverse_ok")

OK = (True, "")


def _fail(msg):
    return False, msg


# ====================================================================== helpers

def _wb(word):
    """Regex for a word or phrase on word boundaries (spaces match any whitespace)."""
    body = r"\s+".join(re.escape(w) for w in word.split())
    return r"(?<![A-Za-z0-9])" + body + r"(?![A-Za-z0-9])"


def _has_any(text, words):
    return [w for w in words if re.search(_wb(w), text, re.I)]


def _norm_quote(q):
    return evmod.normalise(q).strip(" .,;:")


def sentences_of(text):
    """Split a text into sentences with the evidence splitter (abbreviation-aware)."""
    return [text[x["start"]:x["end"]] for x in evmod.split_field(text)]


_SOURCE_SUFFIX = re.compile(r"\s*\((PSI-\d+) record: ([^()]+)\)\s*$")


def split_source_suffix(text):
    """'Sentence. (PSI-25 record: objective)' -> ('Sentence.', 'PSI-25', ['objective'])."""
    m = _SOURCE_SUFFIX.search(text)
    if not m:
        return text, None, []
    fields = [f.strip() for f in re.split(r",|\band\b", m.group(2)) if f.strip()]
    return text[:m.start()], m.group(1), fields


# ---------------------------------------------------------------- numbers

_UNIT_SYNONYM = {"percent": "%", "per cent": "%", "second": "s", "seconds": "s", "sec": "s",
                 "minute": "min", "minutes": "min", "hour": "h", "hours": "h", "hr": "h", "day": "days",
                 "µm": "um", "μm": "um", "mm^2/s": "mm2/s", "mm²/s": "mm2/s"}
_UNITS_SORTED = sorted(LP.UNITS, key=len, reverse=True)
_UNIT_AFTER = re.compile(r"[ \t]?(" + "|".join(re.escape(u) for u in _UNITS_SORTED) + r")(?![A-Za-z0-9])", re.I)
_NUM = re.compile(r"\d+(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?")


def _unit_norm(u):
    u = u.lower()
    return _UNIT_SYNONYM.get(u, u)


def extract_numbers(text):
    """Numerals in text as dicts {value, unit, start, end}. value is the numeral as written,
    thousands commas removed ('1,867' -> '1867'); unit is the normalised unit token after it or None.
    Digits inside identifiers (CO2, PSI-25, NASA-STD-6001, SAFFIRE-II-C01, 6001B) are not numerals."""
    out = []
    for m in _NUM.finditer(text):
        s, e = m.start(), m.end()
        prev = text[s - 1] if s else ""
        if prev and (prev.isalnum() or prev == "_"):
            continue
        if prev in "-‐–/":
            j = s - 1
            while j > 0 and (text[j - 1].isalnum() or text[j - 1] in "-‐–/._"):
                j -= 1
            if any(c.isalpha() for c in text[j:s]):
                continue  # PSI-25, OCHMO-TB-008, NASA/CP-2003-212103
        unit = None
        nxt = text[e:e + 1]
        if nxt.isalpha():
            run = re.match(r"[A-Za-z°µμ/²^0-9]+", text[e:]).group(0)
            if run.lower() in (u.lower() for u in LP.UNITS):
                unit = _unit_norm(run)
            else:
                continue  # an identifier such as 6001B or 2D
        else:
            um = _UNIT_AFTER.match(text, e)
            if um:
                unit = _unit_norm(um.group(1))
        out.append({"value": m.group(0).replace(",", ""), "unit": unit, "start": s, "end": e})
    return out


def number_words(text):
    return [w.lower() for w in re.findall(r"(?<![A-Za-z])(" + "|".join(LP.NUMBER_WORDS) + r")(?![A-Za-z])",
                                          text, re.I)]


# ---------------------------------------------------------------- entities

_TOKEN = re.compile(r"[A-Za-z0-9][A-Za-z0-9]*(?:['’][A-Za-z]+)?(?:[-/][A-Za-z0-9]+)*")


def entity_tokens(sentence):
    """Tokens that name something: 2+ capitals, a capital plus a digit, or a capitalised
    word that is not the first word of the sentence."""
    out = []
    first = True
    for m in _TOKEN.finditer(sentence):
        tok = re.sub(r"['’]s$", "", m.group(0))
        caps = sum(c.isupper() for c in tok)
        digit = any(c.isdigit() for c in tok)
        is_first = first
        first = False
        if not any(c.isalpha() for c in tok):
            continue
        if caps >= 2 or (caps >= 1 and digit):
            out.append(tok)
        elif tok[0].isupper() and len(tok) > 1 and not is_first:
            out.append(tok)
    return out


_RECORD_TEXT = {}


def record_text(inv, ev):
    """The record's title, acronym and every unit text, joined (the text gate 4 searches)."""
    key = (inv, id(ev))
    if key not in _RECORD_TEXT:
        rec = evmod.record(inv, ev)
        parts = [rec.get("title") or "", rec.get("acronym") or ""] + [u["text"] for u in rec["units"]]
        _RECORD_TEXT[key] = "\n".join(parts)
    return _RECORD_TEXT[key]


# ---------------------------------------------------------------- lexical support

_STOP = set("""about above after again against also among because been before being below between both
could does doing down during each from further have having here into itself just more most must once only other
over same should some such than that their theirs them then there these they this those through under until very
were what when where which while whom will with would your record records investigation study studies studied
""".split())


def _stem(w):
    for suf in ("ing", "ed", "es", "s"):
        if w.endswith(suf) and len(w) - len(suf) >= 4:
            return w[:-len(suf)]
    return w


def content_words(text):
    return {_stem(w) for w in re.findall(r"[a-z]+", evmod.normalise(text)) if len(w) >= 4 and w not in _STOP}


def lexical_support(sentence, unit_texts):
    """Share of the sentence's content words found in its cited units (a soft signal for review order only)."""
    sw = content_words(sentence)
    if not sw:
        return None
    uw = set()
    for t in unit_texts:
        uw |= content_words(t)
    return round(len(sw & uw) / len(sw), 3)


# ====================================================================== the gates (model sentences)

def _units_for(evidence, inv, ev):
    out = []
    for e in evidence:
        try:
            out.append(evmod.unit(inv, e.get("id"), ev))
        except KeyError:
            out.append(None)
    return out


def gate_ids(evidence, inv, ev=None):
    """Gate 1: every cited id exists in this record's packet; 1 to 3 evidence items."""
    try:
        evmod.record(inv, ev)
    except KeyError:
        return _fail(f"ids: no record {inv} in evidence.json")
    if not evidence:
        return _fail("ids: no evidence cited")
    if len(evidence) > MAX_EVIDENCE:
        return _fail(f"ids: {len(evidence)} evidence items, at most {MAX_EVIDENCE}")
    missing = [str(e.get("id")) for e, u in zip(evidence, _units_for(evidence, inv, ev)) if u is None]
    if missing:
        return _fail(f"ids: {', '.join(missing)} not in {inv}")
    return OK


def gate_quote(evidence, inv, ev=None):
    """Gate 2: the quote is a substring of the cited unit (after normalisation) and has
    at least 5 words or is the whole unit."""
    for e, u in zip(evidence, _units_for(evidence, inv, ev)):
        if u is None:
            return _fail(f"quote: unit {e.get('id')} does not exist")
        q = _norm_quote(e.get("quote") or "")
        t = _norm_quote(u["text"])
        if not q:
            return _fail(f"quote: empty quote for {e.get('id')}")
        if q not in t:
            return _fail(f"quote: not in {inv} {u['id']}: {e.get('quote')!r}")
        if len(q.split()) < MIN_QUOTE_WORDS and q != t:
            return _fail(f"quote: {len(q.split())} words from {u['id']}, need {MIN_QUOTE_WORDS} or the whole unit")
    return OK


def _words(text):
    return re.findall(r"[a-z0-9]+", evmod.normalise(text))


def _after_quote(quote, unit_text):
    """The unit text that follows the quote, or None when the quote is not in the unit."""
    q, t = _norm_quote(quote), _norm_quote(unit_text)
    pos = t.find(q) if q else -1
    return None if pos < 0 else t[pos + len(q):]


def quote_stops_mid_phrase(quote, unit_text):
    """True when the quote ends before the unit does and the unit goes on without punctuation or a
    clause starter: '... obtained in NASA's normal' + ' gravity material flammability screening test'."""
    rest = _after_quote(quote, unit_text)
    if rest is None or not rest.strip(" .,;:"):
        return False
    if rest[:1] in ",;:)" or rest.lstrip()[:1] in ",;:)(":
        return False
    head = rest.lstrip().lower()
    return not any(head.startswith(w + " ") for w in LP.CLAUSE_STARTERS)


def gate_truncation(sentence, evidence, inv, ev=None):
    """Gate 2, second part: where a clipped quote stops in the middle of a phrase, the sentence
    must go on as the source does (for at least two words). The first batch had sentences that
    stopped with the quote ('compared to those obtained in NASA's normal.', 'in microgravity can
    provide insights.') and one that skipped the next words and changed the claim ('burn as well
    [if not better than] the same material'): verbatim quotes, altered sentences."""
    sw = _words(sentence)
    for e, u in zip(evidence, _units_for(evidence, inv, ev)):
        if u is None:
            continue
        q = e.get("quote") or ""
        qw = _words(_norm_quote(q))
        if len(qw) < 3 or not quote_stops_mid_phrase(q, u["text"]):
            continue
        tail = qw[-3:]
        hits = [i for i in range(len(sw) - 2) if sw[i:i + 3] == tail]
        if not hits:
            continue  # the sentence does not use the end of this quote
        rest = (_after_quote(q, u["text"]) or "").strip()
        want = _words(rest)[:2]
        got = sw[hits[-1] + 3:hits[-1] + 5]
        if got != want:
            how = "stops" if not got else "leaves the source"
            return _fail(f"quote: the sentence {how} where its clipped quote of {u['id']} stops, in the middle "
                         f"of a phrase (the source goes on: '{rest[:50]}')")
    return OK


def gate_numbers(sentence, quotes):
    """Gate 3: every numeral (with its unit), every number word and every quantity word occurs as
    the same token in a cited quote. '21%' does not match '0.21'; '10.2 psi' does not match '70.3 kPa'."""
    qnums = [n for q in quotes for n in extract_numbers(q)]
    for n in extract_numbers(sentence):
        cands = [q for q in qnums if q["value"] == n["value"]]
        if not cands:
            return _fail(f"numbers: {n['value']}{n['unit'] or ''} is not in a cited quote")
        if n["unit"] and not any(q["unit"] == n["unit"] for q in cands):
            return _fail(f"numbers: {n['value']} {n['unit']} - the cited quote has {n['value']} with "
                         f"{', '.join(sorted({str(q['unit']) for q in cands}))}")
    qwords = set(w for q in quotes for w in number_words(q))
    for w in number_words(sentence):
        if w not in qwords:
            return _fail(f"numbers: number word {w!r} is not in a cited quote")
    quote_text = " ".join(quotes)
    for w in _has_any(sentence, LP.QUANTITY_WORDS):
        if not re.search(_wb(w), quote_text, re.I):
            return _fail(f"numbers: quantity word {w!r} is not in a cited quote")
    return OK


def gate_entities(sentence, inv, ev=None):
    """Gate 4: every name-like token occurs, ignoring case, in the record's title, acronym or units."""
    text = record_text(inv, ev)
    for tok in entity_tokens(sentence):
        if tok.lower() in LP.ALLOWED_NAMES:
            continue
        if not re.search(r"(?<![A-Za-z0-9])" + re.escape(tok) + r"(?![A-Za-z0-9])", text, re.I):
            return _fail(f"entities: {tok!r} is not in the {inv} record")
    # application words are lower case, so the rule above does not see them
    for w in _has_any(sentence, LP.APPLICATION_WORDS):
        if not re.search(_wb(w), text, re.I):
            return _fail(f"entities: application word {w!r} is not in the {inv} record")
    return OK


# ---------------------------------------------------------------------- verbatim NASA quotes in team text
# A span inside quotation marks ("...", '...', or curly quotes) that is verbatim NASA text (a PSI record
# field, a cell or note of a PSI experimental table, or the 'quote' of a references.json or sources.json
# item, compared after ai.evidence.normalise) is NASA's wording, not the team's or the model's. The
# wording gates (policy, wording, banned, lint) do not read such spans; every other word of the text is
# read. A quoted span that is not verbatim NASA text is read like any other text.
_QUOTED_SPAN = re.compile(r'"([^"\n]+)"|“([^”\n]+)”|(?<![A-Za-z0-9])\'([^\'\n]+?)\'(?![A-Za-z0-9])'
                          r"|(?<![A-Za-z0-9])‘([^’\n]+?)’(?![A-Za-z0-9])")
QUOTE_PLACEHOLDER = '"(quoted NASA text)"'


def _strings(obj, out):
    if isinstance(obj, str):
        out.append(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            _strings(v, out)
    elif isinstance(obj, list):
        for v in obj:
            _strings(v, out)
    return out


def _quotes_of(obj, out):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "quote" and isinstance(v, str):
                out.append(v)
            else:
                _quotes_of(v, out)
    elif isinstance(obj, list):
        for v in obj:
            _quotes_of(v, out)
    return out


@lru_cache(maxsize=1)
def nasa_text_corpus():
    """Normalised NASA text that a team sentence may quote verbatim."""
    parts = []
    for p in sorted(config.PSI_CATALOG_DIR.glob("PSI-*.json")):
        _strings(json.loads(p.read_text(encoding="utf-8")), parts)
    tables = config.ROOT / "data" / "psi" / "experimental_tables"
    for p in sorted(tables.glob("*.csv")):
        with open(p, newline="", encoding="utf-8-sig", errors="replace") as f:
            for row in csv.reader(f):
                parts += [c for c in row if c.strip()]
    for rel in ("pipeline/spec/references.json", "pipeline/spec/sources.json"):
        p = config.ROOT / rel
        if p.exists():
            _quotes_of(json.loads(p.read_text(encoding="utf-8")), parts)
    return "\n".join(evmod.normalise(x) for x in parts)


def quoted_nasa_spans(text):
    """[(start, end, inner text)] of the quoted spans of `text` that are verbatim NASA text."""
    out = []
    corpus = None
    for m in _QUOTED_SPAN.finditer(text or ""):
        inner = next(g for g in m.groups() if g is not None)
        key = evmod.normalise(inner).strip(" .,;:")
        if not key:
            continue
        corpus = corpus if corpus is not None else nasa_text_corpus()
        if key in corpus:
            out.append((m.start(), m.end(), inner))
    return out


def strip_nasa_quotes(text):
    """`text` with every quoted verbatim NASA span replaced by a neutral placeholder."""
    out, last = [], 0
    for a, b, _ in quoted_nasa_spans(text):
        out += [text[last:a], QUOTE_PLACEHOLDER]
        last = b
    return "".join(out) + (text or "")[last:]


def gate_policy(sentence):
    """Gate 5: no advice or verdict word or phrase (whole words; 'safety' is allowed). Quoted verbatim
    NASA text is not read."""
    sentence = strip_nasa_quotes(sentence)
    hits = _has_any(sentence, LP.ADVICE_PHRASES) + _has_any(sentence, LP.ADVICE_WORDS)
    if hits:
        return _fail(f"policy: {', '.join(dict.fromkeys(h.lower() for h in hits))}")
    return OK


def gate_wording(text):
    """Part of gate 5 for model sentences (and gate 'banned' for template text): no prediction,
    coverage, 'never tested' or flammability-verdict wording outside quoted verbatim NASA text."""
    text = strip_nasa_quotes(text)
    hits = [name for name, rx in LP.WORDING if rx.search(text)]
    if hits:
        return _fail(f"policy: wording {', '.join(hits)}")
    return OK


def gate_lint(sentence):
    """Gate 6: the combustion-misconception linter, sentence by sentence. Quoted verbatim NASA text is
    not read."""
    sentence = strip_nasa_quotes(sentence)
    hits = []
    for s in sentences_of(sentence) or [sentence]:
        hits += LP.lint(s)
    if hits:
        return _fail(f"lint: {', '.join(dict.fromkeys(hits))}")
    return OK


def gate_length(sentence, n_summary=1):
    """Gate 7: one complete sentence of at most 35 words; at most 3 summary sentences in the card.
    Complete means: it ends with a full stop, it is not a bare subordinate clause ('hypothesizes
    that due to X.') and it does not point at text the reader is not shown ('the following')."""
    words = len(sentence.split())
    if words > MAX_WORDS:
        return _fail(f"length: {words} words, at most {MAX_WORDS}")
    parts = sentences_of(sentence)
    if len(parts) > 1:
        return _fail(f"length: {len(parts)} sentences in one item")
    if n_summary > MAX_SUMMARY_SENTENCES:
        return _fail(f"length: {n_summary} summary sentences, at most {MAX_SUMMARY_SENTENCES}")
    body = sentence.strip()
    if body and not body.rstrip("\"')”’").endswith("."):
        return _fail("length: the sentence does not end with a full stop")
    dangling = _has_any(body, LP.DANGLING_REFERENCES)
    if dangling:
        return _fail(f"length: '{dangling[0]}' points at text the reader is not shown")
    m = re.search(r"\bthat\s+(" + "|".join(re.escape(w).replace(r"\ ", r"\s+") for w in LP.FRAGMENT_OPENERS) + r")\b",
                  body, re.I)
    if m and "," not in body[m.end():]:
        return _fail(f"length: not a complete sentence: after 'that {m.group(1).lower()} ...' no main clause follows")
    return OK


def gate_sources(evidence, inv, ev=None):
    """Gate 8: every cited unit's source resolves; a stored source or offsets agree with the unit."""
    for e, u in zip(evidence, _units_for(evidence, inv, ev)):
        if u is None:
            return _fail(f"sources: unit {e.get('id')} does not exist")
        src = e.get("source") or u["source"]
        if src != u["source"]:
            return _fail(f"sources: {e.get('id')} is cited as {src}, the unit is {u['source']}")
        try:
            r = resolve.resolve(src)
        except (resolve.SourceNotFound, resolve.BadSource) as exc:
            return _fail(f"sources: {src} does not resolve ({exc})")
        if "char_start" in e or "char_end" in e:
            cs, ce = e.get("char_start"), e.get("char_end")
            if not isinstance(cs, int) or not isinstance(ce, int):
                return _fail(f"sources: {e.get('id')} char offsets are not integers")
            piece = r["text"][cs:ce]
            if piece != (e.get("quote") or "") and piece != u["text"]:
                return _fail(f"sources: {src}[{cs}:{ce}] is neither the quote nor the unit")
    return OK


def shared_tag(evidence, inv, ev=None):
    """Item 9 (not a gate): if every cited unit is text shared with other records, return the
    records that share all of it (else the union); otherwise []."""
    units = [u for u in _units_for(evidence, inv, ev) if u is not None]
    if not units or not all(u["shared_with"] for u in units):
        return []
    common = set(units[0]["shared_with"])
    for u in units[1:]:
        common &= set(u["shared_with"])
    pick = common or {r for u in units for r in u["shared_with"]}
    return sorted(pick, key=lambda x: int(x.split("-")[1]))


def gate_modality(sentence, evidence, inv, ev=None, quotes=None):
    """Gate 10: no PSI record field holds results, so a sentence never reports one.
    When any cited unit is an objective, hypothesis or approach unit, the sentence has a frame
    ('aims to', 'the record hypothesizes', ...). When it rests on impact statements only, it has
    that frame or an attribution ('the record states that'). In both cases it has no result verb
    that the quote lacks."""
    units = [u for u in _units_for(evidence, inv, ev) if u is not None]
    fields = sorted({u["field"] for u in units})
    aims = [f for f in fields if f in LP.NON_RESULT_FIELDS]
    impacts = [f for f in fields if f in LP.IMPACT_FIELDS]
    if not aims and not impacts:
        return OK
    if aims and not _has_any(sentence, LP.MODALITY_FRAMES):
        return _fail(f"modality: rests on {'/'.join(aims)} and has no frame such as 'aims to', "
                     "'the record hypothesizes' or 'the planned approach'")
    if not aims and not _has_any(sentence, LP.MODALITY_FRAMES + LP.ATTRIBUTION_FRAMES):
        return _fail("modality: rests on an impact statement and is not attributed to the record "
                     "('the record states that ...')")
    quote_text = " ".join(quotes if quotes is not None else [e.get("quote") or "" for e in evidence])
    verbs = [v for v in _has_any(sentence, LP.RESULT_VERBS) if not re.search(_wb(v), quote_text, re.I)]
    if verbs:
        return _fail(f"modality: result verb {', '.join(verbs)} in a sentence about an aim, hypothesis or plan")
    return OK


def gate_hedge(sentence, quotes):
    """Gate 11: when a cited quote has a hedge word, the sentence keeps a hedge word; and the
    sentence uses a certainty word (will, always, never, significantly, ...) only when a cited
    quote has the same word."""
    trig = sorted({w.lower() for q in quotes for w in _has_any(q, LP.HEDGE_TRIGGER)})
    if trig and not _has_any(sentence, LP.HEDGE_ACCEPTED):
        return _fail(f"hedge: the quote says {', '.join(trig)}; the sentence drops it")
    quote_text = " ".join(quotes)
    added = [w for w in _has_any(sentence, LP.CERTAINTY_WORDS) if not re.search(_wb(w), quote_text, re.I)]
    if added:
        return _fail(f"hedge: the sentence adds {', '.join(repr(w) for w in added)}, which no cited quote has")
    return OK


def _first_fail(*results):
    return next((r for r in results if not r[0]), OK)


def check_sentence(sentence, evidence, inv, ev=None, n_summary=1):
    """Run gates 1 to 11 on one model-written summary sentence.

    sentence   the model's text (without the bracketed '(PSI-n record: field)' suffix; it is stripped if present)
    evidence   [{id, quote}] as the model returned them (cards.json items with source/char_start/char_end also work)
    inv        'PSI-25'
    Returns {ok, checks{name: bool}, reasons[], lexical_support, shared_with[]}.
    """
    ev = ev or evmod.load()
    body, _, _ = split_source_suffix(sentence)
    evidence = list(evidence or [])
    quotes = [e.get("quote") or "" for e in evidence]
    results = {
        "ids_ok": gate_ids(evidence, inv, ev),
        "quote_ok": _first_fail(gate_quote(evidence, inv, ev), gate_truncation(body, evidence, inv, ev))
        if evidence else _fail("quote: no evidence"),
        "numbers_ok": gate_numbers(body, quotes),
        "entities_ok": gate_entities(body, inv, ev) if inv in ev["records"] else _fail("entities: no record"),
        "policy_ok": _first_fail(gate_policy(body), gate_wording(body)),
        "lint_ok": gate_lint(body),
        "length_ok": gate_length(body, n_summary),
        "sources_ok": gate_sources(evidence, inv, ev) if evidence else _fail("sources: no evidence"),
        "modality_ok": gate_modality(body, evidence, inv, ev, quotes),
        "hedge_ok": gate_hedge(body, quotes),
    }
    units = [u for u in _units_for(evidence, inv, ev) if u is not None] if inv in ev["records"] else []
    checks = {k: v[0] for k, v in results.items()}
    return {
        "ok": all(checks.values()),
        "checks": checks,
        "reasons": [v[1] for v in results.values() if not v[0]],
        "lexical_support": lexical_support(body, [u["text"] for u in units]),
        "shared_with": shared_tag(evidence, inv, ev) if units else [],
    }


def check_summary(items, inv, ev=None):
    """Gate the summary items of one card ([{text, evidence}]). Returns a list of check_sentence results."""
    n = len(items)
    return [check_sentence(it.get("text") or "", it.get("evidence") or [], inv, ev, n_summary=n) for it in items]


# ====================================================================== template text

def _facts_numbers(facts):
    out = []

    def walk(v):
        if isinstance(v, bool) or v is None:
            return
        if isinstance(v, (int, float)):
            out.append(float(v))
        elif isinstance(v, str):
            for n in extract_numbers(v):
                out.append(float(n["value"]))
            s = v.strip().replace(",", "")
            if re.fullmatch(r"-?\d+(?:\.\d+)?", s):
                out.append(abs(float(s)))
        elif isinstance(v, dict):
            for x in v.values():
                walk(x)
        elif isinstance(v, (list, tuple)):
            for x in v:
                walk(x)
    walk(facts)
    return out


def template_numbers(text):
    """Numerals of a template text that must be in facts. '1 g' and '0 g' name gravity levels
    and are skipped; number words two..twenty are counted ('one' is fixed wording: 'one row per')."""
    spans = [(m.start(), m.end()) for m in LP.GRAVITY_NAMES.finditer(text)]
    nums = [n for n in extract_numbers(text) if not any(s <= n["start"] < e for s, e in spans)]
    words = [w for w in number_words(text) if w != "one"]
    return nums, words


def gate_template_numbers(text, facts):
    vals = _facts_numbers(facts or {})
    nums, words = template_numbers(text)
    for n in nums:
        v = float(n["value"])
        if not any(abs(v - f) < 1e-9 for f in vals):
            return _fail(f"numbers: {n['value']}{n['unit'] or ''} is not a value in facts")
    for w in words:
        v = float(LP.NUMBER_WORDS[w])
        if not any(abs(v - f) < 1e-9 for f in vals):
            return _fail(f"numbers: number word {w!r} is not a value in facts")
    return OK


def gate_banned(text):
    """Template text: no score, rank number or 'best', and the wording list of gate_wording; quoted
    verbatim NASA text is not read."""
    text = strip_nasa_quotes(text)
    for phrase in LP.SCOPE_PHRASES_ALLOWED:  # scope of the needs file, not coverage by tests
        text = text.replace(phrase, "no need of this file addresses it")
    hits = [name for name, rx in LP.BANNED_TEMPLATE + LP.WORDING if rx.search(text)]
    if hits:
        return _fail(f"banned: {', '.join(hits)}")
    return OK


@lru_cache(maxsize=1)
def inverse_flame_sources():
    """Source strings that point at inverse-flame (oxidizer_stream) data: sources.json entries of
    tables with oxidizer-stream rows, and the tests.csv rows themselves."""
    srcs, tests = set(), set()
    p = config.ROOT / "data" / "pipeline" / "tests.csv"
    if p.exists():
        with open(p, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r.get("o2_basis") == "oxidizer_stream":
                    srcs.add(r["source_id"])
                    tests.add(r["test_id"])
    return frozenset({f"pipeline/spec/sources.json#{s}" for s in srcs}
                     | {f"data/pipeline/tests.csv#{t}" for t in tests})


def gate_inverse(text, sources):
    srcs = [sources] if isinstance(sources, str) else list(sources or [])
    inv = [s for s in srcs if s in inverse_flame_sources()]
    if inv and not LP.INVERSE_WORDS.search(text):
        return _fail(f"inverse: cites inverse-flame source {inv[0]} without saying 'burner stream' or 'inverse'")
    return OK


def check_template(text, facts=None, sources=()):
    """Checks for one template statement written by team code.
    Returns {ok, checks{numbers_ok, banned_ok, policy_ok, lint_ok, inverse_ok}, reasons[]}."""
    results = {
        "numbers_ok": gate_template_numbers(text, facts),
        "banned_ok": gate_banned(text),
        "policy_ok": gate_policy(text),
        "lint_ok": gate_lint(text),
        "inverse_ok": gate_inverse(text, sources),
    }
    checks = {k: v[0] for k, v in results.items()}
    return {"ok": all(checks.values()), "checks": checks, "reasons": [v[1] for v in results.values() if not v[0]]}


def lint_text(text):
    """Linter and advice hits for any text (report-only use on files pm does not own).
    Returns a list of pattern names; advice words are reported as 'advice:<word>'."""
    hits = []
    for s in sentences_of(text) or [text]:
        hits += LP.lint(s)
    ok, reason = gate_policy(text)
    if not ok:
        hits += ["advice:" + w.strip() for w in reason.split(":", 1)[1].split(",")]
    return list(dict.fromkeys(hits))


if __name__ == "__main__":
    # python3 ai/checks.py 'PSI-25' 'sentence' 'OBJ-1' 'quote' ['OBJ-2' 'quote' ...]
    if len(sys.argv) >= 5:
        inv, sent = sys.argv[1], sys.argv[2]
        rest = sys.argv[3:]
        evid = [{"id": rest[i], "quote": rest[i + 1]} for i in range(0, len(rest) - 1, 2)]
        print(json.dumps(check_sentence(sent, evid, inv), indent=1))
    else:
        print(__doc__)
