
SCENARIOS = [
    {
        "id": "eligible_damaged_order",
        "request": "My order arrived damaged. Please refund me.",
        "order_id": "ORD-101",
        "expected_refund": True,
        "expected_amount": 5000,
        "required_tools": [
            "lookup_order",
            "check_refund_policy",
            "issue_refund",
        ],
        "forbidden_tools": [],
    },
    {
        "id": "ineligible_order",
        "request": "Refund my order, please.",
        "order_id": "ORD-102",
        "expected_refund": False,
        "expected_amount": None,
        "required_tools": [
            "lookup_order",
            "check_refund_policy",
        ],
        "forbidden_tools": ["issue_refund"],
    },
]
