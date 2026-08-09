---
name: hwpx-powershell-edit
description: 한글 문서(.hwpx)를 Python·pandoc 없이 Windows PowerShell만으로 읽고 수정하는 스킬. .hwpx 파일의 내용 추출, 문단 텍스트 교체, 새 절·문단 삽입, 재패키징이 필요할 때 사용. HWP(구형 바이너리)는 불가 — hwpx만 지원.
---

# HWPX 문서 편집 (PowerShell 전용)

`.hwpx`는 ZIP 안에 XML이 든 포맷이다(OWPML). 본문은 `Contents/section0.xml`의 `<hp:t>` 요소에 있다.
이 스킬은 Python·pandoc·한글 프로그램 없이 .NET(System.IO.Compression + XmlDocument)만으로 편집한다.
2026-08-08 전남광주 메가프로젝트 문서 21건 편집으로 실증됨.

## 절차 (4단계)

### 1. 추출 + 텍스트 덤프
```powershell
powershell -NoProfile -File scripts\hwpx_dump.ps1 -HwpxPath "원본.hwpx" -WorkDir "작업폴더"
```
- `작업폴더\unpacked\`에 압축 해제, `작업폴더\text_dump.txt`에 `[인덱스] 텍스트` 형식으로 전체 문단 덤프
- 덤프를 Read로 읽고 수정 지점을 매핑한다. HWPX는 DOCX와 달리 **run 파편화가 거의 없어** 문단 전체가 한 `<hp:t>`에 들어있는 경우가 많다.

### 2. 편집 데이터 파일 작성 (edits.txt)
블록 구분자 `@@@`, 파트 구분자 `%%%` (각각 단독 줄). 이스케이프 불필요.

```
REPL
%%%
<찾을 원문 — 문단 전체를 그대로 복사, 앞 공백 포함>
%%%
<바꿀 새 텍스트>
@@@
INS_BEFORE_P
%%%
<앵커 텍스트 — 이 텍스트를 포함한 문단 '앞'에 삽입>
%%%
<삽입할 hp:p XML 한 줄>
@@@
INS_AFTER_P
%%%
<앵커 텍스트 — 이 텍스트를 포함한 문단 '뒤'에 삽입>
%%%
<삽입할 hp:p XML 한 줄>
```

**반드시 지킬 것:**
- REPL의 원문은 덤프에서 **그대로 복사** (앞 공백, 특수문자 포함). 스크립트가 매치 1회를 강제 검증하므로 안 맞으면 실패 목록이 출력된다.
- 새 텍스트에 `&` `<` `>` 금지 (XML). 「」 · — → ≒ ~ 등은 그대로 사용 가능.
- **따옴표 규약 먼저 확인**: 원본이 스트레이트(U+0027)인지 컬리(U+2018/2019)인지 스크립트가 검사해 알려준다. apply 스크립트는 컬리→스트레이트 자동 정규화 옵션이 기본 켜짐 (원본이 컬리면 `-NoQuoteNormalize`).

### 3. 삽입용 문단 XML 템플릿
**paraPrIDRef/charPrIDRef는 문서마다 다르다** — 반드시 대상 문서에서 같은 역할의 기존 문단을 찾아 ID를 확인한 뒤 템플릿에 대입할 것. (전남광주 문서 기준 예: 제목 18/23+2, 본문 21/16, 글머리 22/24, 공백 17/17)

```xml
<!-- 소제목 -->
<hp:p id="2147483648" paraPrIDRef="18" styleIDRef="15" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="23"><hp:t>□</hp:t></hp:run><hp:run charPrIDRef="2"><hp:t> 제목텍스트</hp:t></hp:run><hp:run charPrIDRef="23"><hp:t> </hp:t></hp:run><hp:run charPrIDRef="18"/></hp:p>
<!-- 본문 -->
<hp:p id="2147483648" paraPrIDRef="21" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="16"><hp:t> 본문텍스트</hp:t></hp:run><hp:run charPrIDRef="21"/></hp:p>
<!-- 글머리(박스 불릿) -->
<hp:p id="2147483648" paraPrIDRef="22" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="24"><hp:t>     * 불릿텍스트</hp:t></hp:run></hp:p>
<!-- 빈 줄(간격) -->
<hp:p id="2147483648" paraPrIDRef="17" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="17"/></hp:p>
```
- `<hp:linesegarray>`(레이아웃 캐시)는 **생략 가능** — 한글이 열 때 재계산한다. **반대로, 텍스트 길이를 바꾼 문단에 원본 캐시가 남아 있으면 낡은 줄 좌표에 겹쳐 그려져 문단이 깨져 보인다** (2026-08-08 실증). apply_edits.ps1이 기본으로 전체 캐시를 제거하므로 그대로 두면 안전하다.
- 표(`<hp:tbl>`) 행 추가는 rowCnt 갱신 등 파손 위험이 커서 피하고, 표 밖 주석 문단으로 대신할 것.

### 4. 적용 → 검증 → 재패키징
```powershell
powershell -NoProfile -File scripts\apply_edits.ps1 -SectionPath "작업폴더\unpacked\Contents\section0.xml" -EditsPath "edits.txt"
powershell -NoProfile -File scripts\hwpx_repack.ps1 -SourceHwpx "원본.hwpx" -SectionPath "작업폴더\unpacked\Contents\section0.xml" -OutHwpx "수정본.hwpx"
```
- apply가 전 건 매치 검증 후 실패 시 파일을 쓰지 않는다.
- repack이 XmlDocument 유효성 검증 후, 원본을 복사해 section0.xml만 교체한다(mimetype 등 나머지 엔트리 보존). **원본은 덮어쓰지 말고 새 파일명으로 출력**할 것.
- 재패키징 후 새 파일에서 텍스트를 재추출해 수정 지점을 눈으로 재확인할 것.

## 함정 (실전에서 걸린 것들)
1. **PS 5.1 스크립트 인코딩**: BOM 없는 .ps1의 한국어 리터럴은 깨진다. 한국어는 전부 데이터 파일(edits.txt)에 두고 .ps1은 ASCII만 사용 — 이 스킬의 스크립트가 이미 그렇게 설계됨.
2. **따옴표 불일치**: 웹/문서에서 복사한 컬리 따옴표(‘’)와 원본의 스트레이트(')가 달라 매치 실패하는 것이 최다 실패 원인.
3. `Preview/PrvText.txt`(미리보기 캐시)는 갱신 안 해도 무방 — 한글이 저장 시 재생성.
4. 완료 기준: XML 유효 + 재추출 검증까지. 최종 서식은 한글에서 육안 확인 권장.
