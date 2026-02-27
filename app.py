import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, date, timedelta
import os

# ========= 全局配置 =========
THEME_COLOR = "#008080"  # 深青色主题

CSV_PATH = "learning_log.csv"
DEFAULT_SUBJECTS = ["Python", "SQL", "Tableau", "统计学"]

st.set_page_config(page_title="学习时长追踪", layout="wide")


# ========= 工具函数 =========
def init_session_state():
    if "is_running" not in st.session_state:
        st.session_state.is_running = False
    if "start_time" not in st.session_state:
        st.session_state.start_time = None
    if "current_subject" not in st.session_state:
        st.session_state.current_subject = DEFAULT_SUBJECTS[0]
    if "pending_record" not in st.session_state:
        st.session_state.pending_record = None
    if "pomodoro_notifications" not in st.session_state:
        st.session_state.pomodoro_notifications = 0


def load_data():
    if not os.path.exists(CSV_PATH):
        return pd.DataFrame(
            columns=[
                "date",
                "subject",
                "start_time",
                "end_time",
                "duration_min",
                "focus_score",
            ]
        )
    df = pd.read_csv(CSV_PATH)
    if not df.empty:
        # 保证类型正确
        df["date"] = pd.to_datetime(df["date"]).dt.date
        df["duration_min"] = pd.to_numeric(df["duration_min"], errors="coerce").fillna(0)
        df["focus_score"] = pd.to_numeric(df["focus_score"], errors="coerce").fillna(0)
    return df


def append_record(record: dict):
    # record: {date, subject, start_time, end_time, duration_min, focus_score}
    df_new = pd.DataFrame([record])
    header = not os.path.exists(CSV_PATH)
    df_new.to_csv(CSV_PATH, mode="a", index=False, header=header)


def format_time(dt: datetime | None):
    if dt is None:
        return "--:--:--"
    return dt.strftime("%H:%M:%S")


def get_today_range():
    today = date.today()
    start = datetime.combine(today, datetime.min.time())
    end = datetime.combine(today, datetime.max.time())
    return start, end


def get_current_week_range():
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    return monday, sunday


