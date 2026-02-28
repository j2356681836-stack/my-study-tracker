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
                    "target_hours": 100.0,
                    "children": {
                        "System Design": {"target_hours": 40.0},
                        "Algorithms": {"target_hours": 60.0}
                    }
                },
                "Design": {
                    "target_hours": 50.0,
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

# --- Robust Helper Functions ---
def sanitize_hex(color_str):
    if not color_str: return "#000000"
    color_str = color_str.lstrip('#')
    return f"#{color_str[:6]}"

def adjust_color(hex_color, lightness_factor, alpha=1.0):
    """Generate monochromatic variations for the 4-color liquid background"""
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16)/255.0 for i in (0, 2, 4))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    l = max(0, min(1, l * lightness_factor))
    nr, ng, nb = colorsys.hls_to_rgb(h, l, s)
    if alpha < 1.0:
        return f"rgba({int(nr*255)}, {int(ng*255)}, {int(nb*255)}, {alpha})"
    return f"#{int(nr*255):02x}{int(ng*255):02x}{int(nb*255):02x}"

def get_parent_target(parent_name):
    parent_data = config["subjects"].get(parent_name, {})
    children = parent_data.get("children", {})
    if not children:
        return max(0.1, parent_data.get("target_hours", 1.0))
    return max(0.1, sum(child_data.get("target_hours", 1.0) for child_data in children.values()))

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
# 2. Deep Liquid Glass CSS Engine & 4-Color Animation
# ==========================================
raw_theme_color = config.get("theme_color", "#007AFF")
safe_theme_color = sanitize_hex(raw_theme_color)

# Generate 4-color palette for the liquid background
theme_dark = adjust_color(safe_theme_color, 0.6)
theme_light_gray = "#E2EBF0"
theme_alpha = adjust_color(safe_theme_color, 1.0, 0.25)

def generate_monochromatic_palette(base_hex, n=5):
    base_hex = base_hex.lstrip('#')[:6]
    r, g, b = tuple(int(base_hex[i:i+2], 16)/255.0 for i in (0, 2, 4))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    palette =[]
    for i in range(n):
        factor = i / max(n, 1)
        new_l = min(0.9, l + (factor * (0.9 - l)))
        nr, ng, nb = colorsys.hls_to_rgb(h, new_l, s)
        palette.append(f"#{int(nr*255):02x}{int(ng*255):02x}{int(nb*255):02x}")
    return palette

