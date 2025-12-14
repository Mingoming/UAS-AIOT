import json
from flask import Flask, request, jsonify
import paho.mqtt.client as mqtt

from database import (
    init_db,
    fetch_one,
    fetch_all,
    execute
)

MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "smartcount/rfid/scan"

app = Flask(__name__)

def find_student_by_uid(uid):
    return fetch_one(
        "SELECT * FROM mahasiswa WHERE uid_rfid = ?",
        (uid,)
    )

def log_registration(uid, nim, nama, status, message):
    execute(
        """INSERT INTO registration_events
           (uid_rfid, nim, nama, status, message)
           VALUES (?, ?, ?, ?, ?)""",
        (uid, nim, nama, status, message)
    )

def on_connect(client, userdata, flags, rc):
    print("MQTT connected, rc =", rc)
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        uid = payload.get("uid")
        device = payload.get("device")

        if not uid:
            return

        mahasiswa = find_student_by_uid(uid)

        if mahasiswa:
            # 1. Cek apakah ada sesi mata kuliah yang aktif
            sesi = fetch_one(
                "SELECT * FROM sesi_kuliah WHERE aktif = 1"
            )

            if not sesi:
                print("Absensi belum dibuka")
                return

            # 2. Cek apakah UID sudah absen di sesi ini
            already = fetch_one("""
                SELECT id FROM absensi
                WHERE uid_rfid = ? AND sesi_id = ?
            """, (uid, sesi["id"]))

            if already:
                print("Sudah absen di sesi ini:", mahasiswa["nim"])
                return

            # 3. Simpan absensi untuk sesi aktif
            execute(
                """INSERT INTO absensi
                (mahasiswa_id, uid_rfid, device, sesi_id)
                VALUES (?, ?, ?, ?)""",
                (mahasiswa["id"], uid, device, sesi["id"])
            )

            print("ABSENSI:", mahasiswa["nim"], mahasiswa["nama"])
        else:
            execute(
                "INSERT INTO unknown_scans (uid_rfid, device) VALUES (?, ?)",
                (uid, device)
            )
            print("UID belum terdaftar:", uid)

    except Exception as e:
        print("MQTT error:", e)

def start_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()

@app.route("/register", methods=["POST"])
def register_rfid():
    data = request.json or {}
    uid = data.get("uid", "").upper()
    nim = data.get("nim")
    nama = data.get("nama")

    if not uid or not nim or not nama:
        log_registration(uid, nim, nama, "error", "Data tidak lengkap")
        return jsonify({"status": "error", "message": "Data tidak lengkap"}), 400

    if find_student_by_uid(uid):
        log_registration(uid, nim, nama, "rejected", "UID sudah terdaftar")
        return jsonify({"status": "rejected", "message": "UID sudah terdaftar"}), 409

    if find_student_by_nim(nim):
        log_registration(uid, nim, nama, "rejected", "NIM sudah terdaftar")
        return jsonify({"status": "rejected", "message": "NIM sudah terdaftar"}), 409

    execute(
        "INSERT INTO mahasiswa (nim, nama, uid_rfid) VALUES (?, ?, ?)",
        (nim, nama, uid)
    )

    log_registration(uid, nim, nama, "success", "Registrasi berhasil")
    return jsonify({"status": "success"}), 201


@app.route("/rfid", methods=["GET"])
def list_absensi():
    return jsonify(fetch_all("""
        SELECT a.waktu, m.nim, m.nama, a.uid_rfid
        FROM absensi a
        JOIN mahasiswa m ON a.mahasiswa_id = m.id
        ORDER BY a.waktu DESC
        LIMIT 100
    """))

@app.route("/register/status", methods=["GET"])
def register_status():
    row = fetch_one(
        "SELECT * FROM registration_events ORDER BY id DESC LIMIT 1"
    )
    return jsonify(row or {})

@app.route("/attendance/unique", methods=["GET"])
def attendance_unique():
    row = fetch_one("""
        SELECT COUNT(DISTINCT uid_rfid) AS total
        FROM absensi
    """)
    return jsonify({
        "total_unique_attendance": row["total"] if row else 0
    })

@app.route("/session/start", methods=["POST"])
def start_session_manual():
    data = request.json or {}
    mata_kuliah = data.get("mata_kuliah", "DEMO MANUAL")

    # Tutup semua sesi sebelumnya
    execute("UPDATE sesi_kuliah SET aktif = 0")

    # Buka sesi manual
    execute("""
        INSERT INTO sesi_kuliah (mata_kuliah, waktu_mulai, aktif, manual)
        VALUES (?, datetime('now','+8 hours'), 1, 1)
    """, (mata_kuliah,))

    return jsonify({
        "status": "started",
        "mode": "MANUAL",
        "mata_kuliah": mata_kuliah
    })

@app.route("/session/stop", methods=["POST"])
def stop_session():
    execute("""
        UPDATE sesi_kuliah
        SET aktif = 0, waktu_selesai = datetime('now', '+8 hours')
        WHERE aktif = 1
    """)

    return jsonify({"status": "stopped"})

