# 핸드오버: M6 고도화 최종 완료

## 작성일
2026-06-25

## 세션 요약
M5 사이트 배포 + M6 공문 자동화 + 웹페이지 URL 배포까지 완료

---

## 전체 완료 현황

| 단계 | 내용 | 상태 |
|------|------|------|
| M1 | 환경설정 + Claude Code | ✅ |
| M2 | Git + GitHub 레포 | ✅ |
| M3 | Quartz + Cloudflare Pages | ✅ |
| M4 | Supabase DB | ✅ (curl 테스트 보류) |
| M5 | 한 페이지 사이트 | ✅ |
| M6 | 공문 Word 자동생성 | ✅ |
| M6 고도화 | 월 자동화 + 문서번호 | ✅ |
| M6 웹페이지 | 브라우저 공문 생성 URL | ✅ |

---

## 라이브 URL 목록

| 서비스 | URL |
|------|------|
| 내 사이트 | https://sakyowon-ai-c3k.pages.dev |
| 공문 자동생성 | https://sakyowon-ai-c3k.pages.dev/gongmun.html |
| 위키 | https://wiki.sakyowon.co.kr (DNS 전파 중) |
| GitHub | https://github.com/deka2026/sakyowon-ai |

---

## 공문 자동생성 사용법

### 웹 (추천)
```
https://sakyowon-ai-c3k.pages.dev/gongmun.html
```
→ 월 선택 → 공문 다운로드

### 로컬 (Node.js)
```powershell
cd C:\Users\pc\sakyowon-ai
node gongmun.js 7    # 7월 실적 / 8월 계획
```

---

## 공문 고정값

| 항목 | 값 |
|------|-----|
| 수신 | 완도군수(지역개발과장) |
| 담당 | 공동체팀장 김지희 / 대표 김일영 |
| 시행일 | 다음달 3일 고정 |
| 문서번호 | 사교원-YYYYMMDD-1 |
| 주소 | 완도군 완도읍 군내길 209-1, 2층 |
| 전화 | 061-555-0631 |
| 이메일 | mangnam.anchor@gmail.com |

---

## 레슨런

| 항목 | 내용 |
|------|------|
| hwpx | 이미지 삽입 시 손상 반복 → Word(.docx) 권장 |
| 브라우저 docx | `Packer.toBuffer` ❌ → `Packer.toBlob` ✅ |
| 브라우저 이미지 | 파일 경로 ❌ → base64 인라인 내장 ✅ |
| CDN 불안정 | iife 빌드 인라인 삽입으로 해결 |
| PowerShell | `>>` 멀티라인 ❌ → 한 줄씩 실행 ✅ |
| git push | PAT 토큰 터미널에만, 채팅창 절대 금지 |

---

## 스킬 메모

- hwpx 스킬: `C:\Users\pc\sakyowon-ai\skills\hwpx\`
- docx 생성: Node.js `docx` 라이브러리 (npm)
- 브라우저 docx: iife 빌드 인라인 + `Packer.toBlob`
- 로고: base64 내장으로 외부 파일 의존성 제거

---

## 다음 세션

| 항목 | 내용 |
|------|------|
| M6-2 | 실적자료 2페이지 표 Word 자동생성 |
| Supabase | curl GET 테스트 (네트워크 허용 후) |
| logo.png | sakyowon-ai 폴더 저장 (node 스크립트용) |

---

## 규칙
- "정리해" → 핸드오버 작성 + 스킬 + 레슨 + 위키 배포 자동수행
