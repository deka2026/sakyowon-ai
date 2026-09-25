---
name: hwpx-powershell-edit
description: 한글 문서(.hwpx)를 Python·pandoc 없이 Windows PowerShell만으로 읽고 수정·생성하는 스킬. .hwpx 내용 추출, 문단 텍스트 교체, 새 절·문단 삽입, 수정 부분 빨간색 표시(교정본), 재패키징, 그리고 기존 문서를 템플릿 삼아 요약본 등 새 문서를 표(hp:tbl) 포함으로 조립할 때 사용. 대량 교정(수십~수백 건)에는 인덱스 기반 경로를 쓴다. 편집·생성은 hwpx만 가능하고 구형 .hwp를 직접 뜯어 고치지는 못하지만, 완성된 hwpx를 한글 COM으로 .hwp 제출본으로 변환할 수 있다(경로 H) — "한글파일로 만들어줘"가 .hwp를 뜻할 때 쓴다.
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
6-1. **표지 배너 제목은 여러 런으로 쪼개져 있다**: 시민주권 계획안 계열 템플릿의 표지 제목은 `고흥군 영농형태양광 ` / `시민주권` / ` ` / `계획(안)` 처럼 4개 `<hp:t>`로 나뉘어 있다. 제목 전체 문자열로 검색하면 0회이므로 **조각 단위로 치환**할 것. 또한 배너에 이미 제목이 있으므로 **본문 첫머리에 제목 문단(paraPr 15/charPr 1)을 또 넣으면 제목이 두 번 표시된다** — 2026-08-26 실제 발생, 사용자 지적. 새 문서 조립 시 표지 prefix는 그대로 두고 본문은 부제(paraPr 20/charPr 30)부터 시작한다.
6-2. **재조립 반복 시 작업 폴더는 새 이름으로**: 기존 작업 폴더를 `Remove-Item -Recurse`로 지우려다 샌드박스 경로 보호에 걸려 명령이 통째로 중단될 수 있다. `fresh2`, `fresh3`처럼 새 폴더명으로 다시 풀면 그만이다. 원본 hwpx에서 매번 새로 풀어야 이전 회차의 편집이 섞이지 않는다.
7. **완료 기준**: XML 유효 + 재추출 검증(있어야 할 것/없어야 할 것 양방향)까지. 최종 서식은 한글에서 육안 확인 권장. 사용자가 한글에서 확인·정리(빨간색 제거 등)하고 저장하면 런이 다시 병합돼 `<hp:t>` 개수가 줄어드는 것이 정상이다.
8. **한글 재저장본은 서식 ID가 통째로 재매핑된다** (2026-09-09 실증): AI가 만든 hwpx를 사용자가 한글에서 편집·저장하면 paraPr/charPr ID가 바뀐다(시민기금 문서: 불릿 21→28, h1 25→23, 소제목 23/11→31/11, 셀 28/10→26/18·10, 새 charPr 추가·itemCnt 증가). 이전 세션의 채록값을 절대 재사용하지 말고 **편집할 때마다 show_paragraph.ps1로 재채록**할 것. 글자 크기(height)도 함께 확인.
9. **기존 문서 끝에 새 장(章) 삽입 — fragment 삽입법**: 전체 재조립 대신 문단+표 XML fragment를 만들어 section0.xml의 `</hs:sec>` 직전에 문자열 삽입 → minidom 검증 → zipfile 재패키징(mimetype 우선 STORED). 기존 문단과 조판 캐시는 건드리지 않으므로 안전하다(문서 끝 추가는 앞쪽 레이아웃에 영향 없음). 표 골격은 hwpx_gen.table과 동일하되 채록한 셀 paraPr/charPr/borderFill로 교체하고 표 id는 유일화. 2026-09-09 시민기금 12장(표 5개 6쪽 분량), 2026-09-10 펀드 문서 전면 재조립(다른 문서를 서식 템플릿으로 — 스타일 dict만 재채록해 경로 D 함수 재사용)으로 실증.

