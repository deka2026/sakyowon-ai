---
name: sakyowon-server-extension-module
description: 사교원 자체 서버(가비아 FastAPI+SQLite, app.py 단일 파일)에 새 사이트 기능(회계·게시판·문서보관 등)을 "확장 모듈"로 붙이는 스킬. "망남/햇소자 사이트에 백엔드 기능 넣어줘", "관리자만 쓰는 저장 기능 만들어줘", "서버에 API 추가해줘" 같은 요청에 사용. 새 서비스·DB·비밀번호를 늘리지 않고 app.py의 DB·인증을 빌려 쓰며, 서버 반영은 이사장 SSH 한 줄 스크립트로 넘긴다. 첫 사례: mangnam-coop/server/mangnam_api.py (2026-09-25).
---

# 사교원 자체 서버 확장 모듈 만들기

## 언제 쓰나
사교원 관계 사이트(정적 Next/HTML)에 **저장이 필요한 기능**(장부, 회의록, 게시판, 문서보관, 예약 등)을 넣을 때. 서버는 하나(가비아 `sakyowon-api`, `/opt/sakyowon/server/app.py`, 포트 8787, Caddy가 `/api/*` 프록시)이고 root SSH는 이사장님만 갖고 있다.

## 원칙 세 가지
1. **app.py를 고치지 말고 모듈로 붙인다.** app.py는 캐노니컬이 두 레포(haeory-cyber/sakyowon-site `server/`, deka2026/sakyowon-server)에 있어 손대면 동기화 부담이 생긴다. 모듈은 **사이트 레포 `server/`** 에 두고 서버는 raw URL로 내려받는다.
2. **DB·인증·유틸은 빌려 쓴다.** 모듈은 `install(app, *, db, admin_ok, current_user, now_iso, new_id, s, db_path)` 하나만 내보낸다. 새 DB 파일·새 비밀번호·새 systemd 유닛을 만들지 않는다.
3. **새 pip 의존성을 만들지 않는다.** 파일 업로드도 multipart 대신 JSON base64(`python-multipart` 불필요). requirements.txt는 fastapi·uvicorn뿐이다.

## 뼈대 (mangnam_api.py 를 복사해 시작)

```python
PREFIX = "/api/<site>"

def init_tables(db):            # CREATE TABLE IF NOT EXISTS <site>_* …
def install(app, *, db, admin_ok, current_user, now_iso, new_id, s, db_path="", notify=None):
    init_tables(db)
    r = APIRouter(prefix=PREFIX)
    def who(request, body=None):    # 관리자 키(?key= / X-Admin-Key / body.key) 또는 admin·staff 세션
        if not admin_ok(request, key_of(request, body)): return None, _err("관리자 권한이 필요합니다.", 401)
        u = current_user(request); return (u and (u["name"] or u["username"])) or "관리자", None
    @r.get("/health") ...
    @r.get("/public/...")           # 인증 없음 — 내보낼 필드를 명시적으로 고른다
    app.include_router(r)

def standalone_app():               # 로컬 개발용: 자체 sqlite + SAKYOWON_ADMIN_KEY 만
```

- 테이블 접두어를 사이트별로(`mn_`, `hs_` …). id는 `new_id("LED")`처럼 사람이 읽는 형태.
- 공개 엔드포인트는 `public/` 아래로 모으고 **행을 그대로 dict(row) 하지 말고 필드를 골라 내보낸다**(작성자·내부 메모 유출 방지).
- 첨부는 `SAKYOWON_FILES`(기본 DB 폴더/files/<site>)에 저장, `scope` 컬럼으로 공개/내부를 구분하고 게시 상태가 바뀔 때마다 재계산.
- 마감·잠금 같은 상태는 409로 거절, 검증 실패는 400, 없는 것 404.

## 서버 반영 스크립트 (`server/install-on-server.sh`)
```bash
curl -fsSL https://raw.githubusercontent.com/deka2026/<repo>/main/server/install-on-server.sh | sudo bash
```
1) `mangnam_api.py`를 `/opt/sakyowon/server/`에 내려받아 `py_compile` 2) `app.py` 끝에 마커 주석으로 감싼 `try: from <module> import install …` 블록을 **없을 때만** 추가(백업 생성) 3) `systemctl restart sakyowon-api` 후 `/api/<site>/health` 확인. 재실행은 모듈 갱신만 한다. `setup.sh`는 app.py만 복사하므로 서버를 재설치하면 이 스크립트를 한 번 더 돌려야 한다.

## 로컬 검증 순서
```bash
pip install --user "fastapi>=0.110" "uvicorn[standard]>=0.29"
SAKYOWON_ADMIN_KEY=devkey SAKYOWON_DB=C:/Users/User/mn-dev/dev.db SAKYOWON_ALLOW_ORIGINS=http://localhost:3000 python server/<module>.py &
python -X utf8 server/smoke_test.py        # 빈 DB로 시작. 한글 쿼리는 urllib.parse.quote
```
프론트는 `.env.development.local`에 `NEXT_PUBLIC_API_BASE=http://127.0.0.1:8787/api`(gitignore, `next build`가 안 읽음). 프론트의 API 클라이언트는 `admin: true`일 때 sessionStorage 키를 `?key=`로 붙이고 항상 `credentials: "include"`.

## 함정
- **Windows 경로 길이**: 스크래치 폴더(240자)에 SQLite·첨부를 두면 `WinError 206`. `C:\Users\User\mn-dev` 같은 짧은 경로.
- **`next dev` 중 `npm run build` 금지** — `.next`가 덮여 dev가 500. 프리뷰 중지 → 빌드 → `.next` 삭제 → 재시작.
- 스모크 테스트는 **빈 DB**로. 이전 실행이 남긴 "마감" 상태가 409를 일으킨다.
- `page.tsx`는 default 외 export 금지(빌드 타입검사 실패). 공용 컴포넌트는 `app/components/`.
- app.py의 CORS는 `Content-Type` 헤더만 허용 — 같은 출처 운영에선 무관하지만, 로컬 CORS 테스트에서 `X-Admin-Key`를 쓰려면 standalone의 CORS 설정에 넣는다(이미 있음).
- 서버 반영 전에는 실사이트가 404 — 프론트는 404를 "자료 없음"으로 처리해 정적만 먼저 배포돼도 깨지지 않게 한다.

## 첫 사례
`deka2026/mangnam-coop` `server/mangnam_api.py` (월별 회계·회의록·문서 보관·경영공시/실적 게시, 관리 화면 `/admin/*`, 공개 `/disclosure`·`/performance`). 설계 문서 `server/README.md`, 핸드오버 `handover-20260925-mangnam-ops-backend.md`.
