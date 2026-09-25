# -*- coding: utf-8 -*-
"""생성한 .hwpx 구조 검증.

    python verify.py <문서.hwpx> [--body-width 46490] [--articles 72]

XML 유효성만으로는 '한글에서 열리는지'를 보장하지 못한다. 이 검증을 통과한 뒤
반드시 pagecount_auto.ps1 -Pdf 로 실제 개통과 조판까지 확인할 것.
"""
import argparse, re, sys, zipfile
from xml.dom import minidom


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('path')
    ap.add_argument('--body-width', type=int, default=46490)
    ap.add_argument('--articles', type=int, default=0,
                    help='조문 문서라면 기대하는 마지막 조 번호 (예: 72)')
    a = ap.parse_args()

    bad = []
    with zipfile.ZipFile(a.path) as z:
        names = z.namelist()
        sec = z.read('Contents/section0.xml').decode('utf-8')
        hdr = z.read('Contents/header.xml').decode('utf-8')
        hpf = z.read('Contents/content.hpf').decode('utf-8')
        stored = z.getinfo('mimetype').compress_type == zipfile.ZIP_STORED if 'mimetype' in names else False

    minidom.parseString(sec.encode('utf-8'))
    print('XML 유효: OK')
    print('mimetype 첫 엔트리/STORED:', names[0] == 'mimetype', '/', stored)
    if names[0] != 'mimetype' or not stored:
        bad.append('OCF 패키징')

    tbls = re.findall(r'<hp:tbl\b.*?</hp:tbl>', sec, re.S)
    tp = sum(t.count('<hp:p ') for t in tbls)
    tc = sum(t.count('<hp:tc ') for t in tbls)
    ratio = round(tp / tc, 2) if tc else None
    print('표 %d개 / 셀 %d / 표내 문단 %d => paras_per_cell %s' % (len(tbls), tc, tp, ratio))
    if tc and not (0.9 <= tp / tc <= 1.6):
        bad.append('셀당 문단수 %s (셀에 문자열을 넘긴 버그 의심)' % ratio)

    for i, t in enumerate(tbls, 1):
        w = int(re.search(r'<hp:sz width="(\d+)"', t).group(1))
        rc = int(re.search(r'rowCnt="(\d+)"', t).group(1))
        rows = t.count('<hp:tr>')
        tac = re.search(r'treatAsChar="(\d)"', t).group(1)
        flags = []
        if w > a.body_width:
            flags.append('본문폭 초과')
        if rc != rows:
            flags.append('rowCnt 불일치')
        if tac != '0':
            flags.append('treatAsChar=1 → 표가 쪽 경계에서 안 갈림')
        print('  표%-2d width=%d rowCnt=%d(실제 %d) treatAsChar=%s %s'
              % (i, w, rc, rows, tac, ('← ' + ', '.join(flags)) if flags else ''))
        bad.extend('표%d %s' % (i, f) for f in flags)

    caps = dict(charPr=r'<hh:charProperties itemCnt="(\d+)"',
                paraPr=r'<hh:paraProperties itemCnt="(\d+)"',
                style=r'<hh:styles itemCnt="(\d+)"',
                borderFill=r'<hh:borderFills itemCnt="(\d+)"')
    refs = dict(charPr=r'charPrIDRef="(\d+)"', paraPr=r'paraPrIDRef="(\d+)"',
                style=r'styleIDRef="(\d+)"', borderFill=r'borderFillIDRef="(\d+)"')
    for nm in caps:
        m = re.search(caps[nm], hdr)
        if not m:
            continue
        mx = int(m.group(1))
        used = {int(x) for x in re.findall(refs[nm], sec)}
        over = sorted(x for x in used if x >= mx)
        print('%s: itemCnt %d, 사용 최대 %s %s' % (nm, mx, max(used) if used else '-',
                                                 ('← 미해결 %s' % over) if over else 'OK'))
        if over:
            bad.append('%s 미해결 참조 %s' % (nm, over))

    print('secPr 존재:', '<hp:secPr' in sec)
    print('linesegarray 잔존:', sec.count('<hp:linesegarray'))
    print('opf:title:', re.search(r'<opf:title>(.*?)</opf:title>', hpf).group(1))
    print('Preview 잔재:', [n for n in names if n.startswith('Preview/')] or '없음')

    txt = re.sub(r'<[^>]+>', '', ''.join(re.findall(r'<hp:t[^>]*>(.*?)</hp:t>', sec, re.S)))
    md_left = txt.count('**') + txt.count('|')
    print('마크다운 잔재(** 와 |):', md_left)
    if md_left:
        bad.append('마크다운 잔재 %d' % md_left)

    if a.articles:
        nums = sorted({int(n) for n in re.findall(r'제(\d+)조\(', txt)})
        missing = [n for n in range(1, a.articles + 1) if n not in nums]
        print('조문: %d개 (제%d조~제%d조), 누락 %s'
              % (len(nums), min(nums), max(nums), missing or '없음'))
        if missing:
            bad.append('조문 누락 %s' % missing)

    print()
    if bad:
        print('문제 %d건: %s' % (len(bad), '; '.join(bad)))
        return 1
    print('구조 검증 통과 — 이제 pagecount_auto.ps1 -Pdf 로 실제 개통·조판을 확인하세요.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
