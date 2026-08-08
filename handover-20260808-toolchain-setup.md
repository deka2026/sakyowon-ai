# 핸드오버: 신 PC 도구체인 정비 + "정리해" 루틴 스킬화

**날짜**: 2026-08-08 (같은 날 2번째 핸드오버)
**이전 핸드오버**: handover-20260808-jeonnam-megaproject-crosscheck.md

---

## 수행한 작업

### 1. "왜 이 PC에서 느린가" 진단
- 원인은 기기 성능이 아니라 **도구 공백**: 구 PC에 있던 Python·gh·pandoc·poppler가 신 PC에 없어 매 작업마다 PowerShell 우회로를 즉석 개발했음
- 부차 원인: PS 5.1 함정(한국어 인코딩, credential fill 파이프 불가), 일회성 복구 비용(위키 재클론, 낡은 커밋 정리, HWPX 방법 확립)

### 2. 도구 4종 설치 (winget, 전부 성공)
- Python 3.12.10 / GitHub CLI 2.97.0 / pandoc 3.10.1 / Poppler 25.07.0
- 주의: winget 설치 직후 현재 셸엔 PATH 미반영 — `$env:Path = [Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [Environment]::GetEnvironmentVariable('Path','User')` 한 줄로 갱신. Claude Code 재시작 후엔 자동
- **gh 인증 완료**: 디바이스 플로우(Start-Process로 gh를 백그라운드 기동해 일회용 코드 캡처 → 사용자가 브라우저 승인) → deka2026, keyring, repo 스코프

### 3. "정리해" 루틴 스킬화
- `skills/jeongrihae-routine/SKILL.md` 신설 (커밋 `1e28aa4`) + `~/.claude/skills/` 활성화
- 4단계 절차 전체 + 핸드오버/레슨 템플릿 + 함정 모음(사이트 레포 fetch 필수, UTF-8 절대경로, credential fill cmd 경유 등) 수록
- 이번 정리해부터 이 스킬 절차대로 실행 중 (첫 실사용)

### 4. 레슨 + 위키배포 (이번 정리해 ③④)
- 레슨: 「AI 작업환경 정비 — 내 AI가 느린 이유, 도구 공백 진단과 해결」 (실천기술, author=김일영, 정리=데카)
- **PR #11 생성·머지 완료** (gh CLI 정식 경로 — 지난번 REST 우회 대비 즉시 처리됨. 스킬화 효과 실증)
- 편지함에 PR #10·#11 라이브 반영 요청 push (커밋 `b5c7bb4`)
- jeongrihae-routine 스킬 갱신: gh 인증 완료 상태 + 디바이스 코드 비대화식 발급 요령 추가

## 미완료 / 다음 할 일

- [ ] **위키 라이브 확인 대기 ×2**: PR #10(교차검증 레슨)은 8/8 15시 기준 여전히 404 — 편지함 배포 요청(5217003)에 지미 회신 아직 없음. 이번 레슨 PR도 동일하게 대기 예상
- [ ] (이월) 전남광주 수정 HWPX 한글 육안 확인 + DOCX 반영 여부 사용자 확인
- [ ] (이월) 편지함 8/8 존 이전(2안) 흐름 — 지미 회신 확인
- [ ] (이월) 유실 문의 구출, sakyowon-mailbox-watch 재설치 여부

## 파일 위치

| 경로 | 내용 |
|---|---|
| `C:\Users\User\sakyowon-ai\skills\jeongrihae-routine\` | 정리해 루틴 스킬 (원본) |
| `C:\Users\User\sakyowon-ai\skills\hwpx-powershell-edit\` | HWPX 편집 스킬 (오전 제작) |
| `C:\Users\User\.claude\skills\` | 두 스킬의 활성 사본 |
| `C:\Users\User\solidarity-intelligence-wiki-haeory\문서\실천기술\` | 레슨 2편 (교차검증, 환경정비) |
| 설치 도구 | python/gh/pandoc/pdftoppm — 새 셸은 PATH 갱신 필요 |

## 약속

- 사용자가 **"이어서 작업하자"** 라고 하면 이 핸드오버의 "미완료" 목록부터 재개
- 사용자가 **"정리해"** 라고 하면: 스킬 `jeongrihae-routine` 절차대로 ①핸드오버 ②스킬 ③레슨 ④위키배포 자동 수행
