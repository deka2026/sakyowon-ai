# -*- coding: utf-8 -*-
"""망남 어촌신활력증진사업 예산 집행현황(2023~2026) v2: 예산계획 대비 집행실적 (xlsx → 한셀 재계산·.cell 저장)"""
import sys, datetime, re, os
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE); sys.path.insert(0, os.path.dirname(_HERE))  # mangnam/(classify2) + scripts/(xlsx_reader)
from xlsx_reader import load_year
from classify2 import classify, categories, semok_plan, block, SEMOK_ROWS, INGEON_ROWS, BLOCKS, YEAR_RULES, COMMON, FIXED, PLAN, SEMOK_MAP
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter as L
from collections import OrderedDict, defaultdict

OUT = r"D:\2026 사업\월간보고\8월\망남 어촌신활력증진사업_예산 집행현황(2023~2026).xlsx"
YEARS = [2023, 2024, 2025, 2026]
GRANTS = {2023: (316_620_000, "정산완료(반납 15,705,867)"), 2024: (500_000_000, "재이월(이월 4,434,786·집행취소 3,890,995)"),
          2025: (594_000_000, "이월"), 2026: (589_380_000, "당해년도")}
GRANT_SRC = "앵커 예산 집행현황 보고_0831.xlsx"

FONT = "맑은 고딕"
f_norm = Font(name=FONT, size=10); f_bold = Font(name=FONT, size=10, bold=True)
f_title = Font(name=FONT, size=14, bold=True); f_sub = Font(name=FONT, size=11, bold=True)
f_note = Font(name=FONT, size=9, color="666666"); f_blue = Font(name=FONT, size=10, color="0000FF")
fill_hdr = PatternFill("solid", fgColor="D9E1F2"); fill_tot = PatternFill("solid", fgColor="F2F2F2")
fill_grp = PatternFill("solid", fgColor="FFF2CC"); fill_plan = PatternFill("solid", fgColor="EDEDED")
thin = Side(style="thin", color="999999"); box = Border(left=thin, right=thin, top=thin, bottom=thin)
center = Alignment(horizontal="center", vertical="center", wrap_text=True)
right = Alignment(horizontal="right", vertical="center"); left = Alignment(horizontal="left", vertical="center", wrap_text=False)
leftwrap = Alignment(horizontal="left", vertical="center", wrap_text=True)
NUM = '#,##0;(#,##0);"-"'; PCT = '0.0%'

# ---------------- 데이터 적재 ----------------
KEEP = ["순번", "집행등록일자", "작성일자", "거래처명", "집행구분", "증빙구분", "집행용도", "보조세목명", "품목",
        "집행(이체)일자", "이체상태", "집행액", "공급가액", "부가세", "복원액", "등록자", "집행ID"]
data = []  # (예산연도, 사업항목, 세목대응, 예산구조, vals)
for y in YEARS:
    hdr, rows = load_year(y)
    idx = [hdr.index(k) for k in KEEP]; st = hdr.index("이체상태")
    for r in rows:
        assert r[st] == "이체완료", (y, r[st])
        vals = [r[i] for i in idx]
        vals[6] = (vals[6] or "").strip(); vals[7] = (vals[7] or "").strip()
        sp = semok_plan(vals[6], vals[7])
        data.append((y, classify(y, vals[6], vals[7]), sp, block(sp), vals))
N = len(data); LAST = N + 1
KEYS = OrderedDict()
for y, cat, sp, bl, vals in data: KEYS.setdefault((y, cat, vals[6]), len(KEYS) + 1)
xyears_by = {y: sorted({v[9].year for yy, _, _, _, v in data if yy == y}) for y in YEARS}
assert not any(sp == "정산금(기타)" for _, _, sp, _, _ in data), "정산금 세목 중 위탁수수료/부가가치세 미판별 건 존재"

wb = openpyxl.Workbook()

# ---------------- 집행내역 ----------------
wsd = wb.active; wsd.title = "집행내역"
out_hdr = ["예산연도", "집행연도", "통계목", "사업항목(계획 세부사업 대응)", "세목(계획 대응)", "예산구조"] + KEEP + ["용도키"]
wsd.append(out_hdr)
for c in wsd[1]: c.font = f_bold; c.fill = fill_hdr; c.alignment = center; c.border = box
for n, (y, cat, sp, bl, vals) in enumerate(data, start=2):
    vals = list(vals); vals[0] = n - 1
    wsd.append([y, f"=YEAR(P{n})", f'=LEFT(N{n},FIND("-",N{n})-1)', cat, sp, bl] + vals + [KEYS[(y, cat, vals[6])]])
    for c in wsd[n]: c.font = f_norm; c.border = box
    for col in ("H", "I", "P"): wsd[f"{col}{n}"].number_format = "yyyy-mm-dd"
    for col in ("R", "S", "T", "U"): wsd[f"{col}{n}"].number_format = NUM
