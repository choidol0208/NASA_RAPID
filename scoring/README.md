# 카탈로그 필터 (Catalog filter)

> AI 생성 코드·데이터: Claude(AI 도우미)로 2026-11-14에 작성했습니다. 카탈로그 값은 `ai_extracted` 상태이며 사람이 원문과 대조해야 합니다. 점수와 순위는 팀의 방법이지 NASA의 결론이 아닙니다.

사용자가 넣은 환경과 조건에 가장 비슷한 PSI 시험 구성을 찾아 1~3순위 조사를 고릅니다. 점수는 코드가 계산하므로 같은 입력에는 항상 같은 결과가 나옵니다. AI(LLM)는 이 결과를 받아 설명만 합니다.

## 파일

| 파일 | 내용 |
| --- | --- |
| `data/catalog/investigations.csv` | 조사표: PSI 연소 조사 24개, 1행 = 조사 1개 |
| `data/catalog/configurations.csv` | 구성표: 시험 구성 41개, 1행 = 점수를 매기는 단위 |
| `data/catalog/catalog.xlsx` | 사람이 보는 사본 (머리글 음영, 한국어 뜻, 데이터 사전) |
| `data/catalog/data_dictionary.csv` | 열 이름, 한국어 뜻, 허용값, 쓰임 |
| `scoring/scoring_config.json` | 가중치 프로파일, 유사도 기준 폭, 프리셋, 키워드, 경고 문구 (대시보드도 이 파일을 읽으면 됨) |
| `scoring/scorer.py` | 해석 + 점수 계산 + 1~3순위 선정 (표준 라이브러리만 사용) |
| `scoring/test_scorer.py` | 단위 시험 18개 (손계산 예시 포함) |
| `validation/scenarios.json` | 검증 시나리오 22개 + 가중치 안정성 검사 |
| `validation/run_validation.py` | 시나리오 실행기, `validation/report.md` 생성 |
| `presentation/catalog_filter_slide.pptx` | 발표용 설명 슬라이드 1장 (영어, 발표 메모는 한국어) |
| `scripts/build_catalog.py`, `scripts/export_catalog_xlsx.py` | PSI 원본에서 카탈로그를 다시 만드는 스크립트 |

## 실행

```bash
python3 -m scoring.scorer "달 기지 면직물"                 # 사람이 읽는 출력
python3 -m scoring.scorer "ISS" --json                     # 대시보드용 JSON
python3 -m unittest scoring.test_scorer -v                  # 단위 시험
python3 validation/run_validation.py                        # 시나리오 22개 + 안정성 → validation/report.md
python3 validation/run_validation.py --target app.pipeline:rank   # 대시보드의 함수로 같은 검증
python3 scripts/build_catalog.py && python3 scripts/export_catalog_xlsx.py   # 카탈로그 재생성
```

```python
from scoring.scorer import rank
out = rank("lunar habitat cotton fabric")          # 문자열(러프 입력) 또는
out = rank({"preset": "iss", "fuel": "PMMA", "o2_pct": 25})   # 구조화 입력
out["status"]        # ok | out_of_scope | need_input
out["assumptions"]   # 사용자가 말하지 않아 프리셋·기본값으로 채운 값 (화면에 보여주기)
out["warnings"]      # 부분중력, 외삽, 범위 밖 등
out["results"]       # 1~3순위: investigation_id, config_id, score, similarity, why, main_gap, warnings, psi_url, dataset_doi
out["ranking"]       # 전체 조사 순위 (표·차트용)
```

## 다른 팀원 산출물과의 연결

1~3순위가 정해진 뒤 4단계(로우데이터 확인)는 팀원의 파이프라인 결과 `data/pipeline/tests.csv`를 씁니다. 결과의 `psi_accession`(예: PSI-69)으로 `investigation_id` 열을 거르고, 구성의 연료(`fuel_material`)로 한 번 더 거르면 됩니다. 구성표의 `tests_table_ref`는 PSI 원본 표 파일과 조건을 적어 둔 것입니다.

## 러프한 입력 처리

입력은 세 층으로 해석하고, 뒤의 층이 앞의 층을 덮습니다: 기본값 < 프리셋 < 문장 속 단어·숫자 < 명시한 필드.

| 입력 | 해석 |
| --- | --- |
| `ISS` | 산소 21%, 101.3 kPa, 환기, 미세중력, 질문 유형 예방 (모두 "가정"으로 표시) |
| `moon` / `달` | 산소 30%, 70.3 kPa (과제문), 환기, 부분중력 경고 |
| `Mars base` | 대기 수치 없음 → 입력 요청 경고, 부분중력 경고 |
| `spacesuit` | 산소 100%, 29.6 kPa (과제문) → PSI 최고치(85%) 초과 외삽 경고 |
| `fabric`, `smoke`처럼 한 단어 | 재료 또는 질문 유형만으로 순위 |
| `ISS at 30% O2 and 10.2 psi` | 문장 속 숫자가 프리셋을 덮음 |
| 빈 입력 | 순위를 만들지 않고 무엇을 넣을지 안내 (`need_input`) |
| `로켓 추진제` 등 | 범위 밖 (`out_of_scope`) |

사용자가 주지 않은 차원은 점수에서 빼고, 남은 가중치를 합 1로 다시 나눕니다. 결과마다 `confidence`(high/medium/low)는 프로파일 가중치 중 실제로 비교한 몫입니다.

## 점수 규칙

`score = 100 × M × G × Σ wᵢ·Sᵢ`. 차원별 식과 근거는 가이드라인 문서와 `scoring_config.json`의 `why` 항목에 있습니다. 가이드라인 문서 이후 바뀐 규칙은 다섯 가지입니다.

1. **게이트는 계단이 아니라 경사**: 연료나 산소 유사도가 0.2 미만이면 0.5에서 1.0 사이로 줄입니다(0이면 0.5, 0.2면 1.0). 0.199와 0.201이 크게 갈리는 문제를 없앴습니다.
2. **보고되지 않은 대기**: PSI 기록은 특이한 대기를 항상 적으므로, 산소가 비어 있으면 일반 공기(21%)로 계산합니다. 압력은 ISS 선실·MSG·Cygnus에서 한 실험만 101.3 kPa로 계산합니다. 카탈로그는 빈칸 그대로 두고, 이 가정을 쓴 결과에는 `fallback` 경고가 붙습니다.
3. **모름이 측정값을 이기지 않게**: 연료가 비어 있는 행은 0.5와 "이번 질문에서 가장 잘 맞은 실제 값" 중 작은 값으로 계산합니다.
4. **보완 슬롯**: 사용자 산소가 일반 공기(21±2%)가 아닌데 상위 3개 중 그 산소에서 시험한 결과가 없으면, 3위 자리에 그 산소를 시험한 가장 좋은 결과를 넣고 `complementary` 경고로 이유를 밝힙니다.
5. **동점**: 3점 이내 차이는 동점으로 보고, 근거 품질과 1g 비교 여부로 순서를 정합니다.

## 검증 결과 (2026-11-14)

시나리오 22/22 통과, 주요 시나리오 5개에서 가중치를 ±0.05 바꿔도 1위 유지. 기대 답은 팀이 연소 지식으로 정한 것이라 전문가 검토가 남아 있습니다. 자세한 표는 `validation/report.md`.
