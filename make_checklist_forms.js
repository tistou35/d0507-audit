const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType,
  AlignmentType, BorderStyle, ShadingType, VerticalAlign, Header, Footer, PageNumber, HeightRule
} = require('docx');
const fs = require('fs');
const DATA = JSON.parse(fs.readFileSync('/home/claude/audit/forms_data.json','utf8'));

const NAVY='1F3864', BLUE='2E75B6', LBLUE='D6E4F7', GREY='F0F4F8', GREYB='AAAAAA';
const W=9360;
const bAll=(sz,c)=>({top:{style:BorderStyle.SINGLE,size:sz,color:c},bottom:{style:BorderStyle.SINGLE,size:sz,color:c},left:{style:BorderStyle.SINGLE,size:sz,color:c},right:{style:BorderStyle.SINGLE,size:sz,color:c}});
const margins={top:60,bottom:60,left:110,right:110};
const run=(t,o={})=>new TextRun({text:t,font:'Arial',size:o.size||19,bold:!!o.bold,color:o.color||'1A1A2A',italics:!!o.i});
const para=(t,o={})=>new Paragraph({alignment:o.align||AlignmentType.LEFT,spacing:{before:o.before||0,after:o.after||0},children:Array.isArray(t)?t:[run(t,o)]});
const cell=(ch,o={})=>new TableCell({width:{size:o.w||W,type:WidthType.DXA},columnSpan:o.span,verticalAlign:o.va||VerticalAlign.CENTER,shading:o.fill?{type:ShadingType.CLEAR,fill:o.fill}:undefined,borders:o.borders||bAll(2,GREYB),margins,children:Array.isArray(ch)?ch:[ch]});
const row=(cells,o={})=>new TableRow({height:o.h?{value:o.h,rule:HeightRule.ATLEAST}:undefined,children:cells});
const tbl=(rows,cols)=>new Table({width:{size:W,type:WidthType.DXA},columnWidths:cols,rows});
const gap=(n)=>new Paragraph({spacing:{after:n||60},children:[]});
const CB='☐';
const MT={OBS:'สังเกตการณ์',DOC:'ตรวจบันทึก',INT:'สัมภาษณ์',XCK:'ตรวจไขว้',DEMO:'ให้สาธิต'};

const FORMS=[
 {mod:'VEN', code:'D-0507-VAC-001', title:'VENDOR / CONTRACTED SERVICES AUDIT CHECKLIST', th:'รายการตรวจผู้ให้บริการภายนอก',
  ref:'ORA.GEN.205 · OMM Section 5', dual:false,
  info:[['Vendor name','','Service type',''],['Contract No. / validity','','Vendor location',''],['Audit date','','Auditor','']]},
 {mod:'SAF', code:'D-0507-SAC-001', title:'SCHOOL SAFETY AUDIT CHECKLIST', th:'รายการตรวจนิรภัยภาพรวมของโรงเรียน (SMS)',
  ref:'OMM · OMA · TM · TCAR-ORA GEN.200', dual:true,
  info:[['Audit period','','Audit date',''],['Auditor(s)','','Scope','ทั้งโรงเรียน / ระบุ: ']]},
 {mod:'SUR', code:'D-0507-SSC-001', title:'SAFETY SURVEILLANCE CHECKLIST', th:'รายการเฝ้าสังเกตการณ์กิจกรรม (Spot Check)',
  ref:'FSOP 2024 · MMSOP 2024', dual:false,
  info:[['Activity observed','','Date / Time',''],['Location','','Persons observed',''],['Observer','','Aircraft / Equipment','']]},
];

