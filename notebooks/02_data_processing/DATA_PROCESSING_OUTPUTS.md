# MERRA-2 Data Processing Outputs Summary

This document describes the output files produced by the three data processing notebooks in this directory, detailing units, storage locations, file formats, and aggregation methods.

**Date Created:** 2026-03-31
**Period Covered:** 1984-01-01 to 2025-12-31
**Spatial Extent:** US Lower 48 states (masked)
**Spatial Resolution:** ~50km grid (51 lat × 95 lon)

---

## Overview

| Notebook | Output Directory | File Count | Variables |
|----------|------------------|------------|-----------|
| Daytime Heat | `../../data/processed_daytime_heat/` | 504 files | 7 metrics |
| Nighttime Recovery | `../../data/processed_nighttime_recovery/` | 504 files | 8 metrics |
| VPD Statistics | `../../data/processed_vpd/` | 504 files | 3 metrics |

**Total Output Files:** 1,512 monthly NetCDF files
**Total Data Period:** 42 years × 12 months = 504 months (Jan 1984 - Dec 2025)

---

## 1. Daytime Heat Statistics

**Notebook:** `process_daytime_heat_stats.ipynb`
**Input:** `../../data/daily_data/merra2_us_YYYYMMDD.nc` (hourly T2M data)
**Output Directory:** `../../data/processed_daytime_heat/`

### File Format

- **Pattern:** `daytime_heat_YYYYMM.nc`
- **Example:** `daytime_heat_202306.nc` (June 2023)
- **Type:** NetCDF4 Classic with compression (deflate level 4)
- **Dimensions:** `(time, lat, lon)`
  - `time`: Number of days in month (28-31)
  - `lat`: 51 grid points (24.0°N to 49.0°N, 0.5° resolution)
  - `lon`: 95 grid points (-125.0°W to -66.25°W, ~0.63° resolution)

### File Structure

Each file contains **DAILY** statistics (one value per day per grid cell).
Files are organized by **MONTH** (all days of a month in one file).

### Time Window

- **Daytime:** 8am-8pm UTC (hours 8-19)
- **Duration:** 12 hours per day
- **Note:** UTC time, not local time. Actual daylight varies by location and season.

### Variables (7 total)

| Variable Name | Description | Units | Data Type | Fill Value |
|---------------|-------------|-------|-----------|------------|
| `hours_above_25` | Hot conditions (T > 25°C) | hours | int16 (0-12) | -1 |
| `hours_above_30` | Very hot conditions (T > 30°C) | hours | int16 (0-12) | -1 |
| `hours_above_35` | Extreme heat (T > 35°C) | hours | int16 (0-12) | -1 |
| `hours_above_40` | Dangerous heat (T > 40°C) | hours | int16 (0-12) | -1 |
| `hours_below_neg5` | Very cold daytime (T < -5°C) | hours | int16 (0-12) | -1 |
| `hours_below_0` | Freezing daytime (T < 0°C) | hours | int16 (0-12) | -1 |
| `hours_below_5` | Cold daytime (T < 5°C) | hours | int16 (0-12) | -1 |

### Aggregation Method

**COUNT:** For each day, count the number of daytime hours exceeding each threshold.

**Example** for June 15, 2023 in Texas (one grid cell):
- If temperature exceeded 30°C for 8 out of 12 daytime hours
- Then `hours_above_30[June 15, lat_idx, lon_idx] = 8`

**Value Range:** 0 to 12 hours per day (integer)
**Missing Data:** -1 (non-US areas or data gaps)

### Coordinate System

- **Latitude:** 24.0°N to 49.0°N (0.5° spacing, 51 points)
- **Longitude:** -125.0°W to -66.25°W (~0.625° spacing, 95 points)
- **CRS:** WGS84 / EPSG:4326

### Spatial Mask

- **Only US states (Lower 48):** Masked using `../../data/masks/region_mask.nc` (state_mask > 0)
- **Non-US grid cells:** Set to fill value (-1)
- **Excluded:** Ocean/Canada/Mexico

### Metadata

**Global Attributes:**
- `title`: "MERRA-2 Daytime Heat/Cold Statistics"
- `source`: "MERRA-2 M2T1NXSLV collection"
- `daytime_hours`: "8-19 (UTC)"
- `temporal_resolution`: "Daily"
- `spatial_mask`: "US states only (state_mask > 0)"

**Variable Attributes** (example for `hours_above_30`):
- `long_name`: "Very hot conditions (T > 30°C)"
- `units`: "hours"
- `description`: "Daily count of daytime hours with temperature above 30°C"

