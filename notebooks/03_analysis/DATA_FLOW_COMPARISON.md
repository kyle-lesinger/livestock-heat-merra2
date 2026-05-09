# Data Flow Comparison: Raw vs Pre-Processed

## Issue Summary

The original experimental design notebook ([01_experimental_design_setup.ipynb](01_experimental_design_setup.ipynb)) reads **raw daily MERRA-2 files** and recalculates threshold statistics from hourly data. However, these statistics have **already been computed** and saved in the `processed_*` directories by the [02_data_processing](../02_data_processing/) notebooks.

This creates redundant computation and slower processing.

---

## Data Flow Diagram

### Current Approach (Redundant) ❌

```
Raw Daily Files                     Experimental Design
daily_data/                         01_experimental_design_setup.ipynb
├── merra2_us_19840101.nc    ─────▶ Recalculates threshold statistics
├── merra2_us_19840102.nc           from hourly data
├── ...                             (SLOW - processes ~15,000 files)
└── merra2_us_20251231.nc
     (24 hourly timesteps)
```

### Efficient Approach (Pre-Processed) ✅

```
Raw Daily Files                     Processing Notebooks               Monthly Processed Files
daily_data/                         02_data_processing/                processed_*/
├── merra2_us_*.nc           ─────▶ process_daytime_heat_stats.ipynb ─▶ processed_daytime_heat/
                                                                          ├── daytime_heat_198401.nc
                                                                          ├── ...
                                                                          └── daytime_heat_202512.nc
                                                                          (504 monthly files)

                                    process_nighttime_recovery_stats   ─▶ processed_nighttime_recovery/
                                                                          ├── nighttime_recovery_198401.nc
                                                                          ├── ...
                                                                          └── nighttime_recovery_202512.nc

                                    process_vpd_stats.ipynb           ─▶ processed_vpd/
                                                                          ├── vpd_198401.nc
                                                                          ├── ...
                                                                          └── vpd_202512.nc

                                                                                    │
                                                                                    ▼
                                                                          Experimental Design
                                                                          01b_experimental_design_from_processed.ipynb
                                                                          ✓ Loads pre-computed daily statistics
                                                                          ✓ FAST - processes 504×3 = 1,512 files
                                                                          ✓ Lower memory usage
```

---

## File Comparison

### Raw Daily Files (`daily_data/`)

**Format**: NetCDF4
**Count**: 15,341 files (one per day, 1984-2025)
**Variables**:
- `T2M(time, lat, lon)` - 24 hourly temperatures
- `VPD(time, lat, lon)` - 24 hourly VPD values

**Size**: ~570 KB per file → ~8.7 GB total

**Use Case**: Original MERRA-2 processing, exploratory analysis

---

### Processed Monthly Files (`processed_*/`)

**Format**: NetCDF4 with compression
**Count**: 504 files per dataset (monthly, 1984-2025)
**Variables** (daily statistics, NOT hourly):

#### `processed_daytime_heat/`
- `hours_above_25(time, lat, lon)` - Daily count (0-12)
- `hours_above_30(time, lat, lon)` - Daily count (0-12)
- `hours_above_35(time, lat, lon)` - Daily count (0-12)
- `hours_above_40(time, lat, lon)` - Daily count (0-12)
- `hours_below_5(time, lat, lon)` - Daily count (0-12)
- `hours_below_0(time, lat, lon)` - Daily count (0-12)
- `hours_below_neg5(time, lat, lon)` - Daily count (0-12)

#### `processed_nighttime_recovery/`
- `hours_below_18_above_0(time, lat, lon)` - Daily count (0-10)
- `hours_below_21_above_0(time, lat, lon)` - Daily count (0-10)
- `hours_below_24_above_0(time, lat, lon)` - Daily count (0-10)
- `hours_above_21(time, lat, lon)` - Daily count (0-10)
- `hours_above_24(time, lat, lon)` - Daily count (0-10)
- `hours_below_0(time, lat, lon)` - Daily count (0-10)
- `hours_below_neg5(time, lat, lon)` - Daily count (0-10)
- `hours_below_neg10(time, lat, lon)` - Daily count (0-10)

#### `processed_vpd/`
- `vpd_mean(time, lat, lon)` - Daily afternoon mean (kPa)
- `vpd_min(time, lat, lon)` - Daily afternoon min (kPa)
- `vpd_max(time, lat, lon)` - Daily afternoon max (kPa)

**Size**: ~3-4 MB per monthly file → ~2 GB per dataset → ~6 GB total

**Use Case**: Efficient processing for experimental design, regional analysis

---

## Notebook Comparison

### Original Notebook (Not Recommended) ❌

**File**: [01_experimental_design_setup.ipynb](01_experimental_design_setup.ipynb)

**Data Source**: `daily_data/` (raw hourly files)

**Processing Steps**:
1. Open daily file (24 hourly timesteps)
2. Extract nighttime hours (8pm-6am) → calculate thresholds
3. Extract daytime hours (8am-8pm) → calculate thresholds
4. Extract afternoon hours (12pm-6pm) → calculate VPD stats
5. Aggregate spatially to regions
6. Calculate TAS
7. Aggregate temporally to weekly

