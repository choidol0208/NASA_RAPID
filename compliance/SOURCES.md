# 출처 기록

프로젝트 제작에 쓴 모든 자료를 쓰는 시점에 한 줄씩 추가한다. 오픈소스와 무료 자료도 포함한다.
마감 전에 이 표를 제출 양식의 Space Agency Data와 References로 옮긴다.

| 추가 시각 (KST) | 종류 | 이름 | URL | 라이선스 | 제공처 | 프로젝트에서 쓴 곳 |
|---|---|---|---|---|---|---|
| 11/14 09:10 | 데이터 | PSI Combustion Science 실험 기록 24건, 파일 목록, 시험 조건 표 22개 | https://psi.nasa.gov/ | 실험별 CC0-1.0 (PSI-10은 라이선스 칸이 비어 있음) | NASA Biological and Physical Sciences | `data/psi/`, 데이터 구조 분석 |
| 11/14 09:40 | 문서 | Detailed Results from the Flame Extinguishment Experiment (FLEX), NASA/TP-2015-216046 | https://ntrs.nasa.gov/citations/20150023456 | 미국 정부 저작물, 공개 이용 가능 | NASA NTRS | FLEX 표의 열 이름 해석(O, N, CO 열이 O2, N2, CO2임) |
| 11/14 09:10 | 문서 | Apache License 2.0 본문 | https://www.apache.org/licenses/LICENSE-2.0 | Apache-2.0 | Apache Software Foundation | `LICENSE` |
| 11/14 10:00 | 글꼴 | IBM Plex Sans KR, IBM Plex Mono (Google Fonts 경유) | https://fonts.google.com/specimen/IBM+Plex+Sans+KR | SIL Open Font License 1.1 | IBM | 팀 내부 페이지 `reports/data-map.html` |
| 11/14 10:50 | 문서 | BASS-II ReadMe, Test Matrices, Fan calibration data (PSI-25); FLEX DoD, Test Plan (PSI-69); BASS Planned Test Matrix, DLD (PSI-26) | https://psi.nasa.gov/physci/repo/data/investigations/PSI-25 외 | CC0-1.0 | NASA PSI | `data/psi/docs/`, BASS-II 열의 뜻(Air display는 cm/s 등) 확인 |
| 11/14 오후 | 문서 | A Researcher's Guide to: Combustion Science (NP-2015-10-034-JSC) | https://www.nasa.gov/wp-content/uploads/2016/05/np-2015-10-034-jsc_combustion_in_reduced_gravity-iss-mini-book-011116-508.pdf | 미국 정부 저작물, 공개 이용 가능 (이용 조건은 제출 전 재확인) | NASA ISS Program Science Office | `pipeline/spec/needs.json`의 필요 정보 정의 근거 |
| 11/14 오후 | 문서 | Flame in Freefall 과제문 (예방·감지·진압 구분, 산소 농도와 유동, 달 기지 대기 조건) | https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall-ai-powered-fire-safety-insights-from-microgravity-combustion-data/ (공식 페이지는 이 환경에서 열리지 않아 사본으로 읽음. 공식 페이지 대조 필요) | 공개 과제문 | NASA Space Apps Challenge | `pipeline/spec/needs.json`의 필요 정보 정의 근거 |

실험별 DOI는 `data/psi/manifest.json`에 있다. PSI는 데이터를 쓸 때 실험의 DOI로 인용하라고 요구한다.

종류: 데이터 / 문서 / 코드 / 라이브러리 / 모델 / 이미지 / 글꼴 / 기타
