import time
import random
import tempfile
import os
import numpy as np
import aspose.cells as cells
from aspose.cells import BackgroundType
from aspose.pydrawing import Color


# ═══════════════════════════════════════════════════════════
#  辅助函数
# ═══════════════════════════════════════════════════════════

HEADERS = ["Sales", "Cost", "Profit", "Qty", "Discount"]


def _create_workbook(rows=100, cols=5):
    """新建 Workbook，sheet0 填充随机数值测试数据，返回 (wb, ws, data_dict)"""
    wb = cells.Workbook()
    ws = wb.worksheets[0]
    headers = HEADERS[:cols]
    for c, h in enumerate(headers):
        ws.cells.get(0, c).put_value(h)
    for r in range(rows):
        for c in range(cols):
            ws.cells.get(r + 1, c).put_value(round(random.uniform(10, 1000), 2))
    data = {h: [] for h in headers}
    for r in range(1, rows + 1):
        for c, h in enumerate(headers):
            data[h].append(ws.cells.get(r, c).double_value)
    return wb, ws, data


def _write_list_of_dict_result(wb, sheet_name, result):
    """将 list[dict] 结果写入新 sheet（表头 + 行数据）"""
    if not result:
        return
    ws = wb.worksheets.add(sheet_name)
    keys = list(result[0].keys())
    for c, k in enumerate(keys):
        ws.cells.get(0, c).put_value(k)
    for r, row in enumerate(result, start=1):
        for c, k in enumerate(keys):
            ws.cells.get(r, c).put_value(_to_native(row[k]))


def _to_native(val):
    """将 numpy 类型转为 Python 原生类型"""
    if isinstance(val, (np.bool_, np.integer)):
        return int(val)
    if isinstance(val, np.floating):
        return float(val)
    return val


def _write_dict_result(wb, sheet_name, result):
    """将 dict 结果写入新 sheet（key-value 两列）"""
    ws = wb.worksheets.add(sheet_name)
    ws.cells.get(0, 0).put_value("Metric")
    ws.cells.get(0, 1).put_value("Value")
    for r, (k, v) in enumerate(result.items(), start=1):
        ws.cells.get(r, 0).put_value(k)
        if isinstance(v, (dict, list)):
            ws.cells.get(r, 1).put_value(str(v)[:255])
        else:
            ws.cells.get(r, 1).put_value(_to_native(v))


def _write_list_of_float_result(wb, sheet_name, result, label="Value"):
    """将 list[float] 结果写入新 sheet（Index + Label 两列）"""
    ws = wb.worksheets.add(sheet_name)
    ws.cells.get(0, 0).put_value("Index")
    ws.cells.get(0, 1).put_value(label)
    for r, v in enumerate(result, start=1):
        ws.cells.get(r, 0).put_value(r)
        ws.cells.get(r, 1).put_value(_to_native(v))


def _write_result(wb, sheet_name, result, label="Value"):
    """根据结果类型自动选择写入方式"""
    if isinstance(result, list) and result and isinstance(result[0], dict):
        _write_list_of_dict_result(wb, sheet_name, result)
    elif isinstance(result, dict):
        _write_dict_result(wb, sheet_name, result)
    elif isinstance(result, list):
        _write_list_of_float_result(wb, sheet_name, result, label=label)


def _save_and_verify(wb, sheet_name):
    """保存到临时文件并验证 sheet 存在"""
    tmp = tempfile.mktemp(suffix=".xlsx")
    wb.save(tmp)
    verify_wb = cells.Workbook(tmp)
    names = [verify_wb.worksheets[i].name for i in range(len(verify_wb.worksheets))]
    assert sheet_name in names, f"Sheet '{sheet_name}' 未写入，当前 sheets: {names}"
    os.remove(tmp)
    return True


# ═══════════════════════════════════════════════════════════
#  分析层基准测试（SciPy / sklearn + Aspose.Cells）
# ═══════════════════════════════════════════════════════════


# ─── 1. 异常检测 ────────────────────────────────────────
def test_anomaly_detection():
    from app.analysis.anomaly import AnomalyAnalysis

    np.random.seed(42)
    wb, ws, data = _create_workbook(rows=200, cols=1)
    col = data["Sales"]
    col[100] = 10000.0

    result = AnomalyAnalysis.detect_zscore(col, threshold=3.0)
    assert isinstance(result, list) and len(result) >= 1
    assert any(a["value"] == 10000.0 for a in result)

    _write_result(wb, "Anomaly_Result", result)
    _save_and_verify(wb, "Anomaly_Result")


