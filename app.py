import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
import base64

# ==========================================
# 0. 웹페이지 기본 설정
# ==========================================
st.set_page_config(page_title="오영 염료 3in1 솔루션", page_icon="logo.png", layout="wide")

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
                    {login_logo_html}OHYOUNG Solution Login
                </h2>
                <p style="text-align: center; color: #666; font-size: 0.95rem; margin-bottom: 30px;">
                    오영 염료 통합 매칭 시스템 접근을 위해 로그인해 주세요.
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
# 2. 다국어 번역 데이터 사전 정의 (KO / EN)
# ==========================================
t = {
    "KO": {
        "header": "오영(OHYOUNG) 염료 3in1 솔루션",
        "created_by": "Created by tskwon 🧑‍🔬",
        "logout_btn": "🔓 로그아웃 (Logout)",
        "menu_title": "📂 프로그램 선택",
        "tab1": "1. 통합 매칭 및 시뮬레이션",
        "tab2": "2. 견뢰도 스펙 매칭 전용",
        "tab3": "3. 상용성(거동) 단독 분석",
        "sb_group_title": "📌 1. 염료 그룹 선택",
        "select_all": "✅ 전체 선택 / 해제",
        "sb_spec_title": "⚙️ 2. 요구 스펙 설정 (이상)",
        "sb_dye_select": "🎨 비교 염료 선택",
        "spec_warn": "⚠️ 좌측 사이드바에서 염료 그룹을 최소 하나 이상 선택해 주세요.",
        "search_res_hdr": "🔍 견뢰도 스펙 매칭 결과",
        "search_res_sub": "✨ 검색 결과 (만족하는 염료: {count}개)",
        "search_res_desc": "💡 **아래 표의 첫 번째 열(`선택`)을 클릭하여 비교할 염료를 선택하세요.** (최대 3개 권장)",
        "col_select": "선택",
        "col_group": "염료그룹",
        "col_name": "염료명",
        "warn_limit": "⚠️ 안정적인 그래프 비교를 위해 선택하신 순서대로 최대 3개까지만 표시됩니다.",
        "sim_hdr": "📈 선택 염료 상용성 시뮬레이션",
        "no_match": "💡 검색 조건에 맞는 염료가 없습니다.",
        "select_prompt": "👆 표에서 비교하고 싶은 염료의 좌측 **[선택]** 체크박스를 눌러주세요.",
        "select_prompt_tab3": "💡 좌측 사이드바에서 비교 분석할 염료를 1개 이상 선택해 주세요.",
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
    },
    "EN": {
        "header": "OHYOUNG 3-in-1 Dye Solution",
        "created_by": "Created by tskwon 🧑‍🔬",
        "logout_btn": "🔓 Log Out",
        "menu_title": "📂 Select Program",
        "tab1": "1. Integrated Matching & Sim",
        "tab2": "2. Fastness Spec Matching Only",
        "tab3": "3. Compatibility Analysis Only",
        "sb_group_title": "📌 1. Select Dye Group",
        "select_all": "✅ Select / Deselect All",
        "sb_spec_title": "⚙️ 2. Set Min Specs",
        "sb_dye_select": "🎨 Select Dyes to Compare",
        "spec_warn": "⚠️ Please select at least one dye group in the sidebar.",
        "search_res_hdr": "🔍 Fastness Matching Results",
        "search_res_sub": "✨ Results (Matching Dyes: {count})",
        "search_res_desc": "💡 **Click the checkbox in the first column (`Select`) to choose dyes for comparison.**",
        "col_select": "Select",
        "col_group": "Group",
        "col_name": "Dye Name",
        "warn_limit": "⚠️ Only up to 3 selected dyes are shown in click order.",
        "sim_hdr": "📈 Compatibility Simulation",
        "no_match": "💡 No dyes match the criteria.",
        "select_prompt": "👆 Please check the **[Select]** checkbox above to compare dyes.",
        "select_prompt_tab3": "💡 Please select at least one dye from the left sidebar for comparison.",
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
    }
}