for k, v in {"A": 8, "B": 8, "C": 8, "D": 30, "E": 14, "F": 24, "G": 6, "H": 11, "I": 11, "J": 18, "K": 20, "L": 14, "M": 50,
             "N": 20, "O": 14, "P": 11, "Q": 9, "R": 13, "S": 13, "T": 11, "U": 9, "V": 16, "W": 22, "X": 7}.items():
    wsd.column_dimensions[k].width = v
wsd.freeze_panes = "G2"; wsd.auto_filter.ref = f"A1:{L(len(out_hdr))}{LAST}"
D = "집행내역"
R_BY = f"{D}!$A$2:$A${LAST}"; R_XY = f"{D}!$B$2:$B${LAST}"; R_CAT = f"{D}!$D$2:$D${LAST}"; R_SEM = f"{D}!$E$2:$E${LAST}"
R_BLK = f"{D}!$F$2:$F${LAST}"; R_AMT = f"{D}!$R$2:$R${LAST}"; R_KEY = f"{D}!$X$2:$X${LAST}"

# ---------------- 예산계획 ----------------
wsp = wb.create_sheet("예산계획")
wsp["A1"] = "예산계획(연도별 운영예산서 0.총괄표) – 입력 데이터"; wsp["A1"].font = f_title
wsp["A2"] = "파란색 숫자는 계획서에서 옮긴 입력값. 연도별 시트와 총괄의 '예산(계획)' 열은 모두 이 시트를 SUMIFS로 참조. 레벨 1 = 세부사업·세목·구조 총액, 레벨 2 = 하위항목(참고)."; wsp["A2"].font = f_note
phdr = ["예산연도", "구분", "항목", "하위항목", "레벨", "예산액", "출처·비고"]
for j, t in enumerate(phdr, start=1):
    c = wsp.cell(4, j, t); c.font = f_bold; c.fill = fill_hdr; c.alignment = center; c.border = box
for i, (y, g, it, sub, lvl, amt, src) in enumerate(PLAN, start=5):
    for j, v in enumerate([y, g, it, sub, lvl, amt, src], start=1):
        c = wsp.cell(i, j, v); c.border = box; c.font = f_blue if j == 6 else (f_note if j == 7 else f_norm)
        c.alignment = right if j == 6 else (center if j in (1, 2, 5) else left)
        if j == 6: c.number_format = NUM
    if lvl == 1:
        for j in range(1, 7): wsp.cell(i, j).font = Font(name=FONT, size=10, bold=True, color="0000FF" if j == 6 else "000000")
PL = 4 + len(PLAN)
for k, v in {"A": 9, "B": 9, "C": 40, "D": 60, "E": 6, "F": 15, "G": 70}.items(): wsp.column_dimensions[k].width = v
wsp.freeze_panes = "A5"; wsp.auto_filter.ref = f"A4:G{PL}"
Pn = "예산계획"
P_Y = f"{Pn}!$A$5:$A${PL}"; P_G = f"{Pn}!$B$5:$B${PL}"; P_I = f"{Pn}!$C$5:$C${PL}"; P_S = f"{Pn}!$D$5:$D${PL}"
P_L = f"{Pn}!$E$5:$E${PL}"; P_A = f"{Pn}!$F$5:$F${PL}"
for _, _, it, sub, _, _, _ in PLAN: assert not re.search(r"[*?~]", it + sub), (it, sub)

def plan_f(y, gubun, item, sub=None):
    crit = f'{P_Y},{y},{P_G},"{gubun}",{P_I},"{item}",{P_L},{2 if sub else 1}' + (f',{P_S},"{sub}"' if sub else "")
    return f'=IF(COUNTIFS({crit})=0,"",SUMIFS({P_A},{crit}))'

# ---------------- 공통 서식 ----------------
def hdr_row(ws, r, cols, h=28):
    for j, t in enumerate(cols, start=1):
        c = ws.cell(r, j, t); c.font = f_bold; c.fill = fill_hdr; c.alignment = center; c.border = box
    ws.row_dimensions[r].height = h

