---
name: jeongrihae-routine
description: 사용자(김일영/데카)가 "정리해"라고 하면 실행하는 세션 마무리 루틴. ①핸드오버 ②스킬 ③레슨 ④위키배포 4종을 순서대로 자동 수행한다. 요약만 하고 끝내면 안 됨. 마지막에 메모리 현행화까지.
---

# "정리해" 루틴 (세션 마무리 4종 + 메모리)

2026-07-25 사용자 확정, 2026-08-08 전 과정 1회 완주로 검증된 절차. **4종을 모두 수행해야 완료**이며, 각 단계의 완료 정의를 지킬 것.

## 사전 확인 (30초)

```powershell
# 새로 설치된 도구가 PATH에 없으면 세션 셸에서 갱신
$env:Path = [Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [Environment]::GetEnvironmentVariable('Path','User')
```

| 자원 | 경로 | 비고 |
|---|---|---|
| 핸드오버·스킬 레포 | `C:\Users\User\sakyowon-ai` (deka2026, **master**) | push 권한 있음 |
| 공동위키 클론 | `C:\Users\User\solidarity-intelligence-wiki-haeory` (haeory-cyber, main) | deka2026 write 권한 |
| 사이트+편지함 | `C:\Users\User\haeory-sakyowon-site` (haeory-cyber, main) | **반드시 fetch 먼저** — 다른 세션이 활발히 push함 |
| Claude 스킬 활성 폴더 | `C:\Users\User\.claude\skills\` | sakyowon-ai/skills/와 동기화 |

## ① 핸드오버

파일: `C:\Users\User\sakyowon-ai\handover-YYYYMMDD-<주제-영문-kebab>.md`

템플릿 (기존 핸드오버 형식 준수):

```markdown
# 핸드오버: <제목>

**날짜**: YYYY-MM-DD
**이전 핸드오버**: <직전 handover 파일명>
**작업 폴더**: <해당 시>

---

## 수행한 작업
### 1. <작업명>
- 핵심 결과, 커밋 해시, 수치

## 미완료 / 다음 할 일
- [ ] 항목 (이월 항목은 "(이월)" 표시)

## 파일 위치
| 경로 | 내용 |
|---|---|

