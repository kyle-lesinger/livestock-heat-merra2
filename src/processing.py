"""
MERRA-2 Data Processing Functions

Functions for processing hourly MERRA-2 data into daily threshold statistics.
Supports daytime heat, nighttime recovery, and VPD calculations.
"""

from typing import Optional, Dict, List, Tuple, Callable
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import xarray as xr
from tqdm.notebook import tqdm
import os


def load_us_mask(
    mask_path: Path,
    expected_shape: Optional[Tuple[int, int]] = None
) -> Optional[np.ndarray]:
    """
    Load US state mask from NetCDF file.

    Parameters
    ----------
    mask_path : Path
        Path to region_mask.nc file
    expected_shape : tuple of int, optional
        Expected (n_lat, n_lon) dimensions for validation

    Returns
    -------
    np.ndarray or None
        Boolean mask array (True for US states), or None if mask cannot be loaded

    Examples
    --------
    >>> from pathlib import Path
    >>> mask = load_us_mask(Path('masks/region_mask.nc'), expected_shape=(51, 95))
    >>> print(f"US states cover {mask.sum()} grid cells")
    """
    if not mask_path.exists():
        print(f"Warning: Region mask file not found at {mask_path}")
        print("Processing without spatial masking.")
        return None

    try:
        ds_mask = xr.open_dataset(mask_path)
        state_mask = ds_mask.state_mask.values
        ds_mask.close()

        # Create boolean mask: True for US states (state_mask > 0)
        us_mask = state_mask > 0

        # Verify dimensions if expected shape provided
        if expected_shape is not None and us_mask.shape != expected_shape:
            print(f"Warning: Mask dimensions {us_mask.shape} don't match "
                  f"data dimensions {expected_shape}")
            print("Processing without spatial masking.")
            return None

        return us_mask

    except Exception as e:
        print(f"Warning: Error loading region mask: {e}")
        print("Processing without spatial masking.")
        return None


def compute_daily_daytime_stats(
    date: datetime,
    input_dir: Path,
    daytime_hours: List[int] = None
) -> Optional[Dict[str, np.ndarray]]:
    """
    Compute daytime heat/cold statistics for a single day.

    Parameters
    ----------
    date : datetime
        Date to process
    input_dir : Path
        Directory containing daily MERRA-2 NetCDF files
    daytime_hours : list of int, optional
        Hours to consider as daytime (default: 8-19 UTC for 8am-8pm)

    Returns
    -------
    dict or None
        Dictionary with metric names as keys and 2D arrays (lat, lon) as values,
        or None if file is missing

    Notes
    -----
    Computes hour counts for temperature thresholds:
    - hours_above_25, hours_above_30, hours_above_35, hours_above_40
    - hours_below_neg5, hours_below_0, hours_below_5

    Examples
    --------
    >>> from datetime import datetime
    >>> stats = compute_daily_daytime_stats(
    ...     datetime(2020, 6, 15),
    ...     Path('daily_data/')
    ... )
    >>> if stats:
    ...     print(f"Max hours above 30°C: {stats['hours_above_30'].max()}")
    """
    if daytime_hours is None:
        daytime_hours = list(range(8, 20))  # 8am-8pm UTC (hours 8-19)

    date_str = date.strftime('%Y%m%d')
    file_path = input_dir / f'merra2_us_{date_str}.nc'

    if not file_path.exists():
        return None

    try:
        ds = xr.open_dataset(file_path)
        # Extract daytime hours
        temp = ds.T2M.isel(time=daytime_hours).values  # shape: (n_hours, lat, lon)
        ds.close()

        # Compute threshold counts across daytime hours
        stats = {
            'hours_above_25': np.sum(temp > 25, axis=0).astype(np.int16),
            'hours_above_30': np.sum(temp > 30, axis=0).astype(np.int16),
            'hours_above_35': np.sum(temp > 35, axis=0).astype(np.int16),
            'hours_above_40': np.sum(temp > 40, axis=0).astype(np.int16),
            'hours_below_neg5': np.sum(temp < -5, axis=0).astype(np.int16),
            'hours_below_0': np.sum(temp < 0, axis=0).astype(np.int16),
            'hours_below_5': np.sum(temp < 5, axis=0).astype(np.int16),
        }

        # Validation: ensure no value exceeds maximum daytime hours
        max_daytime_hours = len(daytime_hours)
        for metric, values in stats.items():
            max_val = np.max(values)
            if max_val > max_daytime_hours:
                raise ValueError(
                    f"Invalid value detected for {metric} on {date_str}: "
                    f"max value = {max_val} hours, but daytime window is only "
                    f"{max_daytime_hours} hours"
                )

        return stats

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None


