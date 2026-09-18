// 구글 Apps Script 설문 생성 코드를 로컬에서 목(mock) 실행해 검수하는 도구.
//
//   node mock_run.js <생성스크립트.gs> [진입함수명]
//
// FormApp / SpreadsheetApp / Logger 를 가짜 객체로 심어 호출을 포획한다.
// 문항 수·섹션 수·선택지·유효성검사 호출을 세므로, 사람이 눈으로 세다 틀리는 일을 막는다.
// CFG 변이 테스트(값을 바꿔 재실행해 구값 잔존 0건 확인)의 기반이기도 하다.
//
// 한계: 호출 순서와 인자만 검증한다. 구글 서버가 그 조합을 실제로 받아주는지는 알 수 없다.

const fs = require('fs');

function makeItem(kind, sink) {
  const item = { _kind: kind };
  const chain = (name, store) => (...a) => {
    sink[store].push({ kind, name, args: a });
    return item;
  };
  item.setTitle       = chain('setTitle', 'calls');
  item.setHelpText    = chain('setHelpText', 'calls');
  item.setChoiceValues= chain('setChoiceValues', 'calls');
  item.setRequired    = chain('setRequired', 'calls');
  item.setValidation  = chain('setValidation', 'validations');
  item.setBounds      = chain('setBounds', 'calls');
  item.setLabels      = chain('setLabels', 'calls');
  item.showOtherOption= chain('showOtherOption', 'calls');
  return item;
}

function run(file, fnName) {
  const sink = { calls: [], validations: [], items: [], logs: [] };
  const form = {};

  const add = (kind) => () => {
    const i = makeItem(kind, sink);
    sink.items.push(i);
    return i;
  };
  ['TextItem', 'ParagraphTextItem', 'MultipleChoiceItem', 'CheckboxItem',
   'ScaleItem', 'PageBreakItem', 'SectionHeaderItem', 'DateItem', 'GridItem']
    .forEach(k => { form['add' + k] = add(k); });

  ['setTitle', 'setDescription', 'setAcceptingResponses', 'setCustomClosedFormMessage',
   'setConfirmationMessage', 'setCollectEmail', 'setProgressBar', 'setShowLinkToRespondAgain',
   'setDestination', 'setAllowResponseEdits', 'setLimitOneResponsePerUser', 'setShuffleQuestions']
    .forEach(m => { form[m] = (...a) => { sink.calls.push({ kind: 'form', name: m, args: a }); return form; }; });

  form.getEditUrl      = () => 'https://forms.example/edit';
  form.getPublishedUrl = () => 'https://forms.example/view';
  form.getId           = () => 'FORM_ID';

  const validation = (methods) => () => {
    const v = {};
    methods.concat(['setHelpText']).forEach(m => { v[m] = () => v; });
    v.build = () => ({});
    return v;
  };

  const sandbox = {
    FormApp: {
      create: () => form,
      openById: () => form,
      DestinationType: { SPREADSHEET: 'SPREADSHEET' },
      createTextValidation: validation(['requireTextMatchesPattern', 'requireTextIsEmail',
                                        'requireTextIsUrl', 'requireNumberBetween',
                                        'requireWholeNumber', 'requireTextLengthLessThanOrEqualTo']),
      createCheckboxValidation: validation(['requireSelectAtLeast', 'requireSelectExactly',
                                            'requireSelectAtMost'])
    },
    SpreadsheetApp: {
      create: () => ({ getId: () => 'SHEET_ID', getUrl: () => 'https://sheets.example' })
    },
    Logger: { log: (s) => sink.logs.push(String(s)) },
    Utilities: { formatDate: (d) => String(d), sleep: () => {} },
    DriveApp: { getFileById: () => ({ setSharing: () => {} }) }
  };

  const src  = fs.readFileSync(file, 'utf8');
  const keys = Object.keys(sandbox);
  const fn   = new Function(...keys,
    src + '\n;return typeof ' + fnName + ' === "function" ? ' + fnName + ' : null;');
  const entry = fn(...keys.map(k => sandbox[k]));
  if (!entry) throw new Error('진입 함수를 찾지 못함: ' + fnName);
  entry();
  return sink;
}

const [file, fnName = 'createForm'] = process.argv.slice(2);
if (!file) {
  console.error('사용법: node mock_run.js <생성스크립트.gs> [진입함수명]');
  process.exit(1);
}

const s = run(file, fnName);

const SECTION_KINDS = ['PageBreakItem', 'SectionHeaderItem'];
const pages     = s.items.filter(i => i._kind === 'PageBreakItem').length;
const questions = s.items.filter(i => !SECTION_KINDS.includes(i._kind)).length;

// 섹션별 문항 수: PageBreak 를 경계로 나눈다 (첫 섹션은 PageBreak 앞)
const perSection = [];
let cur = 0;
for (const i of s.items) {
  if (i._kind === 'PageBreakItem') { perSection.push(cur); cur = 0; }
  else if (!SECTION_KINDS.includes(i._kind)) cur += 1;
}
perSection.push(cur);
// 첫 PageBreak 가 1번 섹션의 제목 역할이면 선두 항목이 0이 된다 - 표시에서 뺀다
if (perSection.length > 1 && perSection[0] === 0) perSection.shift();

console.log('문항 수        :', questions);
console.log('섹션           :', perSection.length);
console.log('섹션별 문항 수 :', perSection.join(' / '));
console.log('유효성검사     :', s.validations.length);
console.log('유형별         :', JSON.stringify(
  s.items.reduce((a, i) => (a[i._kind] = (a[i._kind] || 0) + 1, a), {})));

const formCalls = s.calls.filter(c => c.kind === 'form').map(c => c.name);
console.log('폼 설정 호출   :', [...new Set(formCalls)].join(', '));
const accepting = s.calls.find(c => c.name === 'setAcceptingResponses');
console.log('접수 상태      :', accepting ? (accepting.args[0] ? '열림 ⚠' : '닫힘 ✓') : '미설정 ⚠');

console.log('\n--- 문항 제목 ---');
s.calls.filter(c => c.name === 'setTitle' && c.kind !== 'form')
  .forEach((c, i) => console.log(String(i + 1).padStart(3) + '. [' + c.kind + '] ' + c.args[0]));

console.log('\n--- 로그 출력 ---');
s.logs.forEach(l => console.log('  ' + l));
