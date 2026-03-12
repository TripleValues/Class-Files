import streamlit as st
import pandas as pd
import mariadb
from db import getConn
import plotly.express as px


st.set_page_config(
	page_title="장거리노선 종합 분석",
	page_icon="🛫",
	layout="wide",
)

st.title("🛫장거리노선 '종합' 분석")

st.markdown("---")

def get_data():
  conn = getConn()
  try:
    sql = f"""
      select 
        `년도`, 
        count(*) as `노선수`, -- 해당 년도의 장거리 노선이 몇 개인지
        round(avg(`평균도착지연시간`), 1) as `평균지연시간`, -- 노선들의 평균을 다시 평균 내기
        round(max(`평균도착지연시간`), 1) as `최대지연시간`,
        max(`비행거리`) as `최대비행거리` -- 그해 가장 멀리 간 거리
      from db_air.`장거리노선`
      group by `년도` -- 년도별로 그룹 묶기
      order by `년도` asc
      ;
    """
    df = pd.read_sql(sql, conn)
    return df
  except mariadb.Error as e:
    print(f"get_data Error : {e}")

data = get_data()
years = sorted(data['년도'].unique())

st.subheader("📌 핵심 통계 요약")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("총 데이터 연수", f"{len(data)}년")
with col2:
    st.metric("최대 비행거리", f"{data['최대비행거리'].max()}마일")
with col3:
    st.metric("전체 평균 지연시간", f"{round(data['평균지연시간'].mean(), 1)}분")
with col4:
    st.metric("최대 지연 기록", f"{data['최대지연시간'].max()}분")

st.markdown("---")

st.subheader("📌 연별 통계 요약")
selected_year = st.selectbox(
    "년도선택",
    years,
    index=None,
    placeholder="년도를 선택하세요"
)
year_data = data[data['년도'] == selected_year]
col5, col6, col7, col8 = st.columns(4)
if selected_year:
  with col5:
      st.metric("기준", f"{selected_year}년")
  with col6:
      st.metric("최대 비행거리", f"{year_data['최대비행거리'].max()}마일")
  with col7:
      st.metric("전체 평균 지연시간", f"{round(year_data['평균지연시간'].mean(), 1)}분")
  with col8:
      st.metric("최대 지연 기록", f"{year_data['최대지연시간'].max()}분")

st.markdown("---")

c1, c2 = st.columns([6, 4])

with c1:
  st.subheader("⏰ 연도별 평균 및 최대 지연시간")
  line = px.line(
    data,
    x="년도",
    y=["평균지연시간", "최대지연시간"], 
    markers=True,
    template="plotly_white",
    color_discrete_sequence=["#FF4B4B", "#31333F"]
  )
  line.update_layout(
    hovermode="x unified", 
    yaxis_title="지연시간",
    legend=dict(
      orientation="h", 
      yanchor="bottom", 
      y=1.02, 
      xanchor="right", 
      x=1
    )
  )
  st.plotly_chart(line, use_container_width=True)

with c2:
  st.subheader("📊 연도별 장거리 노선 수")
  bar = px.bar(
    data, 
    x="년도", 
    y="노선수", 
    text_auto=True,
    color="최대비행거리", 
    color_continuous_scale="Magma",
    template="plotly_white"
  )
  bar.update_layout(showlegend=False)
  st.plotly_chart(bar, use_container_width=True)