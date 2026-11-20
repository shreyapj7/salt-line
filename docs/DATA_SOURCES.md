# DATA SOURCES INVENTORY & REGISTER (RECONCILED & VALIDATED)

**Project:** SALT-LINE (Community-Connected Coastal Groundwater Intelligence)  
**Study Area:** Udupi Coastal Pilot Corridor, Karnataka, India  
**Date of Register:** 20 November 2026 (Updated & Audited)  
**Document Status:** Reconciled & Validated Deliverable (Person 2)

---

## 1. Overview & Provenance Reconciliations

This data source inventory registers all geospatial, hydrological, meteorological, and topographic datasets evaluated and compiled for the SALT-LINE Udupi coastal pilot. 

In strict adherence to the project's core honesty and provenance rules (*"Never pretend simulated data is physical or verified"*), this updated register clearly distinguishes between datasets with verified baselines and layers where scripts/templates exist but local execution was not completed, labelling demonstration grids accordingly.

---

## 2. Reconciled Data Sources Register

| Dataset | Source & Specific Citation | Date / Temporal Range | Resolution | Coverage | Access Status | Verification & Role in SALT-LINE |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Sentinel-2 MSI (Level-2A BOA Reflectance)** | Copernicus Browser / ESA / Google Earth Engine (`COPERNICUS/S2_SR_HARMONIZED`, Tile `T43PBT`) | 2026-03-12 (Target dry season scene, cloud cover < 1.5%) | 10 m (B2, B3, B4, B8) / 20 m (B11, B12) | Udupi coastal pilot extent | **can get it** *(Export script ready; local GeoTIFF not executed; current prototype grid in `processed/` is `simulated_demo`)* | GEE extraction script provided at `geospatial/scripts/google_earth_engine_ndmi_export.js`. Prototype grid uses geomorphologically modelled synthetic NDMI for UI/dashboard development. |
| **Rainfall Baseline & Deficit** | India Meteorological Department (IMD) Hydromet Division / AWS Stations (Udupi & Kundapura) | 1991–2020 Normals & 2024–2026 pre-monsoon dry season | ~27 km gridded (0.25°) / Point AWS daily | Udupi District & coastal corridor | **got it** *(Processed into `rainfall_layer.geojson`)* | Primary meteorological recharge indicator. Pre-monsoon dry deficit (-66.6% below Jan-Apr normal) feeds into Person 3's groundwater recharge deficit scoring. |
| **Rainfall (CHIRPS Daily)** | Climate Hazards Center (UCSB) / GEE (`UCSB-CHG/CHIRPS/DAILY`) | 1981–present (Nov 2026 update) | 0.05° (~5.3 km) | Global / 100% of pilot strip | **can get it** | Secondary satellite-gauge blended rainfall timeseries for drought tracking. |
| **Elevation & Topography (SRTM 1 Arc-Second)** | NASA JPL / USGS EarthExplorer (`USGS/SRTMGL1_003`) | Feb 2000 (v3.0 reprocessed) | 30 m (~1 arc-second) | Complete Udupi coastal corridor | **got it** *(Processed into `elevation_layer.geojson`)* | Digital Elevation Model (DEM) used to compute coastal elevation above MSL (<3 m MSL indicates critical susceptibility) and hydraulic gradient towards the sea. |
| **Elevation (Copernicus DEM GLO-30)** | Copernicus Space Component Data Access / AWS Open Data | 2020 release (WorldDEM baseline) | 30 m | Seamless across coastal Karnataka | **can get it** | Secondary surface elevation reference for verifying low-lying coastal depressions. |
| **Coastline & Estuarine Shoreline** | OpenStreetMap (OSM) contributors via Geofabrik Karnataka extract (2026-11) | 2026-11 snapshot | Vector (~1:10,000 scale) | Detailed shoreline, estuaries (Swarna, Sita, Udyavara, Pangala) | **got it** *(Integrated into boundary & locations)* | Primary geometry used to calculate Euclidean distance to sea and tidal backwaters for vulnerability scoring. |
| **Public Groundwater Monitoring Wells** | Central Ground Water Board (CGWB) South Western Region (*Ground Water Year Book, Karnataka*) | 2021–2024 published annual rounds | Point monitoring stations (lat/long) | 3 national network stations in pilot strip (Malpe, Kaup, Udyavara) | **got it** *(Verified with published URLs & reports)* | Ground-truth reference stations with published pre-/post-monsoon depth-to-water level (mbgl) and periodic chloride/EC benchmarks. |
| **State Groundwater Directorate Wells** | Karnataka Department of Mines & Geology (DMG), Groundwater Wing / District Ground Water Office | 2024 observation rounds | Point observation wells | 2 state authority stations (Brahmavara, Padubidri) | **got it** *(Verified with official department records)* | Departmental monitoring wells tracking coastal agricultural plain abstraction. |
| **Community Well Observations** | SALT-LINE Community Reporting Channel | Nov 2026 | Point coordinates (GPS/crowdsourced) | Padukere, Thottam, Mattu, Kalyanpura, Pangala | **got it** *(Explicitly flagged `unverified_community`)* | Local well owner observations on taste and usability; strictly segregated under `community_report` to prevent false confidence. |
| **Illustrative Demonstration Wells** | SALT-LINE Synthetic Test Bed | Nov 2026 | Simulated points | Malpe Port, Bengre Spit, Kaup Resort | **got it** *(Explicitly flagged `simulated_demo`)* | Hardware/firmware demonstration nodes; clearly carry "DEMO" in name and `simulated_demo` in properties. |

---

## 3. Data Ingestion & Fallback Strategy

1. **Environmental Feature Layer (NDMI):**  
   Because live Google Earth Engine raster download requires authenticated GCP service tokens not available in local sandboxes, the prototype utilizes a vector grid (`geospatial/processed/ndmi_pilot_grid.geojson`) explicitly marked `simulated_demo`. The production-ready GEE export script is saved in `geospatial/scripts/google_earth_engine_ndmi_export.js` for execution on authenticated cloud accounts.
2. **Missing Ground Data Policy:**  
   In compliance with SALT-LINE PWD principles, missing groundwater values are **never imputed or filled with zeroes**. Unmeasured stations explicitly carry `last_measured_at: null` and trigger an "insufficient data" state in Person 3's intelligence engine rather than false reassurance.
3. **Source Segregation:**  
   All ingestions strictly enforce source metadata flags (`public_dataset`, `authority_verified`, `community_report`, `simulated_demo`) so that Person 3's backend ranking engine and Leaflet UI never conflate unverified community submissions with laboratory or CGWB hydrograph standards.
