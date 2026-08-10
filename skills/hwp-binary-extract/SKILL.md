---
name: hwp-binary-extract
description: 구형 한글 문서(.hwp, OLE 바이너리)에서 파이썬으로 본문 텍스트를 추출하는 스킬. 사업계획서·제안서 등 .hwp 파일을 읽어야 할 때 사용. hwpx(zip)는 hwpx-powershell-edit 스킬, 이 스킬은 hwp5txt가 깨진 환경의 폴백 겸 hwpx 텍스트 추출도 지원.
---

# 구형 HWP(.hwp) 텍스트 추출

2026-08-10 인천 청년정책 공모전 계획서 6건(리셋·호식이세마리치킨·숨,셋)으로 검증.
`.hwp`는 OLE 복합문서 바이너리라 hwpx용 도구(zip 해제)로는 열리지 않는다.

## 언제 쓰나

- `.hwp` 파일 내용을 읽어 기획·분석에 써야 할 때 (한글 프로그램 없이)
- `pyhwp`의 `hwp5txt`가 의존성 문제로 죽는 환경 (아래 함정 참고)
- 같은 스크립트가 `.hwpx`(zip)도 감지해 처리하므로 포맷을 모를 때도 안전

## 사용법

```powershell
# 준비 (1회): pyhwp는 불필요, olefile만 있으면 됨
python -m pip install olefile

# 추출: python hwp_extract.py <원본.hwp> <출력.txt>
python scripts\hwp_extract.py "D:\...\계획서.hwp" "$env:TEMP\계획서.txt"
# 출력 예: 계획서.txt: ole, 7771 chars
```

- 출력이 `ole, 0 chars`면 암호화 문서이거나 배포용 문서(뷰어 전용) — 한글에서 다른이름 저장 필요
- 여러 파일은 PowerShell 반복문으로:

```powershell
Get-ChildItem *.hwp | ForEach-Object {
  python scripts\hwp_extract.py $_.FullName "$env:TEMP\$($_.BaseName).txt"
}
```

## 동작 원리 (수정할 때 필요한 만큼만)

1. 파일 시그니처 스니핑: `PK\x03\x04` → hwpx(zip), `D0 CF 11 E0 ...` → hwp5(OLE)
2. OLE의 `FileHeader` 스트림 36~40바이트 플래그에서 압축 여부 판단 → `BodyText/Section*`을 `zlib.decompress(data, -15)` (raw deflate)
3. 레코드 헤더(4바이트)에서 tag(10bit)·size(12bit) 파싱, size가 0xFFF면 다음 4바이트가 확장 크기
4. `HWPTAG_PARA_TEXT`(tag 67)만 골라 UTF-16LE 디코드. 제어문자 중 1,2,3,11,12,14~18,21~23은 16바이트 확장 컨트롤이라 통째로 건너뛴다 (이걸 안 하면 깨진 글자가 섞임)

표는 셀 단위 문단으로 풀려 나오므로 표 구조 복원은 안 된다. 내용 파악·인용 용도로 충분.

## 함정

1. **pyhwp를 먼저 시도하지 말 것** — `pip install pyhwp` 후 `hwp5txt`는 `six` 미포함으로 죽고, `six`를 넣어도 PS에서 `--output` 경로 처리로 조용히 실패했다 (stdout 모드도 무출력). 이 스크립트가 더 빠르고 의존성도 olefile 하나다.
2. PowerShell에서 `python -m pip install ... 2>&1`은 pip의 정상 stderr(notice)도 NativeCommandError로 표시된다 — exit code가 아니라 "Successfully installed" 문자열로 성공 판정할 것.
3. 한국어 경로는 문제없지만, 출력 파일은 UTF-8로 쓰므로 메모장이 아닌 에디터/Read 도구로 열 것.

## 참고

- hwpx 편집(내용 수정·재패키징)은 `hwpx-powershell-edit` 스킬
- 원리 문서: HWP 5.0 포맷 공개 명세 (한글과컴퓨터, "한글문서파일형식_5.0_revision1.3")
