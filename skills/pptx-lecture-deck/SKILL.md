---
name: pptx-lecture-deck
description: 자료(PPT/HWP/PDF/웹)를 바탕으로 한국어 강의안 PPTX를 python-pptx로 생성하고, PowerPoint COM으로 PNG 렌더해 텍스트 넘침을 눈으로 검증·교정하는 스킬. "이 자료로 강의안 만들어줘", "질문마다 1쪽씩 PPT로" 같은 요청에 사용. 카드형 레이아웃 자동 높이 계산과 폰트 자동 축소가 핵심.
---

# 강의안 PPTX 만들기 (생성 → 렌더 검증 → 교정)

한국어 PPT는 **만들고 끝내면 반드시 글자가 넘친다.** python-pptx에는 자동 맞춤(autofit)이 사실상 없기 때문에,
"생성 → PNG로 렌더 → 눈으로 확인 → 높이/폰트 교정"의 루프를 도는 것이 이 스킬의 전부다.

## 0. 사전 준비

```powershell
pip install python-pptx    # Pillow도 함께 설치됨 (이미지 크기 계산에 필요)
```

- **LibreOffice는 이 PC에 없다.** soffice로 PDF 변환하려 하지 말 것.
- 렌더 검증은 **설치된 PowerPoint의 COM 자동화**로 한다 (`scripts/export_png.ps1`).

## 1. 원본 자료에서 내용 뽑기

PPTX는 zip이다. 슬라이드별 텍스트를 한 번에 뽑아 전체 구조부터 파악한다.

```python
import zipfile
from xml.etree import ElementTree as ET
A = '{http://schemas.openxmlformats.org/drawingml/2006/main}'
z = zipfile.ZipFile(src)
for i in range(1, n+1):
    t = ET.fromstring(z.read(f'ppt/slides/slide{i}.xml'))
    for p in t.iter(A+'p'):
        print(''.join(x.text or '' for x in p.iter(A+'t')))
```

- 텍스트가 거의 안 나오면 **이미지로 만든 장표**다. `ppt/slides/_rels/slideN.xml.rels`에서
  `../media/*`를 찾아 꺼낸 뒤 **Read 도구로 이미지를 직접 읽어** 내용을 파악한다 (조직도·그래프는 이 방법뿐).
- 꺼낸 이미지 중 조직도·도표는 새 강의안에 그대로 재활용하면 설득력이 커진다.

## 2. 사실관계 보강

원본에 없는 질문(추진 배경, 초기 과정의 갈등, 최근 쟁점 등)은 웹으로 채운다.
학술 PDF는 WebFetch가 "바이너리라 못 읽는다"고 답해도 **로컬에 저장된 경로를 함께 알려주므로,
그 경로를 Read 도구의 `pages` 인자로 읽으면 본문이 보인다.** (pypdf 설치 불필요)

확인되지 않은 사항은 지어내지 말고 **사용자에게 묻고**, 미결 사항은 슬라이드에 "미결/현재진행형"으로 표기한다.

## 3. 레이아웃 원칙 (카드형)

한 장의 구조를 고정하면 13장이든 30장이든 같은 코드로 찍어낼 수 있다.

```
[헤더 띠]  번호칩 + 질문                      ← 높이 1.12"
[답 띠]    한 줄 답 (굵게)                     ← 높이 0.78"
[본문]     2열 × 카드 여러 장                  ← 2.15" ~ 6.85"
[각주]     자료 출처                           ← 6.92"
```