### Example Access (Python/xarray)

```python
import xarray as xr

# Load one month
ds = xr.open_dataset('../../data/processed_daytime_heat/daytime_heat_202306.nc')

# Access variable
hot_hours = ds['hours_above_30']  # shape: (30 days, 51 lat, 95 lon)

# Example: Get June 15, 2023 data
june_15_data = hot_hours.sel(time='2023-06-15')  # shape: (51, 95)

# Example: Time series for one location
texas_timeseries = hot_hours.sel(lat=31.0, lon=-100.0, method='nearest')
```

---

## 2. Nighttime Recovery Statistics

**Notebook:** `process_nighttime_recovery_stats.ipynb`
**Input:** `../../data/daily_data/merra2_us_YYYYMMDD.nc` (hourly T2M data)
**Output Directory:** `../../data/processed_nighttime_recovery/`

### File Format

- **Pattern:** `nighttime_recovery_YYYYMM.nc`
- **Example:** `nighttime_recovery_202306.nc` (June 2023)
- **Type:** NetCDF4 Classic with compression (deflate level 4)
- **Dimensions:** `(time, lat, lon)`
  - `time`: Number of days in month (28-31)
  - `lat`: 51 grid points
  - `lon`: 95 grid points

### File Structure

Each file contains **DAILY** statistics (one value per day per grid cell).
Files are organized by **MONTH** (all days of a month in one file).

### Time Window

- **Nighttime:** 8pm-6am UTC (hours 20-23, 0-5)
- **Duration:** 10 hours per night
- **Note:** Spans two calendar days (evening of day N and morning of day N+1)

### Variables (8 total)

| Variable Name | Description | Units | Data Type | Fill Value |
|---------------|-------------|-------|-----------|------------|
| `hours_below_18_above_0` | Strong recovery (0°C < T < 18°C) | hours | int16 (0-10) | -1 |
| `hours_below_21_above_0` | Reasonable recovery (0°C < T < 21°C) | hours | int16 (0-10) | -1 |
| `hours_below_24_above_0` | Weak recovery (0°C < T < 24°C) | hours | int16 (0-10) | -1 |
| `hours_above_21` | Poor recovery (T > 21°C) | hours | int16 (0-10) | -1 |
| `hours_above_24` | Very poor recovery (T > 24°C) | hours | int16 (0-10) | -1 |
| `hours_below_0` | Freezing conditions (T < 0°C) | hours | int16 (0-10) | -1 |
| `hours_below_neg5` | Very cold conditions (T < -5°C) | hours | int16 (0-10) | -1 |
| `hours_below_neg10` | Extremely cold (T < -10°C) | hours | int16 (0-10) | -1 |

### Aggregation Method

**COUNT:** For each day, count the number of nighttime hours in each threshold range.

**Recovery Thresholds** (for livestock heat stress):
- **Strong recovery:** Most of night below 18°C
- **Reasonable recovery:** Most of night below 21°C
- **Weak recovery:** Most of night below 24°C
- **Poor recovery:** Night hours above 21°C
- **Very poor recovery:** Night hours above 24°C

**Example** for June 15, 2023 in Oklahoma (one grid cell):
- If temperature was above 24°C for 6 out of 10 nighttime hours
- Then `hours_above_24[June 15, lat_idx, lon_idx] = 6`
- This indicates **VERY POOR** nighttime recovery (no cooling)

**Value Range:** 0 to 10 hours per night (integer)
**Missing Data:** -1 (non-US areas or data gaps)

### Livestock Interpretation

| Recovery Level | `hours_above_21` | Cooling |
|----------------|------------------|---------|
| Good Recovery | < 2 | Most of night cool |
| Moderate Stress | 2-5 | Partial cooling |
| High Stress | 6-8 | Minimal cooling |
| Critical Stress | > 8 | No cooling, heat exhaustion risk |

Same spatial mask and coordinate system as daytime heat data.

### Metadata

**Global Attributes:**
- `title`: "MERRA-2 Nighttime Recovery Statistics"
- `source`: "MERRA-2 M2T1NXSLV collection"
- `nighttime_hours`: "20-23, 0-5 (UTC)"
- `temporal_resolution`: "Daily"

**Variable Attributes** (example for `hours_above_24`):
- `long_name`: "Very poor recovery nights (T > 24°C)"
- `units`: "hours"
- `description`: "Daily count of nighttime hours with temperature above 24°C"

### Example Access (Python/xarray)

