# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
# AI-generated (Claude Code, 2026-11-14) for the Space Apps team. Not human-reviewed.
# Reads every PSI video name (from saved PSI listings) and ties it, by name rules
# only, to rows of NASA's experimental tables. No video is opened.
# Usage: python3 -I video_names.py <work_videos.json> <repo_root> <as_run_matrix.xlsx> <out_dir>
import csv, json, os, re, sys, datetime, collections

VID, REPO, ASRUN, OUT = sys.argv[1:5]
ET = os.path.join(REPO, "data", "psi", "experimental_tables")
videos = json.load(open(VID))

def read_table(fn):
    raw = open(os.path.join(ET, fn), "rb").read()
    try:
        txt = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        txt = raw.decode("cp1252")
    return list(csv.reader(txt.splitlines()))

tests = list(csv.DictReader(open(os.path.join(REPO, "data", "pipeline", "tests.csv"))))
need_tests = list(csv.DictReader(open(os.path.join(REPO, "data", "pipeline", "need_tests.csv"))))
tables = {}
def row_of(t):
    fn = t["source_file"]
    if fn not in tables:
        tables[fn] = read_table(fn)
    tab = tables[fn]
    hdr = [h.strip() for h in tab[0]]
    r = tab[int(t["source_row"]) - 1]
    return dict(zip(hdr, r))

by_inv = collections.defaultdict(list)
for t in tests:
    t["_raw"] = row_of(t)
    by_inv[t["investigation_id"]].append(t)

norm = lambda s: re.sub(r"\s+", "", s or "").upper()

# ---------------------------------------------------------------- indexes
# ACME per-test tables (PSI-10, PSI-159): column 'Test' holds YYDDDX#
acme_idx = {inv: collections.defaultdict(list) for inv in ("PSI-10", "PSI-159")}
for inv in acme_idx:
    for t in by_inv[inv]:
        acme_idx[inv][norm(t["_raw"].get("Test"))].append(t["test_id"])
# BASS-II: test_id = BASS2-<Test #>
b2 = {t["test_id"][6:].upper(): t for t in by_inv["PSI-25"]}
# CFI: Flex Number and CIR
cfi_cir, cfi_num, cfi_days = collections.defaultdict(set), collections.defaultdict(set), collections.defaultdict(set)
for t in by_inv["PSI-39"]:
    cfi_cir[norm(t["_raw"].get("CIR"))].add(t["test_id"])
    cfi_num[t["_raw"].get("Flex Number", "").strip()].add(t["test_id"])
    d = datetime.datetime.strptime(t["_raw"]["Test Date"].strip(), "%d-%b-%y")
    cfi_days[(d.year, d.timetuple().tm_yday)].add(t["test_id"])
# FLEX: FLEX Test # and FLEX Identifier
flex_id, flex_num = collections.defaultdict(set), collections.defaultdict(set)
flex_years = collections.Counter()
for t in by_inv["PSI-69"]:
    flex_id[norm(t["_raw"].get("FLEX Identifier"))].add(t["test_id"])
    flex_num[t["_raw"].get("FLEX Test #", "").strip()].add(t["test_id"])
    flex_years[t["_raw"]["Test Date"].strip()[-2:]] += 1
# BASS (PSI-26): GMT day and year
def bass_year(s):
    s = s.strip()
    if s.endswith("2012") or s.endswith("`12"):
        return 2012, ("" if s.endswith("2012") else "year read from '`12'")
    if s.endswith("2013"):
        return 2013, ""
    if s.endswith("2103"):
        return 2013, "year '2103' read as 2013"
    return None, "year unreadable"
bass_day = collections.defaultdict(list)
for t in by_inv["PSI-26"]:
    y, _ = bass_year(t["_raw"]["Date"])
    bass_day[(y, int(t["_raw"]["GMT"]))].append(t["test_id"])
# SAME-R: Date 'D-Mon' (year 2010 assumed) and Sample Type
samer = collections.defaultdict(list)
for t in by_inv["PSI-101"]:
    r = t["_raw"]
    samer[(r["Date"].strip(), r["Sample Type"].strip().lower())].append((t["test_id"], r["SAME Test #"].strip()))
