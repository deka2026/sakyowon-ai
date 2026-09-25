# 핸드오버: 망남마을협동조합 운영 백엔드 (회계·회의록·문서·경영공시/실적)

**날짜**: 2026-09-25
**이전 핸드오버**: handover-20260925-mangnam-plogging-3dprint-plan.md
**작업 폴더**: `C:\Users\User\mangnam-coop` (deka2026/mangnam-coop, main)

---

## 수행한 작업

### 1. 서버 모듈 `server/mangnam_api.py` (FastAPI 확장, `/api/mangnam/*`)
- 사교원 자체 서버(가비아, `/opt/sakyowon/server/app.py`)에 **붙여 쓰는 확장 모듈**. `install(app, db=…, admin_ok=…, current_user=…, now_iso=…, new_id=…, s=…, db_path=…)` 한 번 호출로 라우터·테이블(`mn_*` 6개)이 붙는다. 새 서비스·DB·비밀번호 없음 — 관리자 인증은 기존 `SAKYOWON_ADMIN_KEY` 또는 통합계정 admin·staff 세션.
- 기능: 월별 회계(전표·월 마감/해제·월별/항목별/사업별 집계·CSV) / 회의록(안건·내용·결정·후속·첨부·공개 플래그) / 문서 보관(파일 또는 외부 링크, 분류·태그·검색) / 공시·실적 게시(초안/게시, 지표, 첨부) / 공개 조회 4종(`public/posts`, `public/posts/{id}`, `public/finance`, `public/meetings`).
- 공개 범위 규칙: 전표 개별 내용은 절대 비공개, **공개로 표시한 달의 수입·지출 합계만** 나감. 회의록은 공개 시 일자·종류·제목·안건·결정·첨부만(논의 경과·참석자·후속조치 제외). 첨부는 게시된 글이 참조할 때만 `scope=public`, 게시를 내리면 자동 회수.
- 파일 업로드는 `python-multipart` 의존성을 피해 **JSON base64**(20MB). 단독 실행 모드(`standalone_app`)로 로컬 개발 가능.
- 회귀 테스트 `server/smoke_test.py` 전 엔드포인트 통과(마감 409, 비공개 파일 401, 게시 해제 후 회수 등).

### 2. 서버 반영 스크립트 `server/install-on-server.sh`
- root SSH 한 줄: `curl -fsSL https://raw.githubusercontent.com/deka2026/mangnam-coop/main/server/install-on-server.sh | sudo bash` → 모듈 내려받기 → `app.py` 끝에 include 블록(없을 때만) → `sakyowon-api` 재시작 → `/api/mangnam/health` 확인. 재실행하면 모듈만 갱신. raw URL 200 확인.
- 설계·운영 문서 `server/README.md`.

### 3. 프론트(Next 14 정적)
- 운영진: `/admin/`(현황) `/admin/ledger/` `/admin/meetings/` `/admin/documents/` `/admin/posts/`. 공통 틀 `app/admin/AdminShell.tsx`(세션 자동 인식 → 없으면 비밀번호, sessionStorage). 푸터 "🗂 조합 운영관리" 링크.
- 공개: `/disclosure/`(경영공시 — 분류별 목록·`?id=` 상세·공개 회의 결과) `/performance/`(사업 실적 — 지표 카드·공개 달 수입·지출 막대). 사이드바 "조합 운영" 메뉴. 서버 모듈이 없을 때(404) 오류 대신 "자료 없음"으로 표시.
- API 클라이언트 `app/lib/api.ts` (`NEXT_PUBLIC_API_BASE` 기본 `/api`; 로컬은 `.env.development.local`로만 재정의 — `next build`가 안 읽음).
- 브라우저 실검증: 로그인→회계·회의록·문서 화면→게시 폼 입력·게시→공개 페이지 노출까지.

### 4. 커밋·배포
- main `00080c9` push, gh-pages 배포 push 완료. **실사이트는 미반영** (`/api/mangnam/health` 404, `/mangnam-coop/disclosure/` 404) — 서버 두 명령 대기.
- 스킬 `mangnam-coop-deploy`에 "조합 운영 백엔드" 절 추가, 신규 스킬 `sakyowon-server-extension-module`.

## 미완료 / 다음 할 일
- [ ] **이사장님 SSH** ① `curl -fsSL https://raw.githubusercontent.com/deka2026/mangnam-coop/main/server/install-on-server.sh | sudo bash` ② `sudo bash /opt/sakyowon/src/deploy-www.sh` → `curl -s https://sakyowon.co.kr/api/mangnam/health` JSON 확인
- [ ] 반영 후 실서버에서 관리 화면 로그인(통합계정) 1회 실증, 첫 공시 자료(정관·2025 결산) 실제 게시
- [ ] `/opt/sakyowon/data/files/mangnam/` 첨부 폴더를 DB 백업 루틴에 포함(기존 백업 미완 항목과 함께)
- [ ] 위키 레슨 서버 반영(4단계) — 아래 위키배포 결과 참조
- [ ] (이월) 정관 빈칸 10곳 확정 → 마을민박 운영방식 → 산업분류 세세분류 (설립 서류)

## 파일 위치
| 경로 | 내용 |
|---|---|
| `C:\Users\User\mangnam-coop\server\mangnam_api.py` | 서버 확장 모듈(캐노니컬, 서버는 raw URL로 내려받음) |
| `…\server\install-on-server.sh` / `README.md` / `smoke_test.py` | 반영 스크립트 / 설계 문서 / 회귀 테스트 |
| `…\app\admin\` · `app\lib\api.ts` · `app\disclosure\` · `app\performance\` · `app\components\PostView.tsx` | 관리 화면 · 클라이언트 · 공개 페이지 |
| `C:\Users\User\.claude\skills\sakyowon-server-extension-module\` | 신규 스킬(= sakyowon-ai/skills) |
| `C:\Users\User\mn-dev\` | 로컬 개발 DB 짧은 경로(비어 있음, 재사용) |

## 레슨(함정)
- `next dev` 프리뷰가 켜진 채 `npm run build` → `.next` 덮여 dev 500(`Cannot find module './52.js'`). 빌드 전 프리뷰 중지, 빌드 후 `.next` 삭제.
- 스크래치 폴더 경로(240자)에 SQLite·첨부를 두면 `WinError 206`. 짧은 경로로.
- Next 페이지 파일(`page.tsx`)은 default 외 export 금지 — 공용 컴포넌트는 `app/components/`로.
- 브라우저 자동화의 `key Return`은 폼 submit을 안 일으킬 수 있음 — 버튼 클릭으로 검증.

## 약속
- 사용자가 **"이어서 작업하자"** 라고 하면 이 핸드오버의 "미완료" 목록부터 재개
- 사용자가 **"정리해"** 라고 하면: ①핸드오버 ②스킬 ③레슨 ④위키배포 자동 수행
