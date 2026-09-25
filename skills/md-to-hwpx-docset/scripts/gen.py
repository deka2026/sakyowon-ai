# -*- coding: utf-8 -*-
"""마크다운 원본 -> 한글(.hwpx) 문서 세트 생성기.

    python gen.py <docset.json> <문서키>
    python gen.py <docset.json> --all
    python gen.py <docset.json> <문서키> --out-suffix _regress   # 회귀 확인용 별도 파일

기존 hwpx 하나를 '서식 템플릿'으로 삼아 본문만 갈아 끼운다.
서식 ID는 문서마다 다르므로 반드시 probe_styles.py 로 채록해 docset.json 에 넣을 것.
"""
import argparse, json, os, re, sys

SK = r'C:\Users\User\.claude\skills\hwpx-powershell-edit\scripts'
if SK not in sys.path:
    sys.path.insert(0, SK)
from hwpx_gen import HwpxDoc, esc                                      # noqa: E402
from docutil import patch_table, fix_tbl_ids, sanitize_package, audit  # noqa: E402

# 사교원 표준 템플릿(12pt 적용본) 기준 기본값. 다른 템플릿이면 docset.json의 "styles"로 덮어쓴다.
DEFAULT_STYLES = {
    'title':  dict(parapr='31', style='24', charpr='23'),
    'h1':     dict(parapr='28', style='23', num_charpr='31', charpr='30'),
    'dept':   dict(parapr='23', style='23', charpr='45'),
    'team':   dict(parapr='27', style='23', charpr='42'),
    'band':   dict(parapr='26', style='23', charpr='46'),
    'body':   dict(parapr='21', style='23', charpr='40'),
    'bullet': dict(b1=('●', '41', '21'), b2=('○', '43', '21'),
                   b3=('–', '41', '22'), b4=('▸', '43', '22'), em_charpr='42'),
    'cell':   dict(parapr='33', style='23', charpr='44',
                   header_border='6', body_border='7', tbl_border='5'),
    'wrap':   dict(parapr='20', style='23', charpr='8'),
}


def build(cfg, key, out_suffix=''):
    base = cfg['base']
    body_w = cfg.get('body_width', 46400)
    styles = dict(DEFAULT_STYLES)
    styles.update(cfg.get('styles', {}))
    pb_prefix = tuple(cfg.get('page_break_prefixes', ['별표', '별지']))
    pb_exact = tuple(cfg.get('page_break_exact', ['부칙']))

    d = cfg['docs'][key]
    src = os.path.join(base, d['stem'] + '.md')
    out = os.path.join(base, d['stem'] + out_suffix + '.hwpx')

    cp_body = styles['body']['charpr']
    cp_em = styles['bullet']['em_charpr']
    pp_body = styles['body']['parapr']
    pp_indent = styles['bullet']['b3'][2]      # 들여쓴 문단용 paraPr
    st = styles['body']['style']

    doc = patch_table(HwpxDoc(os.path.join(base, cfg['template']), styles=styles))
    tbl_i = [0]

    def strip_md(t):
        # .strip() 은 전각공백(U+3000)까지 지워 표의 계층 들여쓰기가 사라진다 → 반각만 제거
        return re.sub(r'\*\*(.+?)\*\*', r'\1', t).strip(' \t')

    def rich_runs(text):
        out_runs = []
        for i, seg in enumerate(re.split(r'\*\*(.+?)\*\*', text)):
            if not seg:
                continue
            cp = cp_em if i % 2 == 1 else cp_body
            out_runs.append('<hp:run charPrIDRef="%s"><hp:t>%s</hp:t></hp:run>' % (cp, esc(seg)))
        return ''.join(out_runs)

    def para(text, indent=False):
        doc._p(pp_indent if indent else pp_body, st, rich_runs(text))

    def emit_table(rows):
        widths = d['widths'][tbl_i[0]]
        tbl_i[0] += 1
        ncol = len(widths)
        norm = []
        for r in rows:
            r = [strip_md(c) for c in r][:ncol]
            r += [''] * (ncol - len(r))
            norm.append(r)
        assert sum(widths) == body_w, \
            '%s 표%d 폭 합 %d != %d' % (key, tbl_i[0], sum(widths), body_w)
        doc.table(norm, widths, header_rows=(0,),
                  header_h=d.get('header_h', 1400), body_h=d.get('body_h', 900))

    lines = open(src, encoding='utf-8').read().split('\n')
    i = 0
    while i < len(lines):
        ln = lines[i].rstrip()

        if ln.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].startswith('|'):
                raw = lines[i].strip().strip('|')
                if not re.fullmatch(r'[-:| ]+', raw):
                    rows.append([c.strip(' \t') for c in raw.split('|')])
                i += 1
            emit_table(rows)
            nxt = next((l for l in lines[i:] if l.strip() and not l.startswith('---')), '')
            # '## '는 쪽나눔되거나 큰 제목이고, 번호 붙은 소제목은 그 자체로 구분된다
            if nxt.startswith('### ') and not re.match(r'### \d', nxt):
                doc.blank()
            continue

        if not ln.strip() or ln.startswith('---'):
            i += 1
            continue

        if ln.startswith('# '):
            doc.title(strip_md(ln[2:]))
            i += 1
            continue

        if ln.startswith('## '):
            t = strip_md(ln[3:])
            m = re.match(r'^(제\d+장)\s+(.*)$', t)
            if m:
                doc.h1(m.group(1), m.group(2), page_break=(m.group(1) == '제1장'))
            else:
                doc.h1(t, '', page_break=(t.startswith(pb_prefix) or t in pb_exact))
            i += 1
            continue

        if ln.startswith('### '):
            doc.dept(strip_md(ln[4:]))
            i += 1
            continue

        if ln.startswith('> '):
            doc.team(strip_md(ln[2:]))
            i += 1
            continue

        if ln.startswith('- '):
            doc.b1(strip_md(ln[2:]))
            i += 1
            continue

        if ln.startswith('―'):
            doc.band(strip_md(ln.strip('― ')))
            i += 1
            continue

        if ln.startswith('\u3000'):                 # 목(가. 나. 다.) — 전각공백으로 시작
            para(ln.lstrip('\u3000'), indent=True)
            i += 1
            continue

        if re.match(r'^\d+\. ', ln):                # 호(1. 2. 3.)
            para(ln, indent=True)
            i += 1
            continue

        para(ln)
        i += 1

    doc.save(out)
    fix_tbl_ids(out)
    sanitize_package(out, d['title'], cfg.get('date_iso'), cfg.get('date_kr'))
    assert tbl_i[0] == len(d['widths']), \
        '%s: 표 %d개인데 폭 정의는 %d개' % (key, tbl_i[0], len(d['widths']))
    return out, tbl_i[0], audit(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('config')
    ap.add_argument('key', nargs='?')
    ap.add_argument('--all', action='store_true')
    ap.add_argument('--out-suffix', default='',
                    help='산출물을 덮어쓰지 않고 별도 파일로 뽑을 때 (회귀 확인용)')
    a = ap.parse_args()

    cfg = json.load(open(a.config, encoding='utf-8'))
    keys = list(cfg['docs']) if a.all else [a.key]
    if not keys or keys == [None]:
        print('문서키를 주거나 --all 을 쓰세요. 사용 가능:', ', '.join(cfg['docs']))
        return 2

    for k in keys:
        out, ntbl, info = build(cfg, k, a.out_suffix)
        print('%-14s 표 %2d개  %s' % (k, ntbl, os.path.basename(out)))
        print('               ', info)
    return 0


if __name__ == '__main__':
    sys.exit(main())
