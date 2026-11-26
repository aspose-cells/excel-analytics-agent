# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.13.0] - 2026-11-24

### Added

- `xy` planning field: regression and polynomial regression can use a real
  numeric x column (for example `Year`) instead of the row index
- Correlation and PCA honor the plan's `columns` selection
- Failure accounting: tools that raise are reported as failed items, with
  `partial` status when only some tools succeed
- Tests for x/y regression, output-path safety, dataframe tool selection,
  metrics accounting and console-safe logging

### Changed

- `ExecutionPipeline.execute` no longer overwrites the input workbook when
  `output_path` is omitted; it writes `<stem>_analyzed.xlsx` instead and
  rejects an explicit output path equal to the input
- PCA drops rows with missing values and reports `rows_used`
- Schema summary flags numeric identifier columns (for example `CustomerID`)
  and tolerates duplicate column names
- Console logging replaces characters that the active code page cannot encode

### Fixed

- Regression R-squared values based on the row index no longer masquerade
  as a relationship with a time column
## [0.12.0] - 2026-11-19

### Added

- Schema-aware planning: the routing pipeline reads the input workbook,
  builds a compact schema summary (rows, columns, dtypes, missing counts,
  ranges, sample rows, identifier hints) and sends it to the planner
- Plans can now target specific columns via `"columns": {"tool": ["col"]}`;
  the execution pipeline only analyzes the requested numeric columns
- Identifier detection in the schema summary (e.g. `Customer`, `*_id`)
- Fallback to all numeric columns when a requested column is missing,
  non-numeric or when no column selection is provided
- Unit tests for schema summaries, planner messages, routing and column
  selection

### Changed

- Planner prompt documents the new `columns` field and the minimum data
  requirements for clustering and seasonality
- Planner receives the schema as untrusted data, with an explicit
  prompt-injection warning
## [0.11.0] - 2026-11-04

### Added

- Data quality profiling tool (`data_profile`): missing values,
  duplicate rows, empty rows/columns, mixed types, constant columns,
  whitespace issues, numeric-as-text, implausible ranges and IQR
  outliers, with a 0-100 quality score and level-based issue list
- Dedicated `Data Quality` worksheet written to the output workbook
- Narrative summary for data quality results
- Unit and pipeline tests for data profiling
- `main.py` scenario profiling the quality of sales data

## [0.10.0] - 2026-10-30

### Added

- Registered five existing analysis modules as LLM-selectable tools:
  `change_point`, `distribution`, `outlier`, `seasonality` and `smoothing`
- Tool descriptions in the planner prompt so the LLM can pick them correctly
- Narrative summary branches for all five new tools
- Unit and pipeline tests covering registration and Excel output
- New `main.py` scenario exercising change point, normality, outlier and
  smoothing analysis

### Fixed

- Change point detection no longer flags every point when the series has a
  constant step size (zero threshold)
- Normality test now returns a native Python bool for `is_normal`
- Pipeline skips columns that are too short for KDE (<10) and seasonality (<8)
  instead of failing the whole tool

## [0.9.0] - 2026-10-20

### Added

- KDE density estimation tool (`kde`) with mode (peak) detection for
  identifying multimodal distributions and hidden subgroups
- Histogram + KDE curve charts embedded into Excel via matplotlib,
  with detected modes marked
- Narrative summary branch for KDE results
- Unit, pipeline and Excel embedding tests for KDE
- Bimodal sample dataset (`samples/customer_segments.xlsx`)

## [0.8.0] - 2026-10-09

### Added

- Polynomial regression tool (`poly_regression`) for non-linear curve fitting (degree 2–4)
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

[0.13.0]: https://github.com/example/excel_agent/releases/tag/v0.13.0
[0.12.0]: https://github.com/example/excel_agent/releases/tag/v0.12.0
[0.11.0]: https://github.com/example/excel_agent/releases/tag/v0.11.0
[0.10.0]: https://github.com/example/excel_agent/releases/tag/v0.10.0
[0.9.0]: https://github.com/example/excel_agent/releases/tag/v0.9.0
[0.8.0]: https://github.com/example/excel_agent/releases/tag/v0.8.0
[0.7.0]: https://github.com/example/excel_agent/releases/tag/v0.7.0
[0.6.0]: https://github.com/example/excel_agent/releases/tag/v0.6.0
[0.5.0]: https://github.com/example/excel_agent/releases/tag/v0.5.0
[0.4.0]: https://github.com/example/excel_agent/releases/tag/v0.4.0
[0.3.0]: https://github.com/example/excel_agent/releases/tag/v0.3.0
[0.2.0]: https://github.com/example/excel_agent/releases/tag/v0.2.0
[0.1.0]: https://github.com/example/excel_agent/releases/tag/v0.1.0
