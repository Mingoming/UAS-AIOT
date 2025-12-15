# 📡 SmartCount - IoT Audit System

SmartCount adalah sistem absensi cerdas yang mengintegrasikan RFID (IoT) untuk pencatatan kehadiran dan Computer Vision (AI) untuk audit integritas data guna mencegah kecurangan (titip absen).

![Status](https://img.shields.io/badge/Status-Active-success)
![Architecture](https://img.shields.io/badge/Architecture-Hybrid-blue)
![Python](https://img.shields.io/badge/Python-3.11-yellow)
![Docker](https://img.shields.io/badge/Docker-Compose-blue)

---

## 🏛️ Arsitektur Sistem

SmartCount menggunakan arsitektur Hybrid yang menghubungkan layanan berbasis container dengan perangkat keras fisik.

### 1. Server Pusat (Docker)

- Backend: API Server (Flask) dan Database SQLite untuk manajemen data absensi
- Dashboard: Home Assistant untuk monitoring real-time dan antarmuka pengguna

### 2. Node Kamera (Laptop/PC – Windows Native)

- Menjalankan script Python berbasis YOLOv8
- Menghitung jumlah orang di ruangan secara visual
- Menyediakan streaming video ke Dashboard

### 3. Node Sensor (Hardware)

- ESP32 + RFID Reader RC522
- Membaca UID kartu RFID
- Mengirim data ke server melalui MQTT

---

## 📂 Struktur Folder Proyek

Pastikan struktur folder proyek sebagai berikut:

```text
UAS-AIOT/
├── backend/                # Server Python (Flask + SQLite)
├── homeassistant/          # Konfigurasi Dashboard (YAML)
├── camera_audit/           # Modul Kamera AI (Laptop)
│   ├── main.py             # Script utama kamera & streaming
│   ├── requirements.txt    # Dependency modul kamera
│   └── audit_log.csv       # Log audit otomatis
├── hardware/               # Program ESP32 / Arduino
└── docker-compose.yaml     # Orkestrasi server
```

---

## 📋 Prasyarat (Requirements)

### Hardware

- Laptop / PC dengan Webcam
- ESP32 dan RFID Reader RC522
- Jaringan WiFi atau LAN yang sama

### Software

- Docker Desktop (status harus running)
- Python 3.11.x (wajib untuk kompatibilitas AI)
- Git (opsional)

---

## 🚀 Panduan Instalasi

### Tahap 1 – Menjalankan Server Pusat (Docker)

1. Buka terminal (CMD / PowerShell) di folder utama UAS-AIOT
2. Jalankan perintah:

```powershell
docker-compose up -d --build
```

3. Pastikan container berjalan:

```powershell
docker ps
```

Pastikan container smartcount_backend dan homeassistant berstatus Up.

---

### Tahap 2 – Menyiapkan Modul Kamera (Laptop)

1. Masuk ke folder kamera:

```powershell
cd camera_audit
```

2. Buat virtual environment Python 3.11:

```powershell
py -3.11 -m venv venv
```

3. Aktifkan virtual environment:

```powershell
.\venv\Scripts\activate
```

4. Install dependency:

```powershell
pip install -r requirements.txt
```

---

### Tahap 3 – Konfigurasi Integrasi Jaringan

#### Cek IP Laptop

1. Buka terminal baru
2. Jalankan perintah:

```powershell
ipconfig
```

3. Catat IPv4 Address (contoh: 192.168.1.5)

#### Daftarkan Kamera di Home Assistant

1. Buka browser: [http://localhost:8123](http://localhost:8123)
2. Masuk ke Settings > Devices & Services
3. Klik + Add Integration
4. Pilih MJPEG IP Camera

Isi konfigurasi:

- Name: Kamera Audit D201
- MJPEG URL: http://IP_LAPTOP:8000/video_feed
- Still Image URL: http://IP_LAPTOP:8000/snapshot

Ganti IP_LAPTOP dengan IP laptop Anda.

#### Firewall (Penting)

Jika kamera tidak muncul:

- Matikan sementara Windows Defender Firewall
- Atau buat inbound rule untuk port 8000

---

## ▶️ Cara Penggunaan

### 1. Menjalankan Kamera (Laptop)

```powershell
cd camera_audit
.\venv\Scripts\activate
python main.py
```

Tunggu hingga muncul pesan "Video Stream Ready".

### 2. Monitoring Dashboard

Buka browser: [http://localhost:8123](http://localhost:8123)

Video live akan tampil di panel Audit Integritas.

### 3. Proses Absensi

1. Dosen menekan tombol Buka Absensi
2. Mahasiswa melakukan tap RFID
3. Kamera melakukan validasi selama ±20 detik
4. Sistem menampilkan status:

   - VALID (Hijau)
   - ANOMALI (Merah)

---

## 🛠️ Troubleshooting

### Kamera tidak tampil / Broken Image

- Pastikan main.py sedang berjalan
- Pastikan IP laptop tidak berubah
- Pastikan port 8000 tidak diblokir firewall

### Status selalu Unknown

- Pastikan koneksi internet aktif
- Pastikan koneksi ke MQTT Broker tidak terputus
- Restart script kamera

### Error install library di Windows

- Pastikan menggunakan Python 3.11.x
- Hindari Python versi terlalu baru (3.13+)

---

## 📌 Catatan

SmartCount dirancang untuk keperluan akademik, riset, dan demonstrasi sistem IoT + AI secara terintegrasi.
