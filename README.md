# Livestock and Heat - MERRA-2 Climate Analysis

Analysis of heat stress impacts on livestock using MERRA-2 climate reanalysis data and USDA cattle slaughter records.

## Setup

### 1. Install Dependencies

```bash
pip install python-dotenv xarray netcdf4 pandas numpy matplotlib seaborn cartopy scipy statsmodels tqdm earthaccess
```

Or install from requirements file (if available):
```bash
pip install -r requirements.txt
```

### 2. Configure Data Paths

The project uses environment variables to manage data directory paths. This keeps personal file system paths out of version control.

**Create your `.env` file:**

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your actual paths
nano .env  # or use your preferred editor
```

**Example `.env` configuration:**

```bash
# If your data is in the default location (research/ subdirectories)
# You don't need to set anything - defaults will work

# If your data is elsewhere, set absolute paths:
PROJECT_ROOT=/Users/yourname/livestock_and_heat/research
DAILY_DATA_DIR=/Volumes/ExternalDrive/merra2/daily_data
PROCESSED_WEEKLY_DIR=/Users/yourname/processed_weekly
```

**Path variables available:**
- `PROJECT_ROOT` - Project root directory (defaults to location of config.py)
- `DAILY_DATA_DIR` - Raw MERRA-2 temperature/VPD data
- `DAILY_DATA_SOIL_PRECIP_DIR` - Raw MERRA-2 soil/precipitation data
- `PROCESSED_NIGHTTIME_DIR` - Daily nighttime recovery statistics
- `PROCESSED_DAYTIME_DIR` - Daily daytime heat statistics
- `PROCESSED_VPD_DIR` - Daily VPD statistics
- `PROCESSED_WEEKLY_DIR` - Weekly aggregated data
- `MASKS_DIR` - Spatial masks and region definitions
- `CATTLE_DATA_DIR` - USDA cattle slaughter data
- `FIGURES_DIR` - Output figures directory
- `IMAGES_DIR` - Output images directory

**Note:** All paths are optional. If not specified, the project uses relative paths from the project root.

### 3. Run Notebooks

See [notebooks/README.md](notebooks/README.md) for detailed workflow documentation.

**Quick start workflow:**

1. **Data Ingestion** (download MERRA-2 data):
   ```
   notebooks/01_data_ingestion/process_merra2_cdo_t2m_vpd.ipynb
   ```

2. **Data Processing** (compute daily statistics):
   ```
   notebooks/02_data_processing/process_nighttime_recovery_stats.ipynb
   notebooks/02_data_processing/process_daytime_heat_stats.ipynb
   notebooks/02_data_processing/process_vpd_stats.ipynb
   ```

3. **Weekly Aggregation** (**REQUIRED** before analysis):
   ```
   notebooks/02_data_processing/aggregate_weekly_cattle_aligned.ipynb
   ```

4. **Analysis** (exploratory analysis):
   ```
   notebooks/03_analysis/01_temporal_analysis.ipynb
   notebooks/03_analysis/02_spatial_analysis.ipynb
   ... (and others)
   ```

## Project Structure

```
research/
├── config.py                    # Centralized configuration (import from all notebooks)
├── .env                         # Your local paths (gitignored)
├── .env.example                 # Example configuration (committed)
├── notebooks/                   # All Jupyter notebooks
│   ├── 01_data_ingestion/      # Download MERRA-2 data
│   ├── 02_data_processing/     # Compute statistics
│   ├── 03_analysis/            # Exploratory analysis
│   └── 04_visualization/       # Plotting
├── daily_data/                  # Raw MERRA-2 T2M/VPD (gitignored)
├── processed_weekly/            # Weekly aggregated data (gitignored)
├── cattle_data/                 # USDA slaughter data (gitignored)
├── masks/                       # Region masks
└── figures/                     # Generated plots
```

## Configuration Module

All notebooks import from `config.py` for consistent paths and definitions:

```python
import sys
from pathlib import Path
sys.path.append(str(Path('../..')))  # Adjust based on notebook location

from config import (
    PROCESSED_WEEKLY_DIR,
    CATTLE_DATA_FILE,
    MASKS_DIR,
    FOCUS_STATES,
    SEASONS
)
```

This ensures:
- Consistent data paths across all notebooks
- Centralized state/region definitions
- Easy path customization via `.env`

## Data Sources

- **Climate Data**: MERRA-2 (Modern-Era Retrospective analysis for Research and Applications, Version 2)
  - Collection: M2T1NXSLV (Single-Level Diagnostics)
  - Variables: Temperature (T2M), Vapor Pressure Deficit (VPD)
  - Period: 1984-2025
  - Resolution: Hourly, 0.5° × 0.625°

- **Cattle Data**: USDA National Agricultural Statistics Service (NASS)
  - Weekly cattle slaughter by region
  - Period: 1984-2025
  - Reporting weeks end on Saturday

## Documentation

- [CLAUDE.md](CLAUDE.md) - Technical documentation and processing details
- [notebooks/README.md](notebooks/README.md) - Notebook organization and workflow
- [.clinerules.md](.clinerules.md) - Project coding guidelines

## Notes

- `.env` file is gitignored to protect personal file paths
- All large data files (`.nc`, `.xlsx`) are gitignored
- Weekly aggregated data must be generated before running analysis notebooks
- Climate data aligns with USDA cattle slaughter reporting weeks (Saturday ending)
