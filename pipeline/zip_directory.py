# AI-generated code: written with an AI coding assistant (Claude Code)
# during the NASA Space Apps Challenge 2026 hackathon (2026-11-14).
"""List the members of PSI .zip archives without downloading them.

For one archive the script reads, by HTTP Range requests only: 1 byte (to
learn the size the server holds), the last 65,536 bytes (End Of Central
Directory record and zip64 locator), the zip64 EOCD record if it lies before
that tail, and the central directory. It never downloads a whole archive: a
reply other than 206 Partial Content is closed without reading its body and
the archive is reported as refused; a central directory over 60 MB is not
fetched. Standard library only.

The download link comes from the public PSI call that scripts/fetch_psi.py
uses (studies/<PSI-n>/download?file=<name>&version=<v>&redirect=false). It is
a pre-signed URL that carries temporary credentials; it is never printed or
written to a file, only its host name is checked to be https.

Usage:
  python3 pipeline/zip_directory.py fetch OUT_DIR FILE_ID [FILE_ID ...]
      writes OUT_DIR/<file_id>.json (member list, bytes fetched, status codes)
      and prints one line per archive; put OUT_DIR outside the repository
  python3 pipeline/zip_directory.py sample OUT_DIR
      writes data/pipeline/archive_members_sample.csv from the member lists
      in OUT_DIR: one row per archive, member name pattern (digits masked as
      #) and extension

The listings of data/psi/file_listings/ (git-ignored) give the names, sizes
and versions of the archives. The member lists are a sample; the members
were not opened. Source: NASA Physical Sciences Informatics, https://psi.nasa.gov/
"""
import csv
import datetime
import glob
import io
import json
import os
import re
import struct
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://psi.nasa.gov/geode-py/ws"
LISTINGS = os.path.join(ROOT, "data", "psi", "file_listings")
OUT_CSV = os.path.join(ROOT, "data", "pipeline", "archive_members_sample.csv")
HEADERS = {"User-Agent": "research-client"}   # generic client, no personal data
TAIL = 65536
MAX_CD = 60 * 1024 * 1024
TIMEOUT = 120
SAMPLE_NOTE = ("A sample: the central directories of these archives were read by byte ranges; "
               "member names and sizes as the directory gives them; no member was opened.")


def listing_records():
    """{file id: (investigation, listing record)} of the saved listings."""
    out = {}
    for path in sorted(glob.glob(os.path.join(LISTINGS, "PSI-*.json"))):
        inv = os.path.basename(path)[:-5]
        with open(path, encoding="utf-8") as f:
            stack = [json.load(f)]
        while stack:
            x = stack.pop()
            if isinstance(x, dict):
                if "key" in x and "bytes_size" in x and x.get("id"):
                    out.setdefault(x["id"], (inv, x))
                    continue
                stack.extend(x.values())
            elif isinstance(x, list):
                stack.extend(x)
    return out


class Refused(Exception):
    pass


class Fetcher:
    def __init__(self):
        self.bytes = 0
        self.log = []

    def link(self, inv, name, version):
        q = urllib.parse.urlencode({"file": name, "version": version, "redirect": "false"})
        req = urllib.request.Request("%s/studies/%s/download?%s" % (BASE, inv, q), headers=HEADERS)
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            url = r.read(8192).decode("utf-8", "replace").strip()
        if urllib.parse.urlsplit(url).scheme != "https":
            raise Refused("the download link is not an https URL")
        return url

    def range(self, url, start, end, label):
        """Bytes start..end inclusive. Anything but 206 is refused unread."""
        want = end - start + 1
        req = urllib.request.Request(url, headers=dict(HEADERS, Range="bytes=%d-%d" % (start, end)))
        entry = {"request": label, "range": "bytes=%d-%d" % (start, end)}
        try:
            r = urllib.request.urlopen(req, timeout=TIMEOUT)
        except urllib.error.HTTPError as e:
            entry["status"] = e.code
            self.log.append(entry)
            raise Refused("%s: HTTP %d" % (label, e.code))
        entry.update(status=r.status, content_range=r.headers.get("Content-Range"))
        self.log.append(entry)
        if r.status != 206:
            r.close()
            raise Refused("%s: status %d, the server does not honour the range; nothing read" % (label, r.status))
        data = r.read(want + 1)
        r.close()
        self.bytes += len(data)
        if len(data) != want:
            raise Refused("%s: %d bytes, %d asked" % (label, len(data), want))
        return data, r.headers.get("Content-Range")


def dos_datetime(d, t):
    try:
        return datetime.datetime(((d >> 9) & 0x7F) + 1980, (d >> 5) & 0x0F, d & 0x1F,
                                 (t >> 11) & 0x1F, (t >> 5) & 0x3F, (t & 0x1F) * 2).strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None


def parse_central_directory(cd, count):
    out, p = [], 0
    for _ in range(count):
        if cd[p:p + 4] != b"PK\x01\x02":
            raise Refused("bad central directory header at offset %d" % p)
        (_, _, flag, method, mtime, mdate, _, csize, usize, nlen, xlen, clen, _, _, _, loff) = \
            struct.unpack("<HHHHHHIIIHHHHHII", cd[p + 4:p + 46])
        name = cd[p + 46:p + 46 + nlen].decode("utf-8" if flag & 0x800 else "cp437", errors="replace")
        extra = cd[p + 46 + nlen:p + 46 + nlen + xlen]
        q = 0
        while q + 4 <= len(extra):
            hid, hlen = struct.unpack("<HH", extra[q:q + 4])
            body = extra[q + 4:q + 4 + hlen]
            if hid == 0x0001:  # zip64 extended information
                r = 0
                if usize == 0xFFFFFFFF:
                    usize = struct.unpack("<Q", body[r:r + 8])[0]
                    r += 8
                if csize == 0xFFFFFFFF:
                    csize = struct.unpack("<Q", body[r:r + 8])[0]
                    r += 8
            q += 4 + hlen
        out.append({"name": name, "uncompressed_bytes": usize, "compressed_bytes": csize, "method": method,
                    "encrypted": bool(flag & 1), "dos_datetime": dos_datetime(mdate, mtime),
                    "is_dir": name.endswith("/")})
        p += 46 + nlen + xlen + clen
    return out


