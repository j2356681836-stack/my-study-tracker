import streamlit as st
import pandas as pd
import json
import os
import time
import colorsys
from datetime import datetime, timedelta, date
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components

# ==========================================
# 1. System Initialization & Data Foundation
# ==========================================
st.set_page_config(page_title="Focus V20", layout="wide", initial_sidebar_state="expanded")

DATA_FILE = "learning_logs.csv"
CONFIG_FILE = "subjects.json"

# --- Robust Helper Functions ---
def init_system():
    """Initialize data files if they don't exist."""
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
                    "children": {
                        "UI Patterns": {"target_hours": 20},
                        "Typography": {"target_hours": 30}
                    }
                }
            }
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(default_config, f, ensure_ascii=False, indent=4)
            
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=["timestamp", "parent_subject", "child_subject", "duration_minutes", "focus_score"])
        df.to_csv(DATA_FILE, index=False, encoding="utf-8")

def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(new_config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(new_config, f, ensure_ascii=False, indent=4)

def sanitize_hex(color_str):
    """Force 6-digit HEX for Plotly stability."""
    if not color_str: return "#000000"
    color_str = color_str.lstrip('#')
    if len(color_str) < 6: color_str = (color_str * 6)[:6]
    return f"#{color_str[:6]}"

def get_focus_score(minutes):
    if minutes < 5: return 1
    elif minutes <= 15: return 2
    elif minutes <= 30: return 3
    elif minutes <= 45: return 4
    else: return 5

def update_csv_history(col_name, old_val, new_val):
    try:
        df_temp = pd.read_csv(DATA_FILE)
        if not df_temp.empty:
            df_temp.loc[df_temp[col_name] == old_val, col_name] = new_val
            df_temp.to_csv(DATA_FILE, index=False, encoding="utf-8")
    except Exception:
        pass

def generate_monochromatic_palette(base_hex, n=5):
    """Generates a strict monochromatic palette from dark to light."""
    base_hex = base_hex.lstrip('#')[:6]
    r, g, b = tuple(int(base_hex[i:i+2], 16)/255.0 for i in (0, 2, 4))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    palette = []
    # Generate gradients from Luminance 0.3 to 0.85
    for i in range(n):
        new_l = 0.3 + (0.55 * (i / max(n-1, 1))) 
        nr, ng, nb = colorsys.hls_to_rgb(h, new_l, s)
        palette.append(f"#{int(nr*255):02x}{int(ng*255):02x}{int(nb*255):02x}")
    return palette

# Initialize
init_system()
config = load_config()

# ==========================================
# 2. Deep Liquid Glass CSS Engine
# ==========================================
raw_theme_color = config.get("theme_color", "#007AFF")
safe_theme_color = sanitize_hex(raw_theme_color)
monochrome_palette = generate_monochromatic_palette(safe_theme_color, 6)

# Liquid Gradient Background
bg_css = f"linear-gradient(135deg, {safe_theme_color}33 0%, #cfd9df 50%, #e2ebf0 100%)"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@200;300;400;600;700&display=swap');

    :root {{
        --theme-color: {safe_theme_color};
        --text-main: #1D1D1F;
        --text-muted: #5A5A5E;
        --glass-bg: rgba(255, 255, 255, 0.45);
        --glass-border: rgba(255, 255, 255, 0.4);
        --glass-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.05);
    }}
    
    /* Global Reset & Background */
    .stApp {{
        background: {bg_css} !important;
        background-attachment: fixed !important;
        font-family: 'Inter', sans-serif;
        color: var(--text-main);
    }}
    
    /* THE GREAT WHITEOUT ERASER - Force Transparency */
    .st-emotion-cache-1wivap2, .st-emotion-cache-1104q3y, .st-emotion-cache-16txtl3, 
    .st-emotion-cache-1y4p8pa, .st-emotion-cache-1n76uvr, .st-emotion-cache-18ni7ap,
    [data-testid="stVerticalBlock"], [data-testid="stHorizontalBlock"],
    [data-testid="stVerticalBlockBorderWrapper"], [data-testid="stHeader"],
    [data-testid="stMarkdownContainer"], .element-container, .stMain, 
    [data-testid="stMetric"], .stPlotlyChart, .stExpander, .stExpanderDetails {{
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
    }}
    
    header, footer {{visibility: hidden;}}

    /* L1 Core Alignment - Absolute Center */
    [data-testid="stHorizontalBlock"] {{
        align-items: center !important;
    }}

    /* Universal Glass Card */
    .glass-card {{
        background: var(--glass-bg) !important;
        backdrop-filter: blur(30px) !important;
        -webkit-backdrop-filter: blur(30px) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 28px !important;
        padding: 24px !important;
        box-shadow: var(--glass-shadow) !important;
        margin-bottom: 20px !important;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }}
    .glass-card:hover {{ transform: translateY(-2px); }}

    /* Active Gallery Card */
    .active-card {{
        background: var(--theme-color) !important;
        color: #FFFFFF !important;
        box-shadow: 0 12px 30px rgba(0,0,0,0.15) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
    }}
    .active-card .pg-title, .active-card .pg-label, .active-card div {{ color: #FFFFFF !important; }}
    .active-card .pg-track {{ background: rgba(0,0,0,0.2) !important; }}
    .active-card .pg-fill {{ background: #FFFFFF !important; }}
    .active-card [data-testid="stExpander"] summary {{ color: rgba(255,255,255,0.9) !important; }}
    .active-card [data-testid="stExpander"] summary:hover {{ color: #FFFFFF !important; }}

    /* KPI Typography */
    .kpi-container {{ display: flex; flex-direction: column; justify-content: center; height: 110px; text-align: center; }}
    .kpi-title {{ color: var(--text-muted); font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1.2px; margin-bottom: 6px; }}
    .kpi-value {{ color: var(--theme-color); font-family: 'Outfit', sans-serif; font-size: 3.2rem; font-weight: 600; line-height: 1; letter-spacing: -1.5px; }}
    .kpi-value span {{ font-size: 1.1rem; color: var(--text-muted); margin-left: 2px; font-weight: 500; letter-spacing: 0; }}

    /* Buttons - Glassmorphism */
    .stButton > button {{
        background: rgba(255, 255, 255, 0.4) !important;
        backdrop-filter: blur(20px) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 20px !important;
        color: var(--text-main) !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
        padding: 8px 20px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
        transition: all 0.2s ease !important;
    }}
    .stButton > button:hover {{
        background: var(--theme-color) !important;
        color: #FFFFFF !important;
        border-color: var(--theme-color) !important;
        transform: scale(1.02);
    }}

    /* Inputs & Selectboxes */
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div {{
        background-color: rgba(255, 255, 255, 0.5) !important;
        border-radius: 16px !important;
        border: 1px solid rgba(255,255,255,0.5) !important;
        color: var(--text-main) !important;
    }}

    /* Expander Styling */
    [data-testid="stExpander"] {{ border: none !important; box-shadow: none !important; }}
    [data-testid="stExpander"] details {{ border: none !important; }}
    [data-testid="stExpander"] summary {{
        padding: 8px 0 !important;
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        font-weight: 600;
        color: var(--text-muted);
        transition: color 0.3s;
    }}
    [data-testid="stExpander"] summary:hover {{ color: var(--theme-color); }}

    /* Custom Progress Bar */
    .pg-track {{ width: 100%; height: 5px; background: rgba(0,0,0,0.06); border-radius: 3px; overflow: hidden; margin: 12px 0; }}
    .pg-fill {{ height: 100%; border-radius: 3px; transition: width 1s ease; background-color: var(--theme-color); }}
    .pg-label {{ display: flex; justify-content: space-between; font-size: 0.8rem; color: var(--text-muted); font-weight: 600; }}
    .pg-title {{ font-family: 'Outfit', sans-serif; font-size: 1.1rem; font-weight: 600; margin-bottom: 4px; color: var(--text-main); letter-spacing: -0.3px; }}

    /* Sidebar Styling */
    [data-testid="stSidebar"] {{
        background-color: rgba(255, 255, 255, 0.4) !important;
        backdrop-filter: blur(40px) !important;
        border-right: 1px solid rgba(255,255,255,0.3) !important;
    }}
    
    /* Radio Button Alignment */
    div[role="radiogroup"] {{ justify-content: flex-end; }}
    div[data-testid="stRadio"] > label {{ display: none; }} 
    
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. State Management & Logic
# ==========================================
if 'timer_state' not in st.session_state: st.session_state.timer_state = 'idle'
if 'start_time' not in st.session_state: st.session_state.start_time = None
if 'active_parent' not in st.session_state: st.session_state.active_parent = None

# --- Rename Sync Callbacks ---
def sync_parent_rename():
    st.session_state.m_p_rn = st.session_state.m_p_sel

def sync_child_rename():
    st.session_state.m_c_rn = st.session_state.m_c_sel

df = pd.read_csv(DATA_FILE)
df['timestamp'] = pd.to_datetime(df['timestamp'])
now = datetime.now() 

# ==========================================
# 4. Sidebar: Config & Report
# ==========================================
@st.dialog("Intelligence Report")
def show_report_dialog(period_type):
    if period_type == "Weekly":
        curr_start = now - timedelta(days=now.weekday())
        prev_start = curr_start - timedelta(weeks=1)
        prev_end = curr_start
        label = "Weekly"
    elif period_type == "Monthly":
        curr_start = now.replace(day=1)
        prev_start = (curr_start - timedelta(days=1)).replace(day=1)
        prev_end = curr_start
        label = "Monthly"
    else: # Yearly
        curr_start = now.replace(month=1, day=1)
        prev_start = curr_start.replace(year=curr_start.year - 1)
        prev_end = curr_start
        label = "Yearly"

    curr_df = df[df['timestamp'] >= curr_start]
    prev_df = df[(df['timestamp'] >= prev_start) & (df['timestamp'] < prev_end)]

    c_hours = curr_df['duration_minutes'].sum() / 60 if not curr_df.empty else 0
    p_hours = prev_df['duration_minutes'].sum() / 60 if not prev_df.empty else 0
    
    growth = ((c_hours - p_hours) / p_hours) * 100 if p_hours > 0 else 0
    growth_str = f"{growth:+.1f}%"
    growth_color = safe_theme_color if growth >= 0 else "#FF3B30"
    
    avg_focus = curr_df['focus_score'].mean() if not curr_df.empty else 0.0

    st.markdown(f"""
    <div style="text-align: center; padding: 10px;">
        <h3 style="color: {safe_theme_color}; font-family: 'Outfit'; margin-bottom: 20px;">{label} Intelligence</h3>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px;">
            <div style="background: rgba(255,255,255,0.6); padding: 20px; border-radius: 20px;">
                <div style="font-size:0.75rem; color:#888; text-transform:uppercase;">Total Hours</div>
                <div style="font-size:2.4rem; font-weight:700; color:{safe_theme_color}; line-height:1;">{c_hours:.1f}h</div>
                <div style="font-size:0.9rem; color:{growth_color}; font-weight:600; margin-top:4px;">{growth_str} MoM</div>
            </div>
            <div style="background: rgba(255,255,255,0.6); padding: 20px; border-radius: 20px;">
                <div style="font-size:0.75rem; color:#888; text-transform:uppercase;">Focus Score</div>
                <div style="font-size:2.4rem; font-weight:700; color:#333; line-height:1;">{avg_focus:.1f}</div>
                <div style="font-size:0.8rem; color:#888; margin-top:4px;">Average Quality</div>
            </div>
        </div>
        <div style="color: #666; font-size: 0.9rem; font-style: italic;">"Persistence guarantees that results are inevitable."</div>
    </div>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.markdown(f"<h3 style='font-family:Outfit; color:{safe_theme_color}'>Focus V20</h3>", unsafe_allow_html=True)
    
    # Theme Color
    new_color = st.color_picker("Theme", raw_theme_color)
    if new_color != raw_theme_color:
        config["theme_color"] = new_color
        save_config(config)
        st.rerun()

    # Report Generator
    st.markdown("---")
    st.caption("REPORT GENERATOR")
    rep_period = st.selectbox("Period", ["Weekly", "Monthly", "Yearly"], label_visibility="collapsed")
    if st.button("Generate Intelligence", use_container_width=True):
        show_report_dialog(rep_period)

    # Laboratory (CRUD)
    st.markdown("---")
    st.caption("LABORATORY")
    
    with st.expander("Create Subject"):
        new_parent = st.text_input("Subject Name", key="c_p_name")
        new_p_target = st.number_input("Target (Hours)", min_value=1, value=50, key="c_p_target")
        if st.button("Add Subject", use_container_width=True) and new_parent:
            if new_parent not in config["subjects"]:
                config["subjects"][new_parent] = {"target_hours": new_p_target, "children": {}}
                save_config(config)
                st.rerun()
                
    with st.expander("Modify Structure"):
        if config["subjects"]:
            mod_type = st.radio("Type", ["Subject", "Task"], horizontal=True, label_visibility="collapsed")
            if mod_type == "Subject":
                # Ensure Session State for Rename Sync
                if "m_p_sel" not in st.session_state: st.session_state.m_p_sel = list(config["subjects"].keys())[0]
                
                mod_p = st.selectbox("Select", list(config["subjects"].keys()), key="m_p_sel", on_change=sync_parent_rename)
                
                # Input initialized from state if available, else current select
                val_init = st.session_state.get("m_p_rn", mod_p)
                new_rn_name = st.text_input("Rename", value=val_init, key="m_p_rn")
                
                has_children = len(config["subjects"][mod_p]["children"]) > 0
                new_rn_target = st.number_input("Target", min_value=0.1, value=float(config["subjects"][mod_p].get("target_hours", 50)), disabled=has_children)
                
                if st.button("Save Changes", use_container_width=True):
                    if new_rn_name and new_rn_name != mod_p:
                        config["subjects"][new_rn_name] = config["subjects"].pop(mod_p)
                        update_csv_history("parent_subject", mod_p, new_rn_name)
                    if not has_children:
                        config["subjects"][new_rn_name if new_rn_name else mod_p]["target_hours"] = new_rn_target
                    save_config(config)
                    st.rerun()
            else:
                # Child logic
                mod_p_c = st.selectbox("Parent", list(config["subjects"].keys()))
                children_list = list(config["subjects"][mod_p_c]["children"].keys())
                if children_list:
                    if "m_c_sel" not in st.session_state: st.session_state.m_c_sel = children_list[0]
                    mod_c = st.selectbox("Task", children_list, key="m_c_sel", on_change=sync_child_rename)
                    
                    val_c_init = st.session_state.get("m_c_rn", mod_c)
                    new_c_name = st.text_input("Rename", value=val_c_init, key="m_c_rn")
                    new_c_tg = st.number_input("Target", min_value=0.1, value=float(config["subjects"][mod_p_c]["children"][mod_c].get("target_hours", 10)))
                    
                    if st.button("Save Task", use_container_width=True):
                        if new_c_name and new_c_name != mod_c:
                            config["subjects"][mod_p_c]["children"][new_c_name] = config["subjects"][mod_p_c]["children"].pop(mod_c)
                            update_csv_history("child_subject", mod_c, new_c_name)
                        config["subjects"][mod_p_c]["children"][new_c_name if new_c_name else mod_c]["target_hours"] = new_c_tg
                        save_config(config)
                        st.rerun()
                else:
                    st.info("No tasks in this subject.")

    with st.expander("Delete"):
        if config["subjects"]:
            del_p = st.selectbox("Subject to Delete", list(config["subjects"].keys()))
            if st.button("Confirm Delete", use_container_width=True):
                del config["subjects"][del_p]
                save_config(config)
                st.rerun()

# ==========================================
# 5. Core L1: Pixel-Perfect Control Center
# ==========================================
col_l1_left, col_l1_center, col_l1_right = st.columns([1.5, 2, 1.5])

# Right: Time Filter (Dimension)
with col_l1_right:
    time_filter = st.radio("Dimension", ["Today", "Week", "Month", "Year"], horizontal=True, label_visibility="collapsed")

# Logic: Time Filter
if time_filter == "Today":
    filtered_df = df[df['timestamp'].dt.date == now.date()]
elif time_filter == "Week":
    start_of_week = now - timedelta(days=now.weekday())
    filtered_df = df[df['timestamp'].dt.date >= start_of_week.date()]
elif time_filter == "Month":
    filtered_df = df[(df['timestamp'].dt.year == now.year) & (df['timestamp'].dt.month == now.month)]
else:
    filtered_df = df[df['timestamp'].dt.year == now.year]

# Left: Selector
with col_l1_left:
    parent_subjects = list(config["subjects"].keys())
    if parent_subjects:
        c_sel1, c_sel2 = st.columns(2)
        with c_sel1:
            sel_parent = st.selectbox("Subject", parent_subjects, disabled=(st.session_state.timer_state != 'idle'), label_visibility="collapsed")
        with c_sel2:
            child_dict = config["subjects"][sel_parent]["children"]
            child_list = list(child_dict.keys())
            sel_child = st.selectbox("Task", child_list if child_list else ["General"], disabled=(st.session_state.timer_state != 'idle'), label_visibility="collapsed")
    else:
        sel_parent, sel_child = None, None

# Center: Timer (Thin Font)
with col_l1_center:
    if parent_subjects:
        if st.session_state.timer_state == 'idle':
            st.markdown(f"""
                <div style="text-align: center; font-family: 'Outfit', sans-serif; font-size: 5rem; font-weight: 200; color: {safe_theme_color}; line-height: 1; margin-bottom: 8px; letter-spacing: -2px;">
                    00:00:00
                </div>
            """, unsafe_allow_html=True)
            
            # Button Centering
            b1, b2, b3 = st.columns([1, 1, 1])
            with b2:
                if st.button("Start Focus", use_container_width=True):
                    st.session_state.start_time = time.time()
                    st.session_state.timer_state = 'running'
                    st.rerun()
        elif st.session_state.timer_state == 'running':
            start_ms = st.session_state.start_time * 1000
            # JS Timer for smooth updates without server roundtrips
            timer_html = f"""
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@200&display=swap');
                body {{ margin: 0; display: flex; justify-content: center; align-items: center; background: transparent; }}
                #timer {{ color: {safe_theme_color}; font-family: 'Outfit', sans-serif; font-size: 5rem; font-weight: 200; line-height: 1; letter-spacing: -2px; }}
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
            components.html(timer_html, height=90)
            
            b1, b2, b3 = st.columns([1, 1, 1])
            with b2:
                if st.button("Stop", use_container_width=True):
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

st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

# ==========================================
# 6. L2: KPI Cards
# ==========================================
total_m = filtered_df['duration_minutes'].sum() if not filtered_df.empty else 0
total_h = total_m / 60
act_subj = filtered_df['parent_subject'].nunique() if not filtered_df.empty else 0
avg_q = filtered_df['focus_score'].mean() if not filtered_df.empty else 0.0

k1, k2, k3 = st.columns(3)
with k1:
    st.markdown(f"""<div class="glass-card kpi-container"><div class="kpi-title">Duration ({time_filter})</div><div class="kpi-value">{total_h:.1f}<span>h</span></div></div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""<div class="glass-card kpi-container"><div class="kpi-title">Active Subjects</div><div class="kpi-value">{act_subj}</div></div>""", unsafe_allow_html=True)
with k3:
    st.markdown(f"""<div class="glass-card kpi-container"><div class="kpi-title">Focus Quality</div><div class="kpi-value">{avg_q:.1f}<span>pts</span></div></div>""", unsafe_allow_html=True)

st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

# ==========================================
# 7. L3: Interactive Gallery & Insights
# ==========================================
col_l3_left, col_l3_right = st.columns([1.6, 1], gap="medium")

with col_l3_left:
    st.caption("SUBJECT GALLERY")
    
    # Calculate Data
    parent_stats = filtered_df.groupby('parent_subject')['duration_minutes'].sum() if not filtered_df.empty else pd.Series()
    
    # Grid Layout for Cards
    parents = list(config["subjects"].items())
    rows = (len(parents) + 1) // 2
    
    for r in range(rows):
        c_row = st.columns(2)
        for c in range(2):
            idx = r * 2 + c
            if idx < len(parents):
                p_name, p_data = parents[idx]
                
                # Metrics
                # If parent has children, target is sum of children, else parent target
                children_config = p_data.get("children", {})
                if children_config:
                    p_target = sum(float(c_data.get("target_hours", 1)) for c_data in children_config.values())
                else:
                    p_target = float(p_data.get("target_hours", 1))
                
                p_target = max(p_target, 0.1) # Safety
                curr_min = parent_stats.get(p_name, 0)
                curr_hr = curr_min / 60
                prog = min((curr_hr / p_target) * 100, 100)
                
                # Styling Class (Active highlight)
                card_cls = "glass-card active-card" if sel_parent == p_name else "glass-card"
                
                with c_row[c]:
                    st.markdown(f"""
                    <div class="{card_cls}" style="padding: 20px !important;">
                        <div class="pg-title">{p_name}</div>
                        <div class="pg-track"><div class="pg-fill" style="width: {prog}%;"></div></div>
                        <div class="pg-label">
                            <span>{curr_hr:.1f}h / {p_target:.1f}h</span>
                            <span>{prog:.1f}%</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Nested Details for Children (if active or just generally available via Expander)
                    if children_config:
                        with st.expander("Details"):
                            child_df = filtered_df[filtered_df['parent_subject'] == p_name] if not filtered_df.empty else pd.DataFrame()
                            child_stats = child_df.groupby('child_subject')['duration_minutes'].sum() if not child_df.empty else pd.Series()
                            
                            html_str = ""
                            for c_name, c_conf in children_config.items():
                                c_tgt = float(c_conf.get("target_hours", 1))
                                c_act = child_stats.get(c_name, 0) / 60
                                c_pct = min((c_act / max(c_tgt, 0.1)) * 100, 100)
                                html_str += f"""
                                <div style="margin-top:8px;">
                                    <div style="display:flex; justify-content:space-between; font-size:0.75rem; opacity:0.8; margin-bottom:2px;">
                                        <span>{c_name}</span><span>{c_act:.1f}/{c_tgt:.1f}h</span>
                                    </div>
                                    <div style="width:100%; height:3px; background:rgba(128,128,128,0.2); border-radius:2px;">
                                        <div style="width:{c_pct}%; height:100%; background:currentColor; opacity:0.7; border-radius:2px;"></div>
                                    </div>
                                </div>
                                """
                            st.markdown(html_str, unsafe_allow_html=True)

with col_l3_right:
    st.caption("INSIGHTS")
    
    # 1. Today's Gauge
    st.markdown("<div class='glass-card' style='padding: 10px !important;'>", unsafe_allow_html=True)
    
    today_mins = df[df['timestamp'].dt.date == now.date()]['duration_minutes'].sum()
    today_hrs = today_mins / 60
    
    # Daily Target Calculation: Sum of all targets / 365
    total_sys_target = sum(
        sum(float(c.get("target_hours", 0)) for c in p["children"].values()) if p.get("children") 
        else float(p.get("target_hours", 0)) 
        for p in config["subjects"].values()
    )
    daily_goal = max(total_sys_target / 365, 0.1)
    
    fig_g = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = today_hrs,
        number = {'suffix': "h", 'font': {'size': 24, 'family': 'Outfit', 'color': safe_theme_color}},
        title = {'text': "Today's Progress", 'font': {'size': 12, 'color': '#5A5A5E'}},
        gauge = {
            'axis': {'range': [0, max(daily_goal * 1.5, today_hrs * 1.2)], 'tickwidth': 0, 'tickcolor': "rgba(0,0,0,0)"},
            'bar': {'color': safe_theme_color},
            'bgcolor': "rgba(0,0,0,0.05)",
            'borderwidth': 0,
            'threshold': {'line': {'color': "white", 'width': 3}, 'thickness': 0.8, 'value': daily_goal}
        }
    ))
    fig_g.update_layout(height=160, margin=dict(l=20, r=20, t=30, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_g, use_container_width=True, config={'displayModeBar': False})
    st.markdown("</div>", unsafe_allow_html=True)

    # 2. Monochromatic Pie
    st.markdown("<div class='glass-card' style='padding: 10px !important;'>", unsafe_allow_html=True)
    if not filtered_df.empty and total_h > 0:
        fig_p = px.pie(filtered_df, names='parent_subject', values='duration_minutes', hole=0.7, color_discrete_sequence=monochrome_palette)
        fig_p.update_traces(textposition='inside', textinfo='none', hoverinfo='label+percent', marker=dict(line=dict(color='rgba(255,255,255,0.8)', width=1)))
        fig_p.update_layout(
            showlegend=True, 
            legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5, font=dict(size=10)),
            height=200, margin=dict(l=10, r=10, t=10, b=10), 
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
        )
        # Center Text
        fig_p.add_annotation(text=f"<b>{total_h:.1f}h</b>", x=0.5, y=0.5, showarrow=False, font=dict(size=20, color=safe_theme_color, family="Outfit"))
        st.plotly_chart(fig_p, use_container_width=True, config={'displayModeBar': False})
    else:
        st.markdown("<div style='text-align:center; padding: 40px; color:#888; font-size:0.8rem;'>No Data</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 8. L4: 2026 Heatmap (Full Year)
# ==========================================
st.caption("ACTIVITY MAP (2026)")
st.markdown("<div class='glass-card' style='padding: 20px !important;'>", unsafe_allow_html=True)

# Generate 2026 Data Structure
d_start = date(2026, 1, 1)
d_end = date(2026, 12, 31)
date_rng = pd.date_range(d_start, d_end)
hm_df = pd.DataFrame({'date': date_rng})
hm_df['date_str'] = hm_df['date'].dt.strftime('%Y-%m-%d')

# Merge Actual Data
if not df.empty:
    df['d_str'] = df['timestamp'].dt.strftime('%Y-%m-%d')
    daily = df.groupby('d_str')['duration_minutes'].sum().reset_index()
    hm_final = pd.merge(hm_df, daily, left_on='date_str', right_on='d_str', how='left').fillna(0)
else:
    hm_final = hm_df
    hm_final['duration_minutes'] = 0

# Heatmap Coordinates
hm_final['week'] = hm_final['date'].dt.isocalendar().week
hm_final['weekday'] = hm_final['date'].dt.weekday # 0=Mon
# Adjust week 1 for plotting if needed (simple x mapping)
hm_final['x'] = (hm_final['date'].dt.dayofyear - 1) // 7
hm_final['y'] = hm_final['weekday']

fig_hm = go.Figure(data=go.Heatmap(
    z=hm_final['duration_minutes'],
    x=hm_final['x'],
    y=hm_final['y'],
    colorscale=[[0, 'rgba(255,255,255,0.1)'], [1, safe_theme_color]],
    showscale=False,
    xgap=2, ygap=2,
    hoverinfo='text',
    text=hm_final['date_str'] + ": " + hm_final['duration_minutes'].astype(int).astype(str) + "m"
))

fig_hm.update_layout(
    height=140,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    margin=dict(t=0, b=0, l=0, r=0),
    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, autorange='reversed')
)
st.plotly_chart(fig_hm, use_container_width=True, config={'displayModeBar': False})
st.markdown("</div>", unsafe_allow_html=True)