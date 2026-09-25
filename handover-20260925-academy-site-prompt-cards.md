# 핸드오버: 아카데미 사이트 실습시작·연대지능 학습 가이드를 "프롬프트 카드" 방식으로 단순화

**날짜**: 2026-09-25
**이전 핸드오버**: handover-20260925-hatsoja-member-roles.md (같은 날 병행 세션) / 아카데미 계열 직전은 handover-20260918-hpc-nipa-hatsoja-integration.md (교안·강의PPT는 2026-09-16~19 세션)
**작업 폴더**: `C:\Users\User\academy-site` (deka2026/academy-site, main) → 사본 `D:\사교원 개발그룹\사교원 개발그룹\연대지능활동가 아카데미\`

---

## 수행한 작업

### 1. 실습시작 15단계 → 프롬프트 카드 (커밋 `3d31304`, 13:56 실사이트 반영)

사용자 지시: "세부 내용이 어려워. 초보자가 자기 클로드 입력창에 넣을 프롬프트만 주고 '복사해서 붙여넣으세요' 안내만 해. 복사 버튼, 그리고 입력창에 '다음'이라고 안 쳐도 넘어가는 다음 버튼."

- `LEARN_PROMPTS`(단계 id → `{where:'web'|'code', text}`) 15개 신설. 화면에는 긴 `guide`·`LEARN_PRECHECKS` 대신 **카드 하나**: 단계 제목 / 한 줄 설명 / "복사 → 내 클로드 입력창에 붙여넣기 → 다음" 안내 / 붙여넣는 곳 / 프롬프트 / 버튼(프롬프트 복사·← 이전·다음 →).
- 이전 단계 점검은 프롬프트 첫 줄에 녹임 ("먼저 node --version으로 1단계가 잘 됐는지 확인시켜 줘").
- 붙여넣는 곳: 1~5·7·9단계는 클로드 앱/claude.ai(`LEARN_WHERE.web`), 6·8·10~15는 Claude Code(`.code`).
- `showLearnStep`이 카드 HTML 렌더, `copyLearnPrompt`(클립보드 API + execCommand 폴백, 라벨 복원), `learnNextStep`/`learnPrevStep`. 상단 버튼줄에도 ← 이전 / 다음 → 추가. 타이핑 "다음/완료/이전 단계/N단계부터" 경로는 전부 새 함수로 위임해 그대로 동작.
- 버그 잡음: 시작 직후 `p.log`가 비어 첫 "다음"이 재시작으로 오인 → 시작 시 `{action:'start'}` 로그를 남김.
- 10단계 프롬프트에 "quartz 폴더를 8단계 저장소(my-solidarity-wiki)에 연결" 문장을 넣어 9단계 배포·11단계 push가 같은 저장소를 가리키게 함(원 교육과정의 어긋남 보정).

### 2. 연대지능 학습 가이드 7단계 → 같은 방식 (커밋 `aed9fb0`, 14:05 반영) + 버튼 색 (`4dcdd4a`, 14:16 반영)

- `SOLID_PROMPTS` 7개. 1~5단계(개념)는 아카데미 핵심 내용(4원칙 / 4역할·L1~L4 / 데이터 주권 / 전문 AI 4단계 / 문서 4종·4요소·5질문)을 **프롬프트 안에 담아** 어느 클로드에 붙여넣어도 같은 틀로 설명하고 확인 질문을 하게 함. 6~7단계는 Claude Code가 my-wiki 문서 작성 → solidarity-intelligence-wiki Fork·PR.
- `showSolidStep`/`solidNextStep`/`solidPrevStep`/`solidJumpToStep`(배지 클릭·"N단계부터" 점프 신설). 카드 CSS·`copyLearnPrompt`·`escHtml`은 실습시작 것 재사용.
- "이어서 학습" 버튼이 정의되지 않은 `var(--good)`을 써서 흰 글자만 보이던 기존 버그 → `#2563eb`.

### 3. 배포 경로 확인 — sakyowon.co.kr/academy-site는 GitHub Pages가 아니다

- `curl -I` → `Server: Caddy`. 가비아 서버가 `/opt/sakyowon/www/academy-site`를 서빙. push + Pages 빌드 성공 후에도 라이브는 옛 파일이었다.
- 반영 사슬: ① `git push origin main` ② 서버에서 `bash /opt/sakyowon/src/deploy-www.sh`(사용자, SSH) ③ 확인 = `Last-Modified` + 새 함수명 grep + **라이브 파일과 커밋 바이트 대조**(세 번 모두 일치).
- 원격에 병행 세션 커밋 2개(자격증아카데미 SQLD 신설 `5fde02d`, 망남 링크 `4991452`)가 먼저 있어 rebase 후 push. 그 커밋이 `<script>` 블록을 하나 더 추가해 문법 검사는 **블록별로** 돌려야 했다.

### 4. 검증

