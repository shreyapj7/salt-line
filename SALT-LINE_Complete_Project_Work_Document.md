# SALT-LINE

## Product & Project Work Document (PWD)

**INNOVEX '26 · Udupi Coastal Region, Karnataka · Version 1.0 · 19
November 2026**

> **One-line description:** SALT-LINE is a community-connected coastal
> groundwater intelligence and adaptive-monitoring platform that
> combines local well observations, field measurements and environmental
> evidence to assess groundwater vulnerability and recommend where
> monitoring should happen next.

------------------------------------------------------------------------

# 1. Executive summary

Coastal groundwater can become vulnerable to seawater intrusion when
freshwater levels are reduced by factors such as groundwater extraction,
drought and aquifer conditions. Local well observations, government
measurements and environmental datasets may be fragmented or incomplete,
making it difficult for communities and governing bodies to understand
where additional investigation is most useful.

SALT-LINE brings these inputs together in one map-led decision-support
platform. It keeps **risk** and **evidence confidence** separate and
uses an adaptive monitoring engine to rank candidate locations for the
next measurement.

The central innovation is not simply displaying a risk map. It is
answering:

**"Where should we collect the next groundwater measurement, and why?"**

The first prototype focuses only on the Udupi coastal region of
Karnataka. The architecture is designed so that other coastal regions
could be added after local validation and calibration.

## 1.1 What SALT-LINE is

-   A community reporting channel for well location, well type, readings
    and observations.
-   A field-data channel using an ESP32 prototype with low-cost sensors.
-   A geospatial layer combining available satellite and public
    environmental data.
-   A transparent intelligence engine for risk, confidence and data
    gaps.
-   An adaptive decision engine that ranks candidate monitoring
    locations.
-   A dashboard for communities and governing bodies.

## 1.2 What SALT-LINE is not

-   It does not directly see underground salinity from satellite
    imagery.
-   It does not certify drinking-water safety.
-   It does not claim to locate the exact saltwater interface from
    sparse data.
-   It does not automatically control groundwater pumping or impose
    restrictions.
-   It does not treat community reports or cheap TDS readings as
    confirmed laboratory evidence.

SALT-LINE supports prioritisation and field investigation. Actual
water-quality decisions require suitable field measurements and, where
appropriate, laboratory analysis and expert assessment.

------------------------------------------------------------------------

# 2. Problem statement

Groundwater in coastal aquifers can be affected by seawater intrusion.
The extent and timing of risk depend on groundwater extraction,
recharge, rainfall, aquifer geology, freshwater head and other local
conditions.

For a local community or governing body, the challenge is that:

1.  Measurements may be spread across different sources and time
    periods.
2.  Many wells may not be monitored regularly.
3.  Community observations may not be linked to verified measurements.
4.  A map may show concern areas without explaining how reliable the
    evidence is.
5.  Monitoring resources are limited, so field teams need help deciding
    where to measure next.

**Problem SALT-LINE addresses:** the lack of a unified,
location-specific and evidence-aware way to understand coastal
groundwater vulnerability and prioritise the next monitoring locations.

## 2.1 Target users

  -----------------------------------------------------------------------
  User                    What they do in         What they get
                          SALT-LINE               
  ----------------------- ----------------------- -----------------------
  Local residents / well  Submit location, well   Understandable local
  owners                  type, readings and      information and a
                          observations            reporting channel

  Governing bodies /      Review locations, add   Monitoring priorities
  water-management groups verified measurements   and transparent
                          and plan field work     evidence

  Field staff / technical Collect and validate    A shortlist of
  users                   measurements            locations and required
                                                  data

  Researchers / students  Review documented       A structured pilot
                          environmental and       dataset with provenance
                          monitoring layers       
  -----------------------------------------------------------------------

**Primary users:** governing bodies and local communities.\
**Pilot geography:** Udupi coastal region, Karnataka.

------------------------------------------------------------------------

# 3. Proposed solution and ideal working

SALT-LINE follows a continuous evidence-to-action cycle.

## 3.1 End-to-end workflow