def fmt_rows(ws, r0, r1, ncols, label_cols, plan_cols=(), pct_cols=(), text_cols=(), grp_rows=(), tot_rows=()):
    for rr in range(r0, r1 + 1):
        for j in range(1, ncols + 1):
            c = ws.cell(rr, j); c.border = box
            c.font = f_bold if (rr in grp_rows or rr in tot_rows) else f_norm
            if rr in grp_rows: c.fill = fill_grp
            if rr in tot_rows: c.fill = fill_tot
            if j <= label_cols: c.alignment = left
            elif j in text_cols: c.alignment = leftwrap; c.font = f_note
            elif j in pct_cols: c.number_format = PCT; c.alignment = right
            else:
                c.number_format = NUM; c.alignment = right
                if j in plan_cols and rr not in grp_rows and rr not in tot_rows: c.fill = fill_plan

def plan_vs_actual_table(ws, r, y, title, row_defs, xs, note_map=None):
    """row_defs: list of dict(label1,label2,plan=formula or None, actual=list of formulas per x or None(=sum), kind='item'|'sub'|'tot', sub_of=[rows])"""
    ws.cell(r, 1, title).font = f_sub; r += 1
    cols = ["구분", "항목", "예산(계획)"] + [f"{x}년 집행" for x in xs] + ["집행 합계", "잔액(계획-집행)", "집행률", "비고"]
    hdr_row(ws, r, cols); H = r; r += 1
    nx = len(xs); c_plan = 3; c_x0 = 4; c_sum = 4 + nx; c_rem = 5 + nx; c_pct = 6 + nx; c_note = 7 + nx
    rows_by_kind = defaultdict(list); placed = {}
    for d in row_defs:
        placed[d["key"]] = r
        ws.cell(r, 1, d["label1"]); ws.cell(r, 2, d["label2"])
        if d.get("plan") is not None: ws.cell(r, c_plan, d["plan"])
        if d["kind"] in ("sub", "tot"):
            src = [placed[k] for k in d["sum_of"]]
            if d.get("plan") is None:
                ws.cell(r, c_plan, "=SUM(" + ",".join(f"{L(c_plan)}{s}" for s in src) + ")")
            for i in range(nx):
                ws.cell(r, c_x0 + i, "=SUM(" + ",".join(f"{L(c_x0 + i)}{s}" for s in src) + ")")
        else:
            for i, x in enumerate(xs): ws.cell(r, c_x0 + i, d["actual"](x))
        ws.cell(r, c_sum, f"=SUM({L(c_x0)}{r}:{L(c_x0 + nx - 1)}{r})")
        ws.cell(r, c_rem, f'=IF({L(c_plan)}{r}="","",{L(c_plan)}{r}-{L(c_sum)}{r})')
        ws.cell(r, c_pct, f'=IF(OR({L(c_plan)}{r}="",{L(c_plan)}{r}=0),"",{L(c_sum)}{r}/{L(c_plan)}{r})')
        if d.get("note"): ws.cell(r, c_note, d["note"])
        rows_by_kind[d["kind"]].append(r); r += 1
    fmt_rows(ws, H + 1, r - 1, len(cols), 2, plan_cols=(c_plan,), pct_cols=(c_pct,), text_cols=(c_note,),
             grp_rows=rows_by_kind["sub"], tot_rows=rows_by_kind["tot"])
    return placed, H, r, (c_plan, c_x0, c_sum, c_rem, c_pct, c_note)

def check_row(ws, r, col, tot_row, y):
    ws.cell(r, 2, "검증: 집행내역 원본 집행액 총합").font = f_note
    c = ws.cell(r, col, f"=SUMIFS({R_AMT},{R_BY},{y})" if y else f"=SUM({R_AMT})"); c.number_format = NUM; c.font = f_note; c.alignment = right
    ws.cell(r, col + 1, f'=IF({L(col)}{r}={L(col)}{tot_row},"일치","불일치")').font = f_note
    return r + 2

def set_widths(ws, widths):
    for k, v in widths.items(): ws.column_dimensions[k].width = v
    ws.sheet_view.showGridLines = False
    ws.page_setup.orientation = "landscape"; ws.page_setup.fitToWidth = 1; ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True

today = datetime.date.today()
FIX_NOTE = {}

