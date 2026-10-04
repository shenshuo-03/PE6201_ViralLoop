"""Audit raw posts, rule-filter without scores, cache upstream records, freeze splits.

Uses source score and its second-retrieval timestamp from the SAME source record.
All outcome percentiles are retrospective month/type cohorts, never input features.
Whole months belong to one partition; tiny cohorts use that month's all-type cutoff.
"""
from common import *
import re, collections, random, time, urllib.request, argparse
import pandas as pd
import numpy as np
import pyarrow.parquet as pq

def content_type(title,body):
    s=(title+' '+body[:700]).lower()
    if re.search(r'\b(released|release announcement|launching|just launched|breaking news|new model release)\b',s):return 'Release / News'
    if re.search(r'\b(benchmark|tokens?/s|tok/s|tokens per second|my experience|i tested|i tried|my setup|performance test)\b',s):return 'Experience / Benchmark'
    if re.search(r'\b(tutorial|guide|how to|step.by.step|walkthrough)\b',s):return 'Tutorial / Guide'
    if '?' in title or re.search(r'\b(help|troubleshoot|how do i|is there|anyone know|question)\b',title.lower()):return 'Question / Troubleshooting'
    return 'Discussion / Opinion'

def audit_filter():
    raw=pq.read_table(RAW_FILE).to_pandas()
    raw['created']=pd.to_datetime(raw.created,utc=True)
    raw['title']=raw.title.fillna('');raw['selftext']=raw.selftext.fillna('')
    raw['year']=raw.created.dt.year;raw['month']=raw.created.dt.strftime('%Y-%m')
    stats={'rows':len(raw),'unique_ids':raw.id.nunique(),'missing_created':int(raw.created.isna().sum()),'by_month':raw.month.value_counts().sort_index().to_dict(),'score_quantiles':raw.score.quantile([0,.25,.5,.75,.95,1]).to_dict(),'zero_score':int((raw.score==0).sum()),'negative_score':int((raw.score<0).sum()),'body_length':raw.selftext.str.len().quantile([0,.25,.5,.75,1]).to_dict(),'sticky':int(raw.stickied.fillna(False).sum()),'authors':raw.author.nunique(),'fields':list(raw.columns),'missing_flair':True}
    write_json(ROOT/'data/raw_audit.json',stats)
    raw.groupby('month',dropna=False).agg(posts=('id','size'),median_score=('score','median'),zero_score=('score',lambda x:(x==0).sum())).to_csv(ROOT/'data/raw_audit.csv')
    reasons=collections.Counter(); keep=[];log=[];seen={}
    for r in raw.to_dict('records'):
        title=r['title'].strip();body=r['selftext'].strip();reason=None
        if r['year']!=2025:reason='outside_2025'
        elif not title:reason='empty_title'
        elif body.lower() in ['[deleted]','[removed]','']:reason='missing_body'
        elif r.get('stickied'):reason='sticky'
        elif len(body)<200:reason='body_under_200_chars'
        elif len(body)>20000:reason='body_over_20000_chars'
        elif re.fullmatch(r'https?://\S+',body):reason='link_only'
        elif (r.get('media') and str(r['media']) not in ['None','nan','null','{}']) or re.search(r'preview\.redd\.it|i\.redd\.it|v\.redd\.it',body):reason='media_body'
        elif re.search(r'\b(use my referral|promo code|buy now|limited time offer)\b',body.lower()):reason='explicit_promotion'
        normalized=re.sub(r'\s+',' ',(title+' '+body).lower()).strip()
        gid=digest(normalized)
        if not reason and gid in seen:reason='exact_duplicate'
        if reason:reasons[reason]+=1
        else:
            seen[gid]=r['id'];r['duplicate_group_id']=gid;r['content_type']=content_type(title,body)
            if r['content_type']=='Release / News':reason='release_news';reasons[reason]+=1
            else:keep.append(r)
        log.append({'id':r['id'],'included':not bool(reason),'reason':reason or 'retained'})
    pool=pd.DataFrame(keep).sort_values('created');pool.to_parquet(ROOT/'data/candidate_pool.parquet',index=False)
    pd.DataFrame(log).to_csv(ROOT/'data/cleaning_log.csv',index=False)
    pool[['id','duplicate_group_id','content_type']].to_csv(ROOT/'data/content_types.csv',index=False)
    write_json(ROOT/'data/filter_summary.json',{'candidate_count':len(pool),'reasons':reasons,'types':pool.content_type.value_counts().to_dict(),'by_month':pool.month.value_counts().sort_index().to_dict(),'selection_uses_score':False})
    print('AUDIT',len(raw),'CANDIDATES',len(pool),flush=True)
    return pool

