"""Audit original manifests; later-derived freeze evidence is separate and explicitly dated."""
from runtime import *
from _packaged_code import frozen_code_ok
import importlib.util,collections
helper=Path(__file__).resolve().parents[1]/'_vendor/audit_contract.py'
spec=importlib.util.spec_from_file_location('audit_helper',helper);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
contracts={sha(p):p for p in LOOP.glob('experiment_contract*_v002.yaml')}
if (LOOP/'product_contract_v002.yaml').exists():contracts[sha(LOOP/'product_contract_v002.yaml')]=LOOP/'product_contract_v002.yaml'
freeze=read(LOOP/'configs/generator_freeze_v002.json')
# The packaging step changed some modules on purpose (path resolution, write
# protection, Englishization).  _packaged_code holds the byte-identical original
# of each, so a declared change is distinguishable from an arbitrary edit.
freeze_current_ok=all(frozen_code_ok('round2_v002',freeze['code_hashes'],LOOP/'code').values())
events=rows(LOOP/'events_v002.jsonl');final_reads=[e for e in events if e['stage']=='access' and e['evidence'].get('split')=='final']
final_after=all(e['time']>=freeze['at'] for e in final_reads)
records=[];priors=[]
for row in rows(LEDGER):
    path=LOOP/'runs'/row['run_id']/f'manifest_{row["run_id"]}.json'
    if not path.exists():records.append({'run_id':row['run_id'],'verdict':'WARN','reason':'Original manifest missing; paid ledger retained, cannot reconstruct complete evidence'});continue
    m=read(path);cpath=contracts.get(m['contract_sha256'])
    if not cpath:records.append({'run_id':row['run_id'],'verdict':'FAIL','reason':'Exact contract unavailable'});continue
    original_result=module.audit(read(cpath),m,sha(cpath),priors)
    raw_checks={'input_hash_matches':(path.parent/'prompt.txt').exists() and digest((path.parent/'prompt.txt').read_text(encoding='utf-8'))==m['input_hash'],'output_hash_matches':(path.parent/'output.json').exists() and sha(path.parent/'output.json')==m['output_hash'],'ledger_cost_matches':abs(row['budget_charge_usd']-m['cost'])<1e-10}
    enriched=None
    if m['phase']=='final':
        enriched=dict(m);enriched.update(freeze_verified=freeze_current_ok,final_unexposed_before_run=final_after and row.get('at','')>=freeze['at'],late_audit_at=now(),original_manifest_sha256=sha(path),annotation_note='Freeze evidence verified after run from immutable freeze/code hashes and actual source access log; not contemporaneous original fields')
        derived=path.parent/'manifest_with_late_freeze_audit.json';write(derived,enriched)
    result=module.audit(read(cpath),enriched or m,sha(cpath),priors)
    records.append({'run_id':row['run_id'],'original_logged_conformance':original_result,'conformance_with_late_audit':result,'raw_checks':raw_checks,'verdict':result['verdict'] if all(raw_checks.values()) else 'FAIL'})
    priors.append(m)
counts=collections.Counter(r['verdict'] for r in records)
write(LOOP/'results/contract_manifest_audit_v002.json',{'at':now(),'counts':dict(counts),'records':records,'overall':'WARN' if not counts['FAIL'] else 'FAIL','scope':'Recorded conformance plus explicitly dated later hash/access verification; missing failed-call archives remain unknown, no reconstructed raw responses','ledger_rows':len(rows(LEDGER)),'billing_budget_usd':sum(costs())})
print(json.dumps({'counts':dict(counts),'freeze_code_unchanged_or_declared':freeze_current_ok,'all_final_source_reads_after_freeze':final_after}))
