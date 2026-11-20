# SALT-LINE --- Project Work Document

**INNOVEX '26 \| Udupi coastal pilot, Karnataka \| Three-person
sprint**\
**Working deadline:** 19 November 2026

## 1. Project overview

SALT-LINE combines community well observations, field measurements,
available government data and satellite-derived environmental indicators
to support coastal groundwater monitoring in Udupi, Karnataka.

The prototype has two core functions: 1. Communicate groundwater
vulnerability/risk separately from evidence confidence. 2. Recommend
where to monitor next using existing risk, nearby well readings,
distance from monitored stations and missing/outdated data.

SALT-LINE is a decision-support prototype. Satellite imagery does not
directly see underground salinity. Community reports are observations,
not laboratory confirmation. Low-cost TDS readings are screening
proxies, not chloride measurements or drinking-water certification.

**Primary users:** governing bodies and local water-management groups;
local residents and well owners; field/technical staff.\
**Pilot:** Udupi coastal region only.

## 2. System architecture

``` text
Residents / well owners      ESP32 demo node      Authority measurements
          \                      |                      /
           +----------------------+---------------------+
                                  |
                         FastAPI data ingestion
                                  |
                     Validation + source labelling
                                  |
                            SQLite database
                                  |
           +----------------------+----------------------+
           |                      |                      |
    Geospatial features    Hydrogeological indicators   Well/report data
    Satellite/rainfall     Risk + evidence confidence   Nearby readings
    Elevation/coastline    Missing-data checks           Station locations
           +----------------------+----------------------+
                                  |
                      Adaptive monitoring engine
                                  |
                 Ranked candidate locations + reasons
                                  |
                       React + Leaflet dashboard
```

## 3. Three-person responsibility split

### Person 1 --- Hardware, ESP32 firmware and IoT integration

**Current context:** Wokwi has demonstrated two analog inputs, JSON
serial output, Wi-Fi connectivity and successful HTTP POSTs to HTTPBin
in an earlier run. The latest Wokwi run is intermittently failing to
connect. This must not block the other workstreams.

Tasks: - Preserve the known-good Wokwi circuit and firmware version. -
Retry Wokwi Wi-Fi: stop/restart simulation, verify SSID exactly
`Wokwi-GUEST`, empty password, and `WiFi.begin("Wokwi-GUEST", "", 6)`.
Refresh/reopen the simulation if needed. - Keep source label
`wokwi_potentiometer_simulation` for simulated readings. - Test FastAPI
ingestion with `curl` if Wokwi remains unavailable. - When physical
sensors arrive, verify pinout and output voltage before connecting to
ESP32 ADC pins. - Document what is simulated versus physically measured.

Pin plan to verify against the actual board/modules: - GPIO34: TDS
analog input / potentiometer substitute. - GPIO35: water-level analog
input / potentiometer substitute. - GPIO25: green LED through its own
series resistor. - GPIO26: red LED through its own series resistor. -
GPIO4: optional DS18B20 data line, with appropriate pull-up if required.

**Deliverable:** Wokwi project link, firmware, sample JSON, HTTPBin
success evidence or local `curl` fallback, and a brief blocker note. Do
not claim potentiometer values are TDS ppm or groundwater depth.

### Person 2 --- Geospatial data and environmental indicators

**Special experience:** GIS / geospatial imaging / satellite data.

Tasks: - Define and document the Udupi coastal pilot boundary. - Prepare
map-ready GeoJSON or CSV for sourced pilot locations, candidate
monitoring points and monitoring stations. - Distinguish sourced
locations, community reports, authority measurements and illustrative
demo points. - Identify available Sentinel-2, rainfall, elevation,
coastline and public groundwater datasets. - If feasible, calculate one
environmental layer (e.g. NDVI or NDMI) for a selected date/period and
study area. - Record source, date, resolution, processing method,
coverage and missing areas. - Export a map-ready layer for the frontend.

