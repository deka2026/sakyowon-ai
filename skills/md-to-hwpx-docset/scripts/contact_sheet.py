# -*- coding: utf-8 -*-
"""PDF 조판 눈 검수 도구.

    python contact_sheet.py <문서.pdf> <out.pdf>            # 전 쪽 접촉시트 + 얇은 쪽 경고
    python contact_sheet.py <문서.pdf> <out.pdf> --zoom 3,5 # 특정 쪽 확대 렌더

접촉시트로 빈 쪽·넘침을 한눈에 보고, 의심스러운 쪽만 --zoom 으로 확대해 읽는다.
출력 경로는 **짧게** 쓸 것 — 윈도 MAX_PATH(260자)를 넘으면 파이썬이 파일을 못 연다.
"""
import argparse, sys
import pymupdf


def contact(src, out, cols=5, dpi=46, thin=120):
    d = pymupdf.open(src)
    z = dpi / 72
    p0 = d[0].get_pixmap(matrix=pymupdf.Matrix(z, z))
    w, h = p0.width, p0.height
    rows = (len(d) + cols - 1) // cols
    sheet = pymupdf.open()
    pg = sheet.new_page(width=w * cols + 6 * (cols + 1), height=(h + 16) * rows + 6)
    for i, p in enumerate(d):
        pix = p.get_pixmap(matrix=pymupdf.Matrix(z, z))
        r, c = divmod(i, cols)
        x, y = 6 + c * (w + 6), 6 + r * (h + 16)
        pg.insert_image(pymupdf.Rect(x, y, x + w, y + h), pixmap=pix)
        pg.insert_text((x + 2, y + h + 11), 'p%d' % (i + 1), fontsize=9)
    sheet.save(out)
    print('쪽 %d개 -> %s' % (len(d), out))
    for i, p in enumerate(d):
        t = p.get_text().strip()
        if len(t) < thin:
            print('  얇은 쪽 p%d: %d자  %r' % (i + 1, len(t), t[:70]))
    return len(d)


def zoom(src, out, pages, scale=1.6):
    d = pymupdf.open(src)
    n = pymupdf.open()
    for i in pages:
        pix = d[i - 1].get_pixmap(matrix=pymupdf.Matrix(scale, scale))
        pg = n.new_page(width=pix.width, height=pix.height)
        pg.insert_image(pymupdf.Rect(0, 0, pix.width, pix.height), pixmap=pix)
    n.save(out)
    print('확대 %d쪽 -> %s' % (len(pages), out))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('out')
    ap.add_argument('--zoom', help='확대할 쪽 번호 (예: 3,5,17)')
    ap.add_argument('--scale', type=float, default=1.6)
    a = ap.parse_args()
    if a.zoom:
        zoom(a.src, a.out, [int(x) for x in a.zoom.split(',')], a.scale)
    else:
        contact(a.src, a.out)
    return 0


if __name__ == '__main__':
    sys.exit(main())
