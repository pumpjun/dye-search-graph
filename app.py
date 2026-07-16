import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
import base64

# ==========================================
# 0. 웹페이지 기본 설정
# ==========================================
st.set_page_config(page_title="Ohyoung Dye Finder", page_icon="logo.png", layout="wide")

# ==========================================
# 1. 공통 로그인 기능 구현
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, login_col, _ = st.columns([1, 2, 1])
    with login_col:
        login_logo_html = "🧪"
        if os.path.exists("logo.png"):
            with open("logo.png", "rb") as f:
                login_img_base64 = base64.b64encode(f.read()).decode()
            login_logo_html = f'<img src="data:image/png;base64,{login_img_base64}" width="45" style="vertical-align: middle; margin-right: 10px; margin-bottom: 5px;">'

        st.markdown(
            f"""
            <div style="background-color:#f9f9f9; padding: 2.5rem; border-radius: 12px; border: 1px solid #ddd; margin-top: 100px; box-shadow: 0px 4px 10px rgba(0,0,0,0.05);">
                <h2 style="text-align: center; margin-top: 0; margin-bottom: 20px; font-weight: 700; color: #1E3A8A;">
                    {login_logo_html}Ohyoung Dye Finder Login
                </h2>
                <p style="text-align: center; color: #666; font-size: 0.95rem; margin-bottom: 30px;">
                    Please log in to access the OHYOUNG Dye Matching System.<br>
                    오영 염료 통합 시스템 접근을 위해 로그인해 주세요.
                </p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        login_id = st.text_input("아이디 (Username / ID)", placeholder="Enter ID")
        login_pw = st.text_input("비밀번호 (Password)", type="password", placeholder="Enter Password")
        st.write("")
        
        if st.button("로그인 (Log In)", use_container_width=True, type="primary"):
            if login_id == "ohyoung" and login_pw == "5050":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("🚨 아이디 또는 비밀번호가 올바르지 않습니다. (Invalid ID or Password.)")
                
    st.stop()

# ==========================================
# 2. 다국어 번역 데이터 사전 정의 (EN / KO)
# ==========================================
t = {
    "EN": {
        "header": "Ohyoung Dye Finder",
        "created_by": "Created by tskwon 🧑‍🔬",
        "logout_btn": "🔓 Log Out",
        "menu_title": "📂 Select Program",
        "tab1": "1. Fastness Matcher",
        "tab2": "2. Compatibility Analyzer",
        "tab3": "3. Fastness & Compatibility",
        "instruction_text": "Please select the desired dye groups and fastness grades from the left sidebar.",
        "sb_group_title": "1. Select Dye Group",
        "select_all": "✅ Select / Deselect All",
        "sb_spec_title": "2. Set Min Specs",
        "sb_dye_select": "🎨 Select Dyes to Compare",
        "spec_warn": "⚠️ Please select at least one dye group in the sidebar.",
        "search_res_hdr": "🔍 Fastness Matching Results",
        "search_res_sub": "Results (Matching Dyes: {count})",
        "search_res_desc": "**Click the checkbox in the first column (`Select`) to choose dyes for comparison.**",
        "col_select": "Select",
        "col_group": "Group",
        "col_name": "Dye Name",
        "warn_limit": "⚠️ Only up to 3 selected dyes are shown in click order.",
        "sim_hdr": "📈 Compatibility Simulation",
        "no_match": "💡 No dyes match the criteria.",
        "select_prompt": "Please check the **[Select]** checkbox above to compare dyes.\n\nGraph colors will be assigned as Yellow, Red, and Blue in the order selected.",
        "select_prompt_tab3": "Please select at least one dye from the left sidebar for comparison.\n\nGraph colors will be assigned as Yellow, Red, and Blue in the order selected.",
        "err_time_data": "⚠️ Time data columns are invalid.",
        "xaxis": "Process Time (min)",
        "yaxis": "Exhaustion / Fixation Rate (%)",
        "summary_hdr": "📋 Numeric Summary",
        "diag_hdr": "🔍 Field Diagnosis",
        "diag_excel": "✅ **Excellent**\n\nBehaviors match closely. Low risk of tailing.",
        "diag_warn": "⚠️ **Caution**\n\nMinor rate differences. Adjust temperature profile.",
        "diag_danger": "🚨 **Danger**\n\nHigh risk of tailing/face-back in bulk production.",
        "minute_unit": "min",
        "crit_light": "Light",
        "crit_p_light_acid": "Persp-Light(Acid)",
        "crit_p_light_alk": "Persp-Light(Alkali)",
        "crit_p_acid": "Persp(Acid)",
        "crit_p_alk": "Persp(Alkali)",
        "crit_wash": "Washing",
        "crit_chlor": "Chlorine"
    },
    "KO": {
        "header": "Ohyoung Dye Finder",
        "created_by": "Created by tskwon 🧑‍🔬",
        "logout_btn": "🔓 로그아웃 (Logout)",
        "menu_title": "📂 프로그램 선택",
        "tab1": "1. 요구견뢰도 등급에 따른 염료선정",
        "tab2": "2. 상용성 비교",
        "tab3": "3. 요구견뢰도+상용성 통합",
        "instruction_text": "왼쪽 사이드바에서 원하는 염료군과 견뢰도 등급을 설정하세요.",
        "sb_group_title": "1. 염료 그룹 선택",
        "select_all": "✅ 전체 선택 / 해제",
        "sb_spec_title": "2. 요구 스펙 설정 (이상)",
        "sb_dye_select": "🎨 비교 염료 선택",
        "spec_warn": "⚠️ 좌측 사이드바에서 염료 그룹을 최소 하나 이상 선택해 주세요.",
        "search_res_hdr": "🔍 견뢰도 스펙 매칭 결과",
        "search_res_sub": "검색 결과 (만족하는 염료: {count}개)",
        "search_res_desc": "**아래 표의 첫 번째 열(`선택`)을 클릭하여 비교할 염료를 선택하세요.** (최대 3개 권장)",
        "col_select": "선택",
        "col_group": "염료그룹",
        "col_name": "염료명",
        "warn_limit": "⚠️ 안정적인 그래프 비교를 위해 선택하신 순서대로 최대 3개까지만 표시됩니다.",
        "sim_hdr": "📈 선택 염료 상용성 시뮬레이션",
        "no_match": "💡 검색 조건에 맞는 염료가 없습니다.",
        "select_prompt": "표에서 비교하고 싶은 염료의 좌측 **[선택]** 체크박스를 눌러주세요.\n\n선택한 순서대로 Yellow, Red, Blue 로 그래프 색상이 선택됩니다.",
        "select_prompt_tab3": "좌측 사이드바에서 비교 분석할 염료를 1개 이상 선택해 주세요.\n\n선택한 순서대로 Yellow, Red, Blue 로 그래프 색상이 선택됩니다.",
        "err_time_data": "⚠️ 상용성 시간 데이터 열(0, 5, 20...)이 올바르지 않습니다.",
        "xaxis": "공정 시간 (분)",
        "yaxis": "염착률 / 고착률 (%)",
        "summary_hdr": "📋 수치 요약",
        "diag_hdr": "🔍 현장 진단",
        "diag_excel": "✅ **우수**\n\n거동이 거의 일치합니다. (Tailing 확률 매우 낮음)",
        "diag_warn": "⚠️ **주의**\n\n구간별 미세한 속도 차이가 있습니다. 승온 조건 조절 권장.",
        "diag_danger": "🚨 **위험**\n\n대량 생산 시 불량(Tailing/Face-back) 발생 확률이 높습니다.",
        "minute_unit": "분",
        "crit_light": "일광",
        "crit_p_light_acid": "땀일광(산성)",
        "crit_p_light_alk": "땀일광(알칼리)",
        "crit_p_acid": "땀(산성)",
        "crit_p_alk": "땀(알칼리)",
        "crit_wash": "세탁",
        "crit_chlor": "염소수"
    }
}

# 세션 상태 초기화 (기본 언어는 EN, 기본 탭은 tab3)
if "lang" not in st.session_state:
    st.session_state.lang = "EN"
lang = st.session_state.lang

if "app_mode" not in st.session_state:
    st.session_state.app_mode = "tab3"

# 전체 선택 토글 콜백 함수
def toggle_all_groups(app_mode_str, all_groups_list):
    master_state = st.session_state[f"chk_all_{app_mode_str}"]
    for g in all_groups_list:
        st.session_state[f"grp_{g}_{app_mode_str}"] = master_state

# ==========================================
# 3. 사이드바 최상단 (언어 전환 버튼)
# ==========================================
sb_col1, sb_col2 = st.sidebar.columns(2)
if sb_col1.button("🇺🇸 ENGLISH", use_container_width=True, type="primary" if lang == "EN" else "secondary"):
    st.session_state.lang = "EN"
    st.rerun()
if sb_col2.button("🇰🇷 KOREAN", use_container_width=True, type="primary" if lang == "KO" else "secondary"):
    st.session_state.lang = "KO"
    st.rerun()

st.sidebar.markdown("---")

# ==========================================
# 4. 메인 화면 헤더 (로고 및 타이틀)
# ==========================================
if os.path.exists("logo.png"):
    with open("logo.png", "rb") as f:
        img_base64 = base64.b64encode(f.read()).decode()
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; margin-bottom: 1.5rem;">
            <img src="data:image/png;base64,{img_base64}" width="50" style="margin-right: 15px;">
            <h1 style="margin: 0; padding: 0; font-size: 2.1rem; font-weight: 700;">{t[lang]["header"]}</h1>
        </div>
        """, 
        unsafe_allow_html=True
    )
