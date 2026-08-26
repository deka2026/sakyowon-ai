---
name: hwpx-powershell-edit
description: 한글 문서(.hwpx)를 Python·pandoc 없이 Windows PowerShell만으로 읽고 수정·생성하는 스킬. .hwpx 내용 추출, 문단 텍스트 교체, 새 절·문단 삽입, 수정 부분 빨간색 표시(교정본), 재패키징, 그리고 기존 문서를 템플릿 삼아 요약본 등 새 문서를 표(hp:tbl) 포함으로 조립할 때 사용. 대량 교정(수십~수백 건)에는 인덱스 기반 경로를 쓴다. HWP(구형 바이너리)는 불가 — hwpx만 지원.
---

# HWPX 문서 편집 (PowerShell 전용)

`.hwpx`는 ZIP 안에 XML이 든 포맷이다(OWPML). 본문은 `Contents/section0.xml`의 `<hp:t>` 요소에 있고, 글자모양은 `Contents/header.xml`의 `<hh:charPr>`에 있다.
이 스킬은 Python·pandoc·한글 프로그램 없이 .NET(System.IO.Compression + XmlDocument)만으로 편집한다.

실증: 2026-08-08 전남광주 메가프로젝트 문서 21건 편집 / 2026-08-10 시민공론장 발제문 v4→v5 교정 **102건 + 문단 삽입 3블록, 빨간색 표시 116런, 실패 0**.

## 두 가지 경로 — 어느 쪽을 쓸 것인가

| | A. 인덱스 기반 (`apply_by_index.ps1`) | B. 원문 매칭 (`apply_edits.ps1`) |
|---|---|---|
| 적합 | **교정 다건**(10건 이상), 짧은 조각 수정, 표 셀 수정 | 단건~소수, 문단 전체 교체 |
| 지정 방식 | 덤프의 `[N]` 인덱스 + 그 안의 조각 | 문서 전체에서 유일한 원문 문자열 |
| 강점 | 같은 문자열이 여러 번 나와도 안전(`불필요` 같은 표 셀), 앞뒤 공백 신경 안 씀 | 인덱스 관리 불필요 |
| 빨간색 표시 | **지원** | 미지원 |

기본은 **A**를 쓴다. 아래 절차는 A 기준이다.

---

## 절차

