# AI-generated code: written with an AI coding assistant (Claude Code)
# during the NASA Space Apps Challenge 2026 hackathon (2026-11-15).
"""Summary of the central directories (member lists) of the PSI .zip archives.

The member lists were read by HTTP range requests (no archive downloaded, no
member opened) by a data-role session job on 15 November 2026 and saved as
one JSON file per archive (<file_id>.json: investigation, key, listing_bytes,
bytes_fetched, members, member_list[{name, uncompressed_bytes, ...}], zip64,
requests) in a scratch folder that is not in the repository. A run.log in the
same folder holds the refusals.

    python3 pipeline/archive_summary.py <folder>

Without the folder (or when it is absent) the script says so and leaves the
committed outputs untouched. It also needs the saved PSI listings
(data/psi/file_listings/, git-ignored). Writes, in data/pipeline/:

  archive_summary.csv          one row per archive whose member list was read:
                               investigation, PSI file id, archive name,
                               listing bytes, bytes fetched, members by
                               extension class, first and last member date,
                               the identifiers that the name rules of
                               spec/raw_names.json find in member names and how
                               the rows they tie relate to the rows the archive
                               name ties, the link level of the archive name
                               and its test where tied
  archive_summary_totals.json  archives listed of all archives of the listings,
                               bytes fetched against archive bytes, members by
                               extension class overall and per investigation,
                               archives whose member identifiers disagree with
                               the archive name, archives not listed with the
                               reason

Member names are tied with the rules of raw_names.py (Investigation.all_ties,
re-applied here with a cache of the row lookups so that 12.6 million names can
be read): the rule order, the first tie decides; a rule with where 'folder' is
applied to the directory path inside the archive.
"""
import collections
import csv
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import raw_inventory  # noqa: E402
import raw_names  # noqa: E402

OUT = os.path.join(ROOT, "data", "pipeline")
GENERATED_BY = "AI-generated (Claude Code), 2026-11-15. Not human-reviewed."
CLASSES = {
    "still_image": ("tif", "tiff", "bmp", "jpeg", "jpg", "jpe", "png", "gif", "nef"),
    "camera_frame_hobj": ("hobj",),
    "text": ("txt", "csv", "log", "xml", "asc", "json", "dat", "tsv"),
}
CLASS_ORDER = ("still_image", "camera_frame_hobj", "text", "other")
RELATIONS = ("no_identifier_in_member_names", "archive_name_ties_no_row", "equal", "member_rows_within_archive_rows",
             "archive_rows_within_member_rows", "disagree")
SHOW = 5
COLUMNS = ("investigation_id", "psi_file_id", "archive_name", "listing_bytes", "bytes_fetched", "zip64", "members",
           "directories", "members_still_image", "members_camera_frame_hobj", "members_text", "members_other",
           "uncompressed_bytes", "first_member_date", "last_member_date", "archive_link_level", "archive_rule",
           "archive_rows", "archive_test_id", "member_identifiers", "member_identifiers_count",
           "members_tied_to_a_test", "members_tied_to_a_day_or_session", "members_not_tied", "member_rows",
           "member_tests", "member_test_ids", "rows_in_both", "identifier_relation")


def ext_class(name):
    base = name.rsplit("/", 1)[-1]
    ext = base.rsplit(".", 1)[-1].lower() if "." in base else ""
    for c, exts in CLASSES.items():
        if ext in exts:
            return c
    return "other"


def first_tie(I, name, folder, category, cache):
    """(rule, level, rows) of the first rule that ties the name, as
    raw_names.Investigation.all_ties()[0]; row lookups are cached."""
    for r in I.rules:
        if r.get("categories") and category not in r["categories"]:
            continue
        if r.get("name_must_match") and not r["name_rx"].search(name):
            continue
        target = folder if r["where"] == "folder" else name
        for m in r["rx"].finditer(target):
            keys = {}
            for g, fld in r["fields"].items():
                if m.group(g) is not None:
                    keys[g] = raw_names.key_value(fld["key"], m.group(g))
            if not keys or any(v is None for v in keys.values()):
                continue
            ck = (r["id"], tuple(sorted(keys.items())))
            if ck not in cache:
                cand = [(t, n) for t, n, cells in I.rows
                        if (not r.get("tables") or t in r["tables"])
                        and all(re.search(f["regex"], cells[f["column"]]) for f in r.get("row_filter", []))]
                if r.get("mode") == "each_field_ties_union":
                    per = [{(t, n) for t, n in cand if keys[g] in I.values[(r["id"], g, t, n)]} for g in keys]
                    rows = sorted(set().union(*per), key=I.order.index) if all(per) else []
                else:
                    rows = [(t, n) for t, n in cand if all(keys[g] in I.values[(r["id"], g, t, n)] for g in keys)]
                cache[ck] = rows
            rows = cache[ck]
            if rows:
                level = r["level"]
                if len(rows) > 1 and r.get("level_if_several_rows"):
                    level = r["level_if_several_rows"]
                ident = "%s:%s" % (r["id"], ",".join("%s=%s" % kv for kv in sorted(keys.items())))
                return r["id"], level, rows, ident
    return None, "none", [], None


