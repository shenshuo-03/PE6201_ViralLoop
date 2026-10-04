"""Sequential orchestration with durable status; never parallelize paid calls."""
from common import *
import subprocess,sys,pandas as pd
def execute(script,*args):
    name=script+' '+' '.join(args);write_json(ROOT/'results/RUN_STATE.json',{'at':now(),'stage':name,'status':'running'})
    logdir=ROOT/'results/execution_logs';logdir.mkdir(exist_ok=True)
    logfile=logdir/(script+'_'+('_'.join(args).replace('--',''))+'.log')
    process=subprocess.Popen([sys.executable,str(ROOT/'src'/script),*args],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8',errors='replace')
    with logfile.open('w',encoding='utf-8') as f:
        for line in process.stdout:f.write(line);f.flush();print(line,end='',flush=True)
    ret=process.wait()
    if ret:write_json(ROOT/'results/RUN_STATE.json',{'at':now(),'stage':name,'status':'failed','exit_code':ret});raise RuntimeError('Stage failed: '+name)
def freeze_generators():
    frame=pd.read_csv(ROOT/'results/generator_summary.csv');s=frame[frame.partition.eq('selection_dev')&frame.variant.str.startswith('G')]
    eligible=s[s.coverage.ge(.75)&s.mean_selected_quality.ge(3.5)&s.mean_selected_clickbait.le(2)]
    if eligible.empty:eligible=s[s.coverage.gt(0)]
    if eligible.empty:raise RuntimeError('No qualified generation version on Selection Dev')
    best=eligible.sort_values('mean_selected_performance',ascending=False).iloc[0]
    near=eligible[eligible.mean_selected_performance.ge(best.mean_selected_performance-.02)]
    practical=near.sort_values('generation_budget_charge_usd').iloc[0]
    hashes={p.name:digest(p.read_text(encoding='utf-8')) for p in (ROOT/'src').glob('*.py')}
    write_json(ROOT/'configs/generator_freeze.json',{'at':now(),'best_performance_selection':best.variant,'best_practical_selection':practical.variant,'selection_rule':'coverage>=.75, quality>=3.5, clickbait<=2; best performance=max scorer; practical=min generation cost within .02 score. Small 2-topic Selection Dev, exploratory.','all_variants_reported':True,'topics_final':10,'generation_model':'google/gemini-2.5-flash-lite','quality_model':'openai/gpt-4.1-mini','optimization_model':'E2_tfidf','prompt_temperature':.65,'baseline_max_output':1800,'optimization_max_output':3600,'file_hashes':hashes,'test_tuning_allowed':False})
    print('GENERATOR FROZEN',best.variant,practical.variant,flush=True)
def main():
    execute('harness.py','--stage','selection_dev')
    execute('quality_calibration.py')
    execute('judge_evaluator.py','--stage','dev')
    freeze_generators()
    execute('performance_evaluator.py','--stage','final')
    execute('judge_evaluator.py','--stage','final')
    execute('harness.py','--stage','final_test')
    execute('upworthy_transfer.py')
    write_json(ROOT/'results/RUN_STATE.json',{'at':now(),'status':'automated_experiments_completed','human_review':'pending genuine user input','face_video':'pending user recording'})
if __name__=='__main__':main()
