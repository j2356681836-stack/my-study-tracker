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
st.set_page_config(page_title="Learning Tracker", page_icon="", layout="wide")

DATA_FILE = "learning_logs.csv"
CONFIG_FILE = "subjects.json"

def init_system():
    """初始化数据文件和配置"""
    if not os.path.exists(CONFIG_FILE):
        default_config = {
            "theme_color": "#007AFF", # Apple Blue
            "subjects": {
                "💻 编程开发": ["Python", "Streamlit", "SQL"],
                "🇬🇧 语言学习":["阅读", "听力", "口语"],
                "📖 深度阅读":["专业书籍", "商业思维"]
            }
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(default_config, f, ensure_ascii=False, indent=4)
            
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=["timestamp", "parent_subject", "child_subject", "duration_minutes", "focus_score"])
        df.to_csv(DATA_FILE, index=False, encoding="utf-8")

init_system()

# 加载配置
with open(CONFIG_FILE, "r", encoding="utf-8") as f:
    config = json.load(f)

def save_config(new_config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(new_config, f, ensure_ascii=False, indent=4)

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
# 3. UI/UX 设计与 CSS 注入 (Apple Style)
# ==========================================
theme_color = config.get("theme_color", "#007AFF")

def inject_custom_css():
    st.markdown(f"""
    <style>
        /* 隐藏默认头部和底部 */
        #MainMenu {{visibility: hidden;}}
        header {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        
        /* 全局字体与背景 */
        .stApp {{
            background-color: #F5F5F7;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }}
        
        /* Apple 风格悬浮卡片 */
        .apple-card {{
            background-color: #FFFFFF;
            border-radius: 20px;
            padding: 24px;
            box-shadow: 0 4px 24px rgba(0,0,0,0.04);
            margin-bottom: 24px;
            transition: transform 0.2s ease;
        }}
        .apple-card:hover {{
            box-shadow: 0 8px 32px rgba(0,0,0,0.08);
        }}
        
        /* 指标卡片样式 */
        .metric-title {{
            color: #86868B;
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }}
        .metric-value {{
            color: #1D1D1F;
            font-size: 2.2rem;
            font-weight: 700;
        }}
        .metric-value span {{
            color: {theme_color};
        }}
        
        /* 按钮动态主题色 */
        .stButton>button {{
            border-radius: 12px !important;
            font-weight: 600 !important;
            border: none !important;
            background-color: #E8E8ED !important;
            color: #1D1D1F !important;
            transition: all 0.3s ease !important;
        }}
        .stButton>button:hover {{
            background-color: {theme_color} !important;
            color: #FFFFFF !important;
            transform: scale(1.02);
        }}
        .primary-btn>div>button {{
            background-color: {theme_color} !important;
            color: #FFFFFF !important;
        }}
    </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# ==========================================
# 4. 侧边栏：设置与过滤 (Sidebar)
# ==========================================
with st.sidebar:
    st.markdown(f"<h2 style='color: #1D1D1F; font-weight: 700;'> Settings</h2>", unsafe_allow_html=True)
    
    # 全局动态配色
    new_color = st.color_picker("主题配色 (Theme Color)", theme_color)
    if new_color != theme_color:
        config["theme_color"] = new_color
        save_config(config)
        st.rerun()
        
    st.markdown("---")
    
    # 多维度时间过滤器
    st.markdown("<p style='color: #86868B; font-weight: 600;'>时间维度 (Time Filter)</p>", unsafe_allow_html=True)
    time_filter = st.radio("选择范围",["今日", "本周", "本月", "本年", "全部"], label_visibility="collapsed")
    
    st.markdown("---")
    
    # 层级学科管理
    with st.expander("📚 学科管理 (Subjects)"):
        st.markdown("**添加父学科**")
        new_parent = st.text_input("父学科名称", key="new_parent")
        if st.button("添加父学科", use_container_width=True):
            if new_parent and new_parent not in config["subjects"]:
                config["subjects"][new_parent] =[]
                save_config(config)
                st.rerun()
                
        st.markdown("**添加子学科**")
        if config["subjects"]:
            selected_parent_add = st.selectbox("选择父学科", list(config["subjects"].keys()), key="sel_p_add")
            new_child = st.text_input("子学科名称", key="new_child")
            if st.button("添加子学科", use_container_width=True):
                if new_child and new_child not in config["subjects"][selected_parent_add]:
                    config["subjects"][selected_parent_add].append(new_child)
                    save_config(config)
                    st.rerun()
        
        st.markdown("**删除操作**")
        del_parent = st.selectbox("删除父学科", ["--选择--"] + list(config["subjects"].keys()))
        if st.button("删除该父学科", use_container_width=True) and del_parent != "--选择--":
            del config["subjects"][del_parent]
            save_config(config)
            st.rerun()

    st.markdown("---")
    
    # 数据导出
    st.markdown("<p style='color: #86868B; font-weight: 600;'>数据导出 (Export)</p>", unsafe_allow_html=True)
    with open(DATA_FILE, "rb") as file:
        st.download_button(
            label="下载 CSV 日志",
            data=file,
            file_name="learning_logs.csv",
            mime="text/csv",
            use_container_width=True
        )

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
    st.markdown("<div class='apple-card'>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color: #1D1D1F; margin-bottom: 20px;'>⏱️ 专注计时</h3>", unsafe_allow_html=True)
    
    # 学科选择
    parent_subjects = list(config["subjects"].keys())
    if not parent_subjects:
        st.warning("请先在侧边栏添加学科！")
    else:
        sel_parent = st.selectbox("选择领域 (Parent)", parent_subjects, disabled=(st.session_state.timer_state != 'idle'))
        child_subjects = config["subjects"][sel_parent]
        sel_child = st.selectbox("当前任务 (Child)", child_subjects if child_subjects else ["无"], disabled=(st.session_state.timer_state != 'idle'))
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 计时器 UI 逻辑
        if st.session_state.timer_state == 'idle':
            # 静态显示 00:00:00
            st.markdown(f"""
                <div style="text-align: center; font-family: 'SF Mono', ui-monospace, monospace; font-size: 4rem; font-weight: 700; color: #1D1D1F; margin: 20px 0;">
                    00:00:00
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<div class='primary-btn'>", unsafe_allow_html=True)
            if st.button("▶ 开始专注 (Start)", use_container_width=True):
                st.session_state.start_time = datetime.now()
                st.session_state.timer_state = 'running'
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            
        elif st.session_state.timer_state == 'running':
            # 注入 JS 实现不阻塞的动态计时器 (Apple 风格等宽字体)
            timer_html = f"""
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@700&display=swap');
                body {{
                    display: flex; justify-content: center; align-items: center;
                    margin: 0; background-color: transparent;
                    color: {theme_color}; font-family: 'Roboto Mono', monospace; font-size: 4rem;
                }}
            </style>
            <div id="stopwatch">00:00:00</div>
            <script>
                var startTime = new Date("{st.session_state.start_time.isoformat()}").getTime();
                setInterval(function() {{
                    var now = new Date().getTime();
                    var distance = now - startTime;
                    var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                    var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
                    var seconds = Math.floor((distance % (1000 * 60)) / 1000);
                    document.getElementById("stopwatch").innerHTML = 
                        (hours < 10 ? "0" + hours : hours) + ":" + 
                        (minutes < 10 ? "0" + minutes : minutes) + ":" + 
                        (seconds < 10 ? "0" + seconds : seconds);
                }}, 1000);
            </script>
            """
            components.html(timer_html, height=100)
            
            if st.button("⏹ 停止并结算 (Stop)", use_container_width=True):
                delta = datetime.now() - st.session_state.start_time
                st.session_state.elapsed_minutes = round(delta.total_seconds() / 60, 2)
                st.session_state.timer_state = 'rating'
                st.rerun()
                
        elif st.session_state.timer_state == 'rating':
            st.markdown(f"""
                <div style="text-align: center; font-size: 2rem; font-weight: 700; color: {theme_color}; margin: 20px 0;">
                    {st.session_state.elapsed_minutes} 分钟
                </div>
            """, unsafe_allow_html=True)
            
            focus_score = st.slider("专注度评分 (1-5星)", 1, 5, 5)
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                st.markdown("<div class='primary-btn'>", unsafe_allow_html=True)
                if st.button("保存记录", use_container_width=True):
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
                st.markdown("</div>", unsafe_allow_html=True)
            with col_btn2:
                if st.button("放弃", use_container_width=True):
                    st.session_state.timer_state = 'idle'
                    st.rerun()
                    
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------
# 右侧：统计看板区 (Dashboard)
# ------------------------------------------
with col_right:
    # 1. 核心指标卡 (3 Cards)
    total_minutes = filtered_df['duration_minutes'].sum() if not filtered_df.empty else 0
    total_hours = total_minutes / 60
    
    unique_days = filtered_df['timestamp'].dt.date.nunique() if not filtered_df.empty else 1
    unique_days = unique_days if unique_days > 0 else 1
    daily_avg_hours = total_hours / unique_days
    
    if not filtered_df.empty:
        top_subject = filtered_df.groupby('parent_subject')['duration_minutes'].sum().idxmax()
    else:
        top_subject = "暂无数据"

    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown(f"""
        <div class="apple-card">
            <div class="metric-title">总学习时长</div>
            <div class="metric-value"><span>{total_hours:.1f}</span> h</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        st.markdown(f"""
        <div class="apple-card">
            <div class="metric-title">日均时长 ({time_filter})</div>
            <div class="metric-value"><span>{daily_avg_hours:.1f}</span> h</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c3:
        st.markdown(f"""
        <div class="apple-card">
            <div class="metric-title">最勤奋学科</div>
            <div class="metric-value" style="font-size: 1.5rem; line-height: 2.2rem;">{top_subject}</div>
        </div>
        """, unsafe_allow_html=True)

    # 2. 学科进度条 (Parent-Child Progress Logic)
    st.markdown("<div class='apple-card'>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: #1D1D1F; margin-bottom: 20px;'>📊 学科时间分布</h4>", unsafe_allow_html=True)
    
    if not filtered_df.empty:
        # 自动汇总父学科下的所有子学科时长
        parent_group = filtered_df.groupby('parent_subject')['duration_minutes'].sum().reset_index()
        parent_group = parent_group.sort_values('duration_minutes', ascending=True)
        
        fig_bar = px.bar(
            parent_group, 
            x='duration_minutes', 
            y='parent_subject', 
            orientation='h',
            color_discrete_sequence=[theme_color]
        )
        fig_bar.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=0, b=0),
            height=200,
            xaxis_title="分钟 (Minutes)",
            yaxis_title="",
            font=dict(family="-apple-system, sans-serif", color="#86868B")
        )
        st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})
    else:
        st.info("当前时间范围内暂无学习记录。")
    st.markdown("</div>", unsafe_allow_html=True)

    # 3. GitHub 风格学习热力图 (Heatmap)
    st.markdown("<div class='apple-card'>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: #1D1D1F; margin-bottom: 10px;'>🔥 学习热力图 (近一年)</h4>", unsafe_allow_html=True)
    
    # 生成过去365天的完整日期框架
    end_date = datetime.now().date()
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

    # 计算周数和星期几用于坐标轴
    heatmap_df['week'] = heatmap_df['date'].dt.isocalendar().week
    heatmap_df['year'] = heatmap_df['date'].dt.isocalendar().year
    heatmap_df['week_id'] = heatmap_df['year'].astype(str) + '-' + heatmap_df['week'].astype(str).str.zfill(2)
    
    unique_weeks = sorted(heatmap_df['week_id'].unique())
    week_mapping = {w: i for i, w in enumerate(unique_weeks)}
    
    heatmap_df['x'] = heatmap_df['week_id'].map(week_mapping)
    heatmap_df['y'] = heatmap_df['date'].dt.weekday # 0=Mon, 6=Sun
    
    fig_heat = go.Figure(data=go.Heatmap(
        z=heatmap_df['duration_minutes'],
        x=heatmap_df['x'],
        y=heatmap_df['y'],
        colorscale=[[0, '#EBEDF0'], [1, theme_color]],
        xgap=4, ygap=4,
        showscale=False,
        hoverinfo='text',
        text=heatmap_df['date_str'] + '<br>专注: ' + heatmap_df['duration_minutes'].astype(str) + ' 分钟'
    ))
    
    fig_heat.update_layout(
        height=180,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=10, b=20, l=30, r=10),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(
            showgrid=False, zeroline=False, 
            tickmode='array', tickvals=[0, 2, 4, 6], 
            ticktext=['一', '三', '五', '日'], 
            autorange='reversed',
            tickfont=dict(color="#86868B")
        )
    )
    st.plotly_chart(fig_heat, use_container_width=True, config={'displayModeBar': False})
    st.markdown("</div>", unsafe_allow_html=True)