# ─── 2. 趋势分析 ────────────────────────────────────────
def test_trend_analysis():
    from app.analysis.trend import TrendAnalysis

    wb, ws, data = _create_workbook(rows=100, cols=1)
    result = TrendAnalysis.analyze(data["Sales"])

    assert isinstance(result, dict)
    assert "slope" in result and "smoothed" in result

    _write_result(wb, "Trend_Result", result)
    _save_and_verify(wb, "Trend_Result")


# ─── 3. 线性回归 ────────────────────────────────────────
def test_regression():
    from app.analysis.regression import RegressionAnalysis

    wb, ws, data = _create_workbook(rows=100, cols=1)
    result = RegressionAnalysis.linear_regression(data["Sales"])

    assert isinstance(result, dict)
    assert "slope" in result and "rvalue" in result

    _write_result(wb, "Regression_Result", result)
    _save_and_verify(wb, "Regression_Result")


# 用例 3.5. 多项式回归
def test_polynomial_regression():
    from app.analysis.regression import RegressionAnalysis

    wb, ws, data = _create_workbook(rows=100, cols=1)
    result = RegressionAnalysis.polynomial_regression(data["Sales"], degree=2)

    assert isinstance(result, dict)
    assert "coefficients" in result and "r_squared" in result
    assert len(result["coefficients"]) == 3
    assert result["degree"] == 2
    assert 0.0 <= result["r_squared"] <= 1.0
    assert isinstance(result["is_better_than_linear"], bool)

    _write_result(wb, "PolyRegression_Result", result)
    _save_and_verify(wb, "PolyRegression_Result")

# ─── 4. FFT 频率分析 ────────────────────────────────────
def test_fft():
    from app.analysis.fft_analysis import FFTAnalysis

    wb, ws, data = _create_workbook(rows=200, cols=1)
    result = FFTAnalysis.analyze(data["Sales"])

    assert isinstance(result, list) and len(result) == 200

    _write_result(wb, "FFT_Result", result, label="Magnitude")
    _save_and_verify(wb, "FFT_Result")


# ─── 5. 聚类 ────────────────────────────────────────────
def test_clustering():
    from app.analysis.clustering import ClusteringAnalysis

    wb, ws, data = _create_workbook(rows=90, cols=1)
    result = ClusteringAnalysis.cluster(data["Sales"], k=3)

    assert isinstance(result, list) and len(result) == 90
    assert all(0 <= l <= 2 for l in result)

    _write_result(wb, "Clustering_Result", result, label="Cluster")
    _save_and_verify(wb, "Clustering_Result")


# ─── 6. 相关性分析 ──────────────────────────────────────
def test_correlation():
    import pandas as pd
    from app.analysis.correlation import CorrelationAnalysis

    wb, ws, data = _create_workbook(rows=100, cols=5)
    df = pd.DataFrame(data)
    result = CorrelationAnalysis.correlation_matrix(df)

    assert isinstance(result, dict)

    _write_result(wb, "Correlation_Result", result)
    _save_and_verify(wb, "Correlation_Result")


# ─── 7. 分布分析 ────────────────────────────────────────
def test_distribution():
    from app.analysis.distribution import DistributionAnalysis

    wb, ws, data = _create_workbook(rows=200, cols=1)
    result = DistributionAnalysis.check_normal_distribution(data["Sales"])

    assert isinstance(result, dict)
    assert "is_normal" in result

    _write_result(wb, "Distribution_Result", result)
    _save_and_verify(wb, "Distribution_Result")


# ─── 8. 变点检测 ────────────────────────────────────────
def test_change_point():
    from app.analysis.change_point import ChangePointAnalysis

    wb, ws, data = _create_workbook(rows=100, cols=1)
    result = ChangePointAnalysis.detect(data["Sales"])

    assert isinstance(result, list)

    _write_result(wb, "ChangePoint_Result", result)
    _save_and_verify(wb, "ChangePoint_Result")


# ─── 9. 平滑分析 ────────────────────────────────────────
def test_smoothing():
    from app.analysis.smoothing import SmoothingAnalysis

    wb, ws, data = _create_workbook(rows=100, cols=1)
    result = SmoothingAnalysis.moving_average(data["Sales"], window=5)

    assert isinstance(result, list) and len(result) == 100

    _write_result(wb, "Smoothing_Result", result, label="Smoothed")
    _save_and_verify(wb, "Smoothing_Result")


