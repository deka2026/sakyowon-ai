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
