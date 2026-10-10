# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.8.0] - 2026-10-09

### Added

- Polynomial regression tool (`poly_regression`) for non-linear curve fitting (degree 2¨C4)
- Automatic degree clamping for numerical stability and small datasets
- Narrative summary branch for polynomial regression results
- Excel roundtrip and full-pipeline integration tests for polynomial regression

### Fixed

- Benchmark tests referenced non-existent class/method names
  (`AnomalyDetection.detect`, `RegressionAnalysis.analyze`, clustering DataFrame signature)

## [0.7.0] - 2026-05-26

### Added

- Maturity scoring framework for evaluating analysis quality
- AI evaluation module for automated result assessment
- Governance documentation (CHANGELOG, SECURITY, LICENSE)
- Best practices guide for secure and reliable usage

## [0.6.0] - 2026-01-10

### Added

- K-means clustering for data segmentation
- Principal Component Analysis (PCA) for dimensionality reduction
- Time series forecasting module (ARIMA, Prophet wrappers)
- Feature importance ranking for regression models

## [0.5.0] - 2025-06-01

### Added

- Dockerfile and docker-compose.yml for containerized deployment
- CI/CD pipeline configuration (GitHub Actions)
- Integration tests for all pipeline stages
- Automated linting and type-checking in CI

## [0.4.0] - 2025-01-15

### Added

- LLM-based planner agent for dynamic workflow construction
- Multi-tool orchestration with parallel execution support
- Tool dependency resolution and conflict detection
- Human-in-the-loop approval step for critical actions

## [0.3.0] - 2024-09-01

### Added

- Pipeline architecture for composable data processing
- Tool registry for dynamic tool discovery and loading
- Plugin system for third-party tool integration
- Pipeline caching and checkpointing

## [0.2.0] - 2024-06-01

### Added

- Trend analysis (moving averages, seasonality decomposition)
- Linear regression and polynomial regression
- Fast Fourier Transform (FFT) for frequency analysis
- Correlation matrix computation

## [0.1.0] - 2024-03-01

### Added

- Basic anomaly detection (Z-score, IQR, Isolation Forest)
- CSV and Excel file loading
- Statistical summary generation
- Command-line interface for basic operations

[0.8.0]: https://github.com/example/excel_agent/releases/tag/v0.8.0
[0.7.0]: https://github.com/example/excel_agent/releases/tag/v0.7.0
[0.6.0]: https://github.com/example/excel_agent/releases/tag/v0.6.0
[0.5.0]: https://github.com/example/excel_agent/releases/tag/v0.5.0
[0.4.0]: https://github.com/example/excel_agent/releases/tag/v0.4.0
[0.3.0]: https://github.com/example/excel_agent/releases/tag/v0.3.0
[0.2.0]: https://github.com/example/excel_agent/releases/tag/v0.2.0
[0.1.0]: https://github.com/example/excel_agent/releases/tag/v0.1.0