10. **같은 낱말을 문서 전체에서 바꿀 때는 REPLIN을 쓰지 말 것**: `apply_by_index.ps1`의 REPLIN은 조각이 한 인덱스 안에서 **정확히 1회**여야 하고, 여러 `<hp:t>` 런에 걸쳐 잘린 낱말(표 셀의 `❹ 공동체기업` + `육성팀`)은 아예 찾지 못한다. 조직개편 팀명 치환처럼 같은 낱말이 수십 번 나오는 작업은 스킬 `orgchart-doc-migration`의 `hwpx_retag.py`를 쓴다 — 모든 런을 이어붙인 문자열에서 찾고 런 경계를 넘는 것도 처리하며, 빨간 표시와 잔존 옛말 0건 검증까지 한다. 2026-09-11 참고문서 2종 22건 치환으로 실증.

## 교정본 워크플로 요약

```
v4 원본 → 덤프 → (교정 목록 작성) → add_red_charpr → REPLIN 일괄 적용
        → 재덤프 → INS 적용 → repack_multi → v5(빨간 교정본)
        → 사람이 한글에서 검토·수락·빨간색 제거 → 최종본
```
빨간색은 "AI가 무엇을 건드렸는지"를 사람이 한눈에 확인하기 위한 것이다. 검토를 거치지 않은 자동 수정본을 최종본으로 삼지 말 것.

## 경로 C — 새 문서 조립 (요약본·통합본 생성, 표 포함)

기존 문서를 **서식 템플릿**으로 삼아 완전히 새 본문(문단+표)을 조립한다. 실증 2회: 2026-08-25 두 사업계획서(322·236런)를 표 10개짜리 6쪽 통합 요약 hwpx로 생성 / 2026-08-26 참고사례집 12건(사례별 개요→5항목 표→시사점 패턴, 표 13개, 종합 비교표 12×5 포함) 생성. 사례집·비교자료처럼 같은 구조가 반복되는 문서에 특히 적합하다.

1. **템플릿 분석**: 원본을 `hwpx_dump.ps1`로 덤프하고 `show_paragraph.ps1`로 제목·절 제목·본문·들여쓰기 문단의 paraPrIDRef/charPrIDRef를 채록. 표가 있으면 표 하나를 잘라 셀 서식(헤더 셀 borderFill/paraPr/charPr, 본문 셀은 별도)과 **표 전체폭**(hp:sz width)을 확인.
   - **표 전체폭은 반드시 본문폭 이하** = `pagePr@width − margin@left − margin@right` (section0.xml secPr에서 매번 계산). 47622를 관행으로 쓰면 여백 6519인 사교원 발제문 템플릿(본문폭 46490)에서 **오른쪽으로 약 4mm 넘친다** — 2026-08-28 사용자 지적. 초과 표 교정법: hp:sz width를 본문폭으로 줄이고 각 hp:tr 마지막 hp:tc의 cellSz width에서 초과분 차감(DOM 처리).