# 세션 상태 초기화 (언어 및 현재 페이지 위치 유지용)
if "lang" not in st.session_state:
    st.session_state.lang = "KO"
lang = st.session_state.lang

if "app_mode" not in st.session_state:
    st.session_state.app_mode = "tab1"

# ==========================================
# 3. 메인 헤더 및 언어 전환 (화면 우측 상단)
# ==========================================
col_header, col_lang_switch = st.columns([7, 3])
with col_header:
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
        
with col_lang_switch:
    st.write("") 
    sub_col1, sub_col2 = st.columns(2)
    if sub_col1.button("🇰🇷 KOREAN (KR)", use_container_width=True, type="secondary" if lang == "EN" else "primary"):
        st.session_state.lang = "KO"
        st.rerun()
    if sub_col2.button("🇺🇸 ENGLISH (EN)", use_container_width=True, type="secondary" if lang == "KO" else "primary"):
        st.session_state.lang = "EN"
        st.rerun()

# ==========================================
# 4. 사이드바 - 프로그램 선택 메뉴 (버튼 형식)
# ==========================================
st.sidebar.markdown(f"**{t[lang]['menu_title']}**")

# 프로그램 1, 2, 3 전환 버튼 (한/영 버튼처럼 동일한 스타일 적용)
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

# 기준 항목 매핑 (공통)
criteria_map = {'일광': 'crit_light', '땀일광(산성)': 'crit_p_light_acid', '땀일광(알칼리)': 'crit_p_light_alk', 
                '땀(산성)': 'crit_p_acid', '땀(알칼리)': 'crit_p_alk', '세탁': 'crit_wash', '염소수': 'crit_chlor'}
criteria_list = ['일광', '땀일광(산성)', '땀일광(알칼리)', '땀(산성)', '땀(알칼리)', '세탁', '염소수']

