"""Usable fact-grounded writing demo; frozen method, real guarded calls, no virality promise."""
from generation import *
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
import threading
LOCK=threading.Lock()
HTML='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ViralLoop · 社区文案生成器</title><style>body{margin:0;background:#f4f6fa;color:#203047;font:16px system-ui,"Microsoft YaHei"}main{max-width:850px;margin:35px auto;padding:24px}section{background:white;padding:24px;margin:20px 0;border-radius:12px}h1{font-size:30px}label{display:block;margin:16px 0}input,textarea{width:100%;box-sizing:border-box;padding:12px;border:1px solid #aab8c8;border-radius:6px;font:inherit}button{background:#2456a4;color:white;border:0;border-radius:6px;padding:13px 22px;font:inherit;cursor:pointer}.body{white-space:pre-wrap;line-height:1.8}.muted{color:#66758b}#result{white-space:pre-wrap;line-height:1.8}</style><main><h1>ViralLoop</h1><p>把真实素材写成自然、具体的 r/LocalLLaMA 社区讨论帖。</p><p class="muted">生成英文发布稿和中文翻译。没有测得真实爆款率；不会自动发布。需要你提供真实事实或来源，不能只给主题后编造亲测经历。</p><section><form id="writer"><label>主题<input name="topic" required maxlength="180" placeholder="例如：如何判断本地模型是否真的会推理"></label><label>真实素材 / 事实<textarea name="material" required rows="9" maxlength="12000" placeholder="粘贴实际报告或自己的素材，包含具体背景、已知事实和限制。未测过的指标不要当作结果。"></textarea></label><label>素材日期（可选）<input name="date" placeholder="例如2025-01-30；未提供时会标记未知"></label><button>生成两篇候选并检查</button></form><p id="status"></p></section><section id="result" hidden></section><script>const form=document.getElementById('writer');form.onsubmit=async e=>{e.preventDefault();let button=form.querySelector('button');button.disabled=true;document.getElementById('status').textContent='正在生成与检查，通常需要半分钟左右……';try{let r=await fetch('/api/generate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(Object.fromEntries(new FormData(form)))});let j=await r.json();if(!r.ok)throw Error(j.error);let out=document.getElementById('result');out.hidden=false;out.textContent=j.display;document.getElementById('status').textContent='完成。本次实际API成本：US$'+j.cost.toFixed(5);}catch(err){document.getElementById('status').textContent='未完成：'+err.message;}button.disabled=false;};</script></main></html>'''

def create_draft(topic,material,date='unknown'):
    frozen=read(LOOP/'configs/generator_freeze_v002.json');variant=frozen['selected_product']
    before=costs()[1];bid='L'+str(time.time_ns());phase='preflight'
    s={'brief_id':bid,'source_title':topic,'source_text':material,'source_date':date or 'unknown','source_url':'user-provided material','split':phase,'id':bid}
    write(LOOP/'sources'/f'{bid}_v002.json',s)
    ans=complete(BRIEF_PROMPT+json.dumps(s,ensure_ascii=False),GEN,'brief_builder:'+bid,2200,phase,.1);b=ans['value']
    source_norm=''.join(c.lower() for c in (topic+' '+material) if c.isalnum())
    b['facts']=[f for f in b['facts'] if ''.join(c.lower() for c in f.get('evidence_quote','') if c.isalnum()) and ''.join(c.lower() for c in f.get('evidence_quote','') if c.isalnum()) in source_norm]
    if len(b['facts'])<2:raise ValueError('素材不足以核对两条事实，请补充具体事实或原始材料')
    b.update(id=bid,split=phase,source_date=date or 'unknown',source_url='user-provided material',content_type='Discussion / Opinion')
    write(LOOP/'evals'/f'brief_{bid}_v002.json',b)
    structure=StructureRetriever().summary(b,phase) if variant=='V2' else {'summary':{}}
    # O1 is not a selectable production mode if its selector failed admission.
    if variant not in ['V0','V1','V2']:raise RuntimeError('No usable production method frozen')
    ans=generate_initial(b,variant,structure,phase);records,u=evaluate_candidates(b,ans['value']['drafts'],phase,bid+':live');chosen,path=select_candidates(b,records,phase,bid+':live')
    if not chosen:raise ValueError('两篇候选均未通过工程质量检查；不把不合格稿当成成品')
    p=chosen['draft'];z=complete('Faithfully translate this draft into plain simplified Chinese. Preserve facts and uncertainty. JSON {"title_zh":"...","body_zh":"..."}.\n'+json.dumps(p,ensure_ascii=False),INTERNALS[0],'translate:'+bid,1300,phase)['value']
    display=z['title_zh']+'\n\n'+z['body_zh']+'\n\n——英文发布稿——\n\n'+p['title']+'\n\n'+p['body']+'\n\n方法：'+variant+'；反馈改写关闭。质量检查是工程筛查，仍需你确认事实和发布价值。'
    rec={'at':now(),'brief':b,'candidates':records,'selected':chosen,'translation':z,'method':variant,'display':display,'cost':costs()[1]-before,'external_judge_used':False,'not_final_experiment_data':True};write(LOOP/'results/live_runs'/f'{bid}_v002.json',rec);return rec

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        data=HTML.encode();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
    def do_POST(self):
        if self.path!='/api/generate':self.send_error(404);return
        if self.headers.get('Origin') not in [None,'http://127.0.0.1:8879']:self.send_error(403);return
        try:
            n=int(self.headers.get('Content-Length','0'))
            if n>60000:raise ValueError('输入太长')
            j=json.loads(self.rfile.read(n));topic=j.get('topic','').strip();material=j.get('material','').strip()
            if not topic or len(material)<100 or len(material)>12000:raise ValueError('请输入主题和至少100字符的具体素材，最多12000字符')
            if not LOCK.acquire(blocking=False):raise ValueError('上一条还在生成，请稍后再试')
            try:r=create_draft(topic,material,j.get('date',''))
            finally:LOCK.release()
            result={'display':r['display'],'cost':r['cost']};status=200
        except Exception as exc:result={'error':str(exc)};status=400
        data=json.dumps(result,ensure_ascii=False).encode();self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)

if __name__=='__main__':print('ViralLoop product: http://127.0.0.1:8879',flush=True);ThreadingHTTPServer(('127.0.0.1',8879),Handler).serve_forever()
