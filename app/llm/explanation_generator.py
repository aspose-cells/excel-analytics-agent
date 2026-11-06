from app.logger import logger
from typing import Any, Dict, List


class NarrativeGenerator:
    """Generates human-readable narrative summaries from analysis results."""

    @staticmethod
    def generate(results: Dict[str, Any]) -> str:
        """Generate a narrative summary from the analysis results.

        Args:
            results: Dict of analysis results keyed by tool name.

        Returns:
            A string containing the narrative summary.
        """
        texts: List[str] = []

        profile = results.get("data_profile", {})
        if isinstance(profile, dict) and "table" in profile:
            table = profile["table"]
            score = float(profile.get("quality_score", 100))
            texts.append(
                f"Data quality score {score:.0f}/100 "
                f"({table.get('rows', 0)} rows, "
                f"{table.get('columns', 0)} columns, "
                f"{table.get('duplicate_rows', 0)} duplicate row(s))."
            )

            issues = profile.get("issues", [])
            if issues:
                for issue in issues[:3]:
                    texts.append(
                        f"[{issue.get('level', 'INFO')}] "
                        f"{issue.get('message', '')}"
                    )
                if len(issues) > 3:
                    texts.append(
                        f"{len(issues) - 3} more data quality issue(s) "
                        f"listed in the 'Data Quality' sheet."
                    )
            else:
                texts.append("No data quality issues detected.")

        anomaly = results.get("anomaly", {})
        for col, items in anomaly.items():
            if items:
                texts.append(f"{col} contains {len(items)} anomalies.")

        trend = results.get("trend", {})
        for col, val in trend.items():
            if isinstance(val, dict) and "slope" in val:
                direction = "upward" if val["slope"] > 0 else "downward"
                texts.append(f"{col} shows a {direction} trend (slope={val['slope']:.4f}).")
            elif val:
                texts.append(f"{col} trend analysis completed.")

        clustering = results.get("clustering", {})
        for col, val in clustering.items():
            if isinstance(val, dict) and "clusters" in val:
                n_clusters = len(set(val["clusters"]))
                texts.append(f"{col} was grouped into {n_clusters} clusters.")

        correlation = results.get("correlation", {})
        if correlation and isinstance(correlation, dict):
            pairs = []
            for col1, row in correlation.items():
                for col2, r in row.items():
                    if col1 < col2 and abs(r) > 0.5:
                        pairs.append(f"{col1}-{col2}(r={r:.3f})")
            if pairs:
                texts.append(f"Strong correlations found: {', '.join(pairs)}.")
            else:
                texts.append("No strong correlations (>0.5) found.")

        pca = results.get("pca", {})
        if isinstance(pca, dict) and pca.get("explained_variance"):
            ev = pca["explained_variance"]
            texts.append(f"PCA: {len(ev)} component(s) explain {sum(ev)*100:.1f}% of variance.")

        regression = results.get("regression", {})
        for col, val in regression.items():
            if isinstance(val, dict) and "rvalue" in val:
                texts.append(
                    f"{col} regression: R={val['rvalue']:.3f}, "
                    f"slope={val['slope']:.4f}, p={val['pvalue']:.4f}."
                )

        poly = results.get("poly_regression", {})
        for col, val in poly.items():
            if isinstance(val, dict) and "r_squared" in val:
                curve = (
                    "nonlinear curve"
                    if val.get("is_better_than_linear")
                    else "linear trend"
                )
                texts.append(
                    f"{col} fits a degree-{val['degree']} polynomial "
                    f"(R²={val['r_squared']:.3f}); {curve} is more appropriate."
                )

        statistics = results.get("statistics", {})
        for col, val in statistics.items():
            if isinstance(val, dict) and "mean" in val:
                texts.append(
                    f"{col}: mean={val['mean']:.2f}, std={val['std']:.2f}, "
                    f"min={val['min']:.2f}, max={val['max']:.2f}."
                )

        kde = results.get("kde", {})
        for col, val in kde.items():
            if isinstance(val, dict) and "n_modes" in val:
                if val.get("is_multimodal"):
                    locations = ", ".join(
                        f"{x:.1f}" for x in val.get("mode_locations", [])
                    )
                    texts.append(
                        f"{col} is multimodal ({val['n_modes']} peaks near "
                        f"{locations}) - likely multiple subgroups."
                    )
                else:
                    texts.append(f"{col} is unimodal (single peak).")

        change_point = results.get("change_point", {})
        for col, val in change_point.items():
            if isinstance(val, list):
                if val:
                    positions = ", ".join(
                        str(item.get("position", "?")) for item in val[:5]
                    )
                    texts.append(
                        f"{col} contains {len(val)} change point(s) at "
                        f"index {positions}."
                    )
                else:
                    texts.append(f"{col} shows no significant change points.")

        distribution = results.get("distribution", {})
        for col, val in distribution.items():
            if isinstance(val, dict) and "pvalue" in val:
                if val.get("is_normal"):
                    texts.append(
                        f"{col} is consistent with a normal distribution "
                        f"(p={val['pvalue']:.4f})."
                    )
                else:
                    texts.append(
                        f"{col} deviates from a normal distribution "
                        f"(p={val['pvalue']:.4f})."
                    )

        outlier = results.get("outlier", {})
        for col, val in outlier.items():
            if isinstance(val, list):
                if val:
                    texts.append(f"{col} contains {len(val)} IQR outliers.")
                else:
                    texts.append(f"{col} contains no IQR outliers.")

        seasonality = results.get("seasonality", {})
        for col, val in seasonality.items():
            if isinstance(val, dict) and "trend" in val:
                texts.append(
                    f"{col}: seasonal decomposition completed "
                    f"({len(val.get('trend', []))} points)."
                )

        smoothing = results.get("smoothing", {})
        for col, val in smoothing.items():
            if isinstance(val, list) and val:
                texts.append(
                    f"{col}: moving average smoothing completed "
                    f"({len(val)} points)."
                )

        forecast = results.get("forecast", {})
        for col, val in forecast.items():
            if isinstance(val, list) and val:
                texts.append(f"{col}: forecast next {len(val)} values (last={val[-1]:.2f}).")

        fft = results.get("fft", {})
        for col, val in fft.items():
            if isinstance(val, list) and val:
                dominant = max(val)
                texts.append(f"{col}: FFT completed, dominant magnitude={dominant:.4f}.")

        summary = "\n".join(texts)
        logger.info(f"Generated narrative ({len(texts)} items)")
        return summary