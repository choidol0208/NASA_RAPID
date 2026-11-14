#!/usr/bin/env python3
# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps
# Challenge 2026 hackathon (2026-11-14).
"""Export the catalog CSVs to a reviewer-friendly workbook and write the data dictionary.

Usage:
    python3 scripts/export_catalog_xlsx.py

Reads   data/catalog/investigations.csv, data/catalog/configurations.csv
Writes  data/catalog/catalog.xlsx         (shaded header bands: group / column key / Korean meaning)
        data/catalog/data_dictionary.csv  (table, column, group, meaning_ko, allowed values, used_by)

The CSVs stay the machine source of truth; the workbook is for people to read and review.
"""
import csv
import os

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAT = os.path.join(ROOT, "data", "catalog")

# (column, group, Korean meaning, allowed values / unit, used_by)
INV_DICT = [
    ("investigation_id", "식별", "조사 ID (팀 지정 짧은 코드)", "BASS-II 형식", "연결 키"),
    ("psi_accession", "식별", "PSI 등록 번호", "PSI-25 형식", "연결 키, 원본"),
    ("investigation_name", "식별", "PSI 정식 이름", "영어", "표시"),
    ("project_group", "식별", "상위 묶음", "ACME, BASS, Saffire, SAME …", "묶어 보기"),
    ("tier", "분류", "팀 우선순위 군", "1 = 과제문이 화재 안전에 직접 연결, 2 = 이름만 언급, 3 = 나머지", "작업 순서"),
    ("platform", "근거 품질", "실험 장소", "ISS, free_flyer (Cygnus), ground", "표시"),
    ("hardware", "식별", "실험 장비 (PSI 기록 그대로)", "자유 텍스트", "표시, 필터"),
    ("operation_period", "식별", "수행 기간 (PSI 기록 그대로, MM-DD-YYYY)", "", "표시"),
    ("objectives", "분류", "목적 1~2문장 (PSI 기록 요약)", "영어", "요약, AI 근거"),
    ("research_focus", "분류", "연구 초점 (여러 개는 ;)", "ignition, flame_spread, burning_rate, extinction_limit, flammability_boundary, smoke_soot, detection, suppression, flame_structure", "S_role"),
    ("fire_safety_role", "분류", "화재 안전 축 (팀 판단, 여러 개는 ;)", "prevention, detection, suppression, fundamental", "S_role"),
    ("fire_scenario_tags", "분류", "연결되는 화재 상황 (팀 판단)", "cabin_material, wire_overheat, liquid_leak, gas_leak, smoldering, dust, high_oxygen, quiescent_ambient", "설명, 필터"),
    ("mu_g_duration_class", "근거 품질", "미세중력 유지 시간", "long, short, none (ground)", "근거 품질 M"),
    ("has_1g_comparison", "근거 품질", "같은 조건 지상(1g) 비교가 기록에 있나", "Y, (빈칸 = 기록에서 확인 안 됨)", "부분중력 범위 제시, 동점 처리"),
    ("data_availability", "근거 품질", "데이터 형태", "raw_table, summary_table, images_video, derived_analysis, papers_only", "근거 품질 M"),
    ("test_count", "근거 품질", "시험 수 (표 행 수 또는 점화된 화염 수)", "숫자", "표시"),
    ("key_findings", "결과", "핵심 결과 (PSI 기록·표에 있는 것만)", "영어, 숫자는 단위와 함께", "요약, AI 근거"),
    ("psi_url", "출처", "PSI 조사 페이지", "URL", "원본 연결"),
    ("psi_dataset_id", "출처", "PSI 데이터셋 번호", "PSI-25 형식", "원본 연결"),
    ("dataset_doi", "출처", "데이터셋 DOI (PSI 인용 요구)", "10.60555/…", "원본 연결, 인용"),
    ("doi_list", "출처", "관련 논문 DOI (최대 6개, ;로 구분)", "", "AI 근거"),
    ("license", "출처", "PSI 기록의 라이선스", "CC0-1.0 등", "규정 준수"),
    ("source_notes", "검증", "출처 메모, 원문과 다른 점", "자유 텍스트", "검증"),
    ("verification_status", "검증", "확인 상태", "ai_extracted, human_verified", "근거 품질 M, 배지"),
    ("verified_by", "검증", "확인한 사람 (이니셜)", "", "검증"),
    ("collected_on", "검증", "수집한 날짜", "YYYY-MM-DD", "검증"),
]
CFG_DICT = [
    ("config_id", "식별", "구성 ID (점수를 매기는 단위)", "BASS-II-C01 형식", "연결 키"),
    ("investigation_id", "식별", "조사표 연결", "", "연결 키"),
    ("psi_accession", "식별", "PSI 등록 번호", "", "연결 키"),
    ("config_label", "식별", "구성 설명", "영어", "표시"),
    ("fuel_phase", "연료", "연료 상", "solid, liquid, gas, aerosol", "S_fuel"),
    ("fuel_material", "연료", "구체 물질", "PMMA, SIBAL, n-heptane …", "S_fuel"),
    ("fuel_class", "연료", "연료 분류 (팀 판단)", "fabric, charring_solid, thermoplastic_solid, pyrolyzing_solid, liquid_hydrocarbon, liquid_alcohol, gaseous_hydrocarbon, hydrogen, particulate", "S_fuel"),
    ("melt_behavior", "연료", "녹음·탄화 거동 (고체)", "melts, chars, neither", "S_fuel"),
    ("surrogate_for", "연료", "이 기체 버너가 흉내 내는 대상", "solid", "S_fuel"),
    ("sooting_tendency", "연료", "그을음 경향 (팀 판단)", "low, medium, high", "감지 프로파일"),
    ("sample_geometry", "형상", "시료·버너 형상", "flat_sheet, rod, sphere, droplet, jet_burner, porous_burner, spherical_burner, counterflow_burner, heated_sample", "S_geom"),
    ("thickness_mm", "형상", "두께 또는 지름 (mm)", "숫자 또는 범위", "thermal_regime 판정"),
    ("length_mm", "형상", "길이 (mm)", "", "표시"),
    ("width_mm", "형상", "폭 (mm)", "", "표시"),
    ("thermal_regime", "형상", "열적 두께 (고체, 팀 판단)", "thin, intermediate, thick", "S_geom"),
    ("flame_type", "형상", "화염 종류", "diffusion, premixed, cool_flame, none", "설명"),
    ("flow_config", "유동", "유동 방식 (여러 개는 ;)", "quiescent, opposed, concurrent, coflow, counterflow, radial", "S_cfg"),
    ("flow_min_cms", "유동", "시험한 기류 속도 최소 (cm/s)", "숫자", "S_v"),
    ("flow_max_cms", "유동", "시험한 기류 속도 최대 (cm/s)", "숫자", "S_v"),
    ("o2_min_pct", "분위기", "산소 몰분율 최소 (%)", "숫자", "S_O2"),
    ("o2_max_pct", "분위기", "산소 몰분율 최대 (%)", "숫자", "S_O2"),
    ("o2_reference", "분위기", "산소 값의 기준 (추가 열)", "ambient = 주변 분위기, oxidizer_stream = 버너에서 나오는 산화제", "설명, 경고"),
    ("pressure_min_kpa", "분위기", "전체 압력 최소 (kPa)", "숫자", "S_P"),
    ("pressure_max_kpa", "분위기", "전체 압력 최대 (kPa)", "숫자", "S_P"),
    ("ppo2_min_kpa", "분위기", "산소 분압 최소 (자동 계산)", "kPa", "표시"),
    ("ppo2_max_kpa", "분위기", "산소 분압 최대 (자동 계산)", "kPa", "표시"),
    ("diluent", "분위기", "희석·불활성 기체", "N2, CO2, He, Ar", "S_dil"),
    ("diluent_max_pct", "분위기", "희석제 최대 농도 (%)", "숫자", "S_dil"),
    ("ambient_temp_k", "분위기", "주변 온도 (K)", "숫자", "표시"),
    ("atmosphere_basis", "분위기", "숫자의 출처 (추가 열)", "table, record, not_reported", "신뢰도 표시"),
    ("o2_source", "분위기", "산소 범위의 출처 (추가 열)", "table, record, test_matrix, team, 빈칸", "이유 문장 (tested 표기)"),
    ("pressure_source", "분위기", "압력 범위의 출처 (추가 열)", "table, record, test_matrix, team, 빈칸", "이유 문장 (tested 표기)"),
    ("flow_source", "분위기", "유속 범위의 출처 (추가 열)", "table, record, test_matrix, team, 빈칸", "이유 문장"),
    ("gravity_level", "분위기", "중력 조건", "microgravity, 1g", "경고"),
    ("ignition_method", "점화", "점화 방식", "hot_wire 등", "표시"),
    ("measured_outputs", "결과", "측정 항목", "flame_spread_rate, burning_rate, extinction_condition, particle_size …", "감지 프로파일, 데이터 연결"),
    ("flammability_boundary_reported", "결과", "소화·가연 한계 데이터가 있나", "Y, N", "근거 설명"),
    ("extinction_mechanism", "결과", "소염 메커니즘", "radiative_loss, blowoff, dilution, quenching, burnout", "결론 설명"),
    ("key_findings", "결과", "이 구성의 결과 (기록·표에 있는 것만)", "영어", "AI 근거"),
    ("test_count_config", "결과", "이 구성의 시험 수", "숫자", "표시"),
    ("tests_table_ref", "결과", "시험 단위 표 파일과 필터", "파일명 (조건)", "로우데이터 연결"),
    ("source_notes", "검증", "출처 메모", "", "검증"),
    ("verification_status", "검증", "확인 상태", "ai_extracted, human_verified", "근거 품질 M, 배지"),
]

