# 학생 전용 폴더 기반 재선별 브리핑 (v2 — 더 나은 영상)

공용 브리핑 `D:\VideoWorks\catalog\SELECTION_BRIEF.md` 의 **JSON 스펙·산출물 형식·촬영 맥락은 그대로** 적용됩니다. 이 문서는 달라지는 점만 적습니다.

## 무엇이 달라졌나
저자(캠프 주최자)가 **학생 12명 각각의 전용 폴더**를 만들어 그 학생이 나온 사진·동영상만 모아 두었습니다.
`D:\VideoWorks\assets\<이름>-2026...\<이름>\`
- 이 폴더가 **유일한 소재 원천**입니다. `D:\VideoWorks\assets\images`·`videos`·카탈로그(`ALL.md`)는 **더 이상 쓰지 않습니다.**
- 폴더 안 파일은 전부 담당 학생이 등장합니다(저자 확정). 다만 **단체·2인 컷이 섞여 있으니 각 컷에서 담당 학생이 누구인지 특정**하고, 9:16 크롭 시 그 학생이 화면에 남도록 `focus`를 잡으세요.
- 신원 레퍼런스: 폴더에 수료식 사진(`photo_2026-09-08_09-12-*`)이 있으면 그것부터 보세요. 없으면 학생 혼자 크게 나온 컷으로 얼굴을 익히세요.

## 목표: 기존 영상보다 확실히 나은 영상
기존 산출물을 먼저 읽고 무엇을 개선할지 판단하세요:
- 기존 JSON: `D:\VideoWorks\projects\skimcamp-shorts\students\<slug>.json`
- 기존 선별 근거: `D:\VideoWorks\catalog\pick_<slug>.md`
- 기존 영상 QC 시트가 있으면 참고: `C:\Users\User\AppData\Local\Temp\claude\D----------\dc86a385-2c09-4bed-a57d-84484e02ffe1\scratchpad\qc\<slug>.jpg`

개선 기준(우선순위 순):
1. **첫 화면(hero)** — 얼굴이 선명하고 밝고 표정이 좋은 컷. 타이틀 카드는 화면 하단 1/3에 이름 블록이 얹히므로 **얼굴이 상단 55% 안에** 오는 구도가 좋습니다. 세로 원본이면 더 좋습니다.
2. **실제 라이딩 동영상** — 폴더에 동영상이 많습니다(10~23편). 물가에서 보드 던지고 올라타는 장면, 파도 위 활주, 넘어졌다 일어나는 장면을 **직접 프레임을 뽑아 확인**하고 가장 좋은 순간을 `mediaStart`로 지정하세요. 동영상은 **최대 4개**까지 허용(기존 3 → 4).
3. **스토리 아크가 실제로 보이게** — 서툰 모습(머뭇거림·넘어짐·강사 손 잡기) → 연습 → 성공(라이딩·웃음) 순. 각 단계에 최소 2컷.
4. **인물이 잘리는 컷 제거** — 가로 원본을 9:16으로 자르면 폭의 42%만 남습니다. `focus`를 정한 뒤 **반드시 ffmpeg로 크롭을 시뮬레이션해 눈으로 확인**하세요(아래 명령). 켄번즈 줌이 최대 1.15배까지 들어가므로 인물이 가장자리에 붙으면 잘립니다 — 여유를 두세요.
5. 기존 컷 중 폴더에도 있고 좋은 컷은 그대로 써도 됩니다. 억지로 바꾸지 마세요. 반대로 기존 컷 중 **폴더에 없는 파일은 쓸 수 없습니다**(그 학생이 아닐 수 있음).

## 9:16 크롭 시뮬레이션 (필수)
```
export PATH="$PATH:/c/Users/User/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0.1-full_build/bin"
# 가로 원본, focus X% 일 때 보이는 영역 (Y는 세로 원본일 때 같은 식으로)
ffmpeg -v error -i SRC.jpg -vf "scale=-2:1920,crop=1080:1920:(iw-1080)*X/100:0,scale=360:-2" -q:v 3 -y preview.jpg
# 동영상 프레임 뽑기
ffmpeg -v error -ss 3.5 -i SRC.mp4 -frames:v 1 -vf "scale=480:-2" -q:v 3 -y frame.jpg
# 동영상 길이·회전 확인
ffprobe -v error -show_entries format=duration:stream=width,height:stream_tags=rotate -of default=nw=1 SRC.mp4
```
- 동영상 원본이 **HEVC 또는 rotate 태그**가 있으면 H.264 1080×1920(세로) 또는 1920×1080으로 회전을 적용해 재인코딩해서 복사하세요(브라우저 렌더 안정성):
  `ffmpeg -v error -i SRC.mp4 -an -c:v libx264 -crf 18 -pix_fmt yuv420p -movflags +faststart -y OUT.mp4` (회전은 자동 적용됨; 필요 시 `-vf transpose=…`)
- 사진 원본이 EXIF 회전만 있고 픽셀은 누워 있으면 `-vf transpose=1`(또는 2)로 구워서 복사.
- 각 shot은 약 2.3~2.8초 재생되므로 동영상은 그 길이 이상 남는 지점을 `mediaStart`로.

## 산출물 (기존과 동일 경로에 덮어쓰기)
1. `D:\VideoWorks\projects\skimcamp-shorts\assets\media\<slug>\` — **기존 파일 전부 삭제 후** 새로 복사 (hero.jpg, cert.jpg, s01.., v01..). 같은 원본을 두 번 쓰지 말 것.
2. `D:\VideoWorks\projects\skimcamp-shorts\students\<slug>.json` — shots 9~11개, 동영상 최대 4개, messages 5개. `note`에 원본 파일명과 한 줄 설명을 꼭 남기세요.
   - `hero`·`cert`·`subtitle`·`endTitle`·`messages`는 새 화면 구성에 맞게 다시 쓰되, 기존 문구가 여전히 맞으면 유지.
   - 수료식 사진이 폴더에 있으면 `cert`로. 없으면 가장 좋은 마무리 컷 + `endBadge`를 수료 전제 없는 문구("잘 해냈어요")로.
3. `D:\VideoWorks\catalog\pick_<slug>.md` — 맨 위에 `## v2 (전용 폴더 기반, 2026-09-10)` 섹션을 추가해 채택/탈락 근거와 **기존 v1 대비 무엇이 좋아졌는지** 3줄 이내로 기록.
4. 마지막에 `cd /d/VideoWorks/projects/skimcamp-shorts && node build.mjs <slug>` 빌드 통과 확인.

## 최종 보고
- 채택 shot 목록(원본 파일명 · 단계 · 한 줄 설명), 동영상 개수
- **v1 대비 개선점** (hero 교체 여부, 새 라이딩 영상, 제거한 약한 컷)
- 폴더 파일 중 쓰지 않은 것과 이유(짧음/저화질/얼굴 안 보임/중복 등)