function buildForm(F){
  const m=DATA[F.mod];
  const children=[];
  // title
  children.push(tbl([
    row([cell(para([run('D-0507 FLIGHT TRAINING CO., LTD.',{size:24,bold:true,color:'FFFFFF'})],{align:AlignmentType.CENTER}),{fill:NAVY,borders:bAll(8,NAVY)})],{h:380}),
    row([cell([para([run(F.title,{size:21,bold:true,color:'FFFFFF'})],{align:AlignmentType.CENTER}),
               para([run(F.th,{size:17,color:'FFFFFF'})],{align:AlignmentType.CENTER})],{fill:NAVY,borders:bAll(8,NAVY)})],{h:460}),
  ],[W]));
  children.push(gap(60));
  const C3=[3120,3120,3120];
  children.push(tbl([row([
    cell(para([run(`Form: ${F.code}`,{size:18,bold:true,color:'FFFFFF'})],{align:AlignmentType.CENTER}),{w:C3[0],fill:BLUE,borders:bAll(4,BLUE)}),
    cell(para([run('ISSUE NO. 01/REVISION NO. 00',{size:18,bold:true,color:'FFFFFF'})],{align:AlignmentType.CENTER}),{w:C3[1],fill:BLUE,borders:bAll(4,BLUE)}),
    cell(para([run(`Ref: ${F.ref}`,{size:18,bold:true,color:'FFFFFF'})],{align:AlignmentType.CENTER}),{w:C3[2],fill:BLUE,borders:bAll(4,BLUE)}),
  ],{h:340})],C3));
  children.push(gap(80));
  // info block
  const IW=[1700,2980,1700,2980];
  children.push(tbl(F.info.map(r=>row([
    cell(para(r[0],{size:18,bold:true,color:NAVY}),{w:IW[0],fill:GREY}),
    cell(para(r[1]||'',{size:19}),{w:IW[1]}),
    cell(para(r[2],{size:18,bold:true,color:NAVY}),{w:IW[2],fill:GREY}),
    cell(para(r[3]||'',{size:19}),{w:IW[3]}),
  ],{h:330})),IW));
  children.push(gap(60));
  // legend
  children.push(para([run('S',{bold:true,size:17,color:'1A6B1A'}),run(' = Satisfactory (สอดคล้อง/มี)   ',{size:17}),
    run('U',{bold:true,size:17,color:'C00000'}),run(' = Unsatisfactory (GAP – ออก CAR)   ',{size:17}),
    run('N/A',{bold:true,size:17}),run(' = ไม่เกี่ยวข้อง',{size:17}),
    ...(F.dual?[run('   ·   Doc = เขียนไว้ในคู่มือครบ?   Impl = ปฏิบัติจริง/มีหลักฐาน?',{size:17,color:'9C6500'})]:[])],{after:80}));

  const COLS = F.dual ? [560,4340,1080,1080,2300] : [560,4640,430,430,520,2780];
  m.parts.forEach(p=>{
    // part header
    children.push(tbl([row([cell([para([run(p.t,{size:20,bold:true,color:'FFFFFF'})]),
      ...(p.th?[para([run(p.th,{size:16,color:'DCE6F5'})])]:[])],{fill:BLUE,borders:bAll(4,BLUE)})],{h:330})],[W]));
    // table header
    const hdr = F.dual
      ? row([cell(para('No.',{size:17,bold:true,color:NAVY,align:AlignmentType.CENTER}),{w:COLS[0],fill:LBLUE}),
             cell(para('Checklist Item / รายการตรวจ',{size:17,bold:true,color:NAVY}),{w:COLS[1],fill:LBLUE}),
             cell(para('Doc',{size:17,bold:true,color:NAVY,align:AlignmentType.CENTER}),{w:COLS[2],fill:LBLUE}),
             cell(para('Impl',{size:17,bold:true,color:NAVY,align:AlignmentType.CENTER}),{w:COLS[3],fill:LBLUE}),
             cell(para('Evidence / Remark',{size:17,bold:true,color:NAVY}),{w:COLS[4],fill:LBLUE})],{h:280})
      : row([cell(para('No.',{size:17,bold:true,color:NAVY,align:AlignmentType.CENTER}),{w:COLS[0],fill:LBLUE}),
             cell(para('Checklist Item / รายการตรวจ',{size:17,bold:true,color:NAVY}),{w:COLS[1],fill:LBLUE}),
             cell(para('S',{size:17,bold:true,color:NAVY,align:AlignmentType.CENTER}),{w:COLS[2],fill:LBLUE}),
             cell(para('U',{size:17,bold:true,color:NAVY,align:AlignmentType.CENTER}),{w:COLS[3],fill:LBLUE}),
             cell(para('N/A',{size:17,bold:true,color:NAVY,align:AlignmentType.CENTER}),{w:COLS[4],fill:LBLUE}),
             cell(para('Evidence / Remark',{size:17,bold:true,color:NAVY}),{w:COLS[5],fill:LBLUE})],{h:280});
    const rows=[hdr];
    let no=0;
    p.secs.forEach(s=>s.groups.forEach(g=>{
      // group subject row
      rows.push(row([cell(para([run(`${g.n}  ${g.subj}`,{size:18,bold:true,color:NAVY})]),{fill:GREY,span:F.dual?5:6})],{h:280}));
      g.items.forEach(it=>{
        no++;
        const body=[para([run(it.d,{size:18})])];
        if(it.th) body.push(para([run(it.th,{size:16,color:'556070'})]));
        if(it.mt&&it.mt.length) body.push(para([run('วิธีตรวจ: '+it.mt.map(x=>MT[x]||x).join(' / ')+(it.ref?`   ·   อ้างอิง: ${it.ref}`:''),{size:15,color:'7A8798',i:true})]));
        else if(it.ref) body.push(para([run('อ้างอิง: '+it.ref,{size:15,color:'7A8798',i:true})]));
        if(it.chk) it.chk.forEach(c=>body.push(para([run(`${CB} ${c}`,{size:16,color:'334455'})])));
        const mark=(w)=>cell(para(CB,{size:20,align:AlignmentType.CENTER}),{w,va:VerticalAlign.TOP});
        if(F.dual){
          rows.push(row([
            cell(para(String(no),{size:17,align:AlignmentType.CENTER}),{w:COLS[0],va:VerticalAlign.TOP}),
            cell(body,{w:COLS[1],va:VerticalAlign.TOP}),
            cell(para(`${CB}S ${CB}U ${CB}N/A`,{size:15,align:AlignmentType.CENTER}),{w:COLS[2],va:VerticalAlign.TOP}),
            cell(para(`${CB}S ${CB}U ${CB}N/A`,{size:15,align:AlignmentType.CENTER}),{w:COLS[3],va:VerticalAlign.TOP}),
            cell(para('',{size:18}),{w:COLS[4],va:VerticalAlign.TOP}),
          ]));
        } else {
          rows.push(row([
            cell(para(String(no),{size:17,align:AlignmentType.CENTER}),{w:COLS[0],va:VerticalAlign.TOP}),
            cell(body,{w:COLS[1],va:VerticalAlign.TOP}),
            mark(COLS[2]), mark(COLS[3]), mark(COLS[4]),
            cell(para('',{size:18}),{w:COLS[5],va:VerticalAlign.TOP}),
          ]));
        }
      });
    }));
    children.push(tbl(rows,COLS));
    children.push(gap(100));
  });
  // findings summary + signatures
  children.push(tbl([row([cell(para([run('SUMMARY — จำนวน U (GAP) ทั้งหมด: ............  ออก CAR เลขที่: ...........................................  แนบรูปหลักฐาน: ............ รายการ',{size:18,bold:true,color:NAVY})]),{fill:GREY,borders:bAll(8,NAVY)})],{h:340})],[W]));
  children.push(gap(80));
  const S3=[3120,3120,3120];
  const sigTitles = F.mod==='VEN' ? ['Auditor / ผู้ตรวจ','Vendor Representative / ผู้แทนผู้ให้บริการ','Compliance Monitoring Manager']
                  : F.mod==='SUR' ? ['Observer / ผู้สังเกตการณ์','Safety Manager','Head of Training']
                  : ['Auditor / ผู้ตรวจ','Safety Manager','Accountable Manager'];
  children.push(tbl([
    row(sigTitles.map((t,i)=>cell(para(t,{size:18,bold:true,color:NAVY,align:AlignmentType.CENTER}),{w:S3[i],fill:LBLUE})),{h:300}),
    row([0,1,2].map(i=>cell([gap(340),para('ลงชื่อ ............................................',{align:AlignmentType.CENTER,size:18}),
      para('( ............................................ )',{align:AlignmentType.CENTER,size:18}),
      para('วันที่ ............ / ............ / ............',{align:AlignmentType.CENTER,size:18})],{w:S3[i],va:VerticalAlign.BOTTOM})),{h:1050}),
  ],S3));

  const doc=new Document({
    styles:{default:{document:{run:{font:'Arial',size:19}}}},
    sections:[{
      properties:{page:{size:{width:11906,height:16838},margin:{top:900,bottom:900,left:900,right:900}}},
      headers:{default:new Header({children:[new Paragraph({alignment:AlignmentType.CENTER,
        border:{bottom:{style:BorderStyle.SINGLE,size:8,color:NAVY,space:4}},
        children:[run(`D-0507 Flight Training Co., Ltd.  —  ${F.title}  —  CONTROLLED`,{size:16,bold:true,color:NAVY})]})]})},
      footers:{default:new Footer({children:[new Paragraph({alignment:AlignmentType.CENTER,
        border:{top:{style:BorderStyle.SINGLE,size:8,color:NAVY,space:4}},
        children:[run(`${F.code}  |  Issue 01 Rev 00  |  ${F.ref}  |  Page `,{size:16,color:'808080'}),
          new TextRun({font:'Arial',size:16,color:'808080',children:[PageNumber.CURRENT]})]})]})},
      children,
    }],
  });
  return Packer.toBuffer(doc).then(b=>{fs.writeFileSync(`/home/claude/audit/${F.code}.docx`,b);console.log(F.code,b.length);});
}
(async()=>{ for(const F of FORMS) await buildForm(F); })();