# =====================================================================
# [App 1] 통합 매칭 및 시뮬레이션
# =====================================================================
if st.session_state.app_mode == "tab1":
    @st.cache_data
    def load_integrated_data():
        if not os.path.exists("integrated_dyes_data.xlsx"): return None
        df = pd.read_excel("integrated_dyes_data.xlsx")
        df.columns = [str(col).strip() for col in df.columns]
        return df
    
    df1 = load_integrated_data()
    if df1 is None:
        st.error("⚠️ `integrated_dyes_data.xlsx` 파일이 없습니다.")
    else:
        # [사이드바 동적 렌더링]
        st.sidebar.markdown(f"**{t[lang]['sb_group_title']}**")
        all_groups1 = list(df1['염료그룹'].dropna().unique()) if '염료그룹' in df1.columns else []
        select_all_t1 = st.sidebar.checkbox(t[lang]["select_all"], value=True, key="t1_chk_all")
        
        sc1, sc2 = st.sidebar.columns(2)
        selected_groups1 = []
        for i, group in enumerate(all_groups1):
            target_col = sc1 if i % 2 == 0 else sc2
            if target_col.checkbox(str(group), value=select_all_t1, key=f"t1_grp_{group}"):
                selected_groups1.append(group)
                
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"**{t[lang]['sb_spec_title']}**")
        req1 = {}
        for c in criteria_list:
            if c in df1.columns:
                display_label = t[lang][criteria_map[c]]
                max_val = 7.0 if c == '일광' else 5.0
                req1[c] = st.sidebar.slider(display_label, 1.0, max_val, 1.0, 0.5, key=f"t1_sld_{c}")

        # [메인 화면 렌더링]
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
            st.write(t[lang]["search_res_desc"])
            
            f_df1.insert(0, '선택', False)
            disp_cols1 = ['선택', '염료그룹', '염료명'] + [c for c in criteria_list if c in f_df1.columns]
            
            col_configs1 = {
                "선택": st.column_config.CheckboxColumn(label=t[lang]["col_select"], width="small"),
                "염료그룹": st.column_config.TextColumn(label=t[lang]["col_group"], width=100),
                "염료명": st.column_config.TextColumn(label=t[lang]["col_name"], width=150)
            }
            for c in disp_cols1[3:]:
                col_configs1[c] = st.column_config.NumberColumn(label=t[lang][criteria_map[c]], width=80)
                
            if "t1_selected_order" not in st.session_state:
                st.session_state.t1_selected_order = []
                
            edited_df1 = st.data_editor(
                f_df1[disp_cols1], hide_index=True, use_container_width=True,
                column_config=col_configs1, disabled=[col for col in disp_cols1 if col != '선택'], key="t1_editor"
            )
            
            curr_checked1 = edited_df1[edited_df1['선택'] == True]['염료명'].tolist()
            st.session_state.t1_selected_order = [d for d in st.session_state.t1_selected_order if d in curr_checked1]
            for d in curr_checked1:
                if d not in st.session_state.t1_selected_order:
                    st.session_state.t1_selected_order.append(d)
            
            sel_dyes1 = st.session_state.t1_selected_order[:3]
            if len(curr_checked1) > 3: st.warning(t[lang]["warn_limit"])
            
            st.markdown("---")
            st.subheader(t[lang]["sim_hdr"])
            if not sel_dyes1:
                st.info(t[lang]["select_prompt"])
            else:
                time_pts1 = ['0', '5', '20', '25', '40', '80', '100']
                val_cols1 = [tc for tc in time_pts1 if tc in df1.columns]
                if len(val_cols1) < 2:
                    st.warning(t[lang]["err_time_data"])
                else:
                    fig1 = go.Figure()
                    colors = ['#FFD700', '#FF4B4B', '#1F77B4']
                    for idx, name in enumerate(sel_dyes1):
                        row = df1[df1['염료명'] == name].iloc[0]
                        color = colors[idx % len(colors)]
                        label = f"[{row['염료그룹']}] {name}"
                        t_p1 = [tc for tc in val_cols1 if int(tc) <= 20]
                        v_p1 = [row[tc] for tc in t_p1]
                        t_p2 = [tc for tc in val_cols1 if int(tc) >= 25]
                        v_p2 = [row[tc] for tc in t_p2]
                        
                        fig1.add_trace(go.Scatter(x=t_p1, y=v_p1, mode='lines', name=label, legendgroup=label, line=dict(width=3, color=color, shape='spline'), hovertemplate='%{x}' + f"{t[lang]['minute_unit']}: " + '<b>%{y}%</b><extra></extra>'))
                        fig1.add_trace(go.Scatter(x=t_p2, y=v_p2, mode='lines', name=label, legendgroup=label, showlegend=False, line=dict(width=3, color=color, shape='spline'), hovertemplate='%{x}' + f"{t[lang]['minute_unit']}: " + '<b>%{y}%</b><extra></extra>'))
                        
                    fig1.update_layout(xaxis_title=t[lang]["xaxis"], yaxis_title=t[lang]["yaxis"], xaxis=dict(tickmode='array', tickvals=[int(tc) for tc in val_cols1]), yaxis=dict(range=[0, 105]), hovermode="x unified", margin=dict(l=40, r=40, t=20, b=40), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
                    fig1.add_vline(x=20, line_dash="dash", line_color="gray")
                    fig1.add_vline(x=25, line_dash="dash", line_color="gray")
                    st.plotly_chart(fig1, use_container_width=True)
                    
                    st.markdown(f"**{t[lang]['summary_hdr']}**")
                    tb_data1 = []
                    for name in sel_dyes1:
                        row = df1[df1['염료명'] == name].iloc[0]
                        rd = {t[lang]["col_name"]: name}
                        for tc in val_cols1: rd[f"{tc}{t[lang]['minute_unit']}"] = f"{row[tc]:.1f}%" if pd.notna(row[tc]) else "-"
                        tb_data1.append(rd)
                    st.dataframe(pd.DataFrame(tb_data1), hide_index=True, use_container_width=True)
                    
                    if len(sel_dyes1) >= 2:
                        st.markdown("<br>", unsafe_allow_html=True)
                        st.markdown(f"#### {t[lang]['diag_hdr']}")
                        all_matrix = np.array([[df1[df1['염료명'] == name].iloc[0][tc] for tc in val_cols1] for name in sel_dyes1], dtype=float)
                        std_per_time = np.nanstd(all_matrix, axis=0)
                        max_dev = np.nanmax(std_per_time)
                        
                        if max_dev < 5: st.success(t[lang]["diag_excel"])
                        elif max_dev < 12: st.warning(t[lang]["diag_warn"])
                        else: st.error(t[lang]["diag_danger"])

# =====================================================================
# [App 2] 견뢰도 스펙 매칭 전용
# =====================================================================
elif st.session_state.app_mode == "tab2":
    @st.cache_data
    def load_spec_data():
        if not os.path.exists("dyes_data.xlsx"): return None
        df = pd.read_excel("dyes_data.xlsx")
        df.columns = df.columns.str.strip()
        return df
    
    df2 = load_spec_data()
    if df2 is None:
        st.error("⚠️ `dyes_data.xlsx` 파일이 없습니다.")
    else:
        # [사이드바 동적 렌더링]
        st.sidebar.markdown(f"**{t[lang]['sb_group_title']}**")
        all_groups2 = list(df2['염료그룹'].dropna().unique()) if '염료그룹' in df2.columns else []
        select_all_t2 = st.sidebar.checkbox(t[lang]["select_all"], value=True, key="t2_chk_all")
        
        sc1_t2, sc2_t2 = st.sidebar.columns(2)
        selected_groups2 = []
        for i, group in enumerate(all_groups2):
            target_col = sc1_t2 if i % 2 == 0 else sc2_t2
            if target_col.checkbox(str(group), value=select_all_t2, key=f"t2_grp_{group}"):
                selected_groups2.append(group)
        
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"**{t[lang]['sb_spec_title']}**")
        req2 = {}
        for c in criteria_list:
            if c in df2.columns:
                display_label = t[lang][criteria_map[c]]
                req2[c] = st.sidebar.slider(display_label, 1.0, 6.0, 1.0, 0.5, key=f"t2_sld_{c}")
                
        # [메인 화면 렌더링]
        if not selected_groups2:
            st.warning(t[lang]["spec_warn"])
        else:
            f_df2 = df2[df2['염료그룹'].isin(selected_groups2)].copy()
            for c, min_val in req2.items():
                if c in f_df2.columns:
                    f_df2[c] = pd.to_numeric(f_df2[c], errors='coerce')
                    f_df2 = f_df2[f_df2[c] >= min_val]
                    
            st.subheader(t[lang]["search_res_hdr"])
            st.markdown(f"*{t[lang]['search_res_sub'].format(count=len(f_df2))}*")
            st.dataframe(f_df2, use_container_width=True)

