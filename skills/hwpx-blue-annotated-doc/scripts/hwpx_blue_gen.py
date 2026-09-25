# -*- coding: utf-8 -*-
"""파란 굵은 글씨 주석이 붙는 hwpx 정책문서 생성기.

기존 hwpx를 서식 템플릿으로 쓰되 본문을 전면 재조립한다.
- 표지 배너/날짜/공백(상위 문단 0,1,2)은 원본 그대로 보존 (secPr 운반)
- 본문·표셀 안에서 «...» 로 감싼 구간이 파란 굵은 글씨 런으로 분리된다
- 서식 ID는 템플릿마다 다르다. 아래 상수를 probe_styles.py 결과로 교체할 것
"""
import re, sys, zipfile, io
import xml.etree.ElementTree as ET
from xml.dom import minidom

HP = 'http://www.hancom.co.kr/hwpml/2011/paragraph'
HH = 'http://www.hancom.co.kr/hwpml/2011/head'
HS = 'http://www.hancom.co.kr/hwpml/2011/section'

BODY_W = 47622          # 표 전체폭 (본문폭 48188 이내)

# 서식 ID (원본 채록값)
PP_HEAD, ST_HEAD = '18', '15'
CP_BOX, CP_HEADTXT, CP_TAIL = '24', '2', '19'
PP_BODY = '23'
PP_INTRO = '21'
CP_TEXT, CP_TEXT_END = '16', '22'
PP_SPACER, CP_SPACER = '17', '17'
PP_TWRAP, CP_TWRAP = '15', '15'
PP_CELL_H, CP_CELL_H = '19', '23'
PP_CELL_B, CP_CELL_B = '22', '22'
BF_TBL, BF_CELL_H, BF_CELL_B = '3', '30', '3'

# 새로 추가할 파란 굵은 글씨 charPr (header 패치로 생성)
CP_BLUE_TEXT = '25'   # 16 복제
CP_BLUE_CELL = '26'   # 22 복제
CP_BLUE_CELLH = '27'  # 23 복제


def esc(t):
    assert '<' not in t and '>' not in t, 'angle bracket in text: %r' % t
    return t.replace('&', '&amp;')


def runs_for(text, cp_normal, cp_blue):
    """«...» 구간을 파란 굵은 글씨 런으로 분리."""
    out = []
    for i, seg in enumerate(re.split(r'«(.*?)»', text, flags=re.S)):
        if not seg:
            continue
        cp = cp_blue if i % 2 else cp_normal
        out.append('<hp:run charPrIDRef="%s"><hp:t>%s</hp:t></hp:run>' % (cp, esc(seg)))
    return ''.join(out) or '<hp:run charPrIDRef="%s"><hp:t> </hp:t></hp:run>' % cp_normal


