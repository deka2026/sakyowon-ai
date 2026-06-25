/**
 * 망남생활권 어촌신활력증진사업 앵커조직
 * 실적 및 업무계획 자동생성 스크립트
 * 
 * 사용법: node siljeok.js <보고월> [데이터파일.js]
 * 예시:  node siljeok.js 6
 *        node siljeok.js 6 data_june.js
 */

const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  AlignmentType, BorderStyle, WidthType, ShadingType, VerticalAlign,
  PageBreak, LevelFormat, HeadingLevel
} = require('docx');
const fs = require('fs');
const path = require('path');

// ──────────────────────────────────────────
// 1. 고정값 (매월 변하지 않음)
// ──────────────────────────────────────────
const FIXED = {
  title: '망남생활권 어촌신활력증진사업 앵커조직',
  region: '완도군 지역개발과\n어촌활력팀',
  manager: '서희웅 주무관 / 010-4174-1300',
  area: '완도군 완도읍 군내리 59-8 일원(망남리)',
  selectedYear: '2023년',
  budget: '100억\n(국비 70%, 지방비 30%)',
  period: "'23~'26(4년)",
  budgetBreakdown: '어항시설 정비(30억원, 30%), 시설조성 및 운영(40억원, 40%),\n활력사업(10억원, 10%), 앵커조직 운영(20억원, 20%)',
  businessContent: [
    "ㅇ '어촌 삶의 질 개선을 통한 지속가능한 어촌 만들기'를 핵심 목표로 설정하여 생활서비스 연계 및 확충, 지역 경제 활성화 도모",
    "- 노년층이 많은 생활권 주민에게 꼭 필요한 돌봄서비스 기반 구축",
    "- 주민을 위한 안전하고 깨끗한 어촌마을 환경개선",
    "- 전국의 관계인구 유입을 위한 생활권만의 브랜드 발굴",
    "- 다양한 실험 사업을 통해 생활권 주민과 관계인구를 만족시키는 경쟁력 발굴",
  ],
  anchorName: '사회혁신교육원\n사회적협동조합',
  contractDate: "계약('23. 07. 04.)",
  anchorContact: '김일영 / 061-555-0631, 010-5545-4522',
  anchorAddress: '완도군 완도읍 군내길 209-1, 2층',
  anchorHistory: [
    '· 양양 후진항 어촌신활력증진사업 앵커조직 선정(2026)',
    '· 해남군 사회적공동체지원센터 위탁 선정(\'24~\'26)',
    '· 인하대학교 지역사회문제해결형 수업 연구 및 수업 운영(\'23.05.)',
    '· 화성시 서신면 주민자치형공공서비스 발전계획 수립(\'22.10.)',
    '· 안성시 푸드플랜 시민역량강화 교육 운영(\'22.07.)',
    '· 사회적경제분야별 창업입문과정 운영 용역(\'22.06.)',
    '· 세종시 청년센터 세청나래 활성화 방안 연구 용역(\'22.05.)',
    '· 인천 서구 푸드플랜 수립 연구 용역(\'21.12.)',
    '· 도봉구 협치체계 현황 진단 및 개선 방안 연구 용역(\'21.09.)',
    '· 목원대학교 지역선도 역량업캠프 운영(\'21.09.)',
    '· 주민자치 전국 민관학 현장 포럼 및 교육 운영(\'21.07.)',
    '· 소상공인 협업 활성화 방안 연구 용역(\'20.12.)',
  ],
  // 사업명·예산·목적 (사업번호별 고정)
  projects: [
    {
      no: 1, name: '시행계획과 후속사업 발굴',
      budget25: null, budget26: null,
      purpose: [
        '기본계획 승인에 따라 시행계획 수립과 시공, 소프트웨어 사업을 추진',
        '주민들의 요구와 기본계획 내용에 적합한 하드웨어 및 소프트웨어 사업이 원만히 추진되도록 앵커조직이 조정하고 공정관리를 하는 것',
        '후속사업 발굴을 위한 지속적인 조사와 주민 논의를 통해 사업종료 후 지속가능성을 높임',
      ],
      quantTarget: '햇빛소득마을 선정',
    },
    {
      no: 2, name: '사업체계 운영(지역협의체 운영, 주민역량강화)',
      budget25: '71,600,000', budget26: null,
      purpose: [
        '기본계획 승인에 따른 단위사업별 지역협의체 위원 재구성 및 회의 운영',
        '기본계획의 적확한 진행 점검을 위한 모니터링단 운영',
        '사업의 원활한 추진과 이행관계자 간 협력 체계 구축 및 사업진행 점검',
        '선진 사업지 견학 등 주민 역량 강화',
        '사업 종료 후 지속가능한 어촌스테이션 운영주체의 마련',
      ],
      quantTarget: [
        '신임 주민리더들과의 상시적 소통체계 구축 및 사업 이해 증진',
        '마을 내 링커와의 협력체계 안정화',
        '단위 사업 주요 목표를 위한 관내 링커와의 협력 구조 구축',
      ],
    },
    {
      no: 3, name: '전복특화생태마을 지정 준비',
      budget25: '35,900,000', budget26: null,
      purpose: [
        '망남특화마을 시범 운영을 통해 어촌·생태·건강·생활기술실험을 통합한 특화마을 모델 구축 여건 마련',
        '어민건강포럼과 연계하여 건강관리실 홍보 및 근골격계 질환 예방 마을로서 이미지 제고, 지역 공공의료 전달체계 공론장 마련',
        '사업 종료 후 특화마을 운영 시스템 안정화',
      ],
      quantTarget: '신활력증진사업 종료 이후 연계 사업 후보 3건 발굴(어촌체험마을, 유어장·어싱장 지정, 평생교육 이용권)',
    },
    {
      no: 4, name: 'ESG 맞춤형 유통체계 혁신',
      budget25: '34,900,000', budget26: null,
      purpose: [
        '기존 공동구매(도시공동체) 대상지의 확대와 일상적 판매 체계 운영',
        '직거래형 공동구매 시 거점이 있는 지역의 제로웨이스트 추진',
        '전복 생산자 주도 유통을 지원할 수 있는 다양한 콘텐츠 개발과 온라인 셀러 양성',
      ],
      quantTarget: '생산자 주도 유통체계 가치사슬체계 구축',
    },
    {
      no: 5, name: '일반운영 및 홍보',
      budget25: '86,600,000', budget26: '81,250,000',
      purpose: [
        '철저한 집행 관리 등을 통한 예산 운영의 투명성, 정확성 추구',
        '지속적인 실무자 역량강화로 사업전문성 및 앵커조직 운영 고도화',
        '홍보를 통한 망남생활권 활동 사례, 소식 확산',
        '주민리더모임, 지역협의체 운영으로 사업의 원활하고 효과적인 의견 수렴, 지역 공감대 형성',
        '리모델링 공사 중 사무공간 임차를 통해 본사업의 원할한 운영 지속',
      ],
      quantTarget: ['직원 전문영역 역량 강화', '망남어촌신활력 사업 홍보 운영', '회계 관리 철저'],
    },
  ],
};

