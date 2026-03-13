import streamlit as st
import pandas as pd
import mariadb
from db import getConn
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# ── 페이지 기본 설정 ───────────────────────────────────────────────────────────
st.set_page_config(
	page_title="장거리노선 종합 분석",
	page_icon="🛫",
	layout="wide",
)

# ── 공통 스타일 ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-title   { font-size: 2rem; font-weight: 800; color: #1a3c6e; }
    .section-title{ font-size: 1.25rem; font-weight: 700; color: #2c5f9e;
                    border-left: 5px solid #2c5f9e; padding-left: 10px; margin-top: 1rem; }
    .desc-box     { background: #8ad4ff; border-radius: 10px; padding: 14px 18px;
                    font-size: 0.92rem; color: #333; line-height: 1.7; margin-bottom: 8px; }
</style>
""", unsafe_allow_html=True)

# ── 데이터 불러오기 ───────────────────────────────────────────────────────────

# 장거리노선 데이터
def get_data1():
  conn = getConn()
  try:
    sql = """
        SELECT
            CONCAT(`출발지`, '→', `도착지`) AS `운항노선`,
            `출발지`, `도착지`,
            `년도`,
            `평균도착지연시간`,
            CAST(`비행거리` AS SIGNED) AS `비행거리`
        FROM db_air.`장거리노선`
        ORDER BY `년도` ASC, `비행거리` DESC
    """
    df = pd.read_sql(sql, conn)
    return df
  except mariadb.Error as e:
    print(f"get_data Error : {e}")

# 년도별요약 데이터
def get_data2():
  conn = getConn()
  try:
    sql = """
        SELECT
            `년도`,
            COUNT(*) AS `노선수`,
            ROUND(AVG(`평균도착지연시간`), 1) AS `평균지연시간`,
            ROUND(MAX(`평균도착지연시간`), 1) AS `최대지연시간`,
            MAX(CAST(`비행거리` AS SIGNED)) AS `최대비행거리`
        FROM db_air.`장거리노선`
        GROUP BY `년도`
        ORDER BY `년도` ASC
    """
    df = pd.read_sql(sql, conn)
    return df
  except mariadb.Error as e:
    print(f"get_data Error : {e}")

# 장거리Top10
def get_data3():
  conn = getConn()
  try:
    sql = "select * from 장거리TOP10"
    df = pd.read_sql(sql, conn)
    return df
  except mariadb.Error as e:
    print(f"get_data Error : {e}")

data1 = get_data1()
data2 = get_data2()
data3 = get_data3()

# ── 타이틀 ───────────────────────────────────────────────────────────
# st.title("장거리노선 '종합' 분석")
st.markdown(
    '<p class="main-title">✈️ 장거리 항공 노선 분석 (1987–1989)</p>',
    unsafe_allow_html=True,
)
st.markdown(
    "항공 데이터를 기반으로 **비행거리 2,500마일 초과 장거리 노선**의 "
    "운항 현황과 지연 패턴 분석."
)
st.divider()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SECTION A — 장거리노선 전체 분석
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown(
    '<p class="section-title">📌 SECTION A — 장거리노선 전체 분석</p>',
    unsafe_allow_html=True,
)

# ── 카드 ───────────────────────────────────────────────────────────────────
# st.subheader("📌 핵심 통계 요약")
col1, col2, col3, col4 = st.columns(4)
with col1:
  st.metric("장거리 노선 수", f"{int(data1["운항노선"].nunique())}개")
with col2:
  st.metric("전체 평균 지연시간", f"{round(data1["평균도착지연시간"].mean(), 1)}분")
with col3:
  st.metric("최대 비행거리", f"{data1["비행거리"].max()}마일")
with col4:
  st.metric("분석 연도 수", f"{len(data2)}년")
st.divider()

# ── Chart 1 : 년도별 노선 수 & 평균 지연시간 ─────────────────────
st.markdown("#### 📈 Chart 1 : 년도별 장거리 노선 운항 현황")
st.markdown(
    '<div class="desc-box">📝 <b>분석 포인트</b><br>'
    "1987년부터 1989년까지 장거리 노선의 수와 "
    "평균 도착지연시간을 연도별로 비교.<br>"
    "<b>노선 수의 증감</b>은 항공사의 장거리 노선 확장 또는 축소 전략을 반영하며, "
    "<b>지연시간의 변화</b>는 운항 효율성의 개선 여부를 보여준다 할 수 있음.</div>",
    unsafe_allow_html=True,
)

fig_a1 = make_subplots(specs=[[{"secondary_y": True}]])
fig_a1.add_trace(
    go.Bar(
        x=data2["년도"].astype(str),
        y=data2["노선수"],
        name="노선 수",
        marker_color="#4A90D9",
        opacity=0.8,
    ),
    secondary_y=False,
)
fig_a1.add_trace(
    go.Scatter(
        x=data2["년도"].astype(str),
        y=data2["평균지연시간"],
        name="평균 지연시간 (분)",
        mode="lines+markers+text",
        marker=dict(size=10, color="#E85D5D"),
        line=dict(width=3, color="#E85D5D"),
        text=data2["평균지연시간"],
        textposition="top center",
    ),
    secondary_y=True,
)
fig_a1.update_layout(
    title="년도별 장거리 노선 수 및 평균 도착지연시간",
    xaxis_title="년도",
    height=420,
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
)
fig_a1.update_yaxes(title_text="노선 수 (개)", secondary_y=False)
fig_a1.update_yaxes(title_text="평균 지연시간 (분)", secondary_y=True)
st.plotly_chart(fig_a1, use_container_width=True)


# ── Chart 2 : 비행거리 vs 지연시간 산점도 ───────────────────────────────────
st.markdown("#### 🔵 Chart 2 : 비행거리 vs 도착지연시간 상관관계")
st.markdown(
    '<div class="desc-box">📝 <b>분석 포인트</b><br>'
    "비행거리와 평균 도착지연시간 사이의 상관관계를 산점도로 표현.<br>"
    "<b>점의 색상</b>은 연도를 구분하며, 거리가 길수록 지연시간이 늘어나는 경향이 있는지 확인할 수 있음.<br>"
    "<b>점의 분포</b>에 따라 특정 연도에 유독 지연이 심한 노선이 존재하는지도 파악할 수 있음.</div>",
    unsafe_allow_html=True,
)

data1_sc = data1.copy()
data1_sc["년도_str"] = data1_sc["년도"].astype(str)
fig_a2 = px.scatter(
    data1_sc,
    x="비행거리",
    y="평균도착지연시간",
    color="년도_str",
    hover_data=["운항노선"],
    labels={
        "비행거리": "비행거리 (마일)",
        "평균도착지연시간": "평균 지연시간 (분)",
        "년도_str": "년도",
    },
    title="비행거리 vs 평균 도착지연시간",
    color_discrete_sequence=px.colors.qualitative.Set1,
)
fig_a2.update_layout(height=450)
st.plotly_chart(fig_a2, use_container_width=True)
st.divider()


# ── Chart 3 : 년도별 지연시간 박스플롯 ─────────────────────────────────────
st.markdown("#### 📦 Chart 3 : 년도별 지연시간 분포")
st.markdown(
    '<div class="desc-box">📝 <b>분석 포인트</b><br>'
    "년도별 평균 도착지연시간의 분포를 박스플롯으로 나타냄.<br>"
    "연도가 지남에 따라 지연시간의 분산이 줄어들면 운항 안정성이 향상되고 있음을 의미.</div>",
    unsafe_allow_html=True,
)

data1_box = data1.copy()
data1_box["년도_str"] = data1_box["년도"].astype(str)
fig_a4 = px.box(
    data1_box,
    x="년도_str",
    y="평균도착지연시간",
    color="년도_str",
    points="all",
    labels={"년도_str": "년도", "평균도착지연시간": "평균 지연시간 (분)"},
    title="년도별 도착지연시간 분포",
    color_discrete_sequence=px.colors.qualitative.Set2,
)
fig_a4.update_layout(height=430, showlegend=False)
st.plotly_chart(fig_a4, use_container_width=True)
st.divider()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SECTION B — 장거리 TOP10 분석
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown(
    '<p class="section-title">📌 SECTION B — 장거리 TOP10 노선 분석</p>',
    unsafe_allow_html=True,
)
st.divider()

# ── Chart 4 : 년도별 TOP10 노선 비행거리 ────────────────────────
st.markdown("#### 🏆 Chart 4 : 년도별 장거리 TOP10 노선 비교")
st.markdown(
    '<div class="desc-box">📝 <b>분석 포인트</b><br>'
    "각 연도의 비행거리 상위 10개 노선을 막대 그래프로 비교.<br>"
    "매년 TOP10에 진입하는 노선이 동일한지, 혹은 새로운 초장거리 노선이 등장하는지를 확인할 수 있음.<br>"
    "색상으로 연도를 구분하여 동일 노선의 연도간 비행거리 변화도 파악 가능.</div>",
    unsafe_allow_html=True,
)

year_selected = st.multiselect(
  "연도 선택",
  options=sorted(data3["년도"].unique()),
  default=sorted(data3["년도"].unique()),
  key="b1_year",
)
df_b1 = data3[data3["년도"].isin(year_selected)].copy()
df_b1["년도_str"] = df_b1["년도"].astype(str)  # ✅ 이산 색상 처리
if not df_b1.empty:
    fig_b1 = px.bar(
        df_b1,
        x="운항노선",
        y="비행거리",
        color="년도_str",
        barmode="group",
        text="비행거리",
        labels={"비행거리": "비행거리 (마일)", "운항노선": "운항 노선", "년도_str": "년도"},
        title="년도별 TOP10 장거리 노선 비행거리",
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    fig_b1.update_traces(textposition="outside", texttemplate="%{text:,}")
    fig_b1.update_layout(height=500, xaxis_tickangle=-35)
    st.plotly_chart(fig_b1, use_container_width=True)
else:
    st.info("선택된 연도 데이터가 없습니다.")
st.divider()

# ── Chart 5 : TOP10 버블차트 (거리 vs 지연, 버블=노선 등장 횟수) ─────────
st.markdown("#### 💫 Chart 5 : 장거리 TOP10 노선 비행거리 vs 지연시간 버블차트")
st.markdown(
    '<div class="desc-box">📝 <b>분석 포인트</b><br>'
    "버블의 X축은 비행거리, Y축은 평균 지연시간, 버블 크기는 해당 노선이 3년간 TOP10에 등장한 횟수를 의미.<br>"
    "자주 TOP10에 등장하는 노선일수록 버블이 크며, 거리 대비 지연이 심한 노선을 한눈에 파악 가능.<br>"
    '오른쪽 상단에 위치한 노선은 장거리이면서 지연도 심한 "관리 필요 노선"으로 볼 수 있음.</div>',
    unsafe_allow_html=True,
)

bubble_df = (
data3.groupby("운항노선")
.agg(
    비행거리=("비행거리", "mean"),
    평균지연=("평균도착지연시간", "mean"),
    등장횟수=("년도", "count"),
)
.reset_index()
.round(1)
)
fig_b2 = px.scatter(
bubble_df,
x="비행거리",
y="평균지연",
size="등장횟수",
color="평균지연",
hover_name="운항노선",
text="운항노선",
color_continuous_scale="RdYlGn_r",
size_max=50,
labels={
    "비행거리": "평균 비행거리 (마일)",
    "평균지연": "평균 지연시간 (분)",
    "등장횟수": "TOP10 등장 횟수",
},
title="TOP10 노선 비행거리 vs 지연시간 버블차트",
)
fig_b2.update_traces(textposition="top center", textfont_size=9)
fig_b2.update_layout(height=500, coloraxis_showscale=True)
st.plotly_chart(fig_b2, use_container_width=True)
st.divider()


# ── 데이터 테이블 (접기/펼치기) ───────────────────────────────────────────────
with st.expander("📋 원본 데이터 테이블 보기"):
    tab1, tab2, tab3 = st.tabs(["장거리노선 전체", "장거리 TOP10", "년도별 요약"])
    with tab1:
        if not data1.empty:
            st.dataframe(data1, use_container_width=True)
        else:
            st.info("데이터 없음")
    with tab2:
        if not data3.empty:
            st.dataframe(data3, use_container_width=True)
        else:
            st.info("데이터 없음")
    with tab3:
        if not data2.empty:
            st.dataframe(data2, use_container_width=True)
        else:
            st.info("데이터 없음")