# ---------------- 연도별 시트 ----------------
year_tot_rows = {}
for y in YEARS:
    ws = wb.create_sheet(f"{y}예산")
    xs = xyears_by[y]
    ws["A1"] = f"망남 어촌신활력증진사업 {y}년 예산 – 계획 대비 집행현황"; ws["A1"].font = f_title
    ws["A2"] = f"단위: 원 / 계획: 예산계획 시트({y}년) / 집행: 집행완료내역_{y}.xlsx(이체완료, 집행연도는 이체일자 기준) / 작성 {today:%Y-%m-%d}"; ws["A2"].font = f_note
    r = 4
    # 표1 세목별
    def act_sem(name, y=y): return lambda x: f'=SUMIFS({R_AMT},{R_SEM},"{name}",{R_BY},{y},{R_XY},{x})'
    defs = []
    for s in SEMOK_ROWS:
        defs.append(dict(key=s, label1="직접경비", label2=s, plan=plan_f(y, "세목", s), actual=act_sem(s), kind="item", note=""))
    defs.append(dict(key="B", label1="직접경비", label2="직접경비 소계(B)", plan=plan_f(y, "구조", BLOCKS[0]), kind="sub", sum_of=SEMOK_ROWS))
    for s in INGEON_ROWS:
        defs.append(dict(key=s, label1="인건비", label2=s, plan=None, actual=act_sem(s), kind="item",
                         note="계획서는 인건비(C) 총액만 편성(세목 구분 없음)"))
    defs.append(dict(key="C", label1="인건비", label2="인건비 소계(C)", plan=plan_f(y, "세목", "인건비"), kind="sub", sum_of=INGEON_ROWS))
    for s in FIXED[1:]:
        defs.append(dict(key=s, label1={"위탁수수료": "위탁수수료(D)", "부가가치세": "부가가치세(E)"}[s], label2=s,
                         plan=plan_f(y, "세목", s), actual=act_sem(s), kind="item", note=""))
    defs.append(dict(key="TOT", label1="합계", label2="합계(A=B+C+D+E)", kind="tot", sum_of=["B", "C"] + FIXED[1:]))
    placed, H1, r, cc = plan_vs_actual_table(ws, r, y, f"표1. {y}년 예산 – 보조세목별 계획 대비 집행", defs, xs)
    T1 = placed["TOT"]; r = check_row(ws, r, cc[2], T1, y)
    # 표2 세부사업별
    def act_cat(name, y=y): return lambda x: f'=SUMIFS({R_AMT},{R_CAT},"{name}",{R_BY},{y},{R_XY},{x})'
    defs = []
    cats = sorted(categories(y)[:-len(FIXED)]) + FIXED
    for c_ in cats:
        note = ""
        if y == 2024 and c_.startswith("1."): note = "계획서 비예산 항목. 기본계획 관련 지출 9건(542,500원)은 링커조직 발굴 및 육성에 포함"
        if c_ in FIXED: note = FIX_NOTE.get(y, {}).get(c_, "")
        defs.append(dict(key=c_, label1=("사업비" if c_ not in FIXED else {"인건비": "인건비(C)", "위탁수수료": "위탁수수료(D)", "부가가치세": "부가가치세(E)"}[c_]),
                         label2=c_, plan=plan_f(y, "세부사업", c_), actual=act_cat(c_), kind="item", note=note))
    biz = [c_ for c_ in cats if c_ not in FIXED]
    defs.insert(len(biz), dict(key="BIZ", label1="사업비", label2="사업비 소계(B)", kind="sub", sum_of=biz))
    defs.append(dict(key="TOT", label1="합계", label2="합계(A=B+C+D+E)", kind="tot", sum_of=["BIZ"] + FIXED))
    placed, H2, r, cc = plan_vs_actual_table(ws, r, y, f"표2. {y}년 예산 – 세부사업(집행용도 분류)별 계획 대비 집행", defs, xs)
    T2 = placed["TOT"]; r = check_row(ws, r, cc[2], T2, y)
    ws.cell(r - 1, 2, "※ 집행용도 문장을 '분류기준' 시트 규칙으로 세부사업에 대응시킨 값. 하위항목 단위 집행은 '집행용도 상세' 시트에서 문장별로 확인.").font = f_note
    # 표2-1 하위항목 계획(참고)
    ws.cell(r, 1, f"표2-1. {y}년 세부사업 하위항목 예산(계획서 참고, 집행은 세부사업 단위로만 집계)").font = f_sub; r += 1
    hdr_row(ws, r, ["세부사업", "하위항목", "예산(계획)"], 20); r0 = r + 1; r += 1
    for (yy, g, it, sub, lvl, amt, src) in PLAN:
        if yy == y and g == "세부사업" and lvl == 2:
            ws.cell(r, 1, it); ws.cell(r, 2, sub); ws.cell(r, 3, plan_f(y, "세부사업", it, sub)); r += 1
    fmt_rows(ws, r0, r - 1, 3, 2, plan_cols=(3,))
    for rr in range(r0, r): ws.cell(rr, 2).alignment = leftwrap
    r += 1
    # 표3 교부액 대비
    ws.cell(r, 1, "표3. 교부액 대비 집행 현황").font = f_sub; r += 1
    hdr_row(ws, r, ["구분", "금액", "비고"], 20); H3 = r; r += 1
    RG = r; ws.cell(r, 1, "교부액"); ws.cell(r, 2, GRANTS[y][0]); ws.cell(r, 3, f"출처: {GRANT_SRC}"); r += 1
    ws.cell(r, 1, "계획 합계(예산서)"); ws.cell(r, 2, f"={L(cc[0])}{T1}"); ws.cell(r, 3, "표1 계획 합계"); r += 1
    for i, x in enumerate(xs):
        ws.cell(r, 1, f"{x}년 집행액"); ws.cell(r, 2, f"={L(cc[1] + i)}{T1}"); ws.cell(r, 3, "집행연도(이체일자) 기준"); r += 1
    RT = r; ws.cell(r, 1, "총집행액"); ws.cell(r, 2, f"={L(cc[2])}{T1}"); r += 1
    ws.cell(r, 1, "잔액"); ws.cell(r, 2, f"=B{RG}-B{RT}"); ws.cell(r, 3, "교부액 - 총집행액"); r += 1
    ws.cell(r, 1, "집행률"); ws.cell(r, 2, f"=IF(B{RG}=0,0,B{RT}/B{RG})"); ws.cell(r, 3, "총집행액 / 교부액"); r += 1
    ws.cell(r, 1, "정산상황"); ws.cell(r, 2, GRANTS[y][1]); r += 1
    fmt_rows(ws, H3 + 1, r - 1, 3, 1, text_cols=(3,), tot_rows=[RT])
    ws.cell(RG, 2).font = f_blue; ws.cell(r - 2, 2).number_format = PCT
    ws.cell(r - 1, 2).alignment = left; ws.cell(r - 1, 2).font = f_norm
    r += 1
    ws.cell(r, 1, "※ 회색 바탕은 계획(예산계획 시트 참조), 파란색은 외부 자료 입력값, 나머지는 모두 수식. 잔액 음수(괄호)는 계획 초과 집행.").font = f_note
    widths = {"A": 12, "B": 36, "C": 15}
    for i in range(len(xs)): widths[L(4 + i)] = 15
    widths[L(4 + len(xs))] = 15; widths[L(5 + len(xs))] = 15; widths[L(6 + len(xs))] = 8; widths[L(7 + len(xs))] = 44
    set_widths(ws, widths); ws.freeze_panes = "A4"
    year_tot_rows[y] = (T1, T2)

