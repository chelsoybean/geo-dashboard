import streamlit as st
import pandas as pd


from script import *
import plotly.express as px

def render():
    st.title("GENERAL DASHBOARD")


    # CSS REVISI
    st.markdown("""
    <style>
    .metric-container {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
    }
    .metric-box {
        width: 100%;
        padding: 20px 10px;
        border-radius: 14px;
        background-color: #1f2937;
        color: white;
        text-align: center;
        min-height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        overflow: hidden;
        box-sizing: border-box;
    }


    .metric-revenue { background-color: #064e3b; }
    .metric-profit { background-color: #312e81; }


    .metric-title {
        font-size: 14px;
        opacity: 0.9;
        margin-bottom: 8px;
        font-weight: 500;
    }


    .metric-value {
        font-size: 1.2rem;
        font-weight: 700;
        white-space: nowrap;
        word-wrap: break-word;
    }


    @media (max-width: 768px) {
        .metric-value { font-size: 1rem; }
    }
    </style>
    """, unsafe_allow_html=True)
   
    # READ DATA FROM GOOGLE SHEETS
    tailor_sheets_id = "1f1_CVH5W8EuV_HGpJRPuR3rDQhUjXM_B"
    tailor_df = read_sheets(tailor_sheets_id, "penjahit")


    project_sheets_id = "18saFv1Kb5waaRbM6qOuufAicjh8MoynG2aVi24tHLjw"
    project_df = read_sheets(project_sheets_id, "table_append")


    # CLEAN DATA
    tailor_df["Kode Penjahit"] = tailor_df["Kode Penjahit"].astype(str).str.strip()

    # --- [TAMBAHKAN INI] ---
    # Hapus data ganda berdasarkan Kode Penjahit agar hitungannya pas
    tailor_df = tailor_df.drop_duplicates(subset=["Kode Penjahit"]) 
    # -----------------------

    # FILTER PENJAHIT AKTIF
    active_tailor_df = tailor_df[tailor_df["Kode Penjahit"] != "Non Aktif"]


    # === CLEAN & PREPARE PROJECT DATA ===
    tanggal_col = "Tanggal Pemesanan"
    project_df[tanggal_col] = pd.to_datetime(project_df[tanggal_col])
    project_df["Tahun"] = project_df[tanggal_col].dt.year
    project_df["Bulan"] = project_df[tanggal_col].dt.strftime('%b')


    # FILTER PENJAHIT AKTIF
    active_tailor_df = tailor_df[tailor_df["Kode Penjahit"] != "Non Aktif"]
    total_penjahit_aktif = active_tailor_df["Kode Penjahit"].nunique()

    #CONVERT TYPE
    num_cols = [
    'Qty', 'Harga', 'Jumlah', 'Total jual',
    'RAB', 'Realisasi', 'Profit',
    'Gap', 'Margin', 'Markup'
    ]

    project_df = clean_numeric(project_df, num_cols)

    project_df['Tanggal Pemesanan'] = pd.to_datetime(project_df['Tanggal Pemesanan'], errors='coerce')
    project_df['year'] = project_df['Tanggal Pemesanan'].dt.year
    project_df['month'] = project_df['Tanggal Pemesanan'].dt.month
    project_df['month_name'] = project_df['Tanggal Pemesanan'].dt.strftime('%b')


    #FILTERS
    years = sorted(project_df['year'].dropna().unique())
    year_options = ["ALL"] + years

    col_filter = st.columns([2,6], gap="large")
    with col_filter[0]:
        selected_year = st.selectbox(
            "Year",
            year_options,
            index=0,
        )

        if selected_year == "ALL":
            filtered_df = project_df.copy()
        else:
            filtered_df = project_df[project_df['year'] == selected_year]

    with col_filter[1]:
        month_map = (
        filtered_df[['month', 'month_name']]
        .drop_duplicates()
        .sort_values('month')
        )

        selected_months = st.pills(
            "Month",
            options=month_map['month_name'],
            default=month_map['month_name'],
            selection_mode="multi"
        )

        filtered_df = filtered_df[
            filtered_df['month_name'].isin(selected_months)
        ]

    # --- LAYOUT ATAS (METRICS + SLICER) ---
    top_left, top_right = st.columns([3, 1], gap="medium")

    # --- HITUNG METRIK BERDASARKAN FILTER ---
    if "Jumlah" in filtered_df.columns:
        total_revenue = filtered_df["Jumlah"].sum()
        total_profit = filtered_df["Profit"].sum()
    else:
        total_revenue = 0
        total_profit = 0


    # SUMMARY METRICS
    col1, col2, col3 = st.columns(3, gap="small")


    with col1:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-title">Total Penjahit Aktif</div>
            <div class="metric-value">{total_penjahit_aktif}</div>
        </div>
        """, unsafe_allow_html=True)


    with col2:
        st.markdown(f"""
        <div class="metric-box metric-revenue">
            <div class="metric-title">Total Revenue</div>
            <div class="metric-value">Rp {total_revenue:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)


    with col3:
        st.markdown(f"""
        <div class="metric-box metric-profit">
            <div class="metric-title">Total Profit</div>
            <div class="metric-value">Rp {total_profit:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)


    st.markdown("---")
   
    # --- LAYOUT CHART GRID (2 Baris x 2 Kolom) ---
    chart_row1_col1, chart_row1_col2 = st.columns(2)
    chart_row2_col1, chart_row2_col2 = st.columns(2)


    # CHART 1: LINE CHART (Project per Bulan)
    with chart_row1_col1:
        st.subheader("Tren Total Quantity Project")
        line_data = filtered_df.groupby("Bulan").size().reset_index(name="Jumlah")


        months_order = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        line_data["Bulan"] = pd.Categorical(line_data["Bulan"], categories=months_order, ordered=True)
        line_data = line_data.sort_values("Bulan")


        st.line_chart(line_data.set_index("Bulan"))


    # CHART 2: Area Chart Revenue Bulanan (dari data real)
    with chart_row1_col2:
        st.subheader("Tren Revenue (Monthly)")
        rev_data = filtered_df.groupby("Bulan")["Jumlah"].sum().reset_index()
        rev_data["Bulan"] = pd.Categorical(rev_data["Bulan"], categories=months_order, ordered=True)
        rev_data = rev_data.sort_values("Bulan")
        st.area_chart(rev_data.set_index("Bulan"), color="#064e3b")


    # CHART 3: Distribusi Kategori Project (FIXED SORTING)
    with chart_row2_col1:
        st.subheader("Project Category Distribution")
        if "Kategori" in filtered_df.columns:
            # Hitung jumlah
            cat_counts = filtered_df["Kategori"].value_counts().reset_index()
            cat_counts.columns = ["Category", "Qty"] # Rename kolom
            
            # Buat Chart dengan Plotly
            fig_cat = px.bar(cat_counts, x="Category", y="Qty", 
                             text="Qty") # Menampilkan angkanya
            
            # KUNCI AGAR URUT: categoryorder='total descending' (Terbanyak di kiri)
            fig_cat.update_layout(
                xaxis={'categoryorder':'total descending'}, 
                height=400
            )
            st.plotly_chart(fig_cat, use_container_width=True)

        else:
            st.write("Kolom 'Kategori' tidak ditemukan.")


    # CHART 4: Top 10 Instansi (FIXED SORTING)
    with chart_row2_col2:
        st.subheader("Top 10 Instansi")
        if "Instansi" in filtered_df.columns:
            # Hitung Top 10
            inst_counts = filtered_df["Instansi"].value_counts().head(10).reset_index()
            inst_counts.columns = ["Instansi", "Qty"]
            
            # Buat Chart
            fig_inst = px.bar(inst_counts, x="Instansi", y="Qty", text="Qty") 
            
            # KUNCI AGAR URUT
            fig_inst.update_layout(
                xaxis={'categoryorder':'total descending'}, 
                height=400
            )
            st.plotly_chart(fig_inst, use_container_width=True)

        else:
            st.write("Kolom 'Instansi' tidak ditemukan.")