# -*- coding: utf-8 -*-
"""템플릿 hwpx의 서식 ID를 채록한다 — docset.json 의 "styles" 를 채우기 위한 첫 단계.

    python probe_styles.py <템플릿.hwpx>

서식 ID는 문서마다 다르고, 한글이 재저장하면 재매핑된다. 전에 쓰던 값을 재사용하지 말고
템플릿을 바꿀 때마다 다시 채록할 것.
"""
import re, sys, zipfile

p = sys.argv[1]
with zipfile.ZipFile(p) as z:
    sec = z.read('Contents/section0.xml').decode('utf-8')
    hdr = z.read('Contents/header.xml').decode('utf-8')

m = re.search(r'<hp:pagePr[^>]*width="(\d+)"', sec)
mm = re.search(r'<hp:margin[^>]*left="(\d+)"[^>]*right="(\d+)"', sec)
if m and mm:
    w, l, r = int(m.group(1)), int(mm.group(1)), int(mm.group(2))
    print('pagePr width=%d  margin L=%d R=%d  => 본문폭 %d  (표 폭은 이 이하로)'
          % (w, l, r, w - l - r))

for nm, pat in [('charProperties', r'<hh:charProperties itemCnt="(\d+)"'),
                ('paraProperties', r'<hh:paraProperties itemCnt="(\d+)"')]:
    mt = re.search(pat, hdr)
    if mt:
        print('%s itemCnt = %s' % (nm, mt.group(1)))

print('\n--- charPr id : 크기 / 굵기 / 색 ---')
for cm in re.finditer(r'<hh:charPr id="(\d+)"[^>]*height="(\d+)"'
                      r'[^>]*?(?:textColor="([^"]*)")?[^>]*>(.*?)</hh:charPr>', hdr, re.S):
    cid, h, col, inner = cm.group(1), int(cm.group(2)), cm.group(3), cm.group(4)
    print('  %3s : %5.1fpt %s %s' % (cid, h / 100, 'B' if '<hh:bold/>' in inner else ' ', col or ''))

print('\n--- 문단 (paraPr/style/charPr : 텍스트) — 제목·절·본문·불릿의 ID를 여기서 고른다 ---')
n = 0
for pm in re.finditer(r'<hp:p id="[^"]*" paraPrIDRef="(\d+)" styleIDRef="(\d+)"[^>]*>(.*?)</hp:p>',
                      sec, re.S):
    pp, st, inner = pm.group(1), pm.group(2), pm.group(3)
    runs = list(dict.fromkeys(re.findall(r'<hp:run charPrIDRef="(\d+)"', inner)))
    txt = re.sub(r'<[^>]+>', '', ''.join(re.findall(r'<hp:t[^>]*>(.*?)</hp:t>', inner, re.S))).strip()
    has_tbl = '<hp:tbl' in inner
    if not txt and not has_tbl:
        continue
    n += 1
    if n > 40:
        break
    print('  pp=%-3s st=%-3s cp=%-12s %s%s'
          % (pp, st, ','.join(runs), '[TBL] ' if has_tbl else '', txt[:60]))

tm = re.search(r'<hp:tbl\b.*?</hp:tbl>', sec, re.S)
if tm:
    t = tm.group(0)
    print('\n--- 첫 표 (cell 서식) ---')
    print('  hp:sz width =', re.search(r'<hp:sz width="(\d+)"', t).group(1))
    print('  tbl borderFillIDRef =', re.search(r'borderFillIDRef="(\d+)"', t).group(1))
    seen = []
    for bf, pp, st, cp in re.findall(
            r'<hp:tc [^>]*borderFillIDRef="(\d+)"[^>]*>.*?'
            r'<hp:p id="[^"]*" paraPrIDRef="(\d+)" styleIDRef="(\d+)"[^>]*>'
            r'<hp:run charPrIDRef="(\d+)"', t, re.S):
        if (bf, pp, st, cp) not in seen:
            seen.append((bf, pp, st, cp))
    for bf, pp, st, cp in seen[:6]:
        print('  cell borderFill=%s parapr=%s style=%s charpr=%s (첫 줄이 머리행, 둘째가 본문행)'
              % (bf, pp, st, cp))
