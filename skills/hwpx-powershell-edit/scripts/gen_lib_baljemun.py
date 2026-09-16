# -*- coding: utf-8 -*-
"""Subclass of HwpxDoc tuned to the 공론장 발제문 template (본문폭 46490)."""
import re, sys, zipfile
sys.path.insert(0, r'C:\Users\User\.claude\skills\hwpx-powershell-edit\scripts')
from hwpx_gen import HwpxDoc, esc

W = 46490  # pagePr 59528 - margin 6519*2

STYLES = {
    'title':  dict(parapr='22', style='24', charpr='25'),
    'h1':     dict(parapr='26', style='23', num_charpr='27', charpr='28'),
    'dept':   dict(parapr='23', style='23', charpr='23'),
    'team':   dict(parapr='23', style='23', charpr='24'),
    'band':   dict(parapr='23', style='23', charpr='23'),
    'body':   dict(parapr='21', style='23', charpr='22'),
    'bullet': dict(b1=('●','20','21'), b2=('○','21','21'), b3=('–','20','21'),
                   b4=('▸','20','21'), em_charpr='24'),
    'cell':   dict(parapr='30', style='23', charpr='11',
                   header_border='6', body_border='7', tbl_border='5'),
    'wrap':   dict(parapr='21', style='23', charpr='22'),
}
HDR_CHARPR = '32'   # 10pt bold
CELL_L = '25'       # left-aligned cell paraPr
CELL_C = '30'       # centered cell paraPr
RED_MARK = '@@'     # paragraph prefix -> red cell text (when RED_ON)
RED_ON = True
RED_CELL_CHARPR = '77'  # red twin of cell charPr 11 in the 발제문 template


