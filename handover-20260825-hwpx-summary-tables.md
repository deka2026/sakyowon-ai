# 핸드오버: 두 사업계획서 hwpx를 표 중심 6쪽 요약 hwpx로 통합 생성

**날짜**: 2026-08-25
**이전 핸드오버**: handover-20260824-mangnam-blue-class-copyedit.md
**작업 폴더**: D:\사교원 개발그룹\전남광주사업게획서 모음

---

## 수행한 작업

### 1. 두 사업계획서 요약 통합 hwpx 생성 (v1: 문단만 → 9쪽)
- 원본: `시민기금_시민재단_사업계획(토론용)_20260720.hwpx`(322런), `시민기업펀드_시민기업육성재단_토론용_20260724.hwpx`(236런)
- hwpx_dump.ps1로 양쪽 텍스트 추출 → 각 3쪽 목표로 요약 94문단 작성
- 원본 doc1을 템플릿으로: section0.xml에서 **첫 문단(secPr·머리말 포함)만 남기고 전부 제거 → 새 문단 append → linesegarray 제거 → repack_multi**
- 서식 ID 재사용: 제목 paraPr17/charPr1, 절 제목 paraPr19/style15/charPr2, 본문 paraPr22/charPr15, 들여쓰기 paraPr15/charPr15
- 결과: 9쪽 — 사용자 "표로 정리해서 6쪽으로" 피드백

### 2. v2: 표 중심 재구성 (표 10개, 6쪽 목표)
- 원본 표 XML 분석: 표 전체폭 47622 HWPUNIT, 헤더 셀 borderFill 9/paraPr 20/charPr 21, 본문 셀 borderFill 3/paraPr 24/charPr 28, treatAsChar 인라인
- **spec 파일(마크업: H1/H1PB/H2/P/TBL/R/END) → build_fragment.ps1이 문단+hp:tbl XML 생성** 방식 신규 확립
- 표 10개: 부별로 사업개요·3층 구조·규모 시나리오·유형별 운영·재원 각 5개씩
- 본문 절반 압축, 각 부 7개 절로 통합. 제2부 첫 문단 pageBreak="1"
- 산출: `시민기금_시민기업펀드_핵심요약_20260825.hwpx` (원본 2건 무변경)
- 검증: 재덤프 204런, 표 문자열·부 구분 확인, XML 유효

### 3. 스킬 갱신
- `hwpx-powershell-edit`에 신규 문서 조립 경로(C) 추가: `scripts/build_fragment.ps1` + SKILL.md 절 추가

### 4. 위키배포 결과 (정리해 루틴)
- (이월) PR #15 머지 완료 — squash bfdfe66 (홈페이지 문구 레슨)
- 신규 레슨 PR #17 생성·머지 완료 — squash f1030b7 (`문서/실천기술/AI와-함께-두-사업계획서를-하나의-한글-요약본으로-합치기.md`)
- 편지함 라이브 반영 요청 push — haeory-sakyowon-site 563e4c5 (#15·#17 동시 요청)
- 라이브 확인: 두 URL 모두 404 — **본부(지미) 배포 대기**

## 미완료 / 다음 할 일
- [ ] 요약본을 한글에서 열어 실제 쪽수 확인 (6쪽 목표 — 넘치면 문단 축약, 모자라면 보강)
- [ ] 위키 라이브 확인 대기 — PR #15·#17 머지 완료, wiki.poomasi.org 반영 여부만 확인하면 됨

## 파일 위치
| 경로 | 내용 |
|---|---|
| D:\사교원 개발그룹\전남광주사업게획서 모음\시민기금_시민기업펀드_핵심요약_20260825.hwpx | 산출물(표 10개, 2부 구성) |
| sakyowon-ai\skills\hwpx-powershell-edit\scripts\build_fragment.ps1 | spec→문단·표 XML 생성기 |
| (스크래치) spec.txt, fragment2.xml, section0_new2.xml | 세션 스크래치 — 재현은 스킬 참조 |

## 약속
- 사용자가 **"이어서 작업하자"** 라고 하면 이 핸드오버의 "미완료" 목록부터 재개
- 사용자가 **"정리해"** 라고 하면: ①핸드오버 ②스킬 ③레슨 ④위키배포 자동 수행