# ---------------- 총괄 ----------------
ws = wb.create_sheet("총괄", 0)
ws["A1"] = "망남 어촌신활력증진사업 예산 집행현황 총괄 (2023~2026년 예산, 계획 대비 집행)"; ws["A1"].font = f_title
ws["A2"] = f"작성 {today:%Y-%m-%d} / 단위: 원 / 계획: 연도별 운영예산서 총괄표(예산계획 시트) / 집행: 집행완료내역_2023~2026.xlsx 이체완료 {N}건"; ws["A2"].font = f_note
ws["A3"] = "예산연도 = 해당 연도 교부 예산. 집행은 차년도 이월 집행분까지 포함한 누계. 계획 출처는 예산계획 시트의 출처·비고 열 참조."; ws["A3"].font = f_note
r = 5
# 표1 예산구조별
ws.cell(r, 1, "표1. 예산연도별 예산구조(B·C·D·E)별 계획 대비 집행").font = f_sub; r += 1
cols = ["예산구조"]
for y in YEARS: cols += [f"{y} 계획", f"{y} 집행", f"{y} 집행률"]
cols += ["4개년 계획", "4개년 집행", "집행률"]
hdr_row(ws, r, cols); H = r; r += 1
rows_ = []
for b in BLOCKS:
    rows_.append(r); ws.cell(r, 1, b)
    for i, y in enumerate(YEARS):
        cp, ca, cr = 2 + 3 * i, 3 + 3 * i, 4 + 3 * i
        ws.cell(r, cp, plan_f(y, "구조", b)); ws.cell(r, ca, f'=SUMIFS({R_AMT},{R_BLK},"{b}",{R_BY},{y})')
        ws.cell(r, cr, f'=IF(OR({L(cp)}{r}="",{L(cp)}{r}=0),"",{L(ca)}{r}/{L(cp)}{r})')
    cp, ca, cr = 2 + 3 * len(YEARS), 3 + 3 * len(YEARS), 4 + 3 * len(YEARS)
    ws.cell(r, cp, "=SUM(" + ",".join(f"{L(2 + 3 * i)}{r}" for i in range(len(YEARS))) + ")")
    ws.cell(r, ca, "=SUM(" + ",".join(f"{L(3 + 3 * i)}{r}" for i in range(len(YEARS))) + ")")
    ws.cell(r, cr, f'=IF({L(cp)}{r}=0,"",{L(ca)}{r}/{L(cp)}{r})'); r += 1
