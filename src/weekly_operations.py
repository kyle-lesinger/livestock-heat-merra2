"""
Weekly Operations

Functions for weekly data operations including lagged variables,
cattle data reshaping, and climate-cattle data merging.
"""

from typing import List, Optional
import pandas as pd
import numpy as np


def create_lagged_variables(
    weekly_df: pd.DataFrame,
    lag_weeks: List[int] = [1, 2, 3, 4]
) -> pd.DataFrame:
    """
    Create lagged predictor variables for time series analysis.

    Parameters
    ----------
    weekly_df : pd.DataFrame
        Weekly data with columns:
        - 'region': Region identifier
        - 'week_ending': Week-ending dates
        - Predictor columns to lag
    lag_weeks : list of int, default=[1,2,3,4]
        Number of weeks to lag each predictor

    Returns
    -------
    pd.DataFrame
        Weekly data with added lagged columns.
        New columns named: '{original_column}_lag{N}'

    Notes
    -----
    - Metadata columns ('region', 'week_ending', 'date') are excluded from lagging
    - Lagged values are grouped by region to avoid cross-region contamination
    - First N rows per region will have NaN for lag N

    Examples
    --------
    >>> weekly_df_lagged = create_lagged_variables(weekly_df, lag_weeks=[1, 2, 3, 4])
    >>> print(f"Original columns: {weekly_df.shape[1]}")
    >>> print(f"With lags: {weekly_df_lagged.shape[1]}")
    >>> # Access 2-week lagged nighttime bad hours
    >>> print(weekly_df_lagged['night_bad_hrs_lag2'].head())
    """
    df = weekly_df.copy()
    df = df.sort_values(['region', 'week_ending'])

    # Exclude metadata columns from lagging
    exclude_cols = ['region', 'week_ending', 'date']
    predictor_cols = [col for col in df.columns if col not in exclude_cols]

    # Create lagged variables
    for lag in lag_weeks:
        for col in predictor_cols:
            lagged_col_name = f"{col}_lag{lag}"
            df[lagged_col_name] = df.groupby('region')[col].shift(lag)

    return df


def reshape_cattle_to_long(
    cattle_df: pd.DataFrame,
    regions: List[str] = ['region_4', 'region_6'],
    date_column: str = 'date'
) -> pd.DataFrame:
    """
    Reshape cattle slaughter data from wide to long format.

    Parameters
    ----------
    cattle_df : pd.DataFrame
        Wide-format cattle data with columns:
        - date_column: Week-ending dates
        - 'region_4_beef_dairy', 'region_4_dairy': Region 4 slaughter
        - 'region_6_beef_dairy', 'region_6_dairy': Region 6 slaughter
    regions : list of str, default=['region_4', 'region_6']
        Regions to extract
    date_column : str, default='date'
        Name of date column in input data

    Returns
    -------
    pd.DataFrame
        Long-format data with columns:
        - 'week_ending': Week-ending dates
        - 'region': Region identifier ('region_4', 'region_6')
        - 'slaughter_beef_dairy': Combined beef+dairy slaughter (thousands)
        - 'slaughter_dairy': Dairy-only slaughter (thousands)

    Examples
    --------
    >>> cattle_long = reshape_cattle_to_long(cattle_df)
    >>> print(f"Wide format: {len(cattle_df)} weeks")
    >>> print(f"Long format: {len(cattle_long)} region-weeks")
    >>> print(cattle_long.groupby('region')['slaughter_beef_dairy'].mean())
    """
    cattle_long = []

    for region in regions:
        # Extract columns for this region
        beef_dairy_col = f'{region}_beef_dairy'
        dairy_col = f'{region}_dairy'

        if beef_dairy_col not in cattle_df.columns or dairy_col not in cattle_df.columns:
            print(f"Warning: Columns for {region} not found in cattle data")
            continue

        region_data = pd.DataFrame({
            'week_ending': cattle_df[date_column],
            'region': region,
            'slaughter_beef_dairy': cattle_df[beef_dairy_col],
            'slaughter_dairy': cattle_df[dairy_col]
        })

        cattle_long.append(region_data)

    # Combine all regions
    cattle_long_df = pd.concat(cattle_long, ignore_index=True)

    return cattle_long_df


def merge_cattle_climate(
    weekly_df: pd.DataFrame,
    cattle_df: pd.DataFrame,
    how: str = 'left',
    add_log_transform: bool = True,
    drop_missing_outcomes: bool = True
) -> pd.DataFrame:
    """
    Merge weekly climate predictors with cattle slaughter data.

    Parameters
    ----------
    weekly_df : pd.DataFrame
        Weekly climate predictors with columns:
        - 'region': Region identifier
        - 'week_ending': Week-ending dates
        - Predictor columns
    cattle_df : pd.DataFrame
        Cattle data (long format) with columns:
        - 'region': Region identifier
        - 'week_ending': Week-ending dates
        - 'slaughter_beef_dairy': Slaughter counts
        - 'slaughter_dairy': Dairy slaughter counts
    how : str, default='left'
        How to merge:
        - 'left': Keep all climate weeks
        - 'inner': Only weeks with both climate and cattle data
    add_log_transform : bool, default=True
        Whether to create log-transformed outcome variables
    drop_missing_outcomes : bool, default=True
        Whether to drop rows with missing slaughter data

    Returns
    -------
    pd.DataFrame
        Merged dataset with climate predictors and cattle outcomes

    Notes
    -----
    - Log transformation uses: log(slaughter + 0.1) to handle any zeros
    - Missing values are reported before dropping
    - Only overlap period between datasets is retained

    Examples
    --------
    >>> merged_df = merge_cattle_climate(weekly_df_lagged, cattle_long_df)
    >>> print(f"Merged shape: {merged_df.shape}")
    >>> print(f"Regions: {merged_df['region'].unique()}")
    """
    # Merge on region and week_ending
    merged_df = weekly_df.merge(
        cattle_df,
        on=['region', 'week_ending'],
        how=how,
        indicator=True
    )

    print(f"Merged data shape: {merged_df.shape}")
    print(f"\nMerge statistics:")
    print(merged_df['_merge'].value_counts())

    # Check overlap period
    climate_dates = weekly_df['week_ending']
    cattle_dates = cattle_df['week_ending']

    overlap_start = max(climate_dates.min(), cattle_dates.min())
    overlap_end = min(climate_dates.max(), cattle_dates.max())

    print(f"\nData coverage:")
    print(f"  Climate data: {climate_dates.min()} to {climate_dates.max()}")
    print(f"  Cattle data: {cattle_dates.min()} to {cattle_dates.max()}")
    print(f"  Overlap: {overlap_start} to {overlap_end}")

    # Filter to overlap period only
    merged_df_overlap = merged_df[
        (merged_df['week_ending'] >= overlap_start) &
        (merged_df['week_ending'] <= overlap_end)
    ].copy()

    print(f"\nFiltered to overlap period:")
    print(f"  Shape: {merged_df_overlap.shape}")

    # Check for missing slaughter data within overlap period
    missing_in_overlap = merged_df_overlap['slaughter_beef_dairy'].isnull().sum()
    print(f"\nMissing slaughter data in overlap period: {missing_in_overlap} "
          f"({100*missing_in_overlap/len(merged_df_overlap):.2f}%)")

    if missing_in_overlap > 0:
        print("\n⚠️  WARNING: Some weeks have missing slaughter data")
        print("Options for handling missing values:")
        print("  1. Drop rows with missing slaughter data (recommended for regression)")
        print("  2. Interpolate missing values (caution: may introduce bias)")
        print("  3. Use as-is (some models can handle NaN)")

    # Create log-transformed outcome variables
    if add_log_transform:
        merged_df_overlap['log_slaughter_beef_dairy'] = np.log(
            merged_df_overlap['slaughter_beef_dairy'] + 0.1
        )
        merged_df_overlap['log_slaughter_dairy'] = np.log(
            merged_df_overlap['slaughter_dairy'] + 0.1
        )

    # Drop rows with missing outcome variable
    if drop_missing_outcomes:
        analysis_df = merged_df_overlap.dropna(subset=['slaughter_beef_dairy']).copy()

        print(f"\nFinal analysis dataset (after dropping missing outcomes):")
        print(f"  Shape: {analysis_df.shape}")
        print(f"  Rows dropped: {len(merged_df_overlap) - len(analysis_df)}")

        if len(analysis_df) > 0:
            print(f"  Regions: {analysis_df['region'].nunique()}")
            print(f"  Weeks per region: {len(analysis_df) // analysis_df['region'].nunique()}")

            print(f"\nOutcome variable summary:")
            print(f"  Slaughter (beef+dairy) - Mean: {analysis_df['slaughter_beef_dairy'].mean():.1f} thousand head")
            print(f"  Slaughter (beef+dairy) - Std: {analysis_df['slaughter_beef_dairy'].std():.1f} thousand head")
            print(f"  Slaughter (beef+dairy) - Range: [{analysis_df['slaughter_beef_dairy'].min():.1f}, "
                  f"{analysis_df['slaughter_beef_dairy'].max():.1f}]")

        return analysis_df
    else:
        return merged_df_overlap
