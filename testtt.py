import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ==============================
# 1. CONFIG & PAGE SETUP
# ==============================
st.set_page_config(
    page_title="Dashboard Harga Pangan Nasional",
    layout="wide",
    page_icon="🛒"
)

# ==============================
# 2. CUSTOM CSS (BLUE THEME PROFESSIONAL)
# ==============================
st.markdown(
    """
    <style>
    /* Global Background */
    .stApp {
        background: radial-gradient(circle at top left, #f0f9ff 0, #f8fafc 40%, #ffffff 100%);
        font-family: "Inter", sans-serif;
        color: #1e293b;
    }

    /* Header Cleaner */
    header[data-testid="stHeader"] {
        background: transparent;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 4rem;
        max-width: 1250px;
    }

    /* --- TYPOGRAPHY & HEADER --- */
    
    /* Judul dengan Flag + Gradient */
    .title-flag {
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        background: linear-gradient(120deg, #0284c7, #0ea5e9, #10b981);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
        display: inline-flex;
        align-items: center;
        gap: 0.7rem;
    }

    /* Bendera Merah Putih (CSS Shape) */
    .id-flag {
        display: inline-block;
        width: 30px;
        height: 20px;
        border-radius: 4px;
        box-shadow: 0 0 0 1px rgba(148,163,184,0.4);
        background: linear-gradient(to bottom, #dc2626 0, #dc2626 50%, #f9fafb 50%, #f9fafb 100%);
    }

    .subtitle {
        font-size: 1rem;
        color: #64748b;
        margin-bottom: 1.5rem;
    }

    /* --- HERO CARD (BLUE GLASSMOPHISM) --- */
    .hero-card {
        display: flex;
        align-items: center;
        gap: 1.5rem;
        padding: 1.5rem 1.8rem;
        border-radius: 1rem;
        background: 
            radial-gradient(circle at top left, rgba(224, 242, 254, 0.9), rgba(240, 253, 244, 0.4)),
            linear-gradient(120deg, #ffffff, #f0f9ff);
        border: 1px solid rgba(14, 165, 233, 0.3);
        box-shadow: 0 10px 30px -5px rgba(14, 165, 233, 0.15);
        margin-bottom: 2rem;
    }

    .hero-emoji {
        font-size: 2.8rem;
        filter: drop-shadow(0 8px 12px rgba(14, 165, 233, 0.2));
    }

    .hero-text-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #0369a1;
        margin-bottom: 0.3rem;
    }

    .hero-text-sub {
        font-size: 0.9rem;
        color: #475569;
        line-height: 1.5;
    }

    .hero-chip-row {
        margin-top: 0.8rem;
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
    }

    .hero-chip {
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.3rem 0.8rem;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.7);
        border: 1px dashed rgba(14, 165, 233, 0.7);
        color: #0284c7;
    }

    /* --- COMPONENTS --- */
    
    .section-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #1e293b;
        margin-top: 1rem;
        margin-bottom: 0.2rem;
    }
    
    .section-caption {
        font-size: 0.9rem;
        color: #64748b;
        margin-bottom: 1.2rem;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        border-bottom: 1px solid #cbd5e1;
        padding-bottom: 0.5rem;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 999px;
        padding: 0.4rem 1rem;
        font-size: 0.9rem;
        font-weight: 500;
        background-color: #f1f5f9;
        color: #64748b;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0ea5e9;
        color: white;
        box-shadow: 0 4px 10px rgba(14, 165, 233, 0.3);
    }

    /* Metrics Box */
    div[data-testid="stMetric"] {
        background: #ffffff;
        padding: 1rem;
        border-radius: 0.8rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.03);
    }
    
    div[data-testid="stMetric"] label {
        color: #64748b;
        font-size: 0.8rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==============================
# 3. DATA HANDLING (REAL + DUMMY FALLBACK)
# ==============================

@st.cache_data
def get_data():
    """
    Mencoba load data asli. Jika gagal, generate dummy data
    agar dashboard tetap bisa tampil (mode demo).
    """
    try:
        # Coba load file asli
        clean = pd.read_csv("data/data_harga_pangan_wide_imputed.csv")
        wins = pd.read_csv("data/data_harga_pangan_wide_imputed_winsor.csv")
        df_geo = pd.read_csv("data/data_harga_pangan_with_latlon_FINAL.csv")
        
        # Standardisasi kolom
        if "Periode" not in clean.columns: clean.rename(columns={clean.columns[0]: "Periode"}, inplace=True)
        if "Periode" not in wins.columns: wins.rename(columns={wins.columns[0]: "Periode"}, inplace=True)
        if "Periode" not in df_geo.columns: df_geo.rename(columns={df_geo.columns[0]: "Periode"}, inplace=True)
        
        clean["Periode"] = pd.to_datetime(clean["Periode"])
        wins["Periode"] = pd.to_datetime(wins["Periode"])
        df_geo["Periode"] = pd.to_datetime(df_geo["Periode"])
        
        # Ambil kolom komoditas (numeric only, exclude coords)
        exclude = ["Tahun", "Bulan_num", "latitude", "longitude", "SPHP_covered"]
        komoditas_cols = [c for c in clean.select_dtypes(include=np.number).columns if c not in exclude]
        
        return clean, wins, df_geo, komoditas_cols, False # False = bukan dummy

    except FileNotFoundError:
        # --- GENERATE DUMMY DATA ---
        dates = pd.date_range(start="2024-01-01", end="2025-08-01", freq="MS")
        # List region dengan koordinat
        regions = [
            ("Jakarta Selatan", -6.26, 106.81), ("Surabaya", -7.25, 112.75),
            ("Medan", 3.59, 98.67), ("Makassar", -5.14, 119.43),
            ("Bandung", -6.91, 107.60), ("Denpasar", -8.67, 115.21),
            ("Jayapura", -2.54, 140.70), ("Balikpapan", -1.23, 116.88),
            ("Semarang", -7.00, 110.42), ("Palembang", -2.97, 104.77)
        ]
        
        data = []
        for d in dates:
            for city, lat, lon in regions:
                # Simulasi harga acak dengan pola musiman sederhana
                base_beras = 15000 + np.random.randint(-1000, 2000)
                base_cabe = 50000 + (np.sin(d.month) * 15000) + np.random.randint(-5000, 5000)
                base_ayam = 38000 + np.random.randint(-3000, 3000)
                base_minyak = 16000 + (d.month * 100) # trend naik tipis
                base_bawang = 30000 + np.random.randint(-5000, 8000)
                
                row = {
                    "Periode": d,
                    "Kab/Kota": city,
                    "latitude": lat,
                    "longitude": lon,
                    "Beras Premium": base_beras,
                    "Cabai Merah Keriting": base_cabe,
                    "Daging Ayam Ras": base_ayam,
                    "Minyak Goreng": base_minyak,
                    "Bawang Merah": base_bawang
                }
                data.append(row)
        
        df = pd.DataFrame(data)
        komoditas_cols = ["Beras Premium", "Cabai Merah Keriting", "Daging Ayam Ras", "Minyak Goreng", "Bawang Merah"]
        
        return df, df.copy(), df.copy(), komoditas_cols, True # True = dummy data

# Load Data
clean, wins, df_geo, komoditas_cols, is_dummy = get_data()

# ==============================
# 4. HEADER UI
# ==============================
st.markdown("<br>", unsafe_allow_html=True)

# Judul Utama
st.markdown(
    '<div class="title-flag"><span class="id-flag"></span> Dashboard Harga Pangan Nasional</div>', 
    unsafe_allow_html=True
)

# Subjudul
st.markdown(
    '<div class="subtitle">'
    'Pantauan komprehensif harga beras, cabai, bawang, dan kebutuhan pokok '
    f'di {clean["Kab/Kota"].nunique() if "Kab/Kota" in clean.columns else 505} Kabupaten/Kota (Jan 2024 – Agu 2025).'
    '</div>',
    unsafe_allow_html=True
)

# Hero Card (Market Insight Edition)
st.markdown(
    """
    <div class="hero-card">
      <div class="hero-emoji">🍚🐟🥚📊</div>
      <div>
        <div class="hero-text-title">“Market Insight Edition” – Data harga pangan yang jernih & transparan.</div>
        <div class="hero-text-sub">
          Setiap angka merepresentasikan dinamika daya beli konsumen, stabilitas pasokan daerah, hingga tren inflasi nasional.
          Dashboard ini menyajikan tren, disparitas wilayah, dan korelasi komoditas.
        </div>
        <div class="hero-chip-row">
          <div class="hero-chip">Harga beras & bahan pokok</div>
          <div class="hero-chip">Volatilitas bumbu dapur</div>
          <div class="hero-chip">Disparitas wilayah</div>
          <div class="hero-chip">Korelasi komoditas</div>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True
)

