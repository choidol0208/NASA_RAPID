# AI-generated code: written with an AI coding assistant (Claude Code)
# during the NASA Space Apps Challenge 2026 hackathon (2026-11-14).
"""Shared helpers of the lab numbers (branch data-lab): exact decimal reading,
exact decimal writing, the forbidden-word scan and deterministic output.
No sentence or choice is written here: they are in spec/lab_numbers.json."""
import json
import re
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC_PATH = ROOT / "pipeline" / "spec" / "lab_numbers.json"
META = "AI-generated (Claude Code), 2026-11-14. Not human-reviewed."


def fail(msg):
    raise SystemExit("lab numbers: " + msg)


def load_json(path, exact=False):
    with open(path, encoding="utf-8") as fh:
        if exact:
            return json.load(fh, parse_float=Decimal, parse_int=Decimal)
        return json.load(fh)


def spec():
    return load_json(SPEC_PATH)


def frac(x):
    """Exact value of a written decimal (string, Decimal or int)."""
    if isinstance(x, float):
        fail(f"float {x!r} reached exact arithmetic; read it as a string")
    return Fraction(str(x).strip())


def dec(f):
    """Exact decimal string of a Fraction whose denominator has only 2 and 5."""
    f = Fraction(f)
    if f.denominator == 1:
        return str(f.numerator)
    d = f.denominator
    twos = fives = 0
    while d % 2 == 0:
        d //= 2
        twos += 1
    while d % 5 == 0:
        d //= 5
        fives += 1
    if d != 1:
        fail(f"{f} is not a finite decimal")
    k = max(twos, fives)
    n = f * 10 ** k
    assert n.denominator == 1
    s = str(abs(n.numerator)).rjust(k + 1, "0")
    out = s[:-k] + "." + s[-k:]
    out = out.rstrip("0").rstrip(".")
    return ("-" if f < 0 else "") + out


def scan_words(obj, words, where):
    text = json.dumps(obj, ensure_ascii=False) if not isinstance(obj, str) else obj
    for w in words:
        if re.search(r"\b" + re.escape(w) + r"\b", text, re.IGNORECASE):
            fail(f"forbidden word '{w}' in {where}")


def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(obj, ensure_ascii=False, indent=1, sort_keys=True) + "\n")


def write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text if text.endswith("\n") else text + "\n")
