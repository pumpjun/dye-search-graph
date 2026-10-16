import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
import base64
import html as html_lib
import streamlit.components.v1 as components

# ==========================================
# 1. 웹페이지 기본 설정 및 세션 초기화
# ==========================================
st.set_page_config(page_title="Ohyoung Dye Finder", page_icon="logo.png", layout="wide")

if "lang" not in st.session_state: st.session_state.lang = "EN"
lang = st.session_state.lang
if "app_mode" not in st.session_state: st.session_state.app_mode = "tab3"

# ==========================================
# 2. 다국어 번역 데이터 사전 정의 (EN / KO)
# ==========================================
t = {
    "EN": {
        "header": "Ohyoung Dye Finder",
        "created_by": "Created by tskwon <span class='material-symbols-outlined' style='font-size: 14px; vertical-align: middle;'>science</span>",
        "menu_title": "Select Program",
        "tab1": "1. Fastness Matcher",
        "tab2": "2. Compatibility Analyzer",
        "tab3": "3. Fastness & Compatibility",
        "nav1": "Fastness Matcher",
        "nav2": "Compatibility",
        "nav3": "Fastness & Compatibility",
        "page1_sub": "Find dyes that meet every minimum fastness grade you set on the left.",
        "page2_sub": "Compare exhaustion / fixation curves of the dyes you pick on the left.",
        "page3_sub": "Filter by fastness, tick dyes in the table, then compare their compatibility curves.",
        "instruction_text": "Please select the desired dye groups and fastness grades from the left sidebar.",
        "sb_group_title": "1. Select Dye Group",
        "sb_group_short": "Dye Group",
        "select_all": "Select / Deselect All",
        "sb_spec_title": "2. Set Min Specs",
        "sb_spec_short": "Min. Fastness",
        "sb_dye_select": "Select Dyes to Compare",
        "spec_warn": "Please select at least one dye group in the sidebar.",
        "search_res_hdr": ":material/manage_search: Fastness Matching Results",
        "res_title": "Matching dyes",
        "search_res_sub": "Results (Matching Dyes: {count})",
        "search_res_desc": "**Click the checkbox in the first column (`Select`) to choose dyes for comparison.**",
        "res_hint": "Tick the Select column to compare up to 3 dyes below.",
        "col_select": "Select",
        "col_group": "Group",
        "col_name": "Dye Name",
        "warn_limit": "Only up to 3 selected dyes are shown in click order.",
        "sim_hdr": ":material/monitoring: Compatibility Simulation",
        "sim_title": "Compatibility simulation",
        "sel_summary_hdr": ":material/fact_check: Selected Dyes Fastness Summary",
        "sel_summary_title": "Fastness of selected dyes",
        "no_match": "No dyes match the criteria.",
        "select_prompt": "Please check the **[Select]** checkbox above to compare dyes.\n\nGraph colors will be assigned as Yellow, Red, and Blue in the order selected.",
        "select_prompt_tab3": "Please select at least one dye from the left sidebar for comparison.",
        "err_time_data": "Time data columns are invalid.",
        "xaxis": "Process Time (min)",
        "yaxis": "Exhaustion / Fixation Rate (%)",
        "summary_hdr": ":material/dataset: Numeric Summary",
        "diag_hdr": ":material/troubleshoot: Field Diagnosis",
        "diag_title": "Field diagnosis",
        "diag_excel": "**Excellent**\n\nBehaviors match closely. Low risk of tailing.",
        "diag_warn": "**Caution**\n\nMinor rate differences. Adjust temperature profile.",
        "diag_danger": "**Danger**\n\nHigh risk of tailing/face-back in bulk production.",
        "diag_dev": "Max. spread between curves",
        "minute_unit": "min",
        "crit_light": "Light",
        "crit_p_light_acid": "Persp-Light(Acid)",
        "crit_p_light_alk": "Persp-Light(Alkali)",
        "crit_p_acid": "Persp(Acid)",
        "crit_p_alk": "Persp(Alkali)",
        "crit_wash": "Washing",
        "crit_chlor": "Chlorine",
        "rep_wash_title": "Repeated Wash",
        "rep_wash_times_label": "Wash Cycles",
        "rep_wash_grade_label": "Rep. Wash Grade",
        "rep_wash_none": "None",
        "active_filters": "Active conditions",
        "no_filters": "No minimum grade set yet",
        "groups_badge": "{n} groups",
        "empty_title": "Pick dyes to compare",
        "empty_sel_title": "Tick dyes in the table",
        "graph_order": "Graph colors follow the color order: Yellow → Red → Blue.",
    },
    "KO": {
        "header": "Ohyoung Dye Finder",
        "created_by": "Created by tskwon <span class='material-symbols-outlined' style='font-size: 14px; vertical-align: middle;'>science</span>",
        "menu_title": "프로그램 선택",
        "tab1": "1. 요구견뢰도 매칭",
        "tab2": "2. 상용성 비교 분석",
        "tab3": "3. 통합 매칭 및 시뮬레이션",
        "nav1": "요구견뢰도 매칭",
        "nav2": "상용성 비교",
        "nav3": "통합 매칭 · 시뮬레이션",
        "page1_sub": "왼쪽에서 정한 최소 견뢰도를 모두 만족하는 염료를 찾습니다.",
        "page2_sub": "왼쪽에서 고른 염료들의 염착·고착 곡선을 비교합니다.",
        "page3_sub": "견뢰도로 거른 뒤 표에서 염료를 체크하면 상용성 곡선을 비교합니다.",
        "instruction_text": "왼쪽 사이드바에서 원하는 염료군과 견뢰도 등급을 설정하세요.",
        "sb_group_title": "1. 염료 그룹 선택",
        "sb_group_short": "염료 그룹",
        "select_all": "전체 선택 / 해제",
        "sb_spec_title": "2. 요구 스펙 설정 (이상)",
        "sb_spec_short": "요구 견뢰도 (이상)",
        "sb_dye_select": "비교 염료 선택",
        "spec_warn": "좌측 사이드바에서 염료 그룹을 최소 하나 이상 선택해 주세요.",
        "search_res_hdr": ":material/manage_search: 견뢰도 스펙 매칭 결과",
        "res_title": "조건을 만족하는 염료",
        "search_res_sub": "검색 결과 (만족하는 염료: {count}개)",
        "search_res_desc": "**아래 표의 첫 번째 열(`선택`)을 클릭하여 비교할 염료를 선택하세요.** (최대 3개 권장)",
        "res_hint": "표의 선택 열을 체크하면 아래에서 최대 3개까지 비교합니다.",
        "col_select": "선택",
        "col_group": "염료그룹",
        "col_name": "염료명",
        "warn_limit": "안정적인 그래프 비교를 위해 선택하신 순서대로 최대 3개까지만 표시됩니다.",
        "sim_hdr": ":material/monitoring: 선택 염료 상용성 시뮬레이션",
        "sim_title": "상용성 시뮬레이션",
        "sel_summary_hdr": ":material/fact_check: 선택 염료 견뢰도 요약",
        "sel_summary_title": "선택 염료 견뢰도",
        "no_match": "검색 조건에 맞는 염료가 없습니다.",
        "select_prompt": "표에서 비교하고 싶은 염료의 좌측 **[선택]** 체크박스를 눌러주세요.",
        "select_prompt_tab3": "좌측 사이드바에서 비교 분석할 염료를 1개 이상 선택해 주세요.",
        "err_time_data": "상용성 시간 데이터 열(0, 5, 20...)이 올바르지 않습니다.",
        "xaxis": "공정 시간 (분)",
        "yaxis": "염착률 / 고착률 (%)",
        "summary_hdr": ":material/dataset: 수치 요약",
        "diag_hdr": ":material/troubleshoot: 현장 진단",
        "diag_title": "현장 진단",
        "diag_excel": "**우수**\n\n거동이 거의 일치합니다. (Tailing 확률 매우 낮음)",
        "diag_warn": "**주의**\n\n구간별 미세한 속도 차이가 있습니다. 승온 조건 조절 권장.",
        "diag_danger": "**위험**\n\n대량 생산 시 불량(Tailing/Face-back) 발생 확률이 높습니다.",
        "diag_dev": "곡선 간 최대 편차",
        "minute_unit": "분",
        "crit_light": "일광",
        "crit_p_light_acid": "땀일광(산성)",
        "crit_p_light_alk": "땀일광(알칼리)",
        "crit_p_acid": "땀(산성)",
        "crit_p_alk": "땀(알칼리)",
        "crit_wash": "세탁",
        "crit_chlor": "염소수",
        "rep_wash_title": "반복세탁",
        "rep_wash_times_label": "세탁 횟수 선택",
        "rep_wash_grade_label": "반복세탁 요구 등급",
        "rep_wash_none": "적용 안 함",
        "active_filters": "적용 중인 조건",
        "no_filters": "아직 설정한 최소 등급이 없습니다",
        "groups_badge": "그룹 {n}개",
        "empty_title": "비교할 염료를 골라 주세요",
        "empty_sel_title": "표에서 염료를 체크해 주세요",
        "graph_order": "그래프 색은 색순서대로 Yellow → Red → Blue로 배정됩니다.",
    }
}

