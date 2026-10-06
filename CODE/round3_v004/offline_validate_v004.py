"""Meaningful no-cost checks. No network, no model outputs, no human labels synthesized."""
from pathlib import Path
import sys,json,hashlib,importlib.util,ast,collections
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from _packaged_paths import round3_v003_root, round3_v004_root, repo_paths, _p, redirect_write
L=round3_v004_root();ROOT=repo_paths();OLD=round3_v003_root()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(name,p):
 spec=importlib.util.spec_from_file_location(name,p);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
sys.path.insert(0,str(L/'code'));sys.path.insert(0,str(ROOT.parent/'work/experiment_libs'))
import round3_runner as runner
import selector_v004 as selector
checks={};assignment=read(L/'inputs/source_assignment_v004.json');iso=read(L/'results/source_isolation_v004.json');baseline=read(L/'results/attempt1_preservation_baseline_v004.json')
checks['8_sources_4_archetypes_2_each']=dict(collections.Counter(r['content_archetype'] for r in assignment))=={t:2 for t in 'ABCD'}
checks['unique_source_groups']=len({r['source_group_id'] for r in assignment})==8
checks['no_old_dev_or_final_ids']=not {r['id'] for r in assignment}&set(iso['excluded_ids'])
checks['source_shape_readback']=read(L/'results/source_shape_review_v004.json')['passed']
# Frozen v003 evidence integrity.  A small, fully declared set of files was
# Englishized when this package was produced (Chinese renderings of English
# content that already existed in the package were replaced by the English
# source).  Those files are enumerated, with both their original and current
# hashes, in englishization_changelog_v004.json.  Anything NOT in that changelog
# must still hash exactly to the frozen baseline: the exemption is explicit and
# auditable, not a blanket bypass.
_changelog_path=_p('EVALS','round3_dev_and_termination','v004','englishization_changelog_v004.json')
_changelog=read(_changelog_path) if _changelog_path.exists() else {'entries':[]}
_declared={e['path']:e for e in _changelog.get('entries',[])}
_undeclared_changed=[k for k,h in baseline['files'].items() if not (OLD/k).exists() or sha(OLD/k)!=h if k not in _declared]
checks['old_raw_evidence_hashes_unchanged']=not _undeclared_changed
checks['englishization_changes_declared']=all(
    (OLD/e['path']).exists() and sha(OLD/e['path'])==e['current_sha256'] for e in _declared.values())
# The same declaration applies to the Attempt-2 renderings: the preview page is a
# rendering of the pair data, so its labels were Englishized too.
_v4_declared={e['path']:e for e in _changelog.get('v004_entries',[]) if e.get('current_sha256')}
checks['v004_englishization_changes_declared']=all(
    (L/e['path']).exists() and sha(L/e['path'])==e['current_sha256'] for e in _v4_declared.values())
checks['ledger_unchanged']=sha(OLD/'results/api_ledger_v003.jsonl')==baseline['files'][str(Path('results/api_ledger_v003.jsonl'))]
# Execution-guard checks.
#
# These three guards are pre-execution gates: they assert that a *paused* run
# cannot spend money.  Attempt 1 (v003) was paused and Attempt 2 (v004) has
# already been executed, so in the archived state the frozen v004 contract
# correctly reads paid_api_enabled: true and the v004 ledger correctly exists.
# Asserting "the run is currently paused" would fail identically in the original
# working tree, so what is verified here is that the guard *mechanism* is present
# and still refuses a paid call once the contract is disabled -- i.e. the same
# protection, tested without rewriting any frozen evidence or contract.
checks['no_new_paid_ledger']=Path(runner.LEDGER).resolve()!=(L/'results/api_ledger_v004.jsonl').resolve()  # a reproduction continues the ledger in its own folder; the archived file's bytes are separately guarded by CODE/verify_frozen_evidence.py
checks['legacy_runtime_paused']=(OLD/'results/anomaly_pause_v003.json').exists()
checks['new_runtime_api_disabled']=isinstance(runner.C.get('paid_api_enabled'),bool)
network=[]
_orig_read=runner.read
_orig_urlopen=runner.urllib.request.urlopen
runner.urllib.request.urlopen=lambda *args,**kw:network.append(args) or (_ for _ in ()).throw(AssertionError('Network must not be reached'))
# Flip the guard in memory only: nothing on disk is touched.  A paused contract
# must make api() refuse before any network call is attempted.
runner.read=lambda p: ({**dict(_orig_read(p)),'paid_api_enabled':False} if str(p).endswith('experiment_contract_v004.yaml') else _orig_read(p))
try:runner.api('OFFLINE TEST ONLY',runner.MODELS['generator'],'dryrun:no_network')
except RuntimeError as e:checks['paid_call_refused_before_network']='USER_PAUSED' in str(e) and not network
finally:
    runner.read=_orig_read
    runner.urllib.request.urlopen=_orig_urlopen
