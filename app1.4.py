import streamlit as st
import pandas as pd
import json
import os
import time
import colorsys
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components

# ==========================================
# 1. System Initialization & Data Foundation
# ==========================================
st.set_page_config(page_title="Focus", layout="wide", initial_sidebar_state="expanded")

DATA_FILE = "learning_logs.csv"
CONFIG_FILE = "subjects.json"

def init_system():
    if not os.path.exists(CONFIG_FILE):
        default_config = {
            "theme_color": "#007AFF",
            "subjects": {
                "Engineering": {
                    "target_hours": 100,
                    "children": {
                        "System Design": {"target_hours": 40},
                        "Algorithms": {"target_hours": 60}
                    }
                },
                "Design": {
                    "target_hours": 50,
                    "children": {}
                }
            }
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(default_config, f, ensure_ascii=False, indent=4)
            
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=["timestamp", "parent_subject", "child_subject", "duration_minutes", "focus_score"])
        df.to_csv(DATA_FILE, index=False, encoding="utf-8")

init_system()

def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(new_config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(new_config, f, ensure_ascii=False, indent=4)

config = load_config()

def get_parent_target(parent_name):
    parent_data = config["subjects"].get(parent_name, {})
    children = parent_data.get("children", {})
    if not children:
        return parent_data.get("target_hours", 1)
    return sum(child_data.get("target_hours", 1) for child_data in children.values())

def get_focus_score(minutes):
    if minutes < 5: return 1
    elif minutes <= 15: return 2
    elif minutes <= 30: return 3
    elif minutes <= 45: return 4
    else: return 5

def update_csv_history(col_name, old_val, new_val):
    df_temp = pd.read_csv(DATA_FILE)
    if not df_temp.empty:
        df_temp.loc[df_temp[col_name] == old_val, col_name] = new_val
        df_temp.to_csv(DATA_FILE, index=False, encoding="utf-8")

# ==========================================
# 2. Visual Standards & CSS Injection
# ==========================================
def generate_palette(base_hex, n=5):
    base_hex = base_hex.lstrip('#')
    if len(base_hex) != 6: base_hex = "007AFF"
    r, g, b = tuple(int(base_hex[i:i+2], 16)/255.0 for i in (0, 2, 4))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    palette =[]
    for i in range(n):
        new_l = max(0.3, min(0.8, l + (i - n/2) * 0.12))
        nr, ng, nb = colorsys.hls_to_rgb(h, new_l, s)
        palette.append(f"#{int(nr*255):02x}{int(ng*255):02x}{int(nb*255):02x}")
    return palette

theme_color = config.get("theme_color", "#007AFF")
palette = generate_palette(theme_color, max(len(config["subjects"]), 5))

st.markdown(f"""
<style>
    :root {{
        --theme-color: {theme_color};
        --bg-color: #F5F5F7;
        --surface-color: #FFFFFF;
        --text-main: #1D1D1F;
        --text-muted: #86868B;
        --glass-bg: rgba(255, 255, 255, 0.7);
    }}
    
    #MainMenu, header, footer {{visibility: hidden;}}
    
    .stApp {{
        background-color: var(--bg-color);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: var(--text-main);
    }}

    /* Buttons */
    .stButton > button {{
        border-radius: 20px !important;
        border: 1px solid rgba(0,0,0,0.05) !important;
        background: var(--surface-color) !important;
        color: var(--text-main) !important;
        font-weight: 600 !important;
        padding: 10px 24px !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.02) !important;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
    }}
    .stButton > button:hover {{
        background: var(--theme-color) !important;
        color: #FFFFFF !important;
        border-color: var(--theme-color) !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.08) !important;
    }}

    /* Glassmorphism KPI Cards */
    .kpi-card {{
        background: var(--glass-bg);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: 24px;
        border: 1px solid rgba(255,255,255,0.4);
        border-left: 6px solid var(--theme-color);
        padding: 24px 32px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.04);
        display: flex;
        flex-direction: column;
        justify-content: center;
        height: 140px;
        margin-bottom: 24px;
        transition: transform 0.3s ease;
    }}
    .kpi-card:hover {{ transform: translateY(-3px); }}
    .kpi-title {{ color: var(--text-muted); font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }}
    .kpi-value {{ color: var(--theme-color); font-size: 2.8rem; font-weight: 700; line-height: 1; letter-spacing: -1px; }}
    .kpi-value span {{ font-size: 1.2rem; color: var(--text-muted); margin-left: 6px; font-weight: 500; letter-spacing: 0; }}

    /* Gallery Cards */
    .gallery-card {{
        background: var(--surface-color);
        border-radius: 24px;
        padding: 28px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.03);
        margin-bottom: 12px;
        border: 1px solid rgba(0,0,0,0.02);
    }}
    .gc-header {{ display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 20px; }}
    .gc-title-wrap {{ display: flex; align-items: center; gap: 12px; }}
    .gc-icon {{ width: 40px; height: 40px; border-radius: 12px; display: flex; align-items: center; justify-content: center; color: white; font-weight: 600; font-size: 1.2rem; }}
    .gc-title {{ font-size: 1.3rem; font-weight: 600; color: var(--text-main); line-height: 1; }}
    .gc-stats {{ font-size: 0.95rem; color: var(--text-muted); font-weight: 500; }}
    .progress-track {{ width: 100%; height: 8px; background: rgba(0,0,0,0.04); border-radius: 4px; overflow: hidden; }}
    .progress-fill {{ height: 100%; border-radius: 4px; transition: width 1s cubic-bezier(0.25, 0.8, 0.25, 1); }}
    
    /* Child Progress */
    .child-row {{ margin-top: 16px; padding-top: 16px; border-top: 1px solid rgba(0,0,0,0.04); }}
    .child-label {{ display: flex; justify-content: space-between; font-size: 0.85rem; color: var(--text-muted); margin-bottom: 6px; font-weight: 500; }}
    
    /* Chart Containers */
    .chart-card {{
        background: var(--surface-color);
        border-radius: 24px;
        padding: 24px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.03);
        margin-bottom: 24px;
        border: 1px solid rgba(0,0,0,0.02);
    }}
    
    /* Typography */
    .section-title {{ font-size: 1.2rem; font-weight: 600; color: var(--text-main); margin-bottom: 20px; letter-spacing: -0.3px; }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. State Management
# ==========================================
if 'timer_state' not in st.session_state: st.session_state.timer_state = 'idle'
if 'start_time' not in st.session_state: st.session_state.start_time = None

# ==========================================
# 4. Sidebar: Modular Laboratory
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='font-weight: 600; margin-bottom: 32px; letter-spacing: -0.5px;'>Laboratory</h2>", unsafe_allow_html=True)
    
    new_color = st.color_picker("Theme Color", theme_color)
    if new_color != theme_color:
        config["theme_color"] = new_color
        save_config(config)
        st.rerun()
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Block 1: Create
    with st.expander("Create Subject", expanded=False):
        st.markdown("<div style='font-size: 0.85rem; color: #86868B; margin-bottom: 8px;'>New Parent Subject</div>", unsafe_allow_html=True)
        new_parent = st.text_input("Name", key="c_p_name", label_visibility="collapsed", placeholder="Subject Name")
        new_p_target = st.number_input("Target (Hours)", min_value=1, value=50, key="c_p_target")
        if st.button("Add Subject", use_container_width=True) and new_parent:
            if new_parent not in config["subjects"]:
                config["subjects"][new_parent] = {"target_hours": new_p_target, "children": {}}
                save_config(config)
                st.rerun()
                
        st.markdown("<hr style='margin: 16px 0; border: none; border-top: 1px solid #E5E5EA;'>", unsafe_allow_html=True)
        
        st.markdown("<div style='font-size: 0.85rem; color: #86868B; margin-bottom: 8px;'>New Child Task</div>", unsafe_allow_html=True)
        if config["subjects"]:
            sel_p_for_c = st.selectbox("Parent", list(config["subjects"].keys()), key="c_c_parent", label_visibility="collapsed")
            new_child = st.text_input("Task Name", key="c_c_name", label_visibility="collapsed", placeholder="Task Name")
            new_c_target = st.number_input("Task Target (Hours)", min_value=1, value=10, key="c_c_target")
            if st.button("Add Task", use_container_width=True) and new_child:
                if new_child not in config["subjects"][sel_p_for_c]["children"]:
                    config["subjects"][sel_p_for_c]["children"][new_child] = {"target_hours": new_c_target}
                    save_config(config)
                    st.rerun()

    # Block 2: Modify
    with st.expander("Modify Subject", expanded=False):
        if config["subjects"]:
            mod_type = st.radio("Type", ["Parent", "Child"], horizontal=True, label_visibility="collapsed")
            if mod_type == "Parent":
                mod_p = st.selectbox("Select Subject", list(config["subjects"].keys()), key="m_p_sel")
                new_rn_name = st.text_input("Rename To", value=mod_p, key="m_p_rn")
                has_children = len(config["subjects"][mod_p]["children"]) > 0
                new_rn_target = st.number_input("New Target", min_value=1, value=config["subjects"][mod_p].get("target_hours", 50), key="m_p_tg", disabled=has_children)
                if has_children:
                    st.caption("Target is auto-calculated from children.")
                
                if st.button("Save Changes", key="m_p_btn", use_container_width=True):
                    if new_rn_name != mod_p:
                        config["subjects"][new_rn_name] = config["subjects"].pop(mod_p)
                        update_csv_history("parent_subject", mod_p, new_rn_name)
                    if not has_children:
                        config["subjects"][new_rn_name]["target_hours"] = new_rn_target
                    save_config(config)
                    st.rerun()
            else:
                mod_p_c = st.selectbox("Select Parent", list(config["subjects"].keys()), key="m_c_p_sel")
                children_list = list(config["subjects"][mod_p_c]["children"].keys())
                if children_list:
                    mod_c = st.selectbox("Select Task", children_list, key="m_c_sel")
                    new_c_name = st.text_input("Rename To", value=mod_c, key="m_c_rn")
                    new_c_tg = st.number_input("New Target", min_value=1, value=config["subjects"][mod_p_c]["children"][mod_c].get("target_hours", 10), key="m_c_tg")
                    
                    if st.button("Save Changes", key="m_c_btn", use_container_width=True):
                        if new_c_name != mod_c:
                            config["subjects"][mod_p_c]["children"][new_c_name] = config["subjects"][mod_p_c]["children"].pop(mod_c)
                            update_csv_history("child_subject", mod_c, new_c_name)
                        config["subjects"][mod_p_c]["children"][new_c_name]["target_hours"] = new_c_tg
                        save_config(config)
                        st.rerun()

    # Block 3: Delete
    with st.expander("Delete Subject", expanded=False):
        if config["subjects"]:
            del_type = st.radio("Type to Delete",["Parent", "Child"], horizontal=True, label_visibility="collapsed")
            if del_type == "Parent":
                del_p = st.selectbox("Select Subject", list(config["subjects"].keys()), key="d_p_sel")
                if st.button("Confirm Delete", key="d_p_btn", use_container_width=True):
                    del config["subjects"][del_p]
                    save_config(config)
                    st.rerun()
            else:
                del_p_c = st.selectbox("Select Parent", list(config["subjects"].keys()), key="d_c_p_sel")
                children_list = list(config["subjects"][del_p_c]["children"].keys())
                if children_list:
                    del_c = st.selectbox("Select Task", children_list, key="d_c_sel")
                    if st.button("Confirm Delete", key="d_c_btn", use_container_width=True):
                        del config["subjects"][del_p_c]["children"][del_c]
                        save_config(config)
                        st.rerun()

# ==========================================
# 5. Data Processing
# ==========================================
df = pd.read_csv(DATA_FILE)
df['timestamp'] = pd.to_datetime(df['timestamp'])
now = datetime.now()

# ==========================================
# 6. Central Core L1: Visual Balance Console
# ==========================================
col_l1_left, col_l1_center, col_l1_right = st.columns([1.5, 2, 1.5])

with col_l1_right:
    st.markdown("<div style='height: 36px;'></div>", unsafe_allow_html=True)
    time_filter = st.radio("Dimension", ["Today", "Week", "Month", "Year"], horizontal=True, label_visibility="collapsed")

if time_filter == "Today":
    filtered_df = df[df['timestamp'].dt.date == now.date()]
elif time_filter == "Week":
    start_of_week = now - timedelta(days=now.weekday())
    filtered_df = df[df['timestamp'].dt.date >= start_of_week.date()]
elif time_filter == "Month":
    filtered_df = df[(df['timestamp'].dt.year == now.year) & (df['timestamp'].dt.month == now.month)]
else:
    filtered_df = df[df['timestamp'].dt.year == now.year]

with col_l1_left:
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    parent_subjects = list(config["subjects"].keys())
    if not parent_subjects:
        st.warning("Configure subjects in Laboratory.")
        sel_parent, sel_child = None, None
    else:
        sel_parent = st.selectbox("Subject", parent_subjects, disabled=(st.session_state.timer_state != 'idle'), label_visibility="collapsed")
        child_dict = config["subjects"][sel_parent]["children"]
        child_list = list(child_dict.keys())
        sel_child = st.selectbox("Task", child_list if child_list else ["General"], disabled=(st.session_state.timer_state != 'idle'), label_visibility="collapsed")

with col_l1_center:
    if not parent_subjects:
        st.markdown("<div style='text-align: center; color: #86868B; margin-top: 40px;'>Awaiting Configuration</div>", unsafe_allow_html=True)
    else:
        if st.session_state.timer_state == 'idle':
            st.markdown(f"""
                <div style="text-align: center; font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 4rem; font-weight: 300; color: var(--text-main); line-height: 1; margin-bottom: 16px; letter-spacing: -2px;">
                    00:00:00
                </div>
            """, unsafe_allow_html=True)
            
            c_btn1, c_btn2, c_btn3 = st.columns([1, 2, 1])
            with c_btn2:
                if st.button("Start Session", use_container_width=True):
                    st.session_state.start_time = time.time()
                    st.session_state.timer_state = 'running'
                    st.rerun()
                    
        elif st.session_state.timer_state == 'running':
            start_ms = st.session_state.start_time * 1000
            timer_html = f"""
            <style>
                @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300&display=swap');
                body {{ margin: 0; display: flex; justify-content: center; background: transparent; color: {theme_color}; font-family: 'JetBrains Mono', monospace; font-size: 4rem; font-weight: 300; line-height: 1; letter-spacing: -2px; }}
            </style>
            <div id="timer">00:00:00</div>
            <script>
                var start = {start_ms};
                setInterval(function() {{
                    var delta = Date.now() - start;
                    var h = Math.floor(delta / 3600000);
                    var m = Math.floor((delta % 3600000) / 60000);
                    var s = Math.floor((delta % 60000) / 1000);
                    document.getElementById('timer').innerText = 
                        String(h).padStart(2, '0') + ':' + String(m).padStart(2, '0') + ':' + String(s).padStart(2, '0');
                }}, 1000);
            </script>
            """
            components.html(timer_html, height=70)
            
            c_btn1, c_btn2, c_btn3 = st.columns([1, 2, 1])
            with c_btn2:
                if st.button("End Session", use_container_width=True):
                    elapsed_sec = time.time() - st.session_state.start_time
                    elapsed_min = round(elapsed_sec / 60, 2)
                    score = get_focus_score(elapsed_min)
                    
                    new_log = pd.DataFrame([{
                        "timestamp": datetime.now().isoformat(),
                        "parent_subject": sel_parent,
                        "child_subject": sel_child,
                        "duration_minutes": elapsed_min,
                        "focus_score": score
                    }])
                    new_log.to_csv(DATA_FILE, mode='a', header=False, index=False, encoding="utf-8")
                    
                    st.session_state.timer_state = 'idle'
                    st.rerun()

st.markdown("<div style='height: 32px;'></div>", unsafe_allow_html=True)

# ==========================================
# 7. Central Core L2: Textured KPIs
# ==========================================
total_minutes = filtered_df['duration_minutes'].sum() if not filtered_df.empty else 0
total_hours = total_minutes / 60
active_subjects = filtered_df['parent_subject'].nunique() if not filtered_df.empty else 0
avg_score = filtered_df['focus_score'].mean() if not filtered_df.empty else 0.0

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f"""<div class="kpi-card"><div class="kpi-title">Duration</div><div class="kpi-value">{total_hours:.1f}<span>h</span></div></div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="kpi-card"><div class="kpi-title">Subjects Active</div><div class="kpi-value">{active_subjects}<span></span></div></div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div class="kpi-card"><div class="kpi-title">Focus Quality</div><div class="kpi-value">{avg_score:.1f}<span>pts</span></div></div>""", unsafe_allow_html=True)

# ==========================================
# 8. Central Core L3: Full Gallery & Insights
# ==========================================
col_l3_left, col_l3_right = st.columns([1.5, 1], gap="large")

with col_l3_left:
    st.markdown("<div class='section-title'>Subject Gallery</div>", unsafe_allow_html=True)
    
    parent_group = filtered_df.groupby('parent_subject')['duration_minutes'].sum() if not filtered_df.empty else pd.Series()
    
    for idx, (parent, details) in enumerate(config["subjects"].items()):
        target_h = get_parent_target(parent)
        current_m = parent_group.get(parent, 0)
        current_h = current_m / 60
        progress_pct = min((current_h / target_h) * 100, 100) if target_h > 0 else 0
        card_color = palette[idx % len(palette)]
        initial = parent[0].upper() if parent else "S"
        
        st.markdown(f"""
        <div class="gallery-card">
            <div class="gc-header">
                <div class="gc-title-wrap">
                    <div class="gc-icon" style="background-color: {card_color};">{initial}</div>
                    <div class="gc-title">{parent}</div>
                </div>
                <div class="gc-stats">{current_h:.1f}h / {target_h}h</div>
            </div>
            <div class="progress-track">
                <div class="progress-fill" style="width: {progress_pct}%; background-color: {card_color};"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        children = details.get("children", {})
        if children:
            with st.expander(f"View {parent} Details"):
                child_df = filtered_df[filtered_df['parent_subject'] == parent] if not filtered_df.empty else pd.DataFrame()
                child_group = child_df.groupby('child_subject')['duration_minutes'].sum() if not child_df.empty else pd.Series()
                
                html_children = ""
                for child, c_details in children.items():
                    c_target_h = c_details.get("target_hours", 1)
                    c_current_m = child_group.get(child, 0)
                    c_current_h = c_current_m / 60
                    c_pct = min((c_current_h / c_target_h) * 100, 100) if c_target_h > 0 else 0
                    
                    html_children += f"""
                    <div class="child-row">
                        <div class="child-label">
                            <span>{child}</span>
                            <span>{c_current_h:.1f}h / {c_target_h}h</span>
                        </div>
                        <div class="progress-track" style="height: 4px;">
                            <div class="progress-fill" style="width: {c_pct}%; background-color: {card_color}; opacity: 0.8;"></div>
                        </div>
                    </div>
                    """
                st.markdown(html_children, unsafe_allow_html=True)

with col_l3_right:
    st.markdown("<div class='section-title'>Insights</div>", unsafe_allow_html=True)
    
    yesterday_df = df[df['timestamp'].dt.date == (now.date() - timedelta(days=1))]
    y_hours = yesterday_df['duration_minutes'].sum() / 60 if not yesterday_df.empty else 0
    t_hours = df[df['timestamp'].dt.date == now.date()]['duration_minutes'].sum() / 60 if not df.empty else 0
    
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = t_hours,
        title = {'text': "Today vs Yesterday (h)", 'font': {'size': 13, 'color': '#86868B'}},
        delta = {'reference': y_hours, 'increasing': {'color': theme_color}},
        gauge = {
            'axis': {'range':[None, max(t_hours, y_hours, 8)], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': theme_color},
            'bgcolor': "#F5F5F7",
            'borderwidth': 0,
            'threshold': {'line': {'color': "#86868B", 'width': 2}, 'thickness': 0.75, 'value': y_hours}
        }
    ))
    fig_gauge.update_layout(height=200, margin=dict(l=20, r=20, t=30, b=10), paper_bgcolor='rgba(0,0,0,0)', font={'family': "-apple-system, sans-serif"})
    st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False})
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    if not filtered_df.empty:
        fig_pie = px.pie(filtered_df, names='parent_subject', values='duration_minutes', hole=0.75, color_discrete_sequence=palette)
        fig_pie.update_traces(textposition='inside', textinfo='percent', marker=dict(line=dict(color='#FFFFFF', width=2)))
        fig_pie.update_layout(
            showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
            height=240, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)', font={'family': "-apple-system, sans-serif"}
        )
        fig_pie.add_annotation(text=f"<b>{total_hours:.1f}h</b>", x=0.5, y=0.5, font_size=22, showarrow=False, font_color="#1D1D1F")
        st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})
    else:
        st.markdown("<div style='height: 240px; display: flex; align-items: center; justify-content: center; color: var(--text-muted);'>No data available</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 9. Central Core L4: Calendar Year Heatmap
# ==========================================
st.markdown("<div class='section-title' style='margin-top: 16px;'>Annual Activity</div>", unsafe_allow_html=True)
st.markdown("<div class='chart-card'>", unsafe_allow_html=True)

curr_year = now.year
start_date = datetime(curr_year, 1, 1).date()
end_date = datetime(curr_year, 12, 31).date()
date_range = pd.date_range(start=start_date, end=end_date)

heatmap_df = pd.DataFrame({'date': date_range})
heatmap_df['date_str'] = heatmap_df['date'].dt.strftime('%Y-%m-%d')

if not df.empty:
    df['date_str'] = df['timestamp'].dt.strftime('%Y-%m-%d')
    daily_sum = df.groupby('date_str')['duration_minutes'].sum().reset_index()
    heatmap_df = pd.merge(heatmap_df, daily_sum, on='date_str', how='left').fillna(0)
else:
    heatmap_df['duration_minutes'] = 0

# Calculate week index relative to the start of the year to ensure a clean 0-52 grid
heatmap_df['day_of_year'] = heatmap_df['date'].dt.dayofyear
heatmap_df['x'] = (heatmap_df['day_of_year'] - 1) // 7
heatmap_df['y'] = heatmap_df['date'].dt.weekday

fig_heat = go.Figure(data=go.Heatmap(
    z=heatmap_df['duration_minutes'],
    x=heatmap_df['x'],
    y=heatmap_df['y'],
    colorscale=[[0, '#E5E5EA'],[1, theme_color]],
    xgap=4, ygap=4,
    showscale=False,
    hoverinfo='text',
    text=heatmap_df['date_str'] + '<br>Duration: ' + heatmap_df['duration_minutes'].astype(str) + ' min'
))

fig_heat.update_layout(
    height=160,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    margin=dict(t=10, b=20, l=30, r=10),
    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    yaxis=dict(
        showgrid=False, zeroline=False, 
        tickmode='array', tickvals=[0, 2, 4, 6], 
        ticktext=['Mon', 'Wed', 'Fri', 'Sun'], 
        autorange='reversed',
        tickfont=dict(color="#86868B", family="-apple-system, sans-serif")
    )
)
st.plotly_chart(fig_heat, use_container_width=True, config={'displayModeBar': False})
st.markdown("</div>", unsafe_allow_html=True)