def compute_daily_nighttime_stats(
    date: datetime,
    input_dir: Path,
    nighttime_hours: List[int] = None
) -> Optional[Dict[str, np.ndarray]]:
    """
    Compute nighttime recovery statistics for a single day.

    Parameters
    ----------
    date : datetime
        Date to process
    input_dir : Path
        Directory containing daily MERRA-2 NetCDF files
    nighttime_hours : list of int, optional
        Hours to consider as nighttime (default: 20-23, 0-5 UTC for 8pm-6am)

    Returns
    -------
    dict or None
        Dictionary with metric names as keys and 2D arrays (lat, lon) as values,
        or None if file is missing

    Notes
    -----
    Computes hour counts for temperature thresholds:
    - hours_below_18_above_0, hours_below_21_above_0, hours_below_24_above_0
    - hours_above_21, hours_above_24
    - hours_below_0, hours_below_neg5, hours_below_neg10

    Examples
    --------
    >>> from datetime import datetime
    >>> stats = compute_daily_nighttime_stats(
    ...     datetime(2020, 6, 15),
    ...     Path('daily_data/')
    ... )
    >>> if stats:
    ...     print(f"Strong recovery hours: {stats['hours_below_18_above_0'].mean():.1f}")
    """
    if nighttime_hours is None:
        nighttime_hours = list(range(20, 24)) + list(range(0, 6))  # 8pm-6am UTC

    date_str = date.strftime('%Y%m%d')
    file_path = input_dir / f'merra2_us_{date_str}.nc'

    if not file_path.exists():
        return None

    try:
        ds = xr.open_dataset(file_path)
        # Extract nighttime hours
        temp = ds.T2M.isel(time=nighttime_hours).values  # shape: (n_hours, lat, lon)
        ds.close()

        # Compute threshold counts across nighttime hours
        stats = {
            'hours_below_18_above_0': np.sum((temp < 18) & (temp > 0), axis=0).astype(np.int16),
            'hours_below_21_above_0': np.sum((temp < 21) & (temp > 0), axis=0).astype(np.int16),
            'hours_below_24_above_0': np.sum((temp < 24) & (temp > 0), axis=0).astype(np.int16),
            'hours_above_21': np.sum(temp > 21, axis=0).astype(np.int16),
            'hours_above_24': np.sum(temp > 24, axis=0).astype(np.int16),
            'hours_below_0': np.sum(temp < 0, axis=0).astype(np.int16),
            'hours_below_neg5': np.sum(temp < -5, axis=0).astype(np.int16),
            'hours_below_neg10': np.sum(temp < -10, axis=0).astype(np.int16),
        }

        # Validation: ensure no value exceeds maximum nighttime hours
        max_nighttime_hours = len(nighttime_hours)
        for metric, values in stats.items():
            max_val = np.max(values)
            if max_val > max_nighttime_hours:
                raise ValueError(
                    f"Invalid value detected for {metric} on {date_str}: "
                    f"max value = {max_val} hours, but nighttime window is only "
                    f"{max_nighttime_hours} hours"
                )

        return stats

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None