if is_dummy:
    st.info("⚠️ **Mode Demo Aktif:** File data asli tidak ditemukan. Dashboard ini berjalan menggunakan **Data Simulasi**.")

# ==============================
# 5. DASHBOARD TABS
# ==============================

# Ringkasan Metrics Kecil
col_m1, col_m2 = st.columns(2)
col_m1.metric("Jumlah Komoditas Dipantau", f"{len(komoditas_cols)}")
col_m2.metric("Jumlah Titik Wilayah", f"{clean['Kab/Kota'].nunique() if 'Kab/Kota' in clean.columns else '505'}")

st.markdown("---")

tab1, tab2, tab3 = st.tabs(["📈 Tren Nasional", "🗺️ Peta & Wilayah", "🔗 Korelasi"])

# --- TAB 1: TREN NASIONAL ---
with tab1:
    st.markdown('<div class="section-title">Perkembangan Rata-rata Harga Nasional</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-caption">Analisis time-series pergerakan harga komoditas utama.</div>', unsafe_allow_html=True)
    
    col_t1, col_t2 = st.columns([1, 3])
    with col_t1:
        selected_kom_trend = st.multiselect(
            "Pilih Komoditas:", 
            options=komoditas_cols, 
            default=komoditas_cols[:2] if len(komoditas_cols) > 1 else komoditas_cols
        )
    
    # Agregasi Rata-rata Nasional per Tanggal
    trend_data = clean.groupby("Periode")[komoditas_cols].mean().reset_index()
    
    if selected_kom_trend:
        fig_trend = px.line(trend_data, x="Periode", y=selected_kom_trend, markers=True)
        fig_trend.update_layout(
            template="plotly_white", 
            xaxis_title=None, 
            yaxis_title="Harga (Rp)",
            legend=dict(orientation="h", y=1.1, x=0),
            hovermode="x unified",
            height=450,
            margin=dict(l=0, r=0, t=0, b=0)
        )
        # Format Rupiah di Hover
        fig_trend.update_traces(hovertemplate="%{y:,.0f}")
        st.plotly_chart(fig_trend, use_container_width=True)
        
        # Insight Otomatis Sederhana
        st.markdown("#### 💡 Ringkasan Perubahan Harga (Bulan Terakhir)")
        cols_m = st.columns(len(selected_kom_trend))
        for i, kom in enumerate(selected_kom_trend):
            curr_price = trend_data[kom].iloc[-1]
            prev_price = trend_data[kom].iloc[-2] if len(trend_data) > 1 else curr_price
            delta = curr_price - prev_price
            cols_m[i].metric(label=kom, value=f"Rp {curr_price:,.0f}", delta=f"{delta:,.0f} (vs bln lalu)")
            
    else:
        st.warning("Silakan pilih minimal satu komoditas untuk menampilkan grafik.")


