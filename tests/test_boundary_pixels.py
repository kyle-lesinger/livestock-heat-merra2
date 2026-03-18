#!/usr/bin/env python3
"""
Investigate how grid cells are assigned near state boundaries.

Current logic: Point-in-polygon using grid cell CENTROIDS
- If centroid falls in State A, entire cell assigned to State A
- Grid cells are ~55km wide, state boundaries are exact vector lines
- Mismatch is inevitable at this resolution
"""

import numpy as np
import xarray as xr
import geopandas as gpd
from pathlib import Path
from shapely.geometry import Point, box

# Load mask and shapefile
print("Loading data...")
script_dir = Path(__file__).parent
mask_file = script_dir.parent / 'masks' / 'region_mask.nc'
shapefile = script_dir.parent.parent / 'shpfiles' / 'cb_2018_us_state_20m.shp'

mask_ds = xr.open_dataset(mask_file)
states_gdf = gpd.read_file(shapefile)
us_states = states_gdf[~states_gdf['STUSPS'].isin(['PR', 'VI', 'GU', 'MP', 'AS'])]

lats = mask_ds.lat.values
lons = mask_ds.lon.values

# MERRA-2 grid spacing
lat_spacing = np.diff(lats).mean()  # ~0.5 degrees
lon_spacing = np.diff(lons).mean()  # ~0.625 degrees

print(f"\nMERRA-2 Grid Resolution:")
print(f"  Latitude spacing: {lat_spacing:.3f}° (~{lat_spacing * 111:.1f} km)")
print(f"  Longitude spacing: {lon_spacing:.3f}° (~{lon_spacing * 111 * np.cos(np.radians(37)):.1f} km at 37°N)")

# The issue: centroids vs cell boundaries
print(f"\nPixel Assignment Logic:")
print(f"  Current method: Point-in-polygon using grid cell CENTROIDS")
print(f"  Problem: Grid cells near boundaries may:")
print(f"    - Have centroid in State A")
print(f"    - But physically overlap State B")
print(f"    - Entire cell gets colored as State A")
print(f"    - Visual mismatch when State B boundary is overlaid")

# Check how many cells might be affected
print(f"\nBoundary Analysis:")

# Count cells on boundaries (cells where neighbors have different state IDs)
state_mask = mask_ds.state_mask.values
boundary_cells = 0

for i in range(1, state_mask.shape[0] - 1):
    for j in range(1, state_mask.shape[1] - 1):
        if state_mask[i, j] > 0:  # Only check US cells
            # Check 4-connected neighbors
            neighbors = [
                state_mask[i-1, j],  # North
                state_mask[i+1, j],  # South
                state_mask[i, j-1],  # West
                state_mask[i, j+1]   # East
            ]
            # If any neighbor is different (and not 0), this is a boundary cell
            if any(n != state_mask[i, j] and n > 0 for n in neighbors):
                boundary_cells += 1

total_us_cells = np.sum(state_mask > 0)
print(f"  Total US grid cells: {total_us_cells}")
print(f"  Boundary cells: {boundary_cells} ({100*boundary_cells/total_us_cells:.1f}%)")
print(f"  Interior cells: {total_us_cells - boundary_cells} ({100*(total_us_cells-boundary_cells)/total_us_cells:.1f}%)")

print(f"\nVisualization Options:")
print(f"\n1. **Emphasize grid structure** (RECOMMENDED):")
print(f"   - Use pcolormesh with edgecolors to show cell boundaries")
print(f"   - Makes it clear data is gridded, not continuous")
print(f"   - Example: ax.pcolormesh(..., edgecolors='gray', linewidth=0.1)")

print(f"\n2. **Remove state boundaries**:")
print(f"   - Don't overlay vector boundaries")
print(f"   - Only show colored grid cells")
print(f"   - No visual mismatch")

print(f"\n3. **Use thicker/semi-transparent boundaries**:")
print(f"   - Make boundaries more prominent")
print(f"   - Set expectation of mismatch")
print(f"   - Example: ax.add_feature(..., linewidth=1.5, alpha=0.7)")

print(f"\n4. **Alternative assignment methods**:")
print(f"   - Area-weighted: Assign based on % overlap (slow, complex)")
print(f"   - Rasterization: Burn polygons to grid (different results)")
print(f"   - Current centroid method is standard for climate data")

mask_ds.close()
