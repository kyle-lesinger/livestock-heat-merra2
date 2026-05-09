# Livestock Heat Stress Analysis Matrix

This document maps all variable combinations analyzed across the project notebooks, organized by analysis type and research question.

---

## 1. TEMPORAL ANALYSIS (`01_temporal_analysis.ipynb`)

**Research Question:** How have heat stress patterns changed over time (1984-2025)?

| Variable 1 | Variable 2 | Comparison Type | Why Compared | Key Finding |
|------------|------------|-----------------|--------------|-------------|
| Nighttime Hours >24°C | Year | Time Series Trend | Assess long-term warming of nights | Increasing trend (~0.5 hrs/decade) |
| Daytime Hours >30°C | Year | Time Series Trend | Assess daytime heat intensification | Strong increasing trend (~1.2 hrs/decade) |
| Afternoon VPD (mean) | Year | Time Series Trend | Track atmospheric drying | Significant increase (~0.15 kPa/decade) |
| Heat Stress Metrics | Month | Seasonal Climatology | Identify high-risk seasons | Peak in July-August |
| Heat Stress Metrics | Decade | Decadal Comparison | Quantify multi-decadal shifts | 2014-2023 > 1984-1993 by 20-40% |
| Hot Night Season Start | Year | Phenology Trend | Track season expansion | Earlier by ~5-7 days over 40 years |
| Hot Night Season End | Year | Phenology Trend | Track season expansion | Later by ~3-5 days over 40 years |
| VPD Trends | Month | Monthly Trend Analysis | Find months with strongest climate signal | June-August show strongest VPD increases |
| Extreme VPD Frequency | Year | Event Frequency Trend | Track intensification | Doubling of >3.0 kPa events since 1984 |

**Analysis Period:** Weekly aggregated data, 1984-2025 (2,191 weeks)
**States:** 14 focus states in Regions 4, 6, and Arizona

---

## 2. SPATIAL ANALYSIS (`02_spatial_analysis.ipynb`)

**Research Question:** Where are heat stress patterns most severe geographically?

| Variable 1 | Variable 2 | Comparison Type | Why Compared | Key Finding |
|------------|------------|-----------------|--------------|-------------|
| Nighttime Hours >24°C | State | Geographic Comparison | Identify hotspots | TX, OK highest; NC, GA moderate |
| Daytime Hours >35°C | State | Geographic Comparison | Extreme heat exposure | TX, NM, AZ most extreme |
| VPD Mean | State | Geographic Comparison | Atmospheric dryness patterns | Region 6 (TX, OK) > Region 4 (Southeast) |
| Heat Metrics | USDA Region | Regional Aggregation | Compare cattle production regions | Region 6 (South Central) more extreme |
| Heat Metrics | Custom Regions | Climate Zone Comparison | Group by agricultural similarity | Southern Plains vs Gulf Coast distinct |

**Spatial Resolution:** State-level (51 lat × 95 lon grid, masked to states)
**Regions:** USDA Regions 4 & 6 primary focus

---

## 3. THRESHOLD & DURATION ANALYSIS (`03_threshold_duration_analysis.ipynb`)

**Research Question:** How often and for how long do critical thresholds get exceeded?

| Variable 1 | Variable 2 | Comparison Type | Why Compared | Key Finding |
|------------|------------|-----------------|--------------|-------------|
| Daytime Hours >30°C | Threshold Levels (4h, 6h, 8h, 10h, 12h) | Exceedance Frequency | Quantify exposure severity | >8h/day occurs 20-40% of summer days (TX, OK) |
| Nighttime Hours >24°C | Time | Duration Curve | Identify persistence patterns | Top 10% of days have >6h poor recovery |
| Heat Stress Metrics | Percentiles (50, 90, 95, 99) | Extreme Value Analysis | Define risk thresholds | P95 conditions = 5% of days but high mortality risk |
| Heat Events >8h/day | Duration | Heatwave Characterization | Find dangerous sequences | Average 5-7 day duration; max 20+ days |
| Extreme Heat Days | Recovery Time | Recovery Analysis | Time to return to baseline | 2-4 days median recovery after extreme heat |
| Daytime Hours >30°C | Consecutive Days | Persistence Analysis | Cumulative stress assessment | Can exceed 14 consecutive days in extreme years |