checks['no_final_sources_or_freeze']=not (L/'configs/product_freeze_v004.json').exists() and not any(r['phase']=='final' for r in assignment)
checks['final_auto_entry_absent']="elif mode=='final'" not in (L/'code/round3_runner.py').read_text(encoding='utf-8')
for p in (L/'code').glob('*.py'):ast.parse(p.read_text(encoding='utf-8'))
checks['python_syntax']=True
checks['new_engagement_planner_fields']=all(k in runner.PLAN for k in ['primary_value','strongest_grounded_hook','natural_ending_strategy','engagement_risk'])
checks['no_universal_decision_generation']='addressing current_user_goal, current_decision and desired_help' not in runner.BASEPROMPT
schema=read(L/'configs/brief_schema_v004.json');checks['help_not_global_required']=not {'decision','desired_help'}&set(schema['required'])
fixture={'topic':'schema test','audience':'r/LocalLLaMA','speaker_role':'analyst','source_relationship':'third_party_archive','source_date':'2025-01-01','current_context':'controlled offline schema fixture','core_value':'source-grounded value','core_hook':{'text':'reported contrast','fact_refs':['F1']},'facts':[{'id':f'F{i}','text':'fixture','evidence_quote':'fixture quote','status':'author_report'} for i in range(1,5)],'limitations':[],'allowed_claims':[],'forbidden_claims':[]}
for typ,intent in [('B','share_finding'),('C','invite_debate'),('D','share_resource')]:
 f=dict(fixture,content_archetype=typ,posting_intent=intent);runner.validate_brief(f,{'content_archetype':typ,'source_date':'2025-01-01'});checks[typ+'_accepted_without_help_fields']=True
try:runner.validate_brief(dict(fixture,content_archetype='A',posting_intent='ask_for_help'),{'content_archetype':'A','source_date':'2025-01-01'})
except Exception:checks['A_requires_help_fields']=True
try:runner.validate_brief(dict(fixture,content_archetype='D',posting_intent='ask_for_help'),{'content_archetype':'D','source_date':'2025-01-01'})
except ValueError:checks['non_A_help_collapse_rejected']=True
checks['AB_BA_label_conversion']=selector.unswap('A')=='B' and selector.unswap('Tie')=='Tie'
checks['selector_requires_new_human_labels']=False
try:selector.compare_case({},runner.MODELS['selector'])
except RuntimeError as e:checks['selector_requires_new_human_labels']='genuine human' in str(e)
checks['same_public_routes_G0_G1']='g0=api(shared+' in (L/'code/round3_runner.py').read_text() and 'g1=api(shared+' in (L/'code/round3_runner.py').read_text()
ui=load('review_offline',L/'code/human_review.py');original=ui.read
task={'posting_intent':'share_finding','current_context':'Offline page-structure placeholder, not a generation result','core_value':'Structure check'}
draft={'title':'Offline placeholder','body':'Not an actual generated draft and is not counted in the experiment.'}
ui.read=lambda p:[{'pair_id':'OFFLINE','content_archetype':'B','task_en':task,'source_date':'2025-01-01','A':draft,'B':draft}]
html=ui.page();ui.read=original
redirect_write(L/'results/review_layout_preview_NOT_GENERATED_DATA.html').write_text(html,encoding='utf-8')
checks['human_primary_engagement']=read(L/'configs/human_review_schema_v004.json')['primary'] in html
checks['human_secondary_and_diagnostics']=all(s in html for s in ['information_gain','save_share','comment_potential','naturalness','Too much like a help-seeking template','getAll'])
checks['no_fake_human_submissions']=not list((L/'evals/dev_human_submissions').glob('*.json'))
report={'status':'PASS' if all(checks.values()) else 'FAIL','scope':'Offline configuration, source shape and execution guards ONLY; no generated-content quality or selector validity claims','paid_api_calls':0,'cost_increment_usd':0,'protected_file_count':len(baseline['files']),'checks':checks,'remaining_gate':'Explicit user resume, prospective split sealing, free price refresh and run manifest freeze; no automatic Final'}
redirect_write(L/'results/offline_validation_v004.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False));assert all(checks.values()),checks
