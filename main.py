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
        "user_prompt": "分析 sales.xlsx 的销售趋势，用多项式回归拟合非线性变化",
        "output_file": "./output/sales_poly_regression.xlsx",
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