``` text
1. COLLECT
   Residents submit well location, well type, readings and observations.
   ESP32 prototype sends sensor readings.
   Governing bodies contribute verified measurements.
                    |
                    v
2. VALIDATE AND STORE
   Check coordinates, units, timestamps, missing values and source.
   Store data with a source and verification label.
                    |
                    v
3. ADD ENVIRONMENTAL CONTEXT
   Add available Sentinel-2 indicators, rainfall, elevation,
   coastline context and public groundwater records.
                    |
                    v
4. ASSESS
   Calculate groundwater vulnerability indicators.
   Calculate evidence confidence separately.
   Identify missing or outdated information.
                    |
                    v
5. ADAPTIVELY PRIORITISE
   Rank candidate locations using risk, nearby well evidence,
   distance from monitored stations and missing data.
                    |
                    v
6. PRESENT AND ACT
   Show map, risk, confidence, monitoring priority and reasons.
   Recommend the next measurement or field investigation.
                    |
                    v
7. VERIFY AND UPDATE
   Governing body / field team collects measurements.
   New verified data returns to the system and updates the assessment.
```

## 3.2 Example user journey

**A. Local resident** 1. Opens the SALT-LINE reporting page. 2. Shares a
well location, well type and optional reading. 3. Adds an observation,
such as a change in water usability. 4. The report is stored as
`community_report`, not automatically treated as verified.

**B. Governing body / field officer** 1. Opens the Udupi map. 2. Reviews
community reports, available measurements and evidence confidence. 3.
Sees locations with high vulnerability indicators, weak evidence or
monitoring gaps. 4. Reviews the adaptive shortlist and reasons. 5.
Chooses a site for field measurement. 6. Adds the verified measurement
after collection.

**C. SALT-LINE intelligence** 1. Validates and records the new
measurement. 2. Updates the location's available evidence. 3.
Recalculates risk and confidence where supported by data. 4. Re-ranks
candidate monitoring locations. 5. Explains what changed and why.

## 3.3 Main outputs

-   Interactive map of wells, reports and monitoring stations.
-   Risk / vulnerability score or "insufficient data" status.
-   Separate evidence-confidence score or status.
-   Data age, data coverage and missing-data indicators.
-   Ranked candidate monitoring locations.
-   Explanation for each recommended location.
-   Suggested next action, such as repeat measurement or laboratory
    testing.

------------------------------------------------------------------------

# 4. System architecture

``` text
COMMUNITY INPUTS                 HARDWARE INPUTS
- Well location                  - ESP32
- Well type                      - TDS sensor module / probe
- Optional reading               - Water-level demo sensor
- Local observation              - Optional temperature probe
          |                                 |
          +---------------+-----------------+
                          |
                          v
                  FASTAPI INGESTION
              Validation · Units · Timestamp
                Source and verification tag
                          |
                          v
                    SQLITE DATABASE
            Wells · Reports · Readings · Stations
                          |
             +------------+-------------+
             |            |             |
             v            v             v
       GEOSPATIAL     HYDROGEOLOGY    OBSERVATION
        FEATURES       INDICATORS       HISTORY
       Sentinel-2     Freshwater       Nearby well
       Rainfall       head / trend     readings
       Elevation      Coast / aquifer  Station points
       Coastline      context          Data age
             |            |             |
             +------------+-------------+
                          |
                          v
                INTELLIGENCE ENGINE
              Risk · Confidence · Data gaps
                          |
                          v
              ADAPTIVE DECISION ENGINE
           Monitoring priority + explanation
                          |
                          v
                REACT + LEAFLET DASHBOARD
        Risk map · Confidence · Priority · Recommendations
```

------------------------------------------------------------------------

# 5. Core formulas and decision logic

**Important:** All weights and scoring rules in this section are initial
prototype assumptions for transparent demonstration. They are not
validated hydrogeological thresholds. They must be calibrated against
reliable field measurements before operational use.

## 5.1 Input variables for the risk model

