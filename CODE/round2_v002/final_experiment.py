"""Freeze without external Selection, then independent held-out comparisons."""
from generation import *
from collections import Counter

def freeze():
    file=LOOP/'configs/generator_freeze_v002.json'
    if file.exists():return read(file)
    rule=read(CONTRACT)['design']['selection_rule'];summary={}
    for v in ['V0','V1','V2','O1']:
        records=[read(LOOP/'results/generator_runs'/f'{bid}_{v}_v002.json') for bid in ['S03','S04']]
        acceptable=[r for r in records if r['selected'] and 90<=r['selected']['quality']['body_words']<=150 and r['selected']['draft']['body'].count('?')<=2]
        summary[v]={'qualified_focus_count':len(acceptable),'n':2,'selected_count':sum(bool(r['selected']) for r in records),'selection_files':[str(LOOP/'results/generator_runs'/f'{bid}_{v}_v002.json') for bid in ['S03','S04']]}
    order=['V0','V1','V2','O1'];chosen=max(order,key=lambda v:(summary[v]['qualified_focus_count'],-order.index(v)))
    record={'at':now(),'selected_product':chosen,'selection_rule':rule,'selection_summary':summary,'external_selection_used':False,'feedback_enabled':False,'selection_n_small':True,'contract_path':CONTRACT.name,'contract_sha256':sha(CONTRACT),'code_hashes':{p.name:sha(p) for p in (LOOP/'code').glob('*.py')},'model_prices_hash':sha(LOOP/'configs/model_prices_v002.json'),'evaluator_freeze_hash':sha(LOOP/'configs/evaluator_freeze_v002.json'),'source_assignment_hash':sha(LOOP/'inputs/source_assignment_v002.json'),'comparisons':['V1_vs_V0','V2_vs_V1','O1_vs_V2'],'final_topics':12,'no_tuning_after_this_point':True}
    write(file,record);event('freeze','Product fixed using Selection only, before Final source preparation',{'product':chosen,'selection_summary':summary,'external_used':False});return record

def verify_freeze():
    f=read(LOOP/'configs/generator_freeze_v002.json')
    for name,h in f['code_hashes'].items():
        if sha(LOOP/'code'/name)!=h:raise RuntimeError('Frozen code changed: '+name)
    if sha(CONTRACT)!=f['contract_sha256']:raise RuntimeError('Frozen contract changed')
    if sha(LOOP/'inputs/source_assignment_v002.json')!=f['source_assignment_hash']:raise RuntimeError('Final assignment changed')

def final_eval():
    verify_freeze();f=read(LOOP/'configs/generator_freeze_v002.json')
    if not read(LOOP/'results/evaluator_admission_v002.json')['external']['admitted']:raise RuntimeError('External judge did not qualify')
    out=LOOP/'results/final_comparisons';out.mkdir(exist_ok=True)
    for item in read(LOOP/'inputs/source_assignment_v002.json'):
        if item['split']!='final':continue
        bid=item['brief_id'];b=read(LOOP/'evals'/f'brief_{bid}_v002.json')
        for newer,older in [('V1','V0'),('V2','V1'),('O1','V2')]:
            target=out/f'{bid}_{newer}_vs_{older}_v002.json'
            if target.exists():continue
            A=read(LOOP/'results/generator_runs'/f'{bid}_{older}_v002.json')['selected'];B=read(LOOP/'results/generator_runs'/f'{bid}_{newer}_v002.json')['selected']
            if not A or not B:record={'outcome':'Failure','reason':'At least one method has no qualified candidate','older_available':bool(A),'newer_available':bool(B)}
            elif A['draft']==B['draft']:record={'outcome':'Tie','reason':'Exact identity due to original retention; deterministic identity, not a judge call','dimensions':{d:'Tie' for d in DIMENSIONS},'identity_check':True}
            else:
                try:
                    c=compare(b,A['draft'],B['draft'],EXTERNAL,'judge_final:'+bid+':'+newer+'_vs_'+older,'final');pred=c['combined']['overall']
                    record={'outcome':{'A':'Loss','B':'Win','Tie':'Tie','Uncertain':'Uncertain'}[pred],'dimensions':c['combined'],'judge':c,'identity_check':False}
                except (RuntimeError,ValueError,KeyError) as exc:
                    record={'outcome':'Failure','reason':'Judge/schema failure: '+type(exc).__name__}
            record.update(brief_id=bid,comparison=newer+'_vs_'+older,older=older,newer=newer,at=now());write(target,record)
    summaries={}
    for comparison in f['comparisons']:
        rs=[read(p) for p in out.glob('*_'+comparison+'_v002.json')];counts=Counter(x['outcome'] for x in rs);w,l=counts['Win'],counts['Loss'];n=len(rs);d=w+l
        if d:
            z=1.96;center=(w/d+z*z/(2*d))/(1+z*z/d);half=z*math.sqrt((w/d)*(1-w/d)/d+z*z/(4*d*d))/(1+z*z/d);interval=[center-half,center+half]
        else:interval=None
        summaries[comparison]={'n':n,'counts':{k:counts[k] for k in ['Win','Loss','Tie','Uncertain','Failure']},'decisive_win_rate':w/d if d else None,'decisive_coverage':d/n if n else 0,'uncertain_rate':counts['Uncertain']/n if n else 0,'tie_rate':counts['Tie']/n if n else 0,'failure_rate':counts['Failure']/n if n else 0,'decisive_win_rate_wilson_95':interval,'identity_ties':sum(x.get('identity_check',False) for x in rs),'conditional_interval_not_all_topic_success_probability':True}
    write(LOOP/'results/final_summary_v002.json',{'at':now(),'selected_product_before_final':f['selected_product'],'comparisons':summaries,'evidence_boundary':'Offline independent model preference; no real posting or real virality outcomes; 12 topics per comparison, exploratory small-sample intervals','human_final_pending':True,'costs':{'prior':costs()[0],'round':costs()[1],'total':sum(costs())}})
    event('final','Independent comparisons complete; product not changed by Final results',{'summary':str(LOOP/'results/final_summary_v002.json'),'human_final_pending':True})

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('action',choices=['freeze','evaluate']);a=p.parse_args()
    if a.action=='freeze':freeze()
    else:final_eval()
