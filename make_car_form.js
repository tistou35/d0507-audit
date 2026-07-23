const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType,
  AlignmentType, BorderStyle, ShadingType, VerticalAlign, Header, Footer, PageNumber, HeightRule
} = require('docx');
const fs = require('fs');

const NAVY='1F3864', BLUE='2E75B6', LBLUE='D6E4F7', GREY='F0F4F8', GREYB='AAAAAA';
const W=9360; // usable width twips
const bAll=(sz,color)=>({top:{style:BorderStyle.SINGLE,size:sz,color},bottom:{style:BorderStyle.SINGLE,size:sz,color},left:{style:BorderStyle.SINGLE,size:sz,color},right:{style:BorderStyle.SINGLE,size:sz,color}});
const margins={top:80,bottom:80,left:130,right:130};

function run(t,o={}){return new TextRun({text:t,font:'Arial',size:o.size||20,bold:!!o.bold,color:o.color||'1A1A2A',italics:!!o.i});}
function para(t,o={}){return new Paragraph({alignment:o.align||AlignmentType.LEFT,spacing:{before:o.before||0,after:o.after||0},children:Array.isArray(t)?t:[run(t,o)]});}
function cell(children,o={}){return new TableCell({width:{size:o.w||W,type:WidthType.DXA},columnSpan:o.span,verticalAlign:o.va||VerticalAlign.CENTER,shading:o.fill?{type:ShadingType.CLEAR,fill:o.fill}:undefined,borders:o.borders||bAll(2,GREYB),margins,children:Array.isArray(children)?children:[children]});}
function row(cells,o={}){return new TableRow({height:o.h?{value:o.h,rule:HeightRule.ATLEAST}:undefined,children:cells});}
function tbl(rows,cols){return new Table({width:{size:W,type:WidthType.DXA},columnWidths:cols,rows});}

const CB='☐ ';

// ---------- title block ----------
const titleTbl=tbl([
 row([cell(para([run('D-0507 FLIGHT TRAINING CO., LTD.',{size:24,bold:true,color:'FFFFFF'})],{align:AlignmentType.CENTER}),{fill:NAVY,borders:bAll(8,NAVY)})],{h:400}),
 row([cell([para([run('CORRECTIVE ACTION REQUEST (CAR)',{size:22,bold:true,color:'FFFFFF'})],{align:AlignmentType.CENTER}),
            para([run('คำขอให้ดำเนินการแก้ไขข้อบกพร่อง',{size:18,color:'FFFFFF'})],{align:AlignmentType.CENTER})],{fill:NAVY,borders:bAll(8,NAVY)})],{h:500}),
],[W]);

const C4=[2340,2340,2340,2340];
const infoTbl=tbl([
 row([
  cell(para([run('Form: D-0507-CAR-001',{size:19,bold:true,color:'FFFFFF'})],{align:AlignmentType.CENTER}),{w:C4[0],fill:BLUE,borders:bAll(4,BLUE)}),
  cell(para([run('ISSUE NO. 01/REVISION NO. 00',{size:19,bold:true,color:'FFFFFF'})],{align:AlignmentType.CENTER}),{w:C4[1],fill:BLUE,borders:bAll(4,BLUE)}),
  cell(para([run('OMM Ref: Section 5 – Compliance Monitoring',{size:19,bold:true,color:'FFFFFF'})],{align:AlignmentType.CENTER}),{w:C4[2],fill:BLUE,borders:bAll(4,BLUE)}),
  cell(para([run('CAR No.: CAR-______-______',{size:19,bold:true,color:'FFFFFF'})],{align:AlignmentType.CENTER}),{w:C4[3],fill:BLUE,borders:bAll(4,BLUE)}),
 ],{h:360}),
],C4);

