---
name: hancell-budget-report
description: e나라도움 집행완료내역(xlsx)과 운영예산서 총괄표를 읽어 연도별·보조세목별·세부사업(집행용도 분류)별 계획 대비 집행현황 통합문서를 만들고, 한셀(HCell.Application COM)로 재계산·검증해 .cell로 저장하는 스킬. "집행현황 엑셀/한셀로 만들어", "예산계획 대비 집행실적 업데이트", "한셀 파일로 저장" 같은 요청에 사용. 한셀이 저장한 xlsx(openpyxl 로드 실패)를 읽을 때도 이 스킬의 XML 리더를 쓴다.
---

# 한셀 예산 집행현황 통합문서 (hancell-budget-report)

2026-09-16 망남 어촌신활력증진사업 앵커조직(2023~2026 예산, 1,181건)으로 검증. 산출물은 `.cell`(한셀 고유 형식)이며 모든 집계가 수식(SUMIFS/COUNTIFS)이라 원본 시트만 갱신하면 표가 따라 바뀐다.

## 언제 쓰나
- 보조사업 집행완료내역(e나라도움 내보내기)을 예산계획 대비 집행현황 표로 만들어야 할 때
- 사용자가 엑셀이 아니라 **한셀** 사용자일 때 (파일 잠금 `~$*.xlsx`가 한셀에서 생긴 것이면 한셀 사용자)
- 한셀이 저장한 xlsx를 파이썬으로 읽어야 할 때 (`docProps/app.xml`의 `<Application>Cell</Application>`)

## 파이프라인 (순서대로)

| 단계 | 도구 | 산출 |
|---|---|---|
| 1 | `scripts/xlsx_reader.py` `load_year()` | 원본 행 리스트 (openpyxl 우선, 실패 시 XML 파서) |
| 2 | `scripts/mangnam/classify2.py` | 집행용도 → 세부사업 분류 규칙(연도별), 세목 대응, 예산계획 데이터(PLAN) |
| 3 | `scripts/mangnam/build_v2.py` | openpyxl로 xlsx 생성 (총괄·연도별·예산계획·집행용도 상세·분류기준·집행내역) |
| 4 | `scripts/hcell_recalc.ps1 -In <xlsx> -Out <cell>` | 한셀 COM 재계산 → `#` 오류·"불일치" 스캔 → `.cell` 저장 |

```powershell
python scripts\mangnam\build_v2.py
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\hcell_recalc.ps1 -In "D:\...\집행현황.xlsx" -Out "D:\...\집행현황.cell"
# 출력: formula errors: 0 ; mismatch cells: 0 → saved: ...
```

`formula errors`가 0이 아니거나 `mismatch`가 있으면 배포 금지. 0/0이어도 수식이 "맞다"는 뜻은 아니므로 총괄 합계를 원본 총합(SUM 집행액)과 대조하는 검증행을 표마다 둔다(빌드 스크립트가 자동 생성).

## 통합문서 설계 원칙 (사용자 확정)
- **예산연도**(교부 예산) × **집행연도**(이체일자 연도): 이월 집행이 있으므로 두 축을 분리. 연도별 시트는 열이 `예산(계획) | Y년 집행 | Y+1년 집행 | 합계 | 잔액 | 집행률 | 비고`
- **예산구조** B 직접경비 / C 인건비 / D 위탁수수료 / E 부가가치세. **일용임금은 C 인건비**(직접경비 아님). 위탁수수료·부가가치세는 세목 무관하게 집행용도 문장으로 판정(2025~는 위탁수수료가 일반수용비 세목으로 편성됨)
- **세부사업 분류는 연도별 계획서의 세부사업 체계**를 따른다(연도마다 다름). 규칙은 위에서 첫 일치, 마지막이 기본값(앵커조직 운영). 계획서 하위항목(①②…)은 계획만 참고표로 싣고 집행은 세부사업 단위로 집계
- 사용자가 개별 건을 다른 항목으로 지정하면 **연도 규칙 맨 앞에 "지정 재분류" 규칙**으로 추가(예: 2023 현황지도·심층조사 분석비·관광협의회 회의비 → 앵커조직 운영). 같은 항목명이 두 규칙에 쓰이면 `categories()`가 중복 제거해야 함(이미 반영)
- 예산계획은 **입력 시트(파란색)** 한 곳에만 두고 표는 SUMIFS로 참조(연도·구분·항목·레벨 조건). 하위항목은 레벨 2
- 글꼴 맑은 고딕 10pt, 숫자 `#,##0;(#,##0);"-"`, 계획 열 회색 바탕, 소계 노란색, 합계 회색

## 함정 (실전에서 걸린 것)
1. **한셀 SUMIFS는 `~~` 이스케이프를 인식하지 않는다.** "4월~7월" 같은 문장을 조건으로 쓰면 그 건이 통째로 빠진다(20건 48,279,540원 누락으로 발견). 문장 조건 대신 **숫자 용도키 열**을 만들어 매칭할 것. 빌드 스크립트는 이미 그렇게 함
2. 한셀 저장 xlsx는 openpyxl에서 `IndexError: _cell_styles`로 죽는다 → `xlsx_reader.read_rows()`(sharedStrings·sheet XML 직접 파싱, `t="e"` 오류셀은 None, 날짜 열은 시리얼→datetime)
3. 엑셀 COM으로 재계산하려다 숨은 인스턴스가 남아 `0x800AC472`(busy)가 반복됐다. 한셀 사용자 환경에서는 **엑셀 경로를 쓰지 말고** HCell COM만 쓴다. 남은 프로세스는 COM `Quit()`으로만 정리하고 `taskkill` 금지(사용자 문서 소실 위험)
4. `.ps1`은 **UTF-8 BOM**으로 저장해야 한국어 경로가 깨지지 않는다(PS 5.1). 스킬 스크립트는 한국어 리터럴 없이 매개변수로 경로를 받게 했다
5. `HCell.Application` 객체 모델은 엑셀과 거의 같다(Workbooks.Open, CalculateFull, Worksheets.Item, Range.Text/Formula, SaveAs). `SaveAs`에 `.cell` 확장자만 주면 한셀 형식으로 저장된다. `Worksheets.Item("한국어시트명")`도 BOM 스크립트에서는 동작
6. 상세 시트 등 1,000행 넘는 SUMIFS는 한셀 재계산에 1~2분 걸린다. PowerShell timeout을 10분으로

## 갱신 절차 (월별)
1. 새 `집행완료내역_<연도>.xlsx`를 같은 폴더에 덮어쓰기
2. 예산 변경이 있으면 `classify2.py`의 `PLAN`(연도 블록)만 수정 — 총괄표(세부사업별·세목별) 숫자 그대로, 출처 라벨 갱신
3. `build_v2.py` 실행 → `hcell_recalc.ps1` 실행 → 0/0 확인 → 사용자에게 `.cell` 전달
4. 분류 이의가 오면 `YEAR_RULES`에 규칙 추가 후 2~3 반복. 통합문서 '분류기준' 시트가 규칙을 그대로 보여주므로 별도 설명 문서 불필요

## 참고
- 원본 위치·확정사항: 핸드오버 `handover-20260916-mangnam-budget-execution-hancell.md`
- 관련 스킬: `hwp-binary-extract`(월간보고 hwp에서 공식 사업명 추출에 사용)
