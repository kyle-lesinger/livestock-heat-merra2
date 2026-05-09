# Feature Selection Analysis - Usage Guide

## Quick Start

### Option 1: Run Complete Analysis (Recommended)

1. Open `18_feature_selection_weekly_lagged.ipynb`
2. Run cells 1-8 (imports through baseline models)
3. Add a new cell and run:
```python
%run complete_feature_selection_analysis.py
```

This will:
- Run 13 additional feature selection models (Models 2-14)
- Create 3+ comprehensive visualization figures
- Generate complete comparison table
- Export all results to CSV
- Identify the best model

**Total runtime**: ~5-10 minutes

### Option 2: Use Pre-Built Complete Notebook

Open `18_feature_selection_weekly_lagged_COMPLETE.ipynb` which has all 13 models pre-coded in separate cells.

---

## What You Get

### Models Tested (15 total):
1. **Null Model** (baseline - mean only)
2. **Full Model** (all 51 features)
3. **Current Week Only** (no lags/rolling)
4. **Base + 1-Week Lag**
5. **LASSO-CV** (automatic feature selection)
6. **Elastic Net-CV** (L1+L2 regularization)
7. **Ridge Regression** (L2 only)
8. **RFE-CV** (recursive feature elimination)
9. **Mutual Information** (top 15 features)
10. **Correlation Filter** (|r| > 0.10)
11. **Theory-Driven** (domain knowledge selection)
12. **Rolling Averages Only**
13. **Base + Interactions**
14. **LASSO on Reduced Space** (base+lag1 only)

### Outputs:

**CSV File**: `cattle_data/weekly_model_selection_results.csv`
- All models ranked by R², AIC, BIC
- Feature lists for each model
- Complete performance metrics

**Figures**: `figures/feature_selection_weekly/`
- `01_model_performance_dashboard.png` - 4-panel comparison
- `02_pareto_frontier.png` - performance vs complexity
- `03_feature_selection_frequency.png` - which features selected most often

### Key Findings You'll Get:

1. **Best Overall Model** - highest R²
2. **Most Parsimonious Model** - fewest features for good performance
3. **Best by BIC** - statistical model selection criterion
4. **Feature Importance Rankings** - which predictors matter most
5. **Method Comparison** - which selection approach works best

---

## Example Results

After running, you'll see output like:

```
MODEL COMPARISON SUMMARY
================================================================================

Rank  Model                     Method           N_Features    R2  Adj_R2  RMSE    AIC    BIC
   1  LASSO-CV                  Regularization           14  0.495   0.489  4.29  3145  3210
   2  Elastic Net-CV            Regularization           15  0.494   0.488  4.29  3146  3214
   3  Theory-Driven             Domain Knowledge         11  0.492   0.487  4.30  3148  3202
   ...

Top 3 models by R²:
  1. LASSO-CV: R²=0.4950, Features=14
  2. Elastic Net-CV: R²=0.4940, Features=15
  3. Theory-Driven: R²=0.4920, Features=11

Best model by BIC: Theory-Driven
Most parsimonious: Theory-Driven (11 features, R²=0.492)
```

---

## Understanding the Results

### Key Metrics:

- **R²**: Proportion of variance explained (higher = better prediction)
- **Adjusted R²**: R² penalized for number of features (accounts for complexity)
- **RMSE**: Average prediction error in 1000s of cattle (lower = better)
- **AIC/BIC**: Information criteria balancing fit and complexity (lower = better)
  - BIC penalizes complexity more heavily than AIC
  - Use BIC when you want simpler, more interpretable models

### How to Choose the Best Model:

1. **For Prediction Accuracy**: Choose highest R²
2. **For Simplicity + Accuracy**: Choose lowest BIC
3. **For Interpretation**: Choose Theory-Driven or fewest features with R² > 0.48
4. **For Robustness**: Choose model selected most often across methods

---

## Next Steps After Running

1. **Examine the best model's features**:
```python
best_model = results_df.iloc[0]
print(best_model['Selected_Features'])
```

2. **Check which features appear most often**:
```python
# Run frequency analysis from script output
```

3. **Validate on held-out data**:
```python
# The test set (2016-2025) is already held out
# Results shown are out-of-sample performance
```

4. **Use for predictions**:
```python
# Train final model on all data with selected features
# Export for operational use
```

---

## Troubleshooting

**"NameError: name 'all_results' is not defined"**
→ Run cells 1-8 of the main notebook first

**"ImportError: No module named 'sklearn'"**
→ Install: `pip install scikit-learn`

**Script runs forever**
→ RFE-CV can be slow with many features. You can comment it out or reduce cv folds

**Different results each run**
→ Random seed is set (42), but minor variations can occur due to CV splits

---

## Customization

To modify the analysis:

1. **Change number of MI features**: Edit `n_mi_features = 15` in Model 8
2. **Adjust correlation threshold**: Edit `> 0.10` in Model 9
3. **Modify theory-driven features**: Edit `theory_selected` list in Model 10
4. **Add more models**: Follow the pattern in the script

---

## Files Included

- `18_feature_selection_weekly_lagged.ipynb` - Main notebook (cells 1-8)
- `complete_feature_selection_analysis.py` - Analysis script (run from notebook)
- `18_feature_selection_weekly_lagged_COMPLETE.ipynb` - Pre-built full version
- `README_FEATURE_SELECTION.md` - This file

---

## Citation

If using these methods in publications:

- **LASSO/Elastic Net**: Zou & Hastie (2005) "Regularization and variable selection via the elastic net"
- **RFE**: Guyon et al. (2002) "Gene selection for cancer classification using support vector machines"
- **Mutual Information**: Kraskov et al. (2004) "Estimating mutual information"
- **AIC/BIC**: Burnham & Anderson (2004) "Model Selection and Multimodel Inference"

---

Last updated: 2025-03-27