2. **spec 파일 작성** (UTF-8, 한국어 가능): 한 줄 한 요소.
   ```
   H1|큰 제목          H1PB|쪽 나눔 후 큰 제목
   H2|절 제목           P|본문 문단
   TBL|열폭1,열폭2,...   ← 합이 표 전체폭과 같아야 함(스크립트가 검증. build_fragment.ps1 기본값 47622는 본문폭 46490 템플릿에서 넘치므로 스크립트의 47622 두 곳을 본문폭으로 바꿔 사용)
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

## 경로 E — 목표 쪽수 맞추기 (한글 COM 측정 루프)

"10쪽 분량으로 만들어" 같은 요구가 붙었을 때. hwpx는 조판 결과를 파일이 갖고 있지 않으므로 **한글로 열어봐야 쪽수를 알 수 있다.** 2026-08-26 공론장 발제문(15쪽 초안 → 10쪽 확정, 이후 기본법 반영으로 11쪽)에서 확립.

```powershell
& scripts\hwpx_pagecount.ps1 -HwpxPath "test.hwpx" -Pdf   # pages=N 출력 + 확인용 PDF
```

측정 → 압축 → 재측정 루프를 돈다. **PDF를 Read 도구로 열어 어느 쪽에 여백이 남는지 눈으로 보는 것이 핵심** — 글자 수만 세면 헛수고한다.

### 쪽수를 줄이는 수단 (효과 큰 순서)

| 수단 | 효과 | 방법 |
|---|---|---|
| 쪽 나눔 제거 | 쪽당 최대 0.5쪽 | `page_break=True`를 꼭 필요한 장에만. 초안에서 7개 → 1개로 줄여 15→12쪽 |
| **큰 표 쪼개기** | 쪽당 최대 0.5쪽 | 인라인 표는 페이지 분할이 안 된다(아래 함정 1). 6행 표 하나를 3행+3행 두 개로 쪼개면 앞 페이지 빈 공간에 앞 조각이 들어간다 |
| 열 폭 재배분 | 행당 1줄 | 셀이 2~3줄로 접히는 열을 넓히고 짧은 열을 좁힌다. 모든 행이 1줄이 되면 표 높이가 절반 |
| `body_h` 축소 | 행당 소폭 | 행 높이는 **최소값**이므로 900~1000으로 낮춰도 내용에 따라 자동 확장. 기본 1800~2200은 과하다 |
| 표 → 산문 | 0.3쪽 | 3~4행짜리 작은 표는 문단 하나로 접는 편이 낫다 |
| 행 병합 | 행당 1~2줄 | 인접한 두 단계·두 항목을 한 행으로("① 의제화 · 예산화") |

### 함정 (2026-08-26 실전)

1. **인라인 표는 페이지를 넘지 못한다.** 생성기가 `treatAsChar="1"`(글자처럼 취급)로 표를 넣기 때문에, `pageBreak="CELL"` 속성이 있어도 한글은 표를 쪼개지 않고 통째로 다음 쪽으로 보낸다. 남은 공간보다 표가 크면 그만큼이 그대로 빈다 — **표를 쪼개는 것이 유일한 해법**.
2. **남은 공간이 표보다 커 보여도 안 들어갈 수 있다.** 여유가 1cm 안쪽이면 실패한다고 보고 표를 2~3줄 더 줄일 것.
3. **여러 파일을 foreach로 돌리면 COM이 멈춘다.** `$o.XHwpDocuments.Close()` 후 다음 파일을 열는 루프가 응답 없이 대기 상태로 빠졌다(5개 문서 일괄 검증 시). **파일 하나당 프로세스 하나**로 호출할 것.
4. **강제 종료 후 첫 호출은 오염될 수 있다.** `Stop-Process`로 한글을 죽인 뒤 다시 열면 `PageCount`가 1로 나오거나 SaveAs가 멈춘다. `-KillStale`로 죽인 뒤 2초 대기하고, 그래도 이상하면 문서 XML(`<hp:p>`·`<hp:tbl>` 개수, 총 글자 수)로 교차 확인한다.
5. **마크다운 강조 기호가 그대로 찍힌다.** 생성기 본문에 `**강조**`를 쓰면 별표가 문서에 남는다. 강조는 `lead=` 인자나 별도 charPr로.
6. 셀에 `\n`을 넣어 줄바꿈하려 하지 말 것 — XML 텍스트에 실제 개행이 들어간다. 셀을 **문단 리스트**로 주면 된다: `['❶ 고흥군', '영농형 분양형']`.

### 마무리 체크

- 목표 쪽수 ±1은 협상 가능하다고 보고, 초과분이 **내용 증가 때문인지 조판 낭비 때문인지** 구분해 보고할 것. 낭비면 줄이고, 내용이면 사용자에게 알린다.
- 최종본은 새 파일명으로 출력하고(경로 D 함정 1) 확인용 PDF를 함께 전달한다.

## 경로 F — 본문 12pt와 생성 후 실검증 (`scripts/patch_body_12pt.py`)

2026-09-09-10 실전에서 확립. **문서를 만들었다고 끝이 아니다** — 실제로 열리는지까지 봐야 완료다.

### F-1. 본문 12pt 만들기

사교원 규칙: **hwpx 본문도 표 셀도 12pt.** (2026-09-10 사용자 확정 — 그 전의 "표 셀 10pt 유지"는 폐기.) 사교원 템플릿의 본문 charPr은 대개 10pt(height=1000)라 그대로 쓰면 규칙에 어긋난다. 본문·불릿·셀에 쓰는 charPr을 12pt 사본으로 복제하고 생성기 STYLES에서 새 id를 가리킨다. 셀을 키우면 좁은 열이 접히므로 열 폭 재배분을 함께 한다. 이미 완성된 문서(외부 빌더 산출물)라면 경로 G의 `hwpx_house_rules.py`가 한 번에 처리한다.

```python
from patch_body_12pt import list_charprs, patch_body_pt
list_charprs('template.hwpx')                                   # id·height·color 채록
m = patch_body_pt('template.hwpx', 'tpl_12pt.hwpx', ['8','10','11','12'])
# m == {'8':'19','10':'20','11':'21','12':'22'}
# STYLES의 body.charpr / bullet 마커·em_charpr 에 새 id를 넣고 cell.charpr은 그대로 둔다
```

글꼴·굵기·색은 원본 그대로 유지되고 크기만 바뀐다. 복제할 id는 `show_paragraph.ps1`이나 `list_charprs`로 먼저 채록할 것.

### F-2. 교정본을 최종본으로 확정하기

빨간펜 교정본을 사용자가 수락하면 `clear_red(src, out)`로 **글자모양의 색만** 검정으로 되돌린다. `section0.xml`은 바이트 그대로 보존되므로 본문이 변형될 위험이 없다.

```python
from patch_body_12pt import clear_red
clear_red('..._교정_v1.0.hwpx', '..._최종.hwpx')   # 되돌린 charPr id 목록 반환
```

### F-3. 생성 직후 검수 4단계 — 이 순서를 건너뛰지 말 것

```python
from docutil import patch_table, fix_tbl_ids, sanitize_package, audit
d = patch_table(HwpxDoc('tpl_12pt.hwpx', styles=STYLES))   # ① 셀 정규화 래퍼 필수
...
d.save(out)
fix_tbl_ids(out)                                           # ② 표 id 유일화
sanitize_package(out, '문서 제목',                          # ③ 템플릿 잔재 제거 (필수)
                 '2026-09-18T00:00:00Z', '2026년 9월 18일 금요일')
