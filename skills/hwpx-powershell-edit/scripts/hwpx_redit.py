"""hwpx_redit.py -- pure-Python red-mark editor for .hwpx (path F).

Why this exists
---------------
The PowerShell path (add_red_charpr.ps1 / apply_by_index.ps1) is the default,
but it is unusable when the shell cannot run .ps1 files -- calling
`powershell -File script.ps1` from Git Bash dies on ExecutionPolicy
(UnauthorizedAccess), and `-ExecutionPolicy Bypass` is not always allowed.
This module does the same job with Python only, so a bash-driven session can
still produce a red-marked correction copy.

Proven 2026-08-28: Goheung agrivoltaics plan, 37 run replacements + 2 new
tables + 4 inserted paragraphs, 80 red runs, tables 14 -> 16, zero failures.

Pipeline
--------
    python hwpx_redit.py dump   <src.hwpx> <workdir>
    python hwpx_redit.py addred <workdir>                  # prints red offset
    python hwpx_redit.py apply  <workdir> <edits.json>
    python hwpx_redit.py pack   <workdir> <src.hwpx> <out.hwpx>
    python hwpx_redit.py verify <out.hwpx> --must A B --gone C

edits.json (UTF-8; this is where all Korean text lives)
-------------------------------------------------------
    {
      "red_offset": 22,
      "replace": [[1, "new text for run 1", true],
                  [4, "plain replacement, no red", false]],
      "insert_after_table": [["1975100003", "<hp:p ...>...</hp:p>"]],
      "insert_after_text":  [["anchor substring", "<hp:p ...>...</hp:p>"]]
    }

Rules that bite
---------------
* Run index == order of <hp:t> matches. Table cells each own one index.
* Replacements are applied in DESCENDING index order so offsets stay valid.
* Red marking bumps the enclosing run's charPrIDRef by red_offset, so the
  whole run turns red. Use short runs (table cells, headings) for precision.
* Only `&` is escaped in replacement text. Raw `<` or `>` will break the XML,
  except deliberate inline tags such as <hp:lineBreak/>, which are passed
  through untouched -- so keep those intentional and rare.
* <hp:linesegarray> layout caches are stripped on apply; Hangul recomputes.
* pack() copies every entry from the source archive in its original order and
  keeps mimetype STORED. Never overwrite the source file.
"""

import json
import os
import re
import sys
import zipfile
import xml.dom.minidom as minidom

SECTION = "Contents/section0.xml"
HEADER = "Contents/header.xml"
RUN_RE = re.compile(r"<hp:t>(.*?)</hp:t>", re.S)


def _sec(workdir):
    return os.path.join(workdir, "unpacked", "Contents", "section0.xml")


def _hdr(workdir):
    return os.path.join(workdir, "unpacked", "Contents", "header.xml")


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _write(path, text):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


# ---------------------------------------------------------------- dump
def cmd_dump(src, workdir):
    unpacked = os.path.join(workdir, "unpacked")
    os.makedirs(unpacked, exist_ok=True)
    with zipfile.ZipFile(src) as zf:
        zf.extractall(unpacked)
    x = _read(_sec(workdir))
    lines = []
    for i, m in enumerate(RUN_RE.finditer(x)):
        start = x.rfind("<hp:run ", 0, m.start())
        cp = re.search(r'charPrIDRef="(\d+)"', x[start:start + 140])
        lines.append("[%d]<%s> %s" % (i, cp.group(1) if cp else "?", m.group(1)))
    out = os.path.join(workdir, "dump.txt")
    _write(out, "\n".join(lines))
    hdr = _read(_hdr(workdir))
    cnt = re.search(r'charProperties itemCnt="(\d+)"', hdr)
    print("runs: %d" % len(lines))
    print("tables: %d" % x.count("<hp:tbl "))
    print("charProperties itemCnt: %s  (red offset candidate)" % (cnt.group(1) if cnt else "?"))
    print("dump: %s" % out)


# -------------------------------------------------------------- addred
def cmd_addred(workdir):
    path = _hdr(workdir)
    h = _read(path)
    m = re.search(r'(<hh:charProperties itemCnt=")(\d+)(")', h)
    if not m:
        sys.exit("charProperties itemCnt not found")
    cnt = int(m.group(2))
    blocks = re.findall(r'<hh:charPr id="\d+".*?</hh:charPr>', h, re.S)
    if len(blocks) != cnt:
        sys.exit("itemCnt %d != charPr blocks %d" % (cnt, len(blocks)))
    if any(int(re.search(r'id="(\d+)"', b).group(1)) >= cnt for b in blocks):
        sys.exit("charPr ids are not 0..N-1; red offset rule would break")
    red = []
    for b in blocks:
        oid = int(re.search(r'id="(\d+)"', b).group(1))
        nb = re.sub(r'^<hh:charPr id="\d+"', '<hh:charPr id="%d"' % (oid + cnt), b)
        nb = re.sub(r'(^<hh:charPr[^>]*?)textColor="#[0-9A-Fa-f]{6}"',
                    r'\1textColor="#FF0000"', nb)
        red.append(nb)
    end = h.rindex("</hh:charProperties>")
    h = h[:end] + "".join(red) + h[end:]
    h = h[:m.start()] + m.group(1) + str(cnt * 2) + m.group(3) + h[m.end():]
    minidom.parseString(h)
    _write(path, h)
    print("red charPr added: %d  (itemCnt %d -> %d)" % (len(red), cnt, cnt * 2))
    print("RED OFFSET = %d   (red(N) = N + %d)" % (cnt, cnt))


