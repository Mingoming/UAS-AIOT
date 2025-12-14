import cv2
import time
import statistics
import requests
import json
import csv
import os
import threading
from datetime import datetime
from flask import Flask, Response
from ultralytics import YOLO
import paho.mqtt.client as mqtt

# ==========================================
# ⚙️ KONFIGURASI SISTEM
# ==========================================
SAMPLING_DURATION = 20
STD_THRESHOLD = 3
CONFIDENCE = 0.4

# Ganti dengan IP Home Assistant/Backend jika perlu, atau biarkan localhost jika dites manual
API_RFID_URL = "http://localhost:5000/attendance/unique/session"
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "smartcount/audit/result"
HTTP_PORT = 8000

LOG_FILE = "audit_log.csv"

# ==========================================
# 🔧 INISIALISASI
# ==========================================
outputFrame = None
lock = threading.Lock()
app = Flask(__name__)

print("[INIT] Loading YOLOv8 model...")
model = YOLO("yolov8n.pt", verbose=False)

# ==========================================
# 📡 VIDEO & SNAPSHOT SERVER (BAGIAN BARU)
# ==========================================
def generate():
    global outputFrame, lock
    while True:
        with lock:
            if outputFrame is None: continue
            (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
            if not flag: continue
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')

@app.route("/video_feed")
def video_feed():
    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")

# --- INI YANG DITAMBAHKAN AGAR TIDAK ERROR ---
@app.route("/snapshot")
def snapshot():
    global outputFrame, lock
    with lock:
        if outputFrame is None:
            return "No image", 503
        (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
    return Response(bytearray(encodedImage), mimetype="image/jpeg")
# ---------------------------------------------

def start_flask():
    # Host 0.0.0.0 agar bisa diakses dari luar (Docker)
    app.run(host="0.0.0.0", port=HTTP_PORT, debug=False, use_reloader=False)

# ==========================================
# 🧠 LOGIKA AUDIT
# ==========================================
def get_rfid_count():
    try:
        response = requests.get(API_RFID_URL, timeout=3)
        if response.status_code == 200:
            return response.json().get("total", 0)
    except:
        return 0
    return 0

def publish_mqtt(payload):
    try:
        client = mqtt.Client()
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.publish(MQTT_TOPIC, json.dumps(payload), retain=True)
        client.disconnect()
        print("[MQTT] Data terkirim.")
    except Exception as e:
        print(f"[MQTT] Gagal: {e}")

def save_csv(data):
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, mode='a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "Cam_Count", "RFID_Count", "Diff", "Status"])
        writer.writerow([data['timestamp'], data['camera_count'], data['rfid_count'], data['diff'], data['status']])

# ==========================================
# 🎥 PROGRAM UTAMA
# ==========================================
def main():
    global outputFrame, lock

    t = threading.Thread(target=start_flask)
    t.daemon = True
    t.start()
    print(f"[INFO] Video Stream Ready at http://localhost:{HTTP_PORT}/video_feed")

    cap = cv2.VideoCapture(0)
    time.sleep(2.0)

    counts = []
    start_time = time.time()
    audit_done = False
    final_status = "SAMPLING..."
    final_cam = 0; final_rfid = 0

    print(f"[INFO] Mulai Sampling {SAMPLING_DURATION} detik...")

    while True:
        ret, frame = cap.read()
        if not ret: break

        results = model(frame, conf=CONFIDENCE, classes=[0], verbose=False)
        current_count = len(results[0].boxes)
        
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)

        elapsed = time.time() - start_time
        
        if elapsed < SAMPLING_DURATION:
            counts.append(current_count)
            countdown = int(SAMPLING_DURATION - elapsed)
            cv2.putText(frame, f"SAMPLING: {countdown}s", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            cv2.putText(frame, f"Count: {current_count}", (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        elif not audit_done:
            print("[INFO] Sampling selesai. Menghitung...")
            if len(counts) > 5:
                final_cam = statistics.mode(counts)
                std_dev = statistics.pstdev(counts)
                final_rfid = get_rfid_count()
                diff = abs(final_cam - final_rfid)
                
                if std_dev > STD_THRESHOLD: final_status = "INVALID (Unstable)"
                elif diff >= 3: final_status = "ANOMALI"
                else: final_status = "VALID"
                
                payload = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "camera_count": final_cam, "rfid_count": final_rfid,
                    "diff": diff, "status": final_status.split()[0]
                }
                publish_mqtt(payload)
                save_csv(payload)
            audit_done = True
        else:
            color = (0, 0, 255) if "ANOMALI" in final_status else (0, 255, 0)
            cv2.putText(frame, f"STATUS: {final_status}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 3)
            cv2.putText(frame, f"Cam: {final_cam} | RFID: {final_rfid}", (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        with lock:
            outputFrame = frame.copy()
        
        cv2.imshow("SmartCount Auditor", frame)
        if cv2.waitKey(1) & 0xFF in [ord('q'), 27]: break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()