@app.route("/attendance/unique/session", methods=["GET"])
def attendance_unique_session():
    row = fetch_one("""
        SELECT COUNT(DISTINCT uid_rfid) AS total
        FROM absensi
        WHERE sesi_id = (
            SELECT id FROM sesi_kuliah WHERE aktif = 1
        )
    """)
    return jsonify({"total": row["total"] if row else 0})

@app.route("/session/status", methods=["GET"])
def session_status():
    row = fetch_one("""
        SELECT mata_kuliah, waktu_mulai, manual
        FROM sesi_kuliah
        WHERE aktif = 1
        ORDER BY id DESC
        LIMIT 1
    """)

    if row:
        return jsonify({
            "aktif": True,
            "mata_kuliah": row["mata_kuliah"],
            "waktu_mulai": row["waktu_mulai"],
            "mode": "MANUAL" if row["manual"] == 1 else "AUTO"
        })

    return jsonify({
        "aktif": False,
        "mata_kuliah": "-",
        "waktu_mulai": "-",
        "mode": "-"
    })

@app.route("/attendance/list/session", methods=["GET"])
def attendance_list_session():
    rows = fetch_all("""
        SELECT
            m.nim,
            m.nama,
            a.waktu
        FROM absensi a
        JOIN mahasiswa m ON a.mahasiswa_id = m.id
        WHERE a.sesi_id = (
            SELECT id FROM sesi_kuliah WHERE aktif = 1
        )
        ORDER BY a.waktu ASC
    """)

    return jsonify({
        "total": len(rows),
        "data": rows
    })

from datetime import datetime, timedelta

@app.route("/session/auto/d201", methods=["POST"])
def auto_start_session_d201():
    """
    AUTO start absensi untuk ruang D201
    - Tidak menabrak sesi manual
    - Tidak membuka ulang sesi yang sudah aktif
    - Aman dipanggil periodik (tiap menit)
    """

    # =========================
    # 1. CEK SESI AKTIF
    # =========================
    active = fetch_one("""
        SELECT *
        FROM sesi_kuliah
        WHERE aktif = 1
        ORDER BY id DESC
        LIMIT 1
    """)

    if active:
        # Jika sesi MANUAL aktif, AUTO wajib berhenti
        if active.get("manual", 0) == 1:
            return jsonify({
                "status": "blocked",
                "reason": "manual_session_active",
                "mata_kuliah": active["mata_kuliah"]
            }), 409

        # Jika sesi AUTO sudah aktif, jangan buka ulang
        return jsonify({
            "status": "already_active",
            "mata_kuliah": active["mata_kuliah"]
        }), 200

    # =========================
    # 2. WAKTU SEKARANG (WITA)
    # =========================
    now = datetime.utcnow() + timedelta(hours=8)
    hari = now.isoweekday()        # Senin = 1
    jam = now.strftime("%H:%M")

    # =========================
    # 3. CARI JADWAL AKTIF
    # =========================
    jadwal = fetch_one("""
        SELECT *
        FROM jadwal_kuliah
        WHERE ruangan = 'D201'
          AND hari = ?
          AND jam_mulai <= ?
          AND jam_selesai > ?
        ORDER BY jam_mulai
        LIMIT 1
    """, (hari, jam, jam))

    if not jadwal:
        # NORMAL: tidak ada jadwal
        return jsonify({
            "status": "no_schedule"
        }), 404

    # =========================
    # 4. BUKA SESI ABSENSI (AUTO)
    # =========================
    execute("UPDATE sesi_kuliah SET aktif = 0")

    execute("""
        INSERT INTO sesi_kuliah
            (mata_kuliah, waktu_mulai, aktif, manual)
        VALUES
            (?, datetime('now','+8 hours'), 1, 0)
    """, (jadwal["mata_kuliah"],))

    return jsonify({
        "status": "started",
        "mode": "AUTO",
        "mata_kuliah": jadwal["mata_kuliah"]
    }), 201

@app.route("/session/auto/stop/d201", methods=["POST"])
def auto_stop_session_d201():
    execute("""
        UPDATE sesi_kuliah
        SET aktif = 0, waktu_selesai = datetime('now','+8 hours')
        WHERE aktif = 1
    """)
    return jsonify({"status": "stopped"})

@app.route("/timeline/d201", methods=["GET"])
def timeline_d201():
    rows = fetch_all("""
        SELECT jam_mulai, jam_selesai, mata_kuliah
        FROM jadwal_kuliah
        WHERE ruangan = 'D201'
          AND hari = cast(strftime('%w','now','+8 hours') as integer)
        ORDER BY jam_mulai
    """)
    return jsonify(rows)

from datetime import datetime, timedelta

def get_current_schedule(ruangan="D201"):
    now = datetime.utcnow() + timedelta(hours=8)  # WITA
    hari = now.weekday() + 1  # SQLite: Senin=1
    jam = now.strftime("%H:%M")

    return fetch_one("""
        SELECT *
        FROM jadwal_kuliah
        WHERE ruangan = ?
          AND hari = ?
          AND jam_mulai <= ?
          AND jam_selesai >= ?
        LIMIT 1
    """, (ruangan, hari, jam, jam))

def find_student_by_nim(nim):
    return fetch_one(
        "SELECT * FROM mahasiswa WHERE nim = ?",
        (nim,)
    )

if __name__ == "__main__":
    init_db()
    start_mqtt()
    app.run(port=5000, debug=True)