```python
import xarray as xr

# Load one month
ds = xr.open_dataset('../../data/processed_nighttime_recovery/nighttime_recovery_202306.nc')

# Access variable
poor_recovery = ds['hours_above_24']  # shape: (30 days, 51 lat, 95 lon)

# Calculate percentage of nights with very poor recovery
pct_poor = (poor_recovery > 6).sum(dim='time') / len(poor_recovery.time) * 100
```

---

## 3. VPD (Vapor Pressure Deficit) Statistics

**Notebook:** `process_vpd_stats.ipynb`
**Input:** `../../data/daily_data/merra2_us_YYYYMMDD.nc` (hourly VPD data)
**Output Directory:** `../../data/processed_vpd/`

### File Format

- **Pattern:** `vpd_YYYYMM.nc`
- **Example:** `vpd_202306.nc` (June 2023)
- **Type:** NetCDF4 Classic with compression (deflate level 4)
- **Dimensions:** `(time, lat, lon)`
  - `time`: Number of days in month (28-31)
  - `lat`: 51 grid points
  - `lon`: 95 grid points

### File Structure

Each file contains **DAILY** statistics (one value per day per grid cell).
Files are organized by **MONTH** (all days of a month in one file).

### Time Window

- **Afternoon:** 12pm-6pm UTC (hours 12-17)
- **Duration:** 6 hours per day
- **Rationale:** Peak VPD occurs during hottest part of day, affecting livestock evaporative cooling when most needed.

### Variables (3 total)

| Variable | Description | Units | Data Type | Fill Value |
|----------|-------------|-------|-----------|------------|
| `vpd_mean` | Mean VPD during afternoon (averaged over 6 hours) | kPa | float32 (0.0-15.0) | NaN |
| `vpd_min` | Minimum VPD during afternoon | kPa | float32 (0.0-15.0) | NaN |
| `vpd_max` | Maximum VPD during afternoon | kPa | float32 (0.0-15.0) | NaN |

### Aggregation Method

**MEAN/MIN/MAX:** For each day, compute statistics across afternoon hours.

**VPD (Vapor Pressure Deficit)** = Saturation Vapor Pressure - Actual Vapor Pressure
- Calculated from T2M (temperature), QV2M (specific humidity), PS (pressure)
- Higher VPD = drier air = reduced evaporative cooling efficiency
- Units: kPa (kiloPascals)

**Example** for June 15, 2023 in Texas (one grid cell):
- Afternoon VPD values: [2.1, 2.5, 2.8, 3.0, 2.7, 2.4] kPa (6 hourly values)
- `vpd_mean[June 15]` = 2.58 kPa (average)
- `vpd_min[June 15]` = 2.1 kPa (lowest)
- `vpd_max[June 15]` = 3.0 kPa (highest)

**Value Range:**
- **Typical:** 0.5-5.0 kPa
- **Extreme:** Up to 8-10 kPa in desert regions
- **Warning:** Values > 15 kPa (rare, extreme desert conditions)
- **Note:** Negative values clamped to 0 (VPD cannot be negative by definition)

### Livestock Interpretation

| VPD Level | Range (kPa) | Interpretation |
|-----------|-------------|----------------|
| Low VPD | < 1.5 | Good cooling conditions (humid) |
| Moderate VPD | 1.5-2.5 | Adequate cooling |
| High VPD | 2.5-3.5 | Reduced cooling (combined with heat = stress) |
| Very High VPD | > 3.5 | Minimal evaporative cooling (extreme stress) |

**Compound Stress:** High temperature (>30°C) + High VPD (>2.5 kPa) = **critical**

Same spatial mask and coordinate system as temperature data.

### Metadata

**Global Attributes:**
- `title`: "MERRA-2 VPD Statistics"
- `source`: "MERRA-2 M2T1NXSLV collection"
- `afternoon_hours`: "12-17 (UTC)"
- `temporal_resolution`: "Daily"

**Variable Attributes** (example for `vpd_mean`):
- `long_name`: "Mean VPD during afternoon window"
- `units`: "kPa"
- `description`: "Daily mean vapor pressure deficit during afternoon hours (12pm-6pm UTC)"

### Example Access (Python/xarray)

```python
import xarray as xr
import numpy as np

# Load one month
ds = xr.open_dataset('../../data/processed_vpd/vpd_202306.nc')

# Access variable
vpd_mean = ds['vpd_mean']  # shape: (30 days, 51 lat, 95 lon)

# Calculate days with high VPD (>2.5 kPa)
high_vpd_days = (vpd_mean > 2.5).sum(dim='time')

# Typical range check
print(f"VPD range: {np.nanmin(vpd_mean.values):.2f} - {np.nanmax(vpd_mean.values):.2f} kPa")
```