class Doc:
    def __init__(self, template):
        self.template = template
        with zipfile.ZipFile(template) as z:
            self.section_src = z.read('Contents/section0.xml').decode('utf-8')
            self.header_src = z.read('Contents/header.xml').decode('utf-8')
        m = re.match(r'(<\?xml[^>]*\?>)(<hs:sec[^>]*>)', self.section_src)
        self.decl, self.sec_open = m.group(1), m.group(2)
        self.prefix = self._keep_cover()
        self.out = []
        self._tid = 1930000001

    def _keep_cover(self):
        """표지 배너(secPr 포함) + 날짜줄 + 공백 문단 3개를 원문 그대로 잘라낸다."""
        root = ET.fromstring(self.section_src)
        ET.register_namespace('hp', HP)
        ET.register_namespace('hs', HS)
        kids = list(root)
        chunks = []
        for p in kids[:3]:
            x = ET.tostring(p, encoding='unicode')
            x = re.sub(r'<hp:linesegarray>.*?</hp:linesegarray>', '', x, flags=re.S)
            x = re.sub(r'\sxmlns:\w+="[^"]*"', '', x)
            chunks.append(x)
        return ''.join(chunks)

    # ---- 문단 ----
    def _p(self, pp, st, runs, pb=False):
        self.out.append('<hp:p id="0" paraPrIDRef="%s" styleIDRef="%s" pageBreak="%s" '
                        'columnBreak="0" merged="0">%s</hp:p>'
                        % (pp, st, '1' if pb else '0', runs))

    def head(self, label, pb=False):
        runs = ('<hp:run charPrIDRef="%s"><hp:t>□</hp:t></hp:run>'
                '<hp:run charPrIDRef="%s"><hp:t> %s</hp:t></hp:run>'
                '<hp:run charPrIDRef="%s"><hp:t> </hp:t></hp:run>'
                '<hp:run charPrIDRef="%s"/>' % (CP_BOX, CP_HEADTXT, esc(label), CP_BOX, CP_TAIL))
        self._p(PP_HEAD, ST_HEAD, runs, pb)

    def body(self, text):
        runs = runs_for(' ㅇ ' + text, CP_TEXT, CP_BLUE_TEXT)
        runs += '<hp:run charPrIDRef="%s"/>' % CP_TEXT_END
        self._p(PP_BODY, '0', runs)

    def intro(self, text):
        runs = runs_for(' ' + text, CP_TEXT, CP_BLUE_TEXT)
        runs += '<hp:run charPrIDRef="%s"/>' % CP_TEXT_END
        self._p(PP_INTRO, '0', runs)

    def spacer(self):
        self._p(PP_SPACER, '0', '<hp:run charPrIDRef="%s"/>' % CP_SPACER)

    # ---- 표 ----
    def table(self, rows, widths, header_rows=(0,), header_h=2408, body_h=2600):
        assert sum(widths) == BODY_W, 'width sum %d != %d' % (sum(widths), BODY_W)
        nrow = len(rows)
        total_h = sum(header_h if r in header_rows else body_h for r in range(nrow))
        trs = []
        for r, row in enumerate(rows):
            is_h = r in header_rows
            bf = BF_CELL_H if is_h else BF_CELL_B
            pp, cp = (PP_CELL_H, CP_CELL_H) if is_h else (PP_CELL_B, CP_CELL_B)
            cpb = CP_BLUE_CELLH if is_h else CP_BLUE_CELL
            h = header_h if is_h else body_h
            cells, col = [], 0
            for cd in row:
                paras, span = (cd if isinstance(cd, tuple) else (cd, 1))
                if isinstance(paras, str):
                    paras = [paras]
                c = col
                w = sum(widths[c:c + span])
                col += span
                ps = ''.join(
                    '<hp:p id="0" paraPrIDRef="%s" styleIDRef="0" pageBreak="0" columnBreak="0" '
                    'merged="0">%s</hp:p>' % (pp, runs_for(t, cp, cpb)) for t in paras)
                cells.append(
                    '<hp:tc name="" header="0" hasMargin="0" protect="0" editable="0" dirty="0" '
                    'borderFillIDRef="%s"><hp:subList id="" textDirection="HORIZONTAL" '
                    'lineWrap="BREAK" vertAlign="CENTER" linkListIDRef="0" linkListNextIDRef="0" '
                    'textWidth="0" textHeight="0" hasTextRef="0" hasNumRef="0">%s</hp:subList>'
                    '<hp:cellAddr colAddr="%d" rowAddr="%d"/><hp:cellSpan colSpan="%d" rowSpan="1"/>'
                    '<hp:cellSz width="%d" height="%d"/>'
                    '<hp:cellMargin left="510" right="510" top="141" bottom="141"/></hp:tc>'
                    % (bf, ps, c, r, span, w, h))
            assert col == len(widths), 'row %d: colspan sum %d != %d' % (r, col, len(widths))
            trs.append('<hp:tr>' + ''.join(cells) + '</hp:tr>')
        self._tid += 1
        tbl = ('<hp:tbl id="%d" zOrder="0" numberingType="TABLE" textWrap="TOP_AND_BOTTOM" '
               'textFlow="BOTH_SIDES" lock="0" dropcapstyle="None" pageBreak="CELL" '
               'repeatHeader="1" rowCnt="%d" colCnt="%d" cellSpacing="0" borderFillIDRef="%s" '
               'noAdjust="0"><hp:sz width="%d" widthRelTo="ABSOLUTE" height="%d" '
               'heightRelTo="ABSOLUTE" protect="0"/>'
               '<hp:pos treatAsChar="0" affectLSpacing="0" flowWithText="1" allowOverlap="0" '
               'holdAnchorAndSO="0" vertRelTo="PARA" horzRelTo="PARA" vertAlign="TOP" '
               'horzAlign="LEFT" vertOffset="0" horzOffset="0"/>'
               '<hp:outMargin left="283" right="283" top="283" bottom="283"/>'
               '<hp:inMargin left="510" right="510" top="141" bottom="141"/>'
               % (self._tid, nrow, len(widths), BF_TBL, BODY_W, total_h)) + ''.join(trs) + '</hp:tbl>'
        self._p(PP_TWRAP, '0',
                '<hp:run charPrIDRef="%s">%s<hp:t/></hp:run>' % (CP_TWRAP, tbl))

    # ---- 저장 ----
    def patch_header(self):
        h = self.header_src
        def clone(src_id, new_id):
            m = re.search(r'<hh:charPr id="%s".*?</hh:charPr>' % src_id, h, re.S)
            x = m.group(0)
            x = x.replace('id="%s"' % src_id, 'id="%s"' % new_id, 1)
            x = re.sub(r'textColor="#[0-9A-Fa-f]{6}"', 'textColor="#0000CC"', x, count=1)
            x = re.sub(r'(<hh:offset[^>]*/>)', r'\1<hh:bold/>', x, count=1)
            return x
        add = clone('16', CP_BLUE_TEXT) + clone('22', CP_BLUE_CELL) + clone('23', CP_BLUE_CELLH)
        h = h.replace('</hh:charProperties>', add + '</hh:charProperties>', 1)
        cnt = int(re.search(r'<hh:charProperties itemCnt="(\d+)"', h).group(1))
        h = h.replace('<hh:charProperties itemCnt="%d"' % cnt,
                      '<hh:charProperties itemCnt="%d"' % (cnt + 3), 1)
        return h

    def save(self, out_path, title):
        content = self.decl + self.sec_open + self.prefix + ''.join(self.out) + '</hs:sec>'
        minidom.parseString(content.encode('utf-8'))
        header = self.patch_header()
        minidom.parseString(header.encode('utf-8'))
        with zipfile.ZipFile(self.template) as zin:
            names = zin.namelist()
            with zipfile.ZipFile(out_path, 'w') as zout:
                if 'mimetype' in names:
                    zout.writestr(zipfile.ZipInfo('mimetype'), zin.read('mimetype'),
                                  zipfile.ZIP_STORED)
                for n in names:
                    if n == 'mimetype':
                        continue
                    if n == 'Contents/section0.xml':
                        data = content.encode('utf-8')
                    elif n == 'Contents/header.xml':
                        data = header.encode('utf-8')
                    elif n == 'Preview/PrvText.txt':
                        data = title.encode('utf-8')
                    else:
                        data = zin.read(n)
                    zout.writestr(n, data, zipfile.ZIP_DEFLATED)
        return out_path