def listed_archives():
    spec = raw_names.read_json(raw_names.SPEC)
    kinds = raw_inventory.Rules(raw_names.read_json(raw_names.KINDS))
    tests = raw_names.read_csv(os.path.join(OUT, "tests.csv"))
    out = {}
    for inv in sorted(spec["investigations"], key=raw_names.psi_key):
        I = raw_names.Investigation(inv, spec["investigations"][inv], tests)
        files = [f for f in raw_names.listing_files(inv, kinds) if f["kind"] == "archive"]
        out[inv] = (I, files)
    return out


def refusals(folder):
    path = os.path.join(folder, "run.log")
    last = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("{"):
                    d = json.loads(line)
                    if "error" in d:
                        last[d["file_id"]] = d["error"]
    return last


def summarise(folder):
    archives = listed_archives()
    errors = refusals(folder)
    rows, not_listed, listing_mismatch = [], [], []
    for inv, (I, files) in archives.items():
        cache = {}
        for f in files:
            fid = f["file_id"]
            path = os.path.join(folder, fid + ".json")
            if not os.path.exists(path):
                reason = ("zero bytes in the listing" if not f["bytes"] else
                          ("refused: " + errors[fid]) if fid in errors else "no member list in the folder")
                not_listed.append({"investigation_id": inv, "psi_file_id": fid, "archive_name": f["name"],
                                   "listing_bytes": f["bytes"], "reason": reason})
                continue
            with open(path, encoding="utf-8") as fh:
                d = json.load(fh)
            if d.get("investigation") != inv or int(d["listing_bytes"]) != int(f["bytes"]):
                listing_mismatch.append(fid)
            rule, level, arows = I.tie(f["base"], f["folder"], f["category"], f["kind"])
            atests = sorted({I.test_of[x] for x in arows if x in I.test_of})
            cls = collections.Counter()
            dirs = 0
            dates = []
            lv = collections.Counter()
            mrows, idents = set(), set()
            for m in d["member_list"]:
                dt = m.get("dos_datetime") or ""
                if dt:
                    dates.append(dt)
                if m.get("is_dir"):
                    dirs += 1
                    continue
                cls[ext_class(m["name"])] += 1
                base = m["name"].rsplit("/", 1)[-1]
                mfolder = m["name"].rsplit("/", 1)[0] if "/" in m["name"] else ""
                _, mlevel, rws, ident = first_tie(I, base, mfolder, f["category"], cache)
                lv[mlevel] += 1
                if rws:
                    mrows.update(rws)
                    idents.add(ident)
            A = set(arows)
            if not mrows:
                rel = "no_identifier_in_member_names"
            elif not A:
                rel = "archive_name_ties_no_row"
            elif mrows == A:
                rel = "equal"
            elif mrows <= A:
                rel = "member_rows_within_archive_rows"
            elif A <= mrows:
                rel = "archive_rows_within_member_rows"
            else:
                rel = "disagree"
            mtests = sorted({I.test_of[x] for x in mrows if x in I.test_of})
            il = sorted(idents)
            rows.append({
                "investigation_id": inv, "psi_file_id": fid, "archive_name": f["name"],
                "listing_bytes": int(f["bytes"]), "bytes_fetched": int(d["bytes_fetched"]),
                "zip64": "yes" if d.get("zip64") else "no", "members": int(d["members"]), "directories": dirs,
                **{"members_" + c: cls.get(c, 0) for c in CLASS_ORDER},
                "uncompressed_bytes": sum(int(m.get("uncompressed_bytes") or 0) for m in d["member_list"]),
                "first_member_date": min(dates) if dates else "", "last_member_date": max(dates) if dates else "",
                "archive_link_level": level, "archive_rule": rule or "", "archive_rows": len(arows),
                "archive_test_id": atests[0] if level == "test" and len(atests) == 1 else "",
                "member_identifiers": "; ".join(il[:SHOW]) + ("; ..." if len(il) > SHOW else ""),
                "member_identifiers_count": len(il),
                "members_tied_to_a_test": lv.get("test", 0), "members_tied_to_a_day_or_session": lv.get("day_or_session", 0),
                "members_not_tied": lv.get("none", 0), "member_rows": len(mrows), "member_tests": len(mtests),
                "member_test_ids": " ".join(mtests[:SHOW]) + (" ..." if len(mtests) > SHOW else ""),
                "rows_in_both": len(mrows & A), "identifier_relation": rel})
    return archives, rows, not_listed, listing_mismatch