# --------------------------------------------------------------- apply
def cmd_apply(workdir, edits_path):
    spec = json.loads(_read(edits_path))
    offset = int(spec.get("red_offset", 0))
    path = _sec(workdir)
    x = _read(path)

    repl = spec.get("replace", [])
    if repl:
        spans = [(m.start(1), m.end(1)) for m in RUN_RE.finditer(x)]
        for item in sorted(repl, key=lambda e: -int(e[0])):
            idx, new = int(item[0]), item[1]
            red = bool(item[2]) if len(item) > 2 else False
            if idx >= len(spans):
                sys.exit("run index %d out of range (max %d)" % (idx, len(spans) - 1))
            s, e = spans[idx]
            txt = new.replace("&", "&amp;")
            if red:
                rs = x.rindex("<hp:run ", 0, s)
                re_end = x.index(">", rs)
                head = x[rs:re_end]
                cm = re.search(r'charPrIDRef="(\d+)"', head)
                oid = int(cm.group(1))
                nid = oid + offset if oid < offset else oid
                x = x[:s] + txt + x[e:]
                x = x[:rs] + head[:cm.start(1)] + str(nid) + head[cm.end(1):] + x[re_end:]
            else:
                x = x[:s] + txt + x[e:]
        print("replaced runs: %d" % len(repl))

    for tid, block in spec.get("insert_after_table", []):
        i = x.index('id="%s"' % tid)
        e = x.index("</hp:tbl>", i) + len("</hp:tbl>")
        e = x.index("</hp:p>", e) + len("</hp:p>")
        x = x[:e] + block + x[e:]
    if spec.get("insert_after_table"):
        print("inserted after tables: %d" % len(spec["insert_after_table"]))

    for anchor, block in spec.get("insert_after_text", []):
        i = x.index(anchor)
        e = x.index("</hp:p>", i) + len("</hp:p>")
        x = x[:e] + block + x[e:]
    if spec.get("insert_after_text"):
        print("inserted after anchors: %d" % len(spec["insert_after_text"]))

    x = re.sub(r"<hp:linesegarray>.*?</hp:linesegarray>", "", x, flags=re.S)
    minidom.parseString(x)
    _write(path, x)
    print("section XML valid; tables now %d" % x.count("<hp:tbl "))


# ---------------------------------------------------------------- pack
def cmd_pack(workdir, src, out):
    if os.path.abspath(src) == os.path.abspath(out):
        sys.exit("refusing to overwrite the source hwpx")
    repl = {SECTION: _sec(workdir), HEADER: _hdr(workdir)}
    if os.path.exists(out):
        os.remove(out)
    with zipfile.ZipFile(src) as zin, zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:
        for it in zin.infolist():
            if it.filename in repl:
                with open(repl[it.filename], "rb") as fh:
                    data = fh.read()
            else:
                data = zin.read(it.filename)
            zi = zipfile.ZipInfo(it.filename, date_time=it.date_time)
            zi.compress_type = (zipfile.ZIP_STORED if it.filename == "mimetype"
                                else zipfile.ZIP_DEFLATED)
            zi.external_attr = it.external_attr
            zout.writestr(zi, data)
    print("packed: %s" % out)


# -------------------------------------------------------------- verify
def cmd_verify(hwpx, must, gone):
    with zipfile.ZipFile(hwpx) as zf:
        x = zf.read(SECTION).decode("utf-8")
        h = zf.read(HEADER).decode("utf-8")
    minidom.parseString(x)
    minidom.parseString(h)
    txt = "\n".join(RUN_RE.findall(x))
    reds = [int(i) for i in re.findall(r'charPrIDRef="(\d+)"', x)]
    cnt = re.search(r'charProperties itemCnt="(\d+)"', h)
    print("XML valid (section+header)")
    print("runs=%d tables=%d charPr itemCnt=%s" % (len(RUN_RE.findall(x)),
                                                   x.count("<hp:tbl "),
                                                   cnt.group(1) if cnt else "?"))
    half = int(cnt.group(1)) // 2 if cnt else 0
    print("runs using red charPr (id >= %d): %d" % (half, sum(1 for r in reds if r >= half)))
    bad = 0
    for s in must:
        ok = s in txt
        bad += 0 if ok else 1
        print("%s must  %s  x%d" % ("OK  " if ok else "MISS", s, txt.count(s)))
    for s in gone:
        ok = s not in txt
        bad += 0 if ok else 1
        print("%s gone  %s  x%d" % ("OK  " if ok else "LEFT", s, txt.count(s)))
    if bad:
        sys.exit("verification failures: %d" % bad)


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__)
    cmd = argv[1]
    if cmd == "dump" and len(argv) == 4:
        cmd_dump(argv[2], argv[3])
    elif cmd == "addred" and len(argv) == 3:
        cmd_addred(argv[2])
    elif cmd == "apply" and len(argv) == 4:
        cmd_apply(argv[2], argv[3])
    elif cmd == "pack" and len(argv) == 5:
        cmd_pack(argv[2], argv[3], argv[4])
    elif cmd == "verify":
        must, gone, bucket = [], [], None
        for a in argv[3:]:
            if a == "--must":
                bucket = must
            elif a == "--gone":
                bucket = gone
            elif bucket is not None:
                bucket.append(a)
        cmd_verify(argv[2], must, gone)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv)