Each variable is normalised to a value from 0 to 1, where 0 means no/low
supporting risk signal and 1 means a strong supporting risk signal.

  ----------------------------------------------------------------------------
  Symbol            Variable           How it is estimated  Important
                                                            limitation
  ----------------- ------------------ -------------------- ------------------
  `E`               Electrical         Deviation from a     TDS is a proxy;
                    conductivity / TDS local, seasonal      raw potentiometer
                    anomaly            baseline using       values are not TDS
                                       suitable, calibrated 
                                       measurements         

  `G`               Groundwater-head   Decline relative to  Requires reliable
                    decline            an appropriate local water-level /
                                       or seasonal baseline groundwater-head
                                                            data

  `P`               Rainfall deficit   Rainfall anomaly     Rainfall deficit
                                       relative to a        alone does not
                                       suitable historical  prove intrusion
                                       baseline             

  `V`               Vegetation stress  Sentinel-2-derived   Supporting
                    anomaly            index anomaly,       evidence only;
                                       e.g. NDVI / NDMI     stress has many
                                                            causes

  `C`               Coastal / aquifer  Relevant coastal     Straight-line
                    susceptibility     proximity, elevation distance to sea
                                       and geology          alone is not an
                                       information where    aquifer model
                                       available            
  ----------------------------------------------------------------------------

## 5.2 Prototype groundwater-risk formula

\[ `\text{Risk}`{=tex}\_i = 100 `\times`{=tex} (0.35E_i + 0.30G_i +
0.15P_i + 0.10V_i + 0.10C_i) \]

Weights sum to 1.00.

**Interpretation:** A higher score means the available indicators show
greater relative vulnerability in the prototype model. It does not mean
there is a 72% probability of seawater intrusion.

Possible initial display bands, to be reviewed and calibrated: - 0--33:
lower relative indicator score - 34--66: moderate relative indicator
score - 67--100: higher relative indicator score

These are display bands only, not scientific or regulatory thresholds.

### Missing risk inputs

Never replace missing values with zero. If some inputs are unavailable,
calculate a provisional weighted mean over the available inputs only:

\[ `\text{Risk}`{=tex}*i = 100 `\times`{=tex}
`\frac{\sum_{j \in A_i} w_j x_{ij}}`{=tex} {`\sum`{=tex}*{j
`\in `{=tex}A_i} w_j} \]

Where: - `A_i` is the set of available, valid indicators for location
`i`. - `w_j` is the prototype weight for indicator `j`. - `x_ij` is its
normalised value.

If there is insufficient direct measurement or too little supporting
evidence, return **"insufficient data"** rather than a numeric score.
Record which indicators are missing. The confidence score should fall
when important data is missing.

### Critical rule for the current simulator

Wokwi potentiometers produce raw ADC values and estimated voltages. They
do **not** simulate calibrated TDS or actual groundwater level. Do not
feed `tds_raw_avg` or `water_level_raw_avg` directly into the real-world
groundwater-risk formula. They are useful for testing the electronics
and data pipeline only.

## 5.3 Simplified hydrogeological relationship

For a suitable idealised coastal aquifer, the Ghyben--Herzberg
approximation is often expressed as:

\[ z `\approx `{=tex}40h \]

Where: - `z` = approximate depth of the freshwater--saltwater interface
below sea level. - `h` = freshwater hydraulic head above sea level.

This is a simplified equilibrium relationship. It assumes idealised
hydrostatic conditions and a sharp interface. It is not a universal
rule, does not directly calculate horizontal inland intrusion distance
and should not be presented as a precise salt-front prediction. Use it
only as a contextual indicator where the required head and aquifer
assumptions are defensible.

## 5.4 Evidence-confidence formula

Risk and confidence answer different questions.

-   **Risk:** How strong are the available indicators of groundwater
    vulnerability?
-   **Confidence:** How complete and reliable is the evidence used to
    make that assessment?

Prototype confidence components, each normalised from 0 to 1:

  -----------------------------------------------------------------------
  Symbol                  Component               Meaning
  ----------------------- ----------------------- -----------------------
  `Q`                     Data quality / source   Whether data is
                          reliability             verified, calibrated
                                                  and traceable

  `F`                     Freshness               Whether measurements
                                                  are recent enough for
                                                  the intended analysis

  `C`                     Completeness            Whether the required
                                                  indicators are present

  `S`                     Spatial coverage /      Whether there are
                          consistency             enough relevant nearby
                                                  observations and
                                                  whether sources are
                                                  broadly consistent
  -----------------------------------------------------------------------

\[ `\text{Confidence}`{=tex}\_i = 100 `\times `{=tex}(0.30Q_i +
0.25F_i + 0.30C_i + 0.15S_i) \]

