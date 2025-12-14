/*************************************************
 * SMARTCOUNT - ESP32 RFID MQTT CLIENT
 * -----------------------------------------------
 * Fungsi:
 * - Baca UID RFID (KTP)
 * - Kirim UID ke MQTT
 * - Sertakan metadata timestamp (ms sejak boot)
 *************************************************/

#include <WiFi.h>
#include <PubSubClient.h>
#include <SPI.h>
#include <MFRC522.h>

/* ========= PIN RFID ========= */
#define SS_PIN 5
#define RST_PIN 22
MFRC522 mfrc522(SS_PIN, RST_PIN);

/* ========= WIFI ========= */
const char *WIFI_SSID = "Meninting Raya 58 Depan";
const char *WIFI_PASSWORD = "muhzaky58";

/* ========= MQTT ========= */
const char *MQTT_BROKER = "broker.hivemq.com";
const int MQTT_PORT = 1883;
const char *MQTT_TOPIC = "smartcount/rfid/scan";
const char *DEVICE_ID = "ESP32-RFID-01";

/* ========= MQTT CLIENT ========= */
WiFiClient espClient;
PubSubClient mqttClient(espClient);

/* ============================================
 * Konversi UID byte → HEX string
 * ============================================ */
String uidToString(MFRC522::Uid uid)
{
    String uidStr = "";
    for (byte i = 0; i < uid.size; i++)
    {
        if (uid.uidByte[i] < 0x10)
            uidStr += "0";
        uidStr += String(uid.uidByte[i], HEX);
    }
    uidStr.toUpperCase();
    return uidStr;
}

/* ============================================
 * Koneksi WiFi
 * ============================================ */
void connectWiFi()
{
    Serial.print("Menghubungkan WiFi");
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nWiFi terhubung");
}

/* ============================================
 * Koneksi MQTT
 * ============================================ */
void connectMQTT()
{
    mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
    while (!mqttClient.connected())
    {
        Serial.print("Menghubungkan MQTT...");
        String clientId = "ESP32-" + String((uint32_t)ESP.getEfuseMac(), HEX);
        if (mqttClient.connect(clientId.c_str()))
        {
            Serial.println("berhasil");
        }
        else
        {
            Serial.print("gagal rc=");
            Serial.println(mqttClient.state());
            delay(2000);
        }
    }
}

/* ============================================
 * SETUP
 * ============================================ */
void setup()
{
    Serial.begin(115200);
    delay(300);

    SPI.begin();
    mfrc522.PCD_Init();
    Serial.println("RFID siap");

    connectWiFi();
    connectMQTT();
}

/* ============================================
 * LOOP
 * ============================================ */
void loop()
{
    if (!mqttClient.connected())
        connectMQTT();
    mqttClient.loop();

    if (!mfrc522.PICC_IsNewCardPresent())
        return;
    if (!mfrc522.PICC_ReadCardSerial())
        return;

    String uid = uidToString(mfrc522.uid);
    unsigned long ts_ms = millis(); // timestamp ESP32 (ms sejak boot)

    /* ============================
     * PAYLOAD JSON + TIMESTAMP
     * ============================ */
    String payload =
        "{"
        "\"uid\":\"" +
        uid + "\","
              "\"device\":\"" +
        String(DEVICE_ID) + "\","
                            "\"source\":\"ktp\","
                            "\"ts_ms\":" +
        String(ts_ms) +
        "}";

    bool ok = mqttClient.publish(MQTT_TOPIC, payload.c_str());

    Serial.println("================================");
    Serial.print("UID        : ");
    Serial.println(uid);
    Serial.print("Timestamp  : ");
    Serial.println(ts_ms);
    Serial.print("MQTT       : ");
    Serial.println(ok ? "TERKIRIM" : "GAGAL");
    Serial.print("Payload    : ");
    Serial.println(payload);
    Serial.println("================================");

    mfrc522.PICC_HaltA();
    delay(1500); // anti spam
}