T = r; ws.cell(r, 1, "합계(A)")
for j in range(2, 5 + 3 * len(YEARS)):
    if (j - 2) % 3 == 2: ws.cell(r, j, f'=IF({L(j - 2)}{r}=0,"",{L(j - 1)}{r}/{L(j - 2)}{r})')
    else: ws.cell(r, j, f"=SUM({L(j)}{rows_[0]}:{L(j)}{rows_[-1]})")
pcts = [4 + 3 * i for i in range(len(YEARS) + 1)]; plans = [2 + 3 * i for i in range(len(YEARS) + 1)]
fmt_rows(ws, H + 1, T, len(cols), 1, plan_cols=plans, pct_cols=pcts, tot_rows=[T]); r += 1
ws.cell(r, 2, "검증: 집행내역 원본 집행액 총합").font = f_note
c = ws.cell(r, 3 + 3 * len(YEARS), f"=SUM({R_AMT})"); c.number_format = NUM; c.font = f_note
ws.cell(r, 4 + 3 * len(YEARS), f'=IF({L(3 + 3 * len(YEARS))}{r}={L(3 + 3 * len(YEARS))}{T},"일치","불일치")').font = f_note; r += 2
# 표2 세목별
ws.cell(r, 1, "표2. 예산연도별 보조세목별 계획 대비 집행").font = f_sub; r += 1
cols = ["보조세목"]
for y in YEARS: cols += [f"{y} 계획", f"{y} 집행"]
cols += ["4개년 계획", "4개년 집행", "집행률"]
hdr_row(ws, r, cols); H = r; r += 1
placed = {}
def sem_row(key, label, plan_by_year, actual_name=None, sum_of=None):
    global r
    placed[key] = r; ws.cell(r, 1, label)
    for i, y in enumerate(YEARS):
        cp, ca = 2 + 2 * i, 3 + 2 * i
        if sum_of:
            ws.cell(r, cp, "=SUM(" + ",".join(f"{L(cp)}{placed[k]}" for k in sum_of) + ")" if plan_by_year is None else plan_by_year(y))
            ws.cell(r, ca, "=SUM(" + ",".join(f"{L(ca)}{placed[k]}" for k in sum_of) + ")")
        else:
            ws.cell(r, cp, plan_by_year(y)); ws.cell(r, ca, f'=SUMIFS({R_AMT},{R_SEM},"{actual_name}",{R_BY},{y})')
    cp, ca, cr = 2 + 2 * len(YEARS), 3 + 2 * len(YEARS), 4 + 2 * len(YEARS)
    ws.cell(r, cp, "=SUM(" + ",".join(f"{L(2 + 2 * i)}{r}" for i in range(len(YEARS))) + ")")
    ws.cell(r, ca, "=SUM(" + ",".join(f"{L(3 + 2 * i)}{r}" for i in range(len(YEARS))) + ")")
    ws.cell(r, cr, f'=IF({L(cp)}{r}=0,"",{L(ca)}{r}/{L(cp)}{r})'); r += 1
