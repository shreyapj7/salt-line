# SALT-LINE: Coastal Groundwater Intelligence & Adaptive Monitoring Platform

**Pilot Geography:** Udupi Coastal Corridor, Karnataka, India  
**INNOVEX '26**

SALT-LINE is a community-connected coastal groundwater intelligence and adaptive-monitoring platform that combines local well observations, field measurements, and environmental evidence to assess groundwater vulnerability and answer: **"Where should we collect the next groundwater measurement, and why?"**

---

## Quick Links & Documentation

* **Backend API Contract & Specification:** [API_DOCUMENTATION.md](./docs/API_DOCUMENTATION.md) (or [root copy](./API_DOCUMENTATION.md))
* **Reconciled Data Sources Register:** [DATA_SOURCES.md](./docs/DATA_SOURCES.md)
* **Project Work Document (PWD):** [PROJECT_WORK_DOCUMENT.md](./docs/PROJECT_WORK_DOCUMENT.md)
* **Geospatial Metadata, Lineage & Guardrails:** [geospatial/metadata/README.md](./geospatial/metadata/README.md)

---

## Geospatial Assets (Person 2 Deliverables)

* **Boundary:** \geospatial/boundary/udupi_pilot_boundary.geojson\ (~42 km coastal strip, Padubidri to Brahmavara).
* **Locations:** \geospatial/processed/locations.geojson\ & \locations.csv\ (13 wells: 5 verified authority stations with published URLs/reports, 5 candidate community points, 3 demo points).
* **NDMI Environmental Layer:** \geospatial/processed/ndmi_pilot_grid.geojson\ (130-cell vegetation moisture indicator, labeled \simulated_demo\).
* **Rainfall Deficit Layer:** \geospatial/processed/rainfall_layer.geojson\ (IMD normals vs -66.6% dry-season recharge deficit).
* **Topography & Elevation Layer:** \geospatial/processed/elevation_layer.geojson\ (SRTM 30m coastal elevation and distance to sea).

---

## FastAPI Backend Endpoints Summary

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| \GET\ | \/\ | Health check & system status |
| \GET\ | \/api/v1/locations\ | List all 13 pilot wells (authority, candidate, demo) |
| \GET\ | \/api/v1/geospatial/boundary\ | Pilot boundary polygon GeoJSON |
| \GET\ | \/api/v1/geospatial/layers/ndmi\ | NDMI vegetation moisture indicator GeoJSON |
| \GET\ | \/api/v1/geospatial/layers/rainfall\ | IMD rainfall deficit layer GeoJSON |
| \GET\ | \/api/v1/geospatial/layers/elevation\ | SRTM coastal elevation & distance-to-coast GeoJSON |
| \POST\ | \/api/v1/sensor-readings\ | Ingest ESP32 telemetry (TDS, water level) |
| \POST\ | \/api/v1/community/reports\ | Ingest community well observations |
| \GET\ | \/api/v1/monitoring/priority\ | Ranked shortlist: **Where to measure next** |
| \GET\ | \/api/v1/recommendations/{id}\ | Location explanation and recommended field action |

See [docs/API_DOCUMENTATION.md](./docs/API_DOCUMENTATION.md) for full request/response schemas and curl examples.
