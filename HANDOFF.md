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

## Build

```bash
python3 audit-app-src/build.py    # ผลลัพธ์เขียนทับ D-0507_Internal_Audit_Checklist.html ที่ root ของโฟลเดอร์
```

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
