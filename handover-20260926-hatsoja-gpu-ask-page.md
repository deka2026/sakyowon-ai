# 핸드오버: 햇소자 GPU 엔진 질문 모음 페이지 + 엔진 오진 정정 + 결함 1 재보고

**날짜**: 2026-09-26
**이전 핸드오버**: handover-20260925-sqld-20-modules.md (HPC 계열 직전: handover-20260918-hpc-nipa-hatsoja-integration.md)
**작업 폴더**: `%LOCALAPPDATA%\Temp\hub-clone` (deka2026.github.io), `~/haeory-sakyowon-site` (편지함)

---

## 수행한 작업

### 1. HPC 사용 여부 판정 (9/25)
- `check_status.py` VERDICT: **햇소자 상담 탭은 GPU 엔진에 연동됨** (`backend=exaone-lora`, engine `/api/v1/health` 200, rag_docs 2000). 서류·법령·번역 탭은 Anthropic 유지.
- 대시보드(as-of 9/23): GPU util 평균 15.9% · 회수 사고 2 · 정확도 88.7% · 데이터셋 29,207건 · 실증 마을 0.

### 2. 「GPU 엔진 질문 모음」 상세페이지 `#/mem/ask` 신설
- 라이브: https://sakyowon.co.kr/hatsoja/#/mem/ask (로그인 회원만. 손님은 홈으로)
- `memAsk()` + `ASK_GROUPS`(참여 요건·설립 절차·설비 수익·서류 점검 × 3문) + `askPreset()`. 입력란은 `sendChat` 공용(`/api/ai/chat`). AI 상담 화면에 링크를 달았다.
- 허브 PR #4 (머지 `36e0a41`) → 예시 6개 교체 PR #6 (머지 `9584dc7`). 두 번 모두 이사장이 `deploy-www.sh` 실행 → 라이브 반영 확인.
- 9/26 라이브 1회 측정 10/12 답함. 전날 3회 반복 측정에서는 교체 뒤 12개 모두 답했다.

### 3. 엔진 「전부 insufficient」 오진 → 정정
- 9/25 18:50 편지(`cc915f5`)에서 "엔진 검색이 0건"이라고 보고했다. 본부 회신(`1df0010`)은 "tokens_in 3194 ≠ 원문 4082"였다.
- 원인은 **데카 쪽 Git Bash curl이 한글을 CP949로 전송**한 것이다(로컬 덤프 서버로 확인). 엔진은 정상이었다.
- 정정 편지 `2f186fe`: 복구 요청 철회, UTF-8 재측정 12문×3회 34/36, 흔들린 request_id 5건, request_id 빈 값(캐시 여부) 질문.

### 4. 결함 1 재보고
- 편지 `13f9b9d`(시각 정정 `6c7c6e0`): 이용자 화면에 「헌법 제1척추(모름의 자리)…」 자기서술이 노출됨(`req_9461f1bfa97f`). 엔진에서 빼 달라고 요청했다. 프런트에서는 거르지 않는다(대조 기록 일관성).
- 이사장이 그룹챗에도 전달.

## 미완료 / 다음 할 일
- [ ] 본부 회신 대기: 결함 1 수정 여부 → 같은 질문(「햇빛소득마을 사업은 어떤 단계로 진행되나요?」)으로 재확인
- [ ] 본부 회신 대기: 흔들린 insufficient 5건이 검색 0건인지 모델 판정인지, `insufficient_reason` 규격 반영 시점, request_id 빈 값 = 캐시인지
- [ ] 예시 질문 흔들림 추적: `ask_probe.py --live-presets -n 3`으로 주 1회 측정
- [ ] (이월) 결함 4(짧은 질문 날짜 지어냄), 법령 탭 재시험(A군 4/6 조건), 영농형태양광사업법 `law_facts` 반영 확인
- [ ] (이월) GPU 사용률 15.9% — 야간 배치 실행 주체를 본부와 확정

## 파일 위치
| 경로 | 내용 |
|---|---|
| deka2026.github.io `hatsoja/index.html` | `memAsk`·`ASK_GROUPS`·`askPreset`, CSS `.ask-groups` |
| `~/haeory-sakyowon-site/JIMMY-DECA.md` | 18:50 편지, 본부 회신, 정정 편지, 결함 1 편지 |
| `skills/hpc-project-status-check/scripts/ask_probe.py` | UTF-8 시험 호출기 (신규) |
| `skills/hpc-project-status-check/SKILL.md` | 15절: curl CP949 함정 + 3회 반복 원칙 |
| `skills/hatsoja-site-deploy/SKILL.md` | 코드 지도에 AI 상담·질문 모음, 함정 7 |

## 약속
- 사용자가 **"이어서 작업하자"** 라고 하면 이 핸드오버의 "미완료" 목록부터 재개
- 사용자가 **"정리해"** 라고 하면: ①핸드오버 ②스킬 ③레슨 ④위키배포 자동 수행

## 위키배포 결과
- 레슨 「AI가 고장났다고 보고하기 전에 내 시험 도구부터 의심하기」(사교원 위키 `연대지능/`)
- v4 `251b2d5` → CI 36214803463 (아티팩트 10896778641, sitemap 129, 문서 포함 확인) → sakyowon-wiki-site master `75f2595`
- **4단계 완료** — 2026-09-26 12:32 KST 이사장 서버 반영. 라이브 sitemap 129, 문서 200 (편지 `54edec2`)