- 슬라이드는 16:9 = `Inches(13.333) × Inches(7.5)`, 좌우 여백 0.55", 본문 폭 12.23"
- 카드 = 배경 사각형 + 상단 색 띠(0.05") + 제목 + 불릿
- 불릿 앞에 `▸`를 직접 붙인다 (python-pptx의 자동 글머리표는 다루기 번거롭다)
- 강조 불릿은 문자열 맨 앞에 `*`를 붙이는 규칙으로 처리 → 렌더 시 굵게+진한 색

## 4. 넘침을 막는 두 장치 (핵심)

`scripts/deck_lib.py`의 `est_lines()` / `card_height()` / `fit_font()`를 그대로 쓴다.

**(1) 줄 수 추정** — 한글은 글자폭이 거의 폰트 크기와 같다.

```python
char_w = size * 0.88 / 72.0        # inch/글자. 0.88은 실측 보정값
per_line = int(width_in / char_w)
lines = ceil(len(text) / per_line)
```

계수 0.80으로 시작했더니 실제보다 줄 수를 적게 잡아 전부 넘쳤다. **0.88이 실전 안전값.**

**(2) 폰트 자동 축소** — 열별 필요 높이를 계산해 11 → 10.5 → 10 → 9.5 → 9 → 8.5pt 순으로 낮춘다.
제목 글자도 `min(13, 본문+2.5)`로 함께 줄여야 효과가 난다 (제목을 13pt로 고정하면 카드 4장에서 무조건 넘친다).

그래도 안 들어가면 **폰트를 더 줄이지 말고 문장을 줄인다.** 8.5pt 아래는 강의안으로 못 쓴다.

## 5. 렌더 검증 루프 (생략 금지)

```powershell
powershell -File scripts\export_png.ps1 -Deck "D:\...\강의안.pptx" -OutDir "...\png1"
```

- 내보낸 `슬라이드N.PNG`를 **Read 도구로 직접 본다.** 텍스트가 카드 밖으로 나갔는지는 눈으로만 확인된다.
- 고칠 때마다 **새 폴더**(png2, png3 …)로 내보낸다. 같은 폴더에 덮어쓰면 이전 파일이 남아 헷갈린다.
- 자주 나오는 두 증상:
  - 카드 아래로 한 줄이 삐져나옴 → 문장 축약 또는 카드 1장을 다른 열로 이동
  - 카드 하나가 열 전체로 늘어나 빈 공간이 큼 → 그 열에 카드를 하나 더 추가하거나 내용을 둘로 쪼갬

## 6. 함정 모음

1. **`$p.Visible = $true` 는 에러난다** — PowerPoint COM은 MsoTriState를 요구한다. 그냥 Visible을 건드리지 말고 열 것.
2. **`Remove-Item "$out\*"` 이 차단될 수 있다** (보호 경로 규칙). 지우지 말고 새 폴더로 내보낼 것.
3. **PowerShell 콘솔에 한국어 파일명이 깨져 보여도 실제 파일은 정상**이다. 깨진 출력 보고 경로를 고치지 말 것.
4. 한글 폰트는 `"맑은 고딕"`을 run마다 `r.font.name`으로 지정한다 (테마 폰트에 맡기면 영문 폰트로 렌더된다).
5. 도형 그림자는 기본이 켜짐 → `shape.shadow.inherit = False`로 꺼야 납작한 카드 디자인이 나온다.
6. 이미지는 `add_picture(..., height=)`로 **높이 기준**으로 넣고 폭은 PIL로 비율 계산한다. 폭 기준으로 넣으면 세로로 긴 조직도가 슬라이드 밖으로 나간다.
7. `Date.now()`류 없이도 되지만, 파일명에 날짜를 넣을 땐 사용자에게 확인한 날짜를 쓴다.

## 7. 결과물 배치

- 강의안은 **원본 자료와 같은 폴더**에 저장한다 (사용자가 원본 옆에서 찾는다).
- 완성 후 SendUserFile로 전달하고, "원본에서 가져온 것 / 웹에서 보강한 것 / 판단해서 처리한 것"을 구분해 보고한다.

## 파일

| 파일 | 용도 |
|---|---|
| `scripts/deck_lib.py` | 색상·para/rect/textbox 헬퍼, est_lines/card_height/fit_font, 카드형 슬라이드 렌더러 |
| `scripts/export_png.ps1` | PowerPoint COM으로 전 슬라이드를 PNG로 내보내기 (한국어 리터럴 없음) |
