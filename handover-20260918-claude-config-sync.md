# 핸드오버 2026-09-18 — 단말기 간 Claude 기억·설정 연동

## 세션 개요

"이 단말기와 다른 단말기를 연동해서 사용하려면?" 에서 출발해, Windows PC와 사교원 운영서버 사이에
Claude Code의 기억·설정을 양방향으로 동기화하는 체계를 구축하고 실제 동작까지 검증했다.

## 최종 구조

```
Windows PC (DESKTOP-IBKE51N, C:\Users\Admin)        ← 기억을 만드는 쪽
   │  sync-push.sh  (full 모드: 기억+설정+권한목록+스킬+스케줄작업)
   ▼
deka2026/claude-config  (private)                   ← 본 레포
   │  sync-pull.sh  (memory-only 모드)
   ▼
sakyowon-server (가비아 운영서버, root, /root)       ← 받아 쓰는 쪽
   │  server-memory-push.sh
   ▼
deka2026/claude-memory-server  (private)            ← 수신함
   │  review-server-memory.sh  (list/show/diff/merge)
   ▼
Windows PC  (확인 후 골라서 병합)
```

## 레포 2개와 권한 분리

| 레포 | 서버 권한 | 배포키 id |
|---|---|---|
| `deka2026/claude-config` (본 기억·설정) | **읽기 전용** | 163676155 |
| `deka2026/claude-memory-server` (수신함) | 쓰기 | 163686244 |

레포를 나눈 이유: GitHub 배포 키는 폴더 단위 권한을 줄 수 없다. 같은 레포에 쓰기를 주면
서버가 본 기억을 직접 고칠 수 있고, 공개 웹서버가 침해되면 기억 오염 → PC의 Claude가
그 지시문을 읽음 → 사전 승인된 명령 347개로 실행, 이라는 경로가 생긴다.
레포를 나누면 GitHub가 접근 자체를 막아준다.

## 스크립트 (모두 `~/claude-config/`)

| 스크립트 | 실행 위치 | 하는 일 |
|---|---|---|
| `sync-push.sh` | PC | `~/.claude` → 레포 커밋·푸시 |
| `sync-pull.sh` | PC·서버 | 레포 → `~/.claude` 복원 (백업 후 덮어씀) |
| `server-memory-push.sh` | 서버 | 서버 기억 → 수신함 |
| `review-server-memory.sh` | PC | 수신함 확인·병합 (list/show/diff/merge) |

### 동작 모드
- `full` (기본): 기억 + settings + 권한목록 + 스킬 + 스케줄작업
- `memory-only`: 기억 + 에이전트 + 직접 만든 스킬만. settings·권한목록·스케줄작업·외부스킬 제외
- 전환: `~/.claude-sync-mode` 파일에 `memory-only` 또는 `full`, 혹은 `--memory-only` 플래그
- 내용 해석 실패 시 **조용히 full 로 가지 않고 중단**한다 (안전한 쪽이 기본값이 아니므로)

## 동기화 대상

**담는 것** — 기억 48개(`memory/C--Users-Admin/`) + Desktop 기억 8개, `agents/alpha.md`,
직접 만든 스킬 `hwp-analyze`·`hwp-fill`·`hwp-template`, `scheduled-tasks/*/SKILL.md`,
`settings.json`, `settings.local.json`(권한 347개 — 자격증명 포함 9건 제외)

**안 담는 것** — `.credentials.json`, 대화기록 76MB, `cache`/`sessions`/`plugins`/`shell-snapshots`,
`state.json`(머신별), 외부 clone 스킬 `kordoc`·`easy-hwp`(→ `external-skills.txt`)

## 자동 백업 이중화

| 경로 | 시각 | 조건 |
|---|---|---|
| Claude 스케줄 작업 `claude-config-daily-push` | 22:37 | Claude 앱이 열려 있을 때 |
| Windows 작업 스케줄러 `ClaudeConfigDailyPush` | 23:30 | 앱과 무관. 놓치면 다음 부팅 시 보충 |

Windows 작업 등록 XML: `~/claude-config/scripts/windows-task.xml`
로그: `C:\Users\Admin\claude-config-sync.log` (실행당 7줄)

## 서버 설정 요약

- Claude Code v2.1.197 (npm 전역), `claude auth login` 으로 인증 완료
- SSH 별칭 2개: `github-claudeconfig`(읽기), `github-claudememory`(쓰기)
- 기억 위치: `~/.claude/projects/-root/memory/` — **홈에서 `claude` 실행해야 잡힘**
- 권한 허용목록 없음 → 모든 명령이 승인 대기 (운영 서버라 의도한 것)

## 해결한 문제들

1. **Linux 폴더명 변환 버그** — 슬러그 계산이 `/`를 변환하지 않아 `/root`가 그대로 남았다.
   정답은 `-root`. `sed 's,[:\/],-,g'` 로 수정. Windows 는 영향 없음
2. **모드 마커 조용한 폴백** — 마커를 못 읽으면 full 로 돌아가 서버에 권한목록이 심길 뻔했다.
   해석 실패 시 중단하도록 변경
3. **백업이 skills/ 오염** — `hwp-analyze.bak-.../SKILL.md` 가 중복 스킬로 등록될 수 있었다.
   백업을 `~/.claude/.sync-backups/<시각>/` 로 분리