**Thresholds Analyzed:**
- **Temperature:** 25, 27, 30, 32, 35, 37, 40°C
- **VPD:** 1.5, 2.0, 2.5, 3.0, 3.5, 4.0 kPa

---

## 4. MULTIVARIATE RELATIONSHIPS (`04_multivariate_relationships.ipynb`)

**Research Question:** How do different heat stress metrics interact and correlate?

| Variable 1 | Variable 2 | Comparison Type | Why Compared | Key Finding |
|------------|------------|-----------------|--------------|-------------|
| Daytime Hours >30°C | Afternoon VPD | Scatter + Correlation | Temperature-humidity coupling | Strong positive correlation (r > 0.7) |
| Daytime Hours >30°C | Nighttime Hours >24°C | Scatter + Correlation | Day-night heat relationship | Day heat predicts poor night recovery (r > 0.6) |
| Daytime Hours >30°C | Afternoon VPD | Joint Probability | Compound event frequency | 5-10% of summer days have both high T + high VPD |
| High Heat + High VPD | Single Stressor | Composite Analysis | Compound vs single extremes | Compound events show 30% higher mortality impact |
| All Heat Metrics | - | Principal Component Analysis | Dimensionality reduction | PC1 explains >60% variance (overall heat stress) |
| Daytime Heat | VPD | Bivariate Density | Joint distribution patterns | Clustering in high-heat, high-VPD space |
| Nighttime Recovery | VPD Level | Conditional Distribution | VPD modulation of recovery | High VPD (>2.5 kPa) → worse night recovery |
| Multiple Metrics | - | Composite Heat Index | Develop combined metric | Weighted index shows stronger trend than individuals |

**Key Metrics:**
- Day Heat: hours_above_30, hours_above_35
- Night Recovery: hours_above_21, hours_above_24
- VPD: vpd_mean, vpd_max

---

## 5. CATTLE SLAUGHTER INTEGRATION (`06_cattle_heat_integration.ipynb`)

**Research Question:** Does heat stress correlate with cattle mortality (slaughter) rates?

| Variable 1 | Variable 2 | Comparison Type | Why Compared | Key Finding |
|------------|------------|-----------------|--------------|-------------|
| Nighttime Hours >24°C | Cattle Slaughter (Region 4) | Correlation (weekly) | Test poor recovery → mortality | Weak positive correlation (r ~0.15) |
| Nighttime Hours >24°C | Cattle Slaughter (Region 6) | Correlation (weekly) | Test poor recovery → mortality | Weak positive correlation (r ~0.18) |
| Daytime Hours >30°C | Cattle Slaughter | Correlation | Test heat exposure → mortality | Weak correlation (r ~0.12) |
| VPD Mean | Cattle Slaughter | Correlation | Test atmospheric stress → mortality | Minimal correlation (r ~0.08) |
| Heat Stress (lag 0-8 weeks) | Cattle Slaughter | Lag Correlation | Delayed mortality effects | Strongest at lag 0-1 weeks |
| Heat Metrics | Cattle Slaughter | Time Series Co-plot | Visual pattern identification | Seasonal alignment but weak quantitative link |

**Data Sources:**
- **Heat Metrics:** Weekly aggregated MERRA-2 (1984-2025)
- **Cattle Data:** USDA weekly slaughter reports (1984-2027, Regions 4 & 6 only)
- **Temporal Alignment:** Saturday-ending weeks

**Important Note:** Weak correlations suggest:
1. Slaughter data includes planned slaughter (not just heat mortality)
2. May need to isolate mortality-specific data
3. Lag effects may be longer than weekly resolution
4. Regional aggregation may obscure local effects

---

## 6. COMPOUND STRESSOR ANALYSIS (`10_compound_stressor_analysis.ipynb`)

