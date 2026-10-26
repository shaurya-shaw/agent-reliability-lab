import json
from pathlib import Path

from agent.support.agent import run_agent
from agent.support.tools import SupportTools
from evals.support.graders import grade_scenario
from evals.support.scenarios import SCENARIOS

def evaluate(mode="safe"):
    results = []

    for scenario in SCENARIOS:
        tools = SupportTools()

        response_data = run_agent(
            request=scenario["request"],
            order_id=scenario["order_id"],
            tools=tools,
            mode=mode,
        )

        result = grade_scenario(
            scenario=scenario,
            response=response_data["response"],
            trace=tools.trace,
            final_state=tools.get_state(),
        )

        result["trace"] = tools.trace
        results.append(result)

        status = "PASS" if result["passed"] else "FAIL"
        print(f"{status} | {result['id']}")

        for check, passed in result["checks"].items():
            print(f"  {'PASS' if passed else 'FAIL'} | {check}")

        if not result["passed"]:
            print(f"  Details: {result['details']}")

    total = len(results)
    passed = sum(result["passed"] for result in results)

    report = {
        "agent_mode": mode,
        "passed": passed,
        "total": total,
        "pass_rate": passed / total if total else 0,
        "results": results,
    }

    output_dir = Path("results")
    output_dir.mkdir(exist_ok=True)

    output_path = output_dir / f"support_eval_{mode}.json"
    output_path.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print(f"\nOverall: {passed}/{total} passed")
    print(f"Report: {output_path}")

    return report


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=["safe", "fake_success", "skip_policy", "over_refuse"],
        default="safe",
    )
    args = parser.parse_args()

    evaluate(args.mode)
