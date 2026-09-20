# -*- coding: utf-8 -*-
"""PDF 링크 활성화 — 링크 사각형을 실제 글자에 맞춰 다시 잡고, 빠진 링크를 채운다.

PowerPoint에서 내보낸 PDF는 링크 주석의 세로 위치가 글자보다 위로 밀려
클릭 영역이 1~2pt만 겹치는 일이 잦다. 이 스크립트는
  ① 기존 링크마다 같은 줄의 글자 상자를 찾아 세로 범위를 덮도록 넓히고
  ② URL 글자인데 링크가 없는 자리에 새 링크를 만든다.
URI 값과 가로 범위는 원본 그대로 둔다.
"""
import sys
import pymupdf

SRC, DST = sys.argv[1], sys.argv[2]
PAD = 1.2          # 글자 위아래 여유 (pt)
NEAR = 8.0         # 링크 기준 세로 탐색 범위 (pt)

# 링크가 빠진 URL 글자 — (페이지번호 1-base, 글자 조각, 주소)
MISSING = [
    (1,  'wiki.poomasi.org',            'https://wiki.poomasi.org'),
    (20, 'sakyowon.co.kr/academy-site', 'https://sakyowon.co.kr/academy-site/'),
]

doc = pymupdf.open(SRC)
widened = added = 0

for pno, page in enumerate(doc, 1):
    words = page.get_text('words')
    links = page.get_links()
    if not links:
        continue

    # 글자를 줄 단위로 모은다 — 옆 줄을 끌어오지 않게
    lines = []
    for blk in page.get_text('dict')['blocks']:
        for ln in blk.get('lines', []):
            lines.append(pymupdf.Rect(ln['bbox']))

    new_rects = []
    for lk in links:
        L = pymupdf.Rect(lk['from'])
        cy = (L.y0 + L.y1) / 2
        # 가로로 겹치고 세로로 가장 가까운 줄 하나만 고른다
        cand = [ln for ln in lines
                if not (ln.x1 < L.x0 or ln.x0 > L.x1)
                and ln.y0 - NEAR < cy < ln.y1 + NEAR]
        if cand:
            # 링크가 아니라 글자줄이 기준이다 — 링크는 위로 밀려 있으므로 따라가지 않는다
            ln = min(cand, key=lambda r: abs((r.y0 + r.y1) / 2 - cy))
            y0, y1 = ln.y0 - PAD, ln.y1 + PAD
        else:
            y0, y1 = L.y0 - PAD, L.y1 + PAD
        new_rects.append(pymupdf.Rect(L.x0, y0, L.x1, y1))

    # 서로 겹치면 가운데에서 갈라 침범을 막는다
    for i in range(len(new_rects)):
        for j in range(i + 1, len(new_rects)):
            a, b = new_rects[i], new_rects[j]
            if a.intersects(b):
                if a.y1 > b.y0 and a.y0 < b.y0:
                    mid = (a.y1 + b.y0) / 2
                    a.y1, b.y0 = mid, mid

    for lk, r in zip(links, new_rects):
        if abs(r.height - pymupdf.Rect(lk['from']).height) > 0.1:
            widened += 1
        lk['from'] = r
        page.update_link(lk)

    # 빠진 링크 채우기
    for mp, frag, uri in MISSING:
        if mp != pno:
            continue
        for w in words:
            if frag in w[4]:
                r = pymupdf.Rect(w[:4])
                r.y0 -= PAD
                r.y1 += PAD
                page.insert_link({'kind': pymupdf.LINK_URI, 'from': r, 'uri': uri})
                added += 1
                break

doc.save(DST, garbage=3, deflate=True)
doc.close()

# 검수 — 다시 열어 링크 수와 글자 덮임을 확인한다
chk = pymupdf.open(DST)
total = 0
thin = 0
uncovered = 0
for page in chk:
    ls = page.get_links()
    total += len(ls)
    words = page.get_text('words')
    for lk in ls:
        R = pymupdf.Rect(lk['from'])
        if R.height < 4.0:
            thin += 1
        hit = [w for w in words
               if not (w[2] < R.x0 or w[0] > R.x1) and w[3] > R.y0 and w[1] < R.y1]
        if hit:
            u = pymupdf.Rect(hit[0][:4])
            for w in hit[1:]:
                u |= pymupdf.Rect(w[:4])
            if min(R.y1, u.y1) - max(R.y0, u.y0) < u.height * 0.8:
                uncovered += 1
print(f'넓힌 링크 {widened}건 / 새로 만든 링크 {added}건')
print(f'검수: 총 링크 {total}건, 높이 4pt 미만 {thin}건, 글자를 80% 미만 덮는 링크 {uncovered}건')
