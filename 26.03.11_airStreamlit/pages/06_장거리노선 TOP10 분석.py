import streamlit as st
import pandas as pd
import mariadb
from db import getConn
import matplotlib.pyplot as plt
import plotly.express as px


st.set_page_config(
	page_title="장거리노선 'TOP 10' 분석",
	page_icon="🛫",
	layout="wide",
)
st.title("🛫장거리노선 'TOP 10' 분석")
st.markdown("---")


def get_data():
  conn = getConn()
  try:
    sql = "select * from 장거리TOP10"
    df = pd.read_sql(sql, conn)
    return df
  except mariadb.Error as e:
    print(f"get_data Error : {e}")

df = get_data()
# st.dataframe(df)
years = sorted(df['년도'].unique())



tab1_1, tab1_2 = st.tabs(["1. 연간 노선별 지연시간 랭킹", "2. 연도별 지연시간 비교"])
with tab1_1:
    st.subheader("📊 노선별 지연시간 랭킹")
    fig = px.bar(
        df, 
        x='평균도착지연시간', 
        y='운항노선', 
        color='평균도착지연시간',
        orientation='h',
        hover_data=['비행거리', '년도'],
        color_continuous_scale='Reds')
    st.plotly_chart(fig, use_container_width=True)
with tab1_2:
    st.subheader("📈 연도별 지연시간 비교")
    fig = px.bar(
        df, 
        x='년도', 
        y='평균도착지연시간', 
        color='운항노선',
        barmode='group',
    )
    st.plotly_chart(fig, use_container_width=True)


st.markdown("---")

selected_year = st.selectbox(
    "년도선택",
    years,
    index=None,
    placeholder="년도를 선택하세요"
)

data = df[df['년도'] == selected_year]
# st.dataframe(data)

tab2_1, tab2_2 = st.tabs(["1. 노선별 평균 지연시간", "2. 비행거리와 지연시간"])

if selected_year:
  with tab2_1:
    st.subheader("📊 노선별 평균 지연시간")
    fig, ax = plt.subplots()
    ax.bar(data["운항노선"], data["평균도착지연시간"], color="#FF4B4B")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    st.pyplot(fig)
  #   st.bar_chart(data, x="운항노선", y="평균도착지연시간", color="#FF4B4B", stack=False)

  with tab2_2:
    st.subheader("🚩 비행거리와 지연시간")
    st.scatter_chart(data, x="비행거리", y="평균도착지연시간", color="#FF4B4B")

st.markdown("---")