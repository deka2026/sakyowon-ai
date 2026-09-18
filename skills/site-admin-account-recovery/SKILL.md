---
name: site-admin-account-recovery
description: 사교원 허브에 연결된 사이트들의 관리자 계정을 잃었거나 재설정해야 할 때, 사이트를 열거하고 각각의 인증 방식·저장 위치를 특정한 뒤 체계별 복구 경로를 실행하는 스킬. "관리자 비번 까먹었어", "계정 재설정해줘", "이 사이트 관리자로 못 들어가" 같은 요청에 사용. 비밀번호는 사용자가 직접 입력하게 하고 대화에 남기지 않는다.
---

# 사이트 관리자 계정 복구

## 핵심 원칙 두 가지

**하나 — 사이트 수가 아니라 계정 체계 수를 센다.** 사교원은 사이트가 10개지만 계정 체계는 4개뿐이다. 사이트별로 접근하면 10번 헤매고, 체계별로 접근하면 4번에 끝난다. 조사 단계에서 반드시 이 매핑을 먼저 만든다.

**둘 — 잠긴 게 아니라 기록이 없는 경우가 흔하다.** 2026-09-18 전수 복구에서 실제로 잠긴 계정은 하나도 없었다. 재설정을 실행하기 전에 **로그인을 먼저 시도하게 한다.** 되면 그걸로 끝이고, 안 되는 것만 재설정한다. 순서를 뒤집으면 멀쩡한 계정의 세션을 전부 날리게 된다.

## 1단계 — 연결 사이트 열거

```bash
curl -s https://sakyowon.co.kr/ | grep -oE 'href="[^"]+"' | sort -u
```

정적 링크만으로는 서브도메인·서버형 앱이 빠진다. 반드시 Caddy 설정을 함께 본다 — 여기에 도메인·포트·프록시 대상이 전부 있다.

```bash
cat ~/haeory-sakyowon-site/server/Caddyfile
cat ~/haeory-sakyowon-site/server/deploy-www.sh   # 정적 사이트 배치 목록
```

`scripts/map-sites.sh` 로 한 번에 돌릴 수 있다.

## 2단계 — 사이트별 인증 방식 특정

로컬 클론이 없어도 gh CLI로 레포 트리를 훑으면 된다. 클론보다 훨씬 빠르다.

```bash
for r in <repo1> <repo2>; do
  echo "=== $r"
  gh api "repos/deka2026/$r/git/trees/HEAD?recursive=1" -q '.tree[].path' \
    | grep -iE "admin|auth|login|user|password|seed" | head -15
done
```

걸린 파일을 `gh api repos/OWNER/REPO/contents/PATH -q .content | base64 -d` 로 바로 읽는다. 볼 것은 **해시 알고리즘·저장 테이블·세션 쿠키 이름·부트스트랩 경로** 넷이다.

## 3단계 — 체계별 복구 경로

### (가) 자체 서버 FastAPI + SQLite (통합계정 SSO)

- 저장: `/opt/sakyowon/data/sakyowon.db` → `users`, 형식 `pbkdf2:200000:<salt>:<hex>`
- 환경변수: `/etc/sakyowon-api.env`, 서비스 `sakyowon-api`

**옛 비번을 몰라도 되는 부트스트랩이 있다.** signup 본문에 `admin_key`(=`SAKYOWON_ADMIN_KEY`)를 넣으면 즉시 승인+admin으로 계정이 생긴다.

기존 계정을 살리려면 `scripts/reset_sso_password.py` 를 서버에 올려 실행한다. **힙독으로 넘기면 안 된다**(아래 함정 3).

### (나) Supabase (아카데미·팀러닝)

- 프로젝트는 **이름이 아니라 ref로 찾는다**: `https://supabase.com/dashboard/project/gklecgujcoznxyvywnyu`
- 권한은 인증과 별개다. 아카데미 = `profiles.role`, 팀러닝 = `tl_admins.approved`. 단 팀러닝 `is_admin()` 이 `profiles.role='admin'` 을 보므로 **아카데미 admin이면 팀러닝도 자동 통과**한다.

현황 파악 SQL:

```sql
select u.id, u.email, u.last_sign_in_at,
       p.role as academy_role, t.approved as teamlearning_approved
from auth.users u
left join public.profiles  p on p.id = u.id
left join public.tl_admins t on lower(t.email) = lower(u.email)
order by u.created_at;
```