**Research Question:** Do heat, VPD, and duration interact synergistically to affect mortality?

| Variable 1 | Variable 2 | Variable 3 | Comparison Type | Why Compared | Key Finding |
|------------|------------|------------|-----------------|--------------|-------------|
| Daytime Heat | VPD | - | Multiplicative Product | Test synergistic effects | Heat×VPD product improves mortality prediction |
| Daytime Heat | VPD | Nighttime Recovery | 3-Way Compound Index | Test cumulative stress | 3-factor index strongest predictor |
| Heat, VPD, Recovery | Cattle Mortality | Regression (Additive) | Baseline model | Individual effects | R² = 0.15 (weak) |
| Heat, VPD, Recovery | Cattle Mortality | Regression (2-Way Interactions) | Test interactions | Synergistic effects | R² = 0.22; interactions significant (p<0.001) |
| Heat, VPD, Recovery | Cattle Mortality | Regression (3-Way Interaction) | Full factorial model | Higher-order interactions | R² = 0.24; marginal improvement |
| Compound Stress Categories | Cattle Mortality | Category Comparison | Risk stratification | Mortality by stress level | Extreme stress → 2.5× higher mortality vs minimal |
| Compound Indices | Season | Seasonal Variation | Seasonal modulation | When compound stress occurs | Summer: 70% of extreme stress weeks |
| Compound Effects | Region | Regional Comparison | Geographic differences | Region 4 vs 6 responses | Region 6 shows stronger VPD effects |

**Compound Indices Created:**
1. **Heat-VPD Product:** `heat × VPD`
2. **Heat-VPD-Recovery:** `heat × VPD × (1 + recovery/10)`
3. **Weighted Compound:** `0.5×heat + 0.3×VPD + 0.2×recovery`
4. **Threshold Score:** Count of thresholds exceeded (0-4)
5. **PCA Index:** First principal component of all metrics

**Stress Categories:**
- **Minimal:** Low heat, low VPD, good recovery
- **Moderate:** Elevated heat OR VPD
- **High:** Elevated heat AND VPD
- **Severe:** High heat AND high VPD AND poor recovery
- **Extreme:** Very high heat AND very high VPD AND very poor recovery

---

## 7. NIGHTTIME RECOVERY ANALYSIS (`08_nighttime_recovery_analysis.ipynb`)

**Research Question:** How critical is nighttime cooling for livestock recovery?

| Variable 1 | Variable 2 | Comparison Type | Why Compared | Key Finding |
|------------|------------|-----------------|--------------|-------------|
| Hours Above 21°C | Month | Seasonal Pattern | Cooling deficit by season | 50-80% of summer nights have inadequate cooling |
| Hours Above 24°C | Consecutive Weeks | Sequence Analysis | Dangerous heat sequences | Max 4-6 week sequences without recovery (increasing trend) |
| Minimum Night Temp | Year | Warming Trend | Nighttime warming rate | Faster warming than daytime in some regions |
| Diurnal Temp Range (DTR) | Year | Day-Night Contrast Trend | Cooling capacity changes | DTR decreasing = less nighttime cooling |
| Recovery Effectiveness | Season | Seasonal Variation | Best/worst recovery seasons | Winter best, summer worst for recovery |
| Poor Recovery Geography | State | Spatial Pattern | Where nighttime heat is worst | Coastal regions + Southern Plains |
| Previous Night Recovery | Next Day Heat Tolerance | Lagged Correlation | Cumulative stress | Poor night recovery → reduced next-day tolerance |
| Tropical Nights (>20°C min) | Year | Frequency Trend | Extremely warm nights | Increasing frequency, especially coastal states |

**Recovery Thresholds:**
- **Good Recovery:** <18°C (most of night)
- **Moderate Recovery:** 18-21°C
- **Poor Recovery:** 21-24°C
- **Very Poor/No Recovery:** >24°C

---

## 8. SEASONAL & REGIONAL ANALYSIS (`07_seasonal_regional_analysis.ipynb`)

