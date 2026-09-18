# -*- coding: utf-8 -*-
"""예제: AI 하네스 구조도 (계층 스택 레이아웃, onepage_lib 사용).

실행:  python build_harness_map.py [출력경로.pptx]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))

from onepage_lib import (Deck, BLUE, TEAL, AMBER, PLUM, ROSE, SLATE,
                         FILL_BLUE, BORDER_BLUE, FILL_TEAL, BORDER_TEAL,
                         FILL_ROSE, BORDER_ROSE)

OUT = sys.argv[1] if len(sys.argv) > 1 else r"AI하네스구조도.pptx"

d = Deck()
d.header("AI 하네스 구조도",
         "모델을 실제 업무에 연결하는 실행 뼈대 — 지시 주입 · 런타임 · 도구 · 확장 · 산출 경로",
         ["Claude Code · Opus 5 · Windows 11", "스킬 20 · 에이전트 5 · 플러그인 39"])

# ① 지시 주입
d.band(1.08, 0.86, "1", "지시 주입", "세션마다 자동 적재", BLUE)
d.chips(1.08, 0.86, [
    ("자동 메모리", ["MEMORY.md 규칙·프로젝트 30건", "매 세션 첫머리에 로드"]),
    ("작업 폴더 신뢰 설정", ["D:\\사교원 개발그룹 · D:\\VideoWorks", "폴더별 권한·기록 분리"]),
    ("환경 프로필(autoMode)", ["조직·배포 대상·민감정보 범위", "settings.json에 고정"]),
    ("호출어 루틴", ["“수정해” · “정리해”", "“이어서 작업하자”"]),
    ("세션 리마인더", ["첨부·변경 파일, 스킬 목록", "대화 중간에 자동 갱신"]),
], BLUE, FILL_BLUE, BORDER_BLUE)
d.arrow(2.00)

# ② 런타임
d.band(2.20, 0.66, "2", "런타임", "모델과 세션 제어", TEAL)
d.chips(2.20, 0.66, [
    ("모델 Opus 5", "긴 추론·대용량 컨텍스트"),
    ("컨텍스트 자동 요약", "긴 세션도 끊기지 않음"),
    ("권한 모드", "자동 실행 / 확인 필요 구분"),
    ("실행 창구", "데스크톱 Code 탭 · CLI"),
    ("세션 저장", "프로젝트별 대화·이력 보관"),
], TEAL, FILL_TEAL, BORDER_TEAL)
d.arrow(2.92)

# ③ 도구 계층
d.band(3.12, 1.32, "3", "도구 계층", "손과 발", AMBER)
d.cards(3.12, 1.32, [
    (AMBER, "내장 도구", [
        "Read · Write · Edit  파일 읽기·쓰기",
        "Bash(Git Bash) · PowerShell 5.1",
        "Glob · Grep  대량 파일 탐색",
        "WebSearch · WebFetch  웹 조사",
        "SendUserFile · Artifact  결과 전달",
    ]),
    (PLUM, "MCP 서버 · 커넥터", [
        "내장 브라우저  미리보기·화면 검증",
        "Chrome 확장  로그인 세션 그대로",
        "터미널 읽기 · 시각화 위젯",
        "세션·창·PR 제어(ccd_*)",
        "구글 드라이브·Gmail 등 — 인증 대기",
    ]),
    (ROSE, "윈도우 실행 브리지", [
        "한글 Hwp COM  서식·쪽수 측정",
        "한셀 HCell COM  재계산·.cell 저장",
        "PowerPoint COM  PNG 렌더 검증",
        "python-pptx · python-hwpx",
        "HyperFrames + FFmpeg + gh · git",
    ]),
])
d.arrow(4.54)

# ④ 확장 계층
d.band(4.76, 1.32, "4", "확장 계층", "내가 만들어 얹은 것", PLUM)
d.cards(4.76, 1.32, [
    (TEAL, "스킬 20종 (직접 제작)", [
        "영상 11 · 문서 5 · 운영 2 · 예산 1 · 발표 1",
        "사용 1위 hwpx-powershell-edit 19회",
        "jeongrihae-routine 19회로 동률",
        "검증된 절차를 명령 한 줄로 고정",
        "~/.claude/skills 에 폴더로 보관",
    ]),
    (BLUE, "서브에이전트 5 (데카 팀)", [
        "파랑  조사·문서 / 보라  사이트·배포",
        "알파  디자인·영상 / 베타  자동화·스킬",
        "알파언니  검증 전담(수정 권한 없음)",
        "역할별로 쓸 수 있는 도구만 부여",
        "~/.claude/agents 에 역할 정의",
    ]),
    (AMBER, "플러그인 39종 (공식 마켓)", [
        "anthropics/claude-plugins-official",
        "docx · xlsx · pdf 등 문서 처리 활용",
        "법무·영업·데이터 팩은 대부분 미사용",
        "다수 커넥터는 계정 인증 전 대기",
        "필요할 때만 켜서 쓰는 예비 자원",
    ]),
    (SLATE, "무인 실행 (여유 슬롯)", [
        "예약 작업 0건 — 아직 미사용",
        "백그라운드 렌더·배치는 이미 가동",
        "/loop 로 반복 점검 실행 가능",
        "주간 리포트 자동화 여지",
        "야간 배치 후보 정리 단계",
    ]),
])
d.arrow(6.20)

# ⑤ 산출 경로
d.band(6.44, 0.70, "5", "산출 경로", "결과가 나가는 곳", ROSE)
d.chips(6.44, 0.70, [
    ("로컬 폴더", "D:\\사교원 개발그룹 · D:\\VideoWorks"),
    ("GitHub deka2026", "push → Pages 자동 배포"),
    ("자체 서버(Caddy)", "사교원 위키 · 신청 API"),
    ("대화창 전달", "파일 전송 · 아티팩트 링크"),
], ROSE, FILL_ROSE, BORDER_ROSE)

print("saved:", d.save(OUT))