else:
    st.title(f"🧪 {t[lang]['header']}")

# ==========================================
# 5. 사이드바 - 프로그램 선택 메뉴 (버튼 형식)
# ==========================================
st.sidebar.markdown(f"**{t[lang]['menu_title']}**")

if st.sidebar.button(t[lang]["tab1"], use_container_width=True, type="primary" if st.session_state.app_mode == "tab1" else "secondary"):
    st.session_state.app_mode = "tab1"
    st.rerun()
if st.sidebar.button(t[lang]["tab2"], use_container_width=True, type="primary" if st.session_state.app_mode == "tab2" else "secondary"):
    st.session_state.app_mode = "tab2"
    st.rerun()
if st.sidebar.button(t[lang]["tab3"], use_container_width=True, type="primary" if st.session_state.app_mode == "tab3" else "secondary"):
    st.session_state.app_mode = "tab3"
    st.rerun()

st.sidebar.markdown("---")

# 기준 항목 매핑 (공통) - 땀일광(알칼리) 버그 수정 완료!
criteria_map = {'일광': 'crit_light', '땀일광(산성)': 'crit_p_light_acid', '땀일광(알칼리)': 'crit_p_light_alk', 
                '땀(산성)': 'crit_p_acid', '땀(알칼리)': 'crit_p_alk', '세탁': 'crit_wash', '염소수': 'crit_chlor'}
