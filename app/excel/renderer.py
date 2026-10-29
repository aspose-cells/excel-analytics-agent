from aspose.cells.charts import ChartType
from aspose.pydrawing import Color
from aspose.cells import BackgroundType
from aspose.cells import CellsHelper

from app.logger import logger

import io

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import gaussian_kde


class ChartRenderer:
    """Renderer for adding charts to Excel worksheets."""

    @staticmethod
    def add_line_chart(
        ws, first_row: int, first_col: int, row_count: int
    ) -> None:
        """Add or update a line chart on the worksheet.

        If a chart already exists, its data series are updated in-place
        (avoids Aspose.Cells save persistence bug with chart removal).

        Args:
            ws: The target worksheet.
            first_row: Row index of the header row.
            first_col: Column index for categories (X axis).
            row_count: Number of data rows (excluding header).
        """
        try:
            data_start_row = first_row + 1
            data_end_row = first_row + row_count - 1

            category_col = first_col
            value_col = first_col + 1

            category_start = CellsHelper.cell_index_to_name(
                data_start_row, category_col
            )
            category_end = CellsHelper.cell_index_to_name(
                data_end_row, category_col
            )

            value_start = CellsHelper.cell_index_to_name(
                data_start_row, value_col
            )
            value_end = CellsHelper.cell_index_to_name(
                data_end_row, value_col
            )

            category_range = f"{category_start}:{category_end}"
            value_range = f"{value_start}:{value_end}"

            existing = list(ws.charts)
            if existing:
                chart = existing[0]
                chart.n_series.clear()
                chart.n_series.add(value_range, True)
                chart.n_series.category_data = category_range
                chart.title.text = "Analysis Result"
                if chart.n_series.length > 0:
                    chart.n_series[0].data_labels.show_value = True
            else:
                chart_index = ws.charts.add(ChartType.LINE, 5, 5, 25, 15)
                chart = ws.charts[chart_index]
                chart.n_series.add(value_range, True)
                chart.n_series.category_data = category_range
                chart.title.text = "Analysis Result"
                if chart.n_series.length > 0:
                    chart.n_series[0].data_labels.show_value = True

            logger.info("Line chart added/updated successfully")
        except Exception as e:
            logger.error(f"Failed to add line chart: {e}")
            raise

    @staticmethod
    def add_poly_fit_chart(
        ws, poly_results: dict, numeric_df,
        min_r_squared: float = 0.5
    ) -> None:
        """Render scatter + polynomial fit curve for each column and
        embed the chart images into the worksheet.

        Columns without a meaningful fit are skipped:
        - ``is_better_than_linear`` is False (a straight line fits as well)
        - ``r_squared`` below ``min_r_squared`` (weak, noise-like fit)

        Args:
            ws: The target worksheet.
            poly_results: ``results["poly_regression"]`` mapping
                ``{column: {coefficients, r_squared, degree, ...}}``.
            numeric_df: DataFrame holding the original numeric columns
                used to draw the scatter points.
            min_r_squared: Minimum R-squared required to draw the chart
                (default 0.5).

        Raises:
            RuntimeError: If rendering or embedding fails.
        """
        try:
            if not poly_results:
                return

            header_row = ws.cells.min_data_row
            first_col = ws.cells.min_data_column
            data_end_row = ws.cells.max_data_row

            # Anchor images below the data and the native line chart
            # (native chart occupies rows 5-25), stacked vertically and
            # after any pictures already embedded by other renderers.
            row_stride = 22
            base_row = max(data_end_row, 25) + 5
            anchor_row = base_row + len(list(ws.pictures)) * row_stride

            chart_index = 0

            for col, val in poly_results.items():

                if not isinstance(val, dict) or "coefficients" not in val:
                    continue
                if col not in numeric_df.columns:
                    continue

                if not val.get("is_better_than_linear"):
                    logger.info(
                        "Poly fit chart skipped for '%s': linear trend "
                        "fits as well as the polynomial",
                        col,
                    )
                    continue

                r_squared = float(val.get("r_squared", 0.0))
                if r_squared < min_r_squared:
                    logger.info(
                        "Poly fit chart skipped for '%s': R2=%.3f "
                        "below threshold %.2f",
                        col, r_squared, min_r_squared,
                    )
                    continue

                values = (
                    numeric_df[col]
                    .dropna()
                    .astype(float)
                    .tolist()
                )
                if len(values) < 3:
                    continue

                x = np.arange(len(values), dtype=float)
                coeffs = np.array(val["coefficients"], dtype=float)

                x_smooth = np.linspace(x.min(), x.max(), 300)
                y_smooth = np.polyval(coeffs, x_smooth)

                fig, ax = plt.subplots(figsize=(6, 3.5), dpi=100)
                ax.scatter(x, values, s=15, color="#1f77b4",
                           label="Original data", zorder=2)
                ax.plot(x_smooth, y_smooth, color="red", linewidth=2,
                        label=f"Degree-{val.get('degree', '?')} fit "
                              f"(R2={r_squared:.3f})",
                        zorder=3)
                ax.set_title(f"{col} - Polynomial Fit")
                ax.set_xlabel("Index")
                ax.set_ylabel(str(col))
                ax.legend(loc="best", fontsize=8)
                ax.grid(True, alpha=0.3)
                fig.tight_layout()

                buf = io.BytesIO()
                fig.savefig(buf, format="png")
                plt.close(fig)
                buf.seek(0)

                pic_row = anchor_row + chart_index * row_stride
                ws.pictures.add(pic_row, first_col, buf)
                chart_index += 1

                logger.info(
                    "Poly fit chart embedded for column '%s'", col
                )

        except Exception as e:
            logger.error(f"Failed to add poly fit chart: {e}")
            raise

    @staticmethod
    def add_kde_chart(ws, kde_results: dict, numeric_df) -> None:
        """Render histogram + KDE density curve for each column and
        embed the chart images into the worksheet.

        Detected modes are marked with dashed vertical lines.

        Args:
            ws: The target worksheet.
            kde_results: ``results["kde"]`` mapping
                ``{column: {bandwidth, n_modes, mode_locations, ...}}``.
            numeric_df: DataFrame holding the original numeric columns.

        Raises:
            RuntimeError: If rendering or embedding fails.
        """
        try:
            if not kde_results:
                return

            first_col = ws.cells.min_data_column
            data_end_row = ws.cells.max_data_row

            row_stride = 22
            base_row = max(data_end_row, 25) + 5
            anchor_row = base_row + len(list(ws.pictures)) * row_stride

            chart_index = 0

            for col, val in kde_results.items():

                if not isinstance(val, dict) or "n_modes" not in val:
                    continue
                if col not in numeric_df.columns:
                    continue

                values = (
                    numeric_df[col]
                    .dropna()
                    .astype(float)
                    .tolist()
                )
                if len(values) < 10:
                    continue

                arr = np.asarray(values, dtype=float)
                if float(np.std(arr)) == 0.0:
                    continue

                x_grid = np.linspace(
                    float(arr.min()), float(arr.max()), 300
                )
                density = gaussian_kde(arr)(x_grid)

                fig, ax = plt.subplots(figsize=(6, 3.5), dpi=100)
                ax.hist(arr, bins=30, density=True, alpha=0.35,
                        color="#1f77b4", label="Histogram")
                ax.plot(x_grid, density, color="red", linewidth=2,
                        label="KDE")

                for location in val.get("mode_locations", []):
                    ax.axvline(location, color="green", linestyle="--",
                               linewidth=1)

                ax.set_title(
                    f"{col} - KDE ({val.get('n_modes', 0)} mode(s))"
                )
                ax.set_xlabel(str(col))
                ax.set_ylabel("Density")
                ax.legend(loc="best", fontsize=8)
                ax.grid(True, alpha=0.3)
                fig.tight_layout()

                buf = io.BytesIO()
                fig.savefig(buf, format="png")
                plt.close(fig)
                buf.seek(0)

                pic_row = anchor_row + chart_index * row_stride
                ws.pictures.add(pic_row, first_col, buf)
                chart_index += 1

                logger.info(
                    "KDE chart embedded for column '%s'", col
                )

        except Exception as e:
            logger.error(f"Failed to add KDE chart: {e}")
            raise