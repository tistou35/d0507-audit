# HANDOFF — Internal Audit Checklist (D-0507-IAC-001) → Claude Code

สำหรับทำงานต่อใน Claude Code (โฟลเดอร์นี้): งานทั้งหมดสร้างใน Cowork cloud session 23 JUL 2026

## ไฟล์ในชุดนี้ (audit-app-src/)

| ไฟล์ | คืออะไร |
|---|---|
| `template.html` | ต้นฉบับแอป (HTML/CSS/JS) มี placeholder `__DATA__` — **แก้แอปที่ไฟล์นี้ ไม่ใช่ที่ไฟล์ build แล้ว** |
| `appdata.json` | ข้อมูล checklist 2,081 รายการ + TCAR-ORA catalog + excerpts/chk/how ที่ประมวลผลแล้ว |
| `site_items.py` | ต้นฉบับรายการตรวจ On-Site 62 ข้อ (แก้เนื้อหา On-Site ที่นี่) |
| `manual_sections.json` | เนื้อหาคู่มือ OMM/OMA แยกราย section (300+311 sections) ใช้ทำ excerpt |
| `make_car_form.js` | สคริปต์สร้างฟอร์ม D-0507-CAR-001.docx (ใช้ npm `docx`) |
| `build.py` | สคริปต์ประกอบ: inject appdata.json → template.html → `D-0507_Internal_Audit_Checklist.html` |

## Build (multi-project ตั้งแต่ 24 JUL 2026)

```bash
python3 audit-app-src/build.py
# → audit-app-src/<outdir>/index.html   (แอปของแต่ละ project — เวอร์ชัน checklist ล่าสุด)
# → audit-app-src/index.html            (Portal หน้ารวม)
# → D-0507_Internal_Audit_Checklist.html ที่ root (สำเนา IAC สำหรับเปิด local/Drive)
```

โครง pack: `packs/<project>/<version>/{appdata.json, pack.json}` —
pack.json กำหนด ชื่อหน้า/doc code/AUDIT_ID/prefix เลข CAR/outdir ·
**เพิ่มงานตรวจใหม่หรือ checklist เวอร์ชันใหม่ = เพิ่มโฟลเดอร์ pack แล้ว build + push** (engine ที่ template.html ใช้ร่วมกันทุกงาน) ·
URL: Portal ที่ root, งาน IAC ที่ `/iac/` (AUDIT_ID เดิม `audit-2026` — ข้อมูล Firestore ไม่กระทบ)

## สถานะปัจจุบัน (Deploy เสร็จ 23 JUL 2026)

- **URL แอป:** https://tistou35.github.io/d0507-audit/ (GitHub Pages)
- **GitHub repo:** `tistou35/d0507-audit` (public, branch `main`, ไฟล์ build = `index.html`)
  → git repo ต้นทางอยู่ที่โฟลเดอร์ `audit-app-src/` นี้ (`git push` เพื่อ deploy เวอร์ชันใหม่)
- **Firebase project:** `d0507-audit` (บัญชี tistou35@gmail.com, แพลน **Blaze** + budget alert 100 THB)
  - Authentication: Google + Email/Password เปิดแล้ว · Authorized domains มี `tistou35.github.io` แล้ว
  - Firestore: asia-southeast1, production mode, Rules email-allowlist วางแล้ว
  - Storage: `d0507-audit.firebasestorage.app` asia-southeast1, Rules email-allowlist วางแล้ว
  - Web app `audit-app` — config **ฝังใน template.html แล้ว** (บรรทัด FIREBASE_CONFIG) และ build/push แล้ว
  - เพิ่ม/ลบคนในทีม = แก้รายชื่ออีเมลใน Rules ทั้ง Firestore และ Storage (ตอนนี้มีแค่ tistou35@gmail.com)
- `AUDIT_ID = 'audit-2026'` เปลี่ยนเมื่อขึ้นรอบตรวจใหม่ แล้ว build + push ใหม่

- **ทดสอบ end-to-end ผ่านแล้ว (23 JUL 2026):** login Google → ติ๊ก OMM-0001 = S → document `audits/audit-2026/items/OMM-0001` ขึ้นใน Firestore จริง (st/t/u ครบ)
  - หมายเหตุ: OMM-0001 ที่ติ๊กไว้เป็นข้อมูลทดสอบ — ถ้าจะเริ่มตรวจจริงจากศูนย์ ลบ document นี้ใน Firestore console หรือติ๊กทับได้เลย