# 반복세탁 사이클 옵션 정의
cycle_opts_en = [t["EN"]["rep_wash_none"], "5 Cycles", "10 Cycles", "15 Cycles", "20 Cycles", "30 Cycles", "40 Cycles", "50 Cycles"]
cycle_opts_ko = [t["KO"]["rep_wash_none"], "5회", "10회", "15회", "20회", "30회", "40회", "50회"]

def get_excel_cycle_string(selected_val, lang):
    if lang == "KO": return selected_val
    mapping = {"5 Cycles": "5회", "10 Cycles": "10회", "15 Cycles": "15회", "20 Cycles": "20회", "30 Cycles": "30회", "40 Cycles": "40회", "50 Cycles": "50회"}
    return mapping.get(selected_val)

def toggle_all_groups(app_mode_str, all_groups_list):
    master_state = st.session_state[f"chk_all_{app_mode_str}"]
    for g in all_groups_list:
        st.session_state[f"grp_{g}_{app_mode_str}"] = master_state

def set_app_mode(mode):
    st.session_state.app_mode = mode

def on_lang_change():
    st.session_state.lang = {"ENG": "EN", "KOR": "KO"}.get(st.session_state.lang_dropdown, "EN")

# ==========================================
# 3. 로고 인코딩 및 UI 커스텀 CSS (Spectra50 · SpectraMatch · UV-Vis와 같은 디자인)
# ==========================================
try:
    with open("logo.png", "rb") as image_file:
        logo_base64 = base64.b64encode(image_file.read()).decode()
except Exception:
    logo_base64 = ""

# 상단 바 로고: 네이비 바탕에 맞춘 logo1.png (없으면 logo.png)
try:
    with open("logo1.png", "rb") as image_file:
        header_logo_base64 = base64.b64encode(image_file.read()).decode()
except Exception:
    header_logo_base64 = logo_base64

