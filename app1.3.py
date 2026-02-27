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
st.set_page_config(page_title="Focus Tracker", layout="wide", initial_sidebar_state="expanded")

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
        return parent_data.get("target_hours", 0)
    return sum(child_data.get("target_hours", 0) for child_data in children.values())

def get_focus_score(minutes):
    if minutes < 5: return 1
    elif minutes <= 15: return 2
    elif minutes <= 30: return 3
    elif minutes <= 45: return 4
    else: return 5

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
        border: none !important;
        background: var(--surface-color) !important;
        color: var(--text-main) !important;
        font-weight: 600 !important;
        padding: 8px 24px !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03) !important;
        transition: all 0.3s ease !important;
    }}
    .stButton > button:hover {{
        background: var(--theme-color) !important;
        color: #FFFFFF !important;
        transform: scale(1.02);
        box-shadow: 0 6px 20px rgba(0,0,0,0.08) !important;
    }}

    /* KPI Cards */
    .kpi-card {{
        background: var(--surface-color);
        border-radius: 24px;
        padding: 24px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.04);
        text-align: center;
        height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        margin-bottom: 24px;
        transition: transform 0.3s ease;
    }}
    .kpi-card:hover {{ transform: translateY(-2px); }}
    .kpi-title {{ color: var(--text-muted); font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }}
    .kpi-value {{ color: var(--text-main); font-size: 2.5rem; font-weight: 700; line-height: 1; }}
    .kpi-value span {{ font-size: 1.2rem; color: var(--text-muted); margin-left: 4px; }}

    /* Gallery Cards */
    .gallery-card {{
        background: var(--surface-color);
        border-radius: 24px;
        padding: 24px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.04);
        margin-bottom: 16px;
    }}
    .gc-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }}
    .gc-title {{ font-size: 1.2rem; font-weight: 600; color: var(--text-main); }}
    .gc-stats {{ font-size: 0.9rem; color: var(--text-muted); }}
    .gc-tags {{ display: flex; gap: 8px; margin-bottom: 16px; flex-wrap: wrap; }}
    .gc-tag {{ background: var(--bg-color); color: var(--text-muted); font-size: 0.75rem; padding: 4px 10px; border-radius: 12px; font-weight: 500; }}
    .progress-track {{ width: 100%; height: 8px; background: var(--bg-color); border-radius: 4px; overflow: hidden; }}
    .progress-fill {{ height: 100%; border-radius: 4px; transition: width 1s ease; }}
    .child-progress-container {{ margin-top: 12px; }}
    .child-progress-label {{ display: flex; justify-content: space-between; font-size: 0.8rem; color: var(--text-muted); margin-bottom: 4px; }}
    
    /* Chart Containers */
    .chart-card {{
        background: var(--surface-color);
        border-radius: 24px;
        padding: 24px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.04);
        margin-bottom: 24px;
    }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. State Management
# ==========================================
if 'timer_state' not in st.session_state: st.session_state.timer_state = 'idle'
if 'start_time' not in st.session_state: st.session_state.start_time = None

# ==========================================
# 4. Sidebar (Non-High-Frequency Zone)
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='font-weight: 600; margin-bottom: 32px;'>Preferences</h2>", unsafe_allow_html=True)
    
    new_color = st.color_picker("Theme Color", theme_color)
    if new_color != theme_color:
        config["theme_color"] = new_color
        save_config(config)
        st.rerun()
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.expander("Subject Laboratory", expanded=False):
        st.markdown("**1. Add Subject**")
        new_parent = st.text_input("Subject Name", key="new_p")
        new_p_target = st.number_input("Target (Hours)", min_value=1, value=50, key="new_p_t")
        if st.button("Create Subject", use_container_width=True) and new_parent:
            if new_parent not in config["subjects"]:
                config["subjects"][new_parent] = {"target_hours": new_p_target, "children": {}}
                save_config(config)
                st.rerun()
                
        st.markdown("<hr style='margin: 16px 0;'>", unsafe_allow_html=True)
        st.markdown("**2. Add Task**")
        if config["subjects"]:
            sel_p_for_c = st.selectbox("Select Subject", list(config["subjects"].keys()), key="sel_p_c")
            new_child = st.text_input("Task Name", key="new_c")
            new_c_target = st.number_input("Task Target (Hours)", min_value=1, value=10, key="new_c_t")
            if st.button("Create Task", use_container_width=True) and new_child:
                if new_child not in config["subjects"][sel_p_for_c]["children"]:
                    config["subjects"][sel_p_for_c]["children"][new_child] = {"target_hours": new_c_target}
                    save_config(config)
                    st.rerun()
                    
        st.markdown("<hr style='margin: 16px 0;'>", unsafe_allow_html=True)
        st.markdown("**3. Rename**")
        if config["subjects"]:
            rn_parent = st.selectbox("Subject to Rename", list(config["subjects"].keys()), key="rn_p")
            new_rn_name = st.text_input("New Name", key="rn_n")
            if st.button("Rename Subject", use_container_width=True) and new_rn_name:
                config["subjects"][new_rn_name] = config["subjects"].pop(rn_parent)
                save_config(config)
                st.rerun()
                
        st.markdown("<hr style='margin: 16px 0;'>", unsafe_allow_html=True)
        st.markdown("**4. Delete**")
        if config["subjects"]:
            del_parent = st.selectbox("Subject to Delete", list(config["subjects"].keys()), key="del_p")
            if st.button("Delete Subject", use_container_width=True):
                del config["subjects"][del_parent]
                save_config(config)
                st.rerun()

