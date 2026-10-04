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
checks['final_requires_product_freeze']=not (LOOP/'configs/generator_freeze_v002.json').exists()
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
checks['chinese_review_page_live']='保存真实反馈' in page and '样例3' in page
for p in (LOOP/'code').glob('*.py'):py_compile.compile(str(p),doraise=True)
checks['all_current_modules_compile']=True
write(LOOP/'results/offline_preparation_checks_v002.json',{'at':now(),'checks':checks,'passed':all(checks.values()),'no_paid_calls':True,'no_human_submission':True,'retrieval_rows':len(retriever.posts)})
assert all(checks.values()),checks
print(json.dumps(checks))
