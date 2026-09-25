---
name: academy-site-deploy
description: 연대지능활동가 아카데미 사이트(deka2026/academy-site, 단일 파일 SPA)를 수정하고 push→서버 배포 스크립트→실사이트(sakyowon.co.kr/academy-site) 반영 확인까지 수행하는 스킬. "아카데미 사이트 실습 메뉴 고쳐줘", "학습 가이드 프롬프트 문구 바꿔줘", "아카데미 사이트 수정해서 반영해줘" 같은 요청에 사용. 실습시작 15단계·연대지능 7단계는 프롬프트 카드 방식이며 문구는 LEARN_PROMPTS/SOLID_PROMPTS 한 곳만 고친다. 라이브는 GitHub Pages가 아니라 자체 서버(Caddy)라 push 뒤 사용자가 서버 스크립트를 돌려야 바뀐다.
---

# 아카데미 사이트 수정→배포 절차

## 저장소·구조

- GitHub `deka2026/academy-site` (기본 브랜치 **main**). 로컬 클론 `C:\Users\User\academy-site` 상시 존재.
- `index.html` **한 파일**(약 480KB, CSS+HTML+JS 인라인, **CRLF**) + `manifest.json` + `supabase/`·`*.sql`(백엔드 메모). 상태 문서 `작업현황_정리.md`(2026-07 기준, 옛 정보 포함).
- 백엔드: Supabase(`gklecgujcoznxyvywnyu`) Auth + profiles. 학습 진행률은 localStorage(`academy_learn_progress`, `academy_solid_progress`, 이메일별). 세션은 localStorage `academy_session` (`{email,name,role}`; role `guest|user|admin`).
- 라이브: https://sakyowon.co.kr/academy-site/ (deka2026.github.io/academy-site는 301로 여기로 옴).
- **작업 전 `git fetch` + `git status -sb`** — 같은 날 병행 세션이 main에 push한다(2026-09-25: 자격증아카데미 신설, 망남 링크). 뒤처져 있으면 `git rebase origin/main`.
- 산출물 사본은 `D:\사교원 개발그룹\사교원 개발그룹\연대지능활동가 아카데미\`에 날짜 접미사로 남긴다(사용자 지시).

## 배포 사슬 (GitHub Pages가 아니다)

`curl -I https://sakyowon.co.kr/academy-site/` → `Server: Caddy`. 가비아 서버가 `/opt/sakyowon/www/academy-site`를 서빙한다. Pages 빌드가 success여도 라이브는 안 바뀐다.

| 단계 | 내용 | 누가 |
|---|---|---|
| 1 | `git push origin main` | 나 |
| 2 | 서버(root@sakyowon-server)에서 `bash /opt/sakyowon/src/deploy-www.sh` — academy-site main을 clone해 재배치 (원본 `C:\Users\User\haeory-sakyowon-site\server\deploy-www.sh`) | **사용자(SSH)** |
| 3 | 확인 | 나 |

2단계 전에는 "push 완료, 서버 반영 대기"로 보고하고 실행할 한 줄을 준다. 사용자가 이 PC용 `cd C:\...` 명령을 서버에 붙여넣은 적이 있으니, 서버용 한 줄만 코드블록으로 준다.

확인은 세 가지를 함께 본다:

```bash
curl -sI "https://sakyowon.co.kr/academy-site/" | grep -i "^last-modified"       # 서버 파일 갱신 시각
curl -sL "https://sakyowon.co.kr/academy-site/?v=$RANDOM" | grep -c "<새 함수명>"   # 새 코드 존재
# 라이브 파일과 커밋 바이트 대조 (CRLF 정규화)
curl -sL "https://sakyowon.co.kr/academy-site/index.html?v=$RANDOM" -o "$TEMP/live.html"
git show HEAD:index.html > "$TEMP/head.html"
python -c "import io,os;t=os.environ['TEMP'];n=lambda p:io.open(p,'rb').read().replace(b'\r\n',b'\n');print(n(t+'/live.html')==n(t+'/head.html'))"
```

## 코드 지도 (`index.html`, 2026-09-25 기준)

