#!/usr/bin/env python3
# AI-generated code: written with an AI coding assistant (Claude Code)
# during the NASA Space Apps Challenge 2026 hackathon (2026-11-14).
"""Fetch catalog-level data for NASA PSI Combustion Science investigations.

Downloads, for every PSI investigation whose Research Area is
"Combustion Science":
  - the investigation record (description, hardware, publications, DOI)
  - the file listing (names and sizes only, no raw data)
  - the experimental table file(s) (small CSV/XLSX files)

Source: NASA Physical Sciences Informatics (PSI), https://psi.nasa.gov/
Nothing here downloads raw experiment data (video, images, sensor archives).

Usage:
    python3 scripts/fetch_psi.py [output_dir]      # default: data/psi
"""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://psi.nasa.gov/geode-py/ws"
RESEARCH_AREA = "combustion science"
PAUSE_S = 0.4  # be polite to the public server


def get(url, data=None, headers=None, timeout=120):
    req = urllib.request.Request(url, data=data, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def get_json(url, data=None, headers=None):
    return json.loads(get(url, data=data, headers=headers).decode("utf-8"))


def save(path, raw):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(raw)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join("data", "psi")
    fetched_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    search_url = (
        f"{BASE}/repo/search?source=psi&type=investigation"
        "&sort=Public%20Release%20Date&order=desc&size=500"
    )
    search = get_json(search_url)
    hits = search["hits"]["hits"]
    accessions = sorted(
        (h["_source"]["Accession"] for h in hits
         if h["_source"].get("Research Area", "").lower() == RESEARCH_AREA),
        key=lambda a: int(a.split("-")[1]),
    )
    print(f"{len(accessions)} combustion investigations of {len(hits)} in PSI")

    manifest = {"fetched_at": fetched_at, "source": "https://psi.nasa.gov/",
                "investigations": []}

    for acc in accessions:
        time.sleep(PAUSE_S)
        raw = get(f"{BASE}/repo/investigations/{acc}")
        inv = json.loads(raw.decode("utf-8"))
        # The record embeds per-file change lists that are large and not needed
        # at catalog level; keep them out of the saved copy.
        slim = {k: v for k, v in inv.items()
                if k not in ("added", "removed", "modified")}
        # Keep researcher names and roles (public record) but not their
        # contact details: this copy may end up in a public repository.
        for person in slim.get("contacts") or []:
            for field in ("email", "phone", "fax", "address"):
                person.pop(field, None)
        save(os.path.join(out, "catalog", f"{acc}.json"),
             json.dumps(slim, ensure_ascii=False, indent=1).encode("utf-8"))

        time.sleep(PAUSE_S)
        body = json.dumps({"folder": f"{acc}/", "fileType": "study",
                           "studyId": acc, "version": inv.get("version", 1),
                           "obfuscationcode": ""}).encode("utf-8")
        files_raw = get(f"{BASE}/files/v2", data=body,
                        headers={"Content-Type": "application/json"})
        save(os.path.join(out, "file_listings", f"{acc}.json"), files_raw)

        tables = []
        for et in inv.get("experimentalTable", []) or []:
            name = et["file_name"]
            q = urllib.parse.urlencode(
                {"file": name, "version": et.get("version", 1),
                 "redirect": "false"})
            time.sleep(PAUSE_S)
            try:
                link = get(f"{BASE}/studies/{acc}/download?{q}").decode().strip()
                data = get(link)
                save(os.path.join(out, "experimental_tables", name), data)
                tables.append({"file": name, "bytes": len(data)})
            except (urllib.error.URLError, OSError) as exc:
                tables.append({"file": name, "error": str(exc)})

        manifest["investigations"].append({
            "accession": acc,
            "acronym": inv.get("investigationAcronym", ""),
            "title": inv.get("title", ""),
            "doi": inv.get("doi", ""),
            "license": inv.get("licenseIdentifier", ""),
            "version": inv.get("version"),
            "experimental_tables": tables,
        })
        print(acc, inv.get("investigationAcronym", ""),
              [t.get("bytes", t.get("error")) for t in tables])

    save(os.path.join(out, "manifest.json"),
         json.dumps(manifest, ensure_ascii=False, indent=1).encode("utf-8"))


if __name__ == "__main__":
    main()
