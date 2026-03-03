p02_rmt_hist_mp_overlay.png : Empirical eigenvalue histogram overlaid with Marchenko-Pastur bulk to separate structural modes from noise-like spectrum mass.
p02_rmt_scree_mp_bounds.png : Scree plot with MP bounds used to identify significant outlier eigenmodes versus random-matrix bulk.
p03_cum_factor_variance.png : Cumulative explained-variance curve showing how quickly volatility structure concentrates in top components.
p03_factor_timeseries.png : Legacy factor-score time series used to inspect whether extracted factors align with stress episodes.
p04_factor_market_corr.png : Correlation summary between retained factors and market-volatility proxy for systemic interpretation.
p05_rolling_angle.png : Legacy rolling principal-angle plot showing subspace rotation between adjacent windows.
p05_rolling_overlap.png : Legacy rolling overlap plot showing persistence of dominant factor directions across windows.
p06_filtered_corr_heatmap.png : Denoised correlation heatmap reconstructed from retained signal modes.
p06_raw_corr_heatmap.png : Raw correlation heatmap before filtering, used as baseline matrix view.
p07_idio_share_by_asset.png : Asset-level idiosyncratic variance share after low-rank decomposition.
p07_variance_observed_vs_recon.png : Observed-versus-reconstructed variance comparison for model fit sanity check.
p08_regime_timeline.png : Regime sequence timeline across sample history.
p08_regime_timeline_drawdowns.png : Regime timeline with drawdown overlay to show stress concentration by state.
p08_signal_change_points.png : Composite signal with detected change points marked.
p09_pc1_stability_by_split.png : Split-level stability summary for first principal component.
p10_scree_estimator_comparison.png : Scree comparison between RS and GK estimators to test dimensionality robustness.
p11_stock_shuffle_hist.png : Legacy stock-shuffle null histogram for falsification tests.
p11_time_shuffle_hist.png : Legacy time-shuffle null histogram for falsification tests.
p12_01_baseline_scree_mp_bounds.png : Baseline phase-12 scree with MP bounds from artifact pipeline output.
p12_02_baseline_histogram_mp_overlay.png : Baseline phase-12 eigenvalue histogram with MP overlay from artifact output.
p12_03_signal_count_by_variant.png : Number of detected signal modes by preprocessing/smoothing variant.
p12_04_mp_bounds_by_variant.png : Estimated MP edge values by variant to compare effective random bulk ranges.
p12_05_signal_concentration_by_variant.png : Signal concentration metrics by variant for robustness comparison.
p12_06_negative_eig_count_by_variant.png : Negative eigenvalue count by variant to track PSD/pathology behavior.
p12_auc_by_horizon.png : Legacy AUC-by-horizon curve for event discrimination.
p12_decile_lift_h5.png : Legacy decile-lift chart at 5-day horizon.
p13_01_factor_time_series.png : Phase-13 factor score time series from selected retained modes.
p13_02_factor_correlation_heatmap.png : Factor-to-factor correlation heatmap for dependence structure inspection.
p14_01_market_vol_corr_by_factor.png : Per-factor market-volatility correlation in interpretation stage.
p14_02_liquidity_corr_by_factor.png : Per-factor liquidity correlation in interpretation stage.
p14_03_factor_persistence_acf.png : Factor persistence/autocorrelation diagnostic plot.
p14_04_sector_hhi_by_factor.png : Sector concentration (HHI) by factor to assess loading localization.
p14_05_sector_weight_heatmap.png : Sector-weight heatmap of factor loadings.
p15_01_rolling_overlap_by_factor.png : Rolling overlap stability by retained factor.
p15_02_rolling_angle_by_factor.png : Rolling principal-angle stability by retained factor.
p15_03_overlap_distribution_boxplot.png : Distribution of overlap scores across windows.
p15_04_subsample_overlap_heatmap.png : Subsample overlap heatmap for stability robustness.
p15_05_stability_score_dashboard.png : Aggregated stability dashboard combining overlap/angle diagnostics.
p16_02_filtered_correlation_heatmap.png : Phase-16 filtered correlation matrix visualization.
p16_03_reconstruction_error_heatmap.png : Reconstruction error heatmap for low-rank filtering fidelity.
p16_04_offdiag_raw_vs_filtered_scatter.png : Off-diagonal raw-versus-filtered scatter for structure preservation check.
p16_06_reconstruction_diagnostics_bars.png : Bar diagnostics summarizing reconstruction quality metrics.
p17_01_variance_observed_vs_reconstructed.png : Phase-17 variance comparison under low-rank model.
p17_03_residual_correlation_heatmap.png : Residual correlation heatmap after factor reconstruction.
p18_01_factor_energy_timeseries.png : Factor-energy time series used for stress/regime feature engineering.
p19_01_signal_with_change_points.png : Phase-19 composite signal with optimized change-point locations.
p19_02_regime_sequence_timeline.png : Phase-19 regime timeline output from segmentation model.
p19_03_penalty_scan_bic.png : Penalty scan with BIC criterion for regime-count selection.
p19_04_regime_mean_signal.png : Mean composite signal level by detected regime.
p19_05_regime_durations.png : Duration distribution/summary across detected regimes.
p20_01_mean_market_vol_by_regime.png : Regime-conditional mean market volatility.
p20_02_dispersion_by_regime.png : Regime-conditional cross-sectional dispersion.
p20_03_factor_variance_share_by_regime.png : Regime-conditional factor variance share.
p20_04_drawdown_share_by_regime.png : Regime-conditional drawdown burden share.
p20_05_regime_timeline_with_drawdowns.png : Regime timeline annotated with drawdown periods.
p21_01_k_signal_modes_by_split.png : Effective signal-mode count by sample split.
p21_02_pc1_stability_by_split.png : PC1 stability comparison across split samples.
p21_04_top1_explained_by_split.png : Top-1 explained variance share by split.
p22_01_k_by_estimator.png : Effective K comparison between RS and GK estimators.
p22_02_top1_ratio_by_estimator.png : Top-1 variance ratio comparison between estimators.
p22_03_signal_mass_share_by_estimator.png : Signal-mass share comparison between estimators.
p22_04_regime_counts_by_estimator.png : Regime count comparison under estimator swap.
p22_05_scree_top20_comparison.png : Top-20 scree comparison under estimator swap.
p23_01_top1_time_shuffle_hist.png : Top-1 concentration under time-shuffle null experiments.
p23_02_top1_stock_shuffle_hist.png : Top-1 concentration under stock-shuffle null experiments.
p23_03_k_signal_boxplot.png : Boxplot of signal-mode count under falsification runs.
p23_04_top1_ratio_boxplot.png : Boxplot of top-1 ratio under falsification runs.
p23_06_mean_offdiag_distribution.png : Distribution of mean off-diagonal correlation under null tests.
p27_01_predictor_timeseries.png : Strict phase-27 predictor time series used for forecasting diagnostics.
p27_02_corr_by_horizon.png : Strict test correlation between predictions and targets by horizon.
p27_03_test_r2_by_horizon.png : Strict out-of-sample R² by horizon.
p27_04_auc_by_horizon.png : Strict event-classification AUC by horizon.
p27_05_scatter_h5.png : Strict predicted-versus-actual scatter at 5-day horizon.
p27_06_decile_lift_h5.png : Strict decile-lift chart at 5-day horizon.