# ==========================================
# 5. Data Processing
# ==========================================
df = pd.read_csv(DATA_FILE)
df['timestamp'] = pd.to_datetime(df['timestamp'])
now = datetime.now()

# ==========================================
# 6. Central Core L1 (Header & Controls)
# ==========================================
col_l1_left, col_l1_right = st.columns([1.5, 1])

with col_l1_right:
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    time_filter = st.radio("Time Dimension", ["Today", "This Week", "This Month", "This Year"], horizontal=True, label_visibility="collapsed")

if time_filter == "Today":
    filtered_df = df[df['timestamp'].dt.date == now.date()]
elif time_filter == "This Week":
    start_of_week = now - timedelta(days=now.weekday())
    filtered_df = df[df['timestamp'].dt.date >= start_of_week.date()]
elif time_filter == "This Month":
    filtered_df = df[(df['timestamp'].dt.year == now.year) & (df['timestamp'].dt.month == now.month)]
else:
    filtered_df = df[df['timestamp'].dt.year == now.year]

with col_l1_left:
    parent_subjects = list(config["subjects"].keys())
    if not parent_subjects:
        st.warning("Please configure subjects in the Preferences sidebar.")
    else:
        c_sel1, c_sel2 = st.columns(2)
        with c_sel1:
            sel_parent = st.selectbox("Subject", parent_subjects, disabled=(st.session_state.timer_state != 'idle'), label_visibility="collapsed")
        with c_sel2:
            child_dict = config["subjects"][sel_parent]["children"]
            child_list = list(child_dict.keys())
            sel_child = st.selectbox("Task", child_list if child_list else["General"], disabled=(st.session_state.timer_state != 'idle'), label_visibility="collapsed")
        
        if st.session_state.timer_state == 'idle':
            st.markdown(f"""
                <div style="font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 3.5rem; font-weight: 300; color: var(--text-main); line-height: 1.2; margin: 10px 0;">
                    00:00:00
                </div>
            """, unsafe_allow_html=True)
            if st.button("Start Session"):
                st.session_state.start_time = time.time()
                st.session_state.timer_state = 'running'
                st.rerun()
                
        elif st.session_state.timer_state == 'running':
            start_ms = st.session_state.start_time * 1000
            timer_html = f"""
            <style>
                body {{ margin: 0; background: transparent; color: {theme_color}; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 3.5rem; font-weight: 300; line-height: 1.2; padding: 10px 0; }}
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
            components.html(timer_html, height=80)
            
            if st.button("End Session"):
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

st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

# ==========================================
# 7. Central Core L2 (KPIs)
# ==========================================
total_minutes = filtered_df['duration_minutes'].sum() if not filtered_df.empty else 0
total_hours = total_minutes / 60
active_subjects = filtered_df['parent_subject'].nunique() if not filtered_df.empty else 0
avg_score = filtered_df['focus_score'].mean() if not filtered_df.empty else 0.0

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f"""<div class="kpi-card"><div class="kpi-title">Total Duration</div><div class="kpi-value">{total_hours:.1f}<span>h</span></div></div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="kpi-card"><div class="kpi-title">Active Subjects</div><div class="kpi-value">{active_subjects}</div></div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div class="kpi-card"><div class="kpi-title">Average Focus</div><div class="kpi-value">{avg_score:.1f}<span>Stars</span></div></div>""", unsafe_allow_html=True)

# ==========================================
# 8. Central Core L3 (Content)
# ==========================================
col_l3_left, col_l3_right = st.columns([1.5, 1])

with col_l3_left:
    st.markdown("<h3 style='font-size: 1.2rem; font-weight: 600; margin-bottom: 16px;'>Subject Gallery</h3>", unsafe_allow_html=True)
    
    parent_group = filtered_df.groupby('parent_subject')['duration_minutes'].sum() if not filtered_df.empty else pd.Series()
    
    for idx, (parent, details) in enumerate(config["subjects"].items()):
        target_h = get_parent_target(parent)
        current_m = parent_group.get(parent, 0)
        current_h = current_m / 60
        progress_pct = min((current_h / target_h) * 100, 100) if target_h > 0 else 0
        card_color = palette[idx % len(palette)]
        
        children = details.get("children", {})
        tags_html = "".join([f"<div class='gc-tag'>{child}</div>" for child in list(children.keys())[:3]])
        
        with st.container():
            st.markdown(f"""
            <div class="gallery-card">
                <div class="gc-header">
                    <div class="gc-title">{parent}</div>
                    <div class="gc-stats">{current_h:.1f}h / {target_h}h</div>
                </div>
                <div class="gc-tags">{tags_html}</div>
                <div class="progress-track">
                    <div class="progress-fill" style="width: {progress_pct}%; background-color: {card_color};"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if children:
                with st.expander(f"Details: {parent}"):
                    child_df = filtered_df[filtered_df['parent_subject'] == parent] if not filtered_df.empty else pd.DataFrame()
                    child_group = child_df.groupby('child_subject')['duration_minutes'].sum() if not child_df.empty else pd.Series()
                    
                    for child, c_details in children.items():
                        c_target_h = c_details.get("target_hours", 0)
                        c_current_m = child_group.get(child, 0)
                        c_current_h = c_current_m / 60
                        c_pct = min((c_current_h / c_target_h) * 100, 100) if c_target_h > 0 else 0
                        
                        st.markdown(f"""
                        <div class="child-progress-container">
                            <div class="child-progress-label">
                                <span>{child}</span>
                                <span>{c_current_h:.1f}h / {c_target_h}h</span>
                            </div>
                            <div class="progress-track" style="height: 4px;">
                                <div class="progress-fill" style="width: {c_pct}%; background-color: {card_color}; opacity: 0.7;"></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

with col_l3_right:
    st.markdown("<h3 style='font-size: 1.2rem; font-weight: 600; margin-bottom: 16px;'>Insights</h3>", unsafe_allow_html=True)
    
    # Apple Watch Style Comparison (Today vs Yesterday)
    yesterday_df = df[df['timestamp'].dt.date == (now.date() - timedelta(days=1))]
    y_hours = yesterday_df['duration_minutes'].sum() / 60 if not yesterday_df.empty else 0
    t_hours = df[df['timestamp'].dt.date == now.date()]['duration_minutes'].sum() / 60 if not df.empty else 0
    
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = t_hours,
        title = {'text': "Today vs Yesterday (Hours)", 'font': {'size': 14, 'color': '#86868B'}},
        delta = {'reference': y_hours, 'increasing': {'color': theme_color}},
        gauge = {
            'axis': {'range':[None, max(t_hours, y_hours, 8)], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': theme_color},
            'bgcolor': "#F5F5F7",
            'borderwidth': 0,
            'threshold': {'line': {'color': "#86868B", 'width': 2}, 'thickness': 0.75, 'value': y_hours}
        }
    ))
    fig_gauge.update_layout(height=220, margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor='rgba(0,0,0,0)', font={'family': "-apple-system, sans-serif"})
    st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False})
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Time Distribution Donut
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    if not filtered_df.empty:
        fig_pie = px.pie(filtered_df, names='parent_subject', values='duration_minutes', hole=0.75, color_discrete_sequence=palette)
        fig_pie.update_traces(textposition='inside', textinfo='percent', marker=dict(line=dict(color='#FFFFFF', width=2)))
        fig_pie.update_layout(
            showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
            height=260, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)', font={'family': "-apple-system, sans-serif"}
        )
        # Center Text
        fig_pie.add_annotation(text=f"<b>{total_hours:.1f}h</b>", x=0.5, y=0.5, font_size=24, showarrow=False, font_color="#1D1D1F")
        st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})
    else:
        st.markdown("<div style='height: 260px; display: flex; align-items: center; justify-content: center; color: var(--text-muted);'>No data available</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 9. Central Core L4 (Heatmap)
# ==========================================
st.markdown("<h3 style='font-size: 1.2rem; font-weight: 600; margin-top: 16px; margin-bottom: 16px;'>Activity Heatmap</h3>", unsafe_allow_html=True)
st.markdown("<div class='chart-card'>", unsafe_allow_html=True)

end_date = now.date()
start_date = end_date - timedelta(days=365)
date_range = pd.date_range(start=start_date, end=end_date)
heatmap_df = pd.DataFrame({'date': date_range})
heatmap_df['date_str'] = heatmap_df['date'].dt.strftime('%Y-%m-%d')

if not df.empty:
    df['date_str'] = df['timestamp'].dt.strftime('%Y-%m-%d')
    daily_sum = df.groupby('date_str')['duration_minutes'].sum().reset_index()
    heatmap_df = pd.merge(heatmap_df, daily_sum, on='date_str', how='left').fillna(0)
else:
    heatmap_df['duration_minutes'] = 0

heatmap_df['week'] = heatmap_df['date'].dt.isocalendar().week
heatmap_df['year'] = heatmap_df['date'].dt.isocalendar().year
heatmap_df['week_id'] = heatmap_df['year'].astype(str) + '-' + heatmap_df['week'].astype(str).str.zfill(2)

unique_weeks = sorted(heatmap_df['week_id'].unique())
week_mapping = {w: i for i, w in enumerate(unique_weeks)}

heatmap_df['x'] = heatmap_df['week_id'].map(week_mapping)
heatmap_df['y'] = heatmap_df['date'].dt.weekday

fig_heat = go.Figure(data=go.Heatmap(
    z=heatmap_df['duration_minutes'],
    x=heatmap_df['x'],
    y=heatmap_df['y'],
    colorscale=[[0, '#F5F5F7'],[1, theme_color]],
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