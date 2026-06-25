const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  ImageRun, AlignmentType, BorderStyle, WidthType, VerticalAlign,
  ShadingType, Footer
} = require('docx');
const fs = require('fs');

const PAGE_W = 11906;
const MARGIN = 1134;
const CONTENT_W = PAGE_W - MARGIN * 2;

const border = { style: BorderStyle.SINGLE, size: 4, color: "000000" };
const borders = { top: border, bottom: border, left: border, right: border };

const logoData = fs.readFileSync("/mnt/user-data/uploads/1782355274657_image.png");
const LOGO_W = 700;
const LOGO_H = Math.round(700 * 138 / 889);

const LINE_SPACING = { line: 360, lineRule: "auto" }; // 150% = 240*1.5=360

// 하단 표 (footer용)
const bottomTable = new Table({
  width: { size: CONTENT_W, type: WidthType.DXA },
  columnWidths: [CONTENT_W / 2, CONTENT_W / 2],
  rows: [
    new TableRow({
      children: [
        new TableCell({
          borders,
          width: { size: CONTENT_W / 2, type: WidthType.DXA },
          shading: { fill: "EEEEEE", type: ShadingType.CLEAR },
          verticalAlign: VerticalAlign.CENTER,
          children: [new Paragraph({
            alignment: AlignmentType.CENTER,
            children: [new TextRun({ text: "공동체팀장  김지희", font: "맑은 고딕", size: 20 })]
          })]
        }),
        new TableCell({
          borders,
          width: { size: CONTENT_W / 2, type: WidthType.DXA },
          shading: { fill: "EEEEEE", type: ShadingType.CLEAR },
          verticalAlign: VerticalAlign.CENTER,
          children: [new Paragraph({
            alignment: AlignmentType.CENTER,
            children: [new TextRun({ text: "대표  김일영", font: "맑은 고딕", size: 20 })]
          })]
        }),
      ]
    }),
    new TableRow({
      children: [
        new TableCell({
          borders,
          columnSpan: 2,
          width: { size: CONTENT_W, type: WidthType.DXA },
          children: [new Paragraph({
            children: [new TextRun({ text: "시행  사교원-20260703  ( 2026. 7. 3. )  접수", font: "맑은 고딕", size: 20 })]
          })]
        }),
      ]
    }),
    new TableRow({
      children: [
        new TableCell({
          borders,
          columnSpan: 2,
          width: { size: CONTENT_W, type: WidthType.DXA },
          children: [
            new Paragraph({
              children: [new TextRun({ text: "우 59111  전라남도 완도군 완도읍 군내길 209-1, 2층  /  http://sakyowon.co.kr", font: "맑은 고딕", size: 18 })]
            }),
            new Paragraph({
              children: [new TextRun({ text: "전화번호  061-555-0631  팩스번호  042-825-3745  /  mangnam.anchor@gmail.com  /  공개", font: "맑은 고딕", size: 18 })]
            }),
          ]
        }),
      ]
    }),
  ]
});

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
          // 기관명
          new Paragraph({
            alignment: AlignmentType.CENTER,
            spacing: { before: 0, after: 160 },
            children: [new TextRun({ text: "사회혁신교육원사회적협동조합", font: "맑은 고딕", size: 36, bold: true })]
          }),
          // 하단 표
          bottomTable,
        ]
      })
    },
    children: [

      // 1. 로고
      new Paragraph({
        spacing: { after: 200 },
        children: [
          new ImageRun({
            type: "png",
            data: logoData,
            transformation: { width: LOGO_W, height: LOGO_H },
            altText: { title: "로고", description: "사회혁신교육원 사회적협동조합", name: "logo" }
          })
        ]
      }),

      // 2. 수신
      new Paragraph({
        spacing: { before: 100, after: 0, line: 360, lineRule: "auto" },
        children: [new TextRun({ text: "수신    완도군수(지역개발과장)", font: "맑은 고딕", size: 22 })]
      }),

      // 3. 경유
      new Paragraph({
        spacing: { before: 0, after: 0, line: 360, lineRule: "auto" },
        children: [new TextRun({ text: "(경유)", font: "맑은 고딕", size: 22 })]
      }),

      // 4. 제목 (밑 실선)
      new Paragraph({
        spacing: { before: 0, after: 240, line: 360, lineRule: "auto" },
        border: { bottom: { style: BorderStyle.THICK, size: 12, color: "000000" } },
        children: [new TextRun({ text: "제목    2026년 6월 앵커조직 활동실적 및 7월 활동계획 보고", font: "맑은 고딕", size: 22, bold: true })]
      }),

      // 5. 본문 1
      new Paragraph({
        spacing: { before: 120, after: 0, line: 360, lineRule: "auto" },
        children: [new TextRun({ text: "1. 귀 청의 무궁한 발전을 기원합니다.", font: "맑은 고딕", size: 22 })]
      }),

      // 6. 본문 2
      new Paragraph({
        spacing: { before: 120, after: 0, line: 360, lineRule: "auto" },
        children: [new TextRun({ text: "2. 「완도 망남생활권 어촌신활력 증진사업」 앵커조직의 2026년 6월 활동실적 및 7월 활동계획을 보고합니다.(붙임 자료 참조)", font: "맑은 고딕", size: 22 })]
      }),

      // 7. 붙임 항목
      ...["앵커조직 기본 현황", "2026년 6월 사업별 추진 실적과 7월 추진 계획", "사업별 세부 추진 내용", "개인별 업무 실적 및 계획", "앵커조직 운영비 총괄 집행 내역(누계)", "제작물 및 성과물"].map(item =>
        new Paragraph({
          spacing: { before: 0, after: 0, line: 360, lineRule: "auto" },
          indent: { left: 720 },
          children: [new TextRun({ text: `- ${item}`, font: "맑은 고딕", size: 22 })]
        })
      ),

      // 8. 빈 줄
      new Paragraph({ spacing: { before: 240, after: 0 }, children: [new TextRun("")] }),

      // 9. 붙임
      new Paragraph({
        spacing: { before: 0, after: 0, line: 360, lineRule: "auto" },
        children: [new TextRun({ text: "붙임  1. 망남생활권 앵커조직 2026년 6월 실적보고 및 7월 업무계획.", font: "맑은 고딕", size: 22 })]
      }),
      new Paragraph({
        spacing: { before: 0, after: 0, line: 360, lineRule: "auto" },
        children: [new TextRun({ text: "      2. 앵커 직원 주간업무일지 묶음.  끝.", font: "맑은 고딕", size: 22 })]
      }),

    ]
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("/home/claude/공문_2026_6월.docx", buffer);
  console.log("완료");
});