---

## Data Type Comparison

| Processing Type | Data Type | Value Range | Aggregation |
|-----------------|-----------|-------------|-------------|
| Daytime Heat | int16 (integer) | 0-12 hours | COUNT (sum) |
| Nighttime Recovery | int16 (integer) | 0-10 hours | COUNT (sum) |
| VPD Statistics | float32 (float) | 0.0-15.0 kPa | MEAN/MIN/MAX |

**Key Difference:**
- **Temperature metrics:** INTEGER hour counts per day
- **VPD metrics:** CONTINUOUS averages (mean/min/max of afternoon values)

---

## Common Characteristics

All three datasets share:

✓ Monthly files with daily temporal resolution
✓ NetCDF4 format with compression (deflate level 4)
✓ Same spatial grid: 51 lat × 95 lon (~50km resolution)
✓ Same spatial extent: US Lower 48 states (masked)
✓ Same coordinate system: WGS84 (EPSG:4326)
✓ Same time period: 1984-2025 (504 monthly files each)
✓ US state mask applied: Non-US areas set to fill value
✓ Source: MERRA-2 reanalysis (NASA GMAO)

### File Size

- **Daytime Heat:** ~2-3 MB per month (compressed)
- **Nighttime Recovery:** ~2-3 MB per month (compressed)
- **VPD:** ~3-4 MB per month (compressed, float32 vs int16)

### Total Storage

- **Daytime Heat:** ~1.5 GB (504 files)
- **Nighttime Recovery:** ~1.5 GB (504 files)
- **VPD:** ~2.0 GB (504 files)
- **TOTAL:** ~5 GB for all three datasets

---

## Downstream Processing

These daily files are further aggregated to **WEEKLY** resolution for analysis:

### Weekly Processing Notebooks

- `aggregate_to_weekly_nighttime.ipynb` → `../../data/processed_weekly/weekly_nighttime_recovery.nc`
- `aggregate_to_weekly_daytime.ipynb` → `../../data/processed_weekly/weekly_daytime_heat.nc`
- `aggregate_to_weekly_vpd.ipynb` → `../../data/processed_weekly/weekly_vpd.nc`

### Weekly Aggregation Method

**Temperature metrics:** SUM of daily hour counts across 7 days
- Example: `hours_above_30` (weekly) = sum of 7 daily hour counts
- Range: 0 to 84 hours per week (7 days × 12 daytime hours)

**VPD metrics:** MEAN of daily means across 7 days
- Example: `vpd_mean` (weekly) = average of 7 daily mean values
- Range: Same as daily (0.0-15.0 kPa)

### Weekly Files Used For

- Time series analysis (reduced noise vs daily data)
- Correlation with USDA weekly cattle slaughter data
- Seasonal/annual trend analysis
- State/regional aggregations

---

## Quality Control & Validation

### Validation Checks Implemented

**1. Daytime Heat:**
- Max value ≤ 12 hours (daytime window duration)
- No negative values (except fill value -1)

**2. Nighttime Recovery:**
- Max value ≤ 10 hours (nighttime window duration)
- No negative values (except fill value -1)
- Complementary thresholds sum correctly (hours_above + hours_below ≤ 10)

**3. VPD:**
- Negative values clamped to 0 (VPD cannot be negative)
- Warning if values > 15.0 kPa (extremely rare, desert extremes)
- Mean value between min and max (vpd_min ≤ vpd_mean ≤ vpd_max)

### Missing Data Handling

- **Input file missing:** Output day filled with fill value
- **US state mask:** Non-US areas always set to fill value
- **Temperature:** -1 (int16)
- **VPD:** NaN (float32)

---

## Usage Examples

### Example 1: Load and Plot Summer Heat Stress for Texas (2023)

```python
import xarray as xr
import matplotlib.pyplot as plt

# Load summer months
ds_jun = xr.open_dataset('../../data/processed_daytime_heat/daytime_heat_202306.nc')
ds_jul = xr.open_dataset('../../data/processed_daytime_heat/daytime_heat_202307.nc')
ds_aug = xr.open_dataset('../../data/processed_daytime_heat/daytime_heat_202308.nc')

# Combine
ds_summer = xr.concat([ds_jun, ds_jul, ds_aug], dim='time')

# Subset to Texas (approximately)
texas = ds_summer.sel(lat=slice(25.5, 36.5), lon=slice(-106.5, -93.5))

# Calculate average summer heat stress
avg_hot_hours = texas['hours_above_30'].mean(dim='time')

# Plot
avg_hot_hours.plot(cmap='YlOrRd')
plt.title('Average Daytime Hours Above 30°C - Texas Summer 2023')
plt.show()
```