**Performance**:
- ⏱️ **Processing time**: ~10-15 minutes for 3 months (Summer 2020)
- ⏱️ **Full dataset** (1984-2025): ~8-12 hours estimated
- 💾 **Memory**: High (loads 24 hourly grids per day)

**When to use**:
- Never (kept for reference only)
- Use if you need to modify the threshold definitions

---

### Updated Notebook (RECOMMENDED) ✅

**File**: [01b_experimental_design_from_processed.ipynb](01b_experimental_design_from_processed.ipynb)

**Data Source**: `processed_*/` (pre-computed monthly files)

**Processing Steps**:
1. Open monthly file (already has daily statistics)
2. Extract relevant variables (already calculated)
3. Aggregate spatially to regions
4. Calculate TAS
5. Aggregate temporally to weekly

**Performance**:
- ⏱️ **Processing time**: ~30 seconds for 3 months (Summer 2020)
- ⏱️ **Full dataset** (1984-2025): ~3-5 minutes estimated
- 💾 **Memory**: Low (loads daily statistics, not hourly grids)

**Speed improvement**: **~20-30x faster** ⚡

**When to use**:
- **Always** for experimental design and analysis
- When working with pre-defined thresholds
- For production workflows

---

## Data Verification Notebook

**File**: [00_data_verification.ipynb](00_data_verification.ipynb)

**Data Source**: `daily_data/` (raw hourly files) ✓ CORRECT

**Purpose**:
- Verify raw MERRA-2 data quality
- Check temporal coverage (gaps, missing files)
- Validate hourly structure
- Ensure spatial dimensions match region masks

**Why it uses raw files**:
This notebook checks the **source data** before processing, so it correctly uses raw daily files. No change needed.

---

## Recommendations

### For New Analysis ✅

**Use**: [01b_experimental_design_from_processed.ipynb](01b_experimental_design_from_processed.ipynb)

**Why**:
1. ✅ 20-30x faster processing
2. ✅ All computation already done and validated
3. ✅ Lower memory footprint
4. ✅ Consistent with existing pipeline
5. ✅ Same output as original (verified)

**Steps**:
1. Run `00_data_verification.ipynb` once to verify raw data
2. Ensure `02_data_processing/` notebooks have created all monthly files
3. Use `01b_experimental_design_from_processed.ipynb` for analysis

---

### For Modifying Thresholds ⚠️

**Use**: [02_data_processing/](../02_data_processing/) notebooks → Then `01b_*`

**Why**:
If you need different temperature thresholds or time windows, modify the processing notebooks and regenerate monthly files.

**Steps**:
1. Edit thresholds in `process_daytime_heat_stats.ipynb` or `process_nighttime_recovery_stats.ipynb`
2. Delete old monthly files: `rm processed_daytime_heat/*.nc`
3. Rerun processing notebooks to regenerate with new thresholds
4. Use `01b_experimental_design_from_processed.ipynb` with new data

---

## Processing Status Check

To verify all processed data exists:

```bash
# Check file counts (should be 504 each for 1984-2025)
ls processed_daytime_heat/ | wc -l
ls processed_nighttime_recovery/ | wc -l
ls processed_vpd/ | wc -l

# Check date coverage
ls processed_daytime_heat/ | head -1  # Should be 198401
ls processed_daytime_heat/ | tail -1  # Should be 202512

# Check variable structure
ncdump -h processed_daytime_heat/daytime_heat_202006.nc
ncdump -h processed_nighttime_recovery/nighttime_recovery_202006.nc
ncdump -h processed_vpd/vpd_202006.nc
```

**Current Status** (as of March 31, 2026):
- ✅ Daytime heat: 504 files ✓
- ✅ Nighttime recovery: 504 files ✓
- ✅ VPD: 504 files ✓
- ✅ Coverage: 1984-01 to 2025-12 ✓

**All data ready for analysis!**

---

## Summary Table

| Feature | Raw Daily Files | Processed Monthly Files |
|---------|----------------|------------------------|
| **File count** | 15,341 | 504 × 3 datasets |
| **Temporal resolution** | Hourly (24/day) | Daily statistics |
| **Processing time** (3 months) | ~10-15 minutes | ~30 seconds |
| **Processing time** (full) | ~8-12 hours | ~3-5 minutes |
| **Memory usage** | High | Low |
| **Data size** | ~8.7 GB | ~6 GB (3 datasets) |
| **Use case** | Data verification, threshold changes | **Experimental design (recommended)** |
| **Notebook** | `01_experimental_design_setup.ipynb` | **`01b_experimental_design_from_processed.ipynb`** ✅ |

---

## Next Steps

1. ✅ Use `01b_experimental_design_from_processed.ipynb` for experimental design
2. ⏭️ Extend date range to full period (1984-2025) - just change cells 3-4
3. ⏭️ Merge with cattle slaughter data
4. ⏭️ Add control variables (week-of-year, year FE, region FE)
5. ⏭️ Export to R for DLNM analysis

**Estimated time to process full dataset**: ~5 minutes ⚡

---

**Last Updated**: March 31, 2026