NAVY = "#1b489d"
# 상단 언어 선택 칸 안쪽 왼쪽에 넣는 국기 그림 (Twemoji, CC-BY 4.0). Windows 프로그램 창은 국기 이모지를 글자로 보여 주기 때문에 그림으로 넣습니다.
LANG_FLAG_SVG_B64 = {
    "KO": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAzNiAzNiI+PHBhdGggZmlsbD0iI0VFRSIgZD0iTTM2IDI3YTQgNCAwIDAgMS00IDRINGE0IDQgMCAwIDEtNC00VjlhNCA0IDAgMCAxIDQtNGgyOGE0IDQgMCAwIDEgNCA0djE4eiIvPjxwYXRoIGZpbGw9IiNDNjBDMzAiIGQ9Ik0yMS40NDEgMTMuMDg1YTYgNiAwIDAgMC04LjM1NiAxLjQ3NEEzLjAwMSAzLjAwMSAwIDAgMCAxOCAxOGEzIDMgMCAwIDEgNC45MTUgMy40NDIgNiA2IDAgMCAwLTEuNDc0LTguMzU3eiIvPjxwYXRoIGZpbGw9IiMwMDM0NzgiIGQ9Ik0yMi4xNzggMTcuMjY0QTMgMyAwIDAgMCAxOCAxOGEzLjAwMSAzLjAwMSAwIDAgMS00LjkxNS0zLjQ0MiA2IDYgMCAxIDAgOS44MjkgNi44ODIgMi45OTcgMi45OTcgMCAwIDAtLjczNi00LjE3NnoiLz48cGF0aCBmaWxsPSIjMjkyRjMzIiBkPSJtMjQuMzM0IDI1LjU3MiAxLjkyOC0yLjI5OC43NjYuNjQzLTEuOTI4IDIuMjk4em0yLjU3LTMuMDYzIDEuOTI4LTIuMjk3Ljc2Ni42NDMtMS45MjggMi4yOTd6bS0xLjAzOCA0LjM1MSAxLjkyOC0yLjI5Ny43NjYuNjQzLTEuOTI4IDIuMjk3em0yLjU3Mi0zLjA2NiAxLjkzLTIuMjk3Ljc2Ni42NDQtMS45MyAyLjI5NnptLTEuMDQxIDQuMzUyIDEuOTMtMi4yOTcuNzY1LjY0My0xLjkyOSAyLjI5N3ptMi41NzEtMy4wNjUgMS45MjctMi4zLjc2Ny42NDMtMS45MjcgMi4zem0uMDA0LTE0LjE2Mi43NjYtLjY0MyAxLjkzIDIuMjk5LS43NjcuNjQzek0yNy40IDcuODUzbC43NjYtLjY0MyAxLjkyOCAyLjI5OS0uNzY3LjY0MnptLTEuNTMzIDEuMjg4Ljc2Ni0uNjQzIDQuNSA1LjM2Mi0uNzY2LjY0M3ptLTEuNTMyIDEuMjg0Ljc2Ny0uNjQzIDEuOTI3IDIuMjk4LS43NjYuNjQyem0yLjU3IDMuMDY1Ljc2Ni0uNjQzIDEuOTMgMi4yOTctLjc2NS42NDN6TTYuNCAyMC44NTRsLjc2Ni0uNjQzIDQuNDk5IDUuMzYzLS43NjcuNjQzek00Ljg3IDIyLjE0bC43NjUtLjY0MiAxLjkyOSAyLjI5OC0uNzY3LjY0M3ptMi41NjcgMy4wNjYuNzY2LS42NDMgMS45MyAyLjI5Ny0uNzY2LjY0M3ptLTQuMTAxLTEuNzgxLjc2Ni0uNjQzIDQuNSA1LjM2Mi0uNzY3LjY0M3ptLS4wMDEtMTAuODUyIDQuNDk4LTUuMzYyLjc2Ny42NDItNC41IDUuMzYzem0xLjUzMiAxLjI4NyA0LjUtNS4zNjMuNzY2LjY0My00LjUgNS4zNjJ6TTYuNCAxNS4xNDVsNC41LTUuMzYzLjc2Ni42NDMtNC41IDUuMzYzeiIvPjwvc3ZnPg==",
    "EN": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAzNiAzNiI+PHBhdGggZmlsbD0iI0IyMjMzNCIgZD0iTTM1LjQ0NSA3QzM0Ljc1MiA1LjgwOSAzMy40NzcgNSAzMiA1SDE4djJoMTcuNDQ1ek0wIDI1aDM2djJIMHptMTgtOGgxOHYySDE4em0wLTRoMTh2MkgxOHpNMCAyMWgzNnYySDB6bTQgMTBoMjhjMS40NzcgMCAyLjc1Mi0uODA5IDMuNDQ1LTJILjU1NWMuNjkzIDEuMTkxIDEuOTY4IDIgMy40NDUgMnpNMTggOWgxOHYySDE4eiIvPjxwYXRoIGZpbGw9IiNFRUUiIGQ9Ik0uMDY4IDI3LjY3OWMuMDE3LjA5My4wMzYuMTg2LjA1OS4yNzcuMDI2LjEwMS4wNTguMTk4LjA5Mi4yOTYuMDg5LjI1OS4xOTcuNTA5LjMzMy43NDNMLjU1NSAyOWgzNC44OWwuMDAyLS4wMDRhNC4yMiA0LjIyIDAgMCAwIC4zMzItLjc0MSAzLjc1IDMuNzUgMCAwIDAgLjE1Mi0uNTc2Yy4wNDEtLjIyLjA2OS0uNDQ2LjA2OS0uNjc5SDBjMCAuMjMzLjAyOC40NTguMDY4LjY3OXpNMCAyM2gzNnYySDB6bTAtNHYyaDM2di0ySDE4em0xOC00aDE4djJIMTh6bTAtNGgxOHYySDE4ek0wIDl6bS41NTUtMi0uMDAzLjAwNUwuNTU1IDd6TS4xMjggOC4wNDRjLjAyNS0uMTAyLjA2LS4xOTkuMDkyLS4yOTdhMy43OCAzLjc4IDAgMCAwLS4wOTIuMjk3ek0xOCA5aDE4YzAtLjIzMy0uMDI4LS40NTktLjA2OS0uNjhhMy42MDYgMy42MDYgMCAwIDAtLjE1My0uNTc2QTQuMjEgNC4yMSAwIDAgMCAzNS40NDUgN0gxOHYyeiIvPjxwYXRoIGZpbGw9IiMzQzNCNkUiIGQ9Ik0xOCA1SDRhNCA0IDAgMCAwLTQgNHYxMGgxOFY1eiIvPjxwYXRoIGZpbGw9IiNGRkYiIGQ9Im0yLjAwMSA3LjcyNi42MTguNDQ5LS4yMzYuNzI1TDMgOC40NTJsLjYxOC40NDgtLjIzNi0uNzI1TDQgNy43MjZoLS43NjRMMyA3bC0uMjM1LjcyNnptMiAyIC42MTguNDQ5LS4yMzYuNzI1LjYxNy0uNDQ4LjYxOC40NDgtLjIzNi0uNzI1TDYgOS43MjZoLS43NjRMNSA5bC0uMjM1LjcyNnptNCAwIC42MTguNDQ5LS4yMzYuNzI1LjYxNy0uNDQ4LjYxOC40NDgtLjIzNi0uNzI1LjYxOC0uNDQ5aC0uNzY0TDkgOWwtLjIzNS43MjZ6bTQgMCAuNjE4LjQ0OS0uMjM2LjcyNS42MTctLjQ0OC42MTguNDQ4LS4yMzYtLjcyNS42MTgtLjQ0OWgtLjc2NEwxMyA5bC0uMjM1LjcyNnptLTggNCAuNjE4LjQ0OS0uMjM2LjcyNS42MTctLjQ0OC42MTguNDQ4LS4yMzYtLjcyNS42MTgtLjQ0OWgtLjc2NEw1IDEzbC0uMjM1LjcyNnptNCAwIC42MTguNDQ5LS4yMzYuNzI1LjYxNy0uNDQ4LjYxOC40NDgtLjIzNi0uNzI1LjYxOC0uNDQ5aC0uNzY0TDkgMTNsLS4yMzUuNzI2em00IDAgLjYxOC40NDktLjIzNi43MjUuNjE3LS40NDguNjE4LjQ0OC0uMjM2LS43MjUuNjE4LS40NDloLS43NjRMMTMgMTNsLS4yMzUuNzI2em0tNi02IC42MTguNDQ5LS4yMzYuNzI1TDcgOC40NTJsLjYxOC40NDgtLjIzNi0uNzI1TDggNy43MjZoLS43NjRMNyA3bC0uMjM1LjcyNnptNCAwIC42MTguNDQ5LS4yMzYuNzI1LjYxNy0uNDQ4LjYxOC40NDgtLjIzNi0uNzI1LjYxOC0uNDQ5aC0uNzY0TDExIDdsLS4yMzUuNzI2em00IDAgLjYxOC40NDktLjIzNi43MjUuNjE3LS40NDguNjE4LjQ0OC0uMjM2LS43MjUuNjE4LS40NDloLS43NjRMMTUgN2wtLjIzNS43MjZ6bS0xMiA0IC42MTguNDQ5LS4yMzYuNzI1LjYxNy0uNDQ4LjYxOC40NDgtLjIzNi0uNzI1LjYxOC0uNDQ5aC0uNzY0TDMgMTFsLS4yMzUuNzI2ek02LjM4MyAxMi45IDcgMTIuNDUybC42MTguNDQ4LS4yMzYtLjcyNS42MTgtLjQ0OWgtLjc2NEw3IDExbC0uMjM1LjcyNmgtLjc2NGwuNjE4LjQ0OXptMy42MTgtMS4xNzQuNjE4LjQ0OS0uMjM2LjcyNS42MTctLjQ0OC42MTguNDQ4LS4yMzYtLjcyNS42MTgtLjQ0OWgtLjc2NEwxMSAxMWwtLjIzNS43MjZ6bTQgMCAuNjE4LjQ0OS0uMjM2LjcyNS42MTctLjQ0OC42MTguNDQ4LS4yMzYtLjcyNS42MTgtLjQ0OWgtLjc2NEwxNSAxMWwtLjIzNS43MjZ6bS0xMiA0IC42MTguNDQ5LS4yMzYuNzI1LjYxNy0uNDQ4LjYxOC40NDgtLjIzNi0uNzI1LjYxOC0uNDQ5aC0uNzY0TDMgMTVsLS4yMzUuNzI2ek02LjM4MyAxNi45IDcgMTYuNDUybC42MTguNDQ4LS4yMzYtLjcyNS42MTgtLjQ0OWgtLjc2NEw3IDE1bC0uMjM1LjcyNmgtLjc2NGwuNjE4LjQ0OXptMy42MTgtMS4xNzQuNjE4LjQ0OS0uMjM2LjcyNS42MTctLjQ0OC42MTguNDQ4LS4yMzYtLjcyNS42MTgtLjQ0OWgtLjc2NEwxMSAxNWwtLjIzNS43MjZ6bTQgMCAuNjE4LjQ0OS0uMjM2LjcyNS42MTctLjQ0OC42MTguNDQ4LS4yMzYtLjcyNS42MTgtLjQ0OWgtLjc2NEwxNSAxNWwtLjIzNS43MjZ6Ii8+PC9zdmc+",
    "VI": "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAzNiAzNiI+PHBhdGggZmlsbD0iI0RBMjUxRCIgZD0iTTMyIDVINGE0IDQgMCAwIDAtNCA0djE4YTQgNCAwIDAgMCA0IDRoMjhhNCA0IDAgMCAwIDQtNFY5YTQgNCAwIDAgMC00LTR6Ii8+PHBhdGggZmlsbD0iI0ZGMCIgZD0iTTE5Ljc1MyAxNi4wMzcgMTggMTAuNjQybC0xLjc1MyA1LjM5NWgtNS42NzJsNC41ODkgMy4zMzMtMS43NTMgNS4zOTVMMTggMjEuNDMxbDQuNTg5IDMuMzM0LTEuNzUzLTUuMzk1IDQuNTg5LTMuMzMzeiIvPjwvc3ZnPg==",
}

