---
name: hpc-project-status-check
description: NIPA 고성능컴퓨팅(GPU) 지원사업의 운영 상태와 사교원 프런트(햇소자) 연동 여부를 실측으로 점검하는 스킬. "햇소자가 GPU 쓰고 있어?", "HPC 사업 지금 어디까지 왔어", "중간점검 서면에 뭐라고 써야 해", "GPU 사용률 확인해줘" 같은 요청에 사용. 문서·코드·라이브·대시보드·편지함 다섯 갈래를 대조해 "연동됐다/안 됐다"를 근거와 함께 판정하고, 본부 안내와 사교원 계획의 차이를 표로 낸다. 콘솔 조작은 하지 않는다(읽기 전용).
---

# HPC 사업 상태 점검 (햇소자 연동 포함)

2026-09-18 세션에서 확립. 사교원이 주관기관인 NIPA 고성능컴퓨팅 사업(kt cloud AI Nexus, H200 1장, EXAONE 기반 엔진)의 상태를 **말이 아니라 실측**으로 확인하는 절차다. 같은 질문이 10월 중간점검·12월 성과보고회까지 되풀이된다.

## 0. 전제

- GPU 세션·엔진·대시보드는 **품앗이 본부(지미)** 가 운영한다. 사교원은 프런트(햇소자)와 보고 책임을 진다. 콘솔 계정은 본부와 공동 사용이며 **첫 한 달은 읽기 전용**. 이 스킬은 콘솔을 만지지 않는다.
- 판정 근거는 다섯 갈래다. 하나만 보면 틀린다(대시보드는 "9월 프런트 연동 선행 달성"인데 사교원 프런트는 0이었다).

| 갈래 | 어디 | 무엇을 본다 |
|---|---|---|
| 문서 | `D:\사교원 개발그룹\사교원 개발그룹\사교원 허브사이트\*.pdf` (kt cloud 가이드 5종) | 플랫폼 제약, 회수 규칙 |
| 코드 | `~/haeory-sakyowon-site/server/app.py` 924행~ | AI 호출부가 어디를 부르나 (`ANTHROPIC_URL` vs `POOME_API_BASE`) |
| 라이브 | `scripts/check_status.py` | 프런트 호출 수, 백엔드 응답, 엔진 health |
| 대시보드 | https://nexus.poomasi.org/ | 정량목표 7개, GPU Util, 회수 사고, 월별 마일스톤 |
| 편지함 | `~/haeory-sakyowon-site/JIMMY-DECA.md` | 규격서 회신 진척, 본부 약속 |

## 1. 실측 한 번에

```bash
python ~/.claude/skills/hpc-project-status-check/scripts/check_status.py
```

출력 예(2026-09-18):

```
| backend /api/ai/chat | NOT_CONNECTED (no key) · backend=(none) |
| engine /api/v1/health | 404 · {"detail":"Not Found"} |
| GPU util avg | 8% |
VERDICT: hatsoja NOT linked to HPC engine (engine /api/v1/health not up) (backend AI not answering)
```

`--json`으로 받으면 중간점검 서면 표에 그대로 옮길 수 있다. 대시보드 기준일(`as_of`)이 오래됐으면 본부에 갱신을 요청한다.

## 2. 코드 확인 (라이브가 "답한다"고 나와도 어느 엔진인지 봐야 한다)

```bash
grep -n "ANTHROPIC_URL\|POOME_API_BASE\|api/v1" ~/haeory-sakyowon-site/server/app.py
```

- `ANTHROPIC_URL`만 있고 `POOME_API_BASE`가 없으면 → **엔진 미연동**. 답이 나와도 그건 Anthropic이다.
- 규격서(`docs/시민재생에너지AI_연동규격서_v0.1_20260831.md`) 6절이 정한 환경변수 이름이 `POOME_API_BASE`·`POOME_API_KEY`다.

## 3. PDF 가이드 채록 — pdftotext는 한국어를 떨군다

이 폴더의 kt cloud PDF는 `pdftotext -layout`로 뽑으면 **한글이 전부 사라진다**(폰트 매핑 문제). `pymupdf`를 쓴다.

```bash
PYTHONIOENCODING=utf-8 python - <<'EOF'
import pymupdf
d = pymupdf.open("2. NIPA 고성능 사업 GPU 사용자 Workflow.pdf")
for p in d: print(p.get_text())
EOF
```

`pdfplumber`는 이 PC에 없다. `pymupdf`(fitz)와 `pypdf`는 있다.

## 4. 판정 문장 쓰는 법 — 중간점검·성과보고서용

세 칸으로 나눠 쓴다. 섞어 쓰면 "달성"이 지어낸 값이 된다(환수 사유).

| 칸 | 예 |
|---|---|
| 본부 엔진 기준 | RAG 통합·챗봇 라이브 — 9월 계획을 6월에 선행 달성 |
| 사교원 프런트 기준 | 햇소자 AI 호출부 5곳 전부 Anthropic 직접 호출 · 엔진 `/api/v1` 미구현 → **연동 0, 10월 내 완료 예정** |
| 측정 불가 항목 | 사업계획서 자동작성 80% · 운영비 절감 70% · 실증 마을 — 연동 전이라 미측정 |

## 5. 본부 안내가 오면 — 계획과 대조하는 표 네 줄

본부가 인수인계·역할 안내를 보내면 아래 넷이 들어 있는지 본다. 2026-09-18 안내에는 넷 다 빠져 있었다.

1. 사교원 프런트 연동(`/api/v1/health`·`ask`·API 키) **날짜**
2. 실증 마을 3~5개를 **어느 화면**으로 하나
3. GPU 사용률(실장 의무 지표)의 **주간 보고와 야간 배치 실행 주체**
4. 공동 계정의 **비밀번호 변경 정책**(사교원이 바꾸면 본부가 잠긴다)

회신 초안 틀은 계획서 8-5절(`고성능컴퓨팅_활용계획_햇소자연동점검_20260918.md`)에 있다.

## 6. 함정

1. **`pdftotext`는 한국어를 떨군다** — 3절. 영어만 남은 출력을 보고 "내용이 비었다"고 판단하지 말 것.
2. **대시보드 "선행 달성"은 본부 챗봇 기준**이다. 사교원 프런트 연동과 별개.
3. **터널이 죽으면 530**(Cloudflare 1033)이 온다. 아웃바운드 방화벽이 아니다. 어느 네트워크에서 찍어도 같으면 본부 cloudflared 문제.
4. **`/api/ai/chat`이 답해도 연동은 아니다** — `backend` 필드나 코드로 엔진을 확인.
5. 지미 인스턴스는 둘(편지함/그룹챗). 그룹챗으로 온 안내에 편지함으로만 답하면 안 닿을 수 있다 — 회신은 **그룹챗에도** 붙인다.
6. 콘솔 조작·세션 삭제는 이 스킬 범위 밖. 모델 두 개와 작업 폴더가 복구 불가로 사라진다.

## 7. 관련 파일

- 계획서: `D:\사교원 개발그룹\사교원 개발그룹\사교원 허브사이트\고성능컴퓨팅_활용계획_햇소자연동점검_20260918.md`
- 규격서: `~/haeory-sakyowon-site/docs/시민재생에너지AI_연동규격서_v0.1_20260831.md`
- 핸드오버: `~/sakyowon-ai/handover-20260918-hpc-nipa-hatsoja-integration.md`