비밀번호 재설정은 **메일 경로뿐**이다. 보내기 전에 `URL Configuration` 의 Site URL을 확인한다(함정 5). 링크 클릭 후 사이트 콘솔에서 마무리한다:

```js
await sb.auth.updateUser({ password: '...' })
```

메일이 막히면 SQL 직접 변경이 대안이지만, **평문이 편집기 자동저장에 남으므로** 실행 후 쿼리를 삭제해야 한다.

```sql
update auth.users
set encrypted_password = extensions.crypt('...', extensions.gen_salt('bf')),
    updated_at = now()
where email = '...';
```

### (다) 환경변수 한 개짜리 (망남활력)

아이디가 없고 `ADMIN_PASSWORD` 만 본다. **미설정이면 코드의 `DEFAULT_PASSWORD` 로 열리는데 그 값이 public 레포에 적혀 있다.** 점검 1순위.

```bash
sudo awk -F= '/^ADMIN_PASSWORD=/{print "len:", length($2)}' /etc/mangnam-vitality.env
```

값을 출력하지 말고 **글자수만** 찍어 확인한다. 기본값과 길이가 다르면 설정된 것이다.

### (라) bcrypt + SQLite (입찰메이트 기업계정)

`/opt/sakyowon/apps/bid-helper/data/app.db` → `companies.pass_hash`. 운영진은 SSO 경로(`/api/auth/sso`)로 들어가므로 (가)만 고치면 손댈 일이 없다.

## 안전 원칙

- **비밀번호를 대화에 남기지 않는다.** 사용자가 붙여넣으려 하면 제지하고, 성공 여부만 보고받는다.
- 서버에서는 `getpass`·`read -s` 로 받아 셸 히스토리를 피한다. `curl -d '{"password":"..."}'` 를 쓰게 했다면 `history -c` 를 안내한다.
- 사용자가 키·토큰을 붙여넣었으면 **그 값은 죽은 것으로 취급하고 교체**를 권한다.
- 2FA 등록 QR은 그 자체가 비밀키다. 화면이 공유됐으면 취소 후 재발급.
- `Ban user` · `Delete user` · `Remove MFA factors` 는 절대 누르게 하지 않는다.

## 함정 모음

1. **Supabase 프로젝트 이름이 내용과 어긋난다.** 사교원 사이트 테이블은 `solidarity intelligence` 에 있고 `sakyowon-db` 는 일시정지된 무관한 프로젝트다.
2. **권한과 인증은 별개다.** 비번만 고치고 role을 안 보면 "관리자 계정이 아닙니다"에서 막힌다.
3. **`python - <<'PY'` 안에서 `input()`/`getpass()` 는 EOFError.** 스크립트가 stdin을 점유한다. 파일로 떨어뜨려 실행할 것.
4. **Supabase 대시보드에 비밀번호 직접 입력 항목이 없다.** 메일 발송 두 가지뿐이고, 마무리는 사이트 콘솔에서 해야 한다. Chrome이 붙여넣기를 막으므로 `allow pasting` 을 **타이핑**하게 안내한다.
5. **Site URL이 기본값 `http://localhost:3000` 이면 복구 메일이 전부 무용지물.** 메일을 보내기 전에 고친다. 이 값은 가입확인 메일에도 쓰이므로, 방치돼 있었다면 그동안 신규 가입이 통째로 깨져 있었다는 뜻이다.
6. **관리자 키를 교체하면 `?key=` 북마크가 전부 죽는다.** 교체 후 반드시 안내한다.
7. 쿠키가 `Domain=.sakyowon.co.kr` 이면 하위 도메인 전체가 한 로그인을 공유한다. 세션을 지우면 **전 사이트가 함께 로그아웃**된다.

## 마무리 체크리스트

- [ ] 체계별로 로그인 실증 (페이지가 열리는지가 아니라 실제 로그인)
- [ ] 비밀번호 관리자 등록 권고 — 이 작업의 재발 방지는 여기에 달렸다
- [ ] 교체한 키에 의존하던 북마크·스크립트 갱신
- [ ] 계정 지도를 메모리에 저장 (`project-sakyowon-accounts.md`)
