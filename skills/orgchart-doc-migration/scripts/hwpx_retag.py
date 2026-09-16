# -*- coding: utf-8 -*-
"""hwpx 문서의 용어(팀명·과명 등)를 대응표대로 일괄 치환하고, 바뀐 글자만 빨간색으로 표시한다.

hwpx-powershell-edit 스킬의 apply_by_index.ps1 은 REPLIN 조각이 한 인덱스 안에서
"정확히 1회" 나와야 하고, 여러 <hp:t> 런에 걸쳐 잘린 낱말은 아예 찾지 못한다.
조직개편 치환은 같은 낱말이 문서 전체에 수십 번 나오고 표 셀에서 자주 잘리므로
이 스크립트를 쓴다.

  python hwpx_retag.py rules.txt 원본.hwpx 출력.hwpx

rules.txt: UTF-8, 한 줄에 `옛말<TAB>새말`. `#`로 시작하는 줄과 빈 줄은 주석.
          위에서부터 우선 적용되므로 **긴 것·문구 단위를 먼저** 적는다
          (예: `❺ 에너지기본사회팀`을 `에너지기본사회팀`보다 위에).

라이브러리로도 쓸 수 있다:
  import hwpx_retag; log = hwpx_retag.process(src, dst, rules)   # rules = [(old, new), ...]
"""
import re
import sys
import zipfile


# ---------------------------------------------------------------- 빨간 charPr

def add_red_charpr(header):
    """원본 charPr 전체를 id+itemCnt 로 복제하고 textColor 를 #FF0000 으로 바꾼다.
    red(N) = N + offset 규칙이 서므로 글꼴·크기는 원본 그대로 유지된다."""
    m = re.search(r'<hh:charProperties itemCnt="(\d+)"\s*>', header)
    cnt = int(m.group(1))
    bs = m.end()
    be = header.index('</hh:charProperties>', bs)
    items = re.findall(r'<hh:charPr id="\d+".*?</hh:charPr>', header[bs:be], re.S)
    assert len(items) == cnt, 'charPr %d개 != itemCnt %d' % (len(items), cnt)
    out = []
    for src in items:
        i = int(re.match(r'<hh:charPr id="(\d+)"', src).group(1))
        new = re.sub(r'^<hh:charPr id="\d+"', '<hh:charPr id="%d"' % (i + cnt), src)
        if re.search(r'textColor="[^"]*"', new):
            new = re.sub(r'textColor="[^"]*"', 'textColor="#FF0000"', new, count=1)
        else:
            new = re.sub(r'^(<hh:charPr id="\d+")', r'\1 textColor="#FF0000"', new, count=1)
        out.append(new)
    header = header[:be] + ''.join(out) + header[be:]
    header = header.replace(m.group(0), '<hh:charProperties itemCnt="%d">' % (cnt * 2), 1)
    return header, cnt


def run_charpr(xml, t_start):
    """hp:t 를 감싸는 hp:run 의 charPrIDRef."""
    rs = xml.rfind('<hp:run ', 0, t_start)
    return int(re.search(r'charPrIDRef="(\d+)"', xml[rs:rs + 200]).group(1))


# ---------------------------------------------------------------- 치환

