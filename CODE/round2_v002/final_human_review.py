"""Chinese paired final review; genuine submissions only, mapping hidden from page."""
from runtime import *
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from html import escape

def prepare():
    pairs=[];mapping=[]
    for i in range(1,13):
        bid='F'+str(i).zfill(2);b=read(LOOP/'evals'/f'brief_{bid}_v002.json')
        drafts={v:read(LOOP/'results/generator_runs'/f'{bid}_{v}_v002.json')['selected'] for v in ['V0','V1']}
        if not all(drafts.values()):continue
        swapped=int(digest('blind1.1:'+bid),16)%2;names=['V1','V0'] if swapped else ['V0','V1']
        file=LOOP/'evals/final_human_pairs'/f'{bid}_v002.json'
        if file.exists():p=read(file)
        else:
            payload={'task':b['problem_or_goal'],'A':drafts[names[0]]['draft'],'B':drafts[names[1]]['draft']}
            prompt='''Translate the task and BOTH drafts faithfully into plain simplified Chinese for blind review. Do not rewrite, improve, add/remove claims, simplify one version more than the other, or change uncertainty. Preserve numbers, model names, source attribution and date. Return JSON {"task_zh":"...","A":{"title":"...","body":"..."},"B":{"title":"...","body":"..."}}.\n'''+json.dumps(payload,ensure_ascii=False)
            ans=complete(prompt,INTERNALS[0],'translate:human_final:'+bid,2300,'final');p=ans['value'];p.update(pair_id=bid,english_A=payload['A'],english_B=payload['B'])
            def nums(x):return sorted(re.findall(r'\d+(?:\.\d+)?',x['title']+' '+x['body']))
            p['translation_numeric_checks']={v:nums(p[v])==nums(payload[v]) for v in ['A','B']}
            write(file,p)
        pairs.append(p);mapping.append({'pair_id':bid,'A':names[0],'B':names[1]})
    write(LOOP/'evals/final_human_public_pairs_v002.json',pairs);write(LOOP/'evals/final_human_private_mapping_v002.json',mapping)
    event('human_final','Chinese blind review package prepared; no votes fabricated',{'n':len(pairs),'comparison':'V1 versus V0','votes':0,'numeric_translation_checks':[p['translation_numeric_checks'] for p in pairs]})

def page():
    pairs=read(LOOP/'evals/final_human_public_pairs_v002.json');cards=[]
    for i,p in enumerate(pairs,1):
        text=f'<section><h2>Pair {i}</h2><p>Task: {escape(p["task_en"])}</p>'
        for label in ['A','B']:
            x=p[label];text+=f'<h3>{label} &middot; {escape(x["title"])}</h3><p class="body">{escape(x["body"])}</p>'
        text+=f'<label>Which is more worth posting?<select name="{p["pair_id"]}" required><option value="">Please choose</option><option>A</option><option>B</option><option value="Tie">About the same</option><option value="Uncertain">Cannot tell / unsure</option></select></label><label>Reason (optional)<textarea name="note_{p["pair_id"]}" rows="2"></textarea></label></section>';cards.append(text)
    ids=json.dumps([p['pair_id'] for p in pairs])
    return '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Round 2 Final blind review</title><style>body{background:#f5f6f9;color:#203047;font:16px system-ui}main{max-width:850px;margin:auto;padding:25px}section{background:white;padding:24px;margin:24px 0;border-radius:10px}.body{white-space:pre-wrap;line-height:1.9}label{display:block;margin-top:20px}input,select,textarea{width:100%;box-sizing:border-box;padding:12px;font:inherit}button{padding:14px 24px;background:#2456a4;color:white;border:0;border-radius:6px;font:inherit}</style><main><h1>Round 2: Final blind review</h1><p>Decide which draft reads more like a natural, useful community post worth publishing. If your technical background is not sufficient, choose &quot;Cannot tell / unsure&quot; &mdash; there is no need to force a choice. No system identity or model score is shown.</p><form id="review"><label>Reviewer name<input name="reviewer" required></label>'''+''.join(cards)+'''<button>Save genuine feedback</button></form><p id="status"></p></main><script>let ids='''+ids+''';document.getElementById('review').onsubmit=async e=>{e.preventDefault();let f=new FormData(e.target),responses=ids.map(id=>({pair_id:id,choice:f.get(id),note:f.get('note_'+id)}));let r=await fetch('/api/review',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({reviewer:f.get('reviewer'),responses})});let j=await r.json();document.getElementById('status').textContent=j.message;if(r.ok)document.querySelector('button').disabled=true;};</script></html>'''

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        data=page().encode();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
    def do_POST(self):
        if self.path!='/api/review':self.send_error(404);return
        if self.headers.get('Origin') not in [None,'http://127.0.0.1:8880']:self.send_error(403);return
        try:
            n=int(self.headers.get('Content-Length','0'))
            if n>50000:raise ValueError('Feedback too long')
            j=json.loads(self.rfile.read(n));expected={p['pair_id'] for p in read(LOOP/'evals/final_human_public_pairs_v002.json')};rs=j['responses']
            if not j.get('reviewer','').strip() or len(rs)!=len(expected) or {x['pair_id'] for x in rs}!=expected or any(x['choice'] not in ['A','B','Tie','Uncertain'] for x in rs):raise ValueError('Please choose an option for every pair')
            j.update(at=now(),source='genuine browser submission',language='Chinese translations, English available');p=LOOP/'evals/final_human_submissions'/f'{time.time_ns()}_v002.json';write(p,j);event('human_final','Actual human blind review received',{'evidence':str(p),'n':len(rs)})
            result={'message':'Genuine feedback saved. Please come back to the conversation and tell me it has been submitted.'};status=200
        except Exception as exc:result={'message':str(exc)};status=400
        data=json.dumps(result,ensure_ascii=False).encode();self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)

if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='prepare':prepare()
    else:print('Final human review: http://127.0.0.1:8880',flush=True);ThreadingHTTPServer(('127.0.0.1',8880),Handler).serve_forever()
