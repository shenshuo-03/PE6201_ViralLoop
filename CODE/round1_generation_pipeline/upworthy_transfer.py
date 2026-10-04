"""Optional honest domain-transfer test: Reddit title classifier vs Upworthy CTR.

No Upworthy tuning; pairs share experiment, image, lede and excerpt. Excludes
known archive nonrandom period. Ties retained and reported, not score-gap picked.
"""
from common import *
import pandas as pd,numpy as np,re,collections
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
def main():
    train=pd.read_parquet(ROOT/'data/splits/train.parquet')
    model=Pipeline([('tfidf',TfidfVectorizer(ngram_range=(1,2),min_df=3,max_features=10000)),('lr',LogisticRegression(C=1,max_iter=1000,random_state=SEED))]);model.fit(train.title,train.label)
    path=ROOT/'data/external/Upworthy_exploratory.csv'
    if not path.exists():path=WORK/'Upworthy_exploratory.csv'
    df=pd.read_csv(path);df['created_at']=pd.to_datetime(df.created_at,utc=True,format='mixed')
    # Conservative boundary excludes January 10 as well.
    df=df[~df.created_at.between('2013-06-25','2014-01-11')]
    df=df[df.impressions.ge(100)&df.headline.notna()]
    pairs=[];rng=np.random.default_rng(SEED)
    for group,g in df.groupby(['clickability_test_id','eyecatcher_id','lede','excerpt'],dropna=False):
        g=g.drop_duplicates('headline')
        if len(g)<2:continue
        selected=g.iloc[rng.choice(len(g),2,replace=False)];a,b=selected.to_dict('records');ca=a['clicks']/a['impressions'];cb=b['clicks']/b['impressions']
        p=model.predict_proba([a['headline'],b['headline']])[:,1]
        pairs.append({'experiment_id':group[0],'a':a['headline'],'b':b['headline'],'ctr_a':ca,'ctr_b':cb,'score_a':p[0],'score_b':p[1],'correct':int((p[0]>p[1])==(ca>cb)) if ca!=cb and p[0]!=p[1] else None,'outcome_tie':ca==cb,'prediction_tie':p[0]==p[1]})
    # One pair per experiment, independent of outcome difference.
    pairs=pd.DataFrame(pairs).drop_duplicates('experiment_id');pairs.to_csv(ROOT/'results/upworthy_transfer_pairs.csv',index=False)
    write_json(ROOT/'results/upworthy_transfer_metrics.json',{'n_experiments':len(pairs),'non_tie_n':int(pairs.correct.notna().sum()),'pairwise_accuracy':float(pairs.correct.mean()),'outcome_ties':int(pairs.outcome_tie.sum()),'prediction_ties':int(pairs.prediction_tie.sum()),'baseline':.5,'trained_on':'Reddit title-only Train; C=1 predetermined','target':'observed CTR ordering, not statistically certain true winner','limitations':'Strong platform/domain/time shift; observed CTR noisy; not evidence of full-post or real Reddit uplift; exploratory Upworthy partition only'})
    print('UPWORTHY',len(pairs),pairs.correct.mean(),flush=True)
if __name__=='__main__':main()
