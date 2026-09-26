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

## 8. 서버 env에 비밀키 넣기 — 이사장이 실행하는 4단계 (2026-09-23 실전)

키 값은 어디에도 찍지 않는다. 각 단계는 "이렇게 나오면 통과" 표와 함께 준다.

```bash
# (1) 모양만: 길이·ASCII·앞 3자
awk -F= '/^SAKYOWON_ANTHROPIC_KEY=/{v=$2; printf "len=%d ascii=%s prefix=%s\n", length(v), (v ~ /^[ -~]*$/ ? "yes" : "NO"), substr(v,1,3)}' /etc/sakyowon-api.env
```

```bash
# (2) 숨김 입력으로 넣기 — nano 붙여넣기는 조용히 실패한다(9/23 len=0 사고). 있으면 바꾸고 없으면 붙인다
read -rs -p "키를 붙여넣고 Enter: " K; echo; grep -q '^NAME=' /etc/sakyowon-api.env && sudo sed -i "s|^NAME=.*|NAME=$K|" /etc/sakyowon-api.env || echo "NAME=$K" | sudo tee -a /etc/sakyowon-api.env >/dev/null; unset K
```

```bash
# (3) 파일 시각 vs 서비스 시작 시각 — 파일이 뒤면 재시작 안 된 것
echo "file=$(stat -c %y /etc/sakyowon-api.env | cut -c1-19)"; systemctl show sakyowon-api -p ActiveEnterTimestamp
```

```bash
# (4) 키만 따로 시험 — 서비스 코드 무관. 값은 명령 안에서 파일로부터 읽힌다
curl -sS https://api.anthropic.com/v1/messages -H "x-api-key: $(sed -n 's/^SAKYOWON_ANTHROPIC_KEY=//p' /etc/sakyowon-api.env)" -H "anthropic-version: 2023-06-01" -H "content-type: application/json" -d '{"model":"claude-haiku-4-5-20251001","max_tokens":20,"messages":[{"role":"user","content":"안녕"}]}'
```

| (4) 응답 | 뜻 |
|---|---|
| `"type":"message"` | 키 정상 |
| `credit balance is too low` | 키 정상, 크레딧 0 → Billing 충전(카드사 3DS 보안프로그램 관문 있음) |
| `authentication_error` | 키 잘림·비활성 |
| `anthropic-workspace-id is required` | 키 생성 때 Workspace 미지정 → Delete 후 재발급(Default Workspace 지정) |

## 9. 서버가 받아 가는 미러를 같이 본다

서버는 `deka2026/sakyowon-server`(공개 미러, **평평한 루트**: `app.py`·`tools/`)에서 `git pull` → `cp app.py /opt/sakyowon/server/`. 원본 `haeory-sakyowon-site/server/`를 고쳤어도 **미러에 안 올리면 서버 pull은 아무 일도 안 한다**(9/23: 미러가 9/18에 멈춰 500 방지 코드가 안 감). 역방향도 있다 — 미러에만 직접 고친 파일(deploy-www.sh·setup-apps.sh)이 있었다. 동기화 전 `cmp`로 어느 쪽이 새것인지 파일마다 확인.

```bash
git clone -q https://github.com/deka2026/sakyowon-server.git /tmp/mirror && cd /tmp/mirror
for f in app.py .env.example deploy-www.sh setup-apps.sh; do cmp -s ~/haeory-sakyowon-site/server/$f $f || echo "DIFF $f"; done
```

## 10. 대조 시험 실행기와 401 읽는 법

`~/haeory-sakyowon-site/server/tools/compare_ask.py`(미러 `tools/`). 서버에서 `sudo python3 /opt/sakyowon/src/tools/compare_ask.py` → `/opt/sakyowon/data/compare/compare_<stamp>.md`. 엔진이 401이면 **키 없이/엉뚱한 키로도 같은 문구인지** 먼저 본다 — 같으면 엔진이 우리 키를 모르는 것(본부 등록 문제), 우리 쪽 3회 이상 반복 금지.

## 11. 함정 추가: Sonnet 5 기본 thinking이 답을 비운다

`max_tokens` 1500에 thinking 미지정이면 생각에 토큰을 다 쓰고 `text`가 빈 채 `output_tokens=1500`으로 끝난다(9/23 15건 중 4건). 단발 답변 경로는 `"thinking": {"type": "disabled"}` + 여유 있는 max_tokens. 프록시(`/api/ai`)는 클라이언트 미지정 시 `setdefault`로 주입.

## 12. 대조 시험 판정 절차 (2026-09-25 확립)

