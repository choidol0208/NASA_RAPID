# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""Resolve any source string used in data/insights/ to the real text or row it names, or raise.

The agreed forms (contracts/README.md, 'From the pm role'), which the page's
sourceLinks() turns into links:

  PSI-25.objective                       a field of data/psi/catalog/PSI-25.json
  PSI-25                                 the PSI record itself (its title)
  doi:10.xxxx/yyyy                       a dataset DOI (data/psi/manifest.json) or a publication
                                         DOI listed in a PSI record, or a DOI in a references.json url
  <repo path>#<id>                       a file and an id inside it:
     data/pipeline/tests.csv#FLEX-41                   CSV: rows whose first column is the id
     data/pipeline/scenario_needs.csv#lunar_habitat/S1 CSV: 'a/b' matches the first two columns
     data/pipeline/objective_links.csv#S1/PSI-69
     data/catalog/configurations.csv#FLEX-C01
     pipeline/spec/references.json#TB008.gaps          JSON: an object whose "id" is the id,
     pipeline/spec/scenarios.json#lunar_habitat        searched at any depth;
     pipeline/spec/sources.json#acme_bre
     pipeline/spec/needs.json#not_covered              or a top-level key, or a key of "_meta";
     data/pipeline/evidence/scenario_iss.json#S1/status.in_atmosphere
                                                       or 'a/b': the one object with id b inside the
                                                       object whose id, need_id, scenario_id or
                                                       investigation_id is a;
     scoring/scoring_config.json#atmosphere_fallback   or a dotted key path

A PSI experimental table is cited through its sources.json entry, never by a
file name that contains spaces. Paths are repo-relative; '..' and absolute paths
are refused.

    python3 ai/resolve.py 'PSI-25.objective' 'doi:10.60555/4qc4-de67' 'data/pipeline/tests.csv#FLEX-41'
