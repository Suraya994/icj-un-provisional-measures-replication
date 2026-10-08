#!/usr/bin/env python3
from pathlib import Path
import csv, json, hashlib, re, sys, collections, subprocess
ROOT=Path(__file__).resolve().parents[1]

def read_csv(p):
    with open(p,encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

def fail(msg):
    print('FAIL:',msg);sys.exit(1)
legal=read_csv(ROOT/'data/01_legal_corpus/ICJ_LEGAL_CORPUS_41_HUMAN.csv')
univ=read_csv(ROOT/'data/02_universe/UN_EVENT_UNIVERSE_13692_STRUCTURED.csv')
pairs=read_csv(ROOT/'data/03_screening/TEMPORAL_PAIRS_17413_SCREENING.csv')
review=read_csv(ROOT/'data/04_human_coding/MANUAL_REVIEW_233_HUMAN.csv')
recall=read_csv(ROOT/'data/04_human_coding/RECALL_AUDIT_120_CANDIDATE_IDS_RECONSTRUCTED.csv')
recall_binary=read_csv(ROOT/'data/04_human_coding/RECALL_REVIEW_120_HUMAN_BINARY_RECONSTRUCTED.csv')
posdocs=read_csv(ROOT/'data/05_results/POSITIVE_DOCUMENTARY_RECORDS_4.csv')
posproc=read_csv(ROOT/'data/05_results/POSITIVE_INSTITUTIONAL_PROCESSES_3.csv')
orders=read_csv(ROOT/'data/05_results/ORDER_LEVEL_RESULTS_41_CANONICAL.csv')
integ=read_csv(ROOT/'data/06_sources/SOURCE_INTEGRITY_VERIFICATION_137.csv')

assert len(legal)==41 and len({r['order_id'] for r in legal})==41
assert len({r['case_number'] for r in legal})==27
assert collections.Counter(r['order_disposition_code_manual'] for r in legal)==collections.Counter({'NEW_PM':20,'MODIFIED_PM':4,'REAFFIRMED_PM':3,'REQUEST_REJECTED':12,'WITHDRAWN_DISCONTINUED':2})
assert len(univ)==13692 and len({r['event_uid'] for r in univ})==13692
assert collections.Counter(r['event_type'] for r in univ)==collections.Counter({'SC_MEETING':6415,'GA_FORMAL_VOTE':5694,'SC_FORMAL_VOTE':1578,'SC_SPECIAL_VETO':5})
assert len(legal)*len(univ)==561372
assert len(pairs)==17413 and len({r['stage6_pair_key'] for r in pairs})==17413
assert len(review)==233 and len({r['stage6_pair_key'] for r in review})==233
assert collections.Counter(r['final_link_code'] for r in review)==collections.Counter({'0':73,'1':31,'2':126,'3':3})
assert all(r['primary_coder']=='Suraya Bazarova' and r['primary_coding_mode']=='HUMAN_MANUAL' for r in review)
assert all('PENDING_DOCUMENT_REVIEW' not in str(r) for r in review)
assert len(recall)==120 and len({r['stage6_pair_key'] for r in recall})==120
assert all(r['published_manuscript_reports_fulltext_review']=='YES' and r['published_manuscript_reports_no_additional_order_specific_positive']=='YES' for r in recall)
assert len(recall_binary)==120 and len({r['stage6_pair_key'] for r in recall_binary})==120
assert {r['stage6_pair_key'] for r in recall_binary}=={r['stage6_pair_key'] for r in recall}
assert all(r['primary_reviewer']=='Suraya Bazarova' and r['review_mode']=='HUMAN_FULLTEXT_REVIEW' and r['review_completed']=='YES' and r['order_specific_engagement']=='0' for r in recall_binary)
assert all('second_coder' not in k.lower() for k in recall_binary[0].keys())
for lp in ['LICENSE','LICENSE-CODE','LICENSE-DATA-DOCS','LICENSE_NOTICE.md']:
    assert (ROOT/lp).exists(), f'missing licence file: {lp}'
assert len(posdocs)==4 and len({r['document_symbol'] for r in posdocs})==4
assert len(posproc)==3 and len({r['process_id'] for r in posproc})==3
primary=[r for r in orders if r['primary_sample']=='1'];sens=[r for r in orders if r['sensitivity_sample']=='1']
assert len(primary)==24 and len(sens)==27
assert [sum(int(r[f'broad_{w}d']) for r in primary) for w in [30,90,180]]==[6,7,10]
assert [sum(int(r[f'order_specific_{w}d']) for r in primary) for w in [30,90,180]]==[2,2,2]
rr=collections.Counter((r['reporting_requirement'],r['order_specific_engagement_final']) for r in primary)
assert rr[('YES','1')]==2 and rr[('YES','0')]==10 and rr[('NO','1')]==0 and rr[('NO','0')]==12
assert len(integ)==137 and sum(int(r['hash_match']) for r in integ)==137
coverage=read_csv(ROOT/'data/07_postpublication_diagnostics/PRIMARY_POSTORDER_4868_REVIEW_COVERAGE.csv')
assert len(coverage)==4868
assert collections.Counter(r['review_evidence_status'] for r in coverage)==collections.Counter({'NO_PRESERVED_MANUAL_REVIEW_EVIDENCE':4626,'PRESERVED_ORIGINAL_233_HUMAN_REVIEW':209,'PUBLISHED_RECALL_REVIEW_REPORTED_CANDIDATE_ID_RECONSTRUCTED':33})
interp=read_csv(ROOT/'data/07_postpublication_diagnostics/ORDER_LEVEL_INTERPRETATION_24.csv')
assert len(interp)==24 and sum(r['evidence_interpretation']=='VERIFIED_POSITIVE_ORDER_SPECIFIC_ENGAGEMENT' for r in interp)==2


# Public row-level data must not imply a second coder who did not contribute to the published coding.
assert all('second_coder' not in k.lower() for k in review[0].keys())
assert all('second_coder' not in k.lower() for k in recall[0].keys())
assert all('second_coder' not in k.lower() for k in recall_binary[0].keys())
# Reconstruct the original case-dictionary selection and require an exact 233-key match.
screen=subprocess.run([sys.executable,str(ROOT/'code/reconstruct_dictionary_screen.py')],capture_output=True,text=True)
if screen.returncode!=0:
    fail('dictionary-screen reconstruction failed:\n'+screen.stdout+screen.stderr)

# --- Added in 1.1.0 -------------------------------------------------------------------------
# These are regression checks against the published numbers. They show that the package is
# consistent with the paper and with itself. They do not validate the coding.
assert all(re.fullmatch(r'[0-9a-f]{64}', r['expected_sha256']) for r in integ)
assert all(r['expected_sha256']==r['recomputed_sha256'] for r in integ), 'expected and recomputed digests differ'
assert all(int(r['relative_day'])>0 for r in review), 'review layer should hold post-order pairs only'
assert all(r['same_icj_case_confirmed']=='1' for r in review if r['final_link_code'] in {'2','3'})
assert all(r['same_icj_case_confirmed']=='0' for r in review if r['final_link_code'] in {'0','1'})
# Paper-versus-data concordance: fails if the set of documented mismatches changes.
res=subprocess.run([sys.executable,str(ROOT/'code/check_paper_concordance.py')],capture_output=True,text=True)
if res.returncode!=0:
    fail('paper concordance check failed:\n'+res.stdout+res.stderr)

# Scan public release artifacts for machine-specific paths and local-environment traces.
for p in ROOT.rglob('*'):
    if p.is_file() and p.suffix.lower() in {'.csv','.md','.py','.json','.txt','.cff','.yml','.yaml'}:
        if p.resolve() == Path(__file__).resolve():
            continue

        txt = p.read_text(encoding='utf-8', errors='ignore')

        local_environment_patterns = [
            re.escape(chr(47) + 'Users' + chr(47)) + r'[^/\\s]+',
            r'[A-Za-z]:\\\\Users\\\\[^\\\\\s]+',
            r'(?i)(?:^|[/\\\\])Desktop(?:[/\\\\])',
            r'(?i)(?:^|[/\\\\])Downloads(?:[/\\\\])',
            r'(?i)\\b' + 'Mac' + 'Book' + r'\\b',
        ]

        for pattern in local_environment_patterns:
            if re.search(pattern, txt):
                fail(f'local-environment trace detected in {p.relative_to(ROOT)}')

print('PASS: release validation completed successfully (consistency checks only, see docs/PAPER_CONCORDANCE.md)')
