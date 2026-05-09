# Experimental Design Notebooks - User Guide

## Quick Start

**→ Use this notebook**: [01b_experimental_design_from_processed.ipynb](01b_experimental_design_from_processed.ipynb) ✅

This notebook:
- ✅ Uses pre-processed monthly data (FAST - ~5 min for full dataset)
- ✅ Handles missing values in cattle data automatically
- ✅ Creates analysis-ready dataset with all predictors
- ✅ Includes Thermal Acclimation State (TAS) calculation
- ✅ Merges climate predictors with cattle slaughter data

---

## Notebook Overview

### Active Notebooks

#### 1. [00_data_verification.ipynb](00_data_verification.ipynb)
**Purpose**: Verify raw MERRA-2 data quality

**Use When**:
- First time setup
- Checking for data gaps
- Validating spatial coverage

**Data Source**: `daily_data/` (raw hourly files)

**Run Time**: ~2-3 minutes

---

#### 2. [01b_experimental_design_from_processed.ipynb](01b_experimental_design_from_processed.ipynb) ⭐ **RECOMMENDED**
**Purpose**: Construct all predictors and merge with cattle data

**Use When**:
- Creating analysis dataset
- Running experimental design pipeline
- Preparing data for DLNM/regression

**Data Sources**:
- `processed_daytime_heat/` (504 monthly files)
- `processed_nighttime_recovery/` (504 monthly files)
- `processed_vpd/` (504 monthly files)
- `cattle_data/cattle_data_clean.csv`

**Run Time**:
- Sample (3 months): ~30 seconds
- Full dataset (1984-2025): ~3-5 minutes

**Outputs**:
- `analysis_ready_YYYYMM.csv` - Complete dataset with:
  - Climate predictors (nighttime, daytime, VPD)
  - Thermal Acclimation State (TAS)
  - Interaction terms
  - 1-4 week lags
  - Cattle slaughter outcomes (raw and log-transformed)
- `analysis_ready_YYYYMM_metadata.json` - Dataset documentation

**Missing Value Handling**:
- ✅ Automatically checks for missing cattle data
- ✅ Reports missing value statistics
- ✅ Drops rows with missing outcomes (clean dataset for regression)
- ✅ Creates log-transformed outcomes: `log(slaughter + 0.1)`

---

### Removed Notebooks

The original slow experimental design notebook (`01_experimental_design_setup.ipynb`) has been **removed** as it was redundant and 20x slower than the current approach. There is now only one experimental design notebook to avoid confusion.

---

## Data Flow

```
Pre-Processed Data                   Experimental Design Notebook         Analysis-Ready Output
processed_*/                         01b_experimental_design_             analysis_ready_*.csv
├── daytime_heat_*.nc         ─────▶ from_processed.ipynb          ─────▶ (climate + cattle merged)
├── nighttime_recovery_*.nc                                               ├── All predictors
└── vpd_*.nc                         cattle_data/                         ├── TAS variable
                                     cattle_data_clean.csv                ├── Lagged variables
                                                                          ├── Interaction terms
                                                                          └── Outcomes (raw + log)
```

---

## Handling Missing Cattle Data

The notebook automatically:

1. **Detects missing values**:
   ```
   Missing slaughter data in overlap period: 0 (0.00%)
   ```

2. **Reports options**:
   - Drop rows (default, recommended for regression)
   - Interpolate (caution: may introduce bias)
   - Keep as-is (some models handle NaN)

3. **Creates clean dataset**:
   - Drops rows where `slaughter_beef_dairy` is NaN
   - Reports how many rows dropped
   - Final dataset has no missing outcomes

### Example Output

```
Missing slaughter data in overlap period: 15 (1.2%)

⚠️  WARNING: Some weeks have missing slaughter data
Options for handling missing values:
  1. Drop rows with missing slaughter data (recommended for regression)
  2. Interpolate missing values (caution: may introduce bias)
  3. Use as-is (some models can handle NaN)

Final analysis dataset (after dropping missing outcomes):
  Shape: (1235, 156)
  Rows dropped: 15
  Regions: 2
  Weeks per region: 617
```

---

## Predictor Variables

### Nighttime Recovery (8pm-6am, 10 hours)
- `night_strong_recovery_hrs` - Hours 0°C < T < 18°C
- `night_reasonable_recovery_hrs` - Hours 0°C < T < 21°C
- `night_poor_recovery_hrs` - Hours T > 21°C
- `night_bad_hrs` - Hours T > 24°C
- `night_below_0c_hrs`, `night_below_neg5c_hrs`, `night_below_neg10c_hrs` - Cold stress

### Daytime Heat (8am-8pm, 12 hours)
- `day_above_25c_hrs` - Moderate heat
- `day_above_30c_hrs` - Intense heat
- `day_above_35c_hrs` - Severe heat
- `day_above_40c_hrs` - Extreme heat
- `day_below_5c_hrs`, `day_below_0c_hrs`, `day_below_neg5c_hrs` - Cold stress

### VPD (12pm-6pm, 6 hours)
- `vpd_afternoon_mean` - Mean VPD (kPa)
- `vpd_afternoon_max` - Max VPD (kPa)
- `vpd_afternoon_min` - Min VPD (kPa)

### Thermal Acclimation State (TAS) 🆕
- `tas` - Mean weekly TAS (0-1)
- `tas_max` - Peak weekly TAS (0-1)

**Innovation**: First market-level implementation of physiological acclimation state

### Interaction Terms
- `day_heat_x_vpd` - Heat-humidity compound stress
- `bad_night_into_heat_sum` - No-recovery sequences

