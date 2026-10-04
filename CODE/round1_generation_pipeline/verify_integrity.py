"""Meaningful integrity checks of frozen evidence, leakage and budget boundaries."""
from common import *
from performance_evaluator import inputs
from quality_evaluator import hard_rules
from topic_bank import TOPICS
from model_api import spent
import pandas as pd
def main():
    posts=pd.read_parquet(ROOT/'data/processed_posts.parquet');checks={}
    checks['unique_ids']=posts.id.nunique()==len(posts)
    checks['fixed_observation_window']=bool(posts.observation_age_hours.between(36,38).all())
    checks['no_result_input']=not bool(set(inputs(posts).columns)&{'raw_score','score','num_comments','label','observed_at','observation_age_hours','performance_percentile'})
    checks['duplicate_groups_do_not_cross']=posts.groupby('duplicate_group_id').split.nunique().max()==1
    chronological=posts.groupby('split').created_at.agg(['min','max'])
    order=['train','tune_dev','selection_dev','final_test'];checks['time_disjoint']=all(chronological.loc[a,'max']<chronological.loc[b,'min'] for a,b in zip(order,order[1:]))
    checks['budget_below_5']=spent()<=5
    examples=ROOT/'results/generator_runs';runs=[json.loads(p.read_text(encoding='utf-8')) for p in examples.glob('T*.json')]
    checks['all_80_final_topic_variant_cells']=len(runs)==80
    checks['all_180_final_candidates']=sum(len(r['results']) for r in runs)==180
    train_ids=set(posts[posts.split.eq('train')].id)
    checks['retrieval_train_only']=all(set(r.get('retrieved_ids',[]))<=train_ids for r in runs)
    keys=set(pd.read_csv(ROOT/'results/judge_classifier/final_test_ids.csv').id)
    checks['judge_same_80_ids']=all(set(pd.read_csv(ROOT/'results/judge_classifier'/f'final_test_{variant}.csv').id)==keys for variant in ['E5a_zero_shot','E5b_few_shot','E5c_retrieval']) and len(keys)==80
    facts=TOPICS[0];valid={'title':'Hypothetical VRAM checklist','body':('This hypothetical setup uses a 12 GB GPU. Fact F1 supplies the capacity. Fact F2 says to separate model weights, KV cache and other allocations. Fact F3 confirms no actual model or runtime was tested. The checklist therefore asks for those allocations to be recorded separately before deciding whether the setup can run a chosen model. It does not give a measured result or promise a particular model will fit. Keep the test conditions and missing evidence visible rather than claiming a successful benchmark.'),'fact_refs':['F1','F2','F3']}
    checks['valid_fact_refs_not_numbers']=hard_rules(valid,facts,[])['hard_rule_pass']
    invalid=dict(valid,body=valid['body'].replace('12 GB','99 GB'));checks['unsupported_number_rejected']=not hard_rules(invalid,facts,[])['hard_rule_pass']
    checks['final_test_markers']=all((ROOT/p).exists() for p in ['results/FINAL_TEST_STARTED.json','results/FINAL_TEST_COMPLETED.json','results/GENERATOR_FINAL_STARTED.json','results/GENERATOR_FINAL_COMPLETED.json','results/judge_classifier/FINAL_COMPLETED.json'])
    write_json(ROOT/'results/integrity_checks.json',{'at':now(),'checks':{k:bool(v) for k,v in checks.items()},'all_passed':bool(all(checks.values()))})
    print('INTEGRITY',checks,flush=True)
    if not all(checks.values()):raise RuntimeError('Integrity check failed')
if __name__=='__main__':main()
