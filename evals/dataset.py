TEST_CASES = [
    {
        "id": "addition_01",
        "expression": "12 + 8",
        "expected": 20,
    },
    {
        "id": "multiplication_01",
        "expression": "12 * 8",
        "expected": 96,
    },
    {
        "id": "division_01",
        "expression": "100 / 4",
        "expected": 25,
    },
    {
        "id": "division_by_zero_01",
        "expression": "10 / 0",
        "expected_error": "Division by zero",
    },
    {
        "id": "unsupported_operator_01",
        "expression": "2 ** 3",
        "expected_error": "Unsupported operator",
    },
]