### Lagged Variables
All predictors available at 1, 2, 3, and 4 week lags:
- `{variable}_lag1`, `{variable}_lag2`, etc.

---

## Outcome Variables

### Raw Slaughter Counts
- `slaughter_beef_dairy` - Combined beef + dairy (thousands of head)
- `slaughter_dairy` - Dairy only (thousands of head)

### Log-Transformed (Recommended for Regression)
- `log_slaughter_beef_dairy` = log(slaughter_beef_dairy + 0.1)
- `log_slaughter_dairy` = log(slaughter_dairy + 0.1)

**Why log-transform**:
- Handles right skew in count data
- Coefficients interpretable as percent changes
- Standard practice in cattle economics literature

---

## Usage Examples

### Example 1: Process Sample Period (Summer 2020)

```python
# Cell 3-4: Define date range
start_year = 2020
start_month = 6
end_year = 2020
end_month = 8

# Run all cells → Outputs: analysis_ready_2020_summer.csv
```

### Example 2: Process Full Dataset (1984-2025)

```python
# Cell 3-4: Define date range
start_year = 1984
start_month = 1
end_year = 2025
end_month = 12

# Run all cells → Outputs: analysis_ready_full.csv
# Expected time: ~3-5 minutes
```

### Example 3: Check for Missing Data

```python
# After running Cell 19 (merge cell), check output:
# "Missing slaughter data in overlap period: X (Y%)"
#
# If Y% > 5%, investigate:
# - Which weeks are missing?
# - Is it systematic (e.g., early years, specific regions)?
# - Decision: drop, interpolate, or model as-is
```

---

## Output Dataset Structure

### Dimensions
- **Rows**: ~2,100 (per region) for full 1984-2025 period
- **Columns**: ~150-200 (base predictors + lags)
- **Regions**: 2 (region_4: Southeast, region_6: South Central)

### Column Types
1. **Identifiers**: `region`, `week_ending`
2. **Climate predictors**: ~20 base variables
3. **Lagged predictors**: 4 lags × 20 variables = 80 variables
4. **Interaction terms**: 2 variables
5. **TAS variables**: 2 variables
6. **Outcomes**: 4 variables (raw + log, beef+dairy + dairy)

### File Formats
- **CSV**: Full dataset with all columns
- **JSON**: Metadata (column names, date range, notes)

---

## Verification Checklist

Before analysis, verify:

- [ ] All processed monthly files exist (504 × 3 = 1,512 files)
  ```bash
  ls processed_daytime_heat/ | wc -l  # Should be 504
  ls processed_nighttime_recovery/ | wc -l  # Should be 504
  ls processed_vpd/ | wc -l  # Should be 504
  ```

- [ ] Cattle data loaded successfully
  ```python
  # Check in notebook output:
  # "Cattle data loaded: Total weeks: 2,XXX"
  ```

- [ ] Date ranges overlap
  ```python
  # Check in notebook output:
  # "Overlap: 1984-01-07 to 2025-XX-XX"
  ```

- [ ] Missing values handled
  ```python
  # Check in notebook output:
  # "Rows dropped: X"  (should be small, < 5%)
  ```

- [ ] Output file created
  ```bash
  ls processed_weekly/analysis_ready_*.csv
  ```

---

## Troubleshooting

### Issue: "File not found" error for processed files

**Solution**: Run the processing notebooks first:
```bash
cd notebooks/02_data_processing/
# Run: process_daytime_heat_stats.ipynb
# Run: process_nighttime_recovery_stats.ipynb
# Run: process_vpd_stats.ipynb
```

---

### Issue: Cattle data not loading

**Solution**: Check file path in config.py:
```python
import config
print(config.CATTLE_DATA_FILE)
# Should point to: cattle_data/cattle_data_clean.csv
```

---

### Issue: High percentage of missing cattle data (>10%)

**Possible Causes**:
1. Date mismatch (cattle uses Saturday week-ending, check merge key)
2. Early years have no cattle data (expected before 1984)
3. Data quality issue in cattle file

**Solution**: Inspect missing weeks:
```python
missing_weeks = merged_df_overlap[merged_df_overlap['slaughter_beef_dairy'].isnull()]
print(missing_weeks[['region', 'week_ending']])
```

---

### Issue: Memory error when processing full dataset

**Solutions**:
1. Process in chunks (e.g., by year)
2. Increase available RAM
3. Use server/cluster instead of laptop

**Code for chunking**:
```python
for year in range(1984, 2026):
    start_year = year
    end_year = year
    # Run processing
    # Save output
```

---

## Next Steps After Creating Dataset

1. **Exploratory Data Analysis**
   - Time series plots of TAS
   - Correlation matrix of predictors
   - Seasonal patterns

2. **Panel Regression** (Python)
   - OLS with region fixed effects
   - Validate predictors

3. **DLNM Analysis** (R)
   - Export CSV to R
   - Use `dlnm` package
   - TAS × temperature cross-basis

4. **Causal Forest** (R/Python)
   - Heterogeneous treatment effects
   - Regional differences

---

## References

- **CLAUDE.md** - Complete project documentation
- **LITERATURE_GAPS_AND_NOVEL_METHODS.md** - Scientific rationale for TAS
- **DATA_FLOW_COMPARISON.md** - Detailed comparison of processing approaches

---

**Last Updated**: March 31, 2026
**Maintained By**: Kyle Lesinger
**Questions**: See CLAUDE.md or LITERATURE_GAPS_AND_NOVEL_METHODS.md
