import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

# ---------------------------------------------------------------- KONFIGURASI
st.set_page_config(page_title="Dashboard Bike Sharing", page_icon="🚲", layout="wide")
sns.set_theme(style="whitegrid")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

URUTAN_MUSIM = ["Dingin", "Semi", "Panas", "Gugur"]
URUTAN_CUACA = ["Cerah", "Berkabut/Berawan", "Hujan/Salju Ringan", "Hujan/Salju Lebat"]
URUTAN_WAKTU = ["Dini Hari (00-05)", "Pagi (06-09)", "Siang (10-15)", "Sore (16-19)", "Malam (20-23)"]
LABEL_SUHU = ["Dingin (<0.3)", "Sejuk (0.3-0.5)", "Hangat (0.5-0.7)", "Panas (>0.7)"]
NAMA_BULAN = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]

BIRU = "#1565C0"
BIRU_MUDA = "#90CAF9"
ORANYE = "#EF6C00"
WARNA_TIPE_HARI = {"Hari Kerja": BIRU, "Akhir Pekan/Libur": ORANYE}


# ---------------------------------------------------------------- DATA
@st.cache_data
def load_data():
    day = pd.read_csv(os.path.join(BASE_DIR, "main_data.csv"), parse_dates=["date"])
    hour = pd.read_csv(os.path.join(BASE_DIR, "hour_data.csv"), parse_dates=["date"])
    return day, hour


day_df, hour_df = load_data()

# ---------------------------------------------------------------- SIDEBAR (FILTER)
st.sidebar.header("Filter Data")

tgl_min = day_df["date"].min().date()
tgl_max = day_df["date"].max().date()
rentang = st.sidebar.date_input(
    "Rentang tanggal", value=(tgl_min, tgl_max), min_value=tgl_min, max_value=tgl_max
)
musim_dipilih = st.sidebar.multiselect("Musim", URUTAN_MUSIM, default=URUTAN_MUSIM)

if not (isinstance(rentang, (tuple, list)) and len(rentang) == 2):
    st.sidebar.info("Pilih tanggal awal dan tanggal akhir pada kalender.")
    st.stop()

mulai, selesai = pd.Timestamp(rentang[0]), pd.Timestamp(rentang[1])

day = day_df[day_df["date"].between(mulai, selesai) & day_df["season"].isin(musim_dipilih)].copy()
hour = hour_df[hour_df["date"].between(mulai, selesai) & hour_df["season"].isin(musim_dipilih)].copy()

st.title("🚲 Dashboard Analisis Penyewaan Sepeda")
st.caption("Bike Sharing Dataset, periode 2011-2012. Gunakan filter di sidebar untuk mengubah rentang tanggal dan musim.")

if day.empty or hour.empty:
    st.warning("Tidak ada data untuk filter yang dipilih. Ubah rentang tanggal atau musim.")
    st.stop()

# ---------------------------------------------------------------- RINGKASAN
total_sewa = int(day["total"].sum())
rata_harian = day["total"].mean()
porsi_registered = day["registered"].sum() / day["total"].sum() * 100

kol1, kol2, kol3, kol4 = st.columns(4)
kol1.metric("Total penyewaan", f"{total_sewa:,}")
kol2.metric("Rata-rata per hari", f"{rata_harian:,.0f}")
kol3.metric("Porsi pengguna registered", f"{porsi_registered:.1f}%")
kol4.metric("Jumlah hari", f"{len(day):,}")

tab1, tab2, tab3, tab4 = st.tabs(
    ["Tren & Musim", "Pola Jam", "Cuaca & Suhu", "Analisis Lanjutan"]
)

