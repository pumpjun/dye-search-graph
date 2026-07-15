import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
import base64  # 🌟 로고 강제 밀착을 위한 도구 추가

# ==========================================
# 0. 웹페이지 기본 설정 (중복 오류 제거)
# ==========================================
st.set_page_config(page_title="오영 염료 통합 솔루션", page_icon="logo.png", layout="wide")

# ==========================================
# 1. 마스터 데이터 로드 (단일 파일)
# ==========================================
@st.cache_data
def load_master_data():
    file_name = "integrated_dyes_data.xlsx"
    if not os.path.exists(file_name):
        return None
    
    df = pd.read_excel(file_name)
    df.columns = [str(col).strip() for col in df.columns]
    return df

df = load_master_data()

# ==========================================
# 2. 메인 화면 & 스펙 매칭 파트 (HTML 로고 타이틀)
# ==========================================
if df is None:
    st.error("⚠️ `integrated_dyes_data.xlsx` 파일을 찾을 수 없습니다. 깃허브에 파일이 있는지 확인해 주세요.")
else:
    # 🌟 로고와 제목 글씨를 HTML/CSS로 강제 결합합니다.
    if os.path.exists("logo.png"):
        with open("logo.png", "rb") as f:
            img_base64 = base64.b64encode(f.read()).decode()
            
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; margin-bottom: 1.5rem;">
                <img src="data:image/png;base64,{img_base64}" width="50" style="margin-right: 15px;">
                <h1 style="margin: 0; padding: 0; font-size: 2.2rem; font-weight: 700;">오영(OHYOUNG) 염료 통합 매칭 & 상용성 솔루션</h1>
            </div>
            """, 
            unsafe_allow_html=True
        )
    else:
        st.title("🧪 오영(OHYOUNG) 염료 통합 매칭 & 상용성 솔루션")

    # --- 사이드바 UI: 필터링 조건 설정 ---
    st.sidebar.markdown("<p style='text-align: left; color: #888888; font-size: 14px; margin-bottom: 20px;'>Created by tskwon 🧑‍🔬</p>", unsafe_allow_html=True)
    
    st.sidebar.header("1. 염료 그룹 선택 (다중 체크)")
    
    if '염료그룹' in df.columns:
        all_groups = list(df['염료그룹'].dropna().unique())
    else:
        all_groups = []
        
    select_all = st.sidebar.checkbox("✅ 전체 선택 / 해제", value=True)
    st.sidebar.markdown("---")
    
    col_sb1, col_sb2 = st.sidebar.columns(2)
    selected_groups = []

    for i, group in enumerate(all_groups):
        target_col = col_sb1 if i % 2 == 0 else col_sb2
        if target_col.checkbox(str(group), value=select_all):
            selected_groups.append(group)

    st.sidebar.markdown("---")
    st.sidebar.header("2. 요구 스펙 설정 (이상)")
    
    criteria = ['일광', '땀일광(산성)', '땀일광(알칼리)', '땀(산성)', '땀(알칼리)', '세탁', '염소수']
    requirements = {}
    for c in criteria:
        if c in df.columns:
            requirements[c] = st.sidebar.slider(c, 1.0, 6.0, 1.0, 0.5)

    # --- 데이터 필터링 및 표 선택 기능 ---
    st.header("🔍 1. 견뢰도 스펙 매칭 결과")
    
    if not selected_groups:
        st.warning("⚠️ 좌측에서 염료 그룹을 최소 하나 이상 선택해 주세요.")
        filtered_df = pd.DataFrame()
        selected_dye_names = []
    else:
        filtered_df = df[df['염료그룹'].isin(selected_groups)].copy()
        for criterion, min_value in requirements.items():
            if criterion in filtered_df.columns:
                filtered_df[criterion] = pd.to_numeric(filtered_df[criterion], errors='coerce')
                filtered_df = filtered_df[filtered_df[criterion] >= min_value]

        # ... 기존 코드 ...
        st.subheader(f"✨ 검색 결과 (만족하는 염료: {len(filtered_df)}개)")
        st.write("💡 **아래 표의 첫 번째 열(`선택`)의 체크박스를 클릭하여 비교할 염료를 선택하세요.** (최대 3개 권장)")
        
        filtered_df.insert(0, '선택', False)
        display_cols = ['선택', '염료그룹', '염료명'] + [c for c in criteria if c in filtered_df.columns]
        
        # 🌟 컬럼 설정 (원래 이름 유지, 가로 길이 80픽셀로 통일)
        col_configs = {
            "선택": st.column_config.CheckboxColumn(width="small"),
            "염료그룹": st.column_config.TextColumn(width=100),
            "염료명": st.column_config.TextColumn(width=150)
        }
        
        # 스펙 항목(일광, 땀일광 등)의 너비를 80으로 고정
        for c in display_cols[3:]:
            col_configs[c] = st.column_config.NumberColumn(width=80)
        
        # 🌟 [수정] 클릭 순서를 저장할 세션 상태 초기화
        if "selected_order" not in st.session_state:
            st.session_state.selected_order = []

        edited_df = st.data_editor(
            filtered_df[display_cols],  # 원본 이름 그대로 사용
            hide_index=True,
            use_container_width=True,
            column_config=col_configs,
            disabled=[col for col in display_cols if col != '선택']
        )
        
        # 현재 체크박스가 켜져 있는 염료 목록 (표 순서대로 가져옴)
        currently_checked = edited_df[edited_df['선택'] == True]['염료명'].tolist()
        # ... 이하 기존 코드 유지 ...
        
        # 🌟 [수정] 클릭 순서 동기화 로직
        # 1. 체크 해제된 항목은 세션 순서 목록에서 제거
        st.session_state.selected_order = [
            dye for dye in st.session_state.selected_order if dye in currently_checked
        ]
        # 2. 새로 체크된 항목은 세션 순서 목록의 맨 뒤에 추가 (클릭 순서대로 쌓임)
        for dye in currently_checked:
            if dye not in st.session_state.selected_order:
                st.session_state.selected_order.append(dye)
        
        # 최종적으로 클릭 순서대로 정렬된 리스트에서 최대 3개 선택
        selected_dye_names = st.session_state.selected_order[:3]
        
        if len(currently_checked) > 3:
            st.warning("⚠️ 안정적인 그래프 비교를 위해 선택하신 순서대로 최대 3개까지만 표시됩니다.")

    # ==========================================
    # 3. 상용성 그래프 시뮬레이션 파트 (다이렉트 연동)
    # ==========================================
    st.markdown("---")
    st.header("📈 2. 선택 염료 상용성 (Compatibility) 시뮬레이션")

    if filtered_df.empty:
        st.info("💡 위의 검색 조건에 맞는 염료가 없습니다.")
    elif not selected_dye_names:
        st.info("👆 위 검색 결과 표에서 비교하고 싶은 염료의 좌측 **[선택]** 체크박스를 눌러주세요.")
    else:
        time_points = ['0', '5', '20', '25', '40', '80', '100']
        valid_time_cols = [t for t in time_points if t in df.columns]
        
        if len(valid_time_cols) < 2:
            st.warning("⚠️ 엑셀 파일에 상용성 시간 데이터(0, 5, 20... 열)가 제대로 입력되지 않았습니다.")
        else:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                fig = go.Figure()
                # 클릭 순서대로 할당될 색상 설정 (1번째: 노랑, 2번째: 빨강, 3번째: 파랑)
                custom_colors = ['#FFD700', '#FF4B4B', '#1F77B4']
                
                for idx, name in enumerate(selected_dye_names):
                    dye_row = df[df['염료명'] == name].iloc[0]
                    group_name = dye_row['염료그룹']
                    color = custom_colors[idx % len(custom_colors)]
                    label = f"[{group_name}] {name}"
                    
                    t1 = [t for t in valid_time_cols if int(t) <= 20]
                    v1 = [dye_row[t] for t in t1]
                    
                    t2 = [t for t in valid_time_cols if int(t) >= 25]
                    v2 = [dye_row[t] for t in t2]
                    
                    fig.add_trace(go.Scatter(
                        x=t1, y=v1, mode='lines', name=label, legendgroup=label,
                        line=dict(width=3, color=color, shape='spline'),
                        hovertemplate='%{x}분: <b>%{y}%</b><extra></extra>'
                    ))
                    fig.add_trace(go.Scatter(
                        x=t2, y=v2, mode='lines', name=label, legendgroup=label, showlegend=False,
                        line=dict(width=3, color=color, shape='spline'),
                        hovertemplate='%{x}분: <b>%{y}%</b><extra></extra>'
                    ))
                    
                fig.update_layout(
                    xaxis_title="공정 시간 (분)",
                    yaxis_title="염착률 / 고착률 (%)",
                    xaxis=dict(tickmode='array', tickvals=[int(t) for t in valid_time_cols]),
                    yaxis=dict(range=[0, 105]),
                    hovermode="x unified",
                    margin=dict(l=40, r=40, t=20, b=40),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                fig.add_vline(x=20, line_dash="dash", line_color="gray")
                fig.add_vline(x=25, line_dash="dash", line_color="gray")
                st.plotly_chart(fig, use_container_width=True)
                
            with col2:
                st.subheader("📋 수치 요약")
                table_data = []
                # 수치 요약 표도 그래프와 일관되게 클릭한 순서대로 출력하도록 수정
                for name in selected_dye_names:
                    dye_row = df[df['염료명'] == name].iloc[0]
                    row_dict = {"염료명": name}
                    for t in valid_time_cols:
                        val = dye_row[t]
                        row_dict[f"{t}분"] = f"{val:.1f}%" if pd.notna(val) else "-"
                    table_data.append(row_dict)
                st.dataframe(pd.DataFrame(table_data), hide_index=True)
                
                if len(selected_dye_names) >= 2:
                    st.markdown("---")
                    st.markdown("#### 🔍 현장 진단")
                    
                    valid_values = []
                    for name in selected_dye_names:
                        dye_row = df[df['염료명'] == name].iloc[0]
                        valid_values.append([dye_row[t] for t in valid_time_cols])
                        
                    all_matrix = np.array(valid_values, dtype=float)
                    std_per_time = np.nanstd(all_matrix, axis=0)
                    max_deviation = np.nanmax(std_per_time)
                    
                    if max_deviation < 5:
                        st.success("✅ **우수**\n\n거동이 거의 일치합니다.")
                    elif max_deviation < 12:
                        st.warning("⚠️ **주의**\n\n구간별 미세한 속도 차이가 있습니다.")
                    else:
                        st.error("🚨 **위험**\n\n대량 생산 시 불량 발생 확률이 높습니다.")