| 찾을 것 | 위치·이름 |
|---|---|
| 페이지 전환 | `go(id, link)` — `<div id="..." class="page">`. 실습시작 `course-practice`, 학습개요 `course-overview`, 연대지능 학습 가이드 `solidarity-unified` |
| 로그인 판정 | `getSession()` / `currentRole()` (SESSION_KEY `academy_session`) |
| **실습시작 15단계** | `LEARN_STEPS`(id·title·desc·guide·check; guide는 화면에 안 나옴) / `LEARN_PRECHECKS`(미사용) / **`LEARN_PROMPTS`**(id → `{where, text}`) / `LEARN_WHERE`(`web`·`code` 라벨) |
| 실습 카드 렌더 | `showLearnStep(idx)` → `.learn-card`(lc-head·lc-desc·lc-how·lc-where·prompt-box>.learn-prompt-text·lc-actions) |
| 실습 버튼 | `learnNextStep()`·`learnPrevStep()`·`jumpToStep(i)`·`copyLearnPrompt(btn)`·`learnCmd('start'|'save'|'resume')`·`sendLearnChat()` |
| **연대지능 7단계** | `SOLID_STEPS` / **`SOLID_PROMPTS`** / `SOLID_FUNCS.getProgress·saveProgress` / `showSolidStep`·`solidNextStep`·`solidPrevStep`·`solidJumpToStep`·`solidCmd`·`sendSolidChat` |
| 카드 CSS | `.learn-card…`, `.learn-btn.next|prev|copy` (프롬프트 카드 CSS 블록, `.prompt-copy.done` 바로 뒤) |
| HTML 이스케이프 | `escHtml(s)` |
| 홈 AI 대화(키워드) | `KB` 배열 — 아직 "교육 과정은 6단계" 옛 문구 |
| 검증 게임 | `GAME_POOL_MONTH`·`GAME_SESSION_SIZE`, 문항 `{cat, source, text, answer, hint}` |

### 프롬프트 문구를 고칠 때

`LEARN_PROMPTS` / `SOLID_PROMPTS`의 `text`만 고친다. 단계 id는 `LEARN_STEPS`/`SOLID_STEPS`의 id와 같아야 카드에 나온다. `where`는 `web`(클로드 앱·claude.ai) 또는 `code`(Claude Code). 유인물 md는 `LEARN_STEPS`+`LEARN_PROMPTS`에서 node로 뽑는다(핸드오버 20260925 참조).

## 편집·검증

