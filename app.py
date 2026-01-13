import streamlit as st
import pandas as pd

from script import *
from tabs import dashboard, database, tailors, project

# st.title("Hello Streamlit")
# st.write("Ini app Streamlit pertamaku.")

# LAYOUT SETTINGS
st.set_page_config(
    # Title and icon for the browser's tab bar:
    page_title="KSMB webapp",
    page_icon=":bar_chart:",
    # Make the content take up the width of the page:
    layout="wide",
    )

#STREAMLIT APP
st.sidebar.title("Menu")
tab = st.sidebar.radio(" ", [
    "General Dashboard",
    "Project",
    "Tailors",
    "Database"
])

if tab == "General Dashboard":
    dashboard.render()
elif tab == "Project":
    project.render()
elif tab == "Tailors":
    tailors.render()
elif tab == "Database":
    database.render()
