# -*- coding: utf-8 -*-
"""header.xml 의 height 1200 미만 charPr 을 모두 1200(12pt)으로 올린다.
빨간 사본도 같은 규칙으로 함께 올라간다(사본 역시 charPr 이므로)."""
import re, zipfile, sys, os


def bump(path, floor=1200):
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        blobs = {n: z.read(n) for n in names}
    h = blobs['Contents/header.xml'].decode('utf-8')
    changed = []

    def rep(m):
        v = int(m.group(2))
        if v < floor:
            changed.append((m.group(1), v))
            return m.group(0).replace('height="%d"' % v, 'height="%d"' % floor, 1)
        return m.group(0)

    h = re.sub(r'<hh:charPr id="(\d+)"[^>]*height="(\d+)"[^>]*>', rep, h)
    from xml.dom import minidom
    minidom.parseString(h.encode('utf-8'))
    blobs['Contents/header.xml'] = h.encode('utf-8')
    with zipfile.ZipFile(path, 'w') as o:
        o.writestr(zipfile.ZipInfo('mimetype'), blobs['mimetype'], zipfile.ZIP_STORED)
        for n in names:
            if n != 'mimetype':
                o.writestr(n, blobs[n], zipfile.ZIP_DEFLATED)
    return changed


if __name__ == '__main__':
    for p in sys.argv[1:]:
        c = bump(p)
        print('%s : %d개 charPr 상향' % (os.path.basename(p), len(c)))
