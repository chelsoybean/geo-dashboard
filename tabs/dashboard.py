import streamlit as st
import pandas as pd

from script import *

def render():
    st.title("Dashboard")
    st.write("Ini isi dashboard umum")

    #READ DATA FROM GOOGLE SHEETS
    tailor_sheets_id = "1f1_CVH5W8EuV_HGpJRPuR3rDQhUjXM_B"
    tailor_df = read_sheets(tailor_sheets_id, "penjahit")

    project_sheets_id = "18saFv1Kb5waaRbM6qOuufAicjh8MoynG2aVi24tHLjw"
    project_df = read_sheets(project_sheets_id, "table_append")