These weights are provisional. The UI should state that the score
describes evidence strength, not the probability that the risk score is
correct.

For a demo, source-quality ranking may be represented as: - Verified lab
/ documented authority measurement: strongest source class. - Calibrated
field instrument with metadata: strong source class. - Documented but
not independently verified sensor reading: intermediate source class. -
Community report with a stated method / reading: useful observational
evidence, lower verification. - Unverified observation without
measurement: limited evidence. - Simulated data: **zero real-world
evidential contribution**; label it as simulation and exclude it from
operational confidence.

Avoid assigning a single universal numeric quality value to each source
class without documenting the project's chosen policy.

## 5.5 Adaptive monitoring priority formula

This is the central SALT-LINE innovation.

For each candidate location `i`, define:

  -----------------------------------------------------------------------
  Symbol                  Factor                  Normalisation
  ----------------------- ----------------------- -----------------------
  `R_i`                   Existing risk indicator Risk / 100, if a
                                                  defensible risk score
                                                  exists

  `N_i`                   Nearby-well evidence    Normalised local
                                                  anomaly / concern
                                                  signal from relevant
                                                  nearby wells

  `D_i`                   Monitoring-station gap  Normalised distance to
                                                  the nearest valid
                                                  monitoring station

  `M_i`                   Missing-data need       Fraction / severity of
                                                  important missing or
                                                  outdated data
  -----------------------------------------------------------------------

Prototype formula:

\[ `\text{Priority}`{=tex}\_i = 100 `\times `{=tex}(0.30R_i + 0.20N_i +
0.20D_i + 0.30M_i) \]

Weights are design assumptions and must be adjusted after field
feedback.

**How to interpret it:** - Higher existing risk can increase monitoring
priority. - Concerning readings from nearby wells can increase local
priority. - Being far from an existing monitoring station can increase
priority because the area may be under-observed. - Missing or outdated
measurements can increase priority because the uncertainty needs to be
resolved.

If a factor is unavailable, do not silently assign 0. Either calculate a
clearly labelled provisional score over available factors and record
coverage, or return "not rankable" until enough inputs exist.

### Example (illustrative only)

  ------------------------------------------------------------------------------
  Candidate           Risk       Nearby  Station gap Missing data Outcome
                               evidence                           
  ----------- ------------ ------------ ------------ ------------ --------------
  A                   High     Moderate         High         High Very high
                                                                  monitoring
                                                                  priority

  B                   High         High          Low          Low High concern;
                                                                  already
                                                                  monitored
                                                                  nearby

  C                Unknown        Low /         High         High Verification
                                unknown                           priority, not
                                                                  confirmed high
                                                                  risk
  ------------------------------------------------------------------------------

The example is a conceptual comparison, not measured Udupi data.

### Recommendation explanation

Every ranked site should carry a plain-language explanation, e.g.:

> "Prioritised because recent measurements are missing, the location is
> relatively far from existing monitoring coverage, and nearby
> observations indicate that additional checking may be useful."

Do not say "saltwater intrusion confirmed" unless validated measurements
actually support that conclusion.

## 5.6 Recommendation rules

  -----------------------------------------------------------------------
  Condition                           Appropriate next step
  ----------------------------------- -----------------------------------
  Unusual TDS / EC reading            Repeat measurement using a
                                      calibrated instrument; arrange lab
                                      testing if warranted

  High risk with low confidence       Collect more reliable field
                                      evidence

  High risk with strong evidence      Review with groundwater staff; plan
                                      follow-up monitoring

  Large monitoring gap                Consider adding a monitoring point
                                      if access and relevance are
                                      confirmed

  Vegetation anomaly only             Investigate other causes; do not
                                      attribute it to salinity alone

  Community report only               Record and prioritise verification;
                                      do not treat as confirmed water
                                      quality
  -----------------------------------------------------------------------

------------------------------------------------------------------------

# 6. Hardware architecture and components

## 6.1 Prototype hardware flow

``` text
TDS sensor module / probe ---- GPIO34 (ADC1) \
                                               \
Water-level demo sensor ------ GPIO35 (ADC1) ---- ESP32
                                               /   |
Status green LED ------------- GPIO25 --------/    |
Status red LED --------------- GPIO26 -------------|
Optional DS18B20 ------------- GPIO4 --------------|
                                                    |
                                                 Wi-Fi
                                                    |
                                                  FastAPI
```