# =====================================================================
# [App 3] 상용성 그래프 단독
# =====================================================================
elif st.session_state.app_mode == "tab3":
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
        app1_data = None
    else:
        try:
            app1_data = parse_dye_data(file_to_read)
        except Exception as e:
            st.error(f"데이터 파싱 오류: {e}")
            app1_data = None

    if app1_data:
        # [사이드바 동적 렌더링]
        st.sidebar.markdown(f"**{t[lang]['sb_dye_select']}**")
        selected_dyes3 = []
        for sheet_name, dyes in app1_data.items():
            dye_names = [d["name"] for d in dyes]
            selections = st.sidebar.multiselect(f"📋 {sheet_name}", options=dye_names, key=f"t3_ms_{sheet_name}")
            for sel in selections:
                for d in dyes:
                    if d["name"] == sel: selected_dyes3.append((sheet_name, d))
                    
        # [메인 화면 렌더링]
        st.subheader(t[lang]["sim_hdr"])
        if not selected_dyes3:
            st.info(t[lang]["select_prompt_tab3"])
        else:
            fig3 = go.Figure()
            custom_colors3 = ['#FFD700', '#FF4B4B', '#1F77B4', '#9467bd', '#2ca02c', '#ff7f0e', '#e377c2']
            
            for idx, (sheet_name, dye) in enumerate(selected_dyes3):
                color = custom_colors3[idx % len(custom_colors3)]
                label = f"[{sheet_name}] {dye['name']}"
                x1 = [t_val for t_val in dye["times"] if t_val <= 20]
                y1 = [v for t_val, v in zip(dye["times"], dye["values"]) if t_val <= 20]
                x2 = [t_val for t_val in dye["times"] if t_val >= 25]
                y2 = [v for t_val, v in zip(dye["times"], dye["values"]) if t_val >= 25]
                
                fig3.add_trace(go.Scatter(x=x1, y=y1, mode='lines', name=label, legendgroup=label, line=dict(width=3, color=color, shape='spline'), hovertemplate='%{x}분: <b>%{y}%</b><extra></extra>'))
                fig3.add_trace(go.Scatter(x=x2, y=y2, mode='lines', name=label, legendgroup=label, showlegend=False, line=dict(width=3, color=color, shape='spline'), hovertemplate='%{x}분: <b>%{y}%</b><extra></extra>'))
                
            fig3.update_layout(xaxis_title=t[lang]["xaxis"], yaxis_title=t[lang]["yaxis"], xaxis=dict(tickmode='array', tickvals=[0, 5, 20, 25, 40, 80, 100]), yaxis=dict(range=[0, 105]), hovermode="x unified", margin=dict(l=40, r=40, t=20, b=40), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            fig3.add_vline(x=20, line_dash="dash", line_color="gray")
            fig3.add_vline(x=25, line_dash="dash", line_color="gray")
            st.plotly_chart(fig3, use_container_width=True)
            
            st.markdown(f"**{t[lang]['summary_hdr']}**")
            table_data3 = []
            for sheet_name, dye in selected_dyes3:
                row_dict = {t[lang]["col_group"]: sheet_name, t[lang]["col_name"]: dye["name"]}
                for time_val, v in zip(dye["times"], dye["values"]):
                    row_dict[f"{time_val}{t[lang]['minute_unit']}"] = f"{v:.1f}%"
                table_data3.append(row_dict)
            st.dataframe(pd.DataFrame(table_data3), hide_index=True, use_container_width=True)
            
            if len(selected_dyes3) >= 2:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(f"#### {t[lang]['diag_hdr']}")
                all_matrix = np.array([d["values"] for _, d in selected_dyes3])
                std_per_time = np.std(all_matrix, axis=0)
                max_dev = np.max(std_per_time)
                
                if max_dev < 5: st.success(t[lang]["diag_excel"])
                elif max_dev < 12: st.warning(t[lang]["diag_warn"])
                else: st.error(t[lang]["diag_danger"])

# ==========================================
# 5. 최하단 공통 요소 (로그아웃 및 제작자 정보)
# ==========================================
st.sidebar.markdown("<br><br><br>", unsafe_allow_html=True) # 공백 추가로 하단으로 밀어내기
st.sidebar.markdown("---")
st.sidebar.markdown(f"<p style='text-align: center; color: #888888; font-size: 13px; margin-bottom: 10px;'>{t[lang]['created_by']}</p>", unsafe_allow_html=True)

if st.sidebar.button(t[lang]["logout_btn"], use_container_width=True, type="secondary"):
    st.session_state.logged_in = False
    st.rerun()