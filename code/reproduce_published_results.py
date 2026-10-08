#!/usr/bin/env python3
from pathlib import Path
import csv, json, collections, math
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'data'; T=ROOT/'outputs/tables'; F=ROOT/'outputs/figures'
T.mkdir(parents=True,exist_ok=True); F.mkdir(parents=True,exist_ok=True)
PDF_META={'Creator':'ICJ_UN_PUBLISHED_REPLICATION','Producer':'matplotlib','CreationDate':None,'ModDate':None}

def read_csv(p):
    with open(p,encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write_csv(p,rows):
    with open(p,'w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys()));w.writeheader();w.writerows(rows)

legal=read_csv(D/'01_legal_corpus/ICJ_LEGAL_CORPUS_41_HUMAN.csv')
univ=read_csv(D/'02_universe/UN_EVENT_UNIVERSE_13692_STRUCTURED.csv')
pairs=read_csv(D/'03_screening/TEMPORAL_PAIRS_17413_SCREENING.csv')
review=read_csv(D/'04_human_coding/MANUAL_REVIEW_233_HUMAN.csv')
recall=read_csv(D/'04_human_coding/RECALL_AUDIT_120_CANDIDATE_IDS_RECONSTRUCTED.csv')
posdocs=read_csv(D/'05_results/POSITIVE_DOCUMENTARY_RECORDS_4.csv')
posproc=read_csv(D/'05_results/POSITIVE_INSTITUTIONAL_PROCESSES_3.csv')
orders=read_csv(D/'05_results/ORDER_LEVEL_RESULTS_41_CANONICAL.csv')
source154=read_csv(D/'06_sources/OFFICIAL_UN_SOURCE_REGISTRY_154_EVENTS.csv')

primary=[r for r in orders if r['primary_sample']=='1']
sens=[r for r in orders if r['sensitivity_sample']=='1']

# Table 1
sample=[
 {'component':'Theoretical order-event pairs','count':str(len(legal)*len(univ)),'unit':'pairs'},
 {'component':'±180-day eligible pairs','count':str(len(pairs)),'unit':'pairs'},
 {'component':'Dictionary-screened pairs','count':str(len(review)),'unit':'pairs'},
 {'component':'Unique UN events','count':str(len({r['stage6_event_key'] for r in review})),'unit':'events'},
 {'component':'Official files','count':str(len({r['archive_pdf_filename'] for r in source154})),'unit':'files'},
 {'component':'Sensitivity orders','count':str(len(sens)),'unit':'orders'},
 {'component':'Primary orders','count':str(len(primary)),'unit':'orders'},
]
write_csv(T/'table_1_sample_architecture.csv',sample)

# Table 2
pc=collections.Counter(r['final_link_code'] for r in review)
# Event-level code is maximum linkage class per unique event key, with code 9 lowest priority only if alone.
rank={'9':-1,'0':0,'1':1,'2':2,'3':3}
ev={}
for r in review:
    k=r['stage6_event_key']; c=r['final_link_code']
    if k not in ev or rank[c]>rank[ev[k]]: ev[k]=c
ec=collections.Counter(ev.values())
meanings={'0':'Unrelated / different case','1':'General thematic overlap','2':'Same dispute, no order-specific engagement','3':'Order-specific institutional engagement','9':'Unresolved'}
t2=[{'code':c,'meaning':meanings[c],'pair_level_n':str(pc.get(c,0)),'event_level_n':str(ec.get(c,0))} for c in ['0','1','2','3','9']]
write_csv(T/'table_2_nominal_code_distribution.csv',t2)
write_csv(T/'table_3_positive_documentary_evidence.csv',posdocs)

# Table 4
rr=collections.Counter((r['reporting_requirement'],r['order_specific_engagement_final']) for r in primary)
t4=[{'reporting_requirement':'Present (N=12)','engagement':str(rr[('YES','1')]),'no_engagement':str(rr[('YES','0')])},
    {'reporting_requirement':'Absent (N=12)','engagement':str(rr[('NO','1')]),'no_engagement':str(rr[('NO','0')])}]
write_csv(T/'table_4_reporting_requirement.csv',t4)

# Figure 1
labels=['Theoretical order-event pairs\n(41 × 13,692)','±180-day eligible pairs','Dictionary-screened pairs','Unique UN events','Official files','Sensitivity orders','Primary orders']
vals=[len(legal)*len(univ),len(pairs),len(review),len({r['stage6_event_key'] for r in review}),len({r['archive_pdf_filename'] for r in source154}),len(sens),len(primary)]
fig,ax=plt.subplots(figsize=(8,5.4)); y=range(len(labels)); ax.barh(list(y),vals,color=['0.25','0.38','0.52','0.58','0.63','0.72','0.76'])
ax.set_yticks(list(y),labels);ax.invert_yaxis();ax.set_xscale('log');ax.set_xlabel('Count (log scale)');ax.grid(axis='x',alpha=.25)
for i,v in enumerate(vals):ax.text(v*1.08,i,f'{v:,}',va='center',fontsize=9)
fig.tight_layout();fig.savefig(F/'figure_1_evidence_architecture.png',dpi=300);fig.savefig(F/'figure_1_evidence_architecture.pdf',metadata=PDF_META);plt.close(fig)

# Figure 2
wins=[30,90,180]; broad=[sum(int(r[f'broad_{w}d']) for r in primary)/len(primary)*100 for w in wins]; strict=[sum(int(r[f'order_specific_{w}d']) for r in primary)/len(primary)*100 for w in wins]
fig,ax=plt.subplots(figsize=(7.6,4.5));ax.plot(wins,broad,marker='o',color='0.25',label='Dispute-level attention');ax.plot(wins,strict,marker='s',linestyle='--',color='0.5',label='Order-specific engagement')
ax.set_xticks(wins,[f'{w} days' for w in wins]);ax.set_ylim(0,50);ax.set_ylabel('Share of primary orders (%)');ax.grid(axis='y',alpha=.25);ax.legend(frameon=False,loc='upper left')
for x,yv in zip(wins,broad):ax.text(x,yv+1.5,f'{yv:.1f}%',ha='center',fontsize=9)
for x,yv in zip(wins,strict):ax.text(x,yv-4,f'{yv:.1f}%',ha='center',fontsize=9)
fig.tight_layout();fig.savefig(F/'figure_2_temporal_window_sensitivity.png',dpi=300);fig.savefig(F/'figure_2_temporal_window_sensitivity.pdf',metadata=PDF_META);plt.close(fig)

# Figure 3
labels3=['Binding measures\n(primary)','Dispute-level attention\nwithin 180 days','Order-specific\ninstitutional engagement']; vals3=[len(primary),sum(int(r['broad_180d']) for r in primary),sum(int(r['order_specific_180d']) for r in primary)]
fig,ax=plt.subplots(figsize=(7,4.3));yy=range(3);ax.barh(list(yy),vals3,color=['0.25','0.5','0.68']);ax.set_yticks(list(yy),labels3);ax.invert_yaxis();ax.set_xlim(0,30);ax.set_xlabel('Number of primary orders');ax.grid(axis='x',alpha=.25)
for i,v in enumerate(vals3):ax.text(v+.5,i,f'{v}/24 ({v/24*100:.1f}%)' if v<24 else '24/24 (100%)',va='center',fontsize=9)
fig.tight_layout();fig.savefig(F/'figure_3_conversion_bottleneck.png',dpi=300);fig.savefig(F/'figure_3_conversion_bottleneck.pdf',metadata=PDF_META);plt.close(fig)

# Figure 4
present=[rr[('YES','1')],rr[('YES','0')]]; absent=[rr[('NO','1')],rr[('NO','0')]]
fig,ax=plt.subplots(figsize=(7,4.2));x=[0,1];eng=[present[0],absent[0]];no=[present[1],absent[1]]
ax.bar(x,eng,color='0.25',label='Order-specific engagement');ax.bar(x,no,bottom=eng,color='0.78',edgecolor='0.55',label='No order-specific engagement')
ax.set_xticks(x,['Reporting requirement\npresent (N=12)','No reporting requirement\n(N=12)']);ax.set_ylabel('Number of primary orders');ax.set_ylim(0,13.5);ax.grid(axis='y',alpha=.25);ax.legend(frameon=False,loc='upper center',ncol=2)
for i,(e,n) in enumerate(zip(eng,no)):
    if e: ax.text(i,e/2,str(e),ha='center',va='center',color='white',fontweight='bold')
    if n: ax.text(i,e+n/2,str(n),ha='center',va='center',fontweight='bold')
fig.tight_layout();fig.savefig(F/'figure_4_reporting_requirement.png',dpi=300);fig.savefig(F/'figure_4_reporting_requirement.pdf',metadata=PDF_META);plt.close(fig)

# Figure 5
p_sorted=sorted(primary,key=lambda r:r['order_date'])
labels5=[f"Case No. {r['case_number']} ({r['order_date'][:4]})" for r in p_sorted]
vals5=[int(r['order_specific_180d']) for r in p_sorted]
fig,ax=plt.subplots(figsize=(8,7));yy=list(range(len(labels5)));colors=['black' if v else '0.85' for v in vals5]
ax.barh(yy,[1]*len(yy),color=colors,edgecolor='black',height=.63);ax.set_yticks(yy,labels5,fontsize=8);ax.invert_yaxis();ax.set_xlim(0,1);ax.set_xticks([]);ax.set_xlabel('Order specific institutional engagement verified within 180 days')
ax.set_title('Order level map of verified order specific institutional engagement\n(N=24 primary orders; black = engagement verified)',fontsize=10)
for s in ['top','right','bottom']:ax.spines[s].set_visible(False)
fig.tight_layout();fig.savefig(F/'figure_5_order_level_map.png',dpi=300);fig.savefig(F/'figure_5_order_level_map.pdf',metadata=PDF_META);plt.close(fig)

# Machine-readable summary
summary={
 'legal_decisions':len(legal),'unique_cases':len({r['case_number'] for r in legal}),
 'un_events':len(univ),'theoretical_pairs':len(legal)*len(univ),'eligible_pairs':len(pairs),
 'manual_pairs':len(review),'recall_pairs':len(recall),'positive_documentary_records':len(posdocs),
 'positive_institutional_processes':len(posproc),'primary_orders':len(primary),'sensitivity_orders':len(sens),
 'broad_30d':sum(int(r['broad_30d']) for r in primary),'broad_90d':sum(int(r['broad_90d']) for r in primary),'broad_180d':sum(int(r['broad_180d']) for r in primary),
 'order_specific_30d':sum(int(r['order_specific_30d']) for r in primary),'order_specific_90d':sum(int(r['order_specific_90d']) for r in primary),'order_specific_180d':sum(int(r['order_specific_180d']) for r in primary)
}
with open(ROOT/'outputs/reproduction_summary.json','w',encoding='utf-8') as f:json.dump(summary,f,indent=2,ensure_ascii=False)
print(json.dumps(summary,indent=2,ensure_ascii=False))
