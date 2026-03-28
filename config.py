"""
Configuration module for livestock_and_heat project.
Loads canonical state and region definitions from region_mask.nc.

All notebooks should import from this module to ensure consistency.

Path Configuration:
-------------------
Paths can be customized via .env file in the project root directory.
See .env.example for configuration options.

If .env is not present, defaults to relative paths from this file's location.
"""

import os
import xarray as xr
from pathlib import Path

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env from project root
except ImportError:
    # python-dotenv not installed, will use defaults
    pass

# =============================================================================
# DATA DIRECTORY PATHS
# =============================================================================
# All paths can be overridden via environment variables in .env file
# Defaults assume notebooks are run from project root or use relative paths

# Project root directory (location of this config.py file)
PROJECT_ROOT = Path(__file__).parent

# Override project root from environment if specified
if os.getenv('PROJECT_ROOT'):
    PROJECT_ROOT = Path(os.getenv('PROJECT_ROOT'))

# Data directories - can be overridden via environment variables
DAILY_DATA_DIR = Path(os.getenv('DAILY_DATA_DIR', PROJECT_ROOT / 'daily_data'))
DAILY_DATA_SOIL_PRECIP_DIR = Path(os.getenv('DAILY_DATA_SOIL_PRECIP_DIR', PROJECT_ROOT / 'daily_data_soil_precip'))
PROCESSED_NIGHTTIME_DIR = Path(os.getenv('PROCESSED_NIGHTTIME_DIR', PROJECT_ROOT / 'processed_nighttime_recovery'))
PROCESSED_DAYTIME_DIR = Path(os.getenv('PROCESSED_DAYTIME_DIR', PROJECT_ROOT / 'processed_daytime_heat'))
PROCESSED_VPD_DIR = Path(os.getenv('PROCESSED_VPD_DIR', PROJECT_ROOT / 'processed_vpd'))
PROCESSED_WEEKLY_DIR = Path(os.getenv('PROCESSED_WEEKLY_DIR', PROJECT_ROOT / 'processed_weekly'))

# Mask and cattle data
MASKS_DIR = Path(os.getenv('MASKS_DIR', PROJECT_ROOT / 'masks'))
CATTLE_DATA_DIR = Path(os.getenv('CATTLE_DATA_DIR', PROJECT_ROOT / 'cattle_data'))

# Output directories
FIGURES_DIR = Path(os.getenv('FIGURES_DIR', PROJECT_ROOT / 'figures'))
IMAGES_DIR = Path(os.getenv('IMAGES_DIR', PROJECT_ROOT / 'images'))

# Specific file paths
MASK_FILE = MASKS_DIR / 'region_mask.nc'
CATTLE_DATA_FILE = CATTLE_DATA_DIR / 'cattle_data_clean.csv'

def load_region_mask_metadata():
    """Load state and region metadata from region_mask.nc"""
    ds = xr.open_dataset(MASK_FILE)

    # Extract metadata
    state_ids = ds['state_id'].values
    state_abbrs = [s.decode() if isinstance(s, bytes) else s for s in ds['state_abbr'].values]
    state_names = [s.decode() if isinstance(s, bytes) else s for s in ds['state_name'].values]
    state_regions = ds['state_region'].values

    ds.close()

    return state_ids, state_abbrs, state_names, state_regions

# Load data once at module import
_ids, _abbrs, _names, _regions = load_region_mask_metadata()

# ============================================================================
# CANONICAL MAPPINGS (from region_mask.nc)
# ============================================================================

# State ID to state name (1-48, alphabetically ordered by abbreviation)
STATE_NAMES = dict(zip(_ids, _names))

# State ID to state abbreviation
STATE_ABBRS = dict(zip(_ids, _abbrs))

# State ID to region number (1-10)
STATE_REGIONS = dict(zip(_ids, _regions))

# Reverse lookups
STATE_ID_FROM_NAME = {name: sid for sid, name in STATE_NAMES.items()}
STATE_ID_FROM_ABBR = {abbr: sid for sid, abbr in STATE_ABBRS.items()}

# Region number to list of state IDs
REGION_STATES = {}
for sid in _ids:
    region = STATE_REGIONS[sid]
    if region not in REGION_STATES:
        REGION_STATES[region] = []
    REGION_STATES[region].append(sid)

# ============================================================================
# FOCUS STATES (for livestock heat stress analysis)
# ============================================================================

