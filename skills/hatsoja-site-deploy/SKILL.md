---
name: hatsoja-site-deploy
description: 햇소자 사이트(deka2026.github.io/hatsoja, 단일 파일 SPA)를 수정하고 PR→머지→GitHub Pages→실사이트(sakyowon.co.kr/hatsoja) 반영 확인까지 수행하는 스킬. "햇소자 메뉴 고쳐줘", "회원등급 바꿔줘", "햇소자 수정해서 반영해줘" 같은 요청에 사용. 등급별 메뉴·권한은 ROLE_MENUS 표 한 곳만 고치면 되고, 라이브 확인은 빌드 성공 후 3분쯤 폴링해야 한다.
---

# 햇소자 수정→배포 절차

## 저장소·구조

- GitHub `deka2026/deka2026.github.io` (기본 브랜치 **main**, push→Pages 자동배포, CNAME = sakyowon.co.kr)
- 햇소자는 `hatsoja/index.html` **한 파일**(약 600KB, HTML+CSS+JS 인라인) + `manual.html`(이용안내) + `manifest.json`
- 로컬 클론은 상시 없음. `C:\Users\User\AppData\Local\Temp\hub-clone`이 있으면 재사용, 없으면:
  ```bash
  git clone --depth 30 https://github.com/deka2026/deka2026.github.io.git "$LOCALAPPDATA/Temp/hub-clone"
  ```
  (긴 한글 경로에서 git이 거부한 적이 있어 Temp에 둔다)
- **작업 전 `git fetch` + `git status -sb`** — 다른 세션이 main에 push한다
- 라이브: https://sakyowon.co.kr/hatsoja/ (캐노니컬 deka2026.github.io/hatsoja는 301로 여기로 옴)

## 코드 지도 (`hatsoja/index.html`, 2026-09-25 기준)

