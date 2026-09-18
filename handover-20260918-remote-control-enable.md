# 핸드오버: 다른 단말기 연동(Remote Control) 진단·활성화

**날짜**: 2026-09-18
**이전 핸드오버**: handover-20260918-deka-team-and-paran-survey.md
**작업 폴더**: (설정 작업 — 산출 문서 없음)

---

## 수행한 작업

### 1. 연동 여부 진단
- `ListAgents` + `get_session`의 `remoteControlState`로 확인 → `off`
- 세션 목록 20건 전부 `local_*` / `isRemote: false` / `remoteControlActive: false`
- **핵심 오해 지점**: 피어로 잡히는 세션들(`에이전트 역할 구분`, `AI 업무 환경 체계도 PPT` 등)은 전부 **같은 PC의 세션**이지 다른 기기가 아니다. "Claude Desktop session" 라벨도 같은 PC를 뜻한다.

### 2. 원인 축소
`set_remote_control(self, true)` 3회 시도 모두 `Remote Control is disabled by your organization's policy`. 공식 문서(code.claude.com/docs/en/remote-control)의 원인 목록을 순서대로 배제:

| 원인 후보 | 판정 | 근거 |
|---|---|---|
| `disableRemoteControl` (기기 관리형 설정) | 아님 | 오류 문구에 키 이름 미언급 |
| Bedrock/Vertex/프록시 경유 | 아님 | `ANTHROPIC_BASE_URL=https://api.anthropic.com`, Bedrock·Vertex unset |
| HIPAA 비호환 | 아님 | "관리자에게 문의" 문구가 붙으면 HIPAA 케이스가 아님 |
| Owner 미설정 | **해당** | 조직 토글이 기본 off 상태였음 |

### 3. 관리자 설정 안내
- 위치: `https://claude.ai/admin-settings/claude-code` → **원격 제어** 토글
- **Owner 권한만** 변경 가능, Team·Enterprise는 **기본 off**
- 전제 조건: 같은 화면의 **클라우드 세션**이 켜져 있어야 함 (이미 켜져 있었음)
- 사용자가 토글 ON, 새로고침 후 유지되는 것까지 확인 (= Owner 권한 정상)

### 4. 재시작이 진짜 원인이었음
토글을 켠 뒤에도 2회 더 실패. `Get-Process claude | Sort StartTime`으로 앱 기동 시각을 확인:

- 앱 본체 기동: **14:48:50**
- 토글 ON 시점: 약 **15:10**
- → 앱이 토글 OFF 시절의 조직 정책을 캐시한 채 돌고 있었음

**조직 정책은 앱 시작 시점에만 로드된다.** 사용자가 앱을 완전 종료 후 재시작(**15:32:53**)하자 즉시 성공:

```json
{"sessionId":"local_d1ba00ab-...","remoteControlState":"on"}
```

Claude Code 업데이트도, 재로그인도 필요 없었다 (버전 2.1.218 그대로).

### 5. 곁가지: 서버에 잘못 설치된 업데이트
사용자가 업데이트 명령을 **SSH로 접속한 `root@sakyowon-server`** 에 입력해 서버 쪽만 2.1.276으로 올라갔다. 그 서버는 **Node v20.20.2**라 `EBADENGINE`(요구 `>=22.0.0`) 경고 발생 — 설치는 됐으나 오작동 가능.
이 PC는 Node v24.18.0 / Claude Code 2.1.218로 변동 없음.
사용자가 터미널 명령을 받으면 SSH 창에 입력하는 일이 잦으므로, **프롬프트(`root@...` vs `PS D:\...`)로 어느 기계인지 명시**해 안내할 것.

---

## 미완료 / 다음 할 일

- [ ] `sakyowon-server`의 Node를 22 이상으로 올리기 — 현재 claude 2.1.276이 미지원 엔진에서 돌고 있음
- [ ] 모든 세션 자동 연결을 원하면 `~/.claude/settings.json`에 `"remoteControlAtStartup": true` 추가 (사용자 확정 대기)
- [ ] (이월) 사교원 위키 레슨 여러 건 **서버 반영(SSH) 대기** — 4단계 `bash /opt/sakyowon/src/deploy-www.sh`
- [ ] (이월) "300백만원" 해석 확인 대기

---

## 파일 위치

| 경로 | 내용 |
|---|---|
| `sakyowon-ai/handover-20260918-remote-control-enable.md` | 이 문서 |
| `sakyowon-ai/skills/remote-control-enable/SKILL.md` | 진단·활성화 스킬 |
| `sakyowon-wiki/content/연대지능/설정은-켰는데-왜-안-되나-캐시된-정책과-앱-재시작.md` | 레슨 |
| `~/.claude/projects/D----------/memory/project-remote-control-blocked.md` | 메모리 |

---

---

## 위키배포 결과 (2026-09-18 15:44)

| 단계 | 내용 | 결과 |
|---|---|---|
| 1 | `deka2026/sakyowon-wiki` **v4** `content/연대지능/` 커밋·push | ✅ `a6705a3` |
| 2 | CI `Deploy Quartz to GitHub Pages` | ✅ 런 `35315838201` (build·deploy 모두 success), 아티팩트 `10534970971`, sitemap **107건** |
| 3 | 아티팩트를 `sakyowon-wiki-site` master에 반영 | ✅ `80304de` (202파일 변경, 내 문서 포함 확인) |
| 4 | 서버에서 `bash /opt/sakyowon/src/deploy-www.sh` | ⏳ **대기** — 편지 `9ecc38e` |

**3단계까지 완료, 서버 반영 대기.** 라이브 확인(셸):

```
Last-Modified: Fri, 18 Sep 2026 05:33:51 GMT   (= 14:33 KST)
sitemap <loc> 105건
내 문서 404
```

**부수 확인**: 라이브 `Last-Modified`가 **오늘 14:33**이고 sitemap이 103 → **105**로 올랐다. 9/16~9/18에 쌓여 있던 대기분 일부가 그 시각에 이미 반영된 것으로 보인다. 이 문서는 그 이후(15:39) push라 다음 반영에 포함된다.

**CI 아티팩트 요령(재확인)**: 이번에는 `gh run download` 대신 **build 잡 완료를 폴링하다가 끝나는 즉시** `gh api repos/.../actions/artifacts/<id>/zip`으로 받았고, deploy 성공 후에도 아티팩트가 목록에 남아 있어 rerun 없이 3단계를 마쳤다. 로컬 Quartz 빌드 불필요.

---

## 약속

- 사용자가 **"이어서 작업하자"** 라고 하면 이 핸드오버의 "미완료" 목록부터 재개
- 사용자가 **"정리해"** 라고 하면: ①핸드오버 ②스킬 ③레슨 ④위키배포 자동 수행