- **CAR workflow ตามฟอร์ม D-0507-CAR-001 (24 JUL 2026):** stepper 3 ขั้นในแอป — ① มอบหมาย (Part 1–2, Auditor, เลือก Finding level/Position ได้) → ② ตอบกลับ (Part 3–5: Root cause → Corrective + วันแล้วเสร็จ → Preventive, บังคับลำดับก่อนส่ง) → ③ ตรวจรับ (Part 6: Accept + verification evidence ปิด CAR / Reject + เหตุผล + กำหนดเสร็จใหม่) · ปุ่ม "ดาวน์โหลด CAR Forms" export หน้าตาตรงฟอร์มจริงทุก Part พร้อม checkbox และลายเซ็น 3 ฝ่าย (เปิดแล้วสั่งพิมพ์เป็น PDF) · CSV register มีคอลัมน์ครบ · ทดสอบแล้วกับ CAR-2026-001 (OMM-0002 — ข้อมูลทดสอบ ติ๊กทับ/ลบได้)
- **ลายเซ็น + Part 6 ในแอป (24 JUL 2026):** ช่องลายเซ็น 3 ฝ่าย (ผู้รับผิดชอบ/Auditor/CMM) เซ็นด้วยนิ้ว/Apple Pencil บน canvas เก็บเป็นรูปใน Firestore และฝังลงฟอร์ม export · Part 6 เป็นฟอร์มกรอกในแอป (Verification evidence ก่อน Accept, เหตุผล + new due date ตอน Reject) · บังคับ: ผู้รับผิดชอบเซ็นก่อนส่งตอบกลับ, Auditor เซ็น + กรอก evidence ก่อนปิด CAR

- **Bulk actions + multi-auditor (24 JUL 2026):** แท็บ CAR มี checkbox เลือกหลายใบ → "ส่งตอบกลับที่เลือก" (เซ็นผู้รับผิดชอบครั้งเดียวใช้ทุกใบ ตรวจความครบ Part 3–4 รายใบก่อน), "ตรวจรับที่เลือก" (evidence กลาง + เซ็น Auditor ครั้งเดียว), "CMM เซ็นที่เลือก" · ทุก action บันทึกชื่อผู้ทำจาก account ที่ login (c.iby, ลายเซ็น prefill, history log) → ผู้ตรวจหลายคน login คนละเครื่องได้ ระบบแยกให้เองว่าใครออก CAR ใบไหน · ลบข้อมูลทดสอบชุดแรกแล้ว ทดสอบรอบใหม่ผ่านครบ (CAR-2026-001/002 ปิดด้วย bulk accept — ยังเป็นข้อมูลทดสอบ ลบได้ก่อนตรวจจริง)

- **แพลตฟอร์ม multi-project เฟส 2–5 (24 JUL 2026):**
  - เฟส 2: แม่แบบ Excel `packs/_TEMPLATE_checklist.xlsx` + ตัวแปลง `xlsx2pack.py` — วาง checklist.xlsx ใน pack แล้ว build จะแปลงเป็น appdata.json อัตโนมัติ
  - เฟส 3: Portal v2 (root URL) — login, การ์ดความคืบหน้าสดจาก `audits/{aid}.sum` (แอปเขียนผ่าน pushSummary), **Audit Plan รายปี** เก็บที่ `plans/{year}` (เพิ่ม Firestore rule แล้ว), แบนเนอร์เตือนใกล้กำหนด 14 วัน/เลยกำหนด
  - เฟส 4: ปุ่มต่อแถวแผน — 📄 หนังสือแจ้งการตรวจ D-0507-ANF-001 (DRAFT, พิมพ์/บันทึก PDF), ✉ ร่างอีเมล, 📅 ไฟล์ .ics
  - เฟส 5: pack แรก `packs/vendor/v2026/` — Vendor / Contracted Activities Audit 13 ข้อ (D-0507-IAC-002 **DRAFT รอ @reviewer/@legal**), AUDIT_ID `vendor-2026`, เลข CAR `CAR-VEN-YYYY-xxx`, URL `/vendor/`
  - ทดสอบแล้ว: การ์ดสด (IAC 2/2081), บันทึกแผนขึ้น Firestore, สถานะ/แบนเนอร์อัตโนมัติ, หนังสือแจ้งการตรวจ · แถวแผน "Q3 รอบหลัก (ทดสอบ)" เป็นข้อมูลทดสอบ ลบได้ใน Portal

