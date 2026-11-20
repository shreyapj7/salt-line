#include <WiFiClientSecure.h>
#include <WiFi.h>
#include <HTTPClient.h>

// WiFi
#define WIFI_SSID "Wokwi-GUEST"
#define WIFI_PASSWORD ""
#define WIFI_CHANNEL 6

// Sensors
#define TDS_PIN 34
#define WATER_LEVEL_PIN 35

// LEDs
#define GREEN_LED 25
#define RED_LED 26

#define DEVICE_ID "saltline_esp32_01"
void connectWiFi() {
  Serial.println("\nConnecting to WiFi...");

  WiFi.disconnect(true);  // clear old state
  delay(1000);

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD, WIFI_CHANNEL);

  Serial.print("WiFi SSID set to: ");
  Serial.println(WIFI_SSID);
  Serial.print("WiFi status before wait: ");
  Serial.println(WiFi.status());

  unsigned long start = millis();

  while (WiFi.status() != WL_CONNECTED &&
         millis() - start < 30000) {
    Serial.print(".");
    Serial.print("Status: ");
    Serial.print(WiFi.status());
    switch (WiFi.status()) {
      case WL_IDLE_STATUS:     Serial.print(" (IDLE)"); break;
      case WL_NO_SSID_AVAIL:   Serial.print(" (NO_SSID_AVAIL)"); break;
      case WL_SCAN_COMPLETED:  Serial.print(" (SCAN_DONE)"); break;
      case WL_CONNECTED:       Serial.print(" (CONNECTED)"); break;
      case WL_CONNECT_FAILED:  Serial.print(" (CONNECT_FAILED)"); break;
      case WL_CONNECTION_LOST: Serial.print(" (CONN_LOST)"); break;
      case WL_DISCONNECTED:    Serial.print(" (DISCONNECTED)"); break;
    }
    Serial.println();
    delay(300);
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi connected!");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nWiFi connection failed.");
    Serial.print("Final status code: ");
    Serial.println(WiFi.status());
  }
}
// Temporary testing endpoint.
// Do not send real or private well data here.
const char* SERVER_URL =
  "https://card-thoroughly-okay-dressing.trycloudflare.com/api/v1/sensor-readings";

const int SAMPLE_COUNT = 20;
const int SAMPLE_DELAY_MS = 10;
const int REPORT_INTERVAL_MS = 5000;
const int WIFI_TIMEOUT_MS = 30000;

// Average ADC readings
int readAveragedADC(int pin) {
  long total = 0;

  for (int i = 0; i < SAMPLE_COUNT; i++) {
    total += analogRead(pin);
    delay(SAMPLE_DELAY_MS);
  }

  return total / SAMPLE_COUNT;
}

// Send JSON over HTTPS POST
void sendSensorData(
  int tdsRaw,
  int waterRaw,
  float tdsVoltage,
  float waterVoltage,
  bool inputWarning
) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("POST skipped: WiFi disconnected.");
    return;
  }

  char payload[400];

  snprintf(
    payload,
    sizeof(payload),
    "{"
      "\"device_id\":\"%s\","
      "\"uptime_ms\":%lu,"
      "\"tds_raw_avg\":%d,"
      "\"water_level_raw_avg\":%d,"
      "\"tds_voltage_est_v\":%.3f,"
      "\"water_voltage_est_v\":%.3f,"
      "\"input_warning\":%s,"
      "\"source\":\"wokwi_potentiometer_simulation\""
    "}",
    DEVICE_ID,
    millis(),
    tdsRaw,
    waterRaw,
    tdsVoltage,
    waterVoltage,
    inputWarning ? "true" : "false"
  );

  Serial.println("\nSending HTTP POST...");
  Serial.println(payload);

  WiFiClientSecure secureClient;
  secureClient.setInsecure();   // test only — do not ship like this

  HTTPClient http;
  http.setConnectTimeout(15000);
  http.setTimeout(15000);

  if (!http.begin(secureClient, SERVER_URL)) {
    Serial.println("HTTPS initialization failed.");
    return;
  }

  http.addHeader("Content-Type", "application/json");

  int responseCode = http.POST((uint8_t*)payload, strlen(payload));

  Serial.print("HTTP Status Code: ");
  Serial.println(responseCode);

  if (responseCode > 0) {
    String response = http.getString();
    Serial.println("Server response:");
    Serial.println(response.substring(0, 400));
  } else {
    Serial.print("Request error: ");
    Serial.println(http.errorToString(responseCode));
  }

  http.end();
}

void setup() {
  Serial.begin(115200);

  pinMode(GREEN_LED, OUTPUT);
  pinMode(RED_LED, OUTPUT);

  digitalWrite(GREEN_LED, LOW);
  digitalWrite(RED_LED, LOW);

  analogReadResolution(12);

  Serial.println("\nSALT-LINE");
  Serial.println("Phase 1.4: HTTP Transmission");

  connectWiFi();
}

void loop() {

  // Reconnect if WiFi drops
  if (WiFi.status() != WL_CONNECTED) {
    digitalWrite(GREEN_LED, LOW);
    digitalWrite(RED_LED, HIGH);

    connectWiFi();
  }

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Still offline, retrying in 3s...");
    delay(3000);
    return;
  }

  // Read sensors
  int tdsRaw = readAveragedADC(TDS_PIN);
  int waterRaw = readAveragedADC(WATER_LEVEL_PIN);

  float tdsVoltage = (tdsRaw / 4095.0) * 3.3;
  float waterVoltage = (waterRaw / 4095.0) * 3.3;

  bool inputWarning =
    tdsRaw <= 5 || tdsRaw >= 4090 ||
    waterRaw <= 5 || waterRaw >= 4090;

  digitalWrite(GREEN_LED, inputWarning ? LOW : HIGH);
  digitalWrite(RED_LED, inputWarning ? HIGH : LOW);

  Serial.printf("TDS raw=%d (%.3fV)  Level raw=%d (%.3fV)\n",
                tdsRaw, tdsVoltage, waterRaw, waterVoltage);

  sendSensorData(tdsRaw, waterRaw, tdsVoltage, waterVoltage, inputWarning);

  delay(REPORT_INTERVAL_MS);
}
