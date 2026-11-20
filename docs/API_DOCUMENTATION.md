# SALT-LINE Backend API Specification & Contract

**Version:** 1.0.0  
**Target Framework:** FastAPI (Python 3.10+)  
**Primary Consumer:** Person 3 (Backend & Dashboard Developer), React + Leaflet Frontend  
**Base Path:** `/api/v1`  
**Data Formats:** JSON, GeoJSON (EPSG:4326), UTC ISO-8601 Timestamps  

---

## 1. System Design Principles

1. **Strict Source Attribution:**  
   Every location, sensor payload, and observation must carry an allowed `source_type`:
   * `public_dataset` (e.g. CGWB, India-WRIS published data)
   * `authority_verified` (e.g. State Minor Irrigation / DMG records)
   * `community_report` (crowdsourced resident submissions)
   * `simulated_demo` (hardware/potentiometer or synthetic test nodes)
2. **Missing Data Policy:**  
   Missing or unmonitored values are strictly represented as `null`. They must **never** be replaced with `0` or fabricated values. Missing values trigger an `"insufficient_data"` state rather than false reassurance.
3. **Decoupled Risk & Evidence Confidence:**  
   Vulnerability score (hydrogeological susceptibility) and evidence confidence (data quantity, age, and verification level) are calculated and exposed separately.

---

## 2. Endpoints Summary Table

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **`GET`** | `/` | Service health status and API metadata |
| **`GET`** | `/api/v1/geospatial/boundary` | Pilot boundary polygon GeoJSON |
| **`GET`** | `/api/v1/geospatial/layers/ndmi` | Sentinel-2 NDMI moisture grid GeoJSON (`simulated_demo`) |
| **`GET`** | `/api/v1/geospatial/layers/rainfall` | IMD rainfall baseline & seasonal recharge deficit GeoJSON |
| **`GET`** | `/api/v1/geospatial/layers/elevation` | SRTM coastal topography, elevation MSL & distance to sea |
| **`GET`** | `/api/v1/locations` | All 13 pilot monitoring, candidate & demo wells |
| **`GET`** | `/api/v1/locations/{id}` | Single well profile, provenance, and latest readings |
| **`POST`** | `/api/v1/sensor-readings` | Ingest ESP32 telemetry (TDS, water level) |
| **`GET`** | `/api/v1/sensor-readings` | Retrieve telemetry logs with source filtering |
| **`POST`** | `/api/v1/community/reports` | Ingest crowdsourced community observations |
| **`GET`** | `/api/v1/community/reports` | List community reports with verification statuses |
| **`GET`** | `/api/v1/risk/map` | Vulnerability & evidence-confidence overlay |
| **`GET`** | `/api/v1/monitoring/priority` | **Adaptive ranking: where to measure next** |
| **`GET`** | `/api/v1/recommendations/{id}` | Explainable assessment & field action for a site |

---

## 3. Detailed Endpoint Specifications

### 3.1 System Health
#### `GET /`
* **Purpose:** Health check and API service information.
* **Response `200 OK`:**
```json
{
  "service": "SALT-LINE Groundwater Intelligence API",
  "version": "1.0.0",
  "status": "healthy",
  "study_area": "Udupi Coastal Corridor, Karnataka",
  "timestamp": "2026-11-20T11:30:00Z"
}
```

---

### 3.2 Geospatial Layers (Person 2 Hand-off)

#### `GET /api/v1/geospatial/boundary`
* **Purpose:** Provides the official coastal pilot boundary for Leaflet map initialization.
* **Response `200 OK`:** GeoJSON `FeatureCollection` containing a single `Polygon` feature (`geospatial/boundary/udupi_pilot_boundary.geojson`).
* **cURL:**
  ```bash
  curl -X GET http://localhost:8000/api/v1/geospatial/boundary
  ```

#### `GET /api/v1/geospatial/layers/ndmi`
* **Purpose:** Serves the 130-cell NDMI vegetation moisture indicator grid.
* **Response `200 OK`:** GeoJSON `FeatureCollection` (`geospatial/processed/ndmi_pilot_grid.geojson`).
* **Notice:** Every cell carries `source_type: "simulated_demo"`.

#### `GET /api/v1/geospatial/layers/rainfall`
* **Purpose:** Serves the IMD rainfall deficit layer (-66.6% dry-season recharge deficit).
* **Response `200 OK`:** GeoJSON `FeatureCollection` (`geospatial/processed/rainfall_layer.geojson`).