for s in SEMOK_ROWS: sem_row(s, s, lambda y, s=s: plan_f(y, "세목", s), s)
sem_row("B", "직접경비 소계(B)", lambda y: plan_f(y, "구조", BLOCKS[0]), sum_of=SEMOK_ROWS)
for s in INGEON_ROWS: sem_row(s, s, lambda y: '=""', s)
sem_row("C", "인건비 소계(C)", lambda y: plan_f(y, "세목", "인건비"), sum_of=INGEON_ROWS)
for s in FIXED[1:]: sem_row(s, s + {"위탁수수료": "(D)", "부가가치세": "(E)"}[s], lambda y, s=s: plan_f(y, "세목", s), s)
sem_row("TOT", "합계(A)", None, sum_of=["B", "C"] + FIXED[1:])
T = placed["TOT"]
fmt_rows(ws, H + 1, T, len(cols), 1, plan_cols=[2 + 2 * i for i in range(len(YEARS) + 1)], pct_cols=(4 + 2 * len(YEARS),), grp_rows=[placed["B"], placed["C"]], tot_rows=[T]); r += 1
ws.cell(r, 1, "※ 인건비(C)는 보수와 일용임금을 합산해 계획(인건비 총액)과 비교. 계획서는 인건비 세목을 나누지 않음.").font = f_note; r += 1
# 표3 교부액 대비
ws.cell(r, 1, "표3. 예산연도별 교부액 대비 집행 현황").font = f_sub; r += 1
cols3 = ["예산연도", "교부액", "계획 합계(예산서)", "당해연도 집행", "차년도(이월) 집행", "총집행액", "잔액", "집행률", "정산상황"]
hdr_row(ws, r, cols3); H3 = r; r += 1
r3 = []
for y in YEARS:
    r3.append(r); ws.cell(r, 1, f"{y}년"); ws.cell(r, 2, GRANTS[y][0])
    ws.cell(r, 3, f"='{y}예산'!{L(3)}{year_tot_rows[y][0]}")
    ws.cell(r, 4, f"=SUMIFS({R_AMT},{R_BY},{y},{R_XY},{y})"); ws.cell(r, 5, f"=SUMIFS({R_AMT},{R_BY},{y},{R_XY},{y + 1})")
    ws.cell(r, 6, f"=D{r}+E{r}"); ws.cell(r, 7, f"=B{r}-F{r}"); ws.cell(r, 8, f"=IF(B{r}=0,0,F{r}/B{r})"); ws.cell(r, 9, GRANTS[y][1]); r += 1
T3 = r; ws.cell(r, 1, "합계")
for j in range(2, 8): ws.cell(r, j, f"=SUM({L(j)}{r3[0]}:{L(j)}{r3[-1]})")
ws.cell(r, 8, f"=IF(B{r}=0,0,F{r}/B{r})")
fmt_rows(ws, H3 + 1, T3, len(cols3), 1, pct_cols=(8,), text_cols=(9,), tot_rows=[T3])
for rr in r3: ws.cell(rr, 2).font = f_blue
r += 1
ws.cell(r, 1, f"※ 회색 바탕 = 계획(예산계획 시트 참조), 파란색 = {GRANT_SRC} 입력값, 나머지는 집행내역 시트 SUMIFS 수식. 세부사업별 계획 대비는 연도마다 체계가 달라 연도별 시트 표2 참조.").font = f_note
set_widths(ws, {"A": 30, **{L(j): 14 for j in range(2, 4 + 3 * len(YEARS) + 2)}}); ws.column_dimensions["I"].width = 14
ws.freeze_panes = "A5"

# ---------------- 집행용도 상세 ----------------
ws = wb.create_sheet("집행용도 상세")
ws["A1"] = "집행용도(문장)별 집행액 – 예산연도·세부사업 순"; ws["A1"].font = f_title
ws["A2"] = "동일 집행용도 문장을 묶어 건수·금액을 집행내역 시트에서 COUNTIFS/SUMIFS로 집계. 당해연도 = 예산연도와 같은 해 집행, 차년도 = 다음 해 집행. 용도키 = 집행내역 X열과 짝을 이루는 매칭 번호."; ws["A2"].font = f_note
cols = ["예산연도", "세부사업(분류)", "집행용도", "보조세목", "건수", "당해연도 집행", "차년도 집행", "집행액 합계", "용도키"]
hdr_row(ws, 4, cols, 22)
agg = OrderedDict()
for y, cat, sp, bl, vals in data:
    a = agg.setdefault((y, cat, vals[6]), [0, 0.0, set()]); a[0] += 1; a[1] += vals[11] or 0; a[2].add(vals[7])
