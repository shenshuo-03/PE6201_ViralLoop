"""Real naturalness audit, review artifact and genuine response collection."""
from evaluator import *
def main():
    cases=read(LOOP/'results/naturalness_previews_v002.json');checked=[]
    for row in cases:
        b=row['brief'];p=row['draft'];file=LOOP/'results'/f'naturalness_quality_{b["id"]}_v002.json'
        if file.exists():q=read(file)
        else:
            js,u=quality(b,[p],'naturalness:'+b['id'],'naturalness');q={'judgment':js[0],'usage':u};write(file,q)
        text=p['title']+' '+p['body']
        manual_flags=[]
        if re.search(r"\b(?:I've found|I have found|I haven't located|I tested|I've tested|my tests|my measurements|I measured)\b",text,re.I):manual_flags.append('First-person source-author research/testing cannot be attributed to reader speaker')
        if '2025' in b.get('source_date','') and re.search(r'\brecent\b',text,re.I) and '2025' not in text:manual_flags.append('2025 archive cannot be described as a recent test in 2026')
        if manual_flags:
            q['judgment']['hard_pass']=False;q['judgment']['unsupported_claims']+=manual_flags
        if not q['judgment']['hard_pass']:
            repair=LOOP/'results'/f'naturalness_repair_{b["id"]}_v002.json'
            if repair.exists():fixed=read(repair)
            else:
                prompt=BASE_PROMPT+STRONG+'Produce exactly ONE draft. Repair factual/identity issues in the current draft; preserve real source facts, do not fabricate new evidence.\n'+json.dumps({'brief':b,'source':read(LOOP/'sources'/f'{b["id"]}_v002.json'),'current_draft':p,'audit':q['judgment']},ensure_ascii=False)
                ans=complete(prompt,GEN,'naturalness:'+b['id']+':fact_repair',1100,'naturalness',.2);fixed={'draft':ans['value']['drafts'][0],'usage':ans['usage']};write(repair,fixed)
            p=fixed['draft'];js,u=quality(b,[p],'naturalness:'+b['id']+':repaired','naturalness');q={'judgment':js[0],'usage':u};write(LOOP/'results'/f'naturalness_quality_repaired_{b["id"]}_v002.json',q)
            event('naturalness','fact repair made before human gate; original preserved',{'id':b['id'],'pass':q['judgment']['hard_pass']})
        checked.append({'brief':b,'draft':p,'quality':q['judgment'],'human_accepted':False})
    write(LOOP/'results/naturalness_checked_v002.json',checked)
    automatic=all(x['quality']['hard_pass'] for x in checked) and sum(x['quality']['quality_pass'] for x in checked)>=5
    write(LOOP/'results/naturalness_gate_v002.json',{'automatic_pass':automatic,'hard_pass_count':sum(x['quality']['hard_pass'] for x in checked),'quality_pass_count':sum(x['quality']['quality_pass'] for x in checked),'n':len(checked),'human_pass':False,'formal_generator_stage_allowed':False,'rule':'All hard pass and at least 5/6 fit,specificity,information>=3; real user acceptance required','source_based_not_human_ground_truth':True})
    # One per type: these are a usability gate, never formal final human results.
    chosen=[next(x for x in checked if x['brief']['id']==bid) for bid in ['D01','D03','S01']]
    prepared=[]
    for row in chosen:
        b=row['brief'];p=row['draft'];out=LOOP/'results'/f'naturalness_review_{b["id"]}_v002.json'
        if out.exists():item=read(out)
        else:
            item={'id':b['id'],'type':b['content_type'],'brief_goal':b['problem_or_goal'],'source_url':b['source_url'],'source_date':b['source_date'],'title_en':p['title'],'body_en':p['body'],'translation_note':'The reviewer was originally shown a Chinese translation of this draft. This submission package is English-only, so the English draft is presented directly.'}
            write(out,item)
        prepared.append(item)
    write(LOOP/'evals/naturalness_user_review_v002.json',prepared)
    doc='# Round 2: three real-material samples for naturalness acceptance\n\nThis is not a formal blind review. Judge only whether each sample reads like something worth posting in a real community, and name the one that most needs work. The sources are archived 2025 user reports, not your own first-hand testing.\n'
    for i,x in enumerate(prepared,1):
        doc+=f'\n## Sample {i}: {x["title_en"]}\n\nType: {x["type"]}; source date: {x["source_date"]}\n\nTask: {x["brief_goal"]}\n\n{x["body_en"]}\n\n[Source post]({x["source_url"]})\n'
    doc+='\n## Please respond\n\nAre these three natural, concrete and worth posting? If not, just name the sample number and the most obvious problem. Do not accommodate the system merely because it produced something. Until acceptance is received, no formal generation comparison or Final is started.\n'
    (LOOP/'three_real_material_samples_for_acceptance.md').write_text(doc,encoding='utf-8')
    write(LOOP/'results/cost_summary_v002.json',{'prior_usd':costs()[0],'round_usd':costs()[1],'total_usd':sum(costs()),'cap_usd':5,'round_cap_usd':2,'calls':len(rows(LEDGER))})
    event('naturalness','review package ready; gate pending real user',{'automatic_pass':automatic,'numeric_translation_checks':'not applicable: English-only package'})
if __name__=='__main__':main()