- 파일이 크므로 Read는 구간 지정, 편집은 Edit(정확 문자열) 또는 파이썬 바이트 치환. **CRLF 보존**: 파이썬으로 쓸 때 `io.open(p,'rb')`로 읽고 `\r\n` 그대로 두거나, `\n`으로 정규화해 작업한 뒤 `.replace('\n','\r\n')`으로 되돌려 `'wb'`로 쓴다. 텍스트 모드 `newline` 인자를 잘못 주면 파일 전체가 LF로 바뀌어 diff가 5천 줄이 된다(`file index.html`로 CRLF 확인).
- 파이썬 스크립트는 **짧은 경로**(`%TEMP%\acad_patch\`)에 둔다. 세션 스크래치패드 경로는 260자를 넘어 python.exe·sed가 "No such file"로 못 연다(Write 도구는 성공하므로 헷갈린다).
- 문법 검사는 **`<script>` 블록별로**(블록이 2개 이상):
  ```bash
  python - <<'EOF'
  import re,io,subprocess,os
  s=io.open('index.html',encoding='utf-8').read()
  for i,b in enumerate(re.findall(r'<script>(.*?)</script>',s,re.S)):
      p=os.path.join(os.environ['TEMP'],'blk%d.js'%i); io.open(p,'w',encoding='utf-8').write(b)
      r=subprocess.run(['node','--check',p],capture_output=True,text=True); print(i,'OK' if r.returncode==0 else r.stderr[:300])
  EOF
  ```
- 로컬 확인: 세션 작업폴더의 `.claude/launch.json`에 `python -m http.server <포트> --bind 127.0.0.1 --directory C:/Users/User/academy-site` 등록 → `preview_start`. `file://`은 브라우저 도구가 못 연다. 포트가 다른 세션 것과 겹치면 바꾼다(8765는 허브 세션이 씀).
- 로그인 없이 시험하려면 javascript_tool로 `localStorage.setItem('academy_session', JSON.stringify({email:'test@example.com',name:'테스트',role:'user'}))` 후 `go('course-practice',null)`. 끝나면 지운다. 실사이트에서 할 때는 원래 값을 보관했다 복원.
- 흐름 점검 JS(한 번에):
  ```js
  learnCmd('start'); learnNextStep(); document.getElementById('learnChatInput').value='다음'; sendLearnChat();
  learnPrevStep(); jumpToStep(14); learnNextStep();
  JSON.parse(localStorage.getItem('academy_learn_progress'))['test@example.com'].step   // 15면 끝까지 감
  ```
- 브라우저 도구 함정: 창이 가려져 있으면 screenshot이 5초 타임아웃 — 재시도하거나 read_page/JS로 확인. 페인이 숨겨진 상태의 `innerWidth`는 0이라 가로 넘침 판정이 오염된다(모바일 프리셋으로 다시 재라). `location.reload()`가 든 스크립트는 거기서 끊기니 다음 호출로 나눈다.

## 함정 모음

1. 라이브 반영은 서버 스크립트까지. Pages 빌드 success·`gh run list`만 보고 "반영 완료"라 쓰지 말 것.
2. 병행 세션이 main에 push → fetch·rebase 없이 push하면 거부된다.
3. 시작 직후 진행 기록이 비어 있으면 "다음"이 재시작으로 오인될 수 있다 — 시작 시 `{action:'start'}` 로그를 남기는 현재 구조를 유지.
4. `addLearnMsg/addSolidMsg`는 `isHtml`이 아닐 때만 `white-space:pre-wrap`. 카드 HTML을 줄바꿈 넣어 만들면 빈 줄이 생긴다.
5. 정의되지 않은 CSS 변수(`--good` 등)를 인라인 스타일에 쓰면 배경이 사라져 흰 글자만 남는다. 정의된 것: `--accent --warn --success --sub --border --card --bg --text`.

## 자격증아카데미 · SQLD 과정 데이터 다루기 (2026-09-25 20회차 기준)

- 코드 위치: `/* ===== 자격증아카데미: SQLD 과정 ===== */` 아래 `var SQLD_KEY = 'sqld_v2'` · `var SQLD_MODULES = [...]` · 렌더 `renderSqldHome` · 학습 `sqldStart → sqldShowReview(보완) → sqldEnterLearn → sqldStartQuiz → sqldFinish`.
- 모듈 형식: `{no, part(1|2), title, intro, yt:[검색어 2개], concepts:[{topic,title,html}], quiz:[{topic, q, c:[4], a:0~3, exp}]}`. `html`은 `<ul><li>`, `<` 는 `&lt;`로. 문자열은 작은따옴표, 안의 따옴표는 `\'`.
- **문항 `topic`은 같은 회차 `concepts`의 `topic`과 정확히 일치**해야 한다. 보완 학습이 `sqldFindConcept(topic)`으로 카드를 찾기 때문에 어긋나면 약점 카드가 비어 나온다.
- 진행 기록은 localStorage `SQLD_KEY`에 `{done:{회차:{s,t,d}}, weak:{topic:n}, wrong:[{m,qi}]}`. **회차 번호나 문항 순서를 바꾸면 `wrong`의 `{m,qi}`가 어긋나므로 키를 올린다**(v1→v2처럼). 문항을 끝에 추가만 하면 키 유지 가능.
- 화면 하드코딩: 과정 홈 "완료 회차 / N", "학습 모듈 (N회차 × 10분)", "확인 문제 N문항", 학습 화면 "확인 문제 풀기 (N문항)". 퀴즈 헤더의 총 문항 수는 `#sq-qtotal`로 동적.
- 편집 절차: 데이터를 `%TEMP%\acad_patch\sqld_modules.js`에 `var SQLD_MODULES = [...]` 형태로 따로 쓰고 → 아래 검증 → 파이썬으로 `var SQLD_MODULES = [` ~ `];\r\n\r\n/* ---- 저장 ---- */` 구간을 바이트 치환(CRLF 유지).
  ```bash
  node --check sqld_modules.js && node -e "
  const M=new Function(require('fs').readFileSync('sqld_modules.js','utf8')+';return SQLD_MODULES;')();let bad=[];
  M.forEach((m,i)=>{if(m.no!==i+1)bad.push('no '+m.no);if(m.quiz.length!==6)bad.push(m.no+' quiz');
   const t=new Set(m.concepts.map(c=>c.topic));m.quiz.forEach((q,j)=>{if(q.c.length!==4||new Set(q.c).size!==4)bad.push(m.no+'-'+j+' choices');
   if(!(q.a>=0&&q.a<4))bad.push(m.no+'-'+j+' answer');if(!t.has(q.topic))bad.push(m.no+'-'+j+' topic '+q.topic);});});
  console.log(M.length,'modules',bad.length?bad.join(' | '):'ALL OK')"
  ```
- 흐름 점검 JS(로컬 프리뷰, 로그인 불필요): `sqldStart(1); sqldStartQuiz(); /* 첫 문제 오답 */ sqldAnswer((SQLD_MODULES[0].quiz[0].a+1)%4); sqldNextQuestion(); …; sqldStart(2)` → `#sq-review-area`가 보이고 `#sq-review-retry`에 재시도 문항이 있으면 정상. `sqldRetryAnswer(0, 정답)` 후 `weak`가 줄어야 한다.
- 문항은 전부 가상 문제(기출 비공개). 과정 홈의 "문제에 대한 안내" 상자를 지우지 말 것.
