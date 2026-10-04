"""Resumable real generator experiments; checkpoints, grouped selection, test lock.

All methods judged by a separate model. Optimizer sees local scores/patterns only;
independent judge reasons and scores are NOT fed into revision prompts.
"""
from common import *
from generator import *
from quality_evaluator import hard_rules,judge_batch
from performance_evaluator import score_posts
from model_api import entries,spent
import pandas as pd,numpy as np, argparse,time
RUNS=ROOT/'results/generator_runs';RUNS.mkdir(exist_ok=True)
def assess(drafts,brief,examples,tag):
    scores=score_posts(drafts);js,usage=judge_batch(drafts,brief,tag)
    results=[]
    for i,(draft,score,j) in enumerate(zip(drafts,scores,js)):
        rule=hard_rules(draft,brief,examples);passed=rule['hard_rule_pass'] and j['quality_constraint_pass']
        results.append({'index':i,'draft':draft,'performance_score':score,'quality':j,'rules':rule,'constraint_pass':bool(passed),'diagnostics':diagnostics(draft,brief['content_type'])})
    valid=[x for x in results if x['constraint_pass']]
    selected=max(valid,key=lambda x:x['performance_score']) if valid else None
    return results,selected,usage
def run_topic(brief):
    records=[];retriever=Retriever()
    for variant in VARIANTS:
        p=RUNS/f"{brief['id']}__{variant}.json"
        if p.exists():record=json.loads(p.read_text(encoding='utf-8'))
        else:
            tag=f"{brief['split']}:{brief['id']}:{variant}"
            drafts,examples,cards,usage,prompt=generate(brief,variant,retriever,tag)
            results,selected,judge_usage=assess(drafts,brief,examples,tag+':quality')
            record={'at':now(),'topic':brief,'variant':variant,'generation_usage':usage,'judge_usage':judge_usage,'retrieved_ids':[x['id'] for x in examples],'pattern_ids':[x['id'] for x in cards],'prompt_sha256':digest(prompt),'results':results,'selected':selected,'abstention':selected is None}
            write_json(p,record)
        records.append(record)
        print('GEN',brief['id'],variant,'qualified',sum(x['constraint_pass'] for x in record['results']),'score',round(record['selected']['performance_score'],3) if record['selected'] else 'ABSTAIN','budget',round(spent(),4),flush=True)
    base=[r for r in records if r['variant']=='G4_both'][0]
    # Every topic retains a parent; if all original drafts fail, edits may repair it.
    parent=base['selected'] or max(base['results'],key=lambda x:x['performance_score'])
    feedback={'performance_score':parent['performance_score'],'diagnostics':parent['diagnostics'],'boundary':'relative classifier score, not causal or real virality probability'}
    for mode in ['O1_resample','O2_feedback']:
        p=RUNS/f"{brief['id']}__{mode}.json"
        if p.exists():record=json.loads(p.read_text(encoding='utf-8'))
        else:
            tag=f"{brief['split']}:{brief['id']}:{mode}"
            drafts,examples,usage,prompt=optimize(parent['draft'],brief,retriever,mode,feedback,tag)
            results,selected,judge_usage=assess(drafts,brief,examples,tag+':quality')
            choices=[x for x in results if x['constraint_pass']]+([parent] if parent['constraint_pass'] else [])
            selected=max(choices,key=lambda x:x['performance_score']) if choices else None
            record={'at':now(),'topic':brief,'variant':mode,'generation_usage':usage,'judge_usage':judge_usage,'results':results,'selected':selected,'parent':parent,'parent_variant':'G4_both','abstention':selected is None,'original_retained':bool(selected is parent),'prompt_sha256':digest(prompt),'feedback_sent':feedback if mode=='O2_feedback' else None}
            write_json(p,record)
        records.append(record);print('OPT',brief['id'],mode,'score',round(record['selected']['performance_score'],3) if record['selected'] else 'ABSTAIN','budget',round(spent(),4),flush=True)
    return records

