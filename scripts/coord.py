#!/usr/bin/env python3
# AI-generated (Claude Code) during the NASA Space Apps Challenge 2026 hackathon.
"""Team coordination helper for the three role sessions (pm, data, ui).

It reads coordination files from every remote branch, so a session sees another
role's status, requests and answers as soon as that role pushes its own branch.
Each coordination file has exactly one writer, so merges never conflict on them.

Usage (run from anywhere inside the repository):
  python3 scripts/coord.py brief                      digest: other roles' status, inbox, outbox, recent main commits
  python3 scripts/coord.py request <to> <title...> [--by HH:MM]
  python3 scripts/coord.py answer <id> <accepted|done|declined>
  python3 scripts/coord.py close <id>                 close one of your own requests
  python3 scripts/coord.py pull [role]                fetch, then merge origin/main (or that role's branch) into your branch
  python3 scripts/coord.py integrate                  pm only: merge every role branch into main
  python3 scripts/coord.py now                        current time in KST

Standard library only. Needs git on PATH.
"""
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone

KST = timezone(timedelta(hours=9))
ID_RE = re.compile(r"^(\d{8}-\d{4})-([a-z]+)-to-([a-z]+)-(.+)$")


def sh(*args, check=True):
    p = subprocess.run(["git", *args], capture_output=True, text=True, cwd=ROOT if "ROOT" in globals() else None)
    if check and p.returncode != 0:
        sys.exit(f"git {' '.join(args)} failed:\n{p.stderr.strip() or p.stdout.strip()}")
    return p.stdout


ROOT = sh("rev-parse", "--show-toplevel").strip()


def now():
    return datetime.now(KST)


def load_roles():
    with open(os.path.join(ROOT, "coord", "roles.json"), encoding="utf-8") as f:
        return json.load(f)


CFG = load_roles()
ROLES = CFG["roles"]
MAIN = CFG.get("integration_branch", "main")


def my_role():
    path = os.path.join(ROOT, ".role")
    if not os.path.exists(path):
        sys.exit("No .role file. Ask your human which role this session has (pm, data or ui) "
                 "and write that one word to .role at the repository root.")
    role = open(path, encoding="utf-8").read().strip()
    if role not in ROLES:
        sys.exit(f".role contains {role!r}; expected one of {', '.join(ROLES)}.")
    return role


def fetch_all(check=True):
    """Fetch every branch explicitly. A single-branch clone would otherwise never update the other role branches."""
    sh("fetch", "--quiet", "origin", "+refs/heads/*:refs/remotes/origin/*", check=check)

def remote_refs():
    out = sh("for-each-ref", "--format=%(refname:short)", "refs/remotes/origin").split()
    return [r for r in out if r not in ("origin", "origin/HEAD")]


def writer_of(path):
    """Role that is allowed to write a coordination file, from its path."""
    name = os.path.basename(path)
    if path.startswith("coord/status/"):
        return name[:-3]
    if path.startswith("coord/requests/"):
        m = ID_RE.match(name[:-3])
        return m.group(2) if m else None
    if path.startswith("coord/answers/"):
        return name[:-3].rsplit(".", 1)[-1]
    return None


def collect(prefix, me=None):
    """Newest version of each file under prefix across all remote branches and the working tree."""
    found = {}
    for ref in remote_refs():
        for p in sh("ls-tree", "-r", "--name-only", ref, "--", prefix, check=False).splitlines():
            if not p.endswith(".md") or os.path.basename(p).startswith("_"):
                continue
            ts = int(sh("log", "-1", "--format=%ct", ref, "--", p, check=False).strip() or 0)
            if p not in found or ts > found[p]["ts"]:
                found[p] = {"text": sh("show", f"{ref}:{p}", check=False), "ts": ts, "where": ref}
    base = os.path.join(ROOT, prefix)
    for d, _, files in os.walk(base):
        for f in files:
            if not f.endswith(".md") or f.startswith("_"):
                continue
            full = os.path.join(d, f)
            p = os.path.relpath(full, ROOT).replace(os.sep, "/")
            text = open(full, encoding="utf-8").read()
            # A local copy wins only for files this role writes (it may be newer than what is pushed).
            if p not in found or (me and writer_of(p) == me and text != found[p]["text"]):
                found[p] = {"text": text, "ts": int(os.path.getmtime(full)), "where": "working tree"}
    return found


def parse(text):
    meta, body = {}, text
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            for line in parts[1].strip().splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip()
            body = parts[2].strip()
    return meta, body


def age(ts):
    mins = int((now().timestamp() - ts) / 60)
    return f"{mins} min ago" if mins < 120 else f"{mins // 60} h ago"


