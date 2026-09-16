---
name: hyperframes-student-shorts
description: 캠프·교육 참가자 1인당 인스타 릴스형 세로 숏폼(9:16, 30초/60초)을 HyperFrames로 대량 제작하는 스킬. 사진·동영상 소스에서 특정 인물이 나온 컷만 골라 "서툰 모습→연습→성공" 성장 스토리로 엮고, 격려 말풍선과 타이틀·엔딩 카드를 자동 조립한다. "학생별로 30초 영상 만들어", "강사 영상 1분짜리", "이 아이 사진으로 릴스 만들어" 같은 요청에 사용. 인물 오분류 방지 절차(전용 폴더·해시 대조)가 핵심.
---

# 참가자별 세로 숏폼 대량 제작 (HyperFrames)

2026-09-08~11 망남한뼘해변 스킴캠프 14편(학생 12·강사 2)으로 검증. 핵심 교훈은 **영상 기술보다 인물 판별이 병목**이라는 것이다.

## 전제 환경
- HyperFrames CLI(`npm i -g hyperframes`), FFmpeg(winget `Gyan.FFmpeg`), Chrome Headless Shell(`hyperframes browser ensure`). `hyperframes doctor`로 확인.
- 작업 폴더는 **영문 경로**(예: `D:\VideoWorks`) — FFmpeg·Chromium이 한글 경로에서 간헐 실패.
- 한글 폰트(BlackHanSans·Jua ttf)와 `gsap.min.js`를 프로젝트 `assets/`에 로컬 번들. 원격 CDN에 의존하면 렌더가 불안정.

## 절차

### 1. 프로젝트 스캐폴딩
```
npx hyperframes init <project> --example blank
mkdir compositions students assets/media assets/fonts assets/vendor
```
`assets/build.mjs`, `render-all.sh`, `watch-and-render.sh`를 프로젝트 루트에 복사. `build.mjs`는 `students/<slug>.json` → `compositions/<slug>.html`을 생성하며 마지막 학생을 `index.html`로도 복사한다(check/preview가 index.html을 열기 때문).

### 2. 신원 근거 확보 — 이 단계를 건너뛰면 반드시 오분류 난다
우선순위:
1. **참가자별 전용 폴더**(학부모·주최자가 그 사람 사진만 모은 것) — 있으면 이것만 소재로 쓴다.
2. 실명이 찍힌 사진(수료증·명찰·이름표) — 로마자 필기체는 10~16배 확대해 판독하고, 흐린 것은 **저자에게 확인**.
3. 카탈로그 라벨(에이전트가 붙인 "BOY-NIKE" 식 별명)은 **배치마다 어긋나므로 신뢰하지 말 것.** 스킴캠프에서 이 라벨을 믿어 한 학생 영상 전체가 다른 학생으로 만들어졌다.

함정: 명단에 없는 참가자(수료식 결석 등)의 사진은 "비슷한 체형"의 다른 참가자로 흡수된다. 참가자 수를 먼저 확정하고, 명단에 없는 얼굴이 반복 등장하면 저자에게 물을 것.

### 3. 소재 선별 — 에이전트 1인 1명 병렬
`assets/SELECTION_BRIEF.md`(JSON 스펙·촬영 맥락)와 `SELECTION_BRIEF_FOLDER.md`(폴더 기반 규칙)를 읽히고 학생당 에이전트 1개를 띄운다. 강사·성인은 `SELECTION_BRIEF_INSTRUCTOR.md`(60초, 말풍선은 1인칭 애정 멘트).

에이전트가 지켜야 할 것:
- 모든 후보를 **직접 Read로 보고** 확정. 동영상은 ffmpeg로 프레임을 뽑아 본다. 확신 없으면 탈락.
- 가로 원본은 9:16에서 폭 42%만 남는다. `focus` 정한 뒤 **크롭 시뮬레이션**(`scale=-2:1920,crop=1080:1920:(iw-1080)*X/100:0`)으로 인물 잔존을 눈으로 확인. 켄번즈 1.15배 여유.
- HEVC/rotate 태그 동영상은 H.264 1080×1920로 회전 구워 재인코딩(`-c:v libx264 -crf 18 -pix_fmt yuv420p -an`). EXIF 회전만 있는 사진은 `transpose`로 구움.
- 848×464 같은 저해상 영상은 세로 크롭 시 4배 확대라 제외(단 유일한 장면이면 보고 후 채택).
- 산출: 미디어 복사(`assets/media/<slug>/`), `students/<slug>.json`, `pick_<slug>.md`(채택/탈락 근거), `node build.mjs <slug>` 빌드 통과.

### 4. 오분류 검증 — 해시 대조
전용 폴더가 생기면 **모든 영상의 사용 파일을 md5로 폴더 파일과 대조**한다(핸드오버의 hashcheck.py 방식). 이름 매칭이 아니라 내용 매칭이라 누락이 없다. 겹침이 곧 오류는 아니다(한 사진에 여러 아이) — 겹친 컷만 직접 열어 주인공을 확인.

### 5. 렌더
```
bash render-all.sh <slug> [<slug>...]     # 인자 없으면 students/*.json 전부
```
`--composition compositions/<slug>.html`로 렌더해 index.html 충돌을 피한다. CRF 22 → 30초 25~30MB(인스타 적정). 대용량 원본 사진은 long side 3200으로 자동 축소.

### 6. 사용량 제한 대응 (무인 진행)
- `watch-and-render.sh`를 `Start-Process bash.exe -WindowStyle Hidden`으로 분리 실행 → 에이전트가 JSON을 완성하면(180초 안정 + pick에 v2 섹션 + 컴포지션이 JSON보다 최신) 자동 렌더. Claude API와 무관하게 돈다.
- `ScheduleWakeup`으로 1~2시간 후 기상해 죽은 에이전트만 재투입. 완료 여부는 `pick_<slug>.md`의 섹션 존재로 판정.

### 7. 검수
학생별 6~7프레임 시트(`select='eq(n\,45)+…'`, `tile=7x1`)와 첫화면 12명 모음(`tile=6x2`)을 만들어 인물 일관성·자막·크롭을 눈으로 확인한 뒤 저자에게 보낸다. 오분류는 이 시트에서 저자가 즉시 잡아낸다.

## JSON 스펙 요약
`assets/example-student.json` 참조. `shots`(8~11, `type` img|vid, `focus`, `mediaStart`, `note`), `messages` 5개(25자 이내, 화면과 맞게), `hero`/`cert`, `duration`(30|60), `endName`.

## 알려진 한계
- BGM 없음(무음). HeyGen 로그인 후 `/media-use --type bgm`으로 해결 가능. 인스타 업로드 시 앱 음원이 도달률에 유리.
- 렌더 1편 약 100초(i3-13100, 5 워커). 14편 약 25분.
