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
st.markdown("<br>", unsafe_allow_html=True)
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
mcol1.metric("Jumlah komoditas", f"{n_komoditas}")
mcol2.metric("Jumlah periode pengamatan", f"{n_periode}")
mcol3.metric("Kabupaten/Kota terliput", f"{n_kabkota}")

# Kelompok komoditas (dipakai di Tab Tren Nasional)
groups = {
    "Semua": komoditas_cols,
    "Beras": [c for c in komoditas_cols if "beras" in c.lower()],
    "Protein Hewani": [c for c in komoditas_cols if any(k in c.lower() for k in ["daging", "telur", "ikan"])],
    "Bumbu Dapur": [c for c in komoditas_cols if any(k in c.lower() for k in ["cabai", "cabe", "bawang"])],
    "Bahan Pokok Lain": [c for c in komoditas_cols if any(k in c.lower() for k in ["minyak", "gula", "tepung", "kedelai", "garam"])]
}

st.markdown("---")

# ==============================
# TABS
# ==============================
tab1, tab2, tab3 = st.tabs([
    "📈 Tren Nasional",
    "🗺️ Perbandingan Wilayah",
    "🔗 Korelasi Komoditas"
])

# ==============================
# TAB 1 – TREN NASIONAL
# ==============================
with tab1:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Perkembangan Rata-rata Harga Komoditas Pangan Nasional</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-caption">Eksplorasi pergerakan harga per komoditas dan tren agregat nasional dari waktu ke waktu.</div>',
        unsafe_allow_html=True
    )

    min_date = clean["Periode"].min()
    max_date = clean["Periode"].max()

    # Slider full-width (periode)
    start_date, end_date = st.slider(
        "Periode analisis",
        min_value=min_date.date(),
        max_value=max_date.date(),
        value=(min_date.date(), max_date.date()),
        format="MMM YYYY"
    )

    # Kolom untuk pengaturan komoditas
    col_f1, col_f2 = st.columns([1, 2])

    with col_f1:
        group_choice = st.selectbox(
            "Kelompok komoditas",
            options=list(groups.keys()),
            key="group_tren"
        )

    with col_f2:
        candidate_koms = groups[group_choice] if groups[group_choice] else komoditas_cols
        default_koms = candidate_koms[:5] if len(candidate_koms) >= 5 else candidate_koms
        selected_koms = st.multiselect(
            "Komoditas yang ditampilkan",
            options=candidate_koms,
            default=default_koms,
            key="komoditas_tren"
        )

    # Filter data sesuai periode
    mask_clean_tren = clean["Periode"].dt.date.between(start_date, end_date)
    clean_tren = clean[mask_clean_tren].copy()

    if clean_tren.empty:
        st.warning("Tidak ada data untuk periode yang dipilih.")
    else:
        # Rata-rata nasional per periode
        avg_trend = clean_tren.groupby("Periode")[komoditas_cols].mean().reset_index()

        # Grafik tren per komoditas
        st.markdown("#### Tren Komoditas Terpilih")

        if not selected_koms:
            st.info("Pilih minimal satu komoditas untuk melihat grafik tren.")
        else:
            fig_trend = go.Figure()
            for col in selected_koms:
                if col not in avg_trend.columns:
                    continue
                fig_trend.add_trace(go.Scatter(
                    x=avg_trend["Periode"],
                    y=avg_trend[col],
                    mode="lines+markers",
                    name=col,
                    hovertemplate="%{x|%b %Y}<br>Rp%{y:,.0f}<extra></extra>"
                ))

            fig_trend.update_layout(
                xaxis_title="Periode",
                yaxis_title="Harga rata-rata (Rp)",
                hovermode="x unified",
                template="plotly_white",
                height=460,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#111827", size=11),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            st.plotly_chart(fig_trend, use_container_width=True)

        # Harga rata-rata nasional
        if selected_koms:
            title_tren_umum = "Rata-rata Harga Pangan (Komoditas Terpilih)"
            monthly_avg_all = avg_trend[selected_koms].mean(axis=1)
        else:
            title_tren_umum = "Tren Umum Harga Pangan Nasional (Semua Komoditas)"
            monthly_avg_all = avg_trend[komoditas_cols].mean(axis=1)

        if len(monthly_avg_all) > 1:
            start_price = float(monthly_avg_all.iloc[0])
            end_price = float(monthly_avg_all.iloc[-1])
            growth_nominal = end_price - start_price
            growth_percent = (growth_nominal / start_price * 100) if start_price != 0 else 0.0

            st.markdown("#### Ringkasan Pergerakan Harga")
            m1, m2, m3 = st.columns(3)
            m1.metric("Harga awal", f"Rp {start_price:,.0f}")
            m2.metric("Harga akhir", f"Rp {end_price:,.0f}", f"{growth_nominal:,.0f}")
            m3.metric(
                "Pertumbuhan rata-rata",
                f"{growth_percent:.2f}%" +
                ("" if selected_koms else " (semua komoditas)")
            )
            st.markdown(
                '<div class="caption-muted">'
                "Ringkasan ini merangkum dinamika harga rata-rata nasional pada komoditas dan periode yang dipilih."
                "</div>",
                unsafe_allow_html=True
            )

        with st.expander("💡 Insight tren nasional"):
            st.markdown(
                """
- Komoditas beras (premium, medium, SPHP) cenderung stabil dengan kenaikan bertahap.
- Cabai dan bawang menunjukkan lonjakan harga yang tajam dan berulang.
- Minyak goreng dan gula naik lebih pelan namun relatif konsisten.
- Secara agregat, rata-rata harga pangan nasional selama periode ini hanya naik tipis
  dan belum menunjukkan tren kenaikan tajam yang permanen.
"""
            )

    st.markdown('</div>', unsafe_allow_html=True)

# ==============================
# TAB 2 – PERBANDINGAN WILAYAH
# ==============================
with tab2:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Perbandingan Harga Antar Kabupaten/Kota</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-caption">Lihat sebaran spasial harga dan daftar kab/kota dengan harga tertinggi maupun terendah.</div>',
        unsafe_allow_html=True
    )

    if wins.empty:
        st.warning("Dataset kosong.")
    else:
        min_date_w = wins["Periode"].min()
        max_date_w = wins["Periode"].max()

        start_date_reg, end_date_reg = st.slider(
            "Periode analisis perbandingan wilayah",
            min_value=min_date_w.date(),
            max_value=max_date_w.date(),
            value=(min_date_w.date(), max_date_w.date()),
            format="MMM YYYY",
            key="periode_wilayah"
        )

        mask_wins_reg = wins["Periode"].dt.date.between(start_date_reg, end_date_reg)
        wins_reg = wins[mask_wins_reg].copy()

        if wins_reg.empty:
            st.warning("Tidak ada data untuk rentang waktu yang dipilih.")
        else:
            # Deteksi kolom kab/kota
            if "Kab/Kota" in wins_reg.columns:
                lokasi_col = "Kab/Kota"
            else:
                obj_cols = wins_reg.select_dtypes(include="object").columns.tolist()
                lokasi_col = obj_cols[0] if obj_cols else wins_reg.columns[0]

            kom_for_region = st.selectbox(
                "Pilih komoditas untuk dibandingkan antar kabupaten/kota",
                options=komoditas_cols
            )

            # PETA SEBARAN HARGA
            st.markdown("#### Peta Sebaran Harga per Kabupaten/Kota")

            if df_geo is None:
                st.info("File data geospasial (data_harga_pangan_with_latlon_FINAL.csv) tidak ditemukan. Peta tidak dapat ditampilkan.")
            else:
                # Filter df_geo berdasar periode yang sama (kalau ada kolom Periode)
                if "Periode" in df_geo.columns:
                    mask_geo_reg = df_geo["Periode"].dt.date.between(start_date_reg, end_date_reg)
                    geo_filtered = df_geo[mask_geo_reg].copy()
                else:
                    geo_filtered = df_geo.copy()

                # Deteksi kolom kab/kota di geo_filtered
                if "Kab/Kota" in geo_filtered.columns:
                    kab_col_geo = "Kab/Kota"
                else:
                    obj_cols_geo = geo_filtered.select_dtypes(include="object").columns.tolist()
                    kab_col_geo = obj_cols_geo[0] if obj_cols_geo else geo_filtered.columns[0]

                if kom_for_region not in geo_filtered.columns:
                    st.warning(f"Kolom {kom_for_region} tidak ditemukan di data geospasial.")
                else:
                    map_agg = (
                        geo_filtered
                        .groupby([kab_col_geo, "latitude", "longitude"], as_index=False)[kom_for_region]
                        .mean()
                        .dropna(subset=["latitude", "longitude"])
                    )

                    if map_agg.empty:
                        st.info("Tidak ada data lokasi yang valid untuk periode & komoditas ini.")
                    else:
                        fig_map = px.scatter_mapbox(
                            map_agg,
                            lat="latitude",
                            lon="longitude",
                            color=kom_for_region,
                            size=kom_for_region,
                            hover_name=kab_col_geo,
                            hover_data={kom_for_region: ":,.0f"},
                            color_continuous_scale="YlOrRd",
                            zoom=4,
                            height=480
                        )
                        fig_map.update_layout(
                            mapbox_style="open-street-map",
                            margin=dict(l=0, r=0, t=30, b=0),
                            paper_bgcolor="rgba(0,0,0,0)",
                            font=dict(color="#111827", size=11)
                        )
                        st.plotly_chart(fig_map, use_container_width=True)

            # RATA-RATA PER KAB/KOTA & JUMLAH KAB/KOTA
            mean_by_region = (
                wins_reg
                .groupby(lokasi_col)[kom_for_region]
                .mean()
                .reset_index()
                .dropna()
            )

            if mean_by_region.empty:
                st.info("Tidak ada data setelah agregasi per kab/kota.")
            else:
                n_region = st.slider(
                    "Jumlah kab/kota termahal & termurah yang ditampilkan",
                    min_value=3,
                    max_value=min(25, len(mean_by_region)),
                    value=10
                )

                top_expensive = (
                    mean_by_region
                    .sort_values(kom_for_region, ascending=False)
                    .head(n_region)
                )
                top_cheap = (
                    mean_by_region
                    .sort_values(kom_for_region, ascending=True)
                    .head(n_region)
                )

                c1, c2 = st.columns(2)

                # Kab/Kota termahal
                with c1:
                    fig_top = px.bar(
                        top_expensive.sort_values(kom_for_region),
                        x=kom_for_region,
                        y=lokasi_col,
                        orientation="h",
                        title=f"{n_region} Kab/Kota dengan Harga Tertinggi ({kom_for_region})",
                        template="plotly_white"
                    )
                    fig_top.update_traces(
                        hovertemplate="<b>%{y}</b><br>Rp %{x:,.0f}<extra></extra>",
                        marker_color="#fb7185"
                    )
                    fig_top.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="#111827", size=11)
                    )
                    st.plotly_chart(fig_top, use_container_width=True)

                # Kab/Kota termurah
                with c2:
                    fig_bottom = px.bar(
                        top_cheap.sort_values(kom_for_region, ascending=False),
                        x=kom_for_region,
                        y=lokasi_col,
                        orientation="h",
                        title=f"{n_region} Kab/Kota dengan Harga Terendah ({kom_for_region})",
                        template="plotly_white"
                    )
                    fig_bottom.update_traces(
                        hovertemplate="<b>%{y}</b><br>Rp %{x:,.0f}<extra></extra>",
                        marker_color="#4ade80"
                    )
                    fig_bottom.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="#111827", size=11)
                    )
                    st.plotly_chart(fig_bottom, use_container_width=True)

                st.markdown(
                    '<div class="caption-muted">'
                    "Bar chart merangkum kab/kota dengan harga rata-rata tertinggi dan terendah "
                    f"untuk komoditas {kom_for_region} pada periode analisis."
                    "</div>",
                    unsafe_allow_html=True
                )

                with st.expander("💡 Insight perbandingan wilayah"):
                    st.markdown(
                        """
- Beberapa kab/kota terpencil cenderung memiliki harga rata-rata lebih tinggi karena biaya logistik dan pasokan.
- Kab/kota sentra produksi agraris sering memiliki harga lebih rendah dan lebih stabil.
- Peta di atas menunjukkan pola spasial, sedangkan bar chart merangkum daftar kab/kota termurah dan termahal.
"""
                    )

    st.markdown('</div>', unsafe_allow_html=True)