def load_requests(me):
    reqs = {}
    for p, f in collect("coord/requests", me).items():
        rid = os.path.basename(p)[:-3]
        m = ID_RE.match(rid)
        if not m:
            continue
        meta, body = parse(f["text"])
        reqs[rid] = {"id": rid, "from": m.group(2), "to": m.group(3), "meta": meta, "body": body, "answers": {}}
    for p, f in collect("coord/answers", me).items():
        name = os.path.basename(p)[:-3]
        rid, _, role = name.rpartition(".")
        if rid in reqs:
            meta, body = parse(f["text"])
            reqs[rid]["answers"][role] = {"state": meta.get("state", "accepted"), "body": body, "ts": f["ts"]}
    return reqs


def cmd_brief(_):
    me = my_role()
    fetch_all(check=False)
    branch = sh("branch", "--show-current").strip()
    print(f"# Coordination brief  |  role: {me}  |  branch: {branch}  |  {now():%Y-%m-%d %H:%M} KST")
    expected = ROLES[me]["branch"]
    if branch != expected:
        print(f"WARNING: role {me} works on branch {expected!r}, but this checkout is on {branch!r}.")

    print("\n## Other roles")
    statuses = collect("coord/status", me)
    for role in ROLES:
        if role == me:
            continue
        f = statuses.get(f"coord/status/{role}.md")
        if not f:
            print(f"\n### {role}: no status file yet")
            continue
        stale = "  <-- STALE, no update for over 45 min" if now().timestamp() - f["ts"] > 45 * 60 else ""
        print(f"\n### {role}  (changed {age(f['ts'])}, from {f['where']}){stale}")
        print(f["text"].strip())

    reqs = load_requests(me)
    inbox, outbox = [], []
    for r in sorted(reqs.values(), key=lambda r: r["id"]):
        closed = r["meta"].get("closed", "false").lower() == "true"
        if r["from"] == me:
            if not closed:
                outbox.append(r)
        elif r["to"] in (me, "all") and not closed:
            mine = r["answers"].get(me)
            if not mine or mine["state"] == "accepted":
                inbox.append(r)

    print(f"\n## Inbox: {len(inbox)} request(s) waiting for you")
    for r in inbox:
        mine = r["answers"].get(me)
        state = "you accepted it, still to finish" if mine else "OPEN, not answered"
        print(f"\n### {r['id']}  [{state}]  from {r['from']}  needed by {r['meta'].get('needed_by', '-')}")
        print(r["body"])

    print(f"\n## Outbox: {len(outbox)} of your request(s) not closed")
    for r in outbox:
        if not r["answers"]:
            print(f"\n### {r['id']}  [no answer yet]  to {r['to']}  needed by {r['meta'].get('needed_by', '-')}")
        for role, a in r["answers"].items():
            print(f"\n### {r['id']}  [{role}: {a['state']}, {age(a['ts'])}]")
            print(a["body"])
            if a["state"] in ("done", "declined"):
                print(f"-> apply it, then: python3 scripts/coord.py close {r['id']}")

    print(f"\n## Last commits on origin/{MAIN}")
    print(sh("log", "-8", "--format=%h %cr | %s", f"origin/{MAIN}", check=False).strip() or "(none)")
    ahead = sh("rev-list", "--count", f"HEAD..origin/{MAIN}", check=False).strip()
    if ahead and ahead != "0":
        print(f"\norigin/{MAIN} has {ahead} commit(s) you do not have: python3 scripts/coord.py pull")


def slug(words):
    s = re.sub(r"[^a-z0-9]+", "-", " ".join(words).lower()).strip("-")
    return s[:48].strip("-") or "request"


def cmd_request(args):
    me = my_role()
    by = "-"
    if "--by" in args:
        i = args.index("--by")
        by = args[i + 1]
        args = args[:i] + args[i + 2:]
    if len(args) < 2 or args[0] not in list(ROLES) + ["all"] or args[0] == me:
        sys.exit("usage: coord.py request <to: " + "|".join(r for r in list(ROLES) + ["all"] if r != me) + "> <title...> [--by HH:MM]")
    to, title = args[0], " ".join(args[1:])
    rid = f"{now():%Y%m%d-%H%M}-{me}-to-{to}-{slug(args[1:])}"
    path = os.path.join(ROOT, "coord", "requests", rid + ".md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"---\nfrom: {me}\nto: {to}\nopened: {now():%Y-%m-%d %H:%M} KST\nneeded_by: {by}\nclosed: false\n---\n"
                f"# {title}\n\n## What I need\n\n(one concrete deliverable: file, field, decision or fix)\n\n"
                f"## Why\n\n(what it unblocks)\n\n## Until then\n\n(what I do meanwhile)\n")
    print(os.path.relpath(path, ROOT))
    print("Fill in the three sections, commit and push your branch.")


