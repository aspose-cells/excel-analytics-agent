"""Build a compact, LLM-friendly summary of an Excel table's schema."""

import math

import pandas as pd

from app.logger import logger


MAX_COLUMNS = 40
MAX_SAMPLE_ROWS = 3
MAX_TEXT_VALUES = 3
MAX_TEXT_LEN = 30


def _format_number(value) -> str:
    """Format a numeric value for a short schema summary."""
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return "nan"
        text = f"{value:.4f}".rstrip("0").rstrip(".")
        return text or "0"
    return str(value)


def _format_cell(value) -> str:
    """Format a single cell value, truncating long text."""
    if isinstance(value, float) and math.isnan(value):
        return "NaN"
    if value is None:
        return "NaN"
    text = _format_number(value) if isinstance(value, (int, float)) else str(value)
    if len(text) > MAX_TEXT_LEN:
        return text[:MAX_TEXT_LEN] + "..."
    return text


def _is_name_identifier(name: str) -> bool:
    """Guess from a column name whether it holds identifiers.

    Name-based detection also covers numeric IDs such as ``CustomerID``
    (1001, 1002, ...), which content-based rules cannot distinguish from
    a continuous measure.

    Args:
        name: Column name.

    Returns:
        True when the name looks like an identifier column.
    """
    lowered = name.lower().replace(" ", "").replace("_", "").replace("-", "")
    if lowered in {"id", "no", "number", "code", "key"}:
        return True
    return lowered.endswith("id")


def _looks_like_text_identifier(series, non_null) -> bool:
    """Return True when a text column is almost entirely unique.

    Args:
        series: The full column.
        non_null: The column without missing values.

    Returns:
        True when at least 95% of the non-null values are unique.
    """
    if not len(non_null):
        return False

    is_text = series.dtype == object or pd.api.types.is_string_dtype(series)
    if not is_text:
        return False

    try:
        return non_null.nunique() / len(non_null) >= 0.95
    except Exception:
        return False


def build_schema_summary(
    df: pd.DataFrame,
    file_name: str | None = None,
    max_columns: int = MAX_COLUMNS,
) -> str:
    """Summarize a DataFrame for inclusion in the LLM planning prompt.

    Only a compact description is produced (column names, types, missing
    counts, ranges and a few sample rows) so that token usage stays low
    and no full data dump is sent to the model.

    Args:
        df: The table to describe.
        file_name: Optional file name shown in the summary header.
        max_columns: Maximum number of columns to describe.

    Returns:
        A plain-text schema summary.
    """
    lines = []

    header = f"Rows: {len(df)} | Columns: {len(df.columns)}"
    if file_name:
        lines.append(f"File: {file_name}")
    lines.append(header)

    numeric_columns = df.select_dtypes(include="number").columns.tolist()
    text_columns = df.select_dtypes(exclude="number").columns.tolist()
    if numeric_columns:
        lines.append(f"Numeric columns: {', '.join(map(str, numeric_columns))}")
    if text_columns:
        lines.append(f"Other columns: {', '.join(map(str, text_columns))}")

    lines.append("Columns:")
    columns = list(df.columns)
    duplicate_names = {
        str(name) for name in columns if columns.count(name) > 1
    }
    shown = columns[:max_columns]
    for index, column in enumerate(shown, start=1):
        # Positional access keeps the summary working when two columns
        # share the same header (df[column] would return a DataFrame).
        series = df.iloc[:, index - 1]
        non_null = series.dropna()
        unique = int(non_null.nunique()) if len(non_null) else 0
        missing = int(series.isna().sum())

        parts = [
            f"{index}. {column}",
            str(series.dtype),
            f"missing={missing}",
            f"unique={unique}",
        ]

        if unique <= 1:
            parts.append("(constant)")
        if str(column) in duplicate_names:
            parts.append("(duplicate name)")

        is_identifier = _is_name_identifier(str(column))
        try:
            if pd.api.types.is_numeric_dtype(series) and len(non_null):
                parts.append(f"min={_format_number(non_null.min())}")
                parts.append(f"max={_format_number(non_null.max())}")
                parts.append(f"median={_format_number(non_null.median())}")
            elif pd.api.types.is_datetime64_any_dtype(series) and len(non_null):
                parts.append(f"min={non_null.min()}")
                parts.append(f"max={non_null.max()}")
            else:
                samples = [
                    _format_cell(value)
                    for value in non_null.head(MAX_TEXT_VALUES)
                ]
                if samples:
                    parts.append(f"sample=[{', '.join(samples)}]")
                if not is_identifier and _looks_like_text_identifier(
                    series, non_null
                ):
                    is_identifier = True
        except Exception as e:
            logger.warning(f"Could not describe column '{column}': {e}")

        if is_identifier:
            parts.append("(likely identifier)")

        lines.append(" | ".join(parts))

    remaining = len(df.columns) - len(shown)
    if remaining > 0:
        lines.append(f"... ({remaining} more column(s) not shown)")

    if len(df):
        lines.append(f"Sample rows (first {min(MAX_SAMPLE_ROWS, len(df))}):")
        for row_index in range(min(MAX_SAMPLE_ROWS, len(df))):
            cells = [
                f"{column}={_format_cell(df.iloc[row_index, position])}"
                for position, column in enumerate(shown)
            ]
            lines.append("  " + ", ".join(cells))

    summary = "\n".join(lines)
    logger.info(
        f"Built schema summary: {len(df)} rows, "
        f"{len(df.columns)} columns, {len(summary)} chars"
    )
    return summary