function secHeader(no,en,th,note){
 return tbl([row([cell([para([run(`${no}  ${en}`,{size:21,bold:true,color:'FFFFFF'}),run(th?`   ${th}`:'',{size:18,color:'FFFFFF'})]),
   ...(note?[para([run(note,{size:16,color:'DCE6F5'})])]:[])],{fill:BLUE,borders:bAll(4,BLUE)})],{h:330})],[W]);
}
function labelRow(pairs){ // [[label,value?,wL,wV],...]
 const cells=[]; const cols=[];
 pairs.forEach(([lab,val,wl,wv])=>{
  cells.push(cell(para(lab,{size:19,bold:true,color:NAVY}),{w:wl,fill:GREY}));
  cells.push(cell(para(val||'',{size:20}),{w:wv,fill:'FFFFFF'}));
  cols.push(wl,wv);
 });
 return {row:row(cells,{h:340}), cols};
}
function boxRow(hint,h){ return tbl([row([cell([para([run(hint||'',{size:16,i:true,color:'8A97A8'})]),para(''),para('')],{va:VerticalAlign.TOP})],{h:h||1100})],[W]); }
function gap(n){ return new Paragraph({spacing:{after:n||60},children:[]}); }

// ---------- Part 1 ----------
const p1a=labelRow([['CAR No.','',1560,3120],['Date issued','',1560,3120]]);
const p1b=labelRow([['Audit ref.','D-0507-IAC-001 / Item ID: ',1560,3120],['Source','',1560,3120]]);
const p1c=labelRow([['Regulatory ref.','TCAR PEL Part ORA: ',1560,3120],['Finding level','☐ Level 1   ☐ Level 2',1560,3120]]);
const p1d=labelRow([['Assigned to','',1560,3120],['Position',' ',1560,3120]]);
const p1e=labelRow([['Issued by (Auditor)','',1560,3120],['Due date','',1560,3120]]);
const part1=tbl([p1a.row,p1b.row,p1c.row,p1d.row,p1e.row],p1a.cols);

// classification row
const clsTbl=tbl([row([
 cell(para('Classification',{size:19,bold:true,color:NAVY}),{w:1560,fill:GREY}),
 cell(para(CB+'Doc GAP (ไม่มี/ไม่ครบในคู่มือ)      '+CB+'Implementation GAP (เขียนไว้แต่ไม่ได้ปฏิบัติ)      '+CB+'ทั้งสองกรณี',{size:19}),{w:7800}),
],{h:340})],[1560,7800]);

// ---------- signatures ----------
const C3=[3120,3120,3120];
const sigTbl=tbl([
 row([
  cell(para('Responsible Person / ผู้รับผิดชอบ',{size:19,bold:true,color:NAVY,align:AlignmentType.CENTER}),{w:C3[0],fill:LBLUE}),
  cell(para('Auditor / ผู้ตรวจ',{size:19,bold:true,color:NAVY,align:AlignmentType.CENTER}),{w:C3[1],fill:LBLUE}),
  cell(para('Compliance Monitoring Manager',{size:19,bold:true,color:NAVY,align:AlignmentType.CENTER}),{w:C3[2],fill:LBLUE}),
 ],{h:320}),
 row([0,1,2].map(i=>cell([gap(400),para('ลงชื่อ ............................................',{align:AlignmentType.CENTER}),
   para('( ............................................ )',{align:AlignmentType.CENTER}),
   para('วันที่ ............ / ............ / ............',{align:AlignmentType.CENTER}),gap(60)],{w:C3[i],va:VerticalAlign.BOTTOM})),{h:1200}),
],C3);

// closure
const cloTbl=tbl([
 row([
  cell(para('Closure decision',{size:19,bold:true,color:NAVY}),{w:2340,fill:GREY}),
  cell(para(CB+'Accepted — CAR closed        '+CB+'Rejected — further action required (new due date: ....................)',{size:19}),{w:7020}),
 ],{h:340}),
 row([
  cell(para('Verification evidence',{size:19,bold:true,color:NAVY}),{w:2340,fill:GREY}),
  cell([para(''),para('')],{w:7020,va:VerticalAlign.TOP}),
 ],{h:600}),
 row([
  cell(para('Close date',{size:19,bold:true,color:NAVY}),{w:2340,fill:GREY}),
  cell(para('',{}),{w:7020}),
 ],{h:340}),
],[2340,7020]);

