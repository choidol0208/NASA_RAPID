"""Builds the "results first" block of the dashboard (pm request 20261115-1513): per environment and
fire-safety question, what NASA's documents and the investigators' papers report, as quotations, in the
data role's fixed order (data/pipeline/results_by_need.json, written by pipeline/results.py).

AI-generated code: written with an AI assistant (Claude Code, ui role) during the NASA Space Apps
Challenge 2026 hackathon (2026-11-15). No language model runs here or on the page. Nothing is computed
from the printed values and nothing is compared with a criterion: the file's entries are resolved
against its own dictionaries (findings, items, documents) and copied, in the file's own order.
"""
import json
import os
import re

BANNED = ["safe", "unsafe", "will", "predict", "likely"]
KIND_WORDS = {"computed_by_authors": "value computed by the authors", "simulation": "simulation", "preliminary": "preliminary value"}
ACCESS_WORDS = {
    "full_text_read": "passage read in the document",
    "abstract_only": "only the abstract was read",
    "cited_not_read": "known only through a citation",
    "read_from_copy": "read from an unofficial copy",
    "read_by_teammate": "read by another session of the team",
}


class ResultsError(RuntimeError):
    pass


# The human lead's decision of 16:35 on 15 Nov (every notice worded positively): the one disclaimer clause of
# the data role's "found" sentence is printed in its positive form. The file itself is unchanged; any other
# wording of the clause stops the build, so a new form is never shown unnoticed.
POSITIVE = {
    "The grouping and the order are the team's, by a fixed rule on the conditions each statement states; they are not NASA's conclusions.":
    "The grouping and the order are Team RAPID's, by a fixed rule on the conditions each statement states.",
}


def positive(sentence):
    for old, new in POSITIVE.items():
        sentence = sentence.replace(old, new)
    if re.search(r"not NASA's conclusions|not (operational )?safety guidance", sentence):
        raise ResultsError(f"a disclaimer clause in a found sentence has a new wording: {sentence[:160]}")
    return sentence


def _value_label(v):
    lab = v.get("material_as_printed") or v.get("row_label") or v.get("column") or v.get("quantity") or ""
    val = f"{v.get('value_as_printed', '')}" + (f" {v['unit']}" if v.get("unit") else "")
    return f"{lab}: {val}" if lab else val


def build(root):
    path = os.path.join(root, "data", "pipeline", "results_by_need.json")
    if not os.path.exists(path):
        return {}
    d = json.load(open(path, encoding="utf-8"))
    F, I, D = d.get("findings", {}), d.get("items", {}), d.get("documents", {})
    meta = d.get("_meta", {})
    group_label = {g["id"]: g["label"] for g in meta.get("order_rule", {}).get("groups", [])}
    out = {}
    texts = []
    for s in d.get("scenarios", []):
        needs = []
        for n in s.get("needs", []):
            found = n.get("found", {})
            entries = []
            for e in found.get("entries", []):
                f = F.get(e["finding_id"])
                if f is None:
                    raise ResultsError(f"{n['block_id']}: finding {e['finding_id']} is not in the file's findings")
                src = e.get("source", {})
                kind = f.get("result_kind")
                vals = f.get("printed_values") or []
                if e["group"] not in group_label:
                    raise ResultsError(f"{n['block_id']}: group {e['group']!r} has no label in _meta.order_rule")
                entries.append({
                    "group": e["group"], "group_label": group_label[e["group"]],
                    "quote": f.get("quote") or "", "text": "" if f.get("quote") else f.get("text", ""),
                    "doc": src.get("title") or (D.get(src.get("document_id"), {}).get("title", "")),
                    "version": src.get("version", ""), "where": src.get("where", ""), "url": src.get("url", ""),
                    "access": ACCESS_WORDS.get(src.get("access", ""), src.get("access", "")),
                    "kind": KIND_WORDS.get(kind, ""), "relation": f.get("relation") or "",
                    "values": [_value_label(v) for v in vals],
                })
            n_tagged = (n.get("headline", {}).get("fields", {}) or {}).get("n_tagged")
            if n_tagged is not None and n_tagged != len(entries):
                raise ResultsError(f"{n['block_id']}: {len(entries)} entries, the headline says {n_tagged}")
            crit = n.get("criteria", {}) or {}
            nq = len(found.get("entries_tagged_for_all_questions", []))
            needs.append({
                "id": n["need_id"], "name": n.get("need", n["need_id"]), "question": n.get("question", ""),
                "headline": (n.get("headline") or {}).get("text", ""),
                "found_sentence": positive(found.get("sentence", "")), "printed_sentence": found.get("printed_values_sentence", ""),
                "all_q_sentence": found.get("all_questions_sentence", "") if nq else "", "n_all_q": nq,
                "criteria_sentence": crit.get("sentence", ""), "n_criteria": (crit.get("counts") or {}).get("n_criterion_findings", 0),
                "entries": entries,
            })
            texts += [needs[-1]["headline"]]
        out[s["id"]] = {"scenario": s["id"], "label": s.get("label", s["id"]), "needs": needs,
                        "order_rule": meta.get("order_rule", {}).get("text", ""),
                        # the human lead's decision of 16:35 (all notices worded positively): the page prints these two
                        # lines instead of the file's _meta.team_output and _meta.not_research_guidance
                        "team_output": "Groups, order, headlines and counts are Team RAPID's computation from the files the data role names in this file.",
                        "ai_note": "Read by an AI agent.",
                        "source": "data/pipeline/results_by_need.json"}
    # the page adds no sentence of its own to these texts; scan the data role's headlines anyway
    for t in texts:
        for w in BANNED:
            if re.search(rf"\b{w}\b", t, re.I):
                raise ResultsError(f"banned word {w!r} in a headline: {t[:100]}")
    return out
