"""True pretrained text embeddings + logistic classifier, bounded API ledger.

No output scores or labels are sent to the embedding endpoint. The final-test
vectors may be cached in advance; labels are used only in the one-shot test.
"""
from common import *
from model_api import entries,spent,LIMIT,LEDGER
from performance_evaluator import metric,choose_threshold,MODEL_DIR,model_path
import pandas as pd,numpy as np,urllib.request,os,time,pickle
from sklearn.linear_model import LogisticRegression
EMBED_MODEL='openai/text-embedding-3-small'
def embeddings(df):
    # Vectors are cached so that reproducing E4_semantic costs nothing.  The
    # cache is not frozen evidence, so new batches are written to ROOT.out.  A
    # cache that a marker places in the packaged data folder
    # (DATA/round1_dataset/embeddings/) is read but never written to, which makes
    # an offline, key-free E4_semantic re-run possible.
    directory=ROOT.out/'data/embeddings';directory.mkdir(parents=True,exist_ok=True)
    read_only=ROOT/'data/embeddings'
    outputs=[]
    text=(df.title.fillna('')+'\n'+df.selftext.fillna('')).str.slice(0,4000).tolist()
    for start in range(0,len(df),64):
        batch=text[start:start+64];key=digest(json.dumps([EMBED_MODEL,batch]));p=directory/f'{key}.json'
        j=None
        for base in dict.fromkeys([directory,read_only]):
            if (base/f'{key}.json').exists():j=json.loads((base/f'{key}.json').read_text(encoding='utf-8'));break
        if j is not None:pass
        else:
            price=2e-8;upper=(sum(len(x.encode()) for x in batch)+2000)*price
            if spent()+upper>LIMIT:raise RuntimeError('US$5 embedding budget guard')
            body={'model':EMBED_MODEL,'input':batch,'encoding_format':'float'}
            req=urllib.request.Request('https://openrouter.ai/api/v1/embeddings',data=json.dumps(body).encode(),headers={'Authorization':'Bearer '+os.environ['OPENROUTER_API_KEY'],'Content-Type':'application/json'})
            started=time.perf_counter()
            try:
                j=json.load(urllib.request.urlopen(req,timeout=90));usage=j.get('usage') or {};actual=usage.get('cost')
                row={'at':now(),'tag':'semantic_embeddings','model':EMBED_MODEL,'cache_key':key,'status':'success','input_tokens':usage.get('prompt_tokens',usage.get('total_tokens')),'output_tokens':0,'actual_cost_usd':actual,'budget_charge_usd':float(actual) if actual is not None else upper,'reserved_upper_usd':upper,'latency_seconds':time.perf_counter()-started,'n_posts':len(batch),'token_price_estimate_usd':usage.get('total_tokens',0)*price}
                write_json(p,j)
            except Exception as e:
                row={'at':now(),'tag':'semantic_embeddings','model':EMBED_MODEL,'cache_key':key,'status':'error','budget_charge_usd':upper,'error_type':type(e).__name__}
                with LEDGER.open('a',encoding='utf-8') as f:f.write(json.dumps(row)+'\n')
                raise
            with LEDGER.open('a',encoding='utf-8') as f:f.write(json.dumps(row)+'\n')
        outputs.extend(x['embedding'] for x in sorted(j['data'],key=lambda x:x['index']))
        print('EMBED',min(start+64,len(df)),'/',len(df),flush=True)
    return np.array(outputs,dtype=np.float32)

def train():
    frames={k:pd.read_parquet(ROOT/'data/splits'/f'{k}.parquet') for k in ['train','tune_dev','selection_dev']}
    matrices={k:embeddings(v) for k,v in frames.items()};rows=[];best=None
    for C in [1.,10.,100.]:
        m=LogisticRegression(C=C,max_iter=1500,random_state=SEED);start=time.perf_counter();m.fit(matrices['train'],frames['train'].label);elapsed=time.perf_counter()-start
        p=m.predict_proba(matrices['tune_dev'])[:,1];t=choose_threshold(frames['tune_dev'].label,p);result=metric(frames['tune_dev'].label,p,t);rows.append({'model':'E4_semantic','C':C,'partition':'tune_dev','training_seconds':elapsed,**result})
        if best is None or result['average_precision']>best[0]:best=(result['average_precision'],m,t,C)
    _,m,t,C=best;p=m.predict_proba(matrices['selection_dev'])[:,1];result=metric(frames['selection_dev'].label,p,t);rows.append({'model':'E4_semantic','C':C,'partition':'selection_dev',**result})
    with model_path('E4_semantic','w').open('wb') as f:pickle.dump(m,f)
    freeze=json.loads((ROOT/'configs/evaluator_freeze.json').read_text(encoding='utf-8'));freeze['E4_semantic']={'threshold':t,'C':C,'selection_average_precision':result['average_precision'],'selection_f1':result['f1'],'embedding_model':EMBED_MODEL,'max_chars':4000}
    freeze['best_selection_model']=max([k for k in freeze if k.startswith('E')],key=lambda k:freeze[k]['selection_average_precision'])
    write_json(ROOT/'configs/evaluator_freeze.json',freeze)
    old=pd.read_csv(ROOT/'results/evaluator_dev_results.csv');pd.concat([old,pd.DataFrame(rows)]).to_csv(ROOT/'results/evaluator_dev_results.csv',index=False)
    print('SEMANTIC selection',result,flush=True)

if __name__=='__main__':train()
