"""Exploratory audit by frozen semantic classifier, never exposed to optimizer.

This is a second proxy, NOT actual Reddit feedback. Protocol recorded before
semantic scoring; no generator or selection changes may follow this audit.
"""
from common import *
from semantic_evaluator import embeddings
from performance_evaluator import MODEL_DIR
import pandas as pd,numpy as np,pickle
def main():
    write_json(ROOT/'configs/independent_generation_audit.json',{'at':now(),'auditor':'frozen E4_semantic','purpose':'post-hoc exploratory proxy disagreement check','optimization_feedback_allowed':False,'generator_tuning_allowed':False,'boundary':'second historical model, not true reader feedback'})
    records=[json.loads(p.read_text(encoding='utf-8')) for p in (ROOT/'results/generator_runs').glob('T*.json')];unique={}
    for r in records:
        for x in r['results']+([r['selected']] if r['selected'] else []):
            draft=x['draft'];k=digest(draft['title']+'\n'+draft['body']);unique[k]={'id':k,'title':draft['title'],'selftext':draft['body']}
    df=pd.DataFrame(unique.values());vectors=embeddings(df)
    with (MODEL_DIR/'E4_semantic.pkl').open('rb') as f:model=pickle.load(f)
    ps=model.predict_proba(vectors)[:,1];scores=dict(zip(df.id,ps));rows=[];selected=[]
    for r in records:
        for x in r['results']:
            k=digest(x['draft']['title']+'\n'+x['draft']['body']);rows.append({'topic_id':r['topic']['id'],'variant':r['variant'],'candidate':x['index'],'optimizer_score':x['performance_score'],'audit_score':float(scores[k]),'constraint_pass':x['constraint_pass'],'negative_pattern_count':sum(d['direction']=='negative' and d['present'] for d in x['diagnostics'])})
        x=r['selected'];selected.append({'topic_id':r['topic']['id'],'variant':r['variant'],'optimizer_score':x['performance_score'] if x else np.nan,'audit_score':float(scores[digest(x['draft']['title']+'\n'+x['draft']['body'])]) if x else np.nan,'abstention':x is None})
    pd.DataFrame(rows).to_csv(ROOT/'results/independent_generation_candidate_audit.csv',index=False);s=pd.DataFrame(selected);s.to_csv(ROOT/'results/independent_generation_selected_audit.csv',index=False)
    rng=np.random.default_rng(SEED);comparisons=[]
    for a,b in [('O2_feedback','O1_resample'),('G4_both','G0_generic'),('G4_both','G4_positive')]:
        aa=s[s.variant.eq(a)].set_index('topic_id');bb=s[s.variant.eq(b)].set_index('topic_id');joined=aa.join(bb,lsuffix='_a',rsuffix='_b')
        for col in ['optimizer_score','audit_score']:
            d=(joined[col+'_a']-joined[col+'_b']).dropna().to_numpy();boot=[rng.choice(d,len(d),replace=True).mean() for _ in range(1000)] if len(d) else []
            comparisons.append({'a':a,'b':b,'metric':col,'n_joint':len(d),'mean_delta':float(d.mean()) if len(d) else None,'ci95_low':float(np.quantile(boot,.025)) if boot else None,'ci95_high':float(np.quantile(boot,.975)) if boot else None})
    pd.DataFrame(comparisons).to_csv(ROOT/'results/independent_generation_audit_comparisons.csv',index=False)
    write_json(ROOT/'results/independent_generation_audit_summary.json',{'at':now(),'unique_generated_texts':len(df),'candidate_score_correlation':pd.DataFrame(rows)[['optimizer_score','audit_score']].corr().iloc[0,1],'all_variants':s.groupby('variant').audit_score.mean().to_dict(),'comparisons':comparisons,'note':'post-hoc exploratory audit; neither model is real audience truth; no generators changed'})
    print('INDEPENDENT GENERATION AUDIT',len(df),flush=True)
if __name__=='__main__':main()