def stratified(df,n):
    # Uniform month/type coverage, sampled without inspecting performance labels.
    groups=[g.sample(frac=1,random_state=SEED).id.tolist() for _,g in df.groupby(['month','content_type'])]
    out=[]
    for i in range(max(map(len,groups))):
        for g in groups:
            if i<len(g):out.append(g[i])
            if len(out)>=n:return out
    return out

def recover(ids):
    records=[]
    for i in range(0,len(ids),100):
        batch=ids[i:i+100]; key=digest(','.join(batch));cache=ROOT/'data/recovery_cache'/f'{key}.json'
        if cache.exists():j=json.loads(cache.read_text(encoding='utf-8'))
        else:
            url='https://arctic-shift.photon-reddit.com/api/posts/ids?ids='+','.join(batch)
            for attempt in range(3):
                try:
                    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'PE6201 academic data audit'}),timeout=50) as resp:j=json.load(resp)
                    write_json(cache,{'requested_ids':batch,'fetched_at':now(),'response':j});break
                except Exception as e:
                    if attempt==2:raise
                    time.sleep(2*(attempt+1))
            j=json.loads(cache.read_text(encoding='utf-8'))
            time.sleep(.4)
        result=j.get('response',j);records.extend(result.get('data',[]) if isinstance(result,dict) else result)
        print('RECOVERY',min(i+100,len(ids)),'/',len(ids),flush=True)
    return records

def recovered_frame(records,pool):
    old=pool.set_index('id').to_dict('index');out=[]
    for r in records:
        if r['id'] not in old:continue
        x=old[r['id']].copy();m=r.get('_meta') or {};obs=m.get('retrieved_2nd_on');created=r.get('created_utc')
        x.update({'id':r['id'],'created_at':created,'observed_at':obs,'first_retrieved_at':r.get('retrieved_on'),'observation_age_hours':(obs-created)/3600 if obs and created else None,'raw_score':r.get('score'),'num_comments':r.get('num_comments'),'source_edited':r.get('edited'),'source_meta':json.dumps(m),'source_deleted':m.get('was_initially_deleted',False) or m.get('was_deleted_later',False),'source_title':r.get('title',''),'source_body':r.get('selftext',''),'score_matches_hf':r.get('score')==x['score']})
        out.append(x)
    result=pd.DataFrame(out)
    result['source_edited']=result.source_edited.map(json.dumps)
    return result

