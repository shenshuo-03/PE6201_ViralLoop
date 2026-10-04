"""Existing local review pattern adapted for v003; no model labels exposed."""
from pathlib import Path
import json,time,datetime,threading
from html import escape
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
L=Path(__file__).resolve().parents[1];LOCK=threading.Lock();PORT=8881
CHOICES={'A':'A更值得发','B':'B更值得发','Tie':'差不多','Both unacceptable':'两个都不值得发','Uncertain':'看不懂／无法判断'}
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def select(name,options):return '<select name="'+escape(name)+'" required><option value="">请选择</option>'+''.join('<option value="'+escape(k)+'">'+escape(v)+'</option>' for k,v in options.items())+'</select>'
def page():
 pairs=read(L/'evals/dev_public_pairs_v003.json');cards=[]
 for i,p in enumerate(pairs,1):
  bid=p['pair_id'];task=p['task_zh'];card=f'<section><h2>第{i}组</h2><aside><b>假设用户任务</b><p>目标：{escape(task["goal"])}</p><p>决策：{escape(task["decision"])}</p><p>希望获得的帮助：{escape(task["desired_help"])}</p><p>历史资料日期：{escape(p["source_date"])}。场景是受控假设；历史测试不代表发帖者亲测。</p></aside>'
  for lab in ['A','B']:
   d=p[lab];en=p['english_'+lab];card+=f'<h3>{lab} · {escape(d["title"])}</h3><div class="body">{escape(d["body"])}</div><details><summary>查看英文原稿</summary><div class="body">{escape(en["title"]+chr(10)+en["body"])}</div></details>'
  card+='<label>如果只能发布一篇，你如何选择？'+select(bid+'_overall',CHOICES)+'</label>'
  for lab in ['A','B']:card+='<label>'+lab+'本身是否值得发布？'+select(bid+'_publish_'+lab,{'Yes':'可发','No':'不可发','Uncertain':'无法判断'})+'</label>'
  for k,word in [('naturalness','哪篇更自然？'),('motivation','哪篇发帖目的更清楚？'),('worth_replying','哪篇更值得读或回复？')]:card+='<label>'+word+select(bid+'_'+k,CHOICES)+'</label>'
  card+='<label>主要问题（可选）<textarea name="'+bid+'_note" rows="2" placeholder="例如像总结、太啰嗦、缺背景、问题不明确"></textarea></label></section>';cards.append(card)
 ids=json.dumps([p['pair_id'] for p in pairs])
 return '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>第三轮中文开发盲评</title><style>body{font:16px system-ui,"Microsoft YaHei";background:#f4f6f8;color:#203047}main{max-width:850px;margin:auto;padding:24px}section{background:white;padding:24px;margin:24px 0;border-radius:12px}aside{background:#edf3fb;padding:14px;border-radius:8px}.body{white-space:pre-wrap;line-height:1.9}label{display:block;margin-top:18px}input,select,textarea{width:100%;padding:10px;box-sizing:border-box;font:inherit}button{background:#285aa5;color:white;padding:14px 24px;border:0;border-radius:8px;font:inherit}details{margin-top:12px}</style><main><h1>第三轮：8组中文开发盲评</h1><p>请按假设任务判断自然性和发布价值；无需判断技术事实。可以选“两个都不值得发”或“无法判断”，不用勉强选赢家。中文忠实翻译，英文可展开。没有显示版本或模型分数。</p><form id="review"><label>评审姓名<input name="reviewer" required></label>'''+''.join(cards)+'''<button>保存真实评价</button></form><p id="status"></p></main><script>let ids='''+ids+''';let form=document.getElementById('review'),storage='viralloop-v003-dev-draft';try{let d=JSON.parse(localStorage.getItem(storage)||'{}');for(let [k,v] of Object.entries(d)){if(form.elements[k])form.elements[k].value=v}}catch(e){}form.onchange=()=>localStorage.setItem(storage,JSON.stringify(Object.fromEntries(new FormData(form))));form.onsubmit=async e=>{e.preventDefault();let f=new FormData(form);let fields=['overall','publish_A','publish_B','naturalness','motivation','worth_replying','note'];let responses=ids.map(id=>Object.fromEntries([['pair_id',id],...fields.map(k=>[k,f.get(id+'_'+k)])]));let r=await fetch('/api/review',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({reviewer:f.get('reviewer'),responses})});let j=await r.json();document.getElementById('status').textContent=j.message;if(r.ok){localStorage.removeItem(storage);document.querySelector('button').disabled=true}};</script></html>'''
class Handler(BaseHTTPRequestHandler):
 def do_GET(self):
  if self.path=='/health':data=json.dumps({'ready':(L/'evals/dev_public_pairs_v003.json').exists(),'submissions':len(list((L/'evals/dev_human_submissions').glob('*.json'))) if (L/'evals/dev_human_submissions').exists() else 0}).encode();typ='application/json'
  elif self.path in ['/','/blind']:data=page().encode();typ='text/html; charset=utf-8'
  else:self.send_error(404);return
  self.send_response(200);self.send_header('Content-Type',typ);self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
 def do_POST(self):
  if self.path!='/api/review' or self.headers.get('Origin') not in [None,f'http://127.0.0.1:{PORT}']:self.send_error(403);return
  try:
   n=int(self.headers.get('Content-Length','0'))
   if not 0<n<60000:raise ValueError('请求长度无效')
   j=json.loads(self.rfile.read(n));pairs=read(L/'evals/dev_public_pairs_v003.json');rs=j['responses']
   if not j.get('reviewer','').strip() or len(rs)!=len(pairs) or {x['pair_id'] for x in rs}!={x['pair_id'] for x in pairs}:raise ValueError('请完整填写8组')
   for x in rs:
    if any(x[k] not in CHOICES for k in ['overall','naturalness','motivation','worth_replying']) or any(x[k] not in ['Yes','No','Uncertain'] for k in ['publish_A','publish_B']):raise ValueError('请完成每组选择')
   j.update(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),loop_version='v003',source='genuine browser submission',language='Chinese faithful translations; English available')
   with LOCK:
    dest=L/'evals/dev_human_submissions';dest.mkdir(exist_ok=True);(dest/(str(time.time_ns())+'_v003.json')).write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8')
   result={'message':'真实评价已保存。请回到对话回复“已提交”，我会继续Selector校准与组件实验。'};status=200
  except Exception as e:result={'message':str(e)};status=400
  data=json.dumps(result,ensure_ascii=False).encode();self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
if __name__=='__main__':print('Round3 blind review http://127.0.0.1:8881/',flush=True);ThreadingHTTPServer(('127.0.0.1',PORT),Handler).serve_forever()
