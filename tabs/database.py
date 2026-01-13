import streamlit as st
import pandas as pd

from script import *

def render():
    st.title("Database Master All Tables")
    # st.write("Ini isi perhitungan stock")

    #READ DATA FROM GOOGLE SHEETS
    tailor_sheets_id = "1f1_CVH5W8EuV_HGpJRPuR3rDQhUjXM_B"
    tailor_df = read_sheets(tailor_sheets_id, "penjahit")

    project_sheets_id = "18saFv1Kb5waaRbM6qOuufAicjh8MoynG2aVi24tHLjw"
    project_df = read_sheets(project_sheets_id, "table_append")

    supplier_sheets_id = "1_S-7u20Mzoz4df-G-Wcg04xPChhQFUqWEeEesEXhLzQ"
    supplier_df = read_sheets(supplier_sheets_id, "supplier_clean")

    #MAKE DATAFRAMES FOR DATABASE TABLES
    # 1. Projects
    projects = pd.DataFrame({
        'project_id': pd.Series(dtype='int'),        # PK int auto increment
        'instansi': pd.Series(dtype='str'),          # char
        'item_project': pd.Series(dtype='str'),      # char
        'order_date': pd.Series(dtype='datetime64[ns]'),  # date
        'category': pd.Series(dtype='str'),          # varchar
        'qty': pd.Series(dtype='int'),                # int
        'price': pd.Series(dtype='int'),              # int
        'deadline': pd.Series(dtype='datetime64[ns]'),# datetime
        'status': pd.Series(dtype='str'),             # enum: planned/on going/done (string)
    })

    # 2. Projects_finance
    projects_finance = pd.DataFrame({
        'finance_id': pd.Series(dtype='int'),        # PK int auto increment
        'project_id': pd.Series(dtype='int'),        # FK ke projects
        'RAB': pd.Series(dtype='int'),                # int
        'realisasi': pd.Series(dtype='int'),          # int
        'revenue': pd.Series(dtype='int'),            # int
        'profit': pd.Series(dtype='int'),             # int
    })

    # 3. worker_assignments
    worker_assignments = pd.DataFrame({
        'assignment_id': pd.Series(dtype='int'),        # PK int auto increment
        'project_id': pd.Series(dtype='int'),            # FK ke projects
        'tailor_id': pd.Series(dtype='int'),             # FK ke tailors (anggap int)
        'qty_assigned': pd.Series(dtype='int'),          # int
        'assign_date': pd.Series(dtype='datetime64[ns]'),# date
        'due_date': pd.Series(dtype='datetime64[ns]'),   # date
        'status': pd.Series(dtype='str'),                 # enum: ongoing / done / overdue
        'completion_date': pd.Series(dtype='datetime64[ns]'),  # date
        'created_at': pd.Series(dtype='datetime64[ns]'),        # timestamp
    })

    # 4. qc_logs
    qc_logs = pd.DataFrame({
        'qc_id': pd.Series(dtype='int'),                 # PK int auto increment
        'assignment_id': pd.Series(dtype='int'),         # FK ke assignment
        'qc_round': pd.Series(dtype='int'),               # int
        'qty_checked': pd.Series(dtype='int'),            # int
        'qty_accepted': pd.Series(dtype='int'),           # int
        'qty_returned': pd.Series(dtype='int'),           # int
        'qc_date': pd.Series(dtype='datetime64[ns]'),    # date
        'notes': pd.Series(dtype='str'),                  # text
    })

    st.subheader("Projects Table")
    st.dataframe(projects)

    st.subheader("Projects Finance Table")
    st.dataframe(projects_finance)

    st.subheader("Worker Assignments Table")
    st.dataframe(worker_assignments)

    st.subheader("QC Logs Table")
    st.dataframe(qc_logs)

    st.subheader("Tailors Data")
    st.dataframe(tailor_df)

    st.subheader("Recap Projects History")
    st.dataframe(project_df)

    st.subheader("Suppliers Data")
    st.dataframe(supplier_df)