# Primary analysis states: Regions 4 & 6 + Arizona (Region 9)
# Region 4 (Southeast): AL, FL, GA, KY, MS, NC, SC, TN
# Region 6 (South Central): AR, LA, NM, OK, TX
# Region 9 (Southwest): AZ (included for cattle analysis)
FOCUS_STATES = {
    'Alabama': 1,
    'Arizona': 3,
    'Arkansas': 2,
    'Florida': 8,
    'Georgia': 9,
    'Kentucky': 15,
    'Louisiana': 16,
    'Mississippi': 23,
    'New Mexico': 30,
    'North Carolina': 25,
    'Oklahoma': 34,
    'South Carolina': 38,
    'Tennessee': 40,
    'Texas': 41
}

# ============================================================================
# CATTLE REGIONS (USDA cattle slaughter regions 4 & 6)
# ============================================================================

CATTLE_REGIONS = {
    'region_4': ['Alabama', 'Florida', 'Georgia', 'Kentucky', 'Mississippi',
                 'North Carolina', 'South Carolina', 'Tennessee'],
    'region_6': ['Arkansas', 'Louisiana', 'New Mexico', 'Oklahoma', 'Texas']
}

# State IDs for cattle regions
CATTLE_REGION_IDS = {
    'region_4': [1, 8, 9, 15, 23, 25, 38, 40],  # Region 4 states
    'region_6': [2, 16, 30, 34, 41]  # Region 6 states (AR, LA, NM, OK, TX)
}

# ============================================================================
# CUSTOM AGRICULTURAL REGIONS (for specialized regional analysis)
# ============================================================================
# NOTE: These are custom groupings and do NOT correspond to the numbered
# regions (1-10) in region_mask.nc. These are agricultural/climatic groupings.

CUSTOM_REGIONS = {
    'Great Plains': [14, 27, 26, 39],  # KS, NE, ND, SD
    'Southern Plains': [34, 41],  # OK, TX
    'Southwest': [3, 30],  # AZ, NM
    'Mountain West': [5, 11, 24, 42, 48],  # CO, ID, MT, UT, WY
    'Corn Belt': [12, 13, 10, 22],  # IL, IN, IA, MO
    'Southeast': [1, 8, 9, 23, 38],  # AL, FL, GA, MS, SC (subset of Region 4)
    'West Coast': [4, 35, 45]  # CA, OR, WA
}

# ============================================================================
# SEASONS
# ============================================================================

SEASONS = {
    'Winter': [12, 1, 2],
    'Spring': [3, 4, 5],
    'Summer': [6, 7, 8],
    'Fall': [9, 10, 11]
}

# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def get_region_name(region_id):
    """Get descriptive name for canonical region number (1-10)"""
    region_names = {
        1: 'Northeast',
        2: 'Mid-Atlantic',
        3: 'Mid-Atlantic South',
        4: 'Southeast',
        5: 'Midwest',
        6: 'South Central',
        7: 'Central Plains',
        8: 'Northern Plains/Rockies',
        9: 'Southwest',
        10: 'Pacific Northwest'
    }
    return region_names.get(region_id, f'Region {region_id}')

def get_states_in_region(region_id):
    """Get list of state names for a given region ID"""
    state_ids = REGION_STATES.get(region_id, [])
    return [STATE_NAMES[sid] for sid in state_ids]

def get_state_info(state_id):
    """Get complete information for a state ID"""
    return {
        'id': state_id,
        'name': STATE_NAMES.get(state_id),
        'abbr': STATE_ABBRS.get(state_id),
        'region': STATE_REGIONS.get(state_id),
        'region_name': get_region_name(STATE_REGIONS.get(state_id))
    }


# =============================================================================
# TIME WINDOWS FOR TEMPERATURE ANALYSIS
# =============================================================================

# Nighttime hours (8pm-6am UTC): 10 hours total
NIGHTTIME_HOURS = list(range(20, 24)) + list(range(0, 6))  # Hours 20-23, 0-5

# Daytime hours (8am-8pm UTC): 12 hours total
DAYTIME_HOURS = list(range(8, 20))  # Hours 8-19

# Afternoon hours for VPD (12pm-6pm UTC): 6 hours total
AFTERNOON_HOURS = list(range(12, 18))  # Hours 12-17


# =============================================================================
# TEMPERATURE THRESHOLDS - NIGHTTIME RECOVERY (8pm-6am)
# =============================================================================
# For each threshold, we count the number of hours per night (0-10 hours)
# Weekly aggregation: SUM across 7 days → 0-70 hours per week

