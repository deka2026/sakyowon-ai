---
name: server-runtime-upgrade
description: 여러 서비스가 함께 도는 서버에서 런타임(Node·Python 등)을 기존 서비스를 깨지 않고 올리는 스킬. "서버 노드 버전 올려줘", "EBADENGINE 뜨는데 업그레이드해줘", "이 서버 파이썬 버전 올려도 되나" 같은 요청에 사용. 시스템 런타임을 교체하지 않고 버전 매니저로 병행 설치하는 것이 기본 선택이며, 판단 근거는 systemd 유닛 파일이다.
---

# 서버 런타임 업그레이드 (서비스를 깨지 않고)

## 0. 전제 — 나는 서버에 직접 붙지 못할 수 있다

`~/.ssh`에 키가 없으면 접속에 비밀번호가 필요하고, 비밀번호 입력은 대신하지 않는다. **명령을 만들어 주고 사용자가 SSH 창에서 실행**하는 방식으로 진행한다. 확인 결과를 받아 다음 단계를 정한다.

```bash
ls ~/.ssh/            # known_hosts만 있으면 키 인증 불가
```

## 1. 먼저 "무엇이 그 런타임을 쓰는가"를 센다

버전을 올리기 전에 **의존하는 서비스 목록**을 만든다. 이게 이 스킬의 전부라고 해도 된다.

```bash
ps -eo user,args | grep -i "node\|pm2\|python\|uvicorn" | grep -v grep
```

```bash
ls /etc/systemd/system/*.service
```

이름만으로는 알 수 없다. **유닛 파일의 실행 줄을 직접 본다.**

```bash
grep -H "ExecStart\|Environment\|WorkingDirectory" /etc/systemd/system/<유닛1>.service /etc/systemd/system/<유닛2>.service
```

판정 기준:

| ExecStart 형태 | 의미 | 버전 매니저 영향 |
|---|---|---|
| `/opt/app/.venv/bin/uvicorn ...` | Python venv — Node와 무관 | 없음 |
| `/usr/bin/node app.js` | 시스템 Node 절대경로 | 없음 |
| `/usr/bin/npm run start` | 시스템 npm → 시스템 Node | 없음 |
| `node app.js` (상대) | systemd 기본 PATH(`/usr/bin`) | 없음 |
| **pm2 / 로그인 셸에서 수동 기동** | 셸 환경을 탄다 | **있음** ← 주의 |

**systemd는 `~/.bashrc`를 읽지 않는다.** 그래서 systemd로 도는 서비스는 사용자 셸에 버전 매니저를 깔아도 영향받지 않는다. 위험한 것은 pm2나 `nohup`으로 로그인 셸에서 띄운 프로세스뿐이다 — 나중에 재시작할 때 새 버전을 물 수 있다.

## 2. 방식을 사용자에게 고르게 한다

임의로 정하지 말 것. 선택지와 권장안을 제시한다.

| 방식 | 언제 | 위험 |
|---|---|---|
| **버전 매니저 병행(권장)** | 새 버전이 특정 도구 하나에만 필요할 때 | 거의 없음. 되돌리기는 디렉터리 삭제 |
| 시스템 패키지 업그레이드 | 서버 전체를 새 버전으로 통일하고 싶을 때 | 모든 의존 서비스 재시작·재검증 필요 |
| 그 도구를 제거 | 애초에 불필요하게 설치된 경우 | 없음 — 가장 간단 |

## 3. nvm 병행 설치 절차 (Node 기준)

순서가 중요하다. **시스템 npm의 전역 패키지를 먼저 정리**해야 나중에 어느 쪽 것인지 헷갈리지 않는다.

```bash
npm rm -g <패키지>
```

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/master/install.sh | bash
```

```bash
export NVM_DIR="$HOME/.nvm"; . "$NVM_DIR/nvm.sh"
```

```bash
nvm install 22 && nvm alias default 22
```

```bash
npm install -g <패키지>@latest
```

`nvm alias default`는 **1단계에서 pm2나 수동 기동 프로세스가 나왔다면 건너뛴다.** 대신 쓸 때마다 `nvm use 22`.

## 4. 검증 — 새 것이 됐는가보다 "옛 것이 그대로인가"

```bash
node -v; which node; <도구> --version; /usr/bin/node -v; /usr/bin/npm -v
```

- `which node`가 `~/.nvm/versions/...` → 새 런타임 적용됨
- **`/usr/bin/node -v`가 작업 전과 동일** ← 진짜 확인점. 이게 그대로여야 기존 서비스가 무사하다

서비스 상태와 외부 응답도 같이 본다.

```bash
systemctl is-active <유닛1> <유닛2>
```

```bash
curl -sS -o /dev/null -w "%{http_code}\n" "https://<서비스 URL>"
```

## 5. 되돌리기 경로를 미리 알려둔다

nvm: `rm -rf ~/.nvm` + `~/.bashrc`의 nvm 3줄 삭제. 시스템 런타임은 처음부터 손대지 않았으므로 그걸로 끝이다. **이 문장을 작업 전에 사용자에게 말해두면 결정이 쉬워진다.**

## 함정

1. **어느 기계인지 확인시킬 것.** 사용자가 윈도우용 명령을 SSH 창에, 서버용 명령을 로컬 PowerShell에 넣는 일이 반복된다. 프롬프트로 구분해 안내한다 — `root@서버:~#`는 서버, `PS D:\...>`는 로컬. `Get-Process: command not found`가 그 증상이다.
2. **`EBADENGINE`은 경고지 차단이 아니다.** npm은 그냥 설치하고 넘어가므로, 설치 성공 메시지만 보고 "됐다"고 판단하면 안 된다. 런타임 버전을 따로 확인한다.
3. **앱 내장 터미널에서 전역 설치 금지** — 앱이 켜져 있으면 실행 파일이 잠기고, 앱을 끄면 터미널도 닫힌다.
4. 유닛 파일 이름으로 언어를 짐작하지 말 것. `sakyowon-api`는 이름과 달리 Python(uvicorn)이었다.
