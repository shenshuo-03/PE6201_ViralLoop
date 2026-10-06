"""Existing local review pattern adapted for v004; no model labels exposed."""
from pathlib import Path
import json,time,datetime,threading
from html import escape
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
L=Path(__file__).resolve().parents[1];LOCK=threading.Lock();PORT=8882
CHOICES={'A':'More willing to read A','B':'More willing to read B','Tie':'About the same','Both unacceptable':'Would not read either','Uncertain':'Cannot tell / unsure'}
DIAGNOSTICS=['Too much like a data summary','Too much like a help-seeking template','Too generic / no hook','Information too dense','Not enough information','Title not compelling','Point or result not prominent','Overly clickbait','Posting motivation feels artificial','Other']
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def select(name,options):return '<select name="'+escape(name)+'" required><option value="">Please choose</option>'+''.join('<option value="'+escape(k)+'">'+escape(v)+'</option>' for k,v in options.items())+'</select>'
def page():
 pairs=read(L/'evals/dev_public_pairs_v004.json');cards=[]
 for i,p in enumerate(pairs,1):
  bid=p['pair_id'];task=p['task_en'];card=f'<section><h2>Pair {i}</h2><aside><b>Content task</b><p>Type: {escape(p["content_archetype"])} &middot; Intent: {escape(task["posting_intent"])}</p><p>Context: {escape(task["current_context"])}</p><p>Value to the reader: {escape(task["core_value"])}</p><p>Source date: {escape(p["source_date"])}. The scenario is a controlled hypothetical; the historical material does not represent the poster\'s own testing.</p></aside>'
  for lab in ['A','B']:
   d=p[lab];card+=f'<h3>{lab} &middot; {escape(d["title"])}</h3><div class="body">{escape(d["body"])}</div>'
  card+='<label>If both appeared in your feed at the same time, which would you be more willing to open and keep reading?'+select(bid+'_overall',CHOICES)+'</label>'
  for lab in ['A','B']:card+='<label>Is '+lab+' itself worth posting?'+select(bid+'_publish_'+lab,{'Yes':'Worth posting','No':'Not worth posting','Uncertain':'Cannot tell'})+'</label>'
  for k,word in [('information_gain','Which one leaves you with more, or something more useful?'),('save_share','Which one would you be more likely to upvote, save or share?'),('comment_potential','Which one is more likely to prompt a substantive comment or discussion?'),('naturalness','Which one reads more like a real person posting rather than an AI assembling material?')]:card+='<label>'+word+select(bid+'_'+k,CHOICES)+'</label>'
  card+=''.join('<label><input type="checkbox" name="'+bid+'_diagnostics" value="'+escape(x)+'">'+escape(x)+'</label>' for x in DIAGNOSTICS)
  card+='<label>Main problem (optional)<textarea name="'+bid+'_note" rows="2" placeholder="e.g. reads like a summary, too wordy, missing context, unclear question"></textarea></label></section>';cards.append(card)
 ids=json.dumps([p['pair_id'] for p in pairs])
 return '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Round 3 development blind review</title><style>body{font:16px system-ui,sans-serif;background:#f4f6f8;color:#203047}main{max-width:850px;margin:auto;padding:24px}section{background:white;padding:24px;margin:24px 0;border-radius:12px}aside{background:#edf3fb;padding:14px;border-radius:8px}.body{white-space:pre-wrap;line-height:1.9}label{display:block;margin-top:18px}input,select,textarea{width:100%;padding:10px;box-sizing:border-box;font:inherit}button{background:#285aa5;color:white;padding:14px 24px;border:0;border-radius:8px;font:inherit}details{margin-top:12px}</style><main><h1>Round 3: 8-pair development blind review</h1><p>Judge first on willingness to read in a feed; judge posting value separately; you do not need to assess the technical facts. You may choose "Would not read either" or "Cannot tell" &mdash; do not force a winner. No version or model score is shown.</p><form id="review"><label>Reviewer name<input name="reviewer" required></label>'''+''.join(cards)+'''<button>Save genuine feedback</button></form><p id="status"></p></main><script>let ids='''+ids+''';let form=document.getElementById('review'),storage='viralloop-v004-dev-draft';try{let d=JSON.parse(localStorage.getItem(storage)||'{}');for(let [k,v] of Object.entries(d)){if(form.elements[k])form.elements[k].value=v}}catch(e){}form.onchange=()=>localStorage.setItem(storage,JSON.stringify(Object.fromEntries(new FormData(form))));form.onsubmit=async e=>{e.preventDefault();let f=new FormData(form);let fields=['overall','publish_A','publish_B','information_gain','save_share','comment_potential','naturalness','note'];let responses=ids.map(id=>Object.fromEntries([['pair_id',id],...fields.map(k=>[k,f.get(id+'_'+k)]),['diagnostics',f.getAll(id+'_diagnostics')]]));let r=await fetch('/api/review',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({reviewer:f.get('reviewer'),responses})});let j=await r.json();document.getElementById('status').textContent=j.message;if(r.ok){localStorage.removeItem(storage);document.querySelector('button').disabled=true}};</script></html>'''
class Handler(BaseHTTPRequestHandler):
 def do_GET(self):
  if self.path=='/health':data=json.dumps({'ready':(L/'evals/dev_public_pairs_v004.json').exists(),'submissions':len(list((L/'evals/dev_human_submissions').glob('*.json'))) if (L/'evals/dev_human_submissions').exists() else 0}).encode();typ='application/json'
  elif self.path in ['/','/blind']:data=page().encode();typ='text/html; charset=utf-8'
  else:self.send_error(404);return
  self.send_response(200);self.send_header('Content-Type',typ);self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
 def do_POST(self):
  if self.path!='/api/review' or self.headers.get('Origin') not in [None,f'http://127.0.0.1:{PORT}']:self.send_error(403);return
  try:
   n=int(self.headers.get('Content-Length','0'))
   if not 0<n<60000:raise ValueError('Invalid request length')
   j=json.loads(self.rfile.read(n));pairs=read(L/'evals/dev_public_pairs_v004.json');rs=j['responses']
   if not j.get('reviewer','').strip() or len(rs)!=len(pairs) or {x['pair_id'] for x in rs}!={x['pair_id'] for x in pairs}:raise ValueError('Please complete all 8 pairs')
   for x in rs:
    if any(x[k] not in CHOICES for k in ['overall','information_gain','save_share','comment_potential','naturalness']) or any(x[k] not in ['Yes','No','Uncertain'] for k in ['publish_A','publish_B']):raise ValueError('Please complete every choice in each pair')
   if any(v not in DIAGNOSTICS for x in rs for v in x.get('diagnostics',[])):raise ValueError('Invalid diagnostic label')
   j.update(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),loop_version='v004',source='genuine browser submission',language='English (the reviewer originally read a Chinese translation; this package is English-only)')
   with LOCK:
    dest=L/'evals/dev_human_submissions';dest.mkdir(exist_ok=True);(dest/(str(time.time_ns())+'_v004.json')).write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8')
   result={'message':'Genuine feedback saved. Please reply "submitted" in the conversation and I will continue with selector calibration and the component experiment.'};status=200
  except Exception as e:result={'message':str(e)};status=400
  data=json.dumps(result,ensure_ascii=False).encode();self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
if __name__=='__main__':print('Round3 blind review http://127.0.0.1:8881/',flush=True);ThreadingHTTPServer(('127.0.0.1',PORT),Handler).serve_forever()