def compute_daily_vpd_stats(
    date: datetime,
    input_dir: Path,
    afternoon_hours: List[int] = None
) -> Optional[Dict[str, np.ndarray]]:
    """
    Compute afternoon VPD statistics for a single day.

    Parameters
    ----------
    date : datetime
        Date to process
    input_dir : Path
        Directory containing daily MERRA-2 NetCDF files
    afternoon_hours : list of int, optional
        Hours to consider as afternoon (default: 12-17 UTC for 12pm-6pm)

    Returns
    -------
    dict or None
        Dictionary with metric names as keys and 2D arrays (lat, lon) as values,
        or None if file is missing

    Notes
    -----
    Computes VPD statistics:
    - vpd_mean: Mean VPD during afternoon (kPa)
    - vpd_min: Minimum VPD during afternoon (kPa)
    - vpd_max: Maximum VPD during afternoon (kPa)

    Negative VPD values are clamped to 0 (small negative values can occur
    due to numerical precision in calculations).

    Examples
    --------
    >>> from datetime import datetime
    >>> stats = compute_daily_vpd_stats(
    ...     datetime(2020, 6, 15),
    ...     Path('daily_data/')
    ... )
    >>> if stats:
    ...     print(f"Mean afternoon VPD: {stats['vpd_mean'].mean():.2f} kPa")
    """
    if afternoon_hours is None:
        afternoon_hours = list(range(12, 18))  # 12pm-6pm UTC

    date_str = date.strftime('%Y%m%d')
    file_path = input_dir / f'merra2_us_{date_str}.nc'

    if not file_path.exists():
        return None

    try:
        ds = xr.open_dataset(file_path)
        # Extract afternoon hours
        vpd = ds.VPD.isel(time=afternoon_hours).values  # shape: (n_hours, lat, lon)
        ds.close()

        # Clamp negative VPD values to 0 (VPD cannot be negative by definition)
        vpd = np.maximum(vpd, 0.0)

        # Compute statistics across afternoon hours
        stats = {
            'vpd_mean': np.nanmean(vpd, axis=0).astype(np.float32),
            'vpd_min': np.nanmin(vpd, axis=0).astype(np.float32),
            'vpd_max': np.nanmax(vpd, axis=0).astype(np.float32),
        }

        # Validation: check for extremely high VPD values
        for metric, values in stats.items():
            max_val = np.nanmax(values)
            if max_val > 15.0:  # Warning threshold
                print(
                    f"Warning: Very high VPD detected for {metric} on {date_str}: "
                    f"max value = {max_val:.2f} kPa (typical range: 0-10 kPa)"
                )

        return stats

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None


