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

                texts.append(
                    f"{col} contains {len(items)} anomalies."
                )

        trend = results.get("trend")

        if trend:
            texts.append(
                "Trend analysis completed."
            )

        summary = "\n".join(texts)
        logger.info(f"Generated narrative ({len(texts)} items)")
        return summary