// ──────────────────────────────────────────
// 2. 월별 변동 데이터 템플릿
//    실제 사용 시 아래 DATA 객체를 직접 편집하거나
//    외부 JS 파일로 불러올 것
// ──────────────────────────────────────────
function getDefaultData(reportMonth) {
  const nextMonth = reportMonth + 1;
  return {
    reportMonth,       // 보고 대상월 (숫자, 예: 6)
    nextMonth,         // 계획 대상월 (숫자, 예: 7)
    year: 2026,

    // ── 업무별 요약표 (2페이지) ──────────────────
    summary: [
      {
        category: '기본계획과\n후속사업 발굴',
        thisMonth: ['특화마을 관련 연계사업 리서치\n- (이번달 주요 실적 입력)'],
        nextMonth: ['특화마을 관련 연계사업 리서치\n- (다음달 계획 입력)'],
      },
      {
        category: '사업추진체계\n운영',
        thisMonth: ['(이번달 실적 입력)'],
        nextMonth: ['(다음달 계획 입력)'],
      },
      {
        category: '단위사업',
        thisMonth: ['(이번달 실적 입력)'],
        nextMonth: ['(다음달 계획 입력)'],
      },
      {
        category: '앵커조직\n운영',
        thisMonth: [
          '마을 진입로 예초작업',
          '사무실 및 공유 공간 관리',
          '앵커 회계관리',
          '아카이빙 자료 정리',
        ],
        nextMonth: [
          '홍보 용역 시행',
          '홍보 관리',
          '사무실 및 공유 공간 관리',
          '앵커 회계 관리',
          '아카이빙 자료 정리',
        ],
      },
    ],
    consultantNote: '없음',
    consultantNextNote: '없음',
    overallReview: ['(사업총평 입력)'],

    // ── 사업별 세부 추진내용 (3~7페이지) ──────────
    projectDetails: [
      {
        // 사업 1
        budget26Exec: '0', execRate: '0',
        quantResult: ['(정량적 추진실적 입력)'],
        detailContents: ['(세부 추진내용 입력)'],
        qualitResult: '(정성적 성과 입력)',
        photoCaption: '(사진 설명)',
      },
      {
        // 사업 2
        budget25Exec: '(집행액 입력)', exec25Rate: '(집행율)',
        quantResult: ['(정량적 추진실적 입력)'],
        detailContents: ['(세부 추진내용 입력)'],
        qualitResult: '(정성적 성과 입력)',
        photoCaption: '(사진 설명)',
      },
      {
        // 사업 3
        budget25Exec: '(집행액 입력)', exec25Rate: '(집행율)',
        quantResult: ['(정량적 추진실적 입력)'],
        detailContents: ['(세부 추진내용 입력)'],
        qualitResult: '(정성적 성과 입력)',
        photoCaption: '(사진 설명)',
      },
      {
        // 사업 4
        budget25Exec: '(집행액 입력)', exec25Rate: '(집행율)',
        quantResult: ['(정량적 추진실적 입력)'],
        detailContents: ['(세부 추진내용 입력)'],
        qualitResult: '(정성적 성과 입력)',
        photoCaption: '(사진 설명)',
      },
      {
        // 사업 5
        budget25Exec: '(집행액 입력)', exec25Rate: '(집행율)',
        budget26Exec: '(집행액 입력)', exec26Rate: '(집행율)',
        quantResult: ['SNS 총 (N)건 게시물', '진입로 예초작업 및 쓰레기 수거', '독거노인 주민지원'],
        detailContents: [
          '1. 홍보\n- SNS (N)건 업데이트',
          '2. 주민지원\n- 독거노인 애로사항 해결',
          '3. 마을진입로 잡초 예초작업',
        ],
        qualitResult: '소셜미디어 활용한 망남생활권 홍보 지속\n홍보채널 통합 운영 준비\n마을 주민 지원 및 소통 지속',
        photoCaption: '홍보 및 기타 관련',
      },
    ],

    // ── 개인별 업무 (8~9페이지) ──────────────────
    personnel: [
      {
        name: '김일영\n(100%)\n/\n앵커\n조직 대표',
        thisMonth: [
          '□ 앵커사업 총괄 업무\n(이번달 총괄 실적 입력)',
          '□ 일상 마을지원 업무\n마을 독거노인 동정 파악 주1회\n마을진입로 예초작업',
          '□ 단위사업 관련 업무\n(단위사업 실적 입력)',
          '□ 법인 사무\n(법인 사무 실적 입력)',
        ],
        nextMonth: [
          '□ 앵커사업 총괄 업무\n어촌신활력증진사업 각종 보고 및 협조사항 작성 후 완도군 발송\n주간전체회의 주 1회',
          '□ 일상 마을지원 업무\n마을 독거노인 동정 파악 주1회\n마을진입로 예초작업 수시',
          '□ 단위사업 관련 업무\n(단위사업 계획 입력)',
          '□ 법인 사무\n(법인 사무 계획 입력)',
        ],
      },
      {
        name: '조영윤\n(100%)\n/\n회계담당,\n주민지원\n 실장',
        thisMonth: [
          '□ 앵커 회계 전담 업무\n앵커조직 임차료 등 지출품의, 결의, 등록, 이체 (N)건\n주간전체회의 주 1회',
          '□ 주민지원 업무\n마을주민 이동보조\n주민이용 다목적실 환경정비 및 소모품 비치',
          '□ 단위사업 업무\n(단위사업 실적 입력)',
        ],
        nextMonth: [
          '앵커조직 회계 책임자 업무 일체\n: 집행등록 및 점검, 급여 및 임차료 지급, 제세공과금 납부, 계좌이체 등',
          '사무실 시설관리 및 비품 관리 업무 일체 : 구매업무, 청소 및 안전 점검',
          '행정 요구 문서 작성 지원 : 각종 회의 및 집행점검 문서',
        ],
      },
      {
        name: '김지희\n(100%)\n/\n공동체\n 팀장',
        thisMonth: [
          '□ 앵커 행정사무 지원 업무\n주간 업무 보고 작성 주 1회, 전직원회의 주 1회\n사무실 환경정비',
          '□ 주민지원 업무\n거동 불편 어르신 이동 지원',
          '□ 단위사업 업무\n(단위사업 실적 입력)',
        ],
        nextMonth: [
          '앵커조직 행정지원 업무 일체 : 생성 문서 정리 및 편철',
          '사무실 시설관리 및 비품 관리 업무 일체 : 구매 업무, 청소 및 안전 점검',
          '행정 요구 문서 작성 지원 : 각종 회의 및 집행점검 문서',
          '마을학교 강사양성 후속사업 기획, 생태기술시연회와 연계',
          '주민 현장 견학 워크숍 기획 및 실무 준비',
          '어민건강포럼 추진체계 구축과 추진계획 협의',
        ],
      },
    ],

    // ── 집행 내역 (10페이지) ──────────────────────
    execSummary: {
      budget25Total: '594,000,000',
      budget25Granted: '594,000,000',
      budget25Exec: '(집행액)',
      budget25Remain: '(잔액)',
      budget25Rate: '(집행율)',
      budget26Total: '589,380,000',
      budget26Granted: '589,380,000',
      budget26Exec: '(집행액)',
      budget26Remain: '(잔액)',
      budget26Rate: '(집행율)',
    },

    // ── 제작물 및 성과물 (11페이지) ─────────────
    products: [
      { label: '인스타 홍보물', caption: '(홍보물 이미지 첨부)' },
      { label: '주요 활동 사진', caption: '(활동 사진 첨부)' },
    ],
  };
}