print(audit(out))                                          # ④ 지표
```

**③을 빠뜨리면 템플릿의 `Preview/PrvText.txt`·`PrvImage.png`가 그대로 딸려 간다.**
탐색기 미리보기와 검색 인덱스에 **이전 문서 1쪽이 통째로** 뜬다 — 회의록 템플릿이면 참석자
실명이 새 문서에 붙어 외부로 나간다(2026-09-18 실제 발생). Preview 파일만 지우는 것으로는
부족하다. **`META-INF/container.xml`이 `Preview/PrvText.txt`를 `<ocf:rootfile>`로 선언**하므로
그 선언도 함께 지워야 끊긴 참조가 남지 않는다(같은 날 2차 회귀로 발생). `content.hpf`의
`opf:manifest`, `META-INF/manifest.xml`, `container.rdf`에는 참조가 없다. `sanitize_package`는
둘을 한 번에 처리하고, 남은 rootfile이 실제 zip 항목인지 검사한 뒤
`opf:title`·`CreatedDate`·`ModifiedDate`·`date`도 새 값으로 바꾼다.

> 템플릿 잔재를 점검할 때는 **zip 전체 항목**을 훑을 것. `Contents/` 아래만 보면 놓친다.
> `zipfile.ZipFile(p).namelist()`를 먼저 찍고 각 항목을 디코드해 검색한다.

| 지표 | 정상 범위 | 벗어나면 |
|---|---|---|
| `paras_per_cell` | 1.0~1.5 | 셀에 문자열을 넘긴 버그(글자마다 문단) |
| `unique_ids` | `tables`와 같아야 | 표 id가 전부 0 |
| `section_kb` | 템플릿과 같은 자릿수 | 위 두 버그 중 하나 |
| 표 폭 | 본문폭 이하 | 오른쪽 넘침 |

③ **한글로 실제 열어본다.** `hwpx_pagecount.ps1 -Pdf`로 열고 PDF를 Read 도구로 눈으로 확인. **XML 검증만으로는 열림을 보장하지 못한다** — 셀 버그 문서도 `minidom.parseString`은 통과한다.

### F-4. 한글이 실행 중일 때 — 죽이지 말고 구조 대조로 대체

```powershell
Get-Process Hwp -ErrorAction SilentlyContinue | Select-Object Id,@{n='T';e={$_.MainWindowTitle}}
```

`MainWindowTitle`에 사용자 문서명이 보이면 **COM을 쓰지 않는다**(미저장 문서 소실 위험). 대신 **열림이 확인된 문서와 구조를 대조**하고, 검증 방식을 사용자에게 그대로 알린다.

대조 항목: XML 유효 / mimetype 첫 엔트리·STORED / 표 개수·id 유일성 / 표 폭 초과 / `paras_per_cell` / 미해결 charPr·paraPr·style 참조 / `secPr` 존재 / `linesegarray` 잔존

### 경로 F 함정

1. **문서가 안 열린다는 신고를 받으면 XML 검증부터 하지 말 것.** well-formed인데 안 열리는 경우가 실제로 있었다. `audit`의 문단 수·파일 크기를 먼저 본다.
2. `list_charprs`는 `with`로 닫지만, 직접 `zipfile.ZipFile(...)`을 열어 비교하면 핸들이 남아 임시파일 삭제가 실패한다(WinError 32). 검증 스크립트에서도 `with`를 쓸 것.
3. **한글이 재저장한 파일은 charPr이 재매핑된다.** 교정본을 사용자가 한글에서 저장했다면 id를 다시 채록해야 한다(이번엔 빨강이 24로 이동해 있었다).

## 표 쪽 분할 규칙 (2026-09-12 실증) — 반드시 `treatAsChar="0"`

한글은 **글자처럼 취급(`<hp:pos treatAsChar="1">`) 표를 쪽 경계에서 나누지 않는다** (`pageBreak="CELL"`이어도). 한 쪽보다 큰 표는 통째로 다음 쪽으로 밀려 앞 쪽이 비고, 넘치는 행은 바닥 여백 밖으로 그려지다 잘린다. 실험 7종 중 **자리차지(`treatAsChar="0"`, textWrap TOP_AND_BOTTOM, vertRelTo PARA)** 만 정상 분할됐다. `hwpx_gen.py`·`gen_lib_baljemun.py`(발제문 템플릿용 Doc 서브클래스, 본문폭 46490)는 이미 0으로 고쳐 두었고, `build_fragment.ps1`은 아직 1이므로 쓸 때 바꿀 것. 기존 문서 교정은 section0.xml에서 `treatAsChar="1" affectLSpacing="0" flowWithText="1"` → `treatAsChar="0" …` 치환만으로 충분.

**쪽수 측정·PDF**: `hwpx_pagecount.ps1`은 한글 보안 확인창("접근 허용/모두 허용", WPF MessageBoxImpl)에 걸려 멈춘다. `scripts\pagecount_auto.ps1`이 UI Automation으로 창을 찾아 Alt+N을 보내며 실행한다:
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\pagecount_auto.ps1 -HwpxPath "out.hwpx" -Pdf
```
`-ExecutionPolicy Bypass` 필수(기본 정책이 .ps1 실행 차단). 실행 전 `tasklist | findstr Hwp`로 사용자 한글이 떠 있지 않은지 확인. 검수는 PDF를 PyMuPDF로 쪽별 PNG + 접촉 시트(6열·40dpi)로 만들어 빈 쪽·넘침을 한눈에 본다.

