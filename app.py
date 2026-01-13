import streamlit as st
import pandas as pd

from script import *
from tabs import dashboard, tailors, stock, project

# st.title("Hello Streamlit")
# st.write("Ini app Streamlit pertamaku.")

#STREAMLIT APP
st.sidebar.title("Menu")
tab = st.sidebar.radio(" ", [
    "Dashboard Umum",
    "Data Penjahit",
    "Perhitungan Stock",
    "Perhitungan Project"
])

if tab == "Dashboard Umum":
    dashboard.render()
elif tab == "Data Penjahit":
    tailors.render()
elif tab == "Perhitungan Stock":
    stock.render()
elif tab == "Perhitungan Project":
    project.render()