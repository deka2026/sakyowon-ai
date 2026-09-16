# 핸드오버: 세무사 인터뷰 질문지 hwpx 생성 — 미머지 브랜치 원본 추적 + 사내 서식 규칙 후처리

**날짜**: 2026-09-16
**이전 핸드오버**: handover-20260916-haebaramul-foundation-proposal.md (같은 날 conference-deck-16x9 핸드오버도 병존)
**작업 폴더**: `D:\사교원 개발그룹\사교원 개발그룹\햇빛발전협동조합 업무자동화 사이트\`

---

## 수행한 작업

### 1. 원본 추적 — 사용자가 준 경로가 로컬에 없었다
- 요청: `wiki/assets/tax-accountant-interview-questions.build.py` "이 내용을 한글파일로 만들어"
- 로컬 6개 클론·D:·Downloads·스크래치패드 전부에 없음. `gh api repos/<r>/git/trees/<branch>?recursive=1`을 두 org(deka2026·haeory-cyber)의 전 레포·전 브랜치로 돌려 발견:
  **`deka2026/solidarity-intelligence-wiki` 브랜치 `claude/tax-accountant-interview-questions-4xi2is`** (main 미머지, 커밋 df1bf2e 2026-09-11)
  - `wiki/how-to/tax-accountant-interview-questions.md` (원본 md, 44문항·6단계)
  - `wiki/assets/tax-accountant-interview-questions.build.py` (python-hwpx 빌더)
  - `wiki/assets/tax-accountant-interview-questions.hwpx` (10.5pt 원판 — Downloads·Telegram에 있던 동명 파일과 바이트 동일)
- 로컬 클론 `solidarity-intelligence-wiki-haeory`에는 이 브랜치가 없다

### 2. 빌드 + 사내 규칙 적용
- `pip install python-hwpx` (6.4.0) 후 원 스크립트 실행 → validate ok. 산출물은 본문 10.5pt·셀 10pt·표 `treatAsChar="1"`·셀 문단 JUSTIFY
- 규칙 적용판 제작: 본문·셀 12pt, 소제목 13pt, 표 자리차지(0), 셀 문단 LEFT(paraPr 29 신설), 번호 열 1.15·항목 열 3.0
- 검증: `pagecount_auto.ps1 -Pdf` → **A4 10쪽**, PyMuPDF 접촉 시트 + 2·6·7쪽 확대로 빈 쪽·넘침·잘림 없음 확인. 사용자 한글이 떠 있었으나 스크립트가 기존 프로세스를 건드리지 않음(정상)
- 산출: `…\햇빛발전협동조합 업무자동화 사이트\세무사 인터뷰 질문지_20260916.hwpx` (사용자 지정 위치) + 같은 파일이 `마을협동조합 사업모델\`에도 있음(첫 저장 위치, 사용자 지시 없어 유지)

### 3. 스킬 갱신 — `hwpx-powershell-edit` 경로 G
- 신규 `scripts/hwpx_house_rules.py`: 어떤 hwpx든 ①참조된 charPr 중 12pt 미만을 1200으로 ②`treatAsChar` 1→0 ③셀 문단 JUSTIFY paraPr을 LEFT 사본으로 복제·재지정. 스모크 테스트는 아래 위키배포 결과 절 참조
- SKILL.md: 경로 G(외부 빌더 산출물 후처리 + GitHub 전 브랜치 파일 탐색법) 추가, F-1의 "표 셀 10pt 유지" 문구를 현행 규칙(셀도 12pt)으로 정정
- 활성 폴더(9/12판: gen_lib_baljemun.py·pagecount_auto.ps1·treatAsChar 0 hwpx_gen.py)가 sakyowon-ai보다 새로웠음 → 활성 → 레포 방향으로 동기화

## 미완료 / 다음 할 일
- [ ] 세무사 인터뷰 질문지 원본 브랜치(`claude/tax-accountant-interview-questions-4xi2is`) main 머지 여부 — 사용자 결정. 머지하면 `wiki/assets` hwpx도 12pt판으로 교체 권장
- [ ] `마을협동조합 사업모델\세무사 인터뷰 질문지_20260916.hwpx` 중복 사본 정리 여부 — 사용자 확인
- [ ] 사교원 위키 4단계(서버 `deploy-www.sh`) 반영 — 아래 위키배포 결과 참조
- [ ] 컨퍼런스 발표자료: 주최측 제출 형식 확인, 영문판 요청 시 같은 빌더로 생성 (이월)
- [ ] (이월) 에너지공단 시범사업 — DSO 문서 처리 방향 결정, 확인 필요 자료 5종 확보
- [ ] (이월) 시민기금 12장 법인격 시나리오 방향 결정 — 사용자 몫
- [ ] (이월) 시민기업펀드 v2 사용자 검토
- [ ] (이월) 공론장 발제문 참고3 수치 불일치(52↔48MW 등) 저자 확정
- [ ] (이월) 사회연대경제기본법 공포문 확인 후 제17·18조 갱신, 시행령 의견서 초안
- 해결됨: "표 셀 글자 크기 규칙 확정" 이월 항목 — 메모리 `feedback-hwpx-body-12pt`에 셀 12pt로 확정돼 있음(2026-09-10). 이번 문서도 셀 12pt로 제작

## 위키배포 결과 (2026-09-16)
- ③ 레슨: `sakyowon-wiki` v4 `content/연대지능/AI에게-스크립트-경로만-주고-한글문서-만들기.md` — PR #1 squash 머지 **b77e465**
- 사교원 위키 사슬: 1단계 완료(b77e465) → 2단계 CI는 사용하지 않음(산출물 삭제 관행) → **3단계 완료**: v4 501204f(다른 세션의 숏폼 레슨 포함)를 `git archive`로 뽑아 클린 트리에서 `npx quartz build -d … -o …`(100문서·350파일) → `sakyowon-wiki-site` master **02b921f**, sitemap 101건 → **4단계 서버 반영 대기**(SSH 필요). 편지함 `haeory-sakyowon-site/JIMMY-DECA.md`에 반영 요청 추가
- 스모크 테스트: `hwpx_house_rules.py baseline.hwpx` → raised 7 charPr, tables_inflow 13, cell_paras_left 297, paraPr 29 신설 — 수작업 결과와 일치
- 병행 세션 주의: 같은 시각 다른 세션들이 sakyowon-ai(hwpx-powershell-edit SKILL.md 함정 10·examples/·hwpx_redit.py, 핸드오버 3건)와 sakyowon-wiki(레슨 2건)를 커밋했다. 이 세션은 자기 파일만 add했고 `git archive v4`로 빌드해 미커밋 파일이 사이트에 섞이지 않게 했다
- 공동위키(solidarity-intelligence-wiki)에는 올리지 않음 — 저장처 기본은 사교원 위키(2026-09-11 지시)

## 파일 위치
| 경로 | 내용 |
|---|---|
| `D:\사교원 개발그룹\사교원 개발그룹\햇빛발전협동조합 업무자동화 사이트\세무사 인터뷰 질문지_20260916.hwpx` | **최종본** A4 10쪽 |
| `D:\사교원 개발그룹\마을협동조합 사업모델\세무사 인터뷰 질문지_20260916.hwpx` | 동일 사본 |
| `deka2026/solidarity-intelligence-wiki@claude/tax-accountant-interview-questions-4xi2is` `wiki/…` | 원본 md·빌더·10.5pt hwpx |
| `sakyowon-ai\skills\hwpx-powershell-edit\scripts\hwpx_house_rules.py` | 사내 규칙 후처리기 |
| `sakyowon-wiki\content\연대지능\AI에게-스크립트-경로만-주고-한글문서-만들기.md` | 레슨 |

## 약속
- 사용자가 **"이어서 작업하자"** 라고 하면 이 핸드오버의 "미완료" 목록부터 재개
- 사용자가 **"정리해"** 라고 하면: ①핸드오버 ②스킬 ③레슨 ④위키배포 자동 수행
