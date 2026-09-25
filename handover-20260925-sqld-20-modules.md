# 핸드오버: SQLD 자격증 과정 20회차 확대·보강 + 학습개요 유료 계정 안내

**날짜**: 2026-09-25
**이전 핸드오버**: handover-20260925-academy-site-prompt-cards.md (같은 세션 앞부분, 실습·학습 가이드 프롬프트 카드화)
**작업 폴더**: `C:\Users\User\academy-site` (deka2026/academy-site, main) → 사본 `D:\사교원 개발그룹\사교원 개발그룹\연대지능활동가 아카데미\`

---

## 수행한 작업

### 1. 학습개요에 "클로드 유료 계정 필요" 안내 (커밋 `9207087`)

- 제목 바로 아래 주황 강조 상자: 준비물 = 클로드 유료 계정(Pro 이상). 이유(5단계부터 Claude Code, 무료 계정은 Claude Code 불가·대화 한도) + claude.ai 가입 → Pro로 시작 → 필요 시 Max + "결제 정보는 본인이 직접 입력" 문장.
- 기존 "클로드 코드 PC판" 절의 유료 구독 문단은 그대로 둠.

### 2. SQLD 과정 10회차 → 20회차, 내용 보강 (커밋 `fc5d377`)

SQLD 과정은 같은 날 병행 세션이 신설한 것(`5fde02d`, 10회차·카드 2~4장·5문항). 사용자 지시 "학습 회차를 20회차로 늘리고 내용을 더 보강해".

- **구성**: 1과목 6회차(모델링 이해 / 엔터티·속성 / 관계·식별자 / 정규화·반정규화 / 관계와 조인의 이해·트랜잭션 모델링 / NULL·본질·인조 식별자) + 2과목 14회차(RDB·SQL 분류·DDL / SELECT·WHERE / 단일행 함수 / NULL 함수·CASE·형변환 / 집계·GROUP BY·HAVING / ORDER BY·Top N / 조인·OUTER / 표준·셀프·비등가 조인 / 서브쿼리·뷰 / 집합 연산자 / 그룹 함수 / 윈도우 함수 / 계층형·PIVOT·정규식 / DML·TCL·DCL 총정리). 회차당 **개념 카드 4장·문제 6문항 = 80카드·120문항**.
- **새로 넣은 시험 포인트**: 좋은 모델 요건, 엔터티 발생 시점 분류, 주식별자 선정 기준, 이상현상 3종, 반정규화 절차·기법, 슈퍼/서브타입 3변환, 트랜잭션 원자성과 필수 관계, 파티셔닝, CHAR/VARCHAR 비교 규칙, 제약조건·FK 삭제 옵션, 암시적 형변환의 인덱스 함정, AVG(NVL) 차이, ROWNUM 인라인 뷰, TOP WITH TIES·FETCH FIRST, OUTER 조인의 ON vs WHERE, (+) 규칙, USING 접두사, EXISTS·NOT IN NULL, 뷰 특징, 집합 연산자 규칙·행 수 계산, GROUPING 함수·행 수 계산, ROWS/RANGE 기본 윈도우, LAST_VALUE 함정, RATIO_TO_REPORT, 계층형 방향(PRIOR)·부가 함수, PIVOT 문법, 정규식 메타문자, MERGE, ACID, DDL 자동 커밋, 시험 직전 체크리스트.
- **구현**: `SQLD_MODULES`(id·part·title·intro·yt[2]·concepts[{topic,title,html}]·quiz[{topic,q,c[4],a,exp}]) 통째로 교체. `part` 필드 신설 → 과정 홈에 1·2과목 헤더. 문항 수 표시 `#sq-qtotal` 동적화. 저장 키 `sqld_v1 → sqld_v2`(회차 번호·문항 위치가 바뀌어 옛 약점 참조 `{m,qi}`가 어긋나므로 분리). 화면 문구 "완료 회차 / 20", "20회차 × 10분", "확인 문제 6문항".
- **데이터 검증 스크립트**(node): 모듈 20·문항 6·보기 4·정답 범위·보기 중복 없음·**문항 topic이 같은 회차 개념 카드 topic에 존재**(보완 학습이 `sqldFindConcept(topic)`로 카드를 찾으므로 필수)·yt 2개. 전부 통과 후 splice.
- **동작 검증**: 로컬에서 1회차 첫 문제 오답 → 결과 5/6 → 2회차 시작 시 보완 학습(카드 1·재시도 1) → 재시도 정답으로 약점 해제 → 20회차 완료 시 "다음 회차" 버튼 숨김 → 홈 완료 2/20. 실사이트에서 14회차 카드 4·문항 6 확인.

