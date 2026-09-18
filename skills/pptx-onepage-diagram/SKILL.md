---
name: pptx-onepage-diagram
description: 작업 환경·조직·사업 구조를 PPT 한 장짜리 체계도(다이어그램)로 만드는 스킬. "내 AI 업무환경 체계도 한 장으로", "이 사업 구조도 PPT로", "하네스 구조도 만들어줘" 같은 요청에 사용. 계층(band) × 카드/칩 격자로 조립하고 PowerPoint COM으로 PNG 렌더해 넘침을 눈으로 검증한다. 여러 장짜리 강의안은 pptx-lecture-deck을 쓴다.
---

# 한 장짜리 체계도 PPTX 만들기

강의안(pptx-lecture-deck)과 목적이 다르다. **한 장 안에 전체 그림을 넣는 것**이 전부라서,
글자 크기를 줄이는 대신 **내용을 줄이고, 층을 나누고, 화살표로 흐름을 만든다.**

## 0. 준비

```powershell
pip install python-pptx
```

렌더 검증은 설치된 PowerPoint COM으로 한다(LibreOffice 없음):
`C:\Users\User\.claude\skills\pptx-lecture-deck\scripts\export_png.ps1`

## 1. 내용부터 확정한다 — 지어내지 말 것

체계도는 "내가 가진 것"을 보여주는 문서라서 **숫자가 틀리면 바로 들킨다.**
말로 기억하지 말고 파일을 세서 쓴다.

| 항목 | 세는 법 |
|---|---|
| 스킬 수 | `ls ~/.claude/skills \| wc -l` |
| 기억(메모리) 건수 | `ls <projects>/memory/*.md \| wc -l` − 1 (MEMORY.md 제외) |
| 진행 프로젝트 | `ls <projects>/memory/project-*.md \| wc -l` |
| 서브에이전트 | `ls ~/.claude/agents/` |
| 플러그인 | `ls ~/.claude/plugins/marketplaces/<마켓>/plugins \| wc -l` |
| 스킬별 사용 횟수 | `~/.claude.json`의 `skillUsage` |
| 예약 작업 | scheduled-tasks MCP의 list (없으면 "0건 · 미사용"으로 솔직히) |

**미사용·인증 대기 항목은 숨기지 말고 그대로 적는다.** 발표에서 질문이 나오면 그 편이 안전하고,
사용자가 빼자고 하면 그때 빼면 된다.

## 2. 레이아웃 두 가지

### (A) 계층 스택 — 흐름이 있을 때 (환경 → 엔진 → 산출물)

```
[헤더 띠]                                   0 ~ 0.95"
[① 라벨] [칩 5개]                           1.08 ~ 1.94"
          ↓
[② 라벨] [칩 5개]                           2.20 ~ 2.86"
          ↓
[③ 라벨] [카드 3장]                         3.12 ~ 4.44"
          ↓
[④ 라벨] [카드 4장]                         4.76 ~ 6.08"
          ↓
[⑤ 라벨] [칩 4개]                           6.44 ~ 7.14"
```

왼쪽 1.42" 라벨 열을 두면 제목 줄이 따로 필요 없어 **세로 0.34"씩 아낀다**(5층이면 1.7").

### (B) 제목 줄 + 전폭 카드 — 층이 3~4개로 적을 때

`band_title()`처럼 번호칩 + 제목 + 회색 부연을 한 줄로 깔고 그 아래 카드 행을 놓는다.
맨 아래에는 한 줄 요약 띠(`strip()`)로 닫는다.

## 3. 조립

`scripts/onepage_lib.py`의 `Deck` 클래스를 쓴다. 예제 2개는 `examples/`에 있다.

```python
from onepage_lib import Deck, BLUE, TEAL, AMBER, FILL_BLUE, BORDER_BLUE

d = Deck()
d.header("AI 하네스 구조도", "지시 주입 · 런타임 · 도구 · 확장 · 산출 경로",
         ["Claude Code · Opus 5", "스킬 20 · 에이전트 5"])
d.band(1.08, 0.86, "1", "지시 주입", "세션마다 자동 적재", BLUE)
d.chips(1.08, 0.86, [("자동 메모리", ["규칙·프로젝트 30건", "매 세션 로드"])],
        BLUE, FILL_BLUE, BORDER_BLUE)
d.arrow(2.00)
d.cards(3.12, 1.32, [(AMBER, "내장 도구", ["Read · Write · Edit", "Bash · PowerShell"])])
d.save(r"D:\사교원 개발그룹\체계도.pptx")
```

치수 감각 (본문 8pt 기준):
- 카드 1장 높이 = `0.22 + 0.20(제목) + 줄수 × 0.17`
- 불릿 5줄 카드 ≈ **1.32"**, 4줄 ≈ 1.15"
- 칩 2줄 ≈ **0.66"**, 3줄 ≈ 0.86"
- 카드 가로 폭이 2.4" 아래면 8pt 한 줄에 한글 15자 정도. 넘으면 줄바꿈돼 카드 밖으로 밀린다.

## 4. 렌더 검증 (필수)

```powershell
powershell -ExecutionPolicy Bypass -File "C:\Users\User\.claude\skills\pptx-lecture-deck\scripts\export_png.ps1" `
  -Deck "D:\...\체계도.pptx" -OutDir "<임시>\png1" -Width 1920 -Height 1080
```

PNG를 Read 도구로 **직접 눈으로 본다.** 이 스킬에서 실제로 걸린 것:

1. **카드 밖으로 흘러나온 마지막 불릿** — 텍스트 상자는 넘쳐도 잘리지 않고 그냥 카드 밖에 그려진다.
   → 문구를 줄이거나(권장) 카드 높이를 키운다.
2. **헤더 오른쪽 수치가 두 줄로 깨짐** — 한 줄에 다 넣으려 하지 말고 처음부터 2줄로 나눈다.
3. **카드 아래 빈 공간** — 텍스트는 위 정렬이라 카드가 크면 아래가 뜬다. 높이를 줄이거나 불릿을 1줄 더 넣어 채운다.
4. 출력 폴더는 **매번 새 폴더**(png1, png2 …). 기존 폴더 덮어쓰기는 막힐 때가 있다.

## 5. 함정

- `run.text`에 `\n`을 넣으면 줄바꿈으로 렌더되긴 하지만, **여러 줄은 문단을 나눠 넣는 편**이 간격 제어가 쉽다.
- `shape.shadow.inherit = False`를 빼먹으면 모든 상자에 기본 그림자가 붙어 조잡해진다.
- 둥근 사각형 곡률은 `adjustments[0]`으로 조절(0.12 = 큰 상자, 0.25~0.35 = 알약 모양).
- 슬라이드 크기는 `prs.slide_width/height`를 EMU로 직접 지정(12192000 × 6858000).
- 한국어 폰트는 `맑은 고딕` 고정. 런마다 `font.name`을 지정하지 않으면 테마 폰트로 떨어진다.
- 파일명·경로에 한글이 있어도 파이썬은 문제없다. 콘솔 출력만 깨져 보일 뿐이다.

## 6. 산출 위치

작업 폴더 최상단에 `<주제>_YYYYMMDD.pptx`로 저장하고, 미리보기 PNG와 함께 사용자에게 전달한다.
생성 스크립트는 같은 폴더에 두어야 다음에 문구만 바꿔 다시 뽑을 수 있다.
