# -*- coding: utf-8 -*-
"""세로쓰기 조직도 PDF에서 과·팀 이름을 x좌표 기준으로 열 재조립해 읽는다.

행정 조직도는 과 이름을 한 글자씩 세로로 쌓아 그린다. 그래서 PDF 텍스트를
그냥 뽑으면 '자 치 분 권 과' 가 아니라 글자들이 y순으로 흩어진 채 나온다.
같은 x좌표(±4pt)에 있는 글자를 한 열로 묶고 y순으로 이으면 원래 이름이 복원된다.

  python orgchart_columns.py 조직도.pdf 0 540 850 370 700
                             (파일)  (쪽) (x0) (x1) (y0) (y1)

출력: 열마다 `--- x=<좌표>` 와 `y:글자` 목록. 과 이름 / 정원 / 팀 이름이 한 줄에 이어진다.

먼저 전체 그림을 보려면 Read 도구로 PDF를 이미지로 띄워 대략의 픽셀 위치를 잡고,
`pt = px / 이미지폭 * 페이지폭` 으로 환산해 위 범위를 정한다.

주의: 콘솔이 cp949면 한국어 출력이 깨진다. `PYTHONIOENCODING=utf-8` 로 실행할 것.
필요 패키지: pymupdf
"""
import sys

import pymupdf


def columns(pdf_path, page, x0, x1, y0, y1, tol=4.0):
    doc = pymupdf.open(pdf_path)
    words = [w for w in doc[page].get_text('words')
             if x0 <= w[0] <= x1 and y0 <= w[1] <= y1]
    cols = {}
    for w in words:
        key = next((k for k in cols if abs(k - w[0]) < tol), None)
        if key is None:
            key = w[0]
            cols[key] = []
        cols[key].append(w)
    return {k: sorted(v, key=lambda w: w[1]) for k, v in sorted(cols.items())}


def main():
    if len(sys.argv) < 7:
        print(__doc__)
        return 1
    path, page = sys.argv[1], int(sys.argv[2])
    x0, x1, y0, y1 = (float(v) for v in sys.argv[3:7])
    for x, items in columns(path, page, x0, x1, y0, y1).items():
        print('--- x=%.1f' % x)
        print('  ' + ' | '.join('%.0f:%s' % (w[1], w[4]) for w in items))
    return 0


if __name__ == '__main__':
    sys.exit(main())
