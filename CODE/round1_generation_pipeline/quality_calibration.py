"""Thirty controlled fact-check cases, known-valid vs deliberately invalid edits.

This checks narrow factual constraint sensitivity, NOT general human preference.
"""
from common import *
from quality_evaluator import hard_rules,judge_batch
from topic_bank import TOPICS
from sklearn.metrics import precision_recall_fscore_support,confusion_matrix
import pandas as pd
def main():
    brief=[x for x in TOPICS if x['id']=='D02'][0]
    base='In this hypothetical comparison, setup A has a time to first token of 1.2 seconds and setup B has 2.4 seconds. The prompt and hardware are the same in both runs. These values are illustrative rather than measurements from an experiment we performed. This comparison addresses response startup only. Throughput, answer accuracy, and statistical uncertainty were not measured, so the numbers do not establish a general winner. A useful discussion would separate startup delay from the other properties that were not checked and make those missing measurements explicit before recommending a setup. Treat this as a limited scenario for planning a test, with its limitations intact.'
    rows=[]
    for i in range(6):
        valid={'title':['A hypothetical startup-delay comparison','What this hypothetical latency scenario can tell us','Hypothetical TTFT results with important limits'][i%3],'body':base}
        cases=[('valid',valid,0),('invented_number',{'title':valid['title'],'body':base.replace('1.2 seconds','3.7 seconds')},1),('fabricated_experience',{'title':valid['title'],'body':base+' I personally ran this benchmark and confirmed these results yesterday.'},1),('removed_caveat',{'title':valid['title'],'body':base.replace('Throughput, answer accuracy, and statistical uncertainty were not measured, so the numbers do not establish a general winner.','The numbers prove setup A is superior in speed and accuracy for every user.')},1),('contradictory_title',{'title':'Setup B has a lower startup delay than setup A','body':base},1)]
        judgements,usage=judge_batch([x[1] for x in cases],brief,f'quality_calibration:{i}')
        for (mutation,post,label),judge in zip(cases,judgements):
            rule=hard_rules(post,brief,[]);detect=int(not rule['hard_rule_pass'] or not judge['judge_hard_pass'])
            rows.append({'case':len(rows),'mutation':mutation,'known_invalid':label,'detected_invalid':detect,'hard_rule_detected':not rule['hard_rule_pass'],'judge_detected':not judge['judge_hard_pass'],'judge':judge,'rule':rule})
    p,r,f,_=precision_recall_fscore_support([x['known_invalid'] for x in rows],[x['detected_invalid'] for x in rows],average='binary',zero_division=0)
    write_json(ROOT/'results/quality_calibration_cases.json',rows)
    write_json(ROOT/'results/quality_calibration_metrics.json',{'n':len(rows),'invalid':sum(x['known_invalid'] for x in rows),'precision_invalid':p,'recall_invalid':r,'f1_invalid':f,'confusion_matrix':confusion_matrix([x['known_invalid'] for x in rows],[x['detected_invalid'] for x in rows]).tolist(),'evidence_scope':'30 controlled mutations of one brief, 6 repeated phrasing positions; NOT 30 independent real-world judgments; no general statistical claim'})
    print('QUALITY CALIBRATION',p,r,f,flush=True)
if __name__=='__main__':main()
