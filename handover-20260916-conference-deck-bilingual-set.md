# 핸드오버: 국제컨퍼런스 발표 세트 — 한글 발제문·15pt 슬라이드·영문판 4종

**날짜**: 2026-09-16 (작업 세션은 2026-09-12 ~ 09-14)
**이전 핸드오버**: `handover-20260916-conference-deck-16x9.md` (같은 산출물의 16:9 규격 정정 — 병렬 세션), 그 앞은 `handover-20260911-wiki-target-and-deploy-chain.md`
**작업 폴더**: `D:\사교원 개발그룹\전남광주사업게획서 모음\공론장 문서\`

---

## 수행한 작업

### 1. 한글 발표자료 PPTX (9/12 → 9/14)
- 원천: `[추진85]시민주권공동체자산형성.hwpx` + `재생에너지_사업_기반_기본사회_전략_…_20260709 (5).hwpx`. 행사 문서는 KEA-REN21 「2026 커뮤니티 에너지 국제 컨퍼런스」 개최 계획(안) PDF — 10.1(목) 오전 "국내 지자체 주도 커뮤니티 에너지" 세션, 발표 15분+패널.
- 사용자 조건: 인수위 논의 소개 차원, **조직체계(3장)·예산(6장·지원단가·출자출연 규모) 제외**, 사업 내용·원리 중심. 정량 목표(개소 수)는 "검토안"으로 남기고 금액은 전부 삭제.
- v1 17장(11→8.5pt 자동 축소) → 사용자 지시로 **본문 15pt 이상판 19장**(`_20260914_15pt.pptx`): 폰트 후보 (17,16,15), 비교표 2장 분할, ④금융 2장 분할. 사용자가 PowerPoint에서 손질·각주 삭제해 `_제출.pdf` 제출.
- 16:9 규격 정정(`_제출_16x9.pptx`)은 병렬 세션이 처리 — 위 이전 핸드오버 참조.

### 2. 한글 발제문 hwpx (9/14)
- `전남광주_시민주권공동체자산형성_컨퍼런스발제문_20260914.hwpx` + PDF, 10쪽, 표 17개. 템플릿은 공론장 발제문 교정 v1.0, `gen_lib_baljemun.Doc` → `fix_tbl_ids` → `patch_header_12pt(11·20~24·32·77)` → `pagecount_auto -Pdf`.
- 여러 문단 셀에 "- " 항목 기호 자동 부여(래퍼). 사용자가 한글에서 직접 수정(발표자 기입, '3차 공모'→'국가 공모', '자부담 우선출자', 토론 질문 삭제).

### 3. 영문판 4종 (9/14)
- **원문은 사용자 제출본 PDF**(pymupdf 텍스트)로 삼아 빌더 원고와 대조 — 제출본에서만 바뀐 것: 실증 시작 2027년, 시군구 시민공동체 추가, 커뮤니티 주식 문구(양도 불가·가치 상승 없음·액면가 인출), 마무리에 사회연대경제과 중심 민관거버넌스, 각주 삭제.
- `JeonnamGwangju_CommunityWealth_Conference_Slides_EN_20260914.pptx/.pdf`(19장, Calibri, 15pt 이상, 각주 없음) / `..._Paper_EN_20260914.docx/.pdf`(python-docx, 11쪽).
- 영문은 한글보다 약 25% 길어 7개 장이 넘침 → 압축 번역 2회로 해결. 발표자 표기 Il-young Kim, Chairperson, Social Innovation Platform.
- 용어표: 시민주권 공동체 자산 형성=Citizen-Sovereign Community Wealth Building, 마을월급=Village Salary, 햇빛소득마을=Sunlight Income Village, 공동체이익회사=CIC, 시민기업=citizen enterprise, 시민기금=Citizen Fund, 연대지능 AI 활동가=Solidarity Intelligence AI Activist, 지산지소=local production, local consumption, 관계인구=non-resident stakeholders.

### 4. 사실 검증 부수 산출
- 메자닌 투자, 영국 커뮤니티 주식(FCA RFCCBS 6.1·2014년 법 £100,000 한도·1인1표) 설명 → 한글 원문 "상환 없는 영구출자"를 "양도 불가·액면가 인출형"으로 정정 제안, 사용자가 슬라이드에 반영.

### 5. 스킬 (② 단계)
- `pptx-lecture-deck` **8절 신설**: 컨퍼런스 모드 `scripts/deck15_lib.py`(15pt 하한·한/영 설정·제목/목차/카드/비교표/흐름도/마무리), `scripts/docx_paper_lib.py`(`Paper` 클래스), `scripts/export_pdf.ps1`(PPTX·DOCX→PDF), `examples/` 3종. 스모크 테스트: ko/en 6장 생성·PDF 변환·docx 생성 통과.
- `hwpx-powershell-edit/examples/build_baljemun_conference_20260914.py` 추가(발제문 실제 빌더).

### 6. 레슨 (③ 단계)
- 사교원 위키 `content/연대지능/AI와-함께-발제문-한-편으로-한글문서-발표자료-영문판-세트-만들기.md`

### 7. 위키배포 (④ 단계)
- (아래 "위키배포 결과"에 추가 커밋으로 기록)

## 미완료 / 다음 할 일
- [ ] 발표 당일(10.1) 전 최종 확인: 영문 슬라이드 4번 장의 커뮤니티 주식 표현("withdrawable capital")을 한글판과 맞출지 사용자 결정
- [ ] 발제문 hwpx 원문 4장 참고 모델 표의 "상환 없는 영구출자" 문구 — 사용자가 슬라이드만 고쳤으므로 hwpx도 정정할지 확인
- [ ] 영문 발제문 11쪽 중 마지막 쪽이 표 꼬리 몇 줄 — 10쪽으로 맞추려면 표 셀 10pt로 조정(선택)
- [ ] (이월) 공론장 발제문 참고3 수치 불일치(52↔48MW 등) 저자 확정
- [ ] 사교원 위키 4단계(서버 `deploy-www.sh`) — 지미 편지함 요청 후 라이브 확인

## 파일 위치
| 경로 | 내용 |
|---|---|
| `…\공론장 문서\전남광주_시민주권공동체자산형성_컨퍼런스발표자료_20260914_제출_16x9.pptx` | 한글 슬라이드 캐노니컬(19장, 16:9) |
| `…\공론장 문서\전남광주_시민주권공동체자산형성_컨퍼런스발제문_20260914.hwpx/.pdf` | 한글 발제문 10쪽(사용자 수정 반영본) |
| `…\공론장 문서\JeonnamGwangju_CommunityWealth_Conference_Slides_EN_20260914.pptx/.pdf` | 영문 슬라이드 19장 |
| `…\공론장 문서\JeonnamGwangju_CommunityWealth_Conference_Paper_EN_20260914.docx/.pdf` | 영문 발제문 11쪽 |
| `skills/pptx-lecture-deck/examples/build_deck15.py · build_deck15_en.py · build_paper_en.py` | 실제 빌더(재생성 가능) |
| `skills/hwpx-powershell-edit/examples/build_baljemun_conference_20260914.py` | 발제문 빌더 |

## 약속
- 사용자가 **"이어서 작업하자"** 라고 하면 이 핸드오버의 "미완료" 목록부터 재개
- 사용자가 **"정리해"** 라고 하면: ①핸드오버 ②스킬 ③레슨 ④위키배포 자동 수행
