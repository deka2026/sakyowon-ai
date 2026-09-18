---
name: google-form-appsscript
description: 구글 설문지(Google Forms)를 Apps Script로 생성하는 스킬. Claude 환경에는 Forms를 직접 만드는 도구가 없으므로, 붙여넣고 한 번 실행하면 문항·유효성검사·응답시트까지 통째로 만들어지는 .gs 파일을 산출한다. "구글 설문지 만들어줘", "참가 신청 폼 만들어", "설문조사 폼 제작" 같은 요청에 사용. 개인정보 동의 문항 배치와 확정 필요값 관리가 핵심.
---

# 구글 설문지를 Apps Script로 만들기

## 왜 이 방식인가

Claude 환경에는 Google Forms를 직접 생성하는 도구가 없다. 대신 **사용자가 자기 계정에서 한 번 실행하면 되는 스크립트**를 준다.

- 설문 소유권이 처음부터 사용자 계정에 있다 (권한 이관 불필요)
- 문항이 29개든 50개든 손으로 만들 때보다 빠르고 오타가 없다
- 값을 고칠 때 스크립트를 고쳐 재실행하면 되므로 이력이 남는다
- Claude가 사용자 계정에 아무것도 실행하지 않는다 (승인 경계가 깨끗하다)

## 산출물 2종

| 파일 | 용도 |
|---|---|
| `<주제>_설문_생성.gs` | 본체. script.google.com에 붙여넣고 실행 |
| `<주제>_설문_문항안.hwpx` | 배포 전 사람이 눈으로 검토할 문항 일람표 |

hwpx는 스킬 `hwpx-powershell-edit`으로 만든다. 문항은 서술이 아니라 **표**로: 번호 / 문항 / 유형 / 필수 / 선택지.

## 필수 설계 규칙

### 1. CFG 단일 출처 — 가장 중요

확정값을 파일 맨 위 `CFG` 객체 한 곳에 모으고, **본문 안내문·섹션 설명·문항 도움말·제출 완료 문구가 전부 CFG를 참조**하게 한다. 파생값은 계산한다.

```javascript
var CFG = {
  startDate : '2026. 10. 12.(월)',
  endDate   : '10. 15.(목)',
  nights    : 3,
  capacity  : '12명',
  feeAmount : '2만원',
  feeNature : '네트워크 다과비 겸 예약금',
  deadline  : '2026. 9. 30.(수)',
  contact   : '홍길동 / 010-0000-0000 / mail@example.com'
};
// 파생값 - 하드코딩하지 말 것
var PERIOD = CFG.startDate + ' ~ ' + CFG.endDate + ', ' + CFG.nights + '박 ' + (CFG.nights + 1) + '일';
var FEE    = CFG.feeAmount + ' (' + CFG.feeNature + ')';
```

**검증 방법(반드시 할 것)**: CFG 값을 전부 딴 값으로 바꿔 실행해 보고, 원래 값 문자열이 결과에 **0건** 남는지 확인한다. 하나라도 남으면 그게 하드코딩이다. 실제로 "CFG 한 곳만 고치면 된다"고 보고했다가 하드코딩 4곳이 적발된 적이 있다.

### 2. 닫힌 상태로 생성

```javascript
form.setAcceptingResponses(false);
```

검토 전에 응답이 들어오면 안 된다. 사용자가 문항을 확인한 뒤 직접 연다. 닫힘 문구는 **상황별로 둘** 준비한다 - 생성 직후(아직 시작 전)와 마감 후는 다른 말이어야 한다.

```javascript
var CLOSED_NEUTRAL        = '지금은 신청을 받지 않는 기간입니다.';
var CLOSED_AFTER_DEADLINE = '참가 접수가 마감되었습니다(' + CFG.deadline + ').';
form.setCustomClosedFormMessage(CLOSED_NEUTRAL);
```

생성 직후인데 "마감되었습니다"가 뜨는 실수가 실제로 있었다. 검토 중 URL이 새면 시작 전인데 마감으로 보인다.

### 3. 개인정보 동의 문항의 위치

구글폼은 **섹션이 순차 진행**이다. 동의를 마지막 섹션에 두면 응답자는 **동의 전에 정보를 입력**하게 된다.

- **민감정보**(건강·질병·정신건강 등, 개인정보보호법 제23조)를 수집하면 **그 수집 문항 바로 앞**에 별도 동의를 둔다
- 일반 개인정보·사진영상 동의는 마지막 섹션이어도 무방
- 동의 3개를 전부 맨 앞에 몰면 첫 화면이 동의서로 시작해 이탈률이 오른다. 취약 계층 대상 설문일수록 주의

