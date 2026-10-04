"""Frozen evaluator ladder: development selection, separate one-shot final test.

Metadata-only explicitly excludes text length; structural context is separately
named. LSA is a latent text baseline, NOT a pretrained semantic/reward model.
"""
from common import *
import numpy as np, pandas as pd, pickle, time, argparse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler,OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import precision_recall_fscore_support,average_precision_score,roc_auc_score,brier_score_loss,log_loss,accuracy_score
from sklearn.decomposition import TruncatedSVD
from scipy import sparse
MODEL_DIR=ROOT/'results/models';MODEL_DIR.mkdir(exist_ok=True)

def inputs(df):
    x=pd.DataFrame(index=df.index)
    dt=pd.to_datetime(df.created_at,unit='s',utc=True)
    x['text']=df.title.fillna('')+'\n'+df.selftext.fillna('')
    x['content_type']=df.content_type;x['weekday']=dt.dt.weekday.astype(str);x['hour']=dt.dt.hour.astype(str)
    x['year_day']=dt.dt.dayofyear
    for k in ['author_prior_post_count','author_prior_median_score','author_prior_missing']:x[k]=df[k]
    x['title_length']=df.title.str.len();x['body_length']=df.selftext.str.len()
    x['code_block']=df.selftext.str.contains('```',regex=False).astype(int)
    x['external_link']=df.selftext.str.contains(r'https?://',regex=True).astype(int)
    x['paragraphs']=df.selftext.str.count(r'\n\s*\n')+1
    x['question_title']=df.title.str.contains('?',regex=False).astype(int)
    x['digits']=df.selftext.str.count(r'\d')
    return x

def make_model(kind,C=1):
    parts=[]
    meta_num=['year_day','author_prior_post_count','author_prior_median_score','author_prior_missing']
    structure=['title_length','body_length','code_block','external_link','paragraphs','question_title','digits']
    if kind in ['E1_context_only','E1b_context_structure','E3_text_context']:
        numeric=meta_num+(structure if kind!='E1_context_only' else [])
        parts+=[('categorical',OneHotEncoder(handle_unknown='ignore'),['content_type','weekday','hour']),('numeric',Pipeline([('impute',SimpleImputer()),('scale',StandardScaler())]),numeric)]
    if kind in ['E2_tfidf','E3_text_context']:
        parts.append(('text',TfidfVectorizer(ngram_range=(1,2),min_df=3,max_df=.95,max_features=15000,sublinear_tf=True),'text'))
    if kind=='E4_lsa':
        parts.append(('text',Pipeline([('tfidf',TfidfVectorizer(ngram_range=(1,2),min_df=3,max_features=15000)),('lsa',TruncatedSVD(n_components=64,random_state=SEED)),('scale',StandardScaler())]),'text'))
    return Pipeline([('features',ColumnTransformer(parts,sparse_threshold=.8)),('classifier',LogisticRegression(C=C,max_iter=1500,random_state=SEED))])

def metric(y,p,threshold):
    pred=np.asarray(p)>=threshold;pr,re,f1,_=precision_recall_fscore_support(y,pred,average='binary',zero_division=0)
    return {'n':len(y),'prevalence':float(np.mean(y)),'precision':float(pr),'recall':float(re),'f1':float(f1),'average_precision':float(average_precision_score(y,p)),'roc_auc':float(roc_auc_score(y,p)) if len(set(y))>1 else None,'brier':float(brier_score_loss(y,p)),'log_loss':float(log_loss(y,np.clip(p,1e-6,1-1e-6))),'accuracy':float(accuracy_score(y,pred)),'threshold':float(threshold)}

def choose_threshold(y,p):
    choices=[(metric(y,p,t)['f1'],t) for t in np.linspace(.1,.8,29)]
    return max(choices,key=lambda x:(x[0],x[1]))[1]