## 약속
- 사용자가 **"이어서 작업하자"** 라고 하면 이 핸드오버의 "미완료" 목록부터 재개
- 사용자가 **"정리해"** 라고 하면: ①핸드오버 ②스킬 ③레슨 ④위키배포 자동 수행
```

커밋 + push (master). 커밋 메시지는 한국어 제목 + Co-Authored-By 푸터.

## ② 스킬

그 세션에서 확립한 **재사용 가능한 작업 방법**을 스킬 패키지로 제작/갱신:
- 위치: `C:\Users\User\sakyowon-ai\skills\<스킬명-영문>\SKILL.md` (+ scripts/ 등)
- SKILL.md는 frontmatter(name, description)를 갖추고, description은 "언제 쓰는지"가 드러나게
- 같은 내용을 `C:\Users\User\.claude\skills\<스킬명>\`에 복사 (활성화)
- 스크립트가 있으면 **스모크 테스트 1회** 실행 후 커밋
- 세션에 새 방법이 없으면 기존 스킬의 갱신(함정 추가 등)으로 대체 가능 — 단 핸드오버에 사유 기록

주의: .ps1 파일에 한국어 리터럴 금지(PS 5.1 인코딩 깨짐) — 한국어는 데이터 파일이나 SKILL.md에.

## ③ 레슨

AI활동가 교육용 문서 — 그 세션에서 배운 것을 **다른 활동가가 따라할 수 있는 형태**로:
- 위치: 위키 클론의 `문서/실천기술/` (분야 지식이면 `문서/분야지식/`)
- 파일명: 한국어-kebab (예: `AI와-함께-정책문서-교차검증하고-한글문서-자동수정하기.md`)
- frontmatter 규칙 (지미 규칙, 필수):

```markdown
---
title: <제목>
author: 김일영        # ← 지식의 원 기여자. 데카 본인 작업이면 김일영
date: YYYY-MM-DD
tags: [실천기술, ...]
---
```

- 구성: 요약 / 왜 이 기술인가 / 단계별 따라하기 / 교훈 / 참고
- 참고 섹션 끝에 **"문서 정리 = 데카(deka2026)"** 병기 ("공은 사람에게, 노동은 정직하게")
- 개인정보·비밀키 금지 (공개 레포), 타인 저작물은 인용·안내 형식으로

## ④ 위키배포

**완료 정의 = push가 아니라 라이브 반영 확인** (wiki.poomasi.org에서 문서가 열려야 완료).

1. 위키 클론에서 브랜치: `lesson/<주제>-YYYYMMDD`
2. 커밋 (PR 제목 형식: `[문서] 제목`) → `git push -u origin <브랜치>`
3. PR 생성·머지 — gh CLI 사용 (2026-08-08 설치·deka2026 인증 완료, keyring):
   ```powershell
   gh pr create --repo haeory-cyber/solidarity-intelligence-wiki --title "[문서] <제목>" --body "<한두 줄 + author/정리자 표기>"
   gh pr merge <번호> --repo haeory-cyber/solidarity-intelligence-wiki --squash
   ```
   gh 재인증이 필요해지면(비대화식 디바이스 플로우 요령): `Start-Process gh -ArgumentList 'auth','login','--web','--hostname','github.com','--git-protocol','https' -RedirectStandardError $log -NoNewWindow`로 백그라운드 기동 → 로그에서 일회용 코드를 읽어 사용자에게 URL(https://github.com/login/device)과 함께 전달 → 사용자가 브라우저 승인하면 자동 완료.
   gh 부재 시 폴백: GCM 토큰을 `git credential fill`로 꺼내(반드시 **cmd stdin 리다이렉트** 경유 — PS 파이프는 실패함) REST API 호출:
   ```powershell
   [System.IO.File]::WriteAllText("$env:TEMP\credq.txt", "protocol=https`nhost=github.com`n`n")
   $out = cmd /c "git credential fill < `"$env:TEMP\credq.txt`"" 2>$null
   $token = (($out | Where-Object { $_ -like 'password=*' }) -replace '^password=','')
   # POST /repos/.../pulls, PUT /pulls/N/merge (토큰은 절대 출력하지 말 것)
   ```
4. **배포 트리거**: 편지함 `haeory-sakyowon-site\JIMMY-DECA.md`에 "라이브 반영 요청" 편지 추가 → push
   - **push 전 반드시 `git fetch` + `git status -sb`** — behind면 로컬 정리 후 진행. 낡은 로컬 커밋은 backup 브랜치에 보관 후 reset
   - 편지 형식: `### [YYYY-MM-DD HH:MM KST] 데카 → 지미 (요청: 공동위키 라이브 반영)` + PR 번호·문서 경로·확인 URL
   - 파일 쓰기는 .NET UTF-8(no BOM) + **절대경로** (상대경로는 프로세스 cwd 불일치로 실패)
5. 라이브 확인: `https://wiki.poomasi.org/실천기술/<파일명-확장자-제외>` (한국어는 URL 인코딩해 요청)
   - 본부 배포 대기로 404면: 핸드오버 미완료 목록에 "위키 라이브 확인 대기" 기록하고 루틴은 종료 가능

## 마무리: 메모리 현행화

- `~/.claude/projects/<프로젝트>/memory/project-sakyowon-resume.md` — 재개 지점 갱신 (레포 상태, 남은 과제, 이번에 해결된 것)
- `MEMORY.md` 인덱스 한 줄 갱신
- 핸드오버에 위키배포 결과(PR 번호, 머지 sha, 라이브 여부)를 추가 커밋으로 반영

## 함정 모음 (실전에서 걸린 것)

1. 사이트 레포는 다른 세션이 수시로 push — fetch 없이 push하면 낡은 커밋이 섞여 나감
2. PS 5.1: `&&` 없음, 한국어 .ps1 깨짐, `git credential fill`은 PS 파이프 불가(cmd 경유), .NET 파일 API는 절대경로 필수
3. 편지함·레슨 등 한국어 파일은 `[System.Text.UTF8Encoding]::new($false)`로 쓸 것 (Set-Content 기본 인코딩은 ANSI)
4. winget으로 설치한 도구는 현 셸 PATH에 없음 — 사전 확인의 PATH 갱신 한 줄 실행
