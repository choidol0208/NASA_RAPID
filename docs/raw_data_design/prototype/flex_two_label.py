# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
# Read-only recount for design.md: PSI-69 (FLEX) file-to-test links under a two-label rule.
# Inputs: ../out/files.csv (PSI listing saved by the probe), the FLEX experimental table in the repo (read-only).
import csv, re, json, collections, os
HERE=os.path.dirname(os.path.abspath(__file__))
ET="/Users/choidol/Desktop/NASA/NASA_RAPID/data/psi/experimental_tables/PSI-69_Experimental table_FLEX.csv"
def tab():
    for enc in ("utf-8-sig","cp1252"):
        try: return list(csv.DictReader(open(ET,encoding=enc)))
        except UnicodeDecodeError: pass
T=tab()
num2id={}; id2nums=collections.defaultdict(list)
for r in T:
    n=int(r["FLEX Test #"]); i=r["FLEX Identifier"].strip()
    num2id[n]=i; id2nums[i].append(n)
dup_ids={i:v for i,v in id2nums.items() if len(v)>1}
files=[r for r in csv.DictReader(open(os.path.join(HERE,"..","out","files.csv"))) if r["acc"]=="PSI-69" and r["cat"]!="Experimental table"]
ids_sorted=sorted(id2nums,key=len,reverse=True)
def strip(n): return re.sub(r"^PSI-\d+_[^_]+_","",n,count=1)
def labels(f):
    n=strip(f["name"]); L={}
    m=re.search(r"FLEX[-_ ]?(\d{3})(?![0-9])",n,re.I)
    if m: L["name_number"]=int(m.group(1))
    for k in ids_sorted:
        if re.search(r"(?<![A-Za-z0-9])"+re.escape(k)+r"[A-Da-d]?(?![A-Za-z0-9])",n):
            L["name_identifier"]=k; break
    m=re.search(r"Flex[-_ ]?(\d{3})(?![0-9])",f["sub"],re.I)
    if m: L["folder_number"]=int(m.group(1))
    return L
def rows_of(L):
    """each label -> set of table test numbers it points to"""
    out={}
    for k,v in L.items():
        if k=="name_identifier": out[k]=set(id2nums.get(v,[]))
        else: out[k]={v} if v in num2id else set()
    return out
def state(L):
    if not L: return "none",None
    R=rows_of(L)
    live={k:v for k,v in R.items() if v}
    if not live: return "id_not_in_table",None
    if len(L)==1:
        (k,v),=live.items()
        return ("one_label", min(v)) if len(v)==1 else ("one_label_ambiguous",None)
    inter=None
    for v in R.values():
        if not v: return "labels_disagree",None   # a label present but not in table
        inter=v if inter is None else inter&v
    if inter and len(inter)==1: return "confirmed",min(inter)
    if inter and len(inter)>1: return "confirmed_ambiguous",None
    return "labels_disagree",None
out=[]
for f in files:
    L=labels(f); s,t=state(L)
    out.append(dict(name=f["name"],sub=f["sub"],bytes=int(f["bytes"]),labels=L,state=s,test=t))
C=collections.Counter(o["state"] for o in out); B=collections.Counter()
for o in out: B[o["state"]]+=o["bytes"]
res=dict(table_rows=len(T),distinct_identifiers=len(id2nums),identifiers_on_more_than_one_row=dup_ids,
         files=len(out),states={k:dict(files=C[k],bytes=B[k]) for k in C})
# folders that hold both a number label (folder) and identifier-named files: do they agree?
fold=collections.defaultdict(set)
for o in out:
    L=o["labels"]
    if "folder_number" in L and "name_identifier" in L: fold[L["folder_number"]].add(L["name_identifier"])
agree=sum(1 for n,ids in fold.items() if n in num2id and all(num2id[n]==i for i in ids))
res["folders_with_folder_number_and_identifier_files"]=len(fold)
res["folders_where_all_identifiers_equal_table_identifier_of_that_number"]=agree
res["folders_where_not"]=len(fold)-agree
# the 17 lunar tests
lun=list(range(19,29))+list(range(37,44))
per={}
tot=collections.Counter(); totb=collections.Counter()
for n in lun:
    i=num2id[n]
    mine=[o for o in out if o["test"]==n or o["labels"].get("name_number")==n or o["labels"].get("folder_number")==n or o["labels"].get("name_identifier")==i]
    c=collections.Counter(o["state"] for o in mine); b=collections.Counter()
    for o in mine: b[o["state"]]+=o["bytes"]
    per[n]=dict(identifier=i,identifier_unique=len(id2nums[i])==1,files=len(mine),bytes=sum(o["bytes"] for o in mine),states=dict(c),
                zip=[(o["name"],o["bytes"],o["state"]) for o in mine if o["name"].lower().endswith(".zip")],
                small_files=sum(1 for o in mine if not o["name"].lower().endswith(".zip")),small_bytes=sum(o["bytes"] for o in mine if not o["name"].lower().endswith(".zip")),
                has_testsheet_txt=any(re.search(r"FLEX-%03d_TestSheet\.txt$"%n,o["name"]) for o in mine),
                summary_pdfs=[o["name"] for o in mine if re.search(r"Summary\.pdf$",o["name"])])
    for k in c: tot[k]+=c[k]; totb[k]+=b[k]
res["lunar_17"]=dict(files=sum(p["files"] for p in per.values()),bytes=sum(p["bytes"] for p in per.values()),
    states={k:dict(files=tot[k],bytes=totb[k]) for k in tot},
    zip_files=sum(len(p["zip"]) for p in per.values()),zip_bytes=sum(z[1] for p in per.values() for z in p["zip"]),
    small_files=sum(p["small_files"] for p in per.values()),small_bytes=sum(p["small_bytes"] for p in per.values()),
    tests_without_zip=[n for n,p in per.items() if not p["zip"]],
    tests_with_testsheet=sum(p["has_testsheet_txt"] for p in per.values()),
    summary_pdfs={n:len(p["summary_pdfs"]) for n,p in per.items()},per_test=per)
ts=[o for o in out if re.search(r"TestSheet\.txt$",o["name"])]
res["testsheet_txt"]=dict(files=len(ts),bytes=sum(o["bytes"] for o in ts),states=dict(collections.Counter(o["state"] for o in ts)))
json.dump(res,open(os.path.join(HERE,"flex_two_label.json"),"w"),indent=1,default=list)
print(json.dumps({k:v for k,v in res.items() if k!="lunar_17"},indent=1,default=list)[:3000])
l=res["lunar_17"]; print(json.dumps({k:v for k,v in l.items() if k!="per_test"},indent=1))
for n,p in per.items(): print(n,p["identifier"],p["identifier_unique"],p["files"],p["bytes"],p["states"],len(p["zip"]),p["has_testsheet_txt"],len(p["summary_pdfs"]))