def train():
    train=pd.read_parquet(ROOT/'data/splits/train.parquet');tune=pd.read_parquet(ROOT/'data/splits/tune_dev.parquet');select=pd.read_parquet(ROOT/'data/splits/selection_dev.parquet')
    rows=[];frozen={};kindlist=['E1_context_only','E1b_context_structure','E2_tfidf','E3_text_context','E4_lsa']
    for kind in kindlist:
        best=None
        for C in [.1,1.,10.]:
            model=make_model(kind,C);start=time.perf_counter();model.fit(inputs(train),train.label);elapsed=time.perf_counter()-start
            p=model.predict_proba(inputs(tune))[:,1];t=choose_threshold(tune.label,p);m=metric(tune.label,p,t)
            rows.append({'model':kind,'C':C,'partition':'tune_dev','training_seconds':elapsed,**m})
            if best is None or m['average_precision']>best[0]:best=(m['average_precision'],model,t,C,elapsed)
        _,model,t,C,elapsed=best
        start=time.perf_counter();p=model.predict_proba(inputs(select))[:,1];lat=(time.perf_counter()-start)/len(select)
        m=metric(select.label,p,t);rows.append({'model':kind,'C':C,'partition':'selection_dev','training_seconds':elapsed,'inference_seconds_per_post':lat,**m})
        frozen[kind]={'threshold':t,'C':C,'selection_average_precision':m['average_precision'],'selection_f1':m['f1']}
        with (MODEL_DIR/f'{kind}.pkl').open('wb') as f:pickle.dump(model,f)
        pd.DataFrame({'id':select.id,'label':select.label,'probability':p}).to_csv(ROOT/'results'/f'{kind}_selection_predictions.csv',index=False)
        print('EVALUATOR',kind,'selection AP',round(m['average_precision'],4),'F1',round(m['f1'],4),flush=True)
    for split,df in [('tune_dev',tune),('selection_dev',select)]:
        rows.append({'model':'E0_lazy','partition':split,**metric(df.label,np.zeros(len(df)),.5)})
        rows.append({'model':'E0_prior','partition':split,**metric(df.label,np.repeat(train.label.mean(),len(df)),.5)})
    # Optimization scorer must work without supplying an author history: text-only.
    frozen['optimization_model']='E2_tfidf';frozen['best_selection_model']=max(kindlist,key=lambda x:frozen[x]['selection_average_precision'])
    frozen['created_at']=now();frozen['final_test_run']=False
    frozen['optimization_signal_gate']=frozen['E2_tfidf']['selection_average_precision']>float(select.label.mean())+.02
    frozen['output_interpretation']='model-relative potential score; not real viral probability'
    write_json(ROOT/'configs/evaluator_freeze.json',frozen)
    pd.DataFrame(rows).to_csv(ROOT/'results/evaluator_dev_results.csv',index=False)

def score_posts(posts):
    with (MODEL_DIR/'E2_tfidf.pkl').open('rb') as f:model=pickle.load(f)
    return model.predict_proba(pd.DataFrame({'text':[p.get('title','')+'\n'+p.get('body','') for p in posts]}))[:,1].tolist()

def final_test():
    freeze=json.loads((ROOT/'configs/evaluator_freeze.json').read_text(encoding='utf-8'))
    marker=ROOT/'results/FINAL_TEST_STARTED.json'
    if marker.exists():raise RuntimeError('Final test already started; no silent repeat allowed')
    write_json(marker,{'at':now(),'models_config_sha256':digest(json.dumps(freeze))})
    df=pd.read_parquet(ROOT/'data/splits/final_test.parquet');train=pd.read_parquet(ROOT/'data/splits/train.parquet');rows=[];allpred={}
    for kind in ['E0_lazy','E0_prior','E1_context_only','E1b_context_structure','E2_tfidf','E3_text_context','E4_lsa','E4_semantic']:
        start=time.perf_counter()
        if kind.startswith('E0'):p=np.zeros(len(df)) if kind=='E0_lazy' else np.repeat(train.label.mean(),len(df));t=.5
        else:
            with (MODEL_DIR/f'{kind}.pkl').open('rb') as f:model=pickle.load(f)
            if kind=='E4_semantic':
                from semantic_evaluator import embeddings
                p=model.predict_proba(embeddings(df))[:,1]
            else:p=model.predict_proba(inputs(df))[:,1]
            t=freeze[kind]['threshold']
        m=metric(df.label,p,t);allpred[kind]=p
        rows.append({'model':kind,'partition':'final_test','inference_seconds_per_post':(time.perf_counter()-start)/len(df),'api_cost_usd':0.,**m})
        pd.DataFrame({'id':df.id,'author':df.author,'month':df.month,'type':df.content_type,'label':df.label,'probability':p,'prediction':p>=t}).to_csv(ROOT/'results'/f'{kind}_final_predictions.csv',index=False)
    # Author cluster resampling; conditions on two held-out months, not broad future uncertainty.
    rng=np.random.default_rng(SEED);groups=df.groupby('author',dropna=False).indices;keys=list(groups);boot=[]
    for _ in range(500):
        ix=np.concatenate([groups[keys[i]] for i in rng.integers(0,len(keys),len(keys))]);y=df.label.to_numpy()[ix]
        if len(np.unique(y))<2:continue
        d={k:average_precision_score(y,p[ix]) for k,p in allpred.items() if not k.startswith('E0')}
        d['E3_minus_E1']=d['E3_text_context']-d['E1_context_only'];d['E2_minus_prior']=d['E2_tfidf']-y.mean();boot.append(d)
    b=pd.DataFrame(boot)
    write_json(ROOT/'results/evaluator_bootstrap.json',{'method':'500 author-cluster bootstrap draws; conditional on heldout months','ci95':{c:[float(b[c].quantile(.025)),float(b[c].quantile(.975))] for c in b}})
    pd.DataFrame(rows).to_csv(ROOT/'results/evaluator_results.csv',index=False)
    write_json(ROOT/'results/FINAL_TEST_COMPLETED.json',{'at':now(),'rows':len(df),'no_tuning_after_test':True})
    print('FINAL TEST',pd.DataFrame(rows)[['model','average_precision','f1','brier']].to_string(index=False),flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--stage',choices=['train','final'],default='train');args=ap.parse_args()
    train() if args.stage=='train' else final_test()
