# Smart Flood Warning 3D

Proyek prototipe Smart Flood Warning dengan visualisasi 3D interaktif berbasis web. Proyek ini dirancang untuk menggambarkan sistem pemantauan ketinggian air dan peringatan dini banjir melalui model 3D serta simulasi perubahan kondisi air.

## Deskripsi Proyek

Smart Flood Warning 3D merupakan prototipe visualisasi sistem peringatan dini banjir yang menampilkan komponen seperti sensor ketinggian air, sensor ultrasonik, sensor hujan, LED indikator, buzzer, dan kotak kontrol.

Model 3D dibuat menggunakan script Python dan diekspor ke format GLB. Model tersebut kemudian ditampilkan pada halaman web menggunakan Three.js sehingga pengguna dapat melihat model, memutar sudut pandang, memilih komponen, dan mencoba simulasi perubahan level air.

**Catatan:** Versi saat ini berfokus pada visualisasi 3D dan simulasi. Pembacaan sensor fisik ESP32 serta pengiriman data secara langsung ke website belum terintegrasi.

## Fitur

- Visualisasi model 3D sistem Smart Flood Warning.
- Interaksi dengan komponen melalui klik pada model.
- Kontrol sudut pandang dan rotasi model 3D.
- Simulasi perubahan ketinggian air.
- Indikator status AMAN, WASPADA, dan BAHAYA.
- Animasi visual LED, sensor ultrasonik, buzzer, dan komponen tertentu.
- Model 3D dalam format GLB yang dihasilkan melalui script Python.

## Teknologi yang Digunakan

- HTML — struktur halaman web.
- CSS — tampilan dan tata letak antarmuka.
- JavaScript — logika interaksi dan simulasi.
- Three.js — rendering dan visualisasi 3D di browser.
- Python — pembuatan model 3D secara prosedural.
- GLB — format file model 3D.

## Struktur Proyek

```text
smart-flood-warning-3d/
├── index.html
├── viewer.js
├── smart_flood.glb
├── build_model.py
└── README.md
```

Sesuaikan nama `build_model.py` dengan nama script Python yang digunakan pada proyek sebenarnya. Jika terdapat file CSS atau folder aset lain, tambahkan juga ke struktur repository.

## Cara Menjalankan

1. Clone repository:

   ```bash
   git clone https://github.com/USERNAME/smart-flood-warning-3d.git
   ```

2. Masuk ke folder proyek:

   ```bash
   cd smart-flood-warning-3d
   ```

3. Jalankan proyek menggunakan local web server, misalnya melalui ekstensi Live Server di Visual Studio Code.

4. Buka alamat lokal yang diberikan oleh Live Server di browser.

5. Pastikan file `smart_flood.glb` tersedia di lokasi yang sesuai dengan path yang digunakan pada kode JavaScript.

## Generate Model 3D

Model 3D dapat dibuat ulang dengan menjalankan script Python di terminal pada folder/direktori proyek.

Contoh perintah:

```bash
python -m http.server 8000
```

Ganti nama file script sesuai nama yang digunakan pada proyek. Pastikan hasil ekspor `smart_flood.glb` tersimpan di lokasi yang benar.

## Pengembangan Selanjutnya

- Integrasi ESP32 dengan sensor ketinggian air dan sensor hujan.
- Pengiriman data sensor secara real-time ke website.
- Pembaruan status banjir berdasarkan data sensor aktual.
- Integrasi sistem notifikasi melalui LED dan buzzer fisik.
- Pengembangan analisis atau prediksi risiko banjir berbasis AI.

## Status Proyek

Prototipe visualisasi 3D dan simulasi antarmuka sedang dikembangkan. Integrasi perangkat IoT secara langsung merupakan pengembangan lanjutan.

## Lisensi

Proyek ini dibuat untuk keperluan pembelajaran dan pengembangan prototipe. Ketentuan penggunaan aset atau library pihak ketiga mengikuti lisensi masing-masing.