## 경로 G — 외부 빌더 산출물에 사내 규칙 적용 (`scripts/hwpx_house_rules.py`)

2026-09-16 실전. 다른 세션·다른 사람이 **python-hwpx**(`from hwpx.document import HwpxDocument`, `pip install python-hwpx`) 같은 외부 빌더로 만든 hwpx는 XML은 유효하지만 사내 규칙(본문·셀 12pt, 표 자리차지, 셀 왼쪽 정렬)에 어긋난다. 스크립트를 고치지 말고 **산출물에 규칙을 덧입힌다** — 어떤 빌더의 결과물에도 같은 도구가 통한다.

```bash
python scripts/hwpx_house_rules.py in.hwpx out_rules.hwpx            # --min-pt 12 기본
# {'raised_charpr': {'11': (1050, 1200), ...}, 'tables_inflow': 13, 'cell_paras_left': 297, 'parapr_added': {'0': '29'}}
```

| 처리 | 방법 | 비고 |
|---|---|---|
| 12pt | section에서 **실제 참조되는** charPr 중 height<1200만 1200으로 | 미참조 기본값(각주 9pt 등)·이미 큰 제목은 그대로 |
| 표 자리차지 | `<hp:pos … treatAsChar="1">` → `"0"` | 표 쪽 분할 규칙 그대로 |
| 셀 왼쪽 정렬 | `<hp:tc>` 안 문단이 쓰는 JUSTIFY paraPr을 LEFT 사본으로 복제(itemCnt 갱신)해 셀 문단만 재지정 | 본문 양쪽 정렬은 유지. 좁은 열에서 "협 동 조 합" 식 글자 벌어짐 제거 |

