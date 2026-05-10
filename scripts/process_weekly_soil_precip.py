"""
Process daily MERRA-2 soil moisture and precipitation to weekly aggregation.

Reads daily NetCDF files from data/daily_data_soil_precip/, computes daily
statistics (mean RZMC, total PRECIP), then aggregates to weekly (Saturday-ending)
matching USDA cattle reporting periods.

Output: data/processed_weekly/weekly_soil_precip.nc
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import xarray as xr
from datetime import datetime

# Project root
PROJECT_ROOT = Path('/Users/klesinger/Library/CloudStorage/GoogleDrive-kdl0040@uah.edu/My Drive/VEDA/Stories/livestock_and_heat/research')
sys.path.insert(0, str(PROJECT_ROOT))
import config

DAILY_DIR = config.DAILY_DATA_SOIL_PRECIP_DIR
OUTPUT_FILE = config.PROCESSED_WEEKLY_DIR / 'weekly_soil_precip.nc'

def process_daily_file(filepath):
    """Extract daily mean RZMC and daily total PRECIP from hourly file."""
    ds = xr.open_dataset(filepath)

    # Daily mean root zone soil moisture (average 24 hourly values)
    rzmc_daily_mean = ds['RZMC'].mean(dim='time').values

    # Daily total precipitation (sum 24 hourly values, already in mm/hr)
    # mm/hr * 1 hr per timestep = mm per timestep, sum = mm/day
    precip_daily_total = ds['PRECIP_TOTAL'].sum(dim='time').values

    lat = ds['lat'].values
    lon = ds['lon'].values

    ds.close()
    return rzmc_daily_mean, precip_daily_total, lat, lon


def main():
    print(f"Processing daily soil/precip to weekly aggregation")
    print(f"Input: {DAILY_DIR}")
    print(f"Output: {OUTPUT_FILE}")

    # Get all daily files
    daily_files = sorted(DAILY_DIR.glob('merra2_soil_precip_us_*.nc'))
    print(f"Found {len(daily_files)} daily files")

    if len(daily_files) == 0:
        print("ERROR: No daily files found")
        return

    # Parse dates from filenames
    dates = []
    for f in daily_files:
        date_str = f.stem.split('_')[-1]  # YYYYMMDD
        dates.append(pd.Timestamp(datetime.strptime(date_str, '%Y%m%d')))

    # Get lat/lon from first file
    _, _, lat, lon = process_daily_file(daily_files[0])
    n_lat, n_lon = len(lat), len(lon)
    print(f"Grid: {n_lat} lat x {n_lon} lon")

    # Process all daily files
    n_days = len(daily_files)
    rzmc_all = np.zeros((n_days, n_lat, n_lon), dtype=np.float32)
    precip_all = np.zeros((n_days, n_lat, n_lon), dtype=np.float32)

    print(f"Processing {n_days} days...")
    for i, fpath in enumerate(daily_files):
        if i % 1000 == 0:
            print(f"  {i}/{n_days} ({100*i/n_days:.0f}%)")

        rzmc_daily, precip_daily, _, _ = process_daily_file(fpath)
        rzmc_all[i] = rzmc_daily
        precip_all[i] = precip_daily

    print(f"  {n_days}/{n_days} (100%) done")

    # Create daily dataset
    daily_ds = xr.Dataset({
        'RZMC': (['time', 'lat', 'lon'], rzmc_all),
        'PRECIP_TOTAL': (['time', 'lat', 'lon'], precip_all),
    }, coords={
        'time': dates,
        'lat': lat,
        'lon': lon,
    })

    # Aggregate to weekly (Saturday-ending, matching USDA cattle weeks)
    # Assign each day to its week-ending Saturday
    week_endings = pd.Series(dates) + pd.offsets.Week(weekday=5)
    daily_ds.coords['week_ending'] = ('time', week_endings.values)

    print("Aggregating to weekly...")

    # RZMC: weekly MEAN of daily means
    rzmc_weekly = daily_ds['RZMC'].groupby('week_ending').mean(dim='time')

    # PRECIP_TOTAL: weekly SUM of daily totals
    precip_weekly = daily_ds['PRECIP_TOTAL'].groupby('week_ending').sum(dim='time')

    # Create weekly dataset
    weekly_ds = xr.Dataset({
        'RZMC': rzmc_weekly,
        'PRECIP_TOTAL': precip_weekly,
    })

    # Rename week_ending to 'week' for consistency with other weekly files
    weekly_ds = weekly_ds.rename({'week_ending': 'week'})

    # Add metadata
    weekly_ds['RZMC'].attrs = {
        'long_name': 'Root zone soil moisture (0-100cm)',
        'units': 'kg/m^2',
        'aggregation': 'weekly mean of daily means',
        'source': 'MERRA-2 M2T1NXLND',
    }
    weekly_ds['PRECIP_TOTAL'].attrs = {
        'long_name': 'Total precipitation',
        'units': 'mm/week',
        'aggregation': 'weekly sum of daily totals',
        'source': 'MERRA-2 M2T1NXLND (converted from mm/hr)',
    }

    n_weeks = len(weekly_ds['week'])
    print(f"Weekly dataset: {n_weeks} weeks, {n_lat} lat, {n_lon} lon")
    print(f"  RZMC range: [{float(weekly_ds['RZMC'].min()):.4f}, {float(weekly_ds['RZMC'].max()):.4f}]")
    print(f"  PRECIP range: [{float(weekly_ds['PRECIP_TOTAL'].min()):.4f}, {float(weekly_ds['PRECIP_TOTAL'].max()):.4f}]")

    # Save with compression
    encoding = {
        'RZMC': {'dtype': 'float32', 'zlib': True, 'complevel': 4},
        'PRECIP_TOTAL': {'dtype': 'float32', 'zlib': True, 'complevel': 4},
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    weekly_ds.to_netcdf(OUTPUT_FILE, encoding=encoding)

    file_size = OUTPUT_FILE.stat().st_size / 1024 / 1024
    print(f"\nSaved: {OUTPUT_FILE} ({file_size:.1f} MB)")

    # Cleanup
    daily_ds.close()
    weekly_ds.close()


if __name__ == '__main__':
    main()
