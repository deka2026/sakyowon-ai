# -*- coding: utf-8 -*-
"""한셀(Cell)이 저장한 xlsx도 읽는 최소 리더. openpyxl 스타일 인덱스 오류 회피용."""
import zipfile, re, datetime
import xml.etree.ElementTree as ET

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
DATE_COLS = {"집행등록일자", "작성일자", "집행(이체)일자"}

def _col_idx(ref):
    letters = re.match(r"[A-Z]+", ref).group(0)
    n = 0
    for ch in letters: n = n * 26 + (ord(ch) - 64)
    return n - 1

def _serial_to_date(v):
    return datetime.datetime(1899, 12, 30) + datetime.timedelta(days=float(v))

def read_rows(path):
    z = zipfile.ZipFile(path)
    strs = []
    if "xl/sharedStrings.xml" in z.namelist():
        root = ET.fromstring(z.read("xl/sharedStrings.xml"))
        for si in root.findall("m:si", NS):
            strs.append("".join(t.text or "" for t in si.iter("{%s}t" % NS["m"])))
    root = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
    rows = []
    for row in root.find("m:sheetData", NS).findall("m:row", NS):
        vals = {}
        for c in row.findall("m:c", NS):
            ref = c.get("r"); t = c.get("t")
            v = c.find("m:v", NS)
            if v is None or v.text is None:
                isn = c.find("m:is", NS)
                val = "".join(x.text or "" for x in isn.iter("{%s}t" % NS["m"])) if isn is not None else None
            elif t == "s": val = strs[int(v.text)]
            elif t == "str": val = v.text
            elif t == "b": val = v.text == "1"
            elif t == "e": val = None
            else:
                f = float(v.text); val = int(f) if f.is_integer() else f
            vals[_col_idx(ref)] = val
        if vals:
            width = max(vals) + 1
            rows.append([vals.get(i) for i in range(width)])
    width = max(len(r) for r in rows)
    rows = [r + [None] * (width - len(r)) for r in rows]
    hdr = [(h or "").strip() if isinstance(h, str) else h for h in rows[0]]
    out = []
    for r in rows[1:]:
        if not any(v is not None for v in r): continue
        r = list(r)
        for i, h in enumerate(hdr):
            if h in DATE_COLS and isinstance(r[i], (int, float)):
                r[i] = _serial_to_date(r[i])
        out.append(r)
    return hdr, out

def load_year(y, folder=r"D:\2026 사업\월간보고\8월"):
    """openpyxl 우선, 실패 시 XML 리더. (hdr, rows) 반환. 이체완료 행만."""
    path = rf"{folder}\집행완료내역_{y}.xlsx"
    try:
        import openpyxl, warnings
        warnings.simplefilter("ignore")
        ws = openpyxl.load_workbook(path, data_only=True).active
        hdr = [(c.value or "").strip() if isinstance(c.value, str) else c.value for c in ws[1]]
        rows = [list(r) for r in ws.iter_rows(min_row=2, values_only=True) if any(v is not None for v in r)]
    except Exception:
        hdr, rows = read_rows(path)
    for i, h in enumerate(hdr):
        if h == "인력정보\n유무": hdr[i] = "인력정보유무"
    return hdr, rows

if __name__ == "__main__":
    import sys
    for y in (2023, 2024, 2025, 2026):
        hdr, rows = load_year(y)
        a = hdr.index("집행액"); d = hdr.index("집행(이체)일자")
        print(y, len(rows), int(sum(r[a] or 0 for r in rows)), sorted({r[d].year for r in rows if r[d]}), type(rows[0][d]).__name__)
    # 2023을 XML 리더로도 읽어 교차검증
    hdr, rows = read_rows(r"D:\2026 사업\월간보고\8월\집행완료내역_2023.xlsx")
    a = hdr.index("집행액"); print("2023 via xml", len(rows), int(sum(r[a] or 0 for r in rows)))
