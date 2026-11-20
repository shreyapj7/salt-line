const fs = require('fs');
const path = require('path');

console.log("======================================================================");
console.log("SALT-LINE PERSON 2 - RECONCILED AUDIT & VERIFICATION SUITE");
console.log("======================================================================\n");

let passed = true;
function assert(condition, message) {
  if (condition) {
    console.log(`[PASS] ${message}`);
  } else {
    console.error(`[FAIL] ${message}`);
    passed = false;
  }
}

// 1. Files existence check
const files = [
  'geospatial/boundary/udupi_pilot_boundary.geojson',
  'geospatial/processed/locations.geojson',
  'geospatial/processed/locations.csv',
  'geospatial/processed/ndmi_pilot_grid.geojson',
  'geospatial/processed/rainfall_layer.geojson',
  'geospatial/processed/elevation_layer.geojson',
  'geospatial/metadata/README.md',
  'geospatial/raw/README.md',
  'docs/DATA_SOURCES.md'
];

console.log("--- 1. Architecture & Deliverable Files Check ---");
files.forEach(f => {
  const full = path.resolve(__dirname, '../../', f);
  const exists = fs.existsSync(full);
  assert(exists, `File exists: ${f}`);
  if (exists) {
    const sz = fs.statSync(full).size;
    assert(sz > 100, `File is non-empty (${sz} bytes): ${f}`);
  }
});

// 2. Boundary Verification
console.log("\n--- 2. Boundary Verification Check ---");
const bGeo = JSON.parse(fs.readFileSync(path.resolve(__dirname, '../boundary/udupi_pilot_boundary.geojson'), 'utf-8'));
assert(bGeo.type === 'FeatureCollection', "Boundary is a FeatureCollection");
const bPoly = bGeo.features[0].geometry.coordinates[0];
assert(bPoly.length >= 15, `Boundary polygon has ${bPoly.length} vertices`);
assert(bGeo.metadata.verification_source.includes("OpenStreetMap"), "Boundary verified against OpenStreetMap");

function pointInPolygon(point, vs) {
  const x = point[0], y = point[1];
  let inside = false;
  for (let i = 0, j = vs.length - 1; i < vs.length; j = i++) {
    const xi = vs[i][0], yi = vs[i][1];
    const xj = vs[j][0], yj = vs[j][1];
    const intersect = ((yi > y) !== (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi);
    if (intersect) inside = !inside;
  }
  return inside;
}

// 3. Locations Dataset Verification
console.log("\n--- 3. Locations Dataset Verification ---");
const locGeo = JSON.parse(fs.readFileSync(path.resolve(__dirname, '../processed/locations.geojson'), 'utf-8'));
assert(locGeo.features.length === 13, `Total locations count is 13`);

let authCount = 0;
let commCount = 0;
let demoCount = 0;

locGeo.features.forEach(f => {
  const p = f.properties;
  const inside = pointInPolygon([p.longitude, p.latitude], bPoly);
  assert(inside, `Location ${p.id} (${p.name}) is INSIDE coastal boundary`);

  if (p.verification_status === 'verified_authority') {
    authCount++;
    assert(p.is_monitoring_station === true, `Authority station ${p.id} is marked monitoring_station=true`);
    assert(p.source_url && p.source_url.startsWith("http"), `Authority station ${p.id} has valid source URL: ${p.source_url}`);
    assert(p.source_document.length > 10, `Authority station ${p.id} has source document citation`);
  } else if (p.verification_status === 'unverified_community') {
    commCount++;
    assert(p.is_monitoring_station === false, `Community point ${p.id} is candidate, monitoring_station=false`);
    assert(p.source_type === 'community_report', `Community point ${p.id} has source_type=community_report`);
  } else if (p.verification_status === 'synthetic_demo') {
    demoCount++;
    assert(p.name.includes("DEMO"), `Demo point ${p.id} contains 'DEMO' in name`);
    assert(p.source_type === 'simulated_demo', `Demo point ${p.id} has source_type=simulated_demo`);
  }
});

assert(authCount === 5, `Found exactly 5 verified authority stations`);
assert(commCount === 5, `Found exactly 5 candidate community points`);
assert(demoCount === 3, `Found exactly 3 illustrative demo points`);

// 4. NDMI Grid Honest Label Check
console.log("\n--- 4. NDMI Grid Transparency Check ---");
const ndmiGeo = JSON.parse(fs.readFileSync(path.resolve(__dirname, '../processed/ndmi_pilot_grid.geojson'), 'utf-8'));
assert(ndmiGeo.metadata.source_type === 'simulated_demo', "NDMI metadata is honest: source_type=simulated_demo");
assert(ndmiGeo.features[0].properties.data_status === 'simulated_demo', "NDMI cell properties explicitly flagged simulated_demo");
assert(!ndmiGeo.features[0].properties.layer_name.toLowerCase().includes("salinity"), "NDMI is neutrally named, not salinity");

// 5. Rainfall & Elevation Layers Check
console.log("\n--- 5. Person 3 Inputs (Rainfall & Elevation) Check ---");
const rainGeo = JSON.parse(fs.readFileSync(path.resolve(__dirname, '../processed/rainfall_layer.geojson'), 'utf-8'));
assert(rainGeo.features.length > 5, `Rainfall layer contains ${rainGeo.features.length} cells`);
assert(typeof rainGeo.features[0].properties.recharge_deficit_pct === 'number', "Rainfall layer contains recharge_deficit_pct");

const elevGeo = JSON.parse(fs.readFileSync(path.resolve(__dirname, '../processed/elevation_layer.geojson'), 'utf-8'));
assert(elevGeo.features.length > 10, `Elevation layer contains ${elevGeo.features.length} cells`);
assert(typeof elevGeo.features[0].properties.mean_elevation_msl_m === 'number', "Elevation layer contains mean_elevation_msl_m");
assert(typeof elevGeo.features[0].properties.distance_to_coast_km === 'number', "Elevation layer contains distance_to_coast_km");

// 6. Metadata README Guardrails Check
console.log("\n--- 6. Metadata README Guardrails & Audit Check ---");
const metaText = fs.readFileSync(path.resolve(__dirname, '../metadata/README.md'), 'utf-8');
assert(metaText.includes("Sentinel-2 Doesn’t Measure Underground Salinity") || metaText.includes("Sentinel-2 doesn’t measure underground salinity"), "Guardrail 1: Sentinel-2 doesn't measure underground salinity");
assert(metaText.includes("Vegetation stress is non-specific") || metaText.includes("Vegetation Stress is Non-Specific"), "Guardrail 2: Vegetation stress is non-specific");
assert(metaText.includes("Supporting indicator only") || metaText.includes("Supporting Indicator Role Only"), "Guardrail 3: Supporting indicator role only");
assert(metaText.toUpperCase().includes("SECTION A") && metaText.toUpperCase().includes("SECTION B") && metaText.toUpperCase().includes("SECTION C"), "Structured sections A, B, and C documented");

console.log("\n======================================================================");
console.log(`FINAL RESULT: ${passed ? 'ALL CHECKS PASSED PERFECTLY!' : 'SOME CHECKS FAILED'}`);
console.log("======================================================================");

process.exit(passed ? 0 : 1);
