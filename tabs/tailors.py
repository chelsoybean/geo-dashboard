import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from script import *

def render():
    st.title("Data Penjahit")
    st.write("Dashboard Analisis Data Penjahit")

    # CSS untuk metric cards
    st.markdown("""
    <style>
    .metric-card {
        background-color: #1f2937;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        color: white;
        min-height: 100px;
    }
    .metric-title {
        font-size: 12px;
        opacity: 0.8;
        margin-bottom: 10px;
    }
    .metric-value {
        font-size: 32px;
        font-weight: bold;
    }
    .metric-subtitle {
        font-size: 14px;
        opacity: 0.7;
        margin-top: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

    # READ DATA FROM GOOGLE SHEETS
    tailor_sheets_id = "1f1_CVH5W8EuV_HGpJRPuR3rDQhUjXM_B"
    tailor_df = read_sheets(tailor_sheets_id, "penjahit")

    # CLEAN DATA
    tailor_df["Kode Penjahit"] = tailor_df["Kode Penjahit"].astype(str).str.strip()
    # --- [TAMBAHKAN INI] ---
    # Ini akan membuat len() nanti hasilnya jadi 109 (sama dengan dashboard)
    tailor_df = tailor_df.drop_duplicates(subset=["Kode Penjahit"])
    
    # Konversi kolom numerik
    numeric_cols = ["Usia", "Kerapian", "Ketepatan Waktu", "Quantity", "Komitmen", 
                    "Index_Kapasitas", "Kapasitas_Harian", "Seragam Hem Putih (Pcs/hari)",
                    "Seragam Hem Pramuka (Pcs/hari)", "Rok Seragam (Pcs/hari)",
                    "Celana Pramuka Seragam (Pcs/hari)", "Kemeja Kerja (Pcs/hari)",
                    "Custom (Sulit) (Pcs/hari)"]
    
    for col in numeric_cols:
        if col in tailor_df.columns:
            tailor_df[col] = pd.to_numeric(tailor_df[col], errors='coerce').fillna(0)

    # Filter penjahit aktif
    active_tailors = tailor_df[tailor_df["Kode Penjahit"] != "Non Aktif"]

    # === METRICS SECTION ===
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        total_active = len(active_tailors)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Aktif</div>
            <div class="metric-value">{total_active}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        avg_rapi = active_tailors["Kerapian"].mean()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Avg Kerapian</div>
            <div class="metric-value">{avg_rapi:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        avg_tepat = active_tailors["Ketepatan Waktu"].mean()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Tepat Waktu</div>
            <div class="metric-value">{avg_tepat:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        avg_qty = active_tailors["Quantity"].mean()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Avg Qty</div>
            <div class="metric-value">{avg_qty:.1f}</div>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        avg_komit = active_tailors["Komitmen"].mean()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Komitmen</div>
            <div class="metric-value">{avg_komit:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

    with col6:
        total_kapasitas = active_tailors["Kapasitas_Harian"].sum()
        st.markdown(f"""
        <div class="metric-card" style="background-color: #064e3b;">
            <div class="metric-title">Total Kapasitas</div>
            <div class="metric-value">{int(total_kapasitas)}</div>
            <div class="metric-subtitle">pcs/hari</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # === CHARTS SECTION ===
    chart_row1_col1, chart_row1_col2 = st.columns(2)

    # CHART 1: Perbandingan Kecamatan (Bar Chart)
    with chart_row1_col1:
        st.subheader("Perbandinan Kecamatan")
        if "Kecamatan" in active_tailors.columns:
            kec_data = active_tailors["Kecamatan"].value_counts().reset_index()
            kec_data.columns = ["Kecamatan", "Jumlah"]
            
            fig1 = px.bar(kec_data, x="Kecamatan", y="Jumlah",
                         color="Jumlah",
                         color_continuous_scale=["#fbbf24", "#f59e0b", "#d97706", "#b45309"],
                         text="Jumlah")
            fig1.update_traces(textposition='outside')
            fig1.update_layout(
                showlegend=False,
                height=400,
                xaxis_title="",
                yaxis_title="Jumlah Penjahit",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            st.plotly_chart(fig1, use_container_width=True)

    # CHART 2: Kapasitas Harian (Bar Chart Horizontal)
    with chart_row1_col2:
        st.subheader("Kapasitas Harian")
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