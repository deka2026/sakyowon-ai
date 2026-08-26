# -*- coding: utf-8 -*-
"""Generate a NEW .hwpx document from a template .hwpx (styles reused, body replaced).

Usage (as library):
    from hwpx_gen import HwpxDoc
    doc = HwpxDoc(r"template.hwpx")          # default style ids fit sakyowon templates
    doc.title("Doc title")
    doc.h1("1.", "Chapter")                  # doc.h1("2.", "...", page_break=True)
    doc.dept("Section heading")              # numbered-circle style
    doc.team("Sub heading")
    doc.band("Band subhead")
    doc.b1("bullet"); doc.b2("o bullet"); doc.b3("dash"); doc.b4("arrow")
    doc.blank()
    doc.table(rows, widths, header_rows=(0,))  # cell = [paras] or ([paras], colspan)
    doc.save(r"out.hwpx")

Style IDs are template-specific. Defaults below were probed from
'재생에너지_사업_기반_기본사회_전략...hwpx' (sakyowon standard plan template).
For another template, probe with show_paragraph.ps1 (hwpx-powershell-edit skill)
and pass a styles dict to HwpxDoc(template, styles={...}).
"""
import re, zipfile, io

DEFAULT_STYLES = {
    'title':  dict(parapr='31', style='24', charpr='23'),
    'h1':     dict(parapr='28', style='23', num_charpr='31', charpr='30'),
    'dept':   dict(parapr='23', style='23', charpr='15'),
    'team':   dict(parapr='27', style='23', charpr='17'),
    'band':   dict(parapr='26', style='23', charpr='16'),
    'body':   dict(parapr='21', style='23', charpr='8'),
    'bullet': dict(b1=('●','10','21'), b2=('○','12','21'), b3=('–','10','22'), b4=('▸','18','22'), em_charpr='11'),
    'cell':   dict(parapr='33', style='23', charpr='14', header_border='6', body_border='7', tbl_border='5'),
    'wrap':   dict(parapr='20', style='23', charpr='8'),
}

def esc(t):
    # < > are forbidden in content; & must be escaped exactly once
    return t.replace('&', '&amp;')

