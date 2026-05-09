"""
Livestock and Heat Research - Source Modules

This package contains reusable functions extracted from Jupyter notebooks
for processing MERRA-2 climate data and analyzing cattle slaughter impacts.

Modules:
--------
- data_loading: Load NetCDF and CSV data files
- aggregation: Spatial and temporal aggregation functions
- thermal_acclimation: Thermal Acclimation State (TAS) calculations
- weekly_operations: Weekly aggregation and cattle data merging
- utils: Utility functions for dates, files, and validation
- processing: Threshold calculations for MERRA-2 processing
- analysis: Common analysis functions for notebooks
"""

__version__ = "0.1.0"
__author__ = "Kyle Lesinger"

# Convenience imports for commonly used functions
from .data_loading import (
    load_monthly_data,
    load_region_mask,
    create_cattle_region_masks,
    load_cattle_data
)
from .aggregation import aggregate_to_region, aggregate_to_weekly
from .thermal_acclimation import calculate_tas
from .weekly_operations import (
    create_lagged_variables,
    reshape_cattle_to_long,
    merge_cattle_climate
)
from .utils import generate_year_months, get_lat_lon_coords
from .processing import (
    load_us_mask,
    compute_daily_daytime_stats,
    compute_daily_nighttime_stats,
    compute_daily_vpd_stats,
    process_month
)
from .analysis import (
    load_weekly_data,
    compute_state_mean,
    compute_state_stats,
    mann_kendall_test,
    get_season,
    resample_to_monthly,
    normalize,
    identify_heatwaves
)

__all__ = [
    # Data loading
    'load_monthly_data',
    'load_region_mask',
    'create_cattle_region_masks',
    'load_cattle_data',
    'load_weekly_data',
    # Aggregation
    'aggregate_to_region',
    'aggregate_to_weekly',
    # Thermal acclimation
    'calculate_tas',
    # Weekly operations
    'create_lagged_variables',
    'reshape_cattle_to_long',
    'merge_cattle_climate',
    # Utilities
    'generate_year_months',
    'get_lat_lon_coords',
    # Processing
    'load_us_mask',
    'compute_daily_daytime_stats',
    'compute_daily_nighttime_stats',
    'compute_daily_vpd_stats',
    'process_month',
    # Analysis
    'compute_state_mean',
    'compute_state_stats',
    'mann_kendall_test',
    'get_season',
    'resample_to_monthly',
    'normalize',
    'identify_heatwaves',
]
