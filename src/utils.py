"""
Utility Functions

General utility functions for date handling, file management, and data validation.
"""

from typing import List, Tuple, Optional
from pathlib import Path
import pandas as pd
import xarray as xr


def generate_year_months(
    start_year: int,
    start_month: int,
    end_year: int,
    end_month: int
) -> List[Tuple[int, int]]:
    """
    Generate list of (year, month) tuples for a date range.

    Parameters
    ----------
    start_year : int
        Starting year
    start_month : int
        Starting month (1-12)
    end_year : int
        Ending year
    end_month : int
        Ending month (1-12)

    Returns
    -------
    List[Tuple[int, int]]
        List of (year, month) tuples

    Examples
    --------
    >>> year_months = generate_year_months(2020, 6, 2020, 8)
    >>> print(year_months)
    [(2020, 6), (2020, 7), (2020, 8)]
    """
    year_months = []
    for year in range(start_year, end_year + 1):
        month_start = start_month if year == start_year else 1
        month_end = end_month if year == end_year else 12
        for month in range(month_start, month_end + 1):
            year_months.append((year, month))
    return year_months


def get_lat_lon_coords(
    input_dir: Path,
    dates: List[pd.Timestamp]
) -> Tuple[Optional[xr.DataArray], Optional[xr.DataArray]]:
    """
    Extract lat/lon coordinates from first available NetCDF file.

    Parameters
    ----------
    input_dir : Path
        Directory containing daily NetCDF files
    dates : List[pd.Timestamp]
        List of dates to search

    Returns
    -------
    Tuple[Optional[xr.DataArray], Optional[xr.DataArray]]
        (lat, lon) coordinate arrays, or (None, None) if no files found

    Examples
    --------
    >>> from pathlib import Path
    >>> dates = pd.date_range('2020-06-01', '2020-06-03')
    >>> lat, lon = get_lat_lon_coords(Path('daily_data/'), list(dates))
    """
    for date in dates:
        date_str = date.strftime('%Y%m%d')
        file_path = input_dir / f'merra2_us_{date_str}.nc'

        if file_path.exists():
            try:
                ds = xr.open_dataset(file_path)
                lat = ds.lat
                lon = ds.lon
                ds.close()
                return lat, lon
            except Exception as e:
                print(f"Warning: Error loading {file_path}: {e}")
                continue

    return None, None


def check_file_exists(file_path: Path, skip_existing: bool = True) -> bool:
    """
    Check if output file already exists and whether to skip processing.

    Parameters
    ----------
    file_path : Path
        Path to check
    skip_existing : bool, default=True
        Whether to skip if file exists

    Returns
    -------
    bool
        True if should skip (file exists and skip_existing=True)

    Examples
    --------
    >>> from pathlib import Path
    >>> should_skip = check_file_exists(Path('output.nc'), skip_existing=True)
    >>> if should_skip:
    ...     print("File exists, skipping")
    """
    if file_path.exists() and skip_existing:
        return True
    return False


def validate_date_range(
    start_year: int,
    start_month: int,
    end_year: int,
    end_month: int
) -> bool:
    """
    Validate that date range is logical.

    Parameters
    ----------
    start_year : int
        Starting year
    start_month : int
        Starting month (1-12)
    end_year : int
        Ending year
    end_month : int
        Ending month (1-12)

    Returns
    -------
    bool
        True if valid, False otherwise

    Examples
    --------
    >>> is_valid = validate_date_range(2020, 1, 2020, 12)
    >>> print(is_valid)
    True
    """
    if start_month < 1 or start_month > 12:
        return False
    if end_month < 1 or end_month > 12:
        return False
    if start_year > end_year:
        return False
    if start_year == end_year and start_month > end_month:
        return False
    return True


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Parameters
    ----------
    size_bytes : int
        Size in bytes

    Returns
    -------
    str
        Formatted size string

    Examples
    --------
    >>> print(format_file_size(1024))
    1.0 KB
    >>> print(format_file_size(1048576))
    1.0 MB
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"
