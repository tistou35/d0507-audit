#!/usr/bin/env python3
# Build (multi-project): packs/<proj>/<version>/{appdata.json,pack.json} + template.html
#   -> <outdir>/index.html (แอปของแต่ละ project, เวอร์ชันล่าสุด)
#   -> index.html (Door เลือกประตู) · audit/index.html (Audit Portal) · forms/index.html (Forms Portal)
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
              .replace('__PROJ__', cfg['project'])
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

# ---------- Portals: door (/) + audit (/audit/) + forms (/forms/) ----------
# แก้หน้า portal ที่ portal_audit.html / portal_forms.html / door.html เท่านั้น (ไม่ใช่ในไฟล์นี้)
def _emit(src_name, outpath, subs):
    t = open(os.path.join(HERE, src_name), encoding='utf-8').read()
    for k, v in subs.items():
        t = t.replace(k, v)
    left = [k for k in subs if k in t]
    if left:
        raise SystemExit('placeholder ยังเหลือใน %s: %s' % (src_name, left))
    os.makedirs(os.path.dirname(outpath), exist_ok=True) if os.path.dirname(outpath) != HERE else None
    open(outpath, 'w', encoding='utf-8').write(t)
    print('built:', outpath, os.path.getsize(outpath), 'bytes')

def _json(o):
    # กัน '</' ปิด <script> กลางคัน
    return json.dumps(o, ensure_ascii=False).replace('</', '<\\/')

# Audit Portal ย้ายจาก / ไป /audit/ — แอปย่อย (iac, vendor, …) ยังอยู่ root จึงลิงก์ด้วย ../
_emit('portal_audit.html', os.path.join(HERE, 'audit', 'index.html'),
      {'@@FBCFG@@': FBCFG, '@@PACKS@@': _json(plist), '@@BASE@@': '../'})

# Forms Portal — ข้อมูลจาก forms_register.json
REG = json.load(open(os.path.join(HERE, 'forms_register.json'), encoding='utf-8'))
_emit('portal_forms.html', os.path.join(HERE, 'forms', 'index.html'),
      {'@@FBCFG@@': FBCFG, '@@REG@@': _json(REG)})

# Door ที่ / — จำประตูล่าสุดใน localStorage, เลือกใหม่ด้วย /?pick=1
_emit('door.html', os.path.join(HERE, 'index.html'),
      {'@@STATS@@': _json({'forms': len(REG['forms']),
                           'lef': REG['lefcount']['unique'],
                           'packs': len(plist),
                           'items': sum(p['total'] for p in plist)})})