# ==============================
# TAB 3 – KORELASI KOMODITAS
# ==============================
with tab3:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Korelasi Harga Antar Komoditas</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-caption">Identifikasi kelompok komoditas yang bergerak searah dan yang relatif independen.</div>',
        unsafe_allow_html=True
    )

    if wins.empty:
        st.warning("Dataset kosong.")
    else:
        st.markdown("#### Pilih Komoditas untuk Analisis Korelasi")

        # Checkbox "Pilih semua"
        pilih_semua = st.checkbox("Pilih semua komoditas", value=True)

        selected_corr = []

        if pilih_semua:
            selected_corr = komoditas_cols.copy()
        else:
            # Tampilkan checkbox per komoditas dalam beberapa kolom agar rapi
            n_cols = 3
            cols = st.columns(n_cols)

            for i, kom in enumerate(komoditas_cols):
                col = cols[i % n_cols]
                cek = col.checkbox(kom, value=False, key=f"corr_{kom}")
                if cek:
                    selected_corr.append(kom)

        if len(selected_corr) < 2:
            st.info("Centang minimal dua komoditas untuk melihat matriks korelasi.")
        else:
            corr = wins[selected_corr].corr()

            fig_corr = px.imshow(
                corr,
                text_auto=True,
                color_continuous_scale="RdBu_r",
                zmin=-1, zmax=1,
                labels=dict(color="Korelasi")
            )
            fig_corr.update_layout(
                template="plotly_white",
                height=650,
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#111827", size=11)
            )

            st.plotly_chart(fig_corr, use_container_width=True)

            with st.expander("💡 Insight korelasi harga antar komoditas"):
                st.markdown(
                    """
- Komoditas sejenis atau substitusi (misalnya berbagai jenis beras, tepung terigu, dan sesama cabai/bawang)
  cenderung memiliki korelasi positif tinggi dan bergerak searah.
- Komoditas dengan rantai pasok dan pola musiman berbeda menunjukkan korelasi rendah atau negatif,
  artinya kenaikan harga di satu komoditas tidak selalu diikuti komoditas lain.
- Informasi ini penting untuk mengidentifikasi kelompok komoditas yang perlu dipantau dan distabilisasi secara bersama-sama.
"""
                )

    st.markdown('</div>', unsafe_allow_html=True)
