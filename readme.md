# 📡 SmartCount - IoT RFID Attendance System

**SmartCount** adalah sistem absensi perkuliahan otomatis yang mengintegrasikan Hardware (ESP32 + RFID), Backend Server (Flask), dan Dashboard Monitoring (Home Assistant).

Sistem ini memungkinkan mahasiswa melakukan absensi hanya dengan menempelkan KTP/KTM, sementara Dosen dapat memantau kehadiran secara _real-time_ melalui dashboard yang interaktif.

![Status](https://img.shields.io/badge/Status-Active-success) ![Docker](https://img.shields.io/badge/Docker-Compose-blue) ![Python](https://img.shields.io/badge/Python-3.10-yellow) ![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Dashboard-blue)

---

## ✨ Fitur Utama

- **Real-time Scanning:** Data kartu RFID dikirim detik itu juga ke server via MQTT.
- **Dual Mode Session:**
  - **Auto:** Absensi terbuka otomatis sesuai jadwal mata kuliah (Hari & Jam).
  - **Manual:** Dosen bisa membuka sesi darurat/demo melalui tombol di Dashboard.
- **Anti-Fraud:** Mencegah satu mahasiswa absen 2x dalam satu sesi pertemuan.
- **Manajemen User:** Pendaftaran kartu RFID baru (Link ke NIM & Nama) langsung dari Dashboard.
- **Dashboard Otomatis:** Tampilan UI Home Assistant langsung ter-load tanpa perlu setup manual.

---

## 📂 Struktur Project

```text
SMARTCOUNT/
├── docker-compose.yaml    # Resep utama menjalankan server
├── backend/               # Logika Server Python
│   ├── app.py             # API & MQTT Handler
│   ├── Dockerfile         # Konfigurasi Container Backend
│   ├── models.sql         # Struktur Database
│   └── requirements.txt   # Library Python
├── homeassistant/         # Konfigurasi Dashboard
│   ├── configuration.yaml # Integrasi Sensor
│   ├── automations.yaml   # Logika Otomatisasi
│   └── ui-lovelace.yaml   # Desain Tampilan Dashboard
└── hardware/              # Kode Mikrokontroler
    └── UAS_IOT.ino        # Kode untuk ESP32
```

---

## 🚀 Panduan Instalasi (Dari Awal)

Ikuti langkah ini jika Anda baru saja menginstall Docker dan belum pernah menjalankan project ini.

### 1\. Persiapan (Prerequisites)

Pastikan komputer Anda sudah terinstall:

- [Git](https://git-scm.com/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Pastikan statusnya _Running_)
- Driver USB untuk ESP32 (CP210x atau CH340)

### 2\. Clone Repository

Buka terminal (CMD/PowerShell) dan jalankan:

```bash
git clone [https://github.com/USERNAME-ANDA/NAMA-REPO.git](https://github.com/USERNAME-ANDA/NAMA-REPO.git)
cd NAMA-REPO
```

### 3\. Setup Hardware (ESP32)

Sebelum menjalankan server, siapkan alatnya dulu.

1.  Buka folder `hardware/` dan buka file `UAS_IOT.ino` menggunakan Arduino IDE.
2.  Edit bagian ini sesuai WiFi Anda:
    ```cpp
    const char* WIFI_SSID     = "NAMA_WIFI_ANDA";
    const char* WIFI_PASSWORD = "PASSWORD_WIFI_ANDA";
    ```
3.  Upload kode ke ESP32.
4.  Pastikan di Serial Monitor muncul tulisan: `WiFi terhubung` dan `RFID siap`.

### 4\. Jalankan Server (Docker)

Ini adalah langkah utama. Docker akan otomatis mendownload Python, Home Assistant, dan menyiapkan database.

Di terminal (pastikan berada di folder project), jalankan:

```bash
docker-compose up -d --build
```

- **Tunggu prosesnya.** Docker akan mendownload image (sekitar 1-2 GB untuk pertama kali).
- Jika selesai, akan muncul status `Started` untuk `smartcount_backend` dan `homeassistant`.

### 5\. Akses Dashboard

1.  Buka browser dan akses: `http://localhost:8123`
2.  **Buat Akun:** Karena ini instalasi baru, Home Assistant akan meminta Anda membuat Username & Password. (Bebas, misal: User/Admin).
3.  **Selesai\!** Dashboard SmartCount akan langsung muncul di depan Anda.

> **Catatan:** Jika dashboard terlihat kosong/error saat pertama kali dibuka, coba refresh browser Anda. Home Assistant sedang membaca file `ui-lovelace.yaml`.

---

## 📖 Cara Menggunakan Sistem

### A. Mendaftarkan Mahasiswa Baru

1.  Pastikan alat ESP32 menyala.
2.  Tempelkan kartu KTP/RFID baru ke alat.
3.  Lihat dashboard, UID kartu akan muncul di kotak **"Monitoring RFID"**.
4.  Isi kolom **NIM Mahasiswa** dan **Nama Mahasiswa**.
5.  Klik tombol **"DAFTARKAN RFID"**.
6.  Cek status di panel "Status Registrasi".

### B. Memulai Absensi (Mode Manual)

1.  Pada panel **Kontrol Dosen**, pilih Mata Kuliah di dropdown.
2.  Klik tombol **BUKA ABSENSI**.
3.  Lampu indikator "Status Absensi" akan berubah menjadi **AKTIF**.
4.  Mahasiswa menempelkan kartu. Jika terdaftar, nama mereka muncul di daftar hadir.
5.  Klik **TUTUP ABSENSI** jika kelas selesai.

### C. Mode Otomatis

Sistem backend mengecek waktu server setiap menit. Jika waktu sekarang cocok dengan jadwal di database (`models.sql`), sesi akan terbuka otomatis tanpa perlu menekan tombol apapun.

---

## 🛠️ Troubleshooting

**1. Data RFID tidak masuk ke Dashboard?**

- Cek koneksi internet ESP32 (harus konek ke WiFi yang ada internetnya).
- Pastikan Docker Backend berjalan (`docker ps` di terminal).
- Cek apakah MQTT Broker (`broker.hivemq.com`) sedang down (jarang terjadi).

**2. Dashboard Home Assistant tidak bisa diedit?**

- Ini fitur keamanan. Dashboard dikunci dalam mode `YAML` agar tampilan selalu konsisten sesuai file `ui-lovelace.yaml`.
- Jika ingin mengedit, editlah file `homeassistant/ui-lovelace.yaml` di VS Code, lalu refresh browser.

**3. Error "Database Locked" atau data tidak tersimpan?**

- Pastikan file `backend/smartcount.db` tidak sedang dibuka oleh aplikasi lain (seperti DB Browser for SQLite) saat server Docker berjalan.

---

## 📝 Credits

Dibuat untuk memenuhi Tugas Akhir Mata Kuliah IoT & Integrasi Sistem.
