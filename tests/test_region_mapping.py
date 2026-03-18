#!/usr/bin/env python3
"""
Test region mapping against original specification.

This script compares the current region mapping in the mask file
against the original requested mapping to identify discrepancies.
"""

import numpy as np
import xarray as xr
from pathlib import Path

# =============================================================================
# Original Requested Mapping (from user specification)
# =============================================================================

ORIGINAL_MAPPING = {
    1: {'name': 'Region 1', 'states': ['CT', 'ME', 'NH', 'VT', 'MA', 'RI']},
    2: {'name': 'Region 2', 'states': ['NY', 'NJ']},
    3: {'name': 'Region 3', 'states': ['DE', 'MD', 'PA', 'WV', 'VA']},
    4: {'name': 'Region 4', 'states': ['AL', 'FL', 'GA', 'KY', 'MS', 'NC', 'SC', 'TN']},
    5: {'name': 'Region 5', 'states': ['IL', 'IN', 'MI', 'MN', 'OH', 'WI']},
    6: {'name': 'Region 6', 'states': ['AR', 'LA', 'NM', 'OK', 'TX']},
    7: {'name': 'Region 7', 'states': ['IA', 'KS', 'MO', 'NE']},
    8: {'name': 'Region 8', 'states': ['CO', 'MT', 'ND', 'SD', 'UT', 'WY']},
    9: {'name': 'Region 9', 'states': ['AZ', 'CA', 'HI', 'NV']},
    10: {'name': 'Region 10', 'states': ['AK', 'ID', 'OR', 'WA']}
}

# =============================================================================
# Load Current Mapping from NetCDF File
# =============================================================================

# Get path relative to this script's location
script_dir = Path(__file__).parent
mask_file = script_dir.parent / 'masks' / 'region_mask.nc'

if not mask_file.exists():
    print(f"ERROR: Mask file not found: {mask_file}")
    print("Please run create_region_mask_pointwise.py first.")
    exit(1)

print("Loading mask file...")
ds = xr.open_dataset(mask_file)

# Extract current mapping
current_mapping = {}
for i, region_id in enumerate(ds.region_id.values):
    region_name = ds.region_name.values[i]
    # Find states in this region
    states_in_region = ds.state_abbr.values[ds.state_region.values == region_id]
    # Decode bytes to strings
    states = sorted([s.decode() if isinstance(s, bytes) else s for s in states_in_region])
    current_mapping[int(region_id)] = {
        'name': region_name,
        'states': states
    }

ds.close()

# =============================================================================
# Compare Mappings
# =============================================================================

print("\n" + "=" * 80)
print("REGION MAPPING VALIDATION")
print("=" * 80)

errors_found = False

for region_id in range(1, 11):
    expected = set(ORIGINAL_MAPPING[region_id]['states'])
    actual = set(current_mapping.get(region_id, {}).get('states', []))

    expected_name = ORIGINAL_MAPPING[region_id]['name']
    actual_name = current_mapping.get(region_id, {}).get('name', 'N/A')

    print(f"\nRegion {region_id}: {actual_name}")
    print("-" * 80)

    # Check if sets match
    if expected == actual:
        print(f"✓ PASS: All states correct")
        print(f"  States ({len(actual)}): {', '.join(sorted(actual))}")
    else:
        errors_found = True
        print(f"✗ FAIL: States do not match expected mapping")

        # Show expected
        print(f"\n  Expected ({len(expected)}): {', '.join(sorted(expected))}")

        # Show actual
        print(f"  Actual   ({len(actual)}): {', '.join(sorted(actual))}")

        # Show differences
        missing = expected - actual
        extra = actual - expected

        if missing:
            print(f"\n  Missing states: {', '.join(sorted(missing))}")
        if extra:
            print(f"  Extra states:   {', '.join(sorted(extra))}")

# =============================================================================
# Check for States in Wrong Regions
# =============================================================================

print("\n" + "=" * 80)
print("STATE ASSIGNMENT VALIDATION")
print("=" * 80)

# Build reverse mapping: state -> expected region
expected_state_to_region = {}
for region_id, info in ORIGINAL_MAPPING.items():
    for state in info['states']:
        expected_state_to_region[state] = region_id

# Build reverse mapping: state -> actual region
actual_state_to_region = {}
for region_id, info in current_mapping.items():
    for state in info['states']:
        actual_state_to_region[state] = region_id

# Check each state
misassigned_states = []
for state in sorted(expected_state_to_region.keys()):
    expected_region = expected_state_to_region[state]
    actual_region = actual_state_to_region.get(state, None)

    if actual_region is None:
        print(f"✗ {state}: MISSING from mask file (should be in Region {expected_region})")
        misassigned_states.append(state)
        errors_found = True
    elif actual_region != expected_region:
        print(f"✗ {state}: In Region {actual_region}, should be in Region {expected_region}")
        misassigned_states.append(state)
        errors_found = True

if not misassigned_states:
    print("✓ All states assigned to correct regions")

# Check for extra states in mask that shouldn't be there
for state in sorted(actual_state_to_region.keys()):
    if state not in expected_state_to_region:
        print(f"⚠ {state}: Present in mask but not in original specification")

# =============================================================================
# Summary
# =============================================================================

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

if errors_found:
    print("✗ FAILED: Region mapping has errors")
    print(f"\nTotal states misassigned: {len(misassigned_states)}")
    print("\nRecommendation: Run the fixed version of create_region_mask_pointwise.py")
else:
    print("✓ PASSED: All regions and states correctly mapped")

print()
