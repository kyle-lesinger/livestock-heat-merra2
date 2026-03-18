#!/usr/bin/env python3
"""
Create comparison plots showing different visualization approaches.
"""

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from pathlib import Path

# Load data
script_dir = Path(__file__).parent
mask_file = script_dir.parent / 'masks' / 'region_mask.nc'
data_file = script_dir.parent / 'daily_data' / 'merra2_us_20200615.nc'

mask_ds = xr.open_dataset(mask_file)
data_ds = xr.open_dataset(data_file)
t2m_daily = data_ds.T2M.mean(dim='time')

# Filter to Texas for demonstration
state_abbr_bytes = 'TX'.encode()
state_idx = np.where(mask_ds.state_abbr.values == state_abbr_bytes)[0][0]
state_id = mask_ds.state_id.values[state_idx]
t2m_state = t2m_daily.where(mask_ds.state_mask == state_id)

# Create comparison figure
fig = plt.figure(figsize=(18, 12))

# Method 1: Current (state boundaries overlay, no grid edges)
ax1 = plt.subplot(2, 3, 1, projection=ccrs.PlateCarree())
im1 = ax1.pcolormesh(
    data_ds.lon, data_ds.lat, t2m_state,
    cmap='RdYlBu_r', vmin=20, vmax=35,
    transform=ccrs.PlateCarree()
)
ax1.add_feature(cfeature.STATES, linewidth=0.5, edgecolor='black')
ax1.set_extent([-107, -93, 25.5, 36.5])
plt.colorbar(im1, ax=ax1, shrink=0.6)
ax1.set_title('Method 1: Current\n(State boundaries, no grid edges)', fontsize=10, fontweight='bold')
ax1.text(0.02, 0.98, 'Mismatch visible', transform=ax1.transAxes, 
         fontsize=9, va='top', bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))

# Method 2: Show grid edges (light)
ax2 = plt.subplot(2, 3, 2, projection=ccrs.PlateCarree())
im2 = ax2.pcolormesh(
    data_ds.lon, data_ds.lat, t2m_state,
    cmap='RdYlBu_r', vmin=20, vmax=35,
    edgecolors='gray', linewidth=0.15, alpha=0.9,
    transform=ccrs.PlateCarree()
)
ax2.add_feature(cfeature.STATES, linewidth=0.5, edgecolor='black')
ax2.set_extent([-107, -93, 25.5, 36.5])
plt.colorbar(im2, ax=ax2, shrink=0.6)
ax2.set_title('Method 2: Grid Edges (Light)\n(Shows discrete cells)', fontsize=10, fontweight='bold')
ax2.text(0.02, 0.98, 'Grid structure clear', transform=ax2.transAxes,
         fontsize=9, va='top', bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))

# Method 3: No state boundaries
ax3 = plt.subplot(2, 3, 3, projection=ccrs.PlateCarree())
im3 = ax3.pcolormesh(
    data_ds.lon, data_ds.lat, t2m_state,
    cmap='RdYlBu_r', vmin=20, vmax=35,
    transform=ccrs.PlateCarree()
)
ax3.add_feature(cfeature.COASTLINE, linewidth=0.8)
ax3.set_extent([-107, -93, 25.5, 36.5])
plt.colorbar(im3, ax=ax3, shrink=0.6)
ax3.set_title('Method 3: No State Boundaries\n(Clean, no mismatch)', fontsize=10, fontweight='bold')
ax3.text(0.02, 0.98, 'No visual conflict', transform=ax3.transAxes,
         fontsize=9, va='top', bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))

# Method 4: Thick semi-transparent boundaries
ax4 = plt.subplot(2, 3, 4, projection=ccrs.PlateCarree())
im4 = ax4.pcolormesh(
    data_ds.lon, data_ds.lat, t2m_state,
    cmap='RdYlBu_r', vmin=20, vmax=35,
    transform=ccrs.PlateCarree()
)
ax4.add_feature(cfeature.STATES, linewidth=1.5, edgecolor='black', alpha=0.6)
ax4.set_extent([-107, -93, 25.5, 36.5])
plt.colorbar(im4, ax=ax4, shrink=0.6)
ax4.set_title('Method 4: Thick Boundaries\n(Emphasizes approximate nature)', fontsize=10, fontweight='bold')
ax4.text(0.02, 0.98, 'Sets expectations', transform=ax4.transAxes,
         fontsize=9, va='top', bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.7))

# Method 5: Grid edges + state boundaries
ax5 = plt.subplot(2, 3, 5, projection=ccrs.PlateCarree())
im5 = ax5.pcolormesh(
    data_ds.lon, data_ds.lat, t2m_state,
    cmap='RdYlBu_r', vmin=20, vmax=35,
    edgecolors='white', linewidth=0.2,
    transform=ccrs.PlateCarree()
)
ax5.add_feature(cfeature.STATES, linewidth=1.0, edgecolor='black')
ax5.set_extent([-107, -93, 25.5, 36.5])
plt.colorbar(im5, ax=ax5, shrink=0.6)
ax5.set_title('Method 5: Both Grid + Boundaries\n(Most informative)', fontsize=10, fontweight='bold')
ax5.text(0.02, 0.98, 'Shows data + context', transform=ax5.transAxes,
         fontsize=9, va='top', bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))

# Method 6: imshow (nearest neighbor)
ax6 = plt.subplot(2, 3, 6, projection=ccrs.PlateCarree())
im6 = ax6.imshow(
    t2m_state,
    cmap='RdYlBu_r', vmin=20, vmax=35,
    origin='lower',
    extent=[data_ds.lon.min(), data_ds.lon.max(), 
            data_ds.lat.min(), data_ds.lat.max()],
    interpolation='nearest',
    transform=ccrs.PlateCarree()
)
ax6.add_feature(cfeature.STATES, linewidth=0.5, edgecolor='black')
ax6.set_extent([-107, -93, 25.5, 36.5])
plt.colorbar(im6, ax=ax6, shrink=0.6)
ax6.set_title('Method 6: imshow (nearest)\n(Alternative rendering)', fontsize=10, fontweight='bold')
ax6.text(0.02, 0.98, 'Blocky pixels', transform=ax6.transAxes,
         fontsize=9, va='top', bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.7))

plt.suptitle('Visualization Comparison: Texas Temperature (2020-06-15)\nCentroid-Based Assignment vs Display Methods', 
             fontsize=14, fontweight='bold', y=0.995)

plt.tight_layout()
plt.savefig('visualization_comparison.png', dpi=150, bbox_inches='tight')
print("\nSaved: visualization_comparison.png")

# Close datasets
mask_ds.close()
data_ds.close()
