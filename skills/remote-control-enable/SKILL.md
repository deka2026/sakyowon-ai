---
name: remote-control-enable
description: 다른 단말기(폰·다른 PC·claude.ai/code)에서 로컬 Claude Code 세션을 이어받는 원격제어(Remote Control)가 연결됐는지 진단하고, 막혔을 때 원인을 순서대로 좁혀 활성화하는 스킬. "다른 단말기와 연동됐는지 확인해봐", "원격제어 켜줘", "폰에서 이어서 하고 싶어" 같은 요청에 사용. 조직 정책 오류의 진짜 원인이 대개 앱 캐시라는 점이 핵심.
---

# 원격제어(다른 단말기 연동) 진단·활성화

## 1단계: 지금 연동돼 있는가

```
ListAgents                          # 피어 세션 목록
get_session(session_id="self")      # remoteControlState 확인
list_sessions(limit=20)             # 전체 세션의 isRemote / remoteControlActive
```

판정 기준:

| 신호 | 의미 |
|---|---|
| `remoteControlState: "on"` | 연동됨 |
| `"off"` / `"connecting"` / `"unavailable"` | 미연동 |
| 세션 id가 `local_*`, `isRemote: false` | **같은 PC**의 세션 |

**가장 흔한 오해**: `ListAgents`에 잡히는 피어 세션들은 다른 기기가 아니다. 전부 같은 PC에서 도는 세션이고, "Claude Desktop session" 라벨도 마찬가지다. 다른 기기가 붙으면 `remoteControlActive: true`로 나타난다. 이 구분을 먼저 설명하지 않으면 "연동돼 있다"는 오답을 준다.

## 2단계: 켜기

```
set_remote_control(session_id="self", enabled=true)
```

**반드시 사용자가 요청했을 때만.** 세션을 claude.ai 계정으로 내보내는 동작이라 사전 확인을 받는다.

## 3단계: "disabled by your organization's policy" 오류 좁히기

문서: https://code.claude.com/docs/en/remote-control (troubleshooting 절)

아래 순서로 배제한다. **위에서부터 확인하되, 대부분의 실전 사례는 5번이다.**

| # | 원인 | 확인 방법 | 조치 |
|---|---|---|---|
| 1 | 기기 관리형 설정 | 오류 문구에 `disableRemoteControl`이 나오는가 | IT 관리자가 기기 단위로 막은 것 — 조직 토글과 무관 |
| 2 | 비-Anthropic 엔드포인트 | `ANTHROPIC_BASE_URL`, `CLAUDE_CODE_USE_BEDROCK`, `CLAUDE_CODE_USE_VERTEX` | 해당 변수 해제 후 세션 재시작 |
| 3 | HIPAA 비호환 | 오류에 "관리자에게 문의" 문구가 **없다** | 관리자도 못 켬. Anthropic 지원 문의 |
| 4 | 조직 토글 off | `claude.ai/admin-settings/claude-code` | **Owner**가 **원격 제어** 토글 ON (전제: **클라우드 세션**도 ON) |
| 5 | **앱이 낡은 정책을 캐시** | 아래 참조 | **앱 완전 재시작** |

### 5번이 핵심 — 앱 기동 시각을 본다

조직 정책은 **앱이 시작할 때만** 로드된다. 토글을 켜도 이미 떠 있는 앱은 예전 정책(off)을 그대로 물고 있어 계속 같은 오류를 낸다.

```powershell
Get-Process -Name "claude" -ErrorAction SilentlyContinue |
  Sort-Object StartTime | Select-Object -First 1 StartTime
```

**앱 기동 시각 < 토글 변경 시각**이면 그것이 원인이다. 추가 진단을 멈추고 재시작을 안내한다:

1. 창 X 버튼만으로는 부족 — **트레이 아이콘 우클릭 → 종료**까지
2. 앱 재실행 → 사이드바에서 같은 대화를 다시 열기
3. `set_remote_control` 재시도

2026-09-18 사례: 토글 ON 확인 후에도 3회 실패했고, 업데이트·재로그인을 의심했으나 실제 원인은 전부 이것이었다. 재시작 직후 `{"remoteControlState":"on"}`.

## 하지 않아도 되는 것들

- **Claude Code 업데이트**: 2.1.218에서도 정상 동작했다. 단 `claude doctor`의 `Organization policy` 진단 줄은 2.1.261+에서만 나오므로, 원인이 끝내 안 잡힐 때만 업데이트 카드를 꺼낸다.
- **재로그인**: `claude doctor`가 "Sign-in is missing the `user:profile` scope"를 보고해도, 그건 **CLI 자격 저장소**를 본 결과일 뿐 데스크톱 앱의 토큰과 별개다. 이것만 보고 재로그인시키지 말 것.

## 함정

1. **명령을 어느 기계에 입력하는지 확인시킬 것.** 사용자가 SSH 창(`root@sakyowon-server:~#`)에 윈도우 명령을 넣는 일이 반복된다. `Get-Process: command not found`가 그 증상이다. 프롬프트로 구분해 안내한다 — `root@...`는 리눅스 서버, `PS D:\...`는 이 PC.
2. **앱 안의 터미널 패널에서 npm 전역 설치를 하지 말 것.** 앱을 끄면 패널도 닫히고, 앱이 켜져 있으면 `claude.exe`가 잠겨 설치가 깨진다. 앱 바깥 PowerShell을 쓰게 한다.
3. **서버에서 업그레이드할 때 Node 버전 확인.** claude 2.1.276은 Node >=22 요구. Node 20이면 `EBADENGINE` 경고만 뜨고 설치는 되지만 오작동한다.
4. 관리자 화면에서 토글이 **새로고침 후에도 유지되는지** 확인시킬 것. 되돌아가면 Owner 권한이 아니다.

## 성공 후 안내

- 접속: `claude.ai/code` 또는 Claude 모바일 앱. 주소는 앱의 Remote Control 배지에서 확인
- 세션은 계속 로컬 PC에서 실행 — 로컬 파일·MCP·한글 COM 그대로. **PC가 켜져 있어야 함**
- 매 세션 자동 연결: `~/.claude/settings.json`에 `"remoteControlAtStartup": true`
- 조직이 **Require trusted devices**를 켰다면 기기 등록 필요 — Claude Code에서 `/login`
