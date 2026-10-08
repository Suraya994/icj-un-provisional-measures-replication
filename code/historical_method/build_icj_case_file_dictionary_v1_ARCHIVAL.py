#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json
from pathlib import Path

# Dava-merkezli tarama terimleri. Tek başına hiçbir terim takip kodu 3 üretmez.
M = {
"126": ("democratic republic of the congo|drc|congo-kinshasa|rwanda", "the situation concerning the democratic republic of the congo|great lakes region", "S/RES/1417|S/RES/1445", "international criminal tribunal for rwanda|ictr|republic of the congo|congo-brazzaville"),
"128": ("avena|mexican nationals|vienna convention on consular relations", "", "A/RES/73/257", "election of members of the international court of justice"),
"129": ("certain criminal proceedings in france|sassou nguesso|meaux|universal jurisdiction", "", "", "democratic republic of the congo|congo-kinshasa|rwanda|ictr"),
"135": ("pulp mills|river uruguay|botnia|fray bentos|caru", "", "", "uruguay round|unrelated argentina or uruguay country resolutions"),
"139": ("avena|medellin|mexican nationals|judgment of 31 march 2004", "", "A/RES/73/257", "election of members of the international court of justice"),
"140": ("georgia|russian federation|south ossetia|abkhazia|cerd", "the situation in georgia", "S/2008/596", "generic russian federation references|icj elections"),
"144": ("hissene habre|prosecute or extradite|belgium|senegal|convention against torture", "", "", "generic senegal or belgium references"),
"150": ("isla portillos|harbour head|san juan river|costa rica|nicaragua|cano", "", "", "generic nicaragua or costa rica resolutions"),
"151": ("preah vihear|provisional demilitarized zone|cambodia|thailand", "", "", "generic cambodia or thailand development resolutions"),
"152": ("construction of a road|route 1856|san juan river|costa rica|nicaragua", "", "", "generic nicaragua or costa rica resolutions"),
"156": ("timor-leste|australia|seized documents|collaery|asi o", "the situation in timor-leste", "", "unmit or timor-leste events unrelated to seized legal documents"),
"163": ("equatorial guinea|france|42 avenue foch|teodoro nguema obiang|diplomatic premises", "", "", "return of confiscated property case 184|generic equatorial guinea resolutions"),
"166": ("ukraine|russian federation|crimea|crimean tatars|mejlis|cerd|terrorism financing", "the situation in ukraine", "S/2014/264", "icj elections|unrelated russian federation agenda"),
"168": ("jadhav|kulbhushan|india|pakistan|vienna convention on consular relations", "the india-pakistan question", "", "kashmir events without jadhav or consular link"),
"172": ("qatar|united arab emirates|uae|gulf blockade|cerd", "", "", "generic qatar-hosted meetings|unrelated uae resolutions"),
"178": ("myanmar|gambia|rohingya|rakhine|genocide convention", "the situation in myanmar", "A/RES/74/246", "other myanmar matters without rohingya or genocide nexus"),
"180": ("armenia|azerbaijan|nagorno-karabakh|lachin corridor|cerd", "maintenance of international peace and security", "S/2022/688", "generic armenia or azerbaijan references unrelated to nagorno-karabakh"),
"181": ("azerbaijan|armenia|nagorno-karabakh|landmines|cerd", "maintenance of international peace and security", "S/2022/688", "generic armenia or azerbaijan references unrelated to bilateral dispute"),
"182": ("ukraine|russian federation|genocide convention|special military operation|donetsk|luhansk", "the situation in ukraine", "S/2022/155", "icj elections|other russian federation matters|crimea-only events without case nexus"),
"183": ("germany|italy|jurisdictional immunities|state-owned property|villa vigoni", "", "", "generic second world war commemoration or reparations"),
"184": ("equatorial guinea|france|42 avenue foch|confiscated property|uncac|convention against corruption", "", "", "immunities and criminal proceedings case 163|generic equatorial guinea resolutions"),
"188": ("syria|canada|netherlands|torture|cidtp|convention against torture", "the situation in the middle east|the situation in syria", "", "syria events without torture or case-specific nexus"),
"171": ("guyana|venezuela|essequibo|guayana esequiba|arbitral award of 3 october 1899", "maintenance of international peace and security", "", "generic guyana or venezuela references unrelated to essequibo"),
"192": ("south africa|israel|gaza|genocide convention|rafah|palestinian group", "the situation in the middle east including the palestinian question", "S/RES/2712|S/RES/2720|S/RES/2728|S/RES/2735", "occupied palestinian territory advisory opinion|nicaragua v germany case 193|icj elections"),
"193": ("nicaragua|germany|gaza|military assistance|unrwa|genocide convention", "the situation in the middle east including the palestinian question", "S/RES/2728", "south africa v israel case 192|occupied palestinian territory advisory opinion"),
"194": ("mexico|ecuador|embassy in quito|jorge glas|diplomatic premises|vienna convention on diplomatic relations", "", "", "generic mexico or ecuador resolutions"),
"197": ("sudan|united arab emirates|uae|masalit|darfur|genocide convention|rapid support forces|rsf", "reports of the secretary-general on the sudan and south sudan|the situation in the sudan", "S/RES/2736", "south sudan-only events|generic uae references|other genocide convention cases"),
}
P5 = {"china", "france", "russian federation", "united kingdom", "united states of america"}

def main(root: Path, output: Path):
    src = root / "data/analysis/icj_case_party_issue_lexicon_v4.csv"
    rows = list(csv.DictReader(src.open(encoding="utf-8-sig")))
    assert len(rows) == 27 and set(M) == {r["case_number"] for r in rows}
    out=[]
    for r in rows:
        terms, agendas, symbols, exclusions = M[r["case_number"]]
        out.append({
            "case_number":r["case_number"], "case_title":r["case_title"],
            "applicant":r["applicant"], "respondent":r["respondent"],
            "applicant_aliases":r["applicant_aliases"], "respondent_aliases":r["respondent_aliases"],
            "respondent_p5":int(r["respondent_normalized"] in P5),
            "case_distinctive_terms":terms, "official_sc_agenda_titles":agendas,
            "known_relevant_un_symbols":symbols, "exclusion_terms_or_files":exclusions,
            "p5_protected_ally":"PENDING_SUBSTANTIVE_CODING",
            "dictionary_status":"CURATED_V1_REQUIRES_SECOND_REVIEW",
            "source_lexicon":"data/analysis/icj_case_party_issue_lexicon_v4.csv",
        })
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    print(json.dumps({"rows":len(out),"respondent_p5":sum(x["respondent_p5"] for x in out)},ensure_ascii=False))

if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("--root",type=Path,required=True); p.add_argument("--output",type=Path,required=True); a=p.parse_args(); main(a.root,a.output)
