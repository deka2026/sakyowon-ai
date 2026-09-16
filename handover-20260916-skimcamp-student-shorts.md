# 핸드오버: 망남한뼘해변 스킴캠프 학생·강사 숏폼 영상 시리즈 (HyperFrames)

**날짜**: 2026-09-16 (작업 기간 2026-09-08 ~ 09-11)
**이전 핸드오버**: handover-20260916-mangnam-budget-execution-hancell.md
**작업 폴더**: `D:\VideoWorks` (프로젝트 `projects\skimcamp-shorts`, 산출 `output\`)

---

## 수행한 작업

### 1. 영상 제작 환경 구축 (09-08)
- HyperFrames(HeyGen 오픈소스, HTML→MP4) v0.8.31 전역 설치. FFmpeg 9.0.1(winget), Chrome Headless Shell v152.
- 전용 폴더 `D:\VideoWorks\{assets,projects,catalog,output}` — 한글 경로 회피를 위해 영문 경로.
- 한글 폰트(BlackHanSans·Jua)·GSAP을 프로젝트에 로컬 번들 → 렌더 시 네트워크 의존 0.

### 2. 30초/60초 템플릿 엔진 `build.mjs`
- 학생 JSON(`students/<slug>.json`) → 9:16 1080×1920 컴포지션 HTML 자동 생성.
- 구조: 타이틀 카드(히어로 사진+이름) → 몽타주 8~11컷(켄번즈, 사진·동영상 혼합) → 말풍선 5개 팝인 → 엔딩 카드.
- `duration` 필드로 30초(학생)/60초(강사) 공용. `endName`으로 끝카드 표기 override.
- lint 오류 0 (자산 경로는 프로젝트 루트 기준, 말풍선 exit tween은 inner wrapper + hard kill).

### 3. 소스 전수 카탈로그 + 인물 판별
- 사진 339장·영상 321편을 에이전트 9개로 병렬 스캔 → `catalog/img_batch_1~5.md`, `vid_batch_1~4.md`, `ALL.md`.
- 수료증 사진 21장을 10~16배 확대해 로마자 이름 판독 → `roster_names.md`. 저자 정정 3건(최인영·김시율·김보영).
- **카탈로그 인물 라벨은 배치마다 어긋나고 오류가 많았음.** 최종 신원 근거는 ①수료증 사진 ②학부모 제공 전용 폴더.

### 4. 오분류 발견·정정 (09-09~10)
- **정호준 영상 전량이 최준우**(수료식 사진 없어 명단 누락 → 사진이 "키 큰 남학생" 정호준에게 흡수). 전용 폴더 3개(김보영·정호준·최준우)의 파일을 **md5 해시로 모든 영상과 대조**해 발견. 최인영 2컷(김보영), 정호준 6컷 정정.
- 판별 규칙 오류 2건 폐기: "정호준=최장신"(실제 중간 키), "회색 헬멧=황서진"(정호준도 착용). 결정적 단서는 반바지 측면 패널(황서진=남색+파랑 패널 / 정호준=무지 검정).

### 5. v2 재선별 — 학생 12명 전용 폴더 기준 (09-10~11)
- 저자가 12명 전원 폴더 제공(사진 8~16·동영상 10~23). `catalog/SELECTION_BRIEF_FOLDER.md` 로 규칙 통일: 폴더 밖 소재 0, hero는 얼굴 상단 55% 안, 동영상 최대 4편, 9:16 크롭 ffmpeg 시뮬레이션 필수.
- 학생당 에이전트 1개가 폴더 전 파일(동영상은 프레임 추출) 확인 → `pick_<slug>.md` v2 섹션에 채택/탈락 근거.
- 결과: hero 11/12가 해변·물속 웃는 컷, 학생당 실전 라이딩 영상 2~4편, "서툰→넘어짐→성공→환호" 아크가 영상으로 보임.

### 6. 사용량 제한 대응 자동화
- `watch-and-render.sh`: JSON+pick+composition이 180초 이상 안정되면 자동 렌더. `Start-Process`로 분리 실행 → API 제한과 무관하게 진행. 실제로 밤사이 10편 자동 렌더 완료.
- `ScheduleWakeup`으로 1~2시간 후 자동 기상 → 죽은 에이전트만 재투입.

### 7. 산출물
- **학생 12편(30초)** + **강사 2편(60초, 규영샘·민경샘)** = 14편, `D:\VideoWorks\output\`. 1080×1920/30fps/**무음**.
- v1 10편 백업: `output\_v1_백업_20260908\`. 검수용 첫화면 모음 `_검수_타이틀카드_학생12명.jpg`, `_검수_강사_타이틀카드.jpg`.

## 미완료 / 다음 할 일
- [ ] 저자 최종 검수(12명 첫화면 모음 전달 완료, 피드백 대기)
- [ ] BGM 없음 — 인스타 업로드 시 앱에서 음원 삽입 권장. 영상 내 삽입 원하면 `npx hyperframes auth login`(HeyGen) 후 `/media-use`로 bgm 해결
- [ ] 김소은 v01(9/5 첫 스탠스 영상)은 848×464 저해상 — 거슬리면 제거해도 아크 유지
- [ ] 김유주 엔딩 수료증 컷은 원본이 어두움(밝기 보정 적용). 대체 컷 없음
- [ ] 강사 2편은 v1 그대로(폴더 없음). 규영샘 밸런스보드 시범 영상들(IMG_1130/1377/1588)은 848×464라 제외됨 — 고화질 원본 확보 시 교체 가치 있음

## 파일 위치
| 경로 | 내용 |
|---|---|
| `D:\VideoWorks\projects\skimcamp-shorts\build.mjs` | JSON→HTML 템플릿 엔진 |
| `…\students\<slug>.json` | 학생별 shot·말풍선 (12명 + teacher-*) |
| `…\render-all.sh` | 빌드+렌더 (`--composition compositions/<slug>.html`, CRF 22) |
| `…\watch-and-render.sh` | 무인 자동 렌더 감시 |
| `D:\VideoWorks\catalog\SELECTION_BRIEF.md` | 공용 선별 브리핑(JSON 스펙·촬영 맥락) |
| `…\SELECTION_BRIEF_FOLDER.md` | v2 폴더 기반 규칙 |
| `…\SELECTION_BRIEF_INSTRUCTOR.md` | 강사 60초 규칙(말풍선=강사 1인칭) |
| `…\pick_<slug>.md` | 학생별 채택/탈락 근거 (v1·v2) |
| `…\roster_names.md` | 수료증 이름 판독 |
| `D:\VideoWorks\assets\<이름>-2026…\<이름>\` | 학부모 제공 전용 폴더 12개 (최우선 신원 근거) |
| `D:\VideoWorks\output\` | 최종 mp4 14편 + 검수 시트 |

## 약속
- 사용자가 **"이어서 작업하자"** 라고 하면 이 핸드오버의 "미완료" 목록부터 재개
- 사용자가 **"정리해"** 라고 하면: ①핸드오버 ②스킬 ③레슨 ④위키배포 자동 수행
