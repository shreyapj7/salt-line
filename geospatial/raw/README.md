# Raw Data Directory

This directory is reserved for raw unprocessed raster and vector packages:
- Sentinel-2 Level-2A GeoTIFFs (when downloaded via Copernicus Dataspace or GEE OAuth)
- Raw SRTM HGT/GeoTIFF 1-arc-second tiles (Tile: N13E074.hgt)
- Raw IMD gridded netCDF/GeoTIFF rainfall files
- Raw CGWB Groundwater Year Book bulletins in PDF/XLSX

Due to repository size constraints and absence of cloud authentication credentials in the local runtime, processed GeoJSON vector grids and CSV extracts are provided in `geospatial/processed/`.
All processing scripts to regenerate raw extractions are located in `geospatial/scripts/`.
