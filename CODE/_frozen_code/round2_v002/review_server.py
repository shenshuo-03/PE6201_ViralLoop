"""Local genuine-human naturalness gate; no simulated votes or hidden scores."""
from runtime import *
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from html import escape
def page():
    items=read(LOOP/'evals/naturalness_user_review_v002.json');cards=[]
    for i,c in enumerate(items,1):
        cards.append(f'''<section><p class="tag">样例{i} · {escape(c['type'])} · 素材日期 {escape(c['source_date'])}</p><h2>{escape(c['title_zh'])}</h2><p class="body">{escape(c['body_zh'])}</p><p><a href="{escape(c['source_url'],quote=True)}" target="_blank">素材原帖</a></p><details><summary>查看英文发布稿</summary><h3>{escape(c['title_en'])}</h3><p class="body">{escape(c['body_en'])}</p></details><label>这篇像真实社区里值得发布的帖子吗？<select name="{c['id']}" required><option value="">请选择</option><option value="yes">是，自然且有信息价值</option><option value="no">否，明显需要修改</option><option value="unsure">不确定</option></select></label><label>最需要改的地方（可选）<textarea name="note_{c['id']}" rows="2"></textarea></label></section>''')
    return '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ViralLoop 1.1 · 三篇样例验收</title><style>body{font-family:system-ui,"Microsoft YaHei",sans-serif;background:#f5f6f8;color:#202c3b;margin:0}main{max-width:850px;margin:35px auto;padding:20px}section{background:white;padding:25px;margin:24px 0;border:1px solid #d9dfe7;border-radius:12px}.body{white-space:pre-wrap;line-height:1.9}h1,h2{line-height:1.5}.tag{color:#65758a;font-size:13px}label{display:block;margin-top:20px}select,textarea,input{display:block;box-sizing:border-box;width:100%;padding:12px;margin-top:8px;border:1px solid #aeb9c8;border-radius:6px;font:inherit}button{padding:15px 24px;border:0;background:#2456a4;color:white;border-radius:8px;font:inherit;cursor:pointer}details{margin:18px 0}#status{white-space:pre-wrap}</style><main><h1>第二轮：先看这三篇是否值得发布</h1><p>这里只做自然度验收，不是正式盲评。来源是2025年真实归档帖子；生成稿是阅读来源后提出的问题或讨论，不是你本人的实测经历。中文是翻译，英文是发布稿。</p><p>请判断是否自然、具体、有价值。若不好，请直接指出；系统不会因为生成了就视为通过。</p><form id="review"><label>评审姓名<input name="reviewer" placeholder="你的姓名" required></label>'''+''.join(cards)+'''<button type="submit">保存真实反馈</button></form><p id="status"></p></main><script>document.getElementById('review').onsubmit=async e=>{e.preventDefault();let f=new FormData(e.target);let responses=['D01','D03','S01'].map(id=>({id,choice:f.get(id),note:f.get('note_'+id)}));let r=await fetch('/api/review',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({reviewer:f.get('reviewer'),responses,review_language:'Chinese translation with English original available'})});let j=await r.json();document.getElementById('status').textContent=j.message||JSON.stringify(j);if(r.ok)document.querySelector('button').disabled=true;};</script></html>'''
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        data=page().encode('utf-8');self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
    def do_POST(self):
        if self.path!='/api/review':self.send_error(404);return
        origin=self.headers.get('Origin')
        if origin and origin!='http://127.0.0.1:8878':self.send_error(403);return
        try:
            n=int(self.headers.get('Content-Length','0'))
            if n>12000:raise ValueError('Payload too large')
            j=json.loads(self.rfile.read(n));rs=j['responses']
            if not j.get('reviewer','').strip() or {x['id'] for x in rs}!={'D01','D03','S01'} or len(rs)!=3 or any(x['choice'] not in ['yes','no','unsure'] for x in rs):raise ValueError('Complete all 3 choices')
            j.update(at=now(),loop_version='v002',source='genuine browser submission');file=LOOP/'evals/human_naturalness_submissions'/f'{time.time_ns()}_v002.json';write(file,j)
            gate=read(LOOP/'results/naturalness_gate_v002.json');gate['human_pass']=all(x['choice']=='yes' for x in rs);gate['human_evidence']=str(file);gate['formal_generator_stage_allowed']=gate['automatic_pass'] and gate['human_pass'];write(LOOP/'results/naturalness_gate_v002.json',gate)
            event('human_naturalness','genuine feedback received',{'source':str(file),'passed':gate['human_pass'],'language':j.get('review_language'),'not_formal_final_blind_review':True})
            result={'saved':True,'message':'反馈已保存。请回到对话告诉我“已提交”；我会按你的真实反馈继续。'};status=200
        except Exception as exc:result={'message':str(exc)};status=400
        data=json.dumps(result,ensure_ascii=False).encode();self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
if __name__=='__main__':
    print('Review ready: http://127.0.0.1:8878',flush=True);ThreadingHTTPServer(('127.0.0.1',8878),Handler).serve_forever()
