#!/usr/bin/env python3
# Build: inject appdata.json into template.html -> ../D-0507_Internal_Audit_Checklist.html
import os
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
data = open(os.path.join(HERE, 'appdata.json'), encoding='utf-8').read().replace('</', '<\\/')
tpl = open(os.path.join(HERE, 'template.html'), encoding='utf-8').read()
if '__DATA__' not in tpl:
    raise SystemExit('template.html ไม่มี __DATA__ placeholder — ห้ามแก้ไฟล์ build แล้วย้อนกลับมาทับ template')
out = os.path.join(ROOT, 'D-0507_Internal_Audit_Checklist.html')
open(out, 'w', encoding='utf-8').write(tpl.replace('__DATA__', data))
print('built:', out, os.path.getsize(out), 'bytes')
