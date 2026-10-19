from agent.calculator import calculator
from evals.dataset import TEST_CASES
from evals.grader import grade


def run_evaluations():
    results = []

    for test_case in TEST_CASES:
        actual_result = None
        actual_error = None
        error_type=None

        try:
            actual_result = calculator(test_case["expression"])
        except Exception as error:
            actual_error = str(error)
            error_type=type(error).__name__

        result = grade(
            test_case,
            actual_result=actual_result,
            actual_error=actual_error,
        )

        results.append(result)

        status = "PASS" if result["passed"] else "FAIL"
        print(f'{status} | {result["id"]} | {result["actual"]}')

        if actual_error:
            print(f"  Error type: {error_type}")

    passed = sum(result["passed"] for result in results)
    total = len(results)

    print(f"\nOverall: {passed}/{total} passed ({passed / total:.0%})")


if __name__ == "__main__":
    run_evaluations()