1. 서버에서 `sudo python3 /opt/sakyowon/src/tools/compare_ask.py` → `/opt/sakyowon/data/compare/compare_<stamp>.md`를 받는다(이사장이 `cat`으로 붙여 줌).
2. 문항지 `docs/대조시험_문항_사교원_15문_20260919.md`의 세 칸(답 맞나·근거 실재·지어냄)으로 채점. **집계는 「핵심 요소 충족」과 「지어냄=오답 엄격」 둘 다** 낸다 — 두 기준이 갈리면 그 자체가 판정 근거다.
3. **영역별로 본다.** 9/25 결과: 공고문·서류·절차(B·C·D) 엔진 9/9 vs Anthropic 4/9, 법령 조문(A) 엔진 1/6 vs 5/6. 「전체 승패」가 아니라 **탭 단위로 전환**(상담 탭만 엔진, 법령 탭은 Anthropic 유지)이 답이었다.
4. **정답지도 의심한다.** A-6 「영농형태양광법은 없다」는 정답지가 틀렸다(제21804호 실재). 법령 문항은 판정 전에 법제처 원문(PDF)으로 정답지부터 다시 닫는다. 자동 채록은 법제처 본문이 스크립트라 실패 — 이사장/실장에게 PDF 다운로드를 부탁하는 게 빠르다.
5. 엔진의 `sources`가 붙었다고 근거 있는 답이 아니다(A-2: sources 27건 중 무관 다수). 조문을 하나씩 연다.
6. 정식 문항이 insufficient로 물러섰어도 **짧은 구어체로 다시 던진다**(「2027년 공모 마감일은?」→ 지어냄). 이용자는 정식 문장으로 묻지 않는다.
7. 판정문은 `docs/대조시험_판정_<날짜>.md` + 사교원 허브사이트 폴더 사본 + 편지함 요지 + 이사장에게 SendUserFile.

## 13. ③단계 켜기·끄기 (2026-09-25 실전)

```bash
# 켜기 — 상담 탭만 엔진으로. 서류·법령·번역은 그대로 Anthropic
read -r -p "엔진 주소를 붙여넣고 Enter: " B; echo; grep -q '^POOME_API_BASE=' /etc/sakyowon-api.env && sudo sed -i "s|^POOME_API_BASE=.*|POOME_API_BASE=$B|" /etc/sakyowon-api.env || echo "POOME_API_BASE=$B" | sudo tee -a /etc/sakyowon-api.env >/dev/null; unset B; sudo systemctl restart sakyowon-api; curl -sS https://sakyowon.co.kr/api/ai/health
```

```bash
# 끄기
sudo sed -i '/^POOME_API_BASE=/d' /etc/sakyowon-api.env && sudo systemctl restart sakyowon-api
```

재시작 직후의 curl은 빈 응답일 수 있다(서비스 기동 중) — 데카 PC에서 다시 찍는다. 켜진 뒤 확인은 `check_status.py`의 VERDICT와 브라우저(데모 로그인 → AI 상담)에서 `.msg-badge` 텍스트.

## 14. 함정 추가 (9/25)

- **품에 키가 두 번 들어감**(86자=43×2): 터미널에서 오른쪽 클릭+Shift+Insert가 둘 다 먹은 것. 지문 대조 `sha256sum | cut -c1-8`(본부 발급값 `cfe33007`). 엔진 401 응답에 이제 `key_check{len,fp}`가 붙는다 — 그걸 그대로 본부에.
- 엔진 401은 「키 없음/틀림/부풀음」이 같은 문구다(9/23 이전). 키 없이 보내 비교하는 진단은 이 경우엔 성립하지 않았다.
- 엔진 답에 「품에의 자리 / 헌법 제N척추」 자기서술이 섞여 나올 수 있다(본부 결함 1, 수정 대기). 이용자 화면에 그대로 뜬다.


## 15. 함정 추가 (9/26): Git Bash의 curl은 한글을 CP949로 보낸다

`curl -d "{\"prompt\":\"한글…\"}"`를 이 PC의 Git Bash에서 돌리면 본문이 **CP949 바이트**로 나간다. 엔진은 깨진 질문을 받고 전부 `insufficient`로 답한다(9/25 저녁 8건이 tokens_in 3194로 똑같았다. 본부에 헛 복구 요청을 보냈다가 정정). 한글이 든 시험 호출은 파이썬 `urllib`로 `json.dumps(..., ensure_ascii=False).encode('utf-8')`를 보내거나, `--data-binary @utf8파일`로 보낸다. 판정 전에 같은 질문을 **3회** 보낸다 — 엔진의 insufficient 판정은 같은 문장에서도 흔들린다(9/26 12문×3회 34/36).

시험 호출기: `python ~/.claude/skills/hpc-project-status-check/scripts/ask_probe.py --live-presets -n 3` — 라이브 햇소자 `#/mem/ask` 예시 질문 12개를 UTF-8로 3회씩 보내 `3/3 src=9 O:req_… | 질문`으로 찍는다. `-q "질문"`으로 개별 질문, `--json`으로 편지함용 표.