keys = sorted(agg, key=lambda k: (k[0], k[1], -agg[k][1]))
r = 5
for (y, cat, ju) in keys:
    ws.cell(r, 1, y); ws.cell(r, 2, cat); ws.cell(r, 3, ju); ws.cell(r, 4, " / ".join(sorted(agg[(y, cat, ju)][2]))); ws.cell(r, 9, KEYS[(y, cat, ju)])
    ws.cell(r, 5, f"=COUNTIFS({R_KEY},I{r})"); ws.cell(r, 6, f"=SUMIFS({R_AMT},{R_KEY},I{r},{R_XY},A{r})")
    ws.cell(r, 7, f"=SUMIFS({R_AMT},{R_KEY},I{r},{R_XY},A{r}+1)"); ws.cell(r, 8, f"=F{r}+G{r}")
    for j in range(1, 10):
        c = ws.cell(r, j); c.font = f_norm; c.border = box
        c.alignment = left if j in (2, 3, 4) else (center if j in (1, 9) else right)
        if 5 <= j <= 8: c.number_format = NUM
    r += 1
TD = r; ws.cell(r, 3, "합계").font = f_bold
for j in range(5, 9): c = ws.cell(r, j, f"=SUM({L(j)}5:{L(j)}{r - 1})"); c.number_format = NUM; c.font = f_bold
for j in range(1, 10): ws.cell(r, j).border = box; ws.cell(r, j).fill = fill_tot
ws.cell(r + 1, 3, "검증: 집행내역 원본 집행액 총합").font = f_note
c = ws.cell(r + 1, 8, f"=SUM({R_AMT})"); c.number_format = NUM; c.font = f_note
ws.cell(r + 1, 10, f'=IF(H{r + 1}=H{r},"일치","불일치")').font = f_note
for k, v in {"A": 9, "B": 34, "C": 70, "D": 24, "E": 7, "F": 14, "G": 14, "H": 14, "I": 7}.items(): ws.column_dimensions[k].width = v
ws.freeze_panes = "A5"; ws.auto_filter.ref = f"A4:I{TD - 1}"

# ---------------- 분류기준 ----------------
ws = wb.create_sheet("분류기준")
ws["A1"] = "집행용도 → 세부사업 분류 기준 (연도별 운영예산서의 세부사업 체계에 대응)"; ws["A1"].font = f_title
ws["A2"] = "공통 규칙을 먼저 적용한 뒤, 예산연도별 규칙을 위에서부터 첫 일치로 적용. 마지막 규칙(정규식 없음)은 기본값. 분류를 바꾸려면 집행내역 시트 D열 값을 직접 고치면 모든 표가 자동 반영."; ws["A2"].font = f_note
hdr_row(ws, 4, ["예산연도", "순위", "세부사업(분류)", "판정 기준(키워드)", "정규식"], 22); r = 5
for i, (name, desc, pat) in enumerate(COMMON, start=1):
    for j, v in enumerate(["공통", i, name, desc, pat or ""], start=1):
        c = ws.cell(r, j, v); c.font = f_norm; c.border = box; c.alignment = center if j <= 2 else leftwrap
    r += 1
for y in YEARS:
    for i, (name, desc, pat) in enumerate(YEAR_RULES[y], start=1):
        for j, v in enumerate([y, i, name, desc, pat or "(기본값)"], start=1):
            c = ws.cell(r, j, v); c.font = f_norm; c.border = box; c.alignment = center if j <= 2 else leftwrap
        r += 1
r += 1
ws.cell(r, 1, "세목(계획 대응) 매핑: 집행용도에 '위탁수수료'→위탁수수료, '부가가치세'→부가가치세(세목 무관). 그 외 " + ", ".join(f"{k}→{v}" for k, v in SEMOK_MAP.items() if k != "정산금-정산금")).font = f_note
r += 1
ws.cell(r, 1, "예산구조: 보수·일용임금→C 인건비, 위탁수수료→D, 부가가치세→E, 그 외→B 직접경비.").font = f_note
for k, v in {"A": 9, "B": 6, "C": 34, "D": 80, "E": 70}.items(): ws.column_dimensions[k].width = v

ORDER = ["총괄", "2023예산", "2024예산", "2025예산", "2026예산", "예산계획", "집행용도 상세", "분류기준", "집행내역"]
wb._sheets = [wb[n] for n in ORDER]
wb.save(OUT)
print("saved", OUT, "sheets", wb.sheetnames)
print("rows", N, "detail", len(keys), "plan rows", len(PLAN))