절차: ① 원 스크립트를 **그대로** 한 번 돌려 원판을 남긴다(비교 기준) → ② 후처리 → ③ 12pt에서 접히는 좁은 열("번호" 0.9 → 1.15)은 스크립트의 열 폭 비율만 고쳐 재빌드 → ④ `pagecount_auto.ps1 -Pdf` + 접촉 시트로 F-3 ③ 검수. 세무사 인터뷰 질문지(표 13개·44문항)로 실증: 10.5pt 원판 → 12pt 10쪽, 표 전부 정상 분할.

**파일이 로컬에 없을 때** — 사용자가 `wiki/assets/….build.py`처럼 경로만 준 경우, AI 세션이 만든 `claude/…` 브랜치는 main에 없는 것이 기본이다. 두 org 전 레포·전 브랜치를 훑는다:
```bash
for r in $(gh repo list <org> --limit 50 --json nameWithOwner --jq '.[].nameWithOwner'); do
  for b in $(gh api "repos/$r/branches?per_page=50" --jq '.[].name'); do
    gh api "repos/$r/git/trees/$b?recursive=1" --jq '.tree[].path' | grep -i "<이름>" && echo "== $r @ $b"; done; done
gh api -H "Accept: application/vnd.github.raw" "repos/<o>/<r>/contents/<path>?ref=<branch>" > 파일   # 클론 없이 받기
```