### Example 2: Calculate Monthly Nighttime Recovery Statistics

```python
import xarray as xr
import pandas as pd

# Load one month
ds = xr.open_dataset('../../data/processed_nighttime_recovery/nighttime_recovery_202307.nc')

# Calculate percentage of nights with poor recovery (>6 hours above 24°C)
poor_recovery_pct = (ds['hours_above_24'] > 6).sum(dim='time') / len(ds.time) * 100

# Find maximum poor recovery location
max_location = poor_recovery_pct.argmax(dim=['lat', 'lon'])
max_lat = ds.lat[max_location['lat']].values
max_lon = ds.lon[max_location['lon']].values
max_pct = poor_recovery_pct.max().values

print(f"Worst nighttime recovery in July 2023:")
print(f"  Location: {max_lat}°N, {max_lon}°E")
print(f"  {max_pct:.1f}% of nights had very poor recovery (>6 hrs above 24°C)")
```

### Example 3: Multi-Year VPD Trend Analysis

```python
import xarray as xr
import numpy as np

# Load all July files 2010-2023
july_files = [f'../../data/processed_vpd/vpd_{year}07.nc' for year in range(2010, 2024)]
ds_list = [xr.open_dataset(f) for f in july_files]
ds_july = xr.concat(ds_list, dim='time')

# Calculate annual July mean VPD
vpd_july_mean = ds_july['vpd_mean'].mean(dim=['time', 'lat', 'lon'])

# Compute trend
years = np.arange(2010, 2024)
trend = np.polyfit(years, vpd_july_mean.values, 1)
print(f"July VPD trend: {trend[0]:.4f} kPa/year")
```

### Example 4: Compound Stress Analysis (Heat + VPD)

```python
import xarray as xr

# Load same month for both datasets
ds_heat = xr.open_dataset('../../data/processed_daytime_heat/daytime_heat_202307.nc')
ds_vpd = xr.open_dataset('../../data/processed_vpd/vpd_202307.nc')

# Define compound stress: high heat (>8 hrs above 30°C) AND high VPD (>2.5 kPa)
high_heat = ds_heat['hours_above_30'] > 8
high_vpd = ds_vpd['vpd_mean'] > 2.5

compound_stress = high_heat & high_vpd

# Count compound stress days
compound_days = compound_stress.sum(dim='time')

compound_days.plot(cmap='Reds')
plt.title('Compound Stress Days (High Heat + High VPD) - July 2023')
plt.show()
```

---

## Citations & References

### Data Source

**MERRA-2:** Modern-Era Retrospective analysis for Research and Applications, Version 2

> Gelaro, R., et al. (2017). The Modern-Era Retrospective Analysis for Research and Applications, Version 2 (MERRA-2). *Journal of Climate*, 30(14), 5419-5454. https://doi.org/10.1175/JCLI-D-16-0758.1

### Collection Details

- **M2T1NXSLV:** MERRA-2 tavg1_2d_slv_Nx (Single-Level Diagnostics)
- **Temporal Resolution:** Hourly
- **Spatial Resolution:** 0.5° × 0.625° (latitude × longitude)
- **Variables Used:** T2M (2-meter temperature), QV2M (specific humidity), PS (surface pressure), VPD (derived)

### Processing Tools

- **CDO** (Climate Data Operators): Spatial subsetting and calculations
- **NCO** (netCDF Operators): Format conversion and compression
- **xarray/Python:** Statistical processing and NetCDF file creation

### Project

**Livestock and Heat Stress Analysis**
VEDA Story: Impact of heat stress on US cattle production
**Period:** 1984-2025 (41 years)
**Regions:** USDA Cattle Slaughter Regions 4 (Southeast) and 6 (South Central)

---

## Version History

### Version 1.0 (2026-03-31)

- Initial documentation of processing outputs
- Covers daytime heat, nighttime recovery, and VPD statistics
- Monthly files with daily resolution
- 504 files per dataset (1984-2025)

---

## Contact & Support

### For Questions About These Datasets

- See [CLAUDE.md](../../CLAUDE.md) in project root for methodology
- See [ANALYSIS_MATRIX.md](../03_analysis/ANALYSIS_MATRIX.md) for analysis combinations
- Check notebook comments for processing details

### Data Issues

- **Missing files:** Check `../../data/daily_data/` input directory
- **Unusual values:** Review validation checks in processing notebooks
- **Coordinate mismatches:** Verify `../../data/masks/region_mask.nc` is correct version

---

*End of Document*
