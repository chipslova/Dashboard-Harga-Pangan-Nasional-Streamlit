import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ==============================
# CONFIG & GLOBAL STYLE
# ==============================
st.set_page_config(
    page_title="Dashboard Harga Pangan Nasional",
    layout="wide",
    page_icon="🛒"
)

# ---- Custom CSS (clean, bright, simple) ----
st.markdown(
    """
    <style>
    .stApp {
        background: radial-gradient(circle at top left, #e0f2fe 0, #f9fafb 40%, #fefce8 100%);
        font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        color: #111827;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    .big-title {
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        background: linear-gradient(120deg,#0ea5e9,#22c55e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.1rem;
    }

    .subtitle {
        font-size: 0.95rem;
        color: #4b5563;
        margin-bottom: 0.8rem;
    }

    .pill {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.25rem 0.7rem;
        border-radius: 999px;
        background: rgba(14, 165, 233, 0.08);
        border: 1px solid rgba(14, 165, 233, 0.22);
        color: #0369a1;
        font-size: 0.78rem;
        font-weight: 500;
        margin-right: 0.35rem;
    }

    .section-card {
        background: rgba(255,255,255,0.94);
        border-radius: 1rem;
        padding: 1.2rem 1.2rem 1rem 1.2rem;
        border: 1px solid rgba(148,163,184,0.35);
        box-shadow: 0 18px 35px rgba(15,23,42,0.08);
        margin-bottom: 1.2rem;
    }

    .section-title {
        font-size: 1.05rem;
        font-weight: 650;
        color: #111827;
        margin-bottom: 0.1rem;
    }

    .section-caption {
        font-size: 0.8rem;
        color: #6b7280;
        margin-bottom: 0.7rem;
    }

    .caption-muted {
        font-size: 0.8rem;
        color: #6b7280;
        margin-top: 0.3rem;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.3rem;
        padding-bottom: 0.25rem;
        border-bottom: 1px solid rgba(148,163,184,0.5);
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 999px;
        padding: 0.2rem 0.9rem;
        font-size: 0.85rem;
        font-weight: 500;
        color: #4b5563;
        background-color: #e5e7eb;
    }

    .stTabs [aria-selected="true"] {
        background: #0ea5e9;
        color: white;
        box-shadow: 0 10px 18px rgba(15,23,42,0.18);
    }

    /* Metrics */
    div[data-testid="stMetric"] {
        background: #f9fafb;
        padding: 0.75rem 0.85rem;
        border-radius: 0.9rem;
        border: 1px solid rgba(209,213,219,0.9);
        box-shadow: 0 14px 28px rgba(15,23,42,0.08);
    }

    div[data-testid="stMetric"] > label {
        font-size: 0.78rem;
        color: #6b7280;
    }

    div[data-testid="stMetric"] > div {
        color: #111827;
    }

    /* Sliders & select widgets */
    .stSlider > div > div > div {
        background: linear-gradient(90deg,#0ea5e9,#22c55e);
    }

    .stSelectbox, .stMultiSelect {
        border-radius: 0.8rem !important;
    }

    .streamlit-expanderHeader {
        font-size: 0.86rem;
        color: #111827;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==============================
# HEADER
# ==============================
st.markdown('<div class="big-title">Dashboard Harga Pangan Konsumen di Indonesia</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">'
    'Analisis pola, tren, dan perbandingan harga komoditas pangan utama di 505 Kabupaten/Kota Indonesia '
    '<span style="color:#6b7280;">(Januari 2024 – Agustus 2025)</span>'
    '</div>',
    unsafe_allow_html=True
)

# ==============================
# LOAD DATA
# ==============================
@st.cache_data
def load_data():
    clean = pd.read_csv("data/data_harga_pangan_wide_imputed.csv")
    wins = pd.read_csv("data/data_harga_pangan_wide_imputed_winsor.csv")

    # Pastikan kolom tanggal benar
    if "Periode" not in clean.columns:
        clean.rename(columns={clean.columns[0]: "Periode"}, inplace=True)
    if "Periode" not in wins.columns:
        wins.rename(columns={wins.columns[0]: "Periode"}, inplace=True)

    clean["Periode"] = pd.to_datetime(clean["Periode"])
    wins["Periode"] = pd.to_datetime(wins["Periode"])

    # Deteksi kolom komoditas (numerik, exclude kolom teknis)
    exclude_cols = ["Tahun", "Bulan_num", "bulan_num", "latitude", "longitude", "SPHP_covered"]
    komoditas_cols = [
        c for c in clean.select_dtypes(include=[np.number]).columns
        if c not in exclude_cols
    ]

    return clean, wins, komoditas_cols


@st.cache_data
def load_geo():
    try:
        df_geo = pd.read_csv("data/data_harga_pangan_with_latlon_FINAL.csv")
        if "Periode" not in df_geo.columns:
            df_geo.rename(columns={df_geo.columns[0]: "Periode"}, inplace=True)
        df_geo["Periode"] = pd.to_datetime(df_geo["Periode"])
        return df_geo
    except FileNotFoundError:
        return None


clean, wins, komoditas_cols = load_data()
df_geo = load_geo()

# Info kecil di header (bikin “pop” dikit)
col_badge1, col_badge2 = st.columns([2, 1])
with col_badge1:
    st.markdown(
        """
        <span class="pill">📊 Rata-rata nasional & tren per komoditas</span>
        <span class="pill">🗺️ Perbandingan antar kabupaten/kota</span>
        <span class="pill">🔗 Korelasi harga komoditas</span>
        """,
        unsafe_allow_html=True
    )
with col_badge2:
    st.caption("Sumber: Panel Harga Pangan Nasional (konsumen)")

# sedikit ringkasan angka
n_komoditas = len(komoditas_cols)
n_periode = clean["Periode"].nunique()
if "Kab/Kota" in clean.columns:
    n_kabkota = clean["Kab/Kota"].nunique()
else:
    # fallback
    obj_cols = clean.select_dtypes(include="object").columns
    n_kabkota = clean[obj_cols[0]].nunique() if len(obj_cols) > 0 else 505

mcol1, mcol2, mcol3 = st.columns(3)
mcol1.metric("Jumlah komodi
