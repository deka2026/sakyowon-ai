# 핸드오버 — M1~M4 (2026-06-24)

## 완료된 단계

### M1 — 환경 설정 + Claude Code
- OS: Windows 10 Pro
- Node.js v24.18.0 / npm 11.16.0
- Git 2.54.0 / VSCode 1.125.1 / Obsidian 1.12.7
- Claude Code v2.1.187 설치 + Team 계정 로그인
- CLAUDE.md 작성 완료 (`~/sakyowon-ai/CLAUDE.md`)

### M2 — Git + GitHub
- 레포: https://github.com/deka2026/sakyowon-ai
- 브랜치: master
- 파일: README.md, CLAUDE.md
- ✅ 5종 자산 1번 완료

### M3 — Obsidian + Quartz + Cloudflare Pages
- Quartz 설치: `C:\Users\pc\quartz` (v5 브랜치)
- GitHub 레포: https://github.com/deka2026/quartz
- Cloudflare Pages: https://sakyowon-quartz.pages.dev
- 커스텀 도메인: wiki.sakyowon.co.kr (DNS 전파 중)
- ✅ 5종 자산 2번 완료

### M4 — Supabase DB
- 프로젝트: sakyowon-db
- 테이블: notes (id, title, body, created_at)
- RLS: anon_read 정책 (SELECT 허용)
- curl 테스트: 회사 네트워크 차단으로 미완 → 나중에 확인
- ✅ 5종 자산 3번 (테이블 생성까지 완료)

## 다음 단계
- M5: 한 페이지 사이트 URL
- M6: 작동하는 자동화 1개
- 미완: Supabase curl GET 테스트 (네트워크 허용 후)

## 레슨런
- PAT 토큰은 절대 채팅창에 붙여넣지 말 것 (오늘 3회 노출)
- PowerShell에서 curl은 Invoke-RestMethod 사용
- Quartz v5 빌드 명령어: `npx quartz plugin install && npx quartz build`
- Cloudflare Pages Node 버전: NODE_VERSION=22 환경변수 필요

## 규칙
- "정리해" → 핸드오버 작성 + 스킬 + 레슨 + 위키 배포 자동수행