"""
import csv
import json
import re
import sys
from functools import lru_cache
from pathlib import Path, PurePosixPath

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ai import config  # noqa: E402


class SourceNotFound(LookupError):
    """The source string is well formed but names nothing that exists."""


class BadSource(ValueError):
    """The source string is not one of the agreed forms."""


_PSI_FIELD = re.compile(r"^(PSI-\d+)\.([A-Za-z_][A-Za-z0-9_]*)$")
_PSI = re.compile(r"^PSI-\d+$")


@lru_cache(maxsize=None)
def _psi(acc):
    p = config.PSI_CATALOG_DIR / f"{acc}.json"
    if not p.exists():
        raise SourceNotFound(f"no PSI record {acc} in data/psi/catalog/")
    return json.loads(p.read_text(encoding="utf-8"))


@lru_cache(maxsize=None)
def _manifest():
    return json.loads(config.PSI_MANIFEST.read_text(encoding="utf-8"))


@lru_cache(maxsize=None)
def _csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    return rows[0], rows[1:]


@lru_cache(maxsize=None)
def _json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _result(source, form, text, data=None, path=None):
    if not isinstance(text, str) or not text.strip():
        raise SourceNotFound(f"{source} resolves to empty text")
    return {"source": source, "form": form, "text": text, "data": data, "path": path}


def _resolve_psi(source):
    m = _PSI_FIELD.match(source)
    if m:
        acc, field = m.groups()
        rec = _psi(acc)
        if field == "record":  # the page's own form for a whole record
            return _result(source, "psi_record", rec.get("title") or "", {"accession": acc},
                           f"data/psi/catalog/{acc}.json")
        if field not in rec:
            raise SourceNotFound(f"PSI record {acc} has no field {field!r}")
        val = rec[field]
        if not isinstance(val, str):
            raise SourceNotFound(f"{acc}.{field} is not a text field")
        return _result(source, "psi_field", val, {"accession": acc, "field": field},
                       f"data/psi/catalog/{acc}.json")
    rec = _psi(source)
    return _result(source, "psi_record", rec.get("title") or "",
                   {"accession": source, "acronym": rec.get("investigationAcronym"), "doi": rec.get("doi")},
                   f"data/psi/catalog/{source}.json")


def _resolve_doi(source):
    doi = source[4:].strip()
    if not doi or "/" not in doi:
        raise BadSource(f"{source!r} is not a DOI")
    low = doi.lower()
    for inv in _manifest()["investigations"]:
        if (inv.get("doi") or "").lower() == low:
            return _result(source, "doi", inv.get("title") or "",
                           {"kind": "psi_dataset", "accession": inv["accession"], "doi": inv["doi"]},
                           "data/psi/manifest.json")
    for p in sorted(config.PSI_CATALOG_DIR.glob("PSI-*.json")):
        rec = _psi(p.stem)
        for pub in rec.get("publications") or []:
            if (pub.get("doi") or "").strip().lower() == low:
                return _result(source, "doi", pub.get("title") or "",
                               {"kind": "publication", "listed_in": p.stem, "doi": pub.get("doi"),
                                "authors": pub.get("authorList")},
                               f"data/psi/catalog/{p.stem}.json")
    refs = config.ROOT / "pipeline" / "spec" / "references.json"
    if refs.exists():
        for r in _json(str(refs)).get("references", []):
            if low in (r.get("url") or "").lower():
                return _result(source, "doi", r.get("title") or "",
                               {"kind": "reference", "reference_id": r.get("id"), "url": r.get("url")},
                               "pipeline/spec/references.json")
    raise SourceNotFound(f"DOI {doi} is not in the PSI manifest, any PSI record's publications or references.json")


def _safe_path(rel):
    pp = PurePosixPath(rel)
    if pp.is_absolute() or ".." in pp.parts or not rel or " " in rel:
        raise BadSource(f"path {rel!r} must be repo-relative, without '..' or spaces")
    p = config.ROOT / rel
    if not p.is_file():
        raise SourceNotFound(f"no file {rel}")
    return p


def _row_text(header, row):
    return "; ".join(f"{h}={v}" for h, v in zip(header, row) if v != "")


def _resolve_csv(source, p, key):
    header, rows = _csv(str(p))
    parts = key.split("/")
    if len(parts) > len(header):
        raise BadSource(f"{source}: more key parts than columns")
    hits = [r for r in rows if r[:len(parts)] == parts]
    if not hits:
        raise SourceNotFound(f"{source}: no row whose first {len(parts)} column(s) "
                             f"({', '.join(header[:len(parts)])}) equal {parts}")
    data = [dict(zip(header, r)) for r in hits]
    text = "\n".join(_row_text(header, r) for r in hits)
    return _result(source, "file_ref", text, {"rows": data, "key_columns": header[:len(parts)]},
                   str(p.relative_to(config.ROOT)))


def _find_id(obj, key):
    if isinstance(obj, dict):
        if obj.get("id") == key:
            return obj
        for v in obj.values():
            hit = _find_id(v, key)
            if hit is not None:
                return hit
    elif isinstance(obj, list):
        for v in obj:
            hit = _find_id(v, key)
            if hit is not None:
                return hit
    return None


_MISSING = object()


def _dotted(obj, key):
    cur = obj
    for part in key.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        elif isinstance(cur, list) and part.isdigit() and int(part) < len(cur):
            cur = cur[int(part)]
        else:
            return _MISSING
    return cur


def _text_of(value):
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        for k in ("quote", "text", "statement", "question", "label", "title", "why"):
            if isinstance(value.get(k), str) and value[k].strip():
                return value[k]
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


SCOPE_KEYS = ("id", "need_id", "scenario_id", "investigation_id")


def _find_all(obj, pred, out, depth=0):
    """[(depth, object)] for every dict that satisfies pred, at any depth."""
    if isinstance(obj, dict):
        if pred(obj):
            out.append((depth, obj))
        for v in obj.values():
            _find_all(v, pred, out, depth + 1)
    elif isinstance(obj, list):
        for v in obj:
            _find_all(v, pred, out, depth + 1)
    return out


def _scoped(source, doc, key):
    """'S1/status.in_atmosphere': the one object whose "id" is the second part, inside the object whose
    id, need_id, scenario_id or investigation_id is the first part (the outermost such object; objects
    nested inside it that carry the same name, such as an indicator's need_id, are part of the scope).
    None when the key has no '/' or the scope does not exist; SourceNotFound when the scope is not
    unique at its depth or the id is missing or not unique inside it."""
    if "/" not in key:
        return None
    scope, inner = key.split("/", 1)
    scopes = _find_all(doc, lambda o: any(o.get(k) == scope for k in SCOPE_KEYS), [])
    if not scopes:
        return None
    top = min(d for d, _ in scopes)
    scopes = [o for d, o in scopes if d == top]
    if len(scopes) > 1:
        raise SourceNotFound(f"{source}: {len(scopes)} objects are named {scope!r}; the scope is not unique")
    hits = [o for _, o in _find_all(scopes[0], lambda o: o.get("id") == inner, [])]
    if len(hits) != 1:
        raise SourceNotFound(f"{source}: {len(hits)} objects with id {inner!r} inside {scope!r} (need exactly one)")
    return hits[0]


def _resolve_json(source, p, key):
    doc = _json(str(p))
    hit, how = None, None
    if isinstance(doc, dict) and key in doc:
        hit, how = doc[key], "top_level_key"
    if hit is None:
        hit, how = _find_id(doc, key), "id"
    if hit is None:
        hit, how = _scoped(source, doc, key), "scoped_id"
    if hit is None and isinstance(doc, dict):
        if isinstance(doc.get("_meta"), dict) and key in doc["_meta"]:
            hit, how = doc["_meta"][key], "_meta_key"
        else:
            v = _dotted(doc, key)
            if v is not _MISSING:
                hit, how = v, "key_path"
    if hit is None:
        raise SourceNotFound(f"{source}: no object with id {key!r}, no key {key!r}")
    return _result(source, "file_ref", _text_of(hit), {"value": hit, "matched_by": how},
                   str(p.relative_to(config.ROOT)))


def resolve(source):
    """Resolve one source string. Returns {source, form, text, data, path}; raises SourceNotFound or BadSource."""
    if not isinstance(source, str) or not source.strip() or source != source.strip():
        raise BadSource(f"{source!r} is not a source string")
    if source.startswith("doi:"):
        return _resolve_doi(source)
    if _PSI_FIELD.match(source) or _PSI.match(source):
        return _resolve_psi(source)
    if "#" in source:
        rel, key = source.split("#", 1)
        if not key or "#" in key:
            raise BadSource(f"{source!r}: expected exactly one '#' followed by an id")
        p = _safe_path(rel)
        if p.suffix == ".csv":
            return _resolve_csv(source, p, key)
        if p.suffix == ".json":
            return _resolve_json(source, p, key)
        raise BadSource(f"{source!r}: only .csv and .json files can be cited with '#id'")
    raise BadSource(f"{source!r} is not one of the agreed forms (PSI-n.field, PSI-n, doi:..., path#id)")


def resolve_all(sources):
    """Resolve a source string or a list of them (the 'sources' arrays in data/insights). Raises on the first failure."""
    if isinstance(sources, str):
        sources = [sources]
    return [resolve(s) for s in sources]


def check(source):
    """True if `source` resolves, False otherwise (never raises for a bad or missing source)."""
    try:
        resolve(source)
        return True
    except (SourceNotFound, BadSource):
        return False


if __name__ == "__main__":
    for s in sys.argv[1:]:
        try:
            r = resolve(s)
            print(f"{s}\n  -> [{r['form']}] {r['path']}: {r['text'][:300]!r}")
        except (SourceNotFound, BadSource) as e:
            print(f"{s}\n  -> FAILED: {e}")
            sys.exit(1)
