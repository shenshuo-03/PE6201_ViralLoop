"""Offline checks of consequential guards; makes no paid calls or human submissions."""
from generation import *
import urllib.request,py_compile

def refused(fn):
    try:fn()
    except RuntimeError:return True
    return False

checks={}
checks['external_cannot_read_tune']=refused(lambda:complete('probe',EXTERNAL,'judge_final:probe',10,'tune'))
checks['external_validation_requires_instrument_tag']=refused(lambda:complete('probe',EXTERNAL,'V1:probe',10,'validation'))
if not read(LOOP/'results/naturalness_gate_v002.json')['formal_generator_stage_allowed']:
    checks['formal_generation_blocked_before_genuine_acceptance']=refused(lambda:guards_for_stage('tune'))
# Originally this asserted that generator_freeze_v002.json did NOT exist yet --
# which is true only before the freeze has been taken.  Replayed against the
# archived evidence the freeze file is present by definition, so assert the
# invariant the original check was standing in for: Final ran only after the
# freeze, and the freeze records a time.
_freeze=read(LOOP/'configs/generator_freeze_v002.json')
checks['final_gated_on_product_freeze']=bool(_freeze.get('at')) and all(
    r.get('at','')>=_freeze['at'] for r in rows(LOOP/'results/api_ledger_v002.jsonl') if r.get('phase')=='final')
retriever=StructureRetriever()
checks['assigned_source_groups_excluded_from_retrieval']=not bool(set(retriever.posts.id)&retriever.excluded_ids)
checks['retrieval_not_empty']=len(retriever.posts)>100
checks['feedback_failed_admission_stays_off']=not read(LOOP/'results/evaluator_admission_v002.json')['feedback_allowed']
# If the fallback calls compare, this offline check must fail rather than spend money.
import generation
def forbidden_compare(*a,**k):raise AssertionError('Failed evaluator used for preference selection')
generation.compare=forbidden_compare
a={'draft':{'title':'a','body':'a'},'quality':{'quality_pass':True}}
b={'draft':{'title':'b','body':'b'},'quality':{'quality_pass':True}}
picked,path=generation.select_candidates({},[a,b],'tune','probe')
checks['failed_evaluator_uses_deterministic_first_qualified']=picked is a and path[0]['result']=='not_judged'
with urllib.request.urlopen('http://127.0.0.1:8878',timeout=5) as res:page=res.read().decode('utf-8')
checks['english_review_page_live']='Save genuine feedback' in page and 'Sample 3' in page
for p in (LOOP/'code').glob('*.py'):py_compile.compile(str(p),doraise=True)
checks['all_current_modules_compile']=True
write(LOOP/'results/offline_preparation_checks_v002.json',{'at':now(),'checks':checks,'passed':all(checks.values()),'no_paid_calls':True,'no_human_submission':True,'retrieval_rows':len(retriever.posts)})
assert all(checks.values()),checks
print(json.dumps(checks))
