import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components

# ==========================================
# 1. 基础配置与初始化 (Data Foundation)
# ==========================================
st.set_page_config(page_title="Glass Tracker", page_icon="", layout="wide", initial_sidebar_state="expanded")

DATA_FILE = "learning_logs.csv"
CONFIG_FILE = "subjects.json"

def init_system():
    """初始化数据文件和配置"""
    if not os.path.exists(CONFIG_FILE):
        default_config = {
            "theme_color": "#007AFF", # Apple Blue
            "subjects": {
                "💻 编程开发": ["Python", "Streamlit", "SQL"],
                "🇬🇧 语言学习": ["阅读", "听力", "口语"],
                "📖 深度阅读": ["专业书籍", "商业思维"]
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
# 2. 状态管理 (State Management)
# ==========================================
if 'timer_state' not in st.session_state:
    st.session_state.timer_state = 'idle' # idle, running, rating
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'elapsed_minutes' not in st.session_state:
    st.session_state.elapsed_minutes = 0

# ==========================================
# 3. 侧边栏：导航与菜单持久化 (Sidebar)
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='font-weight: 700; margin-bottom: 20px;'> Settings</h2>", unsafe_allow_html=True)
    
    tab_filter, tab_theme, tab_crud = st.tabs(["🎯 过滤", "🎨 主题", "📚 学科"])
    
    # --- Tab 1: 过滤设置 ---
    with tab_filter:
        st.markdown("<p style='color: #86868B; font-size: 0.9rem; font-weight: 600;'>时间维度 (Time Filter)</p>", unsafe_allow_html=True)
        time_filter = st.radio("选择范围",["今日", "本周", "本月", "本年", "全部"], label_visibility="collapsed")
        
        st.markdown("<br><p style='color: #86868B; font-size: 0.9rem; font-weight: 600;'>数据导出</p>", unsafe_allow_html=True)
        with open(DATA_FILE, "rb") as file:
            st.download_button("📥 下载 CSV 日志", data=file, file_name="learning_logs.csv", mime="text/csv", use_container_width=True)

    # --- Tab 2: 主题设置 ---
    with tab_theme:
        st.markdown("<p style='color: #86868B; font-size: 0.9rem; font-weight: 600;'>全局强调色</p>", unsafe_allow_html=True)
        new_color = st.color_picker("选择颜色", config.get("theme_color", "#007AFF"), label_visibility="collapsed")
        if new_color != config.get("theme_color"):
            config["theme_color"] = new_color
            save_config(config)
            st.rerun()

    # --- Tab 3: 完整学科管理系统 (CRUD) ---
    with tab_crud:
        st.markdown("<p style='color: #86868B; font-size: 0.9rem; font-weight: 600;'>管理父学科</p>", unsafe_allow_html=True)
        
        # 添加父学科
        new_parent = st.text_input("新增父学科", placeholder="输入名称...")
        if st.button("➕ 添加父学科", use_container_width=True) and new_parent:
            if new_parent not in config["subjects"]:
                config["subjects"][new_parent] =[]
                save_config(config)
                st.rerun()
                
        # 编辑/删除父学科
        if config["subjects"]:
            edit_parent = st.selectbox("选择要编辑的父学科", list(config["subjects"].keys()))
            col_p1, col_p2 = st.columns([2, 1])
            with col_p1:
                rename_parent = st.text_input("重命名", value=edit_parent, key="rename_p", label_visibility="collapsed")
            with col_p2:
                if st.button("保存", key="save_p", use_container_width=True) and rename_parent != edit_parent:
                    config["subjects"][rename_parent] = config["subjects"].pop(edit_parent)
                    # 同步更新 CSV 历史数据
                    df_temp = pd.read_csv(DATA_FILE)
                    df_temp.loc[df_temp['parent_subject'] == edit_parent, 'parent_subject'] = rename_parent
                    df_temp.to_csv(DATA_FILE, index=False)
                    save_config(config)
                    st.rerun()
            if st.button("🗑️ 删除该父学科", use_container_width=True):
                del config["subjects"][edit_parent]
                save_config(config)
                st.rerun()
                
            st.divider()
            
            # 管理子学科
            st.markdown("<p style='color: #86868B; font-size: 0.9rem; font-weight: 600;'>管理子学科</p>", unsafe_allow_html=True)
            new_child = st.text_input("新增子学科", placeholder=f"添加到 {edit_parent}...")
            if st.button("➕ 添加子学科", use_container_width=True) and new_child:
                if new_child not in config["subjects"][edit_parent]:
                    config["subjects"][edit_parent].append(new_child)
                    save_config(config)
                    st.rerun()
                    
            children = config["subjects"][edit_parent]
            if children:
                edit_child = st.selectbox("选择要编辑的子学科", children)
                col_c1, col_c2 = st.columns([2, 1])
                with col_c1:
                    rename_child = st.text_input("重命名", value=edit_child, key="rename_c", label_visibility="collapsed")
                with col_c2:
                    if st.button("保存", key="save_c", use_container_width=True) and rename_child != edit_child:
                        idx = config["subjects"][edit_parent].index(edit_child)
                        config["subjects"][edit_parent][idx] = rename_child
                        df_temp = pd.read_csv(DATA_FILE)
                        df_temp.loc[(df_temp['parent_subject'] == edit_parent) & (df_temp['child_subject'] == edit_child), 'child_subject'] = rename_child
                        df_temp.to_csv(DATA_FILE, index=False)
                        save_config(config)
                        st.rerun()
                if st.button("🗑️ 删除该子学科", use_container_width=True):
                    config["subjects"][edit_parent].remove(edit_child)
                    save_config(config)
                    st.rerun()

# ==========================================
# 4. 全局 CSS 注入 (Glassmorphism & Apple Style)
# ==========================================
theme_color = config.get("theme_color", "#007AFF")

st.markdown(f"""
<style>
    :root {{
        --primary-color: {theme_color};
        --bg-gradient: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%);
        --glass-bg: rgba(255, 255, 255, 0.65);
        --glass-border: rgba(255, 255, 255, 0.4);
        --glass-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.05);
    }}
    
    /* 隐藏默认元素 */
    #MainMenu, header, footer {{visibility: hidden;}}
    
    /* 全局背景 */
    .stApp {{
        background: var(--bg-gradient);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }}
    
    /* 玻璃拟态卡片基础类 */
    .glass-card {{
        background: var(--glass-bg);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid var(--glass-border);
        border-radius: 24px;
        padding: 24px;
        box-shadow: var(--glass-shadow);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        margin-bottom: 24px;
    }}
    .glass-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.08);
    }}
    
    /* KPI 容器：强制等高与对齐 */
    .kpi-grid {{
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 20px;
        margin-bottom: 24px;
    }}
    .kpi-item {{
        background: var(--glass-bg);
        backdrop-filter: blur(16px);
        border: 1px solid var(--glass-border);
        border-radius: 24px;
        box-shadow: var(--glass-shadow);
        height: 130px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        padding: 16px;
    }}
    .kpi-title {{
        color: #86868B;
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    .kpi-value {{
        color: #1D1D1F;
        font-size: 2.2rem;
        font-weight: 700;
        line-height: 1.2;
    }}
    .kpi-value span {{
        color: var(--primary-color);
        font-size: 1.2rem;
        margin-left: 4px;
    }}
    
    /* Apple Watch 风格进度条 */
    .aw-progress-container {{
        margin-bottom: 16px;
    }}
    .aw-progress-header {{
        display: flex;
        justify-content: space-between;
        margin-bottom: 6px;
        font-size: 0.95rem;
        font-weight: 600;
        color: #1D1D1F;
    }}
    .aw-progress-track {{
        width: 100%;
        height: 12px;
        background-color: rgba(0,0,0,0.05);
        border-radius: 10px;
        overflow: hidden;
    }}
    .aw-progress-fill {{
        height: 100%;
        background-color: var(--primary-color);
        border-radius: 10px;
        transition: width 1s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    .aw-child-track {{
        height: 6px;
        margin-top: 4px;
        background-color: rgba(0,0,0,0.03);
    }}
    .aw-child-fill {{
        background-color: var(--primary-color);
        opacity: 0.6;
    }}
    
    /* 按钮美化 */
    .stButton>button {{
        border-radius: 14px !important;
        font-weight: 600 !important;
        border: 1px solid rgba(0,0,0,0.05) !important;
        background: rgba(255,255,255,0.8) !important;
        color: #1D1D1F !important;
        backdrop-filter: blur(10px) !important;
        transition: all 0.3s ease !important;
    }}
    .stButton>button:hover {{
        background: var(--primary-color) !important;
        color: #FFFFFF !important;
        border-color: var(--primary-color) !important;
        transform: scale(1.02);
    }}
    
    /* 空状态 */
    .empty-state {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 300px;
        text-align: center;
        color: #86868B;
    }}
    .empty-state h3 {{
        color: #1D1D1F;
        margin-top: 16px;
    }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 5. 数据过滤逻辑 (Data Filtering)
# ==========================================
df = pd.read_csv(DATA_FILE)
df['timestamp'] = pd.to_datetime(df['timestamp'])
now = datetime.now()

if time_filter == "今日":
    filtered_df = df[df['timestamp'].dt.date == now.date()]
elif time_filter == "本周":
    start_of_week = now - timedelta(days=now.weekday())
    filtered_df = df[df['timestamp'].dt.date >= start_of_week.date()]
elif time_filter == "本月":
    filtered_df = df[(df['timestamp'].dt.year == now.year) & (df['timestamp'].dt.month == now.month)]
elif time_filter == "本年":
    filtered_df = df[df['timestamp'].dt.year == now.year]
else:
    filtered_df = df.copy()

# ==========================================
# 6. 主界面布局 (Main Layout)
# ==========================================
col_left, col_right = st.columns([1.2, 2.8], gap="large")

# ------------------------------------------
# 左侧：计时器系统 (Timer System)
# ------------------------------------------
with col_left:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color: #1D1D1F; margin-bottom: 20px; font-weight: 700;'>⏱️ Focus</h3>", unsafe_allow_html=True)
    
    parent_subjects = list(config["subjects"].keys())
    if not parent_subjects:
        st.warning("请先在侧边栏添加学科！")
    else:
        sel_parent = st.selectbox("领域 (Domain)", parent_subjects, disabled=(st.session_state.timer_state != 'idle'))
        child_subjects = config["subjects"][sel_parent]
        sel_child = st.selectbox("任务 (Task)", child_subjects if child_subjects else ["无"], disabled=(st.session_state.timer_state != 'idle'))
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.session_state.timer_state == 'idle':
            st.markdown(f"""
                <div style="text-align: center; font-family: 'SF Mono', ui-monospace, monospace; font-size: 4.5rem; font-weight: 700; color: #1D1D1F; margin: 10px 0 30px 0; letter-spacing: -2px;">
                    00:00<span style="font-size: 2rem; color: #86868B;">:00</span>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("▶ 开始专注", use_container_width=True):
                st.session_state.start_time = datetime.now()
                st.session_state.timer_state = 'running'
                st.rerun()
                
        elif st.session_state.timer_state == 'running':
            # 注入 JS 实现不阻塞的动态计时器
            timer_html = f"""
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@700&display=swap');
                body {{
                    display: flex; justify-content: center; align-items: center;
                    margin: 0; background-color: transparent;
                    color: {theme_color}; font-family: 'Roboto Mono', monospace; font-size: 4.5rem; letter-spacing: -2px;
                }}
                .sec {{ font-size: 2rem; color: #86868B; }}
            </style>
            <div id="stopwatch">00:00<span class="sec">:00</span></div>
            <script>
                var startTime = new Date("{st.session_state.start_time.isoformat()}").getTime();
                setInterval(function() {{
                    var now = new Date().getTime();
                    var distance = now - startTime;
                    var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                    var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
                    var seconds = Math.floor((distance % (1000 * 60)) / 1000);
                    
                    var h = (hours < 10 ? "0" + hours : hours);
                    var m = (minutes < 10 ? "0" + minutes : minutes);
                    var s = (seconds < 10 ? "0" + seconds : seconds);
                    
                    if(hours > 0) {{
                        document.getElementById("stopwatch").innerHTML = h + ":" + m + '<span class="sec">:' + s + '</span>';
                    }} else {{
                        document.getElementById("stopwatch").innerHTML = m + ":" + s + '<span class="sec"></span>';
                    }}
                }}, 1000);
            </script>
            """
            components.html(timer_html, height=120)
            
            if st.button("⏹ 停止并结算", use_container_width=True):
                delta = datetime.now() - st.session_state.start_time
                st.session_state.elapsed_minutes = round(delta.total_seconds() / 60, 2)
                st.session_state.timer_state = 'rating'
                st.rerun()
                
        elif st.session_state.timer_state == 'rating':
            st.markdown(f"""
                <div style="text-align: center; font-size: 2.5rem; font-weight: 700; color: {theme_color}; margin: 20px 0;">
                    {st.session_state.elapsed_minutes} <span style="font-size: 1.2rem; color: #86868B;">min</span>
                </div>
            """, unsafe_allow_html=True)
            
            focus_score = st.slider("专注度评分 (1-5星)", 1, 5, 5)
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button("💾 保存", use_container_width=True):
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
                if st.button("🗑️ 放弃", use_container_width=True):
                    st.session_state.timer_state = 'idle'
                    st.rerun()
                    
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------
# 右侧：统计看板区 (Dashboard)
# ------------------------------------------
with col_right:
    # 1. 核心指标卡 (KPI Grid - 强制对齐)
    total_minutes = filtered_df['duration_minutes'].sum() if not filtered_df.empty else 0
    total_hours = total_minutes / 60
    
    if not filtered_df.empty:
        top_subject = filtered_df.groupby('parent_subject')['duration_minutes'].sum().idxmax()
        avg_score = filtered_df['focus_score'].mean()
    else:
        top_subject = "-"
        avg_score = 0.0

    # 动态标题
    title_prefix = time_filter if time_filter != "全部" else "累计"
    
    st.markdown(f"""
    <div class="kpi-grid">
        <div class="kpi-item">
            <div class="kpi-title">{title_prefix}总时长</div>
            <div class="kpi-value">{total_hours:.1f}<span>h</span></div>
        </div>
        <div class="kpi-item">
            <div class="kpi-title">最勤奋学科</div>
            <div class="kpi-value" style="font-size: 1.6rem;">{top_subject}</div>
        </div>
        <div class="kpi-item">
            <div class="kpi-title">平均专注度</div>
            <div class="kpi-value">{avg_score:.1f}<span>★</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. 进度与图表区 (2x2 布局模拟)
    if filtered_df.empty:
        st.markdown(f"""
        <div class="glass-card empty-state">
            <div style="font-size: 4rem; opacity: 0.5;">✨</div>
            <h3>暂无数据</h3>
            <p>当前时间范围内没有学习记录，去左侧开启一次专注吧。</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        col_chart1, col_chart2 = st.columns(2, gap="large")
        
        # 左侧：Apple Watch 风格层级进度条
        with col_chart1:
            st.markdown("<div class='glass-card' style='height: 380px; overflow-y: auto;'>", unsafe_allow_html=True)
            st.markdown("<h4 style='color: #1D1D1F; margin-bottom: 20px; font-weight: 700;'>📊 学科进度 (Progress)</h4>", unsafe_allow_html=True)
            
            # 计算最大值用于进度条比例
            parent_group = filtered_df.groupby('parent_subject')['duration_minutes'].sum()
            max_minutes = parent_group.max() if not parent_group.empty else 1
            
            progress_html = ""
            for parent, p_mins in parent_group.sort_values(ascending=False).items():
                p_hours = p_mins / 60
                p_percent = (p_mins / max_minutes) * 100
                
                progress_html += f"""
                <div class="aw-progress-container">
                    <div class="aw-progress-header">
                        <span>{parent}</span>
                        <span style="color: #86868B;">{p_hours:.1f}h</span>
                    </div>
                    <div class="aw-progress-track">
                        <div class="aw-progress-fill" style="width: {p_percent}%;"></div>
                    </div>
                """
                
                # 子学科进度
                child_df = filtered_df[filtered_df['parent_subject'] == parent]
                if not child_df.empty:
                    child_group = child_df.groupby('child_subject')['duration_minutes'].sum()
                    for child, c_mins in child_group.sort_values(ascending=False).items():
                        c_percent = (c_mins / max_minutes) * 100
                        progress_html += f"""
                        <div class="aw-progress-track aw-child-track" title="{child}: {c_mins/60:.1f}h">
                            <div class="aw-progress-fill aw-child-fill" style="width: {c_percent}%;"></div>
                        </div>
                        """
                progress_html += "</div>"
                
            st.markdown(progress_html, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        # 右侧：动态环形图
        with col_chart2:
            st.markdown("<div class='glass-card' style='height: 380px;'>", unsafe_allow_html=True)
            st.markdown("<h4 style='color: #1D1D1F; margin-bottom: 0px; font-weight: 700;'>🍩 时间分布 (Distribution)</h4>", unsafe_allow_html=True)
            
            fig = px.pie(
                filtered_df, 
                names='parent_subject', 
                values='duration_minutes', 
                hole=0.65,
                color_discrete_sequence=px.colors.sequential.Blues_r # 使用蓝色系适配 Apple 风格
            )
            fig.update_traces(textposition='outside', textinfo='percent+label', marker=dict(line=dict(color='#FFFFFF', width=2)))
            fig.update_layout(
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(t=20, b=20, l=20, r=20),
                height=280,
                font=dict(family="-apple-system, sans-serif", color="#86868B")
            )
            # 动态中心文本
            fig.add_annotation(
                text=f"<b>{total_hours:.1f}h</b><br>Total",
                x=0.5, y=0.5, font_size=20, showarrow=False, font_color="#1D1D1F"
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            st.markdown("</div>", unsafe_allow_html=True)