### 경로 G 함정
1. python-hwpx `ensure_run_style`은 속성이 같은 스타일을 **같은 id로 합친다**(C_CELL과 C_BODY가 모두 12pt면 하나). 후처리 보고의 id 개수가 스타일 변수 수보다 적어도 정상.
2. python-hwpx 산출물의 빈 셀 문단은 `charPrIDRef="0"`(기본 10pt)을 참조하므로 0번도 함께 올라간다. 쪽번호 각주(`- 1 -`)도 0번이라 12pt가 된다 — 문제 되면 `--no-font` 후 `patch_body_12pt`로 선택 적용.
3. 셀 LEFT 사본은 문서 전체 paraPr 뒤에 붙는다. 한글이 재저장하면 id가 재매핑되므로(함정 8) 다음 편집 전 재채록.

## 경로 H — 구형 .hwp 제출본 만들기 (`scripts/hwpx_to_hwp.ps1`)

2026-09-25 실증. **"한글파일로 만들어줘"는 대개 .hwp를 뜻한다.** 이미 hwpx를 건넨 뒤에 이 말이 나왔다면 거의 확실히 구형 포맷 요청이다 — 되묻기 전에 이 경로를 먼저 떠올릴 것. 관공서 제출·메일 첨부는 여전히 .hwp를 요구하는 곳이 많다.

XML을 직접 만들 수는 없지만 **한글 COM의 `SaveAs(path, "HWP", "")`가 변환해 준다.** 이 스킬로 hwpx를 완성한 뒤 마지막에 한 번 돌리면 된다.

```powershell
# 변환 (한글 보안 확인창 자동 처리)
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\run_auto.ps1 `
  -Script scripts\hwpx_to_hwp.ps1 -HwpxPath "out.hwpx"
# → pages=38 / hwp=...\out.hwp

# 검증: 변환본을 다시 열어 쪽수와 본문 확인
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\run_auto.ps1 `
  -Script scripts\hwp_verify.ps1 -HwpxPath "out.hwp"
# → pages=38 / txt=...\out.verify.txt  (확인 후 지울 것)
```

- `run_auto.ps1`은 `pagecount_auto.ps1`의 범용판이다 — `-Script`로 아무 COM 워커나 받고, 시작 전부터 떠 있던 Hwp 프로세스는 건드리지 않으며 보안 확인창만 Alt+N으로 닫는다. 새 COM 워커를 쓸 때마다 dismissal 로직을 다시 짜지 말고 이걸 감싸 쓸 것.
- `hwpx_to_hwp.ps1`은 hwpx를 `"HWPX"` 포맷으로 열고 `"HWP"`로 SaveAs한다. `-HwpPath`로 출력 경로 지정 가능(기본은 확장자만 교체).
- `hwp_verify.ps1`은 .hwp를 `"HWP"`로 다시 열어 `PageCount`와 TEXT 덤프를 낸다. **변환만 하고 끝내지 말 것** — 열어서 쪽수와 장 제목이 그대로인지 보는 것까지가 완료다(경로 F-3 ③과 같은 원칙).

### 경로 H 함정
1. **변환·검증은 각각 별개 프로세스로.** 한 프로세스에서 open→save→quit→reopen을 이으면 COM이 멈춘다(경로 E 함정 3과 같은 이유). 그래서 워커를 두 파일로 나눠 두었다.
2. **TEXT 덤프의 `&#8212;`는 오류가 아니다.** 한글의 평문 내보내기가 cp949라 em dash(—)를 HTML 엔티티로 적을 뿐, 문서 안의 글자는 멀쩡하다. 검증 텍스트만 보고 "문자가 깨졌다"고 보고하지 말 것 — 실제 확인은 PDF 렌더로 한다.
3. 세 포맷을 다 남기는 것이 편하다: **`.hwp`(제출·배포) · `.hwpx`(다음 수정 작업) · `.pdf`(육안 확인)**. 다음 편집은 반드시 hwpx 쪽에서 하고, 고친 뒤 .hwp를 다시 뽑는다. .hwp를 고쳐 놓고 hwpx를 갱신하지 않으면 두 파일이 갈라진다.

## 경로 I — 그림 넣기 (`scripts/hwpx_embed_images.py`)