| 찾을 것 | 위치·이름 |
|---|---|
| 상단 메뉴 HTML | `<nav class="topnav">` — `#pubNav`(손님 공개 메뉴, 정적) · `#roleNav`(등급 메뉴, JS가 채움) |
| 등급 정의 | `const ROLES = {admin, federation, coop, guest}` — label·emoji·home·desc |
| **등급별 메뉴·권한** | `const ROLE_MENUS` — `[묶음이름, [[scope, page, 이모지, 메뉴명], ...]]`. 상단 메뉴바·사이드바·`canAccess()` 셋이 전부 이 표를 본다 |
| role 정규화 | `normalizeRole(role, status)` — 서버 값·구 저장값을 4등급으로. `currentUser()`가 읽을 때 적용 |
| 접근 검사 | `canAccess(u, scope, page)` → `navigate()`에서 호출. 차단 시 `roleHome(role)`로 되돌림 |
| 데모 계정 | `const DEMO_ACCOUNTS` + `demoLogin(role)` — 로그인 창 버튼·체험 띠 "등급 바꿔 보기" 공용 |
| 사이드바 | `renderRoleSidebar(role, scope, page)` (관리자는 미리보기 바로가기 추가) |
| 상단 등급 메뉴 | `renderRoleNav()` — `renderTopActions()`·`navigate()` 끝에서 호출 |
| 미리보기 | `startPreview(role)` / `endPreview()` (sessionStorage `sv_preview_admin`) |
| 편의 띠·FAB | `updateConvenienceUI(scope, page)` — 체험 띠 `#demoBar`(등급 전환 버튼 `#demoSwitch`), 미리보기 띠 `#previewBar` |
| 메뉴 설명(툴팁·AI 맥락) | `const MENU_DESC` — adm 대시보드는 키 `admDashboard` |
| 페이지 본문 | `renderMemberPage(page)` switch (mem/*) · `renderAdminPage(page)` switch (adm/*) |
| 라우트 | `#/pub/<view>` · `#/mem/<page>` · `#/adm/<page>` — 뷰는 `<section class="view" id="v-pub-*">`, 로그인 화면은 `#v-app` 하나 |

### 메뉴를 옮기거나 등급을 바꿀 때

1. `ROLE_MENUS`에서 해당 등급 배열만 고친다. 페이지 함수는 건드릴 필요 없다.
2. 새 페이지를 만들면 `renderMemberPage`/`renderAdminPage` switch에 case 추가 + `MENU_DESC`에 설명 한 줄.
3. 접근 규칙(`canAccess`): pub은 누구나, admin은 전부, coop은 `mem/*` 전부, federation은 표에 적힌 것만, guest는 pub만. 등급을 늘리면 여기도 손본다.
4. 서버가 주는 role 문자열이 새로 생기면 `normalizeRole`의 switch에 추가.

## 편집·검증

- 파일이 크므로 Read는 구간 지정, 편집은 Edit(정확 문자열)로. `grep -n "^function 이름"`으로 위치를 잡는다.
- 문법 검사(브라우저 열기 전에):
  ```bash
  node -e "const h=require('fs').readFileSync('hatsoja/index.html','utf8');const re=/<script(?![^>]*src=)[^>]*>([\s\S]*?)<\/script>/g;let m,i=0;while((m=re.exec(h))){i++;try{new Function(m[1])}catch(e){console.log('script#'+i,e.message)}}console.log('scripts',i)"
  ```
- 로컬 확인: `.claude/launch.json`에 `python -m http.server 8765 --bind 127.0.0.1 --directory <클론경로>` 등록 → `preview_start` → `http://localhost:8765/hatsoja/index.html#/pub/home`. `file://`은 브라우저 도구가 못 연다. launch.json은 세션 작업폴더 기준으로 읽히니 클론 밖(세션 폴더)에 둔다.
- 등급 4종 한 번에 점검하는 JS (콘솔·javascript_tool):
  ```js
  const w=ms=>new Promise(r=>setTimeout(r,ms)); const o={};
  for(const r of ['federation','coop','guest','admin']){ demoLogin(r); await w(300);
    o[r]={hash:location.hash, nav:document.getElementById('roleNav').innerText.replace(/\s+/g,' ')}; }
  o
  ```
  차단 확인은 `location.hash='#/adm/users'` 후 hash가 `roleHome`으로 돌아오는지 본다.
- 모바일은 `resize_window` mobile → `toggleNav()` → 스크린샷, 끝나면 desktop으로 복귀.

## 배포

```bash
git checkout -b feat/<주제>            # main에 직접 커밋했다면: git branch -f main origin/main 로 되돌리고 브랜치에 남김
git push -u origin feat/<주제>
gh pr create --base main --title "..." --body "..."
gh pr merge <N> --merge --delete-branch
git checkout main && git pull
gh run list --limit 1 --json status,conclusion,url          # "pages build and deployment"
gh run watch <runId> --exit-status
```

사용자가 "바로 반영해"라면 main에 직접 push해도 된다(Pages 트리거는 같다). 커밋 메시지 한국어 제목 + Co-Authored-By 푸터.

## 라이브 확인 — 빌드 success ≠ 라이브

Pages 빌드가 success여도 **원본 반영까지 약 3분** 걸린다(2026-09-25: 12:53 success → 12:56 반영). 쿼리스트링을 붙여도 옛 파일이 오니 CDN 캐시 문제가 아니다. 반드시 폴링한다.

```bash
for i in $(seq 1 12); do n=$(curl -s "https://sakyowon.co.kr/hatsoja/index.html?v=$(date +%s%N)" | grep -c "<이번 변경의 고유 문자열>"); echo "try $i: $n"; [ "$n" -gt 0 ] && break; sleep 15; done
```

새 코드가 보이면 브라우저로 `https://sakyowon.co.kr/hatsoja/?v=2#/pub/home` 열고 위 등급 점검 JS를 한 번 더 돌린다. 이전에 열어 둔 브라우저는 Ctrl+F5.

## 함정

1. `location.hash = home`이 현재 해시와 같으면 hashchange가 안 나 화면이 안 바뀐다 → `if(location.hash===home) navigate(); else location.hash=home;` (demoLogin·startPreview가 이 패턴)
2. `MOCK.users`의 `role:'member'` 데이터는 그대로 두고 표시 때 `normalizeRole`로 — localStorage에 남은 옛 사용자 값과 호환
3. 체험 띠(`#demoBar`)는 unified가 아닌 사용자면 모든 scope에서 보인다(등급 전환용). 실계정에는 안 보인다
4. 서버 `/api/auth/me`의 role에는 아직 `federation`이 없다 — 실계정 연합회는 본부가 role 값을 줘야 동작
5. 사본을 `D:\...\햇빛발전협동조합 업무자동화 사이트\`에 남길 때 `hatsoja/` 폴더째 복사하면 파일로 열어도 데모 모드로 동작한다