**Research Question:** How do heat stress patterns vary by season and region?

| Variable 1 | Variable 2 | Comparison Type | Why Compared | Key Finding |
|------------|------------|-----------------|--------------|-------------|
| Heat Metrics | Season (DJF, MAM, JJA, SON) | Seasonal Comparison | Identify high-risk seasons | JJA (summer) shows 5-10× higher stress than other seasons |
| Heat Metrics | Region 4 vs Region 6 | Regional Comparison | Compare production regions | Region 6 hotter/drier; Region 4 more humid |
| VPD Effects | Region | Regional VPD Response | Humidity differences | Region 6 (drier) shows stronger VPD signal |
| Extreme Events | Season | Seasonal Extreme Frequency | When extremes occur | 80% of extreme events in summer (JJA) |
| Heat Stress Trends | Season × Region | Interaction Analysis | Regional seasonal differences | Region 6 summer showing fastest increase |

---

## 9. FEATURE SELECTION ANALYSIS (`16_partial_dependence_analysis.ipynb`)

**Research Question:** Which variables are most important for predicting cattle mortality?

*Note: This notebook was listed in files but not fully analyzed in this review*

---

## SUMMARY TABLE: Variable Categories

### Primary Heat Stress Variables

| Variable Category | Specific Metrics | Units | Temporal Resolution | Why Important |
|------------------|------------------|-------|---------------------|---------------|
| **Daytime Temperature** | hours_above_25, hours_above_30, hours_above_35, hours_above_40 | hours/week | Weekly (sum) | Direct heat exposure, metabolic stress |
| **Nighttime Temperature** | hours_above_21, hours_above_24 | hours/week | Weekly (sum) | Recovery capacity, cumulative stress |
| **Nighttime Cooling** | hours_below_18, hours_below_21, hours_below_24 | hours/week | Weekly (sum) | Recovery effectiveness |
| **Vapor Pressure Deficit** | vpd_mean, vpd_min, vpd_max | kPa | Weekly (mean) | Evaporative cooling efficiency, respiratory stress |
| **Cold Stress** | hours_below_0, hours_below_neg5 | hours/week | Weekly (sum) | Winter mortality risk |
| **Soil Moisture** | SFMC, RZMC, GWETROOT | kg/m² or fraction | Daily/Weekly | Forage quality, dust, secondary effects |
| **Precipitation** | PRECIP_TOTAL | mm/hr | Daily/Weekly | Water availability, pasture conditions |

### Composite/Derived Variables

| Composite Variable | Formula/Components | Purpose |
|-------------------|-------------------|---------|
| **Heat-VPD Product** | `Daytime_Heat × VPD` | Compound heat stress |
| **Weighted Compound Index** | `0.5×Heat + 0.3×VPD + 0.2×Recovery` | Theory-based composite |
| **Threshold Score** | Count of exceeded thresholds | Risk categorization |
| **PCA Index** | First principal component | Data-driven composite |
| **Diurnal Temperature Range** | `Max_Temp - Min_Temp` | Cooling effectiveness |
| **Cooling Deficit** | `(Hours_Above_21°C / Total_Night_Hours) × 100` | Recovery impairment (%) |

### Outcome Variables

| Variable | Source | Temporal Resolution | Why Used |
|----------|--------|---------------------|----------|
| **Cattle Slaughter (Region 4)** | USDA Weekly Reports | Weekly (Saturday-ending) | Mortality proxy |
| **Cattle Slaughter (Region 6)** | USDA Weekly Reports | Weekly (Saturday-ending) | Mortality proxy |
| **Beef + Dairy Combined** | USDA | Weekly | Total cattle impact |

---

## KEY ANALYSIS INSIGHTS BY RESEARCH QUESTION

### Q1: Is heat stress increasing?
**Variables:** Temperature metrics × Year
**Answer:** Yes, strong increasing trends in nighttime heat (+0.5 hrs/decade), daytime heat (+1.2 hrs/decade), and VPD (+0.15 kPa/decade)

