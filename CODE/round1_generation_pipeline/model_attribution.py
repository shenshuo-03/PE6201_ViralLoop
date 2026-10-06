"""Faithful linear logit contributions; explanatory associations, not causes."""
from common import *
from performance_evaluator import MODEL_DIR, model_path
import pickle,numpy as np,pandas as pd
def explain(post):
    with model_path('E2_tfidf').open('rb') as f:model=pickle.load(f)
    df=pd.DataFrame({'text':[post['title']+'\n'+post['body']]});features=model.named_steps['features'];matrix=features.transform(df).tocsr();clf=model.named_steps['classifier'];names=features.get_feature_names_out();values=matrix.data*clf.coef_[0,matrix.indices];terms=[{'term':names[ix].removeprefix('text__'),'logit_contribution':float(v)} for ix,v in zip(matrix.indices,values)]
    logit=float(clf.intercept_[0]+values.sum());prob=1/(1+np.exp(-logit));pred=float(model.predict_proba(df)[0,1]);assert abs(pred-prob)<1e-8
    return {'intercept':float(clf.intercept_[0]),'summed_logit':logit,'reconstructed_score':float(prob),'positive_terms':sorted([t for t in terms if t['logit_contribution']>0],key=lambda x:-x['logit_contribution'])[:8],'negative_terms':sorted([t for t in terms if t['logit_contribution']<0],key=lambda x:x['logit_contribution'])[:8],'boundary':'exact linear model contributions; often topics/entities, not proven causal editing effects'}
def main():
    out=[]
    for p in sorted((ROOT/'results/generator_runs').glob('T*.json')):
        r=json.loads(p.read_text(encoding='utf-8'))
        if r['selected']:out.append({'topic_id':r['topic']['id'],'variant':r['variant'],**explain(r['selected']['draft'])})
    write_json(ROOT/'results/selected_model_attributions.json',out);print('MODEL ATTRIBUTIONS',len(out),flush=True)
if __name__=='__main__':main()
