# 핸드오버: 파란교실(청년) 상세페이지 문구·신청서 개편 및 배포 파이프라인 확립

**날짜**: 2026-08-24
**이전 핸드오버**: handover-20260819-westay-lecture-deck.md
**작업 폴더**: `C:\Users\User\mangnam-coop` (deka2026/mangnam-coop)

---

## 수행한 작업

### 1. 파란교실(청년) 상세페이지 문구 수정 (main 4커밋, 전부 라이브 반영 확인)
- `197b013` 본문 카피 교체 — 제목 "섬과 함께하는 3박 4일", 참가비·안전 안내·마을 환원 설명 등 (사용자가 직접 수정, 데카가 빌드·배포)
- `c513e28` 신청서에 **"내가 잘하는 것 (익숙한 것, 즐기는 것)"** 주관식 항목 추가 — 구체적 작성 안내 문구 포함, 요약문(detailsText)·payload·초기화에 반영
- `91bacf4` "1인 1침상이 기본이며," 문구 삭제
- `6b2a382` **신청 절차 3단계 개편** — STEP 1(신청서 작성: 참가비 2만원·환불 불가 포함) → STEP 2(개별 전화 인터뷰) → STEP 3(최종 참가 통보). 신청서에 일정 참가 확인 체크(필수)·인천–완도 고속버스 가능 여부 라디오(필수) 추가, 프로그램 예시를 스킴보드 강습·해안로 탐방·AI 교육·온라인셀러 교육·취창업 교육으로 교체, FACTS 참가비를 "2만원(네트워크 파티 음식 준비용·불참 시 환불 불가)"로 교체
- 폼 검증(일정 미체크·버스 미선택 시 제출 차단)을 로컬 dev 서버 + 브라우저로 실제 클릭 테스트 완료

### 2. 배포 파이프라인 확립 및 서빙 구조 규명
- 배포 절차: `npm run build` → `git worktree`로 gh-pages에 out/ 복사(.nojekyll 유지) → push. deploy 커밋 4건(`c2c7442`→`79ec098`)
- **핵심 발견**: sakyowon.co.kr은 GitHub Pages가 아니라 **가비아 자체 서버(Caddy)가 서빙**. gh-pages push만으로는 반영 안 되고, 서버에서 `sudo bash /opt/sakyowon/src/deploy-www.sh` 실행 시 gh-pages를 clone해 `/opt/sakyowon/www/mangnam-coop/`에 배치. 자동 동기화 타이머는 확인 안 됨(16시간 미반영 구간 있었음) — 이번엔 08-24 08:07 KST에 갱신되어 **4건 전부 라이브 반영 확인 완료**
- **함정 발견·해소**: 로컬 `.env.local`의 `NEXT_PUBLIC_VILLAGE_SCHOOL_ENDPOINT`(옛 Apps Script URL)가 남아 있으면 빌드 시 신청폼이 옛 주소로 회귀. 최신 사이트는 자체 서버 `/api/applications`가 기본이라 **해당 줄을 주석 처리**해 두었음(재활성화 금지)

### 3. 스킬 신설
- `mangnam-coop-deploy` — 파란교실 등 mangnam-coop 문구 수정→빌드→gh-pages 배포→라이브 확인 절차와 함정 모음 (아래 파일 위치 참조)

## 미완료 / 다음 할 일
- [ ] 서버 www 동기화가 수동인지 타이머인지 확정 필요 — 이사장님/후니님께 확인 (gh-pages push 후 미반영이면 `ssh root@sakyowon.co.kr` → `sudo bash /opt/sakyowon/src/deploy-www.sh`)
- [ ] (이월) 위스테이 별내 강의 진행 후 피드백 반영 여부 확인
- [ ] 참가비 정책 표기 확인 — 8/23 사용자 수정("만든 결과물 공유로 대신")과 8/24 지시(2만원)가 충돌해 2만원으로 통일했음. 이사장님 확정값인지 확인

## 파일 위치
| 경로 | 내용 |
|---|---|
| `C:\Users\User\mangnam-coop\app\village-school\youth\page.tsx` | 파란교실 상세페이지 본문·절차 3단계·FACTS |
| `C:\Users\User\mangnam-coop\app\village-school\ApplicationForm.tsx` | 파란교실 신청 폼 (일정·버스 확인, 잘하는 것, 참가비 안내) |
| `C:\Users\User\mangnam-coop\app\village-school\data.ts` | 일정표·프로그램 예시(WISH_OPTIONS)·선택지 문구 |
| `C:\Users\User\mangnam-coop\.env.local` | 옛 Apps Script 엔드포인트 주석 처리됨 — 재활성화 금지 |
| `C:\Users\User\sakyowon-ai\skills\mangnam-coop-deploy\SKILL.md` | 수정→배포 절차 스킬 |
| `C:\Users\User\haeory-sakyowon-site\server\deploy-www.sh` | 가비아 서버 정적 배치 스크립트 (서버의 `/opt/sakyowon/src/`에 존재) |

## 약속
- 사용자가 **"이어서 작업하자"** 라고 하면 이 핸드오버의 "미완료" 목록부터 재개
- 사용자가 **"정리해"** 라고 하면: ①핸드오버 ②스킬 ③레슨 ④위키배포 자동 수행