GPIO assignments are the current proposed Wokwi pin plan and must be
checked against the actual ESP32 board and exact sensor module.

## 6.2 Current hardware inventory

Already available: - ESP32 development board. - Breadboard. -
Male-to-male jumper wires. - Male-to-female jumper wires.

Planned / optional items: - One TDS module with probe. - One analog
water-level sensor module for a controlled demonstration. - Two LEDs
(green and red). - One 220Ω, ¼W resistor per LED. - Optional DS18B20
waterproof temperature probe. - One 4.7kΩ, ¼W pull-up resistor for
DS18B20 if the module does not already include it. - USB data cable
suitable for the ESP32. - Optional 100nF decoupling capacitors near
sensor supply pins.

A small 40-piece M-F jumper set is a practical purchase if existing M-F
supply is low. Use existing M-M wires for breadboard-to-breadboard
connections.

## 6.3 Electrical cautions

-   Verify the exact sensor module's VCC and analog output
    specifications before connecting it.
-   ESP32 ADC input must not exceed its permitted input voltage; treat
    3.3V as the maximum design ceiling for this project.
-   All connected modules need a common ground.
-   Each LED needs its own series resistor.
-   Keep sensor electronics and breadboard connections dry. Only use the
    probe portion intended for immersion.
-   An analog water-level board is a demonstration sensor, not a
    calibrated well-depth instrument.
-   A low-cost TDS module is not a chloride sensor or certified
    drinking-water instrument.
-   Do not connect a 5V analog output directly to an ESP32 ADC pin.

## 6.4 Hardware test levels

1.  Wokwi potentiometer simulation: confirms ADC and code path only.
2.  Physical sensor bench test: confirms module wiring and raw readings.
3.  Sensor calibration / comparison: needed before interpreting readings
    as meaningful water-quality or water-level values.
4.  Field deployment: requires suitable probes, installation,
    waterproofing, power, calibration, maintenance and permission.

------------------------------------------------------------------------

# 7. Technology stack

## 7.1 Recommended stack for the prototype

  -----------------------------------------------------------------------
  Layer                   Technology              Purpose
  ----------------------- ----------------------- -----------------------
  Microcontroller         ESP32-WROOM-32          Field data acquisition

  Firmware                Arduino C++ /           Sensor reading, status
                          PlatformIO              and Wi-Fi

  Circuit simulation      Wokwi                   Simulated ESP32 circuit
                                                  testing

  Satellite processing    Google Earth Engine +   Environmental
                          Sentinel-2              indicators

  GIS processing          GeoPandas, Rasterio,    Spatial data processing
                          Shapely                 

  Scientific computing    NumPy, SciPy            Calculations and data
                                                  processing

  Analytics               Scikit-learn            Baselines / anomaly
                                                  detection where
                                                  justified

  Backend                 Python + FastAPI        REST API and business
                                                  logic

  Validation              Pydantic                Request validation

  Prototype database      SQLite                  Local storage

  Scalable geospatial     PostgreSQL + PostGIS    Future spatial query
  database                                        support

  Frontend                React + Vite            Web dashboard

  Map                     Leaflet + OpenStreetMap Interactive map

  Data visualisation      Recharts                Trends and indicator
                                                  charts

  Testing                 curl, FastAPI Swagger   API and application
                          UI, browser dev tools   testing

  Development             VS Code, Git, GitHub    Team coding and version
                                                  control
  -----------------------------------------------------------------------

### Stack choices

Use SQLite for the first working demo. Move to PostgreSQL/PostGIS when
multi-user and spatial queries justify it. Use transparent formulas
before attempting a trained model; the initial dataset is unlikely to
support a reliable supervised salinity-prediction model.

------------------------------------------------------------------------

# 8. Backend APIs and data contract

