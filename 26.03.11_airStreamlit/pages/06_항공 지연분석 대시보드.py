import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt
import pydeck as pdk
from st_aggrid import AgGrid
from db import findAll

# ---------------------------------------------
# 페이지 설정
# ---------------------------------------------

st.set_page_config(
  page_title="항공 지연 분석 대시보드",
  page_icon="✈️",
  layout="wide"
)

# ---------------------------------------------
# 제목 영역
# ---------------------------------------------

st.title("✈️ 항공 지연 분석 대시보드")
st.caption("60분 이상 도착 지연 데이터 분석 플랫폼")

st.divider()

# ---------------------------------------------
# 사이드바 필터
# ---------------------------------------------

st.sidebar.header("🔎 분석 필터")

year_no = ["1987","1988","1989"]
year_opt = ["1987년","1988년","1989년"]

day_no = ["1","2","3","4","5","6","7"]
day_opt = ["월요일","화요일","수요일","목요일","금요일","토요일","일요일"]

selected_year = st.sidebar.selectbox("년도 선택",year_opt)
selected_day = st.sidebar.selectbox("요일 선택",day_opt)

top_n = st.sidebar.selectbox(
    "TOP 공항 수",
    [10,20,50]
)

yearNo = year_no[year_opt.index(selected_year)]
dayNo = day_no[day_opt.index(selected_day)]

# ---------------------------------------------
# 데이터 캐싱 (속도 향상)
# ---------------------------------------------

@st.cache_data
def load_top10(yearNo, dayNo, top_n):
  sql = f"""
      SELECT
        도착지공항,
        SUM(도착지연시간) AS 지연
      FROM db_air.`60분이상_지연비행`
      WHERE 년도={yearNo}
      AND 요일={dayNo}
      GROUP BY 도착지공항
      ORDER BY 지연 DESC
      LIMIT {top_n}
    """
  return pd.DataFrame(findAll(sql))


@st.cache_data
def load_monthly(yearNo):
  sql = f"""
      SELECT
        월,
        SUM(도착지연시간) AS 지연
      FROM db_air.`60분이상_지연비행`
      WHERE 년도={yearNo}
      GROUP BY 월
      ORDER BY 월
    """
  return pd.DataFrame(findAll(sql))


@st.cache_data
def load_weekday(yearNo):
  sql = f"""
      SELECT
        요일,
        SUM(도착지연시간) AS 지연
      FROM db_air.`60분이상_지연비행`
      WHERE 년도={yearNo}
      GROUP BY 요일
      ORDER BY 요일
    """
  return pd.DataFrame(findAll(sql))


@st.cache_data
def load_routes(yearNo):
  sql = f"""
      SELECT
        CONCAT(출발지공항, ' → ', 도착지공항) AS 노선,
        CAST(SUM(도착지연시간) AS SIGNED) AS 지연
      FROM db_air.`60분이상_지연비행`
      WHERE 년도 = {yearNo}
      GROUP BY 노선
      ORDER BY 지연 DESC
      LIMIT 20
    """
  return pd.DataFrame(findAll(sql))

# ---------------------------------------------
# 데이터 로드
# ---------------------------------------------

df_top10 = load_top10(yearNo, dayNo, top_n)
df_month = load_monthly(yearNo)
df_day = load_weekday(yearNo)
df_route = load_routes(yearNo)

# ---------------------------------------------
# 핵심 지표(KPI)
# ---------------------------------------------

st.subheader("📊 주요 지표")

k1,k2,k3,k4 = st.columns(4)

total_delay = df_top10["지연"].sum()
avg_delay = int(df_top10["지연"].mean())
top_airport = df_top10.iloc[0]["도착지공항"]
top_delay = df_top10.iloc[0]["지연"]

k1.metric("총 지연시간",f"{total_delay:,}")
k2.metric("평균 지연시간",f"{avg_delay:,}")
k3.metric("가장 지연이 많은 공항",top_airport)
k4.metric("최대 지연시간",f"{top_delay:,}")

st.divider()

# -------------------------------------------------
# 자동 분석 문장
# -------------------------------------------------

st.subheader("📌 자동 분석 결과")

insight1 = f"{selected_year} {selected_day} 기준 가장 지연이 많은 공항은 **{top_airport}** 입니다."
insight2 = f"TOP {top_n} 공항의 총 지연시간은 **{total_delay:,}** 입니다."
insight3 = f"평균 지연시간은 **{avg_delay:,}** 입니다."

st.info(insight1)
st.info(insight2)
st.info(insight3)

st.divider()

# ---------------------------------------------
# 차트 영역
# ---------------------------------------------

c1,c2 = st.columns(2)

with c1:
  st.subheader(f"🛬 도착 지연 상위 {top_n}개 공항")

  fig = px.bar(
    df_top10,
    x="지연",
    y="도착지공항",
    orientation="h",
    color="지연",
    color_continuous_scale="Reds"
  )

  fig.update_layout(height=450)

  st.plotly_chart(fig,use_container_width=True)


with c2:
  st.subheader("📅 월별 지연 추이")

  fig2 = px.line(
    df_month,
    x="월",
    y="지연",
    markers=True
  )

  fig2.update_layout(height=450)

  st.plotly_chart(fig2,use_container_width=True)

st.divider()

# ---------------------------------------------
# 요일별 지연 분석
# ---------------------------------------------

st.subheader("📊 요일별 지연 패턴")

fig3 = px.bar(
  df_day,
  x="요일",
  y="지연",
  color="지연",
  color_continuous_scale="Blues"
)

st.plotly_chart(fig3,use_container_width=True)

st.divider()

# ---------------------------------------------
# 노선 분석
# ---------------------------------------------

st.subheader("🛫 지연이 많은 노선 분석")

fig4 = px.bar(
  df_route,
  x="지연",
  y="노선",
  orientation="h",
  color="지연"
)

fig4.update_layout(height=600)
st.plotly_chart(fig4,use_container_width=True)
st.divider()

# ---------------------------------------------
# 데이터 테이블
# ---------------------------------------------

st.subheader("📋 상세 데이터")
AgGrid( df_route, fit_columns_on_grid_load=True )
st.divider()

# ---------------------------------------------
# CSV 다운로드
# ---------------------------------------------

csv = df_route.to_csv(index=False).encode("utf-8")

st.download_button(
  label="📥 CSV 다운로드",
  data=csv,
  file_name="delay_routes.csv",
  mime="text/csv"
)

# ---------------------------------------------
# 하단 설명
# ---------------------------------------------

st.caption("항공 지연 분석 대시보드 | 3팀 화이팅!!")