NIGHTTIME_THRESHOLDS = {
    # Recovery metrics (cooler temperatures)
    # Combined with >0°C to avoid overrepresenting cold conditions
    'hours_below_18_above_0': {
        'description': 'Strong nighttime recovery (0°C < T < 18°C)',
        'threshold_low': 0,
        'threshold_high': 18,
        'daily_max': 10,
        'weekly_max': 70,
    },
    'hours_below_21_above_0': {
        'description': 'Reasonable nighttime recovery (0°C < T < 21°C)',
        'threshold_low': 0,
        'threshold_high': 21,
        'daily_max': 10,
        'weekly_max': 70,
    },
    'hours_below_24_above_0': {
        'description': 'Weak nighttime recovery (0°C < T < 24°C)',
        'threshold_low': 0,
        'threshold_high': 24,
        'daily_max': 10,
        'weekly_max': 70,
    },

    # Poor recovery metrics (warm nights)
    'hours_above_21': {
        'description': 'Poor nighttime recovery (T > 21°C)',
        'threshold': 21,
        'daily_max': 10,
        'weekly_max': 70,
    },
    'hours_above_24': {
        'description': 'Very poor nighttime recovery (T > 24°C)',
        'threshold': 24,
        'daily_max': 10,
        'weekly_max': 70,
    },

    # Cold stress metrics
    'hours_below_0': {
        'description': 'Freezing conditions (T < 0°C)',
        'threshold': 0,
        'daily_max': 10,
        'weekly_max': 70,
    },
    'hours_below_neg5': {
        'description': 'Very cold conditions (T < -5°C)',
        'threshold': -5,
        'daily_max': 10,
        'weekly_max': 70,
    },
    'hours_below_neg10': {
        'description': 'Extremely cold conditions (T < -10°C)',
        'threshold': -10,
        'daily_max': 10,
        'weekly_max': 70,
    },
}


# =============================================================================
# TEMPERATURE THRESHOLDS - DAYTIME HEAT (8am-8pm)
# =============================================================================
# For each threshold, we count the number of hours per day (0-12 hours)
# Weekly aggregation: SUM across 7 days → 0-84 hours per week

DAYTIME_THRESHOLDS = {
    # Heat stress metrics
    'hours_above_25': {
        'description': 'Hot conditions (T > 25°C)',
        'threshold': 25,
        'daily_max': 12,
        'weekly_max': 84,
    },
    'hours_above_30': {
        'description': 'Very hot conditions (T > 30°C)',
        'threshold': 30,
        'daily_max': 12,
        'weekly_max': 84,
    },
    'hours_above_35': {
        'description': 'Extreme heat (T > 35°C)',
        'threshold': 35,
        'daily_max': 12,
        'weekly_max': 84,
    },
    'hours_above_40': {
        'description': 'Dangerous heat (T > 40°C)',
        'threshold': 40,
        'daily_max': 12,
        'weekly_max': 84,
    },

    # Cold stress metrics
    'hours_below_neg5': {
        'description': 'Very cold daytime (T < -5°C)',
        'threshold': -5,
        'daily_max': 12,
        'weekly_max': 84,
    },
    'hours_below_0': {
        'description': 'Freezing daytime (T < 0°C)',
        'threshold': 0,
        'daily_max': 12,
        'weekly_max': 84,
    },
    'hours_below_5': {
        'description': 'Cold daytime (T < 5°C)',
        'threshold': 5,
        'daily_max': 12,
        'weekly_max': 84,
    },
}


# =============================================================================
# VPD THRESHOLDS
# =============================================================================
# VPD is measured in kPa (continuous values, not hour counts)
# Weekly aggregation: AVERAGE of daily values (not summed)

VPD_THRESHOLDS = {
    'vpd_mean': {
        'description': 'Afternoon mean VPD (kPa)',
        'units': 'kPa',
        'aggregation': 'AVERAGE',
    },
    'vpd_max': {
        'description': 'Afternoon maximum VPD (kPa)',
        'units': 'kPa',
        'aggregation': 'AVERAGE',
    },
}


# =============================================================================
# AGGREGATION RULES
# =============================================================================

AGGREGATION_METHODS = {
    'temperature_thresholds': {
        'method': 'SUM',
        'description': 'Sum daily hour counts to get weekly total hours',
        'example': 'hours_above_30: 5 hrs/day × 7 days = 35 hrs/week',
    },
    'vpd_metrics': {
        'method': 'AVERAGE',
        'description': 'Average daily VPD values to get weekly mean',
        'example': 'vpd_mean: (2.1 + 2.3 + 2.0 + ...) / 7 days = 2.15 kPa',
    },
}


# =============================================================================
# CATTLE DATA WEEK DEFINITION
# =============================================================================

CATTLE_WEEK = {
    'ending_day': 'Saturday',
    'description': 'USDA cattle slaughter data reports weekly totals ending on Saturday',
    'aggregation': 'Climate data aggregated to match these week boundaries (Sun-Sat)',
}
