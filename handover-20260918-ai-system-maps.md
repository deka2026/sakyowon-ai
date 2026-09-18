# 핸드오버: AI 업무 체계도 · 하네스 구조도 한 장짜리 PPT 2종

**날짜**: 2026-09-18
**이전 핸드오버**: handover-20260916-mangnam-budget-execution-hancell.md (최근 커밋 기준 2026-09-17 정리분)
**작업 폴더**: `D:\사교원 개발그룹\`

---

## 수행한 작업

### 1. AI 업무 체계도 (1장)

구축한 AI 업무 환경과 그 결과물을 한 장으로 보여주는 PPT.

- 산출: `D:\사교원 개발그룹\AI업무체계도_20260918.pptx` (16:9, 맑은 고딕)
- 구성 4단: **① 작업 환경 → ② 자동화 엔진(스킬 20종을 5계열로) → ③ 산출물(4계열) → ④ 축적 루프**
- ③ 산출물은 메모리의 project-*.md 18건을 근거로 정책·계획 문서 / 운영 시스템 / 교육·미디어 / 지식 자산으로 묶음

### 2. AI 하네스 구조도 (1장)

모델을 업무에 연결하는 실행 뼈대(하네스) 자체를 그린 PPT.

- 산출: `D:\사교원 개발그룹\AI하네스구조도_20260918.pptx`
- 구성 5층: **① 지시 주입 → ② 런타임 → ③ 도구 계층 → ④ 확장 계층 → ⑤ 산출 경로**
- 왼쪽 1.42" 라벨 열 + 오른쪽 칩/카드 격자 레이아웃 (층마다 제목 줄을 따로 두지 않아 세로 1.7" 절약)

### 3. 수치는 전부 파일을 세어서 넣었다

말로 기억한 값을 쓰지 않고 실제 설정을 읽었다.

| 항목 | 값 | 근거 |
|---|---|---|
| 스킬 | 20종 | `~/.claude/skills` 폴더 수 (이번에 추가한 것 제외) |
| 기억(메모리) | 30건 | `memory/*.md` 31개 − MEMORY.md |
| 진행 프로젝트 | 18건 | `memory/project-*.md` |
| 서브에이전트 | 5명 | `~/.claude/agents/` — 파랑·보라·알파·베타·**알파언니** |
| 플러그인 | 39종 | `plugins/marketplaces/claude-plugins-official/plugins` |
| 스킬 사용 1위 | hwpx-powershell-edit 19회 · jeongrihae-routine 19회 | `~/.claude.json`의 `skillUsage` |
| 예약 작업 | **0건(미사용)** | scheduled-tasks MCP 조회 |

미사용·인증 대기 항목(플러그인 다수, 커넥터, 예약 작업)은 감추지 않고 "미사용 / 인증 전 대기"로 명시했다.

### 4. 세션 중 팀 구성이 4명 → 5명으로 바뀐 것을 반영

하네스 구조도를 먼저 4명으로 만든 뒤 알파언니(검증 담당)가 추가되어, 헤더 수치와 확장 계층 카드를 5명으로 고쳐 재생성·재렌더했다.

### 5. 스킬화

`pptx-onepage-diagram` 신규 제작 (아래 "파일 위치" 참조). 스모크 테스트로 `examples/build_harness_map.py`를
라이브러리 경유로 실행해 실제 산출물과 같은 레이아웃이 나오는 것을 PNG로 확인했다.

## 미완료 / 다음 할 일

- [ ] 체계도 ②단 문구가 스킬 이름 위주라 대외 발표용으로는 기술적 — 대외용이 필요하면 "한글 문서 자동 작성·교정" 식으로 풀어쓴 판을 별도 생성
- [ ] 산출물 카드는 메모리에 남은 프로젝트 기준 — 빠진 결과물이 있으면 사용자 확인 후 추가
- [ ] (이월) 사교원 위키 **서버 반영(SSH)** — 4단계 `bash /opt/sakyowon/src/deploy-www.sh` 미실행분 누적
- [ ] (이월) "300백만원" 표기 해석 사용자 확인
- [ ] 예약 작업 0건 — 주간 리포트 등 무인 실행 후보 정리

## 파일 위치

| 경로 | 내용 |
|---|---|
| `D:\사교원 개발그룹\AI업무체계도_20260918.pptx` | 업무 체계도 1장 |
| `D:\사교원 개발그룹\AI하네스구조도_20260918.pptx` | 하네스 구조도 1장 |
| `D:\사교원 개발그룹\build_ai_system_map.py` | 체계도 생성 스크립트(단독 실행) |
| `D:\사교원 개발그룹\build_harness_map.py` | 하네스 구조도 생성 스크립트(단독 실행) |
| `C:\Users\User\sakyowon-ai\skills\pptx-onepage-diagram\` | 신규 스킬 (SKILL.md · scripts/onepage_lib.py · examples 2종) |
| `C:\Users\User\.claude\skills\pptx-onepage-diagram\` | 활성 사본 |
| `C:\Users\User\sakyowon-wiki\content\연대지능\AI로-내-작업환경을-한-장-체계도로-그리기.md` | 레슨 |

## 약속

- 사용자가 **"이어서 작업하자"** 라고 하면 이 핸드오버의 "미완료" 목록부터 재개
- 사용자가 **"정리해"** 라고 하면: ①핸드오버 ②스킬 ③레슨 ④위키배포 자동 수행

---

## 위키배포 결과 (2026-09-18 추기)

| 단계 | 결과 |
|---|---|
| 1 | `deka2026/sakyowon-wiki` v4 `content/연대지능/AI로-내-작업환경을-한-장-체계도로-그리기.md` — **e2bbcdb** |
| 2 | `Deploy Quartz to GitHub Pages` run **35308991680** 성공(attempt 1 배포 완료, 아티팩트 재확보용 rerun) |
| 3 | `deka2026/sakyowon-wiki-site` master **1ab8ba5** (312 파일 변경, sitemap `<loc>` **105**) |
| 4 | **서버 반영 대기** — `bash /opt/sakyowon/src/deploy-www.sh` (SSH 필요) |

라이브 확인(셸): `Last-Modified: Thu, 17 Sep 2026 01:05:20 GMT` · sitemap **103** · 새 문서 **404**
→ **3단계까지 완료, 4단계 서버 반영 대기.** 9/16~9/18 레슨들이 함께 대기 중이다.

### CI 아티팩트 요령 정정 (스킬 반영)

`gh run download`가 "no valid artifacts found"로 실패했다. Pages 배포가 끝나면 `github-pages` 아티팩트가
목록에서 사라지기 때문이다(배포 자체는 `deployments` API로 성공 확인됨). `gh run rerun` 후 **build 잡이
끝난 직후** `gh api .../actions/artifacts/<id>/zip`으로 받으면 로컬 Quartz 빌드 없이 3단계를 끝낼 수 있다.
→ `jeongrihae-routine` SKILL.md ④-2에 추가.
