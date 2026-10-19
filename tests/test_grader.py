from evals.grader import grade


def test_correct_result_passes():
    test_case = {
        "id": "addition_01",
        "expected": 20,
    }

    result = grade(test_case, actual_result=20)

    assert result["passed"] is True


def test_wrong_result_fails():
    test_case = {
        "id": "addition_01",
        "expected": 20,
    }

    result = grade(test_case, actual_result=999)

    assert result["passed"] is False


def test_expected_error_passes():
    test_case = {
        "id": "division_by_zero_01",
        "expected_error": "Division by zero",
    }

    result = grade(
        test_case,
        actual_error="Division by zero",
    )

    assert result["passed"] is True


def test_unexpected_error_fails():
    test_case = {
        "id": "addition_01",
        "expected": 20,
    }

    result = grade(
        test_case,
        actual_error="Unexpected error",
    )

    assert result["passed"] is False