# -*- coding: utf-8 -*-
"""hwpx_gen 보조 유틸 — 셀 정규화, 표 id 유일화, 검수 지표."""
import re, zipfile


def norm_rows(rows):
    """셀이 문자열이면 [문자열]로 감싼다. (문자열을 그대로 주면 글자마다 문단이 생김)"""
    out = []
    for row in rows:
        r = []
        for c in row:
            if isinstance(c, str):
                r.append([c])
            elif isinstance(c, tuple):
                paras, span = c
                r.append(([paras] if isinstance(paras, str) else list(paras), span))
            else:
                r.append(list(c))
        out.append(r)
    return out


def patch_table(doc):
    """doc.table 호출 시 자동으로 norm_rows를 적용하도록 감싼다."""
    orig = doc.table

    def wrapped(rows, widths, **kw):
        return orig(norm_rows(rows), widths, **kw)

    doc.table = wrapped
    return doc


def fix_tbl_ids(path, start=1900000001):
    """모든 <hp:tbl id="0">을 유일 id로 치환. 치환 개수를 반환."""
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        blobs = {n: z.read(n) for n in names}
    s = blobs['Contents/section0.xml'].decode('utf-8')
    counter = [start]

    def rep(m):
        v = counter[0]
        counter[0] += 1
        return '<hp:tbl id="%d"' % v

    s, n = re.subn(r'<hp:tbl id="0"', rep, s)
    blobs['Contents/section0.xml'] = s.encode('utf-8')
    with zipfile.ZipFile(path, 'w') as o:
        if 'mimetype' in names:
            o.writestr(zipfile.ZipInfo('mimetype'), blobs['mimetype'], zipfile.ZIP_STORED)
        for nm in names:
            if nm == 'mimetype':
                continue
            o.writestr(nm, blobs[nm], zipfile.ZIP_DEFLATED)
    return n


def sanitize_package(path, title=None, date_iso=None, date_kr=None):
    """템플릿에서 물려받은 잔재 제거 — 템플릿으로 새 문서를 만들면 반드시 부를 것.

    hwpx는 zip이라 템플릿을 복사해 본문만 갈아 끼우면 다음 두 가지가 그대로 남는다.
      1) Preview/PrvText.txt · Preview/PrvImage.png
         템플릿 원문 1쪽이 통째로 남아 윈도 탐색기 미리보기와 검색 인덱스에 뜬다.
         회의록 템플릿이면 참석자 실명이 새 문서에 그대로 딸려 간다(2026-09-18 실제 발생).
         hwpx 스펙상 Preview는 선택 항목이라 항목째 지워도 되지만,
         ★ META-INF/container.xml 이 Preview/PrvText.txt 를 <ocf:rootfile> 로 선언한다. ★
         파일만 지우고 이 선언을 남기면 끊긴 rootfile 참조가 생긴다(2026-09-18 실제 발생).
         content.hpf 의 opf:manifest 와 META-INF/manifest.xml · container.rdf 에는 참조가 없다.
         그래서 이 함수는 Preview 항목 삭제 + container.xml 의 끊긴 rootfile 선언 제거를
         한 번에 한다. 한글에서 다시 저장하면 Preview 는 새 내용으로 재생성된다.
      2) Contents/content.hpf 의 opf:title · CreatedDate · ModifiedDate · date
         템플릿 원문의 제목과 작성 일자가 남는다.

    제거한 Preview 항목 이름 목록을 반환한다.
    zip 안에 없는 파일을 가리키는 rootfile 선언이 남으면 AssertionError 를 낸다.
    """
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        blobs = {n: z.read(n) for n in names}

    removed = [n for n in names if n.startswith('Preview/')]
    for n in removed:
        names.remove(n)
        blobs.pop(n)

    # container.xml: zip 에 남아 있지 않은 파일을 가리키는 rootfile 선언을 지운다.
    ct_key = 'META-INF/container.xml'
    if ct_key in blobs:
        ct = blobs[ct_key].decode('utf-8')

        def _drop_dangling(m):
            return '' if m.group(1) not in names else m.group(0)

        ct = re.sub(r'<ocf:rootfile\s[^>]*full-path="([^"]+)"[^>]*/>', _drop_dangling, ct)
        blobs[ct_key] = ct.encode('utf-8')
        left = re.findall(r'<ocf:rootfile\s[^>]*full-path="([^"]+)"', ct)
        missing = [f for f in left if f not in names]
        assert not missing, 'container.xml 이 없는 파일을 가리킨다: %s' % missing
        from xml.dom import minidom
        minidom.parseString(ct.encode('utf-8'))  # 유효 XML 인지 확인

    hpf_key = 'Contents/content.hpf'
    if hpf_key in blobs and (title or date_iso or date_kr):
        hpf = blobs[hpf_key].decode('utf-8')
        if title:
            hpf = re.sub(r'<opf:title>.*?</opf:title>',
                         '<opf:title>%s</opf:title>' % title, hpf, count=1)
        if date_iso:
            for key in ('CreatedDate', 'ModifiedDate'):
                hpf = re.sub(r'(<opf:meta name="%s" content="text">)[^<]*' % key,
                             r'\g<1>' + date_iso, hpf, count=1)
        if date_kr:
            hpf = re.sub(r'(<opf:meta name="date" content="text">)[^<]*',
                         r'\g<1>' + date_kr, hpf, count=1)
        blobs[hpf_key] = hpf.encode('utf-8')

    with zipfile.ZipFile(path, 'w') as o:
        if 'mimetype' in names:
            o.writestr(zipfile.ZipInfo('mimetype'), blobs['mimetype'], zipfile.ZIP_STORED)
        for nm in names:
            if nm != 'mimetype':
                o.writestr(nm, blobs[nm], zipfile.ZIP_DEFLATED)
    return removed


def audit(path):
    """생성 직후 검수: 문단 수, 표 수, 표 id 유일성, section 크기."""
    with zipfile.ZipFile(path) as z:
        s = z.read('Contents/section0.xml').decode('utf-8')
    ids = re.findall(r'<hp:tbl id="(\d+)"', s)
    cells = s.count('<hp:tc ')
    paras = s.count('<hp:p ')
    return dict(section_kb=round(len(s.encode('utf-8')) / 1024, 1),
                tables=len(ids), unique_ids=len(set(ids)),
                cells=cells, paragraphs=paras,
                paras_per_cell=round(paras / cells, 2) if cells else None)