- **หนังสือแจ้งการตรวจ เซ็นครบวงจรในแอป (24 JUL 2026):** ลายเซ็น 3 ฝ่ายบนแผ่นเซ็นใน Portal — Lead Auditor / CMM / ผู้รับการตรวจ (ลงนามรับทราบ) เก็บใน plans/{year}.rows[].sg · ผู้รับการตรวจใช้อีเมลในช่อง "อีเมลผู้รับการตรวจ" (ต้องอยู่ใน allowlist) login Portal แล้วเห็นแบนเนอร์ "รอลงนามรับทราบ" กดเซ็นในแอป — ไม่มีการเซ็นกระดาษ/ส่งอีเมลกลับ · หนังสือ 📄 แสดงแถบ DRAFT + ล็อกปุ่มพิมพ์จนลงนามครบ 3 ฝ่าย (หลักการ: ทุกขั้นตอนบนแอป พิมพ์เฉพาะฉบับสมบูรณ์)

- **Pack ที่ 3: Aerodrome Certification Readiness (24 JUL 2026):** สร้างจากไฟล์ผู้ใช้ `D0507_Aerodrome_Cert_Checklist.xlsx` (แปลงเป็นแม่แบบมาตรฐานที่ `packs/aerodrome/v2026/checklist.xlsx`) — 81 ข้อ 4 Parts (Certification Process / Aerodrome Manual / Site Inspection / Organisation-SMS) · D-0507-IAC-003 DRAFT · AUDIT_ID `aerodrome-2026` · CAR-ADR · URL `/aerodrome/` · แก้ engine ให้แถบแท็บโมดูลสร้างจากข้อมูล pack (เดิม hardcode OMM/OMA/TM)

- **Aerodrome pack เสริม guidance (24 JUL 2026):** guidance วิธีตรวจครบ 81/81 ข้อ + รายการตรวจย่อย (chk ติ๊กรายหัวข้อ) 41 ข้อ + EASA ref (Reg 139/2014 ADR.OR/ADR.OPS/CS ADR-DSN) พร้อม note ขอบเขต: สนามบินส่วนบุคคล (ไม่เปิดสาธารณะ) อยู่นอกขอบเขต EASA ตาม Reg 2018/1139 Art.2(1)(e) — ใช้ กพท./พ.ร.บ.เดินอากาศเป็นหลัก EASA เป็น best practice · engine: ช่อง Inspector comment แสดงทุกข้อทุกสถานะ (รวมเหตุผล N.A/ไม่ตรวจ) · แม่แบบ/ตัวแปลงรองรับคอลัมน์ SubChecklist แล้ว

## งานค้าง

1. แก้ reference 16 จุดใน PEL-TO-CK-061/062 ที่เลข section เลื่อน (แอปแสดง ⚠ ในกล่อง "คู่มือ:" ของข้อนั้น ๆ)
2. รายงานตรวจฉบับ .docx ตามฟอร์แมต controlled doc

## สถาปัตยกรรมแอป (สรุปสั้น)

- Single-file HTML, ไม่ใช้ localStorage — state ในหน่วยความจำ + export/import JSON; เมื่อมี FIREBASE_CONFIG จะ sync Firestore (`audits/{AUDIT_ID}/items/{itemId}`, last-write-wins, flush ทุก 2.5s ผ่าน `mark(id)`/`pending` set) + รูปขึ้น Storage
- โมดูล: OMM(153)/OMA(99)/TM(1,767) จาก PEL-TO-CK rev.02 + SITE(62) ตรวจ 2 มิติ Documented/Implemented
- ระบบ CAR: assign→email(mailto)→CA→verify/reject, ฟอร์มพิมพ์, ทะเบียน CSV
- Data pipeline เดิม (parse docx checklist / สกัดคู่มือ) เป็นสคริปต์ Python ที่รันใน cloud — วิธีการ: อ่านตาราง docx ระดับ XML (expand gridSpan/vMerge; อย่าใช้ python-docx .cells กับตารางใหญ่ ช้ามาก), สกัดคู่มือด้วย TOC-to-Heading alignment (เลข section อยู่ใน TOC styles TOC1-5, heading ใช้ auto-numbering)

## ที่เก็บข้อมูลภายนอก

- Google Drive "Audit 2026": `18td_bNiEYsFQbq7uFUjHjUIUHXQgc5E6` — โฟลเดอร์ 00_Summary_Reports / 01_Audit_Data / 02_Evidence_Photos / 03_CAR / 04_Checklist_App
- Document Register อยู่ใน `CLAUDE.md` (อัปเดต D-0507-CAR-001, D-0507-IAC-001 แล้ว)