def cmd_answer(args):
    me = my_role()
    if len(args) != 2 or args[1] not in ("accepted", "done", "declined"):
        sys.exit("usage: coord.py answer <request id> <accepted|done|declined>")
    rid, state = args
    if not ID_RE.match(rid):
        sys.exit(f"not a request id: {rid}")
    path = os.path.join(ROOT, "coord", "answers", f"{rid}.{me}.md")
    body = "(what you did or decided, where the result is, or when it will be ready)"
    if os.path.exists(path):
        _, old = parse(open(path, encoding="utf-8").read())
        body = old.split("\n", 2)[-1].strip() if old.startswith("# ") else old
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"---\nrequest: {rid}\nby: {me}\nstate: {state}\nanswered: {now():%Y-%m-%d %H:%M} KST\n---\n# Answer\n\n{body}\n")
    print(os.path.relpath(path, ROOT))
    print("Write the answer text, commit and push your branch.")


def cmd_close(args):
    me = my_role()
    if len(args) != 1:
        sys.exit("usage: coord.py close <request id>")
    path = os.path.join(ROOT, "coord", "requests", args[0] + ".md")
    m = ID_RE.match(args[0])
    if not m or m.group(2) != me or not os.path.exists(path):
        sys.exit("You can close only your own requests that exist in your working tree.")
    text = open(path, encoding="utf-8").read()
    text = re.sub(r"(?m)^closed:.*$", "closed: true", text, count=1)
    open(path, "w", encoding="utf-8").write(text)
    print(f"closed {args[0]} (commit and push)")


def require_clean():
    dirty = sh("status", "--porcelain", "--untracked-files=no").strip()
    if dirty:
        sys.exit("Commit your own changes first (tracked files are modified):\n" + dirty)


# The commit that added scoring/reference/janaf/. It was removed from every branch on 15 November 2026
# (docs/history_rewrite_20261115.md). A branch that still descends from it holds the old history.
REMOVED_COMMIT = "6202f9a0f05c9a5fd9fb00f9d95bf8488bffa26e"


def holds_removed_history(rev):
    p = subprocess.run(["git", "merge-base", "--is-ancestor", REMOVED_COMMIT, rev], capture_output=True, cwd=ROOT)
    return p.returncode == 0  # 1: not an ancestor; 128: the old commit is not in this clone at all


def merge(ref):
    """Merge ref into the current branch. On conflict, abort and report. Returns True when merged."""
    for side in ("HEAD", ref):
        if holds_removed_history(side):
            print(f"STOP: {side} still holds the history that was removed from GitHub on 15 November 2026. "
                  "Nothing was merged. Reset this clone first: docs/history_rewrite_20261115.md, "
                  "section 'For team members'. Do not push this branch.")
            return False
    p = subprocess.run(["git", "merge", "--no-edit", ref], capture_output=True, text=True, cwd=ROOT)
    if p.returncode == 0:
        last = (p.stdout.strip().splitlines() or ["merged"])[-1]
        print(f"merged {ref}: {last}")
        return True
    conflicted = sh("diff", "--name-only", "--diff-filter=U", check=False).strip()
    subprocess.run(["git", "merge", "--abort"], capture_output=True, cwd=ROOT)
    print(f"CONFLICT merging {ref}; merge aborted, nothing changed. Files:\n{conflicted or p.stderr.strip()}")
    return False


def cmd_pull(args):
    my_role()
    target = MAIN
    if args:
        if args[0] not in ROLES:
            sys.exit("usage: coord.py pull [" + "|".join(ROLES) + "]")
        target = ROLES[args[0]]["branch"]
    fetch_all()
    require_clean()
    if f"origin/{target}" not in remote_refs():
        sys.exit(f"origin/{target} does not exist yet.")
    ok = merge(f"origin/{target}")
    sys.exit(0 if ok else 3)


def cmd_integrate(_):
    if my_role() != "pm":
        sys.exit("Only the pm role integrates into main.")
    if sh("branch", "--show-current").strip() != MAIN:
        sys.exit(f"Check out {MAIN} first.")
    fetch_all()
    require_clean()
    failed = []
    for role, info in ROLES.items():
        ref = f"origin/{info['branch']}"
        if info["branch"] == MAIN or ref not in remote_refs():
            continue
        if not merge(ref):
            failed.append(role)
    if failed:
        print("Open a request to: " + ", ".join(failed) + " asking them to run `coord.py pull` and resolve on their branch.")
    print(f"Next: run checks, then `git push origin HEAD`.")
    sys.exit(3 if failed else 0)


def cmd_now(_):
    print(f"{now():%Y-%m-%d %H:%M} KST")


COMMANDS = {"brief": cmd_brief, "request": cmd_request, "answer": cmd_answer, "close": cmd_close,
            "pull": cmd_pull, "integrate": cmd_integrate, "now": cmd_now}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        sys.exit(__doc__)
    COMMANDS[sys.argv[1]](sys.argv[2:])
