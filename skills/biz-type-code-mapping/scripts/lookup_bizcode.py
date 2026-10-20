# -*- coding: utf-8 -*-
"""한국표준산업분류(KSIC 5자리) → 국세청 업종코드(6자리) 조회.

    python lookup_bizcode.py 56111 47122 35114
    python lookup_bizcode.py --file ksic.txt          # 한 줄에 하나씩

사업자등록 신청서에 적는 것은 KSIC 가 아니라 국세청 업종코드다. 둘은 체계가 달라
한식 음식점이 KSIC 56111 / 업종코드 552101 처럼 번호가 전혀 다르다.

출처: upjong.co.kr (KSIC 11차 ↔ 업종코드 연계, 경비율 포함).
업종코드는 귀속연도마다 바뀌므로 신청 직전 홈택스에서 재확인할 것.
"""
import argparse, re, ssl, sys, time, urllib.error, urllib.request

URL = 'https://upjong.co.kr/korean-standard-industry-classification/ksic-%s/'
UA = {'User-Agent': 'Mozilla/5.0'}


def fetch(ksic, retries=3, pause=2.0):
    """429 가 잦아 간격을 두고 재시도한다."""
    for k in range(retries):
        try:
            req = urllib.request.Request(URL % ksic, headers=UA)
            return urllib.request.urlopen(req, timeout=25,
                                          context=ssl.create_default_context()).read().decode('utf-8', 'ignore')
        except urllib.error.HTTPError as e:
            if e.code == 429 and k < retries - 1:
                time.sleep(pause * (k + 2))
                continue
            raise
    return ''


def parse(html):
    """(업종코드, 종목, 업태) 목록. 업태는 '중분류' 행의 분류명."""
    text = re.sub(r'<[^>]+>', ' ', html)
    text = re.sub(r'[ \t]+', ' ', text)
    out, seen = [], set()
    # '업종코드 552101 한식 일반 음식점업' 블록마다 뒤따르는 '중분류 55 음식점업'
    for m in re.finditer(r'업종코드 (\d{6}) ([^\n]{2,40}?)\s*(?:구분|$|\n)', text):
        code, name = m.group(1), m.group(2).strip()
        if name in ('상세보기',) or code in seen:
            continue
        seen.add(code)
        tail = text[m.end():m.end() + 500]
        mid = re.search(r'중분류 (\d+) ([^\n]{2,40}?)\s*(?:소분류|세분류)', tail)
        out.append((code, name, mid.group(2).strip() if mid else ''))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('ksic', nargs='*')
    ap.add_argument('--file')
    ap.add_argument('--pause', type=float, default=1.5, help='조회 간 쉬는 시간(초)')
    a = ap.parse_args()

    codes = list(a.ksic)
    if a.file:
        codes += [l.strip() for l in open(a.file, encoding='utf-8') if re.fullmatch(r'\d{5}', l.strip())]
    if not codes:
        print('KSIC 5자리를 하나 이상 주세요.')
        return 2

    print('%-7s %-8s %-34s %s' % ('KSIC', '업종코드', '종목', '업태(중분류)'))
    print('-' * 86)
    miss = []
    for i, k in enumerate(codes):
        if i:
            time.sleep(a.pause)
        try:
            rows = parse(fetch(k))
        except Exception as e:
            print('%-7s  조회 실패: %s' % (k, type(e).__name__))
            miss.append(k)
            continue
        if not rows:
            print('%-7s  연계 업종코드 없음' % k)
            miss.append(k)
            continue
        for j, (code, name, up) in enumerate(rows):
            print('%-7s %-8s %-34s %s' % (k if j == 0 else '', code, name[:34], up))
        if len(rows) > 1:
            print('%-7s  ↑ %d개 — 적용범위를 읽고 하나를 고를 것' % ('', len(rows)))
    if miss:
        print('\n확인 못 한 것: %s — 홈택스나 세무서에 문의' % ' '.join(miss))
    return 0


if __name__ == '__main__':
    sys.exit(main())