# ---------------------------------------------------------------- TAB 1: TREN & MUSIM
with tab1:
    st.subheader("Bagaimana tren penyewaan bulanan dan pengaruh musim?")

    bulanan = day.groupby(["year", "month"])["total"].sum().reset_index()
    rata_musim = day.groupby("season")["total"].mean().reindex(URUTAN_MUSIM).dropna()

    kiri, kanan = st.columns(2)

    with kiri:
        fig, ax = plt.subplots(figsize=(8, 4.5))
        palet = {2011: BIRU_MUDA, 2012: BIRU}
        for tahun, grup in bulanan.groupby("year"):
            ax.plot(grup["month"], grup["total"], marker="o", label=str(tahun), color=palet.get(tahun))
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels(NAMA_BULAN)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:,.0f}"))
        ax.set_title("Total Penyewaan per Bulan")
        ax.set_xlabel("Bulan")
        ax.set_ylabel("Total penyewaan")
        ax.legend(title="Tahun")
        st.pyplot(fig)
        plt.close(fig)

    with kanan:
        fig, ax = plt.subplots(figsize=(8, 4.5))
        warna = [BIRU if v == rata_musim.max() else BIRU_MUDA for v in rata_musim]
        batang = ax.bar(rata_musim.index, rata_musim.values, color=warna)
        ax.bar_label(batang, fmt="%.0f", padding=3)
        ax.set_ylim(0, rata_musim.max() * 1.12)
        ax.set_title("Rata-rata Penyewaan Harian per Musim")
        ax.set_xlabel("Musim")
        ax.set_ylabel("Rata-rata penyewaan per hari")
        st.pyplot(fig)
        plt.close(fig)

    bulan_max = bulanan.loc[bulanan["total"].idxmax()]
    teks = (
        f"Bulan dengan penyewaan tertinggi pada filter ini adalah "
        f"**{NAMA_BULAN[int(bulan_max['month']) - 1]} {int(bulan_max['year'])}** "
        f"({int(bulan_max['total']):,} penyewaan). "
        f"Musim dengan rata-rata harian tertinggi adalah **{rata_musim.idxmax()}** "
        f"({rata_musim.max():,.0f} per hari)."
    )
    total_tahun = day.groupby("year")["total"].sum()
    if {2011, 2012}.issubset(total_tahun.index):
        teks += (
            f" Total penyewaan 2012 berbeda **{(total_tahun[2012] / total_tahun[2011] - 1) * 100:+.1f}%** "
            f"dibanding 2011 pada filter ini."
        )
    st.info(teks)

# ---------------------------------------------------------------- TAB 2: POLA JAM
with tab2:
    st.subheader("Pada jam berapa puncak penyewaan terjadi?")

    pola_jam = hour.groupby(["day_type", "hour"])["total"].mean().reset_index()
    pola_pengguna = hour.groupby("hour")[["casual", "registered"]].mean()

    kiri, kanan = st.columns(2)

    with kiri:
        fig, ax = plt.subplots(figsize=(8, 4.5))
        for tipe, warna in WARNA_TIPE_HARI.items():
            grup = pola_jam[pola_jam["day_type"] == tipe]
            if grup.empty:
                continue
            ax.plot(grup["hour"], grup["total"], marker="o", label=tipe, color=warna)
        ax.set_xticks(range(0, 24, 2))
        ax.set_title("Rata-rata Penyewaan per Jam")
        ax.set_xlabel("Jam")
        ax.set_ylabel("Rata-rata penyewaan per jam")
        ax.legend()
        st.pyplot(fig)
        plt.close(fig)

    with kanan:
        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.plot(pola_pengguna.index, pola_pengguna["registered"], marker="o", color=BIRU, label="Registered")
        ax.plot(pola_pengguna.index, pola_pengguna["casual"], marker="o", color=ORANYE, label="Casual")
        ax.set_xticks(range(0, 24, 2))
        ax.set_title("Casual vs Registered per Jam")
        ax.set_xlabel("Jam")
        ax.set_ylabel("Rata-rata penyewaan per jam")
        ax.legend()
        st.pyplot(fig)
        plt.close(fig)

    baris = []
    for tipe, grup in pola_jam.groupby("day_type"):
        top = grup.loc[grup["total"].idxmax()]
        baris.append(f"- **{tipe}**: puncak pukul **{int(top['hour']):02d}:00** (rata-rata {top['total']:.0f} sewa/jam)")
    puncak_reg = pola_pengguna["registered"].idxmax()
    puncak_cas = pola_pengguna["casual"].idxmax()
    baris.append(f"- **Registered** memuncak pukul {puncak_reg:02d}:00, **casual** memuncak pukul {puncak_cas:02d}:00")
    st.info("\n".join(baris))

