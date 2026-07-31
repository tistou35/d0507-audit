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

- **3 checklist ใหม่เข้าระบบเป็น "project แยก" (24 JUL 2026):** เนื้อหาจากฟอร์ม controlled D-0507-VAC-001 / SAC-001 / SSC-001 (สร้างโดย session Cowork — ต้นฉบับ new_checklists.py, make_checklist_forms.js, forms_data.json) ถูกแปลงเข้าโครง multi-project: `/vendor/` (25 ข้อ, vendor-2026, CAR-VEN — แทนร่างเดิม), `/safety/` (26 ข้อ 2 มิติ Doc/Impl, safety-2026, CAR-SAF), `/surveillance/` (29 ข้อ, surveil-2026, CAR-SSC) — แต่ละงานมีรอบตรวจ/ทะเบียน CAR แยกกัน เลือกเป็น "กรอบการตรวจ" ต่อรอบใน Audit Plan ได้ · ทุกแอปมีปุ่ม "⌂ Audit Portal" · หมายเหตุ: session Cowork เขียน template.html/HANDOFF.md ทับด้วยเวอร์ชันเก่า — กู้ template จาก git HEAD แล้ว (ถ้าไฟล์ build หดผิดปกติ ให้ git diff template.html ก่อนเสมอ) · แนวทางไปข้างหน้า: แก้ engine ที่ template.html ใน repo นี้เท่านั้น อย่าให้ session อื่นเขียนทับ

- **ปฏิทินการตรวจ 12 เดือน (Gantt) ใน Portal (24 JUL 2026):** ใต้ตาราง Audit Plan — แถวละงาน แท่งพาดตามช่วงวันที่ (สเกลวันละ 3px), เส้นแบ่ง+ชื่อเดือน ม.ค.–ธ.ค., เส้นแดง "วันนี้", สีแท่งตามสถานะ (วางแผน/ใกล้กำหนด/กำลังตรวจ/เลยกำหนด/เสร็จ), scroll ซ้าย-ขวา + auto-scroll มาที่ช่วงปัจจุบัน, ชื่องานตรึงซ้าย, hover ดูรายละเอียด

- **Portal IA ใหม่ — แผนคือประตูเดียว (24 JUL 2026):** ① การ์ด "งานตรวจสอบ" แสดงเฉพาะรอบจาก Audit Plan ที่อยู่ในกรอบ 30 วัน (รวมกำลังตรวจ/เลยกำหนด) พร้อมปุ่ม ▶ เริ่มตรวจ/เข้าตรวจต่อ ② ทุกรอบมีเลขอ้างอิง AP-YYYY-nn (ออกอัตโนมัติ) แสดงในแผน/การ์ด/Gantt และเป็นรหัสชุดข้อมูล: แอปเปิดผ่าน `?audit=<proj>-<yyyy>-<nn>` → ตรวจกี่รอบต่อปีข้อมูลก็แยกกัน (mock เดิมอยู่ที่ default audit-2026 ไม่ปนรอบใหม่) ③ ส่วน "กรอบการตรวจ/Checklists" ท้ายหน้า = ชั้นวางแม่แบบ มีปุ่ม 👁 เปิดดูรายการตรวจ (`?view=1` read-only ไม่ต้อง login ไม่บันทึก) และ ＋วางแผนรอบตรวจ (เพิ่มแถวแผน prefill)

- **ลงนามรับทราบหลายคน (24 JUL 2026):** แถวแผนมีช่อง "อีเมลผู้ต้องรับทราบ" ใส่หลายคนคั่นด้วย , (เก็บ r.ackList / ลายเซ็น r.ackSigs[] จับคู่อีเมลที่ login · ของเดิมคนเดียว migrate อัตโนมัติ) · badge "รับทราบ x/y" ในแผน+ปุ่ม+หนังสือ · แต่ละคน login แล้วเห็นแบนเนอร์ → กด "✍ รับทราบ" เซ็นของตัวเอง (คนนอกรายชื่อเพิ่มตัวเองได้โดย confirm) · หนังสือแจ้ง: ตารางลายเซ็นรับทราบหลายช่อง (3 ช่อง/แถว) · ฉบับสมบูรณ์/ปุ่มพิมพ์ = Lead + CMM + รับทราบครบทุกคน · ✉ ส่งถึงทุกอีเมลในรายชื่อ

