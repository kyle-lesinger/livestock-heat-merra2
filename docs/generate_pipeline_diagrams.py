"""Generate data pipeline diagrams as PNG files."""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# Common styling
COLORS = {
    'source': '#e8f4fd',
    'source_edge': '#2196f3',
    'notebook': '#fff3e0',
    'notebook_edge': '#ff9800',
    'output': '#e8f5e9',
    'output_edge': '#4caf50',
    'intermediate': '#fce4ec',
    'intermediate_edge': '#e91e63',
    'weekly': '#f3e5f5',
    'weekly_edge': '#9c27b0',
    'cache': '#f5f5f5',
    'cache_edge': '#9e9e9e',
    'paper': '#fff9c4',
    'paper_edge': '#fbc02d',
    'central': '#c8e6c9',
    'central_edge': '#2e7d32',
}


def draw_box(ax, x, y, w, h, text, color, edge_color, fontsize=8, bold_title=None, alpha=1.0):
    """Draw a rounded box with text."""
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.15",
                         facecolor=color, edgecolor=edge_color, linewidth=1.5, alpha=alpha)
    ax.add_patch(box)
    if bold_title:
        ax.text(x + w/2, y + h - 0.3, bold_title, ha='center', va='top',
                fontsize=fontsize, fontweight='bold', wrap=True)
        ax.text(x + w/2, y + h/2 - 0.15, text, ha='center', va='center',
                fontsize=fontsize - 1, wrap=True, style='italic')
    else:
        ax.text(x + w/2, y + h/2, text, ha='center', va='center',
                fontsize=fontsize, wrap=True)


def draw_arrow(ax, x1, y1, x2, y2, label=None, color='#555', style='->', dashed=False):
    """Draw an arrow between two points."""
    ls = '--' if dashed else '-'
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=color, lw=1.5, linestyle=ls))
    if label:
        mx, my = (x1+x2)/2, (y1+y2)/2
        ax.text(mx + 0.1, my + 0.15, label, fontsize=6.5, color='#666', style='italic')


# =========================================================================
# DIAGRAM 1: Data Acquisition
# =========================================================================
fig, ax = plt.subplots(figsize=(14, 8))
ax.set_xlim(-0.5, 14)
ax.set_ylim(-0.5, 8.5)
ax.axis('off')
ax.set_title('1. Data Acquisition', fontsize=16, fontweight='bold', pad=20)

# Raw sources (top row)
draw_box(ax, 0, 6.5, 3, 1.5, 'Hourly T2M, QV2M, PS\n0.625 x 0.5 deg grid',
         COLORS['source'], COLORS['source_edge'], bold_title='MERRA-2 M2T1NXSLV')
draw_box(ax, 3.5, 6.5, 3, 1.5, 'Hourly soil moisture\n& precipitation',
         COLORS['source'], COLORS['source_edge'], bold_title='MERRA-2 M2T1NXLND')
draw_box(ax, 7, 6.5, 3, 1.5, 'Weekly slaughter counts\n10 regions, 1984-2027',
         COLORS['source'], COLORS['source_edge'], bold_title='USDA Dcowslt-13.xlsx')
draw_box(ax, 10.5, 6.5, 3, 1.5, 'Annual cattle inventory\nby state (head count)',
         COLORS['source'], COLORS['source_edge'], bold_title='USDA NASS API')

# Processing notebooks (middle row)
draw_box(ax, 0, 3.8, 3, 1.5, '01_data_ingestion/\nCDO: subset US bbox\ncalc VPD, convert C',
         COLORS['notebook'], COLORS['notebook_edge'], bold_title='process_merra2_cdo_t2m_vpd.ipynb')
draw_box(ax, 3.5, 3.8, 3, 1.5, '01_data_ingestion/\nCDO: subset US bbox\nconvert precip units',
         COLORS['notebook'], COLORS['notebook_edge'], bold_title='process_merra2_soil_precip_cdo.ipynb')
draw_box(ax, 7, 3.8, 3, 1.5, '02_data_processing/\nParse Excel, clean\nreshape wide/long',
         COLORS['notebook'], COLORS['notebook_edge'], bold_title='process_cattle_data.ipynb')