class HwpxDoc:
    def __init__(self, template_path, styles=None):
        self.template = template_path
        self.s = styles or DEFAULT_STYLES
        with zipfile.ZipFile(template_path) as z:
            src = z.read('Contents/section0.xml').decode('utf-8')
        m = re.match(r'(<\?xml[^>]*\?>)(<hs:sec[^>]*>)', src)
        self.xml_decl, self.sec_open = m.group(1), m.group(2)
        self.secpr = re.search(r'<hp:secPr.*?</hp:secPr>', src, re.S).group(0)
        mcol = re.search(r'<hp:ctrl><hp:colPr[^>]*/></hp:ctrl>', src)
        self.colpr = mcol.group(0) if mcol else ''
        self.out = []
        self._titled = False

    def _p(self, parapr, style, runs, page_break=False):
        pb = '1' if page_break else '0'
        self.out.append('<hp:p id="0" paraPrIDRef="%s" styleIDRef="%s" pageBreak="%s" columnBreak="0" merged="0">%s</hp:p>'
                        % (parapr, style, pb, runs))

    def title(self, t):
        st = self.s['title']
        runs = ('<hp:run charPrIDRef="7">' + self.secpr + self.colpr + '</hp:run>'
                '<hp:run charPrIDRef="%s"><hp:t>%s</hp:t></hp:run>' % (st['charpr'], esc(t)))
        self._p(st['parapr'], st['style'], runs)
        self._titled = True

    def h1(self, num, t, page_break=False):
        st = self.s['h1']
        runs = ('<hp:run charPrIDRef="%s"><hp:t>%s </hp:t></hp:run>'
                '<hp:run charPrIDRef="%s"><hp:t>%s</hp:t></hp:run>'
                % (st['num_charpr'], num, st['charpr'], esc(t)))
        self._p(st['parapr'], st['style'], runs, page_break)

    def _simple(self, key, t):
        st = self.s[key]
        self._p(st['parapr'], st['style'],
                '<hp:run charPrIDRef="%s"><hp:t>%s</hp:t></hp:run>' % (st['charpr'], esc(t)))

    def dept(self, t): self._simple('dept', t)
    def team(self, t): self._simple('team', t)
    def band(self, t): self._simple('band', t)

    def _bullet(self, kind, t, lead=None):
        marker, mcp, parapr = self.s['bullet'][kind]
        body_cp = self.s['body']['charpr']
        runs = '<hp:run charPrIDRef="%s"><hp:t>%s </hp:t></hp:run>' % (mcp, marker)
        if lead:
            runs += '<hp:run charPrIDRef="%s"><hp:t>%s</hp:t></hp:run>' % (self.s['bullet']['em_charpr'], esc(lead))
        runs += '<hp:run charPrIDRef="%s"><hp:t>%s</hp:t></hp:run>' % (body_cp, esc(t))
        self._p(parapr, self.s['body']['style'], runs)

    def b1(self, t, lead=None): self._bullet('b1', t, lead)
    def b2(self, t, lead=None): self._bullet('b2', t, lead)
    def b3(self, t, lead=None): self._bullet('b3', t, lead)
    def b4(self, t, lead=None): self._bullet('b4', t, lead)

    def blank(self):
        st = self.s['body']
        self._p(st['parapr'], st['style'], '<hp:run charPrIDRef="%s"><hp:t> </hp:t></hp:run>' % st['charpr'])

    def table(self, rows, widths, header_h=1400, body_h=2200, header_rows=(0,)):
        """rows: list of row; row: list of cell; cell: [para,...] or ([para,...], colspan).
        Every row's colspans must sum to len(widths)."""
        cs = self.s['cell']
        nrow = len(rows)
        total_h = sum(header_h if r in header_rows else body_h for r in range(nrow))
        trs = []
        for r, row in enumerate(rows):
            border = cs['header_border'] if r in header_rows else cs['body_border']
            h = header_h if r in header_rows else body_h
            cells, col = [], 0
            for cell_def in row:
                paras, span = (cell_def if isinstance(cell_def, tuple) else (cell_def, 1))
                c = col; width = sum(widths[c:c+span]); col += span
                ps = ''.join('<hp:p id="0" paraPrIDRef="%s" styleIDRef="%s" pageBreak="0" columnBreak="0" merged="0">'
                             '<hp:run charPrIDRef="%s"><hp:t>%s</hp:t></hp:run></hp:p>'
                             % (cs['parapr'], cs['style'], cs['charpr'], esc(p)) for p in paras)
                cells.append('<hp:tc name="" header="0" hasMargin="1" protect="0" editable="0" dirty="0" borderFillIDRef="%s">'
                             '<hp:subList id="" textDirection="HORIZONTAL" lineWrap="BREAK" vertAlign="CENTER" linkListIDRef="0" linkListNextIDRef="0" textWidth="0" textHeight="0" hasTextRef="0" hasNumRef="0">'
                             '%s</hp:subList><hp:cellAddr colAddr="%d" rowAddr="%d"/><hp:cellSpan colSpan="%d" rowSpan="1"/>'
                             '<hp:cellSz width="%d" height="%d"/><hp:cellMargin left="141" right="141" top="70" bottom="70"/></hp:tc>'
                             % (border, ps, c, r, span, width, h))
            assert col == len(widths), 'row %d colspan sum %d != %d cols' % (r, col, len(widths))
            trs.append('<hp:tr>' + ''.join(cells) + '</hp:tr>')
        tbl = ('<hp:tbl id="0" zOrder="0" numberingType="TABLE" textWrap="TOP_AND_BOTTOM" textFlow="BOTH_SIDES" lock="0" dropcapstyle="None" pageBreak="CELL" repeatHeader="1" rowCnt="%d" colCnt="%d" cellSpacing="0" borderFillIDRef="%s" noAdjust="0">'
               '<hp:sz width="%d" widthRelTo="ABSOLUTE" height="%d" heightRelTo="ABSOLUTE" protect="0"/>'
               '<hp:pos treatAsChar="1" affectLSpacing="0" flowWithText="1" allowOverlap="0" holdAnchorAndSO="0" vertRelTo="PARA" horzRelTo="PARA" vertAlign="TOP" horzAlign="LEFT" vertOffset="0" horzOffset="0"/>'
               '<hp:outMargin left="0" right="0" top="0" bottom="0"/><hp:inMargin left="141" right="141" top="70" bottom="70"/>'
               % (nrow, len(widths), cs['tbl_border'], sum(widths), total_h)) + ''.join(trs) + '</hp:tbl>'
        w = self.s['wrap']
        self._p(w['parapr'], w['style'],
                '<hp:run charPrIDRef="%s">%s<hp:t/></hp:run>' % (w['charpr'], tbl))

    def save(self, out_path):
        assert self._titled, 'call title() first (it carries secPr; a section without secPr breaks the page setup)'
        content = self.xml_decl + self.sec_open + ''.join(self.out) + '</hs:sec>'
        from xml.dom import minidom
        minidom.parseString(content.encode('utf-8'))  # validate before writing
        with zipfile.ZipFile(self.template) as zin:
            names = zin.namelist()
            with zipfile.ZipFile(out_path, 'w') as zout:
                if 'mimetype' in names:  # OCF: mimetype first, stored
                    zout.writestr(zipfile.ZipInfo('mimetype'), zin.read('mimetype'), zipfile.ZIP_STORED)
                for n in names:
                    if n == 'mimetype':
                        continue
                    data = content.encode('utf-8') if n == 'Contents/section0.xml' else zin.read(n)
                    zout.writestr(n, data, zipfile.ZIP_DEFLATED)
        return out_path