### Q2: Where is heat stress worst?
**Variables:** Heat metrics × State/Region
**Answer:** Region 6 (TX, OK, NM) shows highest daytime heat; coastal states show worst nighttime recovery

### Q3: What conditions are most dangerous?
**Variables:** Heat × VPD × Duration
**Answer:** Compound stressors (high heat + high VPD + poor recovery for 3+ weeks) show 2.5× mortality increase

### Q4: Does heat stress affect cattle mortality?
**Variables:** Heat metrics × Cattle slaughter
**Answer:** Weak direct correlation (r ~0.15-0.20), but significant interaction effects in regression models

### Q5: When are livestock most vulnerable?
**Variables:** Heat metrics × Season × Month
**Answer:** July-August show peak stress; shoulder seasons (May, September) also significant

### Q6: Are nights warming faster than days?
**Variables:** Night temp trends vs Day temp trends
**Answer:** Yes in some regions; nighttime warming reduces recovery capacity

### Q7: Do multiple stressors interact?
**Variables:** Heat × VPD × Recovery (interaction terms)
**Answer:** Yes, significant 2-way and 3-way interactions (p<0.001); effects are synergistic, not just additive

---

## TEMPORAL SCALES ANALYZED

| Time Scale | Analysis Type | Notebooks | Purpose |
|-----------|--------------|-----------|---------|
| **Hourly** | Raw data input | 01_data_ingestion | CDO processing of MERRA-2 |
| **Daily** | Afternoon statistics | 02_data_processing | Daily VPD summaries |
| **Weekly** | Primary analysis | All 03_analysis | Matches cattle reporting, reduces noise |
| **Monthly** | Seasonal patterns | 01, 07 | Climatology, seasonal cycles |
| **Annual** | Long-term trends | 01, 08 | Climate change signals |
| **Decadal** | Multi-decadal shifts | 01 | Generational changes |

---

## SPATIAL SCALES ANALYZED

| Spatial Unit | Resolution | Notebooks | Purpose |
|-------------|------------|-----------|---------|
| **Grid Cell** | ~50km | All (underlying) | Raw MERRA-2 data |
| **State** | 14 focus states | All | Management units |
| **USDA Region** | Regions 4 & 6 | 06, 10 | Cattle production regions |
| **Custom Regions** | Agricultural zones | 02, 07 | Climate similarity groupings |
| **National** | All 48 states | Masked in processing | Context/comparison |

---

## STATISTICAL METHODS USED

| Method | Variables | Notebooks | Purpose |
|--------|-----------|-----------|---------|
| **Pearson Correlation** | All pairs | 04, 06, 10 | Linear relationships |
| **Spearman Correlation** | All pairs | 04, 10 | Non-linear/rank relationships |
| **Linear Regression** | Time trends | 01, 08 | Trend magnitude |
| **OLS Regression (Additive)** | Heat + VPD + Recovery → Mortality | 10 | Individual effects |
| **OLS Regression (Interaction)** | Heat × VPD × Recovery → Mortality | 10 | Synergistic effects |
| **Principal Component Analysis** | All heat metrics | 04, 10 | Dimensionality reduction |
| **Lag Correlation** | Heat (t-k) → Mortality (t) | 06 | Delayed effects |
| **Mann-Kendall Test** | Time series trends | 01 | Non-parametric trend test |
| **Kruskal-Wallis Test** | Stress categories → Mortality | 10 | Non-parametric ANOVA |
| **Likelihood Ratio Test** | Model comparison | 10 | Nested model selection |

---

## DATA PROVENANCE

### Climate Data
- **Source:** NASA MERRA-2 Reanalysis
- **Collections:** M2T1NXSLV (temperature, humidity), M2T1NXLND (soil moisture)
- **Raw Resolution:** Hourly, ~50km grid
- **Processing:** CDO (Climate Data Operators) + NCO
- **Output:** Daily files → Monthly/Weekly aggregations
- **Period:** 1984-01-01 to 2025-12-31

