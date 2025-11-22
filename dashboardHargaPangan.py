
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# CONFIG & TITLE
st.set_page_config(
    page_title="Dashboard Harga Pangan Nasional",
    layout="wide"
)

st.title("Dashboard Harga Pangan Konsumen di Indonesia")
st.caption(
    "Analisis pola, tren, dan perbandingan harga komoditas pangan utama "
    "di 505 Kabupaten/Kota Indonesia (Januari 2024 – Agustus 2025)"
)

# LOAD DATA
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

# Kelompok komoditas (dipakai di Tab Tren Nasional)
groups = {
    "Semua": komoditas_cols,
    "Beras": [c for c in komoditas_cols if "beras" in c.lower()],
    "Protein Hewani": [c for c in komoditas_cols if any(k in c.lower() for k in ["daging", "telur", "ikan"])],
    "Bumbu Dapur": [c for c in komoditas_cols if any(k in c.lower() for k in ["cabai", "cabe", "bawang"])],
    "Bahan Pokok Lain": [c for c in komoditas_cols if any(k in c.lower() for k in ["minyak", "gula", "tepung", "kedelai", "garam"])]
}

# TABS
tab1, tab2, tab3 = st.tabs([
    "📈 Tren Nasional",
    "🗺️ Perbandingan Wilayah",
    "🔗 Korelasi Komoditas"
])

# TAB 1 – TREN NASIONAL (Q1 & Q8)
with tab1:
    st.subheader("Perkembangan Rata-rata Harga Komoditas Pangan Nasional")
    
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
        st.markdown("### Tren Komoditas")

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
                height=500
            )
            st.plotly_chart(fig_trend, use_container_width=True)

        # Harga rata-rata nasional
        if selected_koms:
            title_tren_umum = "Rata-Rata Harga Pangan"
            monthly_avg_all = avg_trend[selected_koms].mean(axis=1)
        else:
            title_tren_umum = "Tren Umum Harga Pangan Nasional (Rata-rata Semua Komoditas)"
            monthly_avg_all = avg_trend[komoditas_cols].mean(axis=1)

        if len(monthly_avg_all) > 1:
            start_price = float(monthly_avg_all.iloc[0])
            end_price = float(monthly_avg_all.iloc[-1])
            growth_nominal = end_price - start_price
            growth_percent = (growth_nominal / start_price * 100) if start_price != 0 else 0.0

            st.markdown(f"### {title_tren_umum}")
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Harga awal", f"Rp {start_price:,.0f}")
            m2.metric("Harga akhir", f"Rp {end_price:,.0f}", f"{growth_nominal:,.0f}")
            m3.metric(
                "Pertumbuhan rata-rata",
                f"{growth_percent:.2f}%" +
                ("" if selected_koms else " (semua komoditas)")
            )
            st.caption(
                    "Menunjukkan rata-rata harga pangan pada komoditas dan periode yang dipilih."
                )

        with st.expander("Lihat insight tren nasional"):
            st.markdown("""
- Komoditas beras (premium, medium, SPHP) cenderung stabil dengan kenaikan bertahap.
- Cabai dan bawang menunjukkan lonjakan harga yang tajam dan berulang.
- Minyak goreng dan gula naik lebih pelan namun relatif konsisten.
- Secara agregat, rata-rata harga pangan nasional selama periode ini hanya naik tipis
  dan belum menunjukkan tren kenaikan tajam yang permanen.
""")

# TAB 2 – PERBANDINGAN WILAYAH (Q3 & Q4)
with tab2:
    st.subheader("Perbandingan Harga Antar Kabupaten/Kota")

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
            st.markdown("### Peta Sebaran Harga per Kabupaten/Kota")

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
                            height=500
                        )
                        fig_map.update_layout(
                            mapbox_style="open-street-map",
                            margin=dict(l=0, r=0, t=30, b=0)
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
                        marker_color="#F46D43"   # oranye-merah lembut
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
                        marker_color="#FEE08B"   # kuning lembut
                    )
                    st.plotly_chart(fig_bottom, use_container_width=True)

                st.caption(
                    "Bar chart ini menunjukkan kab/kota dengan harga rata-rata tertinggi dan terendah "
                    f"untuk komoditas {kom_for_region} pada periode yang dipilih."
                )

                with st.expander("Lihat insight perbandingan wilayah"):
                    st.markdown("""
- Beberapa kab/kota terpencil cenderung memiliki harga rata-rata lebih tinggi karena biaya logistik dan pasokan.
- Kab/kota sentra produksi agraris sering memiliki harga lebih rendah dan lebih stabil.
- Peta di atas menunjukkan pola spasial, sedangkan bar chart merangkum daftar kab/kota termurah dan termahal.
""")

# TAB 3 – KORELASI KOMODITAS (Q5)
with tab3:
    st.subheader("Korelasi Harga Antar Komoditas")
    
    if wins.empty:
        st.warning("Dataset kosong.")
    else:
        st.markdown("### Pilih Komoditas untuk Analisis Korelasi")

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
                height=700
            )

            st.plotly_chart(fig_corr, use_container_width=True)

            with st.expander("Lihat insight korelasi harga antar komoditas"):
                st.markdown("""
- Komoditas sejenis atau substitusi (misalnya berbagai jenis beras, tepung terigu, dan sesama cabai/bawang)
  cenderung memiliki korelasi positif tinggi dan bergerak searah.
- Komoditas dengan rantai pasok dan pola musiman berbeda menunjukkan korelasi rendah atau negatif,
  artinya kenaikan harga di satu komoditas tidak selalu diikuti komoditas lain.
- Informasi ini penting untuk mengidentifikasi kelompok komoditas yang perlu dipantau dan distabilisasi secara bersama-sama.
""")
