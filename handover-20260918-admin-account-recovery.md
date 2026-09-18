# 핸드오버: 사교원 허브 연결 사이트 관리자 계정 전수 복구

**날짜**: 2026-09-18
**이전 핸드오버**: handover-20260911-wiki-target-and-deploy-chain.md
**작업 폴더**: 없음(원격 서버·Supabase 대시보드 작업)

---

## 배경

사용자 요청: "사교원 허브 사이트에 연결된 모든 사이트(서남해 그랜드 제외)의 관리자 아이디·비번을 재설정하고 싶다. 기존 계정을 까먹었다."

## 수행한 작업

### 1. 계정 체계 전수 조사 — 사이트 10개 = 계정 체계 4개

허브 `sakyowon.co.kr`의 실제 링크를 긁어 연결 사이트를 확정하고, 각 레포의 인증 코드를 읽어 저장 위치를 특정했다.

| 체계 | 저장 위치 | 덮는 사이트 |
|---|---|---|
| 통합계정 SSO (쿠키 `sk_session`, Domain=.sakyowon.co.kr) | 서버 `/opt/sakyowon/data/sakyowon.db` → `users` (PBKDF2-SHA256 200,000회) | 허브·`/admin.html`·햇소자·망남활력(SSO)·입찰메이트(운영진) |
| Supabase | 프로젝트 ref `gklecgujcoznxyvywnyu` | 아카데미·팀러닝 |
| 망남활력 자체 비번 | `/etc/mangnam-vitality.env` 의 `ADMIN_PASSWORD` (아이디 없음) | vitality.sakyowon.co.kr |
| 입찰메이트 기업계정 | `/opt/sakyowon/apps/bid-helper/data/app.db` → `companies` (bcrypt) | bid.sakyowon.co.kr |

로그인 자체가 없는 곳: 고향사랑·사교원위키·망남협동조합·cre·본진. `wiki.poomasi.org`는 지미 개인 위키, 서남해 그랜드(`seonamhae-grand.pages.dev`)는 사용자 지시로 제외.

### 2. 결론 — 분실이 아니라 기록 부재였다

아카데미는 사용자가 입력한 값이 **이미 현재 비밀번호**였고(`New password should be different from the old password`), 통합계정도 시도해 보니 로그인됐다. 실제로 잠긴 계정은 하나도 없었다. 손본 것은 **방치된 설정 세 가지**였다.

### 3. 실제 조치 (3건)

- **Supabase Site URL 정상화** — 기본값 `http://localhost:3000` 으로 방치돼 그동안 나간 가입확인·복구 메일 링크가 전부 죽어 있었다. `https://sakyowon.co.kr/academy-site/` 로 교정하고 Redirect URL에 `https://sakyowon.co.kr/**` 추가. 교육생 가입 메일이 이제 정상 동작한다.
- **망남활력 `ADMIN_PASSWORD` 설정** — 미설정이면 `lib/auth.ts` 의 `DEFAULT_PASSWORD` 로 열리는데, 그 값이 **public 레포에 그대로 적혀 있다**. 설정 확인 결과 13자로 걸려 있고 `SESSION_SECRET` 64자도 함께. 서비스 active.
- **`SAKYOWON_ADMIN_KEY` 교체** — `openssl rand -hex 32` 로 교체 후 `systemctl restart sakyowon-api`. **기존 `?key=` 북마크는 전부 무효**가 됐다.

### 4. 최종 상태 — 전 사이트 로그인 확인

| 사이트 | 계정 | 결과 |
|---|---|---|
| 허브·`/admin.html`·햇소자·입찰메이트 | 통합계정 `kimilyoung` | 로그인 확인 |
| 망남활력 | 자체 비번 + SSO 양쪽 | 로그인 확인 |
| 아카데미·팀러닝 | 사교원 대표 메일 계정 | 로그인 확인 |

`rcc@inha.ac.kr`(인하대 협업자, 팀러닝 관리자 승인 상태)는 사용자 지시로 **유지** — 조치 없음.

### 5. 부수 작업

GitHub `deka2026` 계정에 2FA가 강제 등록됐다(Supabase를 GitHub 로그인으로 들어가려다 발생). 인증 앱 등록 완료. 등록 중 QR이 화면 공유에 노출돼 **취소 후 재발급**하도록 안내했다.

## 발견한 함정 (다음 세션용)

1. **Supabase 프로젝트 이름이 내용과 어긋난다.** 사교원 사이트 테이블은 `sakyowon-db`가 아니라 **`solidarity intelligence`** 프로젝트에 있다. `sakyowon-db`는 일시정지 상태이고 무관하다. 이름으로 찾지 말고 ref로 직행할 것.
2. **팀러닝의 `is_admin()` 이 `profiles.role='admin'` 을 본다.** 아카데미 admin이면 `tl_admins` 에 넣지 않아도 팀러닝이 통과한다(실측).
3. **`python - <<'PY'` 힙독 안에서 `input()`/`getpass()` 는 EOFError.** 스크립트가 stdin을 점유하기 때문. 파일로 떨어뜨린 뒤 실행해야 한다.
4. **Supabase 대시보드에 비밀번호 직접 입력 항목이 없다.** `Send password recovery` / `Send magic link` 뿐. 링크로 들어간 뒤 콘솔에서 `sb.auth.updateUser({password})` 를 불러야 끝난다. Chrome이 붙여넣기를 막으므로 `allow pasting` 을 **타이핑**해야 한다.
5. **Site URL이 기본값이면 복구 메일이 무용지물.** 메일을 보내기 전에 `URL Configuration` 부터 확인할 것.

## 미완료 / 다음 할 일

- [ ] 비밀번호 관리자에 4항목 등록 — 통합계정 `kimilyoung` / Supabase 사이트 계정 / 망남활력 / GitHub `deka2026`+2FA 복구코드 (**이번 일의 근본 원인**)
- [ ] GitHub 2FA 복구 코드 저장 여부 확인 (https://github.com/settings/auth/recovery-codes) + 패스키 추가
- [ ] Supabase `sakyowon-db` 프로젝트(일시정지) 정체 확인 — 쓰는 곳 있으면 복원, 없으면 정리
- [ ] 옛 `?key=` 북마크 재발급 (망남 신청조회 등)
- [ ] (이월) 사교원 위키 레슨 여러 건 서버 반영(SSH 4단계) 대기
- [ ] (이월) "300백만원" 해석 확인

## 파일 위치

| 경로 | 내용 |
|---|---|
| `~/.claude/projects/D----------/memory/project-sakyowon-accounts.md` | 계정 체계 지도(이번 세션 신규) |
| `~/haeory-sakyowon-site/server/app.py` | 통합계정 인증 구현(PBKDF2·세션·부트스트랩) |
| `~/haeory-sakyowon-site/server/Caddyfile` | 연결 사이트·서브도메인 전체 지도 |
| `~/haeory-sakyowon-site/server/deploy-www.sh` | 정적 7개 사이트 일괄 배치 |
| `sakyowon-ai/skills/site-admin-account-recovery/` | 이번 세션에서 만든 스킬 |

## 약속

- 사용자가 **"이어서 작업하자"** 라고 하면 이 핸드오버의 "미완료" 목록부터 재개
- 사용자가 **"정리해"** 라고 하면: ①핸드오버 ②스킬 ③레슨 ④위키배포 자동 수행