2026-09-25 실증(사업기획안 41쪽에 개념도 4장). hwpx의 그림은 **세 곳이 맞아야** 보인다. 한 곳만 빠져도 한글이 조용히 빈칸으로 연다.

| 위치 | 내용 |
|---|---|
| `BinData/<id>.png` | 이미지 바이트 |
| `Contents/content.hpf` 의 `opf:manifest` | `<opf:item id="<id>" href="BinData/<id>.png" media-type="image/png" isEmbeded="1" hashkey="<md5 base64>"/>` |
| `Contents/section0.xml` 의 `hp:pic` | `<hc:img binaryItemIDRef="<id>" …/>` |

`META-INF/manifest.xml`은 비어 있어도 되고 **header.xml에는 등록하지 않는다** — 참조 문서를 뜯어 확인했다.

```python
from hwpx_embed_images import PicPlacer, embed_images, audit_images
pics = PicPlacer(d, S, body_width=46400)     # d = HwpxDoc, S = 스타일 dict
pics.place('fig1.png', 1000, 560, '[그림 1] 전체 공정 흐름')
d.save(out)
embed_images(out, pics.registry)             # 반드시 save() 뒤에
print(audit_images(out))                     # {'ok': True} 여야 한다
```

- 단위는 HWPUNIT. **1inch = 7200**, 96dpi 이미지는 `px * 75`가 원본 크기(`orgSz`). 표시 크기(`sz`·`curSz`)는 본문폭 이하로.
- `hp:pos`는 표와 같은 이유로 `treatAsChar="0"` — 쪽 경계에서 그림이 통째로 밀리지 않는다.
- `sanitize_package`(경로 F-3)보다 **나중에** 호출한다. 순서가 뒤집히면 BinData가 날아간다.

### 그림 안 글씨 크기 — 인쇄 기준으로 잡을 것 (2026-09-25 사용자 지적)

가장 크게 데인 부분이다. 화면에서 멀쩡해 보이던 도면이 인쇄하면 **4.5pt**로 찍혀 못 읽었다.

    인쇄 글자 크기(pt) = 폰트 px ÷ 캔버스 px 폭 × 본문폭(mm) ÷ 25.4 × 72

- 본문폭 164mm(=46490 HWPUNIT)에 꽉 채우는 그림이라면 **캔버스 1000px에 본문 20px, 제목 24px**이 기준선이다(각각 9.3pt·11.2pt). 문서 본문이 12pt이므로 이보다 작으면 눈에 띄게 답답하다.
- 캔버스를 넓히면(1180px 등) 같은 폰트가 더 작게 찍힌다. **넓은 캔버스에 많이 담는 것이 아니라, 좁은 캔버스에 적게 담아야 크게 나온다.**
- 그래서 한 행에 3~4칸까지만 둔다. 5칸 이상이면 2행으로 쪼갠다(5단계 공정 → 3+2, 7개 존 → 4+3).
- 확인은 눈이 아니라 PDF 실측으로: `pymupdf`로 `page.get_image_info()`의 bbox 폭(mm)을 재서 위 식에 넣는다.
- 2행으로 쪼갤 때 **줄바꿈 연결선의 출발점을 틀리지 말 것** — 1행 마지막 상자에서 내려와 2행 첫 상자로 가야 한다. 1행 첫 상자 밑에서 화살표를 내리면 흐름이 거꾸로 읽힌다(초안에서 두 번 냈다).

### 부수 발견 — `hwpx_gen`의 `lead` 는 구분자가 없다

`d.b1('본문', lead='권장')`은 `권장본문`으로 붙어 나온다. 강조어와 본문 사이에 공백이 없다. 문서 전체에 퍼지므로 조립 시작부에서 감싸 둘 것.

```python
_orig = d._bullet
d._bullet = lambda kind, t, lead=None: _orig(kind, t, (lead + ' — ') if lead else None)
```