## 8.1 Required API endpoints

  -----------------------------------------------------------------------------------------
  Method                  Endpoint                                  Purpose
  ----------------------- ----------------------------------------- -----------------------
  `GET`                   `/`                                       Health check

  `POST`                  `/api/v1/sensor-readings`                 Ingest ESP32 readings

  `GET`                   `/api/v1/sensor-readings`                 Retrieve readings

  `POST`                  `/api/v1/community/reports`               Submit community report

  `GET`                   `/api/v1/community/reports`               Retrieve reports

  `GET`                   `/api/v1/locations`                       Retrieve map locations

  `GET`                   `/api/v1/risk/map`                        Retrieve supported
                                                                    risk/confidence layer

  `GET`                   `/api/v1/monitoring/priority`             Retrieve ranked
                                                                    monitoring candidates

  `GET`                   `/api/v1/recommendations/{location_id}`   Retrieve location
                                                                    explanation and next
                                                                    step
  -----------------------------------------------------------------------------------------

## 8.2 Example sensor payload

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

This is a previous simulator example. It is not actual TDS or water
level.

## 8.3 Suggested database entities

### `locations`

-   `id`
-   `name`
-   `latitude`
-   `longitude`
-   `well_type`
-   `source_type`
-   `is_monitoring_station`
-   `last_measured_at`

### `sensor_readings`

-   `id`
-   `device_id`
-   `location_id` (nullable until linked to a real location)
-   `tds_raw_avg`
-   `water_level_raw_avg`
-   `tds_voltage_est_v`
-   `water_voltage_est_v`
-   `input_warning`
-   `source`
-   `received_at`

### `community_reports`

-   `id`
-   `location_id` (nullable)
-   `latitude`
-   `longitude`
-   `well_type`
-   `reported_reading`
-   `reported_unit`
-   `observation`
-   `source`
-   `verification_status`
-   `reported_at`

### `environmental_features`

-   `id`
-   `location_id` or geometry reference
-   `feature_name`
-   `feature_value`
-   `unit`
-   `source`
-   `observation_date`
-   `processing_version`

### `location_assessments`

-   `id`
-   `location_id`
-   `risk_score` (nullable)
-   `confidence_score` (nullable)
-   `priority_score` (nullable)
-   `risk_reasons`
-   `confidence_reasons`
-   `priority_reasons`
-   `missing_inputs`
-   `assessed_at`
-   `model_version`

Keep raw observations, processed indicators and derived scores traceable
to their sources.

------------------------------------------------------------------------

# 9. Frontend and expected application output

## 9.1 Main dashboard layout

**Top summary cards** - Number of submitted wells / reports. - Number of
verified measurements. - Locations with sufficient evidence for
assessment. - Candidate monitoring locations.

**Main map** - Udupi pilot boundary. - Well and report markers. -
Existing monitoring station markers. - Risk layer where sufficient data
exists. - Confidence / missing-data overlay. - Recommended next
monitoring locations.

**Location details panel** - Well type and source. - Latest available
measurement and date. - Risk score / status. - Confidence score /
status. - Data gaps. - Recommendation and explanation.

**Monitoring priorities panel** - Rank. - Location name / ID. - Why it
is selected. - What measurement is needed next.

**Community report form** - Location (map pin / coordinates). - Well
type. - Optional reading and unit. - Observation / notes. - Optional
image if supported. - Submission source and verification state.

## 9.2 Illustrative output only

``` json
{
  "location_id": "demo_site_01",
  "source": "simulated_demo",
  "risk": {
    "value": null,
    "status": "insufficient_data"
  },
  "confidence": {
    "value": 24,
    "status": "low"
  },
  "monitoring_priority": {
    "rank": 1,
    "status": "verify"
  },
  "reasons": [
    "No recent verified groundwater measurement",
    "Limited nearby monitoring coverage",
    "Important environmental inputs are missing"
  ],
  "recommended_next_step": "Collect a verified field measurement"
}
```

This sample deliberately shows insufficient risk evidence. If the
dashboard uses invented values for visual design, mark the entire record
as `simulated_demo` and display a visible simulation label.

## 9.3 What a judge should be able to do

1.  Open the Udupi pilot map.
2.  Select a well or candidate location.
3.  See its source and data freshness.
4.  View risk and confidence separately.
5.  Open the monitoring recommendation.
6.  Read why that location was prioritised.
7.  See what measurement or investigation is suggested next.
8.  Submit or inspect a community report.

------------------------------------------------------------------------

# 10. Functional and non-functional requirements

## Functional requirements