**Deliverable:** small Udupi pilot geospatial dataset and one documented
environmental layer if feasible. If data cannot be obtained today,
deliver the boundary, source inventory and clearly labelled illustrative
points rather than fabricated measurements.

Scientific guardrails: - Sentinel-2 does not directly measure
underground salinity. - Vegetation stress is non-specific. - Do not
label an environmental index as a salinity measurement. - Do not invent
groundwater measurements to fill spatial gaps.

### Person 3 --- Backend, intelligence and dashboard

Backend tasks: - Continue the existing FastAPI + SQLite project. -
Validate coordinates, timestamps, units, required fields and source
labels. - Build/verify: - `POST /api/v1/sensor-readings` -
`GET /api/v1/sensor-readings` - `POST /api/v1/community/reports` -
`GET /api/v1/community/reports` - `GET /api/v1/locations` -
`GET /api/v1/monitoring/priority` - Store timestamps in UTC. - Add a
health endpoint at `/`.

Suggested minimum tables: - `locations`: id, name, latitude, longitude,
well_type, source_type, is_monitoring_station, last_measured_at. -
`sensor_readings`: id, device_id, location_id, tds_raw_avg,
water_level_raw_avg, tds_voltage_est_v, water_voltage_est_v,
input_warning, source, received_at. - `community_reports`: id,
location_id, latitude, longitude, well_type, reported_reading,
reported_unit, observation, source, verification_status, reported_at. -
`location_assessments`: location_id, risk, confidence,
data_completeness, data_freshness, reasoning, assessed_at.

Risk/confidence rules: - Risk describes estimated vulnerability
indicated by available evidence. - Confidence describes evidence
quality, freshness and completeness. - Keep them separate. - Missing
values remain missing, not zero. - Explain contributing factors. - Label
prototype thresholds/weights as assumptions until field-validated.

Adaptive monitoring factors: 1. Existing vulnerability risk. 2. Nearby
well readings and trends, where available. 3. Distance from existing
monitored stations. 4. Missing, sparse or outdated data. 5. Well
importance and field accessibility, if available.

For every recommended location return its ID/coordinates, priority,
contributing reasons, missing information and suggested next
measurement. A high-risk/low-confidence location may be a priority for
verification, not a confirmed intrusion site.

Frontend: - React + Leaflet. - Udupi pilot map. - Well/report/station
markers. - Separate risk and confidence display. - Monitoring-priority
list and explanation panel. - Community report form if time permits.

**Deliverable:** local dashboard connected to FastAPI and displaying
stored data and adaptive recommendations.

## 4. Shared API contract

### Sensor reading

`POST /api/v1/sensor-readings`

``` json
{
  "device_id": "saltline_esp32_01",
  "uptime_ms": 4960,
  "tds_raw_avg": 1324,
  "water_level_raw_avg": 2697,
  "tds_voltage_est_v": 1.067,
  "water_voltage_est_v": 2.173,
  "input_warning": false,
  "source": "wokwi_potentiometer_simulation"
}
```

Example only; these are simulator values, not field measurements.

### Community report

`POST /api/v1/community/reports`

``` json
{
  "latitude": 13.34,
  "longitude": 74.74,
  "well_type": "open_well",
  "reported_reading": null,
  "reported_unit": null,
  "observation": "Example community observation",
  "source": "community_report"
}
```

Coordinates and observation are illustrative. Use sourced pilot
locations or explicitly labelled demo points.

### Monitoring priority response

`GET /api/v1/monitoring/priority`

``` json
{
  "generated_at": "UTC timestamp",
  "locations": [
    {
      "location_id": "demo_well_01",
      "priority": 1,
      "risk": {"value": null, "label": "insufficient data"},
      "confidence": {"value": null, "label": "low"},
      "reasons": [
        "No recent verified measurement",
        "Limited nearby monitoring coverage"
      ],
      "recommended_next_step": "Collect a verified field measurement"
    }
  ]
}
```

Example shape only; do not imply this is a real Udupi location.

## 5. Today's execution schedule

