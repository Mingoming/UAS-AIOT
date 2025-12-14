-- =========================
-- TABEL MAHASISWA
-- =========================
CREATE TABLE IF NOT EXISTS mahasiswa (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  nim TEXT NOT NULL UNIQUE,
  nama TEXT NOT NULL,
  uid_rfid TEXT NOT NULL UNIQUE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- =========================
-- TABEL ABSENSI
-- =========================
CREATE TABLE IF NOT EXISTS absensi (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  mahasiswa_id INTEGER NOT NULL,
  uid_rfid TEXT NOT NULL,
  device TEXT,
  sesi_id INTEGER NOT NULL,
  waktu DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (mahasiswa_id) REFERENCES mahasiswa(id),
  FOREIGN KEY (sesi_id) REFERENCES sesi_kuliah(id)
);

-- =========================
-- LOG REGISTRASI RFID
-- =========================
CREATE TABLE IF NOT EXISTS registration_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  uid_rfid TEXT,
  nim TEXT,
  nama TEXT,
  status TEXT NOT NULL,     -- success | rejected | error
  message TEXT,
  waktu DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- =========================
-- UID YANG BELUM TERDAFTAR
-- =========================
CREATE TABLE IF NOT EXISTS unknown_scans (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  uid_rfid TEXT NOT NULL,
  device TEXT,
  waktu DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sesi_kuliah (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  mata_kuliah TEXT,
  waktu_mulai DATETIME,
  waktu_selesai DATETIME,
  aktif INTEGER DEFAULT 1,
  manual INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS jadwal_kuliah (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ruangan TEXT NOT NULL,
  hari INTEGER NOT NULL,           -- 0=minggu, 1=senin, dst (SQLite)
  jam_mulai TEXT NOT NULL,         -- HH:MM
  jam_selesai TEXT NOT NULL,       -- HH:MM
  mata_kuliah TEXT NOT NULL
);

INSERT INTO jadwal_kuliah
(ruangan, hari, jam_mulai, jam_selesai, mata_kuliah)
VALUES
('D201', 1, '07:00', '09:30', 'Kecerdasan Buatan D'),
('D201', 1, '09:30', '11:10', 'Jaringan Syaraf Tiruan A'),
('D201', 1, '12:50', '14:30', 'Proyek Perangkat Lunak D'),
('D201', 1, '14:30', '16:10', 'Pemrograman Web Lanjut B'),
('D201', 1, '16:10', '17:50', 'E-Business A'),
('D201', 2, '07:00', '09:30', 'Logika Informatika A'),
('D201', 2, '09:30', '11:10', 'Jaringan Syaraf Tiruan B'),
('D201', 2, '12:50', '15:20', 'Pemrograman Berorientasi Objek B'),
('D201', 2, '15:20', '17:50', 'Kecerdasan Buatan C'),
('D201', 3, '07:00', '09:30', 'Sistem Basis Data C'),
('D201', 3, '09:30', '11:10', 'Jaringan Syaraf Tiruan C'),
('D201', 3, '12:50', '14:30', 'Kecakapan Antar Personal C'),
('D201', 3, '14:30', '16:10', 'Kecakapan Antar Personal A'),
('D201', 3, '16:10', '17:40', 'Mobile Adhoc'),
('D201', 4, '07:00', '09:30', 'Pemrograman Internet B'),
('D201', 4, '09:30', '11:10', 'Jaringan Syaraf Tiruan D'),
('D201', 4, '12:50', '14:30', 'Interaksi Manusia dan Komputer C'),
('D201', 4, '14:30', '16:10', ' Software Quality Assurance'),
('D201', 4, '16:10', '17:40', 'Pemrograman Web Lanjut A'),
('D201', 5, '07:50', '09:30', 'Riset Operasional B'),
('D201', 5, '09:30', '11:10', 'Etika Profesi C'),
('D201', 5, '13:40', '16:10', 'Sistem Operasi B'),
('D201', 5, '16:10', '17:50', 'Aplikasi Internet of Things');
