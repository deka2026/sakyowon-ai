---
name: pdf-link-repair
description: 파워포인트·한글에서 내보낸 PDF의 하이퍼링크가 안 눌리거나 일부가 빠졌을 때 진단하고 고치는 스킬. "PDF 링크가 안 먹혀", "링크 활성화해서 다시 저장해줘", "주석 링크 살려줘" 같은 요청에 사용. 클릭 영역이 글자와 어긋난 경우와, 내보내기가 링크를 통째로 누락한 경우를 갈라서 처리한다. 순서를 바꾼 PPTX에서 뽑은 PDF는 쪽 번호 매핑을 반드시 발표 순서로 잡아야 한다.
---

# PDF 링크 되살리기

PDF에 링크가 "있는데 안 눌린다"와 "아예 없다"는 원인이 다르고 처방도 다르다. 먼저 어느 쪽인지 센다.

## 0. 준비

```bash
python -c "import pymupdf; print(pymupdf.__version__)"   # 없으면 pip install pymupdf
```

## 1. 진단 — 세 가지를 한 번에 센다

```python
import pymupdf, re, unicodedata
HOST = re.compile(r'(?:example\.com|wiki\.example\.org)[^\s]*')   # 우리 도메인으로
d = pymupdf.open(SRC)
for pno, p in enumerate(d, 1):
    links = [pymupdf.Rect(l['from']) for l in p.get_links()]
    hs = [r.height for r in links]
    miss = [w[4] for w in p.get_text('words')
            if HOST.search(unicodedata.normalize('NFC', w[4]))
            and not any(pymupdf.Rect(w[:4]).intersects(r) for r in links)]
    print(pno, '링크', len(links), '높이', f'{min(hs):.1f}~{max(hs):.1f}' if hs else '-', '링크없는주소', len(miss))
```

판단 기준:

| 증상 | 원인 | 처방 |
|---|---|---|
| 링크 높이가 1~3pt | 주석 사각형이 글자보다 위로 밀림 | **2절** 사각형 재설정 |
| 쪽마다 링크 수가 원본 PPTX보다 적음 | 내보내기가 통째로 누락 | **3절** 원본에서 복원 |
| 링크 없는 주소 글자가 있음 | 애초에 링크를 안 건 자리 | 3절과 같은 방법으로 추가 |

파워포인트 내보내기는 한 쪽에 링크가 둘 이상일 때 하나만 내보내는 일이 있다. PPTX의 `hlinkClick` 수와 PDF의 링크 수를 꼭 비교한다.

```bash
python -c "
import zipfile,re;z=zipfile.ZipFile('deck.pptx')
print(sum(len(re.findall('hlinkClick', z.read(n).decode())) for n in z.namelist() if re.match(r'ppt/slides/slide\d+\.xml$',n)))"
```

## 2. 클릭 영역을 글자에 맞춘다

주소는 건드리지 않고 **세로 범위만** 글자 줄에 맞춘다. 가로 범위는 원본을 지킨다.

```python
PAD, NEAR = 1.2, 8.0
for page in doc:
    lines = [pymupdf.Rect(ln['bbox'])
             for blk in page.get_text('dict')['blocks'] for ln in blk.get('lines', [])]
    for lk in page.get_links():
        L = pymupdf.Rect(lk['from']); cy = (L.y0 + L.y1) / 2
        cand = [ln for ln in lines
                if not (ln.x1 < L.x0 or ln.x0 > L.x1) and ln.y0 - NEAR < cy < ln.y1 + NEAR]
        if cand:                      # 링크가 아니라 글자줄이 기준이다
            ln = min(cand, key=lambda r: abs((r.y0 + r.y1) / 2 - cy))
            lk['from'] = pymupdf.Rect(L.x0, ln.y0 - PAD, ln.y1 + PAD and ln.y1 + PAD, L.x1)  # 아래 주의 참조
        page.update_link(lk)
```

주의 세 가지:

- **링크의 y를 따라가지 말 것.** `min(L.y0, ln.y0)`처럼 원래 링크와 합집합을 내면, 위로 밀린 만큼 사각형이 커져 윗줄(각주 위의 강조 띠 등)까지 눌리게 된다. 글자줄 bbox만 쓴다.
- **words가 아니라 lines를 쓴다.** 단어 단위로 합집합을 내면 이웃 줄을 끌어와 높이가 배로 뛴다.
- 한 줄에 링크가 여럿이면 가로로는 안 겹치므로 그대로 두면 된다. 세로로 겹치는 경우만 가운데에서 가른다.

## 3. 빠진 링크를 원본 PPTX에서 복원한다

PDF에 보이는 주소 글자와 PPTX의 하이퍼링크 주소를 대조해, 맞는 것만 붙인다. 대조가 안 되면 붙이지 말고 보고한다.

### 3-1. 쪽 번호 매핑 — 여기서 제일 많이 틀린다

`ppt/slides/slideN.xml`의 **N은 발표 순서가 아니다.** 슬라이드 순서를 한 번이라도 바꾸면 파일 번호는 그대로고 순서만 바뀐다. 파일 번호를 쪽 번호로 쓰면 엉뚱한 주소가 붙는다.