#### `GET /api/v1/geospatial/layers/elevation`
* **Purpose:** Serves the SRTM 30m coastal topography and distance-to-coast layer.
* **Response `200 OK`:** GeoJSON `FeatureCollection` (`geospatial/processed/elevation_layer.geojson`).

---

### 3.3 Locations & Wells

#### `GET /api/v1/locations`
* **Purpose:** Lists all 13 locations for map marker rendering and database queries.
* **Query Parameters:**
  * `source_type` (optional, string): Filter by `public_dataset`, `authority_verified`, `community_report`, or `simulated_demo`.
  * `is_monitoring_station` (optional, boolean): `true` or `false`.
* **Response `200 OK`:**
```json
[
  {
    "id": "udupi_loc_01",
    "name": "CGWB Hydrograph Station Malpe Fishery Port",
    "latitude": 13.3512,
    "longitude": 74.7045,
    "well_type": "open_well",
    "source_type": "public_dataset",
    "verification_status": "verified_authority",
    "is_monitoring_station": true,
    "last_measured_at": "2024-05-15T10:30:00Z",
    "groundwater_head_mbgl": 4.82,
    "distance_to_coast_m": 380,
    "source_document": "CGWB Ground Water Year Book Karnataka (2022-2023, Station: W20412/Malpe)",
    "source_url": "http://cgwb.gov.in/en/ground-water-year-book-reports"
  },
  {
    "id": "udupi_loc_06",
    "name": "Padukere Coastal Strip Domestic Well",
    "latitude": 13.3325,
    "longitude": 74.7061,
    "well_type": "open_well",
    "source_type": "community_report",
    "verification_status": "unverified_community",
    "is_monitoring_station": false,
    "last_measured_at": "2026-11-14T16:45:00Z",
    "groundwater_head_mbgl": null,
    "distance_to_coast_m": 210,
    "source_document": "SALT-LINE Community Intake Form (Report #CR-2026-0042)",
    "source_url": "https://saltline.local/api/v1/community/reports/42"
  }
]
```

#### `GET /api/v1/locations/{id}`
* **Purpose:** Retrieve full profile of a single well.
* **Error `404 Not Found`:** `{"detail": "Location udupi_loc_99 not found"}`

---

### 3.4 Ingestion Channels

#### `POST /api/v1/sensor-readings`
* **Purpose:** Ingests readings from ESP32 prototype hardware or Wokwi simulator.
* **Request Headers:** `Content-Type: application/json`
* **Request Body:**
```json
{
  "device_id": "saltline_esp32_01",
  "location_id": "udupi_loc_11",
  "uptime_ms": 14200,
  "tds_raw_avg": 1324,
  "water_level_raw_avg": 2697,
  "tds_voltage_est_v": 1.067,
  "water_voltage_est_v": 2.173,
  "input_warning": false,
  "source": "wokwi_potentiometer_simulation"
}
```
* **Validation Rules:**
  * `device_id` (string, required)
  * `source` (string, required): e.g. `wokwi_potentiometer_simulation`, `esp32_physical_sensor`
  * `location_id` (string, optional/nullable)
* **Response `201 Created`:**
```json
{
  "status": "success",
  "reading_id": 108,
  "received_at": "2026-11-20T11:30:15Z"
}
```
* **cURL:**
  ```bash
  curl -X POST http://localhost:8000/api/v1/sensor-readings \
    -H "Content-Type: application/json" \
    -d '{"device_id":"saltline_esp32_01","tds_raw_avg":1250,"water_level_raw_avg":2100,"source":"wokwi_potentiometer_simulation"}'
  ```

#### `POST /api/v1/community/reports`
* **Purpose:** Ingests crowdsourced well reports from coastal residents or cooperatives.
* **Request Body:**
```json
{
  "location_id": "udupi_loc_06",
  "latitude": 13.3325,
  "longitude": 74.7061,
  "well_type": "open_well",
  "reported_reading": 850.0,
  "reported_unit": "ppm_tds",
  "observation": "Water has a brackish aftertaste during current high-tide week.",
  "source": "community_report"
}
```
* **Response `201 Created`:**
```json
{
  "status": "success",
  "report_id": 43,
  "verification_status": "unverified_community",
  "reported_at": "2026-11-20T11:30:45Z"
}
```

