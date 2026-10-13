# Proyek Analisis Data: Bike Sharing Dataset

Analisis data penyewaan sepeda (2011-2012) menggunakan data harian (`day.csv`) dan per jam (`hour.csv`), beserta dashboard interaktif dengan Streamlit.

## Pertanyaan Bisnis
1. Bagaimana tren total penyewaan sepeda per bulan, musim apa yang memiliki rata-rata penyewaan harian tertinggi dan terendah, dan berapa pertumbuhan 2012 dibanding 2011?
2. Pada jam berapa puncak penyewaan terjadi pada hari kerja dibanding akhir pekan/libur, dan apa perbedaan pola pengguna *casual* dan *registered*?
3. Bagaimana pengaruh kondisi cuaca dan suhu terhadap rata-rata penyewaan harian?

## Struktur Direktori
```
submission
├── dashboard
│   ├── main_data.csv      # data harian yang sudah dibersihkan (dibuat oleh notebook)
│   ├── hour_data.csv      # data per jam yang sudah dibersihkan (dibuat oleh notebook)
│   └── dashboard.py       # aplikasi dashboard Streamlit
├── data
│   ├── day.csv            # data mentah harian
│   └── hour.csv           # data mentah per jam
├── notebook.ipynb         # proses analisis data
├── README.md
├── requirements.txt
└── url.txt                # tautan dashboard yang sudah di-deploy
```

## Setup Environment
Disarankan memakai Python 3.9 atau lebih baru.

```
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
```

## Menjalankan Notebook
Jalankan `notebook.ipynb` dari folder `submission` (agar file `data/day.csv` dan `data/hour.csv` terbaca). Sel "Menyimpan data bersih untuk dashboard" akan membuat ulang `dashboard/main_data.csv` dan `dashboard/hour_data.csv`.

Jika dijalankan di Google Colab, unggah `day.csv` dan `hour.csv` ke panel Files (atau ke folder `data/`).

## Menjalankan Dashboard
Dari folder `submission`:

```
streamlit run dashboard/dashboard.py
```

Dashboard memiliki filter rentang tanggal dan musim, serta empat tab: Tren & Musim, Pola Jam, Cuaca & Suhu, dan Analisis Lanjutan.

## Deploy ke Streamlit Community Cloud
1. Unggah folder `submission` ke repository GitHub.
2. Buka https://share.streamlit.io, pilih repository tersebut, lalu isi *Main file path* dengan `dashboard/dashboard.py`.
3. Salin URL aplikasi yang dihasilkan ke dalam `url.txt`.
