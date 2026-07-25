# 핸드오버: 새 컴퓨터 이전 복구 + LONLO 정식 승격

**날짜**: 2026-07-24~25
**이전 핸드오버**: handover-20260705-solidarity-wiki-first-pr.md
**환경 변화**: 작업 컴퓨터가 구 PC(`C:\Users\Admin`)에서 신 PC(`C:\Users\User`)로 바뀜

---

## 수행한 작업

### 1. 새 컴퓨터 복구
- `deka2026/sakyowon-ai` 재클론·복원: `C:\Users\User\sakyowon-ai\` (예전 M1~M6 전체 기록 포함. 이전 착오로 만든 새 커밋은 `backup-20260723` 브랜치에 보관)
- `haeory-cyber/sakyowon-site` 재클론: `C:\Users\User\haeory-sakyowon-site\` (우편함 포함)
- GitHub 인증(GCM)은 이 컴퓨터에 이미 저장돼 있어 push 정상 동작 확인

### 2. AI 답변 면책 문구 (지미 7/22 숙제)
- `renderAIChat`에서 AI 말풍선마다 "이 답변은 AI가 생성한 것이며, 정확성은 사교원이 보증하지 않습니다" 부착 (`.ai-disclaimer` 스타일 신설)

### 3. LONLO 정식 승격 (커밋 `4329d60`)
- `lonlo.html` → `index.html` 교체 (git mv)
- 기존 index는 `index-legacy.html`로 백업
- 옛 주소 `/lonlo.html`은 메인(`/`)으로 리다이렉트하는 스텁으로 대체
- **라이브 실측 완료**: 메인 타이틀 LONLO ✓ / 리다이렉트 ✓ / legacy 200 ✓ / `/api/ai/chat` 실답변 ✓

### 4. 병행 세션 발견 (7/24)
- push 과정에서 발견: 7/24에 다른 세션이 이미 작업함 — sakyowon.co.kr DNS 연결·HTTPS 완료, 허브 링크 새 도메인 교체, 실사용 백엔드 요청, mangnam-vitality 배포·키 요청 편지
- **지미 7/24 14:33 회신 도착**: LONLO 승격 점검 완료 + 실사용 인증/회원승인/피드백 백엔드 라이브 (커밋 `277ee` — 아직 정독 안 함)

## 미완료 / 다음 할 일

- [ ] 지미의 7/24 새 메시지 3건 정독 (백엔드 라이브 회신 `277ee`, mangnam-vitality `632ac69` 등)
- [ ] 로컬 커밋 `2240d62`(우편함 승격 보고) 처리 — 내용이 낡음(지미가 이미 점검 완료). 최신 상황에 맞게 다시 써서 push하거나 `git reset --hard origin/main` 후 새로 작성. 현재 main은 ahead 1 / behind 8, rebase는 abort로 원상복구해 둔 상태
- [ ] 유실 문의 구출 (지미 7/22 지적): 7/22 이전 LONLO 문의는 서버 400 거절 → 시연 브라우저 localStorage(`lonlo_inquiries_backup`)에만 존재. 시연 브라우저가 구 PC 쪽일 가능성 — 이사장님 확인 필요
- [ ] 우편함 감시 클라우드 작업(`sakyowon-mailbox-watch`) 신 PC 재설치 여부 결정

## 파일 위치 (신 PC 기준)

| 경로 | 내용 |
|---|---|
| `C:\Users\User\sakyowon-ai\` | 핸드오버·자동화 레포 (deka2026/sakyowon-ai) |
| `C:\Users\User\haeory-sakyowon-site\` | 사교원 사이트 진짜 레포 + 우편함 JIMMY-DECA.md |
| (구 PC) `C:\Users\Admin\solidarity-intelligence-wiki-haeory\` | 공동위키 클론 — 신 PC엔 아직 없음, 필요 시 재클론 |
| (구 PC) `C:\Users\Admin\deka-outputs\` | 다운로드 레포 — 신 PC엔 아직 없음 |

## 약속

- 사용자가 **"이어서 작업하자"** 라고 하면 이 핸드오버의 "미완료" 목록부터 재개
- 사용자가 **"정리해"** 라고 하면: ①핸드오버 작성 ②스킬 ③레슨 ④위키배포 를 자동 수행 (2026-07-25 지시)