Work in parallel and exchange deliverables at each check-in.

  -------------------------------------------------------------------------
  Time block        Person 1          Person 2           Person 3
  ----------------- ----------------- ------------------ ------------------
  First 30 min      Preserve          Define Udupi       Confirm API
                    known-good Wokwi; boundary           schema/endpoints
                    retry Wi-Fi                          

  Next 60--90 min   Test POST or      Find and prepare   Finish SQLite
                    prepare `curl`    map-ready data     tables and APIs
                    fallback                             

  Next 60--90 min   Verify payload    Produce            Implement risk,
                    matches API       environmental      confidence and
                                      layer/metadata     adaptive ranking

  Next 60--90 min   Verify data path  Send               Build React +
                    if possible       GeoJSON/features   Leaflet dashboard

  Final 45--60 min  Test sensor/API   Verify map layers  Integrate, test
                    integration       and provenance     and prepare demo
  -------------------------------------------------------------------------

If time is tight, prioritise a working local demo over adding more
features.

## 6. Definition of done for tonight

The prototype is ready for the sprint if it demonstrates: 1. Udupi
coastal pilot map. 2. A small set of locations with real/demo labels. 3.
Community report submission or clearly labelled demo report. 4. Sensor
reading stored through the API (curl is acceptable if Wokwi fails). 5.
Risk and confidence displayed separately, including insufficient-data
states. 6. Ranked monitoring shortlist with reasons. 7. Dashboard
displays map, data and recommendations. 8. Team can explain what is
working, simulated, planned or awaiting validation.

If time runs out, cut advanced ML first, then multiple satellite
indices, then physical ESP32-to-backend connectivity. Keep the Udupi
map, provenance labels, separate risk/confidence, adaptive ranking and
explanations.

## 7. Data integrity and demo rules

Use these source labels consistently: -
`wokwi_potentiometer_simulation` - `esp32_physical_sensor` -
`community_report` - `authority_verified` - `public_dataset` -
`simulated_demo`

Never present simulated values as real groundwater measurements. TDS is
not a chloride test. Satellite vegetation indices are supporting
environmental indicators, not direct evidence of underground salinity.
Simplified hydrogeological relationships are indicators, not validated
maps of the saltwater interface.

## 8. Team handoff protocol

**Person 1 sends:** Wokwi link, firmware, sample JSON, working/blocked
status.\
**Person 2 sends:** GeoJSON/CSV or map layer, data sources/dates,
processing notes, real-versus-illustrative labels.\
**Person 3 sends:** backend run instructions, endpoint list/sample
requests, schema, frontend run instructions, risk/confidence/adaptive
logic explanation.

Suggested repository:

``` text
salt-line/
├── README.md
├── docs/
│   ├── PROJECT_WORK_DOCUMENT.md
│   ├── API_CONTRACT.md
│   └── DATA_SOURCES.md
├── hardware/
│   ├── wokwi/
│   └── esp32_firmware/
├── backend/
│   ├── app/
│   ├── requirements.txt
│   └── saltline.db
├── geospatial/
│   ├── boundary/
│   ├── raw/
│   ├── processed/
│   └── metadata/
├── frontend/
└── sample_data/
    └── clearly_labelled_demo_data/
```

## 9. Current project status

**Already demonstrated** - Wokwi ESP32 analog input simulation. -
Averaged ADC readings and JSON serial output. - Wi-Fi connection in an
earlier successful Wokwi run. - Successful HTTP POST to HTTPBin in an
earlier successful run. - FastAPI sensor-reading endpoint. - SQLite
storage and retrieval of a test record.

**Blocked or not yet demonstrated** - Latest Wokwi Wi-Fi run is
intermittently failing. - Wokwi-to-local-FastAPI connection is not
demonstrated. - Physical TDS and water-level sensors are not yet
validated. - Geospatial dataset/environmental layer still needs
delivery. - Risk/confidence and adaptive monitoring need implementation
and validation. - Integrated React map/dashboard still needs completion.

**Operating principle:** Build a small, honest, connected prototype.
Clearly show what is measured, reported, modelled and simulated.
