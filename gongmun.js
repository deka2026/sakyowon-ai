/**
 * 망남 신활력증진사업 월별 공문 자동생성
 * 사용법: node gongmun.js [보고월]
 * 예시:   node gongmun.js 7    → 7월 실적 / 8월 계획 공문
 *         node gongmun.js      → 현재 월 기준 자동
 */

const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  ImageRun, AlignmentType, BorderStyle, WidthType, VerticalAlign,
  ShadingType, Footer
} = require('docx');
const fs = require('fs');
const path = require('path');

// ─────────────────────────────────────────────
// 1. 월 계산
// ─────────────────────────────────────────────
const args = process.argv.slice(2);
const today = new Date();
const REPORT_MONTH = args[0] ? parseInt(args[0]) : today.getMonth() + 1;
const NEXT_MONTH   = REPORT_MONTH === 12 ? 1 : REPORT_MONTH + 1;
const YEAR         = today.getFullYear();

// 시행일: 해당 월 다음 달 3일 (보고서 제출일)
const SUBMIT_MONTH  = NEXT_MONTH;
const SUBMIT_YEAR   = REPORT_MONTH === 12 ? YEAR + 1 : YEAR;
const SUBMIT_DATE   = `${SUBMIT_YEAR}${String(SUBMIT_MONTH).padStart(2,'0')}03`;
const SUBMIT_TEXT   = `${SUBMIT_YEAR}. ${SUBMIT_MONTH}. 3.`;

console.log(`📄 ${REPORT_MONTH}월 실적 / ${NEXT_MONTH}월 계획 공문 생성 중...`);
console.log(`📅 시행일: ${SUBMIT_TEXT}`);

// ─────────────────────────────────────────────
// 2. 페이지 설정
// ─────────────────────────────────────────────
const PAGE_W   = 11906;
const MARGIN   = 1134;
const CONTENT_W = PAGE_W - MARGIN * 2;

const border   = { style: BorderStyle.SINGLE, size: 4, color: "000000" };
const borders  = { top: border, bottom: border, left: border, right: border };

// ─────────────────────────────────────────────
// 3. 로고 이미지 (같은 폴더의 logo.png 사용)
// ─────────────────────────────────────────────
const LOGO_PATH = path.join(__dirname, 'logo.png');
let logoData = null;
if (fs.existsSync(LOGO_PATH)) {
  logoData = fs.readFileSync(LOGO_PATH);
} else {
  console.warn('⚠️  logo.png 없음 - 로고 생략');
}
const LOGO_W = 700;
const LOGO_H = Math.round(700 * 138 / 889);

// ─────────────────────────────────────────────
// 4. 텍스트 헬퍼
// ─────────────────────────────────────────────
const T = (text, opts = {}) => new TextRun({
  text,
  font: "맑은 고딕",
  size: opts.size || 22,
  bold: opts.bold || false,
});

const P = (children, opts = {}) => new Paragraph({
  spacing: { line: 360, lineRule: "auto", ...opts.spacing },
  indent: opts.indent,
  border: opts.border,
  alignment: opts.align,
  children: Array.isArray(children) ? children : [children],
});

// ─────────────────────────────────────────────
// 5. 하단 표 (Footer)
// ─────────────────────────────────────────────
const makeBottomTable = () => new Table({
  width: { size: CONTENT_W, type: WidthType.DXA },
  columnWidths: [CONTENT_W / 2, CONTENT_W / 2],
  rows: [
    // 1행: 담당자
    new TableRow({ children: [
      new TableCell({
        borders, width: { size: CONTENT_W / 2, type: WidthType.DXA },
        shading: { fill: "EEEEEE", type: ShadingType.CLEAR },
        verticalAlign: VerticalAlign.CENTER,
        children: [P(T("공동체팀장  김지희", { size: 20 }), { align: AlignmentType.CENTER })]
      }),
      new TableCell({
        borders, width: { size: CONTENT_W / 2, type: WidthType.DXA },
        shading: { fill: "EEEEEE", type: ShadingType.CLEAR },
        verticalAlign: VerticalAlign.CENTER,
        children: [P(T("대표  김일영", { size: 20 }), { align: AlignmentType.CENTER })]
      }),
    ]}),
    // 2행: 시행 (병합)
    new TableRow({ children: [
      new TableCell({
        borders, columnSpan: 2, width: { size: CONTENT_W, type: WidthType.DXA },
        children: [P(T(`시행  사교원-${SUBMIT_DATE}-1  ( ${SUBMIT_TEXT} )  접수`, { size: 20 }))]
      }),
    ]}),
    // 3행: 주소+전화 (병합)
    new TableRow({ children: [
      new TableCell({
        borders, columnSpan: 2, width: { size: CONTENT_W, type: WidthType.DXA },
        children: [
          P(T("우 59111  전라남도 완도군 완도읍 군내길 209-1, 2층  /  http://sakyowon.co.kr", { size: 18 })),
          P(T("전화번호  061-555-0631  팩스번호  042-825-3745  /  mangnam.anchor@gmail.com  /  공개", { size: 18 })),
        ]
      }),
    ]}),
  ]
});

