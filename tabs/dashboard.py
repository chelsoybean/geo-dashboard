import streamlit as st
import pandas as pd

from script import *

def render():
    st.title("Dashboard")
    st.write("Ini isi dashboard umum")

#READ DATA FROM GOOGLE SHEETS
tailor_sheets_id = "1f1_CVH5W8EuV_HGpJRPuR3rDQhUjXM_B"
tailor_df = read_sheets(tailor_sheets_id, "penjahit")