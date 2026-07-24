#!/usr/bin/env python3
# Build (multi-project): packs/<proj>/<version>/{appdata.json,pack.json} + template.html
#   -> <outdir>/index.html (แอปของแต่ละ project, เวอร์ชันล่าสุด)
#   -> index.html (Portal รวมทุก project)
#   -> ../<root_copy> (สำเนา build ที่ root โฟลเดอร์ ถ้า pack กำหนดไว้ — ใช้เปิด local/Drive)
# กติกา: แก้แอปที่ template.html เท่านั้น · เพิ่มงานตรวจ = เพิ่มโฟลเดอร์ pack ใหม่
import os, json, glob, html

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
tpl = open(os.path.join(HERE, 'template.html'), encoding='utf-8').read()
if '__DATA__' not in tpl:
    raise SystemExit('template.html ไม่มี __DATA__ placeholder — ห้ามแก้ไฟล์ build แล้วย้อนกลับมาทับ template')

packs = []
for pj in sorted(glob.glob(os.path.join(HERE, 'packs', '*', '*', 'pack.json'))):
    cfg = json.load(open(pj, encoding='utf-8'))
    cfg['_dir'] = os.path.dirname(pj)
    # ถ้ามี checklist.xlsx และใหม่กว่า appdata.json -> แปลงอัตโนมัติ (เฟส 2)
    xl = os.path.join(cfg['_dir'], 'checklist.xlsx')
    aj = os.path.join(cfg['_dir'], 'appdata.json')
    if os.path.exists(xl) and (not os.path.exists(aj) or os.path.getmtime(xl) > os.path.getmtime(aj)):
        import xlsx2pack; xlsx2pack.convert(xl, aj)
    packs.append(cfg)
if not packs:
    raise SystemExit('ไม่พบ pack ใด ๆ ใน packs/*/*/pack.json')

# ต่อ project ใช้เวอร์ชันล่าสุด (เรียงตามชื่อ version)
latest = {}
for c in sorted(packs, key=lambda c: (c['project'], c['version'])):
    latest[c['project']] = c

built = []
for proj, cfg in latest.items():
    data = open(os.path.join(cfg['_dir'], 'appdata.json'), encoding='utf-8').read().replace('</', '<\\/')
    out = (tpl.replace('__PTITLE__', cfg['ptitle'])
              .replace('__HTITLE__', cfg['htitle'])
              .replace('__HSUB__', cfg['hsub'])
              .replace('__AUDIT_ID__', cfg['audit_id'])
              .replace('__CARPFX__', cfg.get('car_prefix', 'CAR'))
              .replace('__DATA__', data))
    outdir = os.path.join(HERE, cfg['outdir'])
    os.makedirs(outdir, exist_ok=True)
    dst = os.path.join(outdir, 'index.html')
    open(dst, 'w', encoding='utf-8').write(out)
    print('built:', dst, os.path.getsize(dst), 'bytes')
    if cfg.get('root_copy'):
        rc = os.path.join(ROOT, cfg['root_copy'])
        open(rc, 'w', encoding='utf-8').write(out)
        print('copied:', rc)
    built.append(cfg)

# ---------- Portal (v2: login + live progress + Audit Plan + notification) ----------
import re as _re
_m = _re.search(r'const FIREBASE_CONFIG = (\{[\s\S]*?\});', tpl)
FBCFG = _m.group(1) if _m else 'null'

def _count(d):
    n = 0
    for m in d['modules']:
        for p in m['parts']:
            for s2 in p['secs']:
                for g in s2['groups']:
                    n += len(g['items'])
    return n

plist = []
for c in built:
    d = json.load(open(os.path.join(c['_dir'], 'appdata.json'), encoding='utf-8'))
    plist.append({'proj': c['project'], 'outdir': c['outdir'], 'name': c['name'],
                  'desc': c['desc'], 'code': c['doc_code'], 'ver': c['version'],
                  'aid': c['audit_id'], 'total': _count(d)})