FONT = "Arial"
GROUP_FILL = {
    "식별": "1F3A5F", "분류": "2E5E4E", "근거 품질": "5B4A1F", "결과": "5A2E4F", "출처": "3D3D6B",
    "검증": "4A4A4A", "연료": "7A3E12", "형상": "2E5E4E", "유동": "1F4F7A", "분위기": "1F3A5F", "점화": "5B4A1F",
}
KEY_FILL = PatternFill("solid", fgColor="D9E2F3")
KO_FILL = PatternFill("solid", fgColor="EEF2F8")
thin = Side(style="thin", color="B7C3D6")
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)
WIDE = {"objectives": 60, "key_findings": 60, "source_notes": 48, "investigation_name": 44, "config_label": 44,
        "hardware": 34, "fuel_material": 34, "measured_outputs": 34, "doi_list": 40, "research_focus": 30,
        "atmosphere_basis": 32, "tests_table_ref": 40, "psi_url": 44}


def read_csv(name):
    with open(os.path.join(CAT, name), encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
        return rows


def to_value(v):
    if v == "":
        return None
    try:
        f = float(v)
        return int(f) if f.is_integer() and "." not in v else f
    except ValueError:
        return v


def write_sheet(ws, rows, spec, title):
    cols = [c[0] for c in spec]
    assert cols == list(rows[0].keys()), f"{title}: dictionary and CSV columns differ"
    # row 1: group band (merged), row 2: column key, row 3: Korean meaning
    start = 1
    for i in range(1, len(spec) + 1):
        g = spec[i - 1][1]
        nxt = spec[i][1] if i < len(spec) else None
        if nxt != g:
            ws.merge_cells(start_row=1, start_column=start, end_row=1, end_column=i)
            c = ws.cell(row=1, column=start, value=g)
            c.fill = PatternFill("solid", fgColor=GROUP_FILL.get(g, "333333"))
            c.font = Font(name=FONT, bold=True, color="FFFFFF", size=10)
            c.alignment = Alignment(horizontal="center", vertical="center")
            for j in range(start, i + 1):
                ws.cell(row=1, column=j).fill = PatternFill("solid", fgColor=GROUP_FILL.get(g, "333333"))
            start = i + 1
    for j, (col, _g, ko, allowed, _u) in enumerate(spec, start=1):
        k = ws.cell(row=2, column=j, value=col)
        k.fill, k.font, k.border = KEY_FILL, Font(name=FONT, bold=True, size=10, color="1F2A44"), BORDER
        k.alignment = Alignment(vertical="center", wrap_text=True)
        m = ws.cell(row=3, column=j, value=ko)
        m.fill, m.font, m.border = KO_FILL, Font(name=FONT, italic=True, size=9, color="44506A"), BORDER
        m.alignment = Alignment(vertical="top", wrap_text=True)
        ws.column_dimensions[get_column_letter(j)].width = WIDE.get(col, 16)
    for i, row in enumerate(rows, start=4):
        for j, col in enumerate(cols, start=1):
            c = ws.cell(row=i, column=j, value=to_value(row[col]))
            c.font = Font(name=FONT, size=10)
            c.border = BORDER
            c.alignment = Alignment(vertical="top", wrap_text=col in WIDE)
            if col == "psi_url" and row[col]:
                c.hyperlink = row[col]
                c.font = Font(name=FONT, size=10, color="1F4FB4", underline="single")
    ws.row_dimensions[1].height = 18
    ws.row_dimensions[2].height = 30
    ws.row_dimensions[3].height = 42
    ws.freeze_panes = "C4"
    ws.auto_filter.ref = f"A2:{get_column_letter(len(cols))}{len(rows) + 3}"
    ws.sheet_view.zoomScale = 90


def main():
    inv, cfg = read_csv("investigations.csv"), read_csv("configurations.csv")
    wb = Workbook()
    rd = wb.active
    rd.title = "README"
    lines = [
        ("Flame in Freefall 실험 카탈로그", True),
        ("NASA PSI 연소과학 조사 24개(Investigations)와, 점수를 매기는 단위인 시험 구성 41개(Configurations).", False),
        ("", False),
        ("읽는 법", True),
        ("1행(색 띠) = 열 묶음, 2행(파란 음영) = 열 이름(코드가 읽는 키), 3행(옅은 음영, 기울임) = 한국어 뜻. 데이터는 4행부터입니다.", False),
        ("열 이름은 영어 그대로 두세요. 코드(scoring/scorer.py)가 이 이름으로 읽습니다. 원본 데이터는 같은 폴더의 CSV이고, 이 파일은 사람이 보기 위한 사본입니다.", False),
        ("빈칸 = PSI 기록이나 표에서 값을 확인하지 못함. 0으로 채우지 않습니다. 점수 계산에서는 'unknown'(0.5)으로 처리됩니다.", False),
        ("atmosphere_basis 열이 숫자의 출처를 밝힙니다: table = PSI 시험 표, record = PSI 기록 본문, not_reported = 기록 없음.", False),
        ("o2_source, pressure_source, flow_source는 값마다 출처를 나눕니다: table = 시험 표의 값, record = 기록 본문에 적힌 값(시험값 아님), test_matrix = 계획된 시험 행렬, team = 팀의 판독. 순위의 이유 문장은 table 값에만 'tested'를 씁니다.", False),
        ("", False),
        ("주의", True),
        ("모든 행은 AI(Claude)가 PSI 기록(data/psi/)에서 뽑은 값이며 verification_status = ai_extracted 입니다. 사람이 원문과 대조한 뒤 human_verified로 바꿉니다.", False),
        ("tier, fire_safety_role, research_focus, fire_scenario_tags, fuel_class, thermal_regime, sooting_tendency는 NASA의 분류가 아니라 팀의 판단입니다.", False),
        ("o2_reference = oxidizer_stream 인 행(역화염)의 산소 값은 주변 분위기가 아니라 버너에서 나오는 산화제의 산소 농도입니다.", False),
        ("", False),
        ("출처", True),
        ("NASA Physical Sciences Informatics (https://psi.nasa.gov/), 실험별 DOI는 dataset_doi 열. 라이선스는 license 열 (대부분 CC0-1.0, PSI-10은 기록에 없음).", False),
        ("생성: scripts/build_catalog.py → scripts/export_catalog_xlsx.py (2026-11-14).", False),
    ]
    for i, (t, bold) in enumerate(lines, start=1):
        c = rd.cell(row=i, column=1, value=t)
        c.font = Font(name=FONT, bold=bold, size=13 if i == 1 else 10)
        c.alignment = Alignment(wrap_text=True, vertical="top")
    rd.column_dimensions["A"].width = 120
    write_sheet(wb.create_sheet("Investigations"), inv, INV_DICT, "Investigations")
    write_sheet(wb.create_sheet("Configurations"), cfg, CFG_DICT, "Configurations")
    dd = wb.create_sheet("Dictionary")
    hdr = ["table", "column", "group", "meaning_ko", "allowed_values_or_unit", "used_by"]
    for j, h in enumerate(hdr, start=1):
        c = dd.cell(row=1, column=j, value=h)
        c.fill, c.font, c.border = KEY_FILL, Font(name=FONT, bold=True, size=10), BORDER
    rows = [("investigations",) + d for d in INV_DICT] + [("configurations",) + d for d in CFG_DICT]
    for i, r in enumerate(rows, start=2):
        for j, v in enumerate(r, start=1):
            c = dd.cell(row=i, column=j, value=v)
            c.font, c.border = Font(name=FONT, size=10), BORDER
            c.alignment = Alignment(wrap_text=True, vertical="top")
    for j, w in enumerate([16, 30, 12, 40, 60, 24], start=1):
        dd.column_dimensions[get_column_letter(j)].width = w
    dd.freeze_panes = "A2"
    wb.save(os.path.join(CAT, "catalog.xlsx"))
    with open(os.path.join(CAT, "data_dictionary.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(hdr)
        w.writerows(rows)
    print("wrote catalog.xlsx and data_dictionary.csv")


if __name__ == "__main__":
    main()
