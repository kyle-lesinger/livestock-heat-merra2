"""
Aggregation Functions

Functions for spatial (regional) and temporal (weekly) aggregation of climate data.
"""

from typing import List
import xarray as xr
import pandas as pd


def aggregate_to_region(
    data_array: xr.DataArray,
    region_mask: xr.DataArray
) -> xr.DataArray:
    """
    Spatially aggregate a data array to a regional mean.

    Parameters
    ----------
    data_array : xarray.DataArray
        Gridded data to aggregate, typically with dimensions (time, lat, lon)
    region_mask : xarray.DataArray
        Boolean mask for the region with dimensions (lat, lon)
        True indicates grid cells to include in the regional average

    Returns
    -------
    xr.DataArray
        Time series of regional means with dimension (time,)

    Examples
    --------
    >>> # Aggregate daytime heat hours to region 4
    >>> day_30_regional = aggregate_to_region(ds['hours_above_30'], region_masks['region_4'])
    >>> print(f"Mean daytime heat hours: {day_30_regional.mean().item():.2f}")
    """
    # Apply mask and calculate mean over spatial dimensions
    masked_data = data_array.where(region_mask)
    regional_mean = masked_data.mean(dim=['lat', 'lon'], skipna=True)
    return regional_mean


def aggregate_to_weekly(daily_df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate daily metrics to weekly, matching USDA cattle week boundaries (ending Saturday).

    Parameters
    ----------
    daily_df : pd.DataFrame
        Daily metrics dataframe with columns:
        - 'date': Daily timestamps
        - 'region': Region identifier
        - Temperature threshold columns (e.g., 'night_bad_hrs', 'day_above_30c_hrs')
        - VPD columns (e.g., 'vpd_afternoon_mean')
        - TAS column (if present): 'tas'

    Returns
    -------
    pd.DataFrame
        Weekly aggregated metrics with columns:
        - 'region': Region identifier
        - 'week_ending': Saturday week-ending dates
        - Temperature thresholds (summed over week)
        - VPD metrics (averaged over week)
        - 'tas': Weekly mean TAS
        - 'tas_max': Weekly max TAS (if TAS present)

    Notes
    -----
    Aggregation rules:
    - Temperature threshold hours: SUM (total hours over the week)
    - VPD metrics: MEAN (average over the week)
    - TAS: MEAN and MAX (weekly average and peak acclimation)

    Examples
    --------
    >>> weekly_df = aggregate_to_weekly(daily_df)
    >>> print(f"Weekly data shape: {weekly_df.shape}")
    >>> print(f"Weeks: {len(weekly_df) // len(weekly_df['region'].unique())}")
    """
    # Create week-ending-Saturday grouper
    daily_df = daily_df.copy()  # Avoid modifying original
    daily_df['week_ending'] = daily_df['date'] + pd.offsets.Week(weekday=5)

    # Define aggregation rules
    agg_rules = {}

    # Temperature threshold hours: SUM
    temp_cols = [
        'night_strong_recovery_hrs', 'night_reasonable_recovery_hrs',
        'night_weak_recovery_hrs', 'night_poor_recovery_hrs', 'night_bad_hrs',
        'night_below_0c_hrs', 'night_below_neg5c_hrs', 'night_below_neg10c_hrs',
        'day_above_25c_hrs', 'day_above_30c_hrs', 'day_above_35c_hrs', 'day_above_40c_hrs',
        'day_below_5c_hrs', 'day_below_0c_hrs', 'day_below_neg5c_hrs'
    ]
    for col in temp_cols:
        if col in daily_df.columns:
            agg_rules[col] = 'sum'

    # VPD metrics: MEAN
    vpd_cols = ['vpd_afternoon_mean', 'vpd_afternoon_max', 'vpd_afternoon_min']
    for col in vpd_cols:
        if col in daily_df.columns:
            agg_rules[col] = 'mean'

    # TAS: Use list of functions to create multiple aggregations
    if 'tas' in daily_df.columns:
        agg_rules['tas'] = ['mean', 'max']

    # Group and aggregate
    weekly_df = daily_df.groupby(['region', 'week_ending']).agg(agg_rules)

    # Flatten column names (pandas creates MultiIndex with ['mean', 'max'] for tas)
    weekly_df.columns = ['_'.join(col).strip('_') if isinstance(col, tuple) else col
                         for col in weekly_df.columns]

    # Rename tas aggregations for clarity
    if 'tas_mean' in weekly_df.columns:
        weekly_df.rename(columns={'tas_mean': 'tas'}, inplace=True)

    weekly_df = weekly_df.reset_index()

    return weekly_df
