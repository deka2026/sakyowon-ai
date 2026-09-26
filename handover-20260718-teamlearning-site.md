# 핸드오버 2026-07-18 — 사교원 사회혁신팀러닝 사이트 구축

## 세션 요약
이사장 지시로 팀러닝 자문·컨설팅 사이트를 하루 만에 설계→구축→배포→2차 기능(전화번호 회신·알림)까지 완료.

- **공개 URL**: https://deka2026.github.io/teamlearning-site/
- **GitHub**: `deka2026/teamlearning-site` (public, main push 시 Pages 자동 재배포)
- **로컬**: `C:\Users\Admin\sakyowon-ai\teamlearning-site\`
- **DB**: academy·망남과 같은 Supabase(`gklecgujcoznxyvywnyu`), `tl_` 접두사
- **허브 연결**: sakyowon-hub "프로젝트" 섹션에 🌱 버튼 추가·라이브 확인

## 구축 내용

### v1 (오후)
- 페이지 4종: index(팀 등록→전용링크 발급), team(질문·답변/계획안·보완/자료조사/최종보고 4탭), report(인쇄·PDF), admin(질문함·계획안함·조사요청함·팀목록·보고서발행)
- 접근 설계: 팀은 로그인 없이 **토큰 전용링크**로만 접근. 모든 팀 조회·제출은 security definer RPC 경유, 테이블 직접 접근은 RLS 차단(관리자 `is_admin()`만)
- 사용자 선택: 열람=팀 전용 링크 / 팀 등록=팀이 직접
- `db-schema.sql` 적용 완료 (테이블 5 + RPC 9)

### v1.5 — 게시 후 수정 기능
- 이사장 첫 테스트에서 "게시한 답변 수정 불가" 빈틈 발견 → 답변완료/보완완료/게시완료 목록에 ✏️ 수정 버튼 추가

### v2 (밤) — `db-schema2.sql` 적용 완료
- **전화번호 회신**: 질문 폼에 휴대폰(선택) → 답변 게시 순간 트리거가 `tl_notifications`에 문자(팀 링크 포함) 자동 적재. 번호는 관리자만 열람
- **알림함(📨) 탭**: 발송대기 문자 복사→수동발송→발송완료 처리 (SMS 게이트웨이 연결 시 자동화 예정)
- **🤖 AI 답변 시작하기**: admin.html 상단 `AI_ENDPOINT`(현재 빈 값)에 프록시 주소만 넣으면 작동. 규격 POST `{type,team,topic,question}` → `{answer}`
- **모바일 알림**: 스케줄 작업 `teamlearning-watch` (cron `0 9-21/3 * * *`, 로컬 클로드 앱 켜져 있을 때 실행). `tl_pending_counts()`로 건수만 확인 후 새 접수 시 푸시
- 버그 수정: 알림함 등 목록이 로그인 시점 데이터로 고정되던 문제 → 탭 전환·답변 게시 시 자동 갱신 (커밋 e358d5b)

## 표준 운영 흐름 (이사장님용)
1. 팀 질문 접수 → (모바일 푸시 알림)
2. 채팅에 **"질문 답변하자"** → 데카가 대기 질문 읽고 초안 작성
3. 관리페이지 질문함에 초안 붙여넣기 + 🌱 조언 입력 → 답변 게시
4. 전화번호 있으면 📨 알림함에서 문자 복사→발송→발송완료 처리

## 미완료 (다음 세션 "이어서 작업하자" 시)
1. **알림함 트리거 최종 확인** — 이사장이 전화번호 테스트 질문에 답변 게시함(23:21). 새로고침 후 알림함에 문자 1건 보이는지 확인 대기 (stale 표시 버그는 수정·배포됨)
2. **teamlearning-watch Run now** — 사이드바 Scheduled에서 1회 실행해 권한 사전 승인 (안내함, 실행 여부 미확인)
3. **테스트 데이터 정리** — `delete from tl_teams where name = '테스트팀';`
4. (추후) AI_ENDPOINT 연결(지미 /api/ai 또는 Supabase Edge Function), SMS 게이트웨이

## 주의사항
- **배포 순서**: RPC 시그니처가 바뀌는 변경은 반드시 SQL 먼저, 사이트 푸시는 그 다음 (역순이면 실사이트 접수 끊김)
- **RPC 시그니처 변경 시**: `drop function if exists ...(옛 시그니처)` 필수 — create or replace만 하면 함수 중복(오버로드)으로 PostgREST 호출이 모호해짐
- **로컬 프리뷰(serve)**: `team.html?t=...`를 `/team`으로 리다이렉트하며 쿼리를 버림 → 로컬 테스트는 확장자 없는 `/team?t=...`로. GitHub Pages에선 문제 없음
