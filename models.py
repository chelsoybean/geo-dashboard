import streamlit as st
import pandas as pd
import math

from datetime import date, timedelta
from script import *

#READ DATA FROM GOOGLE SHEETS
tailor_sheets_id = "1f1_CVH5W8EuV_HGpJRPuR3rDQhUjXM_B"
tailor_df = read_sheets(tailor_sheets_id, "penjahit")

project_sheets_id = "18saFv1Kb5waaRbM6qOuufAicjh8MoynG2aVi24tHLjw"
project_df = read_sheets(project_sheets_id, "table_append")

# === CATEGORY MAPPING ===
CATEGORY_MAP = {
    "Seragam Full Set": ["Seragam Hem Putih", "Celana Seragam"],

    "Atribut & Non-Baju": ["Custom Sulit"],

    "Kaos & T-Shirt": ["Kemeja Kerja"],
    "Seragam Custom": ["Kemeja Kerja"],
    "Seragam Dinas (PDH)": ["Kemeja Kerja"],
    "Busana Religi": ["Kemeja Kerja"],

    "Celana Seragam": ["Celana Seragam"],
    "Rok Seragam": ["Rok Seragam"],

    "Seragam Lapangan": ["Custom Sulit"],

    "Seragam Atasan Hem Putih": ["Seragam Hem Putih"],
    "Seragam Atasan Hem Pramuka": ["Seragam Hem Pramuka"],
}

SPECIALIZATION_MAP = {
    "Seragam Atasan Hem Putih": ["Modest", "Elite_Produksi", "Umum", "Seragam"],
    "Seragam Atasan Hem Pramuka": ["Modest", "Elite_Produksi", "Umum", "Seragam"],
    "Celana Seragam": ["Modest", "Elite_Produksi", "Umum", "Seragam"],
    "Rok Seragam": ["Modest", "Elite_Produksi", "Umum", "Seragam"],
    "Kemeja Kerja": ["Modest", "Elite_Produksi", "Umum"],
    "Custom Sulit": ["Modest"],
}

#CONVERT TYPE
num_cols = [
        'Qty', 'Harga', 'Jumlah', 'Total jual',
        'RAB', 'Realisasi', 'Profit',
        'Gap', 'Margin', 'Markup'
        ]

numeric_cols = ["Usia", "Kerapian", "Ketepatan Waktu", "Quantity", "Komitmen", 
                "Index_Kapasitas", "Kapasitas_Harian", "Seragam Hem Putih",
                "Seragam Hem Pramuka", "Rok Seragam",
                "Celana Seragam", "Kemeja Kerja",
                "Custom Sulit"]

project_df = clean_numeric(project_df, num_cols)

def estimate_project_duration(df_tailor, kategori, total_qty, deadline: date, start_date: date = None, priority=None):
    # ambil mapping kapasitas
    kapasitas_cols = CATEGORY_MAP.get(kategori)

    if kapasitas_cols is None:
        raise ValueError(f"Kategori '{kategori}' belum dimapping")

    df = df_tailor.copy()
    df = clean_numeric(df, numeric_cols)

    # Filter tailor yang aktif saja
    if 'Kode Penjahit' in df.columns:
        df = df[df['Kode Penjahit'] != "Non Aktif"]

    # Tentukan spesialisasi yang sesuai untuk kategori proyek ini (gabungan dari semua subkategori)
    allowed_specializations = set()
    for subcat in kapasitas_cols:
        allowed_specializations.update(SPECIALIZATION_MAP.get(subcat, []))

    # Filter tailor yg cluster/spesialisasinya ada di allowed_specializations
    if 'Skill_Final' in df.columns:
        df = df[df['Skill_Final'].isin(allowed_specializations)]

    # hitung effective capacity per tailor
    df["effective_capacity"] = 0

    for col in kapasitas_cols:
        if col in df.columns:
            df["effective_capacity"] += df[col].fillna(0)

    # dikalikan index kapasitas
    df["effective_capacity"] *= df["Index_Kapasitas"]

    # buang tailor yg tidak bisa ngerjain
    df_valid = df[df["effective_capacity"] > 0]

    if df_valid.empty:
        return {
            "status": "FAILED",
            "reason": "There is no available tailor for this project category."
        }

    # total kapasitas harian
    total_capacity_per_day = df_valid["effective_capacity"].sum()

    # estimasi hari
    estimated_days = math.ceil(total_qty / total_capacity_per_day)

    if start_date is None:
        start_date = date.today()

    estimated_finish_date = start_date + timedelta(days=estimated_days)
    days_over = (estimated_finish_date - deadline).days

    if days_over <= 0:
        overtime_risk = "LOW"
    elif days_over <= 3:
        overtime_risk = "MEDIUM"
    else:
        overtime_risk = "HIGH"


    # risk keterlambatan
    risk_score = df_valid["Ketepatan Waktu"].mean()
    q1 = df_valid["Ketepatan Waktu"].quantile(0.25)
    q3 = df_valid["Ketepatan Waktu"].quantile(0.75)

    risk_level = (
        "HIGH" if risk_score < q1 else
        "MEDIUM" if risk_score < q3 else
        "LOW"
    )

    #Probability of On-Time Completion
    base_possibility = risk_score * 100  # misal confidence_score diubah ke persen
    deadline_buffer = (deadline - start_date).days - estimated_days

    if deadline_buffer < 0:
        # Kalau overtime gak boleh di urgent, langsung 0%
        if priority.lower() == 'urgent':
            possibility_pct = 0
        else:
            # Normal boleh overtime, tapi tetap 0% kalau waktunya benar-benar mepet
            possibility_pct = max(0, base_possibility - 50)  # misal potong besar juga
    elif deadline_buffer < 3:
        # Buffer kecil, urgent kemungkinan turun lebih tajam
        if priority.lower() == 'urgent':
            possibility_pct = max(0, base_possibility - 40)
        else:
            possibility_pct = max(0, base_possibility - 20)
    else:
        # Buffer cukup, peluang sama base
        possibility_pct = base_possibility

    return {
        "kategori": kategori,
        "qty": total_qty,
        "kapasitas_harian": math.ceil(total_capacity_per_day),
        "estimasi_hari": estimated_days,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "confidence_score": round(risk_score, 2),
        "tailor_recommended": df_valid,
        "total_tailors": len(df_valid),
        "overtime_risk": overtime_risk,
        "possibility_pct": possibility_pct,
    }
