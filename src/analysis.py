"""
Analysis Utilities

Common analysis functions used across notebooks for loading, processing,
and analyzing heat stress data.
"""

from typing import Optional, Tuple, Dict, List
from pathlib import Path
import numpy as np
import pandas as pd
import xarray as xr
from scipy import stats


def load_weekly_data(
    processed_weekly_dir: Path,
    cattle_data_file: Path
) -> Tuple[xr.Dataset, xr.Dataset, xr.Dataset, np.ndarray]:
    """
    Load weekly aggregated climate data files.

    Returns datasets aligned to the available climate data weeks.
    Climate data goes through end of 2025; cattle data extends to 2027.

    Automatically converts timedelta64 variables (hours stored as nanoseconds)
    to float hours for easier interpretation and plotting.

    Parameters
    ----------
    processed_weekly_dir : Path
        Directory containing weekly aggregated NetCDF files
    cattle_data_file : Path
        Path to cattle slaughter CSV file

    Returns
    -------
    tuple
        (ds_night, ds_day, ds_vpd, week_dates)
        - ds_night: Weekly nighttime recovery dataset (hours as float)
        - ds_day: Weekly daytime heat dataset (hours as float)
        - ds_vpd: Weekly VPD dataset (kPa as float)
        - week_dates: Array of week-ending dates

    Notes
    -----
    Temperature threshold variables (hours_above_*, hours_below_*) are
    converted from timedelta64[ns] to float hours for better usability.
    Weekly values represent total hours per week (0-168 for all-day metrics,
    0-70 for nighttime-only metrics).

    Examples
    --------
    >>> from pathlib import Path
    >>> import config
    >>> ds_night, ds_day, ds_vpd, weeks = load_weekly_data(
    ...     config.PROCESSED_WEEKLY_DIR,
    ...     config.CATTLE_DATA_FILE
    ... )
    >>> print(f"Loaded {len(weeks)} weeks of data")
    >>> print(f"Max weekly hours above 30°C: {ds_day['hours_above_30'].max().values:.1f}")
    """
    # Load weekly climate data files
    ds_night = xr.open_dataset(processed_weekly_dir / 'weekly_nighttime_recovery.nc')
    ds_day = xr.open_dataset(processed_weekly_dir / 'weekly_daytime_heat.nc')
    ds_vpd = xr.open_dataset(processed_weekly_dir / 'weekly_vpd.nc')

    # Convert timedelta64 variables to float hours for better usability
    # (Weekly data files store hours as timedelta64[ns] which shows as huge numbers)
    for ds in [ds_night, ds_day]:
        for var in ds.data_vars:
            if ds[var].dtype.kind == 'm':  # 'm' indicates timedelta type
                # Convert nanoseconds to hours
                ds[var] = ds[var] / np.timedelta64(1, 'h')
                # Update units attribute
                ds[var].attrs['units'] = 'hours'
                ds[var].attrs['note'] = 'Converted from timedelta64 to float hours'

    # Get week dates from climate data
    week_dates = ds_night['week'].values
    n_weeks = len(week_dates)

    print(f"Climate data coverage: {n_weeks} weeks")
    print(f"  From: {pd.to_datetime(week_dates[0]).date()}")
    print(f"  To: {pd.to_datetime(week_dates[-1]).date()}")

    # Load cattle data and filter to matching weeks
    cattle_df = pd.read_csv(cattle_data_file)
    cattle_df['date'] = pd.to_datetime(cattle_df['date'])

    # Find overlapping weeks
    cattle_in_range = cattle_df[
        (cattle_df['date'] >= pd.to_datetime(week_dates[0])) &
        (cattle_df['date'] <= pd.to_datetime(week_dates[-1]))
    ].copy()

    print(f"\nCattle data: {len(cattle_df)} total weeks")
    print(f"  Overlapping with climate data: {len(cattle_in_range)} weeks")

    if len(cattle_in_range) != n_weeks:
        print(f"\nWARNING: Week count mismatch - using climate data weeks as authoritative")

    # Add convenience coordinates for time series analysis
    for ds in [ds_night, ds_day, ds_vpd]:
        ds.coords['week_date'] = ds['week']
        ds.coords['year'] = ('week', pd.to_datetime(week_dates).year)
        ds.coords['month'] = ('week', pd.to_datetime(week_dates).month)
        ds.coords['week_number'] = ('week', np.arange(len(week_dates)))

    return ds_night, ds_day, ds_vpd, week_dates


def compute_state_mean(
    data: xr.DataArray,
    state_id: int,
    state_mask: xr.DataArray
) -> xr.DataArray:
    """
    Compute spatial mean for a specific state.

    Works with weekly data (week, lat, lon dimensions).

    Parameters
    ----------
    data : xr.DataArray
        Climate data with dimensions (week, lat, lon)
    state_id : int
        State ID from region mask
    state_mask : xr.DataArray
        State mask array with state IDs

    Returns
    -------
    xr.DataArray
        State-averaged time series

    Examples
    --------
    >>> import xarray as xr
    >>> from config import FOCUS_STATES, MASK_FILE
    >>> mask_ds = xr.open_dataset(MASK_FILE)
    >>> state_mask = mask_ds.state_mask.load()
    >>> mask_ds.close()
    >>> state_mean = compute_state_mean(ds_day['hours_above_30'],
    ...                                  FOCUS_STATES['Texas'],
    ...                                  state_mask)
    """
    mask = state_mask == state_id
    masked_data = data.where(mask)
    state_mean = masked_data.mean(dim=['lat', 'lon'])
    return state_mean.astype(np.float64)


def compute_state_stats(
    data: xr.DataArray,
    state_id: int,
    state_mask: xr.DataArray
) -> Dict[str, xr.DataArray]:
    """
    Compute multiple statistics for a specific state.

    Parameters
    ----------
    data : xr.DataArray
        Climate data with dimensions (week, lat, lon)
    state_id : int
        State ID from region mask
    state_mask : xr.DataArray
        State mask array with state IDs

    Returns
    -------
    dict
        Dictionary with keys: 'mean', 'std', 'min', 'max', 'median'

    Examples
    --------
    >>> stats = compute_state_stats(ds_day['hours_above_30'],
    ...                              FOCUS_STATES['Texas'],
    ...                              state_mask)
    >>> print(f"Mean: {stats['mean'].values[0]:.1f}")
    """
    mask = state_mask == state_id
    masked_data = data.where(mask)

    return {
        'mean': masked_data.mean(dim=['lat', 'lon']).astype(np.float64),
        'std': masked_data.std(dim=['lat', 'lon']).astype(np.float64),
        'min': masked_data.min(dim=['lat', 'lon']).astype(np.float64),
        'max': masked_data.max(dim=['lat', 'lon']).astype(np.float64),
        'median': masked_data.median(dim=['lat', 'lon']).astype(np.float64),
    }


def mann_kendall_test(x: np.ndarray) -> Dict[str, float]:
    """
    Perform Mann-Kendall trend test for time series data.

    The Mann-Kendall test is a non-parametric test for detecting monotonic trends
    in time series data. It's robust to outliers and doesn't assume normality.

    Parameters
    ----------
    x : np.ndarray
        Time series data (1D array)

    Returns
    -------
    dict
        Dictionary with keys:
        - 'z': Z-statistic (positive = increasing trend)
        - 'p': Two-tailed p-value
        - 'trend': 'increasing' or 'decreasing'

    Notes
    -----
    - p < 0.05 indicates statistically significant trend at 95% confidence
    - z > 0: increasing trend, z < 0: decreasing trend

    Examples
    --------
    >>> annual_temps = np.array([20.1, 20.3, 20.5, 20.4, 20.8, 21.0, 21.2])
    >>> result = mann_kendall_test(annual_temps)
    >>> if result['p'] < 0.05:
    ...     print(f"Significant {result['trend']} trend (p={result['p']:.3f})")
    """
    n = len(x)
    s = 0
    for i in range(n-1):
        for j in range(i+1, n):
            s += np.sign(x[j] - x[i])

    var_s = n * (n-1) * (2*n+5) / 18
    z = s / np.sqrt(var_s) if var_s > 0 else 0
    p_value = 2 * (1 - stats.norm.cdf(abs(z)))

    return {
        'z': float(z),
        'p': float(p_value),
        'trend': 'increasing' if z > 0 else 'decreasing'
    }


def get_season(month: int, seasons: Dict[str, List[int]]) -> Optional[str]:
    """
    Get season name from month number.

    Parameters
    ----------
    month : int
        Month number (1-12)
    seasons : dict
        Dictionary mapping season names to month lists
        (typically from config.SEASONS)

    Returns
    -------
    str or None
        Season name ('Winter', 'Spring', 'Summer', 'Fall') or None

    Examples
    --------
    >>> from config import SEASONS
    >>> season = get_season(7, SEASONS)
    >>> print(season)  # 'Summer'
    """
    for season, months in seasons.items():
        if month in months:
            return season
    return None


def resample_to_monthly(
    weekly_data: xr.DataArray,
    week_dates: np.ndarray,
    method: str = 'mean'
) -> pd.Series:
    """
    Resample weekly data to monthly for visualizations.

    Parameters
    ----------
    weekly_data : xr.DataArray
        Weekly time series data
    week_dates : np.ndarray
        Array of week-ending dates
    method : str, default='mean'
        Aggregation method: 'mean', 'sum', 'max', 'min'

    Returns
    -------
    pd.Series
        Monthly resampled data indexed by end-of-month dates

    Examples
    --------
    >>> monthly_temps = resample_to_monthly(state_temps, week_dates, method='mean')
    >>> print(monthly_temps.head())
    """
    df = pd.DataFrame({
        'date': pd.to_datetime(week_dates),
        'value': weekly_data.values
    })
    df = df.set_index('date')

    if method == 'mean':
        return df['value'].resample('ME').mean()
    elif method == 'sum':
        return df['value'].resample('ME').sum()
    elif method == 'max':
        return df['value'].resample('ME').max()
    elif method == 'min':
        return df['value'].resample('ME').min()
    else:
        raise ValueError(f"Unknown method: {method}. Use 'mean', 'sum', 'max', or 'min'")


def normalize(data: np.ndarray, method: str = 'zscore') -> np.ndarray:
    """
    Normalize data array.

    Parameters
    ----------
    data : np.ndarray
        Data to normalize
    method : str, default='zscore'
        Normalization method: 'zscore', 'minmax', or 'robust'

    Returns
    -------
    np.ndarray
        Normalized data

    Notes
    -----
    - 'zscore': (x - mean) / std (standardization)
    - 'minmax': (x - min) / (max - min) (scales to [0, 1])
    - 'robust': (x - median) / IQR (robust to outliers)

    Examples
    --------
    >>> temps = np.array([20, 25, 30, 35, 40])
    >>> norm_temps = normalize(temps, method='minmax')
    >>> print(norm_temps)  # [0.0, 0.25, 0.5, 0.75, 1.0]
    """
    if method == 'zscore':
        return (data - np.nanmean(data)) / np.nanstd(data)
    elif method == 'minmax':
        min_val = np.nanmin(data)
        max_val = np.nanmax(data)
        return (data - min_val) / (max_val - min_val)
    elif method == 'robust':
        median = np.nanmedian(data)
        q75 = np.nanpercentile(data, 75)
        q25 = np.nanpercentile(data, 25)
        iqr = q75 - q25
        return (data - median) / iqr if iqr > 0 else np.zeros_like(data)
    else:
        raise ValueError(f"Unknown method: {method}. Use 'zscore', 'minmax', or 'robust'")


def identify_heatwaves(
    temperature_data: xr.DataArray,
    threshold: float,
    min_duration: int = 3,
    max_gap: int = 1
) -> List[Tuple[pd.Timestamp, pd.Timestamp, int]]:
    """
    Identify heatwave events in temperature time series.

    A heatwave is defined as a period where temperature exceeds a threshold
    for at least `min_duration` consecutive time steps (weeks).

    Parameters
    ----------
    temperature_data : xr.DataArray
        Temperature time series with 'week_date' coordinate
    threshold : float
        Temperature threshold
    min_duration : int, default=3
        Minimum consecutive weeks above threshold
    max_gap : int, default=1
        Maximum gap (weeks) allowed within a heatwave

    Returns
    -------
    list of tuples
        Each tuple: (start_date, end_date, duration_weeks)

    Examples
    --------
    >>> heatwaves = identify_heatwaves(state_temps, threshold=30, min_duration=3)
    >>> for start, end, duration in heatwaves:
    ...     print(f"Heatwave: {start.date()} to {end.date()} ({duration} weeks)")
    """
    # Find weeks exceeding threshold
    above_threshold = temperature_data > threshold

    # Convert to pandas for easier manipulation
    df = pd.DataFrame({
        'date': pd.to_datetime(temperature_data['week_date'].values),
        'above': above_threshold.values
    })

    heatwaves = []
    start_idx = None
    consecutive_count = 0
    gap_count = 0

    for i in range(len(df)):
        if df.iloc[i]['above']:
            if start_idx is None:
                start_idx = i
                consecutive_count = 1
                gap_count = 0
            else:
                consecutive_count += 1
                gap_count = 0
        else:
            if start_idx is not None:
                gap_count += 1
                if gap_count > max_gap:
                    # End of heatwave
                    if consecutive_count >= min_duration:
                        heatwaves.append((
                            df.iloc[start_idx]['date'],
                            df.iloc[i - gap_count]['date'],
                            consecutive_count
                        ))
                    start_idx = None
                    consecutive_count = 0
                    gap_count = 0

    # Check if heatwave extends to end of series
    if start_idx is not None and consecutive_count >= min_duration:
        heatwaves.append((
            df.iloc[start_idx]['date'],
            df.iloc[-1]['date'],
            consecutive_count
        ))

    return heatwaves