# Output files (bottom row)
draw_box(ax, 0, 0.8, 3, 2, 'merra2_us_YYYYMMDD.nc\n~15,300 files\n\nT2M (deg C)\nVPD (kPa)\n24 hourly timesteps',
         COLORS['output'], COLORS['output_edge'], bold_title='data/daily_data/')
draw_box(ax, 3.5, 0.8, 3, 2, 'merra2_soil_precip_us_\nYYYYMMDD.nc  ~15,300 files\n\nSFMC, RZMC, GWETROOT\nPRECIP_TOTAL, PRECIP_SNOW',
         COLORS['output'], COLORS['output_edge'], bold_title='data/daily_data_soil_precip/')
draw_box(ax, 7, 0.8, 3, 2, 'cattle_data_clean.csv\n2,254 weeks x 28 cols\n\ncattle_data_long.csv\n37,289 rows x 5 cols',
         COLORS['output'], COLORS['output_edge'], bold_title='data/cattle_data/')
draw_box(ax, 10.5, 3.8, 3, 1.5, 'nass_cattle_inventory.csv\nRegional annual totals\n1984-2025',
         COLORS['output'], COLORS['output_edge'], bold_title='data/cattle_data/')

# Arrows
draw_arrow(ax, 1.5, 6.5, 1.5, 5.3)
draw_arrow(ax, 5, 6.5, 5, 5.3)
draw_arrow(ax, 8.5, 6.5, 8.5, 5.3)
draw_arrow(ax, 12, 6.5, 12, 5.3, label='REST API')

draw_arrow(ax, 1.5, 3.8, 1.5, 2.8)
draw_arrow(ax, 5, 3.8, 5, 2.8)
draw_arrow(ax, 8.5, 3.8, 8.5, 2.8)

# Legend
legend_items = [
    mpatches.Patch(facecolor=COLORS['source'], edgecolor=COLORS['source_edge'], label='Raw Data Source'),
    mpatches.Patch(facecolor=COLORS['notebook'], edgecolor=COLORS['notebook_edge'], label='Processing Notebook'),
    mpatches.Patch(facecolor=COLORS['output'], edgecolor=COLORS['output_edge'], label='Output File'),
]
ax.legend(handles=legend_items, loc='lower right', fontsize=8, framealpha=0.9)