### 1. 추출 + 텍스트 덤프
```powershell
powershell -NoProfile -File scripts\hwpx_dump.ps1 -HwpxPath "원본.hwpx" -WorkDir "작업폴더"
```
- `작업폴더\unpacked\`에 압축 해제, `작업폴더\text_dump.txt`에 `[인덱스] 텍스트` 형식으로 전체 텍스트런 덤프
- 인덱스 = `<hp:t>` 정규식 매치 순번. 표 셀도 각각 하나의 인덱스를 갖는다.
- **덤프 파일의 줄 번호와 `[N]`은 1 차이가 난다** (줄 1 = `[0]`). Read 도구로 볼 때 줄 번호를 인덱스로 착각하는 것이 최다 실수 — 반드시 대괄호 안 숫자를 쓸 것.

### 2. (교정본이면) 빨간색 글자모양 준비
```powershell
powershell -NoProfile -File scripts\add_red_charpr.ps1 -HeaderPath "작업폴더\unpacked\Contents\header.xml" -Offset 41
```
- 기존 charPr 전체(id 0..N-1)를 복제해 `textColor="#FF0000"`으로 바꾼 사본을 id `N..2N-1`에 추가하고 `itemCnt`를 2배로 갱신한다.
- `-Offset`은 **원본 itemCnt와 같아야 한다** (다르면 스크립트가 중단). 덤프 후 `<hh:charProperties itemCnt="?">`를 먼저 확인할 것.
- 이렇게 하면 `red(N) = N + Offset`이라는 단순 규칙이 서고, 글자 크기·글꼴은 원본 그대로 유지된다.

### 3. 편집 데이터 파일 작성
블록 구분자 `@@@`, 파트 구분자 `%%%` (각각 단독 줄). 이스케이프 불필요.

```
REPLIN <인덱스>
%%%
<새 조각>
%%%
<바꿀 옛 조각 — 해당 인덱스 안에서 정확히 1회 나와야 함>
@@@
SET <인덱스>
%%%
<텍스트런 전체를 대체할 새 텍스트>
%%%
<검증용 현재 전체 텍스트(선택) — 다르면 실패>
@@@
INS_AFTER <인덱스>
%%%
<삽입할 hp:p XML 한 줄(여러 문단 연속 가능)>
@@@
INS_BEFORE <인덱스>
%%%
<삽입할 hp:p XML 한 줄>
```

**반드시 지킬 것**
- `REPLIN`을 기본으로 쓴다. 조각만 지정하므로 앞뒤 공백·긴 문단을 그대로 옮겨 적는 위험이 없다.
- 조각이 0회 또는 2회 이상이면 그 건은 실패로 보고되고 **파일을 아예 쓰지 않는다**. 실패 목록에 실제 텍스트가 찍히므로 그걸로 인덱스를 교정한다.
- 새 텍스트에 `<` `>` 금지, `&`는 `&amp;` 형태로만 허용. 「」 · — → ≒ ~ ² ❶ 등은 그대로 사용 가능.
- **원본이 이미 `&amp;`를 담고 있으면**(예: `O&amp;M`) 옛 조각·새 조각 모두 `&amp;`로 적어야 한다. 덤프는 XML 원문을 그대로 보여준다.

### 4. 삽입용 문단 XML 템플릿
**paraPrIDRef/charPrIDRef는 문서마다 다르다.** 대상 문서에서 같은 역할의 기존 문단을 찾아 ID를 확인한 뒤 대입할 것 — `scripts\show_paragraph.ps1`로 특정 인덱스의 문단 XML을 통째로 볼 수 있다.

```powershell
& scripts\show_paragraph.ps1 -SectionPath "...\section0.xml" -Idx @(34,189,359)
```

```xml
<!-- 절 제목 -->
<hp:p id="0" paraPrIDRef="20" styleIDRef="15" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="2"><hp:t>제목</hp:t></hp:run></hp:p>
<!-- 본문 -->
<hp:p id="0" paraPrIDRef="3" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="16"><hp:t> 본문</hp:t></hp:run></hp:p>
<!-- 목록/개조식 -->
<hp:p id="0" paraPrIDRef="22" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="16"><hp:t>1. 항목</hp:t></hp:run></hp:p>
```
- 삽입 문단을 빨간색으로 하려면 `charPrIDRef`에 **red(N) = N + Offset** 값을 직접 쓴다(예: 16 → 57).
- `<hp:linesegarray>`(레이아웃 캐시)는 **넣지 말 것** — 한글이 열 때 재계산한다. 텍스트 길이가 바뀐 문단에 낡은 캐시가 남으면 줄이 겹쳐 그려진다(2026-08-08 실증). apply 스크립트가 기본으로 전체 캐시를 제거한다.
- 표(`<hp:tbl>`) **행 추가는 하지 말 것** — rowCnt 갱신 등 파손 위험. 셀 **텍스트** 수정은 REPLIN으로 안전하다. 빈 셀 채우기·행 추가는 한글에서 사람이 할 일로 남긴다.

### 5. 적용
```powershell
& scripts\apply_by_index.ps1 -SectionPath "작업폴더\unpacked\Contents\section0.xml" -EditsPath "edits.txt"
```
- 빨간색을 끄려면 `-NoRed`, 캐시를 보존하려면 `-KeepLineSegs`, 오프셋이 다르면 `-RedOffset N`.
- 동작: 전 건 검증 → 겹침 검사 → **내림차순 위치로 스플라이스**(인덱스 밀림 없음) → 캐시 제거 → XmlDocument 유효성 검증 → 기록. 한 건이라도 실패하면 아무것도 쓰지 않는다.
- 빨간색 모드에서는 런을 3분할한다: `앞부분(원래색) + 수정부분(빨강) + 뒷부분(원래색)`.

**중요 — 실행 순서**: REPLIN/SET는 런을 분할하므로 `<hp:t>` 개수가 늘어난다. 따라서
1. **REPLIN/SET만 담은 파일을 먼저 1회 실행**
2. **다시 덤프해 새 인덱스를 확인한 뒤** INS_AFTER/INS_BEFORE 파일을 실행
순서를 지킬 것. 한 파일에 섞으면 삽입 위치가 어긋난다.

### 6. 재패키징 + 검증
```powershell
& scripts\hwpx_repack_multi.ps1 -SourceHwpx "원본.hwpx" -UnpackedDir "작업폴더\unpacked" -OutHwpx "수정본.hwpx"
```
- 기본으로 `Contents/section0.xml`과 `Contents/header.xml`을 함께 교체한다. **빨간색 표시를 했으면 header.xml을 반드시 같이 넣어야 한다** — section만 바꾸면 존재하지 않는 charPr을 참조하게 된다. (구 `hwpx_repack.ps1`은 section만 교체하므로 이 경우 쓰면 안 됨)
- 나머지 엔트리(mimetype 등)는 원본을 복사해 보존한다. **원본은 덮어쓰지 말고 새 파일명으로 출력**할 것.
- 재패키징 후 새 파일을 다시 덤프해, 반영돼야 할 문자열과 **사라져야 할 옛 문자열을 각각 카운트**해 확인한다(0이어야 할 것이 0인지까지).

---

## 함정 (실전에서 걸린 것들)

1. **덤프 줄 번호 ≠ 인덱스** (줄 N = `[N-1]`). 2026-08-10 교정에서 102건 중 8건이 이 착오였다 — 검증기가 전부 잡아냈다.
2. **비분리 공백(U+00A0)**: 한글에서 작성한 문서에는 일반 공백처럼 보이는 NBSP가 섞여 있다. 눈으로 똑같아 보이는데 매치가 0회면 이걸 의심하고, **NBSP를 피한 짧은 조각**으로 바꿔 지정한다. 문자 코드 비교로 확인:
   ```powershell
   ($s.ToCharArray() | ForEach-Object { [int]$_ }) -join ','
   ```
3. **PS 5.1 스크립트 인코딩**: BOM 없는 .ps1의 한국어 리터럴은 깨진다. 한국어는 전부 데이터 파일(edits.txt)에 두고 .ps1은 ASCII만 사용 — 이 스킬의 스크립트가 이미 그렇게 설계됨.
4. **PS 5.1 배열 파라미터**: `-Idx 1,2,3`은 파싱 실패한다. `-Idx @(1,2,3)`으로 쓰고, `powershell -File` 대신 `& 스크립트`로 호출할 것.
5. **따옴표 불일치**: 문서의 컬리(''  U+2018/2019)와 새로 타이핑한 스트레이트(')가 달라 매치 실패. `hwpx_dump.ps1`이 개수를 세어 알려주므로 먼저 확인하고, 통일이 목적이면 옛 조각에 컬리·새 조각에 스트레이트를 적어 REPLIN으로 바꾼다(`apply_by_index.ps1`은 자동 정규화를 하지 않으므로 의도대로 동작한다).
6. `Preview/PrvText.txt`(미리보기 캐시)는 갱신 안 해도 무방 — 한글이 저장 시 재생성.
7. **완료 기준**: XML 유효 + 재추출 검증(있어야 할 것/없어야 할 것 양방향)까지. 최종 서식은 한글에서 육안 확인 권장. 사용자가 한글에서 확인·정리(빨간색 제거 등)하고 저장하면 런이 다시 병합돼 `<hp:t>` 개수가 줄어드는 것이 정상이다.

## 교정본 워크플로 요약

```
v4 원본 → 덤프 → (교정 목록 작성) → add_red_charpr → REPLIN 일괄 적용
        → 재덤프 → INS 적용 → repack_multi → v5(빨간 교정본)
        → 사람이 한글에서 검토·수락·빨간색 제거 → 최종본
