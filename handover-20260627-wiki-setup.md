# 핸드오버: 연대지능 활동가 위키 저장소 구축

**날짜**: 2026-06-27  
**세션**: Cross-device work and folder sharing

---

## 배경

사교원 직원 11명의 자료 동기화 + 연대지능활동가 교육생의 위키 연결·검수 체계가 필요했음. 두 가지 목적 중 후자(활동가 위키)를 이번 세션에서 구축.

## 결정 사항

- **독립 저장소**(C안)로 결정: 품앗이 위키(wiki.poomasi.org)나 sakyowon-ai에 붙이지 않고 별도 운영
- **리뷰어는 @deka2026 단독**: CODEOWNERS로 모든 PR에 자동 배정
- 활동가들은 Fork → 작성 → PR → 검수 → 머지 흐름으로 참여

## 생성된 저장소

**https://github.com/deka2026/solidarity-intelligence-wiki**

## 파일 구조 (13개 → 18개)

```
연대지능-위키/
├── .github/
│   ├── CODEOWNERS                    # 리뷰어 = @deka2026
│   └── PULL_REQUEST_TEMPLATE.md      # PR 제출 양식
├── README.md                         # 저장소 소개
├── docs/
│   ├── onboarding-guide.md           # 활동가 온보딩 6단계
│   └── review-checklist.md           # 검수 체크리스트 (형식/내용/연결/품질)
├── templates/
│   ├── concept.md                    # 개념 정리 템플릿
│   ├── field-note.md                 # 현장 기록 템플릿
│   ├── how-to.md                     # 실습 가이드 템플릿
│   └── case-study.md                 # 사례 연구 템플릿
└── wiki/
    ├── concepts/
    │   └── collaborative-intelligence.md   # 예시: 연대지능 개념
    ├── field-notes/
    │   └── sample-village-meeting-0627.md  # 예시: 마을회의 참관
    ├── how-to/
    │   └── wiki-contribution-guide.md     # 예시: 위키 기여법
    ├── case-studies/
    │   └── mangnim-village-content.md     # 예시: 망님마을 콘텐츠
    └── resources/
```

## 로컬 경로

`C:\Users\Admin\Desktop\인공지능 작업실\연대지능-위키\`

## 미완료

- 직원 11명 자료 동기화 방안 (Google Workspace 등) — 미착수
- branch protection 규칙 설정 (GitHub Settings에서 수동 설정 필요)
- 활동가 교육 시 실습으로 Fork → PR 해보기
