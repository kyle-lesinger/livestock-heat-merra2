"""
Data Loading Functions

Functions for loading NetCDF climate data, region masks, and cattle slaughter data.
"""

from typing import Optional, Dict
from pathlib import Path
import xarray as xr
import pandas as pd


def load_monthly_data(
    year: int,
    month: int,
    data_type: str,
    base_dir: Optional[Path] = None
) -> Optional[xr.Dataset]:
    """
    Load a monthly processed file.

    Parameters
    ----------
    year : int
        Year to load
    month : int
        Month to load (1-12)
    data_type : str
        One of: 'daytime', 'nighttime', 'vpd'
    base_dir : Path, optional
        Base directory for the data_type. If None, expects caller to provide
        the appropriate directory (from config.PROCESSED_*_DIR)

    Returns
    -------
    xr.Dataset or None
        Loaded dataset, or None if file doesn't exist

    Examples
    --------
    >>> import config
    >>> ds = load_monthly_data(2020, 6, 'daytime', config.PROCESSED_DAYTIME_DIR)
    """
    if base_dir is None:
        raise ValueError(
            "base_dir must be provided. Pass config.PROCESSED_DAYTIME_DIR, "
            "config.PROCESSED_NIGHTTIME_DIR, or config.PROCESSED_VPD_DIR"
        )

    # Determine filename based on data type
    if data_type == 'daytime':
        filename = f'daytime_heat_{year}{month:02d}.nc'
    elif data_type == 'nighttime':
        filename = f'nighttime_recovery_{year}{month:02d}.nc'
    elif data_type == 'vpd':
        filename = f'vpd_{year}{month:02d}.nc'
    else:
        raise ValueError(f"Unknown data_type: {data_type}. Must be 'daytime', 'nighttime', or 'vpd'")

    file_path = base_dir / filename

    if not file_path.exists():
        print(f"Warning: File not found: {file_path}")
        return None

    try:
        ds = xr.open_dataset(file_path)
        return ds
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None


def load_region_mask(mask_file: Optional[Path] = None) -> tuple[xr.Dataset, Dict[str, xr.DataArray]]:
    """
    Load region mask and create cattle region masks.

    Parameters
    ----------
    mask_file : Path, optional
        Path to region_mask.nc. If None, expects caller to provide
        (from config.MASK_FILE)

    Returns
    -------
    mask_ds : xr.Dataset
        Full region mask dataset
    region_masks : dict
        Dictionary mapping region names to boolean masks
        Keys: 'region_4', 'region_6'

    Examples
    --------
    >>> import config
    >>> mask_ds, region_masks = load_region_mask(config.MASK_FILE)
    >>> print(f"Region 4 has {region_masks['region_4'].sum().item()} grid cells")
    """
    if mask_file is None:
        raise ValueError("mask_file must be provided. Pass config.MASK_FILE")

    # Load mask dataset
    mask_ds = xr.open_dataset(mask_file)

    return mask_ds, None  # Return None for region_masks since state IDs need to come from config


def create_cattle_region_masks(
    mask_ds: xr.Dataset,
    cattle_region_ids: Dict[str, list]
) -> Dict[str, xr.DataArray]:
    """
    Create boolean masks for cattle regions from state mask.

    Parameters
    ----------
    mask_ds : xr.Dataset
        Region mask dataset with 'state_mask' variable
    cattle_region_ids : dict
        Dictionary mapping region names to state ID lists
        Example: {'region_4': [10, 12, 13, ...], 'region_6': [4, 22, ...]}

    Returns
    -------
    region_masks : dict
        Dictionary mapping region names to boolean DataArrays

    Examples
    --------
    >>> import config
    >>> mask_ds = xr.open_dataset(config.MASK_FILE)
    >>> region_masks = create_cattle_region_masks(mask_ds, config.CATTLE_REGION_IDS)
    >>> print(f"Region 4: {int(region_masks['region_4'].sum())} cells")
    """
    region_masks = {}

    for region_name, state_ids in cattle_region_ids.items():
        region_mask = mask_ds['state_mask'].isin(state_ids)
        region_masks[region_name] = region_mask

    return region_masks


def load_cattle_data(
    file_path: Path,
    parse_dates: bool = True,
    date_column: str = 'date'
) -> Optional[pd.DataFrame]:
    """
    Load cattle slaughter data from CSV.

    Parameters
    ----------
    file_path : Path
        Path to cattle data CSV file
    parse_dates : bool, default=True
        Whether to parse date column as datetime
    date_column : str, default='date'
        Name of the date column

    Returns
    -------
    pd.DataFrame or None
        Cattle slaughter data, or None if file doesn't exist

    Examples
    --------
    >>> import config
    >>> cattle_df = load_cattle_data(config.CATTLE_DATA_FILE)
    >>> print(f"Loaded {len(cattle_df)} weeks of cattle data")
    """
    if not file_path.exists():
        print(f"Warning: Cattle data file not found: {file_path}")
        return None

    try:
        if parse_dates:
            cattle_df = pd.read_csv(file_path, parse_dates=[date_column])
        else:
            cattle_df = pd.read_csv(file_path)
        return cattle_df
    except Exception as e:
        print(f"Error loading cattle data from {file_path}: {e}")
        return None