# ─── 10. 季节性分析 ─────────────────────────────────────
def test_seasonality():
    from app.analysis.seasonality import SeasonalityAnalysis

    wb, ws, data = _create_workbook(rows=100, cols=1)
    result = SeasonalityAnalysis.analyze(data["Sales"])

    assert isinstance(result, dict)
    assert "trend" in result and "seasonal" in result

    _write_result(wb, "Seasonality_Result", result)
    _save_and_verify(wb, "Seasonality_Result")


# ─── 11. 描述统计 ───────────────────────────────────────
def test_statistics():
    from app.analysis.statistics_analysis import StatisticsAnalysis

    wb, ws, data = _create_workbook(rows=200, cols=1)
    result = StatisticsAnalysis.describe(data["Sales"])

    assert isinstance(result, dict)
    assert "mean" in result and "std" in result

    _write_result(wb, "Statistics_Result", result)
    _save_and_verify(wb, "Statistics_Result")


# ─── 12. PCA 降维 ───────────────────────────────────────
def test_pca():
    import pandas as pd
    from app.analysis.pca_analysis import PCAAnalysis

    wb, ws, data = _create_workbook(rows=100, cols=5)
    df = pd.DataFrame(data)
    result = PCAAnalysis.analyze(df)

    assert isinstance(result, dict)
    assert "explained_variance" in result

    _write_result(wb, "PCA_Result", result)
    _save_and_verify(wb, "PCA_Result")


# ─── 13. 离群值检测 ─────────────────────────────────────
def test_outlier():
    from app.analysis.outlier import OutlierAnalysis

    wb, ws, data = _create_workbook(rows=100, cols=1)
    data["Sales"][50] = 99999.0
    result = OutlierAnalysis.iqr_outliers(data["Sales"])

    assert isinstance(result, list)
    assert any(o["value"] == 99999.0 for o in result)

    _write_result(wb, "Outlier_Result", result)
    _save_and_verify(wb, "Outlier_Result")


# ─── 14. 预测分析 ───────────────────────────────────────
def test_forecasting():
    from app.analysis.forecasting import ForecastingAnalysis

    wb, ws, data = _create_workbook(rows=100, cols=1)
    result = ForecastingAnalysis.forecast(data["Sales"], steps=10)

    assert isinstance(result, list) and len(result) == 10

    _write_result(wb, "Forecast_Result", result, label="Forecast")
    _save_and_verify(wb, "Forecast_Result")


# ─── 15. 假设检验 ───────────────────────────────────────
def test_hypothesis():
    from app.analysis.hypothesis import HypothesisAnalysis

    wb, ws, data = _create_workbook(rows=100, cols=3)
    cols = list(data.values())[:3]
    result = HypothesisAnalysis.anova(*cols)

    assert isinstance(result, dict)
    assert "p_value" in result and "significant" in result

    _write_result(wb, "Hypothesis_Result", result)
    _save_and_verify(wb, "Hypothesis_Result")


# ─── 16. ARIMA 预测 ──────────────────────────────────────
def test_arima():
    from app.analysis.arima_forecast import ARIMAForecast

    wb, ws, data = _create_workbook(rows=100, cols=1)
    result = ARIMAForecast.forecast(data["Sales"], steps=10)

    assert isinstance(result, dict)
    assert "forecast" in result and "aic" in result
    assert len(result["forecast"]) == 10

    _write_result(wb, "ARIMA_Result", result)
    _save_and_verify(wb, "ARIMA_Result")


# ═══════════════════════════════════════════════════════════
#  Excel 层基准测试（Aspose.Cells 原生操作）
# ═══════════════════════════════════════════════════════════


# ─── 17. Excel 写入 ──────────────────────────────────────
def test_excel_write():
    from app.excel.writer import ExcelWriter

    reports = {f"metric_{i}": round(random.uniform(10, 1000), 2) for i in range(50)}
    tmp = tempfile.mktemp(suffix=".xlsx")
    ExcelWriter.write_report(tmp, reports)

    verify_wb = cells.Workbook(tmp)
    assert len(verify_wb.worksheets) >= 1
    ws = verify_wb.worksheets[0]
    assert ws.cells.get(0, 0).string_value == "metric_0"
    os.remove(tmp)


