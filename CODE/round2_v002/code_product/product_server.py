"""Usable fact-grounded writing demo; frozen method, real guarded calls, no virality promise."""
from generation import *
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
import threading
LOCK=threading.Lock()
HTML='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ViralLoop · Community Post Drafter</title><style>body{margin:0;background:#f4f6fa;color:#203047;font:16px system-ui,sans-serif}main{max-width:850px;margin:35px auto;padding:24px}section{background:white;padding:24px;margin:20px 0;border-radius:12px}h1{font-size:30px}label{display:block;margin:16px 0}input,textarea{width:100%;box-sizing:border-box;padding:12px;border:1px solid #aab8c8;border-radius:6px;font:inherit}button{background:#2456a4;color:white;border:0;border-radius:6px;padding:13px 22px;font:inherit;cursor:pointer}.body{white-space:pre-wrap;line-height:1.8}.muted{color:#66758b}#result{white-space:pre-wrap;line-height:1.8}</style><main><h1>ViralLoop</h1><p>Turn real material into a natural, specific r/LocalLLaMA discussion post.</p><p class="muted">Produces an English draft ready to publish. No real virality rate has been measured, and nothing is published automatically. You must supply real facts or sources; the system will not invent first-hand experience from a topic alone.</p><section><form id="writer"><label>Topic<input name="topic" required maxlength="180" placeholder="e.g. How can you tell whether a local model really reasons?"></label><label>Real material / facts<textarea name="material" required rows="9" maxlength="12000" placeholder="Paste a real report or your own material, including concrete context, known facts and limitations. Do not present metrics you have not measured as results."></textarea></label><label>Material date (optional)<input name="date" placeholder="e.g. 2025-01-30; marked unknown if omitted"></label><button>Generate two candidates and check</button></form><p id="status"></p></section><section id="result" hidden></section><script>const form=document.getElementById('writer');form.onsubmit=async e=>{e.preventDefault();let button=form.querySelector('button');button.disabled=true;document.getElementById('status').textContent='Generating and checking; this usually takes about half a minute…';try{let r=await fetch('/api/generate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(Object.fromEntries(new FormData(form)))});let j=await r.json();if(!r.ok)throw Error(j.error);let out=document.getElementById('result');out.hidden=false;out.textContent=j.display;document.getElementById('status').textContent='Done. Actual API cost for this run: US$'+j.cost.toFixed(5);}catch(err){document.getElementById('status').textContent='Not completed: '+err.message;}button.disabled=false;};</script></main></html>'''

def create_draft(topic,material,date='unknown'):
    frozen=read(LOOP/'configs/generator_freeze_v002.json');variant=frozen['selected_product']
    before=costs()[1];bid='L'+str(time.time_ns());phase='preflight'
    s={'brief_id':bid,'source_title':topic,'source_text':material,'source_date':date or 'unknown','source_url':'user-provided material','split':phase,'id':bid}
    write(LOOP/'sources'/f'{bid}_v002.json',s)
    ans=complete(BRIEF_PROMPT+json.dumps(s,ensure_ascii=False),GEN,'brief_builder:'+bid,2200,phase,.1);b=ans['value']
    source_norm=''.join(c.lower() for c in (topic+' '+material) if c.isalnum())
    b['facts']=[f for f in b['facts'] if ''.join(c.lower() for c in f.get('evidence_quote','') if c.isalnum()) and ''.join(c.lower() for c in f.get('evidence_quote','') if c.isalnum()) in source_norm]
    if len(b['facts'])<2:raise ValueError('Not enough material to verify two facts; add concrete facts or the original material')
    b.update(id=bid,split=phase,source_date=date or 'unknown',source_url='user-provided material',content_type='Discussion / Opinion')
    write(LOOP/'evals'/f'brief_{bid}_v002.json',b)
    structure=StructureRetriever().summary(b,phase) if variant=='V2' else {'summary':{}}
    # O1 is not a selectable production mode if its selector failed admission.
    if variant not in ['V0','V1','V2']:raise RuntimeError('No usable production method frozen')
    ans=generate_initial(b,variant,structure,phase);records,u=evaluate_candidates(b,ans['value']['drafts'],phase,bid+':live');chosen,path=select_candidates(b,records,phase,bid+':live')
    if not chosen:raise ValueError('Neither candidate passed the engineering quality checks; a failing draft is not shipped as a product')
    p=chosen['draft']
    display=p['title']+'\n\n'+p['body']+'\n\nMethod: '+variant+'. Feedback rewriting is disabled. The quality check is an engineering screen only; you must still confirm the facts and whether the post is worth publishing.'
    rec={'at':now(),'brief':b,'candidates':records,'selected':chosen,'translation':None,'translation_omitted':'This package is English-only; the former Chinese translation preview step was removed.','method':variant,'display':display,'cost':costs()[1]-before,'external_judge_used':False,'not_final_experiment_data':True};write(LOOP/'results/live_runs'/f'{bid}_v002.json',rec);return rec

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        data=HTML.encode();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
    def do_POST(self):
        if self.path!='/api/generate':self.send_error(404);return
        if self.headers.get('Origin') not in [None,'http://127.0.0.1:8879']:self.send_error(403);return
        try:
            n=int(self.headers.get('Content-Length','0'))
            if n>60000:raise ValueError('Input too large')
            j=json.loads(self.rfile.read(n));topic=j.get('topic','').strip();material=j.get('material','').strip()
            if not topic or len(material)<100 or len(material)>12000:raise ValueError('Enter a topic and at least 100 characters of concrete material (maximum 12,000)')
            if not LOCK.acquire(blocking=False):raise ValueError('A previous request is still generating; please try again shortly')
            try:r=create_draft(topic,material,j.get('date',''))
            finally:LOCK.release()
            result={'display':r['display'],'cost':r['cost']};status=200
        except Exception as exc:result={'error':str(exc)};status=400
        data=json.dumps(result,ensure_ascii=False).encode();self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)

if __name__=='__main__':print('ViralLoop product: http://127.0.0.1:8879',flush=True);ThreadingHTTPServer(('127.0.0.1',8879),Handler).serve_forever()
