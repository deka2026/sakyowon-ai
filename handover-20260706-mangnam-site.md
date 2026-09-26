# 핸드오버 — 망남항 어촌신활력증진사업 사이트 v1 (2026-07-06)

## 한 일 (이번 세션, 2026-07-05~06)

### 사이트 구축 완료 (v1)
- **위치**: 로컬 `C:\Users\Admin\sakyowon-ai\mangnam-site\` / GitHub `deka2026/mangnam-site`(public, 커밋 434c95a)
- **DB**: academy와 같은 Supabase(`gklecgujcoznxyvywnyu`), `mn_` 접두사로 분리
- **프리뷰**: launch.json `mangnam-site`, 포트 3004

| 페이지 | 기능 | 검증 |
|---|---|---|
| index.html | 공개: 소개박스·추진전략(단위사업6)·소식게시판·문의창 | E2E ✅ |
| admin.html | 승인제 로그인/회원가입 + 대시보드(회원관리·문의함·개선의견) | E2E ✅ |
| report.html | ①작성→②AI검수(필수)→③임시저장/게시, 사진업로드 | 가드·잠금로직 ✅ |
| monthly-personal.html | 개인 월간실적, 임시/최종(잠금·재열기) | E2E ✅ |
| monthly-subproject.html | 단위사업 6개별 월간실적, 공동작성 | E2E ✅ |
| helpdesk.html | 이나라도움 도우미: 매뉴얼 48섹션 검색·문답 축적·평가 | E2E ✅ |

- 모든 백엔드 페이지 우하단 💬 개선의견 위젯 (mn_feedback, 대시보드에서 모아보기)
- DB 스키마 3종 실행 완료: db-schema.sql, db-auth.sql, db-helpdesk.sql (모두 Success 확인)

### 콘텐츠 근거
- 기본계획보고서(`sakyowon-ai\망남마을\기본계획보고서_251125\` hwp 10개) 숙독 → 정식명칭·기간(2023~2026)·92.1억·3대분야·단위사업 6개(A1~A3, B1~B3) 반영
- 이나라도움 매뉴얼(`4-9.전체메뉴얼.pdf` 140쪽) → manual-data.js 48섹션 추출

### 주요 결정
- 기술: 단일 HTML + Supabase(academy 방식 재활용), AI는 UI만 먼저
- "세부사업 5개" → 문서 확인 후 **단위사업 6개**로 확정 (사용자 선택)
- 사교원 표기: "시행 완도군 · 운영(앵커조직) 사회혁신교육원" (사용자 선택)
- 지명: "전남" → "전남광주통합특별시"
- publishable key는 공개 저장소에 그대로 (공개 설계 키, RLS가 보호) — 사용자 동의

## 남은 과제 (다음 세션 시작점)
1. 직원 테스트 (회원가입→승인→사용→💬 의견 수집)
2. 지미 우편함 메모 — `haeory-sakyowon-site\JIMMY-DECA.md`에 "망남 사이트 완성, sakyowon.poomasi.org/mangnam 서빙 요청" + push (사용자가 보류 지시했다가 "남은 과제"로 확정)
3. AI 실연결 — report `callAiApi()` / helpdesk `composeAnswer()` (연결 지점 주석 참조)
4. 사교원 홈페이지에 망남 연결 버튼
5. Supabase 이메일 확인 OFF 확인 (Authentication→Sign In/Up→Email→Confirm email) — 사용자 실행 여부 미확인

## 데이터 현황 (2026-07-06)
- mn_helpdesk에 실사용 문답 1건 축적("자부담을 먼저 써야 하나요?")
- 테스트 데이터는 모두 정리함 (문의·실적·의견)
- 회원: 아직 mn_members 가입자 없음 (최고관리자 sakyowon@는 is_admin으로 통과)
