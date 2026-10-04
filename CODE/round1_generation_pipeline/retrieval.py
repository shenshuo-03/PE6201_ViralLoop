"""Train-only lexical retrieval; balanced positive/negative examples by content type."""
from common import *
import pandas as pd,numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
class Retriever:
    def __init__(self):
        self.posts=pd.read_parquet(ROOT/'data/splits/train.parquet').reset_index(drop=True)
        self.vectorizer=TfidfVectorizer(ngram_range=(1,2),min_df=2,max_features=15000,sublinear_tf=True)
        self.matrix=self.vectorizer.fit_transform(self.posts.title+'\n'+self.posts.selftext)
    def retrieve(self,query,typ,positive=3,negative=2):
        scores=(self.matrix@self.vectorizer.transform([query]).T).toarray().ravel();order=np.argsort(-scores);out=[]
        for label,count in [(1,positive),(0,negative)]:
            candidates=[i for i in order if self.posts.iloc[i].label==label and self.posts.iloc[i].content_type==typ]
            for i in candidates[:count]:
                r=self.posts.iloc[i];out.append({'id':r.id,'title':r.title,'body':r.selftext[:900],'historical_class':'high' if label else 'not_high','similarity':float(scores[i]),'partition':'train'})
        return out
