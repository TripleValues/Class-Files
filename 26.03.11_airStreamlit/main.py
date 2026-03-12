import streamlit as st
import pandas as pd
from vega_datasets import data
from numpy.random import default_rng as rng
import altair as alt

st.set_page_config(
    page_title="수집 프로젝트",
    page_icon="🚁",
    layout="wide",
    # initial_sidebar_state="collapsed"
)

st.title("가즈아아아")