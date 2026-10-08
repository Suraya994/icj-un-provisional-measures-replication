#!/usr/bin/env python3
"""Reconstruct the original case-dictionary candidate screen from public package files.

This script reproduces the 8,557 nonnegative-lag pair layer and the exact 233
pairs advanced to the published manual-review layer. It implements the logic of
the archived build_case_centered_linkage_v1.py but uses only portable package inputs.
It is candidate selection, not substantive coding.
"""
from pathlib import Path
import csv,re,collections,json,sys
ROOT=Path(__file__).resolve().parents[1]
def read(p):
    with open(p,encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def norm(x):return re.sub(r"\s+"," ",re.sub(r"[^\w]+"," ",str(x or "").casefold())).strip()
def terms(x):return [norm(v) for v in str(x or "").split("|") if norm(v)]
def hit(text,phrases):return sorted({p for p in phrases if re.search(rf"(?<!\w){re.escape(p)}(?!\w)",text)})
pairs=read(ROOT/'data/03_screening/TEMPORAL_PAIRS_17413_SCREENING.csv')
legal=read(ROOT/'data/01_legal_corpus/ICJ_LEGAL_CORPUS_41_HUMAN.csv')
dicts=read(ROOT/'data/03_screening/dictionary/ICJ_CASE_FILE_DICTIONARY_V1.csv')
manual=read(ROOT/'data/04_human_coding/MANUAL_REVIEW_233_HUMAN.csv')
lg={r['order_id']:r for r in legal}; db={r['case_number']:r for r in dicts}
selected=[]; rows=[]; counts=collections.Counter()
for r in pairs:
    if int(r['relative_day'])<0:continue
    d=db[r['case_number']]; l=lg[r['order_id']]
    text=norm(' | '.join(r.get(k,'') for k in ['event_text_metadata','document','meeting_record','draft','resolution']))
    ah=hit(text,terms(d['applicant_aliases'])); rh=hit(text,terms(d['respondent_aliases']))
    dh=hit(text,terms(d['case_distinctive_terms'])); gh=hit(text,terms(d['official_sc_agenda_titles']))
    sh=hit(text,terms(d['known_relevant_un_symbols'])); xh=hit(text,terms(d['exclusion_terms_or_files']))
    icj=bool(re.search(r"\b(?:international court of justice|icj|world court)\b",text))
    pm=bool(re.search(r"\b(?:provisional measures?|article 41|order of \d{1,2} [a-z]+ 20\d{2})\b",text))
    strong=bool(sh or gh or ((ah and rh) and dh) or (len(dh)>=2 and (ah or rh)))
    special=(r['case_number'] in {'192','193'} and 'advisory opinion' in text) or (r['case_number']=='126' and ('international criminal tribunal for rwanda' in text or 'ictr' in text))
    eligible=l['order_disposition_code_manual'] in {'NEW_PM','MODIFIED_PM','REAFFIRMED_PM'}
    if special or (xh and not strong): code='0';basis='KNOWN_EXCLUSION'
    elif eligible and strong: code='9';basis='SAME_DISPUTE_FILE_REQUIRES_FULL_DOCUMENT_TO_DISTINGUISH_2_FROM_3'
    elif icj and (strong or pm or dh): code='9';basis='ICJ_REFERENCE_REQUIRES_FULL_DOCUMENT'
    elif strong: code='2';basis='SAME_DISPUTE_FILE_NONELIGIBLE_ORDER'
    elif gh or ((ah or rh) and dh) or len(dh)>=2: code='1';basis='GENERAL_CRISIS_OR_LEGAL_CONTEXT'
    else: code='0';basis='NO_CASE_FILE_EVIDENCE'
    counts[code]+=1
    rows.append({'stage6_pair_key':r['stage6_pair_key'],'preliminary_code':code,'coding_basis':basis})
    if code=='9':selected.append(r['stage6_pair_key'])
manual_keys={r['stage6_pair_key'] for r in manual}; selected_set=set(selected)
out=ROOT/'outputs/screening_reconstruction';out.mkdir(parents=True,exist_ok=True)
with open(out/'dictionary_screen_selected_233.csv','w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['stage6_pair_key'],lineterminator='\n');w.writeheader();w.writerows({'stage6_pair_key':x} for x in sorted(selected_set))
summary={'post_or_same_day_pairs':len(rows),'preliminary_code_counts':dict(sorted(counts.items())),'selected_code9_pairs':len(selected_set),'manual_review_pairs':len(manual_keys),'exact_pair_key_match':selected_set==manual_keys,'selected_only':len(selected_set-manual_keys),'manual_only':len(manual_keys-selected_set)}
(out/'dictionary_screen_reconstruction.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2))
if not (len(rows)==8557 and counts==collections.Counter({'0':8246,'1':25,'2':53,'9':233}) and selected_set==manual_keys):sys.exit(1)
