# -*- coding: utf-8 -*-
"""hwpx에 PNG/JPG를 넣는다 (경로 I).

hwpx의 그림은 세 곳이 맞아야 보인다.
  1) zip 안 BinData/<id>.png
  2) Contents/content.hpf 의 opf:manifest 에 opf:item 등록
  3) Contents/section0.xml 의 hp:pic 안 hc:img@binaryItemIDRef 가 그 id를 가리킴
META-INF/manifest.xml 은 비어 있어도 되고, header.xml 에는 등록하지 않는다(2026-09-25 확인).

쓰는 법 — hwpx_gen.HwpxDoc 로 문서를 조립하는 중에:

    from hwpx_embed_images import PicPlacer, embed_images
    pics = PicPlacer(doc, styles)          # doc = HwpxDoc 인스턴스
    pics.place('fig1.png', 1000, 560, '[그림 1] 공정 흐름')
    ...
    doc.save(out)
    embed_images(out, pics.registry)       # 저장 뒤에 호출한다

HWPUNIT: 1inch = 7200, 96dpi 이미지는 px * 75. 본문폭은 secPr 에서
pagePr@width - margin@left - margin@right 로 매번 계산할 것.
"""
import base64
import hashlib
import os
import zipfile


def pic_xml(pid, px, py, width, seq):
    """hp:pic 한 덩어리. width 는 HWPUNIT(본문폭 이하)."""
    h = int(width * py / px)
    ow, oh = px * 75, py * 75
    return (
        '<hp:pic id="%d" zOrder="0" numberingType="PICTURE" textWrap="TOP_AND_BOTTOM" '
        'textFlow="BOTH_SIDES" lock="0" dropcapstyle="None" href="" groupLevel="0" '
        'instid="%d" reverse="0">'
        '<hp:offset x="0" y="0"/><hp:orgSz width="%d" height="%d"/>'
        '<hp:curSz width="%d" height="%d"/><hp:flip horizontal="0" vertical="0"/>'
        '<hp:rotationInfo angle="0" centerX="%d" centerY="%d" rotateimage="1"/>'
        '<hp:renderingInfo><hc:transMatrix e1="1" e2="0" e3="0" e4="0" e5="1" e6="0"/>'
        '<hc:scaMatrix e1="%.6f" e2="0" e3="0" e4="0" e5="%.6f" e6="0"/>'
        '<hc:rotMatrix e1="1" e2="0" e3="0" e4="0" e5="1" e6="0"/></hp:renderingInfo>'
        '<hc:img binaryItemIDRef="%s" bright="0" contrast="0" effect="REAL_PIC" alpha="0"/>'
        '<hp:imgRect><hc:pt0 x="0" y="0"/><hc:pt1 x="%d" y="0"/><hc:pt2 x="%d" y="%d"/>'
        '<hc:pt3 x="0" y="%d"/></hp:imgRect>'
        '<hp:imgClip left="0" right="%d" top="0" bottom="%d"/>'
        '<hp:inMargin left="0" right="0" top="0" bottom="0"/>'
        '<hp:imgDim dimwidth="%d" dimheight="%d"/><hp:effects/>'
        '<hp:sz width="%d" widthRelTo="ABSOLUTE" height="%d" heightRelTo="ABSOLUTE" protect="0"/>'
        '<hp:pos treatAsChar="0" affectLSpacing="0" flowWithText="1" allowOverlap="0" '
        'holdAnchorAndSO="0" vertRelTo="PARA" horzRelTo="COLUMN" vertAlign="TOP" '
        'horzAlign="CENTER" vertOffset="0" horzOffset="0"/>'
        '<hp:outMargin left="0" right="0" top="0" bottom="0"/></hp:pic>'
        % (seq, seq + 7000, ow, oh, width, h, width // 2, h // 2,
           width / ow, h / oh, pid, ow, ow, oh, oh, ow, oh, ow, oh, width, h))


class PicPlacer:
    """HwpxDoc 에 그림 문단 + 캡션 문단을 얹고, 넣을 파일 목록을 모은다."""

    def __init__(self, doc, styles, body_width=46400, caption_parapr='22'):
        self.doc = doc
        self.s = styles
        self.width = body_width
        self.caption_parapr = caption_parapr
        self.registry = []          # [(binaryItemID, 로컬 파일 경로), ...]
        self._seq = 1900500000

    def place(self, path, px, py, caption=None):
        pid = 'image%d' % (len(self.registry) + 1)
        self.registry.append((pid, path))
        self._seq += 1
        xml = pic_xml(pid, px, py, self.width, self._seq)
        w = self.s['wrap']
        self.doc._p(w['parapr'], w['style'],
                    '<hp:run charPrIDRef="%s">%s<hp:t/></hp:run>' % (w['charpr'], xml))
        if caption:
            self.doc._p(self.caption_parapr, '23',
                        '<hp:run charPrIDRef="%s"><hp:t>%s</hp:t></hp:run>'
                        % (self.s['cell']['charpr'], caption))
        return pid


def embed_images(path, registry):
    """저장된 hwpx 에 BinData 를 넣고 content.hpf 에 등록한다. 마지막에 호출."""
    tmp = path + '.tmp'
    with zipfile.ZipFile(path) as zin:
        names = zin.namelist()
        hpf = zin.read('Contents/content.hpf').decode('utf-8')
        items = ''
        for pid, fn in registry:
            data = open(fn, 'rb').read()
            hk = base64.b64encode(hashlib.md5(data).digest()).decode()
            ext = os.path.splitext(fn)[1].lower().lstrip('.')
            mt = 'image/jpeg' if ext in ('jpg', 'jpeg') else 'image/' + ext
            items += ('<opf:item id="%s" href="BinData/%s.%s" media-type="%s" '
                      'isEmbeded="1" hashkey="%s"/>' % (pid, pid, ext, mt, hk))
        assert '</opf:manifest>' in hpf, 'content.hpf 에 opf:manifest 가 없다'
        hpf = hpf.replace('</opf:manifest>', items + '</opf:manifest>')
        with zipfile.ZipFile(tmp, 'w') as zout:
            zout.writestr(zipfile.ZipInfo('mimetype'), zin.read('mimetype'), zipfile.ZIP_STORED)
            for nm in names:
                if nm == 'mimetype':
                    continue
                dat = hpf.encode('utf-8') if nm == 'Contents/content.hpf' else zin.read(nm)
                zout.writestr(nm, dat, zipfile.ZIP_DEFLATED)
            for pid, fn in registry:
                ext = os.path.splitext(fn)[1].lower().lstrip('.')
                zout.writestr('BinData/%s.%s' % (pid, ext), open(fn, 'rb').read(),
                              zipfile.ZIP_DEFLATED)
    os.replace(tmp, path)
    return len(registry)


def audit_images(path):
    """본문 참조와 매니페스트 등록이 맞는지 본다."""
    import re
    with zipfile.ZipFile(path) as z:
        ns = z.namelist()
        hpf = z.read('Contents/content.hpf').decode('utf-8')
        sec = z.read('Contents/section0.xml').decode('utf-8')
    bins = [n for n in ns if n.startswith('BinData/')]
    reg = set(re.findall(r'<opf:item id="(image\d+)"', hpf))
    ref = set(re.findall(r'binaryItemIDRef="(image\d+)"', sec))
    return {'bindata': len(bins), 'registered': sorted(reg), 'referenced': sorted(ref),
            'ok': reg == ref and len(bins) == len(reg)}