plt.tight_layout()
plt.savefig('/Users/klesinger/Library/CloudStorage/GoogleDrive-kdl0040@uah.edu/My Drive/VEDA/Stories/livestock_and_heat/research/docs/pipeline_01_data_acquisition.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("Saved: pipeline_01_data_acquisition.png")


# =========================================================================
# DIAGRAM 2: Climate Processing Pipeline
# =========================================================================
fig, ax = plt.subplots(figsize=(14, 10))
ax.set_xlim(-0.5, 14)
ax.set_ylim(-0.5, 10.5)
ax.axis('off')
ax.set_title('2. Climate Processing Pipeline', fontsize=16, fontweight='bold', pad=20)

# Input (top)
draw_box(ax, 1, 8.8, 4.5, 1.2, 'merra2_us_YYYYMMDD.nc\nT2M + VPD (hourly, gridded)',
         COLORS['notebook'], COLORS['notebook_edge'], bold_title='data/daily_data/')
draw_box(ax, 7, 8.8, 4.5, 1.2, 'state_mask, region IDs\n48 states, 10 regions',
         COLORS['source'], COLORS['source_edge'], bold_title='masks/region_mask.nc')

# Three parallel processing tracks
# Nighttime
draw_box(ax, 0, 6.3, 4, 1.8, 'process_nighttime_recovery_stats.ipynb\nHours 20-23, 0-5 UTC (10 hrs/night)\n\nhrs_above_21 (poor recovery)\nhrs_above_24 (very poor)\nhrs_below_0, _neg5, _neg10',
         COLORS['intermediate'], COLORS['intermediate_edge'], bold_title='Nighttime Recovery (8 vars)')

# Daytime
draw_box(ax, 5, 6.3, 4, 1.8, 'process_daytime_heat_stats.ipynb\nHours 8-19 UTC (12 hrs/day)\n\nhrs_above_25, _30, _35, _40\nhrs_below_neg5, _0, _5',
         COLORS['intermediate'], COLORS['intermediate_edge'], bold_title='Daytime Heat (7 vars)')

# VPD
draw_box(ax, 10, 6.3, 3.5, 1.8, 'process_vpd_stats.ipynb\nHours 12-17 UTC (afternoon)\n\nvpd_mean, vpd_max\nvpd_min (kPa)',
         COLORS['intermediate'], COLORS['intermediate_edge'], bold_title='VPD Stats (3 vars)')

# Monthly files
draw_box(ax, 0, 4, 4, 1.2, 'nighttime_recovery_YYYYMM.nc\n504 files (42 yrs x 12 mo)',
         COLORS['intermediate'], COLORS['intermediate_edge'], fontsize=7)
draw_box(ax, 5, 4, 4, 1.2, 'daytime_heat_YYYYMM.nc\n504 files (42 yrs x 12 mo)',
         COLORS['intermediate'], COLORS['intermediate_edge'], fontsize=7)
draw_box(ax, 10, 4, 3.5, 1.2, 'vpd_YYYYMM.nc\n504 files (42 yrs x 12 mo)',
         COLORS['intermediate'], COLORS['intermediate_edge'], fontsize=7)

# Weekly aggregation
draw_box(ax, 3, 1.8, 7.5, 1.5, 'Spatial mean per region  |  Daily to weekly aggregation\n'
         'Temp thresholds: SUM (total hrs/week)  |  VPD: MEAN (avg kPa)\n'
         'Week boundary: Sun-Sat (aligned to USDA cattle weeks)',
         COLORS['notebook'], COLORS['notebook_edge'], bold_title='aggregate_weekly_cattle_aligned.ipynb')

# Weekly output
draw_box(ax, 0.5, -0.2, 4, 1.2, 'weekly_nighttime_recovery.nc\nweekly_daytime_heat.nc\nweekly_vpd.nc',
         COLORS['weekly'], COLORS['weekly_edge'], bold_title='processed_weekly/')

ax.text(5.5, 0.4, '~2,191 weeks\n(1984-2025)\nlat x lon grid', fontsize=8, ha='left', va='center', color='#666')

# Arrows
draw_arrow(ax, 3.25, 8.8, 2, 8.1)
draw_arrow(ax, 3.25, 8.8, 7, 8.1)
draw_arrow(ax, 3.25, 8.8, 11.75, 8.1)
draw_arrow(ax, 9.25, 8.8, 9.25, 8.1, label='mask applied')

draw_arrow(ax, 2, 6.3, 2, 5.2)
draw_arrow(ax, 7, 6.3, 7, 5.2)
draw_arrow(ax, 11.75, 6.3, 11.75, 5.2)

draw_arrow(ax, 2, 4, 5, 3.3)
draw_arrow(ax, 7, 4, 7, 3.3)
draw_arrow(ax, 11.75, 4, 9, 3.3)

draw_arrow(ax, 5, 1.8, 3, 1.0)

plt.tight_layout()
plt.savefig('/Users/klesinger/Library/CloudStorage/GoogleDrive-kdl0040@uah.edu/My Drive/VEDA/Stories/livestock_and_heat/research/docs/pipeline_02_climate_processing.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("Saved: pipeline_02_climate_processing.png")


# =========================================================================
# DIAGRAM 3: Paper Notebook Flow
# =========================================================================
fig, ax = plt.subplots(figsize=(14, 10))
ax.set_xlim(-0.5, 14)
ax.set_ylim(-0.5, 10.5)
ax.axis('off')
ax.set_title('3. Paper Notebook Flow', fontsize=16, fontweight='bold', pad=20)

# Input data (top row)
draw_box(ax, 0, 8.5, 3.2, 1.5, 'weekly_nighttime_recovery.nc\nweekly_daytime_heat.nc\nweekly_vpd.nc',
         COLORS['source'], COLORS['source_edge'], bold_title='Weekly Climate')
draw_box(ax, 3.7, 8.5, 3.2, 1.5, 'cattle_data_clean.csv\n2,254 weeks\n10 regions',
         COLORS['source'], COLORS['source_edge'], bold_title='Cattle Slaughter')
draw_box(ax, 7.4, 8.5, 3, 1.5, 'region_mask.nc\nState/region\nboundaries',
         COLORS['source'], COLORS['source_edge'], bold_title='Region Masks')
draw_box(ax, 10.9, 8.5, 2.6, 1.5, 'nass_cattle_\ninventory.csv\n(annual herd size)',
         COLORS['source'], COLORS['source_edge'], bold_title='NASS Inventory')

# paper_01
draw_box(ax, 0.5, 6, 12.5, 1.8,
         'Load weekly data  ->  Regional aggregation (vectorized)  ->  Merge climate + cattle\n'
         '->  NASS herd normalization  ->  Lags (1,2,3,4,8 wk)  ->  Rolling avg (2,4,8 wk)\n'
         '->  Zero-inflated features  ->  Interactions  ->  Cyclical time  ->  Export CSV',
         COLORS['notebook'], COLORS['notebook_edge'], bold_title='paper_01_data_preparation.ipynb')

# Cache boxes
draw_box(ax, -0.3, 4.5, 3, 0.9, 'climate_weekly_regional.csv\n(skip 3-min recompute)',
         COLORS['cache'], COLORS['cache_edge'], fontsize=7)

# Central artifact
draw_box(ax, 4, 4.2, 5.5, 1.2, 'paper_analysis_ready.csv\n4,382 rows x 271 columns  |  2 regions  |  1984-2025',
         COLORS['central'], COLORS['central_edge'], bold_title='CENTRAL DATASET')

# paper_02, 03, 04
draw_box(ax, 0, 1.5, 4, 2,
         'Mann-Kendall trends\nVPD dose-response\nNighttime recovery\nCompound stress\nLag analysis\nRegional comparison (SE vs SC)',
         COLORS['notebook'], COLORS['notebook_edge'], bold_title='paper_02: Exploratory Analysis')

draw_box(ax, 5, 1.5, 4, 2,
         'Train: 1984-2015 / Test: 2016-2025\nRidge, Random Forest, XGBoost\nSHAP feature importance\nPartial dependence plots',
         COLORS['notebook'], COLORS['notebook_edge'], bold_title='paper_03: Predictive Modeling')

draw_box(ax, 10, 1.5, 3.5, 2,
         'Threshold identification\n(bootstrap CIs)\nRegional risk assessment\nPolicy recommendations',
         COLORS['notebook'], COLORS['notebook_edge'], bold_title='paper_04: Interpretation')

# Outputs
draw_box(ax, 0, -0.3, 5, 1, 'fig02-fig16 (PNG)\ntable1, table2 (CSV)',
         COLORS['paper'], COLORS['paper_edge'], bold_title='figures/paper/')
draw_box(ax, 5.5, -0.3, 3.5, 1, 'best_model.pkl\nscaler, features',
         COLORS['paper'], COLORS['paper_edge'], bold_title='cattle_data/models/')

# Arrows - inputs to paper_01
draw_arrow(ax, 1.6, 8.5, 3, 7.8)
draw_arrow(ax, 5.3, 8.5, 5.3, 7.8)
draw_arrow(ax, 8.9, 8.5, 8.9, 7.8)
draw_arrow(ax, 12.2, 8.5, 11, 7.8)

# paper_01 to cache
draw_arrow(ax, 2, 6, 1.5, 5.4, dashed=True, label='cache')

# paper_01 to central CSV
draw_arrow(ax, 6.75, 6, 6.75, 5.4)

# CSV to paper_02, 03
draw_arrow(ax, 5.5, 4.2, 2, 3.5)
draw_arrow(ax, 6.75, 4.2, 7, 3.5)

# paper_03 to paper_04
draw_arrow(ax, 9, 2.5, 10, 2.5)

# Notebooks to outputs
draw_arrow(ax, 2, 1.5, 2, 0.7)
draw_arrow(ax, 7, 1.5, 7, 0.7)
draw_arrow(ax, 11.75, 1.5, 11, 0.7, dashed=True)

legend_items = [
    mpatches.Patch(facecolor=COLORS['source'], edgecolor=COLORS['source_edge'], label='Input Data'),
    mpatches.Patch(facecolor=COLORS['notebook'], edgecolor=COLORS['notebook_edge'], label='Notebook'),
    mpatches.Patch(facecolor=COLORS['central'], edgecolor=COLORS['central_edge'], label='Central Dataset'),
    mpatches.Patch(facecolor=COLORS['paper'], edgecolor=COLORS['paper_edge'], label='Final Output'),
    mpatches.Patch(facecolor=COLORS['cache'], edgecolor=COLORS['cache_edge'], label='Cache (optional)'),
]
ax.legend(handles=legend_items, loc='lower right', fontsize=8, framealpha=0.9)

plt.tight_layout()
plt.savefig('/Users/klesinger/Library/CloudStorage/GoogleDrive-kdl0040@uah.edu/My Drive/VEDA/Stories/livestock_and_heat/research/docs/pipeline_03_paper_flow.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("Saved: pipeline_03_paper_flow.png")


# =========================================================================
# DIAGRAM 4: Feature Engineering
# =========================================================================
fig, ax = plt.subplots(figsize=(14, 7))
ax.set_xlim(-0.5, 14)
ax.set_ylim(-0.5, 7.5)
ax.axis('off')
ax.set_title('4. Feature Engineering (paper_01)', fontsize=16, fontweight='bold', pad=20)

# Base variables (left)
draw_box(ax, 0, 5, 3.5, 2, 'Nighttime (8 vars)\nhrs_above_21, _24\nhrs_below_18, _21, _24\nhrs_below_0, _neg5, _neg10',
         COLORS['source'], COLORS['source_edge'], bold_title='Nighttime Recovery')
draw_box(ax, 0, 2.5, 3.5, 2, 'Daytime (7 vars)\nhrs_above_25, _30, _35, _40\nhrs_below_neg5, _0, _5',
         COLORS['source'], COLORS['source_edge'], bold_title='Daytime Heat')
draw_box(ax, 0, 0.3, 3.5, 1.5, 'vpd_mean\nvpd_min, vpd_max',
         COLORS['source'], COLORS['source_edge'], bold_title='VPD (3 vars)')

# Feature transforms (middle column)
draw_box(ax, 5, 5.8, 3.5, 1.2, 'Each var x 5 lags\n(1, 2, 3, 4, 8 weeks)\n= 90 columns',
         COLORS['intermediate'], COLORS['intermediate_edge'], bold_title='Lagged (90)')

draw_box(ax, 5, 4.2, 3.5, 1.2, 'Each var x 3 windows\n(2, 4, 8 weeks)\n= 54 columns',
         COLORS['intermediate'], COLORS['intermediate_edge'], bold_title='Rolling Avg (54)')

draw_box(ax, 5, 2.6, 3.5, 1.2, 'Sparse vars only\n_has (binary) + _log1p\n~30 columns',
         COLORS['intermediate'], COLORS['intermediate_edge'], bold_title='Zero-Inflated (~30)')

draw_box(ax, 5, 1, 3.5, 1.2, 'heat x VPD\nextreme_heat x poor_recovery\nweek_sin/cos, year, month',
         COLORS['intermediate'], COLORS['intermediate_edge'], bold_title='Interactions + Time (6)')

# Outcome variables
draw_box(ax, 5, -0.2, 3.5, 0.8, 'slaughter_beef_dairy, slaughter_dairy\n+ log transforms + herd-normalized rate',
         COLORS['paper'], COLORS['paper_edge'], fontsize=7, bold_title='Outcomes (4-7)')

# Final dataset (right)
draw_box(ax, 10, 2, 3.5, 3.5,
         'Base climate: 18\nLagged: 90\nRolling: 54\nZero-inflated: ~30\nInteractions: 2\nTime features: 4\nOutcomes: 4-7\nIdentifiers: 2\nNormalization: ~3\n\n4,382 rows\n(2 regions x ~2,191 weeks)',
         COLORS['central'], COLORS['central_edge'], bold_title='paper_analysis_ready.csv\n271 columns')

# Arrows from base to transforms
for y_target in [6.4, 4.8, 3.2, 1.6]:
    draw_arrow(ax, 3.5, 4.5, 5, y_target)

# Arrows from transforms to final
for y_src in [6.4, 4.8, 3.2, 1.6, 0.2]:
    draw_arrow(ax, 8.5, y_src, 10, 3.75)

plt.tight_layout()
plt.savefig('/Users/klesinger/Library/CloudStorage/GoogleDrive-kdl0040@uah.edu/My Drive/VEDA/Stories/livestock_and_heat/research/docs/pipeline_04_feature_engineering.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("Saved: pipeline_04_feature_engineering.png")

print("\nAll 4 diagrams generated successfully!")
