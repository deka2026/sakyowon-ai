# 핸드오버: 햇소자 회원등급 4단계(관리자·연합회·회원협동조합·손님) 도입 + 등급별 데모 계정

**날짜**: 2026-09-25
**이전 핸드오버**: handover-20260925-mangnam-plogging-3dprint-plan.md (같은 날 병행 세션) / 햇소자 계열 직전은 handover-20260918-hpc-nipa-hatsoja-integration.md
**작업 폴더**: `C:\Users\User\AppData\Local\Temp\hub-clone` (deka2026.github.io 클론) → 사본 `D:\사교원 개발그룹\사교원 개발그룹\햇빛발전협동조합 업무자동화 사이트\햇소자_사이트_회원등급개편_20260925\`

---

## 수행한 작업

### 1. 현황 진단 — "회원등급"은 없었다

사용자 질문 "회원등급이 어떻게 되어 있지?"에 코드로 답했다. 등급 체계는 없고 세 축이 섞여 있었다.

| 축 | 값 | 비고 |
|---|---|---|
| 계정 권한 role | `admin` / `member` 2단계 | 서버 `staff`는 프런트에서 admin으로 뭉개짐 |
| 계정 상태 status | 서버 pending/approved/rejected · 목업 승인/승인대기/정지 | 승인제 |
| 조합원 직위 | 이사장/이사/감사/조합원 + 출자금·의결권 | 명부 데이터일 뿐, 권한과 무관 |

### 2. 등급 4단계 도입 (`hatsoja/index.html` +340/−123, 커밋 03e7ccb → PR #1 → main 66acb7a)

- **`ROLES` / `ROLE_MENUS` 한 곳에서 등급별 메뉴와 접근권한을 정의** — 상단 메뉴바(`#roleNav`)·사이드바(`renderRoleSidebar`)·라우터 접근검사(`canAccess`)가 모두 이 표를 본다. 메뉴를 옮기려면 이 표만 고치면 된다.
- 등급: `admin` 관리자 · `federation` 연합회 · `coop` 회원협동조합 · `guest` 손님(미로그인 또는 승인 전)
- 등급별 메뉴 배치:
  - 관리자: 플랫폼 관리(통계·공모심사·조합마을·회원) / 소통·콘텐츠(문의·콘텐츠·로그) / 연합회 업무(현황판·자료실·AI상담) + 등급별 화면 미리보기(회원협동조합·연합회·손님)
  - 연합회: 연합회(현황판=`mem/union`·조합마을 현황=`adm/villages`·공모심사=`adm/contest`) / 공동업무(문서생성·서류검토·법령·수익시뮬·일정) / 소통(자료실·AI상담·마이페이지)
  - 회원협동조합: 종전 회원 16메뉴 그대로 (내 조합 / 설립·건설 / 운영관리 / 확장)
  - 손님: 공개 메뉴만. 회원 메뉴로 가면 홈으로 돌려보내고 "승인 후 이용" 토스트
- 로그인 후 상단에 등급 메뉴 드롭다운, 모바일(≤900px)은 ☰로 세로 펼침. 사용자 칩에 등급 태그.
- **등급별 데모 계정 4개**(`DEMO_ACCOUNTS`): 로그인 창의 등급 버튼 + 로그인 후 노란 체험 띠의 "등급 바꿔 보기" 버튼으로 로그아웃 없이 즉시 전환 → 사이트 기능을 등급별로 전수 점검 가능
- 통합계정 role 정규화 `normalizeRole(role, status)`: admin/staff→관리자, federation/union→연합회, 그 외→회원협동조합, status pending/rejected→손님. 구 localStorage 값 `member`는 읽을 때 coop으로 호환.
- 회원 관리의 등급 선택 4종, 마이페이지·회원 목록 등급 표기 통일(`roleLabel`).

### 3. 검증·배포·실사이트 확인

- 인라인 스크립트 문법 검사(node `new Function`) 통과. 로컬 정적 서버(python http.server)에서 4등급 데모 로그인·차단 리다이렉트·드롭다운·모바일 ☰·미리보기 시작/복귀 확인.
- PR #1 머지(`--merge --delete-branch`) → Pages 빌드 run 36092166331 success(12:53 KST).
- 실사이트 반영은 12:56에 확인(4등급 데모 실동작). **정정(13:35)**: 이것은 "Pages 전파 3분 지연"이 아니었다. sakyowon.co.kr은 GitHub Pages가 아니라 **자체서버(Caddy, 1.201.116.225)** 가 `deploy-www.sh`로 deka2026.github.io main을 clone해 서빙하며, 12:56은 사용자가 다른 건으로 서버 스크립트를 돌린 시각이었다. PR #2는 머지 후 10분 폴링해도 안 바뀌어 규명. 스킬·메모리·레슨의 해당 문구를 모두 고쳤다.

