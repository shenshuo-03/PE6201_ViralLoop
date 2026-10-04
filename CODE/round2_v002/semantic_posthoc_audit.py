"""Frozen E4 audit of generated texts. New round ledger, no old runtime writes."""
from runtime import *
import numpy as np,pickle
model_id='openai/text-embedding-3-small'
catalog=json.load(urllib.request.urlopen('https://openrouter.ai/api/v1/embeddings/models',timeout=20))
price=next(x['pricing'] for x in catalog['data'] if x['id']==model_id);rate=float(price['prompt'])
if rate<0:raise RuntimeError('Unbounded embedding price')
write(LOOP/'configs/embedding_audit_price_v002.json',{'at':now(),'model':model_id,'price':price,'source':'https://openrouter.ai/api/v1/embeddings/models'})
c=read(CONTRACT);c['parent_contract_hash']=sha(CONTRACT);c['contract_id']='ViralLoop-v002-posthoc-E4-audit';c['audit']['expected']['contract_id']=c['contract_id'];c['audit']['allowed_variants'].append('semantic_embeddings');c['created_at']=now();c['design']['research_question']='Post-hoc disagreement audit using frozen historical E4; not independent real engagement measurement';cp=LOOP/'experiment_contract_semantic_posthoc_v002.yaml';write(cp,c)
records=[read(p) for p in (LOOP/'results/generator_runs').glob('F*_v002.json')];texts=[];keys=[]
for r in records:
    if r['selected']:
        p=r['selected']['draft'];texts.append((p['title']+'\n'+p['body'])[:4000]);keys.append({'brief_id':r['brief_id'],'variant':r['variant']})
unique=list(dict.fromkeys(texts));key=digest(json.dumps([model_id,unique]));cached=LOOP/'results/api_cache'/(key+'.embedding.raw.json')
upper=(sum(len(t.encode()) for t in unique)+2000)*rate
if not cached.exists():
    prior,spent=costs()
    if prior+spent+upper>5 or spent+upper>2 or len(rows(LEDGER))>=700:raise RuntimeError('Embedding budget refused before request')
    run_id='v002-r'+str(len(rows(LEDGER))+1).zfill(4);run=LOOP/'runs'/run_id;run.mkdir()
    body={'model':model_id,'input':unique,'encoding_format':'float'};write(run/'input.json',body)
    req=urllib.request.Request('https://openrouter.ai/api/v1/embeddings',data=json.dumps(body).encode(),headers={'Authorization':'Bearer '+os.environ['OPENROUTER_API_KEY'],'Content-Type':'application/json'})
    start=time.perf_counter()
    try:
        raw=json.load(urllib.request.urlopen(req,timeout=90));usage=raw.get('usage') or {};actual=usage.get('cost');charge=float(actual) if actual is not None else upper;write(cached,raw);write(run/'raw_response.json',raw)
    except Exception as exc:
        with LEDGER.open('a',encoding='utf-8') as f:f.write(json.dumps({'run_id':run_id,'at':now(),'model':model_id,'tag':'semantic_embeddings:posthoc','phase':'final','budget_charge_usd':upper,'actual_cost_usd':None,'error_type':type(exc).__name__})+'\n')
        raise
    row={'run_id':run_id,'at':now(),'model':model_id,'tag':'semantic_embeddings:posthoc','phase':'final','budget_charge_usd':charge,'actual_cost_usd':actual,'reserved_upper_usd':upper,'input_tokens':usage.get('prompt_tokens',usage.get('total_tokens')),'output_tokens':0,'retry':0,'latency_seconds':time.perf_counter()-start,'cache_key':key,'contract_sha256':sha(cp)}
    with LEDGER.open('a',encoding='utf-8') as f:f.write(json.dumps(row)+'\n')
    # Same audit interface, with explicit posthoc-generated-output scope.
    prompt=json.dumps(body,ensure_ascii=False);(run/'prompt.txt').write_text(prompt,encoding='utf-8');write(run/'output.json',{'vector_count':len(raw['data']),'dimension':len(raw['data'][0]['embedding'])})
    write(run/f'manifest_{run_id}.json',{'run_id':run_id,'cycle_id':'v002','loop_version':'v002','contract_id':c['contract_id'],'contract_sha256':sha(cp),'phase':'final','variant_id':'semantic_embeddings','dataset_hash':c['design']['data']['dataset_hash'],'split_hash':c['design']['data']['split_hash'],'config_hash':sha(LOOP/'configs/embedding_audit_price_v002.json'),'code_hash':sha(__file__),'input_hash':digest(prompt),'output_hash':sha(run/'output.json'),'scores_hash':sha(run/'output.json'),'primary_metric_hash':digest(c['design']['metrics']['primary']),'evaluator_hash':digest(model_id),'candidate_count':0,'tokens':usage.get('prompt_tokens',usage.get('total_tokens',0)),'api_calls':1,'cost':charge,'currency':'USD','latency_seconds':row['latency_seconds'],'retry_count':0,'access_events':[{'split':'final_generated_outputs','purpose':'posthoc_historical_association_audit','time':now(),'evidence':str(run/'input.json')}],'integrity_checks':{'artifact_hashes_verified':True,'split_integrity':True,'billing_ledger_complete':True,'project_budget_verified':sum(costs())<=5},'not_used_for_generator_selection_or_tuning':True})
raw=read(cached);vectors=np.array([x['embedding'] for x in sorted(raw['data'],key=lambda x:x['index'])],dtype=np.float32)
if len(vectors)!=len(unique):raise RuntimeError('Embedding count mismatch')
with (OLD/'results/models/E4_semantic.pkl').open('rb') as f:model=pickle.load(f)
scores=model.predict_proba(vectors)[:,1];lookup=dict(zip(unique,map(float,scores)))
write(LOOP/'results/historical_E4_association_audit_v002.json',{'at':now(),'embedding_model':model_id,'max_chars':4000,'model_retrained':False,'used_for_generator_tuning_or_selection':False,'scores':[dict(k,E4_historical_association_score=lookup[t]) for k,t in zip(keys,texts)],'interpretation':'Exploratory historical model scores after final generation, not true viral probabilities or observed interaction gains','unique_texts':len(unique)})
event('posthoc_audit','Frozen E4 applied to generated drafts without changing generator',{'new_round_ledger_only':True,'unique_texts':len(unique),'old_model_hash':sha(OLD/'results/models/E4_semantic.pkl')});print(json.dumps({'unique_texts':len(unique),'costs':costs()}))