- 인라인 스크립트 `node --check` 블록별 통과. 로컬 `python -m http.server`(launch.json은 세션 폴더에, `--directory`로 레포 지정) + 브라우저 도구로 시작→다음→타이핑 "다음"→이전→배지 점프→복사→완료, 진행률 저장, 모바일 375px 가로 넘침 없음 확인. 실사이트에서도 같은 시나리오 재확인.

### 5. 저장 (사용자 지시 "사교원 개발그룹>연대지능활동가 아카데미 폴더에 저장해")

`D:\사교원 개발그룹\사교원 개발그룹\연대지능활동가 아카데미\` — `아카데미사이트_index_실습단순화_20260925.html`(수정본 사본) · `실습15단계_프롬프트_20260925.md` · `연대지능학습가이드7단계_프롬프트_20260925.md`(유인물) · `아카데미사이트_실습메뉴_변경내역_20260925.md`(변경·배포 절차).

## 미완료 / 다음 할 일

- [ ] 홈 "AI 대화" 키워드 답변(`KB`)이 아직 "교육 과정은 6단계…" 옛 구조를 말한다 — 15단계/7단계·프롬프트 카드 방식으로 문구 갱신
- [ ] 학습개요 페이지의 "실습시작 메뉴의 N단계에서 직접 해봐요" 링크는 살아 있으나, 카드가 프롬프트 중심이 됐으니 학습개요 본문의 세부 설치 설명과 역할 분담을 한 번 점검
- [ ] 캡처 올리기 기능은 남겨 두었으나 카드 흐름에서 존재감이 약함 — 쓸모없으면 제거, 쓸모 있으면 "내 클로드에 올리세요" 안내로 통일
- [ ] 15단계 교육과정의 9단계(Cloudflare, my-solidarity-wiki 배포) ↔ 10단계(quartz 별도 폴더) 어긋남은 프롬프트 문구로만 봉합했다. 교안(`마을강사단_AI교육_교안_6질문_20260919.hwpx`)의 3부 15단계 지도와 맞춰 볼 것
- [ ] (이월) 햇소자 `federation` role 서버 신설 요청 등 — handover-20260925-hatsoja-member-roles.md 참조

## 파일 위치

| 경로 | 내용 |
|---|---|
| GitHub `deka2026/academy-site` main `4dcdd4a` → `index.html` | 캐노니컬(라이브 https://sakyowon.co.kr/academy-site/) |
| `C:\Users\User\academy-site` | 로컬 클론(main = origin/main) |
| `index.html` `LEARN_PROMPTS` / `SOLID_PROMPTS` | 프롬프트 문구. 고칠 일이 생기면 여기만 |
| `D:\…\연대지능활동가 아카데미\아카데미사이트_실습메뉴_변경내역_20260925.md` | 변경 요지·배포 절차(사용자용) |
| `sakyowon-ai/skills/academy-site-deploy/` | 스킬(이번 세션 신설): 코드 지도·검증·배포 사슬·함정 |
| 사교원 위키 `content/연대지능아카데미/AI-실습-안내를-프롬프트-카드로-바꾸기.md` | 레슨 |
| 사교원 위키 `content/메타-기록/핸드오버-2026-09-25-아카데미-실습-프롬프트카드.md` | 이 핸드오버 사본 |

## 약속
- 사용자가 **"이어서 작업하자"** 라고 하면 이 핸드오버의 "미완료" 목록부터 재개
- 사용자가 **"정리해"** 라고 하면: ①핸드오버 ②스킬 ③레슨 ④위키배포 자동 수행

## 위키배포 결과 (정리 루틴 ④, 2026-09-25 14:25 KST)

- 사교원 위키 v4 **ef24aa8** → CI `Deploy Quartz to GitHub Pages` run 36094124094 success → 아티팩트(sitemap 124쪽, 신규 2쪽 포함) → `deka2026/sakyowon-wiki-site` master **4ac301f** = **3단계 완료**
- **4단계(서버 반영) 대기** — 사용자가 서버에서 `bash /opt/sakyowon/src/deploy-www.sh` 실행 필요. 실행 전 라이브 실측: `Last-Modified` 04:16 GMT, sitemap 122, 신규 문서 404
- 확인 URL: https://sakyowon.co.kr/sakyowon-wiki/연대지능아카데미/AI-실습-안내를-프롬프트-카드로-바꾸기 (반영 후 sitemap 124·상태 200이면 완료)
- 스킬 `academy-site-deploy`는 `C:\Users\User\.claude\skills\`에 복사·활성화 완료. 메모리(`project-sakyowon-resume`, `project-academy-site-practice-menu`) 현행화
- **4단계 완료(2026-09-25 14:31 KST 사용자 실행)** — 라이브 실측 `Last-Modified` 04:31:17 GMT, sitemap **124**, 레슨·핸드오버 문서 모두 **200**. 위키 배포 대기 0건