동의 문안에는 **목적·항목·보유기간·거부권**을 반드시 넣는다. 응답은 필수로 하되 제목은 `[동의 여부 선택]`처럼 표기해 `[선택]` + `setRequired(true)` 충돌을 피한다.

### 4. 받지 말아야 할 것

- 주민등록번호, 상세주소
- **제3자 정보**(비상연락처 등) - 본인 동의만으로 수집할 수 없다. 참가 확정자 대상 별도 수집으로 미룬다
- 계좌·입금자명 - 납부 방법이 확정되기 전에 받으면 미선발자 처리가 번거롭다

### 5. 확정 필요값은 지어내지 않는다

원본 문서에 없는 값(참가비·마감일·문의처)은 **"추후 안내"로 두고 확정 필요 목록에 올린다.** CFG에 `// 미확정` 주석으로 표시하고, 확정되면 주석도 함께 지운다.

### 6. 안내문과 문항의 정보 비대칭에 주의

참가자가 **첫 화면에서 보는 안내문**과 뒤쪽 문항 도움말이 어긋나면 안 된다. 실제 사례: 안내문에 "집결 장소: 인천종합버스터미널"만 적혀 있고 "완도 현지 합류 가능"은 5번째 섹션 교통편 문항에 가서야 나왔다. 완도 지원자가 첫 화면에서 포기할 수 있다. **검토용 문서에만 적고 안내문에 빠뜨리는 실수가 잦다.**

## 유효성검사 관용구

```javascript
// 휴대전화
.setValidation(FormApp.createTextValidation()
  .requireTextMatchesPattern('^01[016789]-?[0-9]{3,4}-?[0-9]{4}$')
  .setHelpText('010-0000-0000 형식으로 입력해 주세요.').build())
// 이메일
.setValidation(FormApp.createTextValidation().requireTextIsEmail().build())
// 체크박스 최소/정확히
.setValidation(FormApp.createCheckboxValidation().requireSelectAtLeast(1).build())
.setValidation(FormApp.createCheckboxValidation().requireSelectExactly(1).build())
```

## 마무리 관용구

```javascript
var ss = SpreadsheetApp.create('<제목> (응답)');
form.setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId());
Logger.log('편집 URL : ' + form.getEditUrl());
Logger.log('응답 URL : ' + form.getPublishedUrl());
Logger.log('응답 시트 : ' + ss.getUrl());
```

## 검수 절차

1. `node --check` - **확장자가 `.gs`면 실패한다**(`ERR_UNKNOWN_FILE_EXTENSION`). `.js`로 복사해 검사할 것
2. UTF-8(BOM 없음) 확인 - 한글이 깨지면 설문 전체가 망가진다
3. **목(mock) 실행** - `scripts/mock_run.js`로 `FormApp`·`SpreadsheetApp`을 가짜 객체로 심어 돌린다. 문항 수·섹션 수·선택지·유효성검사를 이걸로 센다

   ```bash
   node scripts/mock_run.js <생성스크립트.gs> <진입함수명>
   ```

4. **CFG 변이 테스트** (위 1번 규칙)
5. hwpx 문항안과 `.gs` 문항을 **전량 자동 대조** - 번호·제목·선택지. 문항을 재배치하면 번호가 밀려 대조가 깨진다
6. 구값 전수 검사 - 값을 바꿨으면 옛 값이 0건인지 **정규식으로** 확인. `"9. 28"`(공백형)만 찾다가 `"9.28"`을 통째로 놓친 적이 있다. 공백 허용 패턴(`9\s*\.\s*28`)을 쓸 것

## 함정

- **설문지를 Claude가 실행·발행하지 않는다.** 스크립트까지만 만들고 사용자가 돌린다
- 문항을 중간에 삽입하면 **뒤 번호가 전부 밀린다.** hwpx 문항안과 어긋나므로 재대조 필수
- `setCollectEmail(false)`는 조직 계정 정책에 따라 무시될 수 있다
- 응답 스프레드시트는 스크립트 실행 계정의 드라이브에 생긴다. 공유 설정은 사용자가 따로 한다
- 목 실행은 호출 순서·인자만 검증한다. 구글 서버가 그 조합을 받아주는지는 실제 실행 전까지 알 수 없다