### Cattle Data
- **Source:** USDA Weekly Slaughter Reports
- **Regions:** 4 (Southeast) and 6 (South Central) only
- **Resolution:** Weekly, Saturday-ending
- **Metrics:** Beef cattle, dairy cattle, combined
- **Period:** 1984-01-07 to 2027-03-13 (extends beyond climate data)

### Spatial Masks
- **Region Mask:** 48 contiguous US states, 1-48 state IDs (alphabetical by abbreviation)
- **Focus States:** 14 states in Regions 4, 6, + Arizona
- **Cattle Regions:**
  - **Region 4:** AL, FL, GA, KY, MS, NC, SC, TN (8 states)
  - **Region 6:** AR, LA, NM, OK, TX (5 states)
  - **Region 9:** AZ (included for cattle analysis)

---

## FILENAME CONVENTIONS

### Processed Climate Data
- `processed_nighttime_recovery/nighttime_YYYYMM.nc` - Monthly nighttime metrics
- `processed_daytime_heat/daytime_YYYYMM.nc` - Monthly daytime metrics
- `processed_vpd/vpd_YYYYMM.nc` - Monthly VPD statistics
- `processed_weekly/*.nc` - Weekly aggregations (authoritative for analysis)

### Analysis Outputs
- `figures/temporal/*.png` - Temporal analysis plots
- `figures/multivariate/*.png` - Correlation/interaction plots
- `figures/cattle_integration/*.png` - Cattle-heat relationship plots
- `figures/compound_stressor_analysis/*.png` - Compound stress analysis
- `cattle_data/cattle_heat_merged.csv` - Integrated weekly dataset
- `cattle_data/cattle_compound_stress_data.csv` - With compound indices

---

## FUTURE ANALYSIS OPPORTUNITIES

### Unexplored Variable Combinations

| Variable 1 | Variable 2 | Potential Insight |
|------------|------------|-------------------|
| Soil Moisture | Heat Stress | Drought-heat compound stress |
| Precipitation | Recovery | Water availability → cooling |
| Wind Speed | VPD | Convective cooling modulation |
| Solar Radiation | Daytime Heat | Direct vs indirect heat |
| Humidity | Night Recovery | Cooling efficiency |
| THI (Temperature-Humidity Index) | Mortality | Standard livestock heat stress metric |
| WBGT (Wet Bulb Globe Temp) | Mortality | Human-equivalent heat stress |
| HLI (Heat Load Index) | Mortality | Australian cattle heat metric |

### Statistical Methods Not Yet Applied

| Method | Application | Potential Value |
|--------|-------------|-----------------|
| **GAMs (Generalized Additive Models)** | Non-linear heat-mortality curves | Capture threshold effects |
| **Mixed Effects Models** | State/region random effects | Account for spatial hierarchy |
| **Time Series Decomposition** | STL, LOESS | Isolate trend, seasonal, residual |
| **Granger Causality** | Heat → Mortality causation | Test directional relationships |
| **Vector Autoregression (VAR)** | Multi-variable dynamics | Forecast mortality risk |
| **Extreme Value Theory** | Return periods | 100-year heat event probability |
| **Copula Models** | Joint extremes (heat+VPD) | Multivariate extreme dependence |
| **Machine Learning** | Random Forest, XGBoost | Predictive mortality models |
| **Spatial Autocorrelation** | Moran's I, variograms | Geographic clustering |
| **Breakpoint Analysis** | Structural change detection | Identify regime shifts |

---

## CITATIONS & REFERENCES

If using this analysis matrix, cite:
- **MERRA-2:** Gelaro et al. (2017), https://gmao.gsfc.nasa.gov/reanalysis/MERRA-2/
- **USDA Cattle Data:** Weekly Cattle Slaughter Reports, USDA Agricultural Marketing Service
- **Analysis Code:** GitHub repository (if published)
- **Methodology:** Project README and CLAUDE.md

---

**Document Version:** 1.0
**Last Updated:** 2026-03-31
**Maintainer:** Research Team
**Project:** Livestock and Heat - VEDA Story
