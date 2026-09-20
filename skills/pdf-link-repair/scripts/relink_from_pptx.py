# -*- coding: utf-8 -*-
"""relink_from_pptx.py - PPTX의 하이퍼링크 주소를 읽어, PDF 내보내기에서 빠진 링크를 복원한다.

파워포인트의 PDF 내보내기는 한 쪽에 링크가 둘 이상일 때 일부를 빠뜨리는 일이 있다.
이 스크립트는 PDF 쪽에 보이는 주소 글자와 PPTX의 주소를 대조해, 맞는 것만 붙인다.
대조가 안 되는 주소는 붙이지 않고 보고한다.

사용법
  python relink_from_pptx.py deck.pptx in.pdf out.pdf [도메인 ...]

주의
  - 슬라이드 순서를 바꾼 PPTX는 slideN.xml 파일번호가 쪽 번호와 다르다.
    presentation.xml 의 sldIdLst 순서를 읽어야 한다. (이 스크립트가 그렇게 한다)
  - 파워포인트가 내보낸 PDF의 한글은 NFD로 분해돼 있다. 양쪽을 NFC로 맞춘다.
"""
import re
import sys
import unicodedata
import zipfile
from urllib.parse import unquote

import pymupdf

PPTX, SRC, DST = sys.argv[1], sys.argv[2], sys.argv[3]
HOSTS = tuple(sys.argv[4:]) or ('sakyowon.co.kr', 'wiki.poomasi.org', 'poomasi.org')
URL_RE = re.compile('(?:' + '|'.join(h.replace('.', r'\.') for h in HOSTS) + r')[^\s]*')
PAD = 1.2


def nfc(s):
    return unicodedata.normalize('NFC', s)


# ── 1. 쪽 번호 → 그 쪽 슬라이드의 외부 링크 주소들 ──────────────────────
z = zipfile.ZipFile(PPTX)
pres = z.read('ppt/presentation.xml').decode('utf-8')
prels = z.read('ppt/_rels/presentation.xml.rels').decode('utf-8')
rid2part = dict(re.findall(r'Id="([^"]+)"[^>]*Target="(slides/slide\d+\.xml)"', prels))
order = [rid2part[r] for r in re.findall(r'<p:sldId[^>]*r:id="([^"]+)"', pres) if r in rid2part]

page_urls = {}
for pageno, part in enumerate(order, 1):
    n = re.search(r'slide(\d+)\.xml$', part).group(1)
    srels = z.read(f'ppt/slides/_rels/slide{n}.xml.rels').decode('utf-8')
    tgt = dict(re.findall(r'Id="([^"]+)"[^>]*Target="([^"]+)"[^>]*TargetMode="External"', srels))
    body = z.read(f'ppt/slides/slide{n}.xml').decode('utf-8')
    page_urls[pageno] = [tgt[r] for r in re.findall(r'hlinkClick r:id="([^"]+)"', body) if r in tgt]

# ── 2. PDF 쪽마다 링크 없는 주소 글자를 찾아 붙인다 ──────────────────────
doc = pymupdf.open(SRC)
if doc.page_count != len(page_urls):
    sys.exit(f'쪽수 불일치: PDF {doc.page_count} vs 슬라이드 {len(page_urls)}')

added = skipped = 0
for pno, page in enumerate(doc, 1):
    have = [pymupdf.Rect(l['from']) for l in page.get_links()]
    raw = page_urls[pno]
    cands = [nfc(unquote(u)) for u in raw]
    for blk in page.get_text('dict')['blocks']:
        for ln in blk.get('lines', []):
            text = nfc(''.join(s['text'] for s in ln['spans']))
            m = URL_RE.search(text)
            if not m:
                continue
            r = pymupdf.Rect(ln['bbox'])
            if any(r.intersects(h) for h in have):
                continue
            shown = m.group(0).rstrip('.,)')
            hit = [(len(c), raw[i]) for i, c in enumerate(cands) if shown in c]
            if not hit:
                skipped += 1
                print(f'  p{pno} 대조 실패 - {shown[:60]}')
                continue
            hit.sort(key=lambda t: abs(t[0] - len(shown)))   # 화면 글자와 길이가 가까운 주소
            r.y0 -= PAD
            r.y1 += PAD
            page.insert_link({'kind': pymupdf.LINK_URI, 'from': r, 'uri': hit[0][1]})
            have.append(r)
            added += 1

doc.save(DST, garbage=3, deflate=True)
doc.close()
print(f'복원한 링크 {added}건, 대조 실패 {skipped}건')

# ── 3. 검수 — 보이는 주소와 가는 주소가 같은지 전량 대조 ─────────────────
chk = pymupdf.open(DST)
ok = bad = missing = 0
for pno, page in enumerate(chk, 1):
    have = [pymupdf.Rect(l['from']) for l in page.get_links()]
    words = page.get_text('words')
    for l in page.get_links():
        R = pymupdf.Rect(l['from'])
        uri = nfc(unquote(l.get('uri') or ''))
        txt = nfc(''.join(w[4] for w in words if pymupdf.Rect(w[:4]).intersects(R)))
        m = URL_RE.search(txt)
        if not m:
            continue
        if m.group(0).rstrip('.,)') in uri:
            ok += 1
        else:
            bad += 1
            print(f'  p{pno} 불일치 | 화면 {m.group(0)[:45]} | 링크 {uri[:55]}')
    for w in words:
        if URL_RE.search(nfc(w[4])) and not any(pymupdf.Rect(w[:4]).intersects(h) for h in have):
            missing += 1
print(f'검수: 주소 일치 {ok}건 / 불일치 {bad}건 / 링크 없는 주소 글자 {missing}건')