-   Accept sensor readings via API.
-   Accept community well reports.
-   Store source, timestamp, location and units.
-   Display map locations.
-   Calculate risk only where sufficient evidence exists.
-   Calculate evidence confidence separately.
-   Identify missing/outdated data.
-   Rank monitoring candidates using the agreed factors.
-   Explain every recommendation.
-   Show a visible distinction between verified, reported, public and
    simulated data.

## Non-functional requirements

-   **Explainability:** show the factors behind a score/rank.
-   **Traceability:** preserve source, timestamp and processing version.
-   **Safety:** never present a demo TDS value as certified
    drinking-water safety.
-   **Privacy:** collect only necessary community information; obtain
    consent for location-linked reports.
-   **Robustness:** tolerate missing or stale records.
-   **Usability:** keep map, status and next action easy to understand.
-   **Portability:** run backend and frontend locally for the prototype.

------------------------------------------------------------------------

# 11. Three-person team allocation

## Person 1 --- Hardware and IoT

Tasks: - Maintain Wokwi circuit and firmware. - Read and average analog
inputs. - Test status LEDs. - Verify Wi-Fi and HTTP transmission. - Test
physical sensor modules when available. - Keep simulation and physical
readings clearly labelled.

Deliverables: - Wokwi link. - Firmware source. - Circuit / pin
mapping. - Example JSON. - Demonstration or documented blocker.

## Person 2 --- Geospatial and environmental data

Tasks: - Define Udupi pilot boundary. - Find and document relevant
public datasets. - Prepare GeoJSON/CSV locations. - Process an
environmental feature if possible. - Export map-ready layer(s). -
Explain resolution, date, source and limitations.

Deliverables: - Boundary file. - Map-ready locations / layers. - Data
source register. - Processing notebook/script. - Real-versus-demo
labels.

## Person 3 --- Backend, intelligence and frontend

Tasks: - Complete FastAPI and SQLite. - Add community and sensor APIs. -
Validate and store data. - Implement prototype risk/confidence
formula. - Implement adaptive monitoring ranking. - Build React +
Leaflet dashboard. - Integrate geospatial teammate's files.

Deliverables: - Backend API. - Database. - Risk/confidence/adaptive
engine. - Dashboard and run instructions.

All three collaborate on integration and demo verification.

------------------------------------------------------------------------

# 12. Development roadmap

  -----------------------------------------------------------------------
  Phase                   Work                    Completion evidence
  ----------------------- ----------------------- -----------------------
  1\. Hardware simulation ESP32, potentiometers,  ADC values change and
                          LEDs                    serial output works

  2\. Firmware and        JSON, Wi-Fi, HTTP       Successful HTTP
  transmission                                    response

  3\. Backend/database    FastAPI, SQLite,        API stores and returns
                          validation              a record

  4\. Geospatial data     Udupi boundary and      Map-ready GeoJSON/data
                          environmental layers    layer with sources

  5\. Intelligence        Risk, confidence and    Explainable assessment
                          gaps                    or insufficient-data
                                                  response

  6\. Adaptive monitoring Candidate ranking       Ranked sites with
                                                  reasons

  7\. Frontend            React, Leaflet and      Usable interactive
                          reports                 dashboard

  8\. Integration/demo    End-to-end validation   Complete demonstration
                                                  with source labels
  -----------------------------------------------------------------------

## Definition of done for the first integrated MVP

-   Udupi coastal pilot map opens.
-   At least a small number of wells / candidate locations are displayed
    with real/demo labels.
-   At least one sensor reading can be submitted and retrieved through
    the API.
-   Community report can be submitted or demonstrated with a clearly
    labelled sample.
-   Risk and confidence appear separately.
-   Insufficient data is handled explicitly.
-   Adaptive monitoring returns a ranked candidate list and reasons.
-   Dashboard explains what should be measured next.
-   Team can identify every simulated, reported, public and verified
    data source.

------------------------------------------------------------------------

# 13. Current status at handoff (19 November 2026)

## Already demonstrated

-   Wokwi ESP32 analog input simulation using two potentiometers.
-   Averaged ADC readings and JSON serial output.
-   Wi-Fi connection in an earlier successful Wokwi run.
-   Successful HTTP POST to HTTPBin in an earlier successful run.
-   Local FastAPI sensor-reading endpoint.
-   SQLite storage and retrieval of a test record (`count: 1`).

