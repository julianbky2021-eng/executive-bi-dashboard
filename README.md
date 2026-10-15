# Executive BI Dashboard

Dashboard analitik siswa berbasis Streamlit dengan simulator nilai OLS, KPI, radar profil gender, ranking korelasi, scatter plot, heatmap korelasi, filter, tabel pencarian, dan ekspor CSV.

## Jalankan lokal

```powershell
py -m pip install -r requirements.txt
py -m streamlit run streamlit_app.py
```

Buka alamat lokal yang ditampilkan Streamlit, biasanya `http://localhost:8501`.

## Data

`latihan1.js` memuat dataset latihan fiktif. Jika sumber `latihan1.csv` diperbarui, jalankan `py convert_data.py` untuk membuat ulang berkas JS.

## Deploy

Deploy di [Streamlit Community Cloud](https://share.streamlit.io/) dengan entrypoint `streamlit_app.py`. Lihat [panduan deploy](DEPLOY_STREAMLIT.md) untuk langkah lengkap.