---

### 3.5 Intelligence & Adaptive Monitoring (Person 3 Engine)

#### `GET /api/v1/monitoring/priority`
* **Purpose:** Returns the dynamically ranked list answering **"Where should we measure next, and why?"**
* **Ranking Factors:**
  1. High coastal/estuarine proximity (<500 m)
  2. Severe dry-season recharge deficit
  3. Distance from currently monitored authority stations (data void coverage)
  4. Chronic missing measurements (`last_measured_at: null`)
  5. Community reports indicating taste/usability deterioration
* **Response `200 OK`:**
```json
{
  "generated_at": "2026-11-20T11:30:00Z",
  "total_candidates": 5,
  "candidates": [
    {
      "rank": 1,
      "location_id": "udupi_loc_09",
      "name": "Kalyanpura Estuarine Agricultural Well",
      "coordinates": [74.7312, 13.3895],
      "risk": {
        "score": null,
        "status": "insufficient_data"
      },
      "confidence": {
        "score": 0.15,
        "level": "low"
      },
      "reasons": [
        "Zero historical verified measurements on record",
        "Situated 350m from tidal Swarna estuary backwater",
        "Coupled with -66.6% seasonal precipitation recharge deficit"
      ],
      "recommended_action": "Deploy field team for baseline TDS probe measurement and electrical conductivity profiling."
    },
    {
      "rank": 2,
      "location_id": "udupi_loc_06",
      "name": "Padukere Coastal Strip Domestic Well",
      "coordinates": [74.7061, 13.3325],
      "risk": {
        "score": 0.78,
        "status": "high_vulnerability"
      },
      "confidence": {
        "score": 0.35,
        "level": "low"
      },
      "reasons": [
        "Community complaint of brackish taste during spring tide",
        "Low elevation (<2.5m MSL) and proximity to open sea (210m)",
        "No certified authority measurement within 2.5 km radius"
      ],
      "recommended_action": "Conduct immediate physical TDS check and laboratory chloride titration."
    }
  ]
}
```

#### `GET /api/v1/recommendations/{location_id}`
* **Purpose:** Provides a deep-dive explanation and recommended next steps for a single location.
* **Response `200 OK`:**
```json
{
  "location_id": "udupi_loc_09",
  "name": "Kalyanpura Estuarine Agricultural Well",
  "vulnerability_assessment": "INSUFFICIENT_DATA",
  "evidence_confidence": "LOW (0.15)",
  "primary_driver": "Chronic data gap in critical estuarine transition zone",
  "contributing_factors": {
    "distance_to_coast_m": 2400,
    "distance_to_estuary_m": 350,
    "elevation_msl_m": 3.2,
    "rainfall_deficit_pct": -66.6,
    "last_measured_at": null
  },
  "recommended_field_action": "Schedule physical field team visit for depth-to-water measurement and laboratory chloride titration."
}
```

---

## 4. SQLite Schema Implementation for Person 3

```sql
-- 1. Locations
CREATE TABLE IF NOT EXISTS locations (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    well_type TEXT NOT NULL,
    source_type TEXT NOT NULL,
    verification_status TEXT NOT NULL,
    is_monitoring_station INTEGER NOT NULL,
    last_measured_at TEXT,
    groundwater_head_mbgl REAL,
    distance_to_coast_m INTEGER,
    source_document TEXT,
    source_url TEXT
);

-- 2. Sensor Readings (ESP32)
CREATE TABLE IF NOT EXISTS sensor_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT NOT NULL,
    location_id TEXT REFERENCES locations(id),
    uptime_ms INTEGER,
    tds_raw_avg INTEGER,
    water_level_raw_avg INTEGER,
    tds_voltage_est_v REAL,
    water_voltage_est_v REAL,
    input_warning INTEGER DEFAULT 0,
    source TEXT NOT NULL,
    received_at TEXT NOT NULL
);

-- 3. Community Reports
CREATE TABLE IF NOT EXISTS community_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    location_id TEXT REFERENCES locations(id),
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    well_type TEXT NOT NULL,
    reported_reading REAL,
    reported_unit TEXT,
    observation TEXT,
    source TEXT DEFAULT 'community_report',
    verification_status TEXT DEFAULT 'unverified_community',
    reported_at TEXT NOT NULL
);
```