def process_month(
    year: int,
    month: int,
    input_dir: Path,
    output_dir: Path,
    compute_stats_fn: Callable,
    metric_names: List[str],
    metric_descriptions: Dict[str, Tuple[str, str]],
    output_prefix: str,
    title: str,
    description: str,
    time_window_str: str,
    mask_path: Optional[Path] = None,
    use_int16: bool = True,
    fill_value: Optional[int] = -1,
    skip_existing: bool = True
) -> bool:
    """
    Process all days in a given month and save to NetCDF.

    Parameters
    ----------
    year : int
        Year to process
    month : int
        Month to process (1-12)
    input_dir : Path
        Directory containing daily MERRA-2 NetCDF files
    output_dir : Path
        Directory to save processed monthly files
    compute_stats_fn : callable
        Function(date, input_dir) -> dict that computes daily statistics
    metric_names : list of str
        Names of metrics to extract from compute_stats_fn output
    metric_descriptions : dict
        Mapping of metric name -> (long_name, description)
    output_prefix : str
        Prefix for output filename (e.g., 'daytime_heat', 'nighttime_recovery', 'vpd')
    title : str
        Dataset title for NetCDF metadata
    description : str
        Dataset description for NetCDF metadata
    time_window_str : str
        Human-readable time window description (e.g., '8-19 (UTC)')
    mask_path : Path, optional
        Path to region_mask.nc for spatial masking
    use_int16 : bool, default=True
        If True, use int16 dtype (for hour counts). If False, use float32 (for VPD)
    fill_value : int or None, default=-1
        Fill value for missing data. Use -1 for int16, None for float32 (uses NaN)
    skip_existing : bool, default=True
        If True, skip processing if output file already exists

    Returns
    -------
    bool
        True if successful, False otherwise

    Examples
    --------
    >>> from pathlib import Path
    >>> success = process_month(
    ...     year=2020,
    ...     month=6,
    ...     input_dir=Path('daily_data/'),
    ...     output_dir=Path('processed_daytime_heat/'),
    ...     compute_stats_fn=compute_daily_daytime_stats,
    ...     metric_names=['hours_above_25', 'hours_above_30'],
    ...     metric_descriptions={'hours_above_25': ('Hot conditions', 'Hours > 25C')},
    ...     output_prefix='daytime_heat',
    ...     title='MERRA-2 Daytime Heat Statistics',
    ...     description='Daily daytime temperature threshold hour counts',
    ...     time_window_str='8-19 (UTC)'
    ... )
    """
    output_file = output_dir / f'{output_prefix}_{year}{month:02d}.nc'

    # Skip if output file already exists
    if skip_existing and os.path.exists(output_file):
        print(f"Output file {output_file.name} already exists. Skipping.")
        return True

    # Generate all dates for the month
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = datetime(year, month + 1, 1) - timedelta(days=1)

    dates = pd.date_range(start_date, end_date, freq='D')
    n_days = len(dates)

    # Get lat/lon coordinates from first available file
    # Use utility function from src/utils.py
    from .utils import get_lat_lon_coords
    lat_coords, lon_coords = get_lat_lon_coords(input_dir, list(dates))

    if lat_coords is None:
        print(f"No valid input files found for {year}-{month:02d}")
        return False

    n_lat = len(lat_coords)
    n_lon = len(lon_coords)

    # Load US state mask if provided
    us_mask = None
    if mask_path is not None:
        us_mask = load_us_mask(mask_path, expected_shape=(n_lat, n_lon))

    # Initialize arrays for daily statistics
    if use_int16:
        daily_data = {metric: np.full((n_days, n_lat, n_lon), fill_value, dtype=np.int16)
                      for metric in metric_names}
    else:
        daily_data = {metric: np.full((n_days, n_lat, n_lon), np.nan, dtype=np.float32)
                      for metric in metric_names}

    # Process each day
    print(f"Processing {year}-{month:02d}: {n_days} days")
    for i, date in enumerate(tqdm(dates, desc=f"{year}-{month:02d}")):
        day_stats = compute_stats_fn(date, input_dir)
        if day_stats is not None:
            for metric in metric_names:
                daily_data[metric][i, :, :] = day_stats[metric]

                # Apply US mask: set non-US grid cells to fill value
                if us_mask is not None:
                    if use_int16:
                        daily_data[metric][i, ~us_mask] = fill_value
                    else:
                        daily_data[metric][i, ~us_mask] = np.nan

    # Create xarray Dataset
    ds_daily = xr.Dataset(
        data_vars={metric: (['time', 'lat', 'lon'], daily_data[metric])
                   for metric in metric_names},
        coords={
            'time': dates,
            'lat': lat_coords,
            'lon': lon_coords,
        }
    )

    # Add dataset metadata
    ds_daily.attrs['title'] = title
    ds_daily.attrs['description'] = description
    ds_daily.attrs['source'] = 'MERRA-2 M2T1NXSLV collection'
    ds_daily.attrs['time_window'] = time_window_str
    ds_daily.attrs['temporal_resolution'] = 'Daily'
    ds_daily.attrs['spatial_mask'] = 'US states only (state_mask > 0)'
    ds_daily.attrs['created'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Add variable metadata
    for metric, (long_name, desc) in metric_descriptions.items():
        if metric in ds_daily.data_vars:
            ds_daily[metric].attrs.update({
                'long_name': long_name,
                'units': 'hours' if use_int16 else 'kPa',
                'description': desc
            })

    # Save to NetCDF with compression
    if use_int16:
        encoding = {var: {'zlib': True, 'complevel': 4, 'dtype': 'int16', '_FillValue': fill_value}
                    for var in ds_daily.data_vars}
    else:
        encoding = {var: {'zlib': True, 'complevel': 4, 'dtype': 'float32'}
                    for var in ds_daily.data_vars}

    ds_daily.to_netcdf(output_file, encoding=encoding)
    ds_daily.close()

    print(f"Saved: {output_file.name}")
    return True
