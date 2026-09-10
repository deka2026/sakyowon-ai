# -*- coding: utf-8 -*-
"""템플릿의 본문 글자모양을 지정 크기(기본 12pt) 사본으로 복제한 새 템플릿을 만든다.

사교원 규칙: hwpx 본문은 12pt, 표 셀은 10pt 유지.
템플릿 본문 charPr이 10pt(height=1000)인 경우 그대로 쓰면 규칙에 어긋나므로,
본문·불릿에 쓰는 charPr만 12pt 사본으로 복제하고 생성기 STYLES에서 새 id를 가리킨다.
표 셀 charPr은 건드리지 않으므로 표는 10pt로 남는다.

사용:
    from patch_body_12pt import list_charprs, patch_body_pt
    list_charprs('template.hwpx')                  # id·크기·색 채록
    m = patch_body_pt('template.hwpx', 'tpl_12pt.hwpx', ['8','10','11','12'])
    # m == {'8':'19','10':'20','11':'21','12':'22'}  → STYLES의 body/bullet에 새 id 사용
"""
import re
import zipfile


def list_charprs(hwpx_path):
    """charPr id · height(1/100pt) · textColor 목록. 어떤 id가 본문인지 고를 때 쓴다."""
    with zipfile.ZipFile(hwpx_path) as z:
        h = z.read('Contents/header.xml').decode('utf-8')
    out = []
    for m in re.finditer(r'<hh:charPr id="(\d+)"[^>]*>', h):
        tag = m.group(0)
        hgt = re.search(r'height="(\d+)"', tag)
        col = re.search(r'textColor="([^"]*)"', tag)
        out.append(dict(id=m.group(1),
                        height=int(hgt.group(1)) if hgt else None,
                        color=col.group(1) if col else None))
    return out


def patch_body_pt(src_hwpx, out_hwpx, clone_ids, height=1200):
    """clone_ids의 charPr을 height(1/100pt) 사본으로 복제해 새 hwpx를 만든다.

    새 id는 기존 itemCnt부터 순서대로 부여하고 {old: new} 매핑을 돌려준다.
    글꼴·굵기·색은 원본 그대로 유지되고 크기만 바뀐다.
    """
    with zipfile.ZipFile(src_hwpx) as z:
        names = z.namelist()
        blobs = {n: z.read(n) for n in names}
    h = blobs['Contents/header.xml'].decode('utf-8')

    m = re.search(r'(<hh:charProperties itemCnt=")(\d+)(")', h)
    if not m:
        raise ValueError('charProperties itemCnt not found')
    cnt = int(m.group(2))

    blocks = {}
    for mm in re.finditer(r'<hh:charPr id="(\d+)".*?</hh:charPr>', h, re.S):
        blocks[mm.group(1)] = mm.group(0)

    mapping, added = {}, []
    for i, old in enumerate(clone_ids):
        if old not in blocks:
            raise ValueError('charPr id %s not in template' % old)
        new_id = str(cnt + i)
        b = re.sub(r'^<hh:charPr id="\d+"', '<hh:charPr id="%s"' % new_id, blocks[old])
        b = re.sub(r'height="\d+"', 'height="%d"' % height, b, count=1)
        added.append(b)
        mapping[old] = new_id

    h = h[:m.start()] + m.group(1) + str(cnt + len(clone_ids)) + m.group(3) + h[m.end():]
    h = h.replace('</hh:charProperties>', ''.join(added) + '</hh:charProperties>', 1)
    blobs['Contents/header.xml'] = h.encode('utf-8')

    with zipfile.ZipFile(out_hwpx, 'w') as o:
        if 'mimetype' in names:
            o.writestr(zipfile.ZipInfo('mimetype'), blobs['mimetype'], zipfile.ZIP_STORED)
        for n in names:
            if n == 'mimetype':
                continue
            o.writestr(n, blobs[n], zipfile.ZIP_DEFLATED)
    return mapping


def clear_red(src_hwpx, out_hwpx):
    """빨간 교정 표시(textColor #FF0000)만 검정으로 되돌린다.

    글자모양의 색 속성만 바꾸므로 section0.xml은 바이트 그대로 보존된다.
    교정본을 수락해 최종본으로 확정할 때 쓴다. 되돌린 charPr id 목록을 반환.
    """
    with zipfile.ZipFile(src_hwpx) as z:
        names = z.namelist()
        blobs = {n: z.read(n) for n in names}
    h = blobs['Contents/header.xml'].decode('utf-8')

    changed = []

    def rep(m):
        tag = m.group(0)
        if 'textColor="#FF0000"' in tag:
            changed.append(re.search(r'id="(\d+)"', tag).group(1))
            return tag.replace('textColor="#FF0000"', 'textColor="#000000"')
        return tag

    h = re.sub(r'<hh:charPr id="\d+"[^>]*>', rep, h)
    blobs['Contents/header.xml'] = h.encode('utf-8')

    with zipfile.ZipFile(out_hwpx, 'w') as o:
        if 'mimetype' in names:
            o.writestr(zipfile.ZipInfo('mimetype'), blobs['mimetype'], zipfile.ZIP_STORED)
        for n in names:
            if n == 'mimetype':
                continue
            o.writestr(n, blobs[n], zipfile.ZIP_DEFLATED)
    return changed
