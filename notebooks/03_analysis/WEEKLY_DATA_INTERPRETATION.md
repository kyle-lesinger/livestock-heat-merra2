# Weekly Data Interpretation Guide

## Data Units and Ranges

### Temperature Threshold Metrics (Hours per Week)

**Daytime Heat Metrics** (`hours_above_*`, `hours_below_*` in `ds_day`):
- **Units**: Hours per week
- **Range**: 0 to 168 hours (7 days × 24 hours/day)
- **Interpretation**: Total hours during the week where temperature exceeded/fell below threshold

Example: `hours_above_30 = 84` means 84 hours during that week were above 30°C (50% of the week)

**Nighttime Recovery Metrics** (`hours_above_*`, `hours_below_*` in `ds_night`):
- **Units**: Hours per week
- **Range**: 0 to 70 hours (7 days × 10 nighttime hours/day)
- **Note**: Nighttime defined as 8 PM to 6 AM local time (10 hours)
- **Interpretation**: Total nighttime hours during the week where temperature exceeded/fell below threshold

Example: `hours_above_24 = 35` means 35 nighttime hours above 24°C (50% of nighttime hours that week)

### VPD Metrics (kPa)

**Afternoon VPD** (`vpd_mean`, `vpd_min`, `vpd_max` in `ds_vpd`):
- **Units**: kilopascals (kPa)
- **Range**: Typically 0 to 6 kPa
- **Interpretation**: Weekly average of afternoon (12-6 PM) vapor pressure deficit

Example: `vpd_mean = 2.5` indicates moderate atmospheric dryness

## Converting to More Intuitive Units

### Average Hours Per Day

To convert weekly hours to average daily hours:

```python
# For all-day metrics (0-168 range)
daily_avg = weekly_hours / 7

# Example: 84 weekly hours → 12 hours/day
```

### Percentage of Time

To convert to percentage of available time:

```python
# For all-day metrics
percentage = (weekly_hours / 168) * 100

# For nighttime-only metrics
percentage = (weekly_hours / 70) * 100

# Example: 84 weekly hours → 50% of the week
```

## Typical Values by Season

### Summer (Texas Example)

**Daytime Heat:**
- `hours_above_30`: 50-120 hours/week (7-17 hrs/day)
- `hours_above_35`: 20-80 hours/week (3-11 hrs/day)

**Nighttime Recovery:**
- `hours_above_24`: 10-50 hours/week (1-7 hrs/night, or 14-71% of nights)
- `hours_above_21`: 30-70 hours/week (4-10 hrs/night, or 43-100% of nights)

**VPD:**
- `vpd_mean`: 2.0-4.0 kPa (high atmospheric dryness)

### Winter (Texas Example)

**Daytime Heat:**
- `hours_above_30`: 0-10 hours/week (0-1 hrs/day)
- `hours_below_5`: 20-80 hours/week (3-11 hrs/day)

**Nighttime Recovery:**
- `hours_above_24`: 0-5 hours/week (rare)
- `hours_below_0`: 10-40 hours/week (1-6 hrs/night of freezing)

**VPD:**
- `vpd_mean`: 0.5-1.5 kPa (lower atmospheric dryness)

## Data Quality Notes

1. **Timedelta Conversion**: The `load_weekly_data()` function automatically converts timedelta64[ns] to float hours for ease of use.

2. **Spatial Averaging**: When using `compute_state_mean()`, values represent the spatial average across all grid cells in that state.

3. **Missing Data**: Fill values (-1 in raw data) are replaced with NaN during aggregation.

4. **Week Definition**: Weeks end on Saturday to match USDA cattle slaughter reporting weeks.

## Plotting Recommendations

### For Heatmaps

```python
# Option 1: Show hours per week with clear labeling
cbar_kws={'label': 'Hours per Week'}

# Option 2: Convert to average hours per day
data_daily_avg = data / 7
cbar_kws={'label': 'Average Hours per Day'}

# Option 3: Show as percentage
data_pct = (data / 168) * 100  # For all-day metrics
cbar_kws={'label': '% of Week'}
```

### For Time Series

```python
# Add context to y-axis labels
ax.set_ylabel('Weekly Hours Above 30°C\\n(0-168 range)')

# Or convert to daily average
ax.set_ylabel('Daily Average Hours Above 30°C\\n(0-24 range)')
```

## Example: Calendar Heatmap Interpretation

If a cell shows:
- **Nighttime hours_above_24 = 42**: That week had 42 hours (out of 70 possible nighttime hours) above 24°C
  - Percentage: 42/70 = 60% of nighttime hours
  - Per night: 42/7 = 6 hours/night on average

- **Daytime hours_above_30 = 98**: That week had 98 hours (out of 168 total hours) above 30°C
  - Percentage: 98/168 = 58% of the week
  - Per day: 98/7 = 14 hours/day on average