# ========= 页面样式 =========
def inject_css():
    st.markdown(
        f"""
        <style>
        /* 主按钮样式 */
        .stButton>button {{
            background-color: {THEME_COLOR} !important;
            color: white !important;
            border-radius: 999px !important;
            border: none !important;
        }}

        /* metric 标题颜色 */
        [data-testid="stMetricLabel"] > div {{
            color: {THEME_COLOR} !important;
        }}

        /* 去除多余边距，整体更简洁 */
        .block-container {{
            padding-top: 1.5rem;
            padding-bottom: 1.5rem;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ========= 计时 & 番茄钟逻辑 =========
def handle_timer(subject_selected):
    init_session_state()
    now = datetime.now()

    # 处理按钮点击
    col_left, col_mid, col_right = st.columns([2, 2, 1])

    with col_left:
        st.session_state.current_subject = st.selectbox(
            "学科",
            DEFAULT_SUBJECTS,
            index=DEFAULT_SUBJECTS.index(st.session_state.current_subject)
            if st.session_state.current_subject in DEFAULT_SUBJECTS
            else 0,
            key="subject_select",
        )

    with col_mid:
        elapsed_text = "--:--:--"
        if st.session_state.is_running and st.session_state.start_time is not None:
            elapsed = now - st.session_state.start_time
            total_seconds = int(elapsed.total_seconds())
            h = total_seconds // 3600
            m = (total_seconds % 3600) // 60
            s = total_seconds % 60
            elapsed_text = f"{h:02d}:{m:02d}:{s:02d}"
        st.markdown("**本次已学习**")
        st.markdown(f"<h2 style='margin-top:0;'>{elapsed_text}</h2>", unsafe_allow_html=True)

    with col_right:
        if st.session_state.is_running:
            btn = st.button("停止", use_container_width=True)
        else:
            btn = st.button("开始", use_container_width=True)

    # 开始计时
    if btn and not st.session_state.is_running:
        st.session_state.is_running = True
        st.session_state.start_time = now
        st.session_state.pomodoro_notifications = 0
        st.session_state.pending_record = None
        st.experimental_rerun()

    # 停止计时，生成待保存记录
    if btn and st.session_state.is_running:
        if st.session_state.start_time is not None:
            duration_min = max(
                1, int((now - st.session_state.start_time).total_seconds() // 60)
            )
            record = {
                "date": date.today().isoformat(),
                "subject": st.session_state.current_subject,
                "start_time": format_time(st.session_state.start_time),
                "end_time": format_time(now),
                "duration_min": duration_min,
                "focus_score": None,  # 等待用户输入
            }
            st.session_state.pending_record = record

        st.session_state.is_running = False
        st.session_state.start_time = None
        st.experimental_rerun()

    # 番茄钟提醒（仅在计时中）
    if st.session_state.is_running and st.session_state.start_time is not None:
        elapsed_minutes = (now - st.session_state.start_time).total_seconds() / 60
        current_pomodoro = int(elapsed_minutes // 25)
        if current_pomodoro > st.session_state.pomodoro_notifications:
            st.warning("已专注 25 分钟，休息 5 分钟。")
            st.session_state.pomodoro_notifications = current_pomodoro

        # Pomodoro 进度条（25 分钟一轮）
        progress_pct = max(0, min(100, int((elapsed_minutes % 25) / 25 * 100)))
    else:
        elapsed_minutes = 0
        progress_pct = 0

    st.markdown("**当前番茄进度（25 分钟）**")
    st.markdown(
        f"""
        <div style="width:100%;height:10px;background-color:#e0e0e0;border-radius:999px;overflow:hidden;">
            <div style="height:100%;width:{progress_pct}%;background-color:{THEME_COLOR};"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 倒计时自动刷新（用于更新时间和番茄进度）
    if st.session_state.is_running:
        st.experimental_rerun()


# ========= 评分 & 保存区域 =========
def rating_and_save_ui():
    if st.session_state.pending_record is None:
        return

    st.markdown("---")
    st.markdown("**本次学习记录**")

    rec = st.session_state.pending_record
    cols = st.columns(4)
    with cols[0]:
        st.write(f"日期：{rec['date']}")
    with cols[1]:
        st.write(f"学科：{rec['subject']}")
    with cols[2]:
        st.write(f"开始：{rec['start_time']}")
    with cols[3]:
        st.write(f"结束：{rec['end_time']}（共 {rec['duration_min']} 分钟）")

    focus = st.slider("专注度（1-5）", min_value=1, max_value=5, value=4, step=1)
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("保存本次记录"):
            rec_to_save = rec.copy()
            rec_to_save["focus_score"] = focus
            append_record(rec_to_save)
            st.session_state.pending_record = None
            st.success("已保存。")
            st.experimental_rerun()
    with col2:
        st.caption("（若不想保存，可刷新页面清空该记录。）")


# ========= 可视化看板 =========
def dashboard(df: pd.DataFrame):
    st.markdown("---")
    st.markdown("## 学习统计看板")

    if df.empty:
        st.info("暂无数据，先开始一次学习吧。")
        return

    # 统一日期类型
    df["date"] = pd.to_datetime(df["date"]).dt.date

    # ---- 指标卡 ----
    today = date.today()
    monday, sunday = get_current_week_range()

    today_total = df[df["date"] == today]["duration_min"].sum()
    week_df = df[(df["date"] >= monday) & (df["date"] <= sunday)]
    week_max_focus = week_df["focus_score"].max() if not week_df.empty else 0

    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            label="今日累计时长（分钟）",
            value=int(today_total),
        )
    with col2:
        st.metric(
            label="本周最高专注度（1-5）",
            value=int(week_max_focus) if pd.notna(week_max_focus) else 0,
        )

    # ---- 柱状图：按天总时长 ----
    st.markdown("### 按天学习时长")
    df_daily = (
        df.groupby("date", as_index=False)["duration_min"].sum().sort_values("date")
    )
    chart_daily = (
        alt.Chart(df_daily)
        .mark_bar(color=THEME_COLOR)
        .encode(
            x=alt.X("date:T", title="日期"),
            y=alt.Y("duration_min:Q", title="总时长（分钟）"),
            tooltip=["date:T", "duration_min:Q"],
        )
        .properties(height=250)
    )
    st.altair_chart(chart_daily, use_container_width=True)

    # ---- 饼图：学科占比 ----
    st.markdown("### 各学科学习时长占比")
    df_subject = (
        df.groupby("subject", as_index=False)["duration_min"].sum().sort_values(
            "duration_min", ascending=False
        )
    )
    if not df_subject.empty:
        chart_pie = (
            alt.Chart(df_subject)
            .mark_arc()
            .encode(
                theta=alt.Theta("duration_min:Q", title="总时长"),
                color=alt.Color("subject:N", title="学科"),
                tooltip=["subject:N", "duration_min:Q"],
            )
            .properties(height=250)
        )
        st.altair_chart(chart_pie, use_container_width=True)
    else:
        st.write("暂无数据。")

    # ---- 热力图：近一年 GitHub 风格 ----
    st.markdown("### 过去一年的学习热力图")

    df_heat = df.copy()
    df_heat["date"] = pd.to_datetime(df_heat["date"])
    one_year_ago = pd.to_datetime(today) - timedelta(days=365)
    df_heat = df_heat[df_heat["date"] >= one_year_ago]

    if df_heat.empty:
        st.write("近一年暂无数据。")
        return

    # 以天聚合
    df_heat = (
        df_heat.groupby("date", as_index=False)["duration_min"].sum().rename(
            columns={"duration_min": "total_min"}
        )
    )

    # Altair GitHub 风格：x=week(date), y=day(date)
    chart_heat = (
        alt.Chart(df_heat)
        .mark_rect()
        .encode(
            x=alt.X("yearweek(date):O", title="周"),
            y=alt.Y("day(date):O", title="星期"),
            color=alt.Color(
                "total_min:Q",
                title="分钟数",
                scale=alt.Scale(scheme="teals", domain=[0, df_heat["total_min"].max()]),
            ),
            tooltip=[
                alt.Tooltip("date:T", title="日期"),
                alt.Tooltip("total_min:Q", title="时长（分钟）"),
            ],
        )
        .properties(height=150)
    )
    st.altair_chart(chart_heat, use_container_width=True)


# ========= 主函数 =========
def main():
    inject_css()
    init_session_state()

    st.markdown(
        f"<h2 style='color:{THEME_COLOR};margin-bottom:0.5rem;'>学习时长追踪</h2>",
        unsafe_allow_html=True,
    )

    df = load_data()

    # 顶部：计时器区
    handle_timer(st.session_state.current_subject)

    # 中间：评分 + 保存
    rating_and_save_ui()

    # 底部：统计看板
    dashboard(df)


if __name__ == "__main__":
    main()