### 4. 저장

- `햇빛발전협동조합 업무자동화 사이트\햇소자_사이트_회원등급개편_20260925\` — `hatsoja/`(수정본 사본, 파일로 열면 데모 모드로 동작) + `작업메모_회원등급개편_20260925.md`

## 미완료 / 다음 할 일

- [ ] **서버(통합계정)에 `federation` role 값 신설 요청** — 현재 `/api/auth/me`가 주는 role에 연합회가 없어 실계정 연합회 등급은 동작 불가(데모·미리보기는 됨). 본부(지미)에 편지: 계정 role 값에 `federation` 추가 + 관리자 회원관리에서 지정 가능하게. (이월) 9/6 편지의 백엔드 4건과 함께
- [x] **해소(13:20)**: 연합회는 조합·마을 화면 열람 전용 — PR #2 → main **7c487ce**. **라이브 반영은 서버 스크립트 대기**(사용자 `bash /opt/sakyowon/src/deploy-www.sh`) — 실행 후 `requireAdmin` 문자열로 확인. `isAdminUser()`/`requireAdmin()` 헬퍼, 등록·삭제·편집·담당자 배정 숨김 + 함수 가드. 공모·심사(`adm/contest`) 버튼은 데모 토스트뿐이라 그대로
- [ ] `hatsoja/manual.html`(이용안내)에 등급 4단계 설명 절 추가 — 이번엔 손대지 않음
- [ ] (이월) HPC 연동 후속 — handover-20260918 미완료 목록 참조

## 파일 위치

| 경로 | 내용 |
|---|---|
| GitHub `deka2026/deka2026.github.io` main `66acb7a` → `hatsoja/index.html` | 캐노니컬(라이브 https://sakyowon.co.kr/hatsoja/) |
| PR https://github.com/deka2026/deka2026.github.io/pull/1 | 변경 설명·등급별 메뉴 표·확인 항목 |
| `C:\Users\User\AppData\Local\Temp\hub-clone` | 로컬 클론(main = origin/main). Temp라 지워질 수 있음 — 없으면 다시 clone |
| `D:\사교원 개발그룹\사교원 개발그룹\햇빛발전협동조합 업무자동화 사이트\햇소자_사이트_회원등급개편_20260925\` | 수정본 사본 + 작업메모 |
| `sakyowon-ai/skills/hatsoja-site-deploy/` | 스킬(이번 세션 신설): 수정→PR→머지→Pages→라이브 확인 절차 + 등급 표 고치는 법 |

## 정리 루틴 결과 (2026-09-25 13:40)

| 단계 | 결과 |
|---|---|
| ① 핸드오버 | 이 파일, sakyowon-ai master 1a650cc |
| ② 스킬 | `skills/hatsoja-site-deploy/SKILL.md` 신설 + `~/.claude/skills/`에 활성화 (스크립트 없음, 코드 지도·점검 JS·배포 절차) |
| ③ 레슨 | 사교원 위키 `content/에너지-전환/AI와-함께-사이트-회원등급을-설계하고-등급별-데모계정으로-점검하기.md` |
| ④ 위키배포 | v4 **819b77c** → CI 36092761197 success(build 잡 직후 아티팩트 API로 수령) → site master **c183bfb**(sitemap `<loc>` 120) = 3단계 → **2026-09-25 13:15 KST 사용자가 서버 반영 = 4단계 완료**. 라이브 실측 `Last-Modified` 04:15:40 GMT, sitemap `<loc>` **122**(다른 세션 레슨 동반), 신규 문서 **200**(제목·본문 확인). **위키 배포 대기 0건** |

## 약속
- 사용자가 **"이어서 작업하자"** 라고 하면 이 핸드오버의 "미완료" 목록부터 재개
- 사용자가 **"정리해"** 라고 하면: ①핸드오버 ②스킬 ③레슨 ④위키배포 자동 수행
