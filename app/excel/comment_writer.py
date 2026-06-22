from app.logger import logger


class CommentWriter:
    """Writer for adding anomaly-detection comments to Excel cells."""

    @staticmethod
    def add_comments(
        ws,
        results: dict,
        start_row: int | None = None,
        start_col: int | None = None,
    ) -> None:
        """Add comments to anomaly cells with value and Z-score details.

        Args:
            ws: The target worksheet.
            results: Dictionary containing anomaly data under the ``anomaly`` key.
            start_row: Starting row for header detection. Auto-detected if ``None``.
            start_col: Starting column for header detection. Auto-detected if ``None``.
        """
        try:
            anomaly_results = results.get("anomaly", {})

            cells = ws.cells

            if start_row is None:
                start_row = cells.min_data_row

            if start_col is None:
                start_col = cells.min_data_column

            for column_name, anomalies in anomaly_results.items():

                if not anomalies:
                    continue

                excel_col = -1

                for c in range(start_col, cells.max_data_column + 1):
                    header = cells.get(start_row, c).string_value
                    if header == column_name:
                        excel_col = c
                        break

                if excel_col == -1:
                    logger.warning(
                        f"Column '{column_name}' not found for comments"
                    )
                    continue

                for item in anomalies:
                    pandas_index = item["index"]
                    excel_row = start_row + 1 + pandas_index

                    existing = ws.comments.get(excel_row, excel_col)
                    if existing is not None:
                        comment = existing
                    else:
                        idx = ws.comments.add(excel_row, excel_col)
                        comment = ws.comments[idx]

                    zscore = item.get("zscore", "N/A")
                    comment.note = (
                        f"Anomaly detected\n"
                        f"Value: {item['value']}\n"
                        f"Z-Score: {zscore}"
                    )

            logger.info("Comments added successfully")
        except Exception as e:
            logger.error(f"Failed to add comments: {e}")
            raise