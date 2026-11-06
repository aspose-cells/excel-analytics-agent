from datetime import date, datetime
from numbers import Integral, Real

import pandas as pd

from app.logger import logger
from app.exceptions import AnalysisError


class DataQualityAnalysis:
    """Profile table-level and column-level data quality.

    The profiler is read-only: it never modifies the data, it only
    reports problems (missing values, duplicates, mixed types, constant
    columns, implausible ranges, outliers) together with a quality score.
    """

    ERROR_PENALTY = 15
    WARNING_PENALTY = 5

    @staticmethod
    def profile(df: pd.DataFrame) -> dict:
        """Build a data quality profile for a DataFrame.

        Args:
            df: The table to inspect (numeric and text columns).

        Returns:
            Dict with keys: table (row/column counts and duplicate/empty
            counts), columns (per-column profile), issues (list of
            level/column/message dicts) and quality_score (0-100).

        Raises:
            AnalysisError: If the input is not a DataFrame or profiling
                fails.
        """
        try:
            if not isinstance(df, pd.DataFrame):
                raise AnalysisError(
                    "Data quality profile expects a pandas DataFrame"
                )

            issues: list[dict] = []

            rows = int(len(df))
            column_count = int(len(df.columns))

            try:
                duplicate_rows = int(df.duplicated().sum())
            except Exception:
                duplicate_rows = 0

            if rows:
                empty_rows = int(df.isna().all(axis=1).sum())
            else:
                empty_rows = 0
            empty_columns = int(df.isna().all(axis=0).sum())

            table = {
                "rows": rows,
                "columns": column_count,
                "duplicate_rows": duplicate_rows,
                "duplicate_pct": (
                    round(duplicate_rows / rows * 100, 2) if rows else 0.0
                ),
                "empty_rows": empty_rows,
                "empty_columns": empty_columns,
            }

            if duplicate_rows:
                level = "ERROR" if table["duplicate_pct"] >= 25 else "WARNING"
                issues.append({
                    "level": level,
                    "column": None,
                    "message": (
                        f"table contains {duplicate_rows} duplicate row(s) "
                        f"({table['duplicate_pct']:.1f}%)"
                    ),
                })

            if empty_rows:
                issues.append({
                    "level": "WARNING",
                    "column": None,
                    "message": f"table contains {empty_rows} empty row(s)",
                })

            if empty_columns:
                issues.append({
                    "level": "WARNING",
                    "column": None,
                    "message": (
                        f"table contains {empty_columns} empty column(s)"
                    ),
                })

            columns: dict = {}
            for index, raw_name in enumerate(df.columns):
                name = str(raw_name)
                key = name
                if key in columns:
                    key = f"{name}_{index}"

                series = df.iloc[:, index]
                columns[key] = DataQualityAnalysis._profile_column(
                    key, series, issues
                )

            penalty = 0
            for issue in issues:
                if issue["level"] == "ERROR":
                    penalty += DataQualityAnalysis.ERROR_PENALTY
                elif issue["level"] == "WARNING":
                    penalty += DataQualityAnalysis.WARNING_PENALTY

            return {
                "table": table,
                "columns": columns,
                "issues": issues,
                "quality_score": max(0, 100 - penalty),
            }
        except AnalysisError:
            raise
        except Exception as e:
            logger.error("Data quality profiling failed: %s", e)
            raise AnalysisError(f"Data quality profiling failed: {e}") from e

    @staticmethod
    def _profile_column(name: str, series, issues: list) -> dict:
        """Profile a single column and append its issues to ``issues``.

        Args:
            name: Column name used in the profile and issue messages.
            series: The pandas Series to inspect.
            issues: List that collected issues are appended to.

        Returns:
            Dict describing the column.
        """
        total = int(len(series))
        non_null = series.dropna()
        n_non_null = int(len(non_null))

        missing = int(series.isna().sum())
        missing_pct = round(missing / total * 100, 2) if total else 0.0

        try:
            unique = int(non_null.nunique())
        except Exception:
            unique = n_non_null

        types = sorted({
            DataQualityAnalysis._type_name(v) for v in non_null
        })
        numeric_types = {"int", "float"}
        mixed_types = len(types) > 2 or (
            any(t in numeric_types for t in types)
            and any(t not in numeric_types | {"bool"} for t in types)
        )

        info = {
            "dtype": str(series.dtype),
            "missing": missing,
            "missing_pct": missing_pct,
            "unique": unique,
            "constant": unique <= 1,
            "mixed_types": mixed_types,
            "types": types[:5],
        }

        if missing_pct >= 50:
            level = "ERROR"
        elif missing_pct >= 20:
            level = "WARNING"
        else:
            level = None

        if level:
            issues.append({
                "level": level,
                "column": name,
                "message": (
                    f"{name}: {missing} missing value(s) "
                    f"({missing_pct:.1f}%)"
                ),
            })

        if unique <= 1 and total:
            issues.append({
                "level": "WARNING",
                "column": name,
                "message": (
                    f"{name}: constant column (single distinct value) - "
                    f"carries no information"
                ),
            })

        if mixed_types:
            issues.append({
                "level": "WARNING",
                "column": name,
                "message": (
                    f"{name}: mixed types ({', '.join(types)})"
                ),
            })

        is_datetime = pd.api.types.is_datetime64_any_dtype(series)
        if not is_datetime and n_non_null:
            is_datetime = all(
                isinstance(v, (datetime, date)) for v in non_null
            )

        if is_datetime:
            info["min"] = str(non_null.min())
            info["max"] = str(non_null.max())
            return info

        if not n_non_null or all(isinstance(v, bool) for v in non_null):
            return info

        coerced = pd.to_numeric(non_null, errors="coerce")
        numeric_ratio = float(coerced.notna().sum()) / n_non_null

        if numeric_ratio >= 0.9 and all(isinstance(v, str) for v in non_null):
            issues.append({
                "level": "INFO",
                "column": name,
                "message": f"{name}: numeric values stored as text",
            })

        if numeric_ratio < 0.8:
            empty_strings = int(sum(
                1 for v in non_null
                if isinstance(v, str) and v.strip() == ""
            ))
            whitespace = int(sum(
                1 for v in non_null
                if isinstance(v, str) and v != v.strip()
            ))
            info["empty_strings"] = empty_strings
            info["whitespace"] = whitespace

            if empty_strings:
                issues.append({
                    "level": "INFO",
                    "column": name,
                    "message": (
                        f"{name}: {empty_strings} empty string value(s)"
                    ),
                })
            if whitespace:
                issues.append({
                    "level": "INFO",
                    "column": name,
                    "message": (
                        f"{name}: {whitespace} value(s) with leading or "
                        f"trailing whitespace"
                    ),
                })
            return info

        values = coerced.dropna()
        n_values = int(len(values))

        info["min"] = float(values.min())
        info["max"] = float(values.max())
        info["mean"] = float(values.mean())
        info["median"] = float(values.median())
        info["zeros"] = int((values == 0).sum())
        info["negatives"] = int((values < 0).sum())

        outliers = DataQualityAnalysis._count_outliers(values)
        info["outliers"] = outliers

        median = info["median"]
        if median > 0 and info["max"] > median * 1000:
            issues.append({
                "level": "ERROR",
                "column": name,
                "message": (
                    f"{name}: max ({info['max']:.2f}) is "
                    f"{info['max'] / median:,.0f}x the median "
                    f"({median:.2f}) - possible unit mix-up or "
                    f"concatenated rows"
                ),
            })
        elif median < 0 and info["min"] < median * 1000:
            issues.append({
                "level": "ERROR",
                "column": name,
                "message": (
                    f"{name}: min ({info['min']:.2f}) is far below the "
                    f"median ({median:.2f}) - possible unit mix-up"
                ),
            })

        if n_values and info["zeros"] / n_values >= 0.5:
            issues.append({
                "level": "WARNING",
                "column": name,
                "message": (
                    f"{name}: {info['zeros']} zero value(s) "
                    f"({info['zeros'] / n_values:.1%})"
                ),
            })

        if info["negatives"]:
            issues.append({
                "level": "INFO",
                "column": name,
                "message": (
                    f"{name}: {info['negatives']} negative value(s)"
                ),
            })

        if outliers and n_values and outliers / n_values < 0.2:
            issues.append({
                "level": "INFO",
                "column": name,
                "message": (
                    f"{name}: {outliers} outlier(s) detected (IQR)"
                ),
            })

        return info

    @staticmethod
    def _count_outliers(values) -> int:
        """Count values outside the 1.5 IQR fence.

        Args:
            values: Numeric pandas Series.

        Returns:
            Number of outliers.
        """
        if len(values) < 4:
            return 0

        q1 = float(values.quantile(0.25))
        q3 = float(values.quantile(0.75))
        iqr = q3 - q1
        if iqr == 0:
            return 0

        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        return int(((values < lower) | (values > upper)).sum())

    @staticmethod
    def _type_name(value) -> str:
        """Return a simplified Python type name for a cell value.

        Args:
            value: A non-null cell value.

        Returns:
            One of bool, int, float, datetime, str or the original type name.
        """
        if isinstance(value, bool):
            return "bool"
        if isinstance(value, (Integral,)):
            return "int"
        if isinstance(value, (Real,)):
            return "float"
        if isinstance(value, (datetime, date)):
            return "datetime"
        if isinstance(value, str):
            return "str"
        return type(value).__name__
