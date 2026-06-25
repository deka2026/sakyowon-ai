# 핸드오버: M6-2 실적자료 자동생성

작성일: 2026-06-25
세션: M6-2 실적자료 자동생성

---

## 완료 상태

| 항목 | 내용 | 상태 |
|------|------|------|
| 실적자료 분석 | 4월·5월 PDF 비교 → 고정/변동 항목 분리 | ✅ |
| Node.js 스크립트 | `siljeok.js` — CLI로 월별 docx 생성 | ✅ |
| 데이터 파일 | `data_june_2026.js` — 6월 데이터 템플릿 | ✅ |
| 웹 자동생성 페이지 | `siljeok.html` — 브라우저에서 입력 → Word 다운로드 | ✅ |
| GitHub push | `deka2026/sakyowon-ai` master 브랜치 | ✅ |
| Cloudflare 배포 | https://sakyowon-ai-c3k.pages.dev/siljeok.html | ✅ |

---

## 파일 구조

```
sakyowon-ai/
├── siljeok.js           # Node.js CLI 스크립트
├── siljeok.html         # 브라우저 웹 자동생성 페이지 (서버 불필요)
├── data_june_2026.js    # 6월 데이터 파일 (매월 복사해서 사용)
└── gongmun.html         # 공문 자동생성 (M6-1, 기존)
```

---

## 사용법

### 웹 페이지 (권장)
1. https://sakyowon-ai-c3k.pages.dev/siljeok.html 접속
2. 좌측 메뉴 순서대로 입력 (보고월→업무요약→사업별→개인별→집행내역)
3. "Word 파일 다운로드" 버튼 클릭 → `.docx` 자동 저장

### CLI (로컬 PC)
```powershell
cd C:\Users\pc\sakyowon-ai

# 빈 템플릿으로 생성
node siljeok.js 7

# 데이터 파일로 생성
node siljeok.js 7 data_july_2026.js
```

### 매월 작업 순서
1. `data_june_2026.js` 복사 → `data_july_2026.js`
2. `reportMonth`, `nextMonth` 숫자 변경
3. 변동 항목만 수정 (실적·집행액·개인별 업무)
4. `node siljeok.js 7 data_july_2026.js` 실행

---

## 고정값 vs 변동값

### 고정 (siljeok.js 내 FIXED 객체 — 매월 그대로)
- 지자체/담당과, 담당자 연락처
- 대상지역, 사업비, 사업기간, 사업비 구성
- 사업 내용 (4가지 목표)
- 앵커명, 계약일, 담당자, 주소
- 앵커 활동 주요경력 (12개)
- 5개 사업의 사업명·예산액·사업목적
- 인력 구성 (김일영, 조영윤, 김지희)

### 변동 (매월 data_MONTH_YEAR.js에서 수정)
- 보고월 / 계획월
- 업무별 요약표 (4개 카테고리 × 이번달/다음달)
- 사업별 정량·정성 실적, 세부 추진내용, 사진 캡션
- 집행액·집행율 (누계 갱신)
- 개인별 업무 실적 및 계획
- 사업총평

---

## 기술 스택

| 항목 | 내용 |
|------|------|
| 문서 생성 | docx 9.6.1 (Node.js / 브라우저 UMD) |
| 파일 저장 | FileSaver.js (브라우저) |
| 산출물 형식 | A4, 여백 2cm, 맑은고딕 10pt, 11페이지 |
| 배포 | Cloudflare Pages (GitHub 연동 자동배포) |
| 레포 | https://github.com/deka2026/sakyowon-ai |

---

## 레슨런

- PDF → pdftotext -layout 으로 한글 텍스트 추출 잘 됨 (폰트 임베드 확인 필수)
- docx UMD 번들(839KB)은 HTML에 인라인 삽입 가능 — CDN 없이 오프라인 동작
- webpack으로 docx 번들링 시 `require(...)` 동적 import 에러 → UMD 파일 직접 사용으로 우회
- Cloudflare Pages는 GitHub push 시 자동 배포 — `siljeok.html` push 즉시 공개 URL 생성
- `Get-ChildItem -Recurse` 로 못 찾아도 브라우저 주소창에 경로가 보이면 그게 정답
- 줄바꿈 LF→CRLF 경고는 Windows git 기본 동작, 무시해도 됨

---

## 다음 단계 후보

- [ ] 제작물 페이지(11p)에 이미지 직접 업로드 기능 추가
- [ ] 월별 데이터 자동 저장 (localStorage)
- [ ] 공문(gongmun.html) + 실적자료(siljeok.html) 통합 페이지
- [ ] Supabase 연동 — 월별 실적 데이터 DB 저장 (M4 연결)
