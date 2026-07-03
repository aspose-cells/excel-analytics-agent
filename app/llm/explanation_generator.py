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

        statistics = results.get("statistics", {})
        for col, val in statistics.items():
            if isinstance(val, dict) and "mean" in val:
                texts.append(
                    f"{col}: mean={val['mean']:.2f}, std={val['std']:.2f}, "
                    f"min={val['min']:.2f}, max={val['max']:.2f}."
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