- **Multi-user + ACM + link อ้างอิง (24 JUL 2026):** ① Portal มีปุ่ม "สมัครใหม่" (อีเมล/รหัสผ่าน — ไม่ต้องใช้ Gmail) + แบนเนอร์แจ้งเมื่ออีเมลไม่มีสิทธิ์ (permission-denied) ② ระบบ ACM อนุมัติแผน: ช่องอีเมล ACM ท้ายตาราง (เก็บใน plans/{year}.acm — ถ้าตั้งแล้ว เฉพาะอีเมลนั้นอนุมัติได้), ปุ่ม "ACM อนุมัติทั้งแผนปีนี้" (อนุมัติทุกแถวที่ค้าง = แผนประจำปี) + ปุ่มอนุมัติรายแถว (รายครั้ง/แทรกระหว่างปี), แก้ project/วันที่หลังอนุมัติ → ต้องอนุมัติใหม่, ปุ่ม ▶ เปิดงานตรวจถูกล็อกจนกว่าอนุมัติ, ลงวันที่ย้อนหลังได้ ③ ทุกข้อตรวจมีช่อง "🔗 ลิงก์เอกสารอ้างอิง" วาง URL หลายลิงก์ → แสดงเป็น chip กดเปิดได้ (รวมในโหมด view) sync ขึ้น Firestore ④ **Security Rules อัปเดตแล้ว (25 JUL 2026):** Firestore + Storage รวมเป็นบล็อกเดียว (/{document=**} และ /{allPaths=**}) allowlist 7 อีเมล: tistou35, navywut, bankapoo77, oceanfly46103, thapphawutw, amy.pinnoi, warutmitthumsiri (@gmail.com ทั้งหมด — ทุกคนที่ login ณ วันนั้น) · เพิ่มคนใหม่ = เพิ่มอีเมล 1 บรรทัดใน 2 ที่ (Firestore Rules + Storage Rules) แล้ว Publish

- **Open registration + คลังเอกสารกลาง (25 JUL 2026):** ① Firestore Rules เปลี่ยนเป็น `request.auth != null` — สมัคร (register) แล้วเข้าถึงได้ทันที ไม่ต้องแก้ rules รายคน (ข้อแลก: ใครก็สมัครได้ — URL อย่าแชร์สาธารณะ · **Storage rules ยังเป็น allowlist 7 คน รอผู้ใช้วางเวอร์ชัน auth!=null เอง** เพราะ classifier บล็อกการพิมพ์) ② ยกเลิกช่องลิงก์รายข้อ → เป็น "📎 เอกสารอ้างอิง" แถบใต้ header ทุกหน้าของแต่ละ project (Firestore `library/{proj}` แชร์ทุกรอบ): chip ชื่อเอกสารกดเปิด, ทุกคนเพิ่ม (＋ ชื่อ+URL) / ลบ (✕) ได้, sync สด, โหมด view เห็นแต่กดแก้ไม่ได้

- **Sticky header + กันลบพลาด (25 JUL 2026):** header/tabs/แถบเอกสารอ้างอิงตรึงด้านบนตลอดการ scroll (ย้าย #libbox เข้าใน header + แก้ inline `position:relative` ที่ไปทับ `position:sticky`) · scroll เกิน 60px จะย่อหัว (ซ่อนบรรทัด sub, ลดขนาดชื่อ) ให้เหลือพื้นที่อ่าน · ลบเอกสารต้องกด "✎ จัดการ" เปิดโหมดลบก่อน ✕ จึงปรากฏ แล้วยังมี confirm แสดงชื่อเอกสารอีกชั้น (กันนิ้วโดนบน iPad) — ลบเสร็จปิดโหมดอัตโนมัติ

- **Bulk N/A + สีหมวดชัดขึ้น (25 JUL 2026):** ทุกหมวด (section/วิชา) และทุกกลุ่มมีปุ่มคู่ "S ✓" และ "N/A" (N/A มี confirm บอกจำนวนข้อก่อนตั้งค่า · ตั้งเฉพาะข้อที่ยังไม่ตรวจ ไม่ทับของเดิม) · หัวหมวดเป็นแถบน้ำเงินเข้ม gradient + ตัวนับ x/y และจำนวน GAP ต่อหมวด · กลุ่มมีแถบสีซ้ายและหัวสีอ่อน แยกชั้นชัดเจน — TM "Theoretical Knowledge Syllabus" (856 ข้อ) จึงแบ่งเห็นชัดเป็น 27 วิชา (Air Law 76 ข้อ, Human Performance, Meteorology, …) พร้อม bulk รายวิชา
- **Storage Rules อัปเดตแล้ว (25 JUL 2026):** เป็น `request.auth != null` เหมือน Firestore — สมัครแล้วอัปโหลดรูปหลักฐานได้ทันที

- **แก้หัวกระพริบตอนเลื่อนสุดหน้า (25 JUL 2026):** สาเหตุคือ loop — พอหัวหด หน้าสั้นลง เลื่อนถอยขึ้น หัวขยาย วนซ้ำ (เห็นชัดที่แท็บ GAP Report ซึ่งเนื้อหาสั้น) · แก้ด้วย hysteresis (หดเมื่อ >110px, คลายเมื่อ <45px), ไม่สลับสถานะเมื่ออยู่ใกล้ก้นหน้า, ไม่หดเลยถ้าหน้าสั้นกว่า viewport+140px, throttle ด้วย requestAnimationFrame และตัด CSS transition ที่เร่ง loop · ทดสอบด้วย MutationObserver: เดิมสลับไม่หยุด ตอนนี้เหลือ 1 ครั้งตอนสลับแท็บแล้วนิ่ง

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

## อัปเดต 24 JUL 2026 — เพิ่ม 3 checklist ใหม่

- โมดูลใหม่ในแอป: **VEN** (Vendor audit, 25 ข้อ), **SAF** (School safety audit, 26 ข้อ dual Doc/Impl), **SUR** (Surveillance spot-check, 29 ข้อ อ้างอิง FSOP/MMSOP) → รวมทั้งแอป 2,161 รายการ
- ต้นฉบับเนื้อหา: `new_checklists.py` · ฟอร์มควบคุม: `make_checklist_forms.js` + `forms_data.json` → D-0507-VAC-001 / SAC-001 / SSC-001 .docx (อยู่ root โฟลเดอร์ ลงทะเบียนใน CLAUDE.md แล้ว)
- Tabs ในแอปสร้างจาก MODS อัตโนมัติแล้ว (TAB_LABEL map ใน template.html)
- Catalog เพิ่มกลุ่ม "Internal SOPs" (FSOP, MMSOP) สำหรับ coverage dashboard

---

## อัปเดต 30 JUL 2026 — แยกเป็นสองประตู + Forms Portal (เฟส 1)

### โครง URL ใหม่

```
/                 door.html          → เลือกประตู · จำใน localStorage 'd0507_door' · เลือกใหม่ที่ /?pick=1
/forms/           portal_forms.html  → 📋 FORMS PORTAL (ใหม่)
/audit/           portal_audit.html  → 🔍 AUDIT PORTAL (ย้ายมาจาก /)
/iac/ /vendor/ /safety/ /surveillance/ /aerodrome/   ← ไม่ย้าย คงเดิมทุกอย่าง
```

**หลักการ:** ผู้ใช้รู้สึกว่าเป็นคนละแอป · หลังบ้านเป็น Firebase project เดียว → login ครั้งเดียวใช้ได้ทั้งสองประตู
(same origin + same authDomain) · Firestore/Storage/Rules **ไม่แตะ** · `AUDIT_ID` เดิม ข้อมูลการตรวจไม่กระทบ

### ไฟล์ที่เพิ่ม / เปลี่ยน

| ไฟล์ | สถานะ | คืออะไร |
|---|---|---|
| `portal_audit.html` | **ใหม่** | Portal เดิมที่แกะออกจาก string ใน `build.py` — **แก้ Audit Portal ที่ไฟล์นี้ ไม่ใช่ใน build.py แล้ว** |
| `portal_forms.html` | **ใหม่** | Forms Portal — หัวขาว (แยกตัวตนจาก audit ที่ใช้แถบ navy ทึบ) |
| `door.html` | **ใหม่** | หน้าเลือกประตู · ตัวเลขบนการ์ดคำนวณจาก register + packs |
| `forms_register.json` | **ใหม่** | ทะเบียนฟอร์ม 52 ใบ — **แหล่งข้อมูลกลางของ Forms Portal** แก้ที่นี่แล้ว build |
| `build.py` | แก้ | ตัด PORTAL literal ออก (37,183 → 4,892 bytes) · เพิ่ม `_emit()` สร้างสามประตู |
| `template.html` | แก้ 1 บรรทัด | บรรทัด 180 ปุ่ม `⌂ Audit Portal` จาก `href="../"` → `href="../audit/"` |
| `build.py.bak` | สำรอง | build.py ก่อนแยกไฟล์ (ลบได้เมื่อมั่นใจ) |

### placeholder ในไฟล์ portal (build.py แทนค่าให้)

- `portal_audit.html` — `@@FBCFG@@` `@@PACKS@@` `@@BASE@@` (= `../` เพราะแอปย่อยอยู่ root แต่ portal อยู่ `/audit/`)
- `portal_forms.html` — `@@FBCFG@@` `@@REG@@`
- `door.html` — `@@STATS@@`

`_emit()` จะ **error ถ้ามี placeholder เหลือ** — กันลืมแทนค่า

### ตรวจแล้ว (30 JUL 2026)

- `audit/index.html` ต่างจาก portal เดิมที่ HEAD **แค่ 3 จุด** — เติม `../` หน้าลิงก์แอปย่อยทั้งสามที่ · ที่เหลือ byte-identical (+9 bytes)
- ทั้งสามหน้า: ไม่มี placeholder เหลือ · JSON ที่ฝังใน `<script>` parse ผ่าน (escape `</` → `<\/` แล้ว) · `node --check` ผ่าน
- ทดสอบ render logic ของ Forms Portal ด้วย register ตัวจริง: 5 กลุ่ม (stu 12 / ins 27 / mnt 9 / ops 18 / mgt 27 ฟอร์ม) · ทะเบียน 52 แถว · filter "มีปัญหา" 37 แถว · "ยังไม่อยู่ใน LEF" 22 แถว · ไม่มี undefined/NaN หลุด
- Door แสดงตัวเลขสด: 30 ฟอร์มใน LEF · 52 ในทะเบียน · 5 กรอบการตรวจ · 2,242 รายการ

### Forms Portal เฟสนี้ทำอะไรได้

**อ่านและเปิดฟอร์มเท่านั้น** — ยังไม่ได้ย้ายการกรอกเข้าระบบ ปุ่ม "เปิดฟอร์ม" พาไป Jotform ใบเดิม
ประโยชน์ทันที: เปิดฟอร์ม **ถูกใบ** จากที่เดียว ไม่ต้องพึ่งลิงก์ใน LEF ที่ยังชี้ผิด 21 จุด

- จัดกลุ่มตามผู้ใช้ 5 กลุ่ม: นักเรียน · ครูการบิน/ครูภาคทฤษฎี · ช่างอากาศยาน · ฝ่ายปฏิบัติการ · ฝ่ายบริหาร
- ฟอร์มเดียวโผล่หลายกลุ่มได้ โดยข้อความ "บทบาทคุณ" ต่างกันต่อกลุ่ม (`r` ใน register)
- ป้ายสถานะควบคุมระดับการ์ด: `linkwrong` `nolink` `noform` `pdfonly` `notinlef` `shadow`
- ทะเบียนกลาง 52 แถว + filter + ค้นหา
- cross-link: ฟอร์มที่ `"app":"audit"` (CAR/IAC/VAC/SAC/SSC) มีปุ่มไปประตูงานตรวจสอบ

### ค้างไว้ (เฟสถัดไป)

1. **`users/{uid}.roles`** — โค้ดอ่านแล้ว (`db.collection('users').doc(uid)`) แต่ **ยังไม่มี Firestore rule + ยังไม่มี document**
   ตอนนี้ถ้าอ่านไม่ได้จะ fallback แสดงทุกกลุ่มพร้อมข้อความบอก · ต้องเพิ่ม rule `match /users/{uid} { allow read: if request.auth.uid == uid; }` และสร้าง doc ให้แต่ละคน
2. เฟส 2 — form engine 3 ตัว (dynamic/rule · approval-route · scoring/gate) + นำร่อง FRAE / ASF / PCR-FI
3. `formpacks/<formCode>/<rev>/form.json` — โครง schema ฟอร์ม (ยังไม่สร้าง)
4. DOCX export ด้วย docxtemplater โดยใช้ `.docx` ในโฟลเดอร์ root เป็นแม่แบบ
5. **ยังไม่ push** — build แล้วในเครื่องเท่านั้น ยังไม่ deploy ขึ้น GitHub Pages
