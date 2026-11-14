# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
# Read-only recount: files whose NAME carries one of the 26 tests recorded inside the lunar-habitat oxygen and pressure ranges.
import csv, re, json, collections, os
HERE=os.path.dirname(os.path.abspath(__file__)); REPO="/Users/choidol/Desktop/NASA/NASA_RAPID/"
def tab(p):
    for enc in ("utf-8-sig","cp1252"):
        try: return list(csv.DictReader(open(p,encoding=enc)))
        except UnicodeDecodeError: pass
T=tab(REPO+"data/psi/experimental_tables/PSI-69_Experimental table_FLEX.csv")
num2id={int(r["FLEX Test #"]):r["FLEX Identifier"].strip() for r in T}
lun=list(range(19,29))+list(range(37,44)); lun_ids={num2id[n]:n for n in lun}
files=[r for r in csv.DictReader(open(os.path.join(HERE,"..","out","files.csv"))) if r["acc"]=="PSI-69" and r["cat"]!="Experimental table"]
def strip(n): return re.sub(r"^PSI-\d+_[^_]+_","",n,count=1)
out=[]
for f in files:
    n=strip(f["name"]); sub=f["sub"]
    m=re.search(r"FLEX[-_](\d{3})(?![0-9])",n)
    nn=int(m.group(1)) if m else None
    ii=None
    for k in lun_ids:
        if re.search(r"(?<![A-Za-z0-9])"+re.escape(k)+r"[A-Da-d]?(?![A-Za-z0-9])",n): ii=k
    test=None; by=[]
    if nn in lun: test=nn; by.append("name_number")
    if ii: 
        by.append("name_identifier")
        if test is None: test=lun_ids[ii]
        elif test!=lun_ids[ii]: by.append("CONFLICT_in_name")
    if test is None: continue
    # folder label: any FLEX number or identifier in the folder path
    fm=re.search(r"(?i)flex[-_ ](\d{3})(?![0-9])",sub); fnum=int(fm.group(1)) if fm else None
    fid=[k for k in num2id.values() if re.search(r"(?<![A-Za-z0-9])"+re.escape(k)+r"(?![A-Za-z0-9])",sub)]
    if fnum is None and not fid: folder="folder_names_no_test"
    elif (fnum is None or fnum==test) and (not fid or fid==[num2id[test]]): folder="folder_agrees"
    else: folder="folder_names_another_test"
    out.append(dict(test=test,name=n,sub=sub,bytes=int(f["bytes"]),by="+".join(by),folder=folder,zip=n.lower().endswith(".zip")))
C=collections.Counter((o["by"],o["folder"],o["zip"]) for o in out); B=collections.Counter()
for o in out: B[(o["by"],o["folder"],o["zip"])]+=o["bytes"]
res=dict(files=len(out),bytes=sum(o["bytes"] for o in out),
  zip=dict(files=sum(o["zip"] for o in out),bytes=sum(o["bytes"] for o in out if o["zip"])),
  not_zip=dict(files=sum(not o["zip"] for o in out),bytes=sum(o["bytes"] for o in out if not o["zip"])),
  by_label_and_folder=[dict(label=k[0],folder=k[1],zip=k[2],files=v,bytes=B[k]) for k,v in sorted(C.items())],
  folder_names_another_test=[(o["test"],o["name"],o["sub"]) for o in out if o["folder"]=="folder_names_another_test"],
  per_test={n:dict(files=sum(1 for o in out if o["test"]==n),bytes=sum(o["bytes"] for o in out if o["test"]==n),zips=sum(1 for o in out if o["test"]==n and o["zip"]),
                   testsheet=[o["bytes"] for o in out if o["test"]==n and o["name"].endswith("TestSheet.txt")],
                   summary_pdf=[o["name"] for o in out if o["test"]==n and re.search(r"Summary\.pdf$",o["name"])],
                   comments=[o["bytes"] for o in out if o["test"]==n and o["name"].endswith("Comments.txt")]) for n in lun})
# other files sitting in a folder whose label names a lunar test number but whose name names another test
json.dump(res,open(os.path.join(HERE,"lunar_links_PSI-69.json"),"w"),indent=1)
print(json.dumps({k:v for k,v in res.items() if k not in("per_test","folder_names_another_test")},indent=1))
print(len(res["folder_names_another_test"]), collections.Counter((t,s) for t,_,s in res["folder_names_another_test"]))
for n,p in res["per_test"].items(): print(n,p["files"],p["bytes"],p["zips"],p["testsheet"],len(p["summary_pdf"]),p["comments"])
ext=collections.Counter(os.path.splitext(o["name"])[1].lower() for o in out); print(ext)
small=[o for o in out if not o["zip"]]; print("max non-zip",max(o["bytes"] for o in small))
