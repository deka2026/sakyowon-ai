# -*- coding: utf-8 -*-
"""hwpx_house_rules.py - apply Sakyowon house rules to any finished .hwpx (post-processor).

Made for documents produced by outside builders (python-hwpx `HwpxDocument`, other
generators, files received from colleagues) whose XML is valid but violates the rules
that the user set in 2026-09:

  1. body AND table-cell text >= 12pt          (charPr height >= 1200)
  2. tables placed in-flow, treatAsChar="0"     (so long tables split across pages)
  3. table-cell paragraphs left-aligned         (JUSTIFY in narrow cells stretches letters)

Usage
  python hwpx_house_rules.py in.hwpx out.hwpx [--min-pt 12] [--no-cells-left] [--no-tables] [--no-font]

Only charPr ids actually referenced from section*.xml are raised, so unused defaults
(footnote 9pt etc.) stay untouched. Headings already above the minimum are left alone.
Cell alignment is done by cloning each JUSTIFY paraPr used inside <hp:tc> into a LEFT
twin appended to <hh:paraProperties>, then re-pointing only the cell paragraphs.

Returns a dict report and prints it. Exit code 0 on success.
"""
import argparse
import os
import re
import shutil
import sys
import tempfile
import zipfile

_TC_RE = re.compile(r"<hp:tc\b.*?</hp:tc>", re.S)


def _read(z, name):
    return z.read(name).decode("utf-8")


def apply_rules(src, dst, min_pt=12.0, font=True, tables=True, cells_left=True):
    min_h = int(round(min_pt * 100))
    report = {"raised_charpr": {}, "tables_inflow": 0, "cell_paras_left": 0, "parapr_added": {}}
    tmpdir = tempfile.mkdtemp(prefix="hwpx_rules_")
    try:
        with zipfile.ZipFile(src) as z:
            names = z.namelist()
            header = _read(z, "Contents/header.xml")
            sections = {n: _read(z, n) for n in names if re.match(r"Contents/section\d+\.xml$", n)}
            others = {n: z.read(n) for n in names if n not in sections and n != "Contents/header.xml"}

        # 1. font size ---------------------------------------------------------
        if font:
            used = set()
            for s in sections.values():
                used.update(re.findall(r'charPrIDRef="(\d+)"', s))

            def _raise(m):
                tag = m.group(0)
                cid = re.search(r'\bid="(\d+)"', tag)
                h = re.search(r'\bheight="(\d+)"', tag)
                if not cid or not h or cid.group(1) not in used:
                    return tag
                if int(h.group(1)) < min_h:
                    report["raised_charpr"][cid.group(1)] = (int(h.group(1)), min_h)
                    return tag.replace(h.group(0), 'height="%d"' % min_h, 1)
                return tag

            header = re.sub(r"<hh:charPr\b[^>]*>", _raise, header)

        # 2. tables in-flow ----------------------------------------------------
        if tables:
            for n, s in sections.items():
                new, k = re.subn(r'(<hp:pos\b[^>]*?)treatAsChar="1"', r'\1treatAsChar="0"', s)
                report["tables_inflow"] += k
                sections[n] = new

        # 3. cell paragraphs left ---------------------------------------------
        if cells_left:
            m = re.search(r"<hh:paraProperties\b([^>]*)>(.*?)</hh:paraProperties>", header, re.S)
            if m:
                parapr = {}
                for p in re.findall(r"<hh:paraPr\b.*?</hh:paraPr>", m.group(2), re.S):
                    pid = re.search(r'\bid="(\d+)"', p[: p.find(">")])
                    if pid:
                        parapr[pid.group(1)] = p
                next_id = max(int(i) for i in parapr) + 1 if parapr else 0
                clones = {}  # justify id -> left id
                additions = []
                cell_ids = set()
                for s in sections.values():
                    for tc in _TC_RE.findall(s):
                        cell_ids.update(re.findall(r'paraPrIDRef="(\d+)"', tc))
                for pid in sorted(cell_ids, key=int):
                    p = parapr.get(pid)
                    if not p or 'horizontal="JUSTIFY"' not in p:
                        continue
                    new_p = re.sub(r'\bid="%s"' % pid, 'id="%d"' % next_id, p, count=1)
                    new_p = new_p.replace('horizontal="JUSTIFY"', 'horizontal="LEFT"', 1)
                    clones[pid] = str(next_id)
                    additions.append(new_p)
                    next_id += 1
                if clones:
                    cnt = re.search(r'itemCnt="(\d+)"', m.group(1))
                    head = m.group(1)
                    if cnt:
                        head = head.replace(cnt.group(0), 'itemCnt="%d"' % (int(cnt.group(1)) + len(additions)), 1)
                    header = header[: m.start()] + "<hh:paraProperties%s>%s%s</hh:paraProperties>" % (
                        head, m.group(2), "".join(additions)) + header[m.end():]
                    report["parapr_added"] = clones

                    def _fix_tc(mm):
                        t = mm.group(0)
                        for old, new in clones.items():
                            t, k = re.subn(r'paraPrIDRef="%s"' % old, 'paraPrIDRef="%s"' % new, t)
                            report["cell_paras_left"] += k
                        return t

                    for n, s in sections.items():
                        sections[n] = _TC_RE.sub(_fix_tc, s)

        # write ----------------------------------------------------------------
        import xml.dom.minidom as minidom
        minidom.parseString(header.encode("utf-8"))
        for s in sections.values():
            minidom.parseString(s.encode("utf-8"))

        out_tmp = os.path.join(tmpdir, "out.hwpx")
        with zipfile.ZipFile(out_tmp, "w") as z:
            if "mimetype" in others:
                z.writestr("mimetype", others.pop("mimetype"), compress_type=zipfile.ZIP_STORED)
            z.writestr("Contents/header.xml", header.encode("utf-8"), compress_type=zipfile.ZIP_DEFLATED)
            for n, s in sections.items():
                z.writestr(n, s.encode("utf-8"), compress_type=zipfile.ZIP_DEFLATED)
            for n, b in others.items():
                z.writestr(n, b, compress_type=zipfile.ZIP_DEFLATED)
        os.makedirs(os.path.dirname(os.path.abspath(dst)) or ".", exist_ok=True)
        shutil.copyfile(out_tmp, dst)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
    return report


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--min-pt", type=float, default=12.0)
    ap.add_argument("--no-font", action="store_true")
    ap.add_argument("--no-tables", action="store_true")
    ap.add_argument("--no-cells-left", action="store_true")
    a = ap.parse_args(argv)
    rep = apply_rules(a.src, a.dst, a.min_pt, not a.no_font, not a.no_tables, not a.no_cells_left)
    print(rep)
    return 0


if __name__ == "__main__":
    sys.exit(main())