### 3. 배포

- 두 커밋 push → 사용자가 서버 `deploy-www.sh` 실행 → 18:48 라이브 = `fc5d377` 바이트 일치, 라이브에 모듈 20·키 v2·유료 안내 존재 확인.

### 4. 저장

- `D:\…\연대지능활동가 아카데미\아카데미사이트_index_실습단순화_20260925.html` 갱신(같은 index.html), `아카데미사이트_실습메뉴_변경내역_20260925.md`에 "같은 날 추가 변경" 절.

## 미완료 / 다음 할 일

- [ ] SQLD 문항은 전부 가상 문제. 노랭이(공식 실전문제집) 유형과 대조해 **계산형 문제(표를 주고 결과 행 수·값 묻기)** 비중을 늘리면 실전에 가까워짐 — 현재는 개념 확인형이 많음
- [ ] 회차별 유튜브 검색어(`yt`)가 일반적이라 채널명 포함 검색어로 다듬으면 초보자가 바로 강의를 찾음
- [ ] SQLD 과정 데이터가 index.html 안에 43KB — 자격증 과정이 더 늘면 별도 JS 파일로 분리 고려(단일 파일 SPA 원칙과 상충, 사용자 결정)
- [ ] (이월) 실습시작 관련: 홈 AI 대화 `KB` "6단계" 옛 문구, 캡처 올리기 정리, 9↔10단계 교육과정 어긋남 — handover-20260925-academy-site-prompt-cards.md 참조

## 파일 위치

| 경로 | 내용 |
|---|---|
| GitHub `deka2026/academy-site` main `fc5d377` → `index.html` | 캐노니컬(라이브 https://sakyowon.co.kr/academy-site/) |
| `index.html` `SQLD_MODULES` (`/* ===== 자격증아카데미: SQLD 과정 ===== */` 아래) | 20회차 데이터. 문구·문항 수정은 여기만 |
| `sakyowon-ai/skills/academy-site-deploy/SKILL.md` | 스킬에 "SQLD 과정 데이터 다루기" 절 추가(검증 스크립트 포함) |
| 사교원 위키 `content/연대지능아카데미/AI와-함께-자격증-학습과정을-20회차로-설계하고-검증하기.md` | 레슨 |
| 사교원 위키 `content/메타-기록/핸드오버-2026-09-25-SQLD-20회차.md` | 이 핸드오버 사본 |

## 약속
- 사용자가 **"이어서 작업하자"** 라고 하면 이 핸드오버의 "미완료" 목록부터 재개
- 사용자가 **"정리해"** 라고 하면: ①핸드오버 ②스킬 ③레슨 ④위키배포 자동 수행

## 위키배포 결과 (정리 루틴 ④, 2026-09-25 19:20 KST)

- 사교원 위키 v4 **ddfa3e8**(병행 세션 f5558c0 위에 rebase) → CI run 36122331038 success. deploy 잡까지 끝나 아티팩트가 사라져 **rerun 후 build 직후** 받음(스킬 jeongrihae-routine ④-2 절차) → sitemap **128**쪽(126 + 레슨·핸드오버 2)
- `deka2026/sakyowon-wiki-site` master: 원격에 병행 세션 빌드(2126f00, 126쪽)가 먼저 있어 첫 push 거부 → `reset --hard origin/master` 후 아티팩트 재적용·재커밋·push = **3단계 완료**
- **4단계(서버 반영) 대기** — `bash /opt/sakyowon/src/deploy-www.sh`. 실행 전 라이브: `Last-Modified` 09:48 GMT, sitemap 126
- 확인 URL: https://sakyowon.co.kr/sakyowon-wiki/연대지능아카데미/AI와-함께-자격증-학습과정을-20회차로-설계하고-검증하기 (반영 후 sitemap 128·200이면 완료)
- 함정 기록: 같은 날 병행 세션이 v4·site master 양쪽에 push하므로 **두 레포 모두 fetch 후 behind 확인**. site 레포는 내용 전체 치환이라 rebase 대신 reset 후 재적용이 맞다