```python
pres = z.read('ppt/presentation.xml').decode()
rels = z.read('ppt/_rels/presentation.xml.rels').decode()
rid2part = dict(re.findall(r'Id="([^"]+)"[^>]*Target="(slides/slide\d+\.xml)"', rels))
order = [rid2part[r] for r in re.findall(r'<p:sldId[^>]*r:id="([^"]+)"', pres) if r in rid2part]
# order[i] 가 (i+1)쪽의 슬라이드 파트다
```

각 슬라이드의 주소는 본문의 `hlinkClick r:id` 등장 순서로 뽑는다.

```python
n = re.search(r'slide(\d+)\.xml$', part).group(1)
srels = z.read(f'ppt/slides/_rels/slide{n}.xml.rels').decode()
tgt = dict(re.findall(r'Id="([^"]+)"[^>]*Target="([^"]+)"[^>]*TargetMode="External"', srels))
urls = [tgt[r] for r in re.findall(r'hlinkClick r:id="([^"]+)"', z.read(f'ppt/slides/slide{n}.xml').decode()) if r in tgt]
```

### 3-2. NFC 정규화 — 한글 주소가 안 맞는 진짜 이유

파워포인트가 내보낸 PDF의 한글은 **NFD로 분해**되어 있다. PPTX의 주소는 퍼센트 인코딩된 NFC다. 둘 다 `unicodedata.normalize('NFC', unquote(u))`로 맞춰야 대조된다. 이걸 안 하면 한글 경로가 든 주소는 100% 대조 실패한다.

### 3-3. 붙이기

```python
shown = URL_RE.search(unicodedata.normalize('NFC', 줄_글자)).group(0).rstrip('.,)')
hit = [(len(c), raw[i]) for i, c in enumerate(cands) if shown in c]
hit.sort(key=lambda t: abs(t[0] - len(shown)))      # 여럿이면 화면 글자와 길이가 가까운 것
page.insert_link({'kind': pymupdf.LINK_URI, 'from': 줄_bbox_패딩, 'uri': hit[0][1]})
```

짧은 주소(`example.com`)는 긴 주소의 부분문자열이라 여러 개에 걸린다. **길이가 가까운 것**을 고르는 규칙이 필요하다.

## 4. 검수 — 세 가지를 반드시 다 센다

```python
# ① 주소가 바뀌지 않았나
# ② 높이가 4pt 미만인 링크가 없나
# ③ 링크의 글자와 연결 주소가 실제로 일치하나  ← 이것이 핵심
txt = ''.join(w[4] for w in p.get_text('words') if pymupdf.Rect(w[:4]).intersects(R))
assert HOST.search(NFC(txt)).group(0) in NFC(unquote(uri))
```

①②만 보면 "엉뚱한 주소가 예쁘게 붙은" 상태를 통과시킨다. ③을 전 링크에 돌려 불일치 0을 확인한 뒤에야 완료다.

### 검수기가 잘못 짚는 두 경우

전량 대조를 돌리면 아래 둘은 **오탐**이다. 실제 링크는 멀쩡하다.

- **주소 뒤에 공백 없이 글자가 붙은 줄** — `sakyowon.co.kr/academy-site/신청은검증을...` 처럼 정규식이
  뒤 문장까지 삼킨다. PDF 글자 추출이 공백을 흘린 탓이다.
- **리드 문장의 주소와 각주 링크가 미묘하게 다른 쪽** — 화면엔 `.../#home`, 링크는 기본 주소인 식.
  둘 다 같은 사이트를 가리키면 문제 없다.

불일치가 뜨면 그 쪽을 그려서 눈으로 확인하고, 위 두 경우면 넘어간다. 진짜 사고는
**다른 쪽의 주소가 붙은 경우**이고, 그건 3-1절 쪽 번호 매핑이 틀렸을 때만 생긴다.

마지막으로 한 쪽을 그려서 눈으로 본다.

```python
for l in p.get_links(): p.draw_rect(pymupdf.Rect(l['from']), color=(1,0,0), width=1)
p.get_pixmap(dpi=110).save('check.png')
```

## 5. 되풀이를 막는 법

원본 PPTX에서 PDF를 새로 뽑을 때마다 같은 문제가 재발한다. 배포본을 만드는 사람에게 이렇게 알린다.

- 완성된 PDF를 보관해 쓰고, 다시 뽑았으면 이 절차를 한 번 돌린다
- 파일이 열려 있으면 덮어쓰기가 막힌다(`~$` 잠금 파일 확인). 새 이름으로 저장한 뒤 닫히면 교체한다

## 함정 모음

1. 슬라이드 순서를 바꾼 PPTX → **파일번호 ≠ 쪽번호**. `presentation.xml` 순서를 읽는다
2. PDF 한글은 **NFD** — NFC로 맞추지 않으면 대조 전패
3. 링크 사각형을 원래 링크와 합집합 내지 말 것 — 윗줄까지 눌린다
4. `words`가 아니라 `lines` 기준 — 이웃 줄을 끌어오지 않는다
5. 짧은 주소는 긴 주소에 포함됨 — 길이가 가까운 것을 고른다
6. 검수는 "링크가 있나"가 아니라 "**보이는 주소와 가는 주소가 같나**"로

---

실전 기록: 2026-09-19 마을강사단 AI교육 입문 PDF 26쪽. 링크 53개가 높이 2.8pt로 사실상 안 눌리던 것을 고치고,
순서 재배치 후 재내보내기에서 쪽당 하나씩 빠진 26건을 복원해 **149개 전부 주소 일치**로 맞췄다.