def totals(archives, rows, not_listed, listing_mismatch):
    def block(rs, all_files):
        return {"archives_in_listing": len(all_files), "archive_bytes_in_listing": sum(int(f["bytes"]) for f in all_files),
                "archives_listed": len(rs), "bytes_of_listed_archives": sum(r["listing_bytes"] for r in rs),
                "bytes_fetched": sum(r["bytes_fetched"] for r in rs),
                "members": sum(r["members"] for r in rs), "directories": sum(r["directories"] for r in rs),
                "members_by_class": {c: sum(r["members_" + c] for r in rs) for c in CLASS_ORDER},
                "uncompressed_bytes": sum(r["uncompressed_bytes"] for r in rs),
                "identifier_relation": {k: sum(1 for r in rs if r["identifier_relation"] == k) for k in RELATIONS}}
    per = {}
    for inv, (_, files) in archives.items():
        per[inv] = block([r for r in rows if r["investigation_id"] == inv], files)
    allf = [f for _, (_, files) in archives.items() for f in files]
    overall = block(rows, allf)
    overall["archives_not_listed"] = len(not_listed)
    overall["not_listed_by_reason"] = dict(sorted(collections.Counter(
        re.sub(r"\d+ bytes, \d+ asked", "<n> bytes, <m> asked", x["reason"]) for x in not_listed).items()))
    o = overall
    sentences = [
        "The central directories of %d of the %d archives in the PSI listings were read by byte ranges: %d bytes "
        "fetched for %d bytes of archives; no archive was downloaded and no member was opened."
        % (o["archives_listed"], o["archives_in_listing"], o["bytes_fetched"], o["bytes_of_listed_archives"]),
        "They list %d members: %d still images, %d camera frames (.hobj), %d text files and %d others, by the "
        "extension of the member name." % (o["members"] - o["directories"], o["members_by_class"]["still_image"],
                                           o["members_by_class"]["camera_frame_hobj"], o["members_by_class"]["text"],
                                           o["members_by_class"]["other"]),
        "A member name and an archive name are tied to table rows by the name rules of spec/raw_names.json; a tie "
        "by name says that the name carries an identifier of the table, not what the file holds.",
    ]
    return {
        "_meta": {"generated_by": GENERATED_BY, "written_by": "pipeline/archive_summary.py",
                  "source": "member lists read by HTTP range requests from PSI (https://psi.nasa.gov/) by a data-role "
                            "session job on 2026-11-15; kept in a scratch folder, not in the repository",
                  "inputs": ["<folder>/<file_id>.json", "<folder>/run.log", "data/psi/file_listings/ (git-ignored)",
                             "pipeline/spec/raw_names.json", "pipeline/spec/raw_kinds.json", "data/pipeline/tests.csv"],
                  "extension_classes": {c: list(v) for c, v in CLASSES.items()},
                  "extension_classes_note": "The classes are the team's grouping of member-name extensions; 'other' is every "
                                            "other extension, including names without one. Directories are counted apart.",
                  "identifier_relation": {
                      "no_identifier_in_member_names": "no member name is tied to a table row",
                      "archive_name_ties_no_row": "member names tie rows, the archive name ties none",
                      "equal": "the rows tied by member names are the rows tied by the archive name",
                      "member_rows_within_archive_rows": "member names tie part of the rows of the archive name",
                      "archive_rows_within_member_rows": "member names tie the rows of the archive name and others",
                      "disagree": "each side ties a row that the other does not"},
                  "units": "bytes are decimal bytes as PSI's listing and the HTTP responses report them"},
        "sentences": sentences,
        "overall": overall,
        "investigations": per,
        "archives_whose_member_identifiers_disagree_with_the_archive_name": [
            {k: r[k] for k in ("investigation_id", "psi_file_id", "archive_name", "archive_link_level", "archive_rows",
                               "archive_test_id", "member_identifiers", "member_rows", "member_test_ids", "rows_in_both")}
            for r in rows if r["identifier_relation"] == "disagree"],
        "archives_not_listed": not_listed,
        "member_lists_whose_listing_bytes_differ_from_the_listing": listing_mismatch,
    }


def main(argv):
    folder = argv[1] if len(argv) > 1 else ""
    if not folder or not os.path.isdir(folder):
        print("archive_summary: no folder of member lists given (python3 pipeline/archive_summary.py <folder>); "
              "the committed archive_summary.csv and archive_summary_totals.json are left as they are")
        return 0
    if not os.path.isdir(raw_names.LISTINGS):
        print("archive_summary: data/psi/file_listings/ is absent; committed outputs left as they are")
        return 0
    archives, rows, not_listed, mismatch = summarise(folder)
    with open(os.path.join(OUT, "archive_summary.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    doc = totals(archives, rows, not_listed, mismatch)
    with open(os.path.join(OUT, "archive_summary_totals.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, indent=1, ensure_ascii=False)
        f.write("\n")
    o = doc["overall"]
    print("archive_summary: %d of %d archives listed, %d members, %d not listed, %d disagree"
          % (o["archives_listed"], o["archives_in_listing"], o["members"], len(not_listed),
             o["identifier_relation"]["disagree"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
