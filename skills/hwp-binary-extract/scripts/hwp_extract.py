import sys, os, zipfile, io, re

def sniff(path):
    with open(path, 'rb') as f:
        head = f.read(8)
    if head[:4] == b'PK\x03\x04':
        return 'zip'
    if head == b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1':
        return 'ole'
    return 'unknown:' + repr(head)

def from_ole(path):
    import olefile
    from hwp5.xmlmodel import Hwp5File
    from hwp5.dataio import ParseError
    hf = Hwp5File(path)
    out = []
    try:
        for sec in hf.bodytext:
            pass
    except Exception:
        pass
    # use text transform
    from hwp5.plat import get_xslt
    return None

def ole_text(path):
    """Extract paragraph text from HWP5 BodyText sections directly."""
    import olefile, zlib, struct
    ole = olefile.OleFileIO(path)
    # header: check compressed flag
    header = ole.openstream('FileHeader').read()
    flags = struct.unpack('<I', header[36:40])[0]
    compressed = bool(flags & 1)
    streams = [s for s in ole.listdir() if s[0] == 'BodyText']
    def keyf(s):
        m = re.search(r'(\d+)', s[-1])
        return int(m.group(1)) if m else 0
    streams.sort(key=keyf)
    texts = []
    for s in streams:
        data = ole.openstream(s).read()
        if compressed:
            try:
                data = zlib.decompress(data, -15)
            except Exception:
                continue
        texts.append(parse_records(data))
    ole.close()
    return '\n'.join(texts)

HWPTAG_BEGIN = 0x10
HWPTAG_PARA_TEXT = HWPTAG_BEGIN + 51  # 67

def parse_records(data):
    pos = 0
    n = len(data)
    out = []
    while pos + 4 <= n:
        hdr = struct.unpack_from('<I', data, pos)[0]
        pos += 4
        tag = hdr & 0x3FF
        size = (hdr >> 20) & 0xFFF
        if size == 0xFFF:
            if pos + 4 > n: break
            size = struct.unpack_from('<I', data, pos)[0]
            pos += 4
        chunk = data[pos:pos+size]
        pos += size
        if tag == HWPTAG_PARA_TEXT:
            out.append(decode_para(chunk))
    return '\n'.join(t for t in out if t.strip())

def decode_para(chunk):
    res = []
    i = 0
    n = len(chunk)
    while i + 2 <= n:
        code = struct.unpack_from('<H', chunk, i)[0]
        if code in (0,10,13) or 1 <= code <= 31:
            # control char
            if code in (1,2,3,11,12,14,15,16,17,18,21,22,23):
                i += 16  # extended control
                continue
            elif code in (4,5,6,7,8,9,19,20):
                i += 2
                continue
            elif code == 10 or code == 13:
                res.append('\n')
                i += 2
                continue
            else:
                i += 2
                continue
        res.append(chr(code))
        i += 2
    return ''.join(res)

import struct

def zip_text(path):
    z = zipfile.ZipFile(path)
    names = [n for n in z.namelist() if n.startswith('Contents/section')]
    def keyf(nm):
        m = re.search(r'(\d+)', nm)
        return int(m.group(1)) if m else 0
    names.sort(key=keyf)
    out = []
    for nm in names:
        xml = z.read(nm).decode('utf-8', 'ignore')
        # extract <hp:t>...</hp:t>
        parts = re.findall(r'<hp:t[^>]*>(.*?)</hp:t>', xml, re.S)
        paras = re.split(r'<hp:p\b', xml)
        for p in paras:
            ts = re.findall(r'<hp:t[^>]*>(.*?)</hp:t>', p, re.S)
            line = ''.join(ts)
            line = re.sub(r'<[^>]+>', '', line)
            line = (line.replace('&lt;','<').replace('&gt;','>')
                        .replace('&amp;','&').replace('&quot;','"').replace('&apos;',"'"))
            if line.strip():
                out.append(line)
    z.close()
    return '\n'.join(out)

if __name__ == '__main__':
    src, dst = sys.argv[1], sys.argv[2]
    kind = sniff(src)
    if kind == 'zip':
        text = zip_text(src)
    elif kind == 'ole':
        text = ole_text(src)
    else:
        text = ''
        print('UNKNOWN FORMAT', kind, file=sys.stderr)
    with open(dst, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f'{os.path.basename(dst)}: {kind}, {len(text)} chars')