criteria_list = ['일광', '땀일광(산성)', '땀일광(알칼리)', '땀(산성)', '땀(알칼리)', '세탁', '염소수']

# =====================================================================
# [App 1] 요구견뢰도 스펙 매칭 전용
# =====================================================================
if st.session_state.app_mode == "tab1":
    @st.cache_data
    def load_spec_data():
        if not os.path.exists("dyes_data.xlsx"): return None
        df = pd.read_excel("dyes_data.xlsx")
        df.columns = df.columns.str.strip()
        return df
    
    df1 = load_spec_data()
    if df1 is None:
        st.error("⚠️ `dyes_data.xlsx` 파일이 없습니다.")
    else:
        st.sidebar.markdown(f"**{t[lang]['sb_group_title']}**")
        all_groups1 = list(df1['염료그룹'].dropna().unique()) if '염료그룹' in df1.columns else []
        
        for g in all_groups1:
            if f"grp_{g}_tab1" not in st.session_state:
                st.session_state[f"grp_{g}_tab1"] = True if g == "Sunfix SPD conc." else False

        st.sidebar.checkbox(t[lang]["select_all"], value=False, key="chk_all_tab1", 
                            on_change=toggle_all_groups, args=("tab1", all_groups1))
        
        sc1_t1, sc2_t1 = st.sidebar.columns(2)
        selected_groups1 = []
        for i, group in enumerate(all_groups1):
            target_col = sc1_t1 if i % 2 == 0 else sc2_t1
            if target_col.checkbox(str(group), key=f"grp_{group}_tab1"):
                selected_groups1.append(group)
        
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"**{t[lang]['sb_spec_title']}**")
        req1 = {}
        for c in criteria_list:
            if c in df1.columns:
                display_label = t[lang][criteria_map.get(c, c)]
                default_val = 4.0 if c == '일광' else 3.0
                max_val = 7.0 if c == '일광' else 5.0
                req1[c] = st.sidebar.slider(display_label, 1.0, max_val, default_val, 0.5, key=f"sld_{c}_tab1")
                
        # [메인 화면 렌더링 - 안내 문구를 info 박스 안에 넣음]
        st.info(f"💡 **{t[lang]['instruction_text']}**")
        
        if not selected_groups1:
            st.warning(t[lang]["spec_warn"])
        else:
            f_df1 = df1[df1['염료그룹'].isin(selected_groups1)].copy()
            for c, min_val in req1.items():
                if c in f_df1.columns:
                    f_df1[c] = pd.to_numeric(f_df1[c], errors='coerce')
                    f_df1 = f_df1[f_df1[c] >= min_val]
                    
            st.subheader(t[lang]["search_res_hdr"])
            st.markdown(f"*{t[lang]['search_res_sub'].format(count=len(f_df1))}*")
            st.dataframe(f_df1, use_container_width=True)

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

    file_to_read = "반응성 염료 상용성 실험.xlsx"
    if not os.path.exists(file_to_read):
        st.error(f"❌ `{file_to_read}` 파일이 없습니다.")
        app2_data = None
    else:
        try:
            app2_data = parse_dye_data(file_to_read)
        except Exception as e:
            st.error(f"데이터 파싱 오류: {e}")
            app2_data = None

    if app2_data:
        st.sidebar.markdown(f"**{t[lang]['sb_dye_select']}**")
        selected_dyes2 = []
        for sheet_name, dyes in app2_data.items():
            dye_names = [d["name"] for d in dyes]
            selections = st.sidebar.multiselect(f"📋 {sheet_name}", options=dye_names, key=f"tab2_ms_{sheet_name}")
            for sel in selections:
                for d in dyes:
                    if d["name"] == sel: selected_dyes2.append((sheet_name, d))
                    
        st.subheader(t[lang]["sim_hdr"])
        if not selected_dyes2:
            # 안내 문구 (Info 박스)
            st.info(f"💡 {t[lang]['select_prompt_tab3']}")
        else:
            fig2 = go.Figure()
            custom_colors2 = ['#FFD700', '#FF4B4B', '#1F77B4', '#9467bd', '#2ca02c', '#ff7f0e', '#e377c2']
            
            for idx, (sheet_name, dye) in enumerate(selected_dyes2):
                color = custom_colors2[idx % len(custom_colors2)]
                label = f"[{sheet_name}] {dye['name']}"
                x1 = [t_val for t_val in dye["times"] if t_val <= 20]
                y1 = [v for t_val, v in zip(dye["times"], dye["values"]) if t_val <= 20]
                x2 = [t_val for t_val in dye["times"] if t_val >= 25]
                y2 = [v for t_val, v in zip(dye["times"], dye["values"]) if t_val >= 25]
                
                fig2.add_trace(go.Scatter(x=x1, y=y1, mode='lines', name=label, legendgroup=label, line=dict(width=3, color=color, shape='spline'), hovertemplate='%{x}' + f"{t[lang]['minute_unit']}: " + '<b>%{y}%</b><extra></extra>'))
                fig2.add_trace(go.Scatter(x=x2, y=y2, mode='lines', name=label, legendgroup=label, showlegend=False, line=dict(width=3, color=color, shape='spline'), hovertemplate='%{x}' + f"{t[lang]['minute_unit']}: " + '<b>%{y}%</b><extra></extra>'))
                
            fig2.update_layout(xaxis_title=t[lang]["xaxis"], yaxis_title=t[lang]["yaxis"], xaxis=dict(tickmode='array', tickvals=[0, 5, 20, 25, 40, 80, 100]), yaxis=dict(range=[0, 105]), hovermode="x unified", margin=dict(l=40, r=40, t=20, b=40), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            fig2.add_vline(x=20, line_dash="dash", line_color="gray")
            fig2.add_vline(x=25, line_dash="dash", line_color="gray")
            st.plotly_chart(fig2, use_container_width=True)
            
            st.markdown(f"**{t[lang]['summary_hdr']}**")
            table_data2 = []
            for sheet_name, dye in selected_dyes2:
                row_dict = {t[lang]["col_group"]: sheet_name, t[lang]["col_name"]: dye["name"]}
                for time_val, v in zip(dye["times"], dye["values"]):
                    row_dict[f"{time_val}{t[lang]['minute_unit']}"] = f"{v:.1f}%"
                table_data2.append(row_dict)
            st.dataframe(pd.DataFrame(table_data2), hide_index=True, use_container_width=True)
            
            if len(selected_dyes2) >= 2:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(f"#### {t[lang]['diag_hdr']}")
                all_matrix = np.array([d["values"] for _, d in selected_dyes2])
                std_per_time = np.std(all_matrix, axis=0)
                max_dev = np.max(std_per_time)
                
                if max_dev < 5: st.success(t[lang]["diag_excel"])
                elif max_dev < 12: st.warning(t[lang]["diag_warn"])
                else: st.error(t[lang]["diag_danger"])

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
    
    df3 = load_integrated_data()
    if df3 is None:
        st.error("⚠️ `integrated_dyes_data.xlsx` 파일이 없습니다.")
    else:
        st.sidebar.markdown(f"**{t[lang]['sb_group_title']}**")
        all_groups3 = list(df3['염료그룹'].dropna().unique()) if '염료그룹' in df3.columns else []
        
        for g in all_groups3:
            if f"grp_{g}_tab3" not in st.session_state:
                st.session_state[f"grp_{g}_tab3"] = True if g == "Sunfix SPD conc." else False

        st.sidebar.checkbox(t[lang]["select_all"], value=False, key="chk_all_tab3", 
                            on_change=toggle_all_groups, args=("tab3", all_groups3))
        
        sc1, sc2 = st.sidebar.columns(2)
        selected_groups3 = []
        for i, group in enumerate(all_groups3):
            target_col = sc1 if i % 2 == 0 else sc2
            if target_col.checkbox(str(group), key=f"grp_{group}_tab3"):
                selected_groups3.append(group)
                
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"**{t[lang]['sb_spec_title']}**")
        req3 = {}
        for c in criteria_list:
            if c in df3.columns:
                display_label = t[lang][criteria_map.get(c, c)]
                default_val = 4.0 if c == '일광' else 3.0
                max_val = 7.0 if c == '일광' else 5.0
                req3[c] = st.sidebar.slider(display_label, 1.0, max_val, default_val, 0.5, key=f"sld_{c}_tab3")

        # [메인 화면 렌더링 - 상단 안내문구 Info 박스로 통일]
        st.info(f"💡 **{t[lang]['instruction_text']}**")
        
        if not selected_groups3:
            st.warning(t[lang]["spec_warn"])
        else:
            f_df3 = df3[df3['염료그룹'].isin(selected_groups3)].copy()
            for c, min_val in req3.items():
                if c in f_df3.columns:
                    f_df3[c] = pd.to_numeric(f_df3[c], errors='coerce')
                    f_df3 = f_df3[f_df3[c] >= min_val]
                    
            st.subheader(t[lang]["search_res_hdr"])
            st.markdown(f"*{t[lang]['search_res_sub'].format(count=len(f_df3))}*")
            st.write(t[lang]["search_res_desc"])
            
            f_df3.insert(0, '선택', False)
            disp_cols3 = ['선택', '염료그룹', '염료명'] + [c for c in criteria_list if c in f_df3.columns]
            
            col_configs3 = {
                "선택": st.column_config.CheckboxColumn(label=t[lang]["col_select"], width="small"),
                "염료그룹": st.column_config.TextColumn(label=t[lang]["col_group"], width=100),
                "염료명": st.column_config.TextColumn(label=t[lang]["col_name"], width=150)
            }
            for c in disp_cols3[3:]:
                col_configs3[c] = st.column_config.NumberColumn(label=t[lang][criteria_map.get(c, c)], width=80)
                
            if "tab3_selected_order" not in st.session_state:
                st.session_state.tab3_selected_order = []
                
            edited_df3 = st.data_editor(
                f_df3[disp_cols3], hide_index=True, use_container_width=True,
                column_config=col_configs3, disabled=[col for col in disp_cols3 if col != '선택'], key="tab3_editor"
            )
            
            curr_checked3 = edited_df3[edited_df3['선택'] == True]['염료명'].tolist()
            st.session_state.tab3_selected_order = [d for d in st.session_state.tab3_selected_order if d in curr_checked3]
            for d in curr_checked3:
                if d not in st.session_state.tab3_selected_order:
                    st.session_state.tab3_selected_order.append(d)
            
            sel_dyes3 = st.session_state.tab3_selected_order[:3]
            if len(curr_checked3) > 3: st.warning(t[lang]["warn_limit"])
            
            st.markdown("---")
            st.subheader(t[lang]["sim_hdr"])
            if not sel_dyes3:
                # [그래프 하단 안내문구 Info 박스로 통일]
                st.info(f"💡 {t[lang]['select_prompt']}")
            else:
                time_pts3 = ['0', '5', '20', '25', '40', '80', '100']
                val_cols3 = [tc for tc in time_pts3 if tc in df3.columns]
                if len(val_cols3) < 2:
                    st.warning(t[lang]["err_time_data"])
                else:
                    fig3 = go.Figure()
                    colors = ['#FFD700', '#FF4B4B', '#1F77B4']
                    for idx, name in enumerate(sel_dyes3):
                        row = df3[df3['염료명'] == name].iloc[0]
                        color = colors[idx % len(colors)]
                        label = f"[{row['염료그룹']}] {name}"
                        t_p1 = [tc for tc in val_cols3 if int(tc) <= 20]
                        v_p1 = [row[tc] for tc in t_p1]
                        t_p2 = [tc for tc in val_cols3 if int(tc) >= 25]
                        v_p2 = [row[tc] for tc in t_p2]
                        
                        fig3.add_trace(go.Scatter(x=t_p1, y=v_p1, mode='lines', name=label, legendgroup=label, line=dict(width=3, color=color, shape='spline'), hovertemplate='%{x}' + f"{t[lang]['minute_unit']}: " + '<b>%{y}%</b><extra></extra>'))
                        fig3.add_trace(go.Scatter(x=t_p2, y=v_p2, mode='lines', name=label, legendgroup=label, showlegend=False, line=dict(width=3, color=color, shape='spline'), hovertemplate='%{x}' + f"{t[lang]['minute_unit']}: " + '<b>%{y}%</b><extra></extra>'))
                        
                    fig3.update_layout(xaxis_title=t[lang]["xaxis"], yaxis_title=t[lang]["yaxis"], xaxis=dict(tickmode='array', tickvals=[int(tc) for tc in val_cols3]), yaxis=dict(range=[0, 105]), hovermode="x unified", margin=dict(l=40, r=40, t=20, b=40), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
                    fig3.add_vline(x=20, line_dash="dash", line_color="gray")
                    fig3.add_vline(x=25, line_dash="dash", line_color="gray")
                    st.plotly_chart(fig3, use_container_width=True)
                    
                    st.markdown(f"**{t[lang]['summary_hdr']}**")
                    tb_data3 = []
                    for name in sel_dyes3:
                        row = df3[df3['염료명'] == name].iloc[0]
                        rd = {t[lang]["col_name"]: name}
                        for tc in val_cols3: rd[f"{tc}{t[lang]['minute_unit']}"] = f"{row[tc]:.1f}%" if pd.notna(row[tc]) else "-"
                        tb_data3.append(rd)
                    st.dataframe(pd.DataFrame(tb_data3), hide_index=True, use_container_width=True)
                    
                    if len(sel_dyes3) >= 2:
                        st.markdown("<br>", unsafe_allow_html=True)
                        st.markdown(f"#### {t[lang]['diag_hdr']}")
                        all_matrix = np.array([[df3[df3['염료명'] == name].iloc[0][tc] for tc in val_cols3] for name in sel_dyes3], dtype=float)
                        std_per_time = np.nanstd(all_matrix, axis=0)
                        max_dev = np.nanmax(std_per_time)
                        
                        if max_dev < 5: st.success(t[lang]["diag_excel"])
                        elif max_dev < 12: st.warning(t[lang]["diag_warn"])
                        else: st.error(t[lang]["diag_danger"])

# ==========================================
# 6. 최하단 공통 요소 (로그아웃 및 제작자 정보)
# ==========================================
st.sidebar.markdown("<br><br><br>", unsafe_allow_html=True)
st.sidebar.markdown("---")
st.sidebar.markdown(f"<p style='text-align: center; color: #888888; font-size: 13px; margin-bottom: 10px;'>{t[lang]['created_by']}</p>", unsafe_allow_html=True)

if st.sidebar.button(t[lang]["logout_btn"], use_container_width=True, type="secondary"):
    st.session_state.logged_in = False
    st.rerun()