CSS = """
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css" />
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined" rel="stylesheet" />
<style>
:root { --navy: #1b489d; --navy-2: #2557b8; --navy-d: #133777; --soft: #e9eef8; --soft-2: #f3f6fc;
        --ink: #1d2433; --muted: #6b7487; --line: #e2e7f0; }
html, body, .stApp, .stApp button, .stApp input, .stApp textarea, .stApp select, .stApp p, .stApp li, .stApp label {
    font-family: 'Pretendard', -apple-system, 'Malgun Gothic', sans-serif !important;
}
.material-symbols-outlined { font-family: 'Material Symbols Rounded', 'Material Symbols Outlined' !important; font-weight: normal; font-style: normal;
    letter-spacing: normal; text-transform: none; white-space: nowrap; direction: ltr; font-feature-settings: 'liga'; -webkit-font-feature-settings: 'liga'; line-height: 1; vertical-align: middle; }
.stApp { background: #f4f6fa !important; }
[data-testid="stHeader"], #MainMenu, footer { display: none !important; }
[data-testid="collapsedControl"], [data-testid="stSidebarCollapseButton"], [data-testid="stSidebarHeader"] { display: none !important; height: 0 !important; margin: 0 !important; padding: 0 !important; }
.block-container { padding-top: 84px !important; padding-bottom: 3rem !important; padding-left: 1.75rem !important; padding-right: 1.75rem !important; max-width: none !important; }

/* ---------- 상단 바: 네이비 고정 바 ---------- */
.st-key-topbar {
    position: fixed !important; top: 0; left: 0; right: 0; height: 60px; z-index: 999990;
    background: linear-gradient(100deg, var(--navy) 0%, var(--navy-2) 100%);
    margin: 0 !important; padding: 0 20px !important; box-shadow: 0 4px 18px rgba(19,55,119,.28);
    display: flex; flex-direction: column; justify-content: center;
}
.st-key-topbar [data-testid="stHorizontalBlock"] { align-items: center; gap: 6px !important; }
.brand { display: flex; align-items: center; gap: 12px; color: #fff; white-space: nowrap; transform: translateY(-8px); }
.brand img { height: 38px; width: auto; max-width: 160px; object-fit: contain; }
.brand .mark { width: 36px; height: 36px; border-radius: 9px; background: rgba(255,255,255,.15); display: flex; align-items: center; justify-content: center; }
.brand .t1 { font-size: 21px; font-weight: 800; letter-spacing: -.3px; line-height: 1; color: #fff; }
.st-key-topbar button {
    background: transparent !important; color: rgba(255,255,255,.80) !important; border: 1px solid transparent !important;
    border-radius: 9px !important; font-weight: 600 !important; height: 36px !important; min-height: 36px !important; box-shadow: none !important;
}
.st-key-topbar button p { font-size: 13.5px !important; white-space: nowrap; }
.st-key-topbar button:hover { background: rgba(255,255,255,.12) !important; color: #fff !important; }
.stApp .st-key-topbar button[kind="primary"], .stApp .st-key-topbar button[data-testid="stBaseButton-primary"] {
    background: #fff !important; border-color: #fff !important; color: var(--navy) !important; font-weight: 700 !important; box-shadow: 0 2px 6px rgba(0,0,0,.12) !important;
}
/* 상단 바 언어 선택 */
.st-key-topbar [data-testid="stSelectbox"] [role="group"],
.st-key-topbar div[data-baseweb="select"] > div { background-color: rgba(255,255,255,.12) !important; border-color: transparent !important; border-radius: 9px !important; }
.st-key-topbar [data-testid="stSelectbox"] [role="group"]:hover,
.st-key-topbar div[data-baseweb="select"]:hover > div { background-color: rgba(255,255,255,.20) !important; }
.st-key-topbar [data-testid="stSelectbox"] input, .st-key-topbar div[data-baseweb="select"] * { color: #fff !important; font-weight: 600 !important; font-size: 13.5px !important; }
.st-key-topbar [data-testid="stSelectbox"] svg { fill: #fff !important; color: #fff !important; }
.st-key-lang_dropdown div[data-baseweb="select"] > div:first-child,
.st-key-lang_dropdown [data-testid="stSelectbox"] > div > div[role="group"] {
    background-image: url("data:image/svg+xml;base64,__FLAG_NOW__") !important; background-repeat: no-repeat !important;
    background-position: 10px center !important; background-size: 20px 20px !important; padding-left: 36px !important;
}

/* ---------- 사이드바 ---------- */
[data-testid="stSidebar"] { background: #fff !important; border-right: 1px solid var(--line) !important; z-index: 999980; }
[data-testid="stSidebarUserContent"] { padding-top: 80px !important; }
.step { display: flex; align-items: center; gap: 9px; margin: 14px 0 8px 0; font-weight: 800; color: var(--ink); font-size: 15px; }
.step .n { width: 22px; height: 22px; border-radius: 7px; background: var(--navy); color: #fff; font-size: 12px; display: flex; align-items: center; justify-content: center; font-weight: 800; flex: none; }
.step .opt { margin-left: auto; font-weight: 600; color: var(--navy); font-size: 11.5px; background: var(--soft); border-radius: 999px; padding: 2px 9px; }
[data-testid="stSidebar"] hr { margin: 14px 0 6px !important; border-color: var(--line) !important; }
[data-testid="stSidebar"] [data-testid="stCheckbox"] label p { font-size: 13px !important; }
[data-testid="stSidebar"] [data-testid="stSlider"] label p { font-size: 13px !important; font-weight: 600; color: var(--ink); }
.side-foot { text-align: center; color: #9aa3b2; font-size: 12px; margin-top: 26px; }

/* ---------- 메인 공통 ---------- */
.page-title { font-size: 24px; font-weight: 800; color: var(--ink); letter-spacing: -.5px; margin: 0; display: flex; align-items: center; gap: 10px; }
.page-title .material-symbols-outlined { color: #fff; background: var(--navy); border-radius: 10px; padding: 6px; font-size: 22px; }
.page-sub { color: var(--muted); font-size: 13.5px; margin: 6px 0 16px 0; }
[class*="st-key-card"] { background: #fff; border: 1px solid var(--line) !important; border-radius: 14px; padding: 18px 20px !important;
    box-shadow: 0 1px 2px rgba(16,24,40,.04), 0 4px 14px rgba(16,24,40,.04); margin-bottom: 14px; }
.sec-t { display: flex; align-items: center; gap: 8px; font-size: 16px; font-weight: 800; color: var(--ink); margin: 0 0 4px; letter-spacing: -.2px; }
.sec-t .material-symbols-outlined { color: var(--navy); font-size: 20px; }
.sec-t .badge { margin-left: 4px; background: var(--navy); color: #fff; font-size: 12px; border-radius: 999px; padding: 2px 10px; font-weight: 700; }
.sec-s { color: var(--muted); font-size: 12.5px; margin: 0 0 10px; }
.sub-t { font-size: 13px; font-weight: 800; color: var(--ink); margin: 14px 0 6px; display: flex; align-items: center; gap: 6px; }
.sub-t .material-symbols-outlined { font-size: 17px; color: var(--navy); }
.fchips { display: flex; flex-wrap: wrap; gap: 6px; margin: 0 0 14px; align-items: center; }
.fchips .lbl { font-size: 12px; font-weight: 700; color: var(--muted); margin-right: 2px; }
.fchip { display: inline-flex; align-items: center; gap: 4px; padding: 3px 10px; border-radius: 999px; background: #fff; border: 1px solid var(--line);
    font-size: 12.5px; color: var(--ink); font-weight: 600; }
.fchip b { color: var(--navy); }
.fchip.grp { background: var(--soft); border-color: #c9d6ee; color: var(--navy); }
.fchip.none { color: var(--muted); border-style: dashed; }
.selchips { display: flex; flex-wrap: wrap; gap: 8px; margin: 2px 0 6px; }
.selchip { display: inline-flex; align-items: center; gap: 8px; padding: 6px 12px; border-radius: 10px; background: var(--soft-2);
    border: 1px solid var(--line); font-size: 13.5px; font-weight: 700; color: var(--ink); }
.selchip i { width: 22px; height: 4px; border-radius: 4px; display: inline-block; }
.hint { font-size: 12.5px; color: var(--muted); display: flex; align-items: center; gap: 6px; margin: 4px 0 8px; }
.hint .material-symbols-outlined { font-size: 16px; color: var(--navy); }
/* 진단 카드 */
.verdict { display: flex; gap: 14px; align-items: center; padding: 14px 16px; border-radius: 12px; margin-top: 4px; }
.verdict .ic { width: 42px; height: 42px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex: none; }
.verdict .ic .material-symbols-outlined { font-size: 26px; color: #fff; }
.verdict .tt { font-size: 15.5px; font-weight: 800; }
.verdict .ds { font-size: 13px; margin-top: 2px; }
.verdict .dev { margin-left: auto; text-align: right; font-size: 11.5px; font-weight: 600; opacity: .85; white-space: nowrap; }
.verdict .dev b { display: block; font-size: 20px; font-weight: 800; font-variant-numeric: tabular-nums; }
.verdict.ok { background: #e6f4ec; color: #14532d; } .verdict.ok .ic { background: #167a4a; }
.verdict.warn { background: #fff4e0; color: #6b3d00; } .verdict.warn .ic { background: #d97706; }
.verdict.bad { background: #fdecea; color: #7f1d1d; } .verdict.bad .ic { background: #b42318; }
/* 빈 화면 */
.empty { text-align: center; padding: 36px 16px 30px; }
.empty .eic { width: 60px; height: 60px; border-radius: 18px; background: var(--soft); display: inline-flex; align-items: center; justify-content: center; }
.empty .eic .material-symbols-outlined { font-size: 32px; color: var(--navy); }
.empty b { display: block; font-size: 16px; color: var(--ink); margin-top: 12px; }
.empty p { color: var(--muted); font-size: 13.5px; margin: 6px 0 0; white-space: pre-line; }

/* ---------- 위젯 ---------- */
.stApp button[kind="primary"], .stApp button[data-testid="stBaseButton-primary"] { background: var(--navy) !important; border-color: var(--navy) !important; color: #fff !important; border-radius: 10px !important; font-weight: 700 !important; }
.stApp [data-testid="stSidebar"] button { border-radius: 10px !important; }
.stApp [data-testid="stDataFrame"] { border-radius: 12px !important; overflow: hidden; border: 1px solid var(--line) !important; }
.stApp [data-testid="stAlert"] { border-radius: 12px !important; }
.stApp [data-baseweb="input"], .stApp [data-baseweb="base-input"], .stApp div[data-baseweb="select"] > div, .stApp [data-testid="stSelectbox"] [role="group"] { border-radius: 9px !important; }
.stApp [data-testid="stSlider"] [role="slider"] { background-color: var(--navy) !important; border-color: var(--navy) !important; box-shadow: 0 0 0 3px rgba(27,72,157,.15) !important; }
.stApp [data-testid="stSliderThumbValue"], .stApp [data-testid="stThumbValue"] { color: var(--navy) !important; font-weight: 800 !important; }
.stApp [data-testid="stCheckbox"] label:has(input:checked) span:first-child,
.stApp [data-baseweb="checkbox"] input:checked + div, .stApp [data-baseweb="checkbox"] span[aria-checked="true"] { background-color: var(--navy) !important; border-color: var(--navy) !important; }
.stApp [data-baseweb="tag"] { background-color: var(--navy) !important; border-radius: 7px !important; }
</style>
"""
CSS = CSS.replace("__FLAG_NOW__", LANG_FLAG_SVG_B64.get(lang, LANG_FLAG_SVG_B64["EN"]))
import re as _re
CSS = "\n".join(l for l in _re.sub(r"/\*.*?\*/", "", CSS, flags=_re.S).splitlines() if l.strip())   # 빈 줄이 있으면 CSS가 글자로 찍힘
st.markdown(CSS, unsafe_allow_html=True)