PORTAL = r'''<!DOCTYPE html><html lang="th"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>D-0507 Audit Portal</title>
<style>
:root{--navy:#1F3864;--blue:#2E75B6;--green:#1E7B34;--amber:#9C6500;--red:#C00000;}
*{box-sizing:border-box;margin:0;padding:0;}
body{font-family:-apple-system,'Segoe UI','Noto Sans Thai',Arial,sans-serif;background:#eef2f7;color:#1a1a2a;min-height:100vh;}
header{background:var(--navy);color:#fff;padding:18px 26px 14px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;}
header h1{font-size:20px;}
header .sub{font-size:12.5px;opacity:.85;margin-top:3px;}
#authbox{font-size:13px;text-align:right;}
#authbox button{min-height:38px;border-radius:8px;border:none;background:#fff;color:var(--navy);font-weight:bold;padding:6px 14px;cursor:pointer;margin-left:6px;}
main{max-width:1150px;margin:0 auto;padding:22px 16px 60px;}
h3.sec{color:var(--navy);font-size:16px;margin:18px 0 8px;}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:14px;}
.pcard{display:block;background:#fff;border:1px solid #d8dfe8;border-radius:12px;padding:16px;text-decoration:none;color:inherit;transition:box-shadow .15s;}
.pcard:hover{box-shadow:0 6px 22px rgba(31,56,100,.18);}
.pc-code{font-size:11.5px;color:var(--blue);font-weight:bold;}
.pcard h2{font-size:16.5px;color:var(--navy);margin:5px 0 5px;}
.pcard p{font-size:12.5px;color:#5a6675;}
.bar{height:9px;background:#e4eaf2;border-radius:5px;margin-top:10px;overflow:hidden;}
.bar i{display:block;height:100%;background:var(--blue);border-radius:5px;}
.pc-stat{font-size:12px;color:#5a6675;margin-top:5px;}
.pc-stat b.g{color:var(--red);} .pc-stat b.c{color:var(--amber);}
.banner{border-radius:10px;padding:10px 14px;font-size:13.5px;margin-bottom:8px;border:1px solid;}
.banner.warn{background:#FFF4E5;border-color:#F0C36D;color:#7a5200;}
.banner.late{background:#FDECEC;border-color:#E4A6A6;color:#8f1414;}
table.plan{width:100%;border-collapse:collapse;background:#fff;font-size:13px;}
table.plan th{background:var(--navy);color:#fff;padding:8px;font-size:12px;text-align:left;}
table.plan td{border:1px solid #dde4ee;padding:6px;vertical-align:middle;}
table.plan input,table.plan select{width:100%;min-height:36px;border:1px solid #c8d2e0;border-radius:6px;padding:4px 7px;font-family:inherit;font-size:13px;}
.pill{display:inline-block;border-radius:10px;padding:2px 10px;font-size:11.5px;font-weight:bold;white-space:nowrap;}
.pill.plan{background:#e7ecf3;color:#456;} .pill.run{background:#dbe9ff;color:#1d5eb8;}
.pill.soon{background:#FFF0D5;color:var(--amber);} .pill.late{background:#FBE0E0;color:var(--red);}
.pill.done{background:#DFF2E3;color:var(--green);}
.pbtn{min-height:36px;border-radius:7px;border:1px solid var(--blue);background:#fff;color:var(--blue);font-size:12px;font-weight:bold;padding:4px 9px;cursor:pointer;margin:2px 2px 2px 0;}
.pbtn.x{border-color:var(--red);color:var(--red);}
.pbtn.g{background:var(--blue);color:#fff;}
.note{background:#fff;border-left:4px solid var(--blue);border-radius:8px;padding:11px 15px;font-size:12.5px;color:#445;margin-top:22px;}
#loginui{background:#fff;border:1px solid #d8dfe8;border-radius:12px;padding:22px;max-width:420px;margin:30px auto;text-align:center;}
#loginui input{width:100%;min-height:42px;border:1px solid #c8d2e0;border-radius:8px;padding:8px 10px;margin-top:8px;font-size:14px;}
#loginui button{width:100%;min-height:44px;border-radius:8px;border:none;background:var(--navy);color:#fff;font-weight:bold;font-size:14px;margin-top:10px;cursor:pointer;}
#loginui button.alt{background:#fff;color:var(--blue);border:1px solid var(--blue);}
.gwrap{overflow-x:auto;background:#fff;border:1px solid #d8dfe8;border-radius:10px;margin-top:12px;-webkit-overflow-scrolling:touch;}
.gantt{position:relative;min-width:100%;}
.grow{display:flex;align-items:stretch;border-top:1px solid #eef2f7;}
.glab{flex:0 0 190px;position:sticky;left:0;background:#fff;z-index:3;border-right:1px solid #d8dfe8;padding:7px 10px;font-size:12px;color:var(--navy);}
.glab b{display:block;font-size:12.5px;}
.gtl{position:relative;height:44px;flex:0 0 auto;}
.gbar{position:absolute;top:9px;height:24px;border-radius:6px;font-size:10.5px;font-weight:bold;color:#fff;display:flex;align-items:center;padding:0 7px;white-space:nowrap;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.18);}
.gbar.plan{background:#8fa3bd;} .gbar.run{background:var(--blue);}
.gbar.soon{background:#E39B17;} .gbar.late{background:var(--red);} .gbar.done{background:var(--green);}
.gmonth{position:absolute;top:0;bottom:0;border-left:1px solid #e4eaf2;}
.gmlab{flex:0 0 auto;position:relative;height:26px;background:#F0F4F8;border-bottom:1px solid #d8dfe8;}
.gmlab span{position:absolute;top:4px;font-size:11px;font-weight:bold;color:var(--navy);padding-left:6px;border-left:1px solid #c9d6e8;}
.gtoday{position:absolute;top:0;bottom:0;width:2px;background:var(--red);z-index:2;}
.gtoday i{position:absolute;top:2px;left:3px;font-size:9.5px;color:var(--red);font-style:normal;white-space:nowrap;}
.sigwrap{position:fixed;inset:0;background:rgba(10,20,40,.55);display:flex;align-items:center;justify-content:center;z-index:99;}
.sigbox{background:#fff;border-radius:12px;padding:16px;max-width:580px;width:94%;box-shadow:0 10px 40px rgba(0,0,0,.3);}
.sigbox canvas{border:1.5px dashed #8fa3bd;border-radius:8px;touch-action:none;width:100%;height:170px;background:#fff;display:block;margin-top:6px;}
.sigbox input{width:62%;min-height:36px;border:1px solid #c8d2e0;border-radius:7px;padding:5px 9px;}
.sgb{min-height:32px;border-radius:6px;border:1px solid #c8d2e0;background:#fff;font-size:11px;padding:2px 7px;cursor:pointer;margin:3px 2px 0 0;}
.sgb.ok{border-color:var(--green);color:var(--green);font-weight:bold;}
footer{text-align:center;color:#98a4b4;font-size:11.5px;padding:18px;}
@media(max-width:700px){table.plan{font-size:12px;} main{padding:14px 8px 50px;}}
</style></head><body>
<header>
  <div><h1>D-0507 FLIGHT TRAINING — AUDIT PORTAL</h1>
  <div class="sub">ศูนย์กลางงานตรวจสอบ · Compliance Monitoring (OMM Section 5)</div></div>
  <div id="authbox"></div>
</header>
<main>
  <div id="banners"></div>
  <div id="loginui" class="hide" style="display:none">
    <b style="color:var(--navy);font-size:16px">เข้าสู่ระบบ Audit Portal</b>
    <button onclick="loginGoogle()">🔵 เข้าสู่ระบบด้วย Google</button>
    <input id="lp_em" type="email" placeholder="อีเมล">
    <input id="lp_pw" type="password" placeholder="รหัสผ่าน">
    <button class="alt" onclick="loginEmail()">เข้าสู่ระบบด้วยอีเมล</button>
    <div style="font-size:11.5px;color:#98a4b4;margin-top:8px">อีเมลต้องอยู่ในรายชื่อทีมตรวจ (Security Rules)</div>
  </div>
  <div id="content" style="display:none">
    <h3 class="sec">🔎 งานตรวจสอบ — รอบที่กำลังดำเนินการ / ใกล้ถึงกำหนด (ภายใน 30 วัน)</h3>
    <div class="grid" id="cards"></div>
    <h3 class="sec">📅 Audit Plan ประจำปี
      <select id="planyear" onchange="loadPlan()" style="min-height:36px;border-radius:7px;border:1px solid #c8d2e0;padding:3px 8px;font-size:14px"></select>
      <span id="plansaved" style="font-size:12px;color:var(--green);font-weight:normal"></span>
    </h3>
    <table class="plan" id="plantab"></table>
    <div style="margin-top:8px">
      <button class="pbtn" onclick="addRow()">➕ เพิ่มรายการตรวจ</button>
      <button class="pbtn g" onclick="savePlan()">💾 บันทึกแผน</button>
    </div>
    <h3 class="sec" style="margin-top:20px">🗓 ปฏิทินการตรวจ 12 เดือน (Gantt)</h3>
    <div class="gwrap" id="gwrap"><div class="gantt" id="gantt"></div></div>
    <h3 class="sec" style="margin-top:24px">📚 กรอบการตรวจ / Checklists</h3>
    <div class="note" style="margin-top:6px">กรอบการตรวจคือแม่แบบ — <b>ไม่ใช่ที่เปิดงานตรวจ</b> · จะตรวจอะไร ให้เพิ่มรอบใน Audit Plan แล้วกด ▶ จากแผน/การ์ดด้านบน</div>
    <div id="cklist" style="display:flex;flex-wrap:wrap;gap:10px;margin-top:8px"></div>
    <div class="note"><b>การแจ้งการตรวจ (Audit Notification):</b> ปุ่ม 📄 ในแต่ละแถว = หนังสือแจ้งการตรวจอย่างเป็นทางการ (พิมพ์/บันทึก PDF) ·
    ✉ = ร่างอีเมลแจ้งผู้รับการตรวจ · 📅 = ไฟล์ลงปฏิทิน (.ics) ·
    สถานะคำนวณอัตโนมัติจากความคืบหน้าจริงของแต่ละงาน · แจ้งเตือนล่วงหน้า 14 วันที่แถบด้านบน</div>
  </div>
</main>
<footer>D-0507 Flight Training Co., Ltd. · Internal Audit System · D-0507-ANF-001 (DRAFT)</footer>
<script src="https://www.gstatic.com/firebasejs/10.12.2/firebase-app-compat.js"></script>
<script src="https://www.gstatic.com/firebasejs/10.12.2/firebase-auth-compat.js"></script>
<script src="https://www.gstatic.com/firebasejs/10.12.2/firebase-firestore-compat.js"></script>
<script>
"use strict";
const CFG=@@FBCFG@@;
const PACKS=@@PACKS@@;
firebase.initializeApp(CFG);
const db=firebase.firestore();
let USER=null, SUMS={}, PLAN=[], PLANYEAR=(new Date()).getFullYear(), planUnsub=null;
const esc=s=>String(s==null?'':s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const today=()=>new Date().toISOString().slice(0,10);
function loginGoogle(){ firebase.auth().signInWithPopup(new firebase.auth.GoogleAuthProvider()).catch(e=>alert(e.message)); }
function loginEmail(){ firebase.auth().signInWithEmailAndPassword(document.getElementById('lp_em').value.trim(),document.getElementById('lp_pw').value).catch(e=>alert(e.message)); }
firebase.auth().onAuthStateChanged(u=>{
  USER=u;
  document.getElementById('loginui').style.display=u?'none':'block';
  document.getElementById('content').style.display=u?'block':'none';
  document.getElementById('authbox').innerHTML=u?`${esc(u.displayName||u.email)} <button onclick="firebase.auth().signOut()">ออก</button>`:'';
  if(u){ initYears(); loadPlan(); renderCk(); }
});
function renderCards(){
  const el=document.getElementById('cards'); if(!el) return;
  const rounds=PLAN.map((r,i)=>({r,i})).filter(({r})=>{
    if(r.done||!r.start) return false;
    const d=(new Date(r.start)-new Date(today()))/86400000;
    return d<=30;                              // ภายใน 30 วัน รวมที่เริ่มแล้ว/เลยกำหนด
  });
  if(!rounds.length){
    el.innerHTML='<div class="note" style="margin:0">ยังไม่มีรอบตรวจในกรอบ 30 วัน — วางแผนรอบตรวจในตาราง Audit Plan ด้านล่าง แล้วการ์ดจะปรากฏเมื่อใกล้ถึงกำหนด</div>';
    return;
  }
  el.innerHTML=rounds.map(({r,i})=>{
    const p=PACKS.find(x=>x.proj===r.proj)||{};
    const id=rid(r); watchRound(id);
    const su=SUMS[id];
    const pct=su?Math.round(100*su.done/(su.total||p.total||1)):0;
    const [cls,txt]=rowStatus(r);
    return `<div class="pcard" style="cursor:default">
      <div class="pc-code">${esc(r.ref||'')} · ${esc(p.code||'')} ${esc(p.ver||'')}</div>
      <h2>${esc(p.name||r.proj)}</h2>
      <p>${esc(r.label||'')} · ${esc(r.start||'')} → ${esc(r.end||r.start||'')} · Lead: ${esc(r.lead||'-')}</p>
      <div style="margin-top:6px"><span class="pill ${cls}">${txt}</span></div>
      <div class="bar"><i style="width:${pct}%"></i></div>
      <div class="pc-stat">ตรวจแล้ว <b>${su?su.done:0}/${su?(su.total||p.total):p.total}</b> (${pct}%) · GAP <b class="g">${su?su.gap:0}</b> · CAR ค้าง <b class="c">${su?su.carOpen:0}</b>/${su?su.car:0}</div>
      <a href="${p.outdir}/?audit=${encodeURIComponent(id)}" style="display:inline-block;margin-top:10px;background:var(--blue);color:#fff;font-weight:bold;font-size:13.5px;border-radius:8px;padding:8px 16px;text-decoration:none">▶ ${pct>0?'เข้าตรวจต่อ':'เริ่มตรวจ'}</a>
    </div>`;
  }).join('');
}
function renderCk(){
  const el=document.getElementById('cklist'); if(!el) return;
  el.innerHTML=PACKS.map(p=>`<div style="background:#fff;border:1px solid #d8dfe8;border-radius:10px;padding:11px 14px;font-size:12.5px;min-width:250px">
    <b style="color:var(--navy)">${esc(p.name)}</b><br>
    <span style="color:#7a8798">${esc(p.code)} · ${esc(p.ver)} · ${p.total} ข้อ</span><br>
    <a href="${p.outdir}/?view=1" class="pbtn" style="display:inline-block;text-decoration:none;margin-top:6px">👁 เปิดดูรายการตรวจ</a>
    <button class="pbtn" onclick="planRound('${p.proj}')">＋ วางแผนรอบตรวจ</button>
  </div>`).join('');
}
function initYears(){
  const sel=document.getElementById('planyear'); if(sel.options.length) return;
  const y=(new Date()).getFullYear();
  for(let i=y-1;i<=y+2;i++){ const o=document.createElement('option'); o.value=i; o.textContent=i; if(i===y)o.selected=true; sel.appendChild(o); }
}
function roundRef(){                       // ออกเลขอ้างอิงรอบ AP-YYYY-nn
  let mx=0; PLAN.forEach(r=>{const m=(r.ref||'').match(/(\d+)$/); if(m) mx=Math.max(mx,+m[1]);});
  return 'AP-'+PLANYEAR+'-'+String(mx+1).padStart(2,'0');
}
function rid(r){ return r.proj+'-'+((r.ref||'').replace(/^AP-/i,'').toLowerCase()||'x'); }
function ackList(r){ return (r.ackList&&r.ackList.length)?r.ackList:(r.ackEmail?[r.ackEmail]:[]); }
function ackSigs(r){ if(!r.ackSigs){ r.ackSigs=[]; if(r.sg&&r.sg.ack) r.ackSigs.push({email:(r.ackEmail||'').toLowerCase(), d:r.sg.ack.d, n:r.sg.ack.n, dt:r.sg.ack.dt}); } return r.ackSigs; }
function ackOf(r,email){ return ackSigs(r).find(a=>a.email===(email||'').toLowerCase()); }
function ackDone(r){ const L=ackList(r); return L.length&&L.every(e=>ackOf(r,e)); }
function ackCount(r){ const L=ackList(r); return [L.filter(e=>ackOf(r,e)).length, L.length]; }
const watched=new Set();
function watchRound(id){
  if(watched.has(id)) return; watched.add(id);
  db.collection('audits').doc(id).onSnapshot(d=>{ SUMS[id]=(d.exists&&d.data().sum)||null; renderCards(); },e=>console.error(e));
}
function loadPlan(){
  PLANYEAR=+document.getElementById('planyear').value||PLANYEAR;
  if(planUnsub) planUnsub();
  planUnsub=db.collection('plans').doc(String(PLANYEAR)).onSnapshot(d=>{
    PLAN=(d.exists&&d.data().rows)||[];
    PLAN.forEach(r=>{ if(!r.ref) r.ref=roundRef(); });   // แถวเก่าก่อนมีระบบ ref
    renderPlan();
  },e=>console.error(e));
}
function rowStatus(r){
  if(r.done) return ['done','✅ เสร็จสิ้น'];
  const p=PACKS.find(x=>x.proj===r.proj); const s=p&&SUMS[p.aid];
  const pct=s?Math.round(100*s.done/(s.total||p.total||1)):0;
  if(pct>0&&pct<100) return ['run','🔵 กำลังตรวจ '+pct+'%'];
  if(r.end&&r.end<today()) return ['late','🔴 เลยกำหนด'];
  if(r.start){ const d=(new Date(r.start)-new Date(today()))/86400000;
    if(d<=14&&d>=0) return ['soon','🟠 ใกล้ถึงกำหนด ('+Math.ceil(d)+' วัน)']; }
  return ['plan','⚪ วางแผนแล้ว'];
}
function renderPlan(){
  const t=document.getElementById('plantab');
  let h=`<tr><th style="width:16%">Project</th><th style="width:12%">รอบ/Label</th><th style="width:11%">เริ่ม</th><th style="width:11%">สิ้นสุด</th><th style="width:11%">Lead Auditor</th><th style="width:13%">ผู้รับการตรวจ</th><th>สถานะ</th><th style="width:15%">เอกสารแจ้ง</th><th style="width:4%"></th></tr>`;
  PLAN.forEach((r,i)=>{
    const [cls,txt]=rowStatus(r);
    h+=`<tr>
      <td><span style="font-size:11px;font-weight:bold;color:var(--blue)">${esc(r.ref||'')}</span>
        <select onchange="PLAN[${i}].proj=this.value">${PACKS.map(p=>`<option value="${p.proj}"${r.proj===p.proj?' selected':''}>${esc(p.name)}</option>`).join('')}</select>
        ${r.start?`<a class="pbtn" style="display:inline-block;text-decoration:none;margin-top:4px" href="${(PACKS.find(x=>x.proj===r.proj)||{}).outdir}/?audit=${encodeURIComponent(rid(r))}">${r.done?'📖 ดูผลรอบนี้':'▶ เปิดงานตรวจ'}</a>`:''}</td>
      <td><input value="${esc(r.label||'')}" placeholder="เช่น Q4 รอบหลัก" onchange="PLAN[${i}].label=this.value"></td>
      <td><input type="date" value="${esc(r.start||'')}" onchange="PLAN[${i}].start=this.value"></td>
      <td><input type="date" value="${esc(r.end||'')}" onchange="PLAN[${i}].end=this.value"></td>
      <td><input value="${esc(r.lead||'')}" onchange="PLAN[${i}].lead=this.value"></td>
      <td><input value="${esc(r.auditee||'')}" placeholder="หน่วย/บริษัทที่รับการตรวจ" onchange="PLAN[${i}].auditee=this.value">
        <input value="${esc(ackList(r).join(', '))}" placeholder="อีเมลผู้ต้องรับทราบ — หลายคนคั่นด้วย ," style="margin-top:3px" onchange="PLAN[${i}].ackList=this.value.split(',').map(x=>x.trim().toLowerCase()).filter(Boolean);renderPlan()">
        ${ackList(r).length?`<span class="pill ${ackDone(r)?'done':'soon'}" style="margin-top:3px">รับทราบ ${ackCount(r)[0]}/${ackCount(r)[1]}</span>`:''}</td>
      <td><span class="pill ${cls}">${txt}</span><br><label style="font-size:11px;color:#667"><input type="checkbox" ${r.done?'checked':''} onchange="PLAN[${i}].done=this.checked;renderPlan()"> ปิดงานแล้ว</label></td>
      <td><button class="pbtn" onclick="notiLetter(${i})">📄</button><button class="pbtn" onclick="notiMail(${i})">✉</button><button class="pbtn" onclick="notiIcs(${i})">📅</button><br>
        ${['lead','cmm'].map(ro=>{const g=r.sg&&r.sg[ro];
          return `<button class="sgb${g?' ok':''}" onclick="openSigP(${i},'${ro}')">${g?'✔':'✍'} ${ro==='lead'?'Lead':'CMM'}</button>`;}).join('')}
        <button class="sgb${ackDone(r)?' ok':''}" onclick="openAckSig(${i})">${ackDone(r)?'✔':'✍'} รับทราบ ${ackList(r).length?ackCount(r)[0]+'/'+ackCount(r)[1]:''}</button></td>
      <td><button class="pbtn x" onclick="if(confirm('ลบรายการนี้?')){PLAN.splice(${i},1);renderPlan();}">✕</button></td></tr>`;
  });
  if(!PLAN.length) h+=`<tr><td colspan="9" style="color:#889;text-align:center;padding:14px">ยังไม่มีแผนของปี ${PLANYEAR} — กด "เพิ่มรายการตรวจ"</td></tr>`;
  t.innerHTML=h;
  renderBanners();
  renderGantt();
  renderCards();
  renderCk();
}
function renderGantt(){
  const G=document.getElementById('gantt'); if(!G) return;
  const PX=3;                                     // 3px ต่อวัน ≈ สัปดาห์ละ 21px
  const y=PLANYEAR;
  const jan1=new Date(y,0,1);
  const days=(new Date(y+1,0,1)-jan1)/86400000;
  const W=Math.round(days*PX);
  const doy=d=>Math.max(0,Math.min(days-1,Math.round((new Date(d)-jan1)/86400000)));
  const MTH=['ม.ค.','ก.พ.','มี.ค.','เม.ย.','พ.ค.','มิ.ย.','ก.ค.','ส.ค.','ก.ย.','ต.ค.','พ.ย.','ธ.ค.'];
  let mo='';
  for(let m=0;m<12;m++){
    const x=Math.round((new Date(y,m,1)-jan1)/86400000)*PX;
    mo+=`<span style="left:${x}px">${MTH[m]}</span>`;
  }
  let grid='';
  for(let m=0;m<12;m++){
    const x=Math.round((new Date(y,m,1)-jan1)/86400000)*PX;
    grid+=`<div class="gmonth" style="left:${x}px"></div>`;
  }
  const tNow=new Date(today());
  const todayLine=(tNow.getFullYear()===y)?`<div class="gtoday" style="left:${doy(today())*PX}px"><i>วันนี้</i></div>`:'';
  let rowsH=`<div class="grow"><div class="glab" style="background:#F0F4F8"></div><div class="gmlab" style="width:${W}px">${mo}</div></div>`;
  const withDates=PLAN.map((r,i)=>({r,i})).filter(x=>x.r.start);
  withDates.forEach(({r,i})=>{
    const p=PACKS.find(x=>x.proj===r.proj)||{};
    const [cls,txt]=rowStatus(r);
    const a=doy(r.start), b=doy(r.end||r.start);
    const left=a*PX, wdt=Math.max((b-a+1)*PX, 26);
    rowsH+=`<div class="grow"><div class="glab"><b>${esc(p.name||r.proj)}</b>${esc(r.label||'')}</div>
      <div class="gtl" style="width:${W}px">${grid}${todayLine}
        <div class="gbar ${cls}" style="left:${left}px;width:${wdt}px" title="${esc((p.name||r.proj)+' '+(r.label||''))} · ${esc(r.start)} → ${esc(r.end||r.start)} · ${txt} · Lead: ${esc(r.lead||'-')}">${esc((r.ref?r.ref+" · ":"")+(r.label||p.proj||""))}</div>
      </div></div>`;
  });
  if(!withDates.length) rowsH+=`<div class="grow"><div style="padding:14px;color:#889;font-size:12.5px">ยังไม่มีรายการที่กำหนดวันเริ่ม — กำหนดวันในตารางด้านบนแล้วแท่งจะปรากฏที่นี่</div></div>`;
  G.style.width=(190+W)+'px';
  G.innerHTML=rowsH;
  // เลื่อนให้เห็นช่วงปัจจุบันพอดี
  const wrap=document.getElementById('gwrap');
  if(wrap&&tNow.getFullYear()===y) wrap.scrollLeft=Math.max(0,doy(today())*PX-wrap.clientWidth/2+190);
}
function addRow(proj){ PLAN.push({proj:proj||PACKS[0].proj,ref:roundRef(),label:'',start:'',end:'',lead:'',auditee:'',done:false}); renderPlan(); }
function planRound(proj){ addRow(proj); document.getElementById('plantab').scrollIntoView({behavior:'smooth'}); }
function savePlan(){
  PLAN.forEach(r=>{ if(!r.ref) r.ref=roundRef(); });
  db.collection('plans').doc(String(PLANYEAR)).set({rows:PLAN,u:USER?USER.email:'',t:firebase.firestore.FieldValue.serverTimestamp()})
    .then(()=>{ const el=document.getElementById('plansaved'); el.textContent='☁ บันทึกแล้ว '+new Date().toTimeString().slice(0,5); setTimeout(()=>el.textContent='',4000); })
    .catch(e=>alert('บันทึกไม่สำเร็จ: '+e.message));
}
function renderBanners(){
  const B=document.getElementById('banners'); let h='';
  PLAN.forEach(r=>{
    const [cls,txt]=rowStatus(r); const p=PACKS.find(x=>x.proj===r.proj);
    if(cls==='soon') h+=`<div class="banner warn">🟠 <b>${esc(p?p.name:r.proj)}</b> ${esc(r.label||'')} — ${txt} (เริ่ม ${esc(r.start)}) · Lead: ${esc(r.lead||'-')}</div>`;
    if(cls==='late') h+=`<div class="banner late">🔴 <b>${esc(p?p.name:r.proj)}</b> ${esc(r.label||'')} — เลยกำหนด (สิ้นสุด ${esc(r.end)}) ยังไม่ปิดงาน</div>`;
    if(USER&&!r.done&&ackList(r).includes((USER.email||'').toLowerCase())&&!ackOf(r,USER.email))
      h+=`<div class="banner warn">✍ <b>คุณมีหนังสือแจ้งการตรวจรอลงนามรับทราบ</b> — ${esc(p?p.name:r.proj)} ${esc(r.ref||'')} (${esc(r.start||'')}) · กดปุ่ม "✍ รับทราบ" ในตารางแผน หรือเปิด 📄 ดูรายละเอียดก่อน</div>`;
  });
  B.innerHTML=h;
}
let SIGP=null;
const SIGP_ROLES={lead:'Lead Auditor',cmm:'Compliance Monitoring Manager',ackp:'ลงนามรับทราบการตรวจ (Acknowledgement)'};
function openSigP(i,role){
  const r=PLAN[i]; const prev=r.sg&&r.sg[role];
  const names={lead:r.lead||'',cmm:'',ackp:(USER&&(USER.displayName||USER.email))||''};
  const w=document.createElement('div'); w.className='sigwrap'; w.id='sigpwrap';
  w.innerHTML=`<div class="sigbox">
    <b style="color:var(--navy)">✍ ลงนาม — ${SIGP_ROLES[role]}</b>
    <div style="margin:8px 0">ชื่อ-นามสกุล: <input id="sgp_n" value="${esc((prev&&prev.n)||names[role]||(USER?(USER.displayName||USER.email):''))}"></div>
    <canvas id="sgp_c" width="540" height="170"></canvas>
    <div style="color:#7a8798;font-size:11px;margin-top:3px">เซ็นในกรอบด้วยนิ้ว / Apple Pencil / เมาส์</div>
    <div style="margin-top:10px;text-align:right">
      <button class="pbtn" onclick="sigPClear()">ล้าง</button>
      <button class="pbtn" onclick="document.getElementById('sigpwrap').remove()">ยกเลิก</button>
      <button class="pbtn g" onclick="sigPSave()">✔ บันทึกลายเซ็น</button>
    </div></div>`;
  document.body.appendChild(w);
  const cv=document.getElementById('sgp_c'); const ctx=cv.getContext('2d');
  ctx.lineWidth=2.2; ctx.lineCap='round'; ctx.lineJoin='round'; ctx.strokeStyle='#16305e';
  let drawing=false, drew=false;
  const pos=e=>{const b=cv.getBoundingClientRect(); return [(e.clientX-b.left)*cv.width/b.width,(e.clientY-b.top)*cv.height/b.height];};
  cv.onpointerdown=e=>{drawing=true; drew=true; cv.setPointerCapture(e.pointerId); const p=pos(e); ctx.beginPath(); ctx.moveTo(p[0],p[1]); ctx.lineTo(p[0]+.1,p[1]+.1); ctx.stroke(); e.preventDefault();};
  cv.onpointermove=e=>{if(!drawing)return; const p=pos(e); ctx.lineTo(p[0],p[1]); ctx.stroke(); e.preventDefault();};
  cv.onpointerup=cv.onpointercancel=()=>{drawing=false;};
  SIGP={i,role,cv,ctx,hasInk:()=>drew,reset:()=>{drew=false;}};
}
function openAckSig(i){
  const r=PLAN[i];
  if(!USER){ alert('เข้าสู่ระบบก่อนลงนามรับทราบ'); return; }
  const me=(USER.email||'').toLowerCase();
  const L=ackList(r);
  if(!L.length){ alert('ยังไม่ได้ระบุรายชื่อผู้ต้องรับทราบ — กรอกอีเมลในช่อง "อีเมลผู้ต้องรับทราบ" ก่อน'); return; }
  if(!L.includes(me)){
    if(!confirm('อีเมลของคุณ ('+me+') ไม่อยู่ในรายชื่อผู้ต้องรับทราบของรอบนี้\nต้องการเพิ่มตัวเองเข้ารายชื่อและลงนามรับทราบหรือไม่?')) return;
    r.ackList=[...L, me];
  }
  if(ackOf(r,me) && !confirm('คุณลงนามรับทราบไว้แล้ว — ต้องการลงนามใหม่แทนของเดิม?')) return;
  openSigP(i,'ackp');
}
function sigPClear(){ if(SIGP){ SIGP.ctx.clearRect(0,0,SIGP.cv.width,SIGP.cv.height); SIGP.reset(); } }
function sigPSave(){
  if(!SIGP) return;
  const n=(document.getElementById('sgp_n').value||'').trim();
  if(!n){ alert('กรอกชื่อผู้ลงนาม'); return; }
  if(!SIGP.hasInk()){ alert('ยังไม่ได้เซ็นในกรอบ'); return; }
  const {i,role}=SIGP;
  if(role==='ackp'){
    const me=(USER&&USER.email||'').toLowerCase();
    const arr=ackSigs(PLAN[i]).filter(a=>a.email!==me);
    arr.push({email:me, d:SIGP.cv.toDataURL('image/png'), n:n, dt:today()});
    PLAN[i].ackSigs=arr;
  } else {
    PLAN[i].sg=PLAN[i].sg||{};
    PLAN[i].sg[role]={d:SIGP.cv.toDataURL('image/png'),n:n,dt:today(),by:USER?USER.email:''};
  }
  document.getElementById('sigpwrap').remove(); SIGP=null;
  savePlan(); renderPlan();
}
function notiLetter(i){
  const r=PLAN[i]; const p=PACKS.find(x=>x.proj===r.proj)||{};
  const sg=r.sg||{};
  const full=!!(sg.lead&&sg.cmm&&ackDone(r));
  const dots='............................................';
  const sigTd=(role,fallback)=>{const g=sg[role];
    return g?`<td><img src="${g.d}" style="height:48px"><br>( ${esc(g.n)} )<br>วันที่ ${esc(g.dt)}</td>`
            :`<td style="color:#98a4b4">ยังไม่ลงนาม — ลงนามใน Portal<br>( ${esc(fallback||dots)} )<br>วันที่ ...... / ...... / ......</td>`;};
  const w=window.open('','_blank');
  w.document.write(`<!DOCTYPE html><html lang="th"><head><meta charset="UTF-8"><title>Audit Notification — ${esc(p.name||'')}</title><style>
  body{font-family:Arial,'Noto Sans Thai',sans-serif;font-size:13.3px;color:#1A1A2A;max-width:794px;margin:0 auto;padding:30px}
  table{width:100%;border-collapse:collapse} td{border:0.8px solid #000;padding:5px 9px;vertical-align:top}
  .t0 td{text-align:center;background:#1F3864;color:#fff;font-weight:bold} .t0 .co{font-size:16px;padding:8px}
  .t1 td{background:#2E75B6;color:#fff;font-size:12.7px;font-weight:bold}
  td.l{background:#F0F4F8;font-weight:bold;color:#1F3864;width:22%;font-size:12.7px}
  .sig td{text-align:center;height:90px;vertical-align:bottom;padding-bottom:10px;line-height:1.9}
  .sig td.h{background:#D6E4F7;font-weight:bold;color:#1F3864;height:auto;vertical-align:middle}
  p.b{margin:12px 0;line-height:1.7} .np{margin-top:14px}
  @media print{.np{display:none}}</style></head><body>
  <table class="t0"><tr><td class="co">D-0507 FLIGHT TRAINING CO., LTD.</td></tr>
  <tr><td>AUDIT NOTIFICATION<br><span style="font-size:12px;font-weight:normal">หนังสือแจ้งการตรวจติดตามภายใน</span></td></tr></table>
  <table class="t1"><tr><td>Form: D-0507-ANF-001 (DRAFT)</td><td>ISSUE NO. 01/REVISION NO. 00</td><td>OMM Ref: Section 5 – Compliance Monitoring</td></tr></table>
  <p class="b">เรียน&nbsp; <b>${esc(r.auditee||'.....................................................')}</b><br>
  ตามแผนการตรวจติดตามภายในประจำปี ${PLANYEAR} ของ D-0507 Flight Training Co., Ltd.
  ขอแจ้งกำหนดการตรวจสอบ ดังนี้</p>
  <table>
  <tr><td class="l">Audit</td><td>${esc(p.name||'')} (${esc(p.code||'')} · ${esc(p.ver||'')})</td></tr>
  <tr><td class="l">รอบ / Scope</td><td>${esc(r.label||'-')} ${esc(r.scope||'')}</td></tr>
  <tr><td class="l">วันที่ตรวจ</td><td>${esc(r.start||'..........')} ถึง ${esc(r.end||'..........')}</td></tr>
  <tr><td class="l">Lead Auditor</td><td>${esc(r.lead||'-')}</td></tr>
  <tr><td class="l">เกณฑ์การตรวจ</td><td>${esc(p.code||'')} · ข้อกำหนด/คู่มือที่เกี่ยวข้อง และสัญญา (ถ้ามี)</td></tr>
  <tr><td class="l">การเตรียมการ</td><td>ขอให้จัดเตรียมเอกสาร บุคลากร และการเข้าถึงสถานที่/ระบบที่เกี่ยวข้องตามขอบเขตข้างต้น
  ผลการตรวจที่เป็นข้อบกพร่องจะออกเป็น CAR (D-0507-CAR-001) ซึ่งต้องตอบกลับภายในกำหนด</td></tr></table>
  ${full?'':`<div style="background:#FDECEC;border:1px solid #E4A6A6;color:#8f1414;padding:8px 12px;font-weight:bold;margin:10px 0">
    DRAFT — ยังลงนามไม่ครบ (Lead ${sg.lead?'✔':'—'} · CMM ${sg.cmm?'✔':'—'} · รับทราบ ${ackCount(r)[0]}/${ackCount(r)[1]||'?'})
    · ลงนามทั้งหมดในแอป Portal · พิมพ์ได้เมื่อเป็นฉบับสมบูรณ์เท่านั้น</div>`}
  <table class="sig"><tr><td class="h">Lead Auditor</td><td class="h">Compliance Monitoring Manager</td></tr>
  <tr>${sigTd('lead',r.lead)}${sigTd('cmm','')}</tr></table>
  <table class="sig" style="margin-top:6px"><tr><td class="h" colspan="3">ผู้รับการตรวจ — ลงนามรับทราบ (${ackCount(r)[0]}/${ackCount(r)[1]} คน)</td></tr>
  ${(()=>{const L=ackList(r); if(!L.length) return '<tr><td colspan="3" style="color:#98a4b4">ยังไม่ได้ระบุรายชื่อผู้ต้องรับทราบ</td></tr>';
    let cells=L.map(e=>{const a=ackOf(r,e);
      return a?`<td><img src="${a.d}" style="height:44px"><br>( ${esc(a.n)} )<br>${esc(e)} · ${esc(a.dt)}</td>`
              :`<td style="color:#98a4b4">ยังไม่ลงนาม — ลงนามใน Portal<br>( ${esc(e)} )<br>วันที่ ...... / ...... / ......</td>`;});
    while(cells.length%3) cells.push('<td style="border:none"></td>');
    let out=''; for(let k=0;k<cells.length;k+=3) out+='<tr>'+cells.slice(k,k+3).join('')+'</tr>';
    return out;})()}
  </table>
  <p class="np">${full?'<button onclick="window.print()" style="min-height:40px;padding:6px 18px;font-weight:bold">🖨 พิมพ์ / บันทึก PDF (ฉบับสมบูรณ์)</button>':'<span style="color:#8f1414;font-size:12.5px">🔒 ปุ่มพิมพ์จะเปิดเมื่อลงนามครบ 3 ฝ่าย — ตามหลักการ ทำทุกขั้นตอนบนแอป พิมพ์เฉพาะฉบับสมบูรณ์</span>'}</p>
  </body></html>`);
  w.document.close();
}
function notiMail(i){
  const r=PLAN[i]; const p=PACKS.find(x=>x.proj===r.proj)||{};
  const sub=`[D-0507] Audit Notification — ${p.name||r.proj} (${r.start||''})`;
  const body=[`เรียน ${r.auditee||'ผู้เกี่ยวข้อง'}`,'',
   `ขอแจ้งกำหนดการตรวจติดตามภายในตามแผนประจำปี ${PLANYEAR}:`,
   `• งานตรวจ: ${p.name||r.proj} (${p.code||''})`,
   `• รอบ: ${r.label||'-'}`,
   `• วันที่: ${r.start||'-'} ถึง ${r.end||'-'}`,
   `• Lead Auditor: ${r.lead||'-'}`,'',
   'ขอให้จัดเตรียมเอกสารและบุคลากรที่เกี่ยวข้องตามขอบเขตข้างต้น','',
   'โปรดเข้าสู่ระบบ Audit Portal เพื่ออ่านหนังสือแจ้งการตรวจฉบับเต็ม และลงนามรับทราบในแอป (ไม่ต้องเซ็นเอกสารส่งกลับ):',
   location.href.split('#')[0],'',
   'Compliance Monitoring, D-0507 Flight Training Co., Ltd.'].join('\n');
  location.href=`mailto:${encodeURIComponent(ackList(r).join(','))}?subject=${encodeURIComponent(sub)}&body=${encodeURIComponent(body)}`;
}
function notiIcs(i){
  const r=PLAN[i]; const p=PACKS.find(x=>x.proj===r.proj)||{};
  if(!r.start){ alert('กำหนดวันเริ่มก่อน'); return; }
  const d1=r.start.replace(/-/g,''); 
  const d2=new Date(new Date(r.end||r.start).getTime()+86400000).toISOString().slice(0,10).replace(/-/g,'');
  const ics=['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//D-0507//Audit//TH','BEGIN:VEVENT',
   `UID:${r.proj}-${d1}@d0507-audit`,`DTSTART;VALUE=DATE:${d1}`,`DTEND;VALUE=DATE:${d2}`,
   `SUMMARY:Audit: ${(p.name||r.proj)} ${(r.label||'')}`,
   `DESCRIPTION:Lead: ${(r.lead||'-')} · ${(p.code||'')}`,'END:VEVENT','END:VCALENDAR'].join('\r\n');
  const a=document.createElement('a');
  a.href='data:text/calendar;charset=utf-8,'+encodeURIComponent(ics);
  a.download=`Audit_${r.proj}_${r.start}.ics`; a.click();
}
</script></body></html>'''

PORTAL = PORTAL.replace('@@FBCFG@@', FBCFG).replace('@@PACKS@@', json.dumps(plist, ensure_ascii=False))
pp = os.path.join(HERE, 'index.html')
open(pp, 'w', encoding='utf-8').write(PORTAL)
print('portal:', pp, os.path.getsize(pp), 'bytes')
