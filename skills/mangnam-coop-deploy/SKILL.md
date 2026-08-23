---
name: mangnam-coop-deploy
description: 망남마을협동조합 사이트(mangnam-coop)의 문구·페이지·신청폼을 수정하고 빌드→gh-pages 배포→실사이트(sakyowon.co.kr) 반영 확인까지 수행하는 스킬. "파란교실/연두교실/푸른교실 문구 고쳐줘", "망남 사이트 수정해서 반영해줘" 같은 요청에 사용.
---

# mangnam-coop 수정→배포 절차

## 저장소·구조

- 로컬 레포: `C:\Users\User\mangnam-coop` (GitHub `deka2026/mangnam-coop`, 기본 브랜치 main)
- Next.js 14 정적 export (`output: "export"`, `basePath: "/mangnam-coop"`)
- **작업 전 반드시 `git pull`** — 다른 세션·지미가 main과 gh-pages 양쪽에 push한다 (2026-08-23 로컬이 8커밋 뒤처져 있었음)

## 문구가 사는 곳

| 대상 | 파일 |
|---|---|
| 파란교실(청년) 상세 본문·신청절차·FACTS | `app/village-school/youth/page.tsx` |
| 파란교실 신청 폼 | `app/village-school/ApplicationForm.tsx` |
| 연두(청소년)·푸른(장년) 상세 | `app/village-school/teen/page.tsx`, `senior/page.tsx` |
| 연두·푸른 신청 폼 | `app/village-school/CampApplicationForm.tsx` |
| 일정표·선택지(WISH/AVOID/OPT_OUT/TEAM) | `app/village-school/data.ts` — 세션 `id`는 신청 데이터에 저장되므로 변경 금지, label/desc만 수정 |
| 메뉴 | `app/components/Sidebar.tsx` |

## 신청 백엔드 (중요)

- 신청폼은 **사교원 자체 서버(가비아) `/api/applications`** 로 POST (`app/village-school/config.ts`의 기본값). 같은 출처라 CORS 없음.
- **함정**: `.env.local`의 `NEXT_PUBLIC_VILLAGE_SCHOOL_ENDPOINT`는 옛 Apps Script URL — 살아 있으면 빌드가 옛 주소로 회귀한다. 2026-08-23에 주석 처리해 둠. **재활성화 금지.** 빌드 전 `grep NEXT_PUBLIC .env.local`로 주석 상태 확인.
- 백엔드는 `detailsText`(사람이 읽는 요약)와 raw JSON을 통째로 저장하므로, 폼에 필드를 추가할 때 서버 수정은 불필요. 단 폼의 `summary`와 `payload` 양쪽에 새 필드를 넣을 것.

## 배포 절차

```bash
cd C:/Users/User/mangnam-coop
npm run type-check && npm run build
# 빌드 검증: 새 문구가 out에 있는지, 옛 엔드포인트가 없는지
grep -rl "script.google" out/_next && echo "위험: 옛 엔드포인트!" || echo OK
# gh-pages 배포 (워크트리 방식)
git branch -f gh-pages origin/gh-pages   # 로컬 gh-pages가 뒤처졌을 때
git worktree add ../mangnam-gh gh-pages
cd ../mangnam-gh
find . -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +
cp -r ../mangnam-coop/out/* . && touch .nojekyll
git add -A && git commit -m "deploy: <내용>" && git push origin gh-pages
cd ../mangnam-coop && git worktree remove ../mangnam-gh
```

## 실사이트 반영 (gh-pages push로 끝나지 않음)

- sakyowon.co.kr은 GitHub Pages가 아니라 **가비아 자체 서버(Caddy)** 가 `/opt/sakyowon/www/mangnam-coop/`를 서빙.
- 서버의 `sudo bash /opt/sakyowon/src/deploy-www.sh`가 gh-pages를 clone해 재배치해야 반영. 자동 타이머는 미확인(16시간 미반영 사례 있음) — 접속은 `ssh root@sakyowon.co.kr` (비밀번호는 이사장님/후니님 보유, 데카 키 없음).
- 반영 확인:

```bash
curl -sI "https://sakyowon.co.kr/mangnam-coop/village-school/youth/" | grep -i last-modified
curl -s "https://sakyowon.co.kr/mangnam-coop/village-school/youth/" | grep -c "<새 문구>"
```

## 로컬 검증 (폼 로직을 바꿨을 때)

- `.claude/launch.json`에 dev 서버 등록돼 있음 (`npm run dev`, 포트 3000). 브라우저 프리뷰로 `http://localhost:3000/mangnam-coop/village-school/youth/` 열어 필수 검증(제출 차단)을 실제 클릭으로 확인.
- 루트 `http://localhost:3000/` 은 basePath 때문에 404가 정상.

## 함정 모음

1. `.env.local` 옛 Apps Script 엔드포인트 — 위 참조. 최대 함정.
2. 로컬 main·gh-pages 모두 원격보다 뒤처질 수 있음 — fetch/pull 먼저.
3. gh-pages 배치 시 `.nojekyll` 유지 필수 (`_next/` 디렉토리 서빙용).
4. data.ts 세션 `id`와 폼 선택지 label은 신청 데이터에 저장됨 — label 변경은 이후 데이터부터 적용되고 기존 데이터는 옛 label 유지(관리자 집계 유의).
5. 커밋 메시지는 한국어 제목 + `Co-Authored-By: Claude ...` 푸터.