# ─── 18. 图表渲染 ────────────────────────────────────────
def test_chart_render():
    from app.excel.renderer import ChartRenderer

    wb, ws, _ = _create_workbook(rows=100, cols=2)
    ChartRenderer.add_line_chart(ws, 0, 0, 100)

    assert len(list(ws.charts)) >= 1

    ws2 = wb.worksheets.add("ChartResult")
    ws2.cells.get(0, 0).put_value("Status")
    ws2.cells.get(0, 1).put_value("Chart added")
    _save_and_verify(wb, "ChartResult")


# ─── 19. 格式化高亮 ──────────────────────────────────────
def test_formatter():
    from app.excel.formatter import Formatter

    wb, ws, data = _create_workbook(rows=200, cols=3)
    results = {"anomaly": {}}
    for h in ["Sales", "Cost", "Profit"]:
        results["anomaly"][h] = [
            {"index": i, "value": data[h][i], "zscore": 4.0}
            for i in range(0, 200, 20)
        ]

    Formatter.apply_highlights(ws, results)

    highlighted = False
    for r in range(1, 201):
        for c in range(3):
            style = ws.cells.get(r, c).get_style()
            if style.pattern == BackgroundType.SOLID:
                highlighted = True
                break
        if highlighted:
            break
    assert highlighted, "未检测到高亮单元格"

    ws_result = wb.worksheets.add("Formatter_Result")
    ws_result.cells.get(0, 0).put_value("Status")
    ws_result.cells.get(0, 1).put_value("Highlights applied")
    _save_and_verify(wb, "Formatter_Result")


# ─── 20. 批注写入 ────────────────────────────────────────
def test_comment_writer():
    from app.excel.comment_writer import CommentWriter

    wb, ws, data = _create_workbook(rows=100, cols=3)
    results = {"anomaly": {}}
    for h in ["Sales", "Cost", "Profit"]:
        results["anomaly"][h] = [
            {"index": i, "value": data[h][i], "zscore": round(random.uniform(3.1, 6.0), 2)}
            for i in range(0, 100, 10)
        ]

    CommentWriter.add_comments(ws, results)

    has_comment = False
    for r in range(1, 101):
        for c in range(3):
            if ws.comments.get(r, c) is not None:
                has_comment = True
                break
        if has_comment:
            break
    assert has_comment, "未检测到批注"

    ws_result = wb.worksheets.add("Comment_Result")
    ws_result.cells.get(0, 0).put_value("Status")
    ws_result.cells.get(0, 1).put_value("Comments added")
    _save_and_verify(wb, "Comment_Result")


# ─── 21. 列类型检测 ──────────────────────────────────────
def test_column_detector():
    from app.excel.detector import ColumnDetector

    wb, ws, _ = _create_workbook(rows=50, cols=5)
    ws_text = wb.worksheets.add("TextCol")
    ws_text.cells.get(0, 0).put_value("Name")
    for r in range(1, 51):
        ws_text.cells.get(r, 0).put_value(f"item_{r}")

    detector = ColumnDetector()
    numeric_cols = detector.detect_numeric_columns(ws)

    assert isinstance(numeric_cols, list)
    assert len(numeric_cols) >= 1, "应至少检出 1 个数值列"

    ws_result = wb.worksheets.add("Detector_Result")
    ws_result.cells.get(0, 0).put_value("NumericColumns")
    ws_result.cells.get(0, 1).put_value(str(numeric_cols))
    _save_and_verify(wb, "Detector_Result")


# ─── 22. Excel 读取 ──────────────────────────────────────
def test_excel_read():
    from app.excel.reader import ExcelReader

    wb_src, _, _ = _create_workbook(rows=200, cols=5)
    tmp = tempfile.mktemp(suffix=".xlsx")
    wb_src.save(tmp)

    df = ExcelReader.load_sheet_as_dataframe(tmp)
    os.remove(tmp)

    assert len(df) == 200
    assert list(df.columns) == HEADERS[:5]

    wb_result = cells.Workbook()
    ws = wb_result.worksheets[0]
    ws.cells.get(0, 0).put_value("Status")
    ws.cells.get(0, 1).put_value("Read OK")
    ws.cells.get(1, 0).put_value("Rows")
    ws.cells.get(1, 1).put_value(len(df))
    ws.cells.get(2, 0).put_value("Columns")
    ws.cells.get(2, 1).put_value(str(list(df.columns)))
    _save_and_verify(wb_result, "Sheet1")
