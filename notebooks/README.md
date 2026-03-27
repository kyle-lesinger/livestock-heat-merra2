# Notebooks Directory

This directory contains all Jupyter notebooks for the Livestock and Heat project, organized by workflow stage.

## Directory Structure

```
notebooks/
├── 01_data_ingestion/      # Download and initial data collection
├── 02_data_processing/     # Transform and compute statistics
├── 03_analysis/            # Exploratory analysis and testing
├── 04_visualization/       # Plot generation and figures
└── README.md              # This file
```

## Workflow Overview

### 1. Data Ingestion (01_data_ingestion/)

**Purpose**: Download raw MERRA-2 climate reanalysis data from NASA EarthData

- **process_merra2_cdo_t2m_vpd.ipynb** - Download temperature and vapor pressure deficit
  - Collection: M2T1NXSLV (Single-Level Diagnostics)
  - Variables: T2M (temperature), VPD (vapor pressure deficit)
  - Output: `../daily_data/merra2_us_YYYYMMDD.nc`
  - Status: Production-ready

- **process_merra2_soil_precip_cdo.ipynb** - Download soil moisture and precipitation
  - Collection: M2T1NXLND (Land Surface Diagnostics)
  - Variables: SFMC, RZMC, PRMC, GWETROOT, GWETTOP, PRECIP_TOTAL, PRECIP_SNOW
  - Output: `../daily_data_soil_precip/merra2_soil_precip_us_YYYYMMDD.nc`
  - Status: Production-ready

### 2. Data Processing (02_data_processing/)

**Purpose**: Transform raw data into analysis-ready formats and compute derived statistics

- **process_cattle_data.ipynb** - Process USDA cattle slaughter data
  - Input: `../cattle_data/Dcowslt-13.xlsx`
  - Output: `../cattle_data/cattle_data_long.csv`
  - Transforms: Reshape to long format, extract regional data

- **process_nighttime_recovery_stats.ipynb** - Compute nighttime temperature recovery metrics
  - Input: `../daily_data/merra2_us_*.nc`
  - Output: `../processed_nighttime_recovery/region_*_nighttime_recovery_stats.nc`
  - Metrics: Minimum nighttime temperature, recovery duration, cooling rate

- **process_daytime_heat_stats.ipynb** - Compute daytime heat stress metrics
  - Input: `../daily_data/merra2_us_*.nc`
  - Output: `../processed_daytime_heat/region_*_daytime_heat_stats.nc`
  - Metrics: Maximum daytime temperature, heat duration, heat intensity

- **process_vpd_stats.ipynb** - Compute vapor pressure deficit statistics
  - Input: `../daily_data/merra2_us_*.nc`
  - Output: `../processed_vpd/region_*_vpd_stats.nc`
  - Metrics: Daily mean, max, and duration above thresholds

### 3. Analysis (03_analysis/)

**Purpose**: Exploratory analysis and hypothesis testing notebooks

- **01_temporal_analysis.ipynb** - Time series analysis of heat metrics
  - Trends, seasonality, anomalies over time

- **02_spatial_analysis.ipynb** - Geographic patterns in heat stress
  - Regional differences, spatial autocorrelation

- **03_threshold_duration_analysis.ipynb** - Heat stress threshold analysis
  - Duration above critical thresholds, threshold sensitivity

- **04_multivariate_relationships.ipynb** - Relationships between variables
  - Temperature-VPD correlations, soil moisture effects

- **05_extreme_events_anomalies.ipynb** - Extreme heat event detection
  - Identify and characterize heat waves, anomaly detection

### 4. Visualization (04_visualization/)

**Purpose**: Generate publication-ready figures and plots

- **plot_region_state_data.ipynb** - Regional and state-level plotting
  - Time series plots, heatmaps, summary statistics
  - Output: `../figures/` and `../images/`

## Data Dependencies

All notebooks assume the following directory structure relative to the `research/` root:

```
research/
├── notebooks/              # This directory
├── daily_data/             # MERRA-2 T2M/VPD hourly files
├── daily_data_soil_precip/ # MERRA-2 soil/precip hourly files
├── cattle_data/            # USDA livestock data
├── masks/                  # Spatial region masks
├── processed_nighttime_recovery/  # Nighttime statistics
├── processed_daytime_heat/        # Daytime statistics
├── processed_vpd/                 # VPD statistics
├── figures/                # Generated plots
└── images/                 # Generated images
```

## Path Conventions

All notebooks use **relative paths** with `../` to reference data directories:

```python
# Example: Data ingestion notebook
Path("../../daily_data")          # For notebooks two levels deep

# Example: Processing/analysis notebook
Path("../../daily_data")          # Same pattern
Path("../../masks/region_mask.nc")
```

## Running Notebooks

### Prerequisites

1. **Python Environment**:
   - earthaccess (NASA authentication)
   - xarray, pandas, numpy
   - matplotlib, cartopy (for visualization)
   - tqdm (progress bars)

2. **External Tools**:
   - CDO (Climate Data Operators): `brew install cdo`
   - NCO (NetCDF Operators): `brew install nco`

3. **NASA EarthData Account**:
   - Register at https://urs.earthdata.nasa.gov/
   - Authenticate using `earthaccess.login()`

### Execution Order

1. **Data Ingestion** (run once or to update data)
   - `01_data_ingestion/process_merra2_cdo_t2m_vpd.ipynb`
   - `01_data_ingestion/process_merra2_soil_precip_cdo.ipynb`

2. **Data Processing** (compute derived statistics)
   - `02_data_processing/process_cattle_data.ipynb`
   - `02_data_processing/process_nighttime_recovery_stats.ipynb`
   - `02_data_processing/process_daytime_heat_stats.ipynb`
   - `02_data_processing/process_vpd_stats.ipynb`

3. **Analysis & Visualization** (exploratory, run in any order)
   - `03_analysis/*.ipynb`
   - `04_visualization/*.ipynb`

## Notes

- All data ingestion notebooks include skip logic - rerunning only processes missing dates
- Processing notebooks are idempotent - safe to rerun
- Analysis notebooks are self-contained and can be run independently
- See main project [CLAUDE.md](../CLAUDE.md) for detailed technical documentation
