# 실험 카탈로그

> AI 생성 데이터: Claude(AI 도우미)가 2026-11-14에 `data/psi/`의 PSI 기록과 시험 표에서 뽑았습니다. 모든 행은 `verification_status = ai_extracted`이며, 사람이 원문과 대조한 행만 `human_verified`로 바꿉니다.

- `investigations.csv`: PSI 연소과학 조사 24개 (1행 = 조사 1개, 26열)
- `configurations.csv`: 시험 구성 41개 (1행 = 같은 조건 범위를 공유하는 시험 묶음, 40열). 순위 점수는 이 표에서 계산합니다.
- `catalog.xlsx`: 사람이 검토하는 사본. 1행 묶음 띠, 2행 열 이름(음영), 3행 한국어 뜻, 4행부터 데이터.
- `data_dictionary.csv`: 열마다 한국어 뜻, 허용값, 쓰이는 곳.

## 원칙

- 숫자는 PSI 시험 표(`table`)나 PSI 기록 본문(`record`)에서만 가져왔고, `atmosphere_basis` 열에 출처를 적었습니다. 기록에 없는 값은 빈칸입니다. 0으로 채우지 않습니다.
- `tier`, `fire_safety_role`, `research_focus`, `fire_scenario_tags`, `fuel_class`, `thermal_regime`, `sooting_tendency`는 팀의 분류입니다.
- 가이드라인 문서 대비 추가 열: 조사표 `psi_accession`, `license` / 구성표 `psi_accession`, `o2_reference`(ambient 또는 oxidizer_stream), `atmosphere_basis`.
- 원문과 다른 점, 기록끼리 맞지 않는 점은 `source_notes`에 적었습니다 (예: Saffire-I 기록의 날짜, Saffire 표의 두께 단위).

## Human verification (added 2026-11-14 by the catalog role, AI-generated)

`validation/verification_sheet.csv` lists the catalog values behind the demo rankings (`ISS`, `lunar habitat`, `ISS cotton fabric`, `lunar habitat cotton fabric`): fuel, oxygen, pressure and flow ranges, and test counts. Each value comes with the NASA table rows and raw cells, or the PSI record text, where a person can check it. Rebuild it with `python3 validation/build_verification_sheet.py` after any catalog or scorer change. A person fills in `checked_by`, `matches_source` and `comment`. A row becomes `human_verified` only through `scripts/build_catalog.py`. Row numbers are CSV row numbers (header = row 1), the same numbers that `source_notes` and `data/pipeline/*.csv` use.

## 다시 만들기

```bash
python3 scripts/build_catalog.py        # CSV 2개
python3 scripts/export_catalog_xlsx.py  # catalog.xlsx, data_dictionary.csv
```

출처: NASA Physical Sciences Informatics (https://psi.nasa.gov/). 실험별 DOI는 `dataset_doi` 열, 라이선스는 `license` 열 (PSI-10은 기록에 라이선스가 없음).