class Doc(HwpxDoc):
    def __init__(self, template):
        self.template = template
        self.s = STYLES
        self.out = []
        self._titled = False
        with zipfile.ZipFile(template) as z:
            src = z.read('Contents/section0.xml').decode('utf-8')
        m = re.match(r'(<\?xml[^>]*\?>)\s*(<hs:sec[^>]*>)', src, re.S)
        self.xml_decl, self.sec_open = m.group(1), m.group(2)
        self.secpr = re.search(r'<hp:secPr.*?</hp:secPr>', src, re.S).group(0)
        m = re.search(r'<hp:ctrl>\s*<hp:colPr[^>]*/>\s*</hp:ctrl>', src, re.S)
        self.colpr = m.group(0) if m else ''
        assert self.colpr, 'colPr not found'
        self.pagenum = '<hp:ctrl><hp:pageNum pos="BOTTOM_CENTER" formatType="DIGIT" sideChar="-"/></hp:ctrl>'

    def title(self, t):
        st = self.s['title']
        runs = ('<hp:run charPrIDRef="25">' + self.secpr + self.colpr + '</hp:run>'
                '<hp:run charPrIDRef="25">' + self.pagenum +
                '<hp:t>%s</hp:t></hp:run>' % esc(t))
        self._p(st['parapr'], st['style'], runs)
        self._titled = True

    def subtitle(self, t):
        self._p('22', '24', '<hp:run charPrIDRef="18"><hp:t>%s</hp:t></hp:run>' % esc(t))

    def right(self, t):
        self._p('24', '23', '<hp:run charPrIDRef="22"><hp:t>%s</hp:t></hp:run>' % esc(t))

    def table(self, rows, widths, header_h=900, body_h=900, header_rows=(0,), align=None):
        """align: string of 'C'/'L' per column (default all C)."""
        cs = self.s['cell']
        if align is None:
            align = 'C' * len(widths)
        nrow = len(rows)
        total_h = sum(header_h if r in header_rows else body_h for r in range(nrow))
        trs = []
        for r, row in enumerate(rows):
            border = cs['header_border'] if r in header_rows else cs['body_border']
            h = header_h if r in header_rows else body_h
            cells, col = [], 0
            for cell_def in row:
                paras, span = (cell_def if isinstance(cell_def, tuple) else (cell_def, 1))
                if isinstance(paras, str):
                    paras = [paras]
                c = col
                width = sum(widths[c:c + span])
                col += span
                if r in header_rows:
                    pp, cp = CELL_C, HDR_CHARPR
                else:
                    pp = CELL_L if (span == 1 and align[c] == 'L') else CELL_C
                    cp = cs['charpr']
                ps = ''
                for p in paras:
                    cpx = cp
                    if p.startswith(RED_MARK):
                        p = p[len(RED_MARK):]
                        if RED_ON:
                            cpx = RED_CELL_CHARPR
                    ps += ('<hp:p id="0" paraPrIDRef="%s" styleIDRef="%s" pageBreak="0" columnBreak="0" merged="0">'
                           '<hp:run charPrIDRef="%s"><hp:t>%s</hp:t></hp:run></hp:p>'
                           % (pp, cs['style'], cpx, esc(p)))
                cells.append(
                    '<hp:tc name="" header="0" hasMargin="1" protect="0" editable="0" dirty="0" borderFillIDRef="%s">'
                    '<hp:subList id="" textDirection="HORIZONTAL" lineWrap="BREAK" vertAlign="CENTER" '
                    'linkListIDRef="0" linkListNextIDRef="0" textWidth="0" textHeight="0" hasTextRef="0" hasNumRef="0">'
                    '%s</hp:subList><hp:cellAddr colAddr="%d" rowAddr="%d"/><hp:cellSpan colSpan="%d" rowSpan="1"/>'
                    '<hp:cellSz width="%d" height="%d"/><hp:cellMargin left="141" right="141" top="70" bottom="70"/></hp:tc>'
                    % (border, ps, c, r, span, width, h))
            assert col == len(widths), 'row %d colspan sum %d != %d' % (r, col, len(widths))
            trs.append('<hp:tr>' + ''.join(cells) + '</hp:tr>')
        tbl = ('<hp:tbl id="0" zOrder="0" numberingType="TABLE" textWrap="TOP_AND_BOTTOM" textFlow="BOTH_SIDES" '
               'lock="0" dropcapstyle="None" pageBreak="CELL" repeatHeader="1" rowCnt="%d" colCnt="%d" '
               'cellSpacing="0" borderFillIDRef="%s" noAdjust="0">'
               '<hp:sz width="%d" widthRelTo="ABSOLUTE" height="%d" heightRelTo="ABSOLUTE" protect="0"/>'
               '<hp:pos treatAsChar="0" affectLSpacing="0" flowWithText="1" allowOverlap="0" holdAnchorAndSO="0" '
               'vertRelTo="PARA" horzRelTo="PARA" vertAlign="TOP" horzAlign="LEFT" vertOffset="0" horzOffset="0"/>'
               '<hp:outMargin left="0" right="0" top="0" bottom="0"/>'
               '<hp:inMargin left="141" right="141" top="70" bottom="70"/>'
               % (nrow, len(widths), cs['tbl_border'], sum(widths), total_h)) + ''.join(trs) + '</hp:tbl>'
        w = self.s['wrap']
        self._p(w['parapr'], w['style'],
                '<hp:run charPrIDRef="%s">%s<hp:t/></hp:run>' % (w['charpr'], tbl))


def patch_header_12pt(path, ids=('20', '21', '22', '23', '24'), height='1200'):
    """본문 글자를 12pt로. 표 셀 charPr(11·32)은 10pt 유지."""
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        blobs = {n: z.read(n) for n in names}
    h = blobs['Contents/header.xml'].decode('utf-8')
    n = 0
    for i in ids:
        pat = re.compile(r'(<hh:charPr id="%s" [^>]*?height=")(\d+)(")' % i)
        h, k = pat.subn(lambda m: m.group(1) + height + m.group(3), h, count=1)
        n += k
    blobs['Contents/header.xml'] = h.encode('utf-8')
    with zipfile.ZipFile(path, 'w') as o:
        o.writestr(zipfile.ZipInfo('mimetype'), blobs['mimetype'], zipfile.ZIP_STORED)
        for nm in names:
            if nm != 'mimetype':
                o.writestr(nm, blobs[nm], zipfile.ZIP_DEFLATED)
    return n


def widths(*fracs):
    """비율 리스트를 본문폭에 맞춘 정수 폭으로."""
    tot = sum(fracs)
    ws = [int(W * f / tot) for f in fracs]
    ws[-1] += W - sum(ws)
    return ws
