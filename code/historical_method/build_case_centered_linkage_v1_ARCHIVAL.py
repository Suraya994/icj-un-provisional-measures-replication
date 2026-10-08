#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, re
from collections import Counter
from pathlib import Path

def norm(x): return re.sub(r"\s+"," ",re.sub(r"[^\w]+"," ",str(x or "").casefold())).strip()
def terms(x): return [norm(v) for v in str(x or "").split("|") if norm(v)]
def hit(text, phrases): return sorted({p for p in phrases if re.search(rf"(?<!\w){re.escape(p)}(?!\w)",text)})

def load(path):
    with path.open(encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
def write(path, rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    if not rows: return
    with path.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

def main(root:Path,v8:Path,legal:Path,dictionary:Path,outdir:Path):
    pairs=load(v8); legal_rows=load(legal); dictionaries=load(dictionary)
    legal_by={r["order_id"]:r for r in legal_rows}; d_by={r["case_number"]:r for r in dictionaries}
    meetings=load(root/"data/sc_meetings_raw.csv")
    meeting_urls={r.get("meeting_record",""):{k:r.get(k,"") for k in ["meeting_url","press_release_url","outcome_document_url","source_local_path"]} for r in meetings}
    ga=load(root/"data/ga_vote_proposals_raw.csv")
    ga_urls={v:r.get("undl_link","") for r in ga for v in [r.get("resolution",""),r.get("draft",""),r.get("meeting","")] if v}
    post=[]
    for r in pairs:
        if int(r["relative_day"])<0: continue
        d=d_by[r["case_number"]]; lg=legal_by[r["order_id"]]
        text_raw=" | ".join(r.get(k,"") for k in ["event_text","document","meeting_record","draft","resolution"])
        text=norm(text_raw)
        ah=hit(text,terms(d["applicant_aliases"])); rh=hit(text,terms(d["respondent_aliases"]));
        dh=hit(text,terms(d["case_distinctive_terms"])); gh=hit(text,terms(d["official_sc_agenda_titles"]));
        sh=hit(text,terms(d["known_relevant_un_symbols"])); xh=hit(text,terms(d["exclusion_terms_or_files"]));
        icj=bool(re.search(r"\b(?:international court of justice|icj|world court)\b",text))
        pm=bool(re.search(r"\b(?:provisional measures?|article 41|order of \d{1,2} [a-z]+ 20\d{2})\b",text))
        strong=bool(sh or gh or ((ah and rh) and dh) or (len(dh)>=2 and (ah or rh)))
        special_exclusion = (
            r["case_number"] in {"192","193"} and "advisory opinion" in text
        ) or (r["case_number"]=="126" and ("international criminal tribunal for rwanda" in text or "ictr" in text))
        eligible = lg["order_disposition_code_manual"] in {"NEW_PM","MODIFIED_PM","REAFFIRMED_PM"}
        if special_exclusion or (xh and not strong): code="0"; basis="KNOWN_EXCLUSION"
        elif eligible and strong: code="9"; basis="SAME_DISPUTE_FILE_REQUIRES_FULL_DOCUMENT_TO_DISTINGUISH_2_FROM_3"
        elif icj and (strong or pm or dh): code="9"; basis="ICJ_REFERENCE_REQUIRES_FULL_DOCUMENT"
        elif strong: code="2"; basis="SAME_DISPUTE_FILE_NONELIGIBLE_ORDER"
        elif gh or ((ah or rh) and dh) or len(dh)>=2: code="1"; basis="GENERAL_CRISIS_OR_LEGAL_CONTEXT"
        else: code="0"; basis="NO_CASE_FILE_EVIDENCE"
        m=meeting_urls.get(r.get("meeting_record",""),{})
        urls=[m.get("meeting_url",""),m.get("press_release_url",""),m.get("outcome_document_url",""),ga_urls.get(r.get("resolution",""),""),ga_urls.get(r.get("draft",""),""),r.get("source_url","")]
        best=next((u for u in urls if u),"")
        post.append({**r,
            "order_disposition_code":lg["order_disposition_code_manual"],
            "binding_analysis_eligible":int(eligible),
            "link_code_preliminary":code,"link_code_final":"","coding_basis":basis,
            "matched_applicant_aliases_casefile":"|".join(ah),"matched_respondent_aliases_casefile":"|".join(rh),
            "matched_distinctive_terms_casefile":"|".join(dh),"matched_official_agenda_casefile":"|".join(gh),
            "matched_known_symbols_casefile":"|".join(sh),"matched_exclusions_casefile":"|".join(xh),
            "explicit_icj_reference_metadata":int(icj),"provisional_measure_reference_metadata":int(pm),
            "best_official_document_url":best,"local_document_path":m.get("source_local_path",""),
            "full_document_status":"REQUIRED" if code=="9" else "NOT_REQUIRED_FOR_PRELIMINARY_CODE",
            "evidence_quote_manual":"","coder_manual":"","validation_status_manual":"PENDING" if code in {"1","2","9"} else "METADATA_EXCLUSION_PRECODE",
        })
    assert len(post)==sum(int(r["relative_day"])>=0 for r in pairs)
    write(outdir/"case_centered_post_all_pairs_v1.csv",post)
    queue=[r for r in post if r["link_code_preliminary"] in {"1","2","9"}]
    write(outdir/"case_centered_manual_review_queue_v1.csv",queue)
    nine=[r for r in post if r["link_code_preliminary"]=="9"]
    events={}
    for r in nine:
        e=events.setdefault(r["stage6_event_key"],{
            "stage6_event_key":r["stage6_event_key"],"event_type":r["event_type"],"event_date":r["event_date"],
            "meeting_record":r["meeting_record"],"draft":r["draft"],"resolution":r["resolution"],"event_text":r["event_text"],
            "best_official_document_url":r["best_official_document_url"],"matched_order_ids":[],"matched_case_numbers":[],
            "download_status":"PENDING","local_path":"","sha256":"","final_document_code":"",
        })
        e["matched_order_ids"].append(r["order_id"]); e["matched_case_numbers"].append(r["case_number"])
    event_rows=[]
    for e in events.values():
        e["matched_order_ids"]="|".join(sorted(set(e["matched_order_ids"]))); e["matched_case_numbers"]="|".join(sorted(set(e["matched_case_numbers"])))
        event_rows.append(e)
    event_rows.sort(key=lambda x:(x["event_date"],x["stage6_event_key"]))
    write(outdir/"full_document_download_queue_code9_unique_events_v1.csv",event_rows)
    c=Counter(r["link_code_preliminary"] for r in post)
    summary=[{"metric":"post_pairs","value":len(post)},{"metric":"manual_review_pairs_1_2_9","value":len(queue)},{"metric":"code9_pairs","value":len(nine)},{"metric":"code9_unique_events","value":len(event_rows)}]+[{"metric":f"precode_{k}","value":c[k]} for k in ["0","1","2","9"]]
    write(outdir/"case_centered_linkage_summary_v1.csv",summary)
    print(json.dumps({x["metric"]:x["value"] for x in summary},ensure_ascii=False))

if __name__=="__main__":
    p=argparse.ArgumentParser();
    for name in ["root","v8","legal","dictionary","outdir"]: p.add_argument("--"+name.replace("_","-"),type=Path,required=True)
    a=p.parse_args(); main(a.root,a.v8,a.legal,a.dictionary,a.outdir)
