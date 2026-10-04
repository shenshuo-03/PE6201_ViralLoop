"""Real HTTP end-to-end smoke check, NOT a human review or final benchmark rerun."""
from common import *
import urllib.request,time
def main():
    base='http://127.0.0.1:8877'
    status=json.load(urllib.request.urlopen(base+'/api/status'));topics=json.load(urllib.request.urlopen(base+'/api/topics'));results=json.load(urllib.request.urlopen(base+'/api/results'));blind=json.load(urllib.request.urlopen(base+'/api/blind'))
    payload={'topic':'A hypothetical local inference startup-delay comparison','content_type':'Experience / Benchmark','variant':'G4_both','optimize':True,'facts':['This is a hypothetical scenario, not an actual benchmark.','Setup A has illustrative time-to-first-token of 1.2 seconds and setup B 2.4 seconds.','Both hypothetical configurations use the same prompt and hardware.','Throughput, answer quality and statistical uncertainty have not been measured.']}
    req=urllib.request.Request(base+'/api/generate',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
    start=time.perf_counter();live=json.load(urllib.request.urlopen(req,timeout=240));elapsed=time.perf_counter()-start
    check={'status_api':status['state']['status']=='automated_experiments_completed','14_topics':len(topics)==14,'80_final_result_cells':len(results)==80,'12_blind_pairs':len(blind)==12,'live_real_response':bool(live.get('initial') or live.get('abstention')),'live_complete_loop':bool(live.get('revisions')),'live_final_qualified':bool(live.get('final',{}).get('constraint_pass'))}
    write_json(ROOT/'results/ui_smoke_test.json',{'at':now(),'source':'automated integration test; no human review submission','elapsed_seconds':elapsed,'checks':check,'additional_budget_charge':live.get('additional_budget_charge'),'result':live})
    print('UI SMOKE',check,'additional budget',live.get('additional_budget_charge'),flush=True)
    if not all(check.values()):raise RuntimeError('UI smoke check incomplete; inspect failure/abstention without inventing success')
if __name__=='__main__':main()