```
빨간색은 "AI가 무엇을 건드렸는지"를 사람이 한눈에 확인하기 위한 것이다. 검토를 거치지 않은 자동 수정본을 최종본으로 삼지 말 것.

## 경로 C — 새 문서 조립 (요약본·통합본 생성, 표 포함)

기존 문서를 **서식 템플릿**으로 삼아 완전히 새 본문(문단+표)을 조립한다. 2026-08-25 두 사업계획서(322·236런)를 표 10개짜리 6쪽 통합 요약 hwpx로 생성해 실증.

1. **템플릿 분석**: 원본을 `hwpx_dump.ps1`로 덤프하고 `show_paragraph.ps1`로 제목·절 제목·본문·들여쓰기 문단의 paraPrIDRef/charPrIDRef를 채록. 표가 있으면 표 하나를 잘라 셀 서식(헤더 셀 borderFill/paraPr/charPr, 본문 셀은 별도)과 **표 전체폭**(hp:sz width, 보통 47622 HWPUNIT)을 확인.
2. **spec 파일 작성** (UTF-8, 한국어 가능): 한 줄 한 요소.
   ```
   H1|큰 제목          H1PB|쪽 나눔 후 큰 제목
   H2|절 제목           P|본문 문단
   TBL|열폭1,열폭2,...   ← 합이 표 전체폭(47622)과 같아야 함(스크립트가 검증)
   R|셀1|셀2|...        ← TBL 직후 연속. 첫 R = 머리행(음영)
   END                  ← 표 종료
   ```
   셀 텍스트에 `|` 금지(·로 대체), `< >` 금지, `&`는 `&amp;`.
3. **생성**: `& scripts\build_fragment.ps1 -SpecPath spec.txt -OutPath fragment.xml` — 문단·표 XML을 한 줄로 출력. 서식 ID가 템플릿과 다르면 스크립트 상단 Cell 함수와 H1/H2/P 분기의 ID를 템플릿 채록값으로 교체.
4. **조립**: XmlDocument로 원본 section0.xml을 열어 **첫 hp:p(secPr·머리말 포함)만 남기고 전부 제거** → fragment를 `<wrap xmlns:hp="...">`로 감싸 파싱 → ImportNode로 append → 저장 후 linesegarray 전부 제거.
   - 첫 문단은 중첩 hp:p(머리말 subList)를 포함하므로 정규식으로 자르지 말고 반드시 DOM으로 다룰 것.
5. **재패키징·검증**: `hwpx_repack_multi.ps1`(header.xml 무수정이어도 함께 교체해 무방) → 새 파일 재덤프로 있어야 할 문자열 확인. 쪽수는 한글이 열 때 재계산되므로 목표 쪽수는 내용량으로 근사하고 육안 확인으로 마무리.

표 관련 요령: `treatAsChar="1"`(인라인)·`repeatHeader="1"`이 기본. 셀 높이(cellSz height)는 최소값이라 내용에 따라 자동 확장된다. 표 id는 테이블마다 유일하게(생성기가 1900000001부터 증가). 행 수를 rowCnt와 일치시키는 것은 생성기가 보장한다.

## 경로 D — 파이썬 빌더로 새 문서 생성 (`scripts/hwpx_gen.py`)

경로 C의 파이썬 버전. spec 파일 없이 **코드로 문서를 조립**할 때 쓴다 — 반복 구조(과×팀 20개), 조건 분기, 여러 판본(v2·v3·v4) 재생성이 필요한 문서에 유리. 2026-08-25 시민주권본부 조직설계안(196문단, 박스형 조직도 표 8×5 colSpan 병합 + 총괄표 21×3, 4개 판본 재생성)으로 실증.

```python
import sys; sys.path.insert(0, r'...\skills\hwpx-powershell-edit\scripts')
from hwpx_gen import HwpxDoc
d = HwpxDoc(r'템플릿.hwpx')          # 스타일 ID가 다른 템플릿이면 styles= 로 오버라이드
d.title('문서 제목')                  # 반드시 첫 호출 — secPr·colPr를 이 문단이 운반
d.h1('1.', '장 제목')                 # page_break=True 로 쪽 나눔
d.dept('❶ 절 제목'); d.team('❶-1. 소제목'); d.band('띠 제목')
d.b1('● 불릿'); d.b2('○'); d.b3('–'); d.b4('▸')   # lead= 로 강조 선행어
d.table(rows, widths, header_rows=(0,2))   # 셀 = [문단들] 또는 ([문단들], colspan)
d.save(r'출력.hwpx')                  # XML 검증 → OCF(mimetype 우선·STORED) 재패키징까지 일괄
```

- 기본 스타일 ID는 사교원 표준 사업계획서 템플릿(재생에너지 전략 문서) 기준. 다른 템플릿은 `show_paragraph.ps1`로 채록해 `DEFAULT_STYLES` 형태의 dict를 전달.
- **박스형 조직도**는 colSpan 병합 표로 만든다: 전폭 1셀(위원회) → 전폭 1셀(▼ 화살표 행) → 5셀(과) → 5셀(팀 목록, 셀당 여러 문단) → 전폭 1셀(중간지원조직). `header_rows`로 음영 행 지정.
- 표를 독립된 1쪽에 넣으려면 표 앞뒤 h1에 `page_break=True`.

### 경로 D 함정 (2026-08-25 실전)
1. **출력 파일이 한글에서 열려 있으면 잠겨서 저장 실패** — 같은 이름 덮어쓰기 대신 v2·v3 등 새 파일명으로 출력하고 사용자에게 알릴 것.
2. `esc()`는 `&`만 이스케이프한다. 본문에 `< >`는 아예 넣지 말 것(파싱 오류). `R&D`는 그냥 쓰면 `R&amp;D`로 저장돼 정상.
3. `save()` 안에서 지역변수를 `xml`로 짓지 말 것 — `from xml.dom import minidom` 계열 import가 이름을 가린다(실제로 걸림, 현재 코드는 `content`로 회피).
4. HWP 구형(.hwp)·확장자 없는 3MB 파일 텍스트 추출 시 **서로게이트 문자로 UTF-8 쓰기 실패** 가능 — `text.encode('utf-8','ignore').decode('utf-8')` 후 저장(hwp-binary-extract 스킬 병용).
5. 조판 캐시(linesegarray)는 아예 생성하지 않는 방식이라 별도 제거 불필요. 한글이 열 때 재계산.
