import streamlit as st
import pandas as pd
import json
import os
import time
import colorsys
from datetime import datetime, timedelta
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
            "theme_color": "#000000",
            "subjects": {
                "Engineering": {"target_hours": 100, "children": ["System Design", "Algorithms"]},
                "Design": {"target_hours": 50, "children": ["Typography", "Layout"]},
                "Language": {"target_hours": 80, "children": ["Reading", "Speaking"]}
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

# ==========================================
# 2. Color & Visual Standards
# ==========================================
def generate_palette(hex_color, n=8):
    """Generate a minimalist color palette based on the theme color using colorsys."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        hex_color = "000000"
    r, g, b = tuple(int(hex_color[i:i+2], 16)/255.0 for i in (0, 2, 4))
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    
    palette =[]
    for i in range(n):
        # Adjust saturation and value to create elegant shades
        new_s = max(0.05, s - i * (s / n) * 0.8)
        new_v = min(0.95, v + i * ((1.0 - v) / n) * 0.8)
        nr, ng, nb = colorsys.hsv_to_rgb(h, new_s, new_v)
        palette.append(f"#{int(nr*255):02x}{int(ng*255):02x}{int(nb*255):02x}")
    return palette

theme_color = config.get("theme_color", "#000000")
palette = generate_palette(theme_color, max(len(config["subjects"]), 5))

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@200;300;400&family=Inter:wght@300;400;500;600&display=swap');

    :root {{
        --theme-color: {theme_color};
        --bg-color: #FAFAFA;
        --surface-color: #FFFFFF;
        --text-main: #111111;
        --text-muted: #888888;
        --border-color: rgba(0, 0, 0, 0.06);
    }}
    
    /* Hide Streamlit Defaults */
    #MainMenu, header, footer {{visibility: hidden;}}
    
    .stApp {{
        background-color: var(--bg-color);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: var(--text-main);
    }}

    /* Minimalist Typography */
    h1, h2, h3, h4, h5, h6, p, span {{
        color: var(--text-main);
    }}
    
    /* Buttons */
    .stButton > button {{
        border-radius: 24px !important;
        border: 1px solid var(--border-color) !important;
        background: var(--surface-color) !important;
        color: var(--text-main) !important;
        font-weight: 500 !important;
        padding: 8px 24px !important;
        transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1) !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02) !important;
    }}
    .stButton > button:hover {{
        background: var(--theme-color) !important;
        color: #FFFFFF !important;
        border-color: var(--theme-color) !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.08) !important;
    }}

    /* Cards */
    .minimal-card {{
        background: var(--surface-color);
        border: 1px solid var(--border-color);
        border-radius: 24px;
        padding: 32px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.02);
        transition: transform 0.4s ease, box-shadow 0.4s ease;
        margin-bottom: 24px;
    }}
    .minimal-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 12px 32px rgba(0,0,0,0.06);
    }}

    /* KPI Tile */
    .kpi-tile {{
        text-align: center;
        margin-bottom: 40px;
    }}
    .kpi-label {{
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: var(--text-muted);
        margin-bottom: 8px;
        font-weight: 500;
    }}
    .kpi-value {{
        font-size: 3rem;
        font-weight: 300;
        letter-spacing: -1px;
    }}
    .kpi-value span {{
        font-size: 1.2rem;
        color: var(--text-muted);
        margin-left: 4px;
    }}

    /* Gallery Grid */
    .gallery-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
        gap: 24px;
    }}
    .gallery-card {{
        background: var(--surface-color);
        border: 1px solid var(--border-color);
        border-radius: 24px;
        padding: 24px;
        transition: all 0.4s ease;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 140px;
    }}
    .gallery-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 16px 40px rgba(0,0,0,0.06);
    }}
    .gc-top {{
        display: flex;
        align-items: flex-start;
        gap: 16px;
    }}
    .gc-icon {{
        width: 48px;
        height: 48px;
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        font-weight: 300;
        color: var(--surface-color);
    }}
    .gc-info {{
        flex: 1;
    }}
    .gc-title {{
        font-size: 1.1rem;
        font-weight: 500;
        margin-bottom: 4px;
    }}
    .gc-stats {{
        font-size: 0.85rem;
        color: var(--text-muted);
    }}
    .gc-progress-bg {{
        height: 4px;
        background: #F0F0F0;
        border-radius: 2px;
        margin-top: 20px;
        overflow: hidden;
    }}
    .gc-progress-fill {{
        height: 100%;
        border-radius: 2px;
        transition: width 1s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    
    /* Empty State */
    .empty-state {{
        text-align: center;
        padding: 60px 20px;
        color: var(--text-muted);
        font-weight: 300;
        font-size: 1.1rem;
        letter-spacing: 0.5px;
    }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. State Management
# ==========================================
if 'timer_state' not in st.session_state:
    st.session_state.timer_state = 'idle'
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'elapsed_minutes' not in st.session_state:
    st.session_state.elapsed_minutes = 0

# ==========================================
# 4. Sidebar (Low-Frequency Operations)
# ==========================================
with st.sidebar:
    st.markdown("<h3 style='font-weight: 400; margin-bottom: 32px; letter-spacing: -0.5px;'>Settings</h3>", unsafe_allow_html=True)
    
    st.markdown("<div class='kpi-label'>Time Filter</div>", unsafe_allow_html=True)
    time_filter = st.radio("Filter", ["Today", "This Week", "This Month", "This Year", "All Time"], label_visibility="collapsed")
    
    st.markdown("<br><div class='kpi-label'>Theme Color</div>", unsafe_allow_html=True)
    new_color = st.color_picker("Color", theme_color, label_visibility="collapsed")
    if new_color != theme_color:
        config["theme_color"] = new_color
        save_config(config)
        st.rerun()
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.expander("Subject Laboratory", expanded=False):
        st.markdown("<div class='kpi-label' style='margin-top:10px;'>Add Subject</div>", unsafe_allow_html=True)
        new_parent = st.text_input("Name", key="new_p_name", placeholder="e.g. Mathematics")
        new_target = st.number_input("Target (Hours)", min_value=1, value=100, key="new_p_target")
        if st.button("Create Subject", use_container_width=True):
            if new_parent and new_parent not in config["subjects"]:
                config["subjects"][new_parent] = {"target_hours": new_target, "children":[]}
                save_config(config)
                st.rerun()
                
        if config["subjects"]:
            st.markdown("<div class='kpi-label' style='margin-top:24px;'>Manage Subjects</div>", unsafe_allow_html=True)
            edit_parent = st.selectbox("Select Subject", list(config["subjects"].keys()))
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Delete Subject", use_container_width=True):
                    del config["subjects"][edit_parent]
                    save_config(config)
                    st.rerun()
            
            st.markdown("<div class='kpi-label' style='margin-top:16px;'>Add Sub-topic</div>", unsafe_allow_html=True)
            new_child = st.text_input("Sub-topic Name", placeholder=f"Add to {edit_parent}...")
            if st.button("Create Sub-topic", use_container_width=True) and new_child:
                if new_child not in config["subjects"][edit_parent]["children"]:
                    config["subjects"][edit_parent]["children"].append(new_child)
                    save_config(config)
                    st.rerun()

# ==========================================
# 5. Data Processing
# ==========================================
df = pd.read_csv(DATA_FILE)
df['timestamp'] = pd.to_datetime(df['timestamp'])
now = datetime.now()

if time_filter == "Today":
    filtered_df = df[df['timestamp'].dt.date == now.date()]
elif time_filter == "This Week":
    start_of_week = now - timedelta(days=now.weekday())
    filtered_df = df[df['timestamp'].dt.date >= start_of_week.date()]
elif time_filter == "This Month":
    filtered_df = df[(df['timestamp'].dt.year == now.year) & (df['timestamp'].dt.month == now.month)]
elif time_filter == "This Year":
    filtered_df = df[df['timestamp'].dt.year == now.year]
else:
    filtered_df = df.copy()

total_minutes = filtered_df['duration_minutes'].sum() if not filtered_df.empty else 0
total_hours = total_minutes / 60

# ==========================================
# 6. Main Layout: Focus Zone & Gallery
# ==========================================
col_focus, col_gallery = st.columns([1, 1.6], gap="large")

# --- Left: Central Focus Zone ---
with col_focus:
    st.markdown("<div class='minimal-card'>", unsafe_allow_html=True)
    
    # KPI Tile
    st.markdown(f"""
        <div class="kpi-tile">
            <div class="kpi-label">Cumulative Focus ({time_filter})</div>
            <div class="kpi-value">{total_hours:.1f}<span>h</span></div>
        </div>
    """, unsafe_allow_html=True)
    
    # Timer & Controls
    parent_subjects = list(config["subjects"].keys())
    if not parent_subjects:
        st.markdown("<div class='empty-state'>Please configure subjects in the sidebar.</div>", unsafe_allow_html=True)
    else:
        sel_parent = st.selectbox("Subject", parent_subjects, disabled=(st.session_state.timer_state != 'idle'))
        child_subjects = config["subjects"][sel_parent]["children"]
        sel_child = st.selectbox("Topic", child_subjects if child_subjects else ["General"], disabled=(st.session_state.timer_state != 'idle'))
        
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        
        if st.session_state.timer_state == 'idle':
            st.markdown(f"""
                <div style="text-align: center; font-family: 'Roboto Mono', monospace; font-size: 4.5rem; font-weight: 200; color: var(--text-main); margin: 20px 0 40px 0; line-height: 1;">
                    00:00:00
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("Begin Session", use_container_width=True):
                st.session_state.start_time = time.time()
                st.session_state.timer_state = 'running'
                st.rerun()
                
        elif st.session_state.timer_state == 'running':
            # High-precision JS Timer using time.time() delta
            start_ms = st.session_state.start_time * 1000
            timer_html = f"""
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@200&display=swap');
                body {{
                    display: flex; justify-content: center; align-items: center;
                    margin: 0; background-color: transparent;
                    color: {theme_color}; font-family: 'Roboto Mono', monospace; font-size: 4.5rem; font-weight: 200; line-height: 1;
                }}
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
                        String(h).padStart(2, '0') + ':' + 
                        String(m).padStart(2, '0') + ':' + 
                        String(s).padStart(2, '0');
                }}, 1000);
            </script>
            """
            components.html(timer_html, height=100)
            
            if st.button("End Session", use_container_width=True):
                delta_seconds = time.time() - st.session_state.start_time
                st.session_state.elapsed_minutes = round(delta_seconds / 60, 2)
                st.session_state.timer_state = 'rating'
                st.rerun()
                
        elif st.session_state.timer_state == 'rating':
            st.markdown(f"""
                <div style="text-align: center; font-family: 'Roboto Mono', monospace; font-size: 3rem; font-weight: 300; color: {theme_color}; margin: 20px 0 30px 0;">
                    {st.session_state.elapsed_minutes} <span style="font-size: 1rem; font-family: 'Inter', sans-serif; color: var(--text-muted);">min</span>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<div class='kpi-label' style='text-align: center;'>Session Quality</div>", unsafe_allow_html=True)
            focus_score = st.slider("", 1, 5, 5, label_visibility="collapsed")
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Save", use_container_width=True):
                    new_log = pd.DataFrame([{
                        "timestamp": datetime.now().isoformat(),
                        "parent_subject": sel_parent,
                        "child_subject": sel_child,
                        "duration_minutes": st.session_state.elapsed_minutes,
                        "focus_score": focus_score
                    }])
                    new_log.to_csv(DATA_FILE, mode='a', header=False, index=False, encoding="utf-8")
                    st.session_state.timer_state = 'idle'
                    st.rerun()
            with c2:
                if st.button("Discard", use_container_width=True):
                    st.session_state.timer_state = 'idle'
                    st.rerun()
                    
    st.markdown("</div>", unsafe_allow_html=True)

# --- Right: Subject Gallery ---
with col_gallery:
    st.markdown("<h3 style='font-weight: 400; margin-bottom: 24px; letter-spacing: -0.5px;'>Subject Gallery</h3>", unsafe_allow_html=True)
    
    if filtered_df.empty and time_filter == "All Time":
        st.markdown("<div class='empty-state'>Start your first focus session to see insights.</div>", unsafe_allow_html=True)
    else:
        # Calculate progress
        parent_group = filtered_df.groupby('parent_subject')['duration_minutes'].sum() if not filtered_df.empty else pd.Series()
        
        gallery_html = '<div class="gallery-grid">'
        
        for idx, (parent, details) in enumerate(config["subjects"].items()):
            target_h = details.get("target_hours", 100)
            current_m = parent_group.get(parent, 0)
            current_h = current_m / 60
            progress_pct = min((current_h / target_h) * 100, 100) if target_h > 0 else 0
            
            # Assign color from generated palette
            card_color = palette[idx % len(palette)]
            initial_letter = parent[0].upper() if parent else "S"
            
            gallery_html += f"""
            <div class="gallery-card">
                <div class="gc-top">
                    <div class="gc-icon" style="background-color: {card_color};">{initial_letter}</div>
                    <div class="gc-info">
                        <div class="gc-title">{parent}</div>
                        <div class="gc-stats">{current_h:.1f}h / {target_h}h</div>
                    </div>
                </div>
                <div class="gc-progress-bg">
                    <div class="gc-progress-fill" style="width: {progress_pct}%; background-color: {card_color};"></div>
                </div>
            </div>
            """
            
        gallery_html += '</div>'
        st.markdown(gallery_html, unsafe_allow_html=True)