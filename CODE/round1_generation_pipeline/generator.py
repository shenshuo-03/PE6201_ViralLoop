"""Comparable same-model generation variants; facts and hard constraints shared."""
from common import *
from model_api import complete,GENERATOR
from retrieval import Retriever
from pattern_miner import FEATURES
VARIANTS=['G0_generic','G1_prompt','G2_fewshot_planning','G3_rag','G4_positive','G4_both']
BASE='''Write TWO different English technical Reddit posts for the supplied topic and facts.
The brief is hypothetical: explicitly preserve that status. Never turn hypothetical facts
into personal experience or measured results. Use no new numbers, benchmarks, product
versions, external facts or sources. Advice must preserve all important limitations.
Each body must be 100-220 words; title <=160 characters. No copying historical examples.
Return JSON {"drafts":[{"title":"...","body":"...","fact_refs":["F1"],"plan":"..."},...]}
with exactly two drafts. Fact refs cite supplied ledger IDs and stay outside prose.
'''
GUIDANCE='''Persona: careful local-AI community editor. Audience: technically informed readers.
Objective: useful discussion rather than hype. Make the specific question or result clear
early, keep a restrained title, organize evidence and limitations, and invite a focused
discussion only if suitable. Self-review factual consistency, clarity and credibility.
'''
def cards_for(typ,direction='both'):
    cards=json.loads((ROOT/'patterns/all_patterns.json').read_text(encoding='utf-8'))
    return [c for c in cards if c['applicable_type']==typ and (direction=='both' or c['direction']==direction)]
def diagnostics(post,typ):
    r={'title':post.get('title',''),'selftext':post.get('body','')};out=[]
    for c in cards_for(typ):
        name=c['id'].split('__')[0];present=bool(FEATURES[name][1](r))
        out.append({'id':c['id'],'direction':c['direction'],'present':present,'action':'revise' if present and c['direction']=='negative' else 'keep','severity':'soft','suggestion':c['suggested_action'],'causal':False})
    return out
def build_prompt(brief,variant,retriever):
    examples=[];cards=[];prompt=BASE
    if variant!='G0_generic':prompt+=GUIDANCE
    if variant=='G2_fewshot_planning':
        examples=retriever.retrieve(brief['topic'],brief['content_type'],positive=2,negative=0)
        prompt+='Produce a concise plan before writing, then check the draft against the rubric. Examples illustrate form; their factual content must NOT be transferred.\n'
    if variant in ['G3_rag','G4_positive','G4_both']:
        examples=retriever.retrieve(brief['topic'],brief['content_type'],positive=3,negative=2)
        prompt+='Retrieved high/not-high examples are observational references. Do not assume their styles caused their scores. Do not copy text or facts.\n'
    if variant in ['G4_positive','G4_both']:
        cards=cards_for(brief['content_type'],'positive' if variant=='G4_positive' else 'both')
        prompt+='Consider the following validated-direction correlations as SOFT guidance, never mandatory facts or hard rejection rules. Positive: consider when appropriate. Negative: avoid forcing a feature merely to chase a score. Preserve diversity and required caveats.\n'
    prompt+=json.dumps({'brief':brief,'historical_examples':examples,'pattern_cards':cards},ensure_ascii=False)
    return prompt,examples,cards
def generate(brief,variant,retriever,tag):
    prompt,examples,cards=build_prompt(brief,variant,retriever)
    result=complete(prompt,model=GENERATOR,max_tokens=1800,tag=tag,temperature=.65)
    drafts=result['value'].get('drafts',[])
    if len(drafts)!=2:raise ValueError('Generator must provide two drafts')
    return drafts,examples,cards,result['usage'],prompt
def optimize(parent,brief,retriever,mode,feedback,tag):
    examples=retriever.retrieve(brief['topic'],brief['content_type'],positive=3,negative=2)
    prompt=BASE.replace('TWO different','THREE different').replace('exactly two','exactly three')+GUIDANCE
    if mode=='O1_resample':
        prompt+='Make three fresh alternative drafts from the same supplied facts. The parent is a reference only. No evaluation feedback is available.\n';extra={'parent':parent}
    else:
        prompt+='Make three ONE-STEP revisions of the same parent: title/opening; specificity from supplied facts; organization/conciseness. Do not insert facts or simply repeat positive-scoring keywords. Keep the factual claims unchanged. Each plan states the targeted change.\n';extra={'parent':parent,'feedback':feedback}
    prompt+=json.dumps({'brief':brief,'references':examples,**extra},ensure_ascii=False)
    result=complete(prompt,model=GENERATOR,max_tokens=3600,tag=tag,temperature=.65)
    drafts=result['value'].get('drafts',[])
    if len(drafts)!=3:raise ValueError('Optimization must produce three drafts')
    return drafts,examples,result['usage'],prompt