4. **줄바꿈 오판** — PC는 CRLF, 레포는 LF라 47개 중 46개를 "변경됨"으로 표시했다.
   `diff --strip-trailing-cr` 로 수정
5. **로그 한글 깨짐·CRLF 경고** — `PYTHONIOENCODING=utf-8`, `core.safecrlf false`

## 막힌 것

- **Remote Control 불가** — 조직 정책으로 차단됨. 조직 관리자만 해제 가능.
  휴대폰·claude.ai 에서 데스크톱 세션을 따라보는 기능은 못 쓴다
- **`schtasks /create` 자동 승인 거부** — "무단 지속성"으로 분류되어 세션이 실행할 수 없었다.
  XML 을 만들어 두고 데카가 PowerShell 에서 직접 등록함

## 운영 규칙

1. **기억은 PC에서 만든다.** 서버는 받기만 한다 (배포키가 읽기 전용이라 구조적으로 강제됨)
2. **작업 전 pull, 끝나면 push.** 두 기계가 같은 파일을 고치면 충돌한다
3. **수신함 merge 전 반드시 diff 확인.** 이 도구는 "다르다"만 알려주고 "어느 쪽이 최신인지"는
   모른다. 서버 것이 오래됐는데 합치면 최신 기억이 되돌아간다
4. **서버에서는 `cd ~ && claude`** 로 홈에서 띄운다
5. 레포 2개 모두 **영구 private** — 서버 IP·관리자 계정·사업 메모 포함

## 명령어 트리거

데카가 **"다른 기기와 연동해"** 라고 하면 수신함 확인 → 내용 요약 → (확인 후) 병합 →
본 레포 반영 → 서버용 명령 안내까지 수행한다. 병합만은 자동화하지 않는다.
기억 파일: `feedback-sync-devices-command.md`

## 위키 배포 (2026-09-18~19)

이 세션 내용을 위키 메타-기록에 올렸다. **위키 미러는 public** 이라 서버 주소·호스트명·
배포키 id·레포명을 모두 빼고 재사용 가능한 방법론으로만 정리했다(푸시 전 grep 재확인).
상세 기록은 private 인 이 문서에 둔다.

| 단계 | 상태 |
|---|---|
| ① `sakyowon-wiki` `v4` 푸시 | 완료 `13bac1f0` |
| ② Quartz 빌드 → 미러 `sakyowon-wiki-site` 푸시 | 완료 `aae0fa5` (신규 2 · 수정 315 · 삭제 0) |
| ③ 가비아 서버 `bash /opt/sakyowon/src/deploy-www.sh` | **미실행 — 라이브 404** |

빌드: Quartz v4.5.2, 109문서 → 373파일, 29초.
미러 반영 방법: 로컬 클론에서 `.git` 외 전부 삭제 후 `public/` 통째 복사 → commit → push.
사전에 CNAME·숨김 설정파일이 없음을 확인해야 안전하다(이번엔 없었다).
미러 레포는 Pages 가 꺼져 있어 `gh api .../pages` 가 404 를 준다. 정상이며, 실서빙은 가비아가 한다.

## 아카데미 교육자료화 (2026-09-19)

같은 내용을 **연대지능활동가 아카데미 교육자료**로 다시 써서 위키에 올렸다.
메타-기록(세션 기록)과 달리 교육생 대상이라, 기존 아카데미 문서 형식
(서문 blockquote → 전체 그림 → 단계별 소요시간 → ⚠️/🔴 경고 → 함정 요약 → 서명)을 따랐다.

`content/연대지능아카데미/여러-기기에서-AI와-같은-기억으로-일하기.md` (305줄)

교육 포인트로 뽑은 것은 기술 절차보다 **판단 기준** 쪽이다:
올리면 안 되는 것 가르기 / 운영 서버를 다르게 다루는 이유 / 기억은 데이터가 아니라 지시문 /
저장소를 나눠 경계를 권한으로 강제 / 확인·병합은 자동화하지 않기 / 실패는 조용히 하지 않기.
마지막은 AI 도구를 넘어 공동 문서함·회계·회원명부에도 같은 질문("누가 무엇을 바꿀 수 있는가")이
적용된다는 것으로 닫았다.

| 단계 | 상태 |
|---|---|
| ① `v4` 푸시 | 완료 `ead557a2` |
| ② 미러 푸시 | 완료 `5071273` (신규 3 · 수정 319 · 삭제 0) |
| ③ `deploy-www.sh` | **미실행** |

### 이번에 피한 사고

`git pull --rebase` 로 다른 사람 커밋 3건(GPU 지원사업 문서 등)이 들어왔는데,
빌드 산출물은 그 전 상태였다. 미러는 `.git` 외 전부 지우고 통째 교체하는 방식이라
**그대로 밀었으면 그 문서들이 삭제**됐다. `public/` 에 GPU 문서 본문이 없는 것을 보고 발견.

**순서는 `pull → 빌드 → 미러 교체`** 이고, 푸시 전에 반드시 확인한다:

```bash
git status --porcelain | grep "^D " || echo "삭제 없음"
```

## 관련 기억

`reference-config-sync.md`, `feedback-sync-devices-command.md`,
`lesson-deploy-verify-commit.md`(PowerShell 5.1 함정 추가),
`reference-claude-code-managed-settings.md`(Remote Control 차단 추가)