def icon(name):
    return f"<span class='material-symbols-outlined'>{name}</span>"

def page_head(ic, title, sub):
    st.markdown(f"<div class='page-title'>{icon(ic)}{title}</div><div class='page-sub'>{sub}</div>", unsafe_allow_html=True)

def sec_head(ic, title, badge=None, sub=None):
    b = f"<span class='badge'>{badge}</span>" if badge is not None else ""
    s = f"<div class='sec-s'>{sub}</div>" if sub else ""
    st.markdown(f"<div class='sec-t'>{icon(ic)}{title}{b}</div>{s}", unsafe_allow_html=True)

def sub_head(ic, title):
    st.markdown(f"<div class='sub-t'>{icon(ic)}{title}</div>", unsafe_allow_html=True)

def side_step(n, title, opt=""):
    o = f"<span class='opt'>{opt}</span>" if opt else ""
    st.sidebar.markdown(f"<div class='step'><span class='n'>{n}</span>{title}{o}</div>", unsafe_allow_html=True)

def empty_box(ic, title, desc):
    st.markdown(f"<div class='empty'><div class='eic'>{icon(ic)}</div><b>{title}</b><p>{html_lib.escape(desc.replace('**', ''))}</p></div>", unsafe_allow_html=True)

def filter_chips(groups, req, rep_col, rep_min, rep_label):
    """적용 중인 조건(그룹 · 최소 등급)을 칩으로 보여 줍니다"""
    chips = "".join(f"<span class='fchip grp'>{html_lib.escape(str(g))}</span>" for g in groups)
    active = [(c, v) for c, v in req.items() if v > 1.0]
    chips += "".join(f"<span class='fchip'>{t[lang][criteria_map.get(c, c)]} <b>≥ {v:g}</b></span>" for c, v in active)
    if rep_col and rep_min is not None:
        chips += f"<span class='fchip'>{html_lib.escape(rep_label)} <b>≥ {rep_min:g}</b></span>"
    if not active and not rep_col:
        chips += f"<span class='fchip none'>{t[lang]['no_filters']}</span>"
    st.markdown(f"<div class='fchips'><span class='lbl'>{t[lang]['active_filters']}</span>{chips}</div>", unsafe_allow_html=True)

def diagnosis(max_dev):
    """기존 판정 기준 그대로 (5 미만 우수 / 12 미만 주의 / 그 이상 위험)"""
    if max_dev < 5: cls, ic, key = "ok", "check_circle", "diag_excel"
    elif max_dev < 12: cls, ic, key = "warn", "warning", "diag_warn"
    else: cls, ic, key = "bad", "dangerous", "diag_danger"
    head, _, body = t[lang][key].partition("\n\n")
    st.markdown(f"<div class='verdict {cls}'><div class='ic'>{icon(ic)}</div><div><div class='tt'>{head.replace('**', '')}</div>"
                f"<div class='ds'>{html_lib.escape(body)}</div></div><div class='dev'>{t[lang]['diag_dev']}<b>{max_dev:.1f}%</b></div></div>", unsafe_allow_html=True)

def style_fig(fig):
    fig.update_layout(font=dict(family="Pretendard, Malgun Gothic, sans-serif", color="#1d2433", size=12), plot_bgcolor="white", paper_bgcolor="white",
                      hoverlabel=dict(bgcolor="white", bordercolor="#e2e7f0"), height=440)
    fig.update_xaxes(showgrid=True, gridcolor="#eef1f6", linecolor="#e2e7f0")
    fig.update_yaxes(showgrid=True, gridcolor="#eef1f6", linecolor="#e2e7f0", zeroline=False)
    return fig


# ==========================================
# 4. 상단 메뉴 바 (로고 · 프로그램 선택 · 언어)
# ==========================================
with st.container(key="topbar"):
    c_brand, c_nav, c_gap, c_lang = st.columns([1.55, 3.6, 1.2, 0.75], vertical_alignment="center")
    with c_brand:
        logo_html = (f"<img src='data:image/png;base64,{header_logo_base64}'>" if header_logo_base64
                     else f"<div class='mark'>{icon('science')}</div>")
        st.markdown(f"<div class='brand'>{logo_html}<div class='t1'>{t[lang]['header']}</div></div>", unsafe_allow_html=True)
    with c_nav:
        n1, n2, n3 = st.columns([1, 0.85, 1.25])
        n1.button(t[lang]["nav1"], icon=":material/manage_search:", use_container_width=True, key="nav_tab1",
                  type="primary" if st.session_state.app_mode == "tab1" else "secondary", on_click=set_app_mode, args=("tab1",))
        n2.button(t[lang]["nav2"], icon=":material/monitoring:", use_container_width=True, key="nav_tab2",
                  type="primary" if st.session_state.app_mode == "tab2" else "secondary", on_click=set_app_mode, args=("tab2",))
        n3.button(t[lang]["nav3"], icon=":material/join_inner:", use_container_width=True, key="nav_tab3",
                  type="primary" if st.session_state.app_mode == "tab3" else "secondary", on_click=set_app_mode, args=("tab3",))
    with c_lang:
        st.selectbox("Language", ["ENG", "KOR"], index=0 if lang == "EN" else 1, label_visibility="collapsed",
                     key="lang_dropdown", on_change=on_lang_change)

