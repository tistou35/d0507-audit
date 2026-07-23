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

# ---------- Portal ----------
e = html.escape
cards = '\n'.join(f'''    <a class="pcard" href="{e(c['outdir'])}/">
      <div class="pc-code">{e(c['doc_code'])} · {e(c['version'])}</div>
      <h2>{e(c['name'])}</h2>
      <p>{e(c['desc'])}</p>
      <div class="pc-meta">รอบตรวจ: <b>{e(c['audit_id'])}</b> · เลข CAR: {e(c.get('car_prefix','CAR'))}-YYYY-xxx</div>
      <div class="pc-go">เปิดงานตรวจ →</div>
    </a>''' for c in built)

portal = f'''<!DOCTYPE html><html lang="th"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>D-0507 Audit Portal</title>
<style>
:root{{--navy:#1F3864;--blue:#2E75B6;}}
*{{box-sizing:border-box;margin:0;padding:0;}}
body{{font-family:-apple-system,'Segoe UI','Noto Sans Thai',Arial,sans-serif;background:#eef2f7;color:#1a1a2a;min-height:100vh;}}
header{{background:var(--navy);color:#fff;padding:22px 26px 18px;}}
header h1{{font-size:22px;}}
header .sub{{font-size:13px;opacity:.85;margin-top:4px;}}
main{{max-width:1100px;margin:0 auto;padding:26px 18px 60px;}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px;margin-top:14px;}}
.pcard{{display:block;background:#fff;border:1px solid #d8dfe8;border-radius:12px;padding:18px;text-decoration:none;color:inherit;transition:box-shadow .15s,transform .15s;}}
.pcard:hover{{box-shadow:0 6px 22px rgba(31,56,100,.18);transform:translateY(-2px);}}
.pc-code{{font-size:11.5px;color:var(--blue);font-weight:bold;letter-spacing:.3px;}}
.pcard h2{{font-size:17px;color:var(--navy);margin:6px 0 6px;}}
.pcard p{{font-size:13px;color:#5a6675;}}
.pc-meta{{font-size:12px;color:#7a8798;margin-top:10px;}}
.pc-go{{margin-top:12px;font-weight:bold;color:var(--blue);font-size:14px;}}
.note{{background:#fff;border-left:4px solid var(--blue);border-radius:8px;padding:12px 16px;font-size:13px;color:#445;margin-top:26px;}}
h3.sec{{color:var(--navy);font-size:15px;margin-top:8px;}}
footer{{text-align:center;color:#98a4b4;font-size:11.5px;padding:18px;}}
</style></head><body>
<header>
  <h1>D-0507 FLIGHT TRAINING — AUDIT PORTAL</h1>
  <div class="sub">ศูนย์กลางงานตรวจสอบ · Compliance Monitoring (OMM Section 5) · เลือกงานตรวจด้านล่าง</div>
</header>
<main>
  <h3 class="sec">งานตรวจสอบ / Audit Projects</h3>
  <div class="grid">
{cards}
  </div>
  <div class="note"><b>หมายเหตุ:</b> ทุกงานใช้บัญชีเข้าสู่ระบบเดียวกัน ข้อมูลแยกตามรอบตรวจ ·
  เพิ่มงานตรวจใหม่/อัปเดต checklist เวอร์ชันใหม่: เพิ่มโฟลเดอร์ใน <code>packs/</code> แล้ว build ใหม่ ·
  Audit Plan ประจำปีและการแจ้งการตรวจ (Audit Notification) จะเพิ่มในเฟสถัดไป</div>
</main>
<footer>D-0507 Flight Training Co., Ltd. · Internal Audit System · controlled via audit-app-src (GitHub)</footer>
</body></html>'''
pp = os.path.join(HERE, 'index.html')
open(pp, 'w', encoding='utf-8').write(portal)
print('portal:', pp, os.path.getsize(pp), 'bytes')