# --- TAB 2: PETA WILAYAH ---
with tab2:
    st.markdown('<div class="section-title">Sebaran Harga & Disparitas Wilayah</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-caption">Peta interaktif dan peringkat harga tertinggi/terendah per kota.</div>', unsafe_allow_html=True)
    
    # --- FIX: Filter komoditas yang HANYA ada di df_geo ---
    # Langkah ini mencegah error jika komoditas (misal: Beras SPHP) ada di data utama tapi tidak ada di data peta
    valid_map_cols = [c for c in komoditas_cols if c in df_geo.columns]
    
    if not valid_map_cols:
        st.error("Tidak ada kolom komoditas yang cocok antara data harga dan data peta.")
    else:
        c_map1, c_map2 = st.columns([1, 3])
        with c_map1:
            # Dropdown hanya menampilkan komoditas yang valid untuk peta
            kom_map = st.selectbox("Pilih Komoditas untuk Peta:", options=valid_map_cols)
            
            last_date = df_geo["Periode"].max()
            st.caption(f"Data per tanggal: {last_date.strftime('%d %b %Y')}")
        
        # Filter data geospasial bulan terakhir
        geo_filtered = df_geo[df_geo["Periode"] == last_date].copy()
        
        # Mapbox
        if not geo_filtered.empty and "latitude" in geo_filtered.columns:
            if kom_map in geo_filtered.columns:
                fig_map = px.scatter_mapbox(
                    geo_filtered,
                    lat="latitude", lon="longitude",
                    color=kom_map, size=kom_map,
                    color_continuous_scale="RdYlGn_r", # Merah = Mahal, Hijau = Murah
                    zoom=3.5, 
                    center={"lat": -2.5, "lon": 118},
                    mapbox_style="open-street-map",
                    hover_name="Kab/Kota" if "Kab/Kota" in geo_filtered.columns else None,
                    hover_data={kom_map: ":,.0f", "latitude": False, "longitude": False},
                    height=500
                )
                fig_map.update_layout(margin=dict(l=0,r=0,t=0,b=0))
                st.plotly_chart(fig_map, use_container_width=True)
                
                # Top 5 Mahal vs Murah
                st.markdown(f"#### Peringkat Wilayah: {kom_map}")
                col_rank1, col_rank2 = st.columns(2)
                
                lokasi_col = "Kab/Kota" if "Kab/Kota" in geo_filtered.columns else geo_filtered.columns[1]
                
                # Mahal
                top_exp = geo_filtered.nlargest(5, kom_map).sort_values(kom_map, ascending=True)
                fig_exp = px.bar(top_exp, x=kom_map, y=lokasi_col, orientation='h', title="5 Wilayah Termahal", text_auto=',.0f')
                fig_exp.update_traces(marker_color='#ef4444', hovertemplate="Rp %{x:,.0f}")
                fig_exp.update_layout(template="plotly_white", xaxis_title=None, yaxis_title=None, margin=dict(l=0,r=0,t=40,b=0))
                col_rank1.plotly_chart(fig_exp, use_container_width=True)
                
                # Murah
                top_cheap = geo_filtered.nsmallest(5, kom_map).sort_values(kom_map, ascending=True)
                fig_cheap = px.bar(top_cheap, x=kom_map, y=lokasi_col, orientation='h', title="5 Wilayah Termurah", text_auto=',.0f')
                fig_cheap.update_traces(marker_color='#22c55e', hovertemplate="Rp %{x:,.0f}")
                fig_cheap.update_layout(template="plotly_white", xaxis_title=None, yaxis_title=None, margin=dict(l=0,r=0,t=40,b=0))
                col_rank2.plotly_chart(fig_cheap, use_container_width=True)
            else:
                st.warning(f"Data untuk {kom_map} tidak ditemukan di file geospasial.")
        else:
            st.error("Data Latitude/Longitude tidak ditemukan atau kosong.")