// note
const noteTbl=tbl([row([cell([
 para([run('หมายเหตุ: ',{size:17,bold:true,color:NAVY}),run('1) ผู้รับผิดชอบต้องวิเคราะห์สาเหตุราก กำหนดการแก้ไข และส่งฟอร์มกลับภายในกำหนด  2) แนบหลักฐานประกอบ (ภาพถ่าย/เอกสาร) ทุกครั้ง  3) CAR ปิดได้เมื่อผู้ตรวจ/CMM ทวนสอบประสิทธิผลแล้วเท่านั้น  4) บันทึกลงทะเบียน CAR Register และรายงานสถานะในการประชุมทบทวนฝ่ายบริหาร (OMM Section 5)',{size:17})]),
],{fill:GREY,borders:bAll(8,NAVY),va:VerticalAlign.TOP})],{h:500})],[W]);

const doc=new Document({
 styles:{default:{document:{run:{font:'Arial',size:20}}}},
 sections:[{
  properties:{page:{size:{width:11906,height:16838},margin:{top:900,bottom:900,left:900,right:900}}},
  headers:{default:new Header({children:[new Paragraph({alignment:AlignmentType.CENTER,
    border:{bottom:{style:BorderStyle.SINGLE,size:8,color:NAVY,space:4}},
    children:[run('D-0507 Flight Training Co., Ltd.  —  Corrective Action Request (CAR)  —  CONTROLLED',{size:17,bold:true,color:NAVY})]})]})},
  footers:{default:new Footer({children:[new Paragraph({alignment:AlignmentType.CENTER,
    border:{top:{style:BorderStyle.SINGLE,size:8,color:NAVY,space:4}},
    children:[run('D-0507-CAR-001  |  Issue 01 Rev 00  |  OMM Ref: Section 5  |  Page ',{size:17,color:'808080'}),
      new TextRun({font:'Arial',size:17,color:'808080',children:[PageNumber.CURRENT]})]})]})},
  children:[
   titleTbl, gap(80), infoTbl, gap(120),
   secHeader('PART 1','CAR INFORMATION','ข้อมูลทั่วไป'), part1, clsTbl, gap(120),
   secHeader('PART 2','FINDING / NONCONFORMITY','ข้อบกพร่องที่พบ','(Auditor กรอก — ระบุข้อเท็จจริง หลักฐาน และข้อกำหนดที่เกี่ยวข้อง)'),
   boxRow('Description of finding / objective evidence / photo ref. ...',1400), gap(120),
   secHeader('PART 3','ROOT CAUSE ANALYSIS','การวิเคราะห์สาเหตุราก','(ผู้รับผิดชอบกรอก)'),
   boxRow('Why did this occur? (5-Why / other method) ...',1100), gap(120),
   secHeader('PART 4','CORRECTIVE ACTION','การแก้ไข','(ผู้รับผิดชอบกรอก — การดำเนินการ + วันที่แล้วเสร็จ)'),
   boxRow('Action taken / completion date ...',1100), gap(120),
   secHeader('PART 5','PREVENTIVE ACTION','การป้องกันการเกิดซ้ำ'),
   boxRow('Action to prevent recurrence ...',900), gap(120),
   secHeader('PART 6','VERIFICATION & CLOSURE','การทวนสอบและปิด CAR','(Auditor / CMM กรอก)'),
   cloTbl, gap(160),
   sigTbl, gap(120),
   noteTbl,
  ],
 }],
});
Packer.toBuffer(doc).then(b=>{fs.writeFileSync('/home/claude/audit/D-0507-CAR-001.docx',b);console.log('written',b.length);});
