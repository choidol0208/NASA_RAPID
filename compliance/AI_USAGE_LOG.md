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
| 11/14 오후 | Claude Code | 사용자 지적에 따라 결론을 내는 코드(`scripts/fire_safety.py`, `scripts/build_test_tables.py`와 그 산출물)를 삭제하고, 명세 기반 파이프라인으로 교체. 화재 안전 정보 필요 7개, 표준 변수, 표 22개의 열 매핑을 명세 파일로 작성하고 이를 읽어 실행하는 엔진 작성. 수치는 NASA 원본 칸의 복사 또는 명세의 계산식 결과이며 언어 모델은 수치에 관여하지 않음 | `pipeline/spec/*.json`, `pipeline/run.py`, `pipeline/rules.py`, `pipeline/README.md`, `data/pipeline/*` | 미검토. 필요 정보의 정의·필수 변수·적용 범위는 연소 전공 팀원 확인 필요 |
| 11/14 10:30– | Claude Code | 공식 제출·심사 가이드 원문 확인, PSI 시험 표의 예비 집계, 팀 일정과 역할 계획 정리 | 저장소 밖의 팀 내부 계획 문서. 제출물에 들어간 것 없음 | 사용자가 대화로 확인 |
| 11/14 10:50– | Claude Code | 세션 간 협업 체계 작성: 역할·브랜치 규칙, 조정 파일과 도우미 스크립트, 역할별 브리프, AI 산출물 형식 초안, 저장소 README | `coord/`, `contracts/`, `scripts/coord.py`, `.claude/commands/sync.md`, `.gitattributes`, `README.md`, `AGENTS.md` 8·9절 | 미검토 |
| 11/14 오후 | Claude Code (웹 검색 도구 Exa 사용) | 필요 정보 7개의 근거가 되는 공식 기준·요구사항·문헌 21건을 검색해 읽고, 항목(기준 문장, 수치, 문서 내 위치, 확인 방식)을 명세로 정리. 필요 정보마다 근거 항목을 연결 | `pipeline/spec/references.json`, `pipeline/spec/needs.json`의 `references`, `data/pipeline/need_references.csv` | 미검토. 수치와 조항 번호는 원문 대조 필요. 초록만 확인한 문서 5건, 인용으로만 확인한 문서 1건은 명세에 표시함 |
| 11/14 10:30– | Claude (Opus, claude.ai 세션) | 카탈로그 2단 구조(조사표·구성표) 설계, PSI 기록·시험 표에서 값 추출, 분류 열 작성 | `scripts/build_catalog.py`, `scripts/export_catalog_xlsx.py`, `data/catalog/*` | 미검토. 모든 행 ai_extracted |
| 11/14 10:30– | Claude (Opus, claude.ai 세션) | 순위 점수 규칙(가중치 프로파일·유사도 식) 설정 파일과 계산 코드, 러프 입력 해석, 단위 시험 | `scoring/scoring_config.json`, `scoring/scorer.py`, `scoring/test_scorer.py`, `scoring/README.md` | 미검토. 가중치는 팀 검토 필요 |
| 11/14 10:30– | Claude (Opus, claude.ai 세션) | 검증 시나리오 22개와 실행기, 안정성 검사 | `validation/scenarios.json`, `validation/run_validation.py`, `validation/report.md` | 미검토. 기대 답은 전문가 검토 필요 |
| 11/14 10:30– | Claude (Opus, claude.ai 세션) | 카탈로그 필터 설명 슬라이드 1장(영어)과 생성 스크립트 | `presentation/catalog_filter_slide.pptx`, `presentation/build_catalog_filter_slide.js` | 미검토 |
| 11/14 11:05– | Claude Code (Opus, ui 세션) | 대시보드: 순위 계산기의 JavaScript 이식(`web/scorer.js`)과 Python 결과 일치 검사, 정적 페이지(HTML·CSS·JS), 빌드 스크립트, GitHub Pages 배포 워크플로, Python 계산기에 반올림 보조 함수 `_r` 추가(출력 형식 변화 없음) | `web/`, `.github/workflows/pages.yml`, `scoring/scorer.py` | 미검토. 일치 검사 61/61, 단위 시험, 검증 22/22 자동 통과 |
| 11/14 11:15 | Claude Code (data 역할) | pm 요청에 따라 대기 조건별 시험 수 격자를 파이프라인 출력으로 추가. 구간 경계는 명세에 근거와 함께 기록. 수치는 기록된 시험의 개수이며 추정 없음 | `pipeline/spec/coverage.json`, `pipeline/run.py`의 `coverage_grid`, `data/pipeline/coverage_grid.csv`, `coord/answers/20261114-1056-…data.md`, `coord/status/data.md` | 미검토 |
| 11/14 11:15 | Claude Code (data 역할) | 정정: 위에서 data 역할이 '11/14 오후'로 적은 줄들은 실제로는 11/14 오전(11:05 KST 이전)에 한 작업이다. 시계를 확인하지 않고 적었다 | `compliance/AI_USAGE_LOG.md`, `compliance/SOURCES.md`의 해당 줄 | — |
| 11/14 11:20 | Claude Code (data 역할) | 환경 시나리오(ISS 선실, 달 기지)를 산소·압력·유동·중력 범위로 명세하고, 시험별 일치 여부와 필요 정보별 일치 시험 수를 세는 단계를 파이프라인에 추가. 예측이나 추정 없이 기록된 값의 범위 비교만 함 | `pipeline/spec/scenarios.json`, `pipeline/run.py`의 `match_scenarios`, `data/pipeline/scenario_needs.csv`, `data/pipeline/scenario_tests.csv`, `coord/requests/20261114-1116-data-to-all-…md` | 미검토. 범위 경계는 팀의 선택 |
| 11/14 11:35 | Claude Code (data 역할) | 필요 정보별 지표를 명세로 정의(변수·조건·묶음만 지정, 계산은 고정 틀 3개)하고 계산 단계 추가. 재료 이름 통일 규칙 추가. 연기 발생(D2)의 필수 변수에 숙성 시간 추가. 지표 값은 기록된 값의 개수·최솟값·중앙값·최댓값이며 추정 없음 | `pipeline/spec/indicators.json`, `pipeline/spec/materials.json`, `pipeline/spec/needs.json`, `pipeline/spec/variables.json`, `pipeline/run.py`, `data/pipeline/indicators.csv`, `data/pipeline/indicator_tests.csv`, `data/pipeline/tests.csv`의 `material_id` 열 | 미검토. 지표 정의와 재료 묶음은 연소 전공 팀원 확인 필요 |
| 11/14 11:32 | Claude Code (data 역할) | 지표 결과를 팀원이 볼 수 있는 내부 페이지로 정리(한국어). 파이프라인 출력을 그대로 표시하며 새 계산 없음. 한국어 설명문은 AI가 영어 정의를 옮긴 것 | `reports/indicators.template.html`, `reports/indicators_ko.json`, `reports/build_indicators_page.py`, `reports/indicators.html` | 미검토. 내부용, 제출물 아님 |
| 11/14 11:20– | Claude Code (조사·평가는 Opus, 종합·반박 검토는 Fable 에이전트) | AI 계층에 쓸 기법 조사(논문·웹)와 설계, 프로젝트 차별성 아이디어 탐색. 팀 동기화와 통합 | `coord/`, `contracts/README.md`. 조사·설계 결과는 아직 제출물에 들어가지 않음 | 미검토. 방향 선택은 사용자가 함 |
| 11/14 11:40– | Claude Code | 로컬 모델(gpt-oss:20b)로 근거 인용 방식 시험. 제품 문구는 아직 생성하지 않음 | 저장소 밖 시험 스크립트 | 미검토 |
| 11/14 11:58 | Claude Code (data 역할) | 필요 정보의 근거를 점검: PSI 기록의 실험 목적 문장을 원문 그대로 필요 정보에 연결하고(엔진이 원문 일치 검사), 목적문에 없는 용도의 시험은 근거에서 제외. NASA 문서의 요구사항 문장 12개를 인용으로 추가. pm 요청으로 시나리오 3개 추가. 팀 페이지 갱신 | `pipeline/spec/needs.json`(`stated_by`, `not_covered`), `pipeline/spec/references.json`(`quote`), `pipeline/spec/scenarios.json`, `pipeline/run.py`, `data/pipeline/objective_links.csv`, `data/pipeline/*`, `reports/indicators*`, `coord/requests/*data-to-*` | 미검토. 어느 목적문을 어느 필요 정보에 묶을지는 AI의 판단이며 연소 전공 팀원 확인 필요. 표준 인용문은 PDF 원문 대조 필요 |
| 11/14 12:39 | Claude Code (Anthropic), 서브 에이전트 6개 병렬 | data 역할: 환경별 근거 묶음(`pipeline/evidence.py`, `data/pipeline/evidence/`), 실험별 사실표(`pipeline/facts.py`), 독립 검증기(`pipeline/check.py`) 작성. 별도 에이전트 3개가 원자료 재계산, 과잉 일반화, 인용문 대조를 감사했고, 그 결과로 칸 해석 규칙(주석 번호를 값으로 읽던 오류, BASS-II 팬 눈금을 유속으로 읽던 오류), 재료 이름, 중복 행, 질문 정의, 참고문헌 13건을 고침 | `pipeline/`, `data/pipeline/`, `reports/indicators*` | 없음(사람 검토 전) |
| 11/14 13:07 | Claude Code (Anthropic), 서브 에이전트 | data 역할: 참고문헌 표 2개를 PDF 원문과 칸 단위로 대조해 항목 추가(ICES-2024-365 표 1, Olson·Ferkul 2012 표 I), 감사 지적 48건을 문구 수준에서 반영, 검증기가 명세의 재료 어휘를 읽도록 보완(43개 검사 통과), 사람 점검표 생성 | `pipeline/spec/*.json`, `pipeline/README.md`, `pipeline/check.py`, `data/pipeline/`, `reports/spot_check.csv` | 없음(사람 검토 전) |
| 11/14 13:28 | Claude Code (Anthropic), 서브 에이전트 | data 역할: 작업에 참여하지 않은 에이전트의 최종 수용 검토(재현, 원본 칸 추적 49건, 검증기 변조 시험 12건)와 그 지적 반영(달 기지 압력 경계 주의문, 문장 단축, 비현실적 측정값 비움), 한국어 팀 페이지 문구를 현재 영어 명세에 맞춰 다시 번역 | `pipeline/`, `data/pipeline/evidence/`, `reports/indicators_ko.json`, `reports/indicators.html` | 없음(사람 검토 전) |
| 11/14 12:45–13:20 | Claude Code (Claude Opus 5.5), ui 역할(팀장 PC의 데스크톱 세션) | 대시보드: 근거 규칙(목적 밖 시험 표시), 필요 정보 개수를 파일에서 읽기, 시나리오 2개만 표시, 출처 라벨 3종(PSI 인용·팀 코드 계산·AI 생성), 부분중력 경고 문구, 결과 섹션 순서와 첫 문구. 과제문을 공식 페이지와 대조 | `web/`, `scoring/scoring_config.json`, `.github/workflows/pages.yml`, `coord/*ui*` | 미검토 |
| 11/14 13:05–13:30 | Claude Code (Claude Opus 5.5), ui 역할 | 순위 계산기와 카탈로그 점검. 가정한 대기 값을 "tested"로 쓰지 않게 하고, 역화염 산화제 흐름의 산소를 대기 산소와 비교하지 않게 하고, o2_above_all 기준을 주변 대기 최고치(40%)로 바꾸고, 연료 상태 키워드를 추가. 원 표 대조로 BASS-II·SPICE 유속과 CFI·SPICE·SAME 시험 수를 고치고 행마다 근거를 적음. 카탈로그-파이프라인 일치 검사를 배포 전에 실행. 이전 웹 ui 세션의 점검 메모와 패치를 출발점으로 썼지만 항목마다 원 표로 다시 확인함(BASS-II 막대 유속은 메모의 제안 0–20이 아니라 원 표대로 0–38.5) | `scoring/`, `web/scorer.js`, `scripts/build_catalog.py`, `data/catalog/*.csv`, `validation/` | 미검토. 카탈로그 41행 모두 ai_extracted |
| 11/14 13:20– | Claude Code (Opus 5.5, catalog 역할) | ui에게서 카탈로그·순위 계산기·검증을 넘겨받는 새 세션. 인수인계 목록의 남은 수정(버너 산화제 흐름 산소, `o2_above_all` 기준, 기체·액적 키워드, 카탈로그와 파이프라인의 일치 검사, 사람 확인표, 열린 범위 문구)을 원 표와 대조해 수행 | `coord/status/catalog.md`, `coord/requests/*catalog-to-*`. 넘겨받은 뒤 `data/catalog/`, `scoring/`, `validation/`, `web/scorer.js` | 미검토. 시험·검증·parity 자동 통과만 확인 |
| 11/14 14:00– | Claude Code (Opus 5.5, catalog 역할) | 사용자 요청으로 순위 계산기의 이론적 오류 검토. 찾은 것 중 사용자가 고르게 한 5건을 수정: CO2를 산소로 읽던 정규식, '천장'을 직물로 읽던 키워드, 가정값을 신뢰도에 넣던 계산, 한쪽만 기록된 유속 범위의 유사도, 기록·시험 행렬·팀 판독 값을 'tested'로 쓰던 문구(카탈로그 출처 열 3개 추가). pm 결정 반영(사람 확인은 점수에 영향 없음, `ranges_separate` 경고). pm 점검에서 출처를 못 찾은 카탈로그 문구 4건을 원문 표기대로 수정 | `scoring/scorer.py`, `web/scorer.js`, `scoring/scoring_config.json`, `scoring/test_scorer.py`, `scripts/build_catalog.py`, `scripts/export_catalog_xlsx.py`, `data/catalog/*`, `validation/scenarios.json` | 미검토. 원 표와 기록은 직접 대조했고 시험 35개·검증 29/29·parity 68/68 자동 통과. 데모 순위 불변 확인 |
| 11/14 14:19– | Claude Code (Opus 5.5, catalog 역할) | 사용자가 준 연소공학 교재(Turns 2012, 저작권 자료)의 해당 장을 읽고, 순위 규칙의 방향과 함수 형태를 대조해 근거 문서를 작성. 교재 문장·그림·표는 옮기지 않음. 점수 코드는 바꾸지 않음 | `scoring/MODEL_BASIS.md`, `scoring/README.md`, `compliance/SOURCES.md` | 미검토. 교재 해석은 AI의 요약이며 연소 전공 팀원 확인 필요 |

## 제품 안에서 동작하는 AI

| 모델 | 제공처 | 역할 | 입력 데이터 | 출력 검증 방법 |
|---|---|---|---|---|
| (미정) | | | | |
| gpt-oss:20b (Ollama tag, digest f38aa0c53da5, 20.9B, MXFP4; Apache-2.0) | OpenAI, run locally through Ollama 0.40.16 (offline at build time; the public site calls no model) | writes summary sentences from supplied PSI text; never numbers, scores, need statements or gaps. Only entry point `ai/llm.py`, whose allowlist blocks every other installed model | PSI record prose (objective, approach, hypothesis, researchImpacts), split into numbered sentences by `ai/evidence.py` | code gates, then review of every sentence |
