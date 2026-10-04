"""Predefined, machine-checkable pattern hypotheses with within-type validation.

BH multiple-testing correction on Train; Tune Dev must support same direction.
Patterns are correlations with observational outcomes, not causal writing laws.
"""
from common import *
import pandas as pd,numpy as np,re
from scipy.stats import fisher_exact
FEATURES={
 'concrete_title':('Title contains a number',lambda r:bool(re.search(r'\d',r['title'])),'Mention an existing concrete result in the title; never invent one.'),
 'question_title':('Title asks a question',lambda r:'?' in r['title'],'Consider a precise question when the content type is a discussion/question.'),
 'numbers_early':('Numbers appear in first 300 body characters',lambda r:bool(re.search(r'\d',r['selftext'][:300])),'Put an existing quantitative detail early, preserving its caveats.'),
 'personal_early':('First person appears early',lambda r:bool(re.search(r'\b(I|my|we|our)\b',r['selftext'][:300])),'State the source of experience only when facts establish it.'),
 'code_present':('A fenced code block is present',lambda r:'```' in r['selftext'],'Include actual supplied code only when useful.'),
 'link_present':('An external link is present',lambda r:bool(re.search(r'https?://',r['selftext'])),'Provide an available source link when relevant.'),
 'multi_paragraph':('At least four paragraphs',lambda r:len(re.split(r'\n\s*\n',r['selftext']))>=4,'Break the supplied material into useful paragraphs.'),
 'bullet_present':('A bullet list is present',lambda r:bool(re.search(r'(?m)^\s*[-*]\s+',r['selftext'])),'Use a concise list for comparable facts.'),
 'caveat_present':('A caveat is stated',lambda r:bool(re.search(r'\b(limitation|however|caveat|not necessarily|depends|only tested|small sample)\b',r['selftext'],re.I)),'Preserve or clarify existing limitations.'),
 'hype_title':('Title has hype words',lambda r:bool(re.search(r'\b(insane|revolutionary|game.?changer|shocking|best ever|mind.?blowing)\b',r['title'],re.I)),'Use a concrete title and avoid unsupported superlatives.')}
def flags(df):return pd.DataFrame({k:[int(v[1](r)) for r in df.to_dict('records')] for k,v in FEATURES.items()},index=df.index)
def estimate(g,f):
    y=g.label.to_numpy();a=int(((f==1)&(y==1)).sum());b=int(((f==1)&(y==0)).sum());c=int(((f==0)&(y==1)).sum());d=int(((f==0)&(y==0)).sum())
    _,p=fisher_exact([[a,b],[c,d]]);odds=((a+.5)*(d+.5))/((b+.5)*(c+.5))
    return {'n':len(g),'with_pattern':a+b,'without_pattern':c+d,'high_with':a,'high_without':c,'odds_ratio_smoothed':odds,'p_value':p,'table':[[a,b],[c,d]]}
def main():
    train=pd.read_parquet(ROOT/'data/splits/train.parquet');tune=pd.read_parquet(ROOT/'data/splits/tune_dev.parquet');ft=flags(train);fd=flags(tune);rows=[]
    for typ,g in train.groupby('content_type'):
        for name in FEATURES:
            est=estimate(g,ft.loc[g.index,name].to_numpy());dev=tune[tune.content_type==typ];de=estimate(dev,fd.loc[dev.index,name].to_numpy());rows.append({'pattern_id':name,'content_type':typ,**est,'dev_n':de['n'],'dev_odds_ratio':de['odds_ratio_smoothed'],'dev_p_value':de['p_value'],'dev_with_pattern':de['with_pattern'],'dev_without_pattern':de['without_pattern']})
    order=sorted(range(len(rows)),key=lambda i:rows[i]['p_value']);qs=np.ones(len(rows));running=1
    for rank in range(len(order),0,-1):
        ix=order[rank-1];running=min(running,rows[ix]['p_value']*len(order)/rank);qs[ix]=running
    cards=[]
    for i,r in enumerate(rows):
        r['train_bh_q']=float(qs[i]);r['validated']=bool(qs[i]<=.1 and min(r['with_pattern'],r['without_pattern'])>=15 and min(r['dev_with_pattern'],r['dev_without_pattern'])>=5 and (r['odds_ratio_smoothed']-1)*(r['dev_odds_ratio']-1)>0)
        if r['validated']:
            typ=r['content_type'];name=r['pattern_id'];positive=r['odds_ratio_smoothed']>1;g=train[train.content_type==typ]
            match=ft.loc[g.index,name].eq(1);support=g[match&g.label.eq(1 if positive else 0)].head(3);counter=g[match&g.label.eq(0 if positive else 1)].head(2)
            cards.append({'id':name+'__'+typ,'pattern':FEATURES[name][0],'direction':'positive' if positive else 'negative','applicable_type':typ,'train_evidence':r,'counterexample_ids':counter.id.tolist(),'support_ids':support.id.tolist(),'suggested_action':FEATURES[name][2] if positive else 'Do not force this feature. '+FEATURES[name][2],'limitations':'Observational association; lexical topic and author confounding remain; avoid causal claims.'})
    pd.DataFrame(rows).to_csv(ROOT/'results/pattern_statistics.csv',index=False)
    for direction in ['positive','negative']:write_json(ROOT/'patterns'/f'{direction}_patterns.json',[c for c in cards if c['direction']==direction])
    write_json(ROOT/'patterns/all_patterns.json',cards)
    print('PATTERNS validated',len(cards),'positive',sum(c['direction']=='positive' for c in cards),'negative',sum(c['direction']=='negative' for c in cards),flush=True)
if __name__=='__main__':main()