criteria_map = {'일광': 'crit_light', '땀일광(산성)': 'crit_p_light_acid', '땀일광(알칼리)': 'crit_p_light_alk',
                '땀(산성)': 'crit_p_acid', '땀(알칼리)': 'crit_p_alk', '세탁': 'crit_wash', '염소수': 'crit_chlor'}
criteria_list = ['일광', '땀일광(산성)', '땀일광(알칼리)', '땀(산성)', '땀(알칼리)', '세탁', '염소수']


def sidebar_filters(df, mode):
    """사이드바: ① 염료 그룹 ② 요구 견뢰도 ③ 반복세탁 (탭1·탭3 공통, 위젯 key는 기존과 동일)"""
    all_groups = list(df['염료그룹'].dropna().unique()) if '염료그룹' in df.columns else []
    for g in all_groups:
        if f"grp_{g}_{mode}" not in st.session_state:
            st.session_state[f"grp_{g}_{mode}"] = True if g == "Sunfix SPD conc." else False
    n_on = sum(1 for g in all_groups if st.session_state.get(f"grp_{g}_{mode}"))
    side_step(1, t[lang]["sb_group_short"], f"{n_on} / {len(all_groups)}")
    st.sidebar.checkbox(t[lang]["select_all"], value=False, key=f"chk_all_{mode}",
                        on_change=toggle_all_groups, args=(mode, all_groups))
    sc1, sc2 = st.sidebar.columns(2)
    selected_groups = []
    for i, group in enumerate(all_groups):
        target_col = sc1 if i % 2 == 0 else sc2
        if target_col.checkbox(str(group), key=f"grp_{group}_{mode}"):
            selected_groups.append(group)

    st.sidebar.markdown("---")
    side_step(2, t[lang]["sb_spec_short"])
    req = {}
    for c in criteria_list:
        if c in df.columns:
            display_label = t[lang][criteria_map.get(c, c)]
            max_val = 7.0 if c == '일광' else 5.0
            req[c] = st.sidebar.slider(display_label, 1.0, max_val, 1.0, 0.5, key=f"sld_{c}_{mode}")

    st.sidebar.markdown("---")
    side_step(3, t[lang]["rep_wash_title"])
    cycles_list = cycle_opts_en if lang == "EN" else cycle_opts_ko
    sel_cycle = st.sidebar.selectbox(t[lang]["rep_wash_times_label"], cycles_list, key=f"sel_rep_wash_{mode}")
    rep_wash_min, rep_wash_col = None, None
    if sel_cycle != t[lang]["rep_wash_none"]:
        rep_wash_min = st.sidebar.slider(t[lang]["rep_wash_grade_label"], 1.0, 5.0, 1.0, 0.5, key=f"sld_rep_wash_{mode}")
        rep_wash_col = get_excel_cycle_string(sel_cycle, lang)
    return selected_groups, req, sel_cycle, rep_wash_min, rep_wash_col


def apply_filters(df, selected_groups, req, rep_wash_col, rep_wash_min):
    """기존 필터 로직 그대로"""
    f_df = df[df['염료그룹'].isin(selected_groups)].copy()
    for c, min_val in req.items():
        if c in f_df.columns:
            f_df[c] = pd.to_numeric(f_df[c], errors='coerce')
            f_df = f_df[f_df[c] >= min_val]
    if rep_wash_col and rep_wash_col in f_df.columns:
        f_df[rep_wash_col] = pd.to_numeric(f_df[rep_wash_col], errors='coerce')
        f_df = f_df[f_df[rep_wash_col] >= rep_wash_min]
    return f_df


def rep_label(sel_cycle):
    return f"Rep.Wash ({sel_cycle.split()[0]})" if lang == "EN" else f"반복세탁 ({sel_cycle})"


# =====================================================================
# [App 1] 요구견뢰도 스펙 매칭 전용
# =====================================================================
if st.session_state.app_mode == "tab1":
    @st.cache_data
    def load_spec_data():
        if not os.path.exists("integrated_dyes_data.xlsx"): return None
        df = pd.read_excel("integrated_dyes_data.xlsx")
        df.columns = [str(col).strip() for col in df.columns]
        return df

    page_head("manage_search", t[lang]["nav1"], t[lang]["page1_sub"])
    df1 = load_spec_data()
    if df1 is None:
        st.error("`integrated_dyes_data.xlsx` 파일이 없습니다.", icon=":material/error:")
    else:
        selected_groups1, req1, sel_cycle1, rep_wash_min1, rep_wash_col1 = sidebar_filters(df1, "tab1")

        if not selected_groups1:
            st.warning(t[lang]["spec_warn"], icon=":material/warning:")
        else:
            f_df1 = apply_filters(df1, selected_groups1, req1, rep_wash_col1, rep_wash_min1)
            filter_chips(selected_groups1, req1, rep_wash_col1, rep_wash_min1, rep_label(sel_cycle1))

            disp_cols1 = ['염료명'] + [c for c in criteria_list if c in f_df1.columns]
            col_configs1 = {"염료명": st.column_config.TextColumn(label=t[lang]["col_name"])}
            for c in disp_cols1[1:]:
                col_configs1[c] = st.column_config.NumberColumn(label=t[lang][criteria_map.get(c, c)])
            if rep_wash_col1 and rep_wash_col1 in f_df1.columns:
                disp_cols1.append(rep_wash_col1)
                col_configs1[rep_wash_col1] = st.column_config.NumberColumn(label=rep_label(sel_cycle1))

            with st.container(key="card_res1"):
                sec_head("checklist", t[lang]["res_title"], badge=len(f_df1))
                if len(f_df1) == 0:
                    empty_box("search_off", t[lang]["no_match"], t[lang]["instruction_text"])
                else:
                    st.dataframe(f_df1[disp_cols1], hide_index=True, use_container_width=True, column_config=col_configs1,
                                 height=min(38 + 35 * len(f_df1), 640))


