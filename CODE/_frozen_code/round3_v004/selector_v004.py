"""Narrow two-candidate selector; new objective needs new human calibration."""
import json
from round3_runner import L,C,read,write,api,JUDGE,MODELS
FIELDS=['overall_engagement_preference','attention','information_gain','novelty_or_interest','comment_potential','save_share_potential','naturalness']
LABELS=set(C['labels'])
def unswap(label):return {'A':'B','B':'A'}.get(label,label)
def compare_case(case,model):
 if not list((L/'evals/dev_human_submissions').glob('*.json')):raise RuntimeError('New genuine human Dev labels required before selector calibration')
 if len(case['quality']['judgments'])!=2 or not all(x['hard_pass'] for x in case['quality']['judgments']):raise RuntimeError('Hard-failed draft is ineligible for Selector ranking; keep failure in report')
 outputs=[]
 for order in [(0,1),(1,0)]:
  payload={'brief':case['brief'],'A':case['drafts'][order[0]],'B':case['drafts'][order[1]]}
  result=api(JUDGE+'\n'+json.dumps(payload,ensure_ascii=False),model,'selector:'+case['brief_id']+':'+''.join(map(str,order)),phase='selector',max_tokens=1000)
  if any(result.get(k) not in LABELS for k in FIELDS):raise ValueError('Invalid selector label')
  outputs.append(result)
 return {'model':model,'pair_id':case['brief_id'],'AB':outputs[0],'BA':outputs[1],'canonical_AB':outputs[0]['overall_engagement_preference'],'canonical_BA':unswap(outputs[1]['overall_engagement_preference']),'swap_consistent':outputs[0]['overall_engagement_preference']==unswap(outputs[1]['overall_engagement_preference'])}
def admission(rows,human):
 # human map already unblinded once, using immutable private mapping. No synthetic labels.
 if len(rows)!=8 or set(human)!={r['pair_id'] for r in rows}:return {'admitted':False,'reason':'Requires all eight new pairs; never replace a failed task'}
 decisive={k:v for k,v in human.items() if v in ['A','B']};agree=sum(r['swap_consistent'] and r['canonical_AB']==human[r['pair_id']] for r in rows)
 dec_agree=sum(r['swap_consistent'] and r['canonical_AB']==decisive[r['pair_id']] for r in rows if r['pair_id'] in decisive)
 swap=sum(r['swap_consistent'] for r in rows); coverage=sum(r['swap_consistent'] and r['canonical_AB'] in ['A','B'] for r in rows)
 passed=agree>=6 and len(decisive)>=4 and dec_agree/len(decisive)>=.75 and swap>=7 and coverage>=4
 return {'admitted':passed,'label_agreement':agree,'human_decisive':len(decisive),'decisive_matches':dec_agree,'swap_consistent':swap,'decisive_coverage':coverage,'sample_n':8,'boundary':'exploratory admission, not a general accuracy benchmark'}