# ---------------------------------------------------------------- TAB 3: CUACA & SUHU
with tab3:
    st.subheader("Bagaimana cuaca dan suhu memengaruhi penyewaan?")

    rata_cuaca = day.groupby("weather")["total"].agg(["mean", "count"]).reindex(URUTAN_CUACA).dropna()

    kiri, kanan = st.columns(2)

    with kiri:
        fig, ax = plt.subplots(figsize=(8, 4.5))
        warna = [BIRU if v == rata_cuaca["mean"].max() else BIRU_MUDA for v in rata_cuaca["mean"]]
        batang = ax.bar(rata_cuaca.index, rata_cuaca["mean"], color=warna)
        ax.bar_label(
            batang,
            labels=[f"{m:.0f}\n(n={int(n)} hari)" for m, n in zip(rata_cuaca["mean"], rata_cuaca["count"])],
            padding=3,
        )
        ax.set_ylim(0, rata_cuaca["mean"].max() * 1.2)
        ax.set_title("Rata-rata Penyewaan Harian per Kondisi Cuaca")
        ax.set_xlabel("Kondisi cuaca")
        ax.set_ylabel("Rata-rata penyewaan per hari")
        st.pyplot(fig)
        plt.close(fig)

    with kanan:
        fig, ax = plt.subplots(figsize=(8, 4.5))
        sns.regplot(
            data=day, x="temp", y="total",
            scatter_kws={"alpha": 0.4, "color": BIRU}, line_kws={"color": "#D32F2F"}, ax=ax,
        )
        ax.set_title("Suhu (ternormalisasi) vs Total Penyewaan Harian")
        ax.set_xlabel("Suhu (ternormalisasi 0-1)")
        ax.set_ylabel("Total penyewaan per hari")
        st.pyplot(fig)
        plt.close(fig)

    teks = ""
    if "Cerah" in rata_cuaca.index and len(rata_cuaca) > 1:
        cerah = rata_cuaca.loc["Cerah", "mean"]
        for kondisi in rata_cuaca.index:
            if kondisi != "Cerah":
                selisih = (rata_cuaca.loc[kondisi, "mean"] / cerah - 1) * 100
                teks += f"- Dibanding hari Cerah, rata-rata penyewaan saat **{kondisi}** berbeda **{selisih:+.1f}%**\n"
    korelasi = day["temp"].corr(day["total"])
    if pd.notna(korelasi):
        teks += f"- Korelasi suhu dengan total penyewaan harian: **{korelasi:.2f}**"
    if teks:
        st.info(teks)

# ---------------------------------------------------------------- TAB 4: ANALISIS LANJUTAN
with tab4:
    st.subheader("Binning: periode waktu dan kategori suhu")

    hour["time_group"] = pd.cut(
        hour["hour"], bins=[-1, 5, 9, 15, 19, 23], labels=URUTAN_WAKTU
    )
    porsi_waktu = (
        pd.crosstab(hour["time_group"], hour["day_type"], values=hour["total"],
                    aggfunc="sum", normalize="columns") * 100
    )
    day["temp_group"] = pd.cut(day["temp"], bins=[0, 0.3, 0.5, 0.7, 1.0], labels=LABEL_SUHU, include_lowest=True)
    rata_suhu = day.groupby("temp_group", observed=True)["total"].agg(["mean", "count"])

    kiri, kanan = st.columns(2)

    with kiri:
        fig, ax = plt.subplots(figsize=(8, 4.5))
        warna_kolom = [WARNA_TIPE_HARI[c] for c in porsi_waktu.columns]
        porsi_waktu.plot(kind="bar", ax=ax, color=warna_kolom, rot=15)
        for kontainer in ax.containers:
            ax.bar_label(kontainer, fmt="%.1f%%", padding=2, fontsize=8)
        ax.set_title("Porsi Penyewaan per Periode Waktu")
        ax.set_xlabel("Periode waktu")
        ax.set_ylabel("Porsi total penyewaan (%)")
        ax.legend(title="Jenis hari")
        st.pyplot(fig)
        plt.close(fig)

    with kanan:
        fig, ax = plt.subplots(figsize=(8, 4.5))
        batang = ax.bar(rata_suhu.index.astype(str), rata_suhu["mean"], color=BIRU)
        ax.bar_label(
            batang,
            labels=[f"{m:.0f}\n(n={int(n)} hari)" for m, n in zip(rata_suhu["mean"], rata_suhu["count"])],
            padding=3,
        )
        ax.set_ylim(0, rata_suhu["mean"].max() * 1.2)
        ax.set_title("Rata-rata Penyewaan Harian per Kategori Suhu")
        ax.set_xlabel("Kategori suhu (ternormalisasi)")
        ax.set_ylabel("Rata-rata penyewaan per hari")
        st.pyplot(fig)
        plt.close(fig)

    st.caption("Batas kategori suhu ditentukan manual pada skala ternormalisasi (0-1); n = jumlah hari pada tiap kategori.")

    with st.expander("Lihat data harian (day)"):
        st.dataframe(day.drop(columns=["temp_group"]))