def substitute(xml, offset, rules):
    """모든 hp:t 를 이어붙인 문자열에서 낱말을 찾고, 런 경계를 넘는 것도 처리한다."""
    ts = list(re.finditer(r'<hp:t>([^<]*)</hp:t>', xml))
    texts = [m.group(1) for m in ts]
    pos = []                       # 이어붙인 위치 -> (런 index, 런 안 offset)
    for ri, t in enumerate(texts):
        for oi in range(len(t)):
            pos.append((ri, oi))
    joined = ''.join(texts)

    claimed = [False] * len(joined)   # 앞 규칙이 가져간 구간은 뒤 규칙이 건드리지 않는다
    hits = []
    for old, new in rules:
        s = 0
        while True:
            i = joined.find(old, s)
            if i < 0:
                break
            s = i + 1
            if any(claimed[i:i + len(old)]):
                continue
            for k in range(i, i + len(old)):
                claimed[k] = True
            hits.append((i, i + len(old), old, new))
    hits.sort()

    ops, log = {}, []
    for (i, j, old, new) in hits:
        ra, oa = pos[i]
        rb, ob = pos[j - 1]
        cp = run_charpr(xml, ts[ra].start())
        # 런을 셋으로 쪼갠다: 앞부분(원래색) + 새말(빨강) + 뒷부분(원래색)
        markup = ('</hp:t></hp:run><hp:run charPrIDRef="%d"><hp:t>%s</hp:t></hp:run>'
                  '<hp:run charPrIDRef="%d"><hp:t>' % (cp + offset, new, cp))
        if ra == rb:
            ops.setdefault(ra, []).append((oa, ob + 1, markup))
        else:                                   # 런 경계를 넘는 낱말
            ops.setdefault(ra, []).append((oa, len(texts[ra]), markup))
            for r in range(ra + 1, rb):
                ops.setdefault(r, []).append((0, len(texts[r]), ''))
            ops.setdefault(rb, []).append((0, ob + 1, ''))
        log.append((old, new))

    edits = []
    for ri, oplist in ops.items():
        t = texts[ri]
        for (s, e, ins) in sorted(oplist, reverse=True):
            t = t[:s] + ins + t[e:]
        edits.append((ts[ri].start(1), ts[ri].end(1), t))
    for (s, e, t) in sorted(edits, reverse=True):
        xml = xml[:s] + t + xml[e:]
    return xml, log


# ---------------------------------------------------------------- 입출력

def load_rules(path):
    rules = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            if not line.strip() or line.lstrip().startswith('#'):
                continue
            old, new = line.split('\t', 1)
            rules.append((old.strip(), new.strip()))
    return rules


def plain_text(path):
    with zipfile.ZipFile(path) as z:
        return ''.join(re.findall(r'<hp:t>([^<]*)</hp:t>',
                                  z.read('Contents/section0.xml').decode('utf-8')))


def process(src, dst, rules, verbose=True):
    with zipfile.ZipFile(src) as z:
        names = z.namelist()
        blobs = {n: z.read(n) for n in names}
    header = blobs['Contents/header.xml'].decode('utf-8')
    xml = blobs['Contents/section0.xml'].decode('utf-8')
    header, offset = add_red_charpr(header)
    xml, log = substitute(xml, offset, rules)
    if not log:
        if verbose:
            print('  (치환 없음 - 파일을 쓰지 않는다)')
        return []
    # 조판 캐시는 글자 수가 바뀌면 줄이 겹쳐 그려진다. 한글이 다시 계산하게 둔다.
    ncache = len(re.findall(r'<hp:linesegarray>', xml))
    xml = re.sub(r'<hp:linesegarray>.*?</hp:linesegarray>', '', xml, flags=re.S)
    from xml.dom import minidom
    minidom.parseString(xml.encode('utf-8'))
    minidom.parseString(header.encode('utf-8'))
    blobs['Contents/header.xml'] = header.encode('utf-8')
    blobs['Contents/section0.xml'] = xml.encode('utf-8')
    with zipfile.ZipFile(dst, 'w') as o:
        if 'mimetype' in names:      # OCF: mimetype 먼저, 무압축
            o.writestr(zipfile.ZipInfo('mimetype'), blobs['mimetype'], zipfile.ZIP_STORED)
        for nm in names:
            if nm != 'mimetype':
                o.writestr(nm, blobs[nm], zipfile.ZIP_DEFLATED)
    if verbose:
        print('  charPr offset=%d, 조판캐시 %d개 제거, 치환 %d건' % (offset, ncache, len(log)))
    return log


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        return 1
    rules = load_rules(sys.argv[1])
    src, dst = sys.argv[2], sys.argv[3]
    log = process(src, dst, rules)
    from collections import Counter
    for (o, n), c in sorted(Counter(log).items()):
        print('   %s -> %s  %d건' % (o, n, c))
    # 양방향 검증: 새말이 들어갔는지, 옛말이 0이 되었는지
    after = plain_text(dst) if log else plain_text(src)
    left = [(o, after.count(o)) for o, _ in rules if after.count(o)]
    print('   잔존 옛말:', left if left else '없음')
    return 0


if __name__ == '__main__':
    sys.exit(main())