palette = generate_monochromatic_palette(safe_theme_color, max(len(config["subjects"]), 5))

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@300;400;500;700&display=swap');

    :root {{
        --theme-color: {safe_theme_color};
        --theme-dark: {theme_dark};
        --theme-light-gray: {theme_light_gray};
        --theme-alpha: {theme_alpha};
        --text-main: #1D1D1F;
        --text-muted: #5A5A5E;
        --glass-bg: rgba(255, 255, 255, 0.4);
        --glass-border: rgba(255, 255, 255, 0.3);
        --glass-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
    }}
    
    #MainMenu, header, footer {{visibility: hidden;}}
    
    /* 突破 1: 四色动态液态背景 (15秒周期呼吸感) */
    @keyframes liquid-bg {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}
    .stApp, div.main {{
        background: linear-gradient(-45deg, var(--theme-color), var(--theme-dark), var(--theme-light-gray), var(--theme-alpha)) !important;
        background-size: 400% 400% !important;
        animation: liquid-bg 15s ease infinite !important;
        background-attachment: fixed !important;
        font-family: 'Inter', sans-serif;
        color: var(--text-main);
    }}

    /* THE WHITE BAR KILLER */
    .st-emotion-cache-1wivap2, .st-emotion-cache-1104q3y, .st-emotion-cache-16txtl3, 
    .st-emotion-cache-1y4p8pa, .st-emotion-cache-1n76uvr, .st-emotion-cache-18ni7ap,
    .st-emotion-cache-1jicfl2, .st-emotion-cache-1dp5vir, .st-emotion-cache-1v0mbdj,[data-testid="stVerticalBlock"],[data-testid="stHorizontalBlock"],[data-testid="stVerticalBlockBorderWrapper"],[data-testid="stHeader"],[data-testid="stMarkdownContainer"], .element-container, .stMain,[data-testid="stMetric"], .stPlotlyChart, .stMarkdown {{
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
    }}
    
    /* 突破 2: L1 绝对平衡与对齐 (垂直居中) */[data-testid="stHorizontalBlock"] {{
        align-items: center !important;
    }}
    
    /* Universal Glass Card */
    .glass-card {{
        background: var(--glass-bg) !important;
        backdrop-filter: blur(30px) !important;
        -webkit-backdrop-filter: blur(30px) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 28px !important;
        padding: 32px !important;
        box-shadow: var(--glass-shadow) !important;
        margin-bottom: 24px !important;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    }}

    /* Grid Gallery & Immersive Cards */
    .gallery-grid {{
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 20px;
        align-items: start;
    }}
    
    details.glass-card-detail {{
        background: var(--glass-bg);
        backdrop-filter: blur(30px);
        -webkit-backdrop-filter: blur(30px);
        border: 1px solid var(--glass-border);
        border-radius: 28px;
        padding: 24px;
        box-shadow: var(--glass-shadow);
        color: var(--text-main);
        transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.3s ease, background 0.3s ease;
    }}
    details.glass-card-detail[open] {{ background: rgba(255,255,255,0.6); }}
    
    details.active-glass-card-detail {{
        background: var(--theme-color) !important;
        backdrop-filter: blur(30px);
        border: 1px solid rgba(255,255,255,0.5);
        border-radius: 28px;
        padding: 24px;
        box-shadow: 0 12px 40px {safe_theme_color}66;
        color: #FFFFFF !important;
        transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.3s ease, background 0.3s ease;
    }}
    
    /* 突破 3: 悬停缩放与光晕增强 */
    details.glass-card-detail:hover, details.active-glass-card-detail:hover {{
        transform: scale(1.02);
        box-shadow: 0 20px 40px rgba(0,0,0,0.15), 0 0 20px var(--theme-alpha);
    }}

    details.glass-card-detail > summary, details.active-glass-card-detail > summary {{ list-style: none; outline: none; cursor: pointer; }}
    details.glass-card-detail > summary::-webkit-details-marker, details.active-glass-card-detail > summary::-webkit-details-marker {{ display: none; }}
    
    details.active-glass-card-detail .pg-label, details.active-glass-card-detail span {{ color: rgba(255,255,255,0.9) !important; }}
    details.active-glass-card-detail .pg-fill {{ background-color: #FFFFFF !important; }}
    details.active-glass-card-detail .pg-track {{ background: rgba(0,0,0,0.2) !important; }}
    details.active-glass-card-detail .task-list-container {{ border-top: 1px solid rgba(255,255,255,0.3) !important; }}

    /* KPI Typography */
    .kpi-container {{ display: flex; flex-direction: column; justify-content: center; height: 130px; text-align: center; }}
    .kpi-title {{ color: var(--text-muted); font-size: 0.9rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 8px; }}
    .kpi-value {{ color: var(--theme-color); font-family: 'Outfit', sans-serif; font-size: 3.5rem; font-weight: 700; line-height: 1; letter-spacing: -1px; text-shadow: 0 4px 20px rgba(255,255,255,0.4); }}
    .kpi-value span {{ font-size: 1.2rem; color: var(--text-muted); margin-left: 4px; font-weight: 500; letter-spacing: 0; text-shadow: none; }}

    /* Buttons */
    .stButton > button {{
        background: rgba(255, 255, 255, 0.45) !important;
        backdrop-filter: blur(25px) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 24px !important;
        color: var(--text-main) !important;
        font-weight: 600 !important;
        padding: 10px 24px !important;
        box-shadow: var(--glass-shadow) !important;
        transition: all 0.3s ease !important;
    }}
    .stButton > button:hover {{
        background: var(--theme-color) !important;
        color: #FFFFFF !important;
        border-color: var(--theme-color) !important;
        transform: scale(1.02);
    }}
    
    /* Primary Buttons (Confirm/Save) */
    .stButton > button[kind="primary"] {{
        background: var(--theme-color) !important;
        color: #FFFFFF !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;
    }}
    .stButton > button[kind="primary"]:hover {{
        filter: brightness(1.1);
    }}

    /* Sidebar Expander (Laboratory Card UI) */[data-testid="stSidebar"][data-testid="stExpander"] {{
        background: rgba(255, 255, 255, 0.35) !important;
        backdrop-filter: blur(30px) !important;
        -webkit-backdrop-filter: blur(30px) !important;
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        border-radius: 28px !important;
        box-shadow: var(--glass-shadow) !important;
        margin-bottom: 16px !important;
    }}[data-testid="stExpander"] details {{ border: none !important; background: transparent !important; }}[data-testid="stExpander"] summary {{
        padding: 16px 28px !important;
        border: none !important;
        background: transparent !important;
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        font-weight: 600;
        color: var(--text-main);
    }}
    [data-testid="stExpander"] summary:hover {{ color: var(--theme-color); }}
    [data-testid="stExpander"] div[role="region"] {{ background: transparent !important; padding: 0 28px 28px 28px !important; }}

    /* 突破 2: L1 绝对平衡与对齐 (右对齐维度选择器) */[data-testid="stRadio"] {{ display: flex; justify-content: flex-end; width: 100%; }}
    div[role="radiogroup"] {{ gap: 12px; }}
    div[role="radio"][aria-checked="true"] > div:first-child > div {{ background-color: var(--theme-color) !important; }}
    div[role="radio"][aria-checked="true"] > div:first-child {{ border-color: var(--theme-color) !important; }}
    
    /* Sidebar & Dialog */[data-testid="stSidebar"] {{
        background: rgba(255, 255, 255, 0.25) !important;
        backdrop-filter: blur(40px) !important;
        border-right: 1px solid var(--glass-border) !important;
    }}
    div[data-testid="stDialog"] > div {{
        background: rgba(255, 255, 255, 0.8) !important;
        backdrop-filter: blur(50px) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 30px !important;
        box-shadow: 0 20px 60px rgba(0,0,0,0.1) !important;
    }}
    
    /* Custom Progress */
    .pg-track {{ width: 100%; height: 6px; background: rgba(255,255,255,0.4); border-radius: 3px; overflow: hidden; margin: 10px 0; }}
    .pg-fill {{ height: 100%; border-radius: 3px; transition: width 1s ease; background-color: var(--theme-color); }}
    .pg-label {{ display: flex; justify-content: space-between; font-size: 0.85rem; color: var(--text-muted); font-weight: 600; }}
    
    /* Typography */
    .section-title {{ font-family: 'Outfit', sans-serif; font-size: 1.4rem; font-weight: 600; color: var(--text-main); margin-bottom: 20px; letter-spacing: -0.5px; }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. State Management & Shadow Proxy Pattern
# ==========================================
if 'timer_state' not in st.session_state: st.session_state.timer_state = 'idle'
if 'start_time' not in st.session_state: st.session_state.start_time = None

# 突破 4: 影子状态代理 (彻底解决 StreamlitAPIException)
if 'shadow_p_name' not in st.session_state: st.session_state.shadow_p_name = ""
if 'shadow_c_name' not in st.session_state: st.session_state.shadow_c_name = ""

def sync_p_name_callback():
    st.session_state.shadow_p_name = st.session_state.m_p_sel

def sync_c_name_callback():
    st.session_state.shadow_c_name = st.session_state.m_c_sel

def sync_p_c_name_callback():
    parent = st.session_state.m_c_p_sel
    children = list(config["subjects"][parent]["children"].keys())
    st.session_state.shadow_c_name = children[0] if children else ""

# ==========================================
# 4. Sidebar: Theme -> Report -> Laboratory
# ==========================================
df = pd.read_csv(DATA_FILE)
df['timestamp'] = pd.to_datetime(df['timestamp'])
now = datetime.now()

@st.dialog("Intelligence Report")
def show_report_dialog(period_type):
    if period_type == "Weekly":
        curr_start = now - timedelta(days=now.weekday())
        prev_start = curr_start - timedelta(weeks=1)
        prev_end = curr_start
        period_name = "Weekly"
    elif period_type == "Monthly":
        curr_start = now.replace(day=1)
        prev_start = (curr_start - timedelta(days=1)).replace(day=1)
        prev_end = curr_start
        period_name = "Monthly"
    else:
        curr_start = now.replace(month=1, day=1)
        prev_start = curr_start.replace(year=curr_start.year - 1)
        prev_end = curr_start
        period_name = "Yearly"

    curr_df = df[df['timestamp'] >= curr_start]
    prev_df = df[(df['timestamp'] >= prev_start) & (df['timestamp'] < prev_end)]

    c_hours = curr_df['duration_minutes'].sum() / 60 if not curr_df.empty else 0.0
    p_hours = prev_df['duration_minutes'].sum() / 60 if not prev_df.empty else 0.0
    
    growth = ((c_hours - p_hours) / p_hours) * 100 if p_hours > 0 else (100 if c_hours > 0 else 0)
    growth_str = f"{growth:+.1f}%"
    growth_color = safe_theme_color if growth >= 0 else "#FF3B30"

    top_subj = curr_df.groupby('parent_subject')['duration_minutes'].sum().idxmax() if not curr_df.empty else "None"
    avg_focus = curr_df['focus_score'].mean() if not curr_df.empty else 0.0

    st.markdown(f"""
    <div style="text-align: center; padding: 10px;">
        <h3 style="color: {safe_theme_color}; font-family: 'Outfit'; margin-bottom: 30px;">{period_name} Achievements</h3>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
            <div style="background: rgba(255,255,255,0.5); padding: 20px; border-radius: 20px;">
                <div style="font-size:0.8rem; color:#888; text-transform:uppercase;">Total Hours</div>
                <div style="font-size:2.2rem; font-weight:700; color:{safe_theme_color};">{c_hours:.1f}h</div>
                <div style="font-size:0.9rem; color:{growth_color}; font-weight:600;">{growth_str} vs Prev</div>
            </div>
            <div style="background: rgba(255,255,255,0.5); padding: 20px; border-radius: 20px;">
                <div style="font-size:0.8rem; color:#888; text-transform:uppercase;">Focus Score</div>
                <div style="font-size:2.2rem; font-weight:700; color:#333;">{avg_focus:.1f}</div>
            </div>
        </div>
        <div style="background: rgba(255,255,255,0.5); padding: 15px; border-radius: 20px; margin-bottom: 20px;">
            <div style="font-size:0.8rem; color:#888; text-transform:uppercase;">Top Discipline</div>
            <div style="font-size:1.6rem; font-weight:600; color:{safe_theme_color};">{top_subj}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<h2 style='font-family: Outfit; font-weight: 600; margin-bottom: 24px;'>Settings</h2>", unsafe_allow_html=True)
    
    new_color = st.color_picker("Theme Color", raw_theme_color)
    if new_color != raw_theme_color:
        config["theme_color"] = new_color
        save_config(config)
        st.rerun()
        
    st.markdown("<div style='height: 20px'></div>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div style='font-size: 0.85rem; color: var(--text-muted); font-weight: 600; margin-bottom: 8px;'>Report Generator</div>", unsafe_allow_html=True)
        report_period = st.selectbox("Period", ["Weekly", "Monthly", "Yearly"], label_visibility="collapsed")
        if st.button("Generate Report", use_container_width=True):
            show_report_dialog(report_period)
            
    st.markdown("<div style='height: 30px'></div>", unsafe_allow_html=True)
    st.markdown("<h2 style='font-family: Outfit; font-weight: 600; margin-bottom: 16px;'>Laboratory</h2>", unsafe_allow_html=True)

    with st.expander("Create", expanded=False):
        new_parent = st.text_input("Name", key="c_p_name", placeholder="Subject Name")
        new_p_target = st.number_input("Target (Hours)", min_value=1.0, value=50.0, step=1.0, key="c_p_target")
        if st.button("Add Subject", type="primary", use_container_width=True) and new_parent:
            if new_parent not in config["subjects"]:
                config["subjects"][new_parent] = {"target_hours": new_p_target, "children": {}}
                save_config(config)
                st.rerun()
        
        st.markdown("<hr style='margin: 12px 0; opacity: 0.2;'>", unsafe_allow_html=True)
        if config["subjects"]:
            sel_p_for_c = st.selectbox("Parent", list(config["subjects"].keys()), key="c_c_parent")
            new_child = st.text_input("Task Name", key="c_c_name", placeholder="Task Name")
            new_c_target = st.number_input("Target", min_value=1.0, value=10.0, step=1.0, key="c_c_target")
            if st.button("Add Task", type="primary", use_container_width=True) and new_child:
                if new_child not in config["subjects"][sel_p_for_c]["children"]:
                    config["subjects"][sel_p_for_c]["children"][new_child] = {"target_hours": new_c_target}
                    save_config(config)
                    st.rerun()

    with st.expander("Modify", expanded=False):
        if config["subjects"]:
            mod_type = st.radio("Type",["Parent", "Child"], horizontal=True, label_visibility="collapsed")
            if mod_type == "Parent":
                p_list = list(config["subjects"].keys())
                # 绑定 on_change 回调更新影子变量
                mod_p = st.selectbox("Select", p_list, key="m_p_sel", on_change=sync_p_name_callback)
                
                current_shadow_p = st.session_state.shadow_p_name if st.session_state.shadow_p_name else mod_p
                # 突破 4: 严禁绑定 key，使用 value 接收影子状态，避免双向绑定冲突
                new_rn_name = st.text_input("Rename", value=current_shadow_p)
                
                has_children = len(config["subjects"][mod_p]["children"]) > 0
                new_rn_target = st.number_input("Target", min_value=1.0, value=float(config["subjects"][mod_p].get("target_hours", 50.0)), step=1.0, disabled=has_children)
                
                if st.button("Save", key="m_p_btn", type="primary", use_container_width=True):
                    if new_rn_name and new_rn_name != mod_p:
                        config["subjects"][new_rn_name] = config["subjects"].pop(mod_p)
                        update_csv_history("parent_subject", mod_p, new_rn_name)
                    target_name = new_rn_name if new_rn_name else mod_p
                    if not has_children:
                        config["subjects"][target_name]["target_hours"] = new_rn_target
                    save_config(config)
                    st.session_state.shadow_p_name = ""
                    st.rerun()
            else:
                p_list = list(config["subjects"].keys())
                mod_p_c = st.selectbox("Select Parent", p_list, key="m_c_p_sel", on_change=sync_p_c_name_callback)
                c_list = list(config["subjects"][mod_p_c]["children"].keys())
                
                if c_list:
                    mod_c = st.selectbox("Select Task", c_list, key="m_c_sel", on_change=sync_c_name_callback)
                    
                    current_shadow_c = st.session_state.shadow_c_name if st.session_state.shadow_c_name else mod_c
                    # 突破 4: 严禁绑定 key，使用 value 接收影子状态
                    new_c_name = st.text_input("Rename", value=current_shadow_c)
                    new_c_tg = st.number_input("Target", min_value=1.0, value=float(config["subjects"][mod_p_c]["children"][mod_c].get("target_hours", 10.0)), step=1.0)
                    
                    if st.button("Save", key="m_c_btn", type="primary", use_container_width=True):
                        if new_c_name and new_c_name != mod_c:
                            config["subjects"][mod_p_c]["children"][new_c_name] = config["subjects"][mod_p_c]["children"].pop(mod_c)
                            update_csv_history("child_subject", mod_c, new_c_name)
                        target_c_name = new_c_name if new_c_name else mod_c
                        config["subjects"][mod_p_c]["children"][target_c_name]["target_hours"] = new_c_tg
                        save_config(config)
                        st.session_state.shadow_c_name = ""
                        st.rerun()

    with st.expander("Delete", expanded=False):
        if config["subjects"]:
            del_type = st.radio("Type",["Parent", "Child"], horizontal=True, label_visibility="collapsed", key="del_rad")
            if del_type == "Parent":
                del_p = st.selectbox("Select", list(config["subjects"].keys()), key="d_p_sel")
                if st.button("Confirm Delete", key="d_p_btn", type="primary", use_container_width=True):
                    del config["subjects"][del_p]
                    save_config(config)
                    st.rerun()
            else:
                del_p_c = st.selectbox("Parent", list(config["subjects"].keys()), key="d_c_p_sel")
                children_list = list(config["subjects"][del_p_c]["children"].keys())
                if children_list:
                    del_c = st.selectbox("Task", children_list, key="d_c_sel")
                    if st.button("Confirm Delete", key="d_c_btn", type="primary", use_container_width=True):
                        del config["subjects"][del_p_c]["children"][del_c]
                        save_config(config)
                        st.rerun()

# ==========================================
# 5. Central Core L1: Absolute Balance
# ==========================================
col_l1_left, col_l1_center, col_l1_right = st.columns([1.5, 2, 1.5], vertical_alignment="center")

with col_l1_right:
    time_filter = st.radio("Dimension",["Today", "Week", "Month", "Year"], horizontal=True, label_visibility="collapsed")

if time_filter == "Today":
    filtered_df = df[df['timestamp'].dt.date == now.date()]
    compare_start = now - timedelta(days=1)
    compare_df = df[df['timestamp'].dt.date == compare_start.date()]
    compare_label = "Yesterday"
elif time_filter == "Week":
    start_of_week = now - timedelta(days=now.weekday())
    filtered_df = df[df['timestamp'].dt.date >= start_of_week.date()]
    compare_start = start_of_week - timedelta(weeks=1)
    compare_end = start_of_week
    compare_df = df[(df['timestamp'].dt.date >= compare_start.date()) & (df['timestamp'].dt.date < compare_end.date())]
    compare_label = "Last Week"
elif time_filter == "Month":
    filtered_df = df[(df['timestamp'].dt.year == now.year) & (df['timestamp'].dt.month == now.month)]
    last_month = now.replace(day=1) - timedelta(days=1)
    compare_df = df[(df['timestamp'].dt.year == last_month.year) & (df['timestamp'].dt.month == last_month.month)]
    compare_label = "Last Month"
else:
    filtered_df = df[df['timestamp'].dt.year == now.year]
    compare_df = df[df['timestamp'].dt.year == (now.year - 1)]
    compare_label = "Last Year"

with col_l1_left:
    parent_subjects = list(config["subjects"].keys())
    if not parent_subjects:
        st.markdown("<div style='color: var(--text-muted); font-weight: 500;'>Configure in Sidebar</div>", unsafe_allow_html=True)
        sel_parent, sel_child = None, None
    else:
        c_sel1, c_sel2 = st.columns(2)
        with c_sel1:
            sel_parent = st.selectbox("Subject", parent_subjects, index=None, disabled=(st.session_state.timer_state != 'idle'), label_visibility="collapsed")
        with c_sel2:
            if sel_parent:
                child_dict = config["subjects"][sel_parent]["children"]
                child_list = list(child_dict.keys())
                sel_child = st.selectbox("Task", child_list if child_list else["General"], disabled=(st.session_state.timer_state != 'idle'), label_visibility="collapsed")
            else:
                sel_child = st.selectbox("Task",["Select Subject"], disabled=True, label_visibility="collapsed")

with col_l1_center:
    if parent_subjects:
        if st.session_state.timer_state == 'idle':
            st.markdown(f"""
                <div style="text-align: center; font-family: 'Outfit', sans-serif; font-size: 4.8rem; font-weight: 300; color: {safe_theme_color}; line-height: 1; margin-bottom: 12px; letter-spacing: -2px;">
                    00:00:00
                </div>
            """, unsafe_allow_html=True)
            c_btn1, c_btn2, c_btn3 = st.columns([1, 1.2, 1])
            with c_btn2:
                if st.button("Start Session", use_container_width=True, disabled=(sel_parent is None)):
                    st.session_state.start_time = time.time()
                    st.session_state.timer_state = 'running'
                    st.rerun()
        elif st.session_state.timer_state == 'running':
            start_ms = st.session_state.start_time * 1000
            timer_html = f"""
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300&display=swap');
                body {{ margin: 0; display: flex; justify-content: center; align-items: center; background: transparent; color: {safe_theme_color}; font-family: 'Outfit', sans-serif; font-size: 4.8rem; font-weight: 300; line-height: 1; letter-spacing: -2px; }}
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
            c_btn1, c_btn2, c_btn3 = st.columns([1, 1.2, 1])
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
# 7. Central Core L2: KPIs
# ==========================================
total_minutes = filtered_df['duration_minutes'].sum() if not filtered_df.empty else 0.0
total_hours = total_minutes / 60
active_subjects = filtered_df['parent_subject'].nunique() if not filtered_df.empty else 0
avg_score = filtered_df['focus_score'].mean() if not filtered_df.empty else 0.0

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f"""<div class="glass-card kpi-container"><div class="kpi-title">Duration ({time_filter})</div><div class="kpi-value">{total_hours:.1f}<span>h</span></div></div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="glass-card kpi-container"><div class="kpi-title">Active Subjects</div><div class="kpi-value">{active_subjects}</div></div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div class="glass-card kpi-container"><div class="kpi-title">Focus Quality</div><div class="kpi-value">{avg_score:.1f}<span>pts</span></div></div>""", unsafe_allow_html=True)

st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

# ==========================================
# 8. Central Core L3: Interactive Grid Gallery & Insights
# ==========================================
# 突破 2: 双栏对齐，确保顶部在同一水平线
col_l3_left, col_l3_right = st.columns([2, 1], gap="large")

with col_l3_left:
    st.markdown("<div class='section-title'>Subject Gallery</div>", unsafe_allow_html=True)
    parent_group = filtered_df.groupby('parent_subject')['duration_minutes'].sum() if not filtered_df.empty else pd.Series()
    
    # 突破 3: 彻底解决代码外泄，全量遍历所有科目，使用纯 HTML 字符串拼接并一次性渲染
    gallery_html = "<div class='gallery-grid'>"
    for parent, details in config["subjects"].items():
        target_h = get_parent_target(parent)
        current_m = parent_group.get(parent, 0.0)
        current_h = current_m / 60
        progress_pct = min((current_h / target_h) * 100, 100)
        
        # 突破 3: 变色解耦 (仅手动选中且未计时时高亮)
        is_active = (sel_parent == parent) and (st.session_state.timer_state == 'idle') and (sel_parent is not None)
        card_class = "active-glass-card-detail" if is_active else "glass-card-detail"
        
        tasks_html = ""
        children = details.get("children", {})
        if not children:
            tasks_html = "<div style='color: var(--text-muted); font-size: 0.85rem;'>No specific tasks configured.</div>"
        else:
            for child, c_details in children.items():
                c_target = max(0.1, c_details.get("target_hours", 1.0))
                c_current_m = filtered_df[(filtered_df['parent_subject'] == parent) & (filtered_df['child_subject'] == child)]['duration_minutes'].sum() if not filtered_df.empty else 0.0
                c_current_h = c_current_m / 60
                c_prog = min((c_current_h / c_target) * 100, 100)
                tasks_html += f"""
                <div style="margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; font-size: 0.85rem; font-weight: 500;">
                        <span>{child}</span>
                        <span>{c_current_h:.1f}h / {c_target:.1f}h</span>
                    </div>
                    <div class="pg-track" style="height: 4px; margin: 6px 0;"><div class="pg-fill" style="width: {c_prog:.1f}%; background-color: var(--theme-color);"></div></div>
                </div>
                """

        gallery_html += f"""
        <details class="{card_class}">
            <summary>
                <div style="font-family:'Inter'; font-weight:600; font-size:1.1rem; margin-bottom:12px;">{parent}</div>
                <div class="pg-track"><div class="pg-fill" style="width: {progress_pct:.1f}%;"></div></div>
                <div class="pg-label" style="margin-top: 8px;">
                    <span>{current_h:.1f}h / {target_h:.1f}h</span>
                    <span>{progress_pct:.1f}%</span>
                </div>
            </summary>
            <div class="task-list-container" style="margin-top: 16px; padding-top: 16px; border-top: 1px solid rgba(255,255,255,0.2);">
                {tasks_html}
            </div>
        </details>
        """
    gallery_html += "</div>"
    st.markdown(gallery_html, unsafe_allow_html=True)

with col_l3_right:
    st.markdown("<div class='section-title'>Insights</div>", unsafe_allow_html=True)
    
    # 1. Dynamic Scale Gauge
    st.markdown("<div class='glass-card' style='padding: 24px;'>", unsafe_allow_html=True)
    
    # 突破 5: 动态标尺 (Gauge Max 随维度自动切换，精度保留一位小数)
    if time_filter == "Today": gauge_max = 6.0
    elif time_filter == "Week": gauge_max = 40.0
    elif time_filter == "Month": gauge_max = 160.0
    else: gauge_max = 1800.0
    
    compare_val = compare_df['duration_minutes'].sum() / 60 if not compare_df.empty else 0.0

    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = total_hours,
        number = {'valueformat': ".1f"},
        title = {'text': f"{time_filter} vs {compare_label}", 'font': {'size': 14, 'color': '#5A5A5E', 'family': 'Inter'}},
        delta = {'reference': compare_val, 'increasing': {'color': safe_theme_color}, 'valueformat': ".1f"},
        gauge = {
            'axis': {'range': [0, gauge_max], 'tickwidth': 1, 'tickcolor': "rgba(255,255,255,0)"},
            'bar': {'color': safe_theme_color},
            'bgcolor': "rgba(255,255,255,0.3)",
            'borderwidth': 0,
            'threshold': {'line': {'color': 'white', 'width': 2}, 'thickness': 0.75, 'value': gauge_max * 0.8}
        }
    ))
    fig_gauge.update_layout(height=180, margin=dict(l=20, r=20, t=40, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'family': "Inter, sans-serif"})
    st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False})
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 2. Monochromatic Pie Chart
    st.markdown("<div class='glass-card' style='padding: 24px;'>", unsafe_allow_html=True)
    if not filtered_df.empty and total_hours > 0:
        fig_pie = px.pie(filtered_df, names='parent_subject', values='duration_minutes', hole=0.75, color_discrete_sequence=palette)
        # 突破 5: 环形图开启引导线，百分比显示在圆环外部
        fig_pie.update_traces(textposition='outside', textinfo='percent', marker=dict(line=dict(color='rgba(255,255,255,0.6)', width=1)))
        fig_pie.update_layout(
            title={'text': "Distribution", 'font': {'size': 14, 'color': '#5A5A5E', 'family': 'Inter'}, 'x': 0.5, 'xanchor': 'center'},
            showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
            height=260, margin=dict(l=40, r=40, t=40, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'family': "Inter, sans-serif"}
        )
        fig_pie.add_annotation(text=f"<b>{total_hours:.1f}h</b>", x=0.5, y=0.5, font_size=24, showarrow=False, font_color=safe_theme_color)
        st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})
    else:
        st.markdown("<div style='height: 260px; display: flex; align-items: center; justify-content: center; color: var(--text-muted); font-weight: 500;'>No data available</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 9. Central Core L4: 2026 Heatmap
# ==========================================
st.markdown("<div class='section-title' style='margin-top: 16px;'>Annual Activity (2026)</div>", unsafe_allow_html=True)
st.markdown("<div class='glass-card' style='padding: 28px;'>", unsafe_allow_html=True)

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
    heatmap_df['duration_minutes'] = 0.0

heatmap_df['day_of_year'] = heatmap_df['date'].dt.dayofyear
heatmap_df['x'] = (heatmap_df['day_of_year'] - 1) // 7
heatmap_df['y'] = heatmap_df['date'].dt.weekday

fig_heat = go.Figure(data=go.Heatmap(
    z=heatmap_df['duration_minutes'],
    x=heatmap_df['x'],
    y=heatmap_df['y'],
    colorscale=[[0, 'rgba(255,255,255,0.4)'],[1, safe_theme_color]],
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