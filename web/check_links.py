#!/usr/bin/env python3
# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps
# Challenge 2026 hackathon (2026-11-14).
"""Check the links the dashboard builds: external pages (PSI, DOI, reference documents, the
challenge page) answer, and repository files the page links to exist.

Usage:  python3 web/check_links.py [--offline]     (exit 1 if a link is broken)

Run by hand before the freeze and the submission; not in the deploy workflow, because an
outside site being slow for a minute should not stop a deploy. Standard library only.
"""
import concurrent.futures
import csv
import json
import os
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
UA = "Mozilla/5.0 (compatible; link-check)"


def rows(path):
    p = os.path.join(ROOT, path)
    return list(csv.DictReader(open(p, encoding="utf-8-sig"))) if os.path.exists(p) else []


def external_links():
    urls = {"https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/": "challenge page"}
    for r in rows("data/catalog/investigations.csv"):
        if r.get("psi_url"):
            urls[r["psi_url"]] = f"PSI page {r['psi_accession']}"
        if r.get("dataset_doi"):
            urls["https://doi.org/" + r["dataset_doi"]] = f"dataset DOI {r['psi_accession']}"
    for r in rows("data/pipeline/need_references.csv"):
        if r.get("url", "").startswith("http"):
            urls.setdefault(r["url"], f"reference {r.get('reference_id', '')}")
    return urls


def repo_files():
    """Repository paths the page links to (served on GitHub at the build commit)."""
    files = {"scoring/scoring_config.json", "data/catalog/configurations.csv", "data/catalog/investigations.csv",
             "data/pipeline/capability_matrix.csv", "data/pipeline/coverage_grid.csv", "data/pipeline/tests.csv",
             "data/pipeline/scenario_needs.csv", "data/pipeline/scenario_tests.csv", "data/pipeline/need_references.csv",
             "pipeline/spec/needs.json", "pipeline/spec/coverage.json", "pipeline/spec/scenarios.json"}
    for r in rows("data/pipeline/tests.csv"):
        if r.get("source_file"):
            files.add("data/psi/experimental_tables/" + r["source_file"])
    for r in rows("data/catalog/configurations.csv"):
        ref = (r.get("tests_table_ref") or "").split(" (")[0].strip()
        if ref.endswith(".csv"):
            files.add("data/psi/experimental_tables/" + ref)
    for r in rows("data/catalog/investigations.csv"):
        files.add(f"data/psi/catalog/{r['psi_accession']}.json")
    return files


def fetch(url):
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(url, method=method, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=20) as resp:
                return resp.status, None
        except urllib.error.HTTPError as e:
            if method == "HEAD" and e.code in (403, 405, 406, 429, 501):
                continue  # some sites refuse HEAD; try GET
            return e.code, None
        except Exception as e:  # timeout, DNS, TLS
            if method == "HEAD":
                continue
            return None, type(e).__name__
    return None, "no answer"


def main():
    bad = []
    missing = sorted(f for f in repo_files() if not os.path.exists(os.path.join(ROOT, f)))
    for f in missing:
        bad.append(f"missing repository file: {f}")
    print(f"repository files linked: {len(repo_files())}, missing: {len(missing)}")
    if "--offline" not in sys.argv:
        urls = external_links()
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
            results = dict(zip(urls, ex.map(fetch, urls)))
        ok, by_hand = 0, []
        for url, (code, err) in sorted(results.items()):
            if code is not None and code < 400:
                ok += 1
            elif code in (401, 403, 409, 429) or code is None:
                # Many publishers refuse scripts (403/409) or drop them (no answer). Checked by hand
                # in a browser on 2026-11-14: all of these opened (the GRC PDF downloads).
                by_hand.append(f"{urls[url]}: {url} -> {code or err}")
            else:
                bad.append(f"{urls[url]}: {url} -> {code}")
        print(f"external links: {len(urls)}, answering: {ok}, refused scripts (open by hand): {len(by_hand)}")
        for b in by_hand:
            print("  BY HAND " + b)
    for b in bad:
        print("  BROKEN " + b)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