## Still in progress / not yet demonstrated

-   Latest Wokwi Wi-Fi run has been intermittent.
-   Wokwi-to-local-FastAPI connection has not been demonstrated.
-   Physical TDS / water-level sensors have not yet been validated.
-   Udupi geospatial dataset and environmental layer need to be
    supplied.
-   Risk/confidence and adaptive monitoring need implementation and
    validation.
-   Integrated React map/dashboard needs completion.

## Immediate workaround for Wokwi network issues

-   Preserve the last known-good sketch that connected to Wi-Fi and
    POSTed to HTTPBin.
-   Retry Wokwi after stopping and restarting the simulation and
    refreshing the project.
-   Do not spend the whole sprint debugging the simulator.
-   Person 3 can test FastAPI with `curl` and use clearly labelled demo
    records.
-   When the physical ESP32 is available, connect it to the same local
    network as the Fedora backend for direct local testing.

------------------------------------------------------------------------

# 14. Risks, assumptions and mitigation

  -----------------------------------------------------------------------
  Risk / assumption                   Mitigation
  ----------------------------------- -----------------------------------
  TDS module readings are not         Label as TDS proxy; calibrate and
  certified salinity measurements     compare against suitable reference
                                      instruments

  Water-level demo sensor is not a    Use only as a demonstration input;
  well-depth instrument               deploy proper groundwater-level
                                      instrumentation for field use

  Vegetation stress is non-specific   Treat satellite indices as
                                      supporting context only

  Ghyben--Herzberg assumptions may    Use only as a simplified indicator
  not fit local geology               with explicit caveats

  Sparse or stale data                Display missingness and lower
                                      confidence; prioritise verification

  Community reports may be inaccurate Record source, date, method and
                                      verification status

  Prototype risk weights are          Label them as assumptions;
  arbitrary initially                 calibrate with field data

  Wokwi internet connection is        Use local `curl`/API demo and
  unreliable                          preserve the working simulator
                                      version

  Demo data may be misunderstood as   Visible `simulated_demo` labels and
  real                                provenance in every view
  -----------------------------------------------------------------------

------------------------------------------------------------------------

# 15. Demonstration storyline

A concise SALT-LINE demo can follow this sequence:

1.  **Show the Udupi map:** explain the pilot geography and data
    coverage.
2.  **Add a community report:** select a well location, type and
    observation.
3.  **Show field-data ingestion:** submit a sensor record or replay a
    clearly labelled Wokwi sample.
4.  **Open a location:** show source, latest data, risk and confidence
    separately.
5.  **Open adaptive monitoring:** show candidate ranking.
6.  **Explain the top candidate:** existing risk, nearby readings,
    monitoring-station gap and missing data.
7.  **Show next action:** repeat measurement, verification or field
    investigation.
8.  **Close with the feedback loop:** a new verified measurement updates
    the evidence and future priorities.

**Final message:** SALT-LINE does not claim to replace groundwater
experts or field testing. It helps communities and governing bodies
organise evidence, identify information gaps and decide where further
monitoring may be most valuable.

------------------------------------------------------------------------

# 16. Team handoff checklist

### Person 1 --- Hardware

-   [ ] Wokwi project link shared.
-   [ ] Known-good firmware preserved.
-   [ ] Pin mapping documented.
-   [ ] Example JSON shared.
-   [ ] Simulated vs physical status documented.

### Person 2 --- Geospatial

-   [ ] Udupi pilot boundary shared.
-   [ ] GeoJSON / CSV shared.
-   [ ] Dataset sources and dates documented.
-   [ ] Environmental layer or source inventory shared.
-   [ ] Real vs illustrative locations labelled.

### Person 3 --- Software

-   [ ] Backend run instructions shared.
-   [ ] API endpoints documented.
-   [ ] Database schema committed.
-   [ ] Risk / confidence implementation documented.
-   [ ] Adaptive ranking and explanations working.
-   [ ] Frontend map connected to API.

### Final integration

-   [ ] All three workstreams integrated.
-   [ ] Simulated and real data visibly separated.
-   [ ] No unsupported claim of confirmed seawater intrusion.
-   [ ] Demo flow tested end to end.
-   [ ] README updated with run instructions.
