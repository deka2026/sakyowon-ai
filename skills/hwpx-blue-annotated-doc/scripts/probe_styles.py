# -*- coding: utf-8 -*-
"""템플릿 hwpx의 서식 ID와 본문폭을 채록한다.

사용:  python probe_styles.py "템플릿.hwpx"

출력한 값을 hwpx_blue_gen.py 상단 상수에 옮겨 적는다.
한글이 재저장한 파일은 ID가 재매핑되므로 편집할 때마다 다시 돌릴 것.
"""
import io, re, sys, zipfile
import xml.etree.ElementTree as ET

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HP = 'http://www.hancom.co.kr/hwpml/2011/paragraph'


def txt(e):
    return ''.join(x.text or '' for x in e.iter('{%s}t' % HP))


def main(path):
    with zipfile.ZipFile(path) as z:
        sec = z.read('Contents/section0.xml').decode('utf-8')
        hdr = z.read('Contents/header.xml').decode('utf-8')

    pg = re.search(r'<hp:pagePr[^>]*width="(\d+)"', sec)
    mg = re.search(r'<hp:margin[^>]*left="(\d+)" right="(\d+)"', sec)
    if pg and mg:
        body_w = int(pg.group(1)) - int(mg.group(1)) - int(mg.group(2))
        print('본문폭(BODY_W 상한) =', body_w)
    ls = [int(x) for x in re.findall(r'<hp:lineseg [^>]*horzsize="(\d+)"', sec)]
    if ls:
        print('실측 horzsize(최대) =', max(ls), '  ← 표 전체폭은 이 값 이하로')

    print('charPr 개수 =', len(re.findall(r'<hh:charPr id="(\d+)"', hdr)),
          '| charProperties itemCnt =',
          re.search(r'<hh:charProperties itemCnt="(\d+)"', hdr).group(1))
    print('paraPr 개수 =', len(re.findall(r'<hh:paraPr id="(\d+)"', hdr)))
    print('bold 사용 charPr:', [m.group(1) for m in
                                re.finditer(r'<hh:charPr id="(\d+)"[^>]*>(?:(?!</hh:charPr>).)*?<hh:bold/>',
                                            hdr, re.S)] or '없음')

    root = ET.fromstring(sec)
    print()
    print('--- 상위 문단 (처음 40개) ---')
    print('idx  paraPr style  runs(charPr)          텍스트')
    for i, p in enumerate(list(root)[:40]):
        tb = p.find('.//{%s}tbl' % HP)
        runs = [r.get('charPrIDRef') for r in p.findall('./{%s}run' % HP)]
        mark = 'TBL' if tb is not None else '   '
        print('%3d  %-6s %-5s %-20s %s %s' % (
            i, p.get('paraPrIDRef'), p.get('styleIDRef'), ','.join(runs), mark,
            '' if tb is not None else txt(p)[:44]))

    print()
    print('--- 표 서식 (본문 첫 표 — 표지 배너 표는 건너뜀) ---')
    for i, p in enumerate(root):
        tb = p.find('.//{%s}tbl' % HP)
        if tb is None or i < 3:
            continue
        print('wrap paraPr=%s charPr=%s' % (p.get('paraPrIDRef'),
                                            p.find('./{%s}run' % HP).get('charPrIDRef')))
        print('tbl borderFillIDRef=%s  sz.width=%s  treatAsChar=%s' % (
            tb.get('borderFillIDRef'),
            tb.find('./{%s}sz' % HP).get('width'),
            tb.find('./{%s}pos' % HP).get('treatAsChar')))
        trs = tb.findall('./{%s}tr' % HP)
        for r, label in ((0, '머리행'), (1, '본문행')):
            if r >= len(trs):
                continue
            tc = trs[r].find('./{%s}tc' % HP)
            cp = tc.find('.//{%s}p' % HP)
            print('%s: borderFill=%s cellParaPr=%s cellCharPr=%s' % (
                label, tc.get('borderFillIDRef'), cp.get('paraPrIDRef'),
                cp.find('./{%s}run' % HP).get('charPrIDRef')))
        print('열 폭:', [c.get('width') for c in
                       trs[0].findall('./{%s}tc/{%s}cellSz' % (HP, HP))])
        break


if __name__ == '__main__':
    main(sys.argv[1])
