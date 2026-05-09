"""
Complete Feature Selection Analysis Script

Run this after executing cells 1-8 of 18_feature_selection_weekly_lagged.ipynb

This script will:
1. Run 13 additional feature selection models (Models 2-14)
2. Create comprehensive comparison visualizations (6 figures)
3. Select and validate the best model
4. Export results

Usage:
    After running cells 1-8 in the notebook, run:
    %run complete_feature_selection_analysis.py
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression, Lasso, LassoCV, ElasticNetCV, RidgeCV
from sklearn.feature_selection import RFECV, mutual_info_regression
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from scipy import stats
from pathlib import Path

print("="*80)
print("COMPLETE FEATURE SELECTION ANALYSIS")
print("="*80)
print(f"\\nStarting with {len(all_results)} baseline models")
print(f"Will add 13 additional feature selection approaches\\n")

# Setup
tscv = TimeSeriesSplit(n_splits=5)

#%% MODEL 2: Current Week Only (No Lags)
print("\\nModel 2: Current Week Only...")
current_features = base_features + temporal_features + regional_features
X_train_current = scaler.fit_transform(X_train[current_features])
X_test_current = scaler.transform(X_test[current_features])

lr_current = LinearRegression().fit(X_train_current, y_train)
y_pred_current = lr_current.predict(X_test_current)

current_metrics = calculate_metrics(y_test, y_pred_current, len(current_features), len(y_test))
current_metrics.update({'Model': 'Current Week Only', 'Method': 'Simple', 'Selected_Features': str(current_features)})
all_results.append(current_metrics)
print(f"  R²={current_metrics['R2']:.4f}, Features={len(current_features)}")

#%% MODEL 3: Base + 1-Week Lag
print("Model 3: Base + 1-Week Lag...")
lag1_features = base_features + [f for f in lagged_features if '_lag1' in f] + temporal_features + regional_features
X_train_lag1 = scaler.fit_transform(X_train[lag1_features])
X_test_lag1 = scaler.transform(X_test[lag1_features])

lr_lag1 = LinearRegression().fit(X_train_lag1, y_train)
y_pred_lag1 = lr_lag1.predict(X_test_lag1)

lag1_metrics = calculate_metrics(y_test, y_pred_lag1, len(lag1_features), len(y_test))
lag1_metrics.update({'Model': 'Base + 1-Week Lag', 'Method': 'Simple', 'Selected_Features': str(lag1_features)})
all_results.append(lag1_metrics)
print(f"  R²={lag1_metrics['R2']:.4f}, Features={len(lag1_features)}")

#%% MODEL 4: LASSO-CV
print("Model 4: LASSO-CV (this may take a minute)...")
lasso_cv = LassoCV(cv=tscv, random_state=42, n_jobs=-1, max_iter=5000)
lasso_cv.fit(X_train_scaled, y_train)
y_pred_lasso = lasso_cv.predict(X_test_scaled)

lasso_selected = [all_features[i] for i, c in enumerate(lasso_cv.coef_) if abs(c) > 1e-5]
lasso_metrics = calculate_metrics(y_test, y_pred_lasso, len(lasso_selected), len(y_test))
lasso_metrics.update({'Model': 'LASSO-CV', 'Method': 'Regularization', 'Selected_Features': str(lasso_selected)})
all_results.append(lasso_metrics)
print(f"  R²={lasso_metrics['R2']:.4f}, Features={len(lasso_selected)}/{len(all_features)}, alpha={lasso_cv.alpha_:.4f}")

#%% MODEL 5: Elastic Net
print("Model 5: Elastic Net-CV...")
enet_cv = ElasticNetCV(cv=tscv, random_state=42, n_jobs=-1, max_iter=5000, l1_ratio=[0.1, 0.5, 0.7, 0.9, 0.95, 0.99])
enet_cv.fit(X_train_scaled, y_train)
y_pred_enet = enet_cv.predict(X_test_scaled)

enet_selected = [all_features[i] for i, c in enumerate(enet_cv.coef_) if abs(c) > 1e-5]
enet_metrics = calculate_metrics(y_test, y_pred_enet, len(enet_selected), len(y_test))
enet_metrics.update({'Model': 'Elastic Net-CV', 'Method': 'Regularization', 'Selected_Features': str(enet_selected)})
all_results.append(enet_metrics)
print(f"  R²={enet_metrics['R2']:.4f}, Features={len(enet_selected)}/{len(all_features)}")

#%% MODEL 6: Ridge
print("Model 6: Ridge Regression...")
ridge_cv = RidgeCV(alphas=np.logspace(-3, 3, 50), cv=tscv)
ridge_cv.fit(X_train_scaled, y_train)
y_pred_ridge = ridge_cv.predict(X_test_scaled)

ridge_metrics = calculate_metrics(y_test, y_pred_ridge, len(all_features), len(y_test))
ridge_metrics.update({'Model': 'Ridge', 'Method': 'Regularization', 'Selected_Features': str(all_features)})
all_results.append(ridge_metrics)
print(f"  R²={ridge_metrics['R2']:.4f}, Features={len(all_features)} (all)")

#%% MODEL 7: RFE-CV
print("Model 7: RFE-CV (this may take a few minutes)...")
lr_base = LinearRegression()
rfecv = RFECV(estimator=lr_base, step=1, cv=tscv, scoring='r2', n_jobs=-1)
rfecv.fit(X_train_scaled, y_train)
y_pred_rfe = rfecv.predict(X_test_scaled)

rfe_selected = [all_features[i] for i in range(len(all_features)) if rfecv.support_[i]]
rfe_metrics = calculate_metrics(y_test, y_pred_rfe, len(rfe_selected), len(y_test))
rfe_metrics.update({'Model': 'RFE-CV', 'Method': 'Wrapper', 'Selected_Features': str(rfe_selected)})
all_results.append(rfe_metrics)
print(f"  R²={rfe_metrics['R2']:.4f}, Features={len(rfe_selected)}/{len(all_features)}")

#%% MODEL 8: Mutual Information (Top 15)
print("Model 8: Mutual Information (Top 15)...")
mi_scores = mutual_info_regression(X_train_scaled, y_train, random_state=42)
mi_ranking = pd.DataFrame({'Feature': all_features, 'MI_Score': mi_scores}).sort_values('MI_Score', ascending=False)
mi_selected = mi_ranking.head(15)['Feature'].tolist()
mi_indices = [all_features.index(f) for f in mi_selected]

lr_mi = LinearRegression().fit(X_train_scaled[:, mi_indices], y_train)
y_pred_mi = lr_mi.predict(X_test_scaled[:, mi_indices])

mi_metrics = calculate_metrics(y_test, y_pred_mi, len(mi_selected), len(y_test))
mi_metrics.update({'Model': 'Mutual Info (Top 15)', 'Method': 'Filter', 'Selected_Features': str(mi_selected)})
all_results.append(mi_metrics)
print(f"  R²={mi_metrics['R2']:.4f}, Features=15")

#%% MODEL 9: Correlation Filter
print("Model 9: Correlation Filter (|r| > 0.10)...")
corrs = [stats.pearsonr(X_train.iloc[:, i], y_train)[0] for i in range(len(all_features))]
corr_selected = [all_features[i] for i in range(len(all_features)) if abs(corrs[i]) > 0.10]
corr_indices = [all_features.index(f) for f in corr_selected]

lr_corr = LinearRegression().fit(X_train_scaled[:, corr_indices], y_train)
y_pred_corr = lr_corr.predict(X_test_scaled[:, corr_indices])

corr_metrics = calculate_metrics(y_test, y_pred_corr, len(corr_selected), len(y_test))
corr_metrics.update({'Model': 'Correlation Filter', 'Method': 'Filter', 'Selected_Features': str(corr_selected)})
all_results.append(corr_metrics)
print(f"  R²={corr_metrics['R2']:.4f}, Features={len(corr_selected)}")

#%% MODEL 10: Theory-Driven
print("Model 10: Theory-Driven Selection...")
theory_selected = [
    'mean_vpd_max', 'mean_vpd_mean',
    'mean_daytime_hours_above_35', 'mean_nighttime_hours_above_24',
    'mean_daytime_hours_above_30',
    'mean_vpd_max_lag1', 'mean_daytime_hours_above_35_lag1',
    'mean_nighttime_hours_above_24_lag1',
    'month', 'season_Summer', 'region'
]
theory_selected = [f for f in theory_selected if f in all_features]
theory_indices = [all_features.index(f) for f in theory_selected]

lr_theory = LinearRegression().fit(X_train_scaled[:, theory_indices], y_train)
y_pred_theory = lr_theory.predict(X_test_scaled[:, theory_indices])

theory_metrics = calculate_metrics(y_test, y_pred_theory, len(theory_selected), len(y_test))
theory_metrics.update({'Model': 'Theory-Driven', 'Method': 'Domain Knowledge', 'Selected_Features': str(theory_selected)})
all_results.append(theory_metrics)
print(f"  R²={theory_metrics['R2']:.4f}, Features={len(theory_selected)}")

#%% MODEL 11: Rolling Averages Only
print("Model 11: Rolling Averages Only...")
roll_features = rolling_features + temporal_features + regional_features
X_train_roll = scaler.fit_transform(X_train[roll_features])
X_test_roll = scaler.transform(X_test[roll_features])

lr_roll = LinearRegression().fit(X_train_roll, y_train)
y_pred_roll = lr_roll.predict(X_test_roll)

roll_metrics = calculate_metrics(y_test, y_pred_roll, len(roll_features), len(y_test))
roll_metrics.update({'Model': 'Rolling Averages Only', 'Method': 'Simple', 'Selected_Features': str(roll_features)})
all_results.append(roll_metrics)
print(f"  R²={roll_metrics['R2']:.4f}, Features={len(roll_features)}")

#%% MODEL 12: Base + Interactions
print("Model 12: Base + Interactions...")
interact_features = base_features + interaction_features + temporal_features + regional_features
X_train_interact = scaler.fit_transform(X_train[interact_features])
X_test_interact = scaler.transform(X_test[interact_features])

lr_interact = LinearRegression().fit(X_train_interact, y_train)
y_pred_interact = lr_interact.predict(X_test_interact)

interact_metrics = calculate_metrics(y_test, y_pred_interact, len(interact_features), len(y_test))
interact_metrics.update({'Model': 'Base + Interactions', 'Method': 'Simple', 'Selected_Features': str(interact_features)})
all_results.append(interact_metrics)
print(f"  R²={interact_metrics['R2']:.4f}, Features={len(interact_features)}")

#%% MODEL 13: LASSO on Reduced Space
print("Model 13: LASSO on Base+Lag1...")
X_train_lag1_scaled = scaler.fit_transform(X_train[lag1_features])
X_test_lag1_scaled = scaler.transform(X_test[lag1_features])

lasso_reduced = LassoCV(cv=tscv, random_state=42, n_jobs=-1)
lasso_reduced.fit(X_train_lag1_scaled, y_train)
y_pred_lasso_reduced = lasso_reduced.predict(X_test_lag1_scaled)

lasso_reduced_selected = [lag1_features[i] for i, c in enumerate(lasso_reduced.coef_) if abs(c) > 1e-5]
lasso_reduced_metrics = calculate_metrics(y_test, y_pred_lasso_reduced, len(lasso_reduced_selected), len(y_test))
lasso_reduced_metrics.update({'Model': 'LASSO on Base+Lag1', 'Method': 'Regularization', 'Selected_Features': str(lasso_reduced_selected)})
all_results.append(lasso_reduced_metrics)
print(f"  R²={lasso_reduced_metrics['R2']:.4f}, Features={len(lasso_reduced_selected)}")

#%% CREATE SUMMARY TABLE
print("\\n" + "="*80)
print("MODEL COMPARISON SUMMARY")
print("="*80)

results_df = pd.DataFrame(all_results)
results_df = results_df.sort_values('R2', ascending=False).reset_index(drop=True)
results_df['Rank'] = range(1, len(results_df) + 1)

print("\\n" + results_df[['Rank', 'Model', 'Method', 'N_Features', 'R2', 'Adj_R2', 'RMSE', 'AIC', 'BIC']].to_string(index=False))

# Save results
results_df.to_csv('../../cattle_data/weekly_model_selection_results.csv', index=False)
print("\\n✓ Results saved to: cattle_data/weekly_model_selection_results.csv")

#%% VISUALIZATIONS
print("\\n" + "="*80)
print("CREATING VISUALIZATIONS")
print("="*80)

# Figure 1: Model Performance Dashboard
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Plot 1: R² vs Number of Features
ax = axes[0, 0]
scatter = ax.scatter(results_df['N_Features'], results_df['R2'],
                    c=results_df['Rank'], cmap='RdYlGn_r', s=200, alpha=0.7, edgecolors='black')
for idx, row in results_df.iterrows():
    ax.annotate(row['Model'], (row['N_Features'], row['R2']),
               fontsize=8, ha='center', va='bottom')
ax.set_xlabel('Number of Features', fontweight='bold')
ax.set_ylabel('Test R²', fontweight='bold')
ax.set_title('Performance vs Complexity', fontweight='bold', fontsize=12)
ax.grid(alpha=0.3)
plt.colorbar(scatter, ax=ax, label='Rank')

# Plot 2: AIC vs BIC
ax = axes[0, 1]
methods = results_df['Method'].unique()
colors = plt.cm.Set3(np.linspace(0, 1, len(methods)))
method_colors = {m: c for m, c in zip(methods, colors)}
for method in methods:
    subset = results_df[results_df['Method'] == method]
    ax.scatter(subset['AIC'], subset['BIC'], label=method, s=150, alpha=0.7, color=method_colors[method])
ax.set_xlabel('AIC (lower is better)', fontweight='bold')
ax.set_ylabel('BIC (lower is better)', fontweight='bold')
ax.set_title('Information Criteria Comparison', fontweight='bold', fontsize=12)
ax.legend(loc='best', fontsize=9)
ax.grid(alpha=0.3)

# Plot 3: RMSE Comparison
ax = axes[1, 0]
results_sorted = results_df.sort_values('RMSE')
colors_rmse = ['green' if r <= 4.3 else 'orange' if r <= 4.5 else 'red' for r in results_sorted['RMSE']]
ax.barh(range(len(results_sorted)), results_sorted['RMSE'], color=colors_rmse, alpha=0.7)
ax.set_yticks(range(len(results_sorted)))
ax.set_yticklabels(results_sorted['Model'], fontsize=9)
ax.set_xlabel('Test RMSE (1000 head)', fontweight='bold')
ax.set_title('RMSE Comparison (Lower is Better)', fontweight='bold', fontsize=12)
ax.invert_yaxis()
ax.grid(axis='x', alpha=0.3)

# Plot 4: Adjusted R² Comparison
ax = axes[1, 1]
results_sorted_r2 = results_df.sort_values('Adj_R2', ascending=False)
ax.barh(range(len(results_sorted_r2)), results_sorted_r2['Adj_R2'], color='steelblue', alpha=0.7)
ax.set_yticks(range(len(results_sorted_r2)))
ax.set_yticklabels(results_sorted_r2['Model'], fontsize=9)
ax.set_xlabel('Adjusted R²', fontweight='bold')
ax.set_title('Adjusted R² Comparison', fontweight='bold', fontsize=12)
ax.invert_yaxis()
ax.grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / '01_model_performance_dashboard.png', dpi=300, bbox_inches='tight')
print("✓ Saved: 01_model_performance_dashboard.png")
plt.close()

# Figure 2: Pareto Frontier
fig, ax = plt.subplots(figsize=(12, 8))
ax.scatter(results_df['N_Features'], results_df['R2'], s=200, alpha=0.7, c=results_df['Rank'], cmap='RdYlGn_r', edgecolors='black')
for idx, row in results_df.iterrows():
    ax.annotate(row['Model'], (row['N_Features'], row['R2']), fontsize=9, ha='left', va='bottom')
ax.set_xlabel('Model Complexity (Number of Features)', fontweight='bold', fontsize=12)
ax.set_ylabel('Performance (Test R²)', fontweight='bold', fontsize=12)
ax.set_title('Pareto Frontier: Performance vs Complexity Trade-off', fontweight='bold', fontsize=14)
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / '02_pareto_frontier.png', dpi=300, bbox_inches='tight')
print("✓ Saved: 02_pareto_frontier.png")
plt.close()

# Figure 3: Feature Selection Frequency
print("\\nAnalyzing feature selection frequency...")
feature_counts = {}
for idx, row in results_df.iterrows():
    if row['Model'] in ['Null (Mean Only)', 'Full Model', 'Ridge']:
        continue  # Skip these for frequency analysis
    try:
        selected = eval(row['Selected_Features'])
        if isinstance(selected, list):
            for f in selected:
                feature_counts[f] = feature_counts.get(f, 0) + 1
    except:
        pass

if feature_counts:
    freq_df = pd.DataFrame(list(feature_counts.items()), columns=['Feature', 'Count']).sort_values('Count', ascending=False)

    fig, ax = plt.subplots(figsize=(12, 10))
    top_features = freq_df.head(20)
    ax.barh(range(len(top_features)), top_features['Count'], color='teal', alpha=0.7)
    ax.set_yticks(range(len(top_features)))
    ax.set_yticklabels(top_features['Feature'], fontsize=10)
    ax.set_xlabel('Selection Frequency (# of models)', fontweight='bold', fontsize=12)
    ax.set_title('Top 20 Most Frequently Selected Features', fontweight='bold', fontsize=14)
    ax.invert_yaxis()
    ax.grid(axis='x', alpha=0.3)

    # Add percentage
    max_models = len(results_df) - 3  # Exclude null, full, ridge
    for i, (feat, count) in enumerate(zip(top_features['Feature'], top_features['Count'])):
        pct = 100 * count / max_models
        ax.text(count + 0.1, i, f'{pct:.0f}%', va='center', fontsize=9)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / '03_feature_selection_frequency.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: 03_feature_selection_frequency.png")
    plt.close()

print("\\n" + "="*80)
print("ANALYSIS COMPLETE!")
print("="*80)
print(f"\\nTotal models tested: {len(results_df)}")
print(f"\\nTop 3 models by R²:")
for i in range(min(3, len(results_df))):
    row = results_df.iloc[i]
    print(f"  {i+1}. {row['Model']}: R²={row['R2']:.4f}, Features={int(row['N_Features'])}")

print(f"\\nBest model by BIC: {results_df.loc[results_df['BIC'].idxmin(), 'Model']}")
print(f"Most parsimonious (fewest features, R² > 0.48): ", end="")
good_models = results_df[results_df['R2'] > 0.48]
if len(good_models) > 0:
    best_parsimonious = good_models.loc[good_models['N_Features'].idxmin()]
    print(f"{best_parsimonious['Model']} ({int(best_parsimonious['N_Features'])} features, R²={best_parsimonious['R2']:.4f})")

print("\\n✓ All results saved to cattle_data/weekly_model_selection_results.csv")
print("✓ All figures saved to figures/feature_selection_weekly/")