# =====================================================================
# [App 2] 상용성 그래프 단독
# =====================================================================
elif st.session_state.app_mode == "tab2":
    @st.cache_data
    def parse_dye_data(file):
        xls = pd.ExcelFile(file)
        parsed_sheets = {}
        target_sheets = [s for s in xls.sheet_names if s not in ['그래프', 'SREF', 'H-E SREF']]
        for sheet in target_sheets:
            df = pd.read_excel(xls, sheet_name=sheet, header=None)
            df = df.dropna(how='all')
            header_idx = None
            for idx, row in df.iterrows():
                row_vals = [str(x).strip().split('.')[0] for x in row.values if pd.notna(x)]
                if '0' in row_vals and '5' in row_vals and '20' in row_vals:
                    header_idx = idx
                    break
            if header_idx is None: continue
            header_row = df.iloc[header_idx]
            time_mapping = {}
            for c_idx, val in enumerate(header_row):
                v_str = str(val).strip().split('.')[0]
                if v_str in ['0', '5', '20', '25', '40', '80', '100']: time_mapping[int(v_str)] = c_idx
            sorted_times = sorted(time_mapping.keys())
            dye_list = []
            for idx in range(header_idx + 1, len(df)):
                row = df.iloc[idx]
                dye_name = row.iloc[1]
                if pd.isna(dye_name) or str(dye_name).strip() in ['', 'None', 'Dyes', '염료', 'No.']: continue
                try:
                    y_vals = [float(row.iloc[time_mapping[t]]) for t in sorted_times]
                    dye_list.append({"name": str(dye_name).strip(), "times": sorted_times, "values": y_vals})
                except: continue
            if dye_list: parsed_sheets[sheet] = dye_list
        return parsed_sheets

    page_head("monitoring", t[lang]["nav2"], t[lang]["page2_sub"])
    file_to_read = "반응성 염료 상용성 실험.xlsx"
    if not os.path.exists(file_to_read):
        st.error(f"`{file_to_read}` 파일이 없습니다.", icon=":material/error:")
        app2_data = None
    else:
        try:
            app2_data = parse_dye_data(file_to_read)
        except Exception as e:
            st.error(f"데이터 파싱 오류: {e}", icon=":material/error:")
            app2_data = None

    if app2_data:
        side_step(1, t[lang]["sb_dye_select"])
        selected_dyes2 = []
        for sheet_name, dyes in app2_data.items():
            dye_names = [d["name"] for d in dyes]
            selections = st.sidebar.multiselect(f":material/list: {sheet_name}", options=dye_names, key=f"tab2_ms_{sheet_name}")
            for sel in selections:
                for d in dyes:
                    if d["name"] == sel: selected_dyes2.append((sheet_name, d))

        custom_colors2 = ['#FFD700', '#FF4B4B', '#1F77B4', '#9467bd', '#2ca02c', '#ff7f0e', '#e377c2']
        with st.container(key="card_sim2"):
            sec_head("monitoring", t[lang]["sim_title"], badge=len(selected_dyes2) if selected_dyes2 else None)
            if not selected_dyes2:
                empty_box("touch_app", t[lang]["empty_title"], t[lang]["select_prompt_tab3"])
            else:
                st.markdown("<div class='selchips'>" + "".join(
                    f"<span class='selchip'><i style='background:{custom_colors2[i % len(custom_colors2)]}'></i>{html_lib.escape(d['name'])}</span>"
                    for i, (_, d) in enumerate(selected_dyes2)) + "</div>", unsafe_allow_html=True)

                if len(selected_dyes2) >= 2:
                    all_matrix = np.array([d["values"] for _, d in selected_dyes2])
                    std_per_time = np.std(all_matrix, axis=0)
                    max_dev = np.max(std_per_time)
                    diagnosis(max_dev)

                fig2 = go.Figure()
                for idx, (sheet_name, dye) in enumerate(selected_dyes2):
                    color = custom_colors2[idx % len(custom_colors2)]
                    label = f"{dye['name']}"
                    x1 = [t_val for t_val in dye["times"] if t_val <= 20]
                    y1 = [v for t_val, v in zip(dye["times"], dye["values"]) if t_val <= 20]
                    x2 = [t_val for t_val in dye["times"] if t_val >= 25]
                    y2 = [v for t_val, v in zip(dye["times"], dye["values"]) if t_val >= 25]
                    fig2.add_trace(go.Scatter(x=x1, y=y1, mode='lines', name=label, legendgroup=label, line=dict(width=3, color=color, shape='spline'), hovertemplate='%{x}' + f"{t[lang]['minute_unit']}: " + '<b>%{y}%</b><extra></extra>'))
                    fig2.add_trace(go.Scatter(x=x2, y=y2, mode='lines', name=label, legendgroup=label, showlegend=False, line=dict(width=3, color=color, shape='spline'), hovertemplate='%{x}' + f"{t[lang]['minute_unit']}: " + '<b>%{y}%</b><extra></extra>'))
                fig2.update_layout(
                    xaxis_title=t[lang]["xaxis"], yaxis_title=t[lang]["yaxis"],
                    xaxis=dict(tickmode='array', tickvals=[0, 5, 20, 25, 40, 80, 100]),
                    yaxis=dict(range=[0, 105]), hovermode="x unified", margin=dict(l=40, r=40, t=20, b=40),
                    legend=dict(orientation="v", yanchor="bottom", y=0.05, xanchor="right", x=0.99, font=dict(size=14), bgcolor="rgba(255, 255, 255, 0.85)", bordercolor="#e2e7f0", borderwidth=1)
                )
                fig2.add_vline(x=20, line_dash="dash", line_color="gray")
                fig2.add_vline(x=25, line_dash="dash", line_color="gray")
                st.plotly_chart(style_fig(fig2), use_container_width=True)


