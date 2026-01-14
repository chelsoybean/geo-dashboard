import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from script import *

def render():
    st.title("TAILORS")
    # st.write("Dashboard Analisis Data Penjahit")

    # CSS untuk metric cards
    st.markdown("""
    <style>
    .metric-card {
        background-color: #1f2937;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        color: white;
        min-height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .metric-title {
        font-size: 13px;
        opacity: 0.8;
        margin-bottom: 10px;
    }
    .metric-value {
        font-size: 32px;
        font-weight: bold;
    }
    .metric-subtitle {
        font-size: 12px;
        opacity: 0.7;
        margin-top: 5px;
    }
    .scoring-box {
        background-color: #312e81;
        padding: 15px;
        border-radius: 10px;
        color: white;
    }
    .scoring-item {
        display: flex;
        justify-content: space-between;
        margin: 8px 0;
        font-size: 14px;
    }
    .scoring-label {
        opacity: 0.9;
    }
    .scoring-value {
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

    # READ DATA FROM GOOGLE SHEETS
    tailor_sheets_id = "1f1_CVH5W8EuV_HGpJRPuR3rDQhUjXM_B"
    tailor_df = read_sheets(tailor_sheets_id, "penjahit")

    # CLEAN DATA
    tailor_df["Kode Penjahit"] = tailor_df["Kode Penjahit"].astype(str).str.strip()
    
    # Hapus duplikat
    tailor_df = tailor_df.drop_duplicates(subset=["Kode Penjahit"])
    
    # Konversi kolom numerik
    numeric_cols = ["Usia", "Kerapian", "Ketepatan Waktu", "Quantity", "Komitmen", 
                    "Index_Kapasitas", "Kapasitas_Harian", "Seragam Hem Putih",
                    "Seragam Hem Pramuka", "Rok Seragam",
                    "Celana Seragam", "Kemeja Kerja",
                    "Custom Sulit"]
    
    for col in numeric_cols:
        if col in tailor_df.columns:
            tailor_df[col] = pd.to_numeric(tailor_df[col], errors='coerce').fillna(0)

    # Filter penjahit aktif
    active_tailors = tailor_df[tailor_df["Kode Penjahit"] != "Non Aktif"]

    # === HITUNG METRICS ===
    avg_kapasitas = active_tailors["Kapasitas_Harian"].mean()
    total_kapasitas = active_tailors["Kapasitas_Harian"].sum()

    avg_kerapian = active_tailors["Kerapian"].mean()
    avg_tepat_waktu = active_tailors["Ketepatan Waktu"].mean()
    avg_qty = active_tailors["Quantity"].mean()
    avg_komitmen = active_tailors["Komitmen"].mean()
    avg_usia = active_tailors["Usia"].mean()
    
    # --- [TAMBAHAN BARU] HITUNG OVERALL SCORE ---
    # Kita rata-rata 3 komponen utama (Rapi, Tepat, Komit) jadi satu nilai
    overall_score = (avg_kerapian + avg_tepat_waktu + avg_komitmen + avg_qty) / 4
    # ---------------------------------------------

    # Hitung persentase keluarga miskin
    if "Kategori" in active_tailors.columns:
        # 1. Ambil kolom, ubah jadi string, huruf kecil (lowercase), dan hapus spasi
        status_series = active_tailors["Kategori"].astype(str).str.lower().str.strip()
        
        # 2. FILTER LOGIC:
        # Cari yang diawali kata "miskin"
        # Menangkap: "miskin non ekstrem", "miskin ekstrem"
        # Menolak: "non miskin", "belum terdata"
        miskin_count = status_series[status_series.str.startswith("miskin")].shape[0]
        
        persen_miskin = (miskin_count / len(active_tailors)) * 100 if len(active_tailors) > 0 else 0
    else:
        persen_miskin = 0

    # === METRICS SECTION (5 KOLOM BARU) ===
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Capacity Mean</div>
            <div class="metric-value">{avg_kapasitas:.1f}</div>
            <div class="metric-subtitle">pcs/day</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card" style="background-color: #064e3b;">
            <div class="metric-title">Total Capacity</div>
            <div class="metric-value">{int(total_kapasitas)}</div>
            <div class="metric-subtitle">pcs/day</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card" style="background-color: #312e81; border: 1px solid #4338ca;">
            <div class="metric-title">Quality Score</div>
            <div class="metric-value">{overall_score:.2%}</div>
            <div class="metric-subtitle">Mean Total Peformance</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Low-income family:</div>
            <div class="metric-value">{persen_miskin:.1f}%</div>
            <div class="metric-subtitle">from total tailors</div>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Average Age</div>
            <div class="metric-value">{avg_usia:.1f}</div>
            <div class="metric-subtitle">years</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # === CHARTS SECTION ===
    chart_row1_col1, chart_row1_col2 = st.columns(2)

    # CHART 1: Perbandingan Kecamatan (Bar Chart)
    with chart_row1_col1:
        st.subheader("Dristrict Distribution")
        if "Kecamatan" in active_tailors.columns:
            kec_data = active_tailors["Kecamatan"].value_counts().reset_index()
            kec_data.columns = ["Kecamatan", "Jumlah"]
            kec_data = kec_data.sort_values("Jumlah", ascending=True)  # Sort ascending
            
            fig1 = px.pie(
                kec_data,
                names="Kecamatan",
                values="Jumlah",
                color="Jumlah",  # opsional, kalau mau pakai skala warna
                hole=0  # kalau mau donut chart bisa kasih nilai >0, misal 0.3
            )

            # Kalau mau tampilkan persentase atau label di pie chart
            fig1.update_traces(textinfo='percent+label')
            st.plotly_chart(fig1, use_container_width=True)

    # CHART 2: Kapasitas Harian (Bar Chart Horizontal)
    with chart_row1_col2:
        st.subheader("Daily Capacity")
        if "Kategori_Pekerja" in active_tailors.columns:
            kap_data = active_tailors.groupby("Kategori_Pekerja")["Kapasitas_Harian"].sum().reset_index()
            kap_data = kap_data.sort_values("Kapasitas_Harian", ascending=True)
            
            fig2 = go.Figure(go.Bar(
                x=kap_data["Kapasitas_Harian"],
                y=kap_data["Kategori_Pekerja"],
                orientation='h',
                marker=dict(color='#3b82f6'),
                text=kap_data["Kapasitas_Harian"],
                textposition='outside'
            ))
            fig2.update_layout(
                height=400,
                xaxis_title="Total Kapasitas (pcs/hari)",
                yaxis_title="",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # === SLICER SECTION ===
    st.subheader("Filter & Slicer")
    
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    
    with filter_col1:
        if "Kecamatan" in active_tailors.columns:
            kecamatan_list = ["Semua"] + sorted(active_tailors["Kecamatan"].unique().tolist())
            selected_kec = st.selectbox("Pilih Kecamatan", kecamatan_list)
        else:
            selected_kec = "Semua"
    
    with filter_col2:
        if "Cluster" in active_tailors.columns:
            cluster_list = ["Semua"] + sorted(active_tailors["Cluster"].dropna().unique().tolist())
            selected_cluster = st.selectbox("Pilih Cluster", cluster_list)
        else:
            selected_cluster = "Semua"
    
    with filter_col3:
        if "Kategori_Pekerja" in active_tailors.columns:
            kategori_list = ["Semua"] + sorted(active_tailors["Kategori_Pekerja"].dropna().unique().tolist())
            selected_kategori = st.selectbox("Pilih Kategori Pekerja", kategori_list)
        else:
            selected_kategori = "Semua"

    # Apply filters
    filtered_df = active_tailors.copy()
    if selected_kec != "Semua":
        filtered_df = filtered_df[filtered_df["Kecamatan"] == selected_kec]
    if selected_cluster != "Semua":
        filtered_df = filtered_df[filtered_df["Cluster"] == selected_cluster]
    if selected_kategori != "Semua":
        filtered_df = filtered_df[filtered_df["Kategori_Pekerja"] == selected_kategori]

    st.markdown("---")

    # === PROFIL PEKERJA TABLE ===
    st.subheader("Profil Pekerja")
    st.write(f"Menampilkan {len(filtered_df)} dari {len(active_tailors)} penjahit")

    # Pilih kolom yang ingin ditampilkan
    display_cols = ["Kode Penjahit", "Nama", "Kecamatan", "Usia", "Kerapian", 
                    "Ketepatan Waktu", "Quantity", "Komitmen", "Skill_Final", 
                    "Kategori_Pekerja", "Kapasitas_Harian"]
    
    # Filter kolom yang ada
    display_cols = [col for col in display_cols if col in filtered_df.columns]
    
    # Format display
    display_df = filtered_df[display_cols].copy()
    
    # Sorting options
    sort_col1, sort_col2 = st.columns([1, 3])
    with sort_col1:
        sort_by = st.selectbox("Urutkan berdasarkan", display_cols)
    with sort_col2:
        sort_order = st.radio("Urutan", ["Ascending", "Descending"], horizontal=True)
    
    ascending = sort_order == "Ascending"
    display_df = display_df.sort_values(sort_by, ascending=ascending)

    # Display table with custom styling
    st.dataframe(
        display_df,
        use_container_width=True,
        height=400,
        hide_index=True
    )

    # Download button
    csv = display_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Data (CSV)",
        data=csv,
        file_name='data_penjahit_filtered.csv',
        mime='text/csv',
    )