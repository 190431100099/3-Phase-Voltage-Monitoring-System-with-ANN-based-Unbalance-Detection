Berikut adalah teks untuk file `README.md` yang siap Anda gunakan untuk repositori GitHub Anda. Teks ini disusun secara profesional dan mencakup deskripsi, fitur, cara instalasi, serta panduan penggunaan berdasarkan kode yang telah kita buat.

# Sistem Monitoring Tegangan 3 Fasa dengan Deteksi Unbalance berbasis ANN

Proyek ini adalah aplikasi desktop berbasis Python yang dirancang untuk memantau tegangan dan arus 3 fasa secara *real-time*. Sistem ini menggunakan Arduino untuk pengambilan data sensor dan Komputer untuk pemrosesan data menggunakan Jaringan Saraf Tiruan (Artificial Neural Network/ANN) untuk mendeteksi kondisi "Balance" atau "Unbalance".

## ✨ Fitur Utama

- **Monitoring Real-time:** Membaca data tegangan (R, S, T) dan Arus (R, S, T) secara *live* melalui komunikasi serial.
- **Visualisasi Grafik:** Menampilkan plot dinamis untuk setiap fasa serta grafik gabungan menggunakan `pyqtgraph`.
- **Klasifikasi AI:** Menggunakan model ANN (TensorFlow/Keras) untuk memprediksi kondisi sistem.
- **Confidence Score:** Menampilkan tingkat kepercayaan (confidence) dari hasil prediksi model.
- **Ambang Batas Dinamis:** Dataset dilatih dengan logika deteksi unbalance tegangan > 2% (range 230V-245V) dan arus > 2%.
- **Ekspor Data:** Fitur menyimpan riwayat data monitoring ke dalam file Excel (.xlsx).
- **Feedback Hardware:** Mengirimkan status prediksi kembali ke Arduino (untuk indikator hardware).

## 🛠️ Teknologi yang Digunakan

- **Bahasa Pemrograman:** Python 3.x
- **GUI Framework:** PySide6 (Qt for Python)
- **Plotting:** PyQtGraph
- **Machine Learning:** TensorFlow / Keras, Scikit-Learn
- **Manipulasi Data:** Pandas, NumPy
- **Komunikasi Serial:** PySerial

## 📁 Struktur File

- `main.py`: Skrip utama aplikasi GUI dan logika serial.
- `ui_main.py`: File definisi antarmuka pengguna (hasil konversi Qt Designer).
- `buat_dataset.py`: Skrip untuk menghasilkan dataset sintetis untuk pelatihan.
- `olah_data_training.py`: Skrip untuk melatih model ANN dan menyimpan scaler.
- `model_ann.h5`: File model ANN yang telah dilatih (dihasilkan dari `olah_data_training.py`).
- `scaler.pkl`: File scaler untuk normalisasi data input (dihasilkan dari `olah_data_training.py`).

## ⚙️ Instalasi

1. **Clone Repositori**
   ```bash
   git clone https://github.com/username/nama-repo.git
   cd nama-repo
   ```

2. **Buat Virtual Environment (Opsional namun Disarankan)**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install Dependencies**
   Pastikan Anda memiliki library yang dibutuhkan. Buat file `requirements.txt` atau install manual:
   ```bash
   pip install PySide6 pyqtgraph numpy pandas scikit-learn tensorflow pyserial joblib openpyxl
   ```

## 🚀 Cara Penggunaan

### 1. Persiapan Model (Training)
Sebelum menjalankan aplikasi utama, Anda perlu melatih model AI.

- Jalankan skrip pembuatan dataset:
  ```bash
  python buat_dataset.py
  ```
  *(Ini akan menghasilkan file `dataset_tegangan_balance_unbalance.csv` dengan range tegangan 230V-245V)*.

- Jalankan skrip training model:
  ```bash
  python olah_data_training.py
  ```
  *(Ini akan menghasilkan file `model_ann.h5` dan `scaler.pkl`)*.

### 2. Menjalankan Aplikasi
- Hubungkan perangkat Arduino ke port USB komputer.
- Jalankan aplikasi utama:
  ```bash
  python main.py
  ```

### 3. Alur Kerja Aplikasi
1. **Pilih Port:** Pilih port COM yang terhubung ke Arduino pada dropdown.
2. **Start:** Klik tombol `Start` untuk memulai koneksi serial. Data akan mulai mengalir dan grafik akan bergerak.
3. **Monitoring:** Amati nilai tegangan, arus, dan status prediksi (BALANCE/UNBALANCE) di layar.
4. **Export:** Klik tombol `Export` untuk menyimpan data yang telah terekam ke dalam file Excel.
5. **Stop:** Klik tombol `Stop` untuk memutus koneksi serial.

## 📊 Logika Dataset
Model dilatih untuk mengenali ketidakseimbangan dengan kriteria:
- **Tegangan:** Range 230V - 245V.
- **Status UNBALANCE (Label 1):** Jika deviasi tegangan > 2% ATAU deviasi arus > 2%.
- **Status BALANCE (Label 0):** Jika deviasi di bawah ambang batas tersebut.

## 🤝 Kontribusi
Kontribusi sangat terbuka. Jika Anda menemukan bug atau ingin menambahkan fitur, silakan buat *Pull Request* atau buka *Issue*.

## 📝 Lisensi
Proyek ini berada di bawah lisensi MIT License.
```

### Tips Tambahan:
Anda bisa membuat file `requirements.txt` agar pengguna lain mudah menginstall library dengan perintah:
```text
PySide6
pyqtgraph
numpy
pandas
scikit-learn
tensorflow
pyserial
joblib
openpyxl
```
Simpan file di atas dengan nama `requirements.txt` di folder yang sama, lalu tambahkan instruksi `pip install -r requirements.txt` di bagian instalasi README.
