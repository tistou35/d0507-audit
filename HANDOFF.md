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

## สถานะปัจจุบัน / งานค้าง

1. **รอฝัง Firebase config** — ใน `template.html` มีบรรทัด `const FIREBASE_CONFIG = null;` (บนสุดของ <script>)
   → เมื่อได้ค่าจาก Firebase Console แล้ว แทน null ด้วย object แล้ว build ใหม่
   → `AUDIT_ID = 'audit-2026'` เปลี่ยนเมื่อขึ้นรอบตรวจใหม่
2. **Deploy GitHub Pages** — ตามไฟล์ `คู่มือติดตั้ง_Server_Edition.md` (root โฟลเดอร์):
   สร้าง repo Public → อัปโหลดไฟล์ build เป็น `index.html` → Settings→Pages → เพิ่ม `<user>.github.io` ใน Firebase Authorized domains
   (Claude Code ทำได้เลยด้วย `gh repo create` + `git push` ถ้าติดตั้ง gh/git แล้ว)
3. **Security Rules** email allowlist — โค้ดอยู่ในคู่มือติดตั้ง ต้องวางทั้ง Firestore และ Storage
4. งานแนะนำถัดไป: แก้ reference 16 จุดใน PEL-TO-CK-061/062 ที่เลข section เลื่อน (แอปแสดง ⚠ ในกล่อง "คู่มือ:" ของข้อนั้น ๆ), รายงานตรวจฉบับ .docx ตามฟอร์แมต controlled doc

## สถาปัตยกรรมแอป (สรุปสั้น)

- Single-file HTML, ไม่ใช้ localStorage — state ในหน่วยความจำ + export/import JSON; เมื่อมี FIREBASE_CONFIG จะ sync Firestore (`audits/{AUDIT_ID}/items/{itemId}`, last-write-wins, flush ทุก 2.5s ผ่าน `mark(id)`/`pending` set) + รูปขึ้น Storage
- โมดูล: OMM(153)/OMA(99)/TM(1,767) จาก PEL-TO-CK rev.02 + SITE(62) ตรวจ 2 มิติ Documented/Implemented
- ระบบ CAR: assign→email(mailto)→CA→verify/reject, ฟอร์มพิมพ์, ทะเบียน CSV
- Data pipeline เดิม (parse docx checklist / สกัดคู่มือ) เป็นสคริปต์ Python ที่รันใน cloud — วิธีการ: อ่านตาราง docx ระดับ XML (expand gridSpan/vMerge; อย่าใช้ python-docx .cells กับตารางใหญ่ ช้ามาก), สกัดคู่มือด้วย TOC-to-Heading alignment (เลข section อยู่ใน TOC styles TOC1-5, heading ใช้ auto-numbering)

## ที่เก็บข้อมูลภายนอก

- Google Drive "Audit 2026": `18td_bNiEYsFQbq7uFUjHjUIUHXQgc5E6` — โฟลเดอร์ 00_Summary_Reports / 01_Audit_Data / 02_Evidence_Photos / 03_CAR / 04_Checklist_App
- Document Register อยู่ใน `CLAUDE.md` (อัปเดต D-0507-CAR-001, D-0507-IAC-001 แล้ว)