// ─────────────────────────────────────────────
// 6. 문서 생성
// ─────────────────────────────────────────────
const children = [];

// 로고
if (logoData) {
  children.push(P(
    new ImageRun({
      type: "png", data: logoData,
      transformation: { width: LOGO_W, height: LOGO_H },
      altText: { title: "로고", description: "사회혁신교육원 사회적협동조합", name: "logo" }
    }),
    { spacing: { after: 200 } }
  ));
}

// 수신/경유/제목
children.push(
  P(T("수신    완도군수(지역개발과장)"), { spacing: { before: 100, after: 0, line: 360, lineRule: "auto" } }),
  P(T("(경유)"),                        { spacing: { before: 0,   after: 0, line: 360, lineRule: "auto" } }),
  P(T(`제목    ${YEAR}년 ${REPORT_MONTH}월 앵커조직 활동실적 및 ${NEXT_MONTH}월 활동계획 보고`, { bold: true }),
    { spacing: { before: 0, after: 240, line: 360, lineRule: "auto" },
      border: { bottom: { style: BorderStyle.THICK, size: 12, color: "000000" } } }
  ),
);

// 본문
children.push(
  P(T("1. 귀 청의 무궁한 발전을 기원합니다."), { spacing: { before: 120, after: 0, line: 360, lineRule: "auto" } }),
  P(T(`2. 「완도 망남생활권 어촌신활력 증진사업」 앵커조직의 ${YEAR}년 ${REPORT_MONTH}월 활동실적 및 ${NEXT_MONTH}월 활동계획을 보고합니다.(붙임 자료 참조)`),
    { spacing: { before: 120, after: 0, line: 360, lineRule: "auto" } }
  ),
);

// 붙임 항목
const items = [
  "앵커조직 기본 현황",
  `${YEAR}년 ${REPORT_MONTH}월 사업별 추진 실적과 ${NEXT_MONTH}월 추진 계획`,
  "사업별 세부 추진 내용",
  "개인별 업무 실적 및 계획",
  "앵커조직 운영비 총괄 집행 내역(누계)",
  "제작물 및 성과물",
];
items.forEach(item => {
  children.push(P(T(`- ${item}`), {
    spacing: { before: 0, after: 0, line: 360, lineRule: "auto" },
    indent: { left: 720 },
  }));
});

// 빈 줄
children.push(P(T(""), { spacing: { before: 240, after: 0 } }));

// 붙임
children.push(
  P(T(`붙임  1. 망남생활권 앵커조직 ${YEAR}년 ${REPORT_MONTH}월 실적보고 및 ${NEXT_MONTH}월 업무계획.`),
    { spacing: { before: 0, after: 0, line: 360, lineRule: "auto" } }
  ),
  P(T("      2. 앵커 직원 주간업무일지 묶음.  끝."),
    { spacing: { before: 0, after: 0, line: 360, lineRule: "auto" } }
  ),
);

const doc = new Document({
  sections: [{
    properties: {
      page: {
        size: { width: PAGE_W, height: 16838 },
        margin: { top: MARGIN, bottom: 800, left: MARGIN, right: MARGIN }
      }
    },
    footers: {
      default: new Footer({
        children: [
          P(T("사회혁신교육원사회적협동조합", { size: 36, bold: true }), {
            align: AlignmentType.CENTER,
            spacing: { before: 0, after: 160 },
          }),
          makeBottomTable(),
        ]
      })
    },
    children,
  }]
});

// ─────────────────────────────────────────────
// 7. 파일 저장
// ─────────────────────────────────────────────
const OUTPUT = path.join(__dirname, `공문_${YEAR}_${REPORT_MONTH}월.docx`);
Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync(OUTPUT, buffer);
  console.log(`✅ 완료: ${OUTPUT}`);
});
