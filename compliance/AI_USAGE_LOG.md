# AI 사용 기록

제출물에 AI 도구 사용 설명이 필수다. 작업 세션마다 한 줄씩 추가한다.
마감 전에 이 표를 요약해 제출 양식의 Use of SI로 옮긴다.

## 개발 과정에서 쓴 AI

| 시각 (KST) | 도구·모델 | 용도 | 영향을 받은 산출물 | 사람이 검토한 내용 |
|---|---|---|---|---|
| 11/13 (대회 전) | Claude Code | 대회 규정 조사, 과제문과 공식 리소스 읽기, 미세중력 연소 배경 학습, PSI 카탈로그의 규모 파악 | 제출물 없음. 팀의 사전 학습에만 사용 | 사용자가 대화로 확인 |
| 11/14 09:00– | Claude Code | PSI 카탈로그·시험 표를 받는 스크립트 작성 | `scripts/fetch_psi.py` | 미검토 |
| 11/14 09:00– | Claude Code | 시험 표의 열 단위 분석 스크립트 작성 | `scripts/profile_tables.py`, `data/derived/data_profile.json` | 미검토 |
| 11/14 09:00– | Claude Code | 실험별 한 줄 설명, 열의 뜻, 데이터 품질 문제 목록 작성 | `data/derived/annotations_ko.json` | 미검토. '추정' 표시 항목은 원문 대조 필요 |
| 11/14 09:00– | Claude Code | 팀 내부용 데이터 구조 안내 페이지 작성 | `reports/data-map.template.html`, `scripts/build_data_map.py` | 미검토 |
| 11/14 10:50– | Claude Code | FLEX·BASS-II 시험 표를 단위 통일된 시험 단위 표로 바꾸는 규칙과 코드 작성 | `scripts/build_test_tables.py`(사용자 요청으로 삭제됨), `data/derived/tests_*.csv`(저장소에 올리지 않음) | 미검토 |
| 11/14 오후 | Claude Code | 시험 표 11개를 공통 형식의 시험 단위 표로 바꾸는 규칙과 코드 재작성 | `scripts/build_test_tables.py`, `data/derived/tests_*.csv` | 미검토. 원본 5행 대조 필요 |
| 11/14 오후 | Claude Code | 화재 안전 값 계산, 환경 조건 맞추기, 근거 묶음 생성 코드 작성. 계산은 규칙 기반이며 언어 모델은 수치에 관여하지 않음 | `scripts/fire_safety.py`, `data/derived/fire_safety_metrics.json`, `data/derived/evidence_*.json` | 미검토. 지표 정의는 연소 전공 팀원 확인 필요 |

## 제품 안에서 동작하는 AI

| 모델 | 제공처 | 역할 | 입력 데이터 | 출력 검증 방법 |
|---|---|---|---|---|
| (미정) | | | | |
