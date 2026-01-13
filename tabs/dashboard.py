import streamlit as st
import pandas as pd


from script import *


def render():
    st.title("Dashboard")


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


    # === CLEAN & PREPARE PROJECT DATA ===
    tanggal_col = "Tanggal Pemesanan"
    project_df[tanggal_col] = pd.to_datetime(project_df[tanggal_col])
    project_df["Tahun"] = project_df[tanggal_col].dt.year
    project_df["Bulan"] = project_df[tanggal_col].dt.strftime('%b')


    # ===== PERBAIKAN UTAMA: KONVERSI KOLOM NUMERIC =====
    def clean_numeric(value):
        """Konversi string ke numeric (hapus Rp, titik, koma)"""
        if pd.isna(value):
            return 0
        if isinstance(value, (int, float)):
            return value
        # Hapus 'Rp', spasi, titik pemisah ribuan
        value = (
        str(value)
        .replace("Rp", "")
        .replace(".", "")
        .replace(",", "")
        .strip()
    )


        return pd.to_numeric(value, errors="coerce") or 0


    # Konversi kolom yang dibutuhkan
    numeric_cols = ["Jumlah", "Profit", "Total jual", "RAB", "Realisasi"]
    for col in numeric_cols:
        if col in project_df.columns:
            project_df[col] = project_df[col].apply(clean_numeric)


    # FILTER PENJAHIT AKTIF
    active_tailor_df = tailor_df[tailor_df["Kode Penjahit"] != "Non Aktif"]
    total_penjahit_aktif = active_tailor_df["Kode Penjahit"].nunique()


    # --- LAYOUT ATAS (METRICS + SLICER) ---
    top_left, top_right = st.columns([3, 1], gap="medium")
   
    with top_right:
        # Filter Tahun
        list_tahun = sorted(project_df["Tahun"].unique())
        pilihan_tahun = st.multiselect("Pilih Tahun", list_tahun, default=list_tahun)
        df_filtered = project_df[project_df["Tahun"].isin(pilihan_tahun)]


    # --- HITUNG METRIK BERDASARKAN FILTER ---
    if "Jumlah" in df_filtered.columns:
        total_revenue = df_filtered["Jumlah"].sum()
        total_profit = df_filtered["Profit"].sum()
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
        st.subheader("Tren Jumlah Project")
        line_data = df_filtered.groupby("Bulan").size().reset_index(name="Jumlah")


        months_order = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        line_data["Bulan"] = pd.Categorical(line_data["Bulan"], categories=months_order, ordered=True)
        line_data = line_data.sort_values("Bulan")


        st.line_chart(line_data.set_index("Bulan"))


    # CHART 2: Area Chart Revenue Bulanan (dari data real)
    with chart_row1_col2:
        st.subheader("Tren Revenue (Bulanan)")
        rev_data = df_filtered.groupby("Bulan")["Jumlah"].sum().reset_index()
        rev_data["Bulan"] = pd.Categorical(rev_data["Bulan"], categories=months_order, ordered=True)
        rev_data = rev_data.sort_values("Bulan")
        st.area_chart(rev_data.set_index("Bulan"), color="#064e3b")


    # CHART 3: Distribusi Kategori Project
    with chart_row2_col1:
        st.subheader("Distribusi Kategori Project")
        if "Kategori" in df_filtered.columns:
            cat_counts = df_filtered["Kategori"].value_counts()
            st.bar_chart(cat_counts)
        else:
            st.write("Kolom 'Kategori' tidak ditemukan.")


    # CHART 4: BAR CHART (Top 10 Instansi)
    with chart_row2_col2:
        st.subheader("Top 10 Instansi")
        if "Instansi" in df_filtered.columns:
            inst_counts = df_filtered["Instansi"].value_counts().head(10)
            st.bar_chart(inst_counts, color="#312e81")
        else:
            st.write("Kolom 'Instansi' tidak ditemukan.")