def directory(fid, inv, rec):
    f = Fetcher()
    name = rec["key"].rsplit("/", 1)[-1]
    res = {"file_id": fid, "investigation": inv, "key": rec["key"], "listing_bytes": int(float(rec["bytes_size"] or 0))}
    try:
        url = f.link(inv, name, rec.get("version", 1))
        _, cr = f.range(url, 0, 0, "first_byte")
        total = int(cr.split("/")[-1])
        res["served_bytes"] = total
        start = max(0, total - TAIL)
        tail, _ = f.range(url, start, total - 1, "tail")
        e = tail.rfind(b"PK\x05\x06")
        if e < 0:
            raise Refused("no End Of Central Directory record in the last %d bytes" % TAIL)
        _, _, _, n, cd_size, cd_off, _ = struct.unpack("<HHHHIIH", tail[e + 4:e + 22])
        zip64 = tail[e - 20:e - 16] == b"PK\x06\x07" if e >= 20 else False
        if zip64:
            z_off = struct.unpack("<Q", tail[e - 12:e - 4])[0]
            rec64 = tail[z_off - start:z_off - start + 56] if z_off >= start else \
                f.range(url, z_off, z_off + 55, "zip64_eocd")[0]
            if rec64[:4] != b"PK\x06\x06":
                raise Refused("bad zip64 End Of Central Directory record")
            n, cd_size, cd_off = struct.unpack("<QQQ", rec64[32:56])
        res.update(zip64=zip64, members_declared=n, central_directory_bytes=cd_size)
        if cd_size > MAX_CD:
            raise Refused("central directory of %d bytes is over the cap" % cd_size)
        if cd_off >= start and cd_off + cd_size <= total:
            cd = tail[cd_off - start:cd_off - start + cd_size]
        else:
            cd = f.range(url, cd_off, cd_off + cd_size - 1, "central_directory")[0]
        res["member_list"] = parse_central_directory(cd, n)
        res["members"] = len(res["member_list"])
    except (Refused, urllib.error.URLError, OSError, ValueError, struct.error) as exc:
        res["error"] = "%s: %s" % (type(exc).__name__, exc)
    res["bytes_fetched"] = f.bytes
    res["requests"] = f.log
    return res


def fetch(out_dir, ids):
    if os.path.abspath(out_dir).startswith(ROOT + os.sep):
        sys.exit("zip_directory: OUT_DIR must be outside the repository")
    os.makedirs(out_dir, exist_ok=True)
    recs = listing_records()
    for fid in ids:
        if fid not in recs:
            print(json.dumps({"file_id": fid, "error": "not in the saved listings"}))
            continue
        inv, rec = recs[fid]
        res = directory(fid, inv, rec)
        if "member_list" in res:
            with open(os.path.join(out_dir, fid + ".json"), "w", encoding="utf-8") as f:
                json.dump(res, f, indent=1, sort_keys=True, ensure_ascii=False)
                f.write("\n")
        print(json.dumps({k: v for k, v in res.items() if k != "member_list"}, sort_keys=True), flush=True)


def sample(out_dir):
    rows = []
    for path in sorted(glob.glob(os.path.join(out_dir, "*.json"))):
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        acc = {}
        for m in d["member_list"]:
            base = m["name"].rsplit("/", 1)[-1]
            ext = base.rsplit(".", 1)[-1].lower() if "." in base else "(none)"
            a = acc.setdefault((re.sub(r"\d", "#", base), ext), [0, 0, 0, 0])
            a[0] += 1
            a[1] += m["uncompressed_bytes"]
            a[2] += m["compressed_bytes"]
            a[3] += 1 if m.get("encrypted") else 0
        for (pattern, ext) in sorted(acc):
            a = acc[(pattern, ext)]
            rows.append({"investigation_id": d["investigation"], "archive_file_id": d["file_id"],
                         "archive_name": d["key"].rsplit("/", 1)[-1], "archive_bytes": d["listing_bytes"],
                         "bytes_fetched": d["bytes_fetched"], "members_in_archive": len(d["member_list"]),
                         "member_name_pattern": pattern, "extension": ext, "members": a[0],
                         "uncompressed_bytes": a[1], "compressed_bytes": a[2], "encrypted_members": a[3],
                         "sample_note": SAMPLE_NOTE})
    rows.sort(key=lambda r: (int(r["investigation_id"].split("-")[1]), r["archive_name"], r["member_name_pattern"], r["extension"]))
    cols = ["investigation_id", "archive_file_id", "archive_name", "archive_bytes", "bytes_fetched", "members_in_archive",
            "member_name_pattern", "extension", "members", "uncompressed_bytes", "compressed_bytes", "encrypted_members",
            "sample_note"]
    buf = io.StringIO()
    w = csv.DictWriter(buf, cols, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        f.write(buf.getvalue())
    print("zip_directory: %d archives, %d rows -> %s" % (len({r["archive_file_id"] for r in rows}), len(rows),
                                                          os.path.relpath(OUT_CSV, ROOT)))


def main(argv):
    if len(argv) >= 3 and argv[1] == "fetch":
        fetch(argv[2], argv[3:])
    elif len(argv) == 3 and argv[1] == "sample":
        sample(argv[2])
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv)
