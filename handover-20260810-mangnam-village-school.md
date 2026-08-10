# 핸드오버: 망남마을학교 시범사업 기획안 + 신청 사이트 라이브 배포

**날짜**: 2026-08-10
**이전 핸드오버**: handover-20260808-toolchain-setup.md
**작업 폴더**: `D:\사교원 개발그룹\망남마을학교 시범사업\`, `C:\Users\User\mangnam-coop`

---

## 수행한 작업

### 1. 완도 망남마을학교 시범사업 기획안 (3박4일 · 1,000만원)
- 대상: 인천시 청년정책 공모전 3개 팀(리셋·호식이세마리치킨·숨,셋) 소속·추천 고립은둔/숨고르기 청년 20명
- 3개 팀 .hwp 계획서 6건을 커스텀 파서로 텍스트 추출해 각 팀 정책 핵심을 프로그램에 이식:
  숨,셋(회복체류 골격·CBI/PHQ-9 검사) · 리셋(재고립 방지 계획·작은 역할·3개월 사후동행) · 호식이(트리아지 안전관리·1:3 짝꿍 매칭)
- 어촌신활력 기본계획 연계: S/W B1(건강관리실)·B2(마을학교 — 본 사업이 첫 실증 기수)·B3(유통체계), 거점시설 3개소, 관계인구 지표
- 예산 1,000만원 정확 배분(버스 280 / 숙박 180 / 식비 216 / 주민강사 160 / 외부강사 60 / 기타 104), 마을 내 지출 55.6%
- 산출물: `D:\사교원 개발그룹\망남마을학교 시범사업\완도 망남마을학교 시범사업 기획안.md` + 동명 `.docx` (pandoc 변환)

### 2. mangnam-coop 사이트 — 마을학교 메뉴·신청·관리자 (커밋 a04fc2d, 63d3489, 54ed377)
- `/village-school`: 프로그램 안내 + 4일 일정표 + 개인별 신청 폼 (이름·전화 필수, 금기사항 10보기+기타, 희망체험 7보기+기타, 비희망 세션 체크 — 보기가 `data.ts` 일정 데이터에서 자동 생성됨)
- `/village-school/admin`: 비밀번호 조회, 1인실/알레르기/채식/복약/촬영비동의 집계, 희망체험 순위, 검색, CSV(BOM 포함)
- 백엔드: `apps-script/village-school.gs` — 정적 사이트라 서버가 없어 Google Apps Script 웹앱 + 스프레드시트 사용. 컨테이너 바인딩·독립형(SPREADSHEET_ID 폴백) 둘 다 지원

### 3. Apps Script 설치 지원 및 배포 검증
- 사용자가 sakyowon@gmail.com 계정으로 스프레드시트 바인딩 방식 배포 완료 (설치 중 이슈 대응: 배포 대화상자 오류→다중 로그인 안내, OAuth 미검증 경고→Advanced 통과, 권한 체크박스 안내)
- 엔드포인트 5종 검증: GET 상태 / apply 저장 성공 / 틀린 비밀번호 차단 / 무비밀번호 차단 / 미지원 action 거부
- `ADMIN_PASSWORD`·`NOTIFY_EMAIL`(sakyowon@gmail.com) 스크립트 속성 등록 확인

### 4. 라이브 배포 (gh-pages f2ef106)
- `.env.local`에 엔드포인트 → 재빌드 → 번들 포함 확인 → `git worktree`로 gh-pages 교체 커밋·push → Pages built
- **라이브 도메인(sakyowon.co.kr)에서 실제 폼 전송 성공까지 확인** (CORS 통과, "신청이 접수되었습니다" 렌더)
- URL: https://sakyowon.co.kr/mangnam-coop/village-school/ , .../village-school/admin/

## 미완료 / 다음 할 일
- [ ] 스프레드시트의 검증용 행 3건 삭제 요청됨 ([검증용]·[검증용2]·[검증용3]) — 사용자 몫
- [ ] 관리자 페이지 정상 조회(올바른 비밀번호)는 사용자만 확인 가능 — 확인 여부 미보고
- [ ] main의 `54ed377`는 force-with-lease로 재작성됨(중복 커밋 메시지 정정). 다른 클론이 있으면 pull --rebase 필요
- [ ] (이월) 유실 문의 구출(구 PC localStorage), sakyowon-mailbox-watch 재설치 여부
- [ ] (이월) 8/8 sakyowon.co.kr 존 이전(2안) 흐름 — 이번 세션에서 커스텀 도메인이 정상 서빙되는 것 확인됨(간접 검증)

## 파일 위치
| 경로 | 내용 |
|---|---|
| `D:\사교원 개발그룹\망남마을학교 시범사업\` | 기획안 MD + DOCX |
| `C:\Users\User\mangnam-coop` | 사이트 레포 (main 54ed377, gh-pages f2ef106) |
| `C:\Users\User\mangnam-coop\.env.local` | **엔드포인트 URL — gitignore 대상, 레포에 없음. 분실 시 배포 관리에서 재확인** |
| `C:\Users\User\mangnam-coop\apps-script\` | 백엔드 코드 + 설치 README (독립형 우회 포함) |
| 스프레드시트 `망남마을학교 참가신청` | sakyowon@gmail.com 드라이브, ID `1ZIga4c0RJrHZYy5LD-nc5MHG66Q75wpSp91RcauJdvc` |
| `sakyowon-ai/skills/hwp-binary-extract/` | 이번 세션 신규 스킬 (구형 .hwp 텍스트 추출) |

## 약속
- 사용자가 **"이어서 작업하자"** 라고 하면 이 핸드오버의 "미완료" 목록부터 재개
- 사용자가 **"정리해"** 라고 하면: ①핸드오버 ②스킬 ③레슨 ④위키배포 자동 수행