# --- TAB 3: KORELASI ---
with tab3:
    st.markdown('<div class="section-title">Matriks Korelasi Antar Komoditas</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-caption">Semakin merah = korelasi positif kuat (harga naik bersamaan). Semakin biru = korelasi negatif/lemah.</div>', unsafe_allow_html=True)
    
    # Hitung korelasi
    if len(komoditas_cols) > 1:
        corr_matrix = wins[komoditas_cols].corr()
        
        fig_corr = px.imshow(
            corr_matrix,
            text_auto=".2f",
            color_continuous_scale="RdBu_r",
            zmin=-1, zmax=1,
            aspect="auto"
        )
        fig_corr.update_layout(height=600, template="plotly_white", margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig_corr, use_container_width=True)
        
        with st.expander("💡 Cara membaca matriks ini"):
            st.write("""
            - **Nilai mendekati 1 (Merah Pekat):** Komoditas memiliki hubungan kuat. Jika harga Komoditas A naik, harga Komoditas B kemungkinan besar ikut naik (contoh: Cabai Merah & Cabai Rawit).
            - **Nilai mendekati -1 (Biru Pekat):** Hubungan berlawanan.
            - **Nilai mendekati 0 (Putih):** Tidak ada hubungan yang jelas antara kedua komoditas.
            """)
    else:
        st.info("Data komoditas tidak cukup untuk menghitung korelasi.")
