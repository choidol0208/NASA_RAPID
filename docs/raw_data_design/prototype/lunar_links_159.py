# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
import csv, re, json, collections, os
REPO="/Users/choidol/Desktop/NASA/NASA_RAPID/"; HERE=os.path.dirname(os.path.abspath(__file__))
ST=[r for r in csv.DictReader(open(REPO+"data/pipeline/scenario_tests.csv")) if r["scenario_id"]=="lunar_habitat" and r["o2_match"]=="in" and r["pressure_match"]=="in" and r["investigation_id"]=="PSI-159"]
T={r["test_id"]:r for r in csv.DictReader(open(REPO+"data/pipeline/tests.csv"))}
ids={}
for r in ST:
    t=r["test_id"]; m=re.search(r"(\d{5}[A-Z]\d{1,2})",t); ids[m.group(1)]=t
    print(t,T[t]["fuel_phase"],T[t]["o2_pct"],T[t]["pressure_kpa"],T[t].get("fuel",""))
d=json.load(open(os.path.join(HERE,"..","listings","PSI-159.json")))
flat=[]
def walk(o):
    if isinstance(o,dict):
        if "bytes_size" in o and not o.get("directory"): flat.append(o)
        for v in o.get("files",[]) or []: walk(v)
    elif isinstance(o,list):
        for v in o: walk(v)
walk(d)
print("listed files",len(flat),sum(int(f["bytes_size"]) for f in flat))
out=[]
for f in flat:
    name=f["key"].split("/")[-1]; sub=f.get("subcategory") or ""
    m=re.search(r"(?<!\d)(\d{5}[A-Z]\d{1,2})(?!\d)",name)
    if not m or m.group(1) not in ids: continue
    fm=re.findall(r"(?<!\d)(\d{5}[A-Z]\d{1,2})(?!\d)",sub)
    folder="folder_names_no_test" if not fm else ("folder_agrees" if set(fm)=={m.group(1)} else "folder_names_another_test")
    big=name.lower().endswith((".zip",".ts"))
    out.append(dict(id=m.group(1),name=name,sub=sub,bytes=int(f["bytes_size"]),folder=folder,big=big,cat=f.get("sortingCategory")))
C=collections.Counter((o["folder"],o["big"]) for o in out); B=collections.Counter()
for o in out: B[(o["folder"],o["big"])]+=o["bytes"]
res=dict(tests=len(ids),files=len(out),bytes=sum(o["bytes"] for o in out),
 zip_or_ts=dict(files=sum(o["big"] for o in out),bytes=sum(o["bytes"] for o in out if o["big"])),
 other=dict(files=sum(not o["big"] for o in out),bytes=sum(o["bytes"] for o in out if not o["big"])),
 by_folder=[dict(folder=k[0],zip_or_ts=k[1],files=v,bytes=B[k]) for k,v in sorted(C.items())],
 per_test={i:sum(1 for o in out if o["id"]==i) for i in ids},
 ext=dict(collections.Counter(os.path.splitext(o["name"])[1].lower() for o in out)),
 max_other=max(o["bytes"] for o in out if not o["big"]),
 other_le_10MB=dict(files=sum(1 for o in out if not o["big"] and o["bytes"]<=10_000_000),bytes=sum(o["bytes"] for o in out if not o["big"] and o["bytes"]<=10_000_000)))
json.dump(res,open(os.path.join(HERE,"lunar_links_PSI-159.json"),"w"),indent=1); print(json.dumps(res,indent=1))
print([ (o["id"],o["name"],o["sub"]) for o in out if o["folder"]=="folder_names_another_test"][:10])
print(collections.Counter(o["sub"] for o in out).most_common(6))
