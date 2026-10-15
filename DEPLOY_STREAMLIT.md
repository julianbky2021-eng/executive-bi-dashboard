# Menjalankan dan hosting dashboard

## Jalankan di komputer sendiri

Di PowerShell, dari folder proyek:

```powershell
cd D:\julian_website
py -m pip install -r requirements.txt
py -m streamlit run streamlit_app.py
```

Streamlit akan menampilkan alamat lokal, biasanya `http://localhost:8501`.

## Hosting gratis di Streamlit Community Cloud

1. Buat atau masuk ke akun GitHub, lalu buat repository baru. Untuk data contoh ini, repository publik paling sederhana.
2. Unggah file `streamlit_app.py`, `requirements.txt`, `latihan1.js`, dan folder `.streamlit` beserta `config.toml` ke root repository. Jangan pilih `app.py` Flask sebagai entrypoint.
3. Masuk ke [share.streamlit.io](https://share.streamlit.io/) dan hubungkan akun GitHub.
4. Pilih **Create app**, lalu pilih repository, branch (umumnya `main`), dan file utama `streamlit_app.py`.
5. Tekan **Deploy**. Setelah proses build selesai, Streamlit memberikan alamat publik berakhiran `streamlit.app`.
6. Untuk memperbarui website, unggah perubahan ke GitHub. Community Cloud akan membangun ulang aplikasi dari repository.

Jika repository ingin dikirim lewat Git dari PowerShell, buat repository GitHub kosong terlebih dahulu, lalu jalankan perintah berikut dari folder proyek (ganti URL contoh dengan URL repository Anda):

```powershell
git init
git add .gitignore README.md streamlit_app.py requirements.txt latihan1.js convert_data.py DEPLOY_STREAMLIT.md .streamlit/config.toml
git commit -m "Add Streamlit BI dashboard"
git branch -M main
git remote add origin https://github.com/USERNAME/NAMA-REPO.git
git push -u origin main
```

Dashboard ini hanya menggunakan data contoh yang ikut tersimpan di repository; belum ada kredensial rahasia atau database eksternal yang perlu diatur.

## Catatan tentang format data

`latihan1.js` adalah berkas JavaScript valid yang menetapkan `globalThis.LATIHAN1_DATA`. Nilainya memakai object literal dengan sintaks JSON yang ketat; Streamlit mengambil literal tersebut dan membacanya dengan Python tanpa mengeksekusi JavaScript. CSV asli disimpan sebagai sumber. Untuk memperbarui berkas JS setelah CSV berubah, jalankan `py convert_data.py`. Object literal memerlukan tanda kutip dan pemisah tambahan, jadi format `.js` tidak selalu lebih kecil daripada CSV; gunakan CSV sebagai sumber jika ukuran file adalah satu-satunya pertimbangan.
