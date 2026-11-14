# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
# Independent recount (different method): for each table test code, search it as a
# plain substring in video file names; a video counts if exactly one table code is found.
import csv, json, re, sys, collections
V = json.load(open(sys.argv[1])); REPO = sys.argv[2]
T = list(csv.DictReader(open(REPO + "/data/pipeline/tests.csv")))
def raw(fn):
    b = open(REPO + "/data/psi/experimental_tables/" + fn, "rb").read()
    try: return list(csv.reader(b.decode("utf-8-sig").splitlines()))
    except UnicodeDecodeError: return list(csv.reader(b.decode("cp1252").splitlines()))
cache = {}
def code(t, col):
    if t["source_file"] not in cache: cache[t["source_file"]] = raw(t["source_file"])
    tab = cache[t["source_file"]]; h = [x.strip() for x in tab[0]]
    return tab[int(t["source_row"]) - 1][h.index(col)].replace(" ", "").upper()
spec = {"PSI-10": "Test", "PSI-159": "Test", "PSI-39": "CIR"}
for inv, col in spec.items():
    codes = {code(t, col): t["test_id"] for t in T if t["investigation_id"] == inv}
    n1 = 0; tests = set()
    for v in V:
        if v["investigation"] != inv: continue
        nm = v["name"].upper()
        found = {c for c in codes if c and re.search(r"(?<![0-9A-Z])" + re.escape(c) + r"(?![0-9])", nm)}
        # prefer the longest when one code contains another (e.g. M2 and M2_1)
        found = {c for c in found if not any(c != d and c in d for d in found)}
        if len(found) == 1:
            n1 += 1; tests.add(codes[found.pop()])
    print(inv, "videos with exactly one table code in the file name:", n1, "tests reached:", len(tests))
b2 = {t["test_id"][6:].upper(): t["test_id"] for t in T if t["investigation_id"] == "PSI-25"}
n1 = 0; tests = set()
for v in V:
    if v["investigation"] != "PSI-25": continue
    toks = set(re.findall(r"(?<![A-Z0-9])([BFMOPT]\d{1,2}[AB]?)(?![0-9])", v["name"].upper().replace("TEST", "_")))
    hit = {b2[t] for t in toks if t in b2}
    if len(hit) == 1: n1 += 1; tests |= hit
print("PSI-25 videos with exactly one BASS-II test token:", n1, "tests reached:", len(tests))