def summarize():
    records=[json.loads(p.read_text(encoding='utf-8')) for p in RUNS.glob('*.json')];rows=[];candidate_rows=[];failures=[]
    for r in records:
        selected=r['selected'];topic=r['topic'];gen=r['generation_usage'];judge=r['judge_usage']
        # Exact cost belongs to a call; no duplicated full charge per candidate.
        row={'topic_id':topic['id'],'partition':topic['split'],'variant':r['variant'],'content_type':topic['content_type'],'candidate_count':len(r['results']),'qualified_count':sum(x['constraint_pass'] for x in r['results']),'abstention':r['abstention'],'selected_performance':selected['performance_score'] if selected else np.nan,'selected_quality':selected['quality']['quality_mean'] if selected else np.nan,'selected_clickbait':selected['quality']['clickbait'] if selected else np.nan,'generation_cost_usd':gen.get('actual_cost_usd'),'judge_cost_usd':judge.get('actual_cost_usd'),'generation_budget_charge_usd':gen['budget_charge_usd'],'judge_budget_charge_usd':judge['budget_charge_usd'],'generation_input_tokens':gen.get('input_tokens'),'generation_output_tokens':gen.get('output_tokens'),'generation_latency_seconds':gen['latency_seconds'],'judge_latency_seconds':judge['latency_seconds'],'original_retained':r.get('original_retained',False)}
        rows.append(row)
        for x in r['results']:
            candidate_rows.append({'topic_id':topic['id'],'partition':topic['split'],'variant':r['variant'],'candidate':x['index'],'performance_score':x['performance_score'],'quality_mean':x['quality']['quality_mean'],'clickbait':x['quality']['clickbait'],'constraint_pass':x['constraint_pass'],'hard_rule_pass':x['rules']['hard_rule_pass'],'judge_hard_pass':x['quality']['judge_hard_pass']})
            if not x['constraint_pass']:failures.append({'topic_id':topic['id'],'variant':r['variant'],'candidate':x['index'],'rules':json.dumps(x['rules']['hard_rule_failures']),'judge':json.dumps(x['quality'],ensure_ascii=False)})
    pd.DataFrame(rows).to_csv(ROOT/'results/generator_results.csv',index=False)
    pd.DataFrame(candidate_rows).to_csv(ROOT/'results/generator_candidate_results.csv',index=False)
    pd.DataFrame(failures).to_csv(ROOT/'results/failure_cases.csv',index=False)
    frame=pd.DataFrame(rows)
    if len(frame):
        summary=frame.groupby(['partition','variant']).agg(topics=('topic_id','size'),coverage=('abstention',lambda x:1-x.mean()),mean_selected_performance=('selected_performance','mean'),mean_selected_quality=('selected_quality','mean'),mean_selected_clickbait=('selected_clickbait','mean'),generation_budget_charge_usd=('generation_budget_charge_usd','sum'),judge_budget_charge_usd=('judge_budget_charge_usd','sum'),mean_generation_latency=('generation_latency_seconds','mean')).reset_index();summary.to_csv(ROOT/'results/generator_summary.csv',index=False)
        final=frame[frame.partition=='final_test'];rng=np.random.default_rng(SEED);comparisons=[]
        for a,b in [('G1_prompt','G0_generic'),('G2_fewshot_planning','G1_prompt'),('G3_rag','G1_prompt'),('G4_positive','G3_rag'),('G4_both','G4_positive'),('O2_feedback','O1_resample')]:
            aa=final[final.variant==a].set_index('topic_id');bb=final[final.variant==b].set_index('topic_id')
            joint=aa.join(bb,lsuffix='_a',rsuffix='_b')
            for metric_name in ['selected_performance','selected_quality','selected_clickbait']:
                d=(joint[metric_name+'_a']-joint[metric_name+'_b']).dropna().to_numpy()
                if not len(d):continue
                boots=[float(rng.choice(d,len(d),replace=True).mean()) for _ in range(1000)]
                comparisons.append({'a':a,'b':b,'metric':metric_name,'paired_topics':len(d),'mean_delta':float(d.mean()),'ci95_low':float(np.quantile(boots,.025)),'ci95_high':float(np.quantile(boots,.975)),'interpretation':'exploratory topic bootstrap, excludes joint abstentions; report coverage separately'})
        pd.DataFrame(comparisons).to_csv(ROOT/'results/generator_paired_comparisons.csv',index=False)
    write_json(ROOT/'results/cost_summary.json',{'at':now(),'hard_cap_usd':5,'ledger_calls':len(entries()),'budget_accounted_usd':spent(),'known_actual_cost_usd':sum(float(x.get('actual_cost_usd') or 0) for x in entries()),'unknown_charge_calls':sum(x.get('actual_cost_usd') is None for x in entries()),'note':'unknown request/embedding charges counted conservatively at reserved upper bound; not falsely reported as exact cost'})

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--stage',choices=['tune_dev','selection_dev','final_test'],default='tune_dev');args=ap.parse_args()
    bank=json.loads((ROOT/'configs/topic_bank.json').read_text(encoding='utf-8'))
    if args.stage=='final_test':
        marker=ROOT/'results/GENERATOR_FINAL_STARTED.json'
        if not (ROOT/'configs/generator_freeze.json').exists():raise RuntimeError('Generator protocol must be frozen')
        if not marker.exists():write_json(marker,{'at':now(),'config_sha256':digest((ROOT/'configs/generator_freeze.json').read_text(encoding='utf-8')),'resumption':'existing immutable topics/results are skipped; only incomplete calls resumed'})
    for brief in [x for x in bank if x['split']==args.stage]:run_topic(brief);summarize()
    summarize()
    if args.stage=='final_test':write_json(ROOT/'results/GENERATOR_FINAL_COMPLETED.json',{'at':now(),'topics':10,'tuned_after_test':False})
if __name__=='__main__':main()
