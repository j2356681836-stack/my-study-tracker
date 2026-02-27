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
# 2. Extreme Liquid Glass Perfection & CSS
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

# Deep Liquid Glass Gradient
bg_gradient = f"linear-gradient(135deg, {theme_color}33 0%, #cfd9df 50%, #e2ebf0 100%)"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@300;400;600;700&display=swap');

    :root {{
        --theme-color: {theme_color};
        --text-main: #1D1D1F;
        --text-muted: #5A5A5E;
        --glass-bg: rgba(255, 255, 255, 0.4);
        --glass-border: rgba(255, 255, 255, 0.3);
        --glass-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
    }}
    
    #MainMenu, header, footer {{visibility: hidden;}}
    
    /* Global Extreme Liquid Glass Background */
    .stApp {{
        background: {bg_gradient} !important;
        background-attachment: fixed !important;
        font-family: 'Inter', sans-serif;
        color: var(--text-main);
    }}

    /* Aggressively Eradicate White Blocks & Bars */
    .st-emotion-cache-1wivap2, .st-emotion-cache-1104q3y, .st-emotion-cache-16txtl3, 
    .st-emotion-cache-1y4p8pa, .st-emotion-cache-1n76uvr, .st-emotion-cache-18ni7ap,
    .st-emotion-cache-1jicfl2, .st-emotion-cache-1dp5vir, .st-emotion-cache-1v0mbdj,
    [data-testid="stVerticalBlock"], [data-testid="stHorizontalBlock"],
    [data-testid="stVerticalBlockBorderWrapper"], [data-testid="stHeader"],[data-testid="stMarkdownContainer"], div[data-testid="stMetric"] {{
        background: transparent !important;
        background-color: transparent !important;
    }}
    
    /* Universal Glass Card */
    .glass-card {{
        background: var(--glass-bg) !important;
        backdrop-filter: blur(30px) saturate(150%) !important;
        -webkit-backdrop-filter: blur(30px) saturate(150%) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 28px !important;
        padding: 28px !important;
        box-shadow: var(--glass-shadow) !important;
        margin-bottom: 24px !important;
        transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    .glass-card:hover {{ transform: translateY(-4px); }}

    /* KPI Typography */
    .kpi-container {{ display: flex; flex-direction: column; justify-content: center; height: 140px; text-align: center; }}
    .kpi-title {{ color: var(--text-muted); font-size: 0.95rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 8px; }}
    .kpi-value {{ color: var(--theme-color); font-family: 'Outfit', sans-serif; font-size: 3.8rem; font-weight: 700; line-height: 1; letter-spacing: -1.5px; text-shadow: 0 4px 16px rgba(255,255,255,0.4); }}
    .kpi-value span {{ font-size: 1.2rem; color: var(--text-muted); margin-left: 6px; font-weight: 500; letter-spacing: 0; text-shadow: none; }}

    /* Buttons */
    .stButton > button {{
        background: var(--glass-bg) !important;
        backdrop-filter: blur(30px) saturate(150%) !important;
        -webkit-backdrop-filter: blur(30px) saturate(150%) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 28px !important;
        color: var(--text-main) !important;
        font-weight: 600 !important;
        padding: 12px 28px !important;
        box-shadow: var(--glass-shadow) !important;
        transition: all 0.3s ease !important;
    }}
    .stButton > button:hover {{
        background: var(--theme-color) !important;
        color: #FFFFFF !important;
        border-color: var(--theme-color) !important;
        transform: scale(1.02);
    }}

    /* Expander as Glass Card (Gallery & Sidebar) */[data-testid="stExpander"] {{
        background: var(--glass-bg) !important;
        backdrop-filter: blur(30px) saturate(150%) !important;
        -webkit-backdrop-filter: blur(30px) saturate(150%) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 28px !important;
        box-shadow: var(--glass-shadow) !important;
        overflow: hidden;
        margin-bottom: 20px;
    }}
    [data-testid="stExpander"] details {{ border: none !important; background: transparent !important; }}
    [data-testid="stExpander"] summary {{
        padding: 24px 28px !important;
        border: none !important;
        background: transparent !important;
        font-family: 'Inter', sans-serif;
        font-size: 1.15rem;
        font-weight: 600;
        color: var(--text-main);
    }}
    [data-testid="stExpander"] summary:hover {{ color: var(--theme-color); }}
    [data-testid="stExpander"] div[role="region"] {{ background: transparent !important; padding: 0 28px 28px 28px !important; }}

    /* Custom Progress Bars */
    .pg-track {{ width: 100%; height: 6px; background: rgba(255,255,255,0.5); border-radius: 3px; overflow: hidden; margin: 12px 0; box-shadow: inset 0 1px 3px rgba(0,0,0,0.05); }}
    .pg-fill {{ height: 100%; border-radius: 3px; transition: width 1s ease; background-color: var(--theme-color); }}
    .pg-label {{ display: flex; justify-content: space-between; font-size: 0.85rem; color: var(--text-muted); font-weight: 600; }}

    /* Typography */
    .section-title {{ font-family: 'Outfit', sans-serif; font-size: 1.5rem; font-weight: 600; color: var(--text-main); margin-bottom: 24px; letter-spacing: -0.5px; }}
    
    /* Radio Buttons (Time Filter) & Alignment */
    [data-testid="stRadio"] > div {{ display: flex; justify-content: flex-end; }}
    div[role="radiogroup"] {{ justify-content: flex-end; gap: 16px; }}
    div[role="radio"][aria-checked="true"] > div:first-child > div {{ background-color: var(--theme-color) !important; }}
    div[role="radio"][aria-checked="true"] > div:first-child {{ border-color: var(--theme-color) !important; }}
    
    /* Sidebar Glass */
    [data-testid="stSidebar"] {{
        background: rgba(255, 255, 255, 0.25) !important;
        backdrop-filter: blur(40px) saturate(150%) !important;
        -webkit-backdrop-filter: blur(40px) saturate(150%) !important;
        border-right: 1px solid var(--glass-border) !important;
    }}
    
    /* Dialog Glass */
    div[data-testid="stDialog"] > div {{
        background: rgba(255, 255, 255, 0.6) !important;
        backdrop-filter: blur(40px) saturate(150%) !important;
        -webkit-backdrop-filter: blur(40px) saturate(150%) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 28px !important;
        box-shadow: 0 20px 60px rgba(0,0,0,0.1) !important;
    }}
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
    st.markdown("<h2 style='font-family: Outfit; font-weight: 600; margin-bottom: 32px; letter-spacing: -0.5px;'>Laboratory</h2>", unsafe_allow_html=True)
    
    new_color = st.color_picker("Theme Color", theme_color)
    if new_color != theme_color:
        config["theme_color"] = new_color
        save_config(config)
        st.rerun()
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.expander("Create", expanded=False):
        st.markdown("<div style='font-size: 0.85rem; color: var(--text-muted); margin-bottom: 8px; font-weight: 600;'>Parent Subject</div>", unsafe_allow_html=True)
        new_parent = st.text_input("Name", key="c_p_name", label_visibility="collapsed", placeholder="Subject Name")
        new_p_target = st.number_input("Target (Hours)", min_value=1, value=50, key="c_p_target")
        if st.button("Add Subject", use_container_width=True) and new_parent:
            if new_parent not in config["subjects"]:
                config["subjects"][new_parent] = {"target_hours": new_p_target, "children": {}}
                save_config(config)
                st.rerun()
                
        st.markdown("<hr style='margin: 16px 0; border: none; border-top: 1px solid rgba(255,255,255,0.4);'>", unsafe_allow_html=True)
        
        st.markdown("<div style='font-size: 0.85rem; color: var(--text-muted); margin-bottom: 8px; font-weight: 600;'>Child Task</div>", unsafe_allow_html=True)
        if config["subjects"]:
            sel_p_for_c = st.selectbox("Parent", list(config["subjects"].keys()), key="c_c_parent", label_visibility="collapsed")
            new_child = st.text_input("Task Name", key="c_c_name", label_visibility="collapsed", placeholder="Task Name")
            new_c_target = st.number_input("Task Target (Hours)", min_value=1, value=10, key="c_c_target")
            if st.button("Add Task", use_container_width=True) and new_child:
                if new_child not in config["subjects"][sel_p_for_c]["children"]:
                    config["subjects"][sel_p_for_c]["children"][new_child] = {"target_hours": new_c_target}
                    save_config(config)
                    st.rerun()

    with st.expander("Modify", expanded=False):
        if config["subjects"]:
            mod_type = st.radio("Type", ["Parent", "Child"], horizontal=True, label_visibility="collapsed")
            if mod_type == "Parent":
                mod_p = st.selectbox("Select Subject", list(config["subjects"].keys()), key="m_p_sel")
                new_rn_name = st.text_input("Rename To", value=mod_p, key="m_p_rn")
                has_children = len(config["subjects"][mod_p]["children"]) > 0
                new_rn_target = st.number_input("New Target", min_value=1, value=config["subjects"][mod_p].get("target_hours", 50), key="m_p_tg", disabled=has_children)
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

    with st.expander("Delete", expanded=False):
        if config["subjects"]:
            del_type = st.radio("Type to Delete", ["Parent", "Child"], horizontal=True, label_visibility="collapsed")
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
# 6. Central Core L1: Perfect Alignment
# ==========================================
col_l1_left, col_l1_center, col_l1_right = st.columns([1.5, 2, 1.5])

with col_l1_right:
    st.markdown("<div style='height: 42px;'></div>", unsafe_allow_html=True)
    time_filter = st.radio("Dimension",["Today", "Week", "Month", "Year"], horizontal=True, label_visibility="collapsed")

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
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    parent_subjects = list(config["subjects"].keys())
    if not parent_subjects:
        st.markdown("<div style='color: var(--text-muted); padding-top: 10px; font-weight: 500;'>Awaiting Configuration</div>", unsafe_allow_html=True)
        sel_parent, sel_child = None, None
    else:
        c_sel1, c_sel2 = st.columns(2)
        with c_sel1:
            sel_parent = st.selectbox("Subject", parent_subjects, disabled=(st.session_state.timer_state != 'idle'), label_visibility="collapsed")
        with c_sel2:
            child_dict = config["subjects"][sel_parent]["children"]
            child_list = list(child_dict.keys())
            sel_child = st.selectbox("Task", child_list if child_list else ["General"], disabled=(st.session_state.timer_state != 'idle'), label_visibility="collapsed")

with col_l1_center:
    if parent_subjects:
        if st.session_state.timer_state == 'idle':
            st.markdown(f"""
                <div style="text-align: center; font-family: 'Outfit', sans-serif; font-size: 4.8rem; font-weight: 300; color: var(--theme-color); line-height: 1; margin-bottom: 16px; letter-spacing: -2px;">
                    00:00:00
                </div>
            """, unsafe_allow_html=True)
            
            c_btn1, c_btn2, c_btn3 = st.columns([1, 1.5, 1])
            with c_btn2:
                if st.button("Start Session", use_container_width=True):
                    st.session_state.start_time = time.time()
                    st.session_state.timer_state = 'running'
                    st.rerun()
                    
        elif st.session_state.timer_state == 'running':
            start_ms = st.session_state.start_time * 1000
            timer_html = f"""
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300&display=swap');
                body {{ margin: 0; display: flex; justify-content: center; align-items: center; background: transparent; color: {theme_color}; font-family: 'Outfit', sans-serif; font-size: 4.8rem; font-weight: 300; line-height: 1; letter-spacing: -2px; }}
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
            components.html(timer_html, height=85)
            
            c_btn1, c_btn2, c_btn3 = st.columns([1, 1.5, 1])
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

st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)

# ==========================================
# 7. Central Core L2: Liquid Glass KPIs
# ==========================================
total_minutes = filtered_df['duration_minutes'].sum() if not filtered_df.empty else 0
total_hours = total_minutes / 60
active_subjects = filtered_df['parent_subject'].nunique() if not filtered_df.empty else 0
avg_score = filtered_df['focus_score'].mean() if not filtered_df.empty else 0.0

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f"""<div class="glass-card kpi-container"><div class="kpi-title">Duration</div><div class="kpi-value">{total_hours:.1f}<span>h</span></div></div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="glass-card kpi-container"><div class="kpi-title">Active Subjects</div><div class="kpi-value">{active_subjects}</div></div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div class="glass-card kpi-container"><div class="kpi-title">Focus Quality</div><div class="kpi-value">{avg_score:.1f}<span>pts</span></div></div>""", unsafe_allow_html=True)

# ==========================================
# 7.5 One-Click Weekly Report Feature
# ==========================================
@st.dialog("Weekly Achievement Report")
def generate_weekly_report():
    start_of_week = now - timedelta(days=now.weekday())
    week_df = df[df['timestamp'].dt.date >= start_of_week.date()]
    
    w_total_mins = week_df['duration_minutes'].sum() if not week_df.empty else 0
    w_total_hours = w_total_mins / 60
    w_avg_score = week_df['focus_score'].mean() if not week_df.empty else 0.0
    
    best_subject = "None"
    if not week_df.empty:
        best_subject = week_df.groupby('parent_subject')['duration_minutes'].sum().idxmax()
        
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {theme_color}22 0%, rgba(255,255,255,0.8) 100%); border-radius: 24px; padding: 32px; text-align: center; border: 1px solid rgba(255,255,255,0.5); box-shadow: 0 10px 30px rgba(0,0,0,0.05);">
        <h3 style="font-family: 'Outfit', sans-serif; color: var(--text-main); margin-bottom: 24px;">Weekly Summary</h3>
        <div style="display: flex; justify-content: space-around; margin-bottom: 24px;">
            <div>
                <div style="font-size: 0.85rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px;">Total Time</div>
                <div style="font-size: 2.2rem; font-weight: 700; color: {theme_color}; font-family: 'Outfit', sans-serif;">{w_total_hours:.1f}h</div>
            </div>
            <div>
                <div style="font-size: 0.85rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px;">Top Subject</div>
                <div style="font-size: 1.8rem; font-weight: 600; color: var(--text-main); font-family: 'Inter', sans-serif; margin-top: 6px;">{best_subject}</div>
            </div>
            <div>
                <div style="font-size: 0.85rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px;">Avg Focus</div>
                <div style="font-size: 2.2rem; font-weight: 700; color: {theme_color}; font-family: 'Outfit', sans-serif;">{w_avg_score:.1f}</div>
            </div>
        </div>
        <p style="font-size: 1rem; color: var(--text-muted); font-style: italic;">"Consistency is the architecture of mastery."</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    csv = week_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Weekly CSV",
        data=csv,
        file_name='weekly_focus_report.csv',
        mime='text/csv',
        use_container_width=True
    )

c_rep1, c_rep2, c_rep3 = st.columns([1, 1, 1])
with c_rep2:
    if st.button("Generate Weekly Report", use_container_width=True):
        generate_weekly_report()

st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

# ==========================================
# 8. Central Core L3: Grid Gallery & Insights
# ==========================================
col_l3_left, col_l3_right = st.columns([1.6, 1], gap="large")

with col_l3_left:
    st.markdown("<div class='section-title'>Subject Gallery</div>", unsafe_allow_html=True)
    
    parent_group = filtered_df.groupby('parent_subject')['duration_minutes'].sum() if not filtered_df.empty else pd.Series()
    
    # 2x2 Grid Layout using columns
    gallery_cols = st.columns(2)
    
    for idx, (parent, details) in enumerate(config["subjects"].items()):
        target_h = get_parent_target(parent)
        if target_h <= 0: target_h = 1 # Safety patch
        
        current_m = parent_group.get(parent, 0)
        current_h = current_m / 60
        progress_pct = min((current_h / target_h) * 100, 100)
        
        with gallery_cols[idx % 2]:
            # Expander acts as the entire card
            with st.expander(f"{parent}  |  {current_h:.1f}h / {target_h}h"):
                st.markdown(f"""
                <div class="pg-track">
                    <div class="pg-fill" style="width: {progress_pct}%;"></div>
                </div>
                <div class="pg-label" style="margin-bottom: 16px;">
                    <span>Overall Progress</span>
                    <span>{progress_pct:.0f}%</span>
                </div>
                """, unsafe_allow_html=True)
                
                children = details.get("children", {})
                if children:
                    child_df = filtered_df[filtered_df['parent_subject'] == parent] if not filtered_df.empty else pd.DataFrame()
                    child_group = child_df.groupby('child_subject')['duration_minutes'].sum() if not child_df.empty else pd.Series()
                    
                    html_children = ""
                    for child, c_details in children.items():
                        c_target_h = c_details.get("target_hours", 1)
                        if c_target_h <= 0: c_target_h = 1 # Safety patch
                        
                        c_current_m = child_group.get(child, 0)
                        c_current_h = c_current_m / 60
                        c_pct = min((c_current_h / c_target_h) * 100, 100)
                        
                        html_children += f"""
                        <div style="margin-top: 12px;">
                            <div class="pg-label" style="font-size: 0.8rem;">
                                <span>{child}</span>
                                <span>{c_current_h:.1f}h / {c_target_h}h</span>
                            </div>
                            <div class="pg-track" style="height: 4px; margin: 6px 0;">
                                <div class="pg-fill" style="width: {c_pct}%; opacity: 0.7;"></div>
                            </div>
                        </div>
                        """
                    st.markdown(html_children, unsafe_allow_html=True)

with col_l3_right:
    st.markdown("<div class='section-title'>Insights</div>", unsafe_allow_html=True)
    
    yesterday_df = df[df['timestamp'].dt.date == (now.date() - timedelta(days=1))]
    y_hours = yesterday_df['duration_minutes'].sum() / 60 if not yesterday_df.empty else 0
    t_hours = df[df['timestamp'].dt.date == now.date()]['duration_minutes'].sum() / 60 if not df.empty else 0
    
    st.markdown("<div class='glass-card' style='padding: 24px;'>", unsafe_allow_html=True)
    
    # Robust Plotly Fix: Prevent ValueError when range is [0, 0]
    max_val = max(t_hours, y_hours)
    gauge_max = max_val if max_val > 0 else 1.0

    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = t_hours,
        title = {'text': "Today vs Yesterday (h)", 'font': {'size': 14, 'color': '#5A5A5E', 'family': 'Inter'}},
        delta = {'reference': y_hours, 'increasing': {'color': theme_color}},
        gauge = {
            'axis': {'range':[0, gauge_max], 'tickwidth': 1, 'tickcolor': "rgba(255,255,255,0)"},
            'bar': {'color': theme_color},
            'bgcolor': "rgba(255,255,255,0.3)",
            'borderwidth': 0,
            'threshold': {'line': {'color': f"{theme_color}88", 'width': 2}, 'thickness': 0.75, 'value': y_hours}
        }
    ))
    fig_gauge.update_layout(height=180, margin=dict(l=20, r=20, t=40, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'family': "Inter, sans-serif"})
    st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False})
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='glass-card' style='padding: 24px;'>", unsafe_allow_html=True)
    # Robust Plotly Fix: Prevent empty pie chart rendering
    if not filtered_df.empty and total_hours > 0:
        fig_pie = px.pie(filtered_df, names='parent_subject', values='duration_minutes', hole=0.75, color_discrete_sequence=palette)
        fig_pie.update_traces(textposition='inside', textinfo='percent', marker=dict(line=dict(color='rgba(255,255,255,0.6)', width=1)))
        fig_pie.update_layout(
            title={'text': "Time Distribution", 'font': {'size': 14, 'color': '#5A5A5E', 'family': 'Inter'}, 'x': 0.5, 'xanchor': 'center'},
            showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
            height=240, margin=dict(l=10, r=10, t=40, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'family': "Inter, sans-serif"}
        )
        fig_pie.add_annotation(text=f"<b>{total_hours:.1f}h</b>", x=0.5, y=0.5, font_size=24, showarrow=False, font_color=theme_color)
        st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})
    else:
        st.markdown("<div style='height: 240px; display: flex; align-items: center; justify-content: center; color: var(--text-muted); font-weight: 500;'>No data available</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 9. Central Core L4: 2026 Heatmap
# ==========================================
st.markdown("<div class='section-title' style='margin-top: 16px;'>Annual Activity (2026)</div>", unsafe_allow_html=True)
st.markdown("<div class='glass-card' style='padding: 28px;'>", unsafe_allow_html=True)

# Strictly 2026
curr_year = 2026
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

heatmap_df['day_of_year'] = heatmap_df['date'].dt.dayofyear
heatmap_df['x'] = (heatmap_df['day_of_year'] - 1) // 7
heatmap_df['y'] = heatmap_df['date'].dt.weekday

fig_heat = go.Figure(data=go.Heatmap(
    z=heatmap_df['duration_minutes'],
    x=heatmap_df['x'],
    y=heatmap_df['y'],
    colorscale=[[0, 'rgba(255,255,255,0.4)'],[1, theme_color]],
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
        tickfont=dict(color="#5A5A5E", family="Inter, sans-serif", size=12)
    )
)
st.plotly_chart(fig_heat, use_container_width=True, config={'displayModeBar': False})
st.markdown("</div>", unsafe_allow_html=True)