def finalize(df,window):
    valid=df[df.observation_age_hours.between(*window)&df.raw_score.notna()&~df.source_deleted].copy()
    valid=valid[valid.source_body.fillna('').str.len().ge(200)&~valid.source_body.fillna('').str.lower().isin(['[deleted]','[removed]'])]
    valid['title']=valid.source_title;valid['selftext']=valid.source_body
    valid=valid.sort_values('created_at').reset_index(drop=True)
    # Near duplicates across temporal partitions are removed from later partitions.
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.neighbors import NearestNeighbors
    vec=TfidfVectorizer(analyzer='char',ngram_range=(4,5),max_features=25000,min_df=2)
    mat=vec.fit_transform((valid.title+' '+valid.selftext).str.slice(0,6000))
    nbr=NearestNeighbors(metric='cosine',algorithm='brute',radius=.12).fit(mat)
    neighbors=nbr.radius_neighbors(mat,return_distance=False);parent=list(range(len(valid)))
    def find(x):
        while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
        return x
    for i,inds in enumerate(neighbors):
        for j in inds:
            a,b=find(i),find(int(j));parent[max(a,b)]=min(a,b)
    valid['duplicate_group_id']=[str(find(i)) for i in range(len(valid))]
    valid['split']=np.select([valid.month.le('2025-07'),valid.month.le('2025-09'),valid.month.le('2025-10')],['train','tune_dev','selection_dev'],default='final_test')
    initial=len(valid);dups=valid[valid.duplicated('duplicate_group_id',keep='first')]
    dups[['id','duplicate_group_id','split']].to_csv(ROOT/'data/duplicate_groups.csv',index=False)
    valid=valid.drop_duplicates('duplicate_group_id',keep='first').copy()
    # Outcome cohort quantile is descriptive, not a classifier input or deployed threshold.
    groups=valid.groupby(['month','content_type'])['raw_score'];cutoffs=groups.transform(lambda x:x.quantile(.75));sizes=groups.transform('size')
    fallback=valid.groupby('month').raw_score.transform(lambda x:x.quantile(.75))
    valid['label_cutoff']=np.where(sizes>=20,cutoffs,fallback)
    valid['label_cohort_size']=sizes;valid['label_fallback']=sizes<20
    # Strict greater-than retains discrete ties; high class may be smaller than 25%.
    valid['label']=(valid.raw_score>valid.label_cutoff).astype(int)
    valid['performance_percentile']=valid.groupby(['month','content_type']).raw_score.rank(pct=True,method='average')
    # Use prior outcomes ONLY if their observation had finished before current publication.
    histories=collections.defaultdict(list);features=[]
    for r in valid.to_dict('records'):
        author=r.get('author');key=author if author and author!='[deleted]' else None
        prior=[h for h in histories[key] if h['observed_at']<r['created_at']] if key else []
        features.append({'author_prior_post_count':len(prior),'author_prior_median_score':float(np.median([h['raw_score'] for h in prior])) if prior else 0.,'author_prior_missing':int(not prior)})
        if key:histories[key].append(r)
    for col in features[0]:valid[col]=[x[col] for x in features]
    valid.to_parquet(ROOT/'data/processed_posts.parquet',index=False)
    (ROOT/'data/splits').mkdir(exist_ok=True)
    for split,g in valid.groupby('split'):g.to_parquet(ROOT/'data/splits'/f'{split}.parquet',index=False)
    valid[['id','raw_score','num_comments','label','label_cutoff','performance_percentile','label_cohort_size','label_fallback','split']].to_parquet(ROOT/'data/labels.parquet',index=False)
    manifest={'created_at':now(),'seed':SEED,'window_hours':window,'near_duplicates_removed':initial-len(valid),'rows':len(valid),'splits':{k:{'n':len(g),'positive':int(g.label.sum()),'months':sorted(g.month.unique().tolist())} for k,g in valid.groupby('split')},'cohort_label_rule':'score > month/type 75th percentile; monthly fallback n<20; retrospective target not forward probability','author_history':'sampled, observed_before_publication, missing flagged','final_test_runs':0,'data_sha256':digest((ROOT/'data/processed_posts.parquet').read_bytes().hex())}
    write_json(ROOT/'configs/data_freeze.json',manifest);print('FREEZE',json.dumps(manifest,ensure_ascii=False),flush=True)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--stage',choices=['audit','restore'],default='audit');args=ap.parse_args()
    pool=audit_filter() if args.stage=='audit' else pd.read_parquet(ROOT/'data/candidate_pool.parquet')
    ids=stratified(pool,2800)
    audit=recovered_frame(recover(ids[:400]),pool)
    audit.to_csv(ROOT/'data/recovery_audit.csv',index=False)
    ages=audit.observation_age_hours.dropna()
    histogram=audit.groupby(pd.cut(audit.observation_age_hours,[0,24,35,36,37,38,39,40,48,72,9999]),observed=True).agg(n=('id','size')).reset_index();histogram.to_csv(ROOT/'data/observation_window_analysis.csv',index=False)
    # Set before inspecting labels or predictive performance; per-source natural 36h cluster.
    center=float(ages.median());window=[float(np.floor(center)),float(np.floor(center)+2)]
    coverage=float(audit.observation_age_hours.between(*window).mean())
    decision={'requested':400,'returned':len(audit),'age_median':center,'age_quantiles':ages.quantile([0,.1,.5,.9,1]).to_dict(),'primary_window':window,'coverage':coverage,'score_match_rate':float(audit.score_matches_hf.mean()),'decision':'GO' if coverage>=.7 else 'ADJUST','selected_without_model_scores':True}
    write_json(ROOT/'data/recovery_decision.json',decision);print('AUDIT_DECISION',json.dumps(decision),flush=True)
    if coverage<.7:raise RuntimeError('Recovery not concentrated enough; inspect before continuing.')
    all_df=recovered_frame(recover(ids),pool);all_df.to_parquet(ROOT/'data/recovered_posts.parquet',index=False)
    finalize(all_df,window)

if __name__=='__main__':main()