// ──────────────────────────────────────────
// 3. 헬퍼 함수
// ──────────────────────────────────────────
const CELL_MARGIN = { top: 80, bottom: 80, left: 120, right: 120 };
const BORDER_THIN = { style: BorderStyle.SINGLE, size: 1, color: '999999' };
const BORDERS_ALL = { top: BORDER_THIN, bottom: BORDER_THIN, left: BORDER_THIN, right: BORDER_THIN };
const BORDER_NONE = { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' };
const BORDERS_NONE = { top: BORDER_NONE, bottom: BORDER_NONE, left: BORDER_NONE, right: BORDER_NONE };

const FONT = 'Malgun Gothic';
const PAGE_WIDTH = 11906; // A4

function txt(text, opts = {}) {
  return new TextRun({ text, font: FONT, size: opts.size || 20, bold: opts.bold || false, color: opts.color || '000000', ...opts });
}

function para(children, opts = {}) {
  if (typeof children === 'string') children = [txt(children)];
  return new Paragraph({
    alignment: opts.align || AlignmentType.LEFT,
    spacing: { before: opts.spaceBefore || 40, after: opts.spaceAfter || 40 },
    indent: opts.indent ? { left: opts.indent } : undefined,
    children,
  });
}

function cell(content, opts = {}) {
  const paragraphs = typeof content === 'string'
    ? content.split('\n').map(line => para(line || ' ', { spaceBefore: 20, spaceAfter: 20, align: opts.align }))
    : (Array.isArray(content) ? content : [content]);
  return new TableCell({
    borders: opts.borders || BORDERS_ALL,
    width: opts.width ? { size: opts.width, type: WidthType.DXA } : undefined,
    shading: opts.shade ? { fill: opts.shade, type: ShadingType.CLEAR } : undefined,
    margins: CELL_MARGIN,
    verticalAlign: opts.vAlign || VerticalAlign.TOP,
    columnSpan: opts.span || 1,
    rowSpan: opts.rowSpan || 1,
    children: paragraphs,
  });
}

function headerCell(text, width) {
  return cell(text, { shade: 'D9E2F3', width, borders: BORDERS_ALL });
}

function sectionBreak() {
  return new Paragraph({ children: [new PageBreak()] });
}

// ──────────────────────────────────────────
// 4. 페이지별 생성 함수
// ──────────────────────────────────────────

/** 1페이지: 기본 개요 */
function buildPage1(data) {
  const { reportMonth, nextMonth, year } = data;
  const titleText = `${year}년 ${reportMonth}월 실적 및 ${nextMonth}월 업무계획`;
  const COL = [2200, 4500, 2200, 2500]; // 총 11400
  const totalW = COL.reduce((a, b) => a + b, 0);

  function infoRow(label, value, label2, value2) {
    return new TableRow({
      children: [
        cell(label, { shade: 'D9E2F3', width: COL[0] }),
        cell(value, { width: COL[1] }),
        cell(label2, { shade: 'D9E2F3', width: COL[2] }),
        cell(value2, { width: COL[3] }),
      ],
    });
  }

  return [
    para([txt(FIXED.title, { bold: true, size: 24 })], { align: AlignmentType.CENTER, spaceBefore: 200, spaceAfter: 60 }),
    para([txt(titleText, { bold: true, size: 22 })], { align: AlignmentType.CENTER, spaceAfter: 200 }),
    new Table({
      width: { size: totalW, type: WidthType.DXA },
      columnWidths: COL,
      rows: [
        infoRow('지자체/담당과', FIXED.region, '담당자/연락처', FIXED.manager),
        infoRow('대상지역', FIXED.area, '선정연도', FIXED.selectedYear),
        infoRow('사업비', FIXED.budget, '사업기간', FIXED.period),
        new TableRow({
          children: [
            cell('사업비 구성', { shade: 'D9E2F3', width: COL[0] }),
            cell(FIXED.budgetBreakdown, { width: COL[1] + COL[2] + COL[3], span: 3 }),
          ],
        }),
        new TableRow({
          children: [
            cell('사업 내용', { shade: 'D9E2F3', width: COL[0] }),
            cell(FIXED.businessContent.join('\n'), { width: COL[1] + COL[2] + COL[3], span: 3 }),
          ],
        }),
        infoRow('앵커명', FIXED.anchorName, '앵커 계약(협약)일', FIXED.contractDate),
        infoRow('앵커담당자/연락처', FIXED.anchorContact, '주소', FIXED.anchorAddress),
        new TableRow({
          children: [
            cell('앵커 활동\n주요경력', { shade: 'D9E2F3', width: COL[0] }),
            cell(FIXED.anchorHistory.join('\n'), { width: COL[1] + COL[2] + COL[3], span: 3 }),
          ],
        }),
      ],
    }),
    sectionBreak(),
  ];
}

/** 2페이지: 업무별 요약표 + 사업총평 */
function buildPage2(data) {
  const { reportMonth, nextMonth, year } = data;
  const COL = [1500, 4900, 5000]; // 총 11400
  const rows = [
    new TableRow({
      children: [
        headerCell('업무별 구분', COL[0]),
        headerCell(`이번달(${reportMonth}월) 추진 실적`, COL[1]),
        headerCell(`다음달(${nextMonth}월) 추진 계획`, COL[2]),
      ],
    }),
    ...data.summary.map(s => new TableRow({
      children: [
        cell(s.category, { shade: 'EEF2FA', width: COL[0] }),
        cell(s.thisMonth.join('\n'), { width: COL[1] }),
        cell(s.nextMonth.join('\n'), { width: COL[2] }),
      ],
    })),
    new TableRow({
      children: [
        cell('컨설턴트와 업무\n협의 내용', { shade: 'EEF2FA', width: COL[0] }),
        cell(data.consultantNote, { width: COL[1] }),
        cell(data.consultantNextNote, { width: COL[2] }),
      ],
    }),
  ];

  const totalW = COL.reduce((a, b) => a + b, 0);

  return [
    para([txt(`(${year}년) 사업별 ${reportMonth}월 추진 실적과 ${nextMonth}월 추진 계획`, { bold: true, size: 22 })], { spaceAfter: 120 }),
    new Table({ width: { size: totalW, type: WidthType.DXA }, columnWidths: COL, rows }),
    para(''),
    para([txt('미흡 및 개선점', { bold: true })], { align: AlignmentType.CENTER }),
    para(''),
    para([txt('사업총평', { bold: true, size: 20 })], { spaceBefore: 40 }),
    ...data.overallReview.map(line => para('  ' + line)),
    sectionBreak(),
  ];
}

/** 3~7페이지: 사업별 세부 추진 */
function buildProjectPage(projIdx, data) {
  const proj = FIXED.projects[projIdx];
  const detail = data.projectDetails[projIdx];
  const { reportMonth } = data;
  const COL = [2200, 3000, 2200, 4000]; // 헤더행 레이아웃
  const totalW = 11400;

  // 예산행 구성
  const budgetRows = [];
  if (proj.budget25) {
    budgetRows.push(new TableRow({
      children: [
        cell('25년\n예산액', { shade: 'D9E2F3', width: 1800 }),
        cell(proj.budget25 + '원', { width: 3000 }),
        cell('집행액', { shade: 'D9E2F3', width: 1800 }),
        cell(detail.budget25Exec + '원', { width: 2300 }),
        cell('집행율', { shade: 'D9E2F3', width: 1200 }),
        cell(detail.exec25Rate + '%', { width: 1300 }),
      ],
    }));
  }
  if (proj.budget26) {
    budgetRows.push(new TableRow({
      children: [
        cell('26년\n예산액', { shade: 'D9E2F3', width: 1800 }),
        cell(proj.budget26 + '원', { width: 3000 }),
        cell('집행액', { shade: 'D9E2F3', width: 1800 }),
        cell(detail.budget26Exec + '원', { width: 2300 }),
        cell('집행율', { shade: 'D9E2F3', width: 1200 }),
        cell(detail.exec26Rate + '%', { width: 1300 }),
      ],
    }));
  }
  if (!proj.budget25 && !proj.budget26) {
    budgetRows.push(new TableRow({
      children: [
        cell('예산액', { shade: 'D9E2F3', width: 1800 }),
        cell('0원', { width: 3000 }),
        cell('집행액', { shade: 'D9E2F3', width: 1800 }),
        cell('0원', { width: 2300 }),
        cell('집행율', { shade: 'D9E2F3', width: 1200 }),
        cell('0%', { width: 1300 }),
      ],
    }));
  }

  // 정량 목표/실적
  const targetText = Array.isArray(proj.quantTarget) ? proj.quantTarget.join('\n') : proj.quantTarget;
  const resultText = (detail.quantResult || []).join('\n');
  const qualitText = detail.qualitResult || '';

  const detailBudgetCols = [1800, 3000, 1800, 2300, 1200, 1300];
  const mainCols = [1800, 4800, 4800];

  return [
    para([txt(`사업명  ${proj.no}. ${proj.name}`, { bold: true, size: 22 })], { spaceBefore: 60 }),
    new Table({
      width: { size: totalW, type: WidthType.DXA },
      columnWidths: detailBudgetCols,
      rows: budgetRows,
    }),
    para(''),
    new Table({
      width: { size: totalW, type: WidthType.DXA },
      columnWidths: [1800, 9600],
      rows: [
        new TableRow({
          children: [
            cell('사업목적', { shade: 'D9E2F3', width: 1800 }),
            cell(proj.purpose.join('\n'), { width: 9600 }),
          ],
        }),
        new TableRow({
          children: [
            cell('', { shade: 'D9E2F3', width: 1800 }),
            cell('목표', { shade: 'EEF2FA', width: 4800 }),
            cell('추진실적', { shade: 'EEF2FA', width: 4800 }),
          ],
        }),
        new TableRow({
          children: [
            cell('정량적 성과', { shade: 'D9E2F3', width: 1800 }),
            cell(targetText, { width: 4800 }),
            cell(resultText, { width: 4800 }),
          ],
        }),
        new TableRow({
          children: [
            cell('세부\n추진내용', { shade: 'D9E2F3', width: 1800 }),
            cell((detail.detailContents || []).join('\n'), { width: 9600, span: 2 }),
          ],
        }),
        new TableRow({
          children: [
            cell('정성적 성과', { shade: 'D9E2F3', width: 1800 }),
            cell(qualitText, { width: 9600, span: 2 }),
          ],
        }),
        new TableRow({
          children: [
            cell('관련 사진\n및 증빙', { shade: 'D9E2F3', width: 1800 }),
            cell('\n\n\n' + (detail.photoCaption || '') + '\n\n', { width: 9600, span: 2 }),
          ],
        }),
      ],
    }),
    sectionBreak(),
  ];
}

/** 8~9페이지: 개인별 업무 실적 및 계획 */
function buildPersonnelPage(data) {
  const { reportMonth, nextMonth } = data;
  const COL = [1500, 5000, 4900];
  const totalW = COL.reduce((a, b) => a + b, 0);

  const rows = [
    new TableRow({
      children: [
        headerCell('인력별\n구분', COL[0]),
        headerCell(`이번달(${reportMonth}월) 추진 실적`, COL[1]),
        headerCell(`다음달(${nextMonth}월) 추진 계획`, COL[2]),
      ],
    }),
    ...data.personnel.map(p => new TableRow({
      children: [
        cell(p.name, { shade: 'EEF2FA', width: COL[0] }),
        cell(p.thisMonth.join('\n\n'), { width: COL[1] }),
        cell(p.nextMonth.join('\n'), { width: COL[2] }),
      ],
    })),
  ];

  return [
    para([txt('개인별 업무 실적 및 계획', { bold: true, size: 22 })], { spaceBefore: 60, spaceAfter: 120 }),
    new Table({ width: { size: totalW, type: WidthType.DXA }, columnWidths: COL, rows }),
    sectionBreak(),
  ];
}

/** 10페이지: 집행 내역 */
function buildExecPage(data) {
  const { reportMonth } = data;
  const e = data.execSummary;
  const COL = [2400, 1800, 1800, 1800, 1800, 1800];
  const totalW = COL.reduce((a, b) => a + b, 0);

  function execRow(label, budgetTotal, granted, exec, remain, rate) {
    return new TableRow({
      children: [
        cell(label, { width: COL[0] }),
        cell(budgetTotal, { width: COL[1], align: AlignmentType.RIGHT }),
        cell(granted, { width: COL[2], align: AlignmentType.RIGHT }),
        cell(exec, { width: COL[3], align: AlignmentType.RIGHT }),
        cell(remain, { width: COL[4], align: AlignmentType.RIGHT }),
        cell(rate, { width: COL[5], align: AlignmentType.RIGHT }),
      ],
    });
  }

  const year25Header = `25년\n예산액`;
  const year26Header = `26년\n예산액`;

  return [
    para([txt('망남생활권 앵커조직 운영비 총괄 집행 내역(누계)', { bold: true, size: 22 })], { spaceBefore: 60, spaceAfter: 80 }),
    para([txt('(단위: 원)', { size: 18 })], { align: AlignmentType.RIGHT }),
    new Table({
      width: { size: totalW, type: WidthType.DXA },
      columnWidths: COL,
      rows: [
        new TableRow({
          children: [
            headerCell('총 괄', COL[0]),
            headerCell(year25Header, COL[1]),
            headerCell(`26년 ${reportMonth}월\n기준 교부액`, COL[2]),
            headerCell(`${reportMonth}월 기준\n집행액`, COL[3]),
            headerCell(`${reportMonth}월 기준\n예산잔액`, COL[4]),
            headerCell(`집행률(%)`, COL[5]),
          ],
        }),
        execRow('망남생활권 앵커조직\n운영비', e.budget25Total, e.budget25Granted, e.budget25Exec, e.budget25Remain, e.budget25Rate),
      ],
    }),
    para(''),
    new Table({
      width: { size: totalW, type: WidthType.DXA },
      columnWidths: COL,
      rows: [
        new TableRow({
          children: [
            headerCell('총 괄', COL[0]),
            headerCell(year26Header, COL[1]),
            headerCell(`26년 ${reportMonth}월\n기준 교부액`, COL[2]),
            headerCell(`${reportMonth}월 기준\n집행액`, COL[3]),
            headerCell(`${reportMonth}월 기준\n예산잔액`, COL[4]),
            headerCell(`집행률(%)`, COL[5]),
          ],
        }),
        execRow('망남생활권 앵커조직\n운영비', e.budget26Total, e.budget26Granted, e.budget26Exec, e.budget26Remain, e.budget26Rate),
      ],
    }),
    sectionBreak(),
  ];
}

/** 11페이지: 제작물 및 성과물 */
function buildProductPage(data) {
  return [
    para([txt('제작물 및 성과물', { bold: true, size: 22 })], { spaceBefore: 60, spaceAfter: 120 }),
    ...data.products.flatMap(p => [
      para([txt('· ' + p.label, { bold: true })]),
      para('\n\n\n' + p.caption + '\n\n\n'),
    ]),
    para([txt('. 끝.')], { spaceBefore: 400 }),
  ];
}

// ──────────────────────────────────────────
// 5. 문서 조립 및 출력
// ──────────────────────────────────────────
async function generate(data) {
  const children = [
    ...buildPage1(data),
    ...buildPage2(data),
    ...FIXED.projects.flatMap((_, i) => buildProjectPage(i, data)),
    ...buildPersonnelPage(data),
    ...buildExecPage(data),
    ...buildProductPage(data),
  ];

  const doc = new Document({
    styles: {
      default: {
        document: { run: { font: FONT, size: 20 } },
      },
    },
    sections: [{
      properties: {
        page: {
          size: { width: 11906, height: 16838 }, // A4
          margin: { top: 1134, right: 1134, bottom: 1134, left: 1134 }, // 2cm
        },
      },
      children,
    }],
  });

  const { reportMonth, year } = data;
  const filename = `실적및계획보고_망남앵커조직_${year}년_${reportMonth}월_보고.docx`;
  const outPath = path.join(process.cwd(), filename);
  const buffer = await Packer.toBuffer(doc);
  fs.writeFileSync(outPath, buffer);
  console.log(`✅ 생성 완료: ${filename}`);
  return outPath;
}

// ──────────────────────────────────────────
// 6. CLI 진입점
// ──────────────────────────────────────────
const args = process.argv.slice(2);
const reportMonth = parseInt(args[0]);
if (!reportMonth || reportMonth < 1 || reportMonth > 12) {
  console.error('사용법: node siljeok.js <보고월번호>  예) node siljeok.js 6');
  process.exit(1);
}

let data;
if (args[1] && fs.existsSync(args[1])) {
  data = require(path.resolve(args[1]));
  console.log(`📂 데이터 파일 로드: ${args[1]}`);
} else {
  data = getDefaultData(reportMonth);
  console.log(`📋 기본 템플릿으로 생성 (데이터파일 미지정)`);
}

generate(data).catch(err => {
  console.error('❌ 오류:', err.message);
  process.exit(1);
});
