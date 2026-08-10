import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
import base64
import hashlib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit.components.v1 as components
from streamlit_gsheets import GSheetsConnection

# ==========================================
# 0. 웹페이지 기본 설정 및 커스텀 CSS (모던 UI 적용)
# ==========================================
st.set_page_config(page_title="Ohyoung Dye Finder", page_icon="logo.png", layout="wide")

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined" rel="stylesheet" />
<style>
    h2, h3 { font-weight: 700 !important; color: #111 !important; }
    h3 { border-bottom: 1px solid #eee; padding-bottom: 10px; margin-bottom: 24px; margin-top: 10px; }
    [data-testid="stSidebar"] p strong {
        display: block; border-left: 4px solid #1b489d; padding-left: 10px; 
        margin-top: 20px; margin-bottom: 8px; font-size: 16px; color: #333;
    }
    hr { margin: 1.5em 0; }
    
    /* 🇺🇸 첫 번째 칸(ENGLISH) 버튼 자체에 미국 국기 꽂아넣기 */
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] > div:nth-child(1) button::before {
        content: "";
        display: inline-block;
        width: 24px;
        height: 16px;
        background: url("https://flagcdn.com/w40/us.png") no-repeat center;
        background-size: contain;
        margin-right: 8px;
    }

    /* 🇰🇷 두 번째 칸(KOREAN) 버튼 자체에 한국 국기 꽂아넣기 */
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] > div:nth-child(2) button::before {
        content: "";
        display: inline-block;
        width: 24px;
        height: 16px;
        background: url("https://flagcdn.com/w40/kr.png") no-repeat center;
        background-size: contain;
        margin-right: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. 구글 시트 연동, 메일 발송 및 보안 함수
# ==========================================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_users_df():
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(worksheet="Users", ttl=0) # ttl=0 : 항상 최신 데이터 로드
    df = df.dropna(subset=['username']) # 빈 행 제거
    return df

def update_users_df(df):
    conn = st.connection("gsheets", type=GSheetsConnection)
    conn.update(worksheet="Users", data=df)

def send_approval_email(recipient_email, recipient_name, user_id):
    try:
        sender = st.secrets["email"]["sender"]
        password = st.secrets["email"]["password"]
        
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = recipient_email
        msg['Subject'] = "[Ohyoung Dye Finder] 계정 승인이 완료되었습니다."
        
        body = f"""
{recipient_name}님, 안녕하세요.

요청하신 Ohyoung Dye Finder 시스템 계정({user_id})의 승인이 완료되었습니다.
이제 시스템에 접속하여 로그인하실 수 있습니다.

감사합니다.
        """
        msg.attach(MIMEText(body, 'plain'))
        
        # 하이웍스 SMTP 서버 연결 (알려주신 smtps.hiworks.com / SSL 465 포트 적용)
        server = smtplib.SMTP_SSL('smtps.hiworks.com', 465)
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        # 에러가 발생하면 화면에 빨간색으로 왜 안 되는지 정확히 띄워줍니다.
        st.error(f"메일 발송 에러 발생: {e}")
        return False

# ==========================================
# 2. 로그인 및 회원가입 기능 (관리자 승인 시스템)
# ==========================================
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "username" not in st.session_state: st.session_state.username = ""
if "is_admin" not in st.session_state: st.session_state.is_admin = False

if not st.session_state.logged_in:
    _, login_col, _ = st.columns([1, 2, 1])
    with login_col:
        login_logo_html = "<span class='material-symbols-outlined' style='font-size:40px; color:#1E3A8A; vertical-align:middle; margin-right:10px;'>science</span>"
        if os.path.exists("logo.png"):
            with open("logo.png", "rb") as f:
                login_img_base64 = base64.b64encode(f.read()).decode()
            login_logo_html = f'<img src="data:image/png;base64,{login_img_base64}" width="45" style="vertical-align: middle; margin-right: 10px; margin-bottom: 5px;">'

        st.markdown(
            f"""
            <div style="background-color:#f9f9f9; padding: 2.5rem; border-radius: 12px; border: 1px solid #ddd; margin-top: 50px; box-shadow: 0px 4px 10px rgba(0,0,0,0.05); margin-bottom: 20px;">
                <h2 style="text-align: center; margin-top: 0; margin-bottom: 20px; font-weight: 700; color: #1E3A8A; border: none;">
                    {login_logo_html}Ohyoung Dye Finder
                </h2>
                <p style="text-align: center; color: #666; font-size: 0.95rem; margin-bottom: 0;">
                    관리자의 승인이 필요한 시스템입니다.
                </p>
            </div>
            """, 
            unsafe_allow_html=True
        )

        tab1, tab2 = st.tabs(["🔑 로그인 (Login)", "📝 회원가입 (Sign Up)"])
        
        # [로그인 탭]
        with tab1:
            with st.form("login_form"):
                login_id = st.text_input("아이디 (ID)")
                login_pw = st.text_input("비밀번호 (Password)", type="password")
                submitted_login = st.form_submit_button("로그인", use_container_width=True, type="primary")
                
                if submitted_login:
                    try:
                        users_df = get_users_df()
                        user_row = users_df[users_df['username'] == login_id]

                        if not user_row.empty:
                            stored_pw = str(user_row.iloc[0]['password_hash'])
                            is_approved = int(user_row.iloc[0]['is_approved'])
                            is_admin = int(user_row.iloc[0]['is_admin'])
                            
                            if stored_pw == hash_password(login_pw):
                                if is_approved == 1:
                                    st.session_state.logged_in = True
                                    st.session_state.username = login_id
                                    st.session_state.is_admin = bool(is_admin)
                                    st.rerun()
                                else:
                                    st.warning("승인 대기 중인 계정입니다. 관리자에게 문의하세요.", icon=":material/hourglass_empty:")
                            else:
                                st.error("비밀번호가 올바르지 않습니다.", icon=":material/error:")
                        else:
                            st.error("존재하지 않는 아이디입니다.", icon=":material/error:")
                    except Exception as e:
                        st.error("데이터베이스 연결 오류가 발생했습니다. 구글 시트 설정을 확인하세요.", icon=":material/error:")
                        st.write(e)
                        
        # [회원가입 탭]
        with tab2:
            with st.form("signup_form"):
                new_name = st.text_input("이름 (Name)")
                new_email = st.text_input("이메일 (e-mail) - 승인 결과 수신용")
                new_id = st.text_input("생성할 아이디 (New ID)")
                new_pw = st.text_input("비밀번호 (Password)", type="password")
                new_pw_confirm = st.text_input("비밀번호 확인 (Confirm Password)", type="password")
                submitted_signup = st.form_submit_button("가입 신청", use_container_width=True)
                
                if submitted_signup:
                    if not new_name or not new_email or not new_id or not new_pw:
                        st.warning("이름, 이메일, 아이디, 비밀번호를 모두 입력해주세요.")
                    elif new_pw != new_pw_confirm:
                        st.error("비밀번호가 일치하지 않습니다.")
                    else:
                        users_df = get_users_df()
                        if new_id in users_df['username'].values:
                            st.error("이미 존재하는 아이디입니다.")
                        else:
                            new_user = pd.DataFrame([{
                                'username': new_id,
                                'password_hash': hash_password(new_pw),
                                'name': new_name,
                                'e-mail': new_email,  # 시트 열 이름 일치
                                'is_approved': 0,
                                'is_admin': 0
                            }])
                            updated_df = pd.concat([users_df, new_user], ignore_index=True)
                            update_users_df(updated_df)
                            st.success("가입 신청이 완료되었습니다. 관리자 승인 후 메일로 안내해 드립니다.")
                        
    st.stop()

# ==========================================
# 3. 다국어 번역 데이터 사전 정의 (EN / KO)
# ==========================================
t = {
    "EN": {
        "header": "Ohyoung Dye Finder",
        "created_by": "Created by tskwon <span class='material-symbols-outlined' style='font-size: 14px; vertical-align: middle;'>science</span>",
        "logout_btn": ":material/logout: Log Out",
        "menu_title": "Select Program",
        "tab1": "1. Fastness Matcher",
        "tab2": "2. Compatibility Analyzer",
        "tab3": "3. Fastness & Compatibility",
        "instruction_text": "Please select the desired dye groups and fastness grades from the left sidebar.",
        "sb_group_title": "1. Select Dye Group",
        "select_all": "Select / Deselect All",
        "sb_spec_title": "2. Set Min Specs",
        "sb_dye_select": "Select Dyes to Compare",
        "spec_warn": "Please select at least one dye group in the sidebar.",
        "search_res_hdr": ":material/manage_search: Fastness Matching Results",
        "search_res_sub": "Results (Matching Dyes: {count})",
        "search_res_desc": "**Click the checkbox in the first column (`Select`) to choose dyes for comparison.**",
        "col_select": "Select",
        "col_group": "Group",
        "col_name": "Dye Name",
        "warn_limit": "Only up to 3 selected dyes are shown in click order.",
        "sim_hdr": ":material/monitoring: Compatibility Simulation",
        "no_match": "No dyes match the criteria.",
        "select_prompt": "Please check the **[Select]** checkbox above to compare dyes.\n\nGraph colors will be assigned as Yellow, Red, and Blue in the order selected.",
        "select_prompt_tab3": "Please select at least one dye from the left sidebar for comparison.",
        "err_time_data": "Time data columns are invalid.",
        "xaxis": "Process Time (min)",
        "yaxis": "Exhaustion / Fixation Rate (%)",
        "summary_hdr": ":material/dataset: Numeric Summary",
        "diag_hdr": ":material/troubleshoot: Field Diagnosis",
        "diag_excel": "**Excellent**\n\nBehaviors match closely. Low risk of tailing.",
        "diag_warn": "**Caution**\n\nMinor rate differences. Adjust temperature profile.",
        "diag_danger": "**Danger**\n\nHigh risk of tailing/face-back in bulk production.",
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
        "created_by": "Created by tskwon <span class='material-symbols-outlined' style='font-size: 14px; vertical-align: middle;'>science</span>",
        "logout_btn": ":material/logout: 로그아웃 (Logout)",
        "menu_title": "프로그램 선택",
        "tab1": "1. 요구견뢰도 매칭",
        "tab2": "2. 상용성 비교 분석",
        "tab3": "3. 통합 매칭 및 시뮬레이션",
        "instruction_text": "왼쪽 사이드바에서 원하는 염료군과 견뢰도 등급을 설정하세요.",
        "sb_group_title": "1. 염료 그룹 선택",
        "select_all": "전체 선택 / 해제",
        "sb_spec_title": "2. 요구 스펙 설정 (이상)",
        "sb_dye_select": "비교 염료 선택",
        "spec_warn": "좌측 사이드바에서 염료 그룹을 최소 하나 이상 선택해 주세요.",
        "search_res_hdr": ":material/manage_search: 견뢰도 스펙 매칭 결과",
        "search_res_sub": "검색 결과 (만족하는 염료: {count}개)",
        "search_res_desc": "**아래 표의 첫 번째 열(`선택`)을 클릭하여 비교할 염료를 선택하세요.** (최대 3개 권장)",
        "col_select": "선택",
        "col_group": "염료그룹",
        "col_name": "염료명",
        "warn_limit": "안정적인 그래프 비교를 위해 선택하신 순서대로 최대 3개까지만 표시됩니다.",
        "sim_hdr": ":material/monitoring: 선택 염료 상용성 시뮬레이션",
        "no_match": "검색 조건에 맞는 염료가 없습니다.",
        "select_prompt": "표에서 비교하고 싶은 염료의 좌측 **[선택]** 체크박스를 눌러주세요.",
        "select_prompt_tab3": "좌측 사이드바에서 비교 분석할 염료를 1개 이상 선택해 주세요.",
        "err_time_data": "상용성 시간 데이터 열(0, 5, 20...)이 올바르지 않습니다.",
        "xaxis": "공정 시간 (분)",
        "yaxis": "염착률 / 고착률 (%)",
        "summary_hdr": ":material/dataset: 수치 요약",
        "diag_hdr": ":material/troubleshoot: 현장 진단",
        "diag_excel": "**우수**\n\n거동이 거의 일치합니다. (Tailing 확률 매우 낮음)",
        "diag_warn": "**주의**\n\n구간별 미세한 속도 차이가 있습니다. 승온 조건 조절 권장.",
        "diag_danger": "**위험**\n\n대량 생산 시 불량(Tailing/Face-back) 발생 확률이 높습니다.",
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

if "lang" not in st.session_state: st.session_state.lang = "EN"
lang = st.session_state.lang
if "app_mode" not in st.session_state: st.session_state.app_mode = "tab3"

def toggle_all_groups(app_mode_str, all_groups_list):
    master_state = st.session_state[f"chk_all_{app_mode_str}"]
    for g in all_groups_list:
        st.session_state[f"grp_{g}_{app_mode_str}"] = master_state

# ==========================================
# 4. 사이드바 - 언어 및 메뉴 구성
# ==========================================
sb_col1, sb_col2 = st.sidebar.columns(2)

# 버튼 안의 🇺🇸, 🇰🇷 이모티콘을 지웠습니다! (CSS에서 이미지가 대신 들어갑니다)
if sb_col1.button("ENGLISH", use_container_width=True, type="primary" if lang == "EN" else "secondary"):
    st.session_state.lang = "EN"; st.rerun()
if sb_col2.button("KOREAN", use_container_width=True, type="primary" if lang == "KO" else "secondary"):
    st.session_state.lang = "KO"; st.rerun()

st.sidebar.markdown("---")

st.sidebar.markdown(f"**{t[lang]['menu_title']}**")

if st.sidebar.button(t[lang]["tab1"], use_container_width=True, type="primary" if st.session_state.app_mode == "tab1" else "secondary"):
    st.session_state.app_mode = "tab1"; st.rerun()
if st.sidebar.button(t[lang]["tab2"], use_container_width=True, type="primary" if st.session_state.app_mode == "tab2" else "secondary"):
    st.session_state.app_mode = "tab2"; st.rerun()
if st.sidebar.button(t[lang]["tab3"], use_container_width=True, type="primary" if st.session_state.app_mode == "tab3" else "secondary"):
    st.session_state.app_mode = "tab3"; st.rerun()

# ==========================================
# 5. 메인 화면 헤더 (로고 및 타이틀)
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
        """, unsafe_allow_html=True
    )
else:
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; margin-bottom: 1.5rem;">
            <span class='material-symbols-outlined' style='font-size: 45px; margin-right: 15px; color:#1E3A8A;'>science</span>
            <h1 style="margin: 0; padding: 0; font-size: 2.1rem; font-weight: 700;">{t[lang]["header"]}</h1>
        </div>
        """, unsafe_allow_html=True
    )

criteria_map = {'일광': 'crit_light', '땀일광(산성)': 'crit_p_light_acid', '땀일광(알칼리)': 'crit_p_light_alk', 
                '땀(산성)': 'crit_p_acid', '땀(알칼리)': 'crit_p_alk', '세탁': 'crit_wash', '염소수': 'crit_chlor'}
criteria_list = ['일광', '땀일광(산성)', '땀일광(알칼리)', '땀(산성)', '땀(알칼리)', '세탁', '염소수']

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
    
    df1 = load_spec_data()
    if df1 is None:
        st.error("`integrated_dyes_data.xlsx` 파일이 없습니다.", icon=":material/error:")
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
                max_val = 7.0 if c == '일광' else 5.0
                req1[c] = st.sidebar.slider(display_label, 1.0, max_val, 1.0, 0.5, key=f"sld_{c}_tab1")
                
        st.info(f"**{t[lang]['instruction_text']}**", icon=":material/info:")
        
        if not selected_groups1:
            st.warning(t[lang]["spec_warn"], icon=":material/warning:")
        else:
            f_df1 = df1[df1['염료그룹'].isin(selected_groups1)].copy()
            for c, min_val in req1.items():
                if c in f_df1.columns:
                    f_df1[c] = pd.to_numeric(f_df1[c], errors='coerce')
                    f_df1 = f_df1[f_df1[c] >= min_val]
                    
            st.subheader(t[lang]["search_res_hdr"])
            st.markdown(f"*{t[lang]['search_res_sub'].format(count=len(f_df1))}*")
            
            disp_cols1 = ['염료명'] + [c for c in criteria_list if c in f_df1.columns]
            st.dataframe(f_df1[disp_cols1], hide_index=True, use_container_width=True)

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
        st.error(f"`{file_to_read}` 파일이 없습니다.", icon=":material/error:")
        app2_data = None
    else:
        try:
            app2_data = parse_dye_data(file_to_read)
        except Exception as e:
            st.error(f"데이터 파싱 오류: {e}", icon=":material/error:")
            app2_data = None

    if app2_data:
        st.sidebar.markdown(f"**{t[lang]['sb_dye_select']}**")
        selected_dyes2 = []
        for sheet_name, dyes in app2_data.items():
            dye_names = [d["name"] for d in dyes]
            selections = st.sidebar.multiselect(f":material/list: {sheet_name}", options=dye_names, key=f"tab2_ms_{sheet_name}")
            for sel in selections:
                for d in dyes:
                    if d["name"] == sel: selected_dyes2.append((sheet_name, d))
                    
        st.subheader(t[lang]["sim_hdr"])
        if not selected_dyes2:
            st.info(f"{t[lang]['select_prompt_tab3']}", icon=":material/touch_app:")
        else:
            fig2 = go.Figure()
            custom_colors2 = ['#FFD700', '#FF4B4B', '#1F77B4', '#9467bd', '#2ca02c', '#ff7f0e', '#e377c2']
            
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
                legend=dict(orientation="v", yanchor="bottom", y=0.05, xanchor="right", x=0.99, font=dict(size=16), bgcolor="rgba(255, 255, 255, 0.8)", bordercolor="lightgray", borderwidth=1)
            )
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
                st.subheader(t[lang]['diag_hdr'])
                all_matrix = np.array([d["values"] for _, d in selected_dyes2])
                std_per_time = np.std(all_matrix, axis=0)
                max_dev = np.max(std_per_time)
                
                if max_dev < 5: st.success(t[lang]["diag_excel"], icon=":material/check_circle:")
                elif max_dev < 12: st.warning(t[lang]["diag_warn"], icon=":material/warning:")
                else: st.error(t[lang]["diag_danger"], icon=":material/dangerous:")

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
        st.error("`integrated_dyes_data.xlsx` 파일이 없습니다.", icon=":material/error:")
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
                max_val = 7.0 if c == '일광' else 5.0
                req3[c] = st.sidebar.slider(display_label, 1.0, max_val, 1.0, 0.5, key=f"sld_{c}_tab3")

        st.info(f"**{t[lang]['instruction_text']}**", icon=":material/info:")
        
        if not selected_groups3:
            st.warning(t[lang]["spec_warn"], icon=":material/warning:")
        else:
            f_df3 = df3[df3['염료그룹'].isin(selected_groups3)].copy()
            for c, min_val in req3.items():
                if c in f_df3.columns:
                    f_df3[c] = pd.to_numeric(f_df3[c], errors='coerce')
                    f_df3 = f_df3[f_df3[c] >= min_val]
                    
            st.subheader(t[lang]["search_res_hdr"])
            st.markdown(f"*{t[lang]['search_res_sub'].format(count=len(f_df3))}*")
            st.write(t[lang]["search_res_desc"])
            
            all_filtered_dyes = f_df3['염료명'].tolist()
            dyes_to_copy_str = ",".join(all_filtered_dyes)
            btn_text = "Copy All Dye Names" if lang == "EN" else "검색된 전체 염료명 복사하기"
            success_text = "Copied!" if lang == "EN" else "복사 완료! (프로그램 2에 붙여넣으세요)"

            button_html = f"""
            <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined" rel="stylesheet" />
            <button id="copy-btn" onclick="copyDyes()" style="
                width: 100%; background-color: #F0F2F6; color: #31333F; border: 1px solid #DCDCDC;
                padding: 10px 20px; text-align: center; font-size: 16px; font-weight: 600;
                border-radius: 8px; cursor: pointer; transition: 0.3s; display: flex;
                align-items: center; justify-content: center; gap: 8px;
            ">
                <span class="material-symbols-outlined" style="font-size: 20px;">content_copy</span>
                <span id="btn-text">{btn_text}</span>
            </button>
            <script>
                function copyDyes() {{
                    const textToCopy = "{dyes_to_copy_str}";
                    navigator.clipboard.writeText(textToCopy).then(() => {{
                        const btn = document.getElementById('copy-btn');
                        const btnText = document.getElementById('btn-text');
                        const icon = btn.querySelector('.material-symbols-outlined');
                        btn.style.backgroundColor = '#4CAF50'; btn.style.color = 'white'; btn.style.border = '1px solid #4CAF50';
                        icon.innerText = "check_circle"; btnText.innerText = "{success_text}";
                        setTimeout(() => {{
                            btn.style.backgroundColor = '#F0F2F6'; btn.style.color = '#31333F'; btn.style.border = '1px solid #DCDCDC';
                            icon.innerText = "content_copy"; btnText.innerText = "{btn_text}";
                        }}, 2000);
                    }});
                }}
            </script>
            """
            components.html(button_html, height=60)
            
            f_df3.insert(0, '선택', False)
            disp_cols3 = ['선택', '염료명'] + [c for c in criteria_list if c in f_df3.columns]
            
            col_configs3 = {
                "선택": st.column_config.CheckboxColumn(label=t[lang]["col_select"], width="small"),
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
            if len(curr_checked3) > 3: st.warning(t[lang]["warn_limit"], icon=":material/warning:")
                                      
            st.markdown("---")
            st.subheader(t[lang]["sim_hdr"])
            if not sel_dyes3:
                st.info(f"{t[lang]['select_prompt']}", icon=":material/touch_app:")
            else:
                time_pts3 = ['0', '5', '20', '25', '40', '80', '100']
                val_cols3 = [tc for tc in time_pts3 if tc in df3.columns]
                if len(val_cols3) < 2:
                    st.warning(t[lang]["err_time_data"], icon=":material/warning:")
                else:
                    fig3 = go.Figure()
                    colors = ['#FFD700', '#FF4B4B', '#1F77B4']
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
                        legend=dict(orientation="v", yanchor="bottom", y=0.05, xanchor="right", x=0.99, font=dict(size=16), bgcolor="rgba(255, 255, 255, 0.8)", bordercolor="lightgray", borderwidth=1)
                    )
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
                        st.subheader(t[lang]['diag_hdr'])
                        all_matrix = np.array([[df3[df3['염료명'] == name].iloc[0][tc] for tc in val_cols3] for name in sel_dyes3], dtype=float)
                        std_per_time = np.nanstd(all_matrix, axis=0)
                        max_dev = np.nanmax(std_per_time)
                        
                        if max_dev < 5: st.success(t[lang]["diag_excel"], icon=":material/check_circle:")
                        elif max_dev < 12: st.warning(t[lang]["diag_warn"], icon=":material/warning:")
                        else: st.error(t[lang]["diag_danger"], icon=":material/dangerous:")

# =====================================================================
# [Admin] 사용자 승인 관리 페이지
# =====================================================================
elif st.session_state.app_mode == "admin" and st.session_state.is_admin:
    st.subheader("⚙️ 사용자 승인 관리 (Admin Panel)")
    st.write("회원가입을 신청한 사용자 목록입니다. 승인 버튼을 누르면 로그인이 가능해지며, 해당 사용자에게 안내 메일이 발송됩니다.")
    
    users_df = get_users_df()
    pending_users = users_df[users_df['is_approved'] == 0]
    
    if pending_users.empty:
        st.info("승인 대기 중인 사용자가 없습니다.")
    else:
        for idx, row in pending_users.iterrows():
            username = row['username']
            name = row['name'] if 'name' in row and pd.notna(row['name']) else "이름 없음"
            email = row['e-mail'] if 'e-mail' in row and pd.notna(row['e-mail']) else ""
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**이름:** {name} &nbsp;&nbsp;|&nbsp;&nbsp; **아이디:** `{username}` &nbsp;&nbsp;|&nbsp;&nbsp; **이메일:** `{email}`")
            with col2:
                if st.button("승인하기", key=f"approve_{username}"):
                    # 해당 유저 승인 상태 업데이트
                    users_df.loc[users_df['username'] == username, 'is_approved'] = 1
                    update_users_df(users_df)
                    
                    # 자동 메일 발송 시도
                    if email:
                        mail_sent = send_approval_email(email, name, username)
                        if mail_sent:
                            st.success(f"'{name}' 님 승인 완료! (안내 메일 발송 성공)")
                        else:
                            st.warning(f"'{name}' 님 승인은 완료되었으나, 메일 발송에 실패했습니다.")
                    else:
                        st.success(f"'{name}' 님 승인 완료! (등록된 이메일이 없어 메일은 발송되지 않았습니다.)")
                    
                    st.rerun()
            st.markdown("---")

# ==========================================
# 6. 최하단 공통 요소 (관리자 메뉴, 제작자 정보, 로그아웃)
# ==========================================
st.sidebar.markdown("<br><br><br>", unsafe_allow_html=True)
st.sidebar.markdown("---")

# 관리자 계정일 경우에만 승인 메뉴를 하단에 표시
if st.session_state.is_admin:
    st.sidebar.markdown("**⚙️ 관리자 메뉴**")
    if st.sidebar.button("사용자 승인 관리", use_container_width=True, type="primary" if st.session_state.app_mode == "admin" else "secondary"):
        st.session_state.app_mode = "admin"; st.rerun()
    st.sidebar.markdown("---")

# 제작자 텍스트 표시 (구글 머티리얼 아이콘 적용)
st.sidebar.markdown(f"<p style='text-align: center; color: #888888; font-size: 13px; margin-bottom: 10px;'>{t[lang]['created_by']}</p>", unsafe_allow_html=True)

# 로그아웃 버튼
if st.sidebar.button(t[lang]["logout_btn"], use_container_width=True, type="secondary"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.is_admin = False
    st.rerun()