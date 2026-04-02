"""
Thermal Acclimation State (TAS) Calculations

Functions for calculating Thermal Acclimation State, a novel continuous variable
tracking the thermal conditioning of livestock herds over time.

Reference: See LITERATURE_GAPS_AND_NOVEL_METHODS.md for scientific rationale.
"""

import numpy as np
import pandas as pd


def calculate_tas(
    daily_metrics_df: pd.DataFrame,
    alpha: float = 0.90,
    beta_heat: float = 0.05,
    gamma_cool: float = 0.08,
    heat_threshold_hrs: int = 6,
    cool_threshold_hrs: int = 6
) -> pd.Series:
    """
    Calculate Thermal Acclimation State (TAS) from daily metrics.

    TAS represents the thermal conditioning of the regional herd, ranging from
    0 (naive, unacclimated) to 1 (fully acclimated to heat).

    The TAS model uses exponential decay with heat credits and cool penalties:
        TAS_t = α·TAS_{t-1} + β·HeatCredit_t - γ·CoolPenalty_t

    where:
        - HeatCredit = β * max(0, day_above_25c_hrs - heat_threshold_hrs)
        - CoolPenalty = γ * max(0, night_strong_recovery_hrs - cool_threshold_hrs)

    Parameters
    ----------
    daily_metrics_df : pd.DataFrame
        Daily metrics with required columns:
        - 'day_above_25c_hrs': Daytime hours above 25°C
        - 'night_strong_recovery_hrs': Nighttime hours < 18°C and > 0°C
    alpha : float, default=0.90
        Decay parameter (0-1). Controls memory length.
        - 0.90 ≈ 10-day half-life (recommended)
        - 0.85 ≈ 6-day half-life (faster adaptation)
        - 0.95 ≈ 14-day half-life (slower adaptation)
    beta_heat : float, default=0.05
        Heat credit accumulation rate per hour above threshold.
        Higher values = faster acclimation to heat.
    gamma_cool : float, default=0.08
        Cool depletion rate per hour of strong recovery.
        Higher values = faster de-acclimation with cool nights.
    heat_threshold_hrs : int, default=6
        Minimum daytime heat hours to trigger acclimation gain.
        Below this threshold, no heat credit is added.
    cool_threshold_hrs : int, default=6
        Minimum nighttime cool hours to trigger acclimation loss.
        Below this threshold, no cool penalty is applied.

    Returns
    -------
    pd.Series
        TAS values (0-1) for each day, indexed by original dataframe index

    Notes
    -----
    - TAS is initialized at 0 (naive herd at start of period)
    - Values are clipped to [0, 1] range
    - Missing values in input columns may produce NaN in output

    Examples
    --------
    >>> # Calculate TAS for a single region
    >>> region_data = daily_df[daily_df['region'] == 'region_4'].copy()
    >>> region_data = region_data.sort_values('date').set_index('date')
    >>> tas_series = calculate_tas(region_data)
    >>> print(f"Mean TAS: {tas_series.mean():.3f}")
    >>> print(f"Max TAS: {tas_series.max():.3f}")

    >>> # Calculate with custom parameters (faster adaptation)
    >>> tas_fast = calculate_tas(region_data, alpha=0.85, beta_heat=0.08)
    """
    n_days = len(daily_metrics_df)
    tas = np.zeros(n_days)

    # Initialize TAS at 0 (naive herd)
    tas[0] = 0.0

    for i in range(1, n_days):
        # Previous day TAS with exponential decay
        tas_decay = alpha * tas[i-1]

        # Heat credit: daytime hours > 25°C
        heat_hrs = daily_metrics_df.iloc[i]['day_above_25c_hrs']
        if heat_hrs >= heat_threshold_hrs:
            heat_credit = beta_heat * (heat_hrs - heat_threshold_hrs)
        else:
            heat_credit = 0.0

        # Cool penalty: nighttime strong recovery hours
        cool_hrs = daily_metrics_df.iloc[i]['night_strong_recovery_hrs']
        if cool_hrs >= cool_threshold_hrs:
            cool_penalty = gamma_cool * (cool_hrs - cool_threshold_hrs)
        else:
            cool_penalty = 0.0

        # Update TAS and bound to [0, 1]
        tas[i] = tas_decay + heat_credit - cool_penalty
        tas[i] = np.clip(tas[i], 0.0, 1.0)

    return pd.Series(tas, index=daily_metrics_df.index, name='tas')


def calculate_tas_statistics(tas_series: pd.Series) -> dict:
    """
    Calculate summary statistics for a TAS time series.

    Parameters
    ----------
    tas_series : pd.Series
        TAS values (0-1) from calculate_tas()

    Returns
    -------
    dict
        Dictionary with keys:
        - 'mean': Average TAS over period
        - 'std': Standard deviation
        - 'min': Minimum TAS (should be near 0)
        - 'max': Maximum TAS
        - 'median': Median TAS
        - 'q25': 25th percentile
        - 'q75': 75th percentile

    Examples
    --------
    >>> tas_stats = calculate_tas_statistics(tas_series)
    >>> print(f"Mean TAS: {tas_stats['mean']:.3f}")
    >>> print(f"Range: [{tas_stats['min']:.3f}, {tas_stats['max']:.3f}]")
    """
    return {
        'mean': tas_series.mean(),
        'std': tas_series.std(),
        'min': tas_series.min(),
        'max': tas_series.max(),
        'median': tas_series.median(),
        'q25': tas_series.quantile(0.25),
        'q75': tas_series.quantile(0.75),
    }