samer_day = collections.defaultdict(list)
for (d, m), l in samer.items():
    samer_day[d] += [x[0] for x in l]
# SPICE: GMT date and GMT ignition
spice_day = collections.defaultdict(list)
for t in by_inv["PSI-107"]:
    spice_day[int(t["_raw"]["GMT date"])].append((t["test_id"], t["_raw"]["GMT ignition"].strip()))
# day-level tables
def acme_day_table(fn, col):
    tab = read_table(fn)
    hdr = [h.strip() for h in tab[0]]
    i = hdr.index(col)
    return {r[i].strip() for r in tab[1:] if len(r) > i and r[i].strip()}
day_tables = {
    "PSI-21": acme_day_table("PSI-21_Experimental table_CLD Flame.csv", "Test Day"),
    "PSI-22": acme_day_table("PSI-22_Experimental table_ACME E-FIELD Flames.csv", "Test Day"),
    "PSI-23": acme_day_table("PSI-23_Experimental table_ACME s-Flame.csv", "Test Day*"),
}
MON = {m: i + 1 for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"])}
bre = set()
for r in read_table("PSI-20_Experimental table_ACME BRE.csv")[1:]:
    if len(r) > 2 and r[0].strip().isdigit():
        d = datetime.date(int(r[0]), MON[r[1].strip()[:3].lower()], int(r[2]))
        bre.add(f"{d.year % 100:02d}{d.timetuple().tm_yday:03d}")
day_tables["PSI-20"] = bre
slice_days = set()
for r in read_table("PSI-106_Experimental table_Slice.csv")[1:]:
    m = re.match(r"(\d{4})-([A-Z]{3})-(\d{2})", r[0].strip())
    if m:
        d = datetime.date(int(m.group(1)), MON[m.group(2).lower()], int(m.group(3)))
        slice_days.add(d.timetuple().tm_yday)

# BASS as-run matrix (NASA document PSI-26 'As Run_Test Matrix.xlsx'): start times
asrun = collections.defaultdict(list)
try:
    import openpyxl
    wb = openpyxl.load_workbook(ASRUN, read_only=True, data_only=True)
    for sh in ("2013",):
        for row in wb[sh].iter_rows(values_only=True):
            if not isinstance(row[0], datetime.datetime):
                continue
            st, arn = str(row[2] or ""), row[3]
            tm = re.findall(r"(\d{1,2}):(\d{2})", st)
            if not tm or not str(arn).strip().isdigit():
                continue
            h, mi = map(int, tm[0])
            asrun[row[0].date()].append((h * 60 + mi, f"BASS-{int(arn)}"))
except Exception as e:  # recorded in the summary
    asrun["_error"] = str(e)

# ---------------------------------------------------------------- name words
DESCRIPTORS = [  # (label, regex on the bare name) -- what the words say the clip is
    ("second_view", r"2ND[_ ]VIEW"),
    ("still_sequence", r"Still[_ ]Sequence"),
    ("loss_of_signal_portion", r"LOS[_ -]Portion|LOS\b|during-LOS|-LOS"),
    ("ignition_attempt", r"Ignition[_ ]Attempts?"),
    ("part_of_recording", r"Part-\d|pt\d|(?<=\d)p\d(?![0-9])"),
    ("shifted_video", r"shifted-video"),
    ("post_burn_picture", r"post-burn-picture"),
    ("rack_or_monitor_view", r"rack-video|camera-monitor"),
    ("flame_blowoff_clip", r"Flame-Blowoff"),
    ("igniter_check", r"IgniterCheck|igniter burnout"),
    ("radiometer_point", r"(?<=\d{5})RAD\d|(?<=\d{5})R\d(?![0-9])"),
    ("failed_or_aborted", r"failed|aborted|extinguished early|DROPLET LOSS"),
    ("camera_view_named", r"Droplet[_ ]?(Movie )?View|Flame[_ ]?(Movie )?View|MDCA|HiBMS2|HiMS2|SCIENCE[- ]STATION|PD STATION"),
    ("downlink_recording", r"DOWNLINK"),
    ("stream_recording", r"v[il]c-record|udp"),
    ("ground_1g", r"(?<![A-Za-z])1g(?![A-Za-z])|MFCCalib"),
    ("calibration", r"[Cc]alib|CAL\d|(?<=\d{3})R\d{2}(?![0-9])"),
    ("outreach_or_interview", r"(?i)wo66\d+|Interviews"),
    ("engineering_test", r"Resistive Heater Coil"),
]
DESC = [(l, re.compile(p)) for l, p in DESCRIPTORS]

PREFIX = re.compile(r"^PSI-\d+_(Raw Data|Presentations|Reference Data|Engineering Documents|Analyzed Data|Science Documents)_")

def bare(name):
    b = PREFIX.sub("", name)
    return b

def ext_of(name):
    return name.rsplit(".", 1)[-1].lower()

VLC = re.compile(r"v[il]c-record-(\d{4})-(\d{2})-(\d{2})-(\d{2})h(\d{2})m(\d{2})s")
ACME_CODE = re.compile(r"(?<![0-9])(1[7-9]|2[0-2])(\d{3}) ?([A-Z])(\d{1,2})(_\d)?(?![0-9])")
ACME_RAD = re.compile(r"(?<![0-9])(1[7-9]|2[0-2])(\d{3})RAD(\d+)([ab]?)")
ACME_DAYONLY = re.compile(r"(?<![0-9])(1[7-9]|2[0-2])(\d{3})_IgniterCheck")

def acme_codes(s):
    out = []
    for m in ACME_CODE.finditer(s):
        if 1 <= int(m.group(2)) <= 366:
            out.append(f"{m.group(1)}{m.group(2)}{m.group(3)}{m.group(4)}{m.group(5) or ''}")
    return out

rows = []
for v in videos:
    inv, name, folder = v["investigation"], v["name"], v["folders"]
    b = bare(name)
    stem = b.rsplit(".", 1)[0]
    leaf = folder.split("/")[-1].strip() if folder else ""
    ids, notes = {}, []
    pattern, tie, tid, cands, src, conflict = "", "none", "", [], "", ""
    words = [l for l, rx in DESC if rx.search(stem) or (l in ("ground_1g", "calibration") and rx.search(folder))]
    mv = VLC.search(stem)
    if mv:
        ids["recording_start"] = "{}-{}-{} {}:{}:{}".format(*mv.groups())
    cat = v["category"]
    if cat in ("Presentations", "Reference Data", "Engineering Documents") or "outreach_or_interview" in words:
        pattern = f"{cat}: outreach or document clip" if cat != "Engineering Documents" else "Engineering Documents: test clip"
        if re.search(r"(?i)wo66\d+", stem):
            ids["work_order"] = re.search(r"(?i)wo(66\d+)", stem).group(1)
        rows.append(dict(v, bare=b, pattern=pattern, ids=ids, words=words, tie="none", test_id="", cands=[], src="", conflict="", notes=["not a test recording by category or name"]))
        continue

    if inv in ("PSI-10", "PSI-159", "PSI-20", "PSI-21", "PSI-22", "PSI-23"):
        nc = acme_codes(stem)
        fc = acme_codes(folder)
        if ACME_CODE.match(stem):
            pattern = "{testpoint}-vlc-record-{date}-{time}-udp_{port}"
        elif mv:
            pattern = "vlc-record-{date}-{time}-udp_{testpoint}[_suffix]"
            if stem.startswith("vic-record"):
                notes.append("'vic-record' read as 'vlc-record' (typo in name)")
        else:
            pattern = "(other)"
        rad = ACME_RAD.search(stem)
        dayonly = ACME_DAYONLY.search(stem)
        if rad:
            ids["radiometer_point"] = rad.group(0)
        if nc:
            ids["testpoint"] = ",".join(nc)
        leafc = acme_codes(leaf) or acme_codes(folder.split("/")[-2] if folder.count("/") >= 2 else "")
        if leafc:
            ids["folder_testpoint"] = leafc[0]
        codes, src = (nc, "name") if nc else ((leafc, "folder") if leafc else ([], ""))
        if nc and leafc and leafc[0] not in nc:
            conflict = f"name {','.join(nc)} vs folder {leafc[0]}"
        day = None
        if codes:
            day = codes[0][:5]
        elif rad:
            day, src = rad.group(1) + rad.group(2), "name"
        elif dayonly:
            day, src = dayonly.group(1) + dayonly.group(2), "name"
        else:
            m = re.search(r"(?<![0-9])(1[7-9]|2[0-2])(\d{3})(?![0-9])", folder)
            if m and 1 <= int(m.group(2)) <= 366:
                day, src = m.group(0), "folder"
        if day:
            ids["test_day_yyddd"] = day
        if inv in ("PSI-10", "PSI-159"):
            def look(c):
                return acme_idx[inv].get(c) or acme_idx[inv].get(re.sub(r"_\d$", "", c), [])
            hits = sorted({t for c in codes for t in look(c)})
            if len(codes) == 1 and len(hits) == 1 and not rad and "igniter_check" not in words:
                tie, tid = "single_test", hits[0]
            elif len(hits) > 1:
                tie, cands = "run", hits
                notes.append("several table rows for the codes in the name")
            elif day and any(k.startswith(day) for k in acme_idx[inv]):
                tie = "day"
                cands = sorted({t for k, l in acme_idx[inv].items() if k.startswith(day) for t in l})
                notes.append("test point not in the table; its day is")
            else:
                notes.append("neither the test point nor its day is in the table")
        else:
            if day and day in day_tables[inv]:
                tie = "day"
                notes.append("table has one row per test day, not per test")
            elif day:
                notes.append(f"day {day} not in the per-day table")
            else:
                notes.append("no test day in name or folder")

    elif inv == "PSI-25":
        m = re.search(r"BASS_GMT_?(\d+)_SAMPLE_?(\d+)_TEST[_ -]?([BFMOPT]\d+[ab]?)", stem, re.I)
        if m:
            pattern = "[vlc-record-{date}-{time}-]BASS_GMT{day}_SAMPLE_{sample}_TEST[_]{test}[_descriptor]"
            ids.update(gmt_day=m.group(1), sample=m.group(2), test=m.group(3))
        else:
            m2 = re.search(r"(?:^|[-_])(?:Test-)?([BFMOPT]\d+[ab]?)(?=[-_.]|experiment|$)", stem)
            if m2:
                pattern = "{test}-{words} or {words}-GMT{day}-Test-{test}"
                ids["test"] = m2.group(1)
                g = re.search(r"GMT(\d+)", stem)
                if g:
                    ids["gmt_day"] = g.group(1)
            else:
                pattern = "(other)"
        ftest = re.search(r"/([BFMOPT]\d+)$", folder)
        if ftest:
            ids["folder_test"] = ftest.group(1)
        test = ids.get("test", "").upper()
        src = "name" if test else ""
        if not test and ftest:
            test, src = ftest.group(1).upper(), "folder"
        if ftest and test and re.sub(r"[AB]$", "", test) != ftest.group(1).upper():
            conflict = f"name {test} vs folder {ftest.group(1)}"
        def agrees(k):
            r = b2[k]["_raw"]
            g = ("gmt_day" not in ids) or r.get("GMT", "").strip() == ids["gmt_day"]
            sm = ("sample" not in ids) or re.sub(r"\D", "", r.get("Sample #", "")).lstrip("0") == ids["sample"].lstrip("0")
            return g, sm
        if test in b2 and conflict and ftest and ftest.group(1).upper() in b2 and "gmt_day" in ids and "sample" in ids:
            gn, sn = agrees(test); gf, sf = agrees(ftest.group(1).upper())
            if not (gn and sn) and (gf and sf):
                notes.append(f"name says {test} but its GMT and sample match the table row of folder test {ftest.group(1)}; tied to the folder test (team rule)")
                test, src = ftest.group(1).upper(), "folder (name corrected by GMT+sample check)"
        if test in b2:
            tie, tid = "single_test", b2[test]["test_id"]
            g, sm = agrees(test)
            if "gmt_day" in ids:
                ids["check_gmt_sample"] = "agree" if (g and sm) else ("gmt_differs" if not g else "sample_differs")
            if not g:
                notes.append(f"GMT in name {ids['gmt_day']} vs table {b2[test]['_raw'].get('GMT','').strip()}")
            if not sm:
                notes.append(f"sample in name {ids['sample']} vs table {b2[test]['_raw'].get('Sample #','').strip()}")
        elif test and (test + "A" in b2 or test + "B" in b2):
            tie = "run"
            cands = [b2[k]["test_id"] for k in (test + "A", test + "B") if k in b2]
            notes.append("name has no a/b; table splits the sample into runs a and b")
        elif test:
            notes.append(f"test {test} not in the table")

    elif inv == "PSI-26":
        m = re.match(r"(\d{4})(\d{2})(\d{2})[ .](\d{2})[.](\d{2})[. ](\d{2})[ .]?(iss0(\d{2})m(\d{2})(\d{3})(\d{4}))?", stem)
        if m:
            pattern = "{YYYYMMDD} {hh.mm.ss} iss0{expedition}m{nn}{ddd}{hhmm}" if m.group(7) else "{YYYYMMDD} {hh.mm.ss} iss0{expedition}m"
            vd = datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            ids["date_on_video"] = vd.isoformat()
            ids["time_in_name"] = f"{m.group(4)}:{m.group(5)}:{m.group(6)}"
            if m.group(7):
                ids["iss_code"] = m.group(7)
                ids["iss_code_day"] = m.group(10)
            ad = vd - datetime.timedelta(days=1)
            ids["actual_date"] = ad.isoformat()
            src = "name"
            fd = re.search(r"(\d{4})_(\d{2})_(\d{2})", folder)
            if fd and fd.group(0).replace("_", "") != m.group(1) + m.group(2) + m.group(3):
                conflict = f"folder date {fd.group(0)} vs name date {vd.isoformat()}"
            rws = bass_day.get((ad.year, ad.timetuple().tm_yday), [])
            if rws:
                tie, cands = "day", sorted(rws)
                # candidate by the start times of the as-run matrix (team rule, not checked)
                tmin = int(m.group(4)) * 60 + int(m.group(5))
                starts = sorted(asrun.get(ad, []))
                before = [s for s in starts if s[0] <= tmin]
                if before:
                    ids["asrun_candidate"] = f"{before[-1][1]} (start {before[-1][0]//60:02d}:{before[-1][0]%60:02d}, {tmin-before[-1][0]} min before name time)"
            else:
                notes.append("no table row on the actual date (name date minus one day)")
        else:
            pattern = "(other)"

    elif inv == "PSI-39":
        nf = re.search(r"FLEX-(\d{4})", stem)
        nc = re.search(r"(?i)(?<![A-Za-z0-9])F(\d{3})([A-E])(\d{2})", stem)
        ff = re.search(r"FLEX-(\d{4})A?", folder)
        fcm = re.search(r"(?i)(?<![A-Za-z0-9])F(\d{3})([A-E])(\d{2})", folder)
        if nf and nc:
            pattern = "FLEX-{flex}_{date}-{time}_{cir}"
        elif nc:
            pattern = "vlc-record-{date}-{time}-udp_{cir}[ words]"
        else:
            pattern = "{words} (DOWNLINK VIDEO, Droplet/Flame View Movie)"
        if nf: ids["flex_number"] = nf.group(1)
        if nc: ids["cir_testpoint"] = nc.group(0).upper()
        if ff: ids["folder_flex_number"] = ff.group(1)
        if fcm: ids["folder_cir"] = fcm.group(0).upper()
        cir = nc.group(0).upper() if nc else (fcm.group(0).upper() if fcm else "")
        src = "name" if nc else ("folder" if fcm else "")
        if nc and fcm and nc.group(0).upper() != fcm.group(0).upper():
            conflict = f"name {nc.group(0).upper()} vs folder {fcm.group(0).upper()}"
        if nf and ff and nf.group(1) != ff.group(1):
            conflict = (conflict + "; " if conflict else "") + f"name FLEX-{nf.group(1)} vs folder FLEX-{ff.group(1)}"
        hits = cfi_cir.get(cir, set()) if cir else set()
        if len(hits) == 1:
            tie, tid = "single_test", next(iter(hits))
            if nf and cfi_num.get(nf.group(1)) and cfi_num[nf.group(1)] != hits:
                notes.append("FLEX number in name points to another row")
        elif cir:
            day = (2017, int(cir[1:4]))
            ids["cir_day"] = cir[1:4]
            if cfi_days.get(day):
                tie, cands = "day", sorted(cfi_days[day])
                notes.append("CIR test point not in the table; its day is")
            else:
                notes.append("neither the CIR test point nor its day is in the table")

    elif inv == "PSI-69":
        old = re.search(r"(?<![0-9A-Z])(\d{3}[RF]\d{3})(?![0-9])", stem)
        new = re.search(r"(?<![A-Z0-9])([CXNH])(\d{3})([HMR])(\d{2})(-?[A-D])?(?![0-9])", stem)
        iss = re.search(r"_ISS_(\d{8})_(\d{6})?", stem)
        ffx = re.search(r"(?i)FLEX[- ](\d{3})(?:_(\d{2}_\w{3}_\d{4})_(\w+?)_(\w+))?$", leaf)
        if iss:
            pattern = "_ISS_{YYYYMMDD}_{hhmmss} {testpoint} Movie"
        elif mv and new:
            pattern = "vlc-record-{date}-{time}-udp_{testpoint}[{camera letter}]"
        elif mv:
            pattern = "vlc-record-{date}-{time}-udp_{other}"
        else:
            pattern = "{camera view words} (Droplet/Flame/MDCA/HiBMS2 View Movie)"
        if old: ids["testpoint"] = old.group(1)
        if new: ids["testpoint_2013"] = new.group(0)
        if ffx:
            ids["folder_flex_test"] = ffx.group(1)
            if ffx.group(4): ids["folder_testpoint"] = ffx.group(4)
        tp = old.group(1) if old else ""
        src = "name" if tp else ""
        if not tp and ffx and ffx.group(4):
            tp, src = ffx.group(4), "folder"
        hits = flex_id.get(norm(tp), set()) if tp else set()
        if not hits and ffx and not tp:
            notes.append("folder gives only a FLEX number; not used, because folder numbers do not follow the table's 'FLEX Test #' (team check on 9 folders)")
        if ffx and tp and flex_num.get(str(int(ffx.group(1)))) and flex_id.get(norm(tp)) and flex_num[str(int(ffx.group(1)))] != flex_id[norm(tp)]:
            conflict = f"folder FLEX {ffx.group(1)} vs testpoint {tp}"
        if len(hits) == 1:
            tie, tid = "single_test", next(iter(hits))
        elif new:
            notes.append("2013-2014 test point; the FLEX table ends in 2011")
        elif not hits:
            notes.append("no test point in name or folder")

    elif inv == "PSI-101":
        m = re.match(r"(\d+) (\w+) vlc-record", stem)
        pattern = "{n} {material} vlc-record-{date}-{time}-udp_{ip} _{port}-" if m else "vlc-record-{date}-{time}-udp_{ip} _{port}-"
        mat = (m.group(2) if m else folder.split("/")[-2]).lower()
        mat = {"lampwick": "lampwick", "cotton lamp wick": "lampwick"}.get(mat, mat)
        if m: ids["clip_number"], ids["material"] = m.group(1), m.group(2)
        else: ids["folder_material"] = folder.split("/")[-2]
        src = "name" if m else "name+folder"
        if mv:
            d = datetime.date(int(mv.group(1)), int(mv.group(2)), int(mv.group(3)))
            key = f"{d.day}-{d.strftime('%b')}"
            rr = samer.get((key, mat), [])
            if rr:
                bases = {re.sub(r"a$", "", n) for _, n in rr}
                if len(bases) == 1:
                    tie, cands = "run", sorted(t for t, _ in rr)
                    notes.append("one test number and its aged ('a') row on that date and material")
                else:
                    tie, cands = "day", sorted(t for t, _ in rr)
                    notes.append(f"{len(bases)} test numbers of this material on that date")
            elif samer_day.get(key):
                tie, cands = "day", sorted(samer_day[key])
                notes.append("no row of this material on that date")
            else:
                notes.append("no table row on that date")

    elif inv == "PSI-107":
        a = re.match(r"GMT(\d+)_(\d{2})\.(\d{2})$", stem)
        bm = re.match(r"SPICE_GMT(\d+)_Ign(\d+)([ab]?)$", stem)
        c = re.match(r"SPICE_GMT(\d{4})_(\d{3})_video$", stem)
        if a:
            pattern = "GMT{day}_{hh.mm}"; ids.update(gmt_day=a.group(1), time=f"{a.group(2)}:{a.group(3)}"); day = int(a.group(1))
        elif bm:
            pattern = "SPICE_GMT{day}_Ign{n}[a|b]"; ids.update(gmt_day=bm.group(1), ignition=bm.group(2) + bm.group(3)); day = int(bm.group(1))
        elif c:
            pattern = "SPICE_GMT{year}_{day}_video"; ids.update(year=c.group(1), gmt_day=c.group(2)); day = int(c.group(2))
        else:
            pattern, day = "(other)", None
        src = "name"
        if day and spice_day.get(day):
            tie, cands = "day", sorted(t for t, _ in spice_day[day])
            ign = sorted({g for _, g in spice_day[day]})
            ids["table_ignitions_that_day"] = str(len(ign))
            if bm:
                k = int(bm.group(2))
                if k <= len(ign):
                    ids["ordinal_candidate"] = f"ignition {k} of {len(ign)} by GMT ignition time (team reading, unchecked)"
        elif day:
            notes.append(f"GMT day {day} not in the SPICE table")

    elif inv == "PSI-106":
        dm = re.match(r"DIMSG(\d+)M_1$", stem)
        hx = re.match(r"[0-9a-f]{16}$", stem)
        pattern = "DIMSG{n}M_1" if dm else ("{16 hex digits}" if hx else "(other)")
        if dm: ids["dims_number"] = dm.group(1)
        ut = re.search(r"UT_(\d{3})_(\d{3})", folder)
        fday = re.search(r"_(\d{3})$", folder)
        if ut:
            ids["folder_day_range"] = f"{ut.group(1)}-{ut.group(2)}"
            inside = sorted(d for d in slice_days if int(ut.group(1)) <= d <= int(ut.group(2)))
            src = "folder"
            if len(inside) == 1:
                tie = "day"
            elif inside:
                tie = "several_days"; notes.append(f"folder spans table days {inside}")
        elif fday and "ground_1g" not in words:
            ids["folder_day"] = fday.group(1); src = "folder"
            if int(fday.group(1)) in slice_days:
                tie = "day"; notes.append("table has one row per test day")
        else:
            notes.append("ground (1g) calibration folder" if "ground_1g" in words else "no day")

    if any(w in words for w in ("calibration", "ground_1g")) and tie != "none":
        notes.append("calibration or ground clip by its words; tie kept as the name gives it")
    rows.append(dict(v, bare=b, pattern=pattern, ids=ids, words=words, tie=tie, test_id=tid, cands=cands, src=src, conflict=conflict, notes=notes))

# ---------------------------------------------------------------- outputs
os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "video_index_names.csv"), "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["investigation", "category", "folder", "file_name", "bytes", "extension", "pattern",
                "identifiers", "clip_words", "identifier_source", "tie_level", "test_id",
                "candidate_test_ids_n", "candidate_test_ids", "name_folder_conflict", "notes", "psi_file_id"])
    for r in sorted(rows, key=lambda r: (int(r["investigation"][4:]), r["key"])):
        w.writerow([r["investigation"], r["category"], r["folders"], r["name"], int(r["bytes"]), r["ext"], r["pattern"],
                    "; ".join(f"{k}={v}" for k, v in r["ids"].items()), ";".join(r["words"]), r["src"], r["tie"],
                    r["test_id"], len(r["cands"]), " ".join(r["cands"][:40]) + (" ..." if len(r["cands"]) > 40 else ""),
                    r["conflict"], " | ".join(r["notes"]), r["id"]])

