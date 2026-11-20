                                                      README - INNOVEX
1. Development phases
I suggest eight phases. Each phase should produce something testable before we move to the next.
1. Phase 1: Hardware & circuit simulation
   Current starting point
   Goal: Get the ESP32 reading sensor values.
   
   Tasks:
   - Create the ESP32 circuit in Wokwi.
   - Connect the TDS sensor and water-level sensor.
   - Add status LEDs.
   - Write firmware to read analog inputs.
   - Test the circuit with simulated inputs.
   - Assemble the real breadboard circuit once components arrive.
   Deliverable: Working ESP32 firmware producing sensor readings.
2. Phase 2: Sensor firmware & data transmission
   
   Goal: Send readings from the ESP32 to a computer/server.
   
   Tasks:
   - Read and convert ADC values.
   - Apply TDS conversion and temperature compensation where appropriate.
   - Add timestamps and device IDs.
   - Connect ESP32 to Wi-Fi.
   - Send readings to a FastAPI endpoint using HTTP.
   Deliverable: Live sensor readings reaching the backend.
3. Phase 3: Backend & database
   
   Goal: Establish one reliable source of project data.
   
   Tasks:
   - Create FastAPI backend.
   - Configure SQLite for the initial prototype.
   - Design tables for wells, readings, reports and monitoring stations.
   - Build APIs for sensor and community data.
   - Validate coordinates, timestamps, units and data sources.
   Deliverable: Sensor and community data stored and retrievable through APIs.
4. Phase 4: Geospatial data integration
   
   Goal: Add environmental context to individual well observations.
   
   Tasks:
   - Define the Udupi coastal pilot boundary.
   - Obtain available elevation, rainfall and coastal datasets.
   - Explore Sentinel-2 features using Google Earth Engine.
   - Process selected spatial indicators.
   - Associate environmental information with monitoring locations.
   Deliverable: A geospatial dataset with documented sources and coverage.
5. Phase 5: Intelligence engine
   
   Goal: Turn collected data into interpretable groundwater indicators.
   
   Tasks:
   - Implement simplified hydrogeological indicators.
   - Develop a transparent vulnerability-risk model.
   - Calculate evidence confidence separately.
   - Handle missing and outdated measurements.
   - Perform basic anomaly detection.
   Deliverable: Each location receives a risk assessment and an evidence-confidence assessment.
6. Phase 6: Adaptive monitoring engine
   Main innovation
   Goal: Identify where the next groundwater measurement would be most useful.
   
   Factors:
   - Existing vulnerability risk.
   - Readings from nearby wells.
   - Distance from existing monitoring stations.
   - Missing or outdated measurements.
   - Importance of the well and field accessibility, where available.
   Deliverable: Ranked monitoring locations with an explanation for every recommendation.
7. Phase 7: Frontend & interactive map
   
   Goal: Make SALT-LINE understandable to local communities and governing bodies.
   
   Tasks:
   - Build React dashboard.
   - Add Leaflet map.
   - Display well locations and reports.
   - Display separate risk and confidence indicators.
   - Add monitoring priority layers.
   - Show location-specific recommendations.
   - Include a community well-report form.
   Deliverable: An interactive SALT-LINE web application.
8. Phase 8: Integration, testing & demonstration
   
   Goal: Demonstrate the whole system working together.
   
   Tasks:
   - Connect ESP32 to the deployed/local backend.
   - Test community-report submission.
   - Test risk and confidence calculations.
   - Verify adaptive monitoring rankings.
   - Test missing-data scenarios.
   - Prepare a complete demonstration using clearly labelled real and simulated data.
   Deliverable: An end-to-end working prototype.
2. Seven-day implementation schedule
Assuming we are targeting the one-week prototype we discussed, here's the schedule I'd follow.
Day	Main focus	Expected result
1	Circuit simulation + project setup	ESP32 circuit simulated
2	Firmware + backend	Sensor data reaches API
3	Database + community form	Both input channels working
4	Geospatial data + risk model	First risk/confidence outputs
5	Adaptive monitoring engine	Ranked monitoring locations
6	React dashboard + map	Functional application
7	Integration + testing	End-to-end demonstration

Two-member task distribution
Member 1	Member 2
ESP32 circuit and firmware	Geospatial data preparation
Sensor readings and Wi-Fi	Satellite/environmental analysis
FastAPI backend and database	Risk, confidence and adaptive logic
API integration	React dashboard and maps

Both members should work together on the final integration.
