from app.agents.excel_agent import ExcelAgent

SCENARIOS = [
    {
        "input_file": "./samples/sales.xlsx",
        "user_prompt": "Analyze sales trends and detect anomalies",
        "output_file": "./output/sales_analysis.xlsx",
    },
    {
        "input_file": "./samples/customer.xlsx",
        "user_prompt": "Analyze customer groups and cluster similar sales patterns",
        "output_file": "./output/customer_analysis.xlsx",
    },
    {
        "input_file": "./samples/sales.xlsx",
        "user_prompt": "Analyze the sales trend in sales.xlsx and fit nonlinear changes with polynomial regression",
        "output_file": "./output/sales_poly_regression.xlsx",
    },
    {
        "input_file": "./samples/customer_segments.xlsx",
        "user_prompt": "Analyze the distribution of customer spending amounts with kernel density estimation (KDE) and detect whether the data is multimodal (whether multiple customer segments exist)",
        "output_file": "./output/customer_kde.xlsx",
    },
    {
        "input_file": "./samples/sales.xlsx",
        "user_prompt": "Detect change points in sales data, test whether it follows a normal distribution, find outliers, and apply moving average smoothing",
        "output_file": "./output/sales_data_quality.xlsx",
    },
]


def run_scenario(agent: ExcelAgent, scenario: dict) -> None:
    input_file = scenario["input_file"]
    user_prompt = scenario["user_prompt"]
    output_file = scenario["output_file"]

    print(f"\n=== {user_prompt} ===")

    results = agent.run(
        file_path=input_file,
        output_file=output_file,
        user_request=user_prompt,
    )

    analysis_results = results.get("analysis_results", {})
    print(f"Tools used: {list(analysis_results.keys())}")

    if "poly_regression" in analysis_results:
        for col, val in analysis_results["poly_regression"].items():
            print(f"{col}: R2={val['r_squared']:.3f}, "
                  f"degree={val['degree']}, "
                  f"better_than_linear={val['is_better_than_linear']}")

    if "kde" in analysis_results:
        for col, val in analysis_results["kde"].items():
            if "n_modes" in val:
                print(f"{col}: modes={val['n_modes']}, "
                      f"peaks={[round(x, 1) for x in val['mode_locations']]}, "
                      f"multimodal={val['is_multimodal']}")

    if "change_point" in analysis_results:
        for col, val in analysis_results["change_point"].items():
            if isinstance(val, list):
                print(f"{col}: change_points={len(val)}")

    if "distribution" in analysis_results:
        for col, val in analysis_results["distribution"].items():
            if isinstance(val, dict) and "is_normal" in val:
                print(f"{col}: is_normal={val['is_normal']}, "
                      f"p={val['pvalue']:.4f}")

    if "outlier" in analysis_results:
        for col, val in analysis_results["outlier"].items():
            if isinstance(val, list):
                print(f"{col}: outliers={len(val)}")

    if "seasonality" in analysis_results:
        for col, val in analysis_results["seasonality"].items():
            if isinstance(val, dict) and "trend" in val:
                print(f"{col}: seasonality decomposition completed")

    if "smoothing" in analysis_results:
        for col, val in analysis_results["smoothing"].items():
            if isinstance(val, list) and val:
                print(f"{col}: smoothed_points={len(val)}")

    print(f"Report: {output_file}")
    print(f"Output Excel: {output_file.rsplit('.', 1)[0]}.xlsx")


def main():
    agent = ExcelAgent()

    # Run all scenarios; set indexes to run a subset,
    # e.g. run_scenarios([2]) runs only the polynomial regression one.
    run_scenarios = range(len(SCENARIOS))

    for i in run_scenarios:
        run_scenario(agent, SCENARIOS[i])

    print("\nAnalysis complete")


if __name__ == "__main__":
    main()
