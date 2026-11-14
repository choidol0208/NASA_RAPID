# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""AI-generation disclosure for every file in data/insights/ (AGENTS.md section 4).

meta() builds the block; write_json() writes a data file with it:

- a file that is a JSON object gets the block under its '_meta' key (first key);
- every file, object or array, gets the same block in the companion file
  data/insights/_meta.json, keyed by file name (the page reads cards.json and
  scenarios.json as arrays, so their disclosure lives only there).

write_json() keeps the earlier generated_at when nothing else in the file
changed, so re-running a deterministic build leaves the file byte-identical.
"""
import fcntl
import hashlib
import json
import os
import sys
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ai import config  # noqa: E402

COMPANION = "_meta.json"


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_json(obj):
    """sha256 of a canonical JSON serialisation (sorted keys, no spaces)."""
    blob = json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _rel(path):
    p = Path(path).resolve()
    try:
        return p.relative_to(config.ROOT).as_posix()
    except ValueError:
        return p.as_posix()


def default_label(language_model_used_at_build):
    if language_model_used_at_build == config.NO_MODEL:
        return ("AI-generated data file: built by code written with an AI assistant (Claude Code). "
                "No language model ran to build it. Text in it is quoted or copied from the cited "
                "NASA sources by code; counts and fields are computed by code. Team output, not a NASA conclusion.")
    return ("AI-generated data file: built by code written with an AI assistant (Claude Code). "
            f"Contains text written by the language model {language_model_used_at_build}, "
            "checked by code gates; see each entry's review fields. Team output, not a NASA conclusion.")


def meta(built_by, language_model_used_at_build=config.NO_MODEL, inputs=(), label=None, **extra):
    """Return the disclosure block.

    built_by                       'ai/<script>.py' (a path under ai/)
    language_model_used_at_build   'none' (config.NO_MODEL) or 'gpt-oss:20b (f38aa0c53da5)' (config.MODEL_LABEL)
    inputs                         iterable of file paths (absolute or repo-relative), hashed into inputs_sha256
    label                          one-sentence disclosure; a default is written from the model value
    extra                          further keys (for example params, prompt_sha256), added as given
    """
    if not str(built_by).startswith("ai/") or not str(built_by).endswith(".py"):
        raise ValueError("built_by must be 'ai/<script>.py'")
    if language_model_used_at_build not in (config.NO_MODEL, config.MODEL_LABEL):
        raise ValueError(f"language_model_used_at_build must be {config.NO_MODEL!r} or {config.MODEL_LABEL!r}")
    hashes = {}
    for p in inputs:
        p = Path(p)
        if not p.is_absolute():
            p = config.ROOT / p
        hashes[_rel(p)] = sha256_file(p)
    block = {
        "built_by": built_by,
        "code_written_with": config.CODE_WRITTEN_WITH,
        "language_model_used_at_build": language_model_used_at_build,
        "generated_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "inputs_sha256": dict(sorted(hashes.items())),
        "label": label or default_label(language_model_used_at_build),
    }
    for k, v in extra.items():
        if k in block:
            raise ValueError(f"extra key {k!r} would overwrite a disclosure field")
        block[k] = v
    return block


def _dump(obj):
    return json.dumps(obj, ensure_ascii=False, indent=1) + "\n"


def _atomic_write(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix="." + path.name, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
        os.chmod(tmp, 0o644)  # mkstemp creates 0600; data files must be readable like any other file
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


@contextmanager
def _lock(directory):
    # The lock file lives in the system temp directory, so data/insights/ holds data files only.
    key = hashlib.sha256(str(Path(directory).resolve()).encode()).hexdigest()[:12]
    with open(Path(tempfile.gettempdir()) / f"nasa_rapid_meta_{key}.lock", "w") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)


def _without_time(block):
    return {k: v for k, v in block.items() if k != "generated_at"}


def write_json(path, payload, block):
    """Write `payload` (dict or list) to `path` with the disclosure `block` from meta().

    The block also gets 'content_sha256': the hash of the payload without '_meta'.
    Returns the block as written.
    """
    path = Path(path)
    if not path.is_absolute():
        path = config.ROOT / path
    if not isinstance(payload, (dict, list)):
        raise TypeError("payload must be a JSON object or array")
    body = {k: v for k, v in payload.items() if k != "_meta"} if isinstance(payload, dict) else payload
    block = dict(block, content_sha256=sha256_json(body))

    with _lock(path.parent):
        companion_path = path.parent / COMPANION
        companion = {}
        if companion_path.exists():
            companion = json.loads(companion_path.read_text(encoding="utf-8"))
        old = companion.get(path.name)
        if old and _without_time(old) == _without_time(block):
            block["generated_at"] = old["generated_at"]  # unchanged content: keep the file byte-identical
        out = ({"_meta": block, **body} if isinstance(payload, dict) else body)
        _atomic_write(path, _dump(out))

        companion[path.name] = block
        self_block = companion.get("_meta") or {
            "built_by": "ai/meta.py",
            "code_written_with": config.CODE_WRITTEN_WITH,
            "language_model_used_at_build": config.NO_MODEL,
            "label": ("Companion disclosure file: one AI-generation disclosure block per file in "
                      "data/insights/, keyed by file name, written by ai/meta.py. The same block is "
                      "inside every file that is a JSON object, under '_meta'."),
        }
        ordered = {"_meta": self_block}
        ordered.update({k: companion[k] for k in sorted(companion) if k != "_meta"})
        _atomic_write(companion_path, _dump(ordered))
    return block
