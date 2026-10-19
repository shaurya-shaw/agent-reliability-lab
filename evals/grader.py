
def grade(test_case, actual_result=None, actual_error=None):
    """Return whether the observed behavior matches expectations."""

    expected_error = test_case.get("expected_error")

    if expected_error is not None:
        passed = actual_error == expected_error
    else:
        passed = (
            actual_error is None
            and actual_result == test_case["expected"]
        )

    return {
        "id": test_case["id"],
        "passed": passed,
        "expected": test_case.get(
            "expected", test_case.get("expected_error")
        ),
        "actual": actual_error if actual_error else actual_result,
    }