S = {"videos": len(rows), "bytes": int(sum(r["bytes"] for r in rows))}
inv_sum = collections.OrderedDict()
for r in sorted(rows, key=lambda r: int(r["investigation"][4:])):
    e = inv_sum.setdefault(r["investigation"], {"videos": 0, "bytes": 0, "ext": collections.Counter(), "patterns": collections.Counter(),
                                               "tie": collections.Counter(), "tie_bytes": collections.Counter(), "words": collections.Counter(),
                                               "src": collections.Counter(), "conflicts": 0, "single_tests": set(), "run_tests": set()})
    e["videos"] += 1; e["bytes"] += int(r["bytes"]); e["ext"][r["ext"]] += 1; e["patterns"][r["pattern"]] += 1
    e["tie"][r["tie"]] += 1; e["tie_bytes"][r["tie"]] += int(r["bytes"]); e["src"][r["src"] or "-"] += 1
    for wd in r["words"]: e["words"][wd] += 1
    if r["conflict"]: e["conflicts"] += 1
    if r["tie"] == "single_test": e["single_tests"].add(r["test_id"])
    if r["tie"] == "run": e["run_tests"].update(r["cands"])
tot = collections.Counter(r["tie"] for r in rows)
totb = collections.Counter()
for r in rows: totb[r["tie"]] += int(r["bytes"])
single_all = {r["test_id"] for r in rows if r["tie"] == "single_test"}
run_all = {t for r in rows if r["tie"] == "run" for t in r["cands"]}
tests_n = collections.Counter(t["investigation_id"] for t in tests)
needs = collections.defaultdict(lambda: {"counted": 0, "single": 0, "single_or_run": 0, "in_scope": 0, "in_scope_single": 0})
for n in need_tests:
    e = needs[n["need_id"]]
    e["in_scope"] += 1
    if n["test_id"] in single_all: e["in_scope_single"] += 1
    if n["objective_link"] == "stated":
        e["counted"] += 1
        if n["test_id"] in single_all: e["single"] += 1
        if n["test_id"] in single_all or n["test_id"] in run_all: e["single_or_run"] += 1
need_by_inv = collections.Counter()
for n in need_tests:
    if n["objective_link"] == "stated" and n["test_id"] in single_all:
        need_by_inv[(n["need_id"], n["investigation_id"])] += 1
# second-view / still-sequence share among single ties
desc_single = collections.Counter(wd for r in rows if r["tie"] == "single_test" for wd in r["words"])
out = {
    "totals": S, "tie_videos": dict(tot), "tie_bytes": dict(totb),
    "tests_with_single_video": len(single_all), "tests_with_run_video_only": len(run_all - single_all),
    "per_investigation": {k: {"videos": v["videos"], "bytes": v["bytes"], "ext": dict(v["ext"]), "patterns": dict(v["patterns"]),
                              "tie": dict(v["tie"]), "tie_bytes": dict(v["tie_bytes"]), "words": dict(v["words"]), "id_source": dict(v["src"]),
                              "name_folder_conflicts": v["conflicts"], "tests_in_tests_csv": tests_n.get(k, 0),
                              "tests_with_single_video": len(v["single_tests"]), "tests_reached_by_run_only": len(v["run_tests"] - v["single_tests"])}
                          for k, v in inv_sum.items()},
    "needs_counted_with_video": {k: dict(v) for k, v in sorted(needs.items())},
    "needs_by_investigation_single": {f"{a}|{b}": c for (a, b), c in sorted(need_by_inv.items())},
    "words_on_single_ties": dict(desc_single),
    "asrun_error": asrun.get("_error"),
}
json.dump(out, open(os.path.join(OUT, "video_index_summary.json"), "w"), indent=1, default=str)
print(json.dumps(out, indent=1, default=str)[:12000])
