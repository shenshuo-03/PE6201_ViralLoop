"""Local-only evidence browser, live MVP and genuine human-review submission.

No traffic experiments or social publishing. Fact briefs go to an external model
only after user invokes Live generation. Budget guard is shared with experiments.
"""
from common import *
from http.server import HTTPServer,BaseHTTPRequestHandler
from urllib.parse import urlparse
from model_api import spent,entries
import os,time,json
WEB=ROOT/'web'
class Handler(BaseHTTPRequestHandler):
    def send_json(self,obj,status=200):
        body=json.dumps(obj,ensure_ascii=False,default=str).encode();self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',len(body));self.end_headers();self.wfile.write(body)
    def do_GET(self):
        path=urlparse(self.path).path
        if path=='/api/status':
            state=json.loads((ROOT/'results/RUN_STATE.json').read_text(encoding='utf-8')) if (ROOT/'results/RUN_STATE.json').exists() else {}
            return self.send_json({'budget_limit':5,'budget_accounted':spent(),'calls':len(entries()),'state':state,'api_key_present':bool(os.environ.get('OPENROUTER_API_KEY')),'evidence':'historical outcomes + model-proxy generation eval; real platform uplift unobserved'})
        if path=='/api/topics':return self.send_json(json.loads((ROOT/'configs/topic_bank.json').read_text(encoding='utf-8')))
        if path=='/api/results':
            return self.send_json([json.loads(p.read_text(encoding='utf-8')) for p in sorted((ROOT/'results/generator_runs').glob('*.json')) if p.name.startswith('T')])
        if path=='/api/blind':
            p=ROOT/'evals/human_blind_cases.json';return self.send_json(json.loads(p.read_text(encoding='utf-8')) if p.exists() else [])
        name='blind.html' if path=='/blind' else 'index.html' if path=='/' else None
        if name and (WEB/name).exists():
            body=(WEB/name).read_bytes();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',len(body));self.end_headers();return self.wfile.write(body)
        self.send_json({'error':'not_found'},404)
    def do_POST(self):
        try:
            origin=self.headers.get('Origin')
            if origin and origin!='http://127.0.0.1:8877':return self.send_json({'error':'cross_origin_request_rejected'},403)
            length=int(self.headers.get('Content-Length','0'))
            if length>100000:return self.send_json({'error':'input_too_large'},413)
            body=json.loads(self.rfile.read(length));path=urlparse(self.path).path
            if path=='/api/human-review':
                responses=body.get('responses',[])
                if not body.get('rater_name') or not responses:return self.send_json({'error':'A real reviewer name and answers are required'},400)
                p=ROOT/'evals/human_review_submissions';p.mkdir(exist_ok=True)
                write_json(p/f'{int(time.time())}.json',{'submitted_at':now(),'source':'browser user submission, self-declared real person','rater_name':body['rater_name'],'responses':responses})
                return self.send_json({'saved':True,'responses':len(responses),'note':'Submission saved. It must be unblinded and aggregated, and is not automatically treated as an experimental result.'})
            if path=='/api/generate':
                state=json.loads((ROOT/'results/RUN_STATE.json').read_text(encoding='utf-8'))
                if state.get('status')!='automated_experiments_completed':return self.send_json({'error':'Automated experiments are still running. Review the evidence replay first; live generation becomes available later.'},409)
                from generator import generate,optimize,diagnostics
                from retrieval import Retriever
                from harness import assess
                facts=body.get('facts',[])
                if not facts or not body.get('topic'):return self.send_json({'error':'Topic and facts cannot be empty'},400)
                brief={'id':'LIVE_'+str(int(time.time())),'split':'live','topic':body['topic'],'audience':body.get('audience','r/LocalLLaMA readers'),'content_type':body.get('content_type','Discussion / Opinion'),'style':'restrained technical English','scenario_status':'Hypothetical example input. Do not turn it into personal experience or real test results.','facts':[{'id':f'F{i+1}','text':str(x),'status':'user-provided scenario'} for i,x in enumerate(facts)]}
                config=json.loads((ROOT/'configs/generator_freeze.json').read_text(encoding='utf-8'))
                variant=body.get('variant') or config['best_practical_selection']
                from generator import VARIANTS
                if variant not in VARIANTS:return self.send_json({'error':'unknown_generator_variant'},400)
                retriever=Retriever();before=spent();drafts,examples,cards,usage,prompt=generate(brief,variant,retriever,brief['id']+':initial')
                assessed,parent,ju=assess(drafts,brief,examples,brief['id']+':quality')
                if parent is None:
                    result={'brief':brief,'initial_candidates':assessed,'abstention':True,'reason':'No candidate passed the quality constraints; no further score chasing was attempted.','additional_budget_charge':spent()-before}
                elif not body.get('optimize',False):
                    result={'brief':brief,'variant':variant,'initial_candidates':assessed,'initial':parent,'final':parent,'original_retained':True,'optimization_requested':False,'additional_budget_charge':spent()-before,'boundary':'local model score, not observed reader performance'}
                else:
                    feedback={'performance_score':parent['performance_score'],'diagnostics':parent['diagnostics']}
                    drafts,examples,ou,prompt=optimize(parent['draft'],brief,retriever,'O2_feedback',feedback,brief['id']+':revision')
                    revised,selected,j2=assess(drafts,brief,examples,brief['id']+':revision_quality');options=[x for x in revised if x['constraint_pass']]+[parent];best=max(options,key=lambda x:x['performance_score'])
                    result={'brief':brief,'variant':variant,'initial_candidates':assessed,'initial':parent,'revisions':revised,'final':best,'original_retained':best is parent,'optimization_requested':True,'additional_budget_charge':spent()-before,'boundary':'model-relative improvement only, no real platform performance observed'}
                write_json(ROOT/'results/live_runs'/f"{brief['id']}.json",result);return self.send_json(result)
            self.send_json({'error':'not_found'},404)
        except Exception as e:self.send_json({'error_type':type(e).__name__,'message':'Request failed; the call cost has been recorded. Check the log or retry.'},500)
    def log_message(self,fmt,*args):print(now(),fmt%args,flush=True)
if __name__=='__main__':
    server=HTTPServer(('127.0.0.1',8877),Handler)
    write_json(ROOT/'results/server_pid.json',{'pid':os.getpid(),'host':'127.0.0.1','port':8877,'at':now()})
    print('ViralLoop: http://127.0.0.1:8877 ; blind review: /blind',flush=True)
    server.serve_forever()