# =====================================================================
# [App 3] 통합 매칭 및 시뮬레이션
# =====================================================================
elif st.session_state.app_mode == "tab3":
    @st.cache_data
    def load_integrated_data():
        if not os.path.exists("integrated_dyes_data.xlsx"): return None
        df = pd.read_excel("integrated_dyes_data.xlsx")
        df.columns = [str(col).strip() for col in df.columns]
        return df

    page_head("join_inner", t[lang]["nav3"], t[lang]["page3_sub"])
    df3 = load_integrated_data()
    if df3 is None:
        st.error("`integrated_dyes_data.xlsx` 파일이 없습니다.", icon=":material/error:")
    else:
        selected_groups3, req3, sel_cycle3, rep_wash_min3, rep_wash_col3 = sidebar_filters(df3, "tab3")

        if not selected_groups3:
            st.warning(t[lang]["spec_warn"], icon=":material/warning:")
        else:
            f_df3 = apply_filters(df3, selected_groups3, req3, rep_wash_col3, rep_wash_min3)
            filter_chips(selected_groups3, req3, rep_wash_col3, rep_wash_min3, rep_label(sel_cycle3))

            f_df3.insert(0, '선택', False)
            disp_cols3 = ['선택', '염료명'] + [c for c in criteria_list if c in f_df3.columns]
            col_configs3 = {
                "선택": st.column_config.CheckboxColumn(label=t[lang]["col_select"], width="small"),
                "염료명": st.column_config.TextColumn(label=t[lang]["col_name"], width=150)
            }
            for c in disp_cols3[2:]:
                col_configs3[c] = st.column_config.NumberColumn(label=t[lang][criteria_map.get(c, c)], width=80)
            if rep_wash_col3 and rep_wash_col3 in f_df3.columns:
                disp_cols3.append(rep_wash_col3)
                col_configs3[rep_wash_col3] = st.column_config.NumberColumn(label=rep_label(sel_cycle3), width=100)

            if "tab3_selected_order" not in st.session_state:
                st.session_state.tab3_selected_order = []

            # ---------- 카드 1: 검색 결과 ----------
            with st.container(key="card_res3"):
                sec_head("checklist", t[lang]["res_title"], badge=len(f_df3))
                st.markdown(f"<div class='hint'>{icon('touch_app')}{t[lang]['res_hint']}</div>", unsafe_allow_html=True)
                btn_container = st.empty()
                edited_df3 = st.data_editor(
                    f_df3[disp_cols3], hide_index=True, use_container_width=True,
                    column_config=col_configs3, disabled=[col for col in disp_cols3 if col != '선택'], key="tab3_editor"
                )

            curr_checked3 = edited_df3[edited_df3['선택'] == True]['염료명'].tolist()
            st.session_state.tab3_selected_order = [d for d in st.session_state.tab3_selected_order if d in curr_checked3]
            for d in curr_checked3:
                if d not in st.session_state.tab3_selected_order:
                    st.session_state.tab3_selected_order.append(d)

            all_filtered_dyes = f_df3['염료명'].tolist()
            all_dyes_str = ",".join(all_filtered_dyes)
            sel_dyes_str = ",".join(curr_checked3)

            all_btn_text = "Copy All Dyes" if lang == "EN" else "검색된 전체 염료명 복사하기"
            sel_btn_text = "Copy Selected Dyes" if lang == "EN" else "선택된 염료명 복사하기"
            success_text = "Copied!" if lang == "EN" else "복사 완료!"
            alert_text = "No dyes selected." if lang == "EN" else "표에서 먼저 염료를 선택해주세요."

            button_html = f"""
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css" />
            <style>
                body {{ margin: 0; font-family: 'Pretendard', 'Malgun Gothic', sans-serif; }}
                .cbtn {{ flex: 1; padding: 9px 16px; font-size: 14px; font-weight: 700; border-radius: 10px; cursor: pointer; transition: .2s;
                         display: flex; align-items: center; justify-content: center; gap: 8px; font-family: inherit; }}
                #copy-sel-btn {{ background: {NAVY}; color: #fff; border: 1px solid {NAVY}; }}
                #copy-sel-btn:hover {{ background: #133777; }}
                #copy-all-btn {{ background: #fff; color: #1d2433; border: 1px solid #e2e7f0; }}
                #copy-all-btn:hover {{ border-color: {NAVY}; color: {NAVY}; background: #f3f6fc; }}
            </style>
            <div style="display: flex; gap: 10px; width: 100%; margin-bottom: 6px;">
                <button class="cbtn" id="copy-sel-btn" onclick="copySelected()">
                    <svg class="ic" xmlns="http://www.w3.org/2000/svg" height="19" width="19" viewBox="0 -960 960 960" fill="currentColor"><path d="M222-200 80-342l56-56 85 85 170-170 56 57-225 226Zm0-320L80-662l56-56 85 85 170-170 56 57-225 226Zm298 240v-80h360v80H520Zm0-320v-80h360v80H520Z"/></svg>
                    <span id="sel-btn-text">{sel_btn_text}</span>
                </button>
                <button class="cbtn" id="copy-all-btn" onclick="copyAll()">
                    <svg class="ic" xmlns="http://www.w3.org/2000/svg" height="19" width="19" viewBox="0 -960 960 960" fill="currentColor"><path d="M360-240q-33 0-56.5-23.5T280-320v-480q0-33 23.5-56.5T360-880h360q33 0 56.5 23.5T800-800v480q0 33-23.5 56.5T720-240H360Zm0-80h360v-480H360v480ZM200-80q-33 0-56.5-23.5T120-160v-560h80v560h440v80H200Z"/></svg>
                    <span id="all-btn-text">{all_btn_text}</span>
                </button>
            </div>
            <script>
                function copyToClip(text, btnId, textId, origText) {{
                    if (!text) {{ alert("{alert_text}"); return; }}
                    navigator.clipboard.writeText(text).then(() => {{
                        const btn = document.getElementById(btnId);
                        const btnText = document.getElementById(textId);
                        const icon = btn.querySelector('.ic');
                        const origBg = btn.style.backgroundColor;
                        const origColor = btn.style.color;
                        const origBorder = btn.style.border;
                        const origIcon = icon.innerHTML;

                        btn.style.backgroundColor = '#167a4a'; btn.style.color = 'white'; btn.style.border = '1px solid #167a4a';
                        icon.innerHTML = '<path d="M382-240 154-468l57-57 171 171 367-367 57 57-424 424Z"/>'; btnText.innerText = "{success_text}";
                        setTimeout(() => {{
                            btn.style.backgroundColor = origBg; btn.style.color = origColor; btn.style.border = origBorder;
                            icon.innerHTML = origIcon; btnText.innerText = origText;
                        }}, 2000);
                    }});
                }}
                function copySelected() {{ copyToClip("{sel_dyes_str}", "copy-sel-btn", "sel-btn-text", "{sel_btn_text}"); }}
                function copyAll() {{ copyToClip("{all_dyes_str}", "copy-all-btn", "all-btn-text", "{all_btn_text}"); }}
            </script>
            """
            with btn_container:
                components.html(button_html, height=50)

            # === 선택된 염료 3개를 A열(색순서) 기준으로 정렬 (기존 로직 그대로) ===
            sel_dyes3_click_order = st.session_state.tab3_selected_order[:3]
            sort_col = df3.columns[0]
            df3[sort_col] = pd.to_numeric(df3[sort_col], errors='coerce')
            sorted_sel_df = df3[df3['염료명'].isin(sel_dyes3_click_order)].sort_values(by=sort_col)
            sel_dyes3 = sorted_sel_df['염료명'].tolist()
            colors = ['#FFD700', '#FF4B4B', '#1F77B4']  # Yellow, Red, Blue 순서 보장됨

            # ---------- 카드 2: 상용성 시뮬레이션 ----------
            with st.container(key="card_sim3"):
                sec_head("monitoring", t[lang]["sim_title"], badge=len(sel_dyes3) if sel_dyes3 else None)
                if len(curr_checked3) > 3: st.warning(t[lang]["warn_limit"], icon=":material/warning:")

                if not sel_dyes3:
                    empty_box("touch_app", t[lang]["empty_sel_title"], t[lang]["select_prompt"])
                else:
                    st.markdown("<div class='selchips'>" + "".join(
                        f"<span class='selchip'><i style='background:{colors[i % len(colors)]}'></i>{html_lib.escape(str(n))}</span>"
                        for i, n in enumerate(sel_dyes3)) + "</div>", unsafe_allow_html=True)

                    time_pts3 = ['0', '5', '20', '25', '40', '80', '100']
                    val_cols3 = [tc for tc in time_pts3 if tc in df3.columns]

                    if len(sel_dyes3) >= 2 and len(val_cols3) >= 2:
                        all_matrix = np.array([[df3[df3['염료명'] == name].iloc[0][tc] for tc in val_cols3] for name in sel_dyes3], dtype=float)
                        std_per_time = np.nanstd(all_matrix, axis=0)
                        max_dev = np.nanmax(std_per_time)
                        diagnosis(max_dev)

                    if len(val_cols3) < 2:
                        st.warning(t[lang]["err_time_data"], icon=":material/warning:")
                    else:
                        fig3 = go.Figure()
                        for idx, name in enumerate(sel_dyes3):
                            row = df3[df3['염료명'] == name].iloc[0]
                            color = colors[idx % len(colors)]
                            label = f"{name}"
                            t_p1 = [tc for tc in val_cols3 if int(tc) <= 20]
                            v_p1 = [row[tc] for tc in t_p1]
                            t_p2 = [tc for tc in val_cols3 if int(tc) >= 25]
                            v_p2 = [row[tc] for tc in t_p2]
                            fig3.add_trace(go.Scatter(x=t_p1, y=v_p1, mode='lines', name=label, legendgroup=label, line=dict(width=3, color=color, shape='spline'), hovertemplate='%{x}' + f"{t[lang]['minute_unit']}: " + '<b>%{y}%</b><extra></extra>'))
                            fig3.add_trace(go.Scatter(x=t_p2, y=v_p2, mode='lines', name=label, legendgroup=label, showlegend=False, line=dict(width=3, color=color, shape='spline'), hovertemplate='%{x}' + f"{t[lang]['minute_unit']}: " + '<b>%{y}%</b><extra></extra>'))
                        fig3.update_layout(
                            xaxis_title=t[lang]["xaxis"], yaxis_title=t[lang]["yaxis"],
                            xaxis=dict(tickmode='array', tickvals=[int(tc) for tc in val_cols3]),
                            yaxis=dict(range=[0, 105]), hovermode="x unified", margin=dict(l=40, r=40, t=20, b=40),
                            legend=dict(orientation="v", yanchor="bottom", y=0.05, xanchor="right", x=0.99, font=dict(size=14), bgcolor="rgba(255, 255, 255, 0.85)", bordercolor="#e2e7f0", borderwidth=1)
                        )
                        fig3.add_vline(x=20, line_dash="dash", line_color="gray")
                        fig3.add_vline(x=25, line_dash="dash", line_color="gray")
                        st.plotly_chart(style_fig(fig3), use_container_width=True)

                    # 선택 염료 견뢰도 요약
                    sub_head("fact_check", t[lang]["sel_summary_title"])
                    summary_disp_cols = ['염료명'] + [c for c in criteria_list if c in df3.columns]
                    if rep_wash_col3 and rep_wash_col3 in df3.columns:
                        summary_disp_cols.append(rep_wash_col3)
                    st.dataframe(sorted_sel_df[summary_disp_cols], hide_index=True, use_container_width=True, column_config=col_configs3)

# ==========================================
# 5. 최하단 공통 요소 (제작자 정보)
# ==========================================
st.sidebar.markdown(f"<div class='side-foot'>{t[lang]['created_by']}</div